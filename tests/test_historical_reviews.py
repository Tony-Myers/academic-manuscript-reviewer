"""Saved (historical) reviews opened by the current application.

Independently authored for this release candidate. All reviews are invented
materials-bench texts written here or in fixtures.py; "older format" reviews
are synthetic records shaped like earlier application output (an appendix from
the earlier parser, a bold-marker appraisal, a store without dispositions).
No model is called; no manuscript, review or model output is used.
"""
import hashlib
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'app'))
sys.path.insert(0, str(ROOT / 'tests'))
import fixtures as fx  # noqa: E402
import review_store as store  # noqa: E402
import server  # noqa: E402
import source_verification as sv  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from test_release import Isolated  # noqa: E402

# An appraisal written with bold markers, as some model output is. The earlier
# appendix parser found no concerns or questions in reports like this.
BOLD_REPORT = '''# Overall synopsis
A **fictional** bench exercise for software testing.

# Major strengths
* **Strength:** The reference tile was checked before each batch.
* **Evidence:** "A reference tile was rescanned before every batch."

# Directly supported concerns
* **Concern:** The calibration log does not identify instrument serials.
* **Evidence:** The example does not specify instrument serials.
* **Concern:** The chamber temperature was not logged during the bench run.
* **Evidence:** "The chamber temperature was not logged."

# Verification prompts
* **Check:** Confirm chamber temperature control against the instrument log.
* **Reason:** Drift could affect the synthetic signal readings.
'''

# What the earlier application stored for such a review (synthetic).
OLD_APPENDIX = ('# Human Evidence Appendix\n\nNo substantive concerns or verification questions were '
                'identified for evidence-card rendering.\n\n## Chunk-level candidates not carried into '
                'the review\n\n- [bench.pdf, chunk 2; questions raised by this chunk] Was the fictional '
                'violet tile recalibrated mid-run?\n')

ACCOUNTING = {'distinct': 3, 'total': 3, 'reflected': 1, 'reflected_in_removed_item': 0,
              'not_carried_forward': 2, 'threshold': 0.5, 'records': [
                  {'status': 'not_carried_forward', 'text': 'Was the fictional violet tile recalibrated mid-run?',
                   'section': 'questions raised by this chunk', 'source_name': 'bench.pdf', 'chunk_ids': [2],
                   'item': '', 'nearest': '', 'overlap': 0.1},
                  {'status': 'not_carried_forward', 'text': 'The amber batch used an invented reference card.',
                   'section': 'missing or unclear', 'source_name': 'bench.pdf', 'chunk_ids': [3],
                   'item': '', 'nearest': '', 'overlap': 0.2},
                  {'status': 'reflected', 'text': 'Instrument serials are missing.', 'section': 'missing or unclear',
                   'source_name': 'bench.pdf', 'chunk_ids': [1], 'item': 'C1', 'nearest': 'C1', 'overlap': 0.8}]}

REVISED = 'State the serial of every instrument; the *p* < 0.05 claim needs [Table 2] checked.'


def digests(folder):
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.iterdir() if p.is_file()}


