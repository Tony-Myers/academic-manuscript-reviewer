"""Expected versus served checkpoint identity checks for review requests.

Uses read-only server metadata; never loads, switches or selects a model.
"""

from __future__ import annotations

import json
import copy
import os
import re
import threading
import time
import urllib.request
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

SCHEMA_VERSION = 1

MATCH = "match"
MISMATCH = "mismatch"
UNVERIFIED = "unverified"

STRENGTH_PATH = "checkpoint path"
STRENGTH_FILE = "checkpoint file name"

CODE_MISMATCH = "MODEL_IDENTITY_MISMATCH"
CODE_UNVERIFIED = "MODEL_IDENTITY_UNVERIFIED"
CODE_CHANGED = "MODEL_IDENTITY_CHANGED"

_HF_SNAPSHOT = re.compile(
    r"models--(?P<org>[^/\\]+?)--(?P<name>[^/\\]+)[/\\]snapshots[/\\](?P<rev>[0-9a-fA-F]{7,64})(?:[/\\]|$)")
_QUANT = re.compile(
    r"(?i)(?<![A-Za-z0-9])(?:UD-)?(?:I?Q\d(?:_[A-Z0-9]+)*|F16|BF16|F32|\d+(?:\.\d+)?bpw)(?![A-Za-z0-9])")
_SHARD = re.compile(r"-(\d{5})-of-(\d{5})\.gguf$", re.I)


