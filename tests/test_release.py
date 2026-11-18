"""Release contracts using original synthetic fixtures and no live inference."""
import ast
import asyncio
from contextlib import ExitStack
import hashlib
import io
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'app'))
import fixtures as fx
import academic_chat as ac
import decisions_report as dr
import evidence_availability as ea
import evidence_cards as ec
import human_evidence_appendix as hea
import llm_backend as backend
import review_links as links
import review_pipeline as rp
import review_store as store
import reviewer_notes
import reviewer_presentation as presentation
import server
import source_verification as sv
from fastapi.testclient import TestClient

def forbidden(*args,**kwargs):
    raise AssertionError('Live inference or network access is prohibited in these tests')

class Isolated(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='reviewer-release-test-');self.root=Path(self.tmp.name)
        self.stack=ExitStack();self.addCleanup(self.tmp.cleanup);self.addCleanup(self.stack.close)
        self.stack.enter_context(patch.dict(os.environ,{'QWEN_REVIEW_STORE':str(self.root/'sessions'),
            'QWEN_EVIDENCE_LEDGER_DIR':str(self.root/'receipts'),'QWEN_SYNTHESIS_ACCOUNTING_DIR':str(self.root/'diagnostics'),
            'QWEN_VISION_RECORD':'off'}))
        self.stack.enter_context(patch.object(backend,'load',side_effect=forbidden))
        self.stack.enter_context(patch.object(server,'load',side_effect=forbidden))
        self.stack.enter_context(patch.object(server,'ensure_model',return_value=None))
        self.stack.enter_context(patch.object(socket.socket,'connect',side_effect=forbidden))
        self.stack.enter_context(patch.object(server,'review_jobs',{}))
        self.stack.enter_context(patch.object(server,'_persist_sessions',True))
        self.jid='ab12cd34ef56'
    def save(self,**overrides):
        return store.save_completed(self.jid,fx.job(**overrides),cards=fx.cards(),manuscript_sha256=None)

class Policy(Isolated):
    def test_document_structuring_does_not_invoke_classifiers(self):
        with patch.object(rp,'classify_method',side_effect=forbidden),patch.object(rp.de,'classify_design',side_effect=forbidden):
            manifest=rp.structure_evidence('synthetic-bench.txt',fx.TEXT,[])
        self.assertIsNone(manifest.method_class);self.assertIsNone(manifest.design_class)
        self.assertEqual(manifest.additional_method_classes,[])
    def test_legacy_labels_cannot_become_prompt_expectations(self):
        m=rp.EvidenceManifest('fixture',method_class=rp.MethodClass.BAYESIAN_MODEL)
        summary=m.summary_text()+m.model_block_summary()
        self.assertNotIn(rp.MethodClass.BAYESIAN_MODEL.value,summary)
        self.assertIn('general_manuscript_grounded',rp.APPRAISAL_POLICY)
    def test_active_entrypoints_do_not_route_on_method_categories(self):
        forbidden_names={'classify_method','classify_design','get_method_expectations',
            'get_feature_expectations','apply_method_sensitive_critique_rules','format_expected_elements'}
        for path,name in [(ROOT/'app/server.py','_run_review_inner'),(ROOT/'app/review_pipeline.py','main')]:
            tree=ast.parse(path.read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name)
            called={n.func.attr if isinstance(n.func,ast.Attribute) else n.func.id for n in ast.walk(fn)
                if isinstance(n,ast.Call) and isinstance(n.func,(ast.Name,ast.Attribute))}
            self.assertFalse(called & forbidden_names)
    def test_generated_chunk_prompt_keeps_source_and_general_policy(self):
        captured=[]
        def answer(*args,**kw):captured.append(kw.get('prompt'));return fx.REPORT
        with patch.object(rp,'apply_chat_template_compat',side_effect=lambda t,p,**kw:p),patch.object(rp,'generate',side_effect=answer):
            rp.review_chunk(object(),None,rp.DocChunk('synthetic-bench.txt',1,fx.TEXT))
        rendered=str(captured[0]);self.assertIn(fx.REFERENCE,rendered)
        self.assertIn('manuscript',rendered.lower())
        self.assertNotIn('Method-specific expectations',rendered)

