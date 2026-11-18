"""
Source-grounded verification of a merged review, item by item.

Replaces whole-report regeneration at validation. The old validator was given
the review and the pipeline's own file summary, and asked to return a revised
report. It could not see the manuscript, so a misreading made at chunk level
was checked against the summary that carried it; and because it rewrote the
whole report, a legitimate concern could disappear with no record.

This module does three things differently:

1. It runs once, after the passes are merged, so overlapping items from
   different passes are in front of the verifier together.
2. The verifier is given the manuscript text itself -- the whole of it when it
   fits the prompt budget, otherwise passages retrieved for each item -- and
   returns a disposition per item, not a report.
3. The application, not the model, applies the dispositions, and it keeps
   every item. A "reject" verdict is shown beneath the item as the model's
   objection; it never removes it, because a quotation that exists in the
   manuscript does not show that the model read it correctly or that it bears
   on the item. The only removal is a duplicate merged into an item that
   remains, with its text kept in the record. A missing answer, an
   unlocatable quotation, a retrieval shortfall or a failed call leaves the
   item in place, recorded as unassessed or unresolved.

The report keeps three things apart: what the model said (a verdict), what
the application checked (that a quotation occurs verbatim and contiguously in
the manuscript), and what the application established independently (only
the deterministic checks, reported elsewhere).

What it cannot do, stated so nobody relies on it for these:

- It checks only items that reached the merged report. A concern dropped at
  file synthesis is not recovered here; account_candidates() lists such
  candidates for the human reader instead, without judging them.
- It cannot read figures, and extracted table text may be misaligned, so it is
  told to leave anything that depends on either unresolved. Numerical
  consistency of tables is handled by the deterministic checks in
  manuscript_checks, not by this step.
- Duplicate detection is the model's judgement; the removed duplicate is kept
  verbatim in the record so a wrong merge can be seen.
- A located quotation establishes that the sentence exists, not that the
  verifier read it correctly.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import review_pipeline as rp
import evidence_availability as ea
import llm_backend


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

def enabled() -> bool:
    """On unless QWEN_SOURCE_VERIFICATION is 0/false/off (legacy validation)."""
    value = os.environ.get("QWEN_SOURCE_VERIFICATION", "1").strip().lower()
    return value not in {"0", "false", "no", "off", "legacy"}


VERDICTS = ("supported", "correct", "duplicate", "reject", "unresolved")
# Optional evidence passages (schema extension, version 2). The role is the
# verifier's assessment of how the passage bears on the review item; it is not
# established by the application. Each passage is checked like "quote".
EVIDENCE_ROLES = ("supports", "qualifies", "contradicts")
MAX_EVIDENCE_PASSAGES = 3
# A quotation shorter than this can be found almost anywhere ("the model"),
# so it cannot carry a correction or a removal.
MIN_QUOTE_WORDS = 6
# Two items the verifier calls duplicates must share at least this share of
# content words (of the shorter item). It only stops a merge of items with
# nothing in common; it is deliberately far below SAME_ITEM_OVERLAP.
DUPLICATE_MIN_OVERLAP = 0.25
# Candidate accounting: share of a candidate's content words that must appear
# in one final item for the candidate to count as reflected there.
CANDIDATE_MATCH = 0.5
# Below the match threshold, the nearest item is still named when the overlap
# reaches this, so a reader can see a likely counterpart the matcher missed.
NEAREST_HINT = 0.3
_SECTION_ORDER = ("statistical / methodological concerns", "table-specific notes",
                  "questions raised by this chunk", "missing or unclear")
MAX_ITEMS = 30


# ---------------------------------------------------------------------------
# Items
# ---------------------------------------------------------------------------

_STRENGTH_RE = re.compile(r"^\s*[-*]?\s*\**\s*Strength\**\s*:", re.I)
_BULLET_RE = re.compile(r"^\s*[-*]\s+\S")
_SECTIONS = (
    ("major strengths", "strength", "S", _STRENGTH_RE),
    ("directly supported concerns", "concern", "C", rp._CONCERN_RE),
    ("verification prompts", "prompt", "P", rp._CHECK_RE),
)
KIND_NAMES = {"strength": "Strength", "concern": "Concern", "prompt": "Verification prompt"}


@dataclass
class Item:
    label: str
    kind: str
    start: int          # line index in the report, inclusive
    end: int            # line index in the report, exclusive
    text: str

    @property
    def title(self) -> str:
        first = self.text.splitlines()[0] if self.text else ""
        first = re.sub(r"^\s*[-*]?\s*\**\s*(?:Strength|Concern|Check)\**\s*:\**\s*", "", first, flags=re.I)
        first = re.split(r"\s*\**\s*(?:Evidence|Reason|Why it matters|Severity)\s*\**\s*:", first)[0]
        first = first.strip(" *")
        return first if len(first) <= 110 else first[:107].rstrip() + "..."


def _section_bounds(lines: List[str], name: str) -> Optional[Tuple[int, int]]:
    bounds = None
    for index, line in enumerate(lines):
        heading = rp._HEADING_RE.match(line)
        if not heading:
            continue
        if heading.group(1).strip().strip("*").strip().lower().startswith(name):
            bounds = [index + 1, len(lines)]
        elif bounds and bounds[1] == len(lines):
            bounds[1] = index
            break
    return tuple(bounds) if bounds else None


def extract_items(report_text: str) -> List[Item]:
    """Strengths, concerns and verification prompts, in report order."""
    lines = (report_text or "").splitlines()
    items: List[Item] = []
    for name, kind, prefix, marker in _SECTIONS:
        bounds = _section_bounds(lines, name)
        if not bounds:
            continue
        start, stop = bounds
        starts = [i for i in range(start, stop) if marker.match(lines[i])]
        if not starts and kind == "strength":
            # Strengths are sometimes plain bullets with no "Strength:" label.
            starts = [i for i in range(start, stop) if _BULLET_RE.match(lines[i])]
        for n, begin in enumerate(starts):
            end = starts[n + 1] if n + 1 < len(starts) else stop
            while end > begin + 1 and not lines[end - 1].strip():
                end -= 1
            text = "\n".join(l for l in lines[begin:end] if l.strip())
            items.append(Item(f"{prefix}{n + 1}", kind, begin, end, text))
    return items[:MAX_ITEMS]


# ---------------------------------------------------------------------------
# Source packet
# ---------------------------------------------------------------------------

def _render_sources(sources: Dict[str, str]) -> str:
    if len(sources) == 1:
        return next(iter(sources.values()))
    return "\n\n".join(f"=== Source: {name} ===\n{body}" for name, body in sources.items())


def build_source_packet(items: Sequence[Item], sources: Dict[str, str],
                        budget: int) -> Tuple[str, str, int]:
    """
    The manuscript text to give the verifier.

    Returns (packet, scope, characters omitted). Scope is "complete" when every
    source was supplied whole, "excerpts" when passages were retrieved per
    item. In excerpt mode absence is never evidence, and the prompt says so.
    """
    whole = _render_sources(sources)
    if len(whole) <= budget:
        return whole, "complete", 0
    per_item = max(1500, budget // max(1, len(items)))
    chosen: Dict[Tuple[str, int], Tuple[str, Optional[int], str]] = {}
    order: List[Tuple[str, int]] = []
    # Index blocks once so passages keep their manuscript order.
    blocks = [(name, page, body) for name, text in sources.items()
              for page, body in rp._qa_blocks(text)]
    position = {(name, body): i for i, (name, _p, body) in enumerate(blocks)}
    used = 0
    for item in items:
        for name, page, body in rp.select_source_passages(item.text, sources, per_item):
            key = (name, position.get((name, body), -1))
            if key in chosen:
                continue
            cost = len(body) + len(name) + 40
            if used + cost > budget:
                continue
            chosen[key] = (name, page, body)
            order.append(key)
            used += cost
    rendered = []
    for key in sorted(order, key=lambda k: (list(sources).index(k[0]), k[1])):
        name, page, body = chosen[key]
        where = f"Page {page}" if page is not None else "Page unknown"
        rendered.append(f"[{name}; {where}]\n{body}" if len(sources) > 1 else f"[{where}]\n{body}")
    total = sum(len(t) for t in sources.values())
    return "\n\n---\n\n".join(rendered), "excerpts", max(0, total - used)


# ---------------------------------------------------------------------------
# Prompt and schema
# ---------------------------------------------------------------------------

def output_schema(labels: Sequence[str]) -> dict:
    labels = list(labels)
    return {
        "type": "object",
        "properties": {
            "items": {
                "type": "array",
                "minItems": len(labels),
                "maxItems": len(labels),
                "items": {
                    "type": "object",
                    "properties": {
                        "label": {"type": "string", "enum": labels},
                        "quote": {"type": "string", "maxLength": 600},
                        "reason": {"type": "string", "minLength": 1, "maxLength": 500},
                        "verdict": {"type": "string", "enum": list(VERDICTS)},
                        "correction": {"type": "string", "maxLength": 400},
                        "surviving_point": {"type": "string", "maxLength": 400},
                        "duplicate_of": {"type": "string", "enum": [""] + labels},
                        # Version 2 fields. Required in the response so the
                        # grammar always emits them, but they may be empty;
                        # records without them (version 1) remain valid.
                        "reviewer_check": {"type": "string", "maxLength": 300},
                        "evidence": {
                            "type": "array",
                            "maxItems": MAX_EVIDENCE_PASSAGES,
                            "items": {
                                "type": "object",
                                "properties": {
                                    "quote": {"type": "string", "minLength": 1, "maxLength": 600},
                                    "role": {"type": "string", "enum": list(EVIDENCE_ROLES)},
                                },
                                "required": ["quote", "role"],
                                "additionalProperties": False,
                            },
                        },
                    },
                    "required": ["label", "quote", "reason", "verdict",
                                 "correction", "surviving_point", "duplicate_of",
                                 "reviewer_check", "evidence"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["items"],
        "additionalProperties": False,
    }


def build_prompt(items: Sequence[Item], packet: str, scope: str,
                 unexamined: Sequence[str] = (),
                 automated_flags: Sequence[str] = (),
                 primary_source: str = "") -> str:
    listed = "\n\n".join(f"[{item.label}] {KIND_NAMES[item.kind]}\n{item.text}" for item in items)
    if scope == "complete":
        scope_note = ("You have the complete extracted text of the manuscript"
                      + (" and its supplements" if primary_source else "") + ". "
                      "If the text does not mention something, say so in the reason, "
                      "but extraction can lose material, so an absence alone is not "
                      "grounds for reject.")
    else:
        scope_note = ("You have EXCERPTS only, retrieved for each item; the rest of the "
                      "manuscript was not supplied. Something missing from the excerpts "
                      "may still be in the manuscript. Never use reject or correct "
                      "because a passage is missing; use unresolved.")
    figure_note = ""
    if unexamined:
        figure_note = ("\nThese figures were NOT read; only their captions are in the text: "
                       + "; ".join(unexamined) + ". Any item whose truth depends on what a "
                       "figure shows is unresolved.")
    flag_note = ""
    if automated_flags:
        flag_note = ("\nAutomated flags raised by the application about the draft. They are "
                     "pointers to check against the manuscript, not findings:\n"
                     + "\n".join(f"- {flag}" for flag in automated_flags))
    primary_note = (f"\nThe manuscript under review is {primary_source}; the other sources "
                    "are its supplements." if primary_source else "")
    return f"""You are checking the items of a draft peer-review memo against the manuscript itself.
