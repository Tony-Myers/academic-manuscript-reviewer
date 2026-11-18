"""
Persistent local review sessions.

A completed review is saved as one folder per job under the review store
(default: <project>/reviews/sessions, which is git-ignored; override with
QWEN_REVIEW_STORE). Nothing here is sent anywhere: it is plain files on this
computer.

Layout of a session folder:

    manifest.json              identity, state, and the sha256 of every file below
    report.md                  the critical appraisal as shown
    appendix.md                the Human Evidence Appendix (if produced)
    source_verification.json   the verification record (dispositions etc.)
    evidence_cards.json        snapshot of the evidence-card data at completion
    text.txt                   extracted manuscript text used by Manuscript Ask
    sources.json               per-source text for multi-file reviews (if any)
    verification_sources.json  the exact text the verifier saw (cards locate in it)
    trace.json                 development trace (development mode only)
    decisions.json             the reviewer's decisions (mutable, self-validating)
    document-d0.pdf ...        the uploaded documents, byte for byte: d0 is the primary
                               manuscript, d1.. the supplements in upload order. Names
                               are fixed by the store, never taken from an upload.

Integrity rules:
- Job ids are 12 lower-case hex characters; nothing else names a folder, so a
  request cannot reach outside the store.
- A session is written in a staging folder and renamed into place, so a
  reader never sees a half-written session. Later changes (state, decisions)
  replace single files atomically (write, fsync, rename).
- Every load re-hashes each file against the manifest. A mismatch, a missing
  file or an unknown schema makes the session unreadable; it is reported, never
  served.
- Decisions carry a card fingerprint (job id, manuscript text hash and every
  item's label and original wording). Decisions for a different fingerprint
  are refused, so they cannot attach to the wrong manuscript or card set.
- Deleting needs the job id repeated as confirmation.

Standard library only.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

SCHEMA = 1
JOB_ID = re.compile(r"^[0-9a-f]{12}$")
DECISIONS = ("retain", "revise", "dismiss")
MAX_NOTE = 5000
STATES = ("open", "closed")
_LOCK = threading.RLock()

# File name -> job field. Order is the order written.
_TEXT_FILES = {"report.md": "report", "appendix.md": "appendix", "text.txt": "text"}
_JSON_FILES = {
    "source_verification.json": "source_verification",
    "evidence_cards.json": "evidence_cards_snapshot",
    "sources.json": "sources",
    "verification_sources.json": "verification_sources",
    "trace.json": "trace",
}


class StoreError(Exception):
    """A request the store refuses (bad id, wrong fingerprint, bad data)."""


def store_root() -> Path:
    configured = os.environ.get("QWEN_REVIEW_STORE", "").strip()
    if configured:
        return Path(configured).expanduser()
    return Path(__file__).resolve().parent.parent / "reviews" / "sessions"


def configured_store() -> bool:
    return bool(os.environ.get("QWEN_REVIEW_STORE", "").strip())


def store_status() -> Dict[str, Any]:
    """Whether the review store can be used, said plainly. A configured store
    that does not exist (an unmounted drive, a moved folder) is reported as an
    error; the default store is never used in its place."""
    root = store_root()
    status: Dict[str, Any] = {"path": str(root), "configured": configured_store(),
                              "available": root.is_dir(), "error": ""}
    if not status["available"]:
        if status["configured"]:
            status["error"] = (f"The configured review store {root} (QWEN_REVIEW_STORE) does not exist. "
                               "Reviews saved there cannot be listed and new reviews cannot be saved until "
                               "it is available: check that its drive or folder is present, or change "
                               "QWEN_REVIEW_STORE. The default store is not used instead.")
    elif not os.access(root, os.R_OK | os.W_OK | os.X_OK):
        status["available"] = False
        status["error"] = f"The review store {root} is not readable and writable by this application."
    return status


def _ensure_root(root: Path) -> None:
    """Create the store folder when needed. The default store is created with
    its parents; a configured store only when its parent folder exists, so a
    path on a missing drive or in a mistyped folder is reported instead of
    being created somewhere unexpected."""
    if root.is_dir():
        return
    if configured_store():
        if not root.parent.is_dir():
            raise StoreError(f"the configured review store {root} does not exist and neither does its "
                             f"parent folder {root.parent}; the review was not saved. Check that the "
                             "drive or folder is available, or change QWEN_REVIEW_STORE")
        root.mkdir(exist_ok=True)
    else:
        root.mkdir(parents=True, exist_ok=True)


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def valid_job_id(job_id: str) -> bool:
    return isinstance(job_id, str) and bool(JOB_ID.match(job_id))


def _require_id(job_id: str) -> None:
    if not valid_job_id(job_id):
        raise StoreError("invalid review id")


def session_dir(job_id: str) -> Path:
    _require_id(job_id)
    return store_root() / job_id


def _fsync_dir(path: Path) -> None:
    try:
        fd = os.open(str(path), os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(fd)
    except OSError:
        pass
    finally:
        os.close(fd)


def _write_atomic(path: Path, data: bytes) -> None:
    tmp = path.with_name(f".{path.name}.tmp-{uuid.uuid4().hex}")
    with open(tmp, "wb") as fh:
        fh.write(data)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)
    _fsync_dir(path.parent)


def _dump(obj: Any) -> bytes:
    return json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8")


def card_fingerprint(job_id: str, text_sha256: Optional[str], cards: List[dict]) -> str:
    """Identity of the card set the decisions refer to."""
    items = [[c.get("label"), c.get("original")] for c in cards]
    payload = json.dumps({"job_id": job_id, "text_sha256": text_sha256 or "", "items": items},
                         ensure_ascii=False, sort_keys=True)
    return sha256_text(payload)


# ---------------------------------------------------------------------------
# Saving a completed review
# ---------------------------------------------------------------------------

def save_completed(job_id: str, job: Dict[str, Any], *, cards: Optional[dict],
                   manuscript_sha256: Optional[str], input_sha256: Optional[List[str]] = None,
                   origin: str = "review", documents: Optional[List[dict]] = None) -> Dict[str, Any]:
    """Save a completed review once. Returns its manifest.

    Re-saving the same job with the same manuscript is a no-op; a different
    manuscript under an existing id is refused."""
    _require_id(job_id)
    if job.get("status") != "complete" or not job.get("report"):
        raise StoreError("only a completed review with a report can be saved")
    root = store_root()
    final = root / job_id
    text = job.get("text") or None
    text_sha = sha256_text(text) if text else None
    with _LOCK:
        if final.exists():
            existing = read_manifest(job_id)
            if existing.get("manuscript_sha256") != manuscript_sha256 or existing.get("text_sha256") != text_sha:
                raise StoreError("a different manuscript is already saved under this review id")
            return existing
        _ensure_root(root)
        staging = root / f".staging-{job_id}-{uuid.uuid4().hex}"
        staging.mkdir()
        try:
            files: Dict[str, str] = {}

            def put(name: str, data: bytes) -> None:
                (staging / name).write_bytes(data)
                with open(staging / name, "rb+") as fh:
                    os.fsync(fh.fileno())
                files[name] = sha256_bytes(data)

            for name, field in _TEXT_FILES.items():
                value = job.get(field)
                if isinstance(value, list):
                    value = "\n".join(map(str, value))
                if value:
                    put(name, str(value).encode("utf-8"))
            snapshot = cards if cards is not None else job.get("evidence_cards_snapshot")
            for name, field in _JSON_FILES.items():
                value = snapshot if field == "evidence_cards_snapshot" else job.get(field)
                if value:
                    put(name, _dump(value))
            card_list = (snapshot or {}).get("cards") or []
            doc_records = []
            for doc in documents or []:
                record = {k: doc.get(k) for k in _DOC_KEYS}
                record["file"] = None
                src = doc.get("path")
                if src and Path(src).is_file():
                    name = _doc_file_name(record["id"], record["suffix"])
                    shutil.copyfile(src, staging / name)
                    with open(staging / name, "rb+") as fh:
                        os.fsync(fh.fileno())
                    digest = sha256_file(staging / name)
                    if digest != record["sha256"]:
                        raise StoreError(f"stored copy of {record['id']} does not match its recorded hash")
                    files[name] = digest
                    record["file"] = name
                doc_records.append(record)
            manifest = {
                "schema": SCHEMA,
                "job_id": job_id,
                "origin": origin,
                "filename": job.get("filename") or "manuscript",
                "supplements": [s.get("name") for s in job.get("supplements") or [] if isinstance(s, dict)],
                "completed_at": job.get("completed_at") or now(),
                "saved_at": now(),
                "last_opened_at": now(),
                "state": "open",
                "manuscript_sha256": manuscript_sha256,
                "input_sha256": list(input_sha256 or []),
                "text_sha256": text_sha,
                "ask_available": bool(text),
                "development_mode": bool(job.get("development_mode") and job.get("trace")),
                "has_appendix": "appendix.md" in files,
                "has_evidence_cards": bool(card_list),
                "card_fingerprint": card_fingerprint(job_id, text_sha, card_list) if card_list else None,
                "files": files,
            }
            if documents is not None:
                manifest["documents"] = doc_records
            if isinstance(job.get("execution"), dict):
                manifest["execution"] = job["execution"]
            if isinstance(job.get("vision_record"), dict):
                manifest["vision"] = job["vision_record"]
            (staging / "manifest.json").write_bytes(_dump(manifest))
            with open(staging / "manifest.json", "rb+") as fh:
                os.fsync(fh.fileno())
            _fsync_dir(staging)
            os.rename(staging, final)
            _fsync_dir(root)
        except BaseException:
            shutil.rmtree(staging, ignore_errors=True)
            raise
    return manifest


# ---------------------------------------------------------------------------
# Reading
# ---------------------------------------------------------------------------

def read_manifest(job_id: str) -> Dict[str, Any]:
    path = session_dir(job_id) / "manifest.json"
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise
    except (OSError, ValueError) as exc:
        raise StoreError(f"manifest unreadable: {exc}") from exc
    if not isinstance(manifest, dict) or manifest.get("schema") != SCHEMA or manifest.get("job_id") != job_id:
        raise StoreError("manifest does not match this review")
    if manifest.get("state") not in STATES or not isinstance(manifest.get("files"), dict):
        raise StoreError("manifest incomplete")
    return manifest


def verify(job_id: str) -> Dict[str, Any]:
    """Manifest, after checking every listed file against its hash."""
    manifest = read_manifest(job_id)
    folder = session_dir(job_id)
    for name, digest in manifest["files"].items():
        if "/" in name or name.startswith("."):
            raise StoreError("manifest names an invalid file")
        path = folder / name
        if not path.is_file() or sha256_file(path) != digest:
            raise StoreError(f"{name} is missing or does not match its recorded hash")
    return manifest


def exists(job_id: str) -> bool:
    return valid_job_id(job_id) and (store_root() / job_id / "manifest.json").is_file()


def load_job(job_id: str) -> Dict[str, Any]:
    """A review_jobs entry rebuilt from a verified session."""
    manifest = verify(job_id)
    folder = session_dir(job_id)
    job: Dict[str, Any] = {
        "status": "complete",
        "progress": [f"Restored from the local review store (completed {manifest['completed_at']})."],
        "error": None,
        "filename": manifest["filename"],
        "supplements": [{"name": n} for n in manifest.get("supplements") or []],
        "development_mode": manifest.get("development_mode", False),
        "cancel_requested": False,
        "restored": True,
        "manuscript_sha256": manifest.get("manuscript_sha256"),
        "completed_at": manifest["completed_at"],
    }
    if isinstance(manifest.get("execution"), dict):
        job["execution"] = manifest["execution"]
    for name, field in _TEXT_FILES.items():
        if name in manifest["files"]:
            job[field] = (folder / name).read_text(encoding="utf-8")
    for name, field in _JSON_FILES.items():
        if name in manifest["files"]:
            job[field] = json.loads((folder / name).read_text(encoding="utf-8"))
    if job.get("text") and sha256_text(job["text"]) != manifest.get("text_sha256"):
        raise StoreError("manuscript text does not match the manifest")
    if not manifest.get("ask_available"):
        job["ask_unavailable_reason"] = ("The manuscript text was not saved with this review, so "
                                         "Manuscript Ask is not available for it.")
    return job


def summary(manifest: Dict[str, Any]) -> Dict[str, Any]:
    keys = ("job_id", "filename", "supplements", "completed_at", "last_opened_at", "state", "origin",
            "has_appendix", "has_evidence_cards", "ask_available", "development_mode")
    return {k: manifest.get(k) for k in keys}


def list_sessions() -> List[Dict[str, Any]]:
    root = store_root()
    if not root.is_dir():
        return []
    out = []
    for child in root.iterdir():
        if not child.is_dir() or not valid_job_id(child.name):
            continue
        try:
            out.append(summary(read_manifest(child.name)))
        except (StoreError, OSError) as exc:
            out.append({"job_id": child.name, "state": "unreadable", "error": str(exc)})
    out.sort(key=lambda s: s.get("last_opened_at") or "", reverse=True)
    return out


# ---------------------------------------------------------------------------
# State, decisions, deletion
# ---------------------------------------------------------------------------

def set_state(job_id: str, state: str) -> Dict[str, Any]:
    if state not in STATES:
        raise StoreError("unknown state")
    with _LOCK:
        manifest = verify(job_id)
        manifest["state"] = state
        if state == "open":
            manifest["last_opened_at"] = now()
        _write_atomic(session_dir(job_id) / "manifest.json", _dump(manifest))
    return manifest


def _clean_decisions(decisions: Any, labels: set) -> Dict[str, dict]:
    if not isinstance(decisions, dict):
        raise StoreError("decisions must be an object")
    clean = {}
    for label, entry in decisions.items():
        if label not in labels:
            raise StoreError(f"unknown item {label!r} for this review")
        if not isinstance(entry, dict) or entry.get("decision") not in DECISIONS:
            raise StoreError(f"invalid decision for {label}")
        note = entry.get("note", "")
        if not isinstance(note, str) or len(note) > MAX_NOTE:
            raise StoreError(f"invalid note for {label}")
        stamp = entry.get("confirmed_at", "")
        if not isinstance(stamp, str) or len(stamp) > 64:
            raise StoreError(f"invalid time for {label}")
        clean[label] = {"decision": entry["decision"], "note": note, "confirmed_at": stamp}
    return clean


def _labels(job_id: str) -> set:
    path = session_dir(job_id) / "evidence_cards.json"
    cards = json.loads(path.read_text(encoding="utf-8")).get("cards") or []
    return {c.get("label") for c in cards}


def read_decisions(job_id: str) -> Dict[str, Any]:
    manifest = verify(job_id)
    fingerprint = manifest.get("card_fingerprint")
    path = session_dir(job_id) / "decisions.json"
    base = {"card_fingerprint": fingerprint, "decisions": {}, "updated_at": None, "saved": False}
    if not path.is_file():
        return base
    try:
        stored = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise StoreError(f"decisions unreadable: {exc}") from exc
    if stored.get("job_id") != job_id or stored.get("card_fingerprint") != fingerprint:
        raise StoreError("stored decisions do not belong to this review")
    decisions = _clean_decisions(stored.get("decisions"), _labels(job_id))
    return {"card_fingerprint": fingerprint, "decisions": decisions,
            "updated_at": stored.get("updated_at"), "saved": True}


def write_decisions(job_id: str, card_fingerprint_value: str, decisions: Any) -> Dict[str, Any]:
    with _LOCK:
        manifest = verify(job_id)
        expected = manifest.get("card_fingerprint")
        if not expected:
            raise StoreError("this review has no evidence cards")
        if card_fingerprint_value != expected:
            raise StoreError("these decisions belong to a different manuscript or card set")
        clean = _clean_decisions(decisions, _labels(job_id))
        record = {"schema": SCHEMA, "job_id": job_id, "card_fingerprint": expected,
                  "decisions": clean, "updated_at": now()}
        _write_atomic(session_dir(job_id) / "decisions.json", _dump(record))
    return {"card_fingerprint": expected, "decisions": clean, "updated_at": record["updated_at"], "saved": True}


def delete(job_id: str, confirm_job_id: str) -> None:
    _require_id(job_id)
    if confirm_job_id != job_id:
        raise StoreError("deletion needs the review id repeated as confirmation")
    root = store_root()
    folder = root / job_id
    with _LOCK:
        if not folder.is_dir():
            raise FileNotFoundError(job_id)
        doomed = root / f".deleting-{job_id}-{uuid.uuid4().hex}"
        os.rename(folder, doomed)
        _fsync_dir(root)
        shutil.rmtree(doomed, ignore_errors=True)


# ---------------------------------------------------------------------------
# Uploaded documents (original bytes)
# ---------------------------------------------------------------------------
# A running review's uploads are copied to <store>/.pending-<job_id>/ when it
# starts, because the worker deletes its temporary folder before the review is
# saved. save_completed() copies them into the session; the pending folder is
# always discarded afterwards. Document ids are d0 (primary manuscript), d1..
# (supplements, in upload order); a page number always belongs to one id.

DOCUMENT_MEDIA_TYPES = {
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".txt": "text/plain; charset=utf-8",
    ".md": "text/markdown; charset=utf-8",
    ".csv": "text/csv; charset=utf-8",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".xlsm": "application/vnd.ms-excel.sheet.macroEnabled.12",
}
_DOC_KEYS = ("id", "role", "original_filename", "source_label", "suffix", "media_type", "sha256", "bytes")
_DOC_ID = re.compile(r"^d\d{1,2}$")


def valid_document_id(doc_id: str) -> bool:
    return isinstance(doc_id, str) and bool(_DOC_ID.match(doc_id))


def _suffix(name: Optional[str]) -> str:
    suffix = Path(str(name or "")).suffix.lower()
    return suffix if suffix in DOCUMENT_MEDIA_TYPES else ""


def _doc_file_name(doc_id: str, suffix: str) -> str:
    if not valid_document_id(doc_id) or suffix not in DOCUMENT_MEDIA_TYPES:
        raise StoreError("invalid document id or type")
    return f"document-{doc_id}{suffix}"


def _pending_dir(job_id: str) -> Path:
    _require_id(job_id)
    return store_root() / f".pending-{job_id}"


def stage_pending_documents(job_id: str, uploads: List[dict]) -> List[dict]:
    """Copy a starting review's uploads aside. uploads: [{path, name}], primary first."""
    folder = _pending_dir(job_id)
    shutil.rmtree(folder, ignore_errors=True)
    folder.mkdir(parents=True)
    out = []
    for index, item in enumerate(uploads):
        suffix = _suffix(item.get("name")) or _suffix(item.get("path"))
        doc_id = f"d{index}"
        record = {"id": doc_id, "role": "primary" if index == 0 else "supplement",
                  "original_filename": Path(str(item.get("name") or "")).name or None,
                  "source_label": None, "suffix": suffix,
                  "media_type": DOCUMENT_MEDIA_TYPES.get(suffix), "sha256": None, "bytes": None, "path": None}
        if suffix:
            dest = folder / _doc_file_name(doc_id, suffix)
            shutil.copyfile(item["path"], dest)
            record.update(sha256=sha256_file(dest), bytes=dest.stat().st_size, path=str(dest))
        out.append(record)
    (folder / "pending.json").write_bytes(_dump(out))
    return out


