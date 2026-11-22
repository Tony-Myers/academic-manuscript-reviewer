"""
Evidence cards: one per AI-generated review item, built for a human reviewer.

Purpose: let the reviewer see, for each strength, concern or verification
prompt, what the manuscript actually says, what that does and does not
establish, and what still needs their judgement, then record their own
decision. Evidence, interpretation and uncertainty are kept apart.

Built only from records the pipeline already keeps: the original item text
and the source-verification disposition (model verdict, reason, quotation,
correction, surviving point, application action), plus the manuscript text
the verifier saw. No model is called and no field is invented. A field that
cannot be filled reliably from those records is marked unavailable.

Integrity rules:
- The original item is shown verbatim and never replaced by a correction.
- A passage is shown as manuscript evidence only when the application finds
  it in the manuscript text as one contiguous passage; the text displayed is
  the manuscript's own slice, not the model's transcription. A quotation that
  cannot be located is shown separately, labelled unverified.
- Locations are only those the extracted text marks itself: [Page N] markers
  and explicit table containers (human_evidence_appendix). Sections are not
  marked reliably in the extracted text, so none is given.
- Four descriptive states are shown instead of one label: whether a passage
  was located, whether the item's factual premise is consistent with it
  according to the verifier, whether the methodological conclusion is
  justified (always left to human judgement), and evidence completeness
  (never established by the application). None is a probability, and none
  says the item is correct.
- Passages are grouped by the role the verifier gave them (supports,
  qualifies or contradicts the item). Roles are the verifier's reading; in
  records without roles (version 1) the main quotation's role is inferred
  from the verdict and labelled as inferred.
- Retrieval failure is never read as absence from the manuscript.
- A quotation is authenticated only by matching the manuscript itself. Text
  that matches the review item's own wording but not the manuscript is shown
  as unverified and marked as matching the item. When the verifier's primary
  quotation fails, a notice says so and any other located passages are shown
  first, without implying that they bear out the verdict.
- No sentence of a passage is singled out: passages are shown in full, split
  into sentences for reading only.
"""
from __future__ import annotations

import html
import json
import re
import unicodedata
from typing import Dict, List, Optional, Sequence, Tuple

import human_evidence_appendix as hea
import review_pipeline as rp
import source_verification as sv
import reviewer_presentation as presentation

SCHEMA_VERSION = 3  # 3: no sentence highlight; quotation_notice, duplicate_references_from, matches_item_text

# Descriptive states. None says the review item is correct: locating a passage
# shows only that the manuscript contains it.
EVIDENCE = {
    "located": "Relevant manuscript passage located",
    "item_quote_only": "Passage quoted by the review item located",
    "unverified_only": "Quotation not authenticated",
    "none": "No passage located",
}
PREMISE = {
    "consistent": "Consistent with the located passage, according to the verifier",
    "inconsistent": "Inconsistent with the located passage, according to the verifier",
    "questioned": "Questioned by the verifier",
    "not_assessed": "Not assessed against authenticated evidence",
}
CONCLUSION = {
    "requires_judgement": "Requires human judgement",
    "questioned": "Questioned by the verifier; requires human judgement",
}
COMPLETENESS = {"not_established": "Not established"}
ROLE_FROM_VERDICT = {"supported": "supports", "correct": "qualifies", "reject": "contradicts"}
ROLE_NAMES = {"supports": "supports the item", "qualifies": "qualifies the item",
              "contradicts": "contradicts the item"}


# ---------------------------------------------------------------------------
# Exact location of a passage
# ---------------------------------------------------------------------------

_FOLD = {"‘": "'", "’": "'", "“": '"', "”": '"',
         "–": "-", "—": "-", "−": "-"}


def _fold_with_map(text: str, keep_punct: bool) -> Tuple[str, List[int]]:
    """Fold case, quote styles, dashes and whitespace (and optionally
    punctuation), keeping for every folded character the index of the raw
    character it came from, so a match maps back to an exact raw span."""
    out: List[str] = []
    index: List[int] = []
    last_space = True
    for i, ch in enumerate(text):
        for c in unicodedata.normalize("NFKC", _FOLD.get(ch, ch)).lower():
            if not keep_punct and not c.isalnum():
                c = " "
            if c.isspace():
                if last_space:
                    continue
                c, last_space = " ", True
            else:
                last_space = False
            out.append(c)
            index.append(i)
    while out and out[-1] == " ":
        out.pop(); index.pop()
    return "".join(out), index


def locate_span(quote: str, source_text: str) -> Optional[Tuple[int, int]]:
    import quote_match as qm
    result = qm.classify(quote, qm.Manuscript({"source": source_text}))
    if result.state == qm.EXACT and result.locations:
        loc = result.locations[0]
        return loc.start, loc.end
    return None


def _passage(quote: str, sources: Dict[str, str]) -> dict:
    """Only exact token-preserving matches are authenticated; related is not exact."""
    import quote_match as qm
    result = qm.classify(quote, qm.Manuscript(sources))
    if result.state == qm.EXACT and result.locations:
        loc = result.locations[0]
        return dict(status="located", authentication=result.state, source=loc.source,
                    text=loc.text, location=loc.location, in_table=loc.in_table,
                    start=loc.start, end=loc.end, note=result.reason)
    return dict(status="unverified", authentication=result.state, source=None, text=quote,
                location=None, in_table=False, start=None, end=None,
                note=result.reason)


def passage(quote: str, sources: Dict[str, str], origin: str) -> dict:
    """Backward-compatible single passage with an origin."""
    p = _passage(quote, sources)
    p.update(origins=[origin], origin=origin, role=None, role_basis=None)
    return p


def collect_passages(d: dict, sources: Dict[str, str]) -> List[dict]:
    """All passages for one item, de-duplicated, each with its origins and the
    verifier's role where one exists.

    Sources, in order: quotations in the original item (no role: the item's
    author offers them, nobody has assessed them); the verifier's evidence
    passages (version 2; role as the verifier gave it); the verifier's main
    quotation (role from the evidence list if it appears there, otherwise
    inferred from the verdict in a version-1 record, and labelled so)."""
    passages: List[dict] = []

    def add(quote, origin, role=None, role_basis=None):
        quote = (quote or "").strip()
        if not quote:
            return
        p = _passage(quote, sources)
        for q in passages:
            same = (p["status"] == "located" and q["status"] == "located" and p["start"] is not None
                    and p["start"] == q["start"] and p["source"] == q["source"]) or \
                   (p["status"] == q["status"] == "unverified" and
                    _fold_with_map(p["text"], True)[0] == _fold_with_map(q["text"], True)[0])
            if same:
                if origin not in q["origins"]:
                    q["origins"].append(origin)
                if role and not q["role"]:
                    q["role"], q["role_basis"] = role, role_basis
                return
        p.update(origins=[origin], role=role, role_basis=role_basis)
        p["origin"] = origin
        passages.append(p)

    for q in _item_quotes(d.get("original", "")):
        add(q, "quoted by the review item as its evidence")
    has_v2 = "evidence" in d
    for e in d.get("evidence") or []:
        role = e.get("role") if e.get("role") in ROLE_NAMES else None
        add(e.get("quote", ""), "cited by the verifier", role, "the verifier's reading" if role else None)
    main = (d.get("quote") or "").strip()
    if main:
        role = None if has_v2 and d.get("evidence") else ROLE_FROM_VERDICT.get(d.get("verdict") or "")
        basis = ("inferred from the verifier's verdict (record without evidence roles)"
                 if role else None)
        add(main, "cited by the verifier", role, basis)
    original = d.get("original", "")
    for p in passages:
        p["origin"] = "; ".join(p["origins"])
        p["matches_item_text"] = p["status"] == "unverified" and matches_item_text(p["text"], original)
    return passages


def matches_item_text(quote: str, original: str) -> bool:
    """True when the quotation (each part of it, if joined by an ellipsis)
    appears in the review item's own wording. Used only to explain why a
    quotation failed authentication; never makes a quotation evidence."""
    hay = _fold_with_map(original or "", False)[0]
    parts = [q for q in re.split(r"\.\.\.|\u2026", quote or "") if len(q.split()) >= 3]
    if not hay or not parts:
        return False
    return all(_fold_with_map(q, False)[0].strip() in hay for q in parts)


