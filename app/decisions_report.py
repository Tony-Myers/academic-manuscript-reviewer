"""Human reviewer decisions as a Markdown record.

Deterministic: the report is assembled only from the stored Evidence Card set
and the reviewer's recorded decisions. No model is called, nothing is
summarised or reworded, and nothing is stored or changed. Missing information
is reported as missing, never filled in.

Every piece of text taken from the record (manuscript quotations, AI output,
reviewer comments) is escaped so that Markdown renders it exactly as written:
statistical notation such as "*p* < 0.05", "χ 2(2)", "-0.41" or "[95% CI]" and
any reviewer wording appear unchanged. Escaping uses backslashes only, so the
original text is recovered exactly by removing them.
"""
from __future__ import annotations

from html import escape as html_escape
import json
import re
from typing import Any, Dict, List, Optional

import reviewer_presentation as presentation

DECISION_NAMES = {"retain": "Retain", "revise": "Revise", "dismiss": "Dismiss"}
DECISION_ORDER = ("retain", "revise", "dismiss")

# CommonMark: any ASCII punctuation may be backslash-escaped and then renders
# literally. These are the characters that can start or change formatting.
_INLINE = re.compile(r'([\\`*_{}\[\]<>#|!~$&])')
# Characters that only matter at the start of a line (block markers).
_LINE_START = re.compile(r'^(\s*)([+\-=]|\d+[.)])')


def md_text(text: Any) -> str:
    """Escape one line or paragraph of verbatim text for inline Markdown."""
    s = "" if text is None else str(text)
    s = _INLINE.sub(r'\\\1', s)
    return "\n".join(_LINE_START.sub(lambda m: m.group(1) + _escape_marker(m.group(2)), line)
                     for line in s.split("\n"))


def _escape_marker(marker: str) -> str:
    # "1." -> "1\." ; "-" -> "\-" (the digits stay as written).
    return marker[:-1] + "\\" + marker[-1] if len(marker) > 1 else "\\" + marker


def md_cell(text: Any) -> str:
    """Escape text for a table cell: one line, pipes escaped."""
    return md_text(re.sub(r"\s*\n\s*", " ", "" if text is None else str(text)).strip())


def md_quote(text: Any) -> str:
    """A verbatim blockquote. Line breaks in the source are kept as hard breaks,
    blank lines as paragraph breaks, so the wording and layout survive."""
    # Leading indentation is dropped (it would otherwise turn a line into a
    # code block); it carries no wording.
    lines = [line.strip() for line in md_text(text).split("\n")]
    out = []
    for i, line in enumerate(lines):
        nxt = lines[i + 1] if i + 1 < len(lines) else None
        hard = bool(nxt) and bool(line)
        out.append("> " + line + ("\\" if hard else "") if line else ">")
    return "\n".join(out)


def _when(stamp: Optional[str]) -> str:
    return md_text(stamp) if stamp else "not recorded"


def _dims_table(dims: Dict[str, Any]) -> List[str]:
    rows = ["| Dimension | Assessment | Basis |", "| --- | --- | --- |"]
    for key, name in (("evidence", "Evidence"), ("factual_premise", "Factual premise"),
                      ("methodological_conclusion", "Methodological conclusion"),
                      ("evidence_completeness", "Evidence completeness")):
        d = dims.get(key) or {}
        rows.append(f"| {name} | {md_cell(d.get('label') or 'not recorded')} | {md_cell(d.get('basis') or '')} |")
    return rows


def _passage(p: Dict[str, Any]) -> List[str]:
    out = [md_quote(p.get("text", "")), ""]
    where = []
    if p.get("source"):
        where.append("source: " + md_text(p["source"]))
    where.append(md_text(p["location"]) if p.get("location") else "location not recorded")
    if p.get("in_table"):
        where.append("table text")
    if p.get("role"):
        role = {"supports": "supports this finding", "qualifies": "qualifies this finding",
                "contradicts": "contradicts this finding"}.get(p["role"], p["role"])
        basis = "AI interpretation" if p.get("role_basis") == "the verifier's reading" else "Inferred from the AI assessment"
        where.append(basis + ": " + md_text(role))
    out.extend(["*" + " · ".join(where) + "*", ""])
    if p.get("note"):
        out.extend(["Evidence limitation: " + md_text(p["note"]), ""])
    return out


