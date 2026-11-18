# Test and fixture provenance

All tests in this directory were authored for this release candidate. No prior
application test files, manuscript excerpts, author responses or generated review
records were imported.

| File | Input and expected-output origin | Classification |
| --- | --- | --- |
| fixtures.py | Independently invented ceramic-tile bench, authored appraisal, scripted verification verdicts and hand-built PDF bytes. | Independently synthetic |
| test_release.py | Uses those fixtures plus original malformed JSON, integrity mutations and local request/response protocol examples. Assertions follow application API contracts. | Independently synthetic / generic technical |
| ui_contracts.cjs | Original DOM stubs, literal Markdown, synthetic PDF.js text items and hand-written server-status records; tests real UI functions and passage matcher. | Independently synthetic / generic technical |
| test_model_switching.py | Placeholder files with invented model names (alpha-, beta-, gamma-synthetic and similar), hand-written llama-server protocol replies, scripted service-script output, and a fake llama-server defined in the test that serves fixed JSON on a free loopback port. No model is loaded and no manuscript, review or model output is used. | Independently synthetic / generic technical |
| test_presentation_consistency.py | Short invented materials-bench appraisal texts written in the test in five formatting variants, and hand-written verifier records (including an invented disputed strength). No model is called; no manuscript, review or model output is used. | Independently synthetic |
| test_decision_exports.py | The fictional materials-bench cards from fixtures.py, with reviewer decisions, comments and revised wording invented in the test. No model is called; no manuscript, review or model output is used. | Independently synthetic |
| test_historical_reviews.py | Invented materials-bench appraisals, including a bold-marker appraisal and a synthetic appendix shaped like earlier application output, an invented initial-reading observation record, and invented decisions; saved to a temporary store. No model is called; no manuscript, review or model output is used. | Independently synthetic |
| test_installation.py | Reads the application source and requirement files and runs scripts/check_install.py, once with a package made absent. No fixtures, model or network. | Generic technical |
| test_vision_status.py | Hand-written llama-server replies for invented models (alpha-, beta-synthetic) and placeholder image bytes; the test record is written to a temporary file. No model, manuscript or model output is used. | Independently synthetic / generic technical |
| test_evidence_presentation.py | Invented paged and unpaged bench texts, an invented appraisal (including Markdown and unsafe-looking text), scripted verifier replies and an invented AI summary in a synthetic trace. No model, manuscript or review data. | Independently synthetic |
| test_configuration.py | Runs scripts/qwen_service.sh in a temporary project with a stand-in interpreter that records the environment the app would receive; temporary store paths, including one with spaces and missing ones. Checks script syntax and permissions. | Generic technical |
| test_print_layout.py | The fictional bench cards with invented long findings and reviewer wording; prints through a local Chromium only where one is installed, otherwise skipped. | Independently synthetic / generic technical |
| test_print_view.py | The fictional bench cards with invented long findings, evidence passages and reviewer wording (including unsafe-looking text); endpoint checks with a temporary store; prints through a local Chromium only where one is installed. | Independently synthetic / generic technical |
| test_print_pages.py | Invented bench appraisals with long sections, headings, nested lists, tables and unsafe-looking text, saved to a temporary store; prints through a local Chromium only where one is installed. | Independently synthetic / generic technical |
| test_quotation_states.py | An invented trial text (prose on several pages and an invented functional-screen table with made-up values), invented appraisals and scripted verifier replies. The hurdle-step case reproduces only the structure of a reported problem (a quotation that omits one column of a table row); its values are invented. | Independently synthetic |
| test_extraction_and_classification.py | Synthetic sentences, variable names and values that exercise the text clean-up rules, method-class detection and the appraisal prompt's examples; no manuscript wording. | Independently synthetic |
| pdfjs_read.mjs | Reads the newly generated PDF through the bundled PDF.js; expected strings come only from fixtures.py. | Independently synthetic / generic technical |

No third-party manuscript or research-study test corpus is included. Expected
model responses are hand-authored, not results of model inference. Fictional
values test formatting and program flow; they do not validate methodological
interpretation or model accuracy. The public suite does not contain a private
exclusion register or source-comparison records.
