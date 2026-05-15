# PP&D Daemon Task Board

Status: active
Last supervisor tranche: 2026-05-15

## Worker Rules

- Work one unchecked task per daemon cycle, in order from top to bottom.
- Preserve completed tasks and append new work instead of rewriting history.
- Keep every proposal narrow and deterministic.
- Do not implement live DevHub login, CAPTCHA, MFA, account creation, payment, submission, certification, cancellation, official upload, or inspection scheduling.
- Use committed synthetic fixtures before any live or authenticated automation.
- Do not create private DevHub session files, auth state, traces, HAR files, screenshots, raw crawl output, downloaded documents, or local private document artifacts.
- For every changed Python file, include `python3 -m py_compile ` in validation or rely on `python3 ppd/tests/validate_ppd.py` when it covers the file.
- For every changed TypeScript file, include strict `tsc --noEmit` validation when TypeScript exists.
- After recent syntax preflight failures, prefer one core file plus one narrow fixture/test per task instead of broad multi-contract rewrites.

## Completed Work

- [x] Task supervisor-20260514-001: Establish the PP&D daemon task board and operations boundary for autonomous cycles.
- [x] Task supervisor-20260514-002: Add deterministic daemon validation for PP&D proposals and task-board state.
- [x] Task supervisor-20260514-003: Add PP&D source registry contracts for official public source anchors and policy metadata.
- [x] Task supervisor-20260514-004: Add public crawl allowlist and robots/policy preflight fixtures for official PP&D sources.
- [x] Task supervisor-20260514-005: Add archive manifest and normalized public document record fixtures without committing raw bodies.
- [x] Task supervisor-20260514-006: Add requirement extraction fixtures for source-backed obligations, prohibitions, deadlines, fees, and action gates.
- [x] Task supervisor-20260514-007: Add process model fixtures for a narrow synthetic PP&D permit workflow.
- [x] Task supervisor-20260514-008: Add guardrail bundle compiler fixtures and deterministic predicate validation.
- [x] Task supervisor-20260514-009: Add DevHub action classification and consequential-action blocking fixtures.
- [x] Task supervisor-20260514-010: Add attended DevHub surface-map fixture validation without authenticated session artifacts.
- [x] Task supervisor-20260514-011: Add user gap analysis fixtures for missing facts, stale evidence, conflicting evidence, blocked actions, and next safe actions.
- [x] Task supervisor-20260514-013: Add fixture-first file preparation compliance planning for Single PDF and upload-boundary rules.
- [x] Task supervisor-20260514-014: Implement the minimal file-preparation compliance helper using synthetic PDF/document metadata fixtures only; do not read private files, download documents, persist raw PDFs, or perform upload staging.

## Next Ordered Tranche