Earlier stages read the manuscript in pieces and summarised it; their summaries can contain
misreadings and conclusions that go further than the evidence. Check each item against the
manuscript text below: both its facts and the methodological conclusion it draws from them.
{scope_note}{primary_note}{figure_note}

First, before judging any single item, compare the complete set of items with one another and
identify substantive duplicates: items that ask essentially the same methodological question,
even when worded differently or illustrated with different examples. For example, "was age
modelled non-linearly?", "were spline terms included for age?" and "was a polynomial age term
used?" ask the same question. Items that concern the same variable or model but ask different
things are distinct and stay separate: "was age modelled non-linearly?" and "was an age × sex
interaction included?" are different questions. For each group of duplicates, keep the most
informative formulation (the most specific, or the one carrying the stronger evidence), give it
its own verdict, and mark each other member duplicate, with duplicate_of naming the kept item.
If a member carries a substantive point the kept item lacks, do not mark it duplicate.

Then work through four questions for every item that is not a duplicate.

A. Factual premise. Does the manuscript explicitly state the facts the item relies on? Separate
   what the manuscript reports from what the reviewer infers from it.

B. Methodological inference. Does that evidence justify the item's conclusion? A passage that
   confirms a premise does not confirm the conclusion drawn from it. Check in particular:
   - Comparability of models. The same measured variables or predictor set does not mean the same
     specification. Before accepting that compared models differ in only one respect, read every
     model's specification and compare interaction terms, parameterisation, and whether models are
     fitted separately, pooled or jointly.
   - Interaction terms and parameterisation: which terms each model contains, and whether a claim
     about them matches every statement of that model in the manuscript.
   - Functional form. "Linear" in "linear model", "linear mixed model" or "linear regression"
     means linear in the parameters; such models can include polynomial terms, spline bases and
     other non-linear transformations of a predictor. Distinguish three situations: (1) the
     manuscript explicitly says a predictor enters linearly; (2) it explicitly names non-linear
     terms for it (splines, polynomials, transformations); (3) it does not describe the
     functional form. In (3) the specification needs clarification; do not conclude that
     non-linear terms were absent, and do not treat a question about it as already answered.
   - Silence is not absence. That a manuscript does not mention a term, transformation or
     procedure does not show it was not used; it shows only that it is not reported.
   - Confounding. A list of covariates does not show that confounding is adequately controlled;
     consider unmeasured or structural alternative explanations.
   - Uncertainty. Overlapping marginal confidence intervals do not establish equivalence or the
     absence of a difference; that needs a direct (for example paired) contrast, or an equivalence
     analysis with a stated margin, depending on the claim. A non-significant difference is not
     evidence of no difference.
   - Rigour and reproducibility. A statement that a procedure was used (nested cross-validation,
     blinding, preregistration) shows that it was intended and reported, not that every
     implementation detail was correct (for example that preprocessing and tuning were confined to
     the training folds).

