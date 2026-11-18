#!/usr/bin/env python3
"""
Unified local server for chat and manuscript review.

Loads the model once (llama.cpp for GGUF, mlx_lm for MLX repo ids) and exposes:
  - GET  /                       → serves the web UI
  - POST /v1/chat/completions                 → OpenAI-compatible chat
  - POST /api/chat/academic/draft             → local structured academic draft
  - POST /api/chat/academic/verify-reference  → bibliographic verification
  - POST /api/review                          → file upload → review pipeline
  - GET  /api/review/status/{id}              → SSE progress stream
  - GET  /v1/models                           → model info (for status dot)
  - GET  /api/server/status                   → mode, connection, loaded model
  - POST /api/server/restart                  → switch model (managed only)
"""

from __future__ import annotations

import asyncio
import functools
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import traceback
import uuid
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from starlette.responses import StreamingResponse

import uvicorn

# ---------------------------------------------------------------------------
# Resolve the review pipeline (same directory or via --pipeline-dir)
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import review_pipeline as rp
import design_expectations as de  # noqa: E402
import reviewer_notes as notes  # noqa: E402  standard library only, no model
import llm_backend  # noqa: E402
import model_server as ms  # noqa: E402  connection status and model switching
import evidence_availability as ea  # host-owned sidecar, never report prose
import source_verification as sv  # one source-grounded check after the merge
import evidence_cards as ec  # reviewer-facing cards; built from stored records, no model call
import synthesis_concern_accounting as sca  # observational, no model or review changes
import review_store as rs  # completed reviews saved as local files (reviews/sessions), never synced
import review_links as rl  # deterministic links between appraisal, cards and appendix; no model
import decisions_report as dreport  # reviewer-decisions Markdown record; deterministic, no model
import appendix_view  # reviewer-facing appendix rendered from saved data; deterministic, no model
import print_view  # dedicated Evidence Cards print page; deterministic, no model
import academic_chat  # noqa: E402
import academic_check_further  # noqa: E402
import academic_claim_coverage  # noqa: E402
import academic_claims  # noqa: E402
import academic_claim_assessor  # noqa: E402
import academic_methodology  # noqa: E402
import academic_orchestrator  # noqa: E402
import academic_reconciliation  # noqa: E402
import academic_reconciliation_orchestrator  # noqa: E402
from academic_tools import (  # noqa: E402
    get_openalex_work_by_doi,
    verify_academic_reference,
)
from llm_backend import (  # noqa: E402
    BackendError,
    current_backend,
    generate,
    load,
    make_sampler,
    set_backend,
)

# ---------------------------------------------------------------------------
# Reviewer notes: the second thing a reviewer asks about
# ---------------------------------------------------------------------------
# The manuscript mode answers from this paper and refuses to go outside it. A
# reviewer's other question -- whether an R-hat of 1.05 is acceptable, what a
# credible interval excluding zero does and does not license -- is not about
# the paper at all, and the manuscript mode cannot answer it by design.
#
# Retrieval is the default and reasoning is not offered. The model is given
# numbered passages and told to answer from them or to say that they do not
# settle the question. Two further provenances are already named below --
# model reasoning, and model reasoning supported by a verified reference --
# because the interface should not have to change when they are added. Neither
# is reachable today, and neither should be until the logs written here show
# how often retrieval genuinely falls short and on what.

NOTES_PASSAGES = 3
NOTES_MAX_TOKENS = 700
NOTES_LOG_PATH = SCRIPT_DIR.parent / "logs" / "reviewer-notes-chat.jsonl"

# The provenance vocabulary. Adding a value here and a label is the whole of
# what a new source costs the interface.
SOURCE_MANUSCRIPT = "manuscript"
SOURCE_NOTES = "reviewer_notes"
SOURCE_REASONING = "model_reasoning"                       # reserved
SOURCE_REASONING_REF = "model_reasoning_with_reference"    # reserved
SOURCE_LABELS = {
    SOURCE_MANUSCRIPT: "Source: manuscript",
    SOURCE_NOTES: "Source: reviewer notes",
    SOURCE_REASONING: "Source: model reasoning",
    SOURCE_REASONING_REF: "Source: model reasoning + verified reference",
}

NOTES_SYSTEM = """You are helping a peer reviewer who has just finished reading a report on a manuscript.

Numbered passages from a set of reviewer notes follow. Answer the question using those passages and nothing else. Do not draw on anything you know that is not in them, and do not fill a gap in them with your own explanation.

You have not read the manuscript. Do not say what its authors did, or should have done. Answer the general methodological question and leave the judgement about this paper to the reviewer.

Cite nothing. Do not name papers, books, authors or years, and do not place quotation marks around anything that is not in the passages above. If a passage names a source, you may repeat what the passage says about it; you may not add one. Tested on this model, unprompted references came out misattributed, wrong in four metadata fields, and in one case a quotation that does not exist, at a page that does, in a book that does.

Finish your reply with a line naming every passage you drew on, in this form:

    Used: [1], [3]

If the passages do not settle the question, do not infer an answer. Say in one sentence what they do not cover, and finish with:

    Used: none"""

_notes_index = None
_notes_index_lock = threading.Lock()
_notes_log_lock = threading.Lock()


def get_notes_index():
    """Build the notes index once. It costs milliseconds and holds no model."""
    global _notes_index
    with _notes_index_lock:
        if _notes_index is None:
            _notes_index = notes.NotesIndex()
        return _notes_index


def provenance(source: str, passages=None, used=None, resolved: bool = True,
               reference=None) -> dict:
    """
    Where an answer came from, in the shape every source will use.

    `reference` is reserved for a verified citation drawn from a curated
    registry; nothing populates it yet, and a model must never fill it in.
    """
    return {
        "source": source,
        "label": SOURCE_LABELS.get(source, "Source: unknown"),
        "passages": passages or [],
        "used": used or [],
        "resolved": bool(resolved),
        "reference": reference,
    }


# `resolved` answers one question only: did this source settle what was asked.
# It is not a quality mark. In the manuscript mode the citation check is what
# reports whether quotations were located, and it has its own display; a
# quotation correctly relabelled as coming from the review rather than the
# paper is a note about provenance, not a failure to answer, and marking such
# an answer "did not settle the question" told the reader the opposite of the
# truth.


def parse_used(answer: str):
    """
    Split the trailing "Used:" line off an answer.

    Returns (answer without that line, indices used, the model said none,
    the line was found at all). The last flag matters: a missing line is not
    the same as a model reporting that nothing applied, and conflating them
    would put a parsing failure into the record as evidence about the notes.
    """
    lines = (answer or "").rstrip().split("\n")
    for i in range(len(lines) - 1, -1, -1):
        stripped = lines[i].strip()
        if not stripped:
            continue
        if stripped.lower().startswith("used:"):
            body = stripped[5:].strip()
            rest = "\n".join(lines[:i]).rstrip()
            if body.lower().startswith("none"):
                return rest, [], True, True
            found = [int(n) for n in re.findall(r"\[?(\d+)\]?", body)]
            return rest, found, not found, True
        break
    return (answer or "").rstrip(), [], False, False


def log_notes_interaction(record: dict) -> None:
    """
    Append one interaction to logs/, for inspection after a few reviews.

    Best effort: a chat answer must not fail because a log line could not be
    written. logs/ is excluded from version control, which is where anything
    quoting an unpublished manuscript belongs.
    """
    try:
        NOTES_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(record, ensure_ascii=False)
        with _notes_log_lock:
            with open(NOTES_LOG_PATH, "a", encoding="utf-8") as fh:
                fh.write(line + "\n")
    except Exception as exc:  # pragma: no cover - logging must never raise
        print(f"[notes] could not write the interaction log: {exc}")


def answer_notes_question(question: str, job_id: str = "") -> dict:
    """
    Answer one methodological question from the reviewer notes alone.

    Returns the same shape the manuscript mode returns, so the interface does
    not branch on the source.
    """
    index = get_notes_index()
    hits = index.search(question, NOTES_PASSAGES)
    retrieved = [{"note": h.note, "heading": h.heading, "score": h.score}
                 for h in hits]

    if not hits:
        # Nothing scored above zero. Saying so is the answer; the alternative
        # is the least bad passage presented as though it were relevant.
        answer = ("Nothing in the reviewer notes bears on that question, so "
                  "there is nothing to show you. The notes cover statistical "
                  "reporting and interpretation, not the manuscript itself.")
        log_notes_interaction({
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "job_id": job_id,
            "mode": SOURCE_NOTES, "question": question, "retrieved": [],
            "used": [], "no_suitable_note": True, "used_line_found": None,
            "answer": answer, "model": MODEL_NAME,
            "pipeline": rp.PIPELINE_VERSION,
        })
        return {
            "answer": answer,
            "provenance": provenance(SOURCE_NOTES, [], [], resolved=False),
            "check": "", "problems": [], "passages": 0,
        }

    numbered = "\n\n".join(
        f"[{i + 1}] {h.note} - {h.heading}\n{h.text}"
        for i, h in enumerate(hits)
    )
    user_text = (f"{NOTES_SYSTEM}\n\nPassages from the reviewer notes:\n"
                 f'"""\n{numbered}\n"""\n\nQuestion: {question}')

    prompt = rp.apply_chat_template_compat(tokenizer, user_text)
    out = generate(model, tokenizer, prompt=prompt, max_tokens=NOTES_MAX_TOKENS,
                   sampler=rp.make_default_sampler(), verbose=False)
    answer, used_idx, said_none, line_found = parse_used(rp.clean_model_output(out))

    used = [retrieved[i - 1] for i in used_idx if 1 <= i <= len(retrieved)]
    log_notes_interaction({
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "job_id": job_id,
        "mode": SOURCE_NOTES, "question": question, "retrieved": retrieved,
        "used": used, "no_suitable_note": said_none,
        "used_line_found": line_found, "answer": answer,
        "model": MODEL_NAME, "pipeline": rp.PIPELINE_VERSION,
    })
    return {
        "answer": answer,
        "provenance": provenance(SOURCE_NOTES, retrieved, used,
                                 resolved=not said_none),
        "check": "", "problems": [], "passages": len(retrieved),
    }


# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------
app = FastAPI(title="Local Qwen Server")


# ---------------------------------------------------------------------------
# Global state
# ---------------------------------------------------------------------------
MODEL_NAME = os.environ.get("MODEL_NAME", rp.MODEL_NAME)
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8080
model = None
tokenizer = None
# Review-wide thinking, vision, and reasoning accounting are context-local.
# Individual generations are serialised and bounded centrally by
# llm_backend.generate(), so the server does not maintain a second model lock.
restart_lock = threading.Lock()
restart_scheduled = False
# In-place model switches (managed llama-server only); the app stays running.
# It also counts model-dependent operations, so the two exclude each other.
model_switch = ms.ModelSwitch()
REVIEW_OPERATION = "manuscript appraisal"


def _model_operation(kind: str):
    """
    Register an endpoint as a model-dependent operation for its duration.

    Refused with 409 while a model is loading; while it runs, a model switch
    is refused. Applied below the route decorator, so FastAPI still sees the
    endpoint's own signature.
    """
    def decorate(endpoint):
        @functools.wraps(endpoint)
        async def guarded(*args, **kwargs):
            try:
                model_switch.acquire(kind)
            except ms.SwitchInProgress as exc:
                raise HTTPException(status_code=409, detail=str(exc)) from exc
            try:
                return await endpoint(*args, **kwargs)
            finally:
                model_switch.release(kind)
        return guarded
    return decorate


def _switch_blocked_reason() -> str:
    """Why a model switch must wait, or "" if nothing model-dependent runs."""
    active = model_switch.active_operations()
    if active:
        names = ", ".join(sorted(active))
        return (f"Model work is in progress ({names}). Wait for it to finish, "
                "or cancel it, before switching models.")
    if llm_backend.inference_in_progress():
        return ("A model generation is in progress. Wait for it to finish "
                "before switching models.")
    return ""

# In-flight review jobs: job_id → {status, progress, report, error}
review_jobs: dict = {}

HTML_PATH = SCRIPT_DIR / "chat.html"
ROOT_DIR = SCRIPT_DIR.parent
SERVICE_PATH = ROOT_DIR / "scripts" / "qwen_service.sh"

MODEL_CHOICES = [
    {
        "id": "qwen38",
        "label": "Qwen3.8 27B UD-Q4_K_XL (GGUF)",
        "model": rp.QWEN38_27B_GGUF,
        "aliases": ["27b-gguf", "gguf", "qwen38-27b"],
    },
    {
        "id": "flash",
        "label": "Qwen3.8 Flash-Next 3.84bpw (GGUF)",
        "model": rp.QWEN38_FLASH_NEXT_GGUF,
        "aliases": ["flash-next", "qwen38-flash"],
    },
    {
        "id": "35b",
        "label": "Qwen3.6 35B-A3B 4-bit",
        "model": "mlx-community/Qwen3.6-35B-A3B-4bit",
        "aliases": ["35b-4bit", "qwen35"],
    },
    {
        "id": "27b",
        "label": "Qwen3.6 27B 6-bit",
        "model": "mlx-community/Qwen3.6-27B-6bit",
        "aliases": ["27b-6bit", "qwen27"],
    },
    {
        "id": "27b-4bit",
        "label": "Qwen3.6 27B 4-bit",
        "model": "mlx-community/Qwen3.6-27B-4bit",
        "aliases": [],
    },
    {
        "id": "27b-8bit",
        "label": "Qwen3.6 27B 8-bit",
        "model": "mlx-community/Qwen3.6-27B-8bit",
        "aliases": [],
    },
    {
        "id": "gemma4",
        "label": "Gemma 4 26B-A4B IT 4-bit",
        "model": "mlx-community/gemma-4-26b-a4b-it-4bit",
        "aliases": ["gemma4-26b", "gemma4-26b-it"],
    },
    {
        "id": "gemma4-31b",
        "label": "Gemma 4 31B IT 4-bit",
        "model": "mlx-community/gemma-4-31b-it-4bit",
        "aliases": ["gemma4-31b-it"],
    },
]

# Aliases from the UI model list, folded in on top of the canonical table in
# review_pipeline so that "35b" means the same thing here, on the command line
# and in the launcher.
MODEL_ALIAS_MAP = dict(rp.MODEL_ALIASES)
MODEL_ALIAS_MAP.update({
    key.lower(): choice["model"]
    for choice in MODEL_CHOICES
    for key in [choice["id"], *choice["aliases"]]
})


def _model_header_lines() -> list:
    """
    The Model line, reporting what is loaded rather than what was requested.

    MODEL_NAME is this process's command-line argument. llama-server may hold
    something else -- a launcher that reused a running server, a server started
    by hand, a restart that failed after this process had already exited, or a
    model chosen in the browser without pressing Restart. The header then named
    a model that had not written a word of the review. When the two disagree
    the served model is reported, and the discrepancy is stated rather than
    quietly resolved.
    """
    configured = rp.model_display_name(MODEL_NAME)
    try:
        served = llm_backend.served_model_name()
    except Exception:                                           # noqa: BLE001
        served = ""
    if ms.connection_mode(MODEL_NAME) == ms.MODE_EXTERNAL:
        # An external server chooses its own model; what this process was
        # started with is not a claim about it.
        if served:
            return [f"Model: {served} (reported by an external llama-server)"]
        return [f"Model: not reported by the external llama-server at {ms.server_url()}"]
    if not served or served == Path(configured).name:
        return [f"Model: {configured}"]
    return [
        f"Model: {served}",
        f"WARNING: this app server was started with {Path(configured).name}, "
        f"but llama-server has {served} loaded, so {served} wrote this review. "
        f"If the other model was wanted, restart the service rather than "
        f"choosing it in the browser alone.",
    ]


def _hf_cache_root() -> Path:
    if os.environ.get("HF_HUB_CACHE"):
        return Path(os.environ["HF_HUB_CACHE"]).expanduser()
    if os.environ.get("HF_HOME"):
        return Path(os.environ["HF_HOME"]).expanduser() / "hub"
    return Path.home() / ".cache" / "huggingface" / "hub"


