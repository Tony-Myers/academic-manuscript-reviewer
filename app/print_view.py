"""
print_view.py -- a dedicated, print-optimised page for the Evidence Cards.

The interactive Evidence Cards are shown inside the main Review Workspace, in
a frame beside the manuscript viewer. Printing from there prints the
workspace: the manuscript viewer, the application controls, and only the
visible part of the cards frame. This page is printed on its own instead.

Two modes, from the same saved data:
  summary   every finding, its reviewer decision and any reviewer wording;
  detailed  the same, plus manuscript evidence, suggested checks, what remains
            uncertain and the verification record, for every card.

Every card is printed in full: nothing is collapsible here, so what was
expanded on screen does not matter. The layout uses plain block flow only
(no flex, grid, line clamps, fixed heights or sticky elements), so content
continues across page breaks instead of overlapping. Original AI findings are
printed unchanged and labelled; reviewer decisions and wording are printed in
a separately labelled block. Read-only: nothing is saved or changed.
"""
from __future__ import annotations

import html
import json
from typing import Any, Dict, Optional

import reviewer_presentation as presentation

MODES = ("summary", "detailed")
DECISION_NAMES = {"retain": "Retained", "revise": "Revised", "dismiss": "Dismissed"}

_CSS = """
:root{color-scheme:light}
*{box-sizing:border-box}
body{margin:0;background:#fff;color:#111;font:15px/1.45 -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}
.page{max-width:820px;margin:0 auto;padding:20px 24px 48px}
.toolbar{padding:10px 24px;border-bottom:1px solid #ccc;background:#f4f4f1;font-size:14px}
.toolbar a,.toolbar button{font:inherit;margin-right:10px}
.toolbar .on{font-weight:700;text-decoration:none;color:#111}
h1{font:600 22px/1.3 Georgia,'Times New Roman',serif;margin:0 0 6px}
.meta{color:#444;font-size:13px}
.key{margin:12px 0 18px;padding:8px 10px;border:1px solid #bbb;font-size:13px}
.pcard{border-top:2px solid #333;padding:10px 0 14px;margin-top:6px}
h2{font-size:16px;margin:0 0 6px}
h3{font-size:12px;text-transform:uppercase;letter-spacing:.05em;color:#333;margin:12px 0 4px}
.tag{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.05em;color:#333;margin-bottom:3px}
.ai{border-left:4px solid #999;padding:4px 0 4px 10px;margin:6px 0}
.ai p{margin:0 0 .5em}.ai ul,.ai ol{margin:.3em 0;padding-left:1.3em}
.decision{border:2px solid #1f4a1b;padding:6px 10px;margin:8px 0}
.decision .value{font-weight:700;margin:0}
.wording{white-space:pre-wrap;overflow-wrap:anywhere;margin:6px 0 0}
.flags{font-size:13px;margin:4px 0}
blockquote{margin:6px 0;padding:4px 10px;border-left:3px solid #1f4a1b;background:#f3f6f2;overflow-wrap:anywhere}
blockquote.unv{border-left-color:#7a1c1c;background:#fbf2f2}
ul{margin:4px 0;padding-left:20px}
table{border-collapse:collapse;width:100%;font-size:13px}
td{border-top:1px solid #ccc;padding:4px 6px;vertical-align:top}
td:first-child{font-weight:600;white-space:nowrap;width:1%}
@media print{
  @page{margin:15mm}
  body{font-size:10.5pt}
  .toolbar,.screen-only{display:none!important}
  .page{max-width:none;margin:0;padding:0}
  .pcard{break-inside:auto;page-break-inside:auto}
  h2,h3,.tag{break-after:avoid;page-break-after:avoid}
  .decision,.flags,tr{break-inside:avoid;page-break-inside:avoid}
  a{color:inherit;text-decoration:none}
}
"""

