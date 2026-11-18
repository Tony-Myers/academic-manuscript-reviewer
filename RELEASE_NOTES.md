# Release notes

## 0.1.0 — first public source release (proposed; not yet published)

A local research tool that helps a human reviewer appraise an academic
manuscript with a locally hosted language model. Every finding it produces is
AI-generated and provisional; the reviewer remains responsible for the review.

### Included

- Critical Appraisal, Evidence Cards with Retain / Revise / Dismiss decisions,
  and a Human Evidence Appendix, all generated from a locally saved review.
- Human Evidence Appendix: every AI quotation is shown as an exact quotation
  authenticated, a related manuscript passage (quotation not authenticated) or
  a quotation not located, by deterministic rules documented in the README;
  passages cited more than once for a finding are shown once with every citation.
- Dedicated print pages (Save as PDF) for the Critical Appraisal, the Human
  Evidence Appendix and the Evidence Cards (summary or detailed).
- Reviewer-summary and full-audit Markdown exports of the saved decisions.
- Managed or external llama.cpp `llama-server`; model switching without
  restarting the app; `restart-app` to restart the app without reloading the model.
- Configurable review store (`QWEN_REVIEW_STORE`); a missing store is reported
  rather than shown as empty.
- Reviews saved by earlier versions open without re-running the model.

### Known limitations

- Output quality depends on the model; no model has been validated for
  manuscript appraisal. Locating a passage does not show that the AI's reading
  of it is correct.
- Automated tests run on Linux; macOS (Apple Silicon) use has been checked by
  hand only. Windows is not supported.
- Print layout is tested automatically in Chromium only; Safari printing was
  checked by hand.
- The application has no authentication; bind it to loopback.

### Licence

Apache License 2.0 for the application code; CC BY 4.0 for the reviewer notes;
third-party components under their own licences (see `LICENSING.md`).