def primary_quotation_notice(d: dict, passages: List[dict], sources: Dict[str, str]) -> Optional[dict]:
    """A notice when the verifier's primary quotation is not authenticated by
    the application's own check against the manuscript."""
    main = (d.get("quote") or "").strip()
    if not main:
        return None
    check = _passage(main, sources)
    if check["status"] == "located":
        return None
    copied = matches_item_text(main, d.get("original", ""))
    others = [p for p in passages if p["status"] == "located" and "cited by the verifier" in p["origin"]]
    detail = ("The verifier's primary quotation could not be found in the manuscript as one contiguous "
              f"passage ({check['note']}). It is not shown as manuscript evidence.")
    if copied:
        detail += (" Its text matches the review item's own wording, so it may have been taken from the "
                   "item rather than from the manuscript.")
    if others:
        detail += (f" {len(others)} other passage(s) cited by the verifier were located verbatim and are "
                   "shown first below. Whether they bear out the verdict is the verifier's reading; the "
                   "application has not checked it.")
    else:
        detail += " No other passage cited by the verifier was located."
    return {"code": "primary_quotation_not_authenticated", "detail": detail,
            "matches_item_text": copied, "authenticated_passages": len(others)}


# ---------------------------------------------------------------------------
# Readability: sentence segmentation of authenticated passages
# ---------------------------------------------------------------------------

_ABBREV = re.compile(r"(?:\b(?:e\.g|i\.e|et al|Fig|Figs|Eq|Eqs|vs|approx|cf|No|Ref|Refs|Suppl|Tab)\.)$")
_BOUNDARY = re.compile(r"(?<=[.!?])\s+(?=[\"\u201c(\[]?[A-Z0-9])")


def split_sentences(text: str) -> List[str]:
    """Deterministic sentence segments whose concatenation is exactly the
    passage. Separators stay attached to the preceding segment, so nothing is
    dropped, added or reordered."""
    segments, start = [], 0
    for m in _BOUNDARY.finditer(text):
        if _ABBREV.search(text[start:m.start()]):
            continue
        segments.append(text[start:m.end()])
        start = m.end()
    segments.append(text[start:])
    return [seg for seg in segments if seg]


def _terms(text: str) -> set:
    return rp._content_tokens(text or "") - rp._QA_STOPWORDS


# ---------------------------------------------------------------------------
# Mechanical inconsistency warnings (no model call)
# ---------------------------------------------------------------------------
# Warnings say only that the verifier's own record looks internally
# inconsistent. They never say the item, or the verdict, is right or wrong,
# and they change nothing. Thresholds were fixed before testing and are
# evaluated on fictional fixtures (tests/verification_warning_fixtures.py);
# they were not tuned on any real manuscript record.

WARNING_TEXT = "Potential inconsistency in verification assessment \u2014 human review recommended."
RESTATE_MIN_TERMS = 5
RESTATE_MAX_NOVEL_SHARE = 0.25
_CHANGE_MARKERS = {"not", "no", "never", "none", "neither", "nor", "without", "rather", "instead",
                   "however", "although", "though", "but", "except", "only", "incorrect", "incorrectly",
                   "wrong", "overstates", "overstated", "unsupported", "unjustified", "fails", "cannot"}
_SUBJECT = r"(?:concern|claim|criticism|conclusion|inference|item|strength|point|observation)"
_AFFIRM = re.compile(_SUBJECT + r"\b[^.;]{0,80}?\b(?:is|are|remains|seems)\s+(?:fully\s+|entirely\s+)?"
                     r"(?:valid|justified|warranted|correct|accurate|sound|supported)\b", re.I)
_DENY = re.compile(r"\b(?:not\s+(?:justified|supported|warranted|established)|unjustified|unsupported|"
                   r"unwarranted|overstat\w*|does\s+not\s+follow|is\s+incorrect|is\s+wrong)\b", re.I)


def _words(text: str) -> set:
    return set(re.findall(r"[a-z]+(?:'t)?", (text or "").lower()))


def restates(correction: str, original: str) -> bool:
    """True when the correction adds almost no content words to the original
    item and introduces no negation or contrast word the original lacks."""
    corr, orig = _terms(correction), _terms(original)
    if len(corr) < RESTATE_MIN_TERMS:
        return False
    if (_words(correction) - _words(original)) & _CHANGE_MARKERS:
        return False
    return len(corr - orig) / len(corr) <= RESTATE_MAX_NOVEL_SHARE


def warnings_for(d: dict, passages: List[dict]) -> List[dict]:
    verdict = d.get("verdict") or ""
    out = []
    roles = [p["role"] for p in passages if p["status"] == "located"
             and p.get("role_basis") == "the verifier's reading"]
    if verdict == "correct" and roles and all(r == "supports" for r in roles):
        out.append({"code": "correction_with_only_supporting_evidence",
                    "detail": "The verifier proposes a correction, but every authenticated passage it "
                              "cited is labelled as supporting the original item."})
    if verdict == "correct" and (d.get("correction") or "").strip() and \
            restates(d["correction"], d.get("original", "")):
        out.append({"code": "correction_restates_item",
                    "detail": "The proposed correction repeats the original item's content without an "
                              "identifiable change (no new substantive terms, negation or contrast)."})
    parts = _reason_parts(d.get("reason", ""))
    inference = parts.get("inference") or ("" if parts else d.get("reason", ""))
    affirm = [m.group(0) for m in _AFFIRM.finditer(inference) if not re.search(r"\bnot\b|n't", m.group(0))]
    if verdict in ("correct", "reject") and affirm:
        out.append({"code": "verdict_conflicts_with_reasoning",
                    "detail": f"The verdict is '{verdict}', but the verifier's reasoning states: "
                              f"\u201c{affirm[0]}\u201d."})
    narrowed = narrowed_scope(d.get("original", ""), d.get("reason", "")) if verdict == "supported" else None
    if narrowed:
        out.append({"code": "supported_despite_narrower_scope",
                    "detail": f"The item makes a claim about all {narrowed[0]}, but the verifier's reasoning "
                              f"refers to \u201c{narrowed[1]}\u201d, and the verdict is 'supported' without "
                              f"qualification. Check whether the claim holds for every one of the "
                              f"{narrowed[0]}."})
    if verdict == "supported" and _DENY.search(inference):
        out.append({"code": "verdict_conflicts_with_reasoning",
                    "detail": "The verdict is 'supported', but the verifier's reasoning states: "
                              f"\u201c{_DENY.search(inference).group(0)}\u201d."})
    return out


def duplicate_warnings(d: dict, titles: Optional[Dict[str, str]] = None) -> List[dict]:
    """duplicate_of names another item but the verdict is not 'duplicate'.
    Advisory only: nothing is merged or removed. Items the application itself
    merged (outcome merged_into) carry a duplicate_of it wrote, so they are
    not checked."""
    target = (d.get("duplicate_of") or "").strip()
    verdict = d.get("verdict") or ""
    if not target or verdict == "duplicate" or d.get("outcome") == "merged_into":
        return []
    if target == d.get("label"):
        detail = (f"The verifier's record names this item itself in duplicate_of, with the verdict "
                  f"'{verdict or 'none'}'. Nothing was merged.")
        return [{"code": "duplicate_reference_without_duplicate_verdict", "detail": detail, "ref": None}]
    known = titles is None or target in titles
    detail = (f"The verifier's record names {target} as the item this one duplicates (duplicate_of), but "
              f"its verdict is '{verdict or 'none'}', not 'duplicate'. Neither item was merged or removed; "
              f"compare them yourself.")
    if titles and target in titles:
        detail += f" {target}: {titles[target]}"
    elif not known:
        detail += f" No item labelled {target} is in this record."
    return [{"code": "duplicate_reference_without_duplicate_verdict", "detail": detail,
             "ref": target if known else None}]


_NUMWORDS = {"two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
             "nine": 9, "ten": 10, "eleven": 11, "twelve": 12}
