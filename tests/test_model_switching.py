"""Model configuration, switching and connection status.

Independently authored for this release candidate. Every model "file" is a
few placeholder bytes with an invented name; every server reply is a
hand-written protocol example; the shell tests run a fake llama-server written
below. No model is loaded and no manuscript or review material is involved.
"""
import io
import json
import os
from pathlib import Path
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import threading
import time
import unittest
import urllib.error
from contextlib import ExitStack
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'app'))
import llm_backend as backend  # noqa: E402
import model_server as ms  # noqa: E402
import review_pipeline as rp  # noqa: E402
import server  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

URL = 'http://fixture.invalid:8081'
REAL_POPEN = subprocess.Popen  # the alias test runs bash; everything else is blocked


def forbidden(*args, **kwargs):
    raise AssertionError('Live inference, process control or network access is prohibited here')


class Reply:
    """In-memory urllib response carrying a hand-written JSON body."""
    def __init__(self, payload, status=200):
        self.status = status
        self.data = json.dumps(payload).encode()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return self.data


def fake_llama(routes):
    """urlopen stand-in. routes maps a path suffix to a JSON body, or to an
    int HTTP error status. Anything unrouted is refused, as a dead port is."""
    def urlopen(request, timeout=None, **kwargs):
        url = request if isinstance(request, str) else request.full_url
        for suffix, value in routes.items():
            if url.endswith(suffix):
                if isinstance(value, int):
                    raise urllib.error.HTTPError(url, value, 'fixture', {}, io.BytesIO(b'{}'))
                return Reply(value)
        raise urllib.error.URLError('connection refused (fixture)')
    return urlopen


def refused(request, timeout=None, **kwargs):
    raise urllib.error.URLError('connection refused (fixture)')


class Completed:
    def __init__(self, returncode, stdout='', stderr=''):
        self.returncode, self.stdout, self.stderr = returncode, stdout, stderr


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='model-switch-test-')
        self.root = Path(self.tmp.name)
        self.stack = ExitStack()
        self.addCleanup(self.tmp.cleanup)
        self.addCleanup(self.stack.close)
        models = self.root / 'models'
        models.mkdir()
        self.alpha = models / 'alpha-synthetic.gguf'
        self.beta = models / 'beta-synthetic.gguf'
        for path in (self.alpha, self.beta):
            path.write_bytes(b'GGUF placeholder for tests')
        self.stack.enter_context(patch.dict(os.environ, {
            'QWEN_REVIEW_STORE': str(self.root / 'sessions'),
            'QWEN_EVIDENCE_LEDGER_DIR': str(self.root / 'receipts'),
            'QWEN_SYNTHESIS_ACCOUNTING_DIR': str(self.root / 'diagnostics'),
            'LLAMA_SERVER_URL': URL, 'LLAMA_SERVER_MODE': 'managed',
            'QWEN_SERVICE_MANAGED': '', 'QWEN_LLM_BACKEND': 'llama-server',
            'LLAMA_MODEL_DIRS': '', 'LLAMA_SERVER_AUTOSTART': '', 'QWEN_VISION_RECORD': 'off',
        }))
        self.stack.enter_context(patch.object(socket.socket, 'connect', side_effect=forbidden))
        self.stack.enter_context(patch.object(subprocess, 'Popen', side_effect=forbidden))
        self.stack.enter_context(patch.object(server, 'review_jobs', {}))
        self.stack.enter_context(patch.object(server, 'model', None))
        self.stack.enter_context(patch.object(server, 'tokenizer', None))
        self.stack.enter_context(patch.object(server, 'MODEL_NAME', str(self.alpha)))
        self.stack.enter_context(patch.object(rp, 'MODEL_NAME', str(self.alpha)))
        self.stack.enter_context(patch.object(server, 'model_switch', ms.ModelSwitch()))
        self.stack.enter_context(patch.object(server, 'restart_scheduled', False))
        self.stack.enter_context(patch.object(server, 'ensure_model', return_value=None))
        self.load = self.stack.enter_context(patch.object(server, 'load', side_effect=forbidden))
        self.stack.enter_context(patch.object(backend, '_LAST_LOADED_MODEL', None))
        self.stack.enter_context(patch.object(backend, '_ACTIVE_BACKEND', None))

    def mode(self, value):
        self.stack.enter_context(patch.dict(os.environ, {'LLAMA_SERVER_MODE': value}))

    def serve(self, routes):
        self.stack.enter_context(patch('urllib.request.urlopen', side_effect=fake_llama(routes)))

    def wait_for_switch(self, seconds=5):
        deadline = time.time() + seconds
        while time.time() < deadline:
            if not server.model_switch.busy():
                return server.model_switch.snapshot()
            time.sleep(0.02)
        self.fail('switch did not finish')


