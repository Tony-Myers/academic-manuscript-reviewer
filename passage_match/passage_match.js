// Exact passage location in a PDF.js text layer. Pure functions, no DOM, no
// network: input is PDF.js getTextContent() items per page, output is the
// item/character ranges of a unique exact match, or a reason why there is
// none. Fictional-safe and side-effect free. Intended to be inlined into
// app/document_viewer.html (function by function, like the other harnesses).
//
// Normalisation is deliberately narrow. It only removes differences that
// carry no meaning for a reader:
//   - ligature glyphs (ﬁ, ﬂ, ﬀ, ﬃ, ﬄ, ﬅ, ﬆ) become their letters;
//   - curly and straight quotation marks are unified;
//   - runs of whitespace (including line breaks and no-break spaces) are one space;
//   - soft hyphens are dropped;
//   - a hyphen at a line end may join the word ("exer-\ncise" = "exercise" or "exer-cise");
//   - one space in the quotation may stand for a boundary between two PDF text
//     items on the same line where one item is a superscript or subscript (a
//     different font size) and the PDF has no space: extracted text writes the
//     chi-square symbol and its raised "2" as "χ 2(2)", PDF.js as "χ" + "2" + "(2)".
//     No character is added, removed or substituted; only that space is optional.
// Everything else must match exactly, including case, digits, decimal points,
// commas, signs and inequalities. Hyphen-minus "-" and the minus sign "−"
// are one class (PDF text and extracted text routinely swap them); the en
// dash "–" and em dash "—" each match only themselves, so a missing-value
// dash is never read as a minus sign or the reverse.

const LIGATURES = { 'ﬀ': 'ff', 'ﬁ': 'fi', 'ﬂ': 'fl', 'ﬃ': 'ffi', 'ﬄ': 'ffl', 'ﬅ': 'st', 'ﬆ': 'st' };
const QUOTES = { '‘': "'", '’': "'", '‚': "'", '‛': "'", '′': "'",
                 '“': '"', '”': '"', '„': '"', '‟': '"', '″': '"' };
const MINUS_CLASS = new Set(['-', '−', '‐', '‑']);   // hyphen-minus, minus sign, hyphen, non-breaking hyphen
const SPACE_RE = /[\s  -​  　]/;

function canonChar(ch) {
  if (LIGATURES[ch]) return LIGATURES[ch];
  if (QUOTES[ch]) return QUOTES[ch];
  if (MINUS_CLASS.has(ch)) return '-';
  return ch;
}

// The quote as a canonical string (whitespace collapsed, soft hyphens gone).
function canonQuote(text) {
  let out = '', space = false;
  for (const ch of String(text || '')) {
    if (ch === '­') continue;
    if (SPACE_RE.test(ch)) { space = out.length > 0; continue; }
    if (space) { out += ' '; space = false; }
    out += canonChar(ch);
  }
  return out;
}

// Marginal line numbers: short all-digit items that sit left of the page's
// body text. Only used when the review recorded that line numbers were
// removed from the manuscript text, and never inside a line.
function lineNumberItems(items) {
  const xs = items.filter(it => it.str && /\S/.test(it.str) && !/^\d{1,4}$/.test(it.str.trim()))
                  .map(it => (it.transform ? it.transform[4] : 0));
  if (!xs.length) return new Set();
  const bodyLeft = Math.min(...xs);
  const skip = new Set();
  items.forEach((it, i) => {
    if (it.transform && /^\d{1,4}$/.test((it.str || '').trim()) && it.transform[4] < bodyLeft - 2) skip.add(i);
  });
  return skip;
}

// One page as canonical characters, each mapped back to [item index, char offset].
// Line breaks are recorded so hyphenation can be undone only at a real line end.
// Font size of an item (vertical scale of its transform), or null if unknown.
function itemSize(it) {
  const t = it && it.transform;
  if (!t || t.length < 4) return null;
  const h = Math.hypot(t[2], t[3]);
  return h > 0 ? h : null;
}