_NUM = "|".join(_NUMWORDS)
_UNIVERSAL = r"\b(?:all|each\s+of\s+the|every\s+one\s+of\s+the)\s+(?:of\s+the\s+|the\s+)?({n})\b"
_PARTIAL = re.compile(rf"\b(one|{_NUM})\s+of\s+the\s+({_NUM})\b", re.I)
_SCOPED = re.compile(rf"\b(?:the|these|those|only|just)\s+({_NUM})((?:\s+[a-z-]+){{0,2}}?\s+[a-z-]+s)\b", re.I)
# Counted things that are not members of the set the item quantifies over.
_COUNT_UNITS = {"years", "months", "weeks", "days", "hours", "minutes", "seconds", "times", "folds",
                "repetitions", "repeats", "decimals", "percent", "points"}
_NOT_NOUNS = {"is", "was", "has", "does", "as", "its", "this", "thus", "us", "his", "yes", "less",
              "plus", "across", "always", "whereas"}


def narrowed_scope(original: str, reasoning: str) -> Optional[Tuple[str, str]]:
    """When the item makes a claim about all N of something ("all four
    models") and the verifier's own reasoning speaks of fewer ("the three
    measurement-based models", "three of the four"), return (the count word in
    the item, the reasoning's phrase).

    Deliberately narrow: only counts written as words (two to twelve), only
    universal phrasings in the item, and no match when the reasoning itself
    repeats the universal claim. Counts of time or repetitions are ignored."""
    reasoning = reasoning or ""
    for m in re.finditer(_UNIVERSAL.format(n=_NUM), original or "", re.I):
        word = m.group(1).lower()
        n = _NUMWORDS[word]
        if re.search(_UNIVERSAL.format(n=word), reasoning, re.I):
            continue
        for p in _PARTIAL.finditer(reasoning):
            a = _NUMWORDS.get(p.group(1).lower(), 1)
            if _NUMWORDS[p.group(2).lower()] == n and a < n:
                return word, p.group(0)
        for p in _SCOPED.finditer(reasoning):
            noun = p.group(2).split()[-1].lower()
            if _NUMWORDS[p.group(1).lower()] < n and len(noun) >= 4 and \
                    noun not in _COUNT_UNITS and noun not in _NOT_NOUNS:
                return word, p.group(0).strip()
    return None


# ---------------------------------------------------------------------------
# Building cards
# ---------------------------------------------------------------------------

_REASON_PART = re.compile(r"(Premise|Inference|Acknowledged)\s*:\s*(.*?)(?=(?:;\s*)?(?:Premise|Inference|Acknowledged)\s*:|$)",
                          re.I | re.S)


def _reason_parts(reason: str) -> Dict[str, str]:
    """The verifier's structured reason, when it used the Premise/Inference/
    Acknowledged form. Returned as text only; never classified."""
    parts = {}
    for key, value in _REASON_PART.findall(reason or ""):
        value = value.strip().rstrip(";").strip()
        if value:
            parts[key.lower()] = value
    return parts


def _item_quotes(text: str) -> List[str]:
    """Quotations the original item offers as its own evidence."""
    return rp.authenticatable_quotes(text)


def _dimensions(d: dict, passages: List[dict], scope: str) -> dict:
    verdict = d.get("verdict") or ""
    main = (d.get("quote") or "").strip()
    main_located = bool(main) and bool(d.get("quote_located"))
    located = [p for p in passages if p["status"] == "located"]
    verifier_located = [p for p in located if "cited by the verifier" in p["origin"]]
    unverified = [p for p in passages if p["status"] == "unverified"]
    absence = (" The verifier saw excerpts only." if scope == "excerpts" else "") + \
        " This does not mean the manuscript lacks the information: extraction or retrieval can miss text."

    if verifier_located:
        ev = ("located", "The application found the passage(s) verbatim in the manuscript. That they "
              "are relevant to the item is the verifier's reading.")
    elif located:
        ev = ("item_quote_only", "Only the review item's own quotation was found verbatim; the "
              "verifier cited no located passage.")
    elif unverified:
        ev = ("unverified_only", "Every quotation offered could not be found in the manuscript as one "
              "contiguous passage, so none is shown as manuscript evidence." + absence)
    else:
        ev = ("none", "No passage was cited or located." + absence)

    if verdict == "supported" and main_located:
        prem = ("consistent", "The verifier judged the item's factual premise consistent with a "
                "passage the application located. The application has not checked that reading.")
    elif verdict == "reject" and main_located:
        prem = ("inconsistent", "The verifier judged the item inconsistent with a passage the "
                "application located; the item has not been removed. The application has not "
                "checked that reading.")
    elif verdict == "correct" and main_located:
        prem = ("questioned", "The verifier proposed a correction with a located passage. The "
                "record does not say whether the premise or the conclusion is at fault.")
    elif main and not main_located and verifier_located:
        prem = ("not_assessed", "The verifier's primary quotation could not be located. Other passages "
                "it cited were located and are shown, but the application cannot tell whether they bear "
                "out the verdict.")
    elif main and not main_located:
        prem = ("not_assessed", "The verifier's quotation could not be located, so its verdict is "
                "not backed by authenticated evidence.")
    elif verdict == "supported":
        prem = ("not_assessed", "The verifier judged the item supported but cited no passage.")
    else:
        prem = ("not_assessed", "No verdict backed by a located passage." + absence)

    if verdict in ("correct", "reject") and main_located:
        concl = ("questioned", "The verifier questions the item. Whether its methodological "
                 "conclusion holds is for the reviewer.")
    else:
        concl = ("requires_judgement", "No record establishes whether the evidence justifies the "
                 "item's methodological conclusion. A passage consistent with a factual premise does "
                 "not establish the conclusion drawn from it.")

    comp = ("not_established", "The application cannot judge whether the located passages are all "
            "that is relevant." + ("" if located else " No passage was located." + absence))
    return {
        "evidence": {"state": ev[0], "label": EVIDENCE[ev[0]], "basis": ev[1]},
        "factual_premise": {"state": prem[0], "label": PREMISE[prem[0]], "basis": prem[1]},
        "methodological_conclusion": {"state": concl[0], "label": CONCLUSION[concl[0]], "basis": concl[1]},
        "evidence_completeness": {"state": comp[0], "label": COMPLETENESS[comp[0]], "basis": comp[1]},
    }


