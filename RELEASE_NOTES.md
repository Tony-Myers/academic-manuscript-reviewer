# Release notes

## 0.1.1 — maintenance release candidate (not released)

- Start non-Thinking chunk review at 1,800 tokens instead of 900. Preserve
  the existing recovery mechanism and Thinking-mode token settings.
- Use the existing conservative quotation matcher consistently in appraisal
  labels, Evidence Cards and source verification. Changed numbers, signs,
  operators and omitted table cells do not authenticate as exact quotations.
- Recognise numbered strengths, concerns and verification questions while
  preserving their original text and source positions.
- Check the expected versus served checkpoint before and during API review
  execution. Missing, ambiguous or inconsistent identity stops the review;
  optional Vision or verification handling cannot silently bypass a failure.

Quotation authentication establishes wording and location, not evidential
support or methodological correctness. Existing saved reviews and reviewer
choices are not migrated. The original model verdict remains in provenance.
No experimental synthesis/statistics features or new runtime dependencies
are included. Model choices, sampling and launch settings remain unchanged.

Compatibility: checkpoint identity must be reported consistently by the local
server. Matching a filename alone does not confirm a full checkpoint path or
revision. Managed reviews use the currently configured/browser-loaded target;
external reviews pin the reported checkpoint when the review is created. This
update does not add persistent model preferences across restarts or support
ambiguous multi-model routers. The guard applies to the manuscript-review API
worker and its requests; it is not a general authentication layer for direct
backend calls or the standalone CLI.

The token allowance change is an operational change, not a demonstrated
methodological-accuracy improvement. Full live-model inference and cross-platform
validation have not been performed. A successful read-only checkpoint-identity
check is a prerequisite for the maintenance commit; it does not establish
live inference, Vision or methodological compatibility. Publication remains
pending approval.

## 0.1.0 — first public source release

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
