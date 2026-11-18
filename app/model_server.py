"""
model_server.py -- connection status, model switching and model discovery.

The browser needs to know four separate things about the model server, and
used to be told only one of them (whether the app answered at all):

  who manages it     managed (a launcher here started llama-server and may
                     stop it to change model), external (somebody else started
                     it; the app only connects), or in-process (MLX)
  connection         connected, loading, or unreachable
  which model        the model the server reports, not the one requested
  switch progress    loading, loaded, or failed, with the reason

Nothing here starts or stops a process directly. A switch runs
scripts/qwen_service.sh switch-model, which stops only a llama-server whose
pid it recorded itself. Kept apart from server.py so it can be tested without
a model, a server, or a network.
"""

from __future__ import annotations

import os
import re
import subprocess
import threading
import time
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional

import llm_backend

MODE_MANAGED = llm_backend.LLAMA_MODE_MANAGED
MODE_EXTERNAL = llm_backend.LLAMA_MODE_EXTERNAL
MODE_IN_PROCESS = "in-process"

EXTERNAL_RESTART_REASON = (
    "llama-server is managed outside this app (external mode). Restart it "
    "yourself with the model you want; this page detects the change."
)
FULL_RESTART_REASON = (
    "Changing between an MLX model and a llama.cpp model restarts the app, "
    "which is only possible when it was started with scripts/qwen_service.sh."
)


def service_managed() -> bool:
    """True when scripts/qwen_service.sh started this app and may restart it."""
    return os.environ.get("QWEN_SERVICE_MANAGED", "").strip() == "1"


def connection_mode(model_name: str) -> str:
    """managed, external or in-process, for the model this app is using."""
    try:
        backend = llm_backend.resolve_backend(model_name)
    except llm_backend.BackendError:
        return MODE_EXTERNAL
    if backend != llm_backend.BACKEND_LLAMA_SERVER:
        return MODE_IN_PROCESS
    # With no launcher to say otherwise, the app owns nothing it could restart.
    return llm_backend.llama_server_mode() or MODE_EXTERNAL


def server_url() -> str:
    return (os.environ.get("LLAMA_SERVER_URL")
            or llm_backend.DEFAULT_LLAMA_SERVER_URL).rstrip("/")


def restart_availability(mode: str) -> Dict[str, Any]:
    """Whether the browser may offer Restart, and why not when it may not."""
    if mode == MODE_EXTERNAL:
        return {"available": False, "reason": EXTERNAL_RESTART_REASON}
    if mode == MODE_MANAGED:
        return {"available": True, "reason": ""}
    if service_managed():
        return {"available": True, "reason": ""}
    return {"available": False, "reason": FULL_RESTART_REASON}


# ---------------------------------------------------------------------------
# Switch state
# ---------------------------------------------------------------------------

class SwitchInProgress(RuntimeError):
    """A model-dependent operation was refused because a model is loading."""


