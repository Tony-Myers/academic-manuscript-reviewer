"""Concise reviewer summary and full audit export of reviewer decisions.

Independently authored for this release candidate. Findings come from the
fictional materials-bench fixtures in fixtures.py; the reviewer decisions and
wording below are invented here. No model is called and no manuscript or
review material is used.
"""
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'app'))
sys.path.insert(0, str(ROOT / 'tests'))
import decisions_report as dr  # noqa: E402
import fixtures as fx  # noqa: E402
import review_store as store  # noqa: E402
import server  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from test_release import Isolated  # noqa: E402

REVISED = 'Report each instrument serial; the *p* < 0.05 [95% CI] claim in Table 2 needs #3 checked.'
DECISIONS = {
    'S1': {'decision': 'retain', 'note': 'Agree; mention the batch schedule.', 'confirmed_at': '2026-01-01T10:00:00Z'},
    'C1': {'decision': 'revise', 'note': REVISED, 'confirmed_at': '2026-01-01T10:01:00Z'},
    'C2': {'decision': 'dismiss', 'note': 'The text reports two scans per tile.', 'confirmed_at': '2026-01-01T10:02:00Z'},
}
META = {'filename': 'synthetic-bench.pdf', 'job_id': 'ab12cd34ef56', 'title': 'A fictional tile bench'}


def unescape(text):
    """Undo the export's backslash escaping (CommonMark punctuation escapes)."""
    return re.sub(r'\\(.)', r'\1', text)


def section(markdown, heading):
    match = re.search(r'^## ' + re.escape(heading) + r'\n(.*?)(?=^## |\Z)', markdown, re.M | re.S)
    return match.group(1) if match else ''


class ConciseExport(unittest.TestCase):
    def setUp(self):
        self.cards = fx.cards()
        self.md = dr.render_concise_markdown(self.cards, DECISIONS, META)

    def test_retained_finding_is_identifiable(self):
        retained = section(self.md, 'Retained findings')
        self.assertIn('### S1 (Strength)', retained)
        self.assertIn('The reference tile was checked before each batch.', retained)

    def test_revised_finding_uses_the_reviewers_exact_wording(self):
        revised = section(self.md, 'Revised findings')
        self.assertIn('### C1 (Concern)', revised)
        quoted = '\n'.join(line[2:] for line in revised.splitlines() if line.startswith('> '))
        self.assertEqual(unescape(quoted), REVISED)
        self.assertLess(revised.index("Reviewer's revised wording"), revised.index('Original AI observation'))
        self.assertIn('for reference only', revised)
        self.assertNotIn('C1', section(self.md, 'Retained findings'))

    def test_revision_without_wording_is_not_replaced_by_the_ai_text(self):
        md = dr.render_concise_markdown(self.cards, {'C1': {'decision': 'revise', 'note': ''}}, META)
        revised = section(md, 'Revised findings')
        self.assertIn('No revised wording was recorded', revised)
        self.assertIn('has not been accepted in its place', revised)

    def test_dismissed_finding_is_summarised_not_reproduced(self):
        self.assertNotIn('C2', section(self.md, 'Retained findings'))
        self.assertNotIn('C2', section(self.md, 'Revised findings'))
        dismissed = section(self.md, 'Dismissed findings')
        self.assertIn('**C2** (Concern): Each tile appears to have been scanned once.', dismissed)
        self.assertNotIn('Every tile was scanned twice', dismissed)  # its quotation is not repeated

    def test_undecided_findings_are_outstanding_not_accepted(self):
        waiting = section(self.md, 'Awaiting a decision')
        self.assertIn('**P1**', waiting)
        self.assertIn('have not been accepted', waiting)
        for heading in ('Retained findings', 'Revised findings', 'Dismissed findings'):
            self.assertNotIn('P1', section(self.md, heading))
        self.assertIn('Awaiting a decision: 1', self.md)

    def test_undecided_disputed_finding_keeps_its_warning(self):
        md = dr.render_concise_markdown(self.cards, {}, META)
        waiting = section(md, 'Awaiting a decision')
        line = next(l for l in waiting.splitlines() if l.startswith('- **C2**'))
        self.assertIn('Disputed by the AI verifier', line)
        self.assertNotIn('Disputed', next(l for l in waiting.splitlines() if l.startswith('- **S1**')))

    def test_reviewer_comments_are_kept(self):
        self.assertIn('Agree; mention the batch schedule.', unescape(self.md))
        self.assertIn('The text reports two scans per tile.', unescape(self.md))

    def test_technical_material_is_left_out(self):
        full = dr.render_markdown(self.cards, DECISIONS, META)
        for absent in ('A reference tile was rescanned before every batch',  # manuscript quotation
                       'Detailed verification record', '"label"', 'Verifier', 'What still needs checking',
                       'Evidence not confirmed', '<details>'):
            self.assertNotIn(absent, self.md, absent)
            self.assertIn(absent, full, absent)  # still available in the audit record
        self.assertLess(len(self.md.splitlines()) * 5, len(full.splitlines()))
        self.assertIn('remains responsible', self.md)
        self.assertIn('synthetic-bench.pdf, p. 1', self.md)  # concise evidence reference
        self.assertIn('A fictional tile bench', self.md)

    def test_full_audit_export_is_labelled_and_keeps_every_decision(self):
        full = dr.render_markdown(self.cards, DECISIONS, META)
        self.assertTrue(full.startswith('# Human reviewer decisions: full audit record'))
        self.assertIn(dr.md_quote(REVISED), full)
        self.assertIn('Detailed verification record', full)


class ExportEndpoints(Isolated):
    def test_both_exports_use_the_same_decisions_and_change_nothing(self):
        manifest = self.save()
        with TestClient(server.app) as client:
            saved = client.put('/api/review/' + self.jid + '/decisions',
                               json={'card_fingerprint': manifest['card_fingerprint'], 'decisions': DECISIONS})
            self.assertEqual(saved.status_code, 200, saved.text)
            folder = store.session_dir(self.jid)
            before = {p.name: p.read_bytes() for p in folder.iterdir() if p.is_file()}
            stored_before = client.get('/api/review/' + self.jid + '/decisions').json()
            concise = client.post('/api/review/' + self.jid + '/decisions-summary.md', json={'decisions': DECISIONS})
            audit = client.post('/api/review/' + self.jid + '/decisions.md', json={'decisions': DECISIONS})
            stored_after = client.get('/api/review/' + self.jid + '/decisions').json()
            page = client.get('/review/evidence-cards/' + self.jid)
            bad = client.post('/api/review/' + self.jid + '/decisions-summary.md',
                              json={'decisions': {'C99': {'decision': 'retain'}}})
        self.assertEqual(before, {p.name: p.read_bytes() for p in folder.iterdir() if p.is_file()})
        self.assertEqual(stored_before, stored_after)
        for response, name in ((concise, 'reviewer_summary.md'), (audit, 'reviewer_decisions_full_audit.md')):
            self.assertEqual(response.status_code, 200, response.text)
            self.assertIn('text/markdown', response.headers['content-type'])
            self.assertIn(name, response.headers['content-disposition'])
            self.assertIn(REVISED, unescape(response.text))
        self.assertTrue(concise.text.startswith('# Reviewer summary'))
        self.assertIn('Export reviewer summary (.md)', page.text)
        self.assertIn('Export full audit record (.md)', page.text)
        self.assertEqual(bad.status_code, 400)


if __name__ == '__main__':
    unittest.main()
