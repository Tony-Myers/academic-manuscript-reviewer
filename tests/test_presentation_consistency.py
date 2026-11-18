"""Consistency between the appraisal, the Evidence Cards and the appendix.

Independently authored for this release candidate. The reports are short
invented materials-bench texts, written here; verifier records are
hand-written dictionaries. No model is called and no manuscript, review or
model output is used.
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'app'))
import decisions_report as dr  # noqa: E402
import evidence_cards as ec  # noqa: E402
import human_evidence_appendix as hea  # noqa: E402
import reviewer_presentation as presentation  # noqa: E402
import source_verification as sv  # noqa: E402

BASE = ('# Overall synopsis\nFictional bench exercise.\n\n'
        '# {strengths}\n* Strength: The reference tile was checked before each batch.\n\n'
        '# {concerns}\n{concern} The instrument serial numbers are not given.\n'
        '* Evidence: Not specified in the fictional text.\n'
        '{concern} The chamber temperature was not logged.\n\n'
        '# {prompts}\n{check} Confirm the chamber log against the bench notes.\n')

VARIANTS = {
    'plain': ('Major strengths', 'Directly supported concerns', '* Concern:', 'Verification prompts', '* Check:'),
    'bold markers': ('Major strengths', 'Directly supported concerns', '* **Concern:**',
                     'Verification prompts', '* **Check:**'),
    'bold headings': ('**Major strengths**', '**Directly supported concerns**', '* Concern:',
                      '**Verification prompts**', '* Check:'),
    'suffixed heading': ('Major strengths', 'Directly supported concerns (two items)', '* Concern:',
                         'Verification prompts', '* Check:'),
    'unbulleted': ('Major strengths', 'Directly supported concerns', 'Concern:', 'Verification prompts', 'Check:'),
}


class AppendixMatchesCards(unittest.TestCase):
    def test_appendix_reads_the_same_items_as_the_cards(self):
        for name, (strengths, concerns, concern, prompts, check) in VARIANTS.items():
            report = BASE.format(strengths=strengths, concerns=concerns, concern=concern,
                                 prompts=prompts, check=check)
            card_items = [item for item in sv.extract_items(report) if item.kind != 'strength']
            appendix = hea.extract_final_findings(report)
            with self.subTest(name):
                self.assertEqual([i.label for i in card_items if i.kind == 'concern'],
                                 [f['finding_id'] for f in appendix if f['review_status'] == 'concern'])
                self.assertEqual(len([i for i in card_items if i.kind == 'prompt']),
                                 len([f for f in appendix if f['review_status'] == 'verification_question']))
                self.assertEqual(appendix[0]['text'], 'The instrument serial numbers are not given.')
                rendered = hea.render_human_evidence_appendix(hea.build_evidence_cards(report))
                self.assertNotIn('No concerns or verification questions were found', rendered)

    def test_empty_appendix_explains_what_it_covers(self):
        rendered = hea.render_human_evidence_appendix([])
        self.assertIn('Strengths are not included', rendered)
        self.assertIn('Evidence Cards', rendered)


def card_for(verdict, *, quote='', correction='', reason='', duplicate_of=''):
    disposition = {'label': 'S1', 'kind': 'strength',
                   'original': '* Strength: Baseline groups did not differ, so the groups were equivalent.',
                   'verdict': verdict, 'reason': reason, 'quote': quote, 'correction': correction,
                   'surviving_point': '', 'duplicate_of': duplicate_of, 'reviewer_check': '', 'evidence': []}
    sources = {'bench.txt': 'Synthetic bench text with no matching sentence at all.'}
    outcome = sv.decide([sv.Item('S1', 'strength', 0, 1, disposition['original'])],
                        [disposition], sources)['S1']
    disposition.update(outcome=outcome.outcome, note=outcome.note, quote_located=outcome.quote_located)
    if duplicate_of:
        disposition['outcome'] = 'merged_into'
    return ec.build_card(disposition, sources)


class DisputedFindingsAreFlagged(unittest.TestCase):
    def test_withheld_correction_is_flagged_and_shown_for_human_judgement(self):
        card = card_for('correct', quote='A sentence the fictional text does not contain at all.',
                        correction='A non-significant comparison does not show equivalence.')
        self.assertEqual(card['provenance']['application_action'], 'kept_unresolved')
        self.assertTrue(presentation.disputed(card))
        items = presentation.context_items(card)
        self.assertTrue(any('disputed this finding' in item and 'does not show equivalence' in item
                            for item in items), items)
        html = ec.render_card(card)
        self.assertIn('Disputed by the AI verifier', html)
        self.assertIn('data-warn="1"', html)
        self.assertIn('Baseline groups did not differ', html)  # the original finding is unchanged
        exported = dr.render_markdown({'cards': [card]}, {}, {})
        self.assertIn('does not show equivalence', exported)

    def test_objection_is_flagged(self):
        card = card_for('reject', reason='The cited passage does not support equivalence.')
        self.assertTrue(presentation.disputed(card))
        self.assertIn('Disputed by the AI verifier', ec.render_card(card))

    def test_supported_and_unresolved_items_are_not_flagged(self):
        for verdict in ('supported', 'unresolved', ''):
            card = card_for(verdict, reason='Fixture reason.')
            with self.subTest(verdict=verdict):
                self.assertFalse(presentation.disputed(card))
                self.assertNotIn('Disputed by the AI verifier', ec.render_card(card))

    def test_summary_counts_disputed_items(self):
        cards = [card_for('correct', correction='Fixture correction.'), card_for('supported')]
        self.assertIn('<strong>1</strong>disputed by the AI verifier', ec._summary_html(cards))


if __name__ == '__main__':
    unittest.main()