def _card(card: Dict[str, Any], decision: Optional[Dict[str, Any]]) -> List[str]:
    lab = card.get("label", "")
    out = [f"### {md_text(lab)}. {md_text(card.get('kind_name', ''))}", ""]

    # --- Human record first, clearly separated from AI output ---
    out.append("#### Human reviewer decision")
    out.append("")
    if decision:
        out.append(f"**Decision:** {DECISION_NAMES.get(decision.get('decision'), md_text(decision.get('decision')))}  ")
        out.append(f"**Confirmed:** {_when(decision.get('confirmed_at'))}")
        out.append("")
        note = decision.get("note") or ""
        if note.strip():
            out.append("**Reviewer comment or amendment (verbatim):**")
            out.append("")
            out.append(md_quote(note))
        else:
            out.append("*No comment recorded.*")
    else:
        out.append("**Decision:** none recorded. This item is outstanding.")
    out.append("")

    out.extend(["#### Original finding", "", md_quote(card.get("original", "")), ""])
    out.extend(["#### Evidence from the manuscript", ""])
    message = presentation.authentication_message(card)
    if message:
        out.extend(["**Evidence not confirmed**", "", md_text(message), ""])
    for w in presentation.material_warnings(card):
        out.extend(["- " + md_text(w["detail"]), ""])
    groups = card.get("evidence_groups") or {}
    any_passage = False
    for key, heading in (("supporting", "Evidence cited for this finding"),
                         ("qualifying", "Evidence that may challenge this finding"),
                         ("other", "Other relevant evidence")):
        items = groups.get(key) or []
        if items:
            any_passage = True
            out.extend([f"**{heading}**", ""])
            for passage in items:
                out.extend(_passage(passage))
    if not any_passage and not message:
        out.extend(["No additional evidence was identified.", ""])
    check = card.get("reviewer_check")
    if check:
        out.extend(["#### What needs checking?", ""])
        lead, items = presentation.check_parts(check)
        if lead:
            out.extend([md_quote(lead), ""])
        for item in items:
            out.extend(["- " + md_text(item).replace("\n", "\n  "), ""])
    uncertainty = presentation.context_items(card)
    out.extend(["#### What still needs checking", ""])
    if uncertainty:
        out.extend("- " + md_text(item) for item in uncertainty)
    else:
        out.append("No further explanation is available in the saved record.")
    if (card.get("dimensions", {}).get("evidence_completeness") or {}).get("state") == "not_established":
        out.append("- The evidence shown may be incomplete.")
    out.extend(["", "---", ""])
    return out


def _audit_card(card):
    """Retain all stored technical information separately from the reviewer report."""
    out = ["<details>", f"<summary>{html_escape(str(card.get('label', '')))}: detailed verification record</summary>", ""]
    out.extend(_dims_table(card.get("dimensions") or {}))
    out.extend(["", "Original stored card fields (including authentication details and AI provenance):", "",
                md_quote(json.dumps(card, indent=2, ensure_ascii=False)), "", "</details>", ""])
    return out