def _cached_snapshot_for_model(model_id: str) -> Optional[Path]:
    """Return a complete local snapshot/file path for a model id, if present."""
    # A GGUF model is a single file, so an existence check is the whole test.
    if model_id.lower().endswith(".gguf"):
        gguf_path = Path(model_id).expanduser()
        return gguf_path if gguf_path.exists() else None

    if "/" not in model_id:
        local_path = Path(model_id).expanduser()
        return local_path if local_path.exists() else None

    repo_dir = _hf_cache_root() / f"models--{model_id.replace('/', '--')}"
    snapshots_dir = repo_dir / "snapshots"
    if not snapshots_dir.exists():
        return None

    for snapshot in sorted(snapshots_dir.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
        if not snapshot.is_dir():
            continue
        has_config = (snapshot / "config.json").exists()
        has_tokenizer = (snapshot / "tokenizer.json").exists() or (snapshot / "tokenizer_config.json").exists()
        index_path = snapshot / "model.safetensors.index.json"
        if index_path.exists():
            try:
                index_data = json.loads(index_path.read_text(encoding="utf-8"))
                weight_files = set(index_data.get("weight_map", {}).values())
                has_weights = bool(weight_files) and all((snapshot / name).exists() for name in weight_files)
            except Exception:
                has_weights = False
        else:
            has_weights = any(snapshot.glob("*.safetensors"))
        if has_config and has_tokenizer and has_weights:
            return snapshot
    return None


def installed_model_choices() -> list[dict]:
    """
    Built-in models that are fully cached locally, then any GGUF files found
    under LLAMA_MODEL_DIRS, then the current model. The built-in list is kept
    for compatibility; LLAMA_MODEL_DIRS is how other models are offered
    without editing code.
    """
    choices = []
    for choice in MODEL_CHOICES:
        snapshot = _cached_snapshot_for_model(choice["model"])
        if snapshot is None:
            continue
        item = dict(choice)
        item["cached"] = True
        item["cache_path"] = str(snapshot)
        choices.append(item)

    known = {choice["model"] for choice in choices}
    for item in ms.discovered_model_choices(os.environ.get("LLAMA_MODEL_DIRS")):
        if item["model"] in known:
            continue
        known.add(item["model"])
        item["cached"] = True
        item["cache_path"] = item["model"]
        choices.append(item)

    if not any(choice["model"] == MODEL_NAME for choice in choices):
        snapshot = _cached_snapshot_for_model(MODEL_NAME)
        if snapshot is not None:
            choices.append({
                "id": MODEL_NAME,
                "label": MODEL_NAME,
                "model": MODEL_NAME,
                "aliases": [],
                "cached": True,
                "cache_path": str(snapshot),
            })

    return choices


def resolve_model_choice(value: str) -> str:
    """Resolve a launcher/UI alias to an MLX model id."""
    return MODEL_ALIAS_MAP.get(value.lower(), value)


def _is_valid_model_choice(value: str) -> bool:
    """Keep restart requests to simple aliases, repo ids, or local paths."""
    if not value or "\n" in value or "\r" in value or "\0" in value:
        return False
    # An existing .gguf file may have spaces in its path (a folder such as
    # "Application Support"); it is passed as one argument, never to a shell.
    if value.lower().endswith(".gguf"):
        return Path(value).expanduser().is_file()
    if any(ch.isspace() for ch in value):
        return False
    return "/" in value or value.lower() in MODEL_ALIAS_MAP or value.startswith((".", "~"))


_model_load_lock = threading.Lock()


def ensure_model():
    """Load the model once if it is not yet available."""
    global model, tokenizer
    if model is not None:
        return

    with _model_load_lock:
        # Another readiness caller may have loaded the model while this caller
        # waited for the lock.
        if model is not None:
            return

        print(f"Loading model: {MODEL_NAME}")
        try:
            model, tokenizer = load(MODEL_NAME)
        except BackendError as exc:
            print("\n" + "=" * 60, file=sys.stderr)
            print("Could not load the model.", file=sys.stderr)
            print(exc, file=sys.stderr)
            print("=" * 60 + "\n", file=sys.stderr)
            raise
        rp.MODEL_NAME = MODEL_NAME
        print(f"Model loaded via the {current_backend()} backend.")


# ---------------------------------------------------------------------------
# Startup
# ---------------------------------------------------------------------------
@app.on_event("startup")
async def startup():
    try:
        ensure_model()
    except BackendError:
        # An external llama-server may simply not be running yet. The app
        # stays up so the browser can say so, and connects when it appears.
        if ms.connection_mode(MODEL_NAME) != ms.MODE_EXTERNAL:
            raise
        print(f"No llama-server answering at {ms.server_url()} yet; the app "
              "will connect when one is started there.", file=sys.stderr)


# ---------------------------------------------------------------------------
# Serve the web UI
# ---------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    if HTML_PATH.exists():
        # no-store: after an update and restart the browser must load the
        # current interface, not a cached copy of the previous one.
        return HTMLResponse(HTML_PATH.read_text(encoding="utf-8"),
                            headers={"Cache-Control": "no-store"})
    return HTMLResponse("<h1>chat.html not found</h1><p>Place chat.html next to server.py</p>")


# ---------------------------------------------------------------------------
# GET /v1/models — for the status dot
# ---------------------------------------------------------------------------
@app.get("/v1/models")
async def list_models():
    return {"data": [{"id": MODEL_NAME, "object": "model"}]}


# ---------------------------------------------------------------------------
# GET /api/models/aliases — UI model switcher choices
# ---------------------------------------------------------------------------
@app.get("/api/models/aliases")
async def list_model_aliases():
    mode = ms.connection_mode(MODEL_NAME)
    restart = ms.restart_availability(mode)
    return {
        "current_model": MODEL_NAME,
        "models": installed_model_choices(),
        "mode": mode,
        "restart_available": restart["available"],
        "restart_unavailable_reason": restart["reason"],
    }


# ---------------------------------------------------------------------------
# GET /api/server/status — who manages the model server, whether it answers,
# and which model it reports; a switch is never reported loaded early.
# ---------------------------------------------------------------------------
def _server_status() -> dict:
    mode = ms.connection_mode(MODEL_NAME)
    url, probe, served = None, None, ""
    if mode != ms.MODE_IN_PROCESS:
        handle = model if isinstance(model, llm_backend.LlamaServerModel) else None
        url = handle.base_url if handle is not None else ms.server_url()
        probe_handle = handle or llm_backend.LlamaServerModel(MODEL_NAME, base_url=url)
        probe = probe_handle.probe(timeout=2.0)
        if probe == "ready":
            served = probe_handle.served_model_name(timeout=2.0)
            if model is None and not model_switch.busy():
                # An external server that was not running when the app
                # started; connect now that it answers.
                try:
                    ensure_model()
                except Exception:                               # noqa: BLE001
                    pass
    return ms.build_status(
        mode=mode, url=url, probe=probe, served=served,
        configured_model=MODEL_NAME, switch=model_switch.snapshot(),
        restart=ms.restart_availability(mode),
        in_process_loaded=model is not None,
    )


@app.get("/api/server/status")
async def server_status():
    status = await asyncio.to_thread(_server_status)
    return JSONResponse(status, headers={"Cache-Control": "no-store"})


def _reload_model(target: str) -> str:
    """Connect to the newly loaded model; returns the name the server reports."""
    global model, tokenizer, MODEL_NAME
    with _model_load_lock:
        new_model, new_tokenizer = load(target)
        model, tokenizer = new_model, new_tokenizer
        MODEL_NAME = target
        rp.MODEL_NAME = target
    return llm_backend.served_model_name()


def _service_command(*args: str) -> list:
    """The service script run through bash, so a lost executable bit (seen as
    "Permission denied: scripts/qwen_service.sh") cannot stop a switch or
    restart started from the browser. The script itself is unchanged."""
    bash = "/bin/bash" if Path("/bin/bash").exists() else (shutil.which("bash") or "bash")
    return [bash, str(SERVICE_PATH), *args]


def _switch_in_place(target: str):
    """Load a different GGUF into the managed llama-server; the app stays up."""
    _, llama_port = llm_backend._split_host_port(ms.server_url())
    command = _service_command("switch-model", "--model", target,
                               "--llama-port", str(llama_port))
    try:
        timeout = float(os.environ.get("QWEN_STARTUP_TIMEOUT", "600") or 600) + 60
    except ValueError:
        timeout = 660.0
    ms.perform_switch(model_switch, target, command=command, cwd=str(ROOT_DIR),
                      reload=_reload_model, timeout=timeout)


def _restart_not_started():
    global restart_scheduled
    restart_scheduled = False


def _restart_after_response(model_choice: str):
    """Delegate the whole restart to the service manager.

    qwen_service.sh owns both managed processes and their PID files.  The
    browser must not create a second lifecycle by launching start_server.sh
    directly.  The service command is detached because its stop phase will
    terminate this FastAPI process.
    """
    time.sleep(0.75)
    # The app's own port is passed back, so the restarted app comes up where
    # the browser is looking. Without it, a service started with --port came
    # back on the default port and the page reported "Server not reachable".
    cmd = _service_command(
        "restart",
        "--model",
        model_choice,
        "--port",
        str(SERVER_PORT),
        "--no-open",
    )
    try:
        subprocess.Popen(
            cmd,
            cwd=str(ROOT_DIR),
            start_new_session=True,
        )
    except Exception as exc:
        traceback.print_exc()
        # This process will not be replaced, so release the guard and say why.
        _restart_not_started()
        model_switch.fail(f"The restart could not be started: {exc}")


# ---------------------------------------------------------------------------
# POST /api/server/restart — controlled restart with a different model
# ---------------------------------------------------------------------------
@app.post("/api/server/restart")
async def restart_server(request: dict):
    global restart_scheduled

    model_choice = str(request.get("model") or "").strip()
    if not _is_valid_model_choice(model_choice):
        return JSONResponse({"error": "Invalid model choice"}, status_code=400)

    resolved_model = resolve_model_choice(model_choice)
    if _cached_snapshot_for_model(resolved_model) is None:
        return JSONResponse(
            {"error": "That model is not fully downloaded locally."},
            status_code=409,
        )

    if any(job.get("status") == "running" for job in review_jobs.values()):
        return JSONResponse(
            {"error": "A review is running. Wait for it to finish before switching models."},
            status_code=409,
        )

    if model_switch.busy():
        return JSONResponse({"error": "A model is already loading."}, status_code=409)

    blocked = _switch_blocked_reason()
    if blocked:
        return JSONResponse({"error": blocked}, status_code=409)

    mode = ms.connection_mode(MODEL_NAME)
    if mode == ms.MODE_EXTERNAL:
        return JSONResponse({"error": ms.EXTERNAL_RESTART_REASON}, status_code=409)

    # GGUF to GGUF on a llama-server this app's launcher started: replace the
    # model and keep the app running, so loading and failure can be reported.
    if mode == ms.MODE_MANAGED and llm_backend.is_gguf_model(resolved_model):
        if not model_switch.begin(resolved_model):
            return JSONResponse({"error": _switch_blocked_reason() or "A model is already loading."},
                                status_code=409)
        threading.Thread(target=_switch_in_place, args=(resolved_model,),
                         daemon=True).start()
        return {"status": "switching", "method": "in-place", "model": resolved_model}

    # Anything else (MLX involved) needs the whole app restarted.
    if not ms.service_managed():
        return JSONResponse({"error": ms.FULL_RESTART_REASON}, status_code=409)

    with restart_lock:
        if restart_scheduled:
            return JSONResponse({"error": "A restart is already scheduled"}, status_code=409)
        # Also refuses new model work in the moments before this process is
        # stopped, so nothing starts only to be cut off by the restart.
        if not model_switch.begin(resolved_model):
            return JSONResponse({"error": _switch_blocked_reason() or "A model is already loading."},
                                status_code=409)
        restart_scheduled = True

    # The resolved model is passed, not the alias, so the shell launcher and
    # this process cannot disagree about what an alias means.
    thread = threading.Thread(
        target=_restart_after_response,
        args=(resolved_model,),
        daemon=True,
    )
    thread.start()

    return {
        "status": "restarting",
        "method": "full-restart",
        "model": resolved_model,
    }


def discover_academic_source(doi: str) -> academic_claims.SourceLocation:
    """Discover a scholarly source location using a safe DOI only."""
    return academic_claims.discover_openalex_source(
        doi,
        get_openalex_work_by_doi,
    )


def retrieve_academic_source(
    location: academic_claims.SourceLocation,
) -> academic_claims.RetrievedSource:
    """Retrieve substantive scholarly text from a discovered PDF."""
    return academic_claims.retrieve_pdf_source_from_location(location)


def assess_academic_claim(
    claim: str,
    evidence: list[academic_claims.ClaimEvidence],
) -> academic_claims.ClaimAssessmentResult:
    """Assess located claim evidence using the configured local model."""

    def assessor(*, prompt, schema):
        return academic_claim_assessor.generate_claim_assessor_output(
            model,
            tokenizer,
            prompt,
            schema,
        )

    return academic_claims.assess_located_claim(
        claim=claim,
        evidence=evidence,
        assessor=assessor,
    )


def assess_academic_methodology(*, prompt, schema):
    """Assess methodological consistency using the configured local model."""
    return academic_claim_assessor.generate_claim_assessor_output(
        model,
        tokenizer,
        prompt,
        schema,
    )


def assess_academic_material_restriction(*, prompt, schema):
    """Assess material restriction omission using the configured local model."""
    return academic_claim_assessor.generate_claim_assessor_output(
        model,
        tokenizer,
        prompt,
        schema,
    )


ACADEMIC_COVERAGE_DISCOVERY_MAX_TOKENS = 2000
ACADEMIC_COVERAGE_DECOMPOSITION_MAX_TOKENS = 1000
ACADEMIC_COVERAGE_REPRESENTATION_MAX_TOKENS = 256


def _raised_in(exc: BaseException, function_name: str) -> bool:
    """True when the innermost frame of exc's traceback is function_name."""
    tb = exc.__traceback__
    if tb is None:
        return False
    while tb.tb_next is not None:
        tb = tb.tb_next
    return tb.tb_frame.f_code.co_name == function_name


def assess_academic_claim_coverage(
    *,
    answer_draft: str,
    existing_claims: list[academic_chat.TechnicalClaim],
) -> academic_claim_coverage.ClaimCoverageAssessment:
    """Discover omitted technical claims using a bounded local pipeline."""

    # The pipeline calls global discovery first. Retain only that response,
    # and only for this invocation; later additive checks are not captured.
    diagnostic_raw_output = []
    first_assessment = True

    def assessor(*, prompt, schema):
        nonlocal first_assessment
        if schema == academic_claim_coverage.claim_discovery_output_schema():
            max_tokens = ACADEMIC_COVERAGE_DISCOVERY_MAX_TOKENS
        elif (
            schema
            == academic_claim_coverage.claim_decomposition_output_schema()
        ):
            max_tokens = ACADEMIC_COVERAGE_DECOMPOSITION_MAX_TOKENS
        elif (
            schema
            == academic_claim_coverage.claim_representation_output_schema()
        ):
            max_tokens = ACADEMIC_COVERAGE_REPRESENTATION_MAX_TOKENS
        else:
            raise TypeError(
                "Unexpected schema supplied to claim-coverage pipeline."
            )

        diagnostic_kwargs = (
            {"diagnostic_raw_output": diagnostic_raw_output}
            if first_assessment else {}
        )
        first_assessment = False
        try:
            return academic_claim_assessor.generate_claim_assessor_output(
                model,
                tokenizer,
                prompt,
                schema,
                max_tokens=max_tokens,
                **diagnostic_kwargs,
            )
        except (
            BackendError,
            academic_claim_assessor.ClaimAssessorOutputError,
        ) as exc:
            # The application layer owns stage-specific failure semantics:
            # global discovery lets this translated inference failure escape,
            # while additive audit, decomposition, and representation fail
            # open without erasing already established claims.
            raise academic_claim_coverage.ClaimCoverageOutputError(
                "Claim-coverage inference could not be established."
            ) from exc

    try:
        result = academic_claim_coverage.assess_claim_coverage_two_stage(
            answer_draft=answer_draft,
            existing_claims=existing_claims,
            assessor=assessor,
        )
    except BackendError:
        return academic_claim_coverage.ClaimCoverageAssessment.unavailable(
            "Local claim-coverage inference was unavailable."
        )
    except academic_claim_assessor.ClaimAssessorOutputError:
        return academic_claim_coverage.ClaimCoverageAssessment.unavailable(
            "Local claim-coverage output could not be decoded."
        )
    except academic_claim_coverage.ClaimCoverageOutputError:
        # Keep the reader-facing result unchanged. Tracebacks include chained
        # backend/JSON causes; validation errors name the failing field/anchor.
        # Never log prompts or answer drafts, or turn a logging failure into
        # a failed request. repr keeps model text escaped on one log line.
        try:
            print("[claim-coverage] global discovery failed", file=sys.stderr)
            traceback.print_exc()
            if diagnostic_raw_output:
                print(
                    f"[claim-coverage] raw assessor output: {diagnostic_raw_output[0]!r}",
                    file=sys.stderr,
                    flush=True,
                )
        except Exception:
            pass  # Diagnostics must not change coverage failure semantics.
        return academic_claim_coverage.ClaimCoverageAssessment.unavailable(
            "Local claim-coverage output could not be validated."
        )
    except ValueError as exc:
        # Raised by resolve_claim_source_context when a discovered claim's
        # verbatim anchor does not sit inside one application-owned answer
        # sentence: the model quoted across a full stop. (Abbreviations such
        # as "i.e." no longer split a sentence; see answer_sentence_spans.)
        # The discovery output is unusable
        # for this answer, which is the same situation as the validation
        # failure above, so it takes the same designed path: coverage is
        # unavailable and the release reports checking as incomplete. The
        # traceback is kept in the server log so the cause stays visible.
        # Any other ValueError is a programming error and still propagates.
        if not _raised_in(exc, "resolve_claim_source_context"):
            raise
        traceback.print_exc()
        return academic_claim_coverage.ClaimCoverageAssessment.unavailable(
            "Local claim-coverage output could not be placed within "
            "a single answer sentence."
        )

    if result.rejected_global_items:
        try:
            for rejected in result.rejected_global_items:
                print(
                    f"[claim-coverage] global discovery item rejected "
                    f"index={rejected.index}: {rejected.reason}",
                    file=sys.stderr,
                    flush=True,
                )
            if diagnostic_raw_output:
                print(
                    f"[claim-coverage] raw assessor output: {diagnostic_raw_output[0]!r}",
                    file=sys.stderr,
                    flush=True,
                )
        except Exception:
            pass  # Diagnostics must not change partial-coverage semantics.

    return academic_claim_coverage.ClaimCoverageAssessment.from_result(
        result
    )


# ---------------------------------------------------------------------------
# POST /api/chat/academic
# Academic Chat generation, checking, and bounded reconciliation.
#
# The complete question is used only by the local first stage. External
# bibliographic/discovery services receive only bibliographic metadata or
# identifiers, while source retrieval receives only a discovered source URL.
# If checking blocks release and bounded corrections exist, one local revision
# is permitted and the revised AcademicDraft is independently reassessed.
# Bibliographic verification or source retrieval does not establish claim support.
# ---------------------------------------------------------------------------
@app.post("/api/chat/academic")
@_model_operation("Academic Chat")
async def academic_chat_first_stage(request: dict):
    allowed = {"question"}
    unexpected = set(request) - allowed

    if unexpected:
        return JSONResponse(
            {
                "error": "Unexpected fields in Academic Chat request.",
                "unexpected_fields": sorted(unexpected),
            },
            status_code=400,
        )

    question = request.get("question")
    if not isinstance(question, str) or not question.strip():
        return JSONResponse(
            {"error": "A non-empty question is required."},
            status_code=400,
        )

    await asyncio.to_thread(ensure_model)

    def first_stage_runner(
        local_model,
        local_tokenizer,
        local_question,
    ):
        return academic_orchestrator.run_academic_first_stage(
            local_model,
            local_tokenizer,
            local_question,
            source_discoverer=discover_academic_source,
            source_retriever=retrieve_academic_source,
            claim_locator=academic_claims.prepare_claim_support,
            claim_assessor=assess_academic_claim,
            methodological_assessor=assess_academic_methodology,
            coverage_assessor=assess_academic_claim_coverage,
            material_restriction_assessor=(
                assess_academic_material_restriction
            ),
        )

    def draft_assessor(draft, *, local_guidance):
        return academic_orchestrator.assess_academic_draft(
            draft,
            local_guidance=local_guidance,
            source_discoverer=discover_academic_source,
            source_retriever=retrieve_academic_source,
            claim_locator=academic_claims.prepare_claim_support,
            claim_assessor=assess_academic_claim,
            methodological_assessor=assess_academic_methodology,
            claim_methodological_retriever=(
                academic_orchestrator.retrieve_methodological_context
            ),
            coverage_assessor=assess_academic_claim_coverage,
            material_restriction_assessor=(
                assess_academic_material_restriction
            ),
        )

    try:
        result = await asyncio.to_thread(
            academic_reconciliation_orchestrator.run_academic_reconciliation,
            model,
            tokenizer,
            question,
            first_stage_runner=first_stage_runner,
            correction_extractor=(
                academic_reconciliation.extract_academic_corrections
            ),
            revision_generator=academic_reconciliation.revise_academic_draft,
            draft_assessor=draft_assessor,
        )
    except academic_chat.AcademicDraftError as exc:
        return JSONResponse(
            {
                "error": "Academic Chat model returned invalid structured output.",
                "detail": str(exc),
            },
            status_code=502,
        )
    except academic_methodology.MethodologicalAssessmentOutputError as exc:
        return JSONResponse(
            {
                "error": (
                    "Academic methodological checking could not be completed."
                ),
                "detail": str(exc),
            },
            status_code=502,
        )
    except BackendError as exc:
        return JSONResponse(
            {
                "error": "Academic Chat local model unavailable.",
                "detail": str(exc),
            },
            status_code=502,
        )
    except RuntimeError as exc:
        try:
            traceback.print_exc()
        except Exception:
            pass  # Diagnostics must not change the existing HTTP response.
        return JSONResponse(
            {
                "error": "Academic reference service unavailable.",
                "detail": str(exc),
            },
            status_code=502,
        )

    payload = result.to_dict()

    # Where the reader should check this answer, and against what. A layer
    # over the verdicts already reached: it changes none of them and adds no
    # model call. Built from the same notes index that supplied the guidance,
    # so the references belong to the sections that were actually retrieved.
    # A failure here must not cost the reader the answer, so it is reported
    # in place of the assessment rather than raised.
    try:
        payload["check_further"] = academic_check_further.assess_check_further(
            result.presented,
            academic_orchestrator.methodological_notes_index(),
            source_contradiction_resolution=(
                result.source_contradiction_resolution
            ),
        ).to_dict()
    except Exception as exc:                                    # noqa: BLE001
        traceback.print_exc()
        payload["check_further"] = academic_check_further.incomplete_assessment(
            f"{type(exc).__name__}: {exc}")

    return payload


# ---------------------------------------------------------------------------
# POST /api/chat/academic/draft
# Local first-pass generation for Academic Chat.
#
# The complete question is passed to the configured local model only.
# This endpoint performs no bibliographic or other external lookup.
# ---------------------------------------------------------------------------
@app.post("/api/chat/academic/draft")
@_model_operation("Academic Chat draft")
async def academic_chat_draft(request: dict):
    allowed = {"question"}
    unexpected = set(request) - allowed

    if unexpected:
        return JSONResponse(
            {
                "error": "Unexpected fields in Academic Chat draft request.",
                "unexpected_fields": sorted(unexpected),
            },
            status_code=400,
        )

    question = request.get("question")
    if not isinstance(question, str) or not question.strip():
        return JSONResponse(
            {"error": "A non-empty question is required."},
            status_code=400,
        )

    await asyncio.to_thread(ensure_model)

    try:
        draft = await asyncio.to_thread(
            academic_chat.generate_academic_draft,
            model,
            tokenizer,
            question,
        )
    except academic_chat.AcademicDraftError as exc:
        return JSONResponse(
            {
                "error": "Academic Chat model returned invalid structured output.",
                "detail": str(exc),
            },
            status_code=502,
        )
    except BackendError as exc:
        return JSONResponse(
            {
                "error": "Academic Chat local model unavailable.",
                "detail": str(exc),
            },
            status_code=502,
        )

    return draft.to_dict()


# ---------------------------------------------------------------------------
# POST /api/chat/academic/verify-reference
# Bibliographic verification for Academic Chat only.
#
# This endpoint accepts bibliographic metadata, not manuscript text or
# arbitrary conversation text. Crossref/OpenAlex corroboration establishes
# bibliographic identity only; it does not establish support for a claim.
# ---------------------------------------------------------------------------
@app.post("/api/chat/academic/verify-reference")
async def academic_verify_reference(request: dict):
    allowed = {"title", "author", "year", "venue", "doi"}
    unexpected = set(request) - allowed

    if unexpected:
        return JSONResponse(
            {
                "error": "Unexpected fields in bibliographic verification request.",
                "unexpected_fields": sorted(unexpected),
            },
            status_code=400,
        )

    title = str(request.get("title") or "").strip() or None
    author = str(request.get("author") or "").strip() or None
    venue = str(request.get("venue") or "").strip() or None
    doi = str(request.get("doi") or "").strip() or None

    year = request.get("year")
    if year in ("", None):
        year = None
    else:
        try:
            year = int(year)
        except (TypeError, ValueError):
            return JSONResponse(
                {"error": "year must be an integer or null."},
                status_code=400,
            )

    if not title and not doi:
        return JSONResponse(
            {"error": "A title or DOI is required for reference verification."},
            status_code=400,
        )

    try:
        result = await asyncio.to_thread(
            verify_academic_reference,
            title=title,
            author=author,
            year=year,
            venue=venue,
            doi=doi,
        )
    except RuntimeError as exc:
        return JSONResponse(
            {
                "error": "Academic reference service unavailable.",
                "detail": str(exc),
            },
            status_code=502,
        )

    return result.to_dict()


# ---------------------------------------------------------------------------
# POST /v1/chat/completions — OpenAI-compatible chat
# ---------------------------------------------------------------------------
@app.post("/v1/chat/completions")
@_model_operation("chat")
async def chat_completions(request: dict):
    await asyncio.to_thread(ensure_model)

    messages = request.get("messages", [])
    max_tokens = request.get("max_tokens", 1200)
    temperature = request.get("temperature", rp.TEMPERATURE)
    top_p = request.get("top_p", rp.TOP_P)
    # The endpoint is OpenAI-shaped and was silently discarding two fields it
    # accepts. A client sending presence_penalty got generation without one and
    # no indication that its request had been ignored. Passing them through
    # changes nothing by default -- both fall back to the pipeline's values --
    # and makes the sampler addressable, which is the precondition for
    # measuring it. Qwen3 recommends presence_penalty 1.5 for instruct mode
    # and 0.0 for thinking, and the degenerate repetition loops recorded in
    # section 12 were produced here with none set at all.
    presence_penalty = request.get("presence_penalty", rp.PRESENCE_PENALTY)
    repetition_penalty = request.get("repetition_penalty", rp.REPETITION_PENALTY)
    top_k = int(request.get("top_k", rp.TOP_K))

    # Inject default system prompt if no system message is present
    has_system = any(m.get("role") == "system" for m in messages)
    if not has_system:
        messages = [{"role": "system", "content": rp._DEFAULT_CHAT_SYSTEM}] + messages

    # Build prompt from messages
    if getattr(tokenizer, "chat_template", None) is not None:
        try:
            prompt = tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
                enable_thinking=llm_backend.thinking_enabled(),
            )
        except TypeError:
            prompt = tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
            )
    else:
        prompt = messages[-1]["content"] if messages else ""

    sampler = make_sampler(temperature, top_p=top_p, top_k=top_k,
                           repetition_penalty=repetition_penalty,
                           presence_penalty=presence_penalty)

    output = await asyncio.to_thread(
        generate,
        model,
        tokenizer,
        prompt=prompt,
        max_tokens=max_tokens,
        sampler=sampler,
        verbose=False,
    )

    output = rp.clean_model_output(output)
    output = rp.clean_markdown_math_artifacts(output)

    # Strip markdown heading markers (e.g. "### Title") — the chat UI
    # does not render markdown headings, so these appear as literal "#" chars.
    import re as _re
    output = _re.sub(r"^(#{1,6})\s+", "", output, flags=_re.MULTILINE)

    return {
        "id": f"chatcmpl-{uuid.uuid4().hex[:8]}",
        "object": "chat.completion",
        "model": MODEL_NAME,
        "choices": [{
            "index": 0,
            "message": {"role": "assistant", "content": output},
            "finish_reason": "stop",
        }],
    }