- [x] Task supervisor-20260514-015: Add a synthetic file-preparation-to-guardrail fixture that maps document metadata compliance findings into blocked actions and next safe actions; edit only one narrow helper/test pair plus committed synthetic JSON if needed.
- [x] Task supervisor-20260514-016: Add validation that noncompliant synthetic document metadata blocks upload staging, certification, and submission while still allowing local preview and missing-information prompts.
- [x] Task supervisor-20260514-017: Add a source-evidence freshness fixture for file naming and Single PDF rules that marks stale or missing evidence before any document-preparation recommendation can be considered ready.
- [x] Task supervisor-20260514-018: Add a deterministic requirement-to-process-model consistency check for required documents, file rules, fee triggers, and unsupported paths using existing synthetic public-source fixtures only.
- [x] Task supervisor-20260514-019: Add an action-journal redaction fixture for local PDF preview, reversible draft plan, refused action, and exact-confirmation checkpoint events; ensure credentials, cookies, auth state, screenshots, traces, HAR data, private values, payment details, and local private paths are rejected.
- [x] Task supervisor-20260514-020: Add a DevHub attended-preflight fixture that proves login/MFA/CAPTCHA/account creation are manual handoff states and that authenticated browser state is never committed.
- [x] Task supervisor-20260514-021: Add a synthetic surface-map selector-confidence check that blocks draft-fill actions when labels, headings, or route evidence are ambiguous.
- [x] Task supervisor-20260514-022: Add a reversible draft-fill planning fixture that requires source evidence IDs, user case facts for every filled value, attendance, and a preview before any DevHub field-fill action is allowed.
- [x] Task supervisor-20260514-023: Add exact-confirmation checkpoint fixtures for acknowledgement/certification, official upload, submission, scheduling, cancellation, extension/reactivation, and payment boundaries without automating those actions.
- [x] Task supervisor-20260514-024: Add a change-monitoring fixture that reports changed source hashes and affected requirement/process/guardrail IDs without crawling live sites or storing raw page bodies.
- [x] Task supervisor-20260514-025: Add a fixture-only public source discovery index that records canonical URLs, source page, link text, content type hints, allow/skip decisions, and skip reason codes for official PP&D seed pages; do not crawl live sites or store raw page bodies.
- [x] Task supervisor-20260514-026: Add deterministic validation for public source discovery records covering allowed hosts, unsupported schemes, private/authenticated paths, outside-allowlist links, and public Portland Maps references linked from PP&D guidance.
- [x] Task supervisor-20260514-027: Add a processor-handoff manifest fixture that records PP&D-local policy preflight, processor name/version, redirect metadata, content hash, MIME type, normalized document reference, and `no_raw_body_persisted` for synthetic public captures only.
- [x] Task supervisor-20260514-028: Add validation that archive manifests reject raw body persistence, private/authenticated DevHub URLs, missing processor metadata, missing source IDs, and invented hashes for skipped captures.
- [x] Task supervisor-20260514-029: Add a normalized HTML extraction fixture for one synthetic PP&D guidance page with title, breadcrumbs, headings, ordered steps, warnings, tables, contacts, related links, update dates, and citation spans preserved in source order.
- [x] Task supervisor-20260514-030: Add a normalized PDF/form extraction fixture for synthetic public form metadata covering page anchors, checklist items, fillable field names, signature/certification blocks, file-preparation instructions, and OCR confidence flags without storing PDF binaries.
- [x] Task supervisor-20260514-031: Add a requirement extraction review fixture that marks low-confidence, OCR-derived, stale, conflicting, and unsupported-path requirements for human review before formalization.
- [x] Task supervisor-20260514-032: Add a process dependency graph fixture that links required facts, required documents, deadlines, fee triggers, exceptions, unsupported paths, and DevHub action gates for one narrow synthetic permit process.
- [x] Task supervisor-20260514-033: Add a guardrail explanation fixture that turns blocked action predicates and missing-information predicates into cited, user-facing explanations without exposing private values or raw authenticated page data.
- [x] Task supervisor-20260514-034: Add an agent-facing next-safe-action fixture that combines user gap analysis, process dependency graph state, action classification, and guardrail bundle results into read-only, reversible-draft, manual-handoff, and refused-action recommendations.
- [x] Task supervisor-20260515-035: Add a source-freshness readiness fixture that blocks guardrail readiness when official source evidence is stale, missing, or hash-changed; use synthetic registry/change-monitor records only, and keep the change to one helper/test pair plus one fixture if needed.
- [x] Task supervisor-20260515-036: Add deterministic requirement formalization readiness validation proving only fresh, supported, human-reviewed requirement nodes can feed a guardrail bundle; do not add broad new contracts or live source reads.
- [x] Task supervisor-20260515-037: Add a process-model coverage fixture for permit paths that PP&D guidance says are unsupported by DevHub or require manual/email handling, and validate that next-safe-action output becomes manual handoff rather than DevHub automation.
- [x] Task supervisor-20260515-038: Add a synthetic DevHub surface-recorder redaction fixture that permits accessible structure metadata while rejecting screenshots, traces, HAR data, auth state, cookies, credentials, private values, and local private paths.
- [x] Task supervisor-20260515-039: Add an attended-worker journal sequence fixture requiring preflight, action classification, preview, exact-confirmation checkpoint, and post-action review evidence before any DevHub action can be marked complete; do not automate or simulate final official actions.
- [x] Task supervisor-20260515-040: Add a local PDF draft-preview fixture that maps synthetic user facts to synthetic fillable field metadata and reports missing facts, blocked certification fields, and preview-only status without reading or writing PDF binaries.
- [x] Task supervisor-20260515-041: Add a narrow daemon diagnostics regression test that records repeated syntax-preflight failures with the target task, failing file, validation command, and smaller-next-attempt guidance; do not change worker task selection semantics.
- [x] Task supervisor-20260515-042: Add an end-to-end synthetic readiness fixture that links source registry, archive manifest, extracted requirements, process model, user gap analysis, guardrail bundle, and next-safe-action output for one narrow PP&D workflow without live crawling or authenticated automation.
- [!] Task supervisor-20260515-043: Add a fixture-first citation integrity validator that verifies every requirement, process-model rule, guardrail predicate, and next-safe-action explanation traces back to committed synthetic source evidence IDs and citation spans; do not crawl live sources or broaden contracts.
- [x] Task supervisor-20260515-044: Add a deterministic stale-or-changed-source impact report fixture that maps changed synthetic source hashes to affected requirement IDs, process IDs, guardrail bundle IDs, and blocked readiness statuses before any recommendation is marked current.
- [x] Task supervisor-20260515-045: Add a narrow permit-type taxonomy fixture for DevHub-supported, DevHub-unsupported, email/manual, and public-reference-only paths, and validate that unsupported paths always produce manual handoff rather than browser automation.
- [x] Task supervisor-20260515-046: Add a fixture-only conflict-resolution readiness check for contradictory requirement nodes, proving conflicts block formalization and produce cited missing-information or human-review prompts without choosing a winner automatically.
- [x] Task supervisor-20260515-047: Add an agent-facing missing-information API fixture that returns only missing, stale, ambiguous, or conflicting user facts for one synthetic case, with private values redacted and no local file paths.
- [x] Task supervisor-20260515-048: Add a guarded reversible-draft execution plan fixture that separates local preview, draft field-fill, save-for-later, and consequential submit/certify/upload/payment actions, requiring attendance and exact confirmation only at the appropriate boundaries.
- [x] Task supervisor-20260515-049: Add a synthetic processor-capability adapter fixture that records which ipfs_datasets_py processor capabilities would be used for HTML, PDF, WARC, and metadata capture, without importing network-dependent processors or writing raw archives.
- [x] Task supervisor-20260515-050: Add a daemon validation regression that rejects task-board proposals which mark application/domain work complete without a visible committed source change, while still allowing supervisor-only backlog updates under `plan_next_tasks`.


<!-- ppd-daemon-task-board:start -->
## Generated Status

Last updated: 2026-05-15T07:06:05.052141Z

- Latest target: `Task checkbox-42: Task supervisor-20260515-043: Add a fixture-first citation integrity validator that verifies every requirement, process-model rule, guardrail predicate, and next-safe-action explanation traces back to committed synthetic source evidence IDs and citation spans; do not crawl live sources or broaden contracts.`
- Latest result: `syntax_preflight`
- Latest summary: Add a fixture-first PP&D citation integrity validator with deterministic synthetic fixtures and narrow unit tests.
- Counts: `{"blocked": 1, "complete": 48, "in_progress": 0, "needed": 0}`

<!-- ppd-daemon-task-board:end -->