C. Existing acknowledgement. Does the manuscript already acknowledge, qualify or address the
   issue? Distinguish three levels: (1) acknowledging a limitation, (2) investigating its
   consequences, (3) demonstrating that it does not materially affect the findings. Only (3)
   resolves a concern. (1) or (2) makes a claim that the authors ignored the issue wrong, but the
   concern itself may still stand.

D. Disposition. Choose one verdict:
- supported: the factual premise AND the conclusion hold, and the item does not misstate how the
  manuscript treats the issue. Never use supported because the premise alone is confirmed. A
  strength is supported only if the manuscript shows what the strength claims, not merely that the
  authors intended or reported a procedure. A verification prompt is supported when it is a
  legitimate question the manuscript does not already answer.
- correct: the ORIGINAL ITEM contains a material factual error, overstatement or misleading
  inference (for example "proves", "demonstrably", "necessarily invalidates", "no difference",
  "the authors ignored"), but a defensible point remains or the item needs qualifying. Mixed items
  belong here: keep the defensible concern and qualify the unsupported assertion. Quote the passage
  that shows the problem, state the qualification in correction (one sentence saying what in the
  item is wrong), and give the defensible point in surviving_point (empty if none). Use correct for
  a verification prompt the manuscript already answers, quoting the answer.
  Do NOT use correct when:
  - the manuscript merely acknowledges the issue: an acknowledged limitation can remain a valid
    criticism, so judge whether the item misstates anything;
  - you could only restate the item more precisely, or your correction would repeat the item's
    substantive claim. If the item's claim stands, use supported.
- reject: the manuscript directly contradicts the item's central premise and nothing of its point
  survives. Quote the contradicting passage.
- duplicate: the item was identified in the first step as asking essentially the same
  methodological question as another item, even if the wording or the examples differ. Give the
  kept item's label in duplicate_of, choosing the more informative formulation as the one kept.
  Items that concern the same variable or model but ask different things are NOT duplicates. If
  the item contains a substantive point the other lacks, do not mark it duplicate.
- unresolved: the text does not settle the item, including anything that depends on figures, on
  table values whose extraction may be garbled, or on material not supplied.

In reason, summarise A to C briefly, in the form "Premise: ...; Inference: ...; Acknowledged: ...".

Quotations:
- quote must be copied exactly from the manuscript text below as ONE contiguous passage of at least
  {MIN_QUOTE_WORDS} words (line breaks may be ignored). Never join passages with "..." or any other
  marker, and never leave words out or add words in brackets. The application checks every
  quotation and discards a correct or reject verdict whose quotation is not one contiguous passage.
- When several passages matter, quote the single most decisive one and mention the others in reason.
- The quotation must support the proposition in your verdict (for correct, the passage showing the
  premise is wrong or the conclusion unsupported), not merely contain related terms.
- If no single passage does this, use unresolved rather than forcing a quotation. Leave quote
  empty only for duplicate or unresolved.

Evidence passages (evidence):
- Up to three passages that a human reviewer needs to see to judge the item, especially when it
  depends on comparing sections (for example two model specifications, or a Methods statement and
  a Results statement). The same quotation rules apply to each: exact, contiguous, at least
  {MIN_QUOTE_WORDS} words, no "..." and no omitted or inserted words.
- Give each passage a role relative to the ORIGINAL REVIEW ITEM's claim, never relative to the
  manuscript's internal consistency. The role is your reading of the passage.
  - supports: the passage bears out what the item claims. For a criticism that correctly reports
    an inconsistency, omission or error in the manuscript, the passage that shows that
    inconsistency SUPPORTS the criticism, even though it shows the manuscript contradicting itself.
  - qualifies: the passage limits, complicates or partly answers the item's claim.
  - contradicts: the passage shows the item's claim is wrong. Example: item "the models differ
    only in pooling strategy"; passage "the Separate model additionally includes group ×
    predictor interaction terms"; role: contradicts.
  - For a strength, supports means the passage shows the claimed quality; contradicts means it
    shows the claim goes too far. For a verification question, supports means the passage shows the
    question is legitimate and open; qualifies or contradicts means the passage partly or fully
    answers it.