# Fills decision blocks from this browser's stored decisions, only when the
# review is not in the local review store. Text only (textContent).
_JS = r"""
(function () {
  if (DECISION_SOURCE !== 'browser') return;
  let decisions = {};
  try { decisions = JSON.parse(localStorage.getItem('evidence-card-decisions:' + DOC_ID) || '{}') || {}; }
  catch (e) { decisions = {}; }
  const names = {retain: 'Retained', revise: 'Revised', dismiss: 'Dismissed'};
  document.querySelectorAll('.decision[data-label]').forEach(box => {
    const d = decisions[box.dataset.label];
    box.querySelector('.value').textContent = d && names[d.decision] ? names[d.decision] : 'Not yet reviewed';
    const words = box.querySelector('.wording');
    const note = d && (d.note || '').trim();
    words.textContent = note ? (d.decision === 'revise' ? "Reviewer's revised wording (verbatim): "
                                                       : 'Reviewer comment (verbatim): ') + d.note : '';
    words.hidden = !note;
  });
})();
"""


def _e(text: Any) -> str:
    return html.escape("" if text is None else str(text), quote=True)


def _decision_html(label: str, decision: Optional[Dict[str, Any]]) -> str:
    name = DECISION_NAMES.get((decision or {}).get("decision"), "Not yet reviewed")
    note = ((decision or {}).get("note") or "").strip()
    words = ""
    if note:
        prefix = ("Reviewer's revised wording (verbatim): " if decision.get("decision") == "revise"
                  else "Reviewer comment (verbatim): ")
        words = prefix + decision["note"]
    return (f'<div class="decision" data-label="{_e(label)}"><div class="tag">Reviewer decision</div>'
            f'<p class="value">{_e(name)}</p>'
            f'<p class="wording"{"" if words else " hidden"}>{_e(words)}</p></div>')


def _flags(card: Dict[str, Any]) -> str:
    flags = []
    if presentation.disputed(card):
        flags.append("Disputed by the AI verifier")
    if card.get("warnings"):
        flags.append("Potential inconsistency in the verification record")
    if card.get("quotation_notice") or (card.get("evidence_groups") or {}).get("unverified"):
        flags.append("A quotation supplied by the AI was not located in the manuscript")
    if (card.get("provenance") or {}).get("application_action") == "merged_into":
        flags.append("Merged into " + str((card.get("provenance") or {}).get("model_duplicate_of") or "another item"))
    return f'<p class="flags">{_e(". ".join(flags))}.</p>' if flags else ""


def _detail_html(card: Dict[str, Any]) -> str:
    h = ['<h3>Evidence from the manuscript</h3>']
    message = presentation.authentication_message(card)
    if message:
        h.append(f'<p>{_e(message)}</p>')
    for warning in presentation.material_warnings(card):
        h.append(f'<p class="meta">{_e(warning.get("detail"))}</p>')
    groups = card.get("evidence_groups") or {}
    any_located = False
    for key, heading in (("supporting", "Evidence cited for this finding"),
                         ("qualifying", "Evidence that may challenge this finding"),
                         ("other", "Other relevant evidence")):
        for p in groups.get(key) or []:
            if not any_located:
                h.append('<p class="meta">Passages located verbatim by the application. Evidence roles '
                         'reflect the AI’s interpretation; a located passage does not show that the '
                         'finding is correct.</p>')
                any_located = True
            loc = p.get("location") or "page not marked in the extracted text"
            h.append(f'<blockquote>{_e(p.get("text"))}</blockquote><p class="meta">{_e(heading)} · '
                     f'{_e(p.get("source") or "source not recorded")} · {_e(loc)} · '
                     f'{_e(p.get("origin") or "")}</p>')
    if not any_located:
        h.append('<p>No manuscript passage was located for this finding. An unsuccessful match does not '
                 'show that the information is absent.</p>')
    for p in groups.get("unverified") or []:
        h.append(f'<p class="meta">Quotation not located in the manuscript ({_e(p.get("origin") or "origin not recorded")}; '
                 f'{_e(p.get("note") or "not found")}):</p><blockquote class="unv">{_e(p.get("text"))}</blockquote>')

    h.append('<h3>What needs checking?</h3>')
    if card.get("reviewer_check"):
        h.append(f'<p class="meta">{_e(presentation.CHECK_QUALIFICATION)}</p>'
                 + presentation.markdown_html(card["reviewer_check"]))
    else:
        h.append('<p class="meta">No suggested check is available in this review record.</p>')

    h.append('<h3>What remains uncertain?</h3><p>The evidence does not establish whether this finding is justified.</p>')
    items = presentation.context_items(card)
    if items:
        h.append(f'<p class="meta">{_e(presentation.EXPLANATION_QUALIFICATION)}</p><ul>'
                 + "".join(f'<li>{presentation.markdown_html(t)}</li>' for t in items) + '</ul>')

    h.append('<h3>Verification record</h3>')
    h.append(f'<p class="meta">{_e(card.get("verification_status"))}</p><table>')
    dims = card.get("dimensions") or {}
    for key, name in (("evidence", "Evidence"), ("factual_premise", "Factual premise"),
                      ("methodological_conclusion", "Methodological conclusion"),
                      ("evidence_completeness", "Evidence completeness")):
        d = dims.get(key) or {}
        h.append(f'<tr><td>{_e(name)}</td><td>{_e(d.get("label") or "not recorded")}'
                 f'<br><span class="meta">{_e(d.get("basis") or "")}</span></td></tr>')
    h.append('</table>')
    return "".join(h)


