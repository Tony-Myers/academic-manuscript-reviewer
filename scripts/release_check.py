#!/usr/bin/env python3
"""Read-only pre-publication check for the Academic Manuscript Reviewer.

Run from the repository root before creating or pushing a public repository:

    python3 scripts/release_check.py            # the files Git would publish
    python3 scripts/release_check.py --history  # also every blob in the history

It changes nothing: no file is written, no Git command that modifies state is
run and nothing is sent over the network. It reports:

  - files that would be published (tracked, plus untracked files that are not
    ignored) whose names suggest local, confidential or generated material;
  - text that looks like a credential, a personal path, an e-mail address, a
    manuscript or submission identifier, or the former development repository;
  - required files (LICENSE, NOTICE, README) and executable permissions;
  - with --history, the same content checks on every blob in every commit.

A clean result is not proof that nothing confidential is present: pattern
checks cannot recognise arbitrary manuscript text. Read the diff of anything
you publish. Exit status: 0 no findings, 1 findings, 2 could not run.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APACHE_SHA256 = "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30"
EXECUTABLE = ("run_review.sh", "start_server.sh", "start_llama_server.sh",
              "scripts/qwen_service.sh", "scripts/model_aliases.sh", "scripts/check_install.py",
              "scripts/release_check.py")
REQUIRED = ("LICENSE", "NOTICE", "README.md", "local.env.example", "requirements.txt")

RISKY_PATH = re.compile(
    r"(^|/)(local\.env(\..*)?|\.env(\..*)?|logs/|run/|local_results/|reviews/|sessions/|uploads/|"
    r"inputs/|reports/|backups/|\.venv/|__pycache__/|\.DS_Store)|"
    r"\.(pdf|docx?|rtf|odt|xlsx?|pptx|gguf|safetensors|log|pem|key|p12|bak)$", re.I)
ALLOWED_PATH = {"local.env.example"}

CONTENT_RULES = [
    ("personal or absolute home path", re.compile(r"/Users/[A-Za-z]|/home/[a-z][a-z0-9_-]+/")),
    ("private key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("GitHub token", re.compile(r"\b(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}")),
    ("API key", re.compile(r"\bsk-[A-Za-z0-9]{20,}|\bhf_[A-Za-z0-9]{20,}|\bAKIA[0-9A-Z]{16}\b")),
    ("e-mail address", re.compile(r"\b[A-Za-z0-9._%+-]+@(?!example\.(?:org|com)\b)[A-Za-z0-9.-]+\.[a-z]{2,}\b")),
    ("former development repository", re.compile(r"Qwen-reviewer|qwen35-review|qwen-reviewer-public", re.I)),
    ("possible manuscript or submission identifier",
     re.compile(r"\b(?:e\d{6}|[A-Z]{2,6}-\d{4}-\d{3,6}(?:\.R\d)?|manuscript\s+(?:ID|no\.|number)\b\s*[:#]?\s*\w+)\b")),
]
CITATION = re.compile(r"^\s*-?\s*cite:|doi\.org/|\bdoi:", re.I)
# Paths whose matches are upstream third-party notices, not this project's text.
CONTENT_ALLOW = (re.compile(r"^third_party/"), re.compile(r"^app/vendor/"),
                 re.compile(r"^scripts/release_check\.py$"))


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True,
                          text=True).stdout


def published_files() -> list:
    tracked = git("ls-files", "-z").split("\0")
    untracked = git("ls-files", "-z", "--others", "--exclude-standard").split("\0")
    return sorted({f for f in tracked + untracked if f})


def scan_text(label: str, data: bytes, findings: list) -> None:
    if b"\0" in data[:4096]:
        return
    text = data.decode("utf-8", "replace")
    for name, rule in CONTENT_RULES:
        for m in rule.finditer(text):
            line = text.count("\n", 0, m.start()) + 1
            content = text.splitlines()[line - 1] if text else ""
            if name.startswith("possible manuscript") and CITATION.search(content):
                continue  # an article number in a published reference
            findings.append(f"{label}:{line}: {name}: {m.group(0)[:60]!r}")


def allowed(path: str) -> bool:
    return any(rule.search(path) for rule in CONTENT_ALLOW)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--history", action="store_true", help="also scan every blob in the Git history")
    args = parser.parse_args()
    try:
        files = published_files()
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"Could not list files with Git: {exc}", file=sys.stderr)
        return 2
    findings = []

    for f in files:
        if RISKY_PATH.search(f) and f not in ALLOWED_PATH:
            findings.append(f"{f}: would be published but looks local, confidential or generated")
    for f in files:
        path = ROOT / f
        if path.is_file() and not allowed(f) and path.stat().st_size < 5_000_000:
            scan_text(f, path.read_bytes(), findings)

    for f in REQUIRED:
        if not (ROOT / f).is_file():
            findings.append(f"{f}: missing")
    licence = ROOT / "LICENSE"
    if licence.is_file() and hashlib.sha256(licence.read_bytes()).hexdigest() != APACHE_SHA256:
        findings.append("LICENSE: not byte-identical to the Apache License 2.0 text")
    notice = ROOT / "NOTICE"
    if notice.is_file() and "TO BE CONFIRMED" in notice.read_text("utf-8", "replace"):
        findings.append("NOTICE: copyright holder still marked TO BE CONFIRMED")

    modes = {}
    for line in git("ls-files", "-s").splitlines():
        meta, name = line.split("\t", 1)
        modes[name] = meta.split()[0]
    for f in EXECUTABLE:
        if f in modes and modes[f] != "100755":
            findings.append(f"{f}: tracked without the executable bit (mode {modes[f]})")
        elif f not in modes and (ROOT / f).exists():
            note = "" if (ROOT / f).stat().st_mode & 0o111 else " and is not executable"
            findings.append(f"{f}: not yet tracked{note}")

    commits = git("rev-list", "--all").split()
    print(f"Files that would be published: {len(files)}")
    print(f"Commits in this repository's history: {len(commits)}")
    if args.history:
        seen = set()
        for commit in commits:
            for line in git("ls-tree", "-r", commit).splitlines():
                meta, name = line.split("\t", 1)
                sha = meta.split()[2]
                if sha in seen or allowed(name):
                    continue
                seen.add(sha)
                if RISKY_PATH.search(name) and name not in ALLOWED_PATH:
                    findings.append(f"history {commit[:7]}:{name}: path looks local or confidential")
                data = subprocess.run(["git", "cat-file", "blob", sha], cwd=ROOT, check=True,
                                      capture_output=True).stdout
                scan_text(f"history {commit[:7]}:{name}", data, findings)
        print(f"History blobs scanned: {len(seen)}")

    for f in findings:
        print("FINDING", f)
    print(f"{len(findings)} finding(s).", "A clean result does not prove the absence of confidential "
          "text; review what you publish.")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