// True when items a and b sit on one line and one of them is a superscript or
// subscript of the other: sizes differ by at least 15 % and b starts within
// half a line of a vertically (raised or lowered, not a new line).
function scriptBoundary(a, b) {
  const sa = itemSize(a), sb = itemSize(b);
  if (!sa || !sb || a.hasEOL) return false;
  const small = Math.min(sa, sb), large = Math.max(sa, sb);
  if (small / large > 0.85) return false;
  return Math.abs(a.transform[5] - b.transform[5]) < 0.6 * large;
}

function buildPageIndex(items, opts = {}) {
  const skip = opts.skipLineNumbers ? lineNumberItems(items) : new Set();
  const chars = [];      // { c, item, off, eol, script }
  let pendingSpace = false, pendingEol = false, prevItem = null;
  items.forEach((it, i) => {
    if (skip.has(i)) { pendingSpace = true; pendingEol = true; prevItem = null; return; }
    const s = it.str || '';
    // A script boundary with no space between the items in the PDF.
    let script = false;
    if (s) {
      script = !pendingSpace && prevItem !== null && chars.length > 0 && scriptBoundary(prevItem, it);
      prevItem = it;
    }
    let off = 0;
    for (const ch of s) {
      const len = ch.length;
      if (ch === '­') { off += len; continue; }
      if (SPACE_RE.test(ch)) { pendingSpace = chars.length > 0; script = false; off += len; continue; }
      if (pendingSpace) { chars.push({ c: ' ', item: -1, off: -1, eol: pendingEol }); pendingSpace = false; pendingEol = false; script = false; }
      for (const c of canonChar(ch)) { chars.push({ c, item: i, off, len, eol: false, script }); script = false; }
      off += len;
    }
    if (it.hasEOL) { pendingSpace = chars.length > 0; pendingEol = true; }
  });
  return chars;
}

// All exact matches of the quote in one page index. A match may skip the
// line-break whitespace after a hyphen that ends a line ("exer- cise"), or the
// hyphen and that whitespace together ("exercise"); nothing else is skipped.
function findAll(index, quote) {
  const q = canonQuote(quote);
  const out = [];
  if (!q) return out;
  const n = index.length;
  const isLetter = c => /\p{L}/u.test(c || '');
  for (let s = 0; s < n; s++) {
    if (index[s].c !== q[0] || index[s].c === ' ') continue;
    let i = s, j = 0;
    while (j < q.length && i < n) {
      const pc = index[i].c, qc = q[j];
      if (pc === qc) { i++; j++; continue; }
      // A quotation space at a superscript/subscript boundary that has no space in the PDF.
      if (qc === ' ' && index[i].script && j > 0 && q[j + 1] === pc) { j++; continue; }
      // Line-end hyphenation in the PDF: letter "-" <line break> letter.
      if (pc === '-' && i + 2 < n && index[i + 1].c === ' ' && index[i + 1].eol
          && isLetter(index[i - 1] && index[i - 1].c) && isLetter(index[i + 2].c)) {
        if (isLetter(qc) && qc === index[i + 2].c) { i += 2; continue; }        // "exercise"
      }
      if (pc === ' ' && index[i].eol && i > 0 && index[i - 1].c === '-' && qc === index[i + 1]?.c
          && j > 0 && q[j - 1] === '-') { i += 1; continue; }                     // "exer-cise"
      break;
    }
    if (j === q.length) {
      // Never start or end inside a word or a number: "0.41" must not match
      // inside "-0.41", nor "p < 0.0" inside "p < 0.001".
      const before = s > 0 ? index[s - 1].c : '';
      const after = i < n ? index[i].c : '';
      const alnum = c => /[\p{L}\p{N}]/u.test(c || '');
      if (alnum(q[0]) && (alnum(before) || (/\p{N}/u.test(q[0]) && (before === '-' || before === '.')))) continue;
      if (alnum(q[q.length - 1]) && (alnum(after) || (after === '.' && /\p{N}/u.test(index[i + 1]?.c || '')))) continue;
      const first = index[s];
      let last = index[i - 1];
      out.push({ start: s, end: i, first: { item: first.item, off: first.off },
                 last: { item: last.item, off: last.off + (last.len || 1) } });
    }
  }
  return out;
}