def pending_documents(job_id: str) -> Optional[List[dict]]:
    path = _pending_dir(job_id) / "pending.json"
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def discard_pending(job_id: str) -> None:
    if valid_job_id(job_id):
        shutil.rmtree(_pending_dir(job_id), ignore_errors=True)


def _legacy_documents(manifest: Dict[str, Any]) -> List[dict]:
    """Descriptors for a review saved before documents were kept: identity from
    the recorded hashes and names, nothing stored."""
    digests = list(manifest.get("input_sha256") or [])
    if not digests and manifest.get("manuscript_sha256"):
        digests = [manifest["manuscript_sha256"]]
    names = [manifest.get("filename")] + list(manifest.get("supplements") or [])
    out = []
    for index, digest in enumerate(digests):
        name = names[index] if index < len(names) else None
        suffix = _suffix(name)
        out.append({"id": f"d{index}", "role": "primary" if index == 0 else "supplement",
                    "original_filename": name, "source_label": None, "suffix": suffix,
                    "media_type": DOCUMENT_MEDIA_TYPES.get(suffix), "sha256": digest, "bytes": None,
                    "file": None})
    return out


def documents(job_id: str) -> List[dict]:
    """The review's documents, as recorded. 'available' means the original bytes
    are stored with the review and still match their hash."""
    manifest = verify(job_id)
    records = manifest.get("documents")
    records = list(records) if isinstance(records, list) else _legacy_documents(manifest)
    return [dict(r, available=bool(r.get("file")) and r.get("file") in manifest["files"]) for r in records]


