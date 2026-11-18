"""Evidence Cards print layout.

Independently authored for this release candidate, with the fictional
materials-bench fixtures and invented reviewer wording. The structural checks
always run. The browser check runs only where Playwright and a Chromium-based
browser are installed (set EVIDENCE_PRINT_BROWSER to a browser executable to
choose one); otherwise it is skipped and says so. It prints with Chromium's
engine, not Safari's.
"""
import copy
import functools
import http.server
import json
import os
import re
import shutil
import sys
import tempfile
import threading
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'app'))
sys.path.insert(0, str(ROOT / 'tests'))
import evidence_cards as ec  # noqa: E402
import fixtures as fx  # noqa: E402

LONG = ('The fictional bench protocol describes calibration, scanning and logging steps for each tile; '
        'this synthetic finding is long so that it must continue across a printed page. ') * 6
REVISED = 'Synthetic reviewer wording: the bench log should name each instrument and its calibration date. ' * 5


def page_html():
    cards = fx.cards()
    extra = []
    for n in range(1, 7):
        c = copy.deepcopy(cards['cards'][n % len(cards['cards'])])
        c['label'] = f'C{10 + n}'
        c['original'] = '* Concern: ' + LONG + f'[end of synthetic item {n}]'
        extra.append(c)
    cards['cards'] += extra
    return ec.render_html(cards, 'Evidence cards: synthetic bench', 'doc-print-test')


def print_block(html):
    match = re.search(r'@media print\{(.*?)\n\}\n', html, re.S)
    return match.group(1) if match else ''


class PrintStylesheet(unittest.TestCase):
    def setUp(self):
        self.html = page_html()
        self.css = print_block(self.html)

    def test_print_rules_exist_and_undo_the_overlap_causes(self):
        self.assertTrue(self.css, 'no print stylesheet')
        self.assertIn('.card>summary{display:block', self.css)                 # no flex across pages
        self.assertIn('.obs{display:block;-webkit-line-clamp:none', self.css)  # no clamp, full finding
        self.assertIn('overflow:visible', self.css)
        self.assertIn('break-inside:auto', self.css)                            # long cards may flow
        for hidden in ('.toolbar', '.filters', '.decide', 'textarea', 'button', '.viewnav'):
            self.assertIn(hidden, self.css.split('{display:none!important}')[0])

    def test_screen_layout_is_unchanged(self):
        screen = self.html.split('/* Printing.')[0]
        self.assertIn('.obs{white-space:pre-wrap;font-size:.84rem;margin-top:3px;display:-webkit-box;'
                      '-webkit-line-clamp:6', screen)
        self.assertIn('.card>summary{list-style:none;cursor:pointer;padding:10px 14px;display:flex', screen)
        self.assertIn('.print-note{display:none}', screen)

    def test_reviewer_wording_has_a_printable_place_set_as_text(self):
        self.assertEqual(len(re.findall(r'<div class="print-note" id="pnote-', self.html)), 10)
        self.assertIn('printed.textContent =', self.html)
        self.assertNotIn('printed.innerHTML', self.html)


def find_browser():
    configured = os.environ.get('EVIDENCE_PRINT_BROWSER')
    if configured:
        return configured
    for name in ('google-chrome', 'chromium', 'chromium-browser'):
        found = shutil.which(name)
        if found:
            return found
    return None


class PrintedInBrowser(unittest.TestCase):
    def setUp(self):
        try:
            from playwright.sync_api import sync_playwright  # noqa: F401
        except ImportError:
            self.skipTest('Playwright is not installed; print layout not tested in a browser here')
        self.browser_path = find_browser()
        if not self.browser_path:
            self.skipTest('no Chromium-based browser found; set EVIDENCE_PRINT_BROWSER')

    def test_expanded_and_collapsed_cards_print_without_overlap_or_truncation(self):
        from playwright.sync_api import sync_playwright
        import pdfplumber
        with tempfile.TemporaryDirectory(prefix='print-layout-test-') as tmp:
            folder = Path(tmp)
            (folder / 'cards.html').write_text(page_html())
            handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(folder))
            handler.log_message = lambda *a: None
            server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
            threading.Thread(target=server.serve_forever, daemon=True).start()
            decisions = {'C11': {'decision': 'revise', 'note': REVISED, 'confirmed_at': 't'},
                         'C2': {'decision': 'dismiss', 'note': '', 'confirmed_at': 't'}}
            try:
                with sync_playwright() as p:
                    browser = p.chromium.launch(executable_path=self.browser_path, args=['--no-sandbox'])
                    page = browser.new_page()
                    page.add_init_script("localStorage.setItem('evidence-card-decisions:doc-print-test', "
                                         + json.dumps(json.dumps(decisions)) + ");")
                    page.goto(f'http://127.0.0.1:{server.server_address[1]}/cards.html')
                    page.evaluate("['S1','C11','C12','C13'].forEach(l => document.getElementById('card-' + l).open = true)")
                    page.emulate_media(media='print')
                    state = page.evaluate("""() => {
                      const cards = [...document.querySelectorAll('details.card')];
                      let overlap = 0;
                      for (let i = 0; i + 1 < cards.length; i++)
                        if (cards[i].getBoundingClientRect().bottom > cards[i + 1].getBoundingClientRect().top + 0.5) overlap++;
                      return {overlap,
                        clipped: [...document.querySelectorAll('.obs')].filter(o => o.scrollHeight > o.clientHeight + 1).length,
                        controls: [...document.querySelectorAll('button, textarea')].filter(e => getComputedStyle(e).display !== 'none').length,
                        note: getComputedStyle(document.getElementById('pnote-C11')).display};
                    }""")
                    pdf_path = folder / 'cards.pdf'
                    page.pdf(path=str(pdf_path), format='A4')
                    browser.close()
            finally:
                server.shutdown()
            self.assertEqual(state, {'overlap': 0, 'clipped': 0, 'controls': 0, 'note': 'block'})
            with pdfplumber.open(pdf_path) as pdf:
                text = re.sub(r'\s+', ' ', ' '.join(pg.extract_text() or '' for pg in pdf.pages))
                overlaps = 0
                for pg in pdf.pages:
                    chars = sorted((c for c in pg.chars if c['text'].strip()), key=lambda c: (c['top'], c['x0']))
                    for i, a in enumerate(chars):
                        for b in chars[i + 1:i + 300]:
                            if b['top'] > a['bottom']:
                                break
                            if abs(a['top'] - b['top']) >= 0.5 and \
                                    min(a['x1'], b['x1']) - max(a['x0'], b['x0']) > 1 and \
                                    min(a['bottom'], b['bottom']) - max(a['top'], b['top']) > 2:
                                overlaps += 1
            self.assertEqual(overlaps, 0, 'text drawn over other text in the printed PDF')
            self.assertIn('calibration date', text)              # reviewer wording printed
            for n in range(1, 7):
                self.assertIn(f'end of synthetic item {n}', text)  # long findings complete


if __name__ == '__main__':
    unittest.main()