# ---------------------------------------------------------------------------
# POST /api/review — file upload, runs pipeline in background
# ---------------------------------------------------------------------------

SUPPORTED_REVIEW_SUFFIXES = {
    ".pdf", ".txt", ".md", ".docx", ".csv", ".xlsx", ".xlsm"
}
MAX_REVIEW_UPLOAD_BYTES = 100 * 1024 * 1024  # 100 MiB for the complete upload (primary + supplements)
REVIEW_UPLOAD_CHUNK_BYTES = 1024 * 1024      # 1 MiB

def _development_mode_enabled(value) -> bool:
    """Parse Development mode; non-string values default OFF."""
    return isinstance(value, str) and value.strip().lower() in ("1", "true", "on", "yes")


@app.post("/api/review")
async def start_review(
    file: UploadFile = File(...),
    domain: str = Form("general"),
    thinking: str = Form(""),
    vision: str = Form(""),
    development_mode: str = Form(""),
    supplements: list[UploadFile] | None = File(None),
):
    if model_switch.busy():
        raise HTTPException(status_code=409, detail=(
            "A model is loading. Start the review when the status shows it loaded."))
    # Direct Python callers omit the optional FastAPI File parameter.
    supplements = supplements if isinstance(supplements, list) else []
    uploads = [file, *supplements]
    for i, upload in enumerate(uploads):
        suffix = Path(upload.filename or "").suffix.lower()
        if suffix not in SUPPORTED_REVIEW_SUFFIXES:
            supported = ", ".join(sorted(SUPPORTED_REVIEW_SUFFIXES))
            kind = "manuscript" if i == 0 else "supplementary"
            raise HTTPException(status_code=400, detail=(
                f"Unsupported {kind} file type. Supported types: {supported}."))

    job_id = uuid.uuid4().hex[:12]
    tmp_dir = Path(tempfile.mkdtemp(prefix=f"review_{job_id}_"))
    paths = []
    # One aggregate limit, independent of Content-Length. No supplied filename
    # is used as a storage path, even when two sources share a basename.
    written = 0
    try:
        for i, upload in enumerate(uploads):
            suffix = Path(upload.filename or "").suffix.lower()
            destination_path = tmp_dir / (f"supplement_{i}{suffix}" if i else f"upload{suffix}")
            paths.append(destination_path)
            with open(destination_path, "wb") as destination:
                while True:
                    chunk = upload.file.read(REVIEW_UPLOAD_CHUNK_BYTES)
                    if not chunk:
                        break
                    written += len(chunk)
                    if written > MAX_REVIEW_UPLOAD_BYTES:
                        label = "Manuscript upload" if not supplements else "Complete review upload"
                        raise HTTPException(status_code=413, detail=(
                            f"{label} exceeds the "
                            f"{MAX_REVIEW_UPLOAD_BYTES // (1024 * 1024)} MiB limit."))
                    destination.write(chunk)
    except BaseException:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise
    file_path = paths[0]

    # "" leaves the process default alone; "1"/"0" force one mode for this
    # review only, so the two can be alternated over real use and compared.
    # "synthesis" is the hybrid: the eleven chunk notes, which are most of the
    # time and were never the weak stage, run in instruct, and only the
    # synthesis and validation think.
    choice = str(thinking).strip().lower()
    want_thinking = None
    thinking_scope = "review"
    if choice in ("1", "true", "on", "yes"):
        want_thinking = True
    elif choice in ("0", "false", "off", "no"):
        want_thinking = False
    elif choice in ("synthesis", "hybrid", "2"):
        want_thinking = True
        thinking_scope = "synthesis"

    # Vision was a start-up flag only, so changing it meant restarting the
    # server. "" keeps whatever --vision set; "1"/"0" force it for this review,
    # in the same way the reasoning mode is forced.
    vision_choice = str(vision).strip().lower()
    want_vision = None
    if vision_choice in ("1", "true", "on", "yes"):
        want_vision = True
    elif vision_choice in ("0", "false", "off", "no"):
        want_vision = False

    want_development_mode = _development_mode_enabled(development_mode)

    # Held from here until the review thread ends, so no switch can begin
    # while the appraisal, its evidence verification or its cards are built.
    try:
        model_switch.acquire(REVIEW_OPERATION)
    except ms.SwitchInProgress as exc:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    review_jobs[job_id] = {
        "status": "running",
        "thinking": want_thinking,
        "thinking_choice": choice or "server default",
        "thinking_scope": thinking_scope,
        "vision": want_vision,
        "development_mode": want_development_mode,
        "progress": [],
        "report": None,
        "appendix": None,
        "trace": None,
        "error": None,
        "filename": file.filename,
        "supplements": [
            {"path": str(path), "name": Path((upload.filename or path.name).replace("\\", "/")).name}
            for path, upload in zip(paths[1:], supplements)
        ],
        "cancel_requested": False,
    }

    # Run review in background thread
    try:
        thread = threading.Thread(
            target=_run_review, args=(job_id, file_path, domain, tmp_dir),
            daemon=True,
        )
        thread.start()
    except BaseException:
        review_jobs.pop(job_id, None)
        model_switch.release(REVIEW_OPERATION)
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise

    return {"job_id": job_id, "status": "running"}