class VerificationAndCards(Isolated):
    def test_scripted_verifier_keeps_original_findings(self):
        v=fx.verified();self.assertIn('dispositions',v)
        cards=fx.cards()['cards'];self.assertEqual({c['label'] for c in cards},{'S1','C1','C2','P1'})
        self.assertIn('scanned once',json.dumps(next(c for c in cards if c['label']=='C2')))
    def test_card_html_exposes_decisions_and_literal_source(self):
        html=ec.render_html(fx.cards(),'Synthetic cards','independent-fixture')
        self.assertIn('Confirm decision',html);self.assertIn('Retain',html)
        self.assertIn(fx.REFERENCE,html);self.assertIn('Detailed verification record',html)
    def test_unauthenticated_quote_has_no_document_target(self):
        p=ec.passage('This sentence is absent.',fx.SOURCES,'fixture')
        self.assertIsNone(ec.manuscript_target(p,[],self.jid))
    def test_bound_passage_links_only_its_document_and_page(self):
        p=ec.passage(fx.REFERENCE,fx.SOURCES,'fixture')
        d=dict(id='d0',source_label='synthetic-bench.pdf',available=True,suffix='.pdf',sha256='a'*64)
        target=ec.manuscript_target(p,[d],self.jid)
        self.assertEqual((target['doc'],target['page'],target['quote']),('d0',1,fx.REFERENCE))
        self.assertIsNone(ec.manuscript_target(p,[d,dict(d,id='d1')],self.jid))
    def test_markdown_display_escapes_html_but_formats_emphasis(self):
        html=presentation.markdown_html('**Bench** and *tile*.\n\n- <script>bad</script>')
        self.assertIn('<strong>Bench</strong>',html);self.assertIn('<em>tile</em>',html)
        self.assertNotIn('<script>',html);self.assertIn('&lt;script&gt;',html)
    def test_human_appendix_contains_concerns_and_questions(self):
        appendix=hea.render_human_evidence_appendix(hea.build_evidence_cards(fx.REPORT))
        self.assertIn('instrument serials',appendix);self.assertIn('chamber temperature',appendix)
    def test_appraisal_card_links_keep_finding_identity(self):
        record=links.build_links(fx.REPORT,fx.verified())
        labels={f['id'] for f in record['findings']}
        self.assertTrue({'S1','C1','C2','P1'}<=labels)

class CitationBoundaries(Isolated):
    def test_normalised_quote_across_paragraph_break(self):
        source=('The carriage stopped beside the ceramic tray.\n\n'
                'Its optical shutter remained closed until the lamp stabilised.')
        quote='The carriage stopped beside the ceramic tray. Its optical shutter remained closed until the lamp stabilised.'
        self.assertEqual(rp.quotation_sources(quote,{'bench-log':source}),['bench-log'])
    def test_a_plausible_but_absent_passage_is_not_located(self):
        quote='The carriage stopped beside the metal rack and its lamp stayed off.'
        self.assertEqual(rp.quotation_sources(quote,fx.SOURCES),[])
    def test_short_numeric_quotation_cannot_evade_source_check(self):
        self.assertEqual(rp.verify_report_citations('* Evidence: "4.6"',fx.TEXT),[])
        self.assertTrue(rp.verify_report_citations('* Evidence: "19.27"',fx.TEXT))