def render(card_set: Dict[str, Any], decisions: Dict[str, Any], meta: Dict[str, Any], mode: str) -> str:
    """meta: job_id, filename, printed_at, decision_source ("saved" | "browser"
    | "unavailable"), decisions_saved_at, doc_id (the cards page's storage id)."""
    mode = mode if mode in MODES else "summary"
    cards = card_set.get("cards") or []
    decisions = decisions or {}
    job = meta.get("job_id") or ""
    title = "Evidence Cards — " + ("detailed record" if mode == "detailed" else "summary")
    counts = {k: 0 for k in DECISION_NAMES}
    for c in cards:
        d = decisions.get(c.get("label"))
        if d and d.get("decision") in counts:
            counts[d["decision"]] += 1
    source = meta.get("decision_source")
    if source == "saved":
        decided = (f"Reviewer decisions as saved in the local review store"
                   + (f" (last saved {meta['decisions_saved_at']})" if meta.get("decisions_saved_at") else "")
                   + f": {counts['retain']} retained, {counts['revise']} revised, {counts['dismiss']} dismissed, "
                   f"{len(cards) - sum(counts.values())} not yet reviewed.")
    elif source == "browser":
        decided = "Reviewer decisions as stored in this browser (this review is not in the local review store)."
    else:
        decided = "Reviewer decisions could not be read; every card is shown as not yet reviewed."

    out = [f'<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>{_e(title)}</title>'
           f'<style>{_CSS}</style></head><body>',
           '<div class="toolbar screen-only">'
           '<button type="button" onclick="window.print()">Print / Save as PDF</button>'
           f'<a class="{"on" if mode == "summary" else ""}" href="?mode=summary">Summary</a>'
           f'<a class="{"on" if mode == "detailed" else ""}" href="?mode=detailed">Detailed</a>'
           '<span class="meta">In the print dialogue choose “Save as PDF”.</span></div>',
           '<div class="page">', f'<h1>{_e(title)}</h1>',
           f'<p class="meta">{_e(meta.get("filename") or "Manuscript file not recorded")} · review {_e(job)} · '
           f'printed {_e(meta.get("printed_at") or "")}</p>',
           f'<p class="meta">{_e(decided)} Choices not yet confirmed are not included.</p>',
           '<div class="key"><strong>AI-generated finding</strong>: the original wording, unchanged. '
           '<strong>Reviewer decision</strong>: the reviewer’s recorded decision and any wording of their own, '
           'kept separate from the AI text. Findings are provisional; the reviewer remains responsible for the '
           'final review.</div>']
    for c in cards:
        label = str(c.get("label") or "")
        out.append(f'<section class="pcard" id="print-{_e(label)}"><h2>{_e(label)} · {_e(c.get("kind_name"))}</h2>')
        out.append(_flags(c))
        out.append('<div class="ai"><div class="tag">AI-generated finding (original wording, unchanged)</div>'
                   + presentation.markdown_html(c.get("original", "")) + '</div>')
        out.append(_decision_html(label, decisions.get(label) if source != "browser" else None))
        if mode == "detailed":
            out.append(_detail_html(c))
        out.append('</section>')
    if not cards:
        out.append('<p>No Evidence Cards are available for this review.</p>')
    out.append('</div><script>const DOC_ID = ' + json.dumps(meta.get("doc_id") or "").replace("<", "\\u003c")
               + '; const DECISION_SOURCE = ' + json.dumps(source or "") + ';' + _JS + '</script></body></html>')
    return "".join(out)