class ReviewCancelled(Exception):
    """Internal control flow for a cooperatively cancelled review."""


def _check_review_cancelled(job_id: str):
    """Stop a review at the next safe boundary after cancellation is requested."""
    job = review_jobs.get(job_id)
    if job and job.get("cancel_requested"):
        raise ReviewCancelled("Review cancelled by user.")


@app.post("/api/review/{job_id}/cancel")
async def cancel_review(job_id: str):
    """Request cooperative cancellation of a running review."""
    job = review_jobs.get(job_id)
    if not job:
        return JSONResponse({"error": "Unknown job"}, status_code=404)

    status = job.get("status")
    if status == "running":
        job["cancel_requested"] = True
        return {"job_id": job_id, "status": "cancelling"}

    if status == "cancelled":
        return {"job_id": job_id, "status": "cancelled"}

    return JSONResponse(
        {
            "error": f"Review is already {status}.",
            "status": status,
        },
        status_code=409,
    )


@app.post("/api/review/{job_id}/ask")
@_model_operation("review question")
async def ask_about_review(job_id: str, request: dict):
    """
    Answer one question under a finished review, from one named source.

    Two modes exist. `manuscript` answers from this paper and its supplied
    supplements, retaining source names and checking quotations within each source. `reviewer_notes` answers a general
    methodological question from the notes in resources/, and has not read the
    paper at all. Both return the same shape, and both say which they were, so
    a reader never has to infer where a sentence came from.

    Bound to a completed review rather than to the chat tab: the manuscript
    mode has to be checked against the same extracted text the report was
    built from, which a free-standing chat cannot do, and the notes mode is
    logged against the review that prompted the question.
    """
    _restore_review(job_id)
    job = review_jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="No such review.")
    if job.get("ask_unavailable_reason"):
        raise HTTPException(status_code=409, detail=job["ask_unavailable_reason"])
    if job.get("status") != "complete" or not job.get("text"):
        raise HTTPException(
            status_code=409,
            detail="That review has not finished, so there is nothing to ask about.",
        )
    question = str(request.get("question", "")).strip()
    if not question:
        raise HTTPException(status_code=400, detail="No question was sent.")

    mode = str(request.get("mode") or SOURCE_MANUSCRIPT).strip().lower()
    if mode in ("notes", SOURCE_NOTES):
        mode = SOURCE_NOTES
    if mode not in (SOURCE_MANUSCRIPT, SOURCE_NOTES):
        raise HTTPException(
            status_code=400,
            detail=f"Unknown source '{mode}'. Ask the manuscript or the reviewer notes.",
        )

    await asyncio.to_thread(ensure_model)
    if mode == SOURCE_NOTES:
        return await asyncio.to_thread(
            answer_notes_question,
            question,
            job_id=job_id,
        )

    history = request.get("history") or []
    answer, problems = await asyncio.to_thread(
        rp.answer_manuscript_question,
        model,
        tokenizer,
        question,
        job["text"],
        report_text=job.get("report") or "",
        history=history,
        **({"sources": job["sources"]} if job.get("sources") else {}),
    )
    found = len(rp.select_passages(question, job["text"]))
    searched = [{"note": job.get("filename", "manuscript"),
                 "heading": f"{found} passage(s) searched", "score": None}]
    if job.get("sources"):
        selected = rp.select_source_passages(question, job["sources"],
                                             rp.qa_passage_budget(len(job.get("report") or "")))
        found = len(selected)
        searched = [{"note": name, "heading": f"Page {page}" if page else "Page unknown", "score": None}
                    for name, page, _ in selected]
    authenticated = []
    sources = job.get("verification_sources") or job.get("sources") or {}
    docs = _passage_documents(job_id)
    for quote in dict.fromkeys(rp._quoted_spans(answer)):
        # Refuse cross-document ambiguity. Never authenticate against review prose.
        passages = [ec.passage(quote, {name: body}, "Manuscript answer")
                    for name, body in sources.items()]
        passages = [p for p in passages if p.get("status") == "located"]
        if len(passages) == 1:
            target = ec.manuscript_target(passages[0], docs, job_id)
            if target:
                authenticated.append(target)
    return {
        "authenticated_passages": authenticated,
        "answer": answer,
        "check": rp.format_answer_check(answer, problems),
        "problems": problems,
        "passages": found,
        "provenance": provenance(SOURCE_MANUSCRIPT,
                                 passages=searched,
                                 resolved=found > 0),
    }


def _add_progress(job_id: str, message: str):
    """Thread-safe progress append."""
    if job_id in review_jobs:
        review_jobs[job_id]["progress"].append(message)


def _build_appendix_text(
    file_path: Path,
    manifest,
    table_blocks,
    chunks,
) -> str:
    """Build the evidence appendix as a markdown string (no file I/O)."""
    from datetime import datetime

    lines = []
    lines.append("# Evidence appendix")
    lines.append("")
    lines.append(f"Generated: {datetime.now().isoformat(timespec='seconds')}")
    lines.extend(_model_header_lines())
    lines.append(f"Pipeline: {rp.PIPELINE_VERSION}")
    lines.append("")
    lines.append(f"## Input files\n- {file_path.name}")
    lines.append("")

    # Manifest summary
    lines.append("## Evidence manifest")
    lines.append("")
    lines.append(f"### {manifest.source_name}")
    lines.append("")
    lines.append("```text")
    lines.append(manifest.summary_text())
    lines.append("")
    lines.append("Detected model/result blocks:")
    lines.append(manifest.model_block_summary())
    lines.append("```")
    lines.append("")

    # Block type breakdown
    type_groups = {}
    for b in manifest.blocks:
        preview = b.text[:120].replace("\n", " ") + ("..." if len(b.text) > 120 else "")
        type_groups.setdefault(b.block_type.name, []).append(preview)

    for btype, previews in type_groups.items():
        lines.append(f"**{btype}** ({len(previews)} blocks)")
        lines.append("")
        for prev in previews[:5]:
            lines.append(f"- {prev}")
        if len(previews) > 5:
            lines.append(f"- ... and {len(previews) - 5} more")
        lines.append("")

    # Tables
    lines.append(f"## Extracted tables ({file_path.name})")
    lines.append("")
    if table_blocks:
        for page_num, block in table_blocks:
            lines.append(f"### Page {page_num}")
            lines.append("")
            lines.append("```text\n" + block + "\n```")
            lines.append("")
    else:
        manifest_tables = [b for b in manifest.blocks if b.block_type.name == "TABLE"]
        if manifest_tables:
            lines.append(
                f"No structured tables from PDF parser. "
                f"{len(manifest_tables)} inline table(s) recovered (shown in manifest above)."
            )
        else:
            lines.append("No extracted table blocks recorded.")
    lines.append("")

    # Chunk previews
    max_preview = 1800
    lines.append("## Chunk previews")
    lines.append("")
    for i, chunk_text in enumerate(chunks, start=1):
        preview = chunk_text[:max_preview]
        if len(chunk_text) > max_preview:
            preview += "\n...[truncated]..."
        lines.append(f"### Chunk {i}")
        lines.append("")
        lines.append("```text\n" + preview + "\n```")
        lines.append("")

    return "\n".join(lines)


def _review_thinking_default() -> bool:
    """Review-only default; do not change the backend's chat/CLI default."""
    for key in ("QWEN_REVIEW_THINKING", "LLAMA_ENABLE_THINKING"):
        if os.environ.get(key, "").strip():
            return os.environ[key].strip().lower() in ("1", "true", "yes", "on")
    return True


def _review_execution_configuration(job: dict) -> dict:
    effective = job.get("thinking")
    if effective is None:
        effective = _review_thinking_default()
    hybrid = job.get("thinking_scope") == "synthesis"
    effort = llm_backend.reasoning_effort() or None
    def mode(enabled):
        return {"enable_thinking": bool(enabled), "reasoning_effort": effort if enabled else None}
    return {
        "appraisal_policy": rp.APPRAISAL_POLICY,
        "requested": {"ui_mode": job.get("thinking_choice", "server default"),
                      "reasoning_effort": effort if effective else None,
                      "vision": job.get("vision")},
        "resolved": {"vision": bool(rp.VISION_TABLES if job.get("vision") is None else job["vision"]),
                     "default_source": next((key for key in ("QWEN_REVIEW_THINKING", "LLAMA_ENABLE_THINKING")
                                             if os.environ.get(key, "").strip()), "review default: Thinking")
                                       if job.get("thinking") is None else "explicit review selection",
                     "evidence_gathering": mode(effective and not hybrid),
                     "final_synthesis": mode(effective),
                     "planned_final_synthesis_passes": (min(rp.REVIEW_PASSES, rp.THINKING_PASSES)
                                                        if effective else rp.REVIEW_PASSES),
                     "exceptions": ["Structured JSON assessments use Instruct to preserve their output contract.",
                                    "Visual transcription and backend health inference checks use Instruct.",
                                    "Thinking-budget exhaustion can fall back to Instruct; request receipts record it."]},
        "actual": {"final_synthesis_passes": 0},
    }


def _reasoning_header_lines(scope: str = "review",
                            passes_note: str = "") -> str:
    """
    Two header lines: the mode that was requested, and what the model did.

    They can disagree. A server that rejects chat_template_kwargs, or a chat
    template that emits an empty <think></think> pair, produces a review headed
    "thinking" with no reasoning in it. Recording only the request makes that
    undetectable after the fact -- the same failure the pass count already had,
    fixed the same way, by counting rather than asserting.
    """
    requested = "thinking" if llm_backend.thinking_enabled() else "instruct"
    if requested == "thinking" and scope == "synthesis":
        requested = "thinking (final synthesis only)"
    stats = llm_backend.reasoning_stats()
    seen, total, chars = (stats["with_reasoning"], stats["generations"],
                          stats["chars"])

    if chars > 0:
        check = (f"reasoning emitted in {seen} of {total} generations "
                 f"({chars:,} characters)")
        if requested == "instruct":
            check += "; not requested, and removed from the report"
    elif requested.startswith("thinking"):
        check = (f"no reasoning emitted in {total} generations; the requested "
                 f"mode cannot be confirmed from output alone")
    else:
        check = f"no reasoning emitted, as expected ({total} generations)"

    if stats.get("retries"):
        check += (f"; {stats['retries']} generation(s) were retried at a larger "
                  f"budget ({stats.get('thinking_budget_retries', 0)} thinking-budget retries; "
                  f"{stats.get('output_truncation_retries', 0)} output-truncation retries)")
    if stats.get("fallbacks"):
        check += (f"; {stats['fallbacks']} were finished in instruct mode after "
                  f"the reasoning would not fit at all")
    if stats["template_kwargs_dropped"]:
        check += ("; the server rejected chat_template_kwargs, so the request "
                  "never reached the chat template")
    effort = llm_backend.reasoning_effort()
    if effort and requested.startswith("thinking"):
        check += f"; reasoning effort was requested as {effort}"
    elif requested.startswith("thinking"):
        check += "; no reasoning effort was sent, so the chat template's own " \
                 "default was in force"
    if passes_note:
        check += f"; {passes_note}"

    return f"Reasoning: {requested}\nReasoning check: {check}\n"


def _vision_capability_safe() -> dict:
    try:
        return llm_backend.vision_capability()
    except Exception as exc:  # noqa: BLE001 - reporting must not break a review
        return {"image_input": "unknown", "projector_loaded": None,
                "source": f"capability check failed ({type(exc).__name__})"}


@ea.review_entry("server")
def _run_review(job_id: str, file_path: Path, domain: str, tmp_dir: Path):
    """Run the full review pipeline (called in background thread)."""
    _record_input_digests(job_id, file_path)
    try:
        ensure_model()

        execution = _review_execution_configuration(review_jobs.get(job_id, {}))
        review_jobs[job_id]["execution"] = execution
        ea.execution("appraisal_policy", execution["appraisal_policy"])
        ea.execution("requested", execution["requested"])
        ea.execution("resolved", execution["resolved"])
        want_thinking = execution["resolved"]["final_synthesis"]["enable_thinking"]
        want_vision = review_jobs.get(job_id, {}).get("vision")
        # Review-local execution context keeps reasoning, vision, and
        # cancellation isolated while model generations remain serialised.
        llm_backend.reset_reasoning_stats()

        def review_cancelled():
            job = review_jobs.get(job_id)
            return bool(job and job.get("cancel_requested"))

        # Vision, recorded as three separate facts: what was requested, what
        # the server reported at the start, and what was actually done.
        vision_record = {
            "requested": bool(rp.VISION_TABLES if want_vision is None else want_vision),
            "requested_by": "server default" if want_vision is None else "this review",
            "capability_at_start": _vision_capability_safe(),
            "usage": rp.new_vision_usage(),
        }
        execution["resolved"]["vision_capability_at_start"] = vision_record["capability_at_start"]
        if job_id in review_jobs:
            review_jobs[job_id]["vision_record"] = vision_record

        with (
            llm_backend.thinking(want_thinking, reason="resolved review configuration"),
            rp.vision(want_vision),
            llm_backend.inference_cancellation(review_cancelled),
            rp.vision_usage(vision_record["usage"]),
        ):
            _run_review_inner(job_id, file_path, domain, tmp_dir)
    except llm_backend.InferenceCancelledError:
        if job_id in review_jobs:
            review_jobs[job_id]["status"] = "cancelled"
            review_jobs[job_id]["error"] = None
            _add_progress(job_id, "Review cancelled.")
    except Exception as e:
        if job_id in review_jobs:
            review_jobs[job_id]["status"] = "error"
            review_jobs[job_id]["error"] = f"{e}\n{traceback.format_exc()}"
            _add_progress(job_id, f"Error: {e}")
    finally:
        # Taken in start_review(); released first, whether the review
        # completed, failed or was cancelled, so a failure while saving cannot
        # leave switching blocked. Nothing below uses the model. Never goes
        # below zero for direct callers.
        model_switch.release(REVIEW_OPERATION)
        if job_id in review_jobs:
            execution = review_jobs[job_id].get("execution")
            if execution is not None:
                execution["actual"].update(llm_backend.reasoning_stats())
                execution["actual"]["text_generations"] = llm_backend.reasoning_stats()["generations"]
                execution["actual"]["vision"] = review_jobs[job_id].get("vision_record", {}).get("usage", {})
                ea.execution("actual", execution["actual"])
                execution["actual"].update(ea.execution_totals())
            review_jobs[job_id]["evidence_availability"] = ea.current_status()
        _persist_review(job_id)
        # Worker-level failures can happen before _run_review_inner() acquires
        # ownership of cleanup, so the thread boundary guarantees it as well.
        try:
            shutil.rmtree(tmp_dir, ignore_errors=True)
        except Exception:
            pass