def render_markdown(card_set: Dict[str, Any], decisions: Dict[str, Any], meta: Dict[str, Any]) -> str:
    """The reviewer-decisions record.

    card_set  -- the stored Evidence Card set ({"cards": [...], ...}).
    decisions -- {label: {"decision", "note", "confirmed_at"}} as recorded.
    meta      -- {"job_id", "filename", "title", "completed_at", "exported_at",
                  "decisions_saved_at"}; any may be missing.
    """
    cards = card_set.get("cards") or []
    decisions = decisions or {}
    title = meta.get("title")
    out = ["# Human reviewer decisions: full audit record", ""]
    out.append("Complete record for audit. For preparing your review, the concise reviewer "
               "summary export contains the same decisions without the verification detail.")
    out.append("")
    out.append("| | |")
    out.append("| --- | --- |")
    out.append(f"| Manuscript title | {md_cell(title) if title else 'not recorded by the application'} |")
    out.append(f"| Manuscript file | {md_cell(meta.get('filename') or 'not recorded')} |")
    out.append(f"| Review identifier | {md_cell(meta.get('job_id') or 'not recorded')} |")
    out.append(f"| Review date | {md_cell(meta.get('completed_at') or 'not recorded')} |")
    out.append(f"| Decisions last saved | {md_cell(meta.get('decisions_saved_at') or 'not recorded in the local review store')} |")
    out.append(f"| Report generated | {md_cell(meta.get('exported_at') or 'not recorded')} |")
    out.append("")
    out.append("This report preserves the original findings and human reviewer decisions and comments. "
               "AI findings, suggested checks and explanations require reviewer judgement. Located passages do not "
               "establish that the methodological interpretation is correct; evidence roles reflect the AI’s reading. "
               "Check the assumptions behind suggested checks, and any claims about missing information, against "
               "the manuscript. An unsuccessful match does not establish that information is absent. "
               "Whether a passage was highlighted in the displayed PDF is not recorded in the saved review. "
               "Full technical records are retained separately at the end.")
    out.append("")

    counts = {k: 0 for k in DECISION_ORDER}
    outstanding = []
    for c in cards:
        d = decisions.get(c.get("label"))
        if d and d.get("decision") in counts:
            counts[d["decision"]] += 1
        else:
            outstanding.append(c)
    out.append("## Summary of reviewer decisions")
    out.append("")
    out.append("| Decision | Items |")
    out.append("| --- | --- |")
    for k in DECISION_ORDER:
        labs = [c["label"] for c in cards if (decisions.get(c.get("label")) or {}).get("decision") == k]
        out.append(f"| {DECISION_NAMES[k]} | {counts[k]}" + (f" ({md_cell(', '.join(labs))})" if labs else "") + " |")
    out.append(f"| No decision recorded | {len(outstanding)}"
               + (f" ({md_cell(', '.join(c['label'] for c in outstanding))})" if outstanding else "") + " |")
    out.append(f"| **Total review items** | **{len(cards)}** |")
    out.append("")
    with_comment = [c["label"] for c in cards if ((decisions.get(c.get("label")) or {}).get("note") or "").strip()]
    out.append(f"Items with a reviewer comment or amendment: {md_text(', '.join(with_comment)) if with_comment else 'none'}.")
    out.append("")

    out.append("## Outstanding concerns")
    out.append("")
    if outstanding:
        out.append("No decision has been recorded for these items:")
        out.append("")
        for c in outstanding:
            out.append(f"- **{md_text(c.get('label', ''))}** ({md_text(c.get('kind_name', ''))}): {md_text(c.get('title', ''))}")
    else:
        out.append("None: a decision has been recorded for every review item.")
    out.append("")
    flags = card_set.get("automated_flags") or []
    if flags:
        out.append("Automated checks on the draft that remain open (application output):")
        out.append("")
        out.extend("- " + md_text(f) for f in flags)
        out.append("")

    out.append("## Review items")
    out.append("")
    for c in cards:
        out.extend(_card(c, decisions.get(c.get("label"))))

    out.append("## Overall reviewer notes")
    out.append("")
    notes = meta.get("overall_notes")
    if notes and str(notes).strip():
        out.append(md_quote(notes))
    else:
        out.append("No overall reviewer notes are recorded for this review.")
    out.append("")
    out.extend(["## Detailed verification record", "",
                "Original AI output and application checks, retained for audit. These are not human reviewer decisions.", ""])
    for card in cards:
        out.extend(_audit_card(card))
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Concise reviewer summary
# ---------------------------------------------------------------------------
# For preparing the reviewer's own report. Built from the same card set and
# the same decisions as render_markdown(); it only leaves material out. No
# manuscript quotations, verification narratives, explanations, JSON or
# authentication metadata: those stay in the full audit record.

_MARKER = re.compile(r"^\s*[-*]?\s*\**\s*(?:Strength|Concern|Check)\**\s*:?\**\s*:?\s*", re.I)
_TRAILING_FIELD = re.compile(r"\s*\**\s*(?:Evidence|Reason|Why it matters|Severity)\s*\**\s*:.*$", re.I | re.S)


def finding_statement(card: Dict[str, Any]) -> str:
    """The AI finding's own statement, without its quoted evidence or
    supporting fields. Whole, never shortened; falls back to the title."""
    original = (card.get("original") or "").strip()
    first = original.splitlines()[0] if original else ""
    statement = _TRAILING_FIELD.sub("", _MARKER.sub("", first)).strip(" *")
    return statement or str(card.get("title") or "").strip() or "(no statement recorded)"


def _evidence_reference(card: Dict[str, Any]) -> str:
    """One line naming where evidence was located; no quotations."""
    groups = card.get("evidence_groups") or {}

    def places(items):
        seen = []
        for p in items:
            bits = [str(p.get(k)) for k in ("source", "location") if p.get(k)]
            if p.get("in_table"):
                bits.append("table")
            place = ", ".join(bits) or "location not recorded"
            if place not in seen:
                seen.append(place)
        return "; ".join(seen)

    parts = []
    if groups.get("supporting"):
        parts.append("cited passage(s) located at " + places(groups["supporting"]))
    if groups.get("qualifying"):
        parts.append("passage(s) that may challenge it at " + places(groups["qualifying"]))
    if groups.get("other"):
        parts.append("other relevant passage(s) at " + places(groups["other"]))
    if groups.get("unverified"):
        parts.append(f"{len(groups['unverified'])} AI quotation(s) not located in the manuscript")
    if not parts:
        return "no manuscript passage located"
    return "; ".join(parts)


def _is_disputed(card: Dict[str, Any]) -> bool:
    try:
        return bool(presentation.disputed(card))
    except Exception:                                           # noqa: BLE001
        return False


