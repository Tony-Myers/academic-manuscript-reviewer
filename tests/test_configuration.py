"""Review-store configuration, its persistence across starts and restarts,
and executable permissions of the launch scripts.

Independently authored for this release candidate. The service script runs in
a temporary copy of the project with a stand-in interpreter that records the
environment the app would receive and answers the readiness check; no real app,
model or llama-server is started. All paths are temporary.
"""
import json
import os
import shutil
import socket
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'app'))
import review_store as store  # noqa: E402

EXECUTABLE = ['run_review.sh', 'start_server.sh', 'start_llama_server.sh',
              'scripts/qwen_service.sh', 'scripts/check_install.py', 'scripts/release_check.py']

# Stands in for .venv/bin/python. The preflight check passes; the app launch
# records its environment and serves /v1/models so the service sees it ready.
FAKE_PYTHON = r'''#!/bin/bash
case "$1" in
  */check_install.py) exit 0 ;;
  */app/server.py)
    python3 -c 'import json, os, sys; json.dump(dict(os.environ), open(sys.argv[1], "w"))' "$FAKE_ENV_OUT"
    port=8090; prev=""
    for a in "$@"; do [[ "$prev" == "--port" ]] && port="$a"; prev="$a"; done
    exec python3 -c '
import http.server, sys
class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers(); self.wfile.write(b"{}")
    def log_message(self, *a): pass
http.server.HTTPServer(("127.0.0.1", int(sys.argv[1])), H).serve_forever()
' "$port" "$2" "app/server.py" ;;
esac
exec python3 "$@"
'''


def free_port():
    with socket.socket() as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


@unittest.skipUnless(all(shutil.which(t) for t in ('bash', 'curl', 'lsof', 'ps')),
                     'bash, curl, lsof and ps are needed for the service-script tests')