class ManagedSwitching(Base):
    def test_successful_switch_reports_loaded_only_after_ready(self):
        gate, commands = threading.Event(), []

        def run(command, **kwargs):
            commands.append(command)
            gate.wait(5)
            return Completed(0, '=== Model loaded: beta-synthetic.gguf ===\n')
        handle = backend.LlamaServerModel(str(self.beta), base_url=URL)
        self.load.side_effect = None
        self.load.return_value = (handle, backend.GGUFTokenizer(str(self.beta)))
        self.serve({'/health': {'status': 'ok'}, '/props': {'model_path': str(self.beta)}})
        with patch.object(subprocess, 'run', side_effect=run), \
                patch.object(backend, 'served_model_name', return_value='beta-synthetic.gguf'), \
                TestClient(server.app) as client:
            started = client.post('/api/server/restart', json={'model': str(self.beta)})
            self.assertEqual(started.status_code, 200, started.text)
            self.assertEqual(started.json()['method'], 'in-place')
            during = client.get('/api/server/status').json()
            self.assertEqual(during['model_state'], 'loading')
            self.assertEqual(during['switch']['state'], 'loading')
            blocked = client.post('/api/review', files={'file': ('bench.txt', b'synthetic')})
            self.assertEqual(blocked.status_code, 409)
            gate.set()
            self.wait_for_switch()
            after = client.get('/api/server/status').json()
        self.assertEqual(after['model_state'], 'loaded')
        self.assertEqual(after['switch']['state'], 'loaded')
        self.assertEqual(after['loaded_model'], 'beta-synthetic.gguf')
        self.assertTrue(after['model_identified'])
        self.assertTrue(after['model_matches_configured'])
        self.assertEqual(server.MODEL_NAME, str(self.beta))
        command = commands[0]
        self.assertTrue(command[0].endswith('bash'))  # runs even without the executable bit
        self.assertTrue(command[1].endswith('scripts/qwen_service.sh'))
        self.assertEqual(command[2:5], ['switch-model', '--model', str(self.beta)])
        self.assertEqual(command[-2:], ['--llama-port', '8081'])

    def test_failed_startup_is_reported_and_model_is_not_changed(self):
        output = ('[2026-01-01 00:00:00] Starting llama-server on port 8081 (beta-synthetic.gguf)...\n'
                  '[2026-01-01 00:00:01] ERROR: llama-server exited during startup. Last lines:\n'
                  "[2026-01-01 00:00:01]   fixture: unknown model architecture: 'fixturearch'\n"
                  '[2026-01-01 00:00:01] \n'
                  "[2026-01-01 00:00:01] llama-server does not know this model's architecture.\n"
                  '[2026-01-01 00:00:01] It was run as: llama-server\n')
        self.serve({})
        with patch.object(subprocess, 'run', return_value=Completed(1, output)), \
                TestClient(server.app) as client:
            response = client.post('/api/server/restart', json={'model': str(self.beta)})
            self.assertEqual(response.status_code, 200, response.text)
            self.wait_for_switch()
            status = client.get('/api/server/status').json()
        self.assertEqual(status['model_state'], 'failed')
        self.assertEqual(status['switch']['state'], 'failed')
        self.assertIn('ERROR: llama-server exited during startup', status['switch']['error'])
        self.assertIn("does not know this model's architecture", status['switch']['error'])
        self.assertNotIn('[2026', status['switch']['error'])
        self.assertEqual(status['connection'], 'unreachable')
        self.assertEqual(server.MODEL_NAME, str(self.alpha))
        self.load.assert_not_called()

    def test_switch_rejected_while_one_is_loading_or_a_review_runs(self):
        server.model_switch.begin(str(self.beta))
        self.serve({})
        with TestClient(server.app) as client:
            self.assertEqual(client.post('/api/server/restart',
                                         json={'model': str(self.alpha)}).status_code, 409)
        with patch.object(server, 'review_jobs', {'x': {'status': 'running'}}), \
                TestClient(server.app) as client:
            self.assertEqual(client.post('/api/server/restart',
                                         json={'model': str(self.alpha)}).status_code, 409)

    def test_server_reporting_a_different_model_is_a_failure(self):
        switch = ms.ModelSwitch()
        switch.begin(str(self.beta))
        ms.perform_switch(switch, str(self.beta), command=['fixture'], cwd=str(self.root),
                          reload=lambda target: 'alpha-synthetic.gguf', timeout=5,
                          run=lambda *a, **k: Completed(0))
        state = switch.snapshot()
        self.assertEqual(state['state'], 'failed')
        self.assertIn('reports alpha-synthetic.gguf loaded, not beta-synthetic.gguf', state['error'])

    def test_unreported_model_name_is_loaded_but_unidentified(self):
        switch = ms.ModelSwitch()
        switch.begin(str(self.beta))
        ms.perform_switch(switch, str(self.beta), command=['fixture'], cwd=str(self.root),
                          reload=lambda target: '', timeout=5, run=lambda *a, **k: Completed(0))
        state = switch.snapshot()
        self.assertEqual(state['state'], 'loaded')
        self.assertFalse(state['model_identified'])
        self.assertIsNone(state['loaded_model'])

    def test_timeout_is_reported_as_failure(self):
        def run(*args, **kwargs):
            raise subprocess.TimeoutExpired('fixture', 5)
        switch = ms.ModelSwitch()
        switch.begin(str(self.beta))
        ms.perform_switch(switch, str(self.beta), command=['fixture'], cwd=str(self.root),
                          reload=forbidden, timeout=5, run=run)
        self.assertEqual(switch.snapshot()['state'], 'failed')
        self.assertIn('did not report ready within 5 seconds', switch.snapshot()['error'])