- Include the passage given in quote if it is one of them. Use an empty list when no passage is
  relevant or the item is a duplicate. Never invent a passage to fill the list.

Reviewer check (reviewer_check):
- Give one for EVERY substantive item, strengths included: one concise action a human reviewer
  could take to resolve the item. It must name (1) the specific manuscript information to inspect
  (a section, table, figure, model term, procedure or supplement) and (2) the factual or
  methodological question that inspection settles. A strength needs a check of what would have to
  be true for the claimed quality to hold.
- Do not restate the item, do not repeat evidence already quoted, and do not tell the authors to
  rewrite the manuscript; the check is for the reviewer. Examples of the kind wanted:
  "Compare the predictor terms, interaction terms and penalty structures across the compared
  models, and judge whether the performance difference can be attributed to the single factor the
  authors name."
  "Check whether imputation, standardisation and hyperparameter tuning were performed within the
  training folds."
  "Locate a paired confidence interval for the difference in performance; do not infer equivalence
  from overlapping marginal intervals."
  "Check whether the authors only acknowledge the group imbalance or also analyse its influence."
- If you cannot identify a meaningful check, leave reviewer_check empty. Do not invent one.

Other rules:
- Judge whether the evidence supports each item, not whether you would have raised it or how
  important it is.
- If an item says something is missing, absent or unreported and the manuscript reports it, use
  correct and quote where it is reported.
- Read regulations, eligibility rules and inclusion criteria word by word, including their
  direction (younger/older, required/forbidden) and exceptions.
- correction and surviving_point describe only what the manuscript says and what remains of THIS
  item. Never introduce a new criticism, a new number, or a consequence the item did not raise.
- Extracted tables are text; columns can be misaligned. Do not correct or reject an item on the
  strength of a table cell alone.
- Leave correction, surviving_point and duplicate_of empty when they do not apply.
{flag_note}

Items:
\"\"\"
{listed}
\"\"\"