def _concise_item(card: Dict[str, Any], decision: Optional[Dict[str, Any]], *, revised: bool) -> List[str]:
    lab = md_text(card.get("label", ""))
    kind = md_text(card.get("kind_name", ""))
    note = ((decision or {}).get("note") or "").strip()
    out = [f"### {lab} ({kind})", ""]
    if revised:
        out.append("**Reviewer's revised wording (verbatim):**")
        out.append("")
        if note:
            out.append(md_quote(note))
        else:
            out.append("*No revised wording was recorded. The original AI observation below "
                       "has not been accepted in its place.*")
        out.extend(["", "*Original AI observation, for reference only:* " + md_text(finding_statement(card))])
    else:
        out.append(md_text(finding_statement(card)))
        if note:
            out.extend(["", "**Reviewer comment (verbatim):**", "", md_quote(note)])
    refs = "Evidence: " + md_text(_evidence_reference(card)) + "."
    if _is_disputed(card):
        refs += " The AI verifier disputed this finding; see the full audit record."
    out.extend(["", "*" + refs + "*", ""])
    return out


def render_concise_markdown(card_set: Dict[str, Any], decisions: Dict[str, Any],
                            meta: Dict[str, Any]) -> str:
    """A short reviewer summary for writing the final report.

    Same arguments, and the same decisions, as render_markdown(). Retained and
    revised findings are given in full; revised ones in the reviewer's own
    wording, with the AI observation marked as reference only. Dismissed
    findings get one line each, and findings without a decision are listed as
    outstanding, never as accepted.
    """
    cards = card_set.get("cards") or []
    decisions = decisions or {}

    def decision_of(card):
        d = decisions.get(card.get("label"))
        return d if d and d.get("decision") in DECISION_NAMES else None

    groups = {k: [c for c in cards if (decision_of(c) or {}).get("decision") == k] for k in DECISION_ORDER}
    outstanding = [c for c in cards if decision_of(c) is None]

    out = ["# Reviewer summary", ""]
    title = meta.get("title")
    ident = []
    if title:
        ident.append(f"**Manuscript:** {md_text(title)}")
    if meta.get("filename"):
        ident.append(f"**File:** {md_text(meta['filename'])}")
    if meta.get("job_id"):
        ident.append(f"**Review:** {md_text(meta['job_id'])}")
    if meta.get("completed_at"):
        ident.append(f"**Review date:** {md_text(meta['completed_at'])}")
    if meta.get("decisions_saved_at"):
        ident.append(f"**Decisions saved:** {md_text(meta['decisions_saved_at'])}")
    if meta.get("exported_at"):
        ident.append(f"**Exported:** {md_text(meta['exported_at'])}")
    if ident:
        out.extend(["  \n".join(ident), ""])
    out.extend(["The findings below were generated by AI and assessed by the reviewer, who remains "
                "responsible for the final review. Full evidence and verification details are in the "
                "full audit record.", ""])

    out.extend(["## Decisions", "",
                f"Retained: {len(groups['retain'])} · Revised: {len(groups['revise'])} · "
                f"Dismissed: {len(groups['dismiss'])} · Awaiting a decision: {len(outstanding)} · "
                f"Total: {len(cards)}", ""])

    out.extend(["## Retained findings", ""])
    if groups["retain"]:
        for c in groups["retain"]:
            out.extend(_concise_item(c, decision_of(c), revised=False))
    else:
        out.extend(["None.", ""])

    out.extend(["## Revised findings", ""])
    if groups["revise"]:
        for c in groups["revise"]:
            out.extend(_concise_item(c, decision_of(c), revised=True))
    else:
        out.extend(["None.", ""])

    out.extend(["## Dismissed findings", ""])
    if groups["dismiss"]:
        for c in groups["dismiss"]:
            line = f"- **{md_text(c.get('label', ''))}** ({md_text(c.get('kind_name', ''))}): {md_text(c.get('title', ''))}"
            note = (decision_of(c).get("note") or "").strip()
            if note:
                line += " Reviewer comment: " + md_text(re.sub(r"\s*\n\s*", " ", note))
            if _is_disputed(c):
                line += " *(Disputed by the AI verifier.)*"
            out.append(line)
        out.append("")
    else:
        out.extend(["None.", ""])

    out.extend(["## Awaiting a decision", ""])
    if outstanding:
        out.append("No decision has been recorded for these AI findings; they have not been accepted.")
        out.append("")
        for c in outstanding:
            line = f"- **{md_text(c.get('label', ''))}** ({md_text(c.get('kind_name', ''))}): {md_text(c.get('title', ''))}"
            if _is_disputed(c):
                line += " *(Disputed by the AI verifier; see the full audit record.)*"
            out.append(line)
        out.append("")
    else:
        out.extend(["None.", ""])

    notes = meta.get("overall_notes")
    if notes and str(notes).strip():
        out.extend(["## Overall reviewer notes", "", md_quote(notes), ""])
    return "\n".join(out).rstrip() + "\n"
