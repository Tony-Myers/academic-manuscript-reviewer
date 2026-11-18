"""Dedicated Evidence Cards print view (summary and detailed).

Independently authored for this release candidate: the fictional
materials-bench cards plus invented long findings, evidence and reviewer
wording. The endpoint checks always run. The browser checks print with
Chromium only where Playwright and a Chromium-based browser are installed
(EVIDENCE_PRINT_BROWSER selects one); they say nothing about Safari.
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
import fixtures as fx  # noqa: E402
import print_view  # noqa: E402
import server  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from test_release import Isolated  # noqa: E402

LONG = ('The fictional bench protocol describes calibration, scanning and logging steps for each tile; '
        'this synthetic finding is long so that it must continue across a printed page. ') * 9
PASSAGE = 'Additional synthetic manuscript wording for page-break testing. ' * 25
REVISED = ('Synthetic reviewer wording <script>alert(1)</script>: the bench log should name each '
           'instrument and its calibration date. ') * 6


def long_cards():
    cards = fx.cards()
    extra = []
    for n in range(1, 8):
        c = copy.deepcopy(cards['cards'][n % len(cards['cards'])])
        c['label'] = f'C{10 + n}'
        c['original'] = '* Concern: ' + LONG + f'[end of synthetic item {n}]'
        for group in c['evidence_groups'].values():
            for p in group:
                p['text'] = p['text'] + ' ' + PASSAGE + f'[end of synthetic passage {n}]'
        extra.append(c)
    cards['cards'] += extra
    return cards


FORBIDDEN_LAYOUT = ('<details', 'display:flex', 'display:grid', 'line-clamp', 'position:sticky',
                    'position:fixed', 'overflow:hidden', 'height:')


class PrintViewEndpoint(Isolated):
    def put(self, client, manifest, decisions):
        response = client.put('/api/review/' + self.jid + '/decisions',
                              json={'card_fingerprint': manifest['card_fingerprint'], 'decisions': decisions})
        self.assertEqual(response.status_code, 200, response.text)

    def test_summary_and_detailed_print_every_card_with_saved_decisions(self):
        manifest = self.save()
        with TestClient(server.app) as client:
            self.put(client, manifest, {'C1': {'decision': 'revise', 'note': REVISED},
                                        'C2': {'decision': 'dismiss', 'note': ''}})
            summary = client.get('/review/evidence-cards/' + self.jid + '/print')
            detailed = client.get('/review/evidence-cards/' + self.jid + '/print?mode=detailed')
            page = client.get('/review/evidence-cards/' + self.jid)
        for response in (summary, detailed):
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers.get('cache-control'), 'no-store')
            body = response.text
            for label in ('S1', 'C1', 'C2', 'P1'):
                self.assertIn(f'id="print-{label}"', body)
            self.assertEqual(body.count('AI-generated finding (original wording, unchanged)'), 4)
            self.assertIn('Not yet reviewed', body)                           # S1 and P1
            self.assertIn('Revised', body)
            self.assertIn('Dismissed', body)
            self.assertIn("Reviewer&#x27;s revised wording (verbatim): Synthetic reviewer wording "
                          "&lt;script&gt;alert(1)&lt;/script&gt;", body)
            self.assertNotIn('<script>alert(1)', body)
            self.assertIn('Every tile was scanned twice', body)                # AI text unchanged
            css = body.split('<style>')[1].split('</style>')[0]
            for forbidden in FORBIDDEN_LAYOUT:
                self.assertNotIn(forbidden, css if forbidden != '<details' else body)
        self.assertNotIn('Evidence from the manuscript', summary.text)
        self.assertEqual(detailed.text.count('<h3>Evidence from the manuscript</h3>'), 4)
        self.assertEqual(detailed.text.count('<h3>Verification record</h3>'), 4)
        self.assertIn('Print / Save Evidence Cards as PDF', page.text)
        self.assertIn('/review/evidence-cards/' + self.jid + '/print', page.text)

    def test_current_saved_decisions_are_printed_not_a_snapshot(self):
        manifest = self.save()
        with TestClient(server.app) as client:
            self.put(client, manifest, {'C1': {'decision': 'retain', 'note': 'First synthetic note.'}})
            first = client.get('/review/evidence-cards/' + self.jid + '/print').text
            self.put(client, manifest, {'C1': {'decision': 'revise', 'note': 'Second synthetic wording.'}})
            second = client.get('/review/evidence-cards/' + self.jid + '/print').text
        self.assertIn('First synthetic note.', first)
        self.assertIn('Second synthetic wording.', second)
        self.assertNotIn('First synthetic note.', second)

    def test_review_outside_the_store_uses_this_browsers_decisions(self):
        server.review_jobs[self.jid] = fx.job()
        with TestClient(server.app) as client:
            body = client.get('/review/evidence-cards/' + self.jid + '/print').text
        self.assertIn('const DECISION_SOURCE = "browser"', body)
        self.assertIn("localStorage.getItem('evidence-card-decisions:' + DOC_ID)", body)
        self.assertIn('textContent', body)
        self.assertNotIn('innerHTML', body.split('<script>')[1])

    def test_unknown_review_is_refused(self):
        with TestClient(server.app) as client:
            self.assertEqual(client.get('/review/evidence-cards/ab12cd34ef00/print').status_code, 404)


def find_browser():
    configured = os.environ.get('EVIDENCE_PRINT_BROWSER')
    if configured:
        return configured
    for name in ('google-chrome', 'chromium', 'chromium-browser'):
        if shutil.which(name):
            return shutil.which(name)
    return None


def text_overlaps(pdf):
    hits = 0
    for page in pdf.pages:
        chars = sorted((c for c in page.chars if c['text'].strip()), key=lambda c: (c['top'], c['x0']))
        for i, a in enumerate(chars):
            for b in chars[i + 1:i + 300]:
                if b['top'] > a['bottom']:
                    break
                if abs(a['top'] - b['top']) >= 0.5 and \
                        min(a['x1'], b['x1']) - max(a['x0'], b['x0']) > 1 and \
                        min(a['bottom'], b['bottom']) - max(a['top'], b['top']) > 2:
                    hits += 1
    return hits


class PrintViewInChromium(unittest.TestCase):
    def setUp(self):
        try:
            from playwright.sync_api import sync_playwright  # noqa: F401
        except ImportError:
            self.skipTest('Playwright is not installed; print view not printed in a browser here')
        self.browser_path = find_browser()
        if not self.browser_path:
            self.skipTest('no Chromium-based browser found; set EVIDENCE_PRINT_BROWSER')

    def print_pdf(self, mode):
        from playwright.sync_api import sync_playwright
        import pdfplumber
        cards = long_cards()
        decisions = {'C11': {'decision': 'revise', 'note': REVISED}, 'C12': {'decision': 'retain', 'note': ''},
                     'C2': {'decision': 'dismiss', 'note': 'Synthetic dismissal comment.'}}
        meta = {'job_id': 'ab12cd34ef56', 'filename': 'synthetic-bench.pdf', 'printed_at': 'fixture',
                'decision_source': 'saved', 'doc_id': 'job-ab12cd34ef56'}
        with tempfile.TemporaryDirectory(prefix='print-view-test-') as tmp:
            folder = Path(tmp)
            (folder / 'print.html').write_text(print_view.render(cards, decisions, meta, mode))

            class Quiet(http.server.SimpleHTTPRequestHandler):
                def log_message(self, *args):
                    pass
            srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0),
                                                  functools.partial(Quiet, directory=str(folder)))
            threading.Thread(target=srv.serve_forever, daemon=True).start()
            try:
                with sync_playwright() as p:
                    browser = p.chromium.launch(executable_path=self.browser_path, args=['--no-sandbox'])
                    page = browser.new_page()
                    page.goto(f'http://127.0.0.1:{srv.server_address[1]}/print.html')
                    page.emulate_media(media='print')
                    clipped = page.evaluate("""() => [...document.querySelectorAll('*')]
                        .filter(e => e.scrollHeight > e.clientHeight + 1 && getComputedStyle(e).overflowY !== 'visible'
                                     && e !== document.documentElement && e !== document.body).length""")
                    toolbar = page.evaluate("getComputedStyle(document.querySelector('.toolbar')).display")
                    page.pdf(path=str(folder / 'out.pdf'), format='A4')
                    browser.close()
            finally:
                srv.shutdown()
                srv.server_close()
            with pdfplumber.open(folder / 'out.pdf') as pdf:
                pages = len(pdf.pages)
                overlaps = text_overlaps(pdf)
                text = re.sub(r'\s+', ' ', ' '.join(pg.extract_text() or '' for pg in pdf.pages))
        return {'pages': pages, 'overlaps': overlaps, 'text': text, 'clipped': clipped,
                'toolbar': toolbar, 'cards': len(cards['cards'])}

    def check_common(self, result):
        self.assertGreater(result['pages'], 2)                       # findings span several pages
        self.assertEqual(result['overlaps'], 0, 'text drawn over other text')
        self.assertEqual(result['clipped'], 0, 'content clipped by overflow')
        self.assertEqual(result['toolbar'], 'none')                   # no controls in print
        text = result['text']
        for label in ['S1', 'C1', 'C2', 'P1'] + [f'C{10 + n}' for n in range(1, 8)]:
            self.assertIn(f'{label} · ', text)                        # every finding present
        for n in range(1, 8):
            self.assertIn(f'end of synthetic item {n}', text)         # long findings complete
        self.assertIn('calibration date', text)                       # reviewer revision
        self.assertIn('Not yet reviewed', text)                       # unreviewed findings
        self.assertIn('Synthetic dismissal comment.', text)
        self.assertNotIn('Print / Save as PDF', text)

    def test_summary_prints_every_finding_and_decision(self):
        result = self.print_pdf('summary')
        self.check_common(result)
        self.assertNotIn('Evidence from the manuscript', result['text'].upper().title())
        self.assertNotIn('end of synthetic passage', result['text'])

    def test_detailed_prints_all_evidence_regardless_of_expansion(self):
        result = self.print_pdf('detailed')
        self.check_common(result)
        self.assertEqual(result['text'].upper().count('EVIDENCE FROM THE MANUSCRIPT'), result['cards'])
        self.assertEqual(result['text'].upper().count('VERIFICATION RECORD'), result['cards'])


if __name__ == '__main__':
    unittest.main()
