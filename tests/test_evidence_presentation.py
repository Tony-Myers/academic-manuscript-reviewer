"""Evidence locations, unauthenticated quotations and Markdown in the
reviewer-facing Human Evidence Appendix.

Independently authored for this release candidate. The manuscript text,
appraisal, verifier replies and AI intermediate text are all invented here.
No model is called; no manuscript, review or model output is used.
"""
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'app'))
sys.path.insert(0, str(ROOT / 'tests'))
import appendix_view  # noqa: E402
import evidence_cards as ec  # noqa: E402
import fixtures as fx  # noqa: E402
import review_links as rl  # noqa: E402
import review_store as store  # noqa: E402
import server  # noqa: E402
import source_verification as sv  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from test_release import Isolated  # noqa: E402

PAGED = ('[Page 1]\nA fictional bench introduction.\n\n'
         '[Page 3]\nThe chamber temperature was held at twenty degrees throughout the run.\n'
         '[TABLE_START]\nSource: inline_markdown\nLabel: Table 2\n'
         'Tile colour | Signal units\nAmber | the amber reference tile read four point six units after recalibration\n'
         '[TABLE_END]\n')
UNPAGED = 'The chamber temperature was held at twenty degrees throughout the run.\n'
SUMMARY_ONLY = 'The bench operator recalibrated every tile twice on each working day.'

REPORT = '''# Overall synopsis
A fictional bench.

# Directly supported concerns
* **Concern:** The temperature control is described but never verified against a log.
* **Evidence:** "The chamber temperature was held at twenty degrees throughout the run."
* **Why it matters:** Drift could alter the *signal* readings.
* **Concern:** The amber reading depends on an undocumented recalibration.
* **Evidence:** "the amber reference tile read four point six units after recalibration"
* **Concern:** Recalibration frequency is unclear.
* **Evidence:** "The bench operator recalibrated every tile twice on each working day."

# Verification prompts
* **Check:** Confirm the calibration log. **Reason:** The <script>alert(1)</script> note needs *checking*.
'''


def assessor(*, prompt, schema, max_tokens):
    labels = schema['properties']['items']['items']['properties']['label']['enum']
    return {'items': [dict(label=label, verdict='unresolved', quote='', reason='Fixture.', correction='',
                           surviving_point='', duplicate_of='', reviewer_check='', evidence=[])
                      for label in labels]}


def render(sources, intermediate=None, report=REPORT):
    verification = sv.verify_report(report, sources, assessor, budget=100000, unexamined=[]).as_dict()
    cards = ec.build_cards(verification, sources)
    links = rl.build_links(report, verification)
    return appendix_view.render(report, links, cards, None, 'fixture-time', intermediate=intermediate,
                                sources=sources)


def entry(md, fid):
    return re.search(r'## ' + fid + r' — .*?\n(.*?)(?=\n## )', md, re.S).group(1)


class EvidenceLocations(unittest.TestCase):
    def test_page_and_table_locations_come_from_extraction_markers(self):
        md = render({'bench.pdf': PAGED})
        self.assertIn('p. 3 in bench.pdf', entry(md, 'C1'))
        self.assertIn('Table 2, p. 3 in bench.pdf', entry(md, 'C2'))  # table without its own page
        self.assertIn('> The chamber temperature was held at twenty degrees throughout the run.', entry(md, 'C1'))
        self.assertIn('Matched exactly, apart from spacing and line breaks.', entry(md, 'C1'))
        self.assertNotIn('location not recorded', md)

    def test_missing_page_markers_are_stated_not_invented(self):
        md = render({'bench.docx': UNPAGED})
        text = entry(md, 'C1')
        self.assertIn('page not established', text)
        self.assertNotIn('p. ', text.split('page not established')[0][-20:])

    def test_appraisal_evidence_is_separated_from_located_evidence(self):
        md = render({'bench.pdf': PAGED})
        self.assertIn('**Evidence as stated in the appraisal** (AI-written', entry(md, 'C1'))
        self.assertIn('**Exact quotation authenticated** (verbatim manuscript text', entry(md, 'C1'))
        self.assertIn('**Exact quotation authenticated:** none.', entry(md, 'C3'))

    def test_without_saved_manuscript_text_the_card_results_are_labelled(self):
        verification = sv.verify_report(REPORT, {'bench.pdf': PAGED}, assessor, budget=100000,
                                        unexamined=[]).as_dict()
        cards = ec.build_cards(verification, {'bench.pdf': PAGED})
        md = appendix_view.render(REPORT, rl.build_links(REPORT, verification), cards, None, 'fixture-time')
        self.assertIn('The manuscript text was not saved with this review', entry(md, 'C1'))
        self.assertIn('**Manuscript passages located by the application**', entry(md, 'C1'))


