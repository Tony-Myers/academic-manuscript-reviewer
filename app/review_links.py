"""
Shared finding identifiers across the three views of one review.

The three outputs already carry identifiers, assigned by position:

- Evidence cards (source verification): S1.., C1.., P1.., numbered in the
  draft report before post-processing. These are the shared identifiers.
- Critical Appraisal (the final report): no identifier in the body; the
  "Source verification record" table lists the same S/C/P labels.
- Human Evidence Appendix: C1.., Q1.., numbered in the final report
  (strengths have no appendix entry).

Between the draft and the final report, duplicates are merged away and
post-processing can annotate or remove items, so the numbers alone can differ.
This module links them deterministically, with no model call and no fuzzy
matching:

1. exact: a card is linked to the final-report item of the same kind whose
   statement (the text before "Evidence:" / "Reason:", whitespace-normalised)
   is identical to the card's original statement, when that match is unique in
   both directions;
2. nothing else: matching counts or positions are never treated as evidence
   that two findings are the same. No explicit provenance record links draft
   items to final-report items, so exact identity is the only basis.

Each card gets link_status: exact | merged | absent (not in the final
appraisal; every remaining final item of its type is linked to another card;
no removal record exists, so no reason is asserted) | unlinkable (an unmatched final
item of its type exists, so a reworded version may be present). Its
appendix_status says: linked | none_for_kind (strengths have no appendix
entries) | not_generated (linked finding, but the appendix generator made no
entry for it) | merged | absent | unlinkable (an entry may exist but cannot
be linked).

The appendix entry is the one generated from the same final-report line.
Nothing here changes any stored record.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

import human_evidence_appendix as hea
import source_verification as sv

_MARK = re.compile(r"^\s*[-*]\s*\**\s*(?:Strength|Concern|Check)\s*\**\s*:\s*\**\s*", re.I)
_BULLET = re.compile(r"^\s*[-*]\s+")
_SPLIT = re.compile(r"\s*\**\s*(?:Evidence|Reason|Why it matters|Severity)\s*\**\s*:", re.I)


def statement(text: str) -> str:
    """The finding's own statement: first line, marker and trailing fields removed."""
    first = (text or "").splitlines()[0] if text else ""
    first = _MARK.sub("", first) if _MARK.match(first) else _BULLET.sub("", first)
    first = _SPLIT.split(first)[0]
    return " ".join(first.replace("*", " ").split()).lower()


def appendix_ids_by_line(report_text: str) -> Dict[int, str]:
    """Line index in the final report -> Human Evidence Appendix id, using the
    appendix generator's own rules (human_evidence_appendix.extract_final_findings)."""
    out: Dict[int, str] = {}
    section, concerns, questions = None, 0, 0
    for index, line in enumerate((report_text or "").splitlines()):
        heading = hea._HEADING_RE.match(line)
        if heading:
            section = hea._normalise_heading(heading.group(1))
            continue
        if section == "directly supported concerns" and hea._CONCERN_RE.match(line):
            concerns += 1
            out[index] = f"C{concerns}"
        elif section == "verification prompts" and hea._CHECK_RE.match(line):
            questions += 1
            out[index] = f"Q{questions}"
    expected = [f["finding_id"] for f in hea.extract_final_findings(report_text)]
    return out if list(out.values()) == expected else {}