def _chunk_reasoning(job_id: str):
    """
    The mode the chunk notes run in.

    In the hybrid the outer setting is thinking, and the chunk loop steps back
    into instruct for the duration: the notes are eleven of the fourteen
    generations and most of the two hours, and they were never the stage that
    sourced its evidence badly.
    """
    scope = review_jobs.get(job_id, {}).get("thinking_scope", "review")
    return llm_backend.thinking(False if scope == "synthesis" else None,
                                reason="hybrid evidence gathering: Instruct" if scope == "synthesis" else None)


def _source_verification_assessor(raw_sink: list):
    """The structured, non-thinking call source verification makes.

    Defined here rather than inside the review worker so the worker's tail
    stays free of nested functions."""
    def assess(*, prompt, schema, max_tokens):
        return academic_claim_assessor.generate_claim_assessor_output(
            model, tokenizer, prompt, schema,
            max_tokens=max_tokens,
            diagnostic_raw_output=raw_sink,
        )
    return assess


# ---------------------------------------------------------------------------
# Persistent review sessions (review_store). Only the application process
# started from __main__ saves or restores sessions, so tests and imports of
# this module never touch the reviewer's store unless they enable it.
# ---------------------------------------------------------------------------
_persist_sessions = False


def _record_input_digests(job_id: str, file_path: Path) -> None:
    """sha256 of the uploaded files, taken before the worker deletes them, so a
    saved review records which manuscript it belongs to."""
    job = review_jobs.get(job_id)
    if job is None:
        return
    try:
        digests = [rs.sha256_file(Path(file_path))]
        digests += [rs.sha256_file(Path(item["path"])) for item in job.get("supplements") or []
                    if isinstance(item, dict) and item.get("path")]
        job["manuscript_sha256"], job["input_sha256"] = digests[0], digests
    except OSError:
        job["manuscript_sha256"], job["input_sha256"] = None, []
    if _persist_sessions:
        # Keep the original bytes for the saved review: the worker deletes its
        # temporary folder before the review is saved.
        try:
            uploads = [{"path": str(file_path), "name": job.get("filename")}]
            uploads += [{"path": item["path"], "name": item.get("name")} for item in job.get("supplements") or []
                        if isinstance(item, dict) and item.get("path")]
            rs.stage_pending_documents(job_id, uploads)
        except Exception as exc:  # noqa: BLE001 - keeping documents must not break a review
            job["documents_error"] = f"{type(exc).__name__}: {exc}"


def _persist_review(job_id: str) -> None:
    """Save a completed review to the local store. Never raises: a failure is
    recorded on the job and the in-memory review is unaffected."""
    if not _persist_sessions:
        return
    try:
        job = review_jobs.get(job_id)
        if not job or job.get("status") != "complete":
            return
        try:
            job.setdefault("completed_at", rs.now())
            docs = rs.pending_documents(job_id)
            if docs is not None:
                # The review's own source names (as used in its evidence), in
                # upload order, when they correspond one to one.
                labels = list(job.get("sources") or [])
                if len(labels) == len(docs):
                    for doc, label in zip(docs, labels):
                        doc["source_label"] = label
            rs.save_completed(job_id, job, cards=_evidence_card_set(job_id),
                              manuscript_sha256=job.get("manuscript_sha256"),
                              input_sha256=job.get("input_sha256"), documents=docs)
            job["session_saved"] = True
        except Exception as exc:  # noqa: BLE001 - persistence must not break a review
            job["session_error"] = f"{type(exc).__name__}: {exc}"
            _last_save_error.clear()
            _last_save_error.update(job_id=job_id, error=str(exc), at=rs.now())
            print(f"[review-store] could not save review {job_id}: {exc}", flush=True)
    finally:
        rs.discard_pending(job_id)


def _restore_review(job_id: str) -> bool:
    """Bring a saved review back into memory under its own id. True when the
    job is available (already in memory, or restored from a verified session)."""
    if job_id in review_jobs:
        return True
    if not _persist_sessions or not rs.exists(job_id):
        return False
    try:
        review_jobs[job_id] = rs.load_job(job_id)
    except (rs.StoreError, OSError, ValueError) as exc:
        print(f"[review-store] refused to restore {job_id}: {exc}", flush=True)
        return False
    return True


def _from_document(block: str) -> bool:
    """False for a model transcription of a page image. Such a transcription is
    shown to the model as evidence and kept for inspection, but it never
    verifies a quotation or drives an automatic correction: the PDF itself is
    authoritative. Uses the block's structured provenance, then its label."""
    return not rp.is_visual_transcription(block)


def _apply_automatic_corrections(report: str, all_text: str, all_tables: list) -> str:
    """Numeric direction checks use document-derived tables, never detector flags.

    Legacy contradiction rewriting inferred reporting from document-wide cues;
    it is not evidence that a particular criticism should be replaced.
    """
    authoritative = [t for t in all_tables if _from_document(t)]
    return rp.correct_direction_of_effect_summaries(report, all_text, authoritative)


def _verification_sources(per_file_text: dict, per_file_tables: dict) -> dict:
    """Each source's extracted text, plus any table block not already in it.
    Visual transcriptions are left out (see _from_document)."""
    sources = {}
    for name, body in per_file_text.items():
        extra = [block for _page, block in per_file_tables.get(name, [])
                 if block and _from_document(block) and block.strip()[:200] not in body]
        sources[name] = body + ("\n\n" + "\n\n".join(extra) if extra else "")
    return sources