class UnauthenticatedQuotations(unittest.TestCase):
    def test_quotation_is_named_with_finding_reason_and_uncertainty(self):
        text = entry(render({'bench.pdf': PAGED}), 'C3')
        self.assertIn('**Quotation not located — not authenticated** (not manuscript evidence)', text)
        self.assertIn('> The bench operator recalibrated every tile twice on each working day.', text)
        self.assertIn('quoted by the review item as its evidence', text)
        self.assertIn('Not found in the extracted manuscript text as one continuous passage', text)
        self.assertIn('does not show that the manuscript lacks the information', text)

    def test_provenance_from_saved_intermediate_ai_text(self):
        found = render({'bench.pdf': PAGED}, [('the AI file summary for bench.pdf', 'Notes. ' + SUMMARY_ONLY)])
        self.assertIn('It appears verbatim in the AI file summary for bench.pdf, which is AI-generated text',
                      entry(found, 'C3'))
        absent = render({'bench.pdf': PAGED}, [('the AI file summary for bench.pdf', 'Unrelated notes.')])
        self.assertIn('its origin cannot be established', entry(absent, 'C3'))
        unsaved = render({'bench.pdf': PAGED}, None)
        self.assertIn('saved only for reviews run in Development mode', entry(unsaved, 'C3'))

    def test_concerns_and_questions_remain_listed(self):
        md = render({'bench.pdf': PAGED})
        for heading in ('## C1 — Concern', '## C2 — Concern', '## C3 — Concern', '## Q1 — Verification question'):
            self.assertIn(heading, md)
        self.assertNotIn('No substantive concerns', md)


class MarkdownInAppendix(unittest.TestCase):
    def test_ai_formatting_is_kept_and_manuscript_text_escaped(self):
        md = render({'bench.pdf': PAGED})
        self.assertNotIn('\\*\\*', md)                        # no escaped bold labels
        self.assertIn('Drift could alter the *signal* readings.', md)  # AI emphasis kept as Markdown
        self.assertIn('**Reason (AI-written):** The <script>alert(1)</script> note needs *checking*.', md)
        excerpt = '> the amber reference tile read four point six units after recalibration'
        self.assertIn(excerpt, md)
        star = render({'bench.pdf': PAGED.replace('twenty degrees', 'twenty *p* < 0.05 degrees')},
                      report=REPORT.replace('twenty degrees', 'twenty *p* < 0.05 degrees'))
        self.assertIn('twenty \\*p\\* \\< 0.05 degrees', star)  # verbatim manuscript text is escaped


class AppendixOverHttp(Isolated):
    def test_saved_review_with_trace_reports_provenance(self):
        verification = sv.verify_report(REPORT, {'bench.pdf': PAGED}, assessor, budget=100000,
                                        unexamined=[]).as_dict()
        cards = ec.build_cards(verification, {'bench.pdf': PAGED})
        job = fx.job(report=REPORT, text=PAGED, sources={'bench.pdf': PAGED},
                     verification_sources={'bench.pdf': PAGED},
                     source_verification={'verification': verification}, development_mode=True,
                     trace={'files': [{'source_name': 'bench.pdf', 'file_summary': SUMMARY_ONLY,
                                       'source_chunks': ['Manuscript chunk text is not AI text.']}]})
        store.save_completed(self.jid, job, cards=cards, manuscript_sha256=None)
        with TestClient(server.app) as client:
            md = client.get('/api/review/appendix/' + self.jid).json()['appendix']
        self.assertIn('It appears verbatim in the AI file summary for bench.pdf', md)
        self.assertIn('Table 2, p. 3 in bench.pdf', md)


if __name__ == '__main__':
    unittest.main()