class StorageAndExports(Isolated):
    def test_roundtrip_preserves_appraisal_and_appendix_bytes(self):
        self.save();loaded=store.load_job(self.jid)
        self.assertEqual(loaded['report'],fx.REPORT);self.assertEqual(loaded['appendix'],fx.job()['appendix'])
    def test_hash_tampering_refused(self):
        self.save();(store.session_dir(self.jid)/'report.md').write_text('tampered')
        with self.assertRaises(store.StoreError):store.load_job(self.jid)
    def test_store_path_traversal_refused(self):
        with self.assertRaises(store.StoreError):store.session_dir('../escape')
    def test_decisions_roundtrip_does_not_change_original_report(self):
        m=self.save();before=(store.session_dir(self.jid)/'report.md').read_bytes()
        values={'C1':dict(decision='revise',note='Ask for the instrument list.',confirmed_at='2026-01-01')}
        store.write_decisions(self.jid,m['card_fingerprint'],values)
        self.assertEqual(store.read_decisions(self.jid)['decisions'],values)
        self.assertEqual(before,(store.session_dir(self.jid)/'report.md').read_bytes())
    def test_cross_review_decisions_refused(self):
        self.save()
        with self.assertRaises(store.StoreError):store.write_decisions(self.jid,'wrong',{'C1':{'decision':'retain'}})
    def test_unknown_card_and_unconfirmed_choice_refused(self):
        m=self.save()
        for decisions in ({'C99':{'decision':'retain'}},{'C1':{'decision':'arbitrary'}}):
            with self.assertRaises(store.StoreError):store.write_decisions(self.jid,m['card_fingerprint'],decisions)
    def test_decision_markdown_contains_note_without_html_execution(self):
        md=dr.render_markdown(fx.cards(),{'C1':dict(decision='revise',note='Check <script>markup</script>.')},
                              {'filename':'synthetic-bench.pdf'})
        self.assertIn('revise',md.lower());self.assertIn('markup',md)
        self.assertIn('instrument serials',md)
    def test_development_trace_is_retained_only_when_enabled(self):
        trace={'files':[],'final_report':fx.REPORT}
        self.save(development_mode=True,trace=trace)
        self.assertEqual(store.load_job(self.jid)['trace'],trace)
        self.assertTrue(store.read_manifest(self.jid)['development_mode'])
    def test_execution_metadata_roundtrip(self):
        execution={'appraisal_policy':rp.APPRAISAL_POLICY,'resolved':{'reasoning_effort':'medium'}}
        self.save(execution=execution)
        self.assertEqual(store.load_job(self.jid)['execution'],execution)
    def test_document_bytes_served_with_identity_checks(self):
        pdf=self.root/'bench.pdf';pdf.write_bytes(fx.pdf_bytes([fx.REFERENCE,fx.REPEATS]))
        docs=store.stage_pending_documents(self.jid,[{'path':str(pdf),'name':'synthetic-bench.pdf'}])
        docs[0]['source_label']='synthetic-bench.pdf'
        store.save_completed(self.jid,fx.job(),cards=fx.cards(),manuscript_sha256=store.sha256_file(pdf),documents=docs)
        with TestClient(server.app) as client:
            response=client.get('/api/review/'+self.jid+'/documents/d0')
        self.assertEqual(response.status_code,200);self.assertEqual(response.content,pdf.read_bytes())
        path,_=store.document_file(self.jid,'d0');path.write_bytes(b'changed')
        with self.assertRaises(store.StoreError):store.document_file(self.jid,'d0')

class Interface(Isolated):
    def setUp(self):
        super().setUp();self.stack.enter_context(patch.object(server,'ensure_model',return_value=None))
    def test_startup_lifecycle_and_current_interface(self):
        with patch.object(server,'ensure_model') as load,TestClient(server.app) as client:
            r=client.get('/');self.assertEqual(r.status_code,200);load.assert_called_once()
        self.assertIn('Thinking (default)',r.text);self.assertIn('Evidence Cards',r.text)
        self.assertNotIn('/pwa2',r.text)
    def test_saved_review_opens_without_inference(self):
        self.save()
        with TestClient(server.app) as client:
            self.assertEqual(client.post('/api/review/'+self.jid+'/open').status_code,200)
            response=client.get('/api/review/report/'+self.jid)
        self.assertEqual(response.json()['report'],fx.REPORT)
    def test_cards_and_json_export_use_existing_review(self):
        self.save()
        with TestClient(server.app) as client:
            html=client.get('/review/evidence-cards/'+self.jid)
            data=client.get('/api/review/evidence-cards/'+self.jid)
        self.assertEqual(html.status_code,200);self.assertIn('instrument serials',html.text)
        self.assertIn('cards',data.json())
    def test_decisions_api_roundtrip(self):
        m=self.save();payload={'card_fingerprint':m['card_fingerprint'],'decisions':{'S1':{'decision':'retain','note':'Fixture choice.'}}}
        with TestClient(server.app) as client:
            write=client.put('/api/review/'+self.jid+'/decisions',json=payload)
            read=client.get('/api/review/'+self.jid+'/decisions')
        self.assertEqual(write.status_code,200);self.assertEqual(read.json()['decisions']['S1']['decision'],'retain')
    def test_decision_markdown_endpoint_is_read_only(self):
        self.save();folder=store.session_dir(self.jid)
        before={p.name:p.read_bytes() for p in folder.iterdir() if p.is_file()}
        decisions={'S1':{'decision':'retain','note':'Synthetic bench check.'}}
        with TestClient(server.app) as client:
            response=client.post('/api/review/'+self.jid+'/decisions.md',json={'decisions':decisions})
        self.assertEqual(response.status_code,200);self.assertIn('text/markdown',response.headers['content-type'])
        self.assertIn('Synthetic bench check.',response.text)
        self.assertEqual(before,{p.name:p.read_bytes() for p in folder.iterdir() if p.is_file()})
    def test_appendix_export_and_workspace_assets(self):
        self.save()
        with TestClient(server.app) as client:
            self.assertIn('appendix',client.get('/api/review/appendix/'+self.jid).json())
            for route in ['/review/document-viewer','/review/passage-match.js','/review/passage-navigation.js',
                          '/vendor/pdfjs/pdf.min.mjs','/vendor/pdfjs/pdf.worker.min.mjs']:
                self.assertEqual(client.get(route).status_code,200,route)
    def test_missing_and_traversal_assets_refused(self):
        with TestClient(server.app) as client:
            self.assertEqual(client.get('/vendor/pdfjs/not-a-resource.mjs').status_code,404)
            self.assertNotEqual(client.get('/api/review/'+self.jid+'/documents/..').status_code,200)

