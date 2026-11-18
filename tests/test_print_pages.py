"""Print pages for the Critical Appraisal and the Human Evidence Appendix.

Independently authored for this release candidate: invented materials-bench
appraisals (long sections, headings, lists, tables and unsafe-looking text)
saved to a temporary store. Endpoint checks always run. Browser checks print
with Chromium only where Playwright and a Chromium-based browser are installed
(EVIDENCE_PRINT_BROWSER selects one); they say nothing about Safari.
"""
import functools
import hashlib
import http.server
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
import review_store as store  # noqa: E402
import server  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from test_release import Isolated  # noqa: E402

LONG = ('This synthetic paragraph describes the fictional bench procedure at length so that the section '
        'has to continue across a printed page boundary without overlapping the next section. ') * 8


def long_report():
    sections = ['Model: synthetic-fixture-model', 'Reasoning: instruct', '', '# Overall synopsis', LONG, '',
                '| Tile | Signal units | Note |', '| --- | --- | --- |',
                '| Amber | 4.6 | <script>alert(1)</script> |', '| Violet | 7.3 | pipe \\| inside |', '',
                '# Major strengths', '* Strength: The reference tile was checked before each batch.',
                '  - Nested synthetic detail under the strength.', '',
                '# Directly supported concerns']
    for n in range(1, 9):
        sections += [f'* **Concern:** Synthetic concern {n}. ' + LONG[:400] + f' [end of concern {n}]',
                     '* **Evidence:** "Every tile was scanned twice."', '']
    sections += ['# Verification prompts', '1. Check: Confirm the chamber log.', '2. Check: Confirm the serials.', '',
                 '# Source verification record', '> Verifier note kept for audit.', '', '```', 'raw <b>block</b>', '```']
    return '\n'.join(sections) + '\n'


def digests(folder):
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.iterdir() if p.is_file()}