def build_card(d: dict, sources: Dict[str, str], scope: str = "complete",
               titles: Optional[Dict[str, str]] = None) -> dict:
    model_quote_located = d.get("quote_located")
    d = dict(d)
    d["quote_located"] = bool(sv._located(d.get("quote") or "", sources))
    original = d.get("original", "")
    kind = d.get("kind", "")
    verdict = d.get("verdict") or ""
    outcome = d.get("outcome") or "kept_unassessed"
    passages = collect_passages(d, sources)
    located = [p for p in passages if p["status"] == "located"]
    unverified = [p for p in passages if p["status"] == "unverified"]
    groups = {
        "supporting": [p for p in located if p["role"] == "supports"],
        "qualifying": [p for p in located if p["role"] in ("qualifies", "contradicts")],
        "other": [p for p in located if p["role"] not in ROLE_NAMES],
        "unverified": unverified,
    }
    dims = _dimensions(d, passages, scope)
    parts = _reason_parts(d.get("reason", ""))
    # Sentences are a reading aid only; no sentence is singled out, because
    # any choice made from the verifier's wording would repeat its emphasis.
    for p in located:
        p["sentences"] = split_sentences(p["text"])
    warnings = warnings_for(d, passages)
    warnings += duplicate_warnings(d, titles)
    notice = primary_quotation_notice(d, passages, sources)

    established = None
    if located:
        established = [f"The manuscript contains the {len(located)} passage(s) shown, located "
                       "verbatim by the application."]
        if parts.get("premise"):
            established.append("Verifier on the factual premise (unverified): " + parts["premise"])
        established.append("What the passages mean for the item is the verifier's reading or your "
                           "judgement; the application has not established it.")

    uncertain: List[str] = []
    if outcome == "kept_corrected":
        uncertain.append("Verifier's proposed correction (unverified): " + d.get("correction", ""))
        if d.get("surviving_point"):
            uncertain.append("Point the verifier says remains (unverified): " + d["surviving_point"])
    if outcome == "kept_disputed":
        uncertain.append("Verifier's objection (unverified): " + (d.get("reason") or "no reason given"))
    if parts.get("inference"):
        uncertain.append("Verifier on the inference (unverified): " + parts["inference"])
    if parts.get("acknowledged"):
        uncertain.append("Verifier on author acknowledgement (unverified): " + parts["acknowledged"])
    if verdict == "unresolved" and d.get("reason") and not parts:
        uncertain.append("Verifier could not settle it (unverified): " + d["reason"])
    if d.get("note") and outcome in ("kept_unresolved", "kept_unassessed"):
        uncertain.append("Application note: " + d["note"])
    for p in unverified:
        uncertain.append("A quotation (" + p["origin"] + ") could not be authenticated: " + p["note"]
                         + ". Not evidence that the manuscript lacks the information.")
    if kind != "prompt":
        uncertain.append("Whether the evidence justifies the item's methodological conclusion has not "
                         "been established.")

    if (d.get("reviewer_check") or "").strip():
        check, check_source = d["reviewer_check"].strip(), "suggested by the verifier (unverified)"
    elif "reviewer_check" in d:
        check, check_source = None, "the verifier supplied no check"
    else:
        check, check_source = None, "the verification record predates this field"

    if outcome == "merged_into":
        status = (f"The verifier judged this a duplicate of {d.get('duplicate_of', '')}; it was merged "
                  "there and its text is kept here unchanged.")
    else:
        status = _status_text(located, unverified, verdict)

    return {
        "label": d.get("label"),
        "kind": kind,
        "kind_name": sv.KIND_NAMES.get(kind, kind),
        "title": (titles or {}).get(d.get("label")) or _title(original),
        "original": original,
        "evidence": passages,
        "evidence_groups": groups,
        "established": established,
        "uncertain": uncertain or None,
        "reviewer_check": check,
        "reviewer_check_source": check_source,
        "dimensions": dims,
        "verification_status": status,
        "warnings": warnings,
        "quotation_notice": notice,
        "duplicate_references_from": [],
        "record_version": 2 if ("evidence" in d or "reviewer_check" in d) else 1,
        "provenance": {
            "model_verdict": verdict,
            "model_verdict_name": sv.VERDICT_NAMES.get(verdict, verdict),
            "model_reason": d.get("reason", ""),
            "model_reason_parts": parts or None,
            "model_quote": (d.get("quote") or "").strip(),
            "model_quote_located": model_quote_located,
            "model_correction": d.get("correction", ""),
            "model_surviving_point": d.get("surviving_point", ""),
            "model_duplicate_of": d.get("duplicate_of", ""),
            "model_reviewer_check": d.get("reviewer_check"),
            "model_evidence": d.get("evidence"),
            "application_action": outcome,
            "application_action_name": sv.OUTCOMES.get(outcome, outcome),
            "application_note": d.get("note", ""),
        },
    }


def _title(text: str) -> str:
    return sv.Item("x", "", 0, 0, text).title


def _status_text(located, unverified, verdict) -> str:
    bits = [f"{len(located)} passage(s) located verbatim by the application" if located
            else "no passage located by the application"]
    if unverified:
        bits.append(f"{len(unverified)} quotation(s) could not be authenticated")
    bits.append("verifier's verdict: " + (sv.VERDICT_NAMES.get(verdict, verdict) or "none"))
    bits.append("the item itself has not been verified: a located passage does not establish that "
                "the item is correct")
    return "; ".join(bits).capitalize() + "."


def build_cards(verification: dict, sources: Dict[str, str]) -> dict:
    """Cards for every item in a verification record (source_verification
    VerificationResult.as_dict()), with the record's own context."""
    scope = verification.get("scope", "")
    dispositions = verification.get("dispositions", [])
    titles = {d.get("label"): _title(d.get("original", "")) for d in dispositions}
    cards = [build_card(d, sources, scope, titles) for d in dispositions]
    by_label = {c["label"]: c for c in cards}
    for c in cards:
        for w in c["warnings"]:
            target = w.get("ref")
            if w["code"] == "duplicate_reference_without_duplicate_verdict" and target in by_label:
                by_label[target]["duplicate_references_from"].append(c["label"])
    return {
        "schema_version": SCHEMA_VERSION,
        "verification_status": verification.get("status", "unknown"),
        "verification_error": verification.get("error", ""),
        "scope": scope,
        "unexamined_figures": verification.get("unexamined_figures", []),
        "automated_flags": verification.get("automated_flags", []),
        "cards": cards,
    }


# ---------------------------------------------------------------------------
# Standalone HTML prototype
# ---------------------------------------------------------------------------