class ModelIdentityError(RuntimeError):
    """Raised when a review must not proceed because the model identity is wrong
    or cannot be confirmed. Deliberately not a BackendError: transport-failure
    handlers that tolerate a BackendError (for example the optional vision
    path) must not mistake a substitution for a recoverable failure."""

    def __init__(self, message: str, code: str, record: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.code = code
        self.record = record or {}


# ---------------------------------------------------------------------------
# Describing an identity
# ---------------------------------------------------------------------------

def describe(value: Any, source: str) -> Optional[Dict[str, Any]]:
    """Structured identity for a model path or file name; None when empty.

    ``path`` is set only when the value is a path (it contains a separator);
    a bare file name is never promoted to a path."""
    if not isinstance(value, str) or not value.strip():
        return None
    raw = value.strip()
    is_path = "/" in raw or "\\" in raw
    file_name = re.split(r"[/\\]", raw)[-1]
    hf = _HF_SNAPSHOT.search(raw) if is_path else None
    shard = _SHARD.search(file_name)
    stem = re.sub(r"(?i)\.gguf$", "", _SHARD.sub(".gguf", file_name))
    quants: List[str] = []
    for found in _QUANT.findall(stem):
        if found not in quants:
            quants.append(found)
    return {
        "raw": raw,
        "path": os.path.normpath(raw) if is_path else None,
        "file": file_name,
        "repository": f"{hf.group('org')}/{hf.group('name')}" if hf else None,
        "revision": hf.group("rev").lower() if hf else None,
        "quantisation": " ".join(quants) or None,
        "shard": f"{shard.group(1)} of {shard.group(2)}" if shard else None,
        "source": source,
    }


def display(identity: Optional[Dict[str, Any]]) -> str:
    """Short human-readable label: file name plus repository and revision."""
    if not identity:
        return "not reported"
    parts = [identity.get("file") or identity.get("raw") or "?"]
    extra = []
    if identity.get("repository"):
        extra.append(identity["repository"])
    if identity.get("revision"):
        extra.append("revision " + identity["revision"][:12])
    if extra:
        parts.append("(" + ", ".join(extra) + ")")
    return " ".join(parts)


def compare(expected: Optional[Dict[str, Any]], observed: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Verdict on whether ``observed`` is the expected checkpoint.

    Full paths are compared when both sides have one. Otherwise matching file
    names remain unverified, and a disagreeing repository or revision, when both are
    known, is still a mismatch. Missing information is ``unverified``, never a
    match."""
    if not expected:
        return {"state": UNVERIFIED, "strength": None,
                "reason": "No expected model was established for this review."}
    if not observed:
        return {"state": UNVERIFIED, "strength": None,
                "reason": "The server did not report which model it has loaded."}
    if expected.get("path") and observed.get("path"):
        if expected["path"] == observed["path"]:
            return {"state": MATCH, "strength": STRENGTH_PATH, "reason": "Checkpoint paths are identical."}
        return {"state": MISMATCH, "strength": STRENGTH_PATH, "reason": "Checkpoint paths differ."}
    for key in ("repository", "revision"):
        if expected.get(key) and observed.get(key) and expected[key] != observed[key]:
            return {"state": MISMATCH, "strength": key, "reason": f"Model {key} differs."}
    if expected.get("file") and expected.get("file") == observed.get("file"):
        return {"state": UNVERIFIED, "strength": STRENGTH_FILE,
                "reason": "Matching file names alone cannot establish checkpoint path or revision."}
    return {"state": MISMATCH, "strength": STRENGTH_FILE, "reason": "Checkpoint file names differ."}


# ---------------------------------------------------------------------------
# Asking the server (no inference)
# ---------------------------------------------------------------------------

def _get_json(url: str, timeout: float, opener: Callable) -> Optional[Any]:
    try:
        with opener(url, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8", "replace"))
    except Exception:                                           # noqa: BLE001
        return None


def server_identity(base_url: str, timeout: float = 3.0,
                    opener: Callable = urllib.request.urlopen) -> Dict[str, Any]:
    """What a llama-server reports about its loaded model.

    Reads /props (``model_path``, ``build_info``) and /v1/models (ids). Returns
    ``state`` "reported", "not_reported" or "ambiguous" (more than one model
    listed, as in a router configuration, so the serving model of a request
    cannot be established from these endpoints alone)."""
    base = base_url.rstrip("/")
    props = _get_json(f"{base}/props", timeout, opener)
    models = _get_json(f"{base}/v1/models", timeout, opener)
    ids: List[str] = []
    if isinstance(models, dict):
        for key in ("data", "models"):
            entries = models.get(key)
            if isinstance(entries, list):
                for entry in entries:
                    value = entry.get("id") or entry.get("model") or entry.get("name") if isinstance(entry, dict) else None
                    if isinstance(value, str) and value.strip() and value.strip() not in ids:
                        ids.append(value.strip())
    model_path = props.get("model_path") if isinstance(props, dict) else None
    build = props.get("build_info") if isinstance(props, dict) else None
    result: Dict[str, Any] = {"server": base, "build": build if isinstance(build, str) else None,
                              "listed_models": ids, "checked_at": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
    distinct_paths = {os.path.normpath(i) for i in ids if "/" in i or "\\" in i}
    distinct_files = {re.split(r"[/\\]", i)[-1] for i in ids}
    if len(distinct_files) > 1 or len(distinct_paths) > 1:
        result.update(state="ambiguous", identity=None,
                      reason="The server lists more than one model, so the serving model cannot be established.")
        return result
    if isinstance(model_path, str) and model_path.strip():
        described = describe(model_path, "llama-server /props model_path")
        if any((describe(i, "listed") or {}).get("file") != described.get("file")
               or ((describe(i, "listed") or {}).get("path") and
                   (describe(i, "listed") or {}).get("path") != described.get("path")) for i in ids):
            result.update(state="ambiguous", identity=None,
                          reason="Server model path and listed checkpoint identities disagree.")
            return result
        result.update(state="reported", identity=describe(model_path, "llama-server /props model_path"))
        return result
    if ids:
        result.update(state="reported", identity=describe(ids[0], "llama-server /v1/models id"))
        return result
    result.update(state="not_reported", identity=None,
                  reason="The server did not report a model path or model id.")
    return result


# ---------------------------------------------------------------------------
# The per-review guard
# ---------------------------------------------------------------------------

class IdentityGuard:
    """Checks one review's model identity before and during inference.

    ``probe`` returns a server_identity() result; tests pass a fake. Once
    tripped, every later inference request is refused before it is sent, so a
    caller that swallows the first ModelIdentityError still cannot continue."""

    def __init__(self, expected: Optional[Dict[str, Any]], expected_source: str,
                 base_url: str, probe: Optional[Callable[[], Dict[str, Any]]] = None) -> None:
        self.expected = copy.deepcopy(expected)
        self.expected_source = expected_source
        self.base_url = base_url
        self._probe = probe or (lambda: server_identity(base_url))
        self._lock = threading.Lock()
        self.initial: Optional[Dict[str, Any]] = None
        self.initial_verdict: Optional[Dict[str, Any]] = None
        self.responses: List[Dict[str, Any]] = []
        self.tripped: Optional[Dict[str, Any]] = None

    # -- helpers -----------------------------------------------------------

    def _trip(self, code: str, message: str, **detail: Any) -> ModelIdentityError:
        with self._lock:
            if self.tripped is None:
                self.tripped = {"code": code, "message": message,
                                "at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), **detail}
            record = dict(self.tripped)
        return ModelIdentityError(message, code, record)

    def _message(self, verdict: Dict[str, Any], observed: Optional[Dict[str, Any]], when: str) -> str:
        expected = display(self.expected)
        loaded = display(observed)
        if verdict["state"] == MISMATCH:
            return (f"Review stopped {when}: the loaded model is {loaded}, but this review expected "
                    f"{expected} ({self.expected_source}). No output from a different model is used. "
                    "Load the expected model, or start the review again and explicitly confirm the "
                    "loaded model.")
        return (f"Review stopped {when}: the model identity could not be confirmed "
                f"({verdict['reason']}) Expected: {expected} ({self.expected_source}).")

    # -- checks ------------------------------------------------------------

    def verify_before_inference(self) -> Dict[str, Any]:
        if self.tripped is not None:
            raise ModelIdentityError(self.tripped["message"], self.tripped["code"], dict(self.tripped))
        observed = self._probe()
        verdict = compare(self.expected, observed.get("identity"))
        if observed.get("state") == "ambiguous":
            verdict = {"state": UNVERIFIED, "strength": None, "reason": observed.get("reason")}
        self.initial, self.initial_verdict = observed, verdict
        if verdict["state"] != MATCH:
            code = CODE_MISMATCH if verdict["state"] == MISMATCH else CODE_UNVERIFIED
            raise self._trip(code, self._message(verdict, observed.get("identity"), "before inference"),
                             expected=self.expected, observed=observed, verdict=verdict)
        return verdict

    def before_request(self) -> None:
        if self.tripped is not None:
            raise ModelIdentityError(
                "Inference refused: this review's model identity check has already failed. "
                + self.tripped["message"], self.tripped["code"], dict(self.tripped))
        if self.initial_verdict is None:
            raise self._trip(CODE_UNVERIFIED,
                             "Inference refused: the model identity was not checked before the first request.")
        observed = self._probe()
        verdict = compare(self.expected, observed.get("identity"))
        if observed.get("state") == "ambiguous":
            verdict = {"state": UNVERIFIED, "strength": None, "reason": observed.get("reason")}
        if verdict["state"] != MATCH:
            code = CODE_CHANGED if verdict["state"] == MISMATCH else CODE_UNVERIFIED
            raise self._trip(code, self._message(verdict, observed.get("identity"), "before request"),
                             expected=self.expected, observed=observed, verdict=verdict)

    def after_response(self, response: Any, request_model: Optional[str]) -> Dict[str, Any]:
        """Check one inference response. The response's own ``model`` field is
        recorded; it counts as evidence only when it is not merely an echo of
        the request's model field. The server is then asked again (/props), and
        that report decides."""
        reported = response.get("model") if isinstance(response, dict) else None
        fingerprint = response.get("system_fingerprint") if isinstance(response, dict) else None
        reported_identity = describe(reported, "inference response model field")
        echo = bool(reported and request_model and reported.strip() == str(request_model).strip())
        field_verdict = (compare(self.expected, reported_identity)
                         if reported_identity and not echo else None)
        observed = self._probe()
        server_verdict = compare(self.expected, observed.get("identity"))
        if observed.get("state") == "ambiguous":
            server_verdict = {"state": UNVERIFIED, "strength": None, "reason": observed.get("reason")}
        entry = {"sequence": len(self.responses), "response_model": reported,
                 "response_model_is_request_echo": echo, "system_fingerprint": fingerprint,
                 "response_field_verdict": field_verdict, "server_reported": display(observed.get("identity")),
                 "server_verdict": server_verdict}
        with self._lock:
            self.responses.append(entry)
        failing = [v for v in (field_verdict, server_verdict) if v and v["state"] != MATCH
                   and not (v is field_verdict and v["state"] == UNVERIFIED
                            and reported_identity.get("file") == (self.expected or {}).get("file"))]
        if failing:
            verdict = next((v for v in failing if v["state"] == MISMATCH), failing[0])
            code = CODE_CHANGED if verdict["state"] == MISMATCH else CODE_UNVERIFIED
            observed_identity = (reported_identity if field_verdict is verdict else observed.get("identity"))
            raise self._trip(code, self._message(verdict, observed_identity,
                                                 f"after inference response {entry['sequence'] + 1}"),
                             expected=self.expected, response=entry)
        return entry

    def summary(self) -> Dict[str, Any]:
        verdicts = [r["server_verdict"]["state"] for r in self.responses]
        return {
            "schema_version": SCHEMA_VERSION,
            "expected": self.expected,
            "expected_source": self.expected_source,
            "checked_before_inference": self.initial,
            "verdict_before_inference": self.initial_verdict,
            "inference_responses_checked": len(self.responses),
            "responses_matching": verdicts.count(MATCH),
            "responses": self.responses,
            "stopped": self.tripped,
            "state": ("stopped" if self.tripped else
                      "verified" if self.initial_verdict and self.initial_verdict["state"] == MATCH else
                      "not checked"),
        }


# ---------------------------------------------------------------------------
# Establishing the expected model at review creation
# ---------------------------------------------------------------------------

def expected_for_review(explicit: str, remembered: str, configured: str,
                        external: bool, reported: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Which model this review should use, and why.

    1. An explicit selection made for this review (for example confirming the
       loaded model after a mismatch, or choosing 27B).
    2. Managed server: the model last loaded from the browser (the user's last
       explicit choice), which survives a restart that reloads a different
       start-up default.
    3. Managed server without a remembered choice: the configured start-up model.
    4. External server without an explicit selection: the application cannot
       choose the model, so the model the server reports at creation becomes
       the expectation, and later changes are still detected.
    """
    if explicit:
        return {"identity": describe(explicit, "explicit selection for this review"),
                "source": "explicit selection for this review"}
    if external:
        identity = (reported or {}).get("identity")
        return {"identity": identity,
                "source": "external llama-server, as reported when the review was created"}
    if remembered:
        return {"identity": describe(remembered, "model last selected in the browser"),
                "source": "model last selected in the browser"}
    return {"identity": describe(configured, "configured start-up model"),
            "source": "configured start-up model"}


def creation_check(expected: Dict[str, Any], observed: Dict[str, Any]) -> Dict[str, Any]:
    """Pre-creation verdict plus a user-facing payload for a refusal."""
    verdict = compare(expected.get("identity"), observed.get("identity"))
    if observed.get("state") == "ambiguous":
        verdict = {"state": UNVERIFIED, "strength": None, "reason": observed.get("reason")}
    payload = {
        "code": None if verdict["state"] == MATCH else (CODE_MISMATCH if verdict["state"] == MISMATCH else CODE_UNVERIFIED),
        "verdict": verdict,
        "expected": expected.get("identity"),
        "expected_source": expected.get("source"),
        "loaded": observed.get("identity"),
        "loaded_label": display(observed.get("identity")),
        "expected_label": display(expected.get("identity")),
    }
    if verdict["state"] == MISMATCH:
        payload["message"] = (
            f"The loaded model is {payload['loaded_label']}, but this review would expect "
            f"{payload['expected_label']} ({expected.get('source')}). The review was not started. "
            "Load the expected model, or confirm that this review should use the loaded model.")
        loaded = observed.get("identity") or {}
        payload["confirm_model"] = loaded.get("path") or loaded.get("raw")
    elif verdict["state"] == UNVERIFIED:
        payload["message"] = ("The review was not started because the model identity could not be "
                              f"confirmed: {verdict['reason']}")
    return payload