def build_links(report_text: str, verification: Optional[dict]) -> Dict[str, Any]:
    dispositions = list((verification or {}).get("dispositions") or [])
    final_items = sv.extract_items(report_text or "")
    hea_ids = appendix_ids_by_line(report_text)
    findings: List[dict] = []
    by_label: Dict[str, dict] = {}
    for d in dispositions:
        merged = d.get("outcome") == "merged_into"
        entry = {"id": d.get("label"), "kind": d.get("kind"), "title": sv.Item("x", "", 0, 0, d.get("original", "")).title,
                 "has_card": True, "appraisal_line": None, "appendix_id": None, "basis": None,
                 "link_status": "merged" if merged else None, "appendix_status": None,
                 "note": (f"merged into {d.get('duplicate_of')} as a duplicate; not listed separately in the "
                          "appraisal" if merged else None), "_merged": merged,
                 "_statement": statement(d.get("original", ""))}
        findings.append(entry)
        by_label[entry["id"]] = entry

    unlinked_appraisal: List[dict] = []
    for kind in ("strength", "concern", "prompt"):
        cards = [f for f in findings if f["kind"] == kind and not f["_merged"]]
        items = [i for i in final_items if i.kind == kind]
        item_statements = [statement(i.text) for i in items]
        used = set()
        for card in cards:
            hits = [ii for ii, s in enumerate(item_statements) if s and s == card["_statement"]]
            same = [x for x in cards if x["_statement"] == card["_statement"]]
            if len(hits) == 1 and len(same) == 1:
                item = items[hits[0]]
                used.add(hits[0])
                card.update(appraisal_line=item.start, appendix_id=hea_ids.get(item.start), basis="exact",
                            link_status="exact")
        leftover = [ii for ii in range(len(items)) if ii not in used]
        for card in cards:
            if card["link_status"]:
                continue
            if leftover:
                card["link_status"] = "unlinkable"
                card["note"] = ("no unique identical statement in the final appraisal; a reworded version may "
                                "exist, but it cannot be linked reliably")
            else:
                # No removal record exists, so the reason for the absence is not asserted.
                card["link_status"] = "absent"
                card["note"] = "not present in the final appraisal (reason unknown)"
        uncertain = any(c["link_status"] == "unlinkable" for c in cards)
        for ii in leftover:
            item = items[ii]
            unlinked_appraisal.append({"id": None, "kind": kind, "title": item.title, "has_card": False,
                                       "appraisal_line": item.start, "appendix_id": hea_ids.get(item.start),
                                       "basis": None, "link_status": "unlinkable",
                                       "appendix_status": "linked" if hea_ids.get(item.start) else
                                       ("none_for_kind" if kind == "strength" else "not_generated"),
                                       "card_status": "uncertain" if uncertain else "none",
                                       "note": ("an evidence card of this type is unmatched, so one may correspond, "
                                                "but it cannot be identified reliably" if uncertain else
                                                "every evidence card of this type corresponds to another finding")})
    for f in findings:
        if f["link_status"] == "merged":
            f["appendix_status"] = "merged"
        elif f["kind"] == "strength":
            f["appendix_status"] = "none_for_kind"
        elif f["appendix_id"]:
            f["appendix_status"] = "linked"
        elif f["link_status"] == "exact":
            f["appendix_status"] = "not_generated"
        elif f["link_status"] == "absent":
            f["appendix_status"] = "absent"
        else:
            f["appendix_status"] = "unlinkable"
    for f in findings:
        if f["link_status"] == "exact":
            f["merged_from"] = [d.get("label") for d in dispositions
                                if d.get("outcome") == "merged_into" and d.get("duplicate_of") == f["id"]]
        f.pop("_merged"), f.pop("_statement")
    linked_appendix = {f["appendix_id"] for f in findings + unlinked_appraisal if f["appendix_id"]}
    all_appendix = [f["finding_id"] for f in hea.extract_final_findings(report_text or "")]
    kinds: Dict[str, int] = {}
    for f in findings:
        kinds[f["kind"]] = kinds.get(f["kind"], 0) + 1
    return {
        "findings": findings + unlinked_appraisal,
        "summary": {
            "cards": len(findings), "by_kind": kinds,
            "linked_to_appraisal": sum(1 for f in findings if f["appraisal_line"] is not None),
            "merged": sum(1 for d in dispositions if d.get("outcome") == "merged_into"),
            "unlinked_cards": sum(1 for f in findings if f["appraisal_line"] is None),
            "absent": sum(1 for f in findings if f["link_status"] == "absent"),
            "unlinkable": sum(1 for f in findings if f["link_status"] == "unlinkable"),
            "appraisal_without_card": len(unlinked_appraisal),
            "appendix_entries": len(all_appendix),
            "appendix_without_card": len([a for a in all_appendix
                                          if a not in {f["appendix_id"] for f in findings}]),
        },
    }