_CSS = """
:root{--bg:#f6f5f0;--surface:#fff;--surface-alt:#edece7;--text:#1a1a18;--text-muted:#6b6962;
--accent:#2d5a27;--accent-light:#e8f0e6;--border:#d4d2cb;--radius:10px;--warn:#8a5a00;--warn-bg:#fff7e6;
--error:#9b2c2c;--error-bg:#fef2f2;--shadow:0 1px 3px rgba(0,0,0,.06)}
@media (prefers-color-scheme:dark){:root{--bg:#1a1a18;--surface:#262622;--surface-alt:#2e2e2a;--text:#e8e6df;
--text-muted:#8a877e;--accent:#6abf5e;--accent-light:#2a3d28;--border:#3a3a36;--warn:#e5b45a;--warn-bg:#3a2e14;
--error:#f87171;--error-bg:#3b1c1c}}
*{box-sizing:border-box}body{margin:0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
background:var(--bg);color:var(--text);line-height:1.5}
header{padding:14px 24px;background:var(--surface);border-bottom:1px solid var(--border)}
header h1{font-family:Georgia,'Times New Roman',serif;font-size:1.2rem;margin:0 0 4px}
header p{margin:0;font-size:.82rem;color:var(--text-muted);max-width:900px}
main{max-width:980px;margin:0 auto;padding:18px 24px 60px}
.toolbar{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin:4px 0 16px;font-size:.8rem;color:var(--text-muted)}
.btn{font:inherit;font-size:.78rem;padding:5px 12px;border:1px solid var(--border);border-radius:6px;
background:var(--surface);color:var(--text);cursor:pointer}.btn:hover{border-color:var(--accent);color:var(--accent)}
.btn.on{background:var(--accent);color:#fff;border-color:var(--accent)}.btn.primary{border-color:var(--accent);color:var(--accent);font-weight:600}.btn:disabled{opacity:.45;cursor:not-allowed}
.notice{background:var(--surface);border:1px solid var(--border);border-left:4px solid var(--accent);
border-radius:var(--radius);padding:10px 14px;font-size:.82rem;margin-bottom:14px}
.summary{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px;margin:0 0 12px}
.summary div{background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:8px 10px;font-size:.78rem;color:var(--text-muted)}
.summary strong{display:block;font-size:1.05rem;color:var(--text)}
.filters{display:flex;gap:6px;flex-wrap:wrap;align-items:center;margin:0 0 12px;font-size:.78rem;color:var(--text-muted)}
.obs{white-space:pre-wrap;font-size:.84rem;margin-top:3px;display:-webkit-box;-webkit-line-clamp:6;-webkit-box-orient:vertical;overflow:hidden}
.jumps{font-size:.74rem;margin-top:4px}.jumps a{color:var(--accent)}
.viewnav{position:sticky;top:0;z-index:5;background:var(--surface);border-bottom:1px solid var(--border);padding:8px 24px;display:flex;gap:8px;flex-wrap:wrap;align-items:center}
.viewnav a,.viewnav span.cur{font-size:.8rem;padding:5px 12px;border:1px solid var(--border);border-radius:6px;text-decoration:none;color:var(--text)}
.viewnav span.cur{background:var(--accent);color:#fff;border-color:var(--accent);font-weight:600}
.xlinks{margin:10px 0 2px;font-size:.8rem;display:flex;gap:6px 14px;flex-wrap:wrap;align-items:center}.xlinks a{color:var(--accent)}
.step{display:flex;gap:6px;margin-top:12px}
.card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);box-shadow:var(--shadow);margin-bottom:10px}
.card>summary{list-style:none;cursor:pointer;padding:10px 14px;display:flex;gap:10px;align-items:flex-start}
.card>summary::-webkit-details-marker{display:none}
.lbl{font:600 .72rem 'SFMono-Regular',Consolas,monospace;background:var(--surface-alt);border-radius:4px;padding:2px 6px;white-space:nowrap}
.sumtext{flex:1;font-size:.88rem}.kind{font-size:.7rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:.05em}
.chips{display:flex;gap:4px;flex-wrap:wrap;margin-top:4px}
.chip{font-size:.68rem;border:1px solid var(--border);border-radius:10px;padding:1px 7px;color:var(--text-muted)}
.chip.good{border-color:var(--accent);color:var(--accent)}.chip.warn{border-color:var(--warn);color:var(--warn)}
.chip.bad{border-color:var(--error);color:var(--error)}
.dec{font-size:.72rem;font-weight:600;white-space:nowrap;color:var(--text-muted)}.dec.set{color:var(--accent)}
.body{padding:0 14px 14px;border-top:1px solid var(--border)}.body p{font-size:.86rem}.body h3[id]{scroll-margin-top:110px}
h4{font-size:.78rem;margin:10px 0 2px}.sent{display:block;margin:1px 0}
.authbox{margin:10px 0;padding:8px 10px;border:1px solid var(--warn);background:var(--warn-bg);border-radius:6px;font-size:.82rem}
.backref{margin:10px 0;font-size:.8rem;color:var(--text-muted)}
.warnbox{margin:10px 0;padding:8px 10px;border:1px solid var(--error);background:var(--error-bg);border-radius:6px;font-size:.82rem}
.warnbox ul{margin:4px 0}h3{font-size:.74rem;text-transform:uppercase;letter-spacing:.06em;color:var(--text-muted);margin:14px 0 4px}
.orig{font-size:.86rem;background:var(--surface-alt);border-radius:6px;padding:8px 10px}
.orig p,.obs p{margin:0 0 .55em}
.orig li p,.obs li p{margin:0}
.orig ul,.orig ol,.obs ul,.obs ol{padding-left:1.3em;margin:.35em 0}
.orig blockquote{margin:.5em 0;padding-left:.8em;border-left:3px solid var(--border)}
.orig pre{overflow:auto}
.orig code{white-space:pre-wrap}

blockquote{margin:6px 0;padding:6px 10px;border-left:3px solid var(--accent);background:var(--accent-light);font-size:.84rem}
blockquote.unv{border-left-color:var(--error);background:var(--error-bg)}
.meta{font-size:.72rem;color:var(--text-muted)}.na{font-size:.82rem;color:var(--text-muted);font-style:italic}
ul{margin:4px 0;padding-left:20px;font-size:.84rem}table.dims{border-collapse:collapse;font-size:.8rem;width:100%}
table.dims td{border-top:1px solid var(--border);padding:5px 6px;vertical-align:top}table.dims td:first-child{white-space:nowrap;font-weight:600;width:1%}
.decide{display:flex;gap:6px;flex-wrap:wrap;align-items:center;margin-top:6px}
textarea{width:100%;font:inherit;font-size:.82rem;border:1px solid var(--border);border-radius:6px;padding:6px;background:var(--surface);color:var(--text)}
details.prov summary{cursor:pointer;font-size:.86rem;color:var(--text-muted);margin-top:16px}
pre{white-space:pre-wrap;font-size:.74rem;background:var(--surface-alt);padding:8px;border-radius:6px}
.print-note{display:none}

/* Printing. Screen rules that break page fragmentation are undone here only:
   the finding preview's -webkit-box line clamp and the flex card heading made
   expanded cards overlap the next card when split across pages, the clamp
   truncated long findings, and a textarea prints clipped. Controls are not
   printed; the reviewer's recorded decision and wording are. */
@media print{
:root{--bg:#fff;--surface:#fff;--surface-alt:#f2f2ef;--text:#000;--text-muted:#333;--accent:#1f4a1b;
--accent-light:#f1f5ef;--border:#aaa;--warn:#5c3d00;--warn-bg:#fff;--error:#7a1c1c;--error-bg:#fff;--shadow:none}
@page{margin:14mm}
html,body{background:#fff;color:#000}
body{font-size:10.5pt;line-height:1.4}
.viewnav,.toolbar,.filters,.jumps,.xlinks,.step,.decide,textarea,button,.btn,#syncStatus,details.prov{display:none!important}
header{padding:0 0 6pt;border-bottom:1px solid #999}
main{max-width:none;margin:0;padding:0}
.notice{border-left-width:2px}
.summary{display:block}.summary div{display:inline-block;border:none;padding:0;margin:0 10pt 4pt 0}
.summary strong{display:inline;margin-right:3pt}
.card{display:block;box-shadow:none;border:1px solid #aaa;border-radius:0;margin:0 0 8pt;overflow:visible;
break-inside:auto;page-break-inside:auto}
.card>summary{display:block;padding:6pt 8pt}
.lbl,.dec{display:inline-block;margin-right:6pt}
.sumtext{display:block;margin-top:3pt}
.obs{display:block;-webkit-line-clamp:none;line-clamp:none;-webkit-box-orient:initial;overflow:visible;max-height:none}
.body{display:block;padding:0 8pt 8pt;overflow:visible}
h3,h4{break-after:avoid;page-break-after:avoid}
.warnbox,.authbox,.backref,.chips,table.dims tr,.print-note{break-inside:avoid;page-break-inside:avoid}
blockquote,.orig,pre{overflow:visible}
pre,.orig code{white-space:pre-wrap;overflow-wrap:anywhere}
.print-note.has{display:block;border:1px solid #888;padding:4pt 6pt;margin-top:4pt;white-space:pre-wrap}
a{color:inherit;text-decoration:none}
}
"""

