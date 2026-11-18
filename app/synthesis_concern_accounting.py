"""Observational synthesis accounting. No model, semantic matching or promotion.

Unresolved means insufficient mapping evidence, NOT a missing or valid criticism.
Existing triage groups and candidate identities are retained, never deduplicated.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
import source_verification as sv

TITLE = "Synthesis Concern Accounting — Diagnostic Only"
DISCLAIMER = "Unresolved observations are not verified methodological criticisms. Missing mappings do not establish loss or poor model performance."
CATEGORIES = ("Retained", "Merged", "Excluded", "Unresolved")


def canonical(text):
    # Formatting only. No case folding, punctuation removal or word overlap.
    return " ".join(re.sub(r"^\s*[-*]\s+", "", text or "").split())


def bullets(text, heading):
    lines = (text or "").splitlines()
    bounds = sv._section_bounds(lines, heading)
    if not bounds:
        return []
    result = []
    for line in lines[bounds[0]:bounds[1]]:
        if re.match(r"^\s*[-*]\s+", line):
            result.append(line)
        elif result and line.strip():
            result[-1] += "\n" + line
    return result


def actionable_claim(item):
    """Only the claim/check itself, never a quotation in evidence or reasons."""
    text = re.sub(r"^\s*[-*]?\s*(?:Concern|Check)\s*:\s*", "", item.text, flags=re.I)
    return re.split(r"\b(?:Evidence|Why it matters|Reason)\s*:", text, maxsplit=1)[0].strip()


def preserves(text, item, merged=False):
    claim = actionable_claim(item)
    if canonical(text) == canonical(claim):
        return True
    # A recorded merge additionally needs an unchanged, standalone component.
    # A matching fragment embedded in counterargument/evidence is insufficient.
    return merged and canonical(text) in {canonical(line) for line in claim.splitlines() if line.strip()}


PROVENANCE_MARKER = "<!-- SYNTHESIS_CONCERN_PROVENANCE -->"
PROVENANCE_END = "<!-- END_SYNTHESIS_CONCERN_PROVENANCE -->"


def synthesis_context(files):
    """Compact projection of existing IDs/priorities, not another candidate ledger."""
    themes, known, unavailable = [], {}, []
    for f in files:
        candidates = {c["candidate_id"]: c for c in f.get("candidate_findings") or []}
        for t in (f.get("candidate_triage") or {}).get("themes") or []:
            if t.get("priority") != "high": continue
            ids = list(t.get("candidate_ids") or [])
            valid = [i for i in ids if i in candidates]
            unavailable.extend(i for i in ids if i not in candidates)
            # Invalid upstream references are not transmitted as valid identities.
            for i in valid: known[i] = candidates[i]
            if valid: themes.append({"source":f.get("source_name"),"theme":t.get("theme"),"candidate_ids":valid})
    return {"themes": themes, "candidate_ids": sorted(known), "unavailable_candidate_ids": sorted(set(unavailable))}


def synthesis_instruction(context):
    if not context.get("candidate_ids"): return ""
    return """\n\nDiagnostic provenance only. The trailer is transport metadata, the sole exception to finishing after the final appraisal heading; keep the six appraisal headings unchanged. Select and write the appraisal using all existing instructions, limits and evidence. Do not add concerns to satisfy accounting. After the complete appraisal, on a new line emit:
""" + PROVENANCE_MARKER + """
{"mappings":[{"candidate_ids":["exact supplied ID"],"disposition":"Retained|Merged|Excluded|Unresolved","final_item_id":"C1 or P1, or null","reason":"brief model-reported rationale"}]}
""" + PROVENANCE_END + """
Account for every supplied candidate ID exactly once; group IDs with the same disposition/target if appropriate. C1, C2... are Concern bullets in Directly supported concerns; P1, P2... are Check bullets in Verification prompts, numbered in order. Do not insert IDs or metadata into the appraisal. Retained means an actionable concern/check represents it; Merged means its methodological meaning is incorporated into another actionable item. Retained/Merged require a target ID. Excluded requires a reason and null target. Unresolved requires null target. Confidence/commentary alone is not retention. Report decisions, not claims of independent verification. Do not invent IDs. These observations may legitimately be excluded, qualified or unresolved; priority is not an inclusion requirement.
High-priority source themes and existing candidate IDs (details remain in the file summaries):
""" + json.dumps(context["themes"],ensure_ascii=False,separators=(",", ":"))


def separate_provenance(output, context):
    """Keep native output; remove only the explicitly delimited transport trailer."""
    import re
    positions = list(re.finditer(r"(?m)^" + re.escape(PROVENANCE_MARKER) + r"[ \t]*$",output))
    record = {"native_output":output,"context":context,"raw_metadata":None,"mappings":[],"parse_error":None}
    if not positions:
        record["parse_error"]="MISSING_PROVENANCE_TRAILER"
        return output, record
    p=positions[0]
    body=output[:p.start()].rstrip()
    tail=output[p.end():]
    record["raw_metadata"]=tail
    if len(positions)!=1 or tail.count(PROVENANCE_END)!=1:
        record["parse_error"]="INCOMPLETE_OR_DUPLICATE_PROVENANCE_TRAILER"
        return body,record
    raw,after=tail.split(PROVENANCE_END)
    try:
        def unique_object(pairs):
            obj={}
            for key,value in pairs:
                if key in obj: raise ValueError("Duplicate JSON key: "+key)
                obj[key]=value
            return obj
        value=json.loads(raw,object_pairs_hook=unique_object)
        if after.strip() or not isinstance(value,dict) or set(value)!={"mappings"} or not isinstance(value["mappings"],list):
            raise ValueError("Unexpected provenance structure")
        record["mappings"]=value["mappings"]
    except (ValueError,TypeError) as exc:
        record["parse_error"]="INVALID_PROVENANCE_JSON: "+str(exc)
    return body,record


def validate_model_mappings(record, report):
    """Structural checks only; a valid target does NOT certify substantive fit."""
    expected=record.get("context",{}).get("candidate_ids",[])
    known=set(expected)
    items={i.label:i for i in sv.extract_items(report) if i.kind in ("concern","prompt")}
    problems=[]; by_id={i:[] for i in expected}
    rows=record.get("mappings") or []
    for n,row in enumerate(rows):
        errors=[]
        if not isinstance(row,dict):
            problems.append({"row":n,"problems":["INVALID_MAPPING_OBJECT"]});continue
        if set(row)!={"candidate_ids","disposition","final_item_id","reason"}: errors.append("INVALID_MAPPING_FIELDS")
        ids=row.get("candidate_ids")
        if not isinstance(ids,list) or not ids or any(not isinstance(i,str) for i in ids):
            problems.append({"row":n,"problems":errors+["MISSING_OR_INVALID_CANDIDATE_IDS"]});continue
        if len(set(ids))!=len(ids): errors.append("DUPLICATE_CANDIDATE_IDS")
        if any(i not in known for i in ids): errors.append("UNKNOWN_OR_UNSUPPLIED_CANDIDATE_ID")
        kind,target,reason=row.get("disposition"),row.get("final_item_id"),row.get("reason")
        if kind not in CATEGORIES: errors.append("INVALID_DISPOSITION")
        if not isinstance(reason,str): errors.append("INVALID_RATIONALE")
        if kind in ("Retained","Merged"):
            if not isinstance(target,str) or target not in items:errors.append("MISSING_OR_NONACTIONABLE_FINAL_ITEM")
        elif target is not None: errors.append("UNEXPECTED_FINAL_ITEM")
        if kind=="Excluded" and (not isinstance(reason,str) or not reason.strip()):errors.append("EXCLUSION_REASON_REQUIRED")
        if errors:problems.append({"row":n,"problems":errors})
        for i in set(ids)&known:by_id[i].append((n,row,errors))
    entries=[]
    for cid in expected:
        records=by_id[cid]; errors=[]
        if record.get("parse_error"): errors.append(record["parse_error"])
        if not records:errors.append("MISSING_DISPOSITION")
        if len(records)>1:errors.append("DUPLICATE_OR_CONTRADICTORY_MAPPING")
        for _,_,e in records:errors.extend(e)
        row=records[0][1] if len(records)==1 else None
        valid=bool(row) and not errors
        item=items.get(row.get("final_item_id")) if valid else None
        entries.append({"candidate_id":cid,"model_reported_disposition":row.get("disposition") if row else None,
            "model_reported_rationale":row.get("reason") if row else None,
            "reported_records":[r for _,r,_ in records],
            "application_disposition":row["disposition"] if valid else "Unresolved",
            "structural_validation":"VALID" if valid else "INVALID_OR_MISSING",
            "final_item_id":item.label if item else None,"final_item_text":item.text if item else None,
            "problems":list(dict.fromkeys(errors)),"substantive_preservation":"NOT_INDEPENDENTLY_VERIFIED",
            "semantic_review_required": bool(valid and item)})
    return {"authority":"Model-reported decisions; application checks structure and identity only. No semantic verification.",
            "candidate_mappings":entries,"row_problems":problems,
            "native_record":record,"scope":"final_synthesis_before_source_verification",
            "model_reported_counts":{**{k:sum(e["model_reported_disposition"]==k for e in entries) for k in CATEGORIES},
                                     "unreported_or_ambiguous":sum(e["model_reported_disposition"] not in CATEGORIES for e in entries)},
            "application_counts":{k:sum(e["application_disposition"]==k for e in entries) for k in CATEGORIES}}


# Written by review_pipeline.merge_reports on the last line of every item it
# appends from a later synthesis pass. It is the merge's own record that the
# item is a verbatim copy of a later-pass item; it carries no claim about
# meaning.
MERGE_ADDITION_MARKER = "* Found only in a later pass."


def final_correspondence(pass_text, final_items, later_pass):
    """Where a pass-local item's exact recorded text is in the final report.

    Identity is accepted only for a verbatim copy: the same complete text, or,
    for a later pass, the same complete text followed by the merge's addition
    marker and nothing else. Numbering, titles and word overlap are never used,
    so an item that merge_reports discarded as overlapping an existing item
    (a lexical decision) has no final correspondence here.
    Returns (basis, [matching final items]).
    """
    target = canonical(pass_text)
    verbatim = [i for i in final_items if canonical(i.text) == target]
    added = []
    if later_pass:
        for i in final_items:
            lines = (i.text or "").rstrip().splitlines()
            if (len(lines) > 1 and lines[-1].strip() == MERGE_ADDITION_MARKER
                    and canonical("\n".join(lines[:-1])) == target):
                added.append(i)
    matches = verbatim + [i for i in added if i not in verbatim]
    if len(matches) > 1:
        return "AMBIGUOUS_MULTIPLE_VERBATIM_MATCHES", matches
    if not matches:
        return "NOT_IN_FINAL_REPORT", []
    if added and matches[0] in added:
        return "VERBATIM_LATER_PASS_ADDITION", matches
    return ("VERBATIM_BASE_ITEM" if not later_pass else "VERBATIM_IDENTICAL_FINAL_ITEM"), matches


CORRESPONDENCE_NOTES = {
    "VERBATIM_BASE_ITEM": "The pass-local item's complete text is in the final report unchanged.",
    "VERBATIM_IDENTICAL_FINAL_ITEM": "The final report contains an item with exactly the same complete text.",
    "VERBATIM_LATER_PASS_ADDITION": "The final report contains this later-pass item verbatim, appended by the merge with its addition marker.",
    "NOT_IN_FINAL_REPORT": ("No final item reproduces this pass-local item's text. The merge keeps the first pass and appends a later-pass "
                            "item only when it judges it unlike every existing item; an item judged similar is discarded. That "
                            "similarity judgement is lexical and is not used as evidence that two items are the same concern."),
    "AMBIGUOUS_MULTIPLE_VERBATIM_MATCHES": "More than one final item reproduces this text; no single correspondence can be established.",
}


def model_mapping_diagnostic(trace):
    """Keep pass-local IDs distinct; never infer a rewritten multi-pass merge."""
    merged=[i for i in sv.extract_items(trace.get("synthesis_accounting_input") or "") if i.kind in ("concern","prompt")]
    result=[]
    for index,stage in enumerate(trace.get("final_synthesis") or []):
        raw=stage.get("provenance_output")
        if raw is None:continue
        report=stage.get("raw","")
        validated=validate_model_mappings(raw,report)
        pass_number=stage.get("pass",index+1)
        for e in validated["candidate_mappings"]:
            e["synthesis_pass"]=pass_number
            e["pass_local_final_item_id"]=e["final_item_id"]
            # The model's mapping checked against its own pass's report.
            e["pass_local_structural_validation"]=e["structural_validation"]
            e["final_correspondence"]=None
            e["final_correspondence_note"]=None
            if e["final_item_id"]:
                basis,same=final_correspondence(e["final_item_text"],merged,later_pass=index>0)
                e["final_correspondence"]=basis
                e["final_correspondence_note"]=CORRESPONDENCE_NOTES[basis]
                if len(same)==1:
                    e["final_item_id"]=same[0].label
                    e["final_item_text"]=same[0].text
                else:
                    e["final_item_id"]=None;e["final_item_text"]=None
                    e["application_disposition"]="Unresolved";e["semantic_review_required"]=False
                    e["structural_validation"]="INVALID_OR_MISSING"
                    e["problems"].append("FINAL_ITEM_CHANGED_OR_AMBIGUOUS_AFTER_PASS")
                    e["problems"].append("PASS_LOCAL_ITEM_NOT_IN_FINAL_REPORT" if not same else "MULTIPLE_VERBATIM_FINAL_MATCHES")
            e["original_candidate"] = next((c for f in trace.get("files") or [] for c in f.get("candidate_findings") or [] if c.get("candidate_id")==e["candidate_id"]),None)
            dispositions=(trace.get("source_verification") or {}).get("dispositions",[])
            e["subsequent_source_verification_outcome"]=next((d.get("outcome") for d in dispositions if d.get("label")==e["final_item_id"]),None)
        validated["application_counts"]={k:sum(e["application_disposition"]==k for e in validated["candidate_mappings"]) for k in CATEGORIES}
        validated["final_correspondence_counts"]={k:sum(e["final_correspondence"]==k for e in validated["candidate_mappings"])
                                                  for k in CORRESPONDENCE_NOTES}
        validated["synthesis_pass"]=pass_number
        result.append(validated)
    return result


# --------------------------------------------------------------------------
# Merge decisions and potential information loss (diagnostic only)
# --------------------------------------------------------------------------
# merge_reports records each decision it makes when given a list
# (trace["merge_decisions"]). Nothing below re-implements or re-scores the
# merge; it attaches identifiers and flags to what the merge recorded.

LOSS_LABEL = "Potential information loss — requires human assessment"
LOSS_DISCLAIMER = (
    "A flag means only that a statistical result written in a discarded item does not occur in the "
    "retained item it was matched to. It is not a finding that anything important was lost, that the "
    "discarded item was correct, or that the retained item is deficient. A statistically significant "
    "baseline difference is not by itself evidence of confounding or bias. Methodological qualifications "
    "and verification questions are not detected automatically: compare the discarded and retained texts.")

_OP = r"(<=|>=|≤|≥|=|<|>)"
_NUM = r"([-−]?\d*\.\d+|[-−]?\d+)"
_P_VALUE = re.compile(r"(?<![A-Za-z])p\s*" + _OP + r"\s*" + _NUM, re.I)
# Named test statistics and estimates only; a bare number is never a result.
_STATISTIC = re.compile(
    r"(?<![A-Za-z0-9])(χ\s*²|χ\s*2|chi[-\s]?squared?|chi2|η\s*²|η\s*2|R\s*²|R2|OR|RR|HR|β|t|F|z|r|H|U|W|d|g)"
    r"\s*(\(\s*[\d.,\s]+\))?\s*" + _OP + r"\s*" + _NUM)
_STAT_NAMES = {"χ²": "chi2", "χ2": "chi2", "chi2": "chi2", "chisquare": "chi2", "chisquared": "chi2",
               "chi-square": "chi2", "chi-squared": "chi2", "η²": "eta2", "η2": "eta2", "R²": "R2"}


def _num(value):
    from decimal import Decimal, InvalidOperation
    value = value.replace("−", "-")
    try:
        return format(Decimal(value).normalize(), "f")
    except InvalidOperation:
        return value


def _op(op):
    return {"≤": "<=", "≥": ">="}.get(op, op)


def statistical_results(text):
    """Statistical results written in an item: a p-value, a named statistic or
    estimate, or a statistic immediately followed by its p-value (one result).
    Each carries comparison keys that ignore spacing and number formatting."""
    text = text or ""
    ps = [(m.start(), m.end(), ("p", _op(m.group(1)), _num(m.group(2)))) for m in _P_VALUE.finditer(text)]
    stats = []
    for m in _STATISTIC.finditer(text):
        name = re.sub(r"\s+", "", m.group(1))
        name = _STAT_NAMES.get(name, _STAT_NAMES.get(name.lower(), name))
        stats.append((m.start(), m.end(), (name, _op(m.group(3)), _num(m.group(4)))))
    results, used = [], set()
    for start, end, key in stats:
        follow = next((p for p in ps if p[0] >= end and p[0] - end <= 25
                       and re.fullmatch(r"[\s,;]*", text[end:p[0]])), None)
        keys = [key] + ([follow[2]] if follow else [])
        stop = follow[1] if follow else end
        if follow:
            used.add(follow[0])
        results.append({"text": text[start:stop], "keys": keys, "start": start})
    results += [{"text": text[a:b], "keys": [k], "start": a} for a, b, k in ps if a not in used]
    results.sort(key=lambda r: r["start"])
    for r in results:
        lo = text.rfind("\n", 0, r["start"]) + 1
        hi = text.find("\n", r["start"])
        r["line"] = text[lo:hi if hi >= 0 else len(text)].strip()
    return results


def _keys_in(text):
    return {k for r in statistical_results(text) for k in r["keys"]}


def information_loss_flags(discarded_text, retained_text, final_items):
    """Results in a discarded item absent from the retained item it was matched to."""
    retained = _keys_in(retained_text)
    flags = []
    for result in statistical_results(discarded_text):
        if any(k in retained for k in result["keys"]):
            continue          # the same result (or its p-value) is in the retained item
        elsewhere = [i.label for i in final_items if any(k in _keys_in(i.text) for k in result["keys"])]
        p_keys = [k for k in result["keys"] if k[0] == "p"]
        if len(result["keys"]) > 1:
            kind = "test statistic with p-value"
        elif p_keys and p_keys[0][1] != "=":
            kind = "p-value inequality (may only restate significance or non-significance)"
        elif p_keys:
            kind = "exact p-value"
        else:
            kind = "named statistic or estimate"
        flags.append({
            "label": LOSS_LABEL,
            "result_kind": kind,
            "potentially_missing_detail": result["text"],
            "line_in_discarded_item": result["line"],
            "basis": ("Statistical result written in the discarded item; neither it nor any value in the same "
                      "result occurs in the retained item it was matched to (comparison ignores spacing and "
                      "number formatting, not meaning)."),
            "present_elsewhere_in_final_actionable_items": elsewhere,
        })
    return flags


def _unique_label(text, items):
    same = [i.label for i in items if canonical(i.text) == canonical(text)]
    return same[0] if len(same) == 1 else None


def merge_decision_diagnostic(trace):
    """The merge's own recorded decisions, with identifiers and flags attached.

    Returns None when the review recorded no merge decisions (older reviews).
    Never raises: a malformed record is reported, not repaired.
    """
    raw = trace.get("merge_decisions")
    if raw is None:
        return None
    out = {"authority": ("Recorded merge decisions are what merge_reports did. Potential information-loss flags are "
                         "a deterministic signal for human assessment, not a judgement of substantive omission."),
           "disclaimer": LOSS_DISCLAIMER, "decisions": [], "flags": [], "problems": []}
    if not isinstance(raw, list):
        out["problems"].append("MALFORMED_MERGE_DECISIONS")
        return out
    try:
        final_items = [i for i in sv.extract_items(trace.get("synthesis_accounting_input") or "")
                       if i.kind in ("concern", "prompt")]
    except Exception:
        final_items = []
        out["problems"].append("FINAL_REPORT_UNAVAILABLE")
    pass_items = {}
    for n, stage in enumerate(trace.get("final_synthesis") or []):
        if isinstance(stage, dict):
            text = stage.get("validated", stage.get("raw")) or ""
            pass_items[stage.get("pass", n + 1)] = [i for i in sv.extract_items(text) if i.kind in ("concern", "prompt")]

    def final_id(text, later):
        basis, same = final_correspondence(text, final_items, later_pass=later)
        return (same[0].label if len(same) == 1 else None), basis

    for n, d in enumerate(raw):
        try:
            entry = {
                "synthesis_pass": d["pass"], "section": d["section"], "merge_index": d["index"],
                "pass_local_item_id": _unique_label(d["text"], pass_items.get(d["pass"], [])),
                "original_text": d["text"], "decision": d["decision"], "basis": d.get("basis"),
                "matched_item": None, "score": d.get("score"), "highest_score": d.get("highest_score"),
                "threshold": d.get("threshold"), "shared_words": d.get("shared_words"),
                "comparisons": d.get("comparisons"), "final_item_id": None, "final_correspondence": None,
            }
            if d["decision"] in ("retained", "added"):
                entry["final_item_id"], entry["final_correspondence"] = final_id(d["text"], d["decision"] == "added")
            if d["decision"] == "discarded":
                m = d["matched"]
                later = m["pass"] != (raw[0].get("pass") if raw else 1)
                mid, mbasis = final_id(m["text"], later)
                entry["matched_item"] = {"synthesis_pass": m["pass"], "merge_index": m["index"],
                                         "pass_local_item_id": _unique_label(m["text"], pass_items.get(m["pass"], [])),
                                         "final_item_id": mid, "final_correspondence": mbasis,
                                         "title": m.get("title"), "text": m["text"]}
                for flag in information_loss_flags(d["text"], m["text"], final_items):
                    flag.update(discarded_item={"synthesis_pass": d["pass"], "pass_local_item_id": entry["pass_local_item_id"],
                                                "merge_index": d["index"], "section": d["section"]},
                                matched_retained_item={"synthesis_pass": m["pass"], "final_item_id": mid,
                                                       "pass_local_item_id": entry["matched_item"]["pass_local_item_id"]})
                    out["flags"].append(flag)
            out["decisions"].append(entry)
        except Exception as exc:   # reported, never repaired
            out["problems"].append(f"MALFORMED_DECISION_{n}: {type(exc).__name__}")
    out["counts"] = {k: sum(e["decision"] == k for e in out["decisions"])
                     for k in ("retained", "added", "discarded", "not_considered")}
    return out


def build(trace, review_id, provenance=None):
    """Pure deterministic projection of recorded data; never mutates the input.

    Optional recorded mappings are read, not generated. No current production
    stage emits these. Rewritten interpretations remain Unresolved unless their
    preservation is mechanically demonstrable; a recorded merge label alone
    does not establish preservation of methodological meaning.
    """
    final = trace.get("synthesis_accounting_input")
    if final is None:
        passes = trace.get("final_synthesis") or []
        final = passes[0].get("raw", "") if len(passes) == 1 else ""
    items = {i.label: i for i in sv.extract_items(final or "") if i.kind in ("concern", "prompt")}
    limits = []
    if not final:
        limits.append("Final synthesis text unavailable or multiple passes lack a recorded merged input.")
    entries, contexts = [], []
    if not trace.get("files"):
        limits.append("File-level records unavailable; high-priority coverage cannot be established.")
    links = trace.get("synthesis_concern_dispositions") or []
    for file_index, f in enumerate(trace.get("files") or []):
        source = f.get("source_name")
        concerns = bullets(f.get("file_summary"), "strongly supported concerns")
        context = {"source_document": source, "file_synthesis_concerns": concerns,
                   "record_ref": f"/files/{file_index}/file_summary"}
        contexts.append(context)
        themes = (f.get("candidate_triage") or {}).get("themes")
        if themes is None:
            limits.append(f"{source}: triage priorities unavailable; high-priority coverage cannot be established.")
            themes = []
        if not concerns:
            limits.append(f"{source}: file-synthesis concerns unavailable.")
        candidates = {c.get("candidate_id"): c for c in f.get("candidate_findings") or []}
        for theme_index, theme in enumerate(themes):
            if theme.get("priority") != "high":
                continue
            ids = list(theme.get("candidate_ids") or [])
            original = [dict(candidates[i]) for i in ids if i in candidates]
            entry = dict(candidate_ids=ids, source_document=source,
                         original_concerns=original, theme=dict(theme), priority="high",
                         disposition="Unresolved", final_item_id=None, recorded_reason=None,
                         file_synthesis_representation=None, file_retention="Unresolved",
                         diagnostic_basis="No explicit disposition or complete verbatim correspondence established.",
                         record_refs=[f"/files/{file_index}/candidate_triage/themes/{theme_index}",
                                      f"/files/{file_index}/candidate_findings",
                                      context["record_ref"]], observed_mapping=None)
            if not ids or len(original) != len(ids):
                entry["diagnostic_basis"] = "Candidate records or identifiers missing; no disposition inferred."
                entries.append(entry)
                continue
            recorded = [x for x in links if x.get("source_document") == source
                        and set(x.get("candidate_ids") or []) == set(ids)]
            if len(recorded) == 1:
                link = recorded[0]
                entry["observed_mapping"] = dict(link)
                text = link.get("file_concern_text") or ""
                matching = [c for c in concerns if canonical(c) == canonical(text)] if text else []
                if len(matching) == 1 and link.get("record_ref"):
                    entry.update(file_synthesis_representation=matching[0], file_retention="Explicitly bound")
                    kind, target = link.get("disposition"), items.get(link.get("target_item_id"))
                    if kind == "Excluded" and str(link.get("reason") or "").strip():
                        entry.update(disposition="Excluded", recorded_reason=link["reason"],
                                     diagnostic_basis="Explicit recorded exclusion and rationale; rationale not academically verified.")
                    elif (kind in ("Retained", "Merged") and target
                          and preserves(text, target, kind == "Merged")
                          and (kind != "Merged" or str(link.get("reason") or "").strip())):
                        entry.update(disposition=kind, final_item_id=target.label,
                                     recorded_reason=link.get("reason"),
                                     diagnostic_basis="Recorded mapping plus complete verbatim file-concern text in actionable item.")
                    else:
                        entry["diagnostic_basis"] = "Recorded mapping is incomplete or substantive preservation cannot be verified without semantic judgement."
                else:
                    entry["diagnostic_basis"] = "Recorded mapping lacks a unique file-concern binding or provenance reference."
            elif len(recorded) > 1:
                entry["diagnostic_basis"] = "Conflicting/multiple recorded dispositions; not resolved automatically."
            else:
                # Without a mapping, accept only identical complete observation
                # text throughout, and only when all theme members say that same
                # thing. Do not use one member as a proxy for a broader theme.
                bodies = {canonical(c.get("text")) for c in original}
                matching = [c for c in concerns if canonical(c) in bodies] if len(bodies) == 1 else []
                if len(matching) == 1:
                    text = matching[0]
                    entry.update(file_synthesis_representation=text, file_retention="Complete verbatim observation")
                    targets = [i for i in items.values() if preserves(text, i)]
                    if len(targets) == 1:
                        entry.update(disposition="Retained", final_item_id=targets[0].label,
                                     diagnostic_basis="Complete verbatim observation in file synthesis and one actionable final item.")
            entries.append(entry)
    if any(e["file_retention"] == "Unresolved" for e in entries):
        limits.append("All high-priority triage themes are included conservatively. File-synthesis membership is unconfirmed where no explicit or complete verbatim binding exists; the denominator is not a confirmed retained-concern count.")
    return dict(title=TITLE, version=2, review_id=review_id, authority=DISCLAIMER,
                model_reported_provenance=model_mapping_diagnostic(trace),
                merge_decisions=merge_decision_diagnostic(trace),
                provenance=provenance or {}, entries=entries, file_contexts=contexts,
                actionable_final_items=[dict(id=i.label, kind=i.kind, text=i.text) for i in items.values()],
                non_actionable_confidence_commentary=bullets(final, "overall confidence"),
                existing_candidate_accounting=trace.get("candidate_accounting"),
                counts={"high_priority_themes_examined": len(entries),
                        **{k: sum(e["disposition"] == k for e in entries) for k in CATEGORIES}},
                limitations=limits)


def markdown(record):
    c = record["counts"]
    lines = ["# " + TITLE, "", DISCLAIMER, "", f"Review: {record['review_id']}", "",
             f"High-priority triage themes examined: {c['high_priority_themes_examined']}",
             " · ".join(f"{k}: {c[k]}" for k in CATEGORIES), "", "## Limitations", ""]
    lines += ["- " + s for s in record["limitations"]] or ["No missing-input limitations recorded."]
    lines += ["", "## Unresolved observations", ""]
    for e in record["entries"]:
        if e["disposition"] != "Unresolved":
            continue
        lines += ["### " + e["theme"].get("theme", "Untitled observation"), "",
                  "Candidate IDs: " + ", ".join(e["candidate_ids"]), "",
                  "Source: " + str(e["source_document"]), "",
                  "Diagnostic basis: " + e["diagnostic_basis"], "",
                  "File-synthesis binding: " + e["file_retention"], ""]
        lines += [c.get("text", "") + "\n" for c in e["original_concerns"]]
    lines += ["## Recorded file-synthesis context (not inferred candidate mappings)", ""]
    for context in record["file_contexts"]:
        lines += ["### " + str(context["source_document"]), ""] + context["file_synthesis_concerns"] + [""]
    lines += ["## Non-actionable confidence commentary (does not count as retention)", ""]
    lines += record["non_actionable_confidence_commentary"]
    if record.get("model_reported_provenance"):
        lines += ["", "## Model-reported dispositions — structural validation only", "",
                  "Neither model-reported disposition nor valid structural correspondence verifies methodological meaning. Legacy theme accounting above remains separate.", ""]
        for stage in record["model_reported_provenance"]:
            lines += [f"### Synthesis pass {stage['synthesis_pass']}", "",
                      "Model-reported counts: " + json.dumps(stage["model_reported_counts"]),
                      "Application dispositions after structural checks: " + json.dumps(stage["application_counts"]),
                      "Final-report correspondence (verbatim text only): " + json.dumps(stage.get("final_correspondence_counts", {})), ""]
            for e in stage["candidate_mappings"]:
                lines += [f"- Candidate: {e['candidate_id']}",
                          f"  - Model-reported: {e['model_reported_disposition']}; rationale: {e['model_reported_rationale']}",
                          f"  - Application disposition: {e['application_disposition']}; structural validation: {e['structural_validation']}",
                          f"  - Target: {e['final_item_id']}; pass-local target: {e['pass_local_final_item_id']} "
                          f"(pass-local structural validation: {e.get('pass_local_structural_validation')})",
                          f"  - Final-report correspondence: {e.get('final_correspondence') or 'not applicable'}"
                          + (f" — {e['final_correspondence_note']}" if e.get('final_correspondence_note') else ""),
                          f"  - Problems: {', '.join(e['problems']) or 'none'}; substantive preservation: NOT INDEPENDENTLY VERIFIED.",
                          "  - Original observation: " + str((e.get("original_candidate") or {}).get("text", "unavailable"))]
            if stage["row_problems"]: lines += ["Row validation problems: " + json.dumps(stage["row_problems"])]
    md = record.get("merge_decisions")
    if md:
        lines += ["", "## Recorded merge decisions", "", md["authority"], ""]
        if md.get("problems"): lines += ["Problems: " + ", ".join(md["problems"]), ""]
        lines += ["Counts: " + json.dumps(md.get("counts", {})), ""]
        for e in md["decisions"]:
            lines += [f"- Pass {e['synthesis_pass']} {e['pass_local_item_id'] or '(pass-local id not established)'} "
                      f"({e['section']}): **{e['decision']}**"
                      + (f"; final item {e['final_item_id']}" if e.get("final_item_id") else "")]
            if e["decision"] == "discarded":
                m = e["matched_item"]
                lines += [f"  - Matched to pass {m['synthesis_pass']} {m['pass_local_item_id'] or '?'} "
                          f"(final {m['final_item_id'] or 'not established'}); score {e['score']:.3f} against threshold {e['threshold']}",
                          f"  - Shared words: {', '.join(e['shared_words'] or [])}",
                          "  - Discarded text:", "", "    " + e["original_text"].replace("\n", "\n    "), "",
                          "  - Retained text it was matched to:", "", "    " + m["text"].replace("\n", "\n    "), ""]
            elif e["decision"] == "added":
                lines += [f"  - Highest score {e['highest_score'] if e['highest_score'] is not None else 'n/a'} against threshold {e['threshold']}"]
        lines += ["", "## " + LOSS_LABEL, "", md["disclaimer"], ""]
        if not md["flags"]:
            lines += ["No statistical result in a discarded item is absent from the retained item it was matched to.", ""]
        for f in md["flags"]:
            di, ri = f["discarded_item"], f["matched_retained_item"]
            lines += [f"- {f['label']}: `{f['potentially_missing_detail']}` ({f['result_kind']})",
                      f"  - Discarded item: pass {di['synthesis_pass']} {di['pass_local_item_id'] or '?'}; matched to final item {ri['final_item_id'] or 'not established'}",
                      f"  - Line: {f['line_in_discarded_item']}",
                      f"  - Basis: {f['basis']}",
                      f"  - Also present in final actionable items: {', '.join(f['present_elsewhere_in_final_actionable_items']) or 'none'}"]
    return "\n".join(lines) + "\n"


def publish(trace, review_id, provenance=None, root=None):
    """Write a separate, content-addressed diagnostic; never overwrite evidence."""
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,100}", review_id):
        raise ValueError("Invalid diagnostic review identifier")
    record = build(trace, review_id, provenance)
    data = json.dumps(record, ensure_ascii=False, sort_keys=True, indent=2).encode()
    digest = hashlib.sha256(data).hexdigest()
    base = Path(root) if root else Path(os.environ.get("QWEN_SYNTHESIS_ACCOUNTING_DIR") or Path(__file__).resolve().parents[1]/"local_results"/"review-synthesis-accounting")
    parent = base/review_id
    parent.mkdir(parents=True, exist_ok=True)
    dest = parent/digest
    outputs = {"SYNTHESIS-CONCERN-ACCOUNTING.json": data,
               "SYNTHESIS-CONCERN-ACCOUNTING.md": markdown(record).encode()}
    if dest.exists():
        if any(not (dest/n).is_file() or (dest/n).read_bytes() != b for n,b in outputs.items()):
            raise ValueError("Existing diagnostic differs; refusing overwrite")
        return dest
    import shutil
    tmp = Path(tempfile.mkdtemp(prefix=".accounting-", dir=parent))
    try:
        for name, content in outputs.items():
            with (tmp/name).open("xb") as f:
                f.write(content); f.flush(); os.fsync(f.fileno())
        tmp.rename(dest)
    finally:
        if tmp.exists(): shutil.rmtree(tmp)
    return dest
