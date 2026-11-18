"""Vision status: advertised, tested, failed, and which model a test covers.

Independently authored for this release candidate. Server replies are
hand-written protocol examples; the image is a few placeholder bytes. No model
is loaded and no manuscript content is used. The test record is written to a
temporary file, never to the application's run/ folder.
"""
import json
import os
import sys
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'app'))
import llm_backend as backend  # noqa: E402

PROMPT = 'Transcribe the synthetic fixture table.'
IMAGE = b'\x89PNG synthetic placeholder bytes'


class Reply:
    def __init__(self, payload):
        self.status = 200
        self.data = json.dumps(payload).encode()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return self.data


class FakeServer:
    """GET /props reports the current model; POST /v1/chat/completions
    answers an image request with text, nothing, or an HTTP error."""

    def __init__(self):
        self.props = {}
        self.answer = 'Synthetic transcription.'

    def __call__(self, request, timeout=None, **kwargs):
        url = request if isinstance(request, str) else request.full_url
        if url.endswith('/props'):
            return Reply(self.props)
        if url.endswith('/v1/chat/completions'):
            if self.answer is None:
                raise urllib.error.HTTPError(url, 500, 'fixture', {}, None)
            return Reply({'choices': [{'message': {'content': self.answer}, 'finish_reason': 'stop'}]})
        raise urllib.error.URLError('not routed (fixture)')


class VisionStatus(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='vision-status-test-')
        self.addCleanup(self.tmp.cleanup)
        self.record = Path(self.tmp.name) / 'vision-tests.json'
        self.server = FakeServer()
        patches = [patch.dict(os.environ, {'QWEN_VISION_RECORD': str(self.record)}),
                   patch('urllib.request.urlopen', side_effect=self.server),
                   patch.object(backend, '_VISION_TESTS', None),
                   patch.object(backend, '_VISION_TESTED_THIS_PROCESS', set()),
                   patch.object(backend, '_LAST_LOADED_MODEL',
                                backend.LlamaServerModel('alpha-synthetic.gguf', base_url='http://fixture.invalid:8081'))]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)
        self.load('alpha')

    def load(self, name, vision=True, build='b0001-fixture', url=None):
        self.server.props = {'model_path': f'/models/{name}-synthetic.gguf', 'build_info': build,
                             'modalities': {'vision': vision}}
        if url:
            backend._LAST_LOADED_MODEL.base_url = url

    def status(self):
        return backend.vision_capability()

    def restart_app(self):
        backend._VISION_TESTS = None
        backend._VISION_TESTED_THIS_PROCESS.clear()

    def test_transitions_and_model_switching(self):
        cap = self.status()
        self.assertEqual((cap['image_input'], cap['vision_test']['status']), ('confirmed', 'not_tested'))

        self.assertEqual(backend.describe_image_result(IMAGE, PROMPT).outcome, 'success')
        cap = self.status()
        self.assertEqual(cap['vision_test']['status'], 'succeeded')
        self.assertTrue(cap['exercised_in_this_process'])
        self.assertEqual(cap['vision_test']['model'], 'alpha-synthetic.gguf')

        self.load('beta')                       # a switch: alpha's success must not count
        cap = self.status()
        self.assertEqual(cap['vision_test']['status'], 'not_tested')
        self.assertFalse(cap['exercised_in_this_process'])

        self.server.answer = None               # beta's image request fails
        self.assertEqual(backend.describe_image_result(IMAGE, PROMPT).outcome, 'failed')
        self.assertEqual(self.status()['vision_test']['status'], 'failed')
        self.server.answer = ''                 # and an empty answer is not a success
        self.assertEqual(backend.describe_image_result(IMAGE, PROMPT).outcome, 'empty')
        self.assertEqual(self.status()['vision_test']['status'], 'failed')

        self.load('alpha')                      # back to alpha: its own result stands
        self.assertEqual(self.status()['vision_test']['status'], 'succeeded')

    def test_result_survives_restart_only_for_the_same_identity(self):
        backend.describe_image_result(IMAGE, PROMPT)
        self.restart_app()
        cap = self.status()
        self.assertEqual(cap['vision_test']['status'], 'succeeded')   # same server, model, build
        self.assertFalse(cap['exercised_in_this_process'])           # but not in this process
        self.load('alpha', build='b0002-fixture')
        self.assertEqual(self.status()['vision_test']['status'], 'not_tested')
        self.load('alpha', url='http://other.invalid:8082')
        self.assertEqual(self.status()['vision_test']['status'], 'not_tested')

    def test_unidentified_model_is_neither_recorded_nor_shown_as_tested(self):
        self.server.props = {'modalities': {'vision': True}}
        backend.describe_image_result(IMAGE, PROMPT)
        cap = self.status()
        self.assertEqual(cap['image_input'], 'confirmed')
        self.assertEqual(cap['vision_test']['status'], 'unknown_model')
        self.assertFalse(self.record.exists())

    def test_advertised_is_distinct_from_unavailable(self):
        self.load('alpha', vision=False)
        self.assertEqual(self.status()['image_input'], 'unavailable')
        self.server.props = {'model_path': '/models/alpha-synthetic.gguf'}
        self.assertEqual(self.status()['image_input'], 'unknown')

    def test_record_holds_no_prompt_image_or_output(self):
        backend.describe_image_result(IMAGE, PROMPT)
        stored = self.record.read_text()
        for absent in (PROMPT, 'Synthetic transcription', 'synthetic placeholder', 'base64'):
            self.assertNotIn(absent, stored)
        entry = next(iter(json.loads(stored).values()))
        self.assertEqual(entry['model'], 'alpha-synthetic.gguf')
        self.assertEqual(entry['succeeded'], 1)

    def test_external_server_uses_the_reported_model(self):
        with patch.dict(os.environ, {'LLAMA_SERVER_MODE': 'external'}):
            backend._LAST_LOADED_MODEL.model_path = 'llama-server'   # what the app was started with
            backend.describe_image_result(IMAGE, PROMPT)
            self.assertEqual(self.status()['vision_test']['model'], 'alpha-synthetic.gguf')

    def test_saving_can_be_disabled(self):
        with patch.dict(os.environ, {'QWEN_VISION_RECORD': 'off'}):
            backend.describe_image_result(IMAGE, PROMPT)
            self.assertEqual(self.status()['vision_test']['status'], 'succeeded')  # this process only
        self.assertFalse(self.record.exists())


if __name__ == '__main__':
    unittest.main()
