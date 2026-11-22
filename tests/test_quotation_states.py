"""Quotation states and de-duplication in the Human Evidence Appendix.

Independently authored for this release candidate. Every manuscript line,
table, value, appraisal and verifier reply below is invented; the hurdle-step
case reproduces only the *structure* of a reported problem (an AI quotation
that leaves out one column of a table row), with made-up numbers. No model
is called; no manuscript, review or model output is used.
"""
import copy
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
import print_view  # noqa: E402
import quote_match as qm  # noqa: E402
import review_links as rl  # noqa: E402
import review_store as store  # noqa: E402
import server  # noqa: E402
import source_verification as sv  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from test_release import Isolated  # noqa: E402

EXACT, RELATED, MISSING = qm.STATE_LABELS[qm.EXACT], qm.STATE_LABELS[qm.RELATED], qm.STATE_LABELS[qm.NOT_LOCATED]

# Invented functional-screen table (structure only; values are made up).
TABLE = ('[Page 6]\n[TABLE_START]\nSource: inline_markdown\nLabel: Table 4\n'
         '| Test | Week 0 | Week 8 | p |\n'
         '| Hurdle step | 2.14 ± 0.6318 | 2.37 ± 0.5102 | 0.0412 |\n'
         '| Inline lunge | 2.02 ± 0.4411 | 2.25 ± 0.3907 | 0.0236 |\n'
         '[TABLE_END]\n')
PROSE = ('[Page 2]\nTwenty-four volunteers from a fictional rowing club completed every session.\n'
         'The warm-up lasted ten minutes before each fictional test battery.\n'
         '[Page 5]\nThe warm-up lasted ten minutes before each fictional test battery.\n'
         'Mean change in the experimental group was -0.5 points (95% CI -0.9 to -0.1).\n'
         'The control group post-test score was 12.3 ± 1.2 units.\n')
MANUSCRIPT = PROSE + TABLE
SOURCES = {'fictional-trial.pdf': MANUSCRIPT}

HURDLE_QUOTE = 'Hurdle step 2.37 ± 0.5102,'


def report_with(concerns):
    lines = ['# Overall synopsis', 'A fictional appraisal for software testing.', '',
             '# Directly supported concerns']
    for concern, evidence in concerns:
        lines += [f'* **Concern:** {concern}', f'* **Evidence:** "{evidence}"']
    return '\n'.join(lines) + '\n'


def make_assessor(replies):
    """replies: label -> dict(quote=..., evidence=[(quote, role)], verdict=...)."""
    def assessor(*, prompt, schema, max_tokens):
        labels = schema['properties']['items']['items']['properties']['label']['enum']
        items = []
        for label in labels:
            r = replies.get(label, {})
            items.append(dict(label=label, verdict=r.get('verdict', 'unresolved'), quote=r.get('quote', ''),
                              reason='Scripted fixture reply.', correction='', surviving_point='',
                              duplicate_of='', reviewer_check='',
                              evidence=[dict(quote=q, role=role) for q, role in r.get('evidence', [])]))
        return {'items': items}
    return assessor


def build(concerns, replies=None, sources=SOURCES, intermediate=None, save_sources=True):
    report = report_with(concerns)
    verification = sv.verify_report(report, sources, make_assessor(replies or {}), budget=100000,
                                     unexamined=[]).as_dict()
    cards = ec.build_cards(verification, sources)
    links = rl.build_links(report, verification)
    md = appendix_view.render(report, links, cards, None, 'fixture-time', intermediate=intermediate,
                              sources=sources if save_sources else None)
    return md, cards, report, verification


def entry(md, fid):
    return re.search(r'## ' + fid + r' — .*?\n(.*?)(?=\n## )', md, re.S).group(1)


