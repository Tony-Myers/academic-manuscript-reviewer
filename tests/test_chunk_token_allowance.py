"""Synthetic wire-level chunk-budget regressions. No server/model is used."""
import copy
import socket
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'app'))
import llm_backend as backend
import review_pipeline as pipeline

class ChunkTokenAllowance(unittest.TestCase):
    def run_chunk(self, thinking, finishes, ceiling=4000):
        model=backend.LlamaServerModel('synthetic-model.gguf','http://unused.invalid')
        tokenizer=backend.GGUFTokenizer('synthetic-model.gguf')
        payloads=[]
        def reply(path,payload):
            self.assertEqual(path,'/v1/chat/completions')
            payloads.append(copy.deepcopy(payload))
            message={'content':'Accepted synthetic chunk notes.'}
            if thinking:message['reasoning_content']='Synthetic reasoning.'
            return {'choices':[{'message':message,'finish_reason':finishes[len(payloads)-1]}]}
        backend.reset_reasoning_stats()
        with patch.object(socket.socket,'connect',side_effect=AssertionError('Network forbidden')), \
             patch.object(model,'_post_json',side_effect=reply), \
             patch.object(backend,'_generation_ceiling',return_value=ceiling), \
             backend.thinking(thinking),pipeline.vision(False):
            result=pipeline.review_chunk(model,tokenizer,pipeline.DocChunk('synthetic.txt',1,
                'Twelve fictional ceramic specimens were measured twice.'))
        return result,payloads
    def test_non_thinking_starts_at_1800_and_keeps_payload_on_recovery(self):
        text,payloads=self.run_chunk(False,['length','stop'])
        self.assertEqual(text,'Accepted synthetic chunk notes.')
        self.assertEqual([p['max_tokens'] for p in payloads],[1800,3600])
        a,b=map(dict,payloads);a.pop('max_tokens');b.pop('max_tokens')
        self.assertEqual(a,b)
        self.assertEqual(a['chat_template_kwargs'],{'enable_thinking':False})
    def test_existing_ceiling_and_host_return_semantics_are_preserved(self):
        _,payloads=self.run_chunk(False,['length','length','length'])
        self.assertEqual([p['max_tokens'] for p in payloads],[1800,3600,4000])
    def test_stop_response_does_not_retry(self):
        _,payloads=self.run_chunk(False,['stop'])
        self.assertEqual([p['max_tokens'] for p in payloads],[1800])
    def test_thinking_budget_is_unchanged(self):
        _,payloads=self.run_chunk(True,['stop'],ceiling=32768)
        self.assertEqual(payloads[0]['max_tokens'],900+backend.THINKING_EXTRA_TOKENS)
        self.assertTrue(payloads[0]['chat_template_kwargs']['enable_thinking'])

if __name__=='__main__':unittest.main()