class ModelSwitch:
    """
    The state of the most recent in-place model switch, and the
    model-dependent operations in progress, shared by threads.

    The two exclude each other under one lock: a switch cannot begin while an
    appraisal, chat answer or other model call is running, and none of those
    can begin while a model is loading. A switch therefore never interrupts
    work silently; the user finishes or cancels it first.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._operations: Dict[str, int] = {}
        self._state: Dict[str, Any] = {
            "state": "idle", "target": None, "target_name": None,
            "error": None, "detail": [], "started_at": None,
            "finished_at": None, "loaded_model": None, "model_identified": None,
        }

    def snapshot(self) -> Dict[str, Any]:
        with self._lock:
            state = dict(self._state)
            state["detail"] = list(state["detail"])
            state["active_operations"] = dict(self._operations)
            return state

    def busy(self) -> bool:
        with self._lock:
            return self._state["state"] == "loading"

    def acquire(self, kind: str) -> str:
        """Register one model-dependent operation; refused while loading."""
        with self._lock:
            if self._state["state"] == "loading":
                raise SwitchInProgress(
                    f"A model is loading ({self._state.get('target_name') or 'model'}). "
                    "Try again when the status shows it loaded.")
            self._operations[kind] = self._operations.get(kind, 0) + 1
        return kind

    def release(self, kind: str) -> None:
        with self._lock:
            remaining = self._operations.get(kind, 0) - 1
            if remaining > 0:
                self._operations[kind] = remaining
            else:
                self._operations.pop(kind, None)

    def active_operations(self) -> Dict[str, int]:
        with self._lock:
            return dict(self._operations)

    def begin(self, target: str) -> bool:
        """Mark a switch as started; False if one is already in progress or
        a model-dependent operation is still running."""
        with self._lock:
            if self._state["state"] == "loading" or self._operations:
                return False
            self._state.update(state="loading", target=target,
                               target_name=Path(target).name, error=None,
                               detail=[], started_at=time.time(),
                               finished_at=None, loaded_model=None,
                               model_identified=None)
            return True

    def succeed(self, loaded_model: str) -> None:
        with self._lock:
            self._state.update(state="loaded", finished_at=time.time(),
                               loaded_model=loaded_model or None,
                               model_identified=bool(loaded_model))

    def fail(self, error: str, detail: Optional[List[str]] = None) -> None:
        with self._lock:
            self._state.update(state="failed", finished_at=time.time(),
                               error=error, detail=list(detail or []))


_TIMESTAMP = re.compile(r"^\[\d{4}-\d\d-\d\d \d\d:\d\d:\d\d\]\s?")
_EXPLANATION_STARTS = ("llama-server does not know", "llama-server rejected")


def _clean_lines(output: str) -> List[str]:
    lines = []
    for raw in (output or "").splitlines():
        line = _TIMESTAMP.sub("", raw).rstrip()
        if line.strip():
            lines.append(line)
    return lines


def summarise_failure(output: str, returncode: int) -> str:
    """A short, accurate account of why the service script failed."""
    lines = _clean_lines(output)
    picked: List[str] = []
    for i, line in enumerate(lines):
        text = line.strip()
        if text.startswith("ERROR:"):
            picked.append(text)
        elif text.startswith(_EXPLANATION_STARTS):
            picked.extend(l.strip() for l in lines[i:i + 5])
            break
    if not picked:
        picked = [l.strip() for l in lines[-3:]] or [
            f"The service script exited with status {returncode} and printed nothing."]
    # De-duplicate while keeping order; keep it readable in a status line.
    seen, unique = set(), []
    for text in picked:
        if text not in seen:
            seen.add(text)
            unique.append(text)
    return " ".join(unique[:8])


def perform_switch(switch: ModelSwitch, target: str, *, command: List[str],
                   cwd: str, reload: Callable[[str], str],
                   timeout: float, run: Optional[Callable[..., Any]] = None) -> None:
    """
    Run the service's switch-model command, then reconnect and verify.

    Success is reported only after the script has seen llama-server answer
    ready AND the app has reconnected AND the server's reported model, when it
    reports one, is the file that was asked for.
    """
    run = run or subprocess.run
    try:
        result = run(command, cwd=cwd, capture_output=True, text=True,
                     timeout=timeout)
    except subprocess.TimeoutExpired:
        switch.fail(f"llama-server did not report ready within {timeout:.0f} "
                    "seconds. See logs/llama-server.log.")
        return
    except OSError as exc:
        switch.fail(f"Could not run the service script: {exc}")
        return

    output = (result.stdout or "") + "\n" + (result.stderr or "")
    if result.returncode != 0:
        switch.fail(summarise_failure(output, result.returncode),
                    detail=_clean_lines(output)[-20:])
        return

    try:
        loaded = reload(target) or ""
    except Exception as exc:                                    # noqa: BLE001
        switch.fail("llama-server reported ready, but the app could not "
                    f"connect to it: {exc}")
        return

    wanted = Path(target).name
    if loaded and loaded != wanted:
        switch.fail(f"llama-server reports {loaded} loaded, not {wanted}.")
        return
    switch.succeed(loaded)


# ---------------------------------------------------------------------------
# Status
# ---------------------------------------------------------------------------

def build_status(*, mode: str, url: Optional[str], probe: Optional[str],
                 served: str, configured_model: str, switch: Dict[str, Any],
                 restart: Dict[str, Any], in_process_loaded: bool = False) -> Dict[str, Any]:
    """
    One status record for the browser. probe is ready / loading / down for
    llama-server, or None for an in-process backend.
    """
    configured_name = (Path(configured_model).name
                       if configured_model.lower().endswith(".gguf")
                       else configured_model)
    if mode == MODE_IN_PROCESS:
        connection = "in-process"
    else:
        connection = {"ready": "connected", "loading": "loading"}.get(probe or "", "unreachable")

    identified = bool(served)
    if switch.get("state") == "loading":
        model_state = "loading"
        message = f"Loading {switch.get('target_name') or 'the selected model'}..."
    elif switch.get("state") == "failed":
        model_state = "failed"
        message = f"Model failed to load: {switch.get('error') or 'reason not reported'}"
    elif mode == MODE_IN_PROCESS:
        model_state = "loaded" if in_process_loaded else "loading"
        identified = in_process_loaded
        served = configured_name if in_process_loaded else ""
        message = served or "Loading the model in this process..."
    elif connection == "connected":
        model_state = "loaded"
        message = served or ("Connected; llama-server did not report which "
                             "model it has loaded.")
    elif connection == "loading":
        model_state = "loading"
        message = "llama-server is loading a model."
    else:
        model_state = "unknown"
        message = f"llama-server is not reachable at {url}."

    matches = None
    if mode == MODE_MANAGED and served and configured_model.lower().endswith(".gguf"):
        matches = served == configured_name

    return {
        "mode": mode,
        "server_url": url if mode != MODE_IN_PROCESS else None,
        "connection": connection,
        "model_state": model_state,
        "loaded_model": served or None,
        "model_identified": identified,
        "configured_model": configured_name,
        "configured_model_id": configured_model,
        "model_matches_configured": matches,
        "restart_available": bool(restart.get("available")),
        "restart_unavailable_reason": restart.get("reason") or "",
        "switch": switch,
        "message": message,
    }


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------

_SHARD = re.compile(r"-(\d{5})-of-\d{5}\.gguf$", re.IGNORECASE)


def discover_gguf_models(spec: Optional[str], limit: int = 200) -> List[Path]:
    """
    GGUF files under the directories in spec (os.pathsep-separated), so a new
    model can be offered in the browser without editing code. Vision
    projectors and every shard but the first of a split model are left out:
    llama-server is given the first shard and finds the rest.
    """
    found: List[Path] = []
    seen = set()
    for entry in (spec or "").split(os.pathsep):
        if not entry.strip():
            continue
        folder = Path(entry.strip()).expanduser()
        if not folder.is_dir():
            continue
        try:
            candidates: Iterable[Path] = sorted(folder.rglob("*.gguf"))
        except OSError:
            continue
        for path in candidates:
            name = path.name.lower()
            if "mmproj" in name:
                continue
            shard = _SHARD.search(name)
            if shard and shard.group(1) != "00001":
                continue
            key = str(path)
            if key in seen or not path.is_file():
                continue
            seen.add(key)
            found.append(path)
            if len(found) >= limit:
                return found
    return found


def discovered_model_choices(spec: Optional[str]) -> List[Dict[str, Any]]:
    """Dropdown entries for discovered models; labels are file names."""
    paths = discover_gguf_models(spec)
    names = [p.name for p in paths]
    choices = []
    for path in paths:
        label = path.name
        if names.count(path.name) > 1:
            label = f"{path.name} ({path.parent.name})"
        choices.append({"id": str(path), "label": label, "model": str(path),
                        "aliases": [], "source": "LLAMA_MODEL_DIRS"})
    return choices