_JS = r"""
const KEY = 'evidence-card-decisions:' + DOC_ID;
let decisions = {};
try { decisions = JSON.parse(localStorage.getItem(KEY) || '{}') || {}; } catch (e) { decisions = {}; }
function save() {
  try { localStorage.setItem(KEY, JSON.stringify(decisions)); localStorage.setItem(KEY + ':updated', new Date().toISOString()); } catch (e) {}
}
// Local review store (only when the page was served for a saved review): the
// only request this page makes, to its own review's decisions on this
// computer, carrying the fingerprint of this manuscript's card set.
function syncStatus(text) { const e = document.getElementById('syncStatus'); if (e) e.textContent = text; }
async function pushToStore() {
  if (!SYNC) return;
  try {
    const r = await fetch(SYNC.url, { method: 'PUT', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ card_fingerprint: SYNC.fingerprint, decisions: decisions }) });
    syncStatus(r.ok ? 'Decisions saved in the local review store on this computer.'
      : 'Not saved to the local review store (' + r.status + '); kept in this browser only.');
  } catch (e) { syncStatus('Local review store not reachable; decisions are kept in this browser only.'); }
}
async function pullFromStore() {
  if (!SYNC) return;
  try {
    const r = await fetch(SYNC.url, { cache: 'no-store' });
    if (!r.ok) { syncStatus('Not saved to the local review store (' + r.status + '); decisions are kept in this browser only.'); return; }
    const d = await r.json();
    if (d.card_fingerprint !== SYNC.fingerprint) { syncStatus('Stored decisions belong to a different manuscript or card set and were not loaded.'); return; }
    let localUpdated = null;
    try { localUpdated = localStorage.getItem(KEY + ':updated'); } catch (e) {}
    const localNewer = Object.keys(decisions).length && (!d.saved || (localUpdated && localUpdated > (d.updated_at || '')));
    if (localNewer) { await pushToStore(); return; }
    if (d.saved) {
      decisions = d.decisions || {};
      try { localStorage.setItem(KEY, JSON.stringify(decisions)); localStorage.setItem(KEY + ':updated', d.updated_at || ''); } catch (e) {}
      LABELS.forEach(refresh);
    }
    syncStatus('Decisions are saved in the local review store on this computer as you confirm them.');
  } catch (e) { syncStatus('Local review store not reachable; decisions are kept in this browser only.'); }
}
const pending = {};
function choose(label, choice) {
  pending[label] = choice;
  document.querySelectorAll('[data-choice-for="' + label + '"]').forEach(b =>
    b.classList.toggle('on', b.dataset.choice === choice));
  const note = document.getElementById('note-' + label);
  if (note) note.style.display = choice === 'revise' ? 'block' : 'none';
  document.getElementById('confirm-' + label).disabled = false;
}
function confirmDecision(label) {
  const choice = pending[label];
  if (!choice) return;
  const note = document.getElementById('note-' + label);
  decisions[label] = { decision: choice, note: note ? note.value : '', confirmed_at: new Date().toISOString() };
  delete pending[label];
  save(); refresh(label); pushToStore();
}
function undoDecision(label) { delete decisions[label]; save(); refresh(label); pushToStore(); }
function refresh(label) {
  const d = decisions[label];
  const tag = document.getElementById('dec-' + label);
  tag.textContent = d ? ('Your decision: ' + d.decision) : 'Unreviewed';
  tag.classList.toggle('set', !!d);
  document.getElementById('undo-' + label).style.display = d ? 'inline-block' : 'none';
  document.getElementById('confirm-' + label).disabled = true;
  document.querySelectorAll('[data-choice-for="' + label + '"]').forEach(b =>
    b.classList.toggle('on', !!d && b.dataset.choice === d.decision));
  const note = document.getElementById('note-' + label);
  if (note) { note.value = d ? d.note : note.value; note.style.display = d && d.decision === 'revise' ? 'block' : 'none'; }
  // Printed in place of the text box, which prints clipped; set as text only.
  const printed = document.getElementById('pnote-' + label);
  if (printed) {
    const wording = d && (d.note || '').trim();
    printed.textContent = wording
      ? (d.decision === 'revise' ? "Reviewer's revised wording: " : 'Reviewer comment: ') + d.note : '';
    printed.classList.toggle('has', !!wording);
  }
  const done = Object.keys(decisions).length;
  document.getElementById('progress').textContent = done + ' of ' + LABELS.length + ' items decided';
  updateSummary();
  applyFilter();
}
function exportDecisions() {
  const blob = new Blob([JSON.stringify({ document: DOC_ID, decisions: decisions }, null, 2)], { type: 'application/json' });
  const a = document.createElement('a'); a.href = URL.createObjectURL(blob);
  a.download = 'evidence-card-decisions.json'; a.click();
}
// Human-readable record, generated by the server from the stored cards and
// these decisions (deterministic; nothing is saved or changed).
async function exportDecisionsMarkdown(kind) {
  if (!EXPORT_MD) return;
  // 'summary' is the concise reviewer summary; anything else the full audit
  // record. Both are built from the same decisions.
  const url = kind === 'summary' ? EXPORT_MD.replace(/decisions\.md$/, 'decisions-summary.md') : EXPORT_MD;
  try {
    const r = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ decisions: decisions }) });
    if (!r.ok) { syncStatus('The Markdown record could not be created (' + r.status + '). The JSON export is still available.'); return; }
    const name = ((r.headers.get('Content-Disposition') || '').match(/filename="([^"]+)"/) || [])[1] || 'reviewer-decisions.md';
    const a = document.createElement('a'); a.href = URL.createObjectURL(await r.blob());
    a.download = name; a.click();
  } catch (e) { syncStatus('The Markdown record could not be created. The JSON export is still available.'); }
}
function expandAll(open) { document.querySelectorAll('details.card').forEach(d => d.open = open); }
// Navigation only: counts and filters read the confirmed decisions above.
let FILTER = 'all';
function stateOf(label) { const d = decisions[label]; return d ? d.decision : 'unreviewed'; }
function updateSummary() {
  const c = { unreviewed: 0, retain: 0, revise: 0, dismiss: 0 };
  LABELS.forEach(l => { const s = stateOf(l); c[s] = (c[s] || 0) + 1; });
  Object.keys(c).forEach(k => { const e = document.getElementById('count-' + k); if (e) e.textContent = c[k]; });
}
function applyFilter() {
  let shown = 0;
  LABELS.forEach(l => {
    const card = document.getElementById('card-' + l);
    if (!card) return;
    const show = FILTER === 'all' || (FILTER === 'warnings' ? card.dataset.warn === '1' : stateOf(l) === FILTER);
    card.style.display = show ? '' : 'none';
    if (show) shown += 1;
  });
  const e = document.getElementById('shown');
  if (e) e.textContent = shown + ' of ' + LABELS.length + ' shown';
  document.querySelectorAll('[data-filter]').forEach(b => b.classList.toggle('on', b.dataset.filter === FILTER));
}
function setFilter(f) { FILTER = f; applyFilter(); }
// Previous / Next among the cards the current filter shows.
function visibleLabels() {
  return LABELS.filter(l => { const c = document.getElementById('card-' + l); return c && c.style.display !== 'none'; });
}
function showCard(label) {
  const card = document.getElementById('card-' + label);
  if (!card) return false;
  if (card.style.display === 'none') { FILTER = 'all'; applyFilter(); }
  card.open = true;
  if (card.scrollIntoView) card.scrollIntoView({ block: 'start' });
  return true;
}
function stepFinding(label, direction) {
  const shown = visibleLabels();
  const i = shown.indexOf(label);
  const next = shown[i + direction];
  if (i < 0 || !next) return false;
  const here = document.getElementById('card-' + label);
  if (here) here.open = false;
  return showCard(next);
}
function openFromHash() {
  if (typeof location === 'undefined') return;
  const m = /^#card-([A-Z]\d{1,3})$/.exec(location.hash || '');
  if (m && LABELS.indexOf(m[1]) >= 0) showCard(m[1]);
}
if (typeof addEventListener === 'function') addEventListener('hashchange', openFromHash);
function jumpTo(ev, label, section) {
  if (ev) { ev.preventDefault(); ev.stopPropagation(); }
  const card = document.getElementById('card-' + label);
  if (card) card.open = true;
  const target = document.getElementById(section + '-' + label);
  if (target && target.scrollIntoView) target.scrollIntoView({ block: 'start' });
  return false;
}
LABELS.forEach(refresh);
pullFromStore();
openFromHash();
"""


def _js(value) -> str:
    """JSON for embedding inside a <script> element."""
    return json.dumps(value).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")


def _e(text) -> str:
    return html.escape(str(text if text is not None else ""), quote=True)


def _chip(state: str, label: str, good: Sequence[str], bad: Sequence[str]) -> str:
    cls = "good" if state in good else "bad" if state in bad else "warn"
    return f'<span class="chip {cls}">{_e(label)}</span>'


def manuscript_target(p: dict, documents: list, job_id: str) -> Optional[dict]:
    """Navigation only: require an existing exact source/document binding.

    No filename guesses, primary-document fallback, or visual transcriptions.
    The PDF matcher independently refuses text it cannot locate exactly.
    """
    if (not re.fullmatch(r"[0-9a-f]{12}", job_id or "") or p.get("status") != "located"
            or not p.get("source") or p.get("start") is None or not p.get("text")):
        return None
    matches = [d for d in documents if d.get("source_label") == p["source"]]
    if len(matches) != 1:
        return None
    d = matches[0]
    if (not d.get("available") or d.get("suffix") != ".pdf"
            or not re.fullmatch(r"d\d{1,2}", d.get("id") or "")
            or not re.fullmatch(r"[0-9a-f]{64}", d.get("sha256") or "")):
        return None
    page = re.search(r"\bp\.\s*(\d+)", p.get("location") or "")
    return {"job": job_id, "doc": d["id"], "sha256": d["sha256"], "quote": p["text"],
            "page": int(page.group(1)) if page else None}


def _passage_html(p: dict, nav=None) -> str:
    loc = p["location"] or "location not marked in the extracted text"
    role = ""
    if p.get("role") in ROLE_NAMES:
        basis = "AI interpretation" if p.get("role_basis") == "the verifier's reading" else "Inferred from the AI assessment"
        description = {"supports": "supports this finding", "qualifies": "qualifies this finding",
                       "contradicts": "contradicts this finding"}[p["role"]]
        role = f' · {_e(basis)}: {_e(description)}'
    extra = f' · {_e(p["note"])}' if p.get("note") else ""
    target = manuscript_target(p, (nav or {}).get("documents", []), (nav or {}).get("job_id", ""))
    control = (f'<button type="button" class="btn show-manuscript" data-passage="{_e(_js(target))}">'
               'Show in manuscript</button>' if target else "")
    sentences = p.get("sentences") or [p["text"]]
    body = "".join(f'<span class="sent">{_e(s)}</span>' for s in sentences)
    return (f'<blockquote>{body}</blockquote><div class="meta">Matched manuscript text · '
            f'{_e(p["source"])} · {_e(loc)} · section not reliably available{role}{extra}</div>{control}')