def _run_review_inner(job_id: str, file_path: Path, domain: str, tmp_dir: Path):
    try:
        supplementary = review_jobs[job_id].get("supplements", [])
        primary_name = Path(str(review_jobs[job_id].get("filename") or file_path.name).replace("\\", "/")).name
        inputs = [(file_path, f"Primary manuscript: {primary_name}" if supplementary else file_path.name)]
        inputs += [(Path(item["path"]), f"Supplement {i}: {item['name']}")
                   for i, item in enumerate(supplementary, 1)]
        file_summaries, all_manifests = [], []
        per_file_text, per_file_tables, per_file_chunks = {}, {}, {}
        # Chunk-level candidates from every file, kept only so the final review
        # can account for them deterministically. Never supplied to a model.
        accounted_candidates = []
        all_extraction_notes = []

        # Diagnostic-only review trace. This records intermediate outputs
        # without changing anything supplied to the model or any review logic.
        trace = {
            "job_id": job_id,
            "pipeline": rp.PIPELINE_VERSION,
            "files": [],
            "final_synthesis": [],
        }
        source_role = ("Appraise only the primary manuscript: " + primary_name + ". "
                       "Other files are supplementary evidence, not separate manuscripts. "
                       "Use supplements to support, qualify or challenge primary claims. "
                       "Do not criticise information as missing from the manuscript when "
                       "appropriately supplied in supplements. Attribute every quotation "
                       "and finding to its exact source name; qualify absence claims until "
                       "all supplied evidence has been considered.")
        for source_index, (file_path, source_name) in enumerate(inputs):
            _check_review_cancelled(job_id)
            _add_progress(job_id, f"Reading {source_name}...")
            text, table_blocks, extraction_notes = rp.load_document(file_path)

            _check_review_cancelled(job_id)
            _add_progress(job_id, "Structuring evidence...")
            derived = rp.detect_derived_input(text)
            if derived:
                raise ValueError(
                    f"{source_name} looks like output from this pipeline rather "
                    f"than a manuscript (found {', '.join(repr(d) for d in derived[:3])}). "
                    "Reviewing a review produces a report that reads normally but "
                    "describes the wrong document. Upload the original manuscript."
                )

            manifest = rp.structure_evidence(source_name, text, table_blocks)
            tables_text = rp.tables_for_prompt(table_blocks)
            appraisal_context = ""
            if source_index == 0:
                primary_context = appraisal_context
            if supplementary:
                appraisal_context = primary_context + "\n" + source_role
                if source_index:
                    appraisal_context += (
                        "\nThis file supplies supplementary evidence. Extract findings relevant "
                        "to the primary manuscript; do not assess it as a standalone paper.")
            manifest_summary = manifest.summary_text()

            chunks = rp.split_text(text)
            if not chunks:
                review_jobs[job_id]["status"] = "error"
                review_jobs[job_id]["error"] = "No usable text extracted."
                return

            # Chunk review
            chunk_outputs = []
            for i, chunk_text in enumerate(chunks, start=1):
                _check_review_cancelled(job_id)
                _add_progress(job_id, f"Reviewing chunk {i}/{len(chunks)}...")
                chunk = rp.DocChunk(source_name=source_name, chunk_id=i, text=chunk_text)
                with _chunk_reasoning(job_id):
                    reviewed = rp.review_chunk(
                        model, tokenizer, chunk,
                        appraisal_context=appraisal_context,
                        manifest_summary=manifest_summary,
                    )
                chunk_outputs.append(reviewed)

            candidate_findings = []
            for chunk_id, reviewed in enumerate(chunk_outputs, start=1):
                candidate_findings.extend(
                    rp.extract_candidate_findings(
                        reviewed,
                        source_name=source_name,
                        chunk_id=chunk_id,
                    )
                )

            finding_groups = rp.group_candidate_findings(candidate_findings)

            # Priority 4C observational candidate triage.
            #
            # This is deliberately NOT supplied to file-level synthesis yet.
            # First establish whether bounded whole-file triage preserves and
            # prioritises the right candidate themes. The structured adapter
            # runs non-thinking regardless of the user's review reasoning mode.
            candidate_triage = None
            candidate_triage_raw = []
            candidate_triage_budget = None
            candidate_triage_note = ""
            candidate_triage_error = ""

            # Observational whole-file methodological propositions.
            #
            # These are traced only. They are deliberately NOT supplied to
            # candidate triage or file-level synthesis in this experiment.
            candidate_propositions = None
            candidate_propositions_raw = []
            candidate_propositions_error = ""

            # Observational verification of constructed propositions.
            #
            # This is traced only. It does NOT alter candidate propositions,
            # candidate triage, or file-level synthesis.
            candidate_proposition_verification = None
            candidate_proposition_verification_raw = []
            candidate_proposition_verification_error = ""

            if candidate_findings:
                _check_review_cancelled(job_id)
                _add_progress(
                    job_id,
                    "Triaging candidate findings (observational)...",
                )
                try:
                    triage_evidence, candidate_triage_note, candidate_triage_budget = (
                        rp.prepare_candidate_triage_evidence(
                            candidate_findings,
                            chunks,
                            manifest_summary=manifest_summary,
                            appraisal_context=appraisal_context,
                        )
                    )

                    _check_review_cancelled(job_id)
                    _add_progress(
                        job_id,
                        "Constructing methodological propositions (observational)...",
                    )

                    def candidate_proposition_assessor(*, prompt, schema):
                        return academic_claim_assessor.generate_claim_assessor_output(
                            model,
                            tokenizer,
                            prompt,
                            schema,
                            max_tokens=5000,
                            diagnostic_raw_output=candidate_propositions_raw,
                        )

                    try:
                        candidate_propositions = rp.generate_candidate_propositions(
                            candidate_findings,
                            triage_evidence,
                            candidate_proposition_assessor,
                            manifest_summary=manifest_summary,
                            appraisal_context=appraisal_context,
                        )
                    except (
                        ValueError,
                        BackendError,
                        academic_claim_assessor.ClaimAssessorOutputError,
                    ) as exc:
                        candidate_propositions_error = (
                            f"{type(exc).__name__}: {exc}"
                        )

                    _check_review_cancelled(job_id)

                    if (
                        candidate_propositions
                        and candidate_propositions.get("propositions")
                    ):
                        _add_progress(
                            job_id,
                            "Verifying methodological propositions "
                            "(observational)...",
                        )

                        def candidate_proposition_verification_assessor(
                            *, prompt, schema
                        ):
                            return academic_claim_assessor.generate_claim_assessor_output(
                                model,
                                tokenizer,
                                prompt,
                                schema,
                                max_tokens=3000,
                                diagnostic_raw_output=(
                                    candidate_proposition_verification_raw
                                ),
                            )

                        try:
                            candidate_proposition_verification = (
                                rp.verify_candidate_propositions(
                                    candidate_propositions,
                                    triage_evidence,
                                    candidate_proposition_verification_assessor,
                                    manifest_summary=manifest_summary,
                                    appraisal_context=appraisal_context,
                                )
                            )
                        except (
                            ValueError,
                            BackendError,
                            academic_claim_assessor.ClaimAssessorOutputError,
                        ) as exc:
                            candidate_proposition_verification_error = (
                                f"{type(exc).__name__}: {exc}"
                            )

                    _check_review_cancelled(job_id)

                    def candidate_triage_assessor(*, prompt, schema):
                        return academic_claim_assessor.generate_claim_assessor_output(
                            model,
                            tokenizer,
                            prompt,
                            schema,
                            max_tokens=3000,
                            diagnostic_raw_output=candidate_triage_raw,
                        )

                    candidate_triage = rp.triage_candidate_findings(
                        candidate_findings,
                        triage_evidence,
                        candidate_triage_assessor,
                        manifest_summary=manifest_summary,
                        appraisal_context=appraisal_context,
                    )
                except (
                    ValueError,
                    BackendError,
                    academic_claim_assessor.ClaimAssessorOutputError,
                ) as exc:
                    candidate_triage_error = (
                        f"{type(exc).__name__}: {exc}"
                    )

            combined = "\n\n".join(
                f"### Chunk {i}\n{txt}" for i, txt in enumerate(chunk_outputs, start=1)
            )

            # File-level synthesis
            _check_review_cancelled(job_id)
            _add_progress(job_id, "Synthesising file-level review...")
            with _chunk_reasoning(job_id):
                file_summary = rp.synthesize_file_review(
                    model, tokenizer, source_name, combined,
                    appraisal_context=appraisal_context,
                    manifest_summary=manifest_summary,
                    tables_text=tables_text,
                )

            trace["files"].append({
                "source_name": source_name,
                "chunk_count": len(chunks),
                "source_chunks": list(chunks),
                "chunk_outputs": list(chunk_outputs),
                "candidate_findings": list(candidate_findings),
                "finding_groups": list(finding_groups),
                "candidate_propositions": candidate_propositions,
                "candidate_propositions_raw": list(candidate_propositions_raw),
                "candidate_propositions_error": candidate_propositions_error,
                "candidate_proposition_verification": candidate_proposition_verification,
                "candidate_proposition_verification_raw": list(
                    candidate_proposition_verification_raw
                ),
                "candidate_proposition_verification_error": (
                    candidate_proposition_verification_error
                ),
                "candidate_triage": candidate_triage,
                "candidate_triage_raw": list(candidate_triage_raw),
                "candidate_triage_budget": candidate_triage_budget,
                "candidate_triage_note": candidate_triage_note,
                "candidate_triage_error": candidate_triage_error,
                "combined_chunk_review": combined,
                "tables_text": tables_text,
                "file_summary": file_summary,
            })

            file_summaries.append((source_name, file_summary))
            accounted_candidates.extend(candidate_findings)
            all_manifests.append(manifest)
            per_file_text[source_name] = text
            per_file_tables[source_name] = table_blocks
            per_file_chunks[source_name] = chunks
            all_extraction_notes.extend(f"{source_name}: {note}" for note in extraction_notes)

        # Retain the primary manuscript's source identity for the appraisal.
        file_path, source_name = inputs[0]
        manifest = all_manifests[0]
        text = per_file_text[source_name]
        table_blocks = per_file_tables[source_name]
        chunks = per_file_chunks[source_name]
        if supplementary:
            tables_text = "\n\n".join(
                f"## {name}\n{rp.tables_for_prompt(tables)}"
                for name, tables in per_file_tables.items())
            extraction_notes = all_extraction_notes
        synthesis_options = {"primary_source": source_name} if supplementary else {}

        passes = rp.REVIEW_PASSES
        passes_note = ""
        if llm_backend.thinking_enabled() and passes > rp.THINKING_PASSES:
            passes_note = (f"passes reduced from {passes} to {rp.THINKING_PASSES} "
                           f"because reasoning repeats with every pass "
                           f"(QWEN_THINKING_PASSES to override)")
            _add_progress(job_id, passes_note[0].upper() + passes_note[1:])
            passes = rp.THINKING_PASSES
        drafts = []
        kept_total = [0, 0]
        raw_total = [0, 0]
        all_corrections = []
        # With source verification on, the per-pass summary-based validation is
        # replaced by one check of the merged report against the manuscript
        # (below). QWEN_SOURCE_VERIFICATION=0 restores the previous behaviour.
        use_source_verification = sv.enabled()
        accounting_context = sca.synthesis_context(trace["files"])
        for attempt in range(passes):
            _check_review_cancelled(job_id)
            label = f" (pass {attempt + 1} of {passes})" if passes > 1 else ""
            _add_progress(job_id, f"Synthesising final report{label}...")
            # The first pass uses the validated review temperature and becomes
            # the base report; later passes use the configured repeat-pass
            # temperature, which defaults to the same validated baseline.
            temperature = None if attempt == 0 else rp.REPEAT_PASS_TEMPERATURE
            print(f"[synthesis] pass {attempt + 1} of {passes} "
                  f"(temperature={temperature or rp.TEMPERATURE})", flush=True)
            accounting_output = []
            draft = rp.synthesize_report(
                model, tokenizer, file_summaries,
                all_manifests=all_manifests,
                tables_text=tables_text,
                temperature=temperature,
                **({"accounting_context": accounting_context, "accounting_sink": accounting_output}
                   if accounting_context["candidate_ids"] else {}),
                **synthesis_options,
            )

            execution = review_jobs[job_id].get("execution")
            if execution is not None:
                execution["actual"]["final_synthesis_passes"] = attempt + 1
            raw_draft = draft

            corrections = rp.programmatic_post_checks(draft, manifest)
            if supplementary:
                for extra in all_manifests[1:]:
                    corrections.extend(f"Evidence from {extra.source_name}: {c}"
                                       for c in rp.programmatic_post_checks(draft, extra))
            all_corrections.extend(corrections)
            _check_review_cancelled(job_id)
            before = rp.count_report_items(draft)
            if use_source_verification:
                after = before
            else:
                _add_progress(job_id, f"Validating report against evidence{label}...")
                draft = rp.validate_report_against_evidence(
                    model, tokenizer, draft, file_summaries,
                    programmatic_corrections=corrections if corrections else None,
                    **synthesis_options,
                )
                after = rp.count_report_items(draft)
            for index in (0, 1):
                raw_total[index] += before[index]
                kept_total[index] += after[index]
            print(f"[validation] pass {attempt + 1}: concerns {before[0]} -> {after[0]}, "
                  f"checks {before[1]} -> {after[1]}", flush=True)
            trace["final_synthesis"].append({
                "pass": attempt + 1,
                "temperature": temperature if temperature is not None else rp.TEMPERATURE,
                "raw": raw_draft,
                "provenance_output": accounting_output[0] if accounting_output else None,
                "programmatic_corrections": list(corrections),
                "validated": draft,
                "validation": ("deferred to source verification after the merge"
                               if use_source_verification else "per-pass summary validation"),
                "items_before_validation": {
                    "concerns": before[0],
                    "checks": before[1],
                },
                "items_after_validation": {
                    "concerns": after[0],
                    "checks": after[1],
                },
            })
            drafts.append(draft)

        merge_stats = {}
        merge_decisions = []  # diagnostic record of the merge's own decisions; never read back into the report
        final_report = rp.merge_reports(drafts, stats=merge_stats, decisions=merge_decisions)
        trace["merge_decisions"] = merge_decisions
        trace["synthesis_accounting_input"] = final_report  # diagnostic-only snapshot before verification
        if use_source_verification:
            synthesis_note = (
                f"{merge_stats.get('passes', 1)} pass(es) merged, then verified once "
                f"against the manuscript; "
                f"{merge_stats.get('added', 0)} item(s) added to the base by later passes"
            )
        else:
            synthesis_note = (
                f"{merge_stats.get('passes', 1)} pass(es), each validated before merging; "
                f"validation kept {kept_total[0]}/{raw_total[0]} concerns and "
                f"{kept_total[1]}/{raw_total[1]} checks across passes; "
                f"{merge_stats.get('added', 0)} item(s) added to the base by later passes"
            )
        print(f"[synthesis] {synthesis_note}", flush=True)
        if passes > 1:
            _add_progress(job_id, f"Merged {passes} "
                                  f"{'synthesis' if use_source_verification else 'validated'} passes "
                                  f"({merge_stats.get('added', 0)} item(s) added).")

        # Source-grounded verification: one call, the manuscript itself as
        # evidence, a disposition per item applied by the application.
        verification = None
        verification_note = ""
        if use_source_verification:
            _check_review_cancelled(job_id)
            _add_progress(job_id, "Verifying report items against the manuscript...")
            verification_sources = _verification_sources(per_file_text, per_file_tables)
            # Kept so evidence cards locate passages in exactly the text the verifier saw.
            review_jobs[job_id]["verification_sources"] = verification_sources
            verification_raw = []
            verification = sv.verify_report(
                final_report, verification_sources,
                _source_verification_assessor(verification_raw),
                automated_flags=list(dict.fromkeys(all_corrections)),
                primary_source=source_name if supplementary else "",
                passthrough=(ReviewCancelled, llm_backend.InferenceCancelledError),
                retry_on=(academic_claim_assessor.ClaimAssessorOutputError,),
            )
            final_report = verification.report
            counts = verification.counts()
            verification_note = (
                f"{verification.status}"
                + (f" against {'the complete text' if verification.scope == 'complete' else 'retrieved passages'}"
                   if verification.scope else "")
                + "; " + ", ".join(f"{k.replace('_', ' ')} {v}" for k, v in sorted(counts.items()))
            )
            print(f"[verification] {verification_note}", flush=True)
            _add_progress(job_id, f"Source verification {verification_note}.")
            trace["source_verification"] = dict(verification.as_dict(),
                                                raw_output=list(verification_raw))
        trace["merged_pre_postprocessing"] = final_report
        trace["final_tables_text"] = tables_text

        # Post-processing passes
        _add_progress(job_id, "Post-processing...")
        all_text = "\n\n".join(f"## {name}\n{t}" for name, t in file_summaries) if supplementary else "\n\n".join(t for _, t in file_summaries)
        all_tables = [tbl for tables in per_file_tables.values() for _, tbl in tables]

        # A safety net independent of cause. Every stage below handles an empty
        # string without complaint, so a review with nothing in it assembles
        # into a tidy report: a header, and a citation check reporting -- quite
        # accurately -- that it found no unverifiable quotations. One did. An
        # empty review is a failure and should arrive as one.
        if not final_report.strip():
            raise ValueError(
                "The model returned nothing for this paper, so there is no "
                "review to write. The app-server log holds the generations."
            )

        # Half a report is still valid markdown, and reads as though it were
        # meant to end where it does. It should arrive as a failure instead.
        cut_short = rp.report_looks_truncated(final_report)
        if cut_short:
            raise ValueError(
                f"The synthesis is incomplete: {cut_short}. In thinking mode "
                f"this usually means the reasoning took the generation budget; "
                f"raise QWEN_THINKING_EXTRA_TOKENS or QWEN_SYNTHESIS_MAX_TOKENS "
                f"and run it again, or choose Instruct."
            )

        final_report = _apply_automatic_corrections(final_report, all_text, all_tables)
        final_report = rp.enforce_negative_constraints(final_report)
        final_report = rp.clean_markdown_math_artifacts(final_report)

        # Mechanical citation check: quotations must be findable in the
        # manuscript, and evidence must not cite the pipeline's own summary.
        # Quotations are checked against what was read from the documents, not
        # against a model's transcription of a page image.
        table_source = "\n".join(t for t in all_tables if _from_document(t))
        citation_source = text + "\n" + table_source
        if supplementary:
            citation_source = {name: body + "\n" + "\n".join(b for _, b in per_file_tables[name] if _from_document(b))
                               for name, body in per_file_text.items()}
        final_report = rp.annotate_concern_confidence(
            final_report, citation_source, table_source
        )
        report_problems = (rp.verify_report_citations(final_report, citation_source)
                           + rp.evidence_echo_problems(final_report)
                           + rp.overclaim_problems(final_report))
        quote_sources = rp.format_quote_sources(final_report, citation_source) if supplementary else ""
        # Both checks above read the quotation marks; strip only afterwards.
        final_report = rp.mark_unverified_quotations(final_report, citation_source)
        final_report = rp.report_reliability_banner(final_report) + final_report
        # Stated availability is not verified availability, and a strength
        # resting on one has twice been the thing a reviewer attacked.
        final_report = de.annotate_self_report_strengths(final_report)
        final_report += rp.format_action_list(final_report)
        if supplementary:
            for name, body in per_file_text.items():
                check = rp.format_consistency_check(body, per_file_tables[name])
                if check:
                    final_report += f"\n\n### Consistency evidence: {name}\n" + check
        else:
            final_report += rp.format_consistency_check(text, table_blocks)
        # Every chunk-level candidate is accounted for, deterministically.
        candidate_accounting = sv.account_candidates(
            accounted_candidates,
            verification.items if verification is not None else sv.extract_items(final_report),
            verification.decisions if verification is not None else None,
        )
        if verification is not None:
            final_report += sv.format_record(verification, candidate_accounting)
        final_report += quote_sources
        final_report += rp.format_citation_check(report_problems, final_report)

        # Add header
        from datetime import datetime
        header = (
            f"# Reviewer critical-appraisal aid\n\n"
            f"Generated: {datetime.now().isoformat(timespec='seconds')}\n"
            + "".join(f"{line}\n" for line in _model_header_lines())
            + f"Pipeline: {rp.PIPELINE_VERSION}\n"
            f"Appraisal policy: {rp.APPRAISAL_POLICY}\n"
            # Recorded so reviews accumulated over real use can be grouped by
            # mode afterwards; without it the comparison is unrecoverable.
            # Said out loud, because a silent repair to the text everything
            # else reads is the failure mode this pipeline keeps finding.
            + "".join(f"Extraction: {note}\n" for note in extraction_notes)
            + _reasoning_header_lines(
                review_jobs.get(job_id, {}).get("thinking_scope", "review"),
                passes_note)
            # Recorded so a run is never ambiguous about whether the extra
            # passes actually happened, and what they contributed.
            + f"Synthesis: {synthesis_note}\n"
            + (f"Verification: {verification_note}\n" if verification_note else "")
            + f"\n"
            f"Input files:\n- {file_path.name}\n\n"
            f"Evidence inventory:\n"
            f"- **{file_path.name}**: {manifest.summary_text()}\n\n---\n\n"
        )
        if supplementary:
            header = header[:header.index("Input files:")] + "Input files:\n" + "\n".join(
                f"- {name}" for _, name in inputs) + "\n\nEvidence inventory:\n" + "\n".join(
                f"- **{m.source_name}**: {m.summary_text()}" for m in all_manifests) + "\n\n---\n\n"
        final_report = header + final_report

        # --- Generate human-facing evidence appendix deterministically ---
        _add_progress(job_id, "Generating human evidence appendix...")
        from human_evidence_appendix import (
            build_evidence_cards,
            render_human_evidence_appendix,
        )
        evidence_cards = build_evidence_cards(final_report)
        appendix_lines = render_human_evidence_appendix(evidence_cards)
        appendix_lines += sv.format_candidate_appendix(candidate_accounting)

        if supplementary:
            review_jobs[job_id]["sources"] = citation_source

        # Kept so the reviewer can ask where the paper says something. It is
        # the same extracted text the report was built from, so an answer and a
        # concern are checked against exactly the same source.
        _check_review_cancelled(job_id)
        trace["final_report"] = final_report
        trace["synthesis_note"] = synthesis_note
        trace["merge_stats"] = dict(merge_stats)
        trace["candidate_accounting"] = candidate_accounting
        review_jobs[job_id]["source_verification"] = {
            "verification": verification.as_dict() if verification is not None else
                            {"status": "disabled (QWEN_SOURCE_VERIFICATION=0)"},
            "candidate_accounting": candidate_accounting,
        }

        review_jobs[job_id]["text"] = text
        review_jobs[job_id]["report"] = final_report
        review_jobs[job_id]["appendix"] = appendix_lines
        if review_jobs[job_id].get("development_mode"):
            review_jobs[job_id]["trace"] = trace
        try:
            diagnostic_path = sca.publish(trace, job_id)
            review_jobs[job_id]["synthesis_concern_accounting_path"] = str(diagnostic_path)
        except Exception as exc:  # Diagnostics must never change review completion.
            review_jobs[job_id]["synthesis_concern_accounting_error"] = str(exc)
            print(f"[synthesis-accounting] diagnostic unavailable for {job_id}: {exc}", flush=True)
        review_jobs[job_id]["status"] = "complete"
        _add_progress(job_id, "Review complete.")

    except (ReviewCancelled, llm_backend.InferenceCancelledError):
        review_jobs[job_id]["status"] = "cancelled"
        review_jobs[job_id]["error"] = None
        _add_progress(job_id, "Review cancelled.")

    except Exception as e:
        review_jobs[job_id]["status"] = "error"
        review_jobs[job_id]["error"] = f"{e}\n{traceback.format_exc()}"
        _add_progress(job_id, f"Error: {e}")

    finally:
        # Clean up temp files
        try:
            shutil.rmtree(tmp_dir, ignore_errors=True)
        except Exception:
            pass



# ---------------------------------------------------------------------------
# GET /api/review/status/{job_id} — SSE progress stream
# ---------------------------------------------------------------------------
@app.get("/api/review/status/{job_id}")
async def review_status(job_id: str):
    _restore_review(job_id)
    if job_id not in review_jobs:
        return JSONResponse({"error": "Unknown job"}, status_code=404)

    async def event_stream():
        seen = 0
        while True:
            job = review_jobs.get(job_id)
            if not job:
                break

            # Send any new progress messages
            progress = job["progress"]
            while seen < len(progress):
                data = json.dumps({"type": "progress", "message": progress[seen]})
                yield f"data: {data}\n\n"
                seen += 1

            if job["status"] == "complete":
                data = json.dumps({
                    "type": "complete",
                    "report": job["report"],
                    "has_appendix": bool(job.get("appendix")),
                    "has_development_trace": bool(job.get("development_mode") and job.get("trace")),
                    "has_evidence_cards": bool(
                        (job.get("source_verification") or {}).get("verification", {}).get("dispositions")),
                })
                yield f"data: {data}\n\n"
                break
            elif job["status"] == "error":
                data = json.dumps({"type": "error", "message": job.get("error", "Unknown error")})
                yield f"data: {data}\n\n"
                break
            elif job["status"] == "cancelled":
                data = json.dumps({
                    "type": "cancelled",
                    "message": "Review cancelled.",
                })
                yield f"data: {data}\n\n"
                break

            await asyncio.sleep(0.5)

    return StreamingResponse(event_stream(), media_type="text/event-stream")


