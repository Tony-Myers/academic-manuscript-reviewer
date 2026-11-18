"""Fresh-installation and runtime-import checks.

Independently authored for this release candidate. No model is loaded and
nothing is installed: these read the source and run scripts/check_install.py.
"""
import ast
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECK = ROOT / 'scripts' / 'check_install.py'

# Import name -> distribution name in requirements.txt.
DISTRIBUTION = {'fastapi': 'fastapi', 'starlette': 'fastapi', 'uvicorn': 'uvicorn',
                'multipart': 'python-multipart', 'python_multipart': 'python-multipart',
                'pdfplumber': 'pdfplumber', 'docx': 'python-docx', 'openpyxl': 'openpyxl',
                'pypdf': 'pypdf', 'httpcore': 'httpcore', 'pypdfium2': 'pypdfium2'}
# Removed from the standard library in Python 3.13 (PEP 594) or earlier.
REMOVED_IN_313 = {'aifc', 'audioop', 'cgi', 'cgitb', 'chunk', 'crypt', 'imghdr', 'mailcap', 'msilib',
                  'nis', 'nntplib', 'ossaudiodev', 'pipes', 'sndhdr', 'spwd', 'sunau', 'telnetlib',
                  'uu', 'xdrlib', 'lib2to3', 'distutils', 'imp', 'asynchat', 'asyncore', 'smtpd'}


def requirement_names(*files):
    names = set()
    for name in files:
        for line in (ROOT / name).read_text().splitlines():
            line = line.split('#')[0].strip()
            if line and not line.startswith('-r'):
                names.add(re.split(r'[=<>!~\[ ]', line)[0].lower())
    return names


def startup_imports(path):
    """Third-party modules imported when the module is loaded (not inside
    functions or classes, which are optional or lazy)."""
    found = set()

    def visit(nodes):
        for node in nodes:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            if isinstance(node, ast.Import):
                found.update(a.name.split('.')[0] for a in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                found.add(node.module.split('.')[0])
            for field in ('body', 'orelse', 'finalbody', 'handlers'):
                visit(getattr(node, field, []) or [])
    visit(ast.parse(path.read_text()).body)
    local = {p.stem for p in (ROOT / 'app').glob('*.py')}
    return {m for m in found if m not in sys.stdlib_module_names and m not in local and m != '__future__'}


def all_imports(path):
    found = set()
    for node in ast.walk(ast.parse(path.read_text())):
        if isinstance(node, ast.Import):
            found.update(a.name.split('.')[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            found.add(node.module.split('.')[0])
    return found


class RuntimeDependencies(unittest.TestCase):
    def test_requirements_cover_every_startup_import(self):
        runtime = requirement_names('requirements.txt')
        uncovered = {}
        for path in sorted((ROOT / 'app').glob('*.py')):
            for module in startup_imports(path):
                dist = DISTRIBUTION.get(module)
                if dist is None or dist not in runtime:
                    uncovered.setdefault(module, []).append(path.name)
        self.assertEqual(uncovered, {}, 'imported at start-up but not in requirements.txt')

    def test_httpcore_is_a_runtime_requirement_not_only_a_test_one(self):
        self.assertIn('httpcore', requirement_names('requirements.txt'))

    def test_check_install_passes_in_this_environment(self):
        run = subprocess.run([sys.executable, str(CHECK)], capture_output=True, text=True, timeout=120)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertIn('application modules import', run.stdout)

    def test_check_install_names_a_missing_package(self):
        # Make httpcore absent, as in a fresh runtime-only install: find_spec
        # returns None and importing it raises ModuleNotFoundError.
        blocker = ('import sys, runpy\n'
                   'sys.modules["httpcore"] = None\n'
                   f'sys.argv = [{str(CHECK)!r}, "--quiet"]\n'
                   f'runpy.run_path({str(CHECK)!r}, run_name="__main__")\n')
        run = subprocess.run([sys.executable, '-c', blocker], capture_output=True, text=True, timeout=120)
        self.assertEqual(run.returncode, 1, run.stderr)
        self.assertIn('Missing required package(s): httpcore', run.stderr)
        self.assertNotIn('Traceback', run.stderr)

    def test_no_module_removed_by_python_313(self):
        used = {}
        for path in list((ROOT / 'app').glob('*.py')) + list((ROOT / 'scripts').glob('*.py')):
            for module in all_imports(path) & REMOVED_IN_313:
                used.setdefault(module, []).append(path.name)
        self.assertEqual(used, {})

    def test_test_and_vision_requirements_include_the_runtime_ones(self):
        self.assertIn('-r requirements.txt', (ROOT / 'requirements-vision.txt').read_text())
        self.assertIn('-r requirements-vision.txt', (ROOT / 'requirements-test.txt').read_text())


if __name__ == '__main__':
    unittest.main()