def _ref_link(label, short=False) -> str:
    """In-page link to another card; opens it. Navigation only."""
    if not label:
        return ""
    lab = _e(label)
    text = "open" if short else f"Go to {lab}"
    return (f' (<a href="#card-{lab}" onclick="document.getElementById(\'card-{lab}\').open=true">'
            f'{text}</a>)')


_APPENDIX_STATUS = {
    "none_for_kind": "No Human Evidence Appendix entry exists for this kind of finding",
    "not_generated": "No Human Evidence Appendix entry exists for this finding",
    "merged": "Merged into another finding; see that finding's appendix entry",
    "absent": "Not present in the final appraisal (reason unknown); no appendix entry",
    "unlinkable": "An appendix entry may exist but cannot be reliably linked",
}
WORKSPACE_TARGET = "qwen-review-workspace"   # the name the main page gives its window


def _cross_links_html(card: dict, nav: Optional[dict]) -> str:
    """Links from a card to the same finding in the other two views. A link
    is given only where the server established it; otherwise the card says so."""
    if not nav:
        return ""
    lab = _e(card["label"])
    job = _e(nav["job_id"])
    link = (nav.get("links") or {}).get(card["label"]) or {}
    base = f'/#review={job}'
    target = f'target="{WORKSPACE_TARGET}"'
    if link.get("appraisal_line") is not None:
        appraisal = f'<a href="{base}&amp;finding={lab}" {target}>Critical Appraisal finding</a>'
    else:
        appraisal = ('<span class="meta">Not linked to a Critical Appraisal finding'
                     + (f' ({_e(link["note"])})' if link.get("note") else "") + '</span>')
    if link.get("appendix_id"):
        aid = _e(link["appendix_id"])
        appendix = f'<a href="{base}&amp;appendix={aid}" {target}>Human Evidence Appendix entry {aid}</a>'
    else:
        appendix = '<span class="meta">' + _e(_APPENDIX_STATUS.get(link.get("appendix_status"),
                                                               _APPENDIX_STATUS["unlinkable"])) + '</span>'
    investigate = (f'<a href="{base}&amp;investigate={lab}" {target} title="Opens Investigate a finding for this '
                   f'review. Nothing is asked until you type a question.">Investigate this finding</a>')
    return f'<div class="xlinks">{appraisal}<span>·</span>{appendix}<span>·</span>{investigate}</div>'


def _reviewer_checks_html(check: str) -> str:
    """Display generated Markdown without altering the suggested checks."""
    return '<div class="suggested-checks">' + presentation.markdown_html(check) + '</div>'


def _reviewer_context_html(card: dict) -> str:
    items = presentation.context_items(card)
    h = ['<p>The evidence does not establish whether this finding is justified.</p>']
    if items:
        h.append(f'<p class="meta">{_e(presentation.EXPLANATION_QUALIFICATION)}</p><ul>')
        h.extend(f'<li>{presentation.markdown_html(text)}</li>' for text in items)
        h.append('</ul>')
    if (card.get("dimensions", {}).get("evidence_completeness") or {}).get("state") == "not_established":
        h.append('<p class="meta">The evidence shown may be incomplete.</p>')
    return "".join(h)


def render_card(card: dict, nav: Optional[dict] = None) -> str:
    lab = _e(card["label"])
    dims = card["dimensions"]
    chips = ""
    if card.get("warnings"):
        chips += '<span class="chip bad">Potential inconsistency</span>'
    for w in card.get("warnings") or []:
        if w["code"] == "duplicate_reference_without_duplicate_verdict" and w.get("ref"):
            chips += f'<span class="chip bad">Names {_e(w["ref"])} as duplicate; not merged</span>'
    if card["provenance"]["application_action"] == "merged_into":
        chips += f'<span class="chip warn">Merged into {_e(card["provenance"]["model_duplicate_of"])}</span>'
    # The original finding stays as written; the chip only says that the AI
    # verifier disputed it, so the reviewer weighs the two assessments.
    if presentation.disputed(card):
        chips += ('<span class="chip warn" title="The AI verifier proposed a correction or objected; '
                  'neither assessment has been established. See section 4.">Disputed by the AI verifier</span>')
    warn = "1" if (card.get("warnings") or card.get("quotation_notice") or presentation.disputed(card)) else "0"
    jumps = (f'<div class="jumps"><a href="#check-{lab}" onclick="return jumpTo(event,\'{lab}\',\'check\')">'
             f'What needs checking?</a> · <a href="#evidence-{lab}" onclick="return jumpTo(event,\'{lab}\',\'evidence\')">'
             'Manuscript evidence</a></div>')
    h = [f'<details class="card" id="card-{lab}" data-label="{lab}" data-warn="{warn}"><summary>',
         f'<span class="lbl">{lab}</span><div class="sumtext"><div class="kind">{_e(card["kind_name"])}</div>',
         f'<div class="obs" title="Original AI-generated review item">{presentation.markdown_html(card["original"])}</div>'
         f'<div class="chips">{chips}</div>{jumps}</div>',
         f'<span class="dec" id="dec-{lab}">Unreviewed</span></summary><div class="body">']
    if presentation.material_warnings(card):
        h.append(f'<div class="warnbox"><strong>{_e(WARNING_TEXT)}</strong><ul>'
                 + "".join(f"<li>{_e(w['detail'])}{_ref_link(w.get('ref'))}</li>" for w in presentation.material_warnings(card))
                 + '</ul><div class="meta">A check of the AI\'s own record. It does not '
                   'say whether the item or the verdict is right, and nothing has been changed.</div></div>')
    if card.get("duplicate_references_from"):
        h.append('<div class="backref">Named as the duplicated item by '
                 + ", ".join(f'{_e(x)}{_ref_link(x, short=True)}' for x in card["duplicate_references_from"])
                 + ", whose verdict is not 'duplicate'. Nothing was merged.</div>")
    h.append(_cross_links_html(card, nav))
    h.append('<h3>1. Original finding</h3><p class="meta">AI-generated; wording unchanged.</p>')
    h.append(f'<div class="orig">{presentation.markdown_html(card["original"])}</div>')

    h.append(f'<h3 id="evidence-{lab}">2. Evidence from the manuscript</h3>')
    g = card["evidence_groups"]
    message = presentation.authentication_message(card)
    if message:
        h.append(f'<div class="authbox"><strong>Evidence not confirmed</strong><p>{_e(message)}</p></div>')
    if g["supporting"] or g["qualifying"] or g["other"]:
        h.append('<p class="meta">Passages located in the manuscript are shown below. '
                 'Evidence roles reflect the AI’s interpretation.</p>')
    elif not message:
        h.append('<p>No manuscript passage was located for this finding.</p>')
    if message or not (g["supporting"] or g["qualifying"] or g["other"]):
        h.append('<p class="meta">An unsuccessful match does not show that the information is absent.</p>')
    for key, heading in (
            ("supporting", "Evidence cited for this finding"),
            ("qualifying", "Evidence that may challenge this finding"),
            ("other", "Other relevant evidence")):
        if g[key]:
            h.append(f'<h4>{heading}</h4>')
            h.append("".join(_passage_html(p, nav) for p in g[key]))
    if not (g["supporting"] or g["qualifying"] or g["other"]):
        h.append('<p class="na">No additional evidence was identified.</p>')
    if g["unverified"]:
        h.append('<h4>Quotations not located in the manuscript</h4>')
        for p in g["unverified"]:
            h.append(f'<blockquote class="unv">{_e(p["text"])}</blockquote>')
    h.append(f'<h3 id="check-{lab}">3. What needs checking?</h3>')
    h.append(f'<p class="meta">{_e(presentation.CHECK_QUALIFICATION)}</p>')
    if card["reviewer_check"]:
        h.append(_reviewer_checks_html(card["reviewer_check"]))
    else:
        h.append('<p class="na">No suggested check is available in this review record.</p>')
    h.append('<h3>4. What remains uncertain?</h3>')
    h.append(_reviewer_context_html(card))
    h.append('<h3>5. Your decision</h3><div class="decide">')
    for choice, name in (("retain", "Retain"), ("revise", "Revise"), ("dismiss", "Dismiss")):
        h.append(f'<button class="btn" data-choice-for="{lab}" data-choice="{choice}" '
                 f'onclick="choose(\'{lab}\',\'{choice}\')">{name}</button>')
    h.append(f'<button class="btn" id="confirm-{lab}" disabled onclick="confirmDecision(\'{lab}\')">Confirm decision</button>'
             f'<button class="btn" id="undo-{lab}" style="display:none" onclick="undoDecision(\'{lab}\')">Undo</button></div>'
             f'<textarea id="note-{lab}" rows="2" style="display:none;margin-top:6px" '
             f'placeholder="How should this item be revised? (your wording; the review is not changed)"></textarea>'
             f'<div class="print-note" id="pnote-{lab}"></div>')
    h.append('<details class="prov"><summary>6. Detailed verification record</summary>')
    h.append('<h4>Evidence checks and limitations</h4>')
    h.append(f'<p>{_e(card["verification_status"])}</p><table class="dims">')
    for key, name in (("evidence", "Evidence"), ("factual_premise", "Factual premise"),
                      ("methodological_conclusion", "Methodological conclusion"),
                      ("evidence_completeness", "Evidence completeness")):
        h.append(f'<tr><td>{name}</td><td><strong>{_e(dims[key]["label"])}</strong><br>'
                 f'<span class="meta">{_e(dims[key]["basis"])}</span></td></tr>')
    h.append('</table><p class="meta">Descriptive states, not probabilities. None of them states that '
             'the finding is correct.</p>')
    h.append(f'<div class="step"><button class="btn" onclick="stepFinding(\'{lab}\',-1)">← Previous finding</button>'
             f'<button class="btn" onclick="stepFinding(\'{lab}\',1)">Next finding →</button></div>')
    h.append('</div></details>')
    return "".join(h)