# ---------------------------------------------------------------------------
# GET /api/review/report/{job_id} — download report as markdown
# ---------------------------------------------------------------------------
@app.get("/api/review/report/{job_id}")
async def download_report(job_id: str):
    _restore_review(job_id)
    job = review_jobs.get(job_id)
    if not job or not job.get("report"):
        return JSONResponse({"error": "Report not ready"}, status_code=404)

    filename = job.get("filename", "document").rsplit(".", 1)[0]
    return JSONResponse(
        content={"report": job["report"], "filename": f"{filename}_appraisal.md"},
    )


# ---------------------------------------------------------------------------
# GET /api/review/trace/{job_id} — diagnostic intermediate trace
# ---------------------------------------------------------------------------
@app.get("/api/review/trace/{job_id}")
async def download_review_trace(job_id: str):
    _restore_review(job_id)
    job = review_jobs.get(job_id)
    if not job or not job.get("development_mode"):
        return JSONResponse({"error": "Development trace not enabled for this review"}, status_code=404)
    if not job.get("trace"):
        return JSONResponse({"error": "Trace not ready"}, status_code=404)

    filename = job.get("filename", "document").rsplit(".", 1)[0]
    return JSONResponse(
        content={
            "trace": job["trace"],
            "filename": f"{filename}_review_trace.json",
        }
    )


# Separate sidecars: never injected into report, appendix, prompts or SSE output.
def _read_review_availability(job_id):
    data = ea.read_sidecar(job_id)
    status = review_jobs.get(job_id, {}).get("evidence_availability") or {}
    if status.get("state") == "AUDIT_INCOMPLETE":
        data["integrity_state"] = "AUDIT_INCOMPLETE"
        data["instrumentation_errors"] = list(dict.fromkeys(data.get("instrumentation_errors", []) + status.get("errors", [])))
    return data


@app.get("/api/review/evidence-availability/{job_id}")
async def download_review_availability(job_id: str):
    try:
        data = _read_review_availability(job_id)
    except (ValueError, OSError) as exc:
        return JSONResponse({"error": str(exc)}, status_code=404)
    return JSONResponse(content=data)


@app.get("/api/review/coverage/{job_id}")
async def download_review_coverage(job_id: str):
    try:
        data = _read_review_availability(job_id)
    except (ValueError, OSError) as exc:
        return JSONResponse({"error": str(exc)}, status_code=404)
    return JSONResponse(content={"notice": ea.coverage_notice(data), "authority": "AVAILABILITY ONLY"})


# ---------------------------------------------------------------------------
# GET /api/review/source-verification/{job_id} — per-item audit record
# ---------------------------------------------------------------------------
@app.get("/api/review/source-verification/{job_id}")
async def download_source_verification(job_id: str):
    _restore_review(job_id)
    job = review_jobs.get(job_id)
    if not job or not job.get("source_verification"):
        return JSONResponse({"error": "Source verification record not ready"}, status_code=404)
    return JSONResponse(content=job["source_verification"])


# ---------------------------------------------------------------------------
# Evidence cards (prototype): read-only views of stored records. Reviewer
# decisions stay in the browser and never alter the stored review.
# ---------------------------------------------------------------------------
def _evidence_card_set(job_id: str):
    _restore_review(job_id)
    job = review_jobs.get(job_id)
    if not job:
        return None
    verification = (job.get("source_verification") or {}).get("verification") or {}
    if not verification.get("dispositions"):
        # An older saved review may hold the card snapshot without the
        # dispositions it was built from; show the cards as saved rather than
        # none at all. Nothing is rebuilt or changed.
        snapshot = job.get("evidence_cards_snapshot")
        if isinstance(snapshot, dict) and snapshot.get("cards"):
            return snapshot
        return None
    if not (job.get("verification_sources") or job.get("sources") or job.get("text")) \
            and job.get("evidence_cards_snapshot"):
        # A saved review without its manuscript text: show the cards as saved.
        return job["evidence_cards_snapshot"]
    sources = job.get("verification_sources") or job.get("sources") or {"manuscript": job.get("text", "")}
    return ec.build_cards(verification, sources)


@app.get("/api/review/evidence-cards/{job_id}")
async def download_evidence_cards(job_id: str):
    cards = _evidence_card_set(job_id)
    if cards is None:
        return JSONResponse({"error": "Evidence cards not available for this review"}, status_code=404)
    return JSONResponse(content=cards)


@app.get("/review/evidence-cards/{job_id}")
async def view_evidence_cards(job_id: str):
    cards = _evidence_card_set(job_id)
    if cards is None:
        return HTMLResponse("<p>Evidence cards are not available for this review.</p>", status_code=404)
    name = review_jobs.get(job_id, {}).get("filename", "manuscript")
    sync = None
    if _persist_sessions and rs.exists(job_id):
        try:
            fingerprint = rs.read_manifest(job_id).get("card_fingerprint")
        except (rs.StoreError, OSError):
            fingerprint = None
        if fingerprint:
            sync = {"url": f"/api/review/{job_id}/decisions", "fingerprint": fingerprint}
    links = _review_links(job_id, cards) or {}
    nav = {"job_id": job_id, "links": {f["id"]: f for f in links.get("findings", []) if f.get("has_card")}} \
        if rs.valid_job_id(job_id) else None
    if nav:
        nav["documents"] = _passage_documents(job_id)
    return HTMLResponse(ec.render_html(cards, f"Evidence cards: {name}", f"job-{job_id}", sync=sync, nav=nav),
                        headers={"Cache-Control": "no-store"})


@app.get("/review/evidence-cards/{job_id}/print")
async def print_evidence_cards(job_id: str, mode: str = "summary"):
    """A dedicated print view of the Evidence Cards (summary or detailed).

    Printing the Review Workspace prints the whole application, with the cards
    in a clipped frame; this page holds only the cards, every one in full.
    Decisions are read from the local review store at request time, so the
    current saved decisions are printed; read-only."""
    if not rs.valid_job_id(job_id):
        return HTMLResponse("<p>Unknown review.</p>", status_code=404)
    cards = _evidence_card_set(job_id)
    if cards is None:
        return HTMLResponse("<p>Evidence cards are not available for this review.</p>", status_code=404)
    job = review_jobs.get(job_id, {})
    meta = {"job_id": job_id, "filename": job.get("filename"), "printed_at": rs.now(),
            "doc_id": f"job-{job_id}", "decision_source": "browser"}
    decisions = {}
    if _persist_sessions and rs.exists(job_id):
        try:
            stored = rs.read_decisions(job_id)
            decisions = stored.get("decisions") or {}
            meta.update(decision_source="saved", decisions_saved_at=stored.get("updated_at"))
            meta["filename"] = meta["filename"] or rs.read_manifest(job_id).get("filename")
        except (rs.StoreError, OSError):
            meta["decision_source"] = "unavailable"
    return HTMLResponse(print_view.render(cards, decisions, meta, mode),
                        headers={"Cache-Control": "no-store"})


def _review_links(job_id: str, cards=None):
    """Links between the three views, computed from the stored appraisal and
    verification record each time; nothing is stored or changed."""
    _restore_review(job_id)
    job = review_jobs.get(job_id)
    if not job or not job.get("report"):
        return None
    verification = (job.get("source_verification") or {}).get("verification") or {}
    links = rl.build_links(job["report"], verification)
    cards = cards if cards is not None else _evidence_card_set(job_id)
    card_list = (cards or {}).get("cards") or []
    links["summary"]["with_warnings"] = sum(1 for c in card_list if c.get("warnings"))
    links["summary"]["unauthenticated_primary"] = sum(1 for c in card_list if c.get("quotation_notice"))
    links["job_id"] = job_id
    return links


@app.get("/api/review/{job_id}/links")
async def get_review_links(job_id: str):
    links = _review_links(job_id)
    if links is None:
        return JSONResponse({"error": "No completed review with that id."}, status_code=404)
    return links


# ---------------------------------------------------------------------------
# Saved reviews: list, open, close, delete, decisions. Local files only.
# ---------------------------------------------------------------------------
def _store_error(exc: Exception, status: int = 400):
    return JSONResponse({"error": str(exc)}, status_code=status)


_last_save_error: dict = {}


@app.get("/api/reviews")
async def list_saved_reviews():
    """Saved reviews, with the store's location and any reason it cannot be
    used, so that a missing store is reported rather than shown as empty."""
    return {"persistent": _persist_sessions,
            "store": rs.store_status() if _persist_sessions else None,
            "last_save_error": dict(_last_save_error) or None,
            "reviews": rs.list_sessions() if _persist_sessions else []}


@app.post("/api/review/{job_id}/open")
async def open_saved_review(job_id: str):
    if not _persist_sessions or not rs.exists(job_id):
        return JSONResponse({"error": "No saved review with that id."}, status_code=404)
    try:
        manifest = rs.set_state(job_id, "open")
    except (rs.StoreError, OSError) as exc:
        return _store_error(exc, 409)
    if not _restore_review(job_id):
        return JSONResponse({"error": "The saved review could not be restored."}, status_code=409)
    return rs.summary(manifest)


@app.post("/api/review/{job_id}/close")
async def close_saved_review(job_id: str):
    """Remove a review from the active workspace. Its records are kept."""
    if not _persist_sessions or not rs.exists(job_id):
        return JSONResponse({"error": "No saved review with that id."}, status_code=404)
    try:
        return rs.summary(rs.set_state(job_id, "closed"))
    except (rs.StoreError, OSError) as exc:
        return _store_error(exc, 409)


@app.delete("/api/review/{job_id}")
async def delete_saved_review(job_id: str, request: dict):
    """Delete a saved review and its records. The id must be repeated in
    confirm_job_id; a running review cannot be deleted."""
    if not rs.valid_job_id(job_id):
        return JSONResponse({"error": "Invalid review id."}, status_code=400)
    if (request or {}).get("confirm_job_id") != job_id:
        return JSONResponse({"error": "Deletion needs the review id repeated as confirmation."}, status_code=400)
    job = review_jobs.get(job_id)
    if job and job.get("status") == "running":
        return JSONResponse({"error": "A running review cannot be deleted; cancel it first."}, status_code=409)
    removed = False
    if _persist_sessions and rs.exists(job_id):
        try:
            rs.delete(job_id, request.get("confirm_job_id"))
            removed = True
        except (rs.StoreError, OSError) as exc:
            return _store_error(exc, 409)
    sidecar = ea.storage_root() / ea.safe_id(job_id)
    if _persist_sessions and sidecar.is_dir():
        shutil.rmtree(sidecar, ignore_errors=True)
    if review_jobs.pop(job_id, None) is not None:
        removed = True
    if not removed:
        return JSONResponse({"error": "No review with that id."}, status_code=404)
    return {"deleted": job_id}


# ---------------------------------------------------------------------------
# Review Workspace: original documents and the local PDF viewer
# ---------------------------------------------------------------------------
# Documents are addressed only as (review id, document id); both are validated
# and resolved through the review's own manifest, so no request can name a
# path. Bytes are re-hashed before every response. PDF.js is served from
# app/vendor/pdfjs only; nothing is fetched from outside this computer.
VENDOR_PDFJS = SCRIPT_DIR / "vendor" / "pdfjs"
_VENDOR_TYPES = {".mjs": "text/javascript; charset=utf-8", ".js": "text/javascript; charset=utf-8",
                 ".bcmap": "application/octet-stream", ".pfb": "application/octet-stream",
                 ".ttf": "font/ttf", ".wasm": "application/wasm", ".icc": "application/vnd.iccprofile"}
_VENDOR_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,80}$")
_DOCUMENT_HEADERS = {"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff",
                     "Content-Security-Policy": "sandbox; default-src 'none'",
                     "Referrer-Policy": "no-referrer"}


@app.get("/vendor/pdfjs/{name}")
@app.get("/vendor/pdfjs/{folder}/{name}")
async def vendor_pdfjs(name: str, folder: str = ""):
    if folder not in ("", "cmaps", "standard_fonts", "wasm", "iccs") or not _VENDOR_NAME.match(name):
        return JSONResponse({"error": "Not found."}, status_code=404)
    path = VENDOR_PDFJS / folder / name if folder else VENDOR_PDFJS / name
    media = _VENDOR_TYPES.get(path.suffix.lower())
    if media is None or not path.is_file():
        return JSONResponse({"error": "Not found."}, status_code=404)
    return FileResponse(path, media_type=media, headers={"X-Content-Type-Options": "nosniff"})


def _passage_documents(job_id: str):
    if not (rs.valid_job_id(job_id) and _persist_sessions and rs.exists(job_id)):
        return []
    try:
        docs = rs.documents(job_id)
        # Older single-PDF sessions may retain the upload-time source name
        # (e.g. upload.pdf), but no source_label in the document descriptor.
        # Recover navigation metadata only when the verified saved packet
        # establishes the relationship; never guess by filename or list order.
        if len(docs) == 1 and not docs[0].get("source_label"):
            manifest = rs.read_manifest(job_id)
            saved = rs.load_job(job_id)  # verifies all stored file hashes
            sources = saved.get("verification_sources") or saved.get("sources") or {}
            text = saved.get("text")
            doc = docs[0]
            if (doc.get("role") == "primary" and doc.get("suffix") == ".pdf"
                    and doc.get("available") and not manifest.get("supplements")
                    and doc.get("sha256") == manifest.get("manuscript_sha256")
                    and manifest.get("files", {}).get(doc.get("file")) == doc.get("sha256")
                    and manifest.get("input_sha256") == [doc.get("sha256")]
                    and isinstance(text, str) and text
                    and rs.sha256_text(text) == manifest.get("text_sha256")
                    and isinstance(sources, dict) and len(sources) == 1
                    and next(iter(sources.values())) == text):
                docs = [dict(doc, source_label=next(iter(sources)))]
        return docs
    except (rs.StoreError, OSError, ValueError):
        return []  # No reliable document binding: no navigation controls.


@app.get("/review/passage-match.js")
async def passage_match_script():
    return FileResponse(SCRIPT_DIR.parent / "passage_match" / "passage_match.js",
                        media_type="text/javascript", headers={"X-Content-Type-Options": "nosniff"})


@app.get("/review/passage-navigation.js")
async def passage_navigation_script():
    return FileResponse(SCRIPT_DIR / "passage_navigation.js", media_type="text/javascript",
                        headers={"X-Content-Type-Options": "nosniff"})


@app.get("/review/document-viewer")
async def document_viewer_page():
    return FileResponse(SCRIPT_DIR / "document_viewer.html", media_type="text/html; charset=utf-8",
                        headers={"Cache-Control": "no-store"})


def _public_document(record: dict) -> dict:
    keys = ("id", "role", "original_filename", "source_label", "suffix", "media_type", "sha256", "bytes",
            "available")
    out = {k: record.get(k) for k in keys}
    out["viewable"] = bool(record.get("available")) and record.get("suffix") == ".pdf"
    return out


@app.get("/api/review/{job_id}/documents")
async def list_review_documents(job_id: str):
    if not rs.valid_job_id(job_id):
        return JSONResponse({"error": "Invalid review id."}, status_code=400)
    if not (_persist_sessions and rs.exists(job_id)):
        return JSONResponse({"documents": [], "saved": False,
                             "note": "Original documents are kept only with saved reviews."})
    try:
        docs = [_public_document(d) for d in rs.documents(job_id)]
    except (rs.StoreError, OSError) as exc:
        return _store_error(exc, 409)
    return JSONResponse({"documents": docs, "saved": True}, headers={"Cache-Control": "no-store"})


def _content_disposition(kind: str, filename: str) -> str:
    from urllib.parse import quote
    ascii_name = re.sub(r"[^A-Za-z0-9._-]+", "_", filename)[:120] or "document"
    return f"{kind}; filename=\"{ascii_name}\"; filename*=UTF-8''{quote(filename[:200])}"