class Classifier(unittest.TestCase):
    def setUp(self):
        self.m = qm.Manuscript(SOURCES)

    def state(self, quote):
        return qm.classify(quote, self.m)

    def test_exact_match_reports_the_normalisation_it_relied_on(self):
        r = self.state('twenty-four volunteers from a fictional rowing club completed every session.')
        self.assertEqual(r.state, qm.EXACT)
        self.assertEqual(r.normalised, [qm.RULE_NAMES['case']])
        styled = self.state('Mean change in the experimental group was −0.5 points (95% CI −0.9 to −0.1)')
        self.assertEqual(styled.state, qm.EXACT)
        self.assertIn(qm.RULE_NAMES['styles'], styled.normalised)

    def test_whitespace_and_line_breaks_are_normalised(self):
        r = self.state('every session.\nThe   warm-up lasted ten minutes')
        self.assertEqual(r.state, qm.EXACT)

    def test_signs_decimal_places_and_symbols_are_compared_exactly(self):
        for quote in ('Mean change in the experimental group was 0.5 points',
                      'Mean change in the experimental group was -0.50 points',
                      'The control group post-test score was 12.3 ± 1.20 units',
                      'The control group post-test score was 12.3 = 1.2 units'):
            self.assertEqual(self.state(quote).state, qm.NOT_LOCATED, quote)

    def test_numbers_inside_longer_numbers_do_not_match(self):
        self.assertEqual(self.state('The control group post-test score was 12.3 ± 1.').state, qm.NOT_LOCATED)

    def test_table_row_with_extra_columns_is_related_not_exact(self):
        r = self.state(HURDLE_QUOTE)
        self.assertEqual(r.state, qm.RELATED)
        self.assertEqual(r.omitted, ['2.14 ± 0.6318'])
        self.assertEqual(r.locations[0].location, 'Table 4, p. 6')
        self.assertIn('which column, group and time point', r.check)

    def test_whole_row_quoted_without_separators_is_exact(self):
        r = self.state('Hurdle step 2.14 ± 0.6318 2.37 ± 0.5102 0.0412')
        self.assertEqual(r.state, qm.EXACT)
        self.assertIn(qm.RULE_NAMES['punctuation'], r.normalised)

    def test_repeated_numbers_in_different_tables_are_not_attributed(self):
        two = {'a.pdf': '[TABLE_START]\nLabel: Table 1\n| Sprint 10 m | 3.45 ± 0.12 |\n[TABLE_END]\n'
                        '[TABLE_START]\nLabel: Table 2\n| Sprint 20 m | 3.61 ± 0.12 |\n'
                        '| Sprint 10 m | 3.45 ± 0.12 | retest |\n[TABLE_END]\n'}
        m = qm.Manuscript(two)
        wrong_condition = qm.classify('Sprint 20 m 3.45 ± 0.12', m)
        self.assertEqual(wrong_condition.state, qm.NOT_LOCATED)
        ambiguous = qm.classify('Sprint 10 m 0.12', m)
        self.assertEqual(ambiguous.state, qm.NOT_LOCATED)
        self.assertIn('2 lines', ambiguous.reason)

    def test_incorrect_group_label_or_occasion_is_not_located(self):
        self.assertEqual(self.state('The experimental group post-test score was 12.3 ± 1.2 units').state,
                         qm.NOT_LOCATED)
        self.assertEqual(self.state('The control group pre-test score was 12.3 ± 1.2 units').state,
                         qm.NOT_LOCATED)
        self.assertEqual(self.state('Inline lunge 2.37 ± 0.5102').state, qm.NOT_LOCATED)

    def test_numbers_alone_are_never_authenticated(self):
        r = self.state('2.37 ± 0.5102')
        self.assertEqual(r.state, qm.NOT_LOCATED)
        self.assertIn('only of numbers', r.reason)

    def test_repeated_passage_lists_every_occurrence(self):
        r = self.state('The warm-up lasted ten minutes before each fictional test battery.')
        self.assertEqual(r.state, qm.EXACT)
        self.assertEqual(r.occurrences, 2)
        self.assertEqual([loc.location for loc in r.locations], ['p. 2', 'p. 5'])

    def test_short_phrases_need_a_single_occurrence(self):
        self.assertEqual(self.state('fictional rowing club').state, qm.EXACT)
        self.assertEqual(self.state('fictional test battery').state, qm.NOT_LOCATED)

    def test_ellipsis_is_never_exact(self):
        r = self.state('Twenty-four volunteers ... completed every session')
        self.assertNotEqual(r.state, qm.EXACT)

    def test_prose_numbers_must_stay_attached_to_their_words(self):
        # -0.1 is on the line, but not next to "was" as the quotation places it.
        self.assertEqual(self.state('The experimental group was -0.1').state, qm.NOT_LOCATED)
        # Leaving out a word keeps the number beside "was": related, with the omission shown.
        related = self.state('The control group score was 12.3 ± 1.2 units')
        self.assertEqual(related.state, qm.RELATED)
        self.assertEqual(related.omitted, ['post-test'])
        self.assertIn('leaves out changes its meaning', related.check)

    def test_classification_is_deterministic(self):
        a = [vars(self.state(q)) for q in (HURDLE_QUOTE, 'fictional rowing club', 'not in the text at all here')]
        b = [vars(qm.classify(q, qm.Manuscript(SOURCES))) for q in (HURDLE_QUOTE, 'fictional rowing club',
                                                                  'not in the text at all here')]
        self.assertEqual(repr(a), repr(b))