class ExternalServer(Base):
    def setUp(self):
        super().setUp()
        self.mode('external')
        self.stack.enter_context(patch.object(server, 'MODEL_NAME', 'llama-server'))

    def test_external_connection_identifies_model_and_offers_no_restart(self):
        self.serve({'/health': {'status': 'ok'},
                    '/props': {'model_path': '/srv/models/gamma-synthetic.gguf'},
                    '/v1/models': {'data': [{'id': 'gamma-synthetic'}]}})
        with patch.object(subprocess, 'run', side_effect=forbidden), TestClient(server.app) as client:
            status = client.get('/api/server/status').json()
            aliases = client.get('/api/models/aliases').json()
            refused_restart = client.post('/api/server/restart', json={'model': str(self.beta)})
        self.assertEqual(status['mode'], 'external')
        self.assertEqual(status['connection'], 'connected')
        self.assertEqual(status['model_state'], 'loaded')
        self.assertEqual(status['loaded_model'], 'gamma-synthetic.gguf')
        self.assertEqual(status['server_url'], URL)
        self.assertIsNone(status['model_matches_configured'])
        self.assertFalse(status['restart_available'])
        self.assertIn('external', status['restart_unavailable_reason'])
        self.assertEqual(aliases['mode'], 'external')
        self.assertFalse(aliases['restart_available'])
        self.assertEqual(refused_restart.status_code, 409)
        self.assertIn('external', refused_restart.json()['error'])

    def test_backend_load_identifies_served_model_without_a_local_file(self):
        self.serve({'/health': {'status': 'ok'},
                    '/props': {'model_path': '/srv/models/gamma-synthetic.gguf'},
                    '/v1/models': {'data': [{'id': 'gamma-synthetic'}]}})
        handle, tokenizer = backend.load('placeholder-that-is-not-a-file')
        self.assertIsInstance(handle, backend.LlamaServerModel)
        self.assertEqual(handle.model_path, 'gamma-synthetic')
        self.assertEqual(backend.served_model_name(), 'gamma-synthetic.gguf')
        self.assertEqual(backend.current_backend(), backend.BACKEND_LLAMA_SERVER)

    def test_unavailable_server_is_reported_and_never_started(self):
        self.stack.enter_context(patch('urllib.request.urlopen', side_effect=refused))
        self.stack.enter_context(patch.dict(os.environ, {'LLAMA_SERVER_AUTOSTART': '1'}))
        with patch.object(backend.LlamaServerModel, 'autostart', side_effect=forbidden):
            with self.assertRaises(backend.BackendError) as caught:
                backend.load('placeholder-that-is-not-a-file')
        self.assertIn('will not start one', str(caught.exception))
        with patch.object(server, 'ensure_model',
                          side_effect=backend.BackendError('fixture: nothing listening')), \
                TestClient(server.app) as client:
            status = client.get('/api/server/status').json()
        self.assertEqual(status['connection'], 'unreachable')
        self.assertEqual(status['model_state'], 'unknown')
        self.assertIn(URL, status['message'])
        self.assertIsNone(status['loaded_model'])

    def test_incomplete_model_metadata_is_not_guessed(self):
        self.serve({'/health': {'status': 'ok'}, '/props': {}, '/v1/models': {'data': []}})
        with TestClient(server.app) as client:
            status = client.get('/api/server/status').json()
        self.assertEqual(status['connection'], 'connected')
        self.assertEqual(status['model_state'], 'loaded')
        self.assertFalse(status['model_identified'])
        self.assertIsNone(status['loaded_model'])
        self.assertIn('did not report', status['message'])
        self.serve({'/health': {'status': 'ok'}, '/props': ['not', 'an', 'object'],
                    '/v1/models': 'none'})
        self.assertEqual(backend.LlamaServerModel('x', base_url=URL).served_model_name(), '')

    def test_report_header_names_the_served_model_without_a_false_warning(self):
        handle = backend.LlamaServerModel('gamma-synthetic', base_url=URL)
        self.stack.enter_context(patch.object(backend, '_LAST_LOADED_MODEL', handle))
        self.serve({'/props': {'model_path': '/srv/models/gamma-synthetic.gguf'}})
        self.assertEqual(server._model_header_lines(),
                         ['Model: gamma-synthetic.gguf (reported by an external llama-server)'])
        self.serve({'/props': {}, '/v1/models': {'data': []}})
        self.assertIn('not reported', server._model_header_lines()[0])