class HistoricalReviews(Isolated):
    def save_old_format(self, *, with_dispositions=True, accounting=ACCOUNTING):
        verification = sv.verify_report(BOLD_REPORT, fx.SOURCES, fx.assessor, budget=100000,
                                        unexamined=[]).as_dict()
        cards = __import__('evidence_cards').build_cards(verification, fx.SOURCES)
        stored_verification = verification if with_dispositions else {'status': 'completed'}
        job = fx.job(report=BOLD_REPORT, appendix=OLD_APPENDIX,
                     source_verification={'verification': stored_verification,
                                          'candidate_accounting': accounting})
        return store.save_completed(self.jid, job, cards=cards, manuscript_sha256=None)

    def appendix(self, client, version=None):
        url = '/api/review/appendix/' + self.jid + ('?version=' + version if version else '')
        response = client.get(url)
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.headers.get('cache-control'), 'no-store')
        return response.json()

    # 1, 3, 8: current format, concerns and questions, unlocated evidence
    def test_current_format_review_gets_concise_appendix(self):
        self.save()
        with TestClient(server.app) as client:
            current = self.appendix(client)
            original = self.appendix(client, 'original')
        md = current['appendix']
        self.assertEqual(current['presentation'], 'current')
        self.assertTrue(current['original_available'])
        for heading in ('## C1 — Concern', '## C2 — Concern', '## Q1 — Verification question'):
            self.assertIn(heading, md)
        # The fixture's five-word quotation occurs once: authenticated here, and the
        # difference from the Evidence Card (which needs six words) is stated, not hidden.
        self.assertIn('**Exact quotation authenticated** (verbatim manuscript text', md)
        self.assertIn('The Evidence Card does not list this quotation as located (too short', md)
        self.assertIn('> Every tile was scanned twice.', md)
        self.assertIn('The AI verifier disputed this finding', md)  # C2 in the fixture
        self.assertEqual(original['presentation'], 'original')
        self.assertEqual(original['appendix'], fx.job()['appendix'])

    # 2, 5, 9: older stored format, intermediate observations, stored vs rendered
    def test_older_review_shows_its_concerns_and_keeps_its_original(self):
        self.save_old_format()
        folder = store.session_dir(self.jid)
        before = digests(folder)
        with TestClient(server.app) as client:
            current = self.appendix(client)
            original = self.appendix(client, 'original')
            links = client.get('/api/review/' + self.jid + '/links').json()
        md = current['appendix']
        self.assertNotIn('No substantive concerns', md)
        for heading in ('## C1 — Concern', '## C2 — Concern', '## Q1 — Verification question'):
            self.assertIn(heading, md)
        self.assertIn('The chamber temperature was not logged during the bench run.', md)
        self.assertIn('Presentation generated by the current application', md)
        self.assertIn('original appendix', md)
        self.assertIn('## B. Additional observations from the initial reading (not independently verified)', md)
        self.assertIn('2 observation(s)', md)
        self.assertNotIn('violet tile recalibrated', md)          # summarised, not listed
        self.assertEqual(original['appendix'], OLD_APPENDIX)        # stored output, unchanged
        self.assertIn('violet tile recalibrated', original['appendix'])
        self.assertEqual(before, digests(folder))                  # nothing on disk changed
        appendix_ids = {f['appendix_id'] for f in links['findings'] if f.get('appendix_id')}
        self.assertEqual(appendix_ids, {'C1', 'C2', 'Q1'})          # appraisal and cards now link to it

    # 4
    def test_appraisal_without_concerns(self):
        report = '# Overall synopsis\nFictional.\n\n# Major strengths\n* Strength: The tile was checked.\n'
        job = fx.job(report=report)
        store.save_completed(self.jid, job, cards=fx.cards(), manuscript_sha256=None)
        with TestClient(server.app) as client:
            md = self.appendix(client)['appendix']
        self.assertIn('The final appraisal contains no concerns or verification questions.', md)
        self.assertIn('No record of initial-reading observations was saved', md)

    # 8: a finding with no Evidence Card is not given invented evidence
    def test_finding_without_a_card_says_so(self):
        report = fx.REPORT.replace('# Verification prompts',
                                   '* Concern: An invented fourth issue with no card.\n\n# Verification prompts')
        store.save_completed(self.jid, fx.job(report=report), cards=fx.cards(), manuscript_sha256=None)
        with TestClient(server.app) as client:
            md = self.appendix(client)['appendix']
        entry = re.search(r'## C3 — Concern\n(.*?)(?=\n## )', md, re.S).group(1)
        self.assertIn('No Evidence Card corresponds to this finding', entry)

    # 6, 7: historical access to both exports; amendments preserved; decisions unchanged
    def test_older_review_has_both_decision_exports(self):
        manifest = self.save_old_format()
        decisions = {'C1': {'decision': 'revise', 'note': REVISED},
                     'C2': {'decision': 'dismiss', 'note': 'Covered by the bench notes.'},
                     'S1': {'decision': 'retain', 'note': ''}}
        with TestClient(server.app) as client:
            self.assertEqual(client.put('/api/review/' + self.jid + '/decisions', json={
                'card_fingerprint': manifest['card_fingerprint'], 'decisions': decisions}).status_code, 200)
            stored = client.get('/api/review/' + self.jid + '/decisions').json()
            page = client.get('/review/evidence-cards/' + self.jid)
            concise = client.post('/api/review/' + self.jid + '/decisions-summary.md',
                                  json={'decisions': stored['decisions']})
            audit = client.post('/api/review/' + self.jid + '/decisions.md',
                                json={'decisions': stored['decisions']})
            after = client.get('/api/review/' + self.jid + '/decisions').json()
        self.assertEqual(stored, after)
        self.assertIn('Export reviewer summary (.md)', page.text)
        self.assertIn('Export full audit record (.md)', page.text)
        self.assertNotIn('Export reviewer decisions (.md)', page.text)
        self.assertEqual(page.headers.get('cache-control'), 'no-store')
        text = re.sub(r'\\(.)', r'\1', concise.text)
        self.assertIn(REVISED, text)
        self.assertIn('Original AI observation, for reference only', text)
        self.assertIn('P1', text.split('## Awaiting a decision')[1])  # undecided, listed as outstanding
        self.assertIn('Covered by the bench notes.', text)
        self.assertIn('Disputed by the AI verifier', text.split('## Dismissed findings')[1])  # C2 dispute kept
        self.assertEqual(audit.status_code, 200)
        self.assertIn('full audit record', audit.text)

    # 2: an older store holding the card snapshot but not its dispositions
    def test_card_snapshot_without_dispositions_still_serves_cards_and_exports(self):
        self.save_old_format(with_dispositions=False)
        with TestClient(server.app) as client:
            page = client.get('/review/evidence-cards/' + self.jid)
            concise = client.post('/api/review/' + self.jid + '/decisions-summary.md',
                                  json={'decisions': {'C1': {'decision': 'retain', 'note': ''}}})
            md = self.appendix(client)['appendix']
        self.assertEqual(page.status_code, 200)
        self.assertIn('Export reviewer summary (.md)', page.text)
        self.assertEqual(concise.status_code, 200, concise.text)
        self.assertIn('## C1 — Concern', md)

    def test_interface_is_served_uncached_with_original_download(self):
        with TestClient(server.app) as client:
            page = client.get('/')
        self.assertEqual(page.headers.get('cache-control'), 'no-store')
        self.assertIn('Download original appendix .md', page.text)
        self.assertIn("version=original", page.text)

    def test_new_reviews_store_renamed_observation_section(self):
        stored = sv.format_candidate_appendix(ACCOUNTING)
        self.assertIn('Additional observations from the initial reading (not independently verified)', stored)
        self.assertNotIn('Chunk-level candidates not carried into the review', stored)
        self.assertIn('violet tile recalibrated', stored)  # the full list is kept for audit


if __name__ == '__main__':
    unittest.main()
