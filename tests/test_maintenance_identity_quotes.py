"""Synthetic maintenance regressions; no manuscript, network or model needed."""
import copy
import io
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'app'))
import model_identity as mi
import llm_backend as lb
import review_pipeline as rp
import source_verification as sv
import evidence_cards as ec
import human_evidence_appendix as hea
import server
from test_release import Isolated

A='/models/alpha-synthetic.gguf';B='/models/beta-synthetic.gguf'
def reported(path=A):return {'state':'reported','identity':mi.describe(path,'synthetic server')}
def guard(probe=None):return mi.IdentityGuard(mi.describe(A,'explicit'),'explicit','http://fixture.invalid',probe or (lambda:reported()))
class QuoteAuthentication(unittest.TestCase):
    def test_signed_decimal_and_operator_changes_never_authenticate(self):
        sources={'synthetic.txt':'[Page 2]\nThe adjusted value was −1.93 and p < .05 in the control group.'}
        for quote in ['The adjusted value was 1.93','The adjusted value was −1.9','p > .05 in the control group']:
            self.assertEqual(rp.quotation_sources(quote,sources),[])
            self.assertEqual(sv._located(quote,sources),[])
            self.assertEqual(ec._passage(quote,sources)['status'],'unverified')
    def test_table_elision_is_related_not_authenticated(self):
        source='[Page 3]\n[TABLE_START]\n| Measure | Start | End | p |\n| Flexion | 2.14 ± 0.63 | 2.37 ± 0.51 | 0.041 |\n[TABLE_END]'
        quote='Flexion 2.14 2.37 0.041'
        self.assertEqual(rp.quotation_sources(quote,{'synthetic':source}),[])
        self.assertIsNone(ec.locate_span(quote,source))
    def test_exact_formatting_match_has_original_offsets(self):
        source='[Page 1]\nThe adjusted value was −1.93 in the control group.';q='the adjusted value was -1.93 in the control group'
        self.assertEqual(sv._located(q,{'synthetic':source}),['synthetic'])
        start,end=ec.locate_span(q,source);self.assertEqual(source[start:end],'The adjusted value was −1.93 in the control group')
    def test_no_matching_across_documents_or_joined_fragments(self):
        self.assertFalse(rp.quotation_sources('The adjusted value was 2.4',{'a':'The adjusted','b':'value was 2.4'}))
        self.assertFalse(rp.quotation_sources('The adjusted ... 2.4',{'a':'The adjusted value was 2.4'}))
    def test_appraisal_authentication_label_is_not_a_quality_score(self):
        source='The adjusted value was −1.93 in the control group.'
        report='## Directly supported concerns\n1. Concern: Interpretation\nEvidence: “The adjusted value was −1.93 in the control group.”\n'
        display=rp.annotate_concern_confidence(report,source)
        self.assertIn('Exact quotation authenticated',display);self.assertNotIn('Evidence match: High',display);self.assertIn('methodological correctness',display)
    def test_card_rechecks_legacy_authentication_without_mutating_record(self):
        original={'label':'C1','kind':'concern','original':'Concern: Synthetic','quote':'The value was 1.9 in controls','quote_located':True,'outcome':'kept_unassessed'};before=copy.deepcopy(original)
        card=ec.build_card(original,{'synthetic':'The value was 1.93 in controls'})
        self.assertEqual(original,before)
        self.assertTrue(card['evidence'])
        self.assertTrue(all(p['status'] == 'unverified' for p in card['evidence']))
        self.assertTrue(card['provenance']['model_quote_located'])
        self.assertEqual(card['dimensions']['methodological_conclusion']['state'], 'requires_judgement')
class NumberedFindings(unittest.TestCase):
    def test_numbered_strength_concern_and_check_preserve_order_and_offsets(self):
        text='## Major strengths\n1. Strength: Calibrated instrument\nEvidence: Present.\n## Directly supported concerns\n1. Concern: Repeated measures\nEvidence: Present.\n2) Concern: Missing interval\nEvidence: Present.\n## Verification prompts\n1. Check: Confirm the unit\n'
        items=sv.extract_items(text);self.assertEqual([x.label for x in items],['S1','C1','C2','P1'])
        self.assertEqual(items[1].title,'Repeated measures');self.assertTrue(items[2].text.startswith('2) Concern:'))
        appendix=hea.build_evidence_cards(text);self.assertTrue(appendix)
