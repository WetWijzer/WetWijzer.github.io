# PP&D Daemon Task Board

Status: supervisor-repaired backlog
Last supervisor update: 2026-05-09T04:22:57Z

## Preserved Completion State

The prior daemon run reported 9305 completed tasks, 0 blocked tasks, 0 in-progress tasks, and 0 eligible needed tasks before this supervisor repair. Those completed tasks remain treated as closed work by the daemon progress ledger and should not be recreated as generated placeholder tranches.

Recent completed work established deterministic daemon fallback and blocked-cascade repair coverage in `ppd/platform/deterministic_fallback_progress.py`, `ppd/platform/blocked_cascade_daemon_repair.py`, and `ppd/daemon/deterministic-progress.json`. The supervisor diagnosis requires stopping generated placeholder tranche creation and returning to agentic or human-authored PP&D work.

## Current Narrow Tranche

These tasks are ordered. Each task is intentionally small enough for one daemon cycle. Do not automate CAPTCHA, MFA, account creation, payment, submission, certification, cancellation, official upload, inspection scheduling, or private DevHub session capture.

- [!] Task supervisor-20260509-001: Add a fixture-only validation test that enumerates the official PP&D source anchors from the original plan and fails when any anchor is missing from the committed public source registry or documented as intentionally deferred.
- [x] Task supervisor-20260509-002: Add the minimal committed fixture or registry metadata needed for the PP&D bureau landing page, online permitting tools overview, DevHub FAQ, DevHub sign-in guide, apply-for-permits page, DevHub permit application guide, submit-plans-online page, forms index, file naming standards page, fee payment guide, DevHub portal, and Portland Maps public reference anchor to satisfy the source-anchor validation without fetching live pages.
- [x] Task supervisor-20260509-003: Add a fixture-first unit test for public crawl preflight decisions covering allowlisted `www.portland.gov`, `devhub.portlandoregon.gov`, `www.portlandoregon.gov`, and linked public `www.portlandmaps.com` URLs, plus skipped outside-allowlist, unsupported-scheme, private/authenticated, raw-download-not-permitted, and unsupported-content-type cases.
- [!] Task supervisor-20260509-004: Implement or tighten the PP&D public crawl preflight policy so the fixture cases from Task supervisor-20260509-003 pass using deterministic local inputs only, with no network calls and no raw body persistence.
- [x] Task supervisor-20260509-005: Add fixture-first tests for `ArchiveManifest` records proving skipped captures preserve URL, skip reason, source id, content type when known, processor policy, and `no_raw_body_persisted` semantics.
- [!] Task supervisor-20260509-006: Implement the smallest manifest normalization change needed for skipped public crawl records to satisfy Task supervisor-20260509-005 while preserving existing archive and processor handoff behavior.
- [!] Task supervisor-20260509-007: Add a fixture-only test for public HTML extraction ordering that verifies headings, ordered steps, callouts, tables, related links, and visible updated dates remain in document order for a synthetic PP&D guidance page.
- [x] Task supervisor-20260509-008: Implement the smallest public HTML extraction normalization change needed for the ordering fixture from Task supervisor-20260509-007, without adding live crawl behavior or storing raw downloaded pages.
- [!] Task supervisor-20260509-009: Add a fixture-only test for PDF/form extraction contracts covering page-anchored text, checklist items, certification blocks, fillable field names, checkbox/radio options, and OCR confidence flags using synthetic committed fixtures only.
- [!] Task supervisor-20260509-010: Implement the smallest PDF/form contract normalization change needed for Task supervisor-20260509-009 without downloading official PDFs or committing raw extracted public documents.
- [x] Task supervisor-20260509-011: Add a fixture-first test for requirement extraction that maps synthetic PP&D guidance text into obligation, prohibition, permission, precondition, deadline, fee_trigger, license_requirement, document_requirement, and action_gate nodes with source evidence ids.
- [!] Task supervisor-20260509-012: Implement the minimal deterministic requirement extraction or validation helper needed for Task supervisor-20260509-011 while keeping human-review and formalization status explicit.
- [!] Task supervisor-20260509-013: Add a fixture-only guardrail compiler test proving financial actions, official submission, certification, correction upload, inspection scheduling, cancellation, extension/reactivation requests, CAPTCHA, MFA, account creation, and password recovery all require refusal, exact confirmation, attended handoff, or manual handling as appropriate.
- [!] Task supervisor-20260509-014: Implement the smallest guardrail compiler or action classification change needed for Task supervisor-20260509-013 without adding browser automation.
- [!] Task supervisor-20260509-015: Add a fixture-only user gap analysis test for a standard trade permit scenario where contractor license data affects fixture availability, proving the gap analysis asks for missing license-related facts before allowing a draft-ready state.
- [x] Task supervisor-20260509-016: Implement the smallest user gap analysis rule needed for Task supervisor-20260509-015 using source evidence ids and deterministic local facts only.
- [!] Task supervisor-20260509-017: Add a fixture-only DevHub surface map test for a synthetic attended login-complete page that records title, heading, accessible roles/names, stable labels, validation messages, upload controls, save/back/continue/submit button states, selector confidence, redaction policy, attendance requirement, and exact-confirmation requirement.
- [!] Task supervisor-20260509-018: Implement the smallest DevHub surface map normalization change needed for Task supervisor-20260509-017 without storing credentials, auth state, screenshots, traces, HAR data, or private page values.
- [x] Task supervisor-20260509-019: Add daemon diagnostics coverage proving `no_eligible_tasks` after placeholder exhaustion triggers supervisor planning guidance instead of appending generated deterministic tranches.
- [!] Task supervisor-20260509-020: Implement the smallest daemon or supervisor task-selection diagnostic change needed for Task supervisor-20260509-019, keeping retries bounded and validation-first.