class ExecutionAndVision(Isolated):
    def transport(self, enabled):
        captured=[]
        def post(request,**kwargs):captured.append(json.loads(request.data));return fx.Reply()
        model=backend.LlamaServerModel('fixture.gguf',base_url='http://fixture.invalid')
        with patch('urllib.request.urlopen',side_effect=post),patch.dict(os.environ,{'LLAMA_REASONING_EFFORT':'medium'}),backend.thinking(enabled):
            model.complete([{'role':'user','content':'Return the synthetic bench label.'}],40,backend.Sampler(),enabled)
        return captured[0]
    def test_thinking_sends_medium_to_actual_request_adapter(self):
        self.assertEqual(self.transport(True)['chat_template_kwargs'],{'enable_thinking':True,'reasoning_effort':'medium'})
    def test_instruct_request_disables_thinking(self):
        self.assertEqual(self.transport(False)['chat_template_kwargs'],{'enable_thinking':False})
    def test_per_review_explicit_choices_override_defaults(self):
        with patch.dict(os.environ,{'QWEN_REVIEW_THINKING':'1'}):
            config=server._review_execution_configuration({'thinking':False,'thinking_scope':'review','vision':False})
        self.assertFalse(config['resolved']['final_synthesis']['enable_thinking'])
    def test_review_defaults_are_separate_from_chat_context(self):
        with patch.dict(os.environ,{'QWEN_REVIEW_THINKING':'','LLAMA_ENABLE_THINKING':''}):
            self.assertTrue(server._review_thinking_default())
        before=backend.thinking_enabled()
        with backend.thinking(not before):self.assertEqual(backend.thinking_enabled(),not before)
        self.assertEqual(backend.thinking_enabled(),before)
    def test_vision_context_selection_is_scoped(self):
        before=rp.vision_enabled()
        with rp.vision(not before):self.assertEqual(rp.vision_enabled(),not before)
        self.assertEqual(rp.vision_enabled(),before)
    def test_vision_page_rendering_dependency_can_read_own_pdf(self):
        import pypdfium2 as pdfium
        document=pdfium.PdfDocument(fx.pdf_bytes([fx.REFERENCE]))
        try:
            image=document[0].render(scale=0.5).to_pil();self.assertGreater(image.width,100)
        finally:document.close()
    def test_local_receipt_records_its_own_source_hash(self):
        f=self.root/'bench.txt';f.write_text(fx.TEXT)
        with ea.capture('independent-fixture',self.root/'ledger') as rec:
            source=rec.begin_source(f)
            self.assertEqual(source,hashlib.sha256(f.read_bytes()).hexdigest())
        self.assertTrue((self.root/'ledger'/'independent-fixture'/'LEDGER.json').exists())

    def test_image_request_contains_image_and_disables_thinking(self):
        seen=[];model=backend.LlamaServerModel('fixture.gguf',base_url='http://fixture.invalid')
        def post(path,payload):seen.append(payload);return json.loads(fx.Reply('Amber | 4.6').data)
        with patch.object(backend,'_LAST_LOADED_MODEL',model),patch.object(model,'_post_json',side_effect=post):
            result=backend.describe_image_result(b'fictional image transport bytes','Transcribe the synthetic bench label.')
        self.assertEqual(result.outcome,'success');self.assertEqual(result.text,'Amber | 4.6')
        self.assertEqual(seen[0]['chat_template_kwargs'],{'enable_thinking':False})
        self.assertEqual(seen[0]['messages'][0]['content'][1]['type'],'image_url')
    def test_failed_image_request_reports_failure_without_making_up_values(self):
        model=backend.LlamaServerModel('fixture.gguf',base_url='http://fixture.invalid')
        with patch.object(backend,'_LAST_LOADED_MODEL',model),patch.object(model,'_post_json',side_effect=backend.BackendError('HTTP 503')):
            result=backend.describe_image_result(b'fictional','Read the fictional bench label.')
        self.assertEqual(result.outcome,'failed');self.assertFalse(result.text)