Manuscript text:
\"\"\"
{packet}
\"\"\"
""".strip()


# ---------------------------------------------------------------------------
# Applying dispositions
# ---------------------------------------------------------------------------

@dataclass
class Disposition:
    label: str
    kind: str
    original: str
    verdict: str = ""            # what the verifier proposed ("" if nothing)
    outcome: str = "kept_unassessed"  # what the application did
    reason: str = ""
    quote: str = ""
    quote_located: Optional[bool] = None
    quote_sources: List[str] = field(default_factory=list)
    correction: str = ""
    surviving_point: str = ""
    duplicate_of: str = ""
    note: str = ""
    # Version 2 (optional): the verifier's suggested check and up to three
    # passages, each {"quote", "role", "located", "sources"}; "located" is the
    # application's contiguous check, "role" is the verifier's reading.
    reviewer_check: str = ""
    evidence: List[dict] = field(default_factory=list)

    def as_dict(self) -> dict:
        return dict(self.__dict__)


# What the APPLICATION did. The model's verdict and the quotation check are
# reported in their own columns; none of these labels asserts that the model
# was right.
OUTCOMES = {
    "kept_supported": "kept unchanged",
    "kept_corrected": "kept; model's proposed correction shown beneath it",
    "kept_disputed": "kept; model's objection shown beneath it (not removed)",
    "kept_unresolved": "kept; model could not settle it",
    "kept_unassessed": "kept; no usable model verdict",
    "merged_into": "removed as a duplicate (text retained below)",
    "kept_absorbed": "kept; a duplicate was merged into it",
}
VERDICT_NAMES = {
    "supported": "no conflict found",
    "correct": "premise wrong or overstated",
    "reject": "contradicted",
    "duplicate": "duplicate",
    "unresolved": "not settled",
    "": "none",
}
QUALIFIER = ("model's reading, not independently verified; the quoted passage occurs "
             "verbatim in the manuscript")


# Anything that marks an omission or an editorial insertion: an ellipsis in any
# form, a bracketed gap or insertion, or a dash run standing in for elided
# text. A quotation containing one may join passages that never stood
# together, so it cannot support a verdict.
_NON_CONTIGUOUS = re.compile(r"\.\s*\.\s*\.|\u2026|\[[^\]]*\]|\(\s*\.\.\.?\s*\)|\s(?:--|\u2014\u2014)\s")


def _located(quote: str, sources: Dict[str, str]) -> List[str]:
    """Sources containing the quotation as ONE contiguous passage.

    Whitespace, line breaks, quote styles, dashes and punctuation are folded
    (extraction varies them), but nothing may be omitted: no ellipses, no
    bracketed insertions, and the whole quotation must occur in one place.
    rp.quotation_sources is deliberately not used here, because it accepts
    ellipses and checks each fragment separately."""
    quote = (quote or "").strip().strip('"\u201c\u201d\u00ab\u00bb').strip()
    if len(quote.split()) < MIN_QUOTE_WORDS or _NON_CONTIGUOUS.search(quote):
        return []
    needle = rp._normalise_for_match(quote)
    stripped = rp._strip_punctuation(needle)
    found = []
    for name, body in sources.items():
        hay = rp._normalise_for_match(body)
        punct = rp._strip_punctuation(hay)
        if needle in hay or (stripped and stripped in punct) or \
                (stripped and re.sub(r"\s+", "", stripped) in re.sub(r"\s+", "", punct)):
            found.append(name)
    return found


# Field labels appear in every item, so they would make any two items look alike.
_FIELD_LABELS = re.compile(
    r"\b(?:Strength|Concern|Check|Evidence|Why it matters|Reason|Severity|Limit|"
    r"Found only in a later pass)\b\s*\**\s*:?", re.I)


def _content(text: str) -> set:
    return rp._content_tokens(_FIELD_LABELS.sub(" ", text or "")) - rp._QA_STOPWORDS - _EXTRA_STOP


_EXTRA_STOP = {"may", "not", "but", "its", "can", "has", "have", "had", "than", "such",
               "whether", "if", "into", "also", "more", "only", "between", "because"}


def _overlap(a: str, b: str) -> float:
    left, right = _content(a), _content(b)
    if not left or not right:
        return 0.0
    return len(left & right) / min(len(left), len(right))


def _parse_evidence(raw, sources: Dict[str, str]) -> List[dict]:
    """Optional evidence passages: at most three, each checked for contiguous
    location exactly as "quote" is. Missing or malformed input gives []. An
    unknown role is kept as "unspecified" rather than guessed."""
    if not isinstance(raw, list):
        return []
    out = []
    for item in raw[:MAX_EVIDENCE_PASSAGES]:
        if not isinstance(item, dict):
            continue
        quote = str(item.get("quote", "") or "").strip()
        if not quote:
            continue
        role = str(item.get("role", "") or "").strip().lower()
        found = _located(quote, sources)
        out.append({"quote": quote,
                    "role": role if role in EVIDENCE_ROLES else "unspecified",
                    "located": bool(found), "sources": found})
    return out


def decide(items: Sequence[Item], proposals: Optional[List[dict]],
           sources: Dict[str, str]) -> Dict[str, Disposition]:
    """Turn the verifier's proposals into application decisions."""
    by_label = {item.label: item for item in items}
    result = {item.label: Disposition(item.label, item.kind, item.text) for item in items}
    if not proposals:
        return result

    seen = set()
    for entry in proposals:
        if not isinstance(entry, dict):
            continue
        label = str(entry.get("label", "")).strip()
        if label not in result or label in seen:
            continue
        seen.add(label)
        d = result[label]
        d.verdict = str(entry.get("verdict", "")).strip().lower()
        d.reason = str(entry.get("reason", "") or "").strip()
        d.quote = str(entry.get("quote", "") or "").strip()
        d.correction = str(entry.get("correction", "") or "").strip()
        d.surviving_point = str(entry.get("surviving_point", "") or "").strip()
        d.duplicate_of = str(entry.get("duplicate_of", "") or "").strip()
        d.reviewer_check = str(entry.get("reviewer_check", "") or "").strip()
        d.evidence = _parse_evidence(entry.get("evidence"), sources)
        if d.quote:
            d.quote_sources = _located(d.quote, sources)
            d.quote_located = bool(d.quote_sources)

        if d.verdict == "supported":
            d.outcome = "kept_supported"
        elif d.verdict == "unresolved":
            d.outcome = "kept_unresolved"
        elif d.verdict == "correct":
            if d.quote_located and d.correction:
                d.outcome = "kept_corrected"
            else:
                d.outcome = "kept_unresolved"
                d.note = ("proposed correction not shown: "
                          + ("no correction text" if not d.correction else
                             "its quotation was not found as one contiguous passage "
                             "in the manuscript"))
        elif d.verdict == "reject":
            # Never removed: a located quotation shows only that the passage
            # exists, not that it contradicts the item.
            if d.quote_located:
                d.outcome = "kept_disputed"
            else:
                d.outcome = "kept_unresolved"
                d.note = ("objection not shown: its quotation was not found as one "
                          "contiguous passage in the manuscript")
        elif d.verdict == "duplicate":
            d.outcome = "kept_unassessed"   # settled below
        else:
            d.outcome = "kept_unassessed"
            d.note = "unrecognised verdict"

    # Duplicates are settled after every other verdict is known, so an item is
    # never merged into one that is itself being removed.
    def target_of(label: str) -> Optional[str]:
        visited = {label}
        current = result[label].duplicate_of
        while current and current in result and current not in visited:
            visited.add(current)
            nxt = result[current]
            if nxt.verdict == "duplicate" and nxt.duplicate_of and nxt.duplicate_of not in visited:
                current = nxt.duplicate_of
                continue
            return current
        return None

    for label, d in result.items():
        if d.verdict != "duplicate":
            continue
        target = target_of(label)
        item = by_label[label]
        if not target or target == label:
            d.note = "duplicate claim not applied: no valid target"
            continue
        other = by_label[target]
        if result[target].outcome == "merged_into":
            d.note = f"duplicate claim not applied: {target} is itself removed"
            continue
        if (item.kind == "strength") != (other.kind == "strength"):
            d.note = "duplicate claim not applied: a strength cannot duplicate a criticism"
            continue
        if _overlap(item.text, other.text) < DUPLICATE_MIN_OVERLAP:
            d.note = "duplicate claim not applied: the two items share too little wording to check"
            continue
        # A concern is never dropped in favour of a verification prompt.
        keep, drop = other, item
        if item.kind == "concern" and other.kind == "prompt":
            keep, drop = item, other
        result[drop.label].outcome = "merged_into"
        result[drop.label].duplicate_of = keep.label
        if result[keep.label].outcome in ("kept_unresolved", "kept_unassessed") and \
                result[keep.label].verdict in ("", "duplicate"):
            result[keep.label].outcome = "kept_absorbed"
        if drop is other:
            # The concern absorbed the prompt; record why on both.
            result[drop.label].note = f"merged into {keep.label} (verifier marked {label} a duplicate of it)"
            d.duplicate_of = ""
    return result


def _quote_for_display(quote: str) -> str:
    quote = re.sub(r"\s+", " ", quote).strip().strip('"“”«»').strip()
    # Guillemets, not quotation marks: the citation check and the Evidence
    # match line read quotation marks, and a manuscript sentence quoted AGAINST
    # an item must not be counted as evidence FOR it.
    return f"«{quote}»"