# ---------------------------------------------------------------------------
# Print pages for the Critical Appraisal and the Human Evidence Appendix
# ---------------------------------------------------------------------------
# Same page design as the Evidence Cards print view: a screen-only toolbar,
# a title block (document, manuscript file, review, time of printing), a key
# saying who wrote what, and plain block flow that continues across pages.
# The saved Markdown is rendered here, safely: every character of the source
# is HTML-escaped before the few supported Markdown forms become markup.

import re as _re

_DOC_CSS = """
.doc h2{font-size:18px;margin:18px 0 6px;border-bottom:1px solid #999;padding-bottom:2px}
.doc h3{font-size:15px;text-transform:none;letter-spacing:0;color:#111;margin:14px 0 4px}
.doc h4,.doc h5,.doc h6{font-size:14px;margin:12px 0 4px}
.doc p{margin:0 0 .6em}
.doc ul,.doc ol{margin:.3em 0 .6em;padding-left:1.4em}
.doc li{margin:.15em 0}
.doc li.l1{margin-left:1.2em}.doc li.l2{margin-left:2.4em}.doc li.l3{margin-left:3.6em}
.doc table{margin:6px 0 10px}
.doc th,.doc td{border:1px solid #bbb;padding:4px 6px;text-align:left;vertical-align:top;overflow-wrap:anywhere}
.doc td:first-child{font-weight:normal;white-space:normal;width:auto}
.doc th{background:#f1f1ee}
.doc pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f4f4f1;padding:6px 8px;font-size:12px}
.doc code{font-size:.92em}
.doc hr{border:0;border-top:1px solid #bbb;margin:12px 0}
.part{margin-top:18px}
.part>.tag{font-size:12px}
@media print{
  .doc h2,.doc h3,.doc h4{break-after:avoid;page-break-after:avoid}
  .doc thead{display:table-header-group}
  .doc tr,.doc li{break-inside:avoid;page-break-inside:avoid}
}
"""


def _inline_md(text: str) -> str:
    tokens = []

    def keep(markup: str) -> str:
        tokens.append(markup)
        return "\x00%d\x00" % (len(tokens) - 1)

    s = str(text).replace("\x00", "")
    s = _re.sub(r"`([^`]+)`", lambda m: keep("<code>" + _e(m.group(1)) + "</code>"), s)
    # Backslash escapes: the escaped character is shown as itself.
    s = _re.sub(r"\\([!-/:-@\[-`{-~])", lambda m: keep(_e(m.group(1))), s)
    # Links print as their text, followed by the address for web links only.
    s = _re.sub(r"\[([^\]\n]+)\]\(([^)\s]+)\)",
                lambda m: keep(_inline_md(m.group(1))
                               + (" (" + _e(m.group(2)) + ")" if _re.match(r"https?://", m.group(2)) else "")), s)
    s = _e(s)
    s = _re.sub(r"\*\*([^*]+)\*\*|__([^_]+)__", lambda m: "<strong>" + (m.group(1) or m.group(2)) + "</strong>", s)
    s = _re.sub(r"\*([^*\n]+)\*", r"<em>\1</em>", s)
    s = _re.sub(r"(?<!\w)_([^_\n]+)_(?!\w)", r"<em>\1</em>", s)
    return _re.sub(r"\x00(\d+)\x00", lambda m: tokens[int(m.group(1))], s)


def _cells(line: str) -> list:
    value = line.strip()
    if value.startswith("|"):
        value = value[1:]
    if value.endswith("|") and not value.endswith("\\|"):
        value = value[:-1]
    out, cell, i = [], "", 0
    while i < len(value):
        if value[i] == "\\" and i + 1 < len(value) and value[i + 1] == "|":
            cell += "|"
            i += 2
            continue
        if value[i] == "|":
            out.append(cell.strip())
            cell = ""
        else:
            cell += value[i]
        i += 1
    out.append(cell.strip())
    return out