class PrintPageEndpoints(Isolated):
    def get(self, client, kind):
        response = client.get(f'/review/{self.jid}/print/{kind}')
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.headers.get('cache-control'), 'no-store')
        return response.text

    def test_appraisal_print_is_complete_structured_and_safe(self):
        report = long_report()
        store.save_completed(self.jid, fx.job(report=report), cards=fx.cards(), manuscript_sha256=None)
        folder = store.session_dir(self.jid)
        before = digests(folder)
        with TestClient(server.app) as client:
            body = self.get(client, 'appraisal')
        self.assertEqual(before, digests(folder))                       # nothing saved or changed
        for heading in ('Overall synopsis', 'Major strengths', 'Directly supported concerns',
                        'Verification prompts', 'Source verification record'):
            self.assertRegex(body, f'<h2>{heading}</h2>')
        for n in range(1, 9):
            self.assertIn(f'[end of concern {n}]', body)                 # complete
        self.assertIn('<table><thead><tr><th>Tile</th>', body)
        self.assertIn('<td>pipe | inside</td>', body)
        self.assertIn('<li class="l1">Nested synthetic detail', body)
        self.assertIn('<ol><li class="l0">Check: Confirm the chamber log.</li>', body)
        self.assertIn('<strong>Concern:</strong>', body)
        self.assertIn('&lt;script&gt;alert(1)&lt;/script&gt;', body)      # escaped, not executed
        self.assertIn('raw &lt;b&gt;block&lt;/b&gt;', body)
        self.assertNotIn('<script>alert', body)
        self.assertIn('Model: synthetic-fixture-model', body)             # technical part kept
        self.assertIn('AI-generated appraisal', body)
        self.assertIn('Reviewer decisions are not part of it', body)
        self.assertIn('synthetic-bench.pdf · review ' + self.jid + ' · printed ', body)
        for workspace in ('<iframe', 'modelSelect', 'restartBtn', 'reviewWorkspace', 'Manuscript Review'):
            self.assertNotIn(workspace, body)

    def test_appraisal_order_and_wording_match_the_saved_report(self):
        report = long_report()
        technical, appraisal, audit = print_view.split_appraisal(report)
        self.assertEqual(technical + appraisal + audit, report)
        self.assertTrue(appraisal.startswith('# Overall synopsis'))
        self.assertTrue(audit.startswith('# Source verification record'))

    def test_appendix_print_matches_the_current_appendix(self):
        self.save()
        with TestClient(server.app) as client:
            body = self.get(client, 'appendix')
            tab = client.get('/api/review/appendix/' + self.jid).json()['appendix']
            original = client.get('/api/review/appendix/' + self.jid + '?version=original')
        for heading in ('C1 — Concern', 'C2 — Concern', 'Q1 — Verification question',
                        'A. Final appraisal findings',
                        'B. Additional observations from the initial reading (not independently verified)'):
            self.assertIn(f'<h3>{heading}</h3>', body)
        self.assertIn('Exact quotation authenticated', body)
        self.assertIn('The Evidence Card does not list this quotation as located', body)
        self.assertEqual(tab.split('## A.')[1].split('## C. ')[0].count('> Every tile was scanned twice.'),
                         body.count('<blockquote>Every tile was scanned twice.</blockquote>'))
        self.assertIn('<blockquote>Every tile was scanned twice.</blockquote>', body)
        self.assertIn('generated now from the saved review data', body)
        self.assertNotIn('\\*', body)                                    # no stray escape backslashes
        self.assertEqual(tab.count('## C'), body.count('<h3>C'))
        self.assertEqual(original.status_code, 200)                      # original download unchanged
        self.assertEqual(original.json()['appendix'], fx.job()['appendix'])

    def test_appendix_locations_print(self):
        paged = ('[Page 3]\nThe chamber temperature was held at twenty degrees throughout the run.\n')
        report = fx.REPORT.replace('* Evidence: The example does not specify instrument serials.',
                                   '* Evidence: "The chamber temperature was held at twenty degrees throughout the run."')
        import source_verification as sv, evidence_cards as ec
        verification = sv.verify_report(report, {'bench.pdf': paged}, fx.assessor, budget=100000,
                                         unexamined=[]).as_dict()
        job = fx.job(report=report, text=paged, sources={'bench.pdf': paged},
                     verification_sources={'bench.pdf': paged}, source_verification={'verification': verification})
        store.save_completed(self.jid, job, cards=ec.build_cards(verification, {'bench.pdf': paged}),
                             manuscript_sha256=None)
        with TestClient(server.app) as client:
            body = self.get(client, 'appendix')
        self.assertIn('p. 3 in bench.pdf', body)
        self.assertIn('<blockquote>The chamber temperature was held at twenty degrees throughout the run.</blockquote>', body)
        self.assertEqual(body.count('<h1>'), 1)
        self.assertNotIn('<h2>Human Evidence Appendix</h2>', body)

    def test_historical_review_prints_both(self):
        from test_historical_reviews import BOLD_REPORT, OLD_APPENDIX
        store.save_completed(self.jid, fx.job(report=BOLD_REPORT, appendix=OLD_APPENDIX), cards=fx.cards(),
                             manuscript_sha256=None)
        with TestClient(server.app) as client:
            appraisal = self.get(client, 'appraisal')
            appendix = self.get(client, 'appendix')
        self.assertIn('<strong>Concern:</strong>', appraisal)
        self.assertIn('<h3>C1 — Concern</h3>', appendix)
        self.assertNotIn('No substantive concerns', appendix)

    def test_unknown_or_unsaved_review_is_refused(self):
        with TestClient(server.app) as client:
            self.assertEqual(client.get('/review/ab12cd34ef00/print/appraisal').status_code, 404)
            self.assertEqual(client.get('/review/not-a-review/print/appendix').status_code, 404)

    def test_interface_offers_all_three_print_buttons(self):
        self.save()
        with TestClient(server.app) as client:
            ui = client.get('/').text
            cards = client.get('/review/evidence-cards/' + self.jid).text
        self.assertIn('Print / Save Critical Appraisal as PDF', ui)
        self.assertIn('Print / Save Human Evidence Appendix as PDF', ui)
        self.assertIn('Print / Save Evidence Cards as PDF', cards)
        self.assertIn('dlOriginalAppendix', ui)                          # original download kept


def find_browser():
    configured = os.environ.get('EVIDENCE_PRINT_BROWSER')
    if configured:
        return configured
    for name in ('google-chrome', 'chromium', 'chromium-browser'):
        if shutil.which(name):
            return shutil.which(name)
    return None