def _summary_html(cards: List[dict]) -> str:
    """Compact overview: what the review contains, what the checks flagged,
    and the reviewer's decisions (filled in by the page script)."""
    kinds = {}
    for c in cards:
        kinds[c["kind_name"]] = kinds.get(c["kind_name"], 0) + 1
    composition = ", ".join(f"{n} {_e(k.lower())}{'s' if n != 1 else ''}" for k, n in kinds.items()) or "none"
    flagged = sum(1 for c in cards if c.get("warnings"))
    notices = sum(1 for c in cards if c.get("quotation_notice"))
    merged = sum(1 for c in cards if c["provenance"]["application_action"] == "merged_into")
    contested = sum(1 for c in cards if presentation.disputed(c))
    cells = [
        f'<div><strong>{len(cards)}</strong>review items ({composition})</div>',
        f'<div><strong>{contested}</strong>disputed by the AI verifier</div>',
        f'<div><strong>{flagged}</strong>with a potential-inconsistency warning</div>',
        f'<div><strong>{notices}</strong>with an unauthenticated primary quotation</div>',
        f'<div><strong>{merged}</strong>merged as duplicates</div>',
        '<div><strong id="count-unreviewed">0</strong>unreviewed</div>',
        '<div><strong id="count-retain">0</strong>retained</div>',
        '<div><strong id="count-revise">0</strong>revised</div>',
        '<div><strong id="count-dismiss">0</strong>dismissed</div>',
    ]
    filters = "".join(
        f'<button class="btn" data-filter="{key}" onclick="setFilter(\'{key}\')">{name}</button>'
        for key, name in (("all", "All"), ("unreviewed", "Unreviewed"), ("retain", "Retained"),
                          ("revise", "Revised"), ("dismiss", "Dismissed"), ("warnings", "With warnings")))
    return (f'<div class="summary" aria-label="Summary">{"".join(cells)}</div>'
            f'<div class="filters"><span>Show:</span>{filters}<span id="shown"></span></div>')


def render_html(card_set: dict, title: str, doc_id: str, sync: Optional[dict] = None,
                nav: Optional[dict] = None) -> str:
    """The standalone page. With sync ({"url", "fingerprint"}), confirmed
    decisions are also saved to that review's record in the local review
    store; without it the page makes no request at all."""
    cards = card_set["cards"]
    labels = [c["label"] for c in cards]
    status = card_set.get("verification_status", "unknown")
    notes = []
    if status != "completed":
        notes.append(f"Source verification status: {_e(status)} {_e(card_set.get('verification_error', ''))}. "
                     "Model verdicts may be missing.")
    if card_set.get("scope") == "excerpts":
        notes.append("The verifier saw retrieved excerpts, not the whole manuscript.")
    if card_set.get("unexamined_figures"):
        notes.append("Figures not read (caption only): " + _e("; ".join(card_set["unexamined_figures"])) + ".")
    if card_set.get("automated_flags"):
        notes.append("Automated checks on the draft (still open): " +
                     "".join(f"<br>· {_e(f)}" for f in card_set["automated_flags"]))
    body = "".join(render_card(c, nav) for c in cards) or '<p class="na">No review items.</p>'
    viewnav = ""
    if nav:
        job = _e(nav["job_id"])
        viewnav = (f'<nav class="viewnav" aria-label="Review views">'
                   f'<a href="/#review={job}&amp;view=appraisal" target="{WORKSPACE_TARGET}">Critical Appraisal</a>'
                   f'<span class="cur" aria-current="page">Evidence Cards</span>'
                   f'<a href="/#review={job}&amp;view=appendix" target="{WORKSPACE_TARGET}">Human Evidence Appendix</a>'
                   f'</nav>')
    summary = _summary_html(cards)
    export_md = (f"/api/review/{nav['job_id']}/decisions.md"
                 if nav and re.fullmatch(r"[0-9a-f]{12}", str(nav.get("job_id") or "")) else None)
    # Opens the dedicated print view in its own tab: printing from the Review
    # Workspace prints the whole application with this page clipped in a frame.
    print_button = (f'<a class="btn primary" href="/review/evidence-cards/{_e(nav["job_id"])}/print" '
                    'target="_blank" rel="noopener" title="Opens a print-ready page with every card in full; '
                    'choose Summary or Detailed there">Print / Save Evidence Cards as PDF</a>'
                    if export_md else "")
    export_md_button = ('<button class="btn primary" onclick="exportDecisionsMarkdown(\'summary\')" '
                        'title="Concise summary of your decisions, for preparing your review">'
                        'Export reviewer summary (.md)</button>'
                        '<button class="btn" onclick="exportDecisionsMarkdown(\'audit\')" '
                        'title="Complete record with evidence, verification details and technical records">'
                        'Export full audit record (.md)</button>' if export_md else "")
    sync = {"url": str(sync["url"]), "fingerprint": str(sync["fingerprint"])} if sync else None
    storage = ("Decisions are saved in this browser and in this review's record in the local review store on "
               "this computer (and can be exported as a Markdown record or as JSON); they are not sent anywhere else and do not alter "
               "the review." if sync else
               "Decisions are stored only in this browser (and can be exported as JSON); they are not sent to "
               "the server and do not alter the review.")
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0"><title>{_e(title)}</title>
<style>{_CSS}</style></head><body>
<header><h1>{_e(title)}</h1><p>Each card shows the original AI-generated finding, manuscript evidence, suggested checks and
questions that need your judgement. Your decisions are recorded here only; the review itself is not changed.</p></header>
{viewnav}
<main><div class="notice"><strong>Prototype.</strong> {storage}
{"<br>" + "<br>".join(notes) if notes else ""}<br><span id="syncStatus" class="meta"></span></div>
{summary}
<div class="toolbar"><span id="progress"></span>
<button class="btn" onclick="expandAll(true)">Expand all</button>
<button class="btn" onclick="expandAll(false)">Collapse all</button>
{print_button}{export_md_button}<button class="btn" onclick="exportDecisions()" title="Structured data, for re-use in other tools">Export decisions (JSON)</button></div>
{body}</main>
<script>const DOC_ID = {_js(doc_id)}; const LABELS = {_js(labels)}; const SYNC = {_js(sync)};
const EXPORT_MD = {_js(export_md)};
{_JS}</script><script src="/review/passage-navigation.js"></script></body></html>"""