// Locate a quotation in one document.
//   pages: [{ page: 1-based number, items: PDF.js text items }]
//   hintPage: the page the application recorded for the quotation, or null.
// Returns { status: 'exact', page, ranges, disambiguatedByHint }
//      or { status: 'ambiguous' | 'not_found' | 'no_text_layer', reason }.
// A unique match anywhere in the document is accepted. Several matches are
// accepted only if exactly one of them is on the hinted page.
function locatePassage(pages, quote, hintPage = null, opts = {}) {
  const q = canonQuote(quote);
  if (!q) return { status: 'not_found', reason: 'The quotation is empty.' };
  if (!pages.some(p => (p.items || []).some(it => /\S/.test(it.str || ''))))
    return { status: 'no_text_layer', reason: 'This PDF has no text layer (it may be a scanned image), so passages cannot be located in it.' };
  const matches = [];
  for (const p of pages) {
    const index = buildPageIndex(p.items || [], opts);
    for (const m of findAll(index, q)) matches.push({ page: p.page, ...m });
  }
  // A passage running over a page break: search each adjacent pair joined.
  for (let k = 0; k + 1 < pages.length; k++) {
    const a = pages[k], b = pages[k + 1];
    const ia = buildPageIndex(a.items || [], opts), ib = buildPageIndex(b.items || [], opts);
    const joined = ia.concat([{ c: ' ', item: -1, off: -1, eol: true }], ib.map(ch => ({ ...ch, item: ch.item < 0 ? -1 : ch.item + 1e6 })));
    for (const m of findAll(joined, q)) {
      if (m.first.item < 1e6 && m.last.item >= 1e6) matches.push({ page: a.page, spansTo: b.page, ...m });
    }
  }
  if (!matches.length)
    return { status: 'not_found', reason: 'This passage could not be located exactly in the PDF text, so it is not highlighted.' };
  let chosen = null, byHint = false;
  if (matches.length === 1) chosen = matches[0];
  else if (hintPage != null) {
    const onHint = matches.filter(m => m.page === hintPage && !m.spansTo);
    if (onHint.length === 1) { chosen = onHint[0]; byHint = true; }
  }
  if (!chosen)
    return { status: 'ambiguous', count: matches.length,
             reason: `This passage occurs ${matches.length} times in the PDF text` +
                     (hintPage != null ? ` and not exactly once on page ${hintPage}` : '') +
                     ', so it cannot be highlighted unambiguously.' };
  const ranges = [];
  const split = m => {
    if (!m.spansTo) return [{ page: m.page, first: m.first, last: m.last }];
    const pa = pages.find(p => p.page === m.page), pa_items = (pa.items || []).length;
    return [{ page: m.page, first: m.first, last: { item: pa_items - 1, off: (pa.items[pa_items - 1].str || '').length } },
            { page: m.spansTo, first: { item: 0, off: 0 }, last: { item: m.last.item - 1e6, off: m.last.off } }];
  };
  ranges.push(...split(chosen));
  return { status: 'exact', page: chosen.page, ranges, disambiguatedByHint: byHint };
}

// The rendered text-layer elements for each text item. PDF.js does not
// promise one element per item (empty items are skipped and items may be
// merged or split), so items are aligned to elements by their text, in
// order. Returns an array: item index -> { el, start } or null.
function alignItemsToSpans(items, spanTexts) {
  const map = new Array(items.length).fill(null);
  let k = 0, used = 0;                       // element index, characters used in it
  for (let i = 0; i < items.length; i++) {
    const s = items[i].str || '';
    if (!s) continue;
    while (k < spanTexts.length && used >= spanTexts[k].length) { k++; used = 0; }
    if (k >= spanTexts.length) break;
    const rest = spanTexts[k].slice(used);
    if (rest.startsWith(s)) { map[i] = { el: k, start: used }; used += s.length; }
    else if (s.startsWith(rest) || !rest.includes(s)) {
      // Element text does not continue with this item: resynchronise by search.
      const at = spanTexts.findIndex((t, idx) => idx >= k && t.includes(s));
      if (at < 0) continue;
      k = at; used = spanTexts[k].indexOf(s);
      map[i] = { el: k, start: used }; used += s.length;
    } else { map[i] = { el: k, start: used + rest.indexOf(s) }; used += rest.indexOf(s) + s.length; }
  }
  return map;
}

if (typeof module !== 'undefined') module.exports = { canonQuote, buildPageIndex, findAll, locatePassage, alignItemsToSpans, lineNumberItems };