class CapabilitiesAndCompatibility(Base):
    def transport(self, enabled, model_path):
        captured = []

        def post(request, **kwargs):
            captured.append(json.loads(request.data))
            return Reply({'choices': [{'message': {'content': 'Fixture.'}, 'finish_reason': 'stop'}],
                          'usage': {'completion_tokens': 2}})
        handle = backend.LlamaServerModel(model_path, base_url=URL)
        with patch('urllib.request.urlopen', side_effect=post), \
                patch.dict(os.environ, {'LLAMA_REASONING_EFFORT': 'medium'}), backend.thinking(enabled):
            handle.complete([{'role': 'user', 'content': 'Return the fixture label.'}], 20,
                            backend.Sampler(), enabled)
        return captured[0]

    def test_thinking_and_instruct_requests_are_unchanged_in_external_mode(self):
        self.mode('external')
        self.assertEqual(self.transport(True, 'gamma-synthetic')['chat_template_kwargs'],
                         {'enable_thinking': True, 'reasoning_effort': 'medium'})
        sent = self.transport(False, 'gamma-synthetic')
        self.assertEqual(sent['chat_template_kwargs'], {'enable_thinking': False})
        self.assertEqual(sent['model'], 'gamma-synthetic')

    def test_vision_is_reported_from_the_server_not_assumed(self):
        handle = backend.LlamaServerModel('gamma-synthetic', base_url=URL)
        self.stack.enter_context(patch.object(backend, '_LAST_LOADED_MODEL', handle))
        for props, expected in (({'modalities': {'vision': True}}, 'confirmed'),
                                ({'modalities': {'vision': False}}, 'unavailable'),
                                ({}, 'unknown')):
            with patch('urllib.request.urlopen', side_effect=fake_llama({'/props': props})):
                self.assertEqual(backend.vision_capability()['image_input'], expected, props)
        with patch('urllib.request.urlopen', side_effect=refused):
            self.assertEqual(backend.vision_capability()['image_input'], 'unknown')
        self.stack.enter_context(patch.object(backend, '_LAST_LOADED_MODEL', object()))
        self.assertEqual(backend.vision_capability()['image_input'], 'unavailable')

    def test_managed_mode_still_requires_a_local_model_file(self):
        self.stack.enter_context(patch('urllib.request.urlopen', side_effect=forbidden))
        with self.assertRaises(backend.BackendError):
            backend.load(str(self.root / 'missing-synthetic.gguf'))

    def test_managed_startup_failure_still_stops_the_app(self):
        with patch.object(server, 'ensure_model', side_effect=backend.BackendError('fixture')):
            with self.assertRaises(backend.BackendError):
                with TestClient(server.app):
                    pass

    def test_existing_endpoints_and_choices_are_kept(self):
        self.serve({'/health': {'status': 'ok'}, '/props': {'model_path': str(self.alpha)}})
        with TestClient(server.app) as client:
            models = client.get('/v1/models').json()
            aliases = client.get('/api/models/aliases').json()
        self.assertEqual(models['data'][0]['id'], str(self.alpha))
        self.assertEqual(aliases['current_model'], str(self.alpha))
        self.assertTrue(any(m['model'] == str(self.alpha) for m in aliases['models']))
        ids = [choice['id'] for choice in server.MODEL_CHOICES]
        for expected in ('qwen38', 'flash', '35b', '27b', 'gemma4'):
            self.assertIn(expected, ids)
        self.assertEqual(server.resolve_model_choice('flash'), rp.QWEN38_FLASH_NEXT_GGUF)

    def test_shell_and_python_alias_tables_agree(self):
        if not shutil.which('bash'):
            self.skipTest('bash not available')
        env = {k: v for k, v in os.environ.items() if k != 'HF_HUB_CACHE'}
        env['HOME'] = str(Path.home())
        script = 'source scripts/model_aliases.sh\n' + ''.join(
            f'printf "%s\\t%s\\n" {alias} "$(resolve_model {alias})"\n' for alias in rp.MODEL_ALIASES)
        with patch.object(subprocess, 'Popen', REAL_POPEN):
            run = subprocess.run(['bash', '-c', script], cwd=ROOT, env=env, capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        shell = dict(line.split('\t', 1) for line in run.stdout.splitlines())
        self.assertEqual(shell, dict(rp.MODEL_ALIASES))

    def test_models_are_discovered_from_configured_directories(self):
        folder = self.root / 'discovered' / 'nested'
        folder.mkdir(parents=True)
        for name in ('delta-synthetic.gguf', 'mmproj-delta-synthetic.gguf',
                     'epsilon-synthetic-00001-of-00002.gguf', 'epsilon-synthetic-00002-of-00002.gguf'):
            (folder / name).write_bytes(b'GGUF placeholder')
        self.stack.enter_context(patch.dict(os.environ, {'LLAMA_MODEL_DIRS': str(self.root / 'discovered')}))
        names = [choice['label'] for choice in server.installed_model_choices()]
        self.assertIn('delta-synthetic.gguf', names)
        self.assertIn('epsilon-synthetic-00001-of-00002.gguf', names)
        self.assertNotIn('mmproj-delta-synthetic.gguf', names)
        self.assertNotIn('epsilon-synthetic-00002-of-00002.gguf', names)
        spaced = self.root / 'Application Support' / 'zeta-synthetic.gguf'
        spaced.parent.mkdir()
        spaced.write_bytes(b'GGUF placeholder')
        self.assertTrue(server._is_valid_model_choice(str(spaced)))
        self.assertFalse(server._is_valid_model_choice(str(spaced) + '\nrm'))
        self.assertFalse(server._is_valid_model_choice(str(self.root / 'absent-synthetic.gguf')))

    def test_full_restart_keeps_port_and_is_refused_without_the_service(self):
        self.stack.enter_context(patch.dict(os.environ, {'QWEN_LLM_BACKEND': 'mlx', 'LLAMA_SERVER_MODE': ''}))
        self.stack.enter_context(patch.object(server, 'MODEL_NAME', 'fixture-org/fixture-mlx-model'))
        self.stack.enter_context(patch.object(server, '_cached_snapshot_for_model', return_value=self.root))
        with TestClient(server.app) as client:
            refused_restart = client.post('/api/server/restart', json={'model': 'fixture-org/other-mlx-model'})
        self.assertEqual(refused_restart.status_code, 409)
        self.assertIn('qwen_service.sh', refused_restart.json()['error'])
        launched = []
        with patch.object(server.time, 'sleep'), patch.object(server, 'SERVER_PORT', 8095), \
                patch.object(server.subprocess, 'Popen', side_effect=lambda cmd, **k: launched.append(cmd)):
            server._restart_after_response('fixture-org/other-mlx-model')
        self.assertTrue(launched[0][0].endswith('bash'))
        self.assertEqual(launched[0][2:], ['restart', '--model', 'fixture-org/other-mlx-model',
                                           '--port', '8095', '--no-open'])


class ActiveOperationGuard(Base):
    """A switch must not silently interrupt model-dependent work, and no such
    work may start while a model is loading."""

    def wait_for_operation(self, kind, seconds=5):
        deadline = time.time() + seconds
        while time.time() < deadline:
            if kind in server.model_switch.active_operations():
                return
            time.sleep(0.02)
        self.fail(f'{kind} never became active')

    def test_switch_refused_while_academic_chat_runs(self):
        gate, results = threading.Event(), {}

        class Draft:
            def to_dict(self):
                return {'draft': 'Synthetic fixture draft.'}

        def slow_draft(*args, **kwargs):
            gate.wait(5)
            return Draft()
        self.serve({})
        with patch.object(server.academic_chat, 'generate_academic_draft', side_effect=slow_draft), \
                patch.object(subprocess, 'run', side_effect=forbidden), TestClient(server.app) as client:
            worker = threading.Thread(target=lambda: results.update(
                draft=client.post('/api/chat/academic/draft', json={'question': 'Synthetic question?'})))
            worker.start()
            self.wait_for_operation('Academic Chat draft')
            refused_switch = client.post('/api/server/restart', json={'model': str(self.beta)})
            gate.set()
            worker.join(5)
        self.assertEqual(refused_switch.status_code, 409)
        self.assertIn('Academic Chat draft', refused_switch.json()['error'])
        self.assertEqual(results['draft'].status_code, 200)
        self.assertEqual(server.model_switch.active_operations(), {})
        self.assertEqual(server.model_switch.snapshot()['state'], 'idle')

    def test_switch_refused_while_an_appraisal_runs_and_released_after(self):
        gate = threading.Event()

        def slow_inner(*args, **kwargs):
            gate.wait(5)
            raise backend.InferenceCancelledError('fixture: cancelled by the test')
        self.serve({})
        with patch.object(server, '_run_review_inner', side_effect=slow_inner), \
                patch.object(subprocess, 'run', side_effect=forbidden), TestClient(server.app) as client:
            started = client.post('/api/review', files={'file': ('bench.txt', b'Synthetic bench text.')})
            self.assertEqual(started.status_code, 200, started.text)
            job_id = started.json()['job_id']
            self.wait_for_operation(server.REVIEW_OPERATION)
            # Mark the job finished early, to show the operation guard (not
            # only the job-status check) is what refuses the switch.
            server.review_jobs[job_id]['status'] = 'complete'
            refused_switch = client.post('/api/server/restart', json={'model': str(self.beta)})
            gate.set()
            deadline = time.time() + 5
            while server.model_switch.active_operations() and time.time() < deadline:
                time.sleep(0.02)
        self.assertEqual(refused_switch.status_code, 409)
        self.assertIn('manuscript appraisal', refused_switch.json()['error'])
        self.assertEqual(server.model_switch.active_operations(), {})

    def test_model_work_refused_while_a_model_loads(self):
        server.model_switch.begin(str(self.beta))
        self.serve({})
        with TestClient(server.app) as client:
            responses = [
                client.post('/api/chat/academic', json={'question': 'Synthetic question?'}),
                client.post('/api/chat/academic/draft', json={'question': 'Synthetic question?'}),
                client.post('/v1/chat/completions', json={'messages': [{'role': 'user', 'content': 'Hi'}]}),
                client.post('/api/review/ab12cd34ef56/ask', json={'question': 'Synthetic?'}),
                client.post('/api/review', files={'file': ('bench.txt', b'Synthetic.')}),
            ]
        for response in responses:
            self.assertEqual(response.status_code, 409, response.text)
            self.assertIn('loading', response.json()['detail'])
        self.assertEqual(server.model_switch.active_operations(), {})

    def test_untracked_generation_also_blocks_a_switch(self):
        self.serve({})
        with backend._INFERENCE_SCHEDULER.admit(), TestClient(server.app) as client:
            refused_switch = client.post('/api/server/restart', json={'model': str(self.beta)})
        self.assertEqual(refused_switch.status_code, 409)
        self.assertIn('generation is in progress', refused_switch.json()['error'])
        self.assertFalse(backend.inference_in_progress())

    def test_operation_and_switch_exclude_each_other(self):
        switch = ms.ModelSwitch()
        switch.acquire('chat')
        self.assertFalse(switch.begin(str(self.beta)))
        switch.release('chat')
        switch.release('chat')  # extra release never goes below zero
        self.assertEqual(switch.active_operations(), {})
        self.assertTrue(switch.begin(str(self.beta)))
        with self.assertRaises(ms.SwitchInProgress):
            switch.acquire('chat')


FAKE_LLAMA_SERVER = r'''#!/usr/bin/env python3
"""Fake llama-server for process-handling tests; serves fixed JSON only."""
import http.server, json, os, sys
args = sys.argv[1:]
model, host, port = (args[args.index(flag) + 1] for flag in ('--model', '--host', '--port'))
if 'broken' in os.path.basename(model):
    print("fixture: unknown model architecture: 'fixturearch'", flush=True)
    sys.exit(1)
class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        bodies = {'/health': {'status': 'ok'}, '/props': {'model_path': model},
                  '/v1/models': {'data': [{'id': model}]}}
        if self.path not in bodies:
            self.send_response(404); self.end_headers(); return
        data = json.dumps(bodies[self.path]).encode()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)
    def log_message(self, *args):
        pass
http.server.HTTPServer((host, int(port)), Handler).serve_forever()
'''


@unittest.skipUnless(all(shutil.which(tool) for tool in ('bash', 'curl', 'lsof', 'ps', 'sleep')),
                     'bash, curl, lsof, ps and sleep are needed for the process tests')
class ServiceProcessSafety(unittest.TestCase):
    """Runs scripts/qwen_service.sh switch-model against a fake llama-server
    on a free loopback port, in a temporary copy of the scripts folder."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='service-process-test-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        project = self.root / 'project'
        (project / 'scripts').mkdir(parents=True)
        for name in ('qwen_service.sh', 'model_aliases.sh'):
            shutil.copy2(ROOT / 'scripts' / name, project / 'scripts' / name)
        self.service = project / 'scripts' / 'qwen_service.sh'
        self.pid_file = project / 'run' / 'llama-server.pid'
        bin_dir = self.root / 'bin'
        bin_dir.mkdir()
        fake = bin_dir / 'llama-server'
        fake.write_text(FAKE_LLAMA_SERVER)
        fake.chmod(0o755)
        self.models = self.root / 'models'
        self.models.mkdir()
        for name in ('alpha-synthetic.gguf', 'beta-synthetic.gguf', 'broken-synthetic.gguf'):
            (self.models / name).write_bytes(b'GGUF placeholder')
        with socket.socket() as probe:
            probe.bind(('127.0.0.1', 0))
            self.port = probe.getsockname()[1]
        self.env = {k: v for k, v in os.environ.items() if not k.startswith(('LLAMA_', 'QWEN_'))}
        self.env.update(PATH=f'{bin_dir}{os.pathsep}{os.environ.get("PATH", "")}',
                        HOME=str(self.root), LLAMA_SERVER_MODE='managed',
                        LLAMA_SERVER_HOST='127.0.0.1', LLAMA_SERVER_PORT=str(self.port),
                        QWEN_STARTUP_TIMEOUT='30', QWEN_LOAD_MMPROJ='0')
        self.others = []
        self.addCleanup(self.stop_everything)

    def stop_everything(self):
        for proc in self.others:
            if proc.poll() is None:
                proc.kill()
                proc.wait(5)
        pid = self.recorded_pid()
        if pid and self.alive(pid):
            os.kill(pid, signal.SIGKILL)

    def recorded_pid(self):
        try:
            return int(self.pid_file.read_text().strip())
        except (OSError, ValueError):
            return None

    @staticmethod
    def alive(pid):
        state = subprocess.run(['ps', '-p', str(pid), '-o', 'stat='], capture_output=True, text=True).stdout.strip()
        return bool(state) and not state.startswith('Z')

    def switch(self, model, **env):
        run = subprocess.run(['bash', str(self.service), 'switch-model', '--model', str(self.models / model)],
                             env={**self.env, **env}, capture_output=True, text=True, timeout=90)
        return run.returncode, run.stdout + run.stderr

    def served(self):
        out = subprocess.run(['curl', '-s', '-m', '3', f'http://127.0.0.1:{self.port}/props'],
                             capture_output=True, text=True).stdout
        return Path(json.loads(out)['model_path']).name if out else ''

    def listening(self):
        return subprocess.run(['curl', '-s', '-o', '/dev/null', '-m', '2', f'http://127.0.0.1:{self.port}/'],
                              capture_output=True).returncode == 0

    def test_managed_switch_replaces_only_its_own_server(self):
        code, out = self.switch('alpha-synthetic.gguf')
        self.assertEqual(code, 0, out)
        first = self.recorded_pid()
        self.assertTrue(first and self.alive(first))
        self.assertEqual(self.served(), 'alpha-synthetic.gguf')
        code, out = self.switch('beta-synthetic.gguf')
        self.assertEqual(code, 0, out)
        second = self.recorded_pid()
        self.assertNotEqual(first, second)
        self.assertFalse(self.alive(first))
        self.assertEqual(self.served(), 'beta-synthetic.gguf')
        self.assertIn('Model loaded: beta-synthetic.gguf', out)

    def test_failed_startup_is_reported_with_its_cause(self):
        code, out = self.switch('broken-synthetic.gguf')
        self.assertEqual(code, 1, out)
        self.assertIn('ERROR: llama-server exited during startup', out)
        self.assertIn("does not know this model's architecture", out)
        self.assertIsNone(self.recorded_pid())

    def test_unrelated_listener_on_the_port_is_not_stopped(self):
        other = subprocess.Popen([sys.executable, '-m', 'http.server', str(self.port), '--bind', '127.0.0.1'],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.others.append(other)
        deadline = time.time() + 10
        while time.time() < deadline and not self.listening():
            time.sleep(0.1)
        code, out = self.switch('alpha-synthetic.gguf')
        self.assertEqual(code, 3, out)
        self.assertIn('Refusing to stop it', out)
        self.assertIsNone(other.poll())

    def test_stale_pid_naming_an_unrelated_process_is_left_alone(self):
        other = subprocess.Popen(['sleep', '60'])
        self.others.append(other)
        self.pid_file.parent.mkdir(parents=True, exist_ok=True)
        self.pid_file.write_text(str(other.pid))
        code, out = self.switch('alpha-synthetic.gguf')
        self.assertEqual(code, 0, out)
        self.assertIn('is alive but is not llama-server', out)
        self.assertIsNone(other.poll())
        self.assertNotEqual(self.recorded_pid(), other.pid)

    def test_external_mode_never_starts_or_stops_a_server(self):
        code, out = self.switch('alpha-synthetic.gguf', LLAMA_SERVER_MODE='external')
        self.assertEqual(code, 3, out)
        self.assertIsNone(self.recorded_pid())
        self.assertFalse(self.listening())


if __name__ == '__main__':
    unittest.main()