class MockedReview(Isolated):
    def run_worker(self,thinking,development):
        folder=self.root/'upload';folder.mkdir();document=folder/'synthetic-bench.txt';document.write_text(fx.TEXT)
        server.review_jobs[self.jid]=dict(status='running',progress=[],filename=document.name,
            thinking=thinking,thinking_scope='review',vision=False,development_mode=development,supplements=[])
        with ExitStack() as stack:
            stack.enter_context(patch.object(server,'model',object()))
            stack.enter_context(patch.object(server,'_vision_capability_safe',return_value={'image_input':'unknown'}))
            stack.enter_context(patch.object(rp,'REVIEW_PASSES',3))
            stack.enter_context(patch.object(rp,'review_chunk',return_value=fx.REPORT))
            stack.enter_context(patch.object(rp,'extract_candidate_findings',return_value=[]))
            stack.enter_context(patch.object(rp,'synthesize_file_review',return_value=fx.REPORT))
            synthesis=stack.enter_context(patch.object(rp,'synthesize_report',return_value=fx.REPORT))
            stack.enter_context(patch.object(server,'_source_verification_assessor',return_value=fx.assessor))
            stack.enter_context(patch.object(sv,'enabled',return_value=True))
            stack.enter_context(patch.object(rp,'generate',side_effect=forbidden))
            server._run_review(self.jid,document,'general',folder)
            result=server.review_jobs[self.jid]
            self.assertEqual(result['status'],'complete',result.get('error'))
            return result,synthesis.call_count
    def test_thinking_review_caps_synthesis_and_persists_development_trace(self):
        result,passes=self.run_worker(True,True)
        self.assertEqual(passes,1);self.assertEqual(result['execution']['actual']['final_synthesis_passes'],1)
        self.assertIn(rp.APPRAISAL_POLICY,result['report'])
        self.assertIn('trace',store.load_job(self.jid));self.assertTrue(store.read_manifest(self.jid)['development_mode'])
    def test_instruct_review_repeats_and_has_no_development_trace(self):
        result,passes=self.run_worker(False,False)
        self.assertEqual(passes,3);self.assertEqual(result['execution']['actual']['final_synthesis_passes'],3)
        self.assertNotIn('trace',store.load_job(self.jid))


class AcademicChat(Isolated):
    def test_structured_draft_roundtrip(self):
        payload={'answer_draft':'Check the fictional calibration log.','references':[],'source_claims':[],'technical_claims':[]}
        self.assertEqual(ac.parse_academic_draft(json.dumps(payload)).answer_draft,payload['answer_draft'])
    def test_model_cannot_assign_its_own_verification_status(self):
        payload={'answer_draft':'Fixture.','references':[],'source_claims':[],'technical_claims':[],'verified':True}
        with self.assertRaises(ac.AcademicDraftError):ac.parse_academic_draft(json.dumps(payload))
    def test_academic_draft_generation_uses_mocked_local_backend(self):
        payload={'answer_draft':'Inspect the reference tile.','references':[],'source_claims':[],'technical_claims':[]}
        with patch.object(backend,'generate',return_value=json.dumps(payload)) as generate:
            result=ac.generate_academic_draft(object(),None,'What records support calibration?')
        self.assertEqual(result.answer_draft,payload['answer_draft']);generate.assert_called_once()
    def test_reviewer_notes_are_locally_searchable(self):
        index=reviewer_notes.NotesIndex();hits=index.search('confidence interval uncertainty',3)
        self.assertTrue(hits)

class Toolchain(Isolated):
    def test_pdfjs_reads_new_generated_pdf(self):
        run=subprocess.run(['node',str(ROOT/'tests/pdfjs_read.mjs')],input=fx.pdf_bytes([fx.REFERENCE,fx.REPEATS]),capture_output=True)
        self.assertEqual(run.returncode,0,run.stderr.decode());result=json.loads(run.stdout)
        self.assertEqual(result['pages'],2);self.assertEqual(result['text'],fx.REPEATS)
    def test_javascript_behaviour_harness(self):
        run=subprocess.run(['node',str(ROOT/'tests/ui_contracts.cjs')],capture_output=True,text=True)
        self.assertEqual(run.returncode,0,run.stdout+run.stderr)

if __name__=='__main__':unittest.main()