class ReviewStoreReachesTheApp(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='store-config-test-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.project = self.root / 'project'
        (self.project / 'scripts').mkdir(parents=True)
        (self.project / 'app').mkdir()
        (self.project / 'app' / 'server.py').write_text('# placeholder; never run\n')
        for name in ('qwen_service.sh', 'model_aliases.sh'):
            shutil.copy2(ROOT / 'scripts' / name, self.project / 'scripts' / name)
        (self.project / 'scripts' / 'check_install.py').write_text('')
        venv = self.project / '.venv' / 'bin'
        venv.mkdir(parents=True)
        (venv / 'python').write_text(FAKE_PYTHON)
        (venv / 'python').chmod(0o755)
        self.env_out = self.root / 'app-env.json'
        self.app_port = free_port()
        self.env = {k: v for k, v in os.environ.items() if not k.startswith(('LLAMA_', 'QWEN_'))}
        self.env.update(HOME=str(self.root), FAKE_ENV_OUT=str(self.env_out),
                        QWEN_STARTUP_TIMEOUT='20')
        self.addCleanup(self.service, 'stop')

    def local_env(self, *lines):
        base = [': "${LLAMA_SERVER_MODE:=external}"',
                f': "${{LLAMA_SERVER_URL:=http://127.0.0.1:{free_port()}}}"',
                f': "${{QWEN_APP_PORT:={self.app_port}}}"']
        (self.project / 'local.env').write_text('\n'.join(base + list(lines)) + '\n')

    def service(self, command, env=None):
        run = subprocess.run(['bash', str(self.project / 'scripts' / 'qwen_service.sh'), command, '--no-open'],
                             env=env or self.env, capture_output=True, text=True, timeout=90)
        return run.returncode, run.stdout + run.stderr

    def app_env(self):
        return json.loads(self.env_out.read_text())

    def test_store_from_local_env_reaches_the_app_and_survives_restarts(self):
        store_path = str(self.root / 'My Review Store' / 'sessions')   # a path with spaces
        self.local_env(f': "${{QWEN_REVIEW_STORE:={store_path}}}"',
                       f': "${{LLAMA_MODEL_DIRS:={self.root}/models}}"')
        code, out = self.service('start')
        self.assertEqual(code, 0, out)
        first = self.app_env()
        self.assertEqual(first['QWEN_REVIEW_STORE'], store_path)
        self.assertEqual(first['LLAMA_MODEL_DIRS'], f'{self.root}/models')  # other local.env settings too
        self.assertIn('Review store: ' + store_path, out)

        self.env_out.unlink()
        code, out = self.service('restart')
        self.assertEqual(code, 0, out)
        self.assertEqual(self.app_env()['QWEN_REVIEW_STORE'], store_path)

        # A restart started from the browser runs the service with the app's
        # own environment (and local.env is read again).
        browser_env = dict(self.app_env())
        self.env_out.unlink()
        code, out = self.service('restart', env=browser_env)
        self.assertEqual(code, 0, out)
        self.assertEqual(self.app_env()['QWEN_REVIEW_STORE'], store_path)

    def test_store_from_the_environment_alone_also_reaches_the_app(self):
        self.local_env()
        store_path = str(self.root / 'store from shell')
        code, out = self.service('start', env=dict(self.env, QWEN_REVIEW_STORE=store_path))
        self.assertEqual(code, 0, out)
        self.assertEqual(self.app_env()['QWEN_REVIEW_STORE'], store_path)

    def test_unset_keeps_the_default_and_off_still_disables(self):
        self.local_env()
        code, out = self.service('start')
        self.assertEqual(code, 0, out)
        self.assertEqual(self.app_env().get('QWEN_REVIEW_STORE', ''), '')
        self.service('stop')
        self.local_env(': "${QWEN_REVIEW_STORE:=off}"')
        self.env_out.unlink()
        code, out = self.service('start')
        self.assertEqual(code, 0, out)
        self.assertEqual(self.app_env()['QWEN_REVIEW_STORE'], 'off')


    def test_every_launcher_setting_reaches_the_app(self):
        # A comment between continuation lines once cut the launch command
        # short, so QWEN_SERVICE_MANAGED and QWEN_APP_PORT never reached the app.
        self.local_env()
        env = dict(self.env)
        code, out = self.service('start', env=env)
        self.assertEqual(code, 0, out)
        app = self.app_env()
        self.assertEqual(app['QWEN_SERVICE_MANAGED'], '1')
        self.assertEqual(app['QWEN_APP_PORT'], str(self.app_port))
        for name in ('LLAMA_SERVER_MODE', 'LLAMA_SERVER_URL', 'QWEN_LLM_BACKEND', 'REVIEW_PASSES',
                     'QWEN_VISION_TABLES', 'LLAMA_SERVER_PORT', 'LLAMA_SERVER_CTX'):
            self.assertIn(name, app)

    def test_restart_app_restarts_only_the_app(self):
        store_path = str(self.root / 'kept store')
        self.local_env(f': "${{QWEN_REVIEW_STORE:={store_path}}}"')
        code, out = self.service('start')
        self.assertEqual(code, 0, out)
        first_pid = (self.project / 'run' / 'app-server.pid').read_text().strip()
        self.env_out.unlink()
        code, out = self.service('restart-app')
        self.assertEqual(code, 0, out)
        self.assertIn('the model server is left running', out)
        self.assertNotIn('Stopping Qwen review', out)          # the full stop path was not used
        self.assertNotEqual((self.project / 'run' / 'app-server.pid').read_text().strip(), first_pid)
        self.assertEqual(self.app_env()['QWEN_REVIEW_STORE'], store_path)
        self.assertEqual(self.app_env()['QWEN_SERVICE_MANAGED'], '1')


class ShellScriptSyntax(unittest.TestCase):
    SCRIPTS = ['run_review.sh', 'start_server.sh', 'start_llama_server.sh',
               'scripts/qwen_service.sh', 'scripts/model_aliases.sh']

    def test_no_comment_inside_a_continued_command(self):
        for name in self.SCRIPTS:
            lines = (ROOT / name).read_text().splitlines()
            for n, (prev, line) in enumerate(zip(lines, lines[1:]), start=2):
                if prev.rstrip().endswith('\\') and line.lstrip().startswith('#'):
                    self.fail(f'{name}:{n}: a comment after a continuation line ends the command')

    @unittest.skipUnless(shutil.which('bash'), 'bash is needed')
    def test_scripts_parse(self):
        for name in self.SCRIPTS:
            run = subprocess.run(['bash', '-n', str(ROOT / name)], capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, name + ': ' + run.stderr)


class StoreRootInTheApp(unittest.TestCase):
    def test_configured_store_is_used_as_given_and_never_replaced_by_the_default(self):
        default = ROOT / 'reviews' / 'sessions'
        with tempfile.TemporaryDirectory(prefix='store root ') as tmp:
            missing = Path(tmp) / 'not created yet'
            os.environ['QWEN_REVIEW_STORE'] = str(missing)
            try:
                self.assertEqual(store.store_root(), missing)
                self.assertEqual(store.list_sessions(), [])   # empty, not the default store's reviews
            finally:
                del os.environ['QWEN_REVIEW_STORE']
        os.environ['QWEN_REVIEW_STORE'] = ''
        try:
            self.assertEqual(store.store_root(), default)
        finally:
            del os.environ['QWEN_REVIEW_STORE']


class MissingStoreIsReported(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='store status ')
        self.addCleanup(self.tmp.cleanup)
        self.saved = os.environ.get('QWEN_REVIEW_STORE')
        self.addCleanup(self.restore)

    def restore(self):
        if self.saved is None:
            os.environ.pop('QWEN_REVIEW_STORE', None)
        else:
            os.environ['QWEN_REVIEW_STORE'] = self.saved

    def test_configured_store_on_a_missing_drive_is_an_error_not_an_empty_list(self):
        missing = Path(self.tmp.name) / 'Unmounted Drive' / 'reviews'
        os.environ['QWEN_REVIEW_STORE'] = str(missing)
        status = store.store_status()
        self.assertFalse(status['available'])
        self.assertIn('does not exist', status['error'])
        self.assertIn('The default store is not used instead', status['error'])
        sys.path.insert(0, str(ROOT / 'tests'))
        import fixtures as fx
        with self.assertRaises(store.StoreError) as raised:
            store.save_completed('ab12cd34ef56', fx.job(), cards=None, manuscript_sha256=None)
        self.assertIn('neither does its parent folder', str(raised.exception))
        self.assertFalse(missing.exists())                       # nothing created elsewhere

    def test_configured_store_is_created_when_its_parent_exists(self):
        target = Path(self.tmp.name) / 'new store'
        os.environ['QWEN_REVIEW_STORE'] = str(target)
        self.assertIn('does not exist', store.store_status()['error'])
        sys.path.insert(0, str(ROOT / 'tests'))
        import fixtures as fx
        store.save_completed('ab12cd34ef56', fx.job(), cards=None, manuscript_sha256=None)
        self.assertTrue((target / 'ab12cd34ef56').is_dir())
        self.assertEqual(store.store_status()['error'], '')



sys.path.insert(0, str(ROOT / 'tests'))
from test_release import Isolated  # noqa: E402


class ReviewsApiReportsTheStore(Isolated):
    def test_reviews_api_reports_the_store_problem(self):
        from unittest.mock import patch
        import server
        from fastapi.testclient import TestClient
        gone = str(self.root / 'gone' / 'sessions')
        with patch.dict(os.environ, {'QWEN_REVIEW_STORE': gone}), TestClient(server.app) as client:
            body = client.get('/api/reviews').json()
        self.assertEqual(body['reviews'], [])
        self.assertIn('does not exist', body['store']['error'])
        self.assertTrue(body['store']['configured'])
        self.assertIsNone(body['last_save_error'])


class ExecutablePermissions(unittest.TestCase):
    def test_scripts_are_executable_on_disk(self):
        missing = [name for name in EXECUTABLE
                   if not (ROOT / name).stat().st_mode & stat.S_IXUSR]
        self.assertEqual(missing, [], 'restore with: chmod +x ' + ' '.join(missing))

    def test_git_records_the_executable_bit(self):
        if not shutil.which('git') or not (ROOT / '.git').exists():
            self.skipTest('not a Git checkout')
        run = subprocess.run(['git', '-C', str(ROOT), 'ls-files', '-s', '--', *EXECUTABLE],
                             capture_output=True, text=True)
        if run.returncode != 0:
            self.skipTest('git ls-files failed: ' + run.stderr.strip())
        modes = {line.split('\t', 1)[1]: line.split()[0] for line in run.stdout.splitlines()}
        wrong = {name: mode for name, mode in modes.items() if mode != '100755'}
        self.assertEqual(wrong, {}, 'tracked without the executable bit; a clean checkout would '
                                    'lose it (fix with: git update-index --chmod=+x <file>)')
        file_mode = subprocess.run(['git', '-C', str(ROOT), 'config', '--get', 'core.fileMode'],
                                   capture_output=True, text=True).stdout.strip()
        untracked = [name for name in EXECUTABLE if name not in modes]
        if untracked and file_mode == 'false':
            self.fail('core.fileMode is false, so adding ' + ', '.join(untracked) +
                      ' would not record its executable bit')

    def test_browser_actions_do_not_depend_on_the_executable_bit(self):
        import server
        command = server._service_command('status')
        self.assertTrue(command[0].endswith('bash'))
        self.assertEqual(command[1], str(ROOT / 'scripts' / 'qwen_service.sh'))


if __name__ == '__main__':
    unittest.main()