class Identity(unittest.TestCase):
    def test_expected_checkpoint_precedence_and_revision(self):
        expected=mi.expected_for_review(A,'',B,False)
        self.assertEqual(expected['identity']['path'],A)
        self.assertEqual(mi.compare(mi.describe(A,'a'),mi.describe(B,'b'))['state'],mi.MISMATCH)
        self.assertEqual(mi.compare(mi.describe(A,'a'),mi.describe('alpha-synthetic.gguf','b'))['state'],mi.UNVERIFIED)
    def test_before_first_request_and_mid_review_change_are_refused(self):
        g=guard(lambda:reported(B))
        with self.assertRaises(mi.ModelIdentityError):g.verify_before_inference()
        g=guard();g.verify_before_inference();g._probe=lambda:reported(B)
        with self.assertRaises(mi.ModelIdentityError):g.before_request()
        with self.assertRaises(mi.ModelIdentityError):g.before_request()
    def test_wrong_response_not_used_and_swallowed_error_cannot_complete(self):
        g=guard();g.verify_before_inference()
        with self.assertRaises(mi.ModelIdentityError):g.after_response({'model':B},'alpha-synthetic.gguf')
        with lb.identity_guard(g):
            with self.assertRaises(mi.ModelIdentityError):lb.raise_if_identity_compromised()
    def test_transport_checks_before_dispatch_and_preserves_response_receipt(self):
        g=guard();g.verify_before_inference();m=lb.LlamaServerModel(A,'http://fixture.invalid')
        with lb.identity_guard(g),patch.object(lb.urllib.request,'urlopen',return_value=io.BytesIO(json.dumps({'model':A,'choices':[]}).encode())) as opened:
            result=m._post_json('/v1/chat/completions',{'model':'alpha-synthetic.gguf'});self.assertEqual(result['model'],A);self.assertEqual(g.summary()['inference_responses_checked'],1)
        g._probe=lambda:reported(B)
        with lb.identity_guard(g),patch.object(lb.urllib.request,'urlopen') as opened:
            with self.assertRaises(mi.ModelIdentityError):m._post_json('/v1/chat/completions',{'model':'alpha-synthetic.gguf'})
            opened.assert_not_called()
    def test_server_pin_for_external_and_configured_managed(self):
        self.assertEqual(mi.expected_for_review('', '', B,True,reported(A))['identity']['path'],A)
        self.assertEqual(mi.expected_for_review('', '', B,False)['identity']['path'],B)
class WorkerIdentityFailure(Isolated):
    def test_worker_does_not_enter_pipeline_on_wrong_checkpoint(self):
        folder=self.root/'upload';folder.mkdir();doc=folder/'synthetic.txt';doc.write_text('Synthetic specimen measurements only.')
        server.review_jobs[self.jid]={'status':'running','progress':[],'filename':doc.name,'expected_model_identity':{'identity':mi.describe(A,'explicit'),'source':'explicit'}}
        m=lb.LlamaServerModel(B,'http://fixture.invalid')
        with patch.object(server,'model',m),patch.object(server.mi,'server_identity',return_value=reported(B)),patch.object(server,'_run_review_inner') as inner:
            server._run_review(self.jid,doc,'general',folder)
        inner.assert_not_called();self.assertEqual(server.review_jobs[self.jid]['status'],'error');self.assertEqual(server.review_jobs[self.jid]['model_identity_error']['code'],mi.CODE_MISMATCH)

class ExportQuotationControls(unittest.TestCase):
    def test_exact_and_altered_quotes_in_cards_and_full_exports(self):
        import decisions_report as dr
        source='[Page 1]\nThe adjusted value was −1.93 and p < .05 in the control group.'
        for quote,located in [
            ('The adjusted value was −1.93 and p < .05 in the control group',True),
            ('The adjusted value was 1.93 and p < .05 in the control group',False),
            ('The adjusted value was −1.9 and p < .05 in the control group',False),
            ('The adjusted value was −1.93 and p > .05 in the control group',False)]:
            with self.subTest(quote=quote):
                record={'label':'C1','kind':'concern','original':'Concern: Inspect the synthetic interpretation. Evidence: “'+quote+'”',
                        'quote':quote,'quote_located':True,'verdict':'supported','outcome':'kept_unassessed'}
                before=copy.deepcopy(record)
                cards=ec.build_cards({'scope':'complete synthetic source','dispositions':[record]},{'synthetic.txt':source})
                card=cards['cards'][0]
                self.assertEqual(record,before)
                self.assertEqual(any(p['status']=='located' for p in card['evidence']),located)
                self.assertEqual(card['provenance']['model_verdict'],'supported')
                self.assertTrue(card['provenance']['model_quote_located'])
                self.assertEqual(card['dimensions']['methodological_conclusion']['state'],'requires_judgement')
                full=dr.render_markdown(cards,{}, {'filename':'synthetic.txt'})
                self.assertIn('Requires human judgement',full)
                self.assertIn('Relevant manuscript passage located' if located else 'Quotation not authenticated',full)
                self.assertIn('the item is correct',full)

class IdentityUnavailableControls(unittest.TestCase):
    def test_missing_ambiguous_and_conflicting_server_identity_fail_before_dispatch(self):
        for observed in [
            {'state':'not_reported','identity':None},
            {'state':'ambiguous','identity':None,'reason':'More than one synthetic checkpoint'},
            reported(B)]:
            g=guard(lambda:observed);m=lb.LlamaServerModel(A,'http://fixture.invalid')
            with self.subTest(state=observed['state']),patch.object(lb.urllib.request,'urlopen') as opened:
                with self.assertRaises(mi.ModelIdentityError):g.verify_before_inference()
                with lb.identity_guard(g):
                    with self.assertRaises(mi.ModelIdentityError):m._post_json('/v1/chat/completions',{'model':A})
                opened.assert_not_called()
    def test_disagreeing_props_and_models_are_ambiguous(self):
        def opener(url,timeout):
            data={'model_path':A} if url.endswith('/props') else {'data':[{'id':B}]}
            return io.BytesIO(json.dumps(data).encode())
        result=mi.server_identity('http://fixture.invalid',opener=opener)
        self.assertEqual(result['state'],'ambiguous');self.assertIsNone(result['identity'])