def apply(report_text: str, items: Sequence[Item],
          decisions: Dict[str, Disposition]) -> str:
    """Rewrite only by removal and host-written annotation lines."""
    lines = (report_text or "").splitlines()
    by_start = {item.start: item for item in items}
    titles = {item.label: item.title for item in items}
    absorbed: Dict[str, List[str]] = {}
    for d in decisions.values():
        if d.outcome == "merged_into" and d.duplicate_of:
            absorbed.setdefault(d.duplicate_of, []).append(d.label)

    out: List[str] = []
    i = 0
    while i < len(lines):
        item = by_start.get(i)
        if item is None:
            out.append(lines[i]); i += 1
            continue
        d = decisions[item.label]
        block = lines[item.start:item.end]
        if d.outcome == "merged_into":
            i = item.end
            continue
        out.extend(block)
        bullet = "-" if block and block[0].lstrip().startswith("-") else "*"
        if d.outcome == "kept_corrected":
            line = (f"{bullet} Verifier's proposed correction ({QUALIFIER}): "
                    f"{d.correction.rstrip('.')}. Passage cited: {_quote_for_display(d.quote)}")
            if d.surviving_point:
                line += f" Point the verifier says remains: {d.surviving_point.rstrip('.')}."
            out.append(line)
        elif d.outcome == "kept_disputed":
            out.append(f"{bullet} Verifier's objection ({QUALIFIER}; the item has not been "
                       f"removed and should be checked against the manuscript): "
                       f"{(d.reason or 'no reason given').rstrip('.')}. "
                       f"Passage cited: {_quote_for_display(d.quote)}")
        elif d.outcome == "kept_unresolved" and d.verdict in ("unresolved", "correct", "reject"):
            out.append(f"{bullet} Source check: not settled by the manuscript text "
                       f"({(d.note or d.reason or 'no reason given').rstrip('.')}).")
        for other in absorbed.get(item.label, []):
            out.append(f"{bullet} Also raised as: {titles[other]}")
        i = item.end

    text = "\n".join(out)
    # Sections emptied by removals say so rather than vanishing.
    for name, kind, _prefix, _marker in _SECTIONS:
        had = [it for it in items if it.kind == kind]
        if had and all(decisions[it.label].outcome == "merged_into" for it in had):
            new_lines = text.splitlines()
            bounds = _section_bounds(new_lines, name)
            if bounds:
                new_lines.insert(bounds[0], "* None retained after source verification; see the "
                                            "Source verification record.")
                text = "\n".join(new_lines)

    changed = sum(1 for d in decisions.values()
                  if d.outcome in ("kept_corrected", "kept_disputed"))
    if changed:
        new_lines = text.splitlines()
        bounds = _section_bounds(new_lines, rp.FINAL_REPORT_HEADING.lower())
        if bounds:
            stop = bounds[1]
            while stop > bounds[0] and not new_lines[stop - 1].strip():
                stop -= 1
            new_lines.insert(stop, f"* The source verifier objected to or proposed corrections to "
                                   f"{changed} item(s) after this assessment was drafted; statements "
                                   "here that rely on them may need revisiting once those notes are "
                                   "checked.")
            text = "\n".join(new_lines)
    if report_text.endswith("\n") and not text.endswith("\n"):
        text += "\n"
    return text


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

