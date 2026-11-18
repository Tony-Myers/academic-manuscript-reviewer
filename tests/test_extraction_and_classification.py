"""Text clean-up, method classification and the appraisal prompt after the
removal of document-specific rules.

Independently authored for this release candidate. Every sentence, variable
name and value below is synthetic. No model is called; no manuscript, review
or model output is used.
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'app'))
import review_pipeline as rp  # noqa: E402

MC = rp.MethodClass


class GeneralExtractionRepairs(unittest.TestCase):
    clean = staticmethod(rp.clean_ocr_artifacts)
    tidy = staticmethod(rp.clean_extracted_evidence_text)

    def test_dollar_decimal_between_digits_is_repaired(self):
        self.assertEqual(self.clean('mean 0$512 and 12$5 s'), 'mean 0.512 and 12.5 s')

    def test_names_containing_a_dollar_are_left_alone(self):
        self.assertEqual(self.clean('the synthetic index IDX$5R rose'), 'the synthetic index IDX$5R rose')
        self.assertEqual(self.clean('a cost of $5 per unit'), 'a cost of $5 per unit')

    def test_equals_read_as_z_only_before_a_number(self):
        self.assertEqual(self.clean('r Z 0.40 and p Z .03 and F Z 4.2'), 'r = 0.40 and p = .03 and F = 4.2')
        self.assertEqual(self.clean('r Z −0.21'), 'r = −0.21')
        for untouched in ('factor F Z was retained', 'a p Z-score', 'variables r Z and Y'):
            self.assertEqual(self.clean(untouched), untouched)

    def test_font_specific_cid_codes_are_not_mapped(self):
        self.assertEqual(self.clean('value (cid:3)0.5 (cid:2) 0.1'), 'value (cid:3)0.5 (cid:2) 0.1')

    def test_nul_becomes_space(self):
        self.assertEqual(self.clean('a\x00b'), 'a b')

    def test_split_physiological_subscript_is_joined_without_losing_brackets(self):
        self.assertEqual(self.tidy('VO 2max rose'), 'VO2max rose')
        self.assertEqual(self.tidy('VO ₂peak rose'), 'VO2peak rose')
        self.assertEqual(self.tidy('(VO2max) was measured'), '(VO2max) was measured')
        self.assertEqual(self.tidy('VO 2 was recorded'), 'VO 2 was recorded')

    def test_spacing_repairs_keep_case_and_characters(self):
        self.assertEqual(self.tidy('Ln (height) and ln (mass)'), 'Ln(height) and ln(mass)')
        self.assertEqual(self.tidy('kg −1 and min −1'), 'kg−1 and min−1')
        self.assertEqual(self.tidy('a drop of 5 min -1 h'), 'a drop of 5 min -1 h')

    def test_former_document_specific_rewrites_no_longer_apply(self):
        for text in ('children at age 2 years', 'see page 2', 'an average 25 points',
                     'Age 2 entered the model', 'flow of 3 L. min−1', 'body fat % fell',
                     'BF % fell', 'ln(mass(g)) was used', 'a Cyc le test'):
            self.assertEqual(self.tidy(text), text)
        self.assertEqual(self.tidy('lnfvc rose', domain='exercise_physiology'), 'lnfvc rose')

    def test_hyphenation_repair_keeps_compounds_and_suspended_hyphens(self):
        self.assertEqual(self.tidy('log- transformed and out- of- sample'), 'log-transformed and out-of-sample')
        self.assertEqual(self.tidy('statis- tical model'), 'statistical model')
        self.assertEqual(self.tidy('pre- and post-test scores'), 'pre- and post-test scores')
        self.assertEqual(self.tidy('short- or long-term'), 'short- or long-term')


class MethodClassification(unittest.TestCase):
    def classes(self, text):
        return rp.detect_method_classes(text)

    def test_ancova_and_log_transformation_alone_are_not_allometric(self):
        found = self.classes('An ANCOVA adjusted the synthetic outcome for baseline values.')
        self.assertIn(MC.FREQUENTIST_ANOVA, found)
        self.assertNotIn(MC.FREQUENTIST_ALLOMETRIC, found)
        found = self.classes('The outcome was log-transformed before linear regression.')
        self.assertNotIn(MC.FREQUENTIST_ALLOMETRIC, found)
        self.assertIn(MC.FREQUENTIST_REGRESSION, found)

    def test_allometric_scaling_is_still_recognised(self):
        self.assertIn(MC.FREQUENTIST_ALLOMETRIC, self.classes('Strength was scaled with an allometric model.'))
        self.assertIn(MC.FREQUENTIST_ALLOMETRIC, self.classes('A power-law scaling model was fitted.'))

    def test_profile_models_by_method_name_not_by_abbreviation(self):
        self.assertIn(MC.FREQUENTIST_PROFILE_MODEL,
                      self.classes('A force-velocity profile was fitted for each synthetic athlete.'))
        self.assertIn(MC.FREQUENTIST_PROFILE_MODEL,
                      self.classes('The torque-cadence relationship was described by a fitted model.'))
        self.assertNotIn(MC.FREQUENTIST_PROFILE_MODEL,
                         self.classes('Plasma Tmax and Pmax were tabulated after a second-order polynomial fit.'))

    def test_model_block_nesting_in_general_terms(self):
        self.assertEqual(rp.classify_model_block(
            'A multinomial logit model was fitted with observations nested within participants.'),
            MC.MULTILEVEL_MCMC)
        self.assertEqual(rp.classify_model_block(
            'A multinomial logit model with cross-classified random effects.'), MC.CROSS_CLASSIFIED_MCMC)
        self.assertEqual(rp.classify_model_block(
            'MCMC estimation in MLwiN; observations nested within schools.'), MC.MULTILEVEL_MCMC)
        self.assertNotEqual(rp.classify_model_block(
            'Responses were classified by age and sex in a multinomial logit model.'), MC.CROSS_CLASSIFIED_MCMC)

    def test_design_model_and_analysis_stay_distinct(self):
        # A design word does not decide the statistical model class.
        found = self.classes('A cluster randomised trial analysed with an ANCOVA.')
        self.assertEqual(found, [MC.FREQUENTIST_ANOVA])
        features = rp.detect_methodological_features('A cluster randomised trial analysed with an ANCOVA.')
        self.assertIn(rp.MethodologicalFeature.CLUSTER_RANDOMISED, features)


class IntroductionParagraphs(unittest.TestCase):
    def blocks(self, text):
        return [(b.block_type, b.text) for b in rp.structure_evidence('synthetic.txt', text, []).blocks]

    def test_introduction_heading_paragraph_is_narrative(self):
        text = ('1. Introduction\nPrevious synthetic work used ANCOVA and mixed-effects models widely.\n\n'
                'Methods\nA linear mixed-effects model with random intercepts was fitted to the synthetic data.')
        blocks = self.blocks(text)
        intro = next(t for kind, t in blocks if 'Previous synthetic work' in t)
        self.assertEqual(dict((t, k) for k, t in blocks)[intro], rp.BlockType.NARRATIVE)

    def test_the_word_introduction_inside_a_sentence_does_not_force_narrative(self):
        para = ('The introduction of a random intercept for each synthetic participant was tested '
                'with a likelihood-ratio test in the mixed-effects model.')
        blocks = self.blocks(para)
        self.assertEqual(blocks[0][0], rp.classify_paragraph_block(para))


class AppraisalPromptExamples(unittest.TestCase):
    SOURCE = (ROOT / 'app' / 'review_pipeline.py').read_text(encoding='utf-8')

    def test_document_specific_examples_are_gone(self):
        for token in ('WHT', 'vconsi', 'LEV2bout', 'u(3)0', 'MLwiN version 2.1', 'MLwiN 2.1 vs 2.10',
                      '90.85', 'Waist/Height', 'rpmopt', 'maturity\\s+offset', 'respondent\\s+and\\s+problem'):
            self.assertNotIn(token, self.SOURCE, token)

    def test_principles_are_kept(self):
        for rule in ('EQUATION OCR RULE', 'PEDANTRY RULE', "OCR sometimes extracts '=' as 'Z'",
                     'Ignore minor OCR artefacts in variable names',
                     'a value offered as an exception to a threshold that does not in fact breach it',
                     'Do not critique garbled equations', 'trivial typographical discrepancies'):
            self.assertIn(rule, self.SOURCE, rule)


if __name__ == '__main__':
    unittest.main()