def document_file(job_id: str, doc_id: str) -> tuple:
    """(path, record) for a stored document of this review, after re-checking its
    hash. Only ids recorded in this review's manifest can be resolved."""
    if not valid_document_id(doc_id):
        raise StoreError("invalid document id")
    manifest = read_manifest(job_id)
    records = manifest.get("documents") if isinstance(manifest.get("documents"), list) else []
    record = next((r for r in records if r.get("id") == doc_id), None)
    if not record or not record.get("file") or record["file"] not in manifest["files"]:
        raise FileNotFoundError(doc_id)
    if record["file"] != _doc_file_name(doc_id, record.get("suffix") or ""):
        raise StoreError("manifest names an invalid document file")
    path = session_dir(job_id) / record["file"]
    if not path.is_file() or sha256_file(path) != manifest["files"][record["file"]]:
        raise StoreError("the stored document does not match its recorded hash")
    return path, record


def reattach_document(job_id: str, upload_path: Path, upload_name: Optional[str] = None) -> dict:
    """Store an original document for a review that lacks it. Accepted only when
    its sha256 equals a hash recorded for this review; it then takes that
    document's id and role, so a supplement can never become the primary."""
    digest = sha256_file(Path(upload_path))
    with _LOCK:
        manifest = verify(job_id)
        records = manifest.get("documents")
        records = list(records) if isinstance(records, list) else _legacy_documents(manifest)
        match = next((r for r in records if r.get("sha256") and r["sha256"] == digest), None)
        if match is None:
            raise StoreError("this file does not match the manuscript or any supplement recorded for this "
                             "review (SHA-256 differs); it was not attached")
        if match.get("file") and match["file"] in manifest["files"]:
            return dict(match, available=True, already_stored=True)
        suffix = match.get("suffix") or _suffix(upload_name)
        if not suffix:
            raise StoreError("unsupported document type")
        name = _doc_file_name(match["id"], suffix)
        _write_atomic(session_dir(job_id) / name, Path(upload_path).read_bytes())
        if sha256_file(session_dir(job_id) / name) != digest:
            (session_dir(job_id) / name).unlink(missing_ok=True)
            raise StoreError("the stored copy did not match; nothing was attached")
        match.update(file=name, suffix=suffix, media_type=DOCUMENT_MEDIA_TYPES[suffix],
                     bytes=(session_dir(job_id) / name).stat().st_size,
                     original_filename=match.get("original_filename") or Path(str(upload_name or "")).name or None)
        manifest["documents"] = records
        manifest["files"][name] = digest
        _write_atomic(session_dir(job_id) / "manifest.json", _dump(manifest))
        return dict(match, available=True, already_stored=False)