@dataclass
class VerificationResult:
    report: str
    items: List[Item]
    decisions: Dict[str, Disposition]
    scope: str = ""
    omitted_chars: int = 0
    prompt_chars: int = 0
    status: str = "not_run"   # completed | failed | no_items | not_run
    error: str = ""
    raw: Optional[dict] = None
    unexamined: List[str] = field(default_factory=list)
    automated_flags: List[str] = field(default_factory=list)
    attempts: int = 0

    def counts(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for d in self.decisions.values():
            counts[d.outcome] = counts.get(d.outcome, 0) + 1
        return counts

    def as_dict(self) -> dict:
        return {
            "status": self.status,
            "error": self.error,
            "scope": self.scope,
            "omitted_chars": self.omitted_chars,
            "prompt_chars": self.prompt_chars,
            "unexamined_figures": list(self.unexamined),
            "automated_flags": list(self.automated_flags),
            "attempts": self.attempts,
            "counts": self.counts(),
            "dispositions": [self.decisions[i.label].as_dict() for i in self.items],
            "raw": self.raw,
        }


# 450 tokens per item covered verdict, quotation and reason; the optional
# evidence passages and reviewer check need roughly 200 more.
TOKENS_PER_ITEM = 650
MAX_OUTPUT_TOKENS = 12000


def max_tokens_for(n_items: int) -> int:
    """Output allowance: about 450 tokens per item, within a ceiling. Unused
    allowance costs nothing; a truncated answer costs the whole call."""
    return min(MAX_OUTPUT_TOKENS, max(1500, 600 + TOKENS_PER_ITEM * n_items))


def _retry_allowance(max_tokens: int, prompt: str) -> int:
    """Double the allowance for the single retry, but never past the room the
    context has left after the prompt (a request beyond it is refused)."""
    try:
        context = rp.available_context()
    except Exception:
        context = 32768
    room = context - int(len(prompt) / rp.PROMPT_CHARS_PER_TOKEN) - 512
    return max(max_tokens, min(max_tokens * 2, room))


def verification_budget(max_tokens: int) -> int:
    """Prompt characters for the verifier. The call itself is non-thinking, so
    the budget is computed with thinking off: otherwise a thinking review
    reserves reasoning room the call never uses, and the whole manuscript
    falls back to excerpts."""
    with llm_backend.thinking(False):
        return rp.prompt_char_budget(reserve_tokens=max_tokens)


@ea.stage("source-verification")
def verify_report(report_text: str, sources: Dict[str, str],
                  assessor: Callable[..., dict], *,
                  automated_flags: Sequence[str] = (),
                  primary_source: str = "",
                  budget: Optional[int] = None,
                  unexamined: Optional[Sequence[str]] = None,
                  passthrough: Sequence[type] = (),
                  retry_on: Sequence[type] = ()) -> VerificationResult:
    """
    Verify every item of a merged report against the manuscript.

    ``assessor(prompt=..., schema=..., max_tokens=...)`` returns the decoded
    JSON object. An exception in ``retry_on`` (output that was truncated or
    would not decode), or output without an item list, earns ONE further
    attempt with double the output allowance. Any other exception except those
    in ``passthrough`` (cancellation), or a second failure, leaves the report
    unchanged and every item unassessed.
    """
    items = extract_items(report_text)
    decisions = {item.label: Disposition(item.label, item.kind, item.text) for item in items}
    if unexamined is None:
        unexamined = unexamined_figures()
    result = VerificationResult(report_text, items, decisions, unexamined=list(unexamined),
                                automated_flags=list(dict.fromkeys(automated_flags)))
    if not items:
        result.status = "no_items"
        return result

    max_tokens = max_tokens_for(len(items))
    if budget is None:
        budget = verification_budget(max_tokens)
    skeleton = build_prompt(items, "", "complete", unexamined, automated_flags, primary_source)
    source_budget = max(4000, budget - len(skeleton) - 200)
    packet, scope, omitted = build_source_packet(items, sources, source_budget)
    prompt = build_prompt(items, packet, scope, unexamined, automated_flags, primary_source)
    result.scope, result.omitted_chars, result.prompt_chars = scope, omitted, len(prompt)

    schema = output_schema([i.label for i in items])
    proposals, raw, errors = None, None, []
    for attempt in range(2):
        allowance = max_tokens if attempt == 0 else _retry_allowance(max_tokens, prompt)
        try:
            raw = assessor(prompt=prompt, schema=schema, max_tokens=allowance)
        except tuple(passthrough):
            raise
        except tuple(retry_on) as exc:
            errors.append(f"{type(exc).__name__}: {exc}")
            continue
        except Exception as exc:  # the report must survive any verifier failure
            errors.append(f"{type(exc).__name__}: {exc}")
            break
        proposals = raw.get("items") if isinstance(raw, dict) else None
        if isinstance(proposals, list):
            break
        errors.append("verifier output had no item list")
        proposals = None
    result.attempts = len(errors) + (1 if proposals is not None else 0)
    if proposals is None:
        result.status = "failed"
        result.error = "; ".join(errors) or "no output"
        result.raw = raw if isinstance(raw, dict) or raw is None else {"unexpected": repr(raw)[:2000]}
        for d in decisions.values():
            d.note = "verification call failed"
        return result
    result.raw = raw
    result.decisions = decide(items, proposals, sources)
    for d in result.decisions.values():
        if d.outcome == "kept_unassessed" and not d.note:
            d.note = "no verdict returned for this item"
    result.report = apply(report_text, items, result.decisions)
    result.status = "completed"
    return result


def unexamined_figures() -> List[str]:
    """Figures the evidence ledger recorded by caption only, never as images."""
    try:
        return ea.unexamined_figures()
    except Exception:
        return []


# ---------------------------------------------------------------------------
# Reader-facing record
# ---------------------------------------------------------------------------

def _quote_status(d: Disposition) -> str:
    if not d.quote:
        return "none given"
    if d.quote_located:
        return "found verbatim, contiguous"
    return "NOT found as one contiguous passage"


def flag_dispositions(result: VerificationResult) -> List[Tuple[str, str]]:
    """Each deterministic flag, with what happened to it. A flag is never
    marked resolved: the application cannot tell whether the model's notes
    address it, so it stays visible for the reader."""
    acted = [i.label for i in result.items
             if result.decisions[i.label].outcome in ("kept_corrected", "kept_disputed")]
    out = []
    for flag in result.automated_flags:
        if result.status != "completed":
            state = "not reviewed by the verifier (verification did not complete); still open"
        elif acted:
            state = ("given to the verifier, which annotated " + ", ".join(acted)
                     + "; whether those notes address this flag is not checked; still open")
        else:
            state = "given to the verifier, which annotated no item; still open"
        out.append((flag, state))
    return out


def format_record(result: VerificationResult,
                  candidate_summary: Optional[dict] = None) -> str:
    """A report section stating what verification did to every item.

    Three columns are kept apart on purpose: the model's verdict, whether the
    application found the model's quotation in the manuscript, and what the
    application then did. Only the second is checked by code, and it shows
    that a passage exists, not that the model read it correctly."""
    lines = ["", "", "# Source verification record", ""]
    if result.status == "no_items":
        lines.append("No strengths, concerns or verification prompts were found to verify.")
    elif result.status == "failed":
        lines.append("Source verification did not complete "
                     f"({result.error or 'unknown error'}). No item was checked against the "
                     "manuscript, and none was changed. Treat every item above as unverified.")
    else:
        scope = ("the complete extracted text" if result.scope == "complete" else
                 f"passages retrieved for each item ({result.omitted_chars:,} characters of the "
                 "manuscript were not supplied, so an absence there settles nothing)")
        lines.append(f"A language model checked each item above once against {scope}. "
                     "Its verdicts are its own reading and are not independently verified. The "
                     "application checked one thing: whether each quotation the model gave occurs "
                     "verbatim, as one contiguous passage, in the manuscript. That shows the passage "
                     "exists, not that the model read it correctly or that it bears on the item. No "
                     "item was removed on the model's word; only duplicates were merged, and their "
                     "text is kept below. Findings established by application code alone are those "
                     "under Data consistency check.")
    if result.unexamined:
        lines.append("")
        lines.append("Not examined (caption only, image never read): "
                     + "; ".join(result.unexamined) + ". Items about what these show are unverified.")
    if result.items and result.status == "completed":
        lines.append("")
        lines.append("| Item | Model verdict | Model's quotation | Application action |")
        lines.append("| --- | --- | --- | --- |")
        for item in result.items:
            d = result.decisions[item.label]
            action = OUTCOMES.get(d.outcome, d.outcome)
            if d.outcome == "merged_into":
                action += f" into {d.duplicate_of}"
            title = item.title.replace("|", "/")
            verdict = VERDICT_NAMES.get(d.verdict, d.verdict or "none")
            lines.append(f"| {item.label} {KIND_NAMES[item.kind]}: {title} | {verdict} | "
                         f"{_quote_status(d)} | {action} |")
        counts = result.counts()
        lines.append("")
        lines.append("Totals: " + ", ".join(f"{OUTCOMES.get(k, k)}: {v}" for k, v in sorted(counts.items())))

    merged = [result.decisions[i.label] for i in result.items
              if result.decisions[i.label].outcome == "merged_into"]
    if merged:
        lines.append("")
        lines.append("## Duplicates merged, as drafted")
        for d in merged:
            lines.append("")
            lines.append(f"**{d.label}** — merged into {d.duplicate_of}: "
                         f"{(d.reason or d.note or 'no reason given').rstrip('.')}.")
            lines.append("")
            lines.extend("> " + l for l in d.original.splitlines())
    not_shown = [result.decisions[i.label] for i in result.items
                 if result.decisions[i.label].note.startswith(
                     ("proposed correction not shown", "objection not shown", "duplicate claim"))]
    if not_shown:
        lines.append("")
        lines.append("Model proposals not shown in the review: " + "; ".join(
            f"{d.label} ({d.note})" for d in not_shown) + ".")
    flags = flag_dispositions(result)
    if flags:
        lines.append("")
        lines.append("## Automated checks on the draft")
        lines.append("")
        lines.append("Raised by application code about the draft review before verification. "
                     "Each still applies unless the review above plainly no longer makes the "
                     "claim it targets.")
        lines.append("")
        for flag, state in flags:
            lines.append(f"- {flag} — {state}.")
    if candidate_summary:
        lines.append("")
        lines.append(candidate_summary_line(candidate_summary))
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Candidate accounting (no model call)
# ---------------------------------------------------------------------------

def _candidate_body(text: str) -> str:
    return re.sub(r"^\s*[-*]\s*", "", text or "").strip()


def account_candidates(candidate_findings: Sequence[dict],
                       items: Sequence[Item],
                       decisions: Optional[Dict[str, Disposition]] = None) -> dict:
    """
    Account for every chunk-level candidate against the final items.

    Matching is lexical: a candidate counts as reflected in an item when most
    of its content words appear there. That is a provenance aid, not a claim
    that the two say the same thing, and it errs towards "not carried
    forward", which is the safe direction: the reader sees one candidate too
    many rather than one too few. Nothing here judges whether a candidate is
    right, and none of it is sent to a model.
    """
    decisions = decisions or {}
    distinct: Dict[str, dict] = {}
    for cand in candidate_findings or []:
        key = rp._normalise_candidate_group_text(cand.get("text", ""))
        if not key:
            continue
        entry = distinct.setdefault(key, {
            "candidate_ids": [], "text": _candidate_body(cand.get("text", "")),
            "section": cand.get("section", ""), "source_name": cand.get("source_name", ""),
            "chunk_ids": [],
        })
        entry["candidate_ids"].append(cand.get("candidate_id", ""))
        if cand.get("chunk_id") not in entry["chunk_ids"]:
            entry["chunk_ids"].append(cand.get("chunk_id"))

    item_tokens = [(item, _content(item.text)) for item in items]
    records = []
    for entry in distinct.values():
        tokens = _content(entry["text"])
        best, best_score = None, 0.0
        for item, toks in item_tokens:
            if not tokens:
                break
            score = len(tokens & toks) / len(tokens)
            if score > best_score:
                best, best_score = item, score
        if best is not None and best_score >= CANDIDATE_MATCH and len(tokens) >= 3:
            outcome = decisions.get(best.label).outcome if best.label in decisions else "kept_unassessed"
            status = ("reflected_in_removed_item" if outcome == "merged_into"
                      else "reflected")
            records.append(dict(entry, status=status, item=best.label,
                                nearest=best.label, overlap=round(best_score, 2)))
        else:
            records.append(dict(entry, status="not_carried_forward", item="",
                                nearest=best.label if best is not None else "",
                                overlap=round(best_score, 2)))
    summary = {
        "distinct": len(records),
        "total": len(candidate_findings or []),
        "reflected": sum(1 for r in records if r["status"] == "reflected"),
        "reflected_in_removed_item": sum(1 for r in records if r["status"] == "reflected_in_removed_item"),
        "not_carried_forward": sum(1 for r in records if r["status"] == "not_carried_forward"),
        "threshold": CANDIDATE_MATCH,
        "records": records,
    }
    return summary


def candidate_summary_line(summary: dict) -> str:
    return (f"Chunk-level candidates: {summary['distinct']} distinct observations were raised while "
            f"reading the manuscript in sections; {summary['reflected']} have a lexical counterpart "
            f"in an item above, {summary['reflected_in_removed_item']} in a removed item, and "
            f"{summary['not_carried_forward']} were not carried into this review. Those are listed, "
            "unverified and verbatim, in the evidence appendix: some will be minor or mistaken, "
            "but none was discarded silently.")


def format_candidate_appendix(summary: dict) -> str:
    if not summary or not summary.get("records"):
        return ""
    lines = ["", "## Additional observations from the initial reading (not independently verified)", "",
             "Raised by the section-by-section reading and absent from the final review, "
             "by lexical matching only. They have not been checked against the manuscript and are "
             "not findings. They are listed so that nothing noticed is lost without trace. "
             "Matching is by shared wording: a candidate may be listed here although an item says "
             "the same thing differently (the nearest item is named where the overlap is "
             "appreciable), and a short candidate can be counted as reflected on shared words alone.",
             ""]
    missing = [r for r in summary["records"] if r["status"] == "not_carried_forward"]
    if not missing:
        lines.append("None: every candidate has a lexical counterpart in the review.")
    order = {name: i for i, name in enumerate(_SECTION_ORDER)}
    for record in sorted(missing, key=lambda r: (order.get(r["section"], len(order)), r["source_name"],
                                                  min(c or 0 for c in r["chunk_ids"]))):
        chunks = ", ".join(str(c) for c in record["chunk_ids"])
        text = re.sub(r"\s+", " ", record["text"])
        near = (f" (nearest item {record['nearest']}, word overlap {record['overlap']:.2f})"
                if record.get("nearest") and record["overlap"] >= NEAREST_HINT else "")
        lines.append(f"- [{record['source_name']}, chunk {chunks}; {record['section']}] {text}{near}")
    removed = [r for r in summary["records"] if r["status"] == "reflected_in_removed_item"]
    if removed:
        lines += ["", "Candidates whose counterpart was removed by source verification "
                  "(see the Source verification record):", ""]
        for record in removed:
            text = re.sub(r"\s+", " ", record["text"])
            lines.append(f"- [{record['item']}] {text}")
    return "\n".join(lines) + "\n"