## Validation

Each completed task must pass the PP&D validation entry point before being marked complete:

- `python3 ppd/tests/validate_ppd.py`


<!-- ppd-daemon-task-board:start -->
## Generated Status

Last updated: 2026-05-09T05:05:00.518802Z

- Latest target: `Task checkbox-6: Task supervisor-20260509-006: Implement the smallest manifest normalization change needed for skipped public crawl records to satisfy Task supervisor-20260509-005 while preserving existing archive and processor handoff behavior.`
- Latest result: `llm`
- Latest summary: LLM proposal failed.
- Counts: `{"blocked": 13, "complete": 7, "in_progress": 0, "needed": 0}`

<!-- ppd-daemon-task-board:end -->
## Built-In Supervisor Repair Notes

- Reset dead-worker in-progress task `Task supervisor-20260509-003: Add a fixture-first unit test for public crawl preflight decisions covering allowlisted `www.portland.gov`, `devhub.portlandoregon.gov`, `www.portlandoregon.gov`, and linked public `www.portlandmaps.com` URLs, plus skipped outside-allowlist, unsupported-scheme, private/authenticated, raw-download-not-permitted, and unsupported-content-type cases.` to pending after the daemon process exited mid-cycle. The supervisor will restart the worker and let the task be selected again with a fresh timeout window.
## Built-In Supervisor Repair Notes

- Reset dead-worker in-progress task `Task supervisor-20260509-005: Add fixture-first tests for `ArchiveManifest` records proving skipped captures preserve URL, skip reason, source id, content type when known, processor policy, and `no_raw_body_persisted` semantics.` to pending after the daemon process exited mid-cycle. The supervisor will restart the worker and let the task be selected again with a fresh timeout window.
## Built-In Supervisor Repair Notes

- Reset dead-worker in-progress task `Task supervisor-20260509-008: Implement the smallest public HTML extraction normalization change needed for the ordering fixture from Task supervisor-20260509-007, without adding live crawl behavior or storing raw downloaded pages.` to pending after the daemon process exited mid-cycle. The supervisor will restart the worker and let the task be selected again with a fresh timeout window.
## Built-In Supervisor Repair Notes

- Reset dead-worker in-progress task `Task supervisor-20260509-010: Implement the smallest PDF/form contract normalization change needed for Task supervisor-20260509-009 without downloading official PDFs or committing raw extracted public documents.` to pending after the daemon process exited mid-cycle. The supervisor will restart the worker and let the task be selected again with a fresh timeout window.
## Built-In Supervisor Repair Notes

- Reset dead-worker in-progress task `Task supervisor-20260509-012: Implement the minimal deterministic requirement extraction or validation helper needed for Task supervisor-20260509-011 while keeping human-review and formalization status explicit.` to pending after the daemon process exited mid-cycle. The supervisor will restart the worker and let the task be selected again with a fresh timeout window.
## Built-In Supervisor Repair Notes

- Reset dead-worker in-progress task `Task supervisor-20260509-014: Implement the smallest guardrail compiler or action classification change needed for Task supervisor-20260509-013 without adding browser automation.` to pending after the daemon process exited mid-cycle. The supervisor will restart the worker and let the task be selected again with a fresh timeout window.
## Built-In Supervisor Repair Notes

- Reset dead-worker in-progress task `Task supervisor-20260509-016: Implement the smallest user gap analysis rule needed for Task supervisor-20260509-015 using source evidence ids and deterministic local facts only.` to pending after the daemon process exited mid-cycle. The supervisor will restart the worker and let the task be selected again with a fresh timeout window.
## Built-In Supervisor Repair Notes

- Reset dead-worker in-progress task `Task supervisor-20260509-018: Implement the smallest DevHub surface map normalization change needed for Task supervisor-20260509-017 without storing credentials, auth state, screenshots, traces, HAR data, or private page values.` to pending after the daemon process exited mid-cycle. The supervisor will restart the worker and let the task be selected again with a fresh timeout window.
## Built-In Supervisor Repair Notes

- Reset dead-worker in-progress task `Task supervisor-20260509-020: Implement the smallest daemon or supervisor task-selection diagnostic change needed for Task supervisor-20260509-019, keeping retries bounded and validation-first.` to pending after the daemon process exited mid-cycle. The supervisor will restart the worker and let the task be selected again with a fresh timeout window.