@app.get("/api/review/{job_id}/documents/{doc_id}")
async def get_review_document(job_id: str, doc_id: str, download: int = 0):
    if not rs.valid_job_id(job_id) or not rs.valid_document_id(doc_id):
        return JSONResponse({"error": "Invalid id."}, status_code=400)
    if not (_persist_sessions and rs.exists(job_id)):
        return JSONResponse({"error": "No saved review with that id."}, status_code=404)
    try:
        path, record = rs.document_file(job_id, doc_id)
    except FileNotFoundError:
        return JSONResponse({"error": "This document is not stored with the review."}, status_code=404)
    except (rs.StoreError, OSError) as exc:
        return _store_error(exc, 409)
    suffix = record.get("suffix") or ""
    name = record.get("original_filename") or f"{doc_id}{suffix}"
    if not name.lower().endswith(suffix):
        name += suffix
    kind = "inline" if suffix == ".pdf" and not download else "attachment"
    headers = dict(_DOCUMENT_HEADERS, **{"Content-Disposition": _content_disposition(kind, name)})
    return FileResponse(path, media_type=rs.DOCUMENT_MEDIA_TYPES[suffix], headers=headers)


@app.post("/api/review/{job_id}/documents/reattach")
async def reattach_review_document(job_id: str, file: UploadFile = File(...)):
    """Attach an original document to an older saved review. Accepted only when
    its SHA-256 equals one recorded for this review."""
    if not rs.valid_job_id(job_id):
        return JSONResponse({"error": "Invalid review id."}, status_code=400)
    if not (_persist_sessions and rs.exists(job_id)):
        return JSONResponse({"error": "No saved review with that id."}, status_code=404)
    tmp = Path(tempfile.mkdtemp(prefix=f"reattach_{job_id}_"))
    try:
        dest, written = tmp / "upload.bin", 0
        with open(dest, "wb") as fh:
            while True:
                chunk = file.file.read(REVIEW_UPLOAD_CHUNK_BYTES)
                if not chunk:
                    break
                written += len(chunk)
                if written > MAX_REVIEW_UPLOAD_BYTES:
                    return JSONResponse({"error": "The file exceeds the upload limit."}, status_code=413)
                fh.write(chunk)
        try:
            record = rs.reattach_document(job_id, dest, file.filename)
        except (rs.StoreError, OSError) as exc:
            return _store_error(exc, 409)
        out = _public_document(record)
        out["already_stored"] = record.get("already_stored", False)
        return out
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------------------
# Vision: server capability and what each review actually did
# ---------------------------------------------------------------------------
_VISION_CAP_CACHE = {"at": 0.0, "value": None}


@app.get("/api/vision-capability")
async def vision_capability_endpoint():
    now_t = time.time()
    if _VISION_CAP_CACHE["value"] is None or now_t - _VISION_CAP_CACHE["at"] > 20:
        _VISION_CAP_CACHE.update(at=now_t, value=_vision_capability_safe())
    return JSONResponse(_VISION_CAP_CACHE["value"], headers={"Cache-Control": "no-store"})


_VISION_METHODS = ("vision-table-rescue", "vision-table-page", "render-table-page")


def _ledger_vision_events(job_id: str) -> Optional[list]:
    """Vision events from a review's evidence ledger, if it has one. Methods,
    statuses and the ledger's own fixed reasons only."""
    path = ea.storage_root() / ea.safe_id(job_id) / "LEDGER.json"
    try:
        ledger = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    found = []

    def walk(node):
        if isinstance(node, dict):
            if node.get("method") in _VISION_METHODS and isinstance(node.get("status"), str):
                found.append({"method": node["method"], "status": node["status"],
                              "page": node.get("physical_page"), "reason": node.get("reason")})
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)
    walk(ledger)
    return found


def _historical_vision(job_id: str, report: str) -> dict:
    """What an older review's own records say about vision. Nothing is inferred
    beyond them: capability at the time was never recorded."""
    lines = [ln.strip() for ln in (report or "").splitlines()[:40] if ln.strip().startswith("Extraction:")]
    events = _ledger_vision_events(job_id)
    out = {"recorded": False, "report_extraction_lines": lines,
           "capability_at_start": None, "ledger_available": events is not None}
    if events is not None:
        pages = [e for e in events if e["method"] == "vision-table-page"]
        out["ledger"] = {
            "pages_submitted": sum(1 for e in pages if e["status"] == "STARTED"),
            "responses_with_results": sum(1 for e in pages if e["status"] == "COMPLETED_WITH_RESULTS"),
            "responses_empty_or_no_table": sum(1 for e in pages if e["status"] == "COMPLETED_EMPTY"),
            "pages_over_limit": sum(1 for e in pages if e["status"] == "SKIPPED"),
            "pages_not_rendered": sum(1 for e in events if e["method"] == "render-table-page" and e["status"] == "FAILED"),
            "rescue_decisions": sorted({f"{e['status']}: {e['reason']}" for e in events
                                        if e["method"] == "vision-table-rescue" and e.get("reason")}),
        }
    return out


@app.get("/api/review/{job_id}/vision")
async def review_vision(job_id: str):
    if not rs.valid_job_id(job_id):
        return JSONResponse({"error": "Invalid review id."}, status_code=400)
    job = review_jobs.get(job_id)
    if job and isinstance(job.get("vision_record"), dict):
        return dict(job["vision_record"], recorded=True)
    if _persist_sessions and rs.exists(job_id):
        try:
            manifest = rs.read_manifest(job_id)
        except (rs.StoreError, OSError) as exc:
            return _store_error(exc, 409)
        if isinstance(manifest.get("vision"), dict):
            return dict(manifest["vision"], recorded=True)
        report_path = rs.session_dir(job_id) / "report.md"
        report = report_path.read_text(encoding="utf-8") if "report.md" in manifest["files"] else ""
        return _historical_vision(job_id, report)
    if job:
        return _historical_vision(job_id, job.get("report") or "")
    return JSONResponse({"error": "No review with that id."}, status_code=404)


@app.get("/api/review/{job_id}/decisions")
async def get_review_decisions(job_id: str):
    if not _persist_sessions or not rs.exists(job_id):
        return JSONResponse({"error": "This review is not in the local review store."}, status_code=404)
    try:
        return rs.read_decisions(job_id)
    except (rs.StoreError, OSError) as exc:
        return _store_error(exc, 409)


def _decisions_export(job_id: str, request: dict, concise: bool):
    """Shared by both decision exports, so they validate and use exactly the
    same decisions and metadata; only the renderer differs."""
    if not rs.valid_job_id(job_id):
        return JSONResponse({"error": "Unknown review."}, status_code=404)
    cards = _evidence_card_set(job_id)
    if cards is None:
        return JSONResponse({"error": "Evidence cards not available for this review"}, status_code=404)
    labels = {c.get("label") for c in cards.get("cards") or []}
    try:
        decisions = rs._clean_decisions((request or {}).get("decisions") or {}, labels)
    except rs.StoreError as exc:
        return JSONResponse({"error": str(exc)}, status_code=400)
    job = review_jobs.get(job_id, {})
    meta = {"job_id": job_id, "filename": job.get("filename"), "completed_at": job.get("completed_at"),
            "exported_at": rs.now()}
    if _persist_sessions and rs.exists(job_id):
        try:
            manifest = rs.read_manifest(job_id)
            meta["filename"] = meta["filename"] or manifest.get("filename")
            meta["completed_at"] = meta["completed_at"] or manifest.get("completed_at")
            stored = rs.read_decisions(job_id)
            if stored.get("saved"):
                meta["decisions_saved_at"] = (stored.get("updated_at") if stored.get("decisions") == decisions
                                              else "the local review store holds different decisions; this "
                                                   "record shows the decisions on the Evidence Cards page")
        except (rs.StoreError, OSError):
            pass
    render = dreport.render_concise_markdown if concise else dreport.render_markdown
    body = render(cards, decisions, meta)
    stem = re.sub(r"[^A-Za-z0-9._-]+", "_", Path(meta.get("filename") or "manuscript").stem)[:80] or "manuscript"
    suffix = "reviewer_summary" if concise else "reviewer_decisions_full_audit"
    return HTMLResponse(body, media_type="text/markdown; charset=utf-8", headers={
        "Content-Disposition": f'attachment; filename="{stem}_{suffix}.md"', "Cache-Control": "no-store"})


@app.post("/api/review/{job_id}/decisions.md")
async def export_review_decisions_markdown(job_id: str, request: dict):
    """The reviewer's decisions as the full audit record in Markdown.

    Read-only: built from the stored Evidence Cards and the decisions the
    Evidence Cards page currently holds (the same object its JSON export
    writes). Decisions are validated as the store validates them; nothing is
    saved or changed, and no model is called.
    """
    return _decisions_export(job_id, request, concise=False)


@app.post("/api/review/{job_id}/decisions-summary.md")
async def export_review_decisions_summary(job_id: str, request: dict):
    """The concise reviewer summary: the same decisions as the audit record,
    without quotations, verification narratives or technical records.
    Read-only; nothing is saved or changed, and no model is called."""
    return _decisions_export(job_id, request, concise=True)


@app.put("/api/review/{job_id}/decisions")
async def put_review_decisions(job_id: str, request: dict):
    if not _persist_sessions or not rs.exists(job_id):
        return JSONResponse({"error": "This review is not in the local review store."}, status_code=404)
    try:
        return rs.write_decisions(job_id, (request or {}).get("card_fingerprint"),
                                  (request or {}).get("decisions"))
    except rs.StoreError as exc:
        return _store_error(exc, 400)
    except OSError as exc:
        return _store_error(exc, 500)


# ---------------------------------------------------------------------------
# GET /api/review/appendix/{job_id} — download evidence appendix
# ---------------------------------------------------------------------------
def _intermediate_ai_text(trace):
    """AI-generated intermediate text saved with a review (Development mode
    only), as (label, text) pairs; None when the review did not keep it. Used
    only to say where an unauthenticated quotation came from. The manuscript
    chunks in the trace are deliberately excluded: they are not AI text."""
    if not isinstance(trace, dict) or not isinstance(trace.get("files"), list):
        return None
    out = []
    for entry in trace["files"]:
        if not isinstance(entry, dict):
            continue
        name = entry.get("source_name") or "a source file"
        for key, label in (("file_summary", "the AI file summary"),
                           ("combined_chunk_review", "the AI section notes")):
            value = entry.get(key)
            if isinstance(value, str) and value.strip():
                out.append((f"{label} for {name}", value))
        for value in entry.get("chunk_outputs") or []:
            if isinstance(value, str) and value.strip():
                out.append((f"the AI section notes for {name}", value))
    return out


@app.get("/api/review/appendix/{job_id}")
async def download_appendix(job_id: str, version: str = "current"):
    """The Human Evidence Appendix.

    version=current (default): the concise reviewer-facing presentation,
    rendered now from the saved appraisal, Evidence Cards and observation
    record. Works for reviews completed before it existed; no model is run.
    version=original: the appendix exactly as stored when the review
    completed, including the full list of initial-reading observations.
    The response names which one it is; nothing is stored or changed.
    """
    _restore_review(job_id)
    job = review_jobs.get(job_id)
    headers = {"Cache-Control": "no-store"}
    if not job:
        return JSONResponse({"error": "Appendix not ready"}, status_code=404)
    stored = job.get("appendix")
    if version == "original":
        if not stored:
            return JSONResponse({"error": "No original appendix was saved with this review"}, status_code=404)
        return JSONResponse({"appendix": stored, "presentation": "original",
                             "original_available": True}, headers=headers)
    if not job.get("report"):
        if not stored:
            return JSONResponse({"error": "Appendix not ready"}, status_code=404)
        return JSONResponse({"appendix": stored, "presentation": "original",
                             "original_available": True}, headers=headers)
    generated_at = rs.now()
    body = _current_appendix(job_id, generated_at)
    return JSONResponse({"appendix": body, "presentation": "current", "generated_at": generated_at,
                         "original_available": bool(stored)}, headers=headers)


def _current_appendix(job_id: str, generated_at: str) -> str:
    """The reviewer-facing appendix, rendered now from saved data. Shared by
    the appendix tab, its Markdown download and its print page."""
    job = review_jobs.get(job_id) or {}
    cards = _evidence_card_set(job_id)
    links = _review_links(job_id, cards)
    candidate_accounting = (job.get("source_verification") or {}).get("candidate_accounting")
    # The manuscript text the verifier saw, as the Evidence Cards use it; None
    # for a saved review without its text (the appendix then says so).
    sources = job.get("verification_sources") or job.get("sources") or \
        ({"manuscript": job["text"]} if job.get("text") else None)
    return appendix_view.render(job["report"], links, cards, candidate_accounting, generated_at,
                                intermediate=_intermediate_ai_text(job.get("trace")),
                                sources=sources)


def _print_meta(job_id: str) -> dict:
    job = review_jobs.get(job_id) or {}
    meta = {"job_id": job_id, "filename": job.get("filename"), "printed_at": rs.now(),
            "completed_at": job.get("completed_at")}
    if _persist_sessions and rs.exists(job_id) and not meta["filename"]:
        try:
            meta["filename"] = rs.read_manifest(job_id).get("filename")
        except (rs.StoreError, OSError):
            pass
    return meta


@app.get("/review/{job_id}/print/appraisal")
async def print_critical_appraisal(job_id: str):
    """The saved Critical Appraisal as a print page; read-only, no model."""
    if not rs.valid_job_id(job_id):
        return HTMLResponse("<p>Unknown review.</p>", status_code=404)
    _restore_review(job_id)
    job = review_jobs.get(job_id)
    if not job or not job.get("report"):
        return HTMLResponse("<p>No saved appraisal is available for this review.</p>", status_code=404)
    return HTMLResponse(print_view.render_appraisal(job["report"], _print_meta(job_id)),
                        headers={"Cache-Control": "no-store"})


@app.get("/review/{job_id}/print/appendix")
async def print_human_evidence_appendix(job_id: str):
    """The current Human Evidence Appendix as a print page, rendered from saved
    data exactly as the appendix tab shows it; read-only, no model."""
    if not rs.valid_job_id(job_id):
        return HTMLResponse("<p>Unknown review.</p>", status_code=404)
    _restore_review(job_id)
    job = review_jobs.get(job_id)
    if not job or not job.get("report"):
        return HTMLResponse("<p>No saved appraisal is available for this review.</p>", status_code=404)
    meta = _print_meta(job_id)
    body = _current_appendix(job_id, meta["printed_at"])
    return HTMLResponse(print_view.render_appendix(body, meta), headers={"Cache-Control": "no-store"})


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Local Qwen chat + review server")
    parser.add_argument("--model", default=MODEL_NAME,
                        help="Path to a .gguf file, or an MLX repo id")
    parser.add_argument("--backend", choices=["llama-server", "llama-cpp", "mlx"],
                        default=None,
                        help="Force a backend (default: inferred from --model)")
    parser.add_argument("--llama-url", default=None,
                        help="Base URL of the llama-server instance")
    parser.add_argument("--port", type=int, default=8080, help="Server port")
    parser.add_argument("--host", default="127.0.0.1", help="Bind address")
    args = parser.parse_args()

    if args.llama_url:
        os.environ["LLAMA_SERVER_URL"] = args.llama_url
    if args.backend:
        set_backend(args.backend)

    MODEL_NAME = resolve_model_choice(args.model)
    rp.MODEL_NAME = MODEL_NAME
    SERVER_HOST = args.host
    SERVER_PORT = args.port
    _persist_sessions = os.environ.get("QWEN_REVIEW_STORE", "").strip().lower() != "off"

    # Logged so that it is always clear which installation and which review
    # store a running app uses, when more than one copy exists on a machine.
    print(f"Application folder: {ROOT_DIR}", flush=True)
    print(f"Review store: {rs.store_root() if _persist_sessions else 'disabled (QWEN_REVIEW_STORE=off)'}",
          flush=True)
    if _persist_sessions and rs.store_status()["error"]:
        # Said plainly rather than showing an empty list: the configured store
        # is used as given and the default store is not consulted instead.
        print("WARNING: " + rs.store_status()["error"], flush=True)
    print(f"llama-server: {ms.connection_mode(MODEL_NAME)} at {ms.server_url()}", flush=True)

    uvicorn.run(app, host=args.host, port=args.port)