class Deduplication(unittest.TestCase):
    QUOTE = 'Twenty-four volunteers from a fictional rowing club completed every session.'

    def test_identical_passage_cited_by_several_components_is_shown_once(self):
        md, *_ = build([('Attrition is not reported.', self.QUOTE)],
                       {'C1': dict(quote=self.QUOTE, verdict='supported',
                                   evidence=[(self.QUOTE.rstrip('.'), 'supports')])})
        text = entry(md, 'C1')
        self.assertEqual(text.count('> Twenty-four volunteers'), 1)
        self.assertIn('quoted by the review item as its evidence; cited by the verifier, which reads it '
                      'as supporting the finding', text)

    def test_distinct_locations_and_similar_passages_stay_separate(self):
        md, *_ = build([('Two passages are cited.', self.QUOTE)],
                       {'C1': dict(evidence=[('The warm-up lasted ten minutes before each fictional test battery.', 'supports'),
                                             ('Twenty-four volunteers from a fictional rowing club completed every', 'qualifies')])})
        text = entry(md, 'C1')
        # The full sentence and its shorter, overlapping version are different extents: not merged.
        self.assertEqual(text.count('> Twenty-four volunteers'), 2)
        self.assertIn('occurs 2 times', text)
        self.assertIn('Also at: p. 5 in fictional-trial.pdf', text)

    def test_unlocated_duplicates_merge_only_on_identical_wording(self):
        md, *_ = build([('A claim.', 'Thirty volunteers attended the fictional sessions.')],
                       {'C1': dict(quote='Thirty volunteers attended the fictional sessions.',
                                   evidence=[('Thirty volunteers attended the fictional session.', 'supports')])})
        text = entry(md, 'C1')
        self.assertEqual(text.count('> Thirty volunteers attended the fictional sessions.'), 1)
        self.assertEqual(text.count('> Thirty volunteers attended the fictional session.'), 1)


class HurdleStepReproduction(unittest.TestCase):
    def test_partial_row_quotation_is_shown_as_related_passage(self):
        md, cards, report, _ = build([('The Week 8 hurdle-step score is reported without its change.', HURDLE_QUOTE)],
                                     {'C1': dict(quote=HURDLE_QUOTE.rstrip(','), verdict='supported',
                                                 evidence=[(HURDLE_QUOTE.rstrip(','), 'supports')])})
        text = entry(md, 'C1')
        self.assertIn('**' + EXACT + ':** none.', text)
        self.assertIn('**' + RELATED + '**', text)
        self.assertIn('Table 4, p. 6 in fictional-trial.pdf', text)
        self.assertIn('AI quotation (AI-written; not manuscript text):', text)
        self.assertIn('> Hurdle step 2.37 ± 0.5102,', text)
        self.assertIn('> Hurdle step \\| 2.14 ± 0.6318 \\| 2.37 ± 0.5102 \\| 0.0412', text)
        self.assertIn('left out by the quotation: “2.14 ± 0.6318”', text)
        self.assertIn('> \\| Test \\| Week 0 \\| Week 8 \\| p \\|', text)
        self.assertIn('not evidence that the AI\'s statistical interpretation is correct', text)
        self.assertEqual(text.count('> Hurdle step 2.37'), 1)   # the two AI citations merge
        self.assertIn('same quotation with different punctuation', text)

    def test_evidence_cards_are_not_changed_by_the_appendix(self):
        report = report_with([('A concern.', HURDLE_QUOTE)])
        verification = sv.verify_report(report, SOURCES, make_assessor({}), budget=100000, unexamined=[]).as_dict()
        cards = ec.build_cards(verification, SOURCES)
        before = copy.deepcopy(cards)
        appendix_view.render(report, rl.build_links(report, verification), cards, None, 't', sources=SOURCES)
        self.assertEqual(cards, before)
        self.assertEqual(cards, ec.build_cards(verification, SOURCES))


