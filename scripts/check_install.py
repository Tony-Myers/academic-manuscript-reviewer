#!/usr/bin/env python3
"""
check_install.py -- can this Python environment run the application?

Run it with the application's own interpreter:

    .venv/bin/python scripts/check_install.py

It checks every package the application imports when it starts (the ones in
requirements.txt), then imports the application's server module itself, which
also catches a dependency missing from that list. Optional packages are
reported but do not fail the check. No model is loaded, nothing is started and
nothing is written. Exit status: 0 ready, 1 a required package is missing.

The launchers run it before starting the app, so a missing package is named
here instead of surfacing as a traceback in the app log.
"""
from __future__ import annotations

import importlib
import importlib.util
import sys
from pathlib import Path

# (distribution in requirements.txt, module the application imports)
REQUIRED = [
    ("fastapi", "fastapi"),
    ("uvicorn", "uvicorn"),
    ("python-multipart", "python_multipart"),
    ("pdfplumber", "pdfplumber"),
    ("python-docx", "docx"),
    ("openpyxl", "openpyxl"),
    ("pypdf", "pypdf"),
    ("httpcore", "httpcore"),
]
# (distribution, module, what is lost without it)
OPTIONAL = [
    ("pypdfium2", "pypdfium2",
     "Vision page rendering (install requirements-vision.txt); reviews run on the text layer"),
]
TESTED_PYTHON = (3, 11)

APP_DIR = Path(__file__).resolve().parent.parent / "app"


def missing_required() -> list:
    return [dist for dist, module in REQUIRED if importlib.util.find_spec(module) is None]


def main(argv: list) -> int:
    quiet = "--quiet" in argv
    problems = 0

    def say(text: str) -> None:
        if not quiet:
            print(text)

    say(f"Python {sys.version.split()[0]} at {sys.executable}")
    if sys.version_info[:2] < TESTED_PYTHON:
        say(f"  note  Python {TESTED_PYTHON[0]}.{TESTED_PYTHON[1]} or newer is the documented requirement")

    missing = missing_required()
    for dist, module in REQUIRED:
        say(f"  {'MISS' if dist in missing else 'ok  '}  {dist} (import {module})")
    for dist, module, loss in OPTIONAL:
        if importlib.util.find_spec(module) is None:
            say(f"  info  {dist} not installed: {loss}")
        else:
            say(f"  ok    {dist} (optional)")

    if missing:
        problems = 1
        print("Missing required package(s): " + ", ".join(missing), file=sys.stderr)
        print(f"Fix: {sys.executable} -m pip install -r requirements.txt", file=sys.stderr)
    else:
        # Importing the server is the definitive test: it imports everything
        # the application needs at start-up, including anything not listed.
        sys.path.insert(0, str(APP_DIR))
        try:
            importlib.import_module("server")
        except ModuleNotFoundError as exc:
            problems = 1
            print(f"The application cannot start: module '{exc.name}' is not installed.", file=sys.stderr)
            print(f"Fix: {sys.executable} -m pip install -r requirements.txt "
                  "(and report the missing module if it is not listed there)", file=sys.stderr)
        except Exception as exc:                                # noqa: BLE001
            problems = 1
            print(f"The application cannot start: importing it failed ({type(exc).__name__}: {exc}).",
                  file=sys.stderr)
        else:
            say("  ok    application modules import")

    say("Ready." if not problems else "Not ready: see the messages above.")
    return problems


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