class PrintPagesInChromium(unittest.TestCase):
    def setUp(self):
        try:
            from playwright.sync_api import sync_playwright  # noqa: F401
        except ImportError:
            self.skipTest('Playwright is not installed; print pages not printed in a browser here')
        self.browser_path = find_browser()
        if not self.browser_path:
            self.skipTest('no Chromium-based browser found; set EVIDENCE_PRINT_BROWSER')

    def print_pdf(self, html):
        from playwright.sync_api import sync_playwright
        import pdfplumber
        from test_print_view import text_overlaps
        with tempfile.TemporaryDirectory(prefix='print-pages-test-') as tmp:
            folder = Path(tmp)
            (folder / 'page.html').write_text(html)

            class Quiet(http.server.SimpleHTTPRequestHandler):
                def log_message(self, *args):
                    pass
            srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Quiet, directory=str(folder)))
            threading.Thread(target=srv.serve_forever, daemon=True).start()
            try:
                with sync_playwright() as p:
                    browser = p.chromium.launch(executable_path=self.browser_path, args=['--no-sandbox'])
                    page = browser.new_page()
                    page.goto(f'http://127.0.0.1:{srv.server_address[1]}/page.html')
                    page.emulate_media(media='print')
                    clipped = page.evaluate("""() => [...document.querySelectorAll('*')]
                        .filter(e => e.scrollHeight > e.clientHeight + 1 && getComputedStyle(e).overflowY !== 'visible'
                                     && e !== document.documentElement && e !== document.body).length""")
                    wide = page.evaluate("""() => [...document.querySelectorAll('.doc *')]
                        .filter(e => e.getBoundingClientRect().right > document.documentElement.clientWidth + 1).length""")
                    toolbar = page.evaluate("getComputedStyle(document.querySelector('.toolbar')).display")
                    page.pdf(path=str(folder / 'out.pdf'), format='A4')
                    browser.close()
            finally:
                srv.shutdown()
                srv.server_close()
            with pdfplumber.open(folder / 'out.pdf') as pdf:
                return {'pages': len(pdf.pages), 'overlaps': text_overlaps(pdf), 'clipped': clipped, 'wide': wide,
                        'toolbar': toolbar,
                        'text': re.sub(r'\s+', ' ', ' '.join(pg.extract_text() or '' for pg in pdf.pages))}

    def test_long_appraisal_prints_completely_without_overlap(self):
        meta = {'job_id': 'ab12cd34ef56', 'filename': 'synthetic-bench.pdf', 'printed_at': 'fixture'}
        result = self.print_pdf(print_view.render_appraisal(long_report(), meta))
        self.assertGreater(result['pages'], 2)
        self.assertEqual((result['overlaps'], result['clipped'], result['wide'], result['toolbar']), (0, 0, 0, 'none'))
        for n in range(1, 9):
            self.assertIn(f'end of concern {n}', result['text'])
        for heading in ('Overall synopsis', 'Directly supported concerns', 'Verification prompts',
                        'Source verification record', 'Violet', 'AI-generated appraisal'):
            self.assertIn(heading, result['text'])
        self.assertNotIn('Print / Save as PDF', result['text'])

    def test_long_appendix_prints_completely_without_overlap(self):
        import appendix_view
        passage = 'Synthetic located manuscript wording for page-break testing. ' * 60
        md = ['# Human Evidence Appendix', '', '## A. Final appraisal findings', '']
        for n in range(1, 7):
            md += [f'## C{n} — Concern', '', f'**Finding (final appraisal, AI-generated):** Synthetic finding {n}.', '',
                   '**Manuscript passages located by the application** (verbatim):', '',
                   f'- p. {n} in bench.pdf · cited by the verifier', '', '> ' + passage + f'[end of passage {n}]', '',
                   '**Quotations that could not be authenticated** (not manuscript evidence):', '',
                   '- Not authenticated: not found.', '', '> An invented unlocatable quotation.', '']
        md += appendix_view.STATUS_KEY
        meta = {'job_id': 'ab12cd34ef56', 'filename': 'synthetic-bench.pdf', 'printed_at': 'fixture'}
        result = self.print_pdf(print_view.render_appendix('\n'.join(md), meta))
        self.assertGreater(result['pages'], 2)
        self.assertEqual((result['overlaps'], result['clipped'], result['wide'], result['toolbar']), (0, 0, 0, 'none'))
        for n in range(1, 7):
            self.assertIn(f'end of passage {n}', result['text'])
            # The dash can be extracted from the PDF as a private-use glyph.
            self.assertRegex(result['text'], rf'C{n} \S Concern')
        self.assertIn('What the evidence statuses mean', result['text'])


if __name__ == '__main__':
    unittest.main()
