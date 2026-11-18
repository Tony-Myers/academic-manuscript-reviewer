# Academic Manuscript Reviewer

A local assistant for academic manuscript reviewers. It produces a manuscript-grounded
Critical Appraisal, Evidence Cards and a Human Evidence Appendix that help a human
inspect findings alongside the original PDF. It is a research tool, not an automated
peer reviewer or a validated authority on statistical methodology. It is provided
under the Apache License 2.0 without warranty of any kind (see [Licensing](#licensing)):
no claim is made that its findings are complete, correct or suitable for any
particular review.

## Intended role

- The application assists human peer reviewers; it does not review manuscripts
  on its own.
- Every AI-generated finding, suggested check and verifier note is provisional.
  Each needs the reviewer's evaluation before it is used.
- Finding a quoted passage in the manuscript shows that the passage exists. It
  does not show that the AI read it correctly or that its methodological
  conclusion is right.
- The reviewer remains responsible for evaluating the manuscript and for the
  content of the final report.
- Any llama.cpp-compatible model can be used. Being able to load a model does
  not mean it appraises manuscripts equally well; output quality differs
  between models and has not been shown to be equivalent.

## Features

- General manuscript-grounded appraisal, without predetermined method/design routing.
- Thinking (Medium effort by default), Instruct and synthesis-only Thinking options.
- Vision-assisted page/table extraction when a compatible local model and projector are available.
- Critical Appraisal with technical and verification information collapsed by default.
- Evidence Cards showing original findings, located passages, suggested checks and uncertainty.
- Human Evidence Appendix and local saved reviews, including original documents.
- Split-screen PDF viewing, finding links and passage highlighting where text can be matched.
- Retain, Revise and Dismiss decisions, stored separately from the generated appraisal.
- Markdown review/appendix exports; decision exports as a concise reviewer summary, a full audit record (Markdown) or JSON; card JSON and diagnostic JSON.
- Development mode retaining additional local trace information for inspection.
- Academic Chat, with structured drafts, methodological guidance and optional reference/source checks.

## Requirements and installation

- Python 3.10 or newer (the test suite has been run with 3.10 and 3.13).
- A llama.cpp `llama-server` build that supports your model, and a GGUF model
  file; sufficient memory for that model. Optional MLX configurations exist but
  are not part of the release validation.
- `bash`, `curl`, `lsof` and `ps` for the launcher scripts; Node.js only for the
  JavaScript checks.

**Platforms.** The application is developed and used on macOS (Apple Silicon),
where the launchers, Safari and the print pages have been checked by hand. The
automated tests were run on Linux (Python 3.10 and 3.13; the print-page PDF
tests in Chromium). Linux therefore has automated coverage only, and macOS has
manual checks only for the steps listed under [Testing](#testing). Windows is
not supported: the launchers are Bash scripts. Model weights and projectors are
not distributed here; actual architecture, chat-template and image support
depend on your installed model and server versions.

```bash
cd /path/to/academic-manuscript-reviewer-release
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
# Optional page rendering for Vision-assisted extraction:
.venv/bin/pip install -r requirements-vision.txt
# Offline tests, including mocked API transport:
.venv/bin/pip install -r requirements-test.txt
# Confirm the environment can run the app (no model is loaded):
.venv/bin/python scripts/check_install.py
```

`scripts/check_install.py` checks every package the app imports at start-up
and then imports the app itself; the launchers run it before starting and name
any missing package. If a launcher reports "Permission denied", restore the
executable bits with `chmod +x run_review.sh start_server.sh start_llama_server.sh scripts/*.sh scripts/*.py`.

Install llama.cpp separately from its official project or your package manager.
MLX users need compatible `mlx` and `mlx-lm` packages; that optional backend is
not part of the offline release validation. Node.js is needed for JavaScript
checks; no npm packages or browser CDN are required.

## Configuration and running

The app works with a llama.cpp `llama-server` and any GGUF model that server can
load. Qwen models appear in the examples and built-in aliases because the
application was developed with them; they are an example configuration, not a
requirement. No Python code needs editing to use or switch models.

Copy `local.env.example` to `local.env` and choose one of two ways of running
the model server. Every setting in `local.env` is exported to the app. The
example contains no machine-specific model path. Existing short aliases are
retained for compatibility; their versioned home-relative cache paths may not
exist on your machine.

### Review store

Completed reviews are saved in `reviews/sessions` in this folder unless
`QWEN_REVIEW_STORE` names another folder (paths with spaces are fine;
`off` saves nothing). The app log and `./scripts/qwen_service.sh status` name
the store in use. A configured store is used exactly as given: if it does not
exist (for example, its drive is not connected), the log, the Saved Reviews
panel and `/api/reviews` say so instead of showing an empty list, and the
default store is not used in its place. A configured folder is created on the
first save only if its parent folder exists; otherwise the save is refused and
the reason is shown in the Saved Reviews panel, so export the review before
closing it. Saved reviews contain manuscript text and are confidential local
records.

### Starting, stopping and restarting

```bash
./scripts/qwen_service.sh start [--no-open]   # model server (managed mode) and app
./scripts/qwen_service.sh status
./scripts/qwen_service.sh restart-app         # app only; the model stays loaded
./scripts/qwen_service.sh restart             # both (reloads a managed model)
./scripts/qwen_service.sh stop
```

Use `restart-app` after updating the application: it stops and starts only
the app server, so a large model is not reloaded. In external mode no command
here starts, stops or restarts your llama-server.

### Managed llama-server (the app's launcher starts it)

Set `QWEN_MODEL` to your GGUF file and `LLAMA_SERVER_BIN` to your llama-server
executable, then:

```bash
./scripts/qwen_service.sh start --no-open
./scripts/qwen_service.sh status
./scripts/qwen_service.sh stop
```

The managed interface defaults to http://127.0.0.1:8090 and the model server to
127.0.0.1:8081. `start_server.sh` offers the single-terminal alternative, while
`run_review.sh` invokes the CLI. Use distinct ports if you run another instance.

The launchers stop only a llama-server whose process they recorded themselves
(`run/llama-server.pid`, checked against the process command line). A server
started any other way is never stopped: a launcher that finds one on its port
reuses it and treats it as external, and warns if it holds a different model.
`start_server.sh` likewise frees its app port only if this app's own `server.py`
holds it, and otherwise refuses to start.

### External llama-server (you start it)

Start llama-server yourself with the model you want, for example:

```bash
llama-server --model /path/to/model.gguf --host 127.0.0.1 --port 8081 \
    --ctx-size 32768 --n-gpu-layers 99 --jinja
```

(`./start_llama_server.sh --model /path/to/model.gguf` runs the same command.)
Then set in `local.env`:

```bash
: "${LLAMA_SERVER_MODE:=external}"
: "${LLAMA_SERVER_URL:=http://127.0.0.1:8081}"
```

and start the app as usual with `./scripts/qwen_service.sh start` or
`./start_server.sh`. For Vision, start llama-server with the model's projector
as well (`--mmproj /path/to/mmproj.gguf`, plus any image-token flags your build
supports): in external mode the app cannot add flags. In external mode the app only connects: it reads the loaded
model's name from the server (`/props`, then `/v1/models`), needs no local copy
of the model file, and never starts, stops or restarts the server. The model
selector shows the reported model and the Restart button is hidden. If the
server is not running when the app starts, the app still starts, reports the
server as unreachable, and connects once the server answers.

### Switching models

- **Managed:** choose a model in the selector and press **Restart**. For a
  GGUF model the app stays running while its launcher stops the llama-server
  it started and loads the new file with the same port, context size and
  flags. The header shows *Loading*, then either the model the server reports
  or *Model failed to load* with the reason. A switch is reported as complete
  only after the server answers ready and reports the requested file (or, if
  it reports no name, says so). Reviews cannot be started while a model is
  loading (the app refuses them), and the Review button stays disabled after a
  failed switch until a model has loaded. If loading fails
  the previous model is not reloaded automatically; choose a working model and
  press Restart. Changing between an MLX model and a GGUF model restarts the
  whole app, which requires it to have been started with
  `scripts/qwen_service.sh`.
- **Active work is never interrupted.** A switch is refused while a manuscript
  appraisal (including its evidence verification), an Academic Chat answer, a
  question about a review or any other model generation is in progress. Let it
  finish, or cancel the appraisal, then switch. While a model loads, new model
  work is refused until it has loaded.
- **External:** stop your llama-server and start it again with the other
  model. The header updates to the newly reported model within about 15
  seconds; no restart of the app is needed.
- **Command line:** `./scripts/qwen_service.sh switch-model --model /path/to/model.gguf`
  does the same as the managed Restart button.

The selector lists built-in aliases whose files exist, the current model, and
any GGUF files found under `LLAMA_MODEL_DIRS` (multimodal projector files and
all but the first shard of a split model are left out). Adding a directory there
is how new models are offered; no code changes are needed. Keep each model in
its own folder with only its own projector: managed launchers load the first
`*mmproj*.gguf` beside the model file, which in a shared folder may belong to a
different model.

### Diagnosing connection failures

The header distinguishes these cases:

| Header | Meaning | What to check |
| --- | --- | --- |
| *App not reachable* | The browser cannot reach the reviewer app itself. | `./scripts/qwen_service.sh status`, `logs/app-server.log`; the page address and `QWEN_APP_PORT`. Safari reports such failed requests as "Load failed". |
| *Server unreachable (managed/external server)* | The app runs but nothing answers at the llama-server address. | `LLAMA_SERVER_URL` or `LLAMA_SERVER_PORT`; whether llama-server is running; `logs/llama-server.log` (managed). |
| *Loading ...* | llama-server is reading a model (HTTP 503 from `/health`). | Large models can take minutes; `QWEN_STARTUP_TIMEOUT` sets the limit. |
| *Model failed to load* | The managed switch failed; hover for the script's output. | Commonly a llama.cpp build without the model's architecture (set `LLAMA_SERVER_BIN`), a flag the build does not support, a missing file, or a port held by another process. |
| *model not reported* | Connected, but the server did not name its model. | Report headers then say the model was not reported rather than guessing. |

`./scripts/qwen_service.sh doctor` checks the environment, and
`./scripts/qwen_service.sh logs llama` follows the model-server log.

| Setting | Meaning |
| --- | --- |
| `QWEN_MODEL` | Model path/alias used by launchers in managed mode; launcher passes the resolved model to the app. Informational only in external mode. |
| `MODEL_NAME` | Direct Python/CLI default when not using a launcher. |
| `LLAMA_SERVER_MODE` | `managed` (default for the launchers) or `external`. |
| `LLAMA_SERVER_URL` | Address of an external llama-server. In managed mode the address is built from host and port. |
| `LLAMA_MODEL_DIRS` | Directories (separated by `:`) searched for GGUF files to offer in the selector. |
| `LLAMA_SERVER_BIN` | Compatible llama-server executable. |
| `LLAMA_SERVER_EXTRA_ARGS` | Extra llama-server flags for every managed start. |
| `QWEN_APP_PORT`, `LLAMA_SERVER_PORT` | Managed app and model ports. |
| `LLAMA_SERVER_CTX` | Context size; must fit the model and available memory. |
| `QWEN_STARTUP_TIMEOUT` | Seconds to wait for a managed model to load (default 600). |
| `QWEN_REVIEW_THINKING` | Default for API reviews with no explicit thinking choice. |
| `LLAMA_REASONING_EFFORT` | Override Medium with low/medium/high/xhigh; template/default leaves it to the server. |
| `REVIEW_PASSES` | Instruct synthesis repeats; the service defaults to three. |
| `QWEN_THINKING_PASSES` | Thinking synthesis normally caps at one pass. |
| `QWEN_VISION_TABLES` | Default Vision selection; service defaults to off. |
| `QWEN_REVIEW_STORE` | Saved-session directory; `off` disables persistence in the normal launcher. |
| `QWEN_CONTACT_URL` | Optional contact (a URL or `mailto:` address) added to the User-Agent sent to Crossref and OpenAlex by Academic Chat's reference checks. Unset: none is sent. |

Per-review Thinking/Instruct and Vision choices override review defaults. Some
structured JSON assessments and visual transcription intentionally use Instruct.
Thinking token exhaustion can fall back to Instruct; execution receipts record
such overrides. Requesting reasoning is not evidence of correct reasoning.

Vision requires a matching multimodal projector loaded by llama-server and
`pypdfium2` for page rendering. Enable it in the per-review control or launcher.
Capability/status records distinguish selected, attempted, skipped and failed
image extraction. The app does not send every page as an image. CPU vision
encoding and image-token caps are configurable (`QWEN_VISION_CPU`,
`QWEN_IMAGE_MAX_TOKENS`) and require supporting llama.cpp flags.

### Features that depend on the model and server

- **Thinking/Instruct** is requested through `chat_template_kwargs`
  (`enable_thinking`, `reasoning_effort`). Whether it has any effect depends on
  the model's chat template and on llama-server being started with `--jinja`.
  Templates that ignore these keys run the same way in both modes. Report headers
  record what was requested and whether reasoning was actually observed; a
  server that rejects the keys is recorded as such.
- **Vision** requires the model to have a matching multimodal projector loaded
  by llama-server (managed launchers load an `*mmproj*.gguf` found beside the
  model; set `QWEN_LOAD_MMPROJ=0` to prevent it). Availability is taken from the
  server's own `/props` report, never from the model name or a file being present.
  When the server does not report image support, Vision is shown as unavailable
  or unknown and reviews proceed from the text layer.
- **Vision status** in the header separates what the server advertises from
  what has been tried. *Reported available* means llama-server says it accepts
  images (`/props`). *Tested* means an image request to the model the server
  reports now, at this server address and llama.cpp build, returned text;
  *last test failed* means the latest such request did not. A result is never
  shown for a different model or server. Results are kept in `run/vision-tests.json`
  (model file names, addresses, times and counts only; `QWEN_VISION_RECORD=off`
  disables saving), so they survive an app restart. A request is made only when
  a review uses Vision. llama-server does not report its projector file, so a
  restart with the same model and a different projector is not detected.
  *Page rendering not installed* means the server accepts images but this app
  cannot render PDF pages (install `requirements-vision.txt`).
- **Image-token flags** (`--image-min-tokens`, `--image-max-tokens`) and
  `--no-mmproj-offload` need a llama.cpp build that has them. An older build
  rejects them at startup; the failure message says so.
- **Context size** is read from the server; long submissions need a context the
  model and memory can support.
- The appraisal prompts and policy are the same for every model. No
  model-specific appraisal rules are applied, and output quality differs
  between models.

## Workflow

1. Upload a manuscript and any supplementary evidence. Choose reasoning, Vision
   and Development mode, then start the review.
2. Read the Critical Appraisal. Expand technical details and verification/audit
   information when useful.
3. Follow a finding to its Evidence Card. Inspect the actual passages and the
   model's interpretation; expand suggested checks and the detailed record.
4. Use split view to compare with the original PDF. **Show in manuscript** is
   offered when evidence can be bound to a document and page. An exact quotation
   can still lack usable PDF geometry. Ambiguous matches, scans and damaged text
   layers require manual inspection. A yellow highlight establishes location,
   not the validity of a criticism.
5. Confirm your own Retain (accept), Revise (amend, with your wording) or
   Dismiss (reject) decision for each card. These decisions do not rewrite the
   original appraisal. Cards marked **Disputed by the AI verifier** carry two
   competing AI assessments: the original finding is left as written and the
   verifier's correction or objection is shown with it. Neither has been
   established; weigh both against the manuscript. Reopen saved reviews without
   processing the manuscript again; older records may need document reattachment.
6. Export the appraisal, appendix, cards or reviewer decisions as available.
   On the Evidence Cards page, **Export reviewer summary (.md)** gives a concise
   record for writing your report: retained findings, revised findings in your
   own wording (the AI observation shown only for reference), one line per
   dismissed finding, findings still awaiting a decision, and where the
   evidence was located. **Export full audit record (.md)** gives the complete
   record with quotations, verification details and technical data. Both use
   the same saved decisions, and exporting changes nothing. Decision exports
   remain drafts for human editing, not approved peer-review reports.
   Observations of your own that do not belong to an AI finding are not
   recorded in the application; add them when you write your report.

The Human Evidence Appendix helps you evaluate the final appraisal's concerns
and verification questions (strengths appear in the Evidence Cards). For each
it gives the statement and the evidence as the appraisal states it (both
AI-written), then checks every quotation the AI gave for that finding against
the saved manuscript text and shows it in one of three states:

- **Exact quotation authenticated.** The quotation occurs in the extracted
  manuscript text as one continuous passage. Only spacing, line breaks, letter
  case, Unicode compatibility forms, quotation-mark and dash styles, and the
  punctuation `, ; : ' " ( ) [ ] { } |` (and full stops outside numbers) are
  disregarded; each entry says which of these the match relied on. Signs,
  digits, decimal places, units, labels and symbols such as `± < > = %` must
  agree exactly. A quotation of fewer than six words and numbers is accepted
  only when it occurs exactly once and contains at least two words; numbers
  alone are never accepted.
- **Related manuscript passage located — quotation not authenticated.** Every
  word, number and symbol of the quotation occurs, in order, on one extracted
  line (typically a table row), but with other text between them: for example,
  a quotation of a row that leaves out one column's values. The AI's quotation
  and the manuscript line are both shown, with the omitted text and, for tables,
  the table's first row. Only one line in the manuscript may qualify; outside
  tables, each number must stay next to the words the quotation places it
  beside. The passage is shown for comparison and is not evidence that the
  AI's statistical interpretation is correct.
- **Quotation not located — not authenticated.** No reliable location was
  found. This does not show that the manuscript lacks the information. Where
  the review was saved in Development mode, the appendix says whether the
  quotation occurs in the AI's own intermediate text.

A passage cited more than once for the same finding (for example, by the
review item and by the verifier) is shown once, with every citation listed.
Passages at different places, and similar but different passages, are kept
separate. Locations are the page and table that the extracted text marks
(sections are not given, and documents other than PDFs have no page markers).
The Evidence Cards are not changed by any of this; where their own, less strict
check gives a different result for a quotation, the appendix says so. A saved
review without its manuscript text shows the Evidence Cards' results instead,
labelled as such. Observations from the initial reading
that were not carried into the appraisal are only summarised there; they are
unverified and are listed in full in the original appendix. The appendix shown
and downloaded is generated on request from the review's saved data and says
so; **Download original appendix .md** gives the appendix exactly as stored
when the review completed. Reviewer-facing outputs (the appraisal, this
appendix, the cards and the reviewer summary) are separate from the technical
audit material (the original appendix, the verification record and the full
audit export).

Each review tab has its own print button, which opens a print-ready page in a
new tab without the application workspace: **Print / Save Critical Appraisal
as PDF** (the saved appraisal, unaltered, with its technical details and
verification record), **Print / Save Human Evidence Appendix as PDF** (the
current appendix, as the tab shows it) and the Evidence Cards button below.
All are built from the saved review; no model is run, and the Markdown
downloads are unchanged.

To print the Evidence Cards or save them as PDF, use **Print / Save Evidence
Cards as PDF** on the Evidence Cards page. It opens a separate print page
(Summary: every finding with its saved reviewer decision and any reviewer
wording; Detailed: the same plus evidence, suggested checks, uncertainties and
the verification record for every card, whatever was expanded on screen).
AI findings are printed unchanged and kept apart from reviewer wording; the
decisions are the ones currently saved. Printing the Review Workspace itself
prints the whole application, with the cards clipped in their frame.

### Reviews completed with earlier versions

Saved reviews open without rerunning the model. Their Evidence Cards, both
decision exports and the concise appendix are produced by the current code
from what was saved, so they gain these features where their data allow:

- Nothing saved is changed: the stored appraisal, original appendix, cards
  snapshot, verification record and decisions stay as they were.
- If a review lacks Evidence Cards data, its appendix entries say that no
  evidence location is available; if it lacks the record of initial-reading
  observations, the appendix says so. Nothing is reconstructed.
- These features appear only when the application is started from this
  folder. Saved reviews live in its `reviews/sessions` folder (or
  `QWEN_REVIEW_STORE`); reviews saved by a copy of the application elsewhere
  are not visible here unless that store is copied or pointed to. If an older
  page or button is still shown after an update, check with
  `./scripts/qwen_service.sh status` which folder the running app comes from,
  and restart it from here.

Academic Chat can help investigate methodological questions. Inference is local,
but reference verification and public-source discovery/retrieval can contact
Crossref, OpenAlex and source websites. Those checks do not establish that a
methodological interpretation is correct. See the provenance and access notices
shown in the interface.

## Data and network boundary

Bind the app and model server to loopback. The app has no authentication; do not
expose it to another network without appropriate access controls. A manuscript
review sends text only to the configured llama-server, so keep that server on
this computer. Academic Chat's reference checks and source discovery can
contact Crossref, OpenAlex and source websites.

Saved manuscripts, reviews, decisions, traces, request receipts
(`local_results/`), logs (`logs/`), run state (`run/`) and chat logs are local
confidential records. Their default directories and `local.env` are listed in
`.gitignore`, but `.gitignore` is a convenience, not a safeguard: `git add -f`,
copying folders by hand or publishing an existing history bypasses it. Before
sharing or publishing a copy of this folder, run the read-only check
`python3 scripts/release_check.py --history` and read what will be published.
Development mode increases the diagnostic material retained on disk and must be
treated accordingly.

## Troubleshooting

- **The Saved Reviews panel reports that the review store does not exist.**
  Connect the drive or restore the folder named in the message, or change
  `QWEN_REVIEW_STORE` in `local.env`, then `./scripts/qwen_service.sh restart-app`.
- **An older page or button appears after an update.** Check which folder the
  running app comes from (`./scripts/qwen_service.sh status`) and run
  `restart-app` from this folder.
- **"Permission denied" from a launcher.** See the `chmod` command under
  installation.
- **The header reports a server problem.** See
  [Diagnosing connection failures](#diagnosing-connection-failures) and
  `./scripts/qwen_service.sh doctor`.
- **Printing the workspace clips the cards.** Use the print buttons, which
  open dedicated print pages.

## Testing

```bash
.venv/bin/python -m unittest discover -s tests -v
node tests/ui_contracts.cjs
```

Browser-based print tests (PDF output from Chromium via Playwright) run when
Playwright and Chromium are installed and are skipped otherwise. A Chromium
result is not evidence about Safari; printing in Safari was checked by hand on
macOS. `scripts/release_check.py` is a read-only pre-publication check.

The suite uses independently constructed fictional materials-bench documents,
hand-authored responses and generic protocol data. It blocks live model loading
and external connections, and uses temporary stores. It covers application
startup, source policy, execution settings, cards, saved decisions, exports,
document identity, PDF navigation/matching, Markdown, Vision integration,
Development mode and Academic Chat contracts, and model switching, external
servers and connection status. The process-handling tests run
`scripts/qwen_service.sh` against a small fake llama-server on a free loopback
port (they need `bash`, `curl`, `lsof` and `ps`, and are skipped without them).
No model-quality claims follow from those tests. See `tests/PROVENANCE.md` for
fixture origins.

## Methodological limitations and discontinued approaches

Earlier methodological classification was removed because incorrect classifications
could introduce inappropriate appraisal instructions. No controlled evaluation
demonstrated an improvement from classification-dependent prompting. Experimental
approaches were discontinued where they added complexity without demonstrated
benefit. Compatibility classifiers remain outside the active appraisal route.

Source verification locates text; it does not establish the correctness of
methodological interpretations. The model can make statistical reasoning errors.
Candidate selection and final synthesis may omit important findings. Vision-derived
numbers require checking against the original PDF. Expert methodological judgement
remains necessary. Software regression checks are not controlled scientific validation.

## Current research priorities

Independent expert evaluation of finding accuracy and omissions; quantitative/table
reasoning; faithful use of supplementary evidence; explicit uncertainty and source
coverage; and usability for reviewers working with the original manuscript.
Comparisons of configurations need controlled, representative evaluation rather
than a small number of favourable examples.

## Licensing

The application code is Copyright © 2026 Tony Myers and is licensed under the
Apache License, Version 2.0: see `LICENSE` and `NOTICE`. The reviewer notes in `resources/reviewer_notes/` are
licensed separately under CC BY 4.0. Twenty-three were drafted by Tony Myers
with ChatGPT assistance and twelve were generated by Fable 5.2 at his request,
with their bibliographic references checked; the `LICENCE.md` in that folder lists which is
which.
Bundled third-party components keep their own licences (PDF.js under Apache
2.0; its fonts, character maps, ICC profile and WebAssembly modules under the
terms in their own licence files; the Liberation 1.07.4 fonts under GPL-2.0
with a font exception, with their source in `third_party/`): see
`THIRD_PARTY_NOTICES.md` and `LICENSING.md`, and preserve those notices when
redistributing. Python dependencies are installed separately under their own
licences (`DEPENDENCIES.md`).

The Apache licence does not cover language models, model weights, projectors
or llama.cpp, none of which is distributed here; they remain under their own
terms. Nothing in this repository grants rights to manuscripts or to reviews
produced with the application.