_LIST = _re.compile(r"^(\s*)(?:([-*+•])|(\d+)[.)])\s+(.*)$")
_HEAD = _re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")


def markdown_document_html(md: str) -> str:
    """Saved review Markdown as print HTML. Headings (shifted one level below
    the page title), paragraphs, nested lists, tables, blockquotes, code and
    rules. Unrecognised text is kept as escaped text, never dropped."""
    lines = str(md or "").replace("\r\n", "\n").split("\n")
    out, i = [], 0

    def table_at(n):
        return (n + 1 < len(lines) and "|" in lines[n] and len(_cells(lines[n + 1])) > 1
                and all(_re.fullmatch(r":?-{3,}:?", c) for c in _cells(lines[n + 1])))

    def block_start(n):
        line = lines[n]
        return (not line.strip() or line.startswith("```") or _HEAD.match(line) or line.startswith(">")
                or _LIST.match(line) or _re.fullmatch(r"\s*(-{3,}|\*{3,})\s*", line) or table_at(n))

    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if line.startswith("```"):
            code = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                code.append(lines[i])
                i += 1
            i += 1
            out.append("<pre><code>" + _e("\n".join(code)) + "</code></pre>")
            continue
        heading = _HEAD.match(line)
        if heading:
            level = min(len(heading.group(1)) + 1, 6)
            out.append(f"<h{level}>{_inline_md(heading.group(2))}</h{level}>")
            i += 1
            continue
        if _re.fullmatch(r"\s*(-{3,}|\*{3,})\s*", line):
            out.append("<hr>")
            i += 1
            continue
        if table_at(i):
            head = _cells(line)
            i += 2
            rows = []
            while i < len(lines) and lines[i].strip() and "|" in lines[i]:
                rows.append(_cells(lines[i]))
                i += 1
            out.append("<table><thead><tr>" + "".join(f"<th>{_inline_md(c)}</th>" for c in head)
                       + "</tr></thead><tbody>"
                       + "".join("<tr>" + "".join(f"<td>{_inline_md(c)}</td>" for c in row) + "</tr>"
                                 for row in rows) + "</tbody></table>")
            continue
        if line.startswith(">"):
            quote = []
            while i < len(lines) and lines[i].startswith(">"):
                text = _re.sub(r"^> ?", "", lines[i])
                trailing = len(text) - len(text.rstrip("\\"))
                if trailing % 2 == 1:      # a Markdown hard line break, not text
                    text = text[:-1]
                quote.append(text)
                i += 1
            out.append("<blockquote>" + "<br>".join(_inline_md(q) for q in quote) + "</blockquote>")
            continue
        if _LIST.match(line):
            ordered = bool(_LIST.match(line).group(3))
            items = []
            while i < len(lines) and _LIST.match(lines[i]):
                m = _LIST.match(lines[i])
                level = min(len(m.group(1).replace("\t", "    ")) // 2, 3)
                text = [m.group(4)]
                i += 1
                while i < len(lines) and lines[i].strip() and not block_start(i):
                    text.append(lines[i].strip())
                    i += 1
                items.append(f'<li class="l{level}">' + _inline_md(" ".join(text)) + "</li>")
            tag = "ol" if ordered else "ul"
            out.append(f"<{tag}>" + "".join(items) + f"</{tag}>")
            continue
        para = [line.strip()]
        i += 1
        while i < len(lines) and lines[i].strip() and not block_start(i):
            para.append(lines[i].strip())
            i += 1
        out.append("<p>" + "<br>".join(_inline_md(p) for p in para) + "</p>")
    return "".join(out)


_MAIN_HEADINGS = ("overall synopsis", "major strengths", "directly supported concerns")
_AUDIT_HEADINGS = _re.compile(r"^(items by evidence|source verification record|citation check|candidate accounting"
                              r"|chunk[- ]level candidate.*|review verification.*|verification audit.*)$")


def split_appraisal(md: str) -> tuple:
    """The same three consecutive parts the Critical Appraisal tab shows
    (technical details, appraisal, verification and audit record); together
    they are the whole saved report, in its own order."""
    lines = _re.findall(r"[^\n]*(?:\n|$)", str(md or ""))
    main = audit = -1
    fenced = False
    for i, line in enumerate(lines):
        if _re.match(r"^\s*```", line):
            fenced = not fenced
            continue
        if fenced:
            continue
        heading = _re.match(r"^#{1,6}\s+(.+?)\s*#*\s*$", line)
        if not heading:
            continue
        title = heading.group(1).strip().lower()
        if main < 0 and title in _MAIN_HEADINGS:
            main = i
        if audit < 0 and _AUDIT_HEADINGS.match(title):
            audit = i
    if main < 0:
        main = 0
    if audit < main:
        audit = -1
    technical = "".join(lines[:main])
    appraisal = "".join(lines[main:audit if audit >= 0 else None])
    rest = "".join(lines[audit:]) if audit >= 0 else ""
    return technical, appraisal, rest


def render_document(title: str, parts: list, meta: Dict[str, Any], key_html: str) -> str:
    """A print page in the Evidence Cards print design. parts: (tag, html)
    pairs; a tag labels its part (for example, whose content it is)."""
    out = [f'<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>{_e(title)}</title>'
           f'<style>{_CSS}{_DOC_CSS}</style></head><body>',
           '<div class="toolbar screen-only">'
           '<button type="button" onclick="window.print()">Print / Save as PDF</button>'
           '<span class="meta">In the print dialogue choose “Save as PDF”.</span></div>',
           '<div class="page">', f'<h1>{_e(title)}</h1>',
           f'<p class="meta">{_e(meta.get("filename") or "Manuscript file not recorded")} · review '
           f'{_e(meta.get("job_id") or "")} · printed {_e(meta.get("printed_at") or "")}'
           + (f' · review completed {_e(meta["completed_at"])}' if meta.get("completed_at") else "") + '</p>',
           f'<div class="key">{key_html}</div>']
    for tag, body in parts:
        out.append('<section class="part">' + (f'<div class="tag">{_e(tag)}</div>' if tag else "")
                   + f'<div class="doc">{body}</div></section>')
    out.append('</div></body></html>')
    return "".join(out)


def render_appraisal(report_md: str, meta: Dict[str, Any]) -> str:
    technical, appraisal, audit = split_appraisal(report_md)
    parts = []
    if technical.strip():
        parts.append(("Review details and technical information", markdown_document_html(technical)))
    parts.append(("Critical Appraisal (AI-generated; saved wording, unaltered)", markdown_document_html(appraisal)))
    if audit.strip():
        parts.append(("Review verification and audit (model judgements and mechanical evidence checks; "
                      "locating a quotation does not establish that its interpretation is valid)",
                      markdown_document_html(audit)))
    key = ('<strong>AI-generated appraisal</strong>, printed from the saved review without change, to '
           'support the human reviewer\u2019s judgement; it is not a final peer-review report. Reviewer '
           'decisions are not part of it: they are recorded separately in the Evidence Cards.')
    return render_document("Critical Appraisal", parts, meta, key)


def render_appendix(appendix_md: str, meta: Dict[str, Any]) -> str:
    key = ('<strong>Human Evidence Appendix</strong>, generated now from the saved review data (no model was '
           'run). All findings, stated evidence and reasons are <strong>AI-generated</strong>. Each AI quotation '
           'is shown in one of three states: <strong>exact quotation authenticated</strong> (found in the '
           'manuscript text as one continuous passage), <strong>related manuscript passage located</strong> '
           '(the quotation is not authenticated; the passage is shown for comparison) or <strong>quotation not '
           'located</strong>. Locating a passage does not show that the AI\u2019s reading of it is correct. '
           'Reviewer decisions are recorded separately in the Evidence Cards.')
    # The appendix's own first heading repeats the page title; only that
    # line is dropped from the printed copy.
    body = _re.sub(r"\A\s*#\s+Human Evidence Appendix\s*\n", "", appendix_md or "")
    return render_document("Human Evidence Appendix", [("", markdown_document_html(body))], meta, key)
