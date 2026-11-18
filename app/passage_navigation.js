/* Same-origin navigation, never put quotation text in URLs or browser history.
 * "Show in manuscript" / "Clear highlight" is a two-state toggle. The PDF
 * viewer owns the highlight; these buttons only mirror what it announces. */
(function () {
  function valid(t) {
    return t && /^[0-9a-f]{12}$/.test(t.job || '') && /^d\d{1,2}$/.test(t.doc || '')
      && /^[0-9a-f]{64}$/.test(t.sha256 || '') && typeof t.quote === 'string' && t.quote.length > 0;
  }
  // Must equal passageKey() in the viewer and manuscriptPassageKey() in chat.html.
  function key(t) {
    return t ? [t.job, t.doc, t.sha256, t.page == null ? '' : String(t.page), t.quote].join('\u0000') : null;
  }
  let active = null, popup = null;
  function sync(k) {
    active = k || null;
    document.querySelectorAll('.show-manuscript').forEach(b => {
      let on = false;
      try { on = active !== null && key(JSON.parse(b.dataset.passage)) === active; } catch (e) {}
      b.textContent = on ? 'Clear highlight' : 'Show in manuscript';
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
  }
  function embedded() {
    try {
      return window.parent !== window && window.parent.location.origin === location.origin
        && typeof window.parent.showManuscriptPassage === 'function';
    } catch (e) { return false; }
  }
  function clear() {
    if (embedded() && typeof window.parent.clearManuscriptPassage === 'function') {
      window.parent.clearManuscriptPassage(); return true;
    }
    if (popup && !popup.closed) { popup.postMessage({ type: 'review-viewer:clear-passage' }, location.origin); return true; }
    sync(null); return false;
  }
  function show(t) {
    if (!valid(t)) return false;
    if (embedded()) return window.parent.showManuscriptPassage(t);
    if (popup && !popup.closed) {
      popup.postMessage({ type: 'review-viewer:passage', target: t }, location.origin);
      popup.focus(); return true;
    }
    const url = '/review/document-viewer#job=' + t.job + '&doc=' + t.doc;
    const w = window.open(url, '_blank');
    if (!w) { window.alert('Allow this local manuscript viewer to open, then try again.'); return false; }
    popup = w;
    // The viewer signals readiness after installing its API (no timing guesses).
    const receive = e => {
      if (e.origin !== location.origin || e.source !== w || e.data?.type !== 'review-viewer:ready') return;
      window.removeEventListener('message', receive);
      w.postMessage({ type: 'review-viewer:passage', target: t }, location.origin);
    };
    window.addEventListener('message', receive);
    setTimeout(() => window.removeEventListener('message', receive), 60000);
    return true;
  }
  // State announced by a viewer this page opened (embedded pages are synced by the parent).
  window.addEventListener('message', e => {
    if (e.origin !== location.origin || !popup || e.source !== popup
        || e.data?.type !== 'review-viewer:passage-state') return;
    sync(e.data.active);
  });
  document.addEventListener('click', e => {
    const b = e.target.closest('.show-manuscript'); if (!b) return;
    const t = JSON.parse(b.dataset.passage);
    if (active !== null && key(t) === active) clear(); else show(t);
  });
  // Pick up the current state when the cards page loads inside the workspace.
  try {
    if (embedded() && typeof window.parent.currentManuscriptPassage === 'function') sync(window.parent.currentManuscriptPassage());
  } catch (e) {}
  window.ReviewPassages = { show, clear, sync, valid, key };
})();
