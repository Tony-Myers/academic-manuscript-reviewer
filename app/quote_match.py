"""
quote_match.py -- deterministic classification of an AI quotation against the
manuscript text, for the reviewer-facing Human Evidence Appendix.

No model is called. The manuscript text is authoritative; the AI quotation is
never rewritten or corrected. Each quotation is given one of three states:

  exact        Exact quotation authenticated. The quotation occurs in the
               extracted manuscript text as one continuous passage once the
               documented normalisation below is applied to both. Every
               occurrence is reported.
  related      Related manuscript passage located; the quotation is NOT
               authenticated. Every word, number and symbol of the quotation
               occurs, in the same order, on one extracted line of the
               manuscript, but with other text between them (for example, a
               table row whose other columns the quotation leaves out). Only
               one line in the whole manuscript may qualify.
  not_located  Quotation not located. No reliable location could be
               established. This is not evidence that the manuscript lacks the
               information: extraction can miss or alter text.

Normalisation (applied identically to quotation and manuscript; nothing else
is folded):
  - Unicode compatibility forms (NFKC), e.g. full-width characters;
  - letter case;
  - curly and straight quotation marks; hyphen, en dash, em dash and minus
    sign (all read as "-", so a negative sign is kept as a sign);
  - spacing and line breaks;
  - the punctuation characters , ; : ' " ( ) [ ] { } and the table cell
    separator |, and full stops that are not part of a number. A full stop
    or comma between digits (1.93, 1,250) and a full stop before a digit
    (.05) are kept, so decimal places and separators must agree.
  Signs, digits, decimal places, units, group labels, time points and symbols
  such as ± < > = % are compared exactly, token by token. Matching is on whole
  tokens, so "1.9" never matches inside "1.93".

Why no similarity threshold is used: a score cannot say which column, group or
time point a number belongs to, and any cut-off would be arbitrary. The rules
above are all-or-nothing: every token must match. The "related" state adds no
tolerance for different wording or numbers; it allows only omitted text, which
is shown to the reviewer, and it is withheld whenever more than one line
qualifies, because repeated numbers or labels could otherwise be attributed to
the wrong table or condition.

Further rules, all conservative:
  - Fewer than MIN_TOKENS words and numbers: "exact" only when the passage
    occurs exactly once in the manuscript and contains at least two words.
  - A quotation of numbers and symbols only is never authenticated and is
    never given a related passage: numbers alone cannot establish what they
    refer to.
  - A quotation with an ellipsis or a bracketed insertion is not one
    continuous passage, so it cannot be "exact".
  - "related" requires at least one number and one word, every token present
    in order on a single line, and, outside tables, every number joined to at
    least one neighbouring token of the quotation exactly as the quotation
    places it (so a number is not borrowed from an unrelated phrase).
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import human_evidence_appendix as hea

EXACT, RELATED, NOT_LOCATED = "exact", "related", "not_located"
MIN_TOKENS = 6          # the application's existing minimum for authenticating a quotation
MAX_LOCATIONS = 5       # occurrences listed in full; the remainder are counted

STATE_LABELS = {
    EXACT: "Exact quotation authenticated",
    RELATED: "Related manuscript passage located — quotation not authenticated",
    NOT_LOCATED: "Quotation not located — not authenticated",
}

_STYLE = {"‘": "'", "’": "'", "‚": "'", "‛": "'", "′": "'",
          "“": '"', "”": '"', "„": '"', "‟": '"', "″": '"',
          "«": '"', "»": '"',
          "‐": "-", "‑": "-", "‒": "-", "–": "-", "—": "-",
          "―": "-", "−": "-", "﹣": "-", "－": "-"}
_IGNORABLE = set(",;:'\"()[]{}|")
_NON_CONTIGUOUS = re.compile(r"\.\s*\.\s*\.|…|\[[^\]]*\]|\(\s*\.\.\.?\s*\)|\s(?:--|——)\s")
_TOKEN = re.compile(r"(?:(?<![\w.])-)?(?:\d+(?:[.,]\d+)*|\.\d+)|[^\W\d_]+(?:-[^\W\d_]+)*|\S")
_NUMBER = re.compile(r"-?(?:\d|\.\d)")
_WORD = re.compile(r"[^\W\d_]")

ALL_RULES = frozenset({"nfkc", "case", "styles", "punctuation"})
RULE_NAMES = {
    "nfkc": "Unicode compatibility forms",
    "case": "letter case",
    "styles": "quotation-mark or dash style",
    "punctuation": "punctuation (commas, colons, semicolons, brackets, quotation marks, table "
                   "separators or full stops outside numbers)",
}


def _normalise(text: str, rules=ALL_RULES) -> Tuple[str, List[int]]:
    """Normalised text and, for every character, the raw index it came from."""
    out: List[str] = []
    index: List[int] = []
    last_space = True
    n = len(text)
    for i, ch in enumerate(text):
        expanded = unicodedata.normalize("NFKC", ch) if "nfkc" in rules else ch
        for c in expanded:
            if "styles" in rules:
                c = _STYLE.get(c, c)
            if "punctuation" in rules:
                prev_digit = i > 0 and text[i - 1].isdigit()
                next_digit = i + 1 < n and text[i + 1].isdigit()
                if c in _IGNORABLE and not (c == "," and prev_digit and next_digit):
                    c = " "
                elif c == "." and not next_digit:
                    c = " "
            for c2 in (c.lower() if "case" in rules else c):
                if c2.isspace():
                    if last_space:
                        continue
                    c2, last_space = " ", True
                else:
                    last_space = False
                out.append(c2)
                index.append(i)
    while out and out[-1] == " ":
        out.pop()
        index.pop()
    return "".join(out), index


@dataclass
class Token:
    text: str
    start: int   # raw offsets
    end: int


def tokens(text: str, rules=ALL_RULES) -> List[Token]:
    norm, index = _normalise(text, rules)
    return [Token(m.group(0), index[m.start()], index[m.end() - 1] + 1)
            for m in _TOKEN.finditer(norm)]


def _is_number(t: str) -> bool:
    return bool(_NUMBER.match(t))


def _is_word(t: str) -> bool:
    return bool(_WORD.match(t))


@dataclass
class Location:
    source: str
    start: int
    end: int
    text: str
    location: Optional[str]
    in_table: bool


@dataclass
class Result:
    state: str
    quote: str
    locations: List[Location] = field(default_factory=list)
    occurrences: int = 0
    normalised: List[str] = field(default_factory=list)     # RULE_NAMES needed for an exact match
    reason: str = ""
    omitted: List[str] = field(default_factory=list)         # related: manuscript text between parts
    check: str = ""
    key: tuple = ()
    focus: Tuple[int, int] = (0, 0)                         # related: raw span of the matched tokens
    table_first_row: str = ""                                # related, in a table: its first extracted row

    @property
    def label(self) -> str:
        return STATE_LABELS[self.state]


class Manuscript:
    """Sources tokenised once, for classifying many quotations."""

    def __init__(self, sources: Dict[str, str]):
        self.sources = {name: body or "" for name, body in (sources or {}).items()}
        self._tokens = {name: tokens(body) for name, body in self.sources.items()}
        self._first: Dict[str, Dict[str, List[int]]] = {}
        for name, toks in self._tokens.items():
            first: Dict[str, List[int]] = {}
            for i, t in enumerate(toks):
                first.setdefault(t.text, []).append(i)
            self._first[name] = first

    # -- exact -------------------------------------------------------------
    def occurrences(self, qtext: Sequence[str]) -> List[Tuple[str, int, int]]:
        found = []
        k = len(qtext)
        for name, toks in self._tokens.items():
            for i in self._first[name].get(qtext[0], []):
                if i + k <= len(toks) and all(toks[i + j].text == qtext[j] for j in range(1, k)):
                    found.append((name, toks[i].start, toks[i + k - 1].end))
        return found

    def _location(self, name: str, start: int, end: int) -> Location:
        body = self.sources[name]
        where, in_table = hea._source_span_location(body, source_start_char=start, source_end_char=end)
        return Location(name, start, end, body[start:end], where, bool(in_table))

    # -- related -----------------------------------------------------------
    def _lines(self, name: str):
        """(line start, line end, token slice) for each line with tokens."""
        body, toks = self.sources[name], self._tokens[name]
        lines, i = [], 0
        while i < len(toks):
            ls = body.rfind("\n", 0, toks[i].start) + 1
            le = body.find("\n", toks[i].start)
            le = len(body) if le < 0 else le
            j = i
            while j < len(toks) and toks[j].start < le:
                j += 1
            lines.append((ls, le, toks[i:j]))
            i = j
        return lines

    def related_lines(self, qtext: Sequence[str]):
        hits = []
        need = set(qtext)
        for name in self.sources:
            for ls, le, line in self._lines(name):
                if not need <= {t.text for t in line}:
                    continue
                align = _align(qtext, [t.text for t in line])
                if align is not None:
                    hits.append((name, ls, le, line, align))
        return hits


def _align(q: Sequence[str], line: Sequence[str]) -> Optional[List[int]]:
    """Positions in line matching q in order, with the fewest breaks (then
    leftmost), or None. A break is a place where matched tokens are not
    adjacent in the line."""
    INF = float("inf")
    m = len(line)
    best = [[INF] * m for _ in q]
    back = [[-1] * m for _ in q]
    for j in range(m):
        if line[j] == q[0]:
            best[0][j] = 0
    for i in range(1, len(q)):
        run_min, run_arg = INF, -1
        for j in range(m):
            # predecessors k <= j - 2 (with one break)
            if j - 2 >= 0 and best[i - 1][j - 2] < run_min:
                run_min, run_arg = best[i - 1][j - 2], j - 2
            if line[j] != q[i]:
                continue
            cont = best[i - 1][j - 1] if j >= 1 else INF
            if cont <= run_min + 1 and cont < INF:
                best[i][j], back[i][j] = cont, j - 1
            elif run_min < INF:
                best[i][j], back[i][j] = run_min + 1, run_arg
    last = min(range(m), key=lambda j: (best[-1][j], j)) if m else None
    if last is None or best[-1][last] == INF:
        return None
    pos = [last]
    for i in range(len(q) - 1, 0, -1):
        pos.append(back[i][pos[-1]])
    return pos[::-1]


def _rules_needed(quote: str, passage: str) -> List[str]:
    """Which documented normalisations the match actually relied on."""
    needed = []
    for rule in ("nfkc", "case", "styles", "punctuation"):
        rules = ALL_RULES - {rule}
        if [t.text for t in tokens(quote, rules)] != [t.text for t in tokens(passage, rules)]:
            needed.append(RULE_NAMES[rule])
    return needed


ABSENCE = ("This does not show that the manuscript lacks the information: extraction can miss "
           "or alter text, so check the manuscript itself.")


def classify(quote: str, manuscript: Manuscript) -> Result:
    quote = (quote or "").strip()
    qtoks = tokens(quote)
    qtext = [t.text for t in qtoks]
    substantive = [t for t in qtext if _is_word(t) or _is_number(t)]
    words = [t for t in qtext if _is_word(t)]
    numbers = [t for t in qtext if _is_number(t)]
    result = Result(NOT_LOCATED, quote, key=("text", tuple(qtext)))
    if not substantive:
        result.reason = "The quotation contains no words or numbers to locate."
        return result
    contiguous = not _NON_CONTIGUOUS.search(quote)

    found = manuscript.occurrences(qtext) if contiguous else []
    if not words:
        result.reason = ("The quotation consists only of numbers and symbols, which cannot establish "
                         "what they refer to, so it is not authenticated or matched to a passage.")
        if found:
            result.reason += (f" The same characters occur at {len(found)} place(s) in the extracted "
                              "manuscript text.")
        result.check = "Find the values in the manuscript and confirm what they describe."
        return result

    short = len(substantive) < MIN_TOKENS
    if found and (not short or (len(found) == 1 and len(words) >= 2)):
        result.state = EXACT
        result.occurrences = len(found)
        # Identity is the span of the matched words and numbers, so quotations
        # that differ only in closing punctuation resolve to the same passage.
        result.key = ("exact", tuple(sorted(found)))
        bare = quote.strip('"\'\u201c\u201d\u2018\u2019\u00ab\u00bb').strip()
        tail = len(bare) - len(bare.rstrip(_CLOSING))
        found = [(name, start, _extend(manuscript.sources[name], end, tail)) for name, start, end in found]
        result.locations = [manuscript._location(*f) for f in found[:MAX_LOCATIONS]]
        result.normalised = _rules_needed(bare, result.locations[0].text)
        if len(found) > 1:
            result.reason = (f"The passage occurs {len(found)} times in the extracted manuscript text; "
                             "the application cannot tell which occurrence the AI meant.")
            result.check = "Confirm which occurrence the finding refers to."
        return result
    if found:  # short and repeated, or short with too few words
        result.reason = (f"The quotation is short ({len(substantive)} words and numbers) and occurs "
                         f"{len(found)} time(s) in the extracted manuscript text; a short phrase "
                         "cannot be attributed to one place reliably." if len(found) > 1 else
                         "The quotation is short and contains fewer than two words, so its single "
                         "occurrence cannot establish what it refers to.")
        result.check = "Find the phrase in the manuscript and confirm which passage the finding means."
        return result

    if numbers:
        hits = manuscript.related_lines(qtext)
        hits = [h for h in hits if h[3] and (_table_row(manuscript, h) or _numbers_anchored(qtext, h[4]))]
        if len(hits) == 1:
            name, ls, le, line, align = hits[0]
            loc = manuscript._location(name, line[0].start, line[-1].end)
            result.state = RELATED
            result.locations = [loc]
            result.occurrences = 1
            body = manuscript.sources[name]
            result.omitted = [body[line[a].end:line[b].start].strip(" \t|,;:")
                              for a, b in zip(align, align[1:]) if b != a + 1]
            result.omitted = [o for o in result.omitted if o]
            result.key = ("related", tuple(qtext), name, ls, le)
            result.focus = (line[align[0]].start, line[align[-1]].end)
            result.reason = ("The quotation's words and numbers all occur, in the same order, on one "
                             "line of the extracted manuscript text, but not as one continuous passage: "
                             "the manuscript has other text between them, shown with this entry. The AI's "
                             "quotation is therefore not the manuscript's wording.")
            if loc.in_table:
                result.table_first_row = _first_table_row(body, ls)
                result.check = ("Check in the manuscript which column, group and time point each value "
                                "in the quotation belongs to, and whether the finding uses the right "
                                "ones. That the line was located is not evidence that the AI's "
                                "statistical interpretation is correct.")
            else:
                result.check = ("Check whether the text the quotation leaves out changes its meaning, "
                                "and whether the finding's reading of the passage is correct. That the "
                                "line was located is not evidence that the interpretation is correct.")
            return result
        if len(hits) > 1:
            result.reason = (f"{len(hits)} lines of the extracted manuscript text contain the quotation's "
                             "words and numbers in order, so no single passage can be identified "
                             "(repeated labels or values could belong to different tables or "
                             "conditions).")
            result.check = "Find the passage in the manuscript and confirm which one the finding means."
            return result

    if not contiguous:
        result.reason = ("The quotation contains an ellipsis or a bracketed insertion, so it is not one "
                         "continuous passage, and no single line contains all of it.")
    else:
        result.reason = "Not found in the extracted manuscript text as one continuous passage."
    result.reason += " " + ABSENCE
    result.check = "Search the manuscript for this wording before relying on the finding."
    return result


_CLOSING = ".,;:!?)]"


def _extend(body: str, end: int, count: int) -> int:
    """Include up to count closing punctuation marks that directly follow a
    matched passage, when the quotation itself ends with punctuation, so the
    passage is shown as the manuscript punctuates it."""
    while count > 0 and end < len(body) and body[end] in _CLOSING:
        end += 1
        count -= 1
    return end


_TABLE_META = re.compile(r"^(?:Source|Label|Caption|Title|Page)\s*:", re.I)


def _first_table_row(body: str, line_start: int) -> str:
    """The first row of the explicit table containing the line, as extracted
    (usually its column headings), or "" when it is the line itself or no
    table marker encloses it. Shown only to help the reviewer read columns."""
    start = body.rfind("[TABLE_START]", 0, line_start)
    if start < 0 or body.rfind("[TABLE_END]", start, line_start) >= 0:
        return ""
    pos = body.find("\n", start) + 1
    while 0 < pos < line_start:
        end = body.find("\n", pos)
        end = len(body) if end < 0 else end
        row = body[pos:end].strip()
        if row and not _TABLE_META.match(row) and set(row) - set("|-: "):
            return row
        pos = end + 1
    return ""


def _table_row(manuscript: Manuscript, hit) -> bool:
    name, ls, le, line, _ = hit
    _, in_table = hea._source_span_location(manuscript.sources[name],
                                            source_start_char=line[0].start,
                                            source_end_char=line[-1].end)
    return bool(in_table)


def _numbers_anchored(qtext: Sequence[str], align: Sequence[int]) -> bool:
    """Outside tables, every number must sit next to a neighbouring quotation
    token exactly as the quotation places it."""
    for i, t in enumerate(qtext):
        if not _is_number(t):
            continue
        left = i > 0 and align[i] == align[i - 1] + 1
        right = i + 1 < len(qtext) and align[i + 1] == align[i] + 1
        if not (left or right):
            return False
    return True