class Provenance(unittest.TestCase):
    QUOTE = 'The rowers reported no soreness after any fictional session.'

    def test_unlocated_quotation_with_and_without_intermediate_text(self):
        unsaved, *_ = build([('Soreness is unaddressed.', self.QUOTE)])
        self.assertIn(MISSING, entry(unsaved, 'C1'))
        self.assertIn('saved only for reviews run in Development mode', entry(unsaved, 'C1'))
        self.assertIn('does not show that the manuscript lacks the information', entry(unsaved, 'C1'))
        found, *_ = build([('Soreness is unaddressed.', self.QUOTE)],
                          intermediate=[('the AI file summary for fictional-trial.pdf', 'Notes: ' + self.QUOTE)])
        self.assertIn('It appears verbatim in the AI file summary for fictional-trial.pdf', entry(found, 'C1'))

    def test_card_and_appendix_both_reject_an_altered_sign(self):
        quote = 'Mean change in the experimental group was 0.5 points'
        md, cards, *_ = build([('The change is positive.', quote)])
        self.assertFalse(any(p['status'] == 'located' for c in cards['cards'] for p in c['evidence']))
        self.assertNotIn('The Evidence Card lists this quotation as located', entry(md, 'C1'))
        exact_quote = 'Mean change in the experimental group was -0.5 points'
        exact_md, exact_cards, *_ = build([('The change is positive.', exact_quote)])
        self.assertTrue(any(p['status'] == 'located' for c in exact_cards['cards'] for p in c['evidence']))
        self.assertIn(EXACT, entry(exact_md, 'C1'))
        self.assertNotIn('does not list this quotation as located', entry(exact_md, 'C1'))
        self.assertIn(MISSING, entry(md, 'C1'))


class SafeOutput(unittest.TestCase):
    def test_markup_in_manuscript_and_quotation_is_escaped(self):
        sources = {'x.pdf': '[TABLE_START]\nLabel: Table 9\n| <b>Grip</b> *left* | 31.2 ± 4.1 | 33.0 ± 3.9 |\n[TABLE_END]\n'}
        quote = '<b>Grip</b> *left* 33.0 ± 3.9'
        md, *_ = build([('Grip <script>x</script>.', quote)], sources=sources)
        text = entry(md, 'C1')
        self.assertIn(RELATED, text)
        self.assertIn('\\<b\\>Grip\\</b\\> \\*left\\*', text)
        html = print_view.render_appendix(md, {'job_id': 'ab12cd34ef56', 'filename': 'x.pdf', 'printed_at': 't'})
        self.assertNotIn('<b>Grip', html)
        self.assertNotIn('<script>x', html)


class SameContentEverywhere(Isolated):
    def test_tab_markdown_and_print_page_carry_the_same_states(self):
        report = report_with([('The Week 8 hurdle-step score is reported without its change.', HURDLE_QUOTE),
                              ('Soreness is unaddressed.', Provenance.QUOTE)])
        verification = sv.verify_report(report, SOURCES, make_assessor({}), budget=100000, unexamined=[]).as_dict()
        cards = ec.build_cards(verification, SOURCES)
        job = fx.job(report=report, text=MANUSCRIPT, sources=SOURCES, verification_sources=SOURCES,
                     source_verification={'verification': verification})
        store.save_completed(self.jid, job, cards=cards, manuscript_sha256=None)
        with TestClient(server.app) as client:
            tab = client.get('/api/review/appendix/' + self.jid).json()
            original = client.get('/api/review/appendix/' + self.jid + '?version=original').json()
            page = client.get(f'/review/{self.jid}/print/appendix').text
        md = tab['appendix']
        self.assertEqual(tab['presentation'], 'current')
        self.assertEqual(original['presentation'], 'original')
        self.assertNotIn(RELATED, original['appendix'])     # the stored original is unchanged
        for label in (RELATED, MISSING):
            self.assertIn(label, md)
            self.assertIn(label, page)
        for text in ('Hurdle step 2.37 ± 0.5102,', '2.14 ± 0.6318', Provenance.QUOTE):
            self.assertIn(text, md.replace('\\', ''))
            self.assertIn(text, page)


class HistoricalWithoutManuscriptText(Isolated):
    def test_saved_review_without_text_uses_labelled_card_results(self):
        report = report_with([('Soreness is unaddressed.', Provenance.QUOTE)])
        verification = sv.verify_report(report, SOURCES, make_assessor({}), budget=100000, unexamined=[]).as_dict()
        cards = ec.build_cards(verification, SOURCES)
        job = fx.job(report=report, text='', sources={}, verification_sources={},
                     source_verification={'verification': verification}, evidence_cards_snapshot=cards)
        store.save_completed(self.jid, job, cards=cards, manuscript_sha256=None)
        with TestClient(server.app) as client:
            md = client.get('/api/review/appendix/' + self.jid).json()['appendix']
        self.assertIn('The manuscript text was not saved with this review', md)
        self.assertNotIn(RELATED, md.split('## C. What')[0])


if __name__ == '__main__':
    unittest.main()
