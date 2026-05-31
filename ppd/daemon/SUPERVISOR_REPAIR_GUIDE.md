# PP&D Supervisor Repair Guide

This guide is for supervisor repair cycles after repeated daemon rollbacks. It must not implement the stalled PP&D domain task directly. Its job is to restore useful autonomous progress by narrowing the next daemon prompt, preflight, retry, selection, or diagnostics work.

## Current Recovery Focus: Checkbox 25 and 26

The current stalled work is the agent readiness regression replay packet v3 and its validation pair:

- checkbox-25 / supervisor-20260531-969: fixture-first agent readiness regression replay packet v3.
- checkbox-26 / supervisor-20260531-970: validation for agent readiness regression replay packet v3.

Recent failures include repeated LLM termination before file production and one Python syntax-preflight failure in `ppd/tests/test_agent_readiness_replay_packet_v3.py` with an incomplete assertion fragment:

- `assert REQUIRED_CASE_KEYS 30`

The next daemon cycle must not retry the broad packet or validation task as a source-plus-fixture-plus-test bundle. Treat the next cycle as supervisor repair or parser recovery. The acceptable next patch shapes are:

- Replace only `ppd/daemon/SUPERVISOR_REPAIR_GUIDE.md` with narrower instructions.
- Replace only one daemon helper under `ppd/daemon/` that makes repeated LLM termination or syntax-preflight retries smaller.
- Replace only `ppd/daemon/task-board.md` to append narrow recovery tasks, preserving completed tasks and appending new unchecked tasks.
- If the supervisor deliberately resumes checkbox-25 or checkbox-26, require at most one parser-bearing Python file plus one essential fixture, and require a mentally checked `python3 -m py_compile` for that Python file before JSON is returned.

A parser-recovery prompt for `ppd/tests/test_agent_readiness_replay_packet_v3.py` must say that every Python assertion must contain a complete boolean expression, such as `is None`, `is not None`, `==`, `!=`, `in`, `issubset(...)`, or `isinstance(...)`. It must also require the worker to mentally run:

```text
python3 -m py_compile ppd/tests/test_agent_readiness_replay_packet_v3.py
```

before returning JSON.

## Recent Parser Failure Patterns

Treat these malformed fragments as parser-failure examples that require a smaller retry before any broader feature work:

- `page_number None`
- `page_number list[str]`
- `page_count list[str]`
- `if self.page_count list[str]`
- `if len(text) dict[str, str]`
- `if _checkbox_178_syntax_preflight_count(history) RetryScopeDecision`
- `if _checkbox_178_syntax_preflight_count(history) None`
- `self.assertTrue(set(field_fill["sourceEvidenceIds"]) None`
- `assert REQUIRED_CASE_KEYS 30`
- unmatched closing braces such as a bare `}` in a Python unittest file

These are not business-rule failures. They are syntax and code-generation failures. A retry should repair daemon supervision or add a very small validation guardrail before the worker attempts another DevHub, crawler, extraction, logic, contract, or fixture bundle.

## Parser Failure Escalation

When two or more recent rollbacks for the same target task include `SyntaxError`, `py_compile`, `TS1005`, `TS1109`, or `TS1128`, the supervisor must classify the next cycle as parser repair before selecting any PP&D domain task.

The next worker prompt must require all of the following:

- JSON only with complete file replacements.
- The smallest file set that can prove parser recovery.
- At most one parser-bearing Python or TypeScript file, unless the second file is this daemon repair guide.
- No source-plus-fixture-plus-test bundles.
- No new DevHub, crawler, extraction, logic, contract, or live automation behavior.
- A validation command that includes `python3 ppd/tests/validate_ppd.py`.

If the failed proposal touched a Python file, the retry prompt must tell the worker to mentally run `python3 -m py_compile` for that exact changed Python file before returning JSON. If the failed proposal touched a TypeScript file, the retry prompt must tell the worker to mentally run strict TypeScript parsing for that exact changed TypeScript file before returning JSON.

## LLM Termination Escalation

When two or more consecutive daemon rounds for the same target task fail before validation with no changed files and an error like `llm_router child timed out`, `llm_router child exited with code -15`, or return code `143`, the supervisor must stop immediately retrying that target task. Treat the next cycle as supervisor repair or task planning, not as another attempt to implement the blocked PP&D domain task.

The next prompt after repeated LLM termination should be smaller than the failed prompt and should request exactly one of these outcomes:

- One daemon operations document update that narrows retry behavior.
- One daemon prompt, timeout, or diagnostics helper under `ppd/daemon/`.
- One task-board append that adds a narrow fixture-first or validation-first recovery task.

The prompt should omit bulky historical context unless it is necessary for the repair decision. It should preserve the hard constraints, the active target label, the recent failure kind, and the exact validation command. It should not ask the worker to resume the same broad DevHub, crawler, extraction, or logic task until a repair or planning patch has validated.

## Allowed Recovery Shapes

Use one of these shapes after SyntaxError, py_compile, TS1005, TS1109, TS1128, or repeated LLM termination failures:

- One syntax-valid Python unittest file.
- One syntax-valid daemon helper file.
- One small JSON fixture plus one syntax-valid Python unittest file, only when the fixture is essential to the parser-clean test.
- One daemon operations document that tightens retry instructions.
- One task-board update that appends narrow unchecked recovery tasks.

Avoid source-plus-fixture-plus-test bundles until the parser-bearing file has passed syntax preflight. Every Python conditional uses complete comparisons such as `is None`, `is not None`, `==`, `!=`, `in`, `issubset(...)`, or `isinstance(...)`. No Python file contains TypeScript-style expression fragments.

## Preflight Order

Parser preflight runs before broad validation whenever a proposal changes Python or TypeScript files.

For Python files, run syntax preflight file by file with `python3 -m py_compile` before unittest discovery. For TypeScript files, run strict TypeScript parsing or typecheck before fixture, crawler, or domain validation. If parser preflight fails, stop immediately, roll back the patch, persist the failure kind as `syntax_preflight`, and make the next retry smaller.

The failure diagnostic should include the exact parser-bearing path, the first parser error line, and this next-action hint: replace only the syntactically failing file or one daemon repair file before attempting broader PP&D work.

## Separation From Domain Work

A supervisor repair cycle must not implement the stalled PP&D domain task directly. It may describe how to unblock later work, but it does not download documents, does not create private DevHub artifacts, does not open authenticated DevHub sessions, and does not automate upload, payment, submission, certification, cancellation, inspection scheduling, CAPTCHA, MFA, account creation, or password recovery.

## Prompt Guidance

When the board has blocked work or repeated LLM termination for the same target, append or select a narrow daemon-repair task first. The next prompt should ask for JSON only, complete file replacements only, and a small file set. If the recent failure is parser-related, require the worker to mentally run py_compile for changed Python files or strict TypeScript parsing for changed TypeScript files before returning JSON.

For checkbox-specific parser loops, prefer a daemon-repair or parser-clean test task over reopening blocked domain work. After one syntax_preflight failure and two LLM terminations for the same checkbox family, the retry prompt should permit exactly one parser-bearing file or one daemon repair file and should reject bundled source, fixture, and test proposals before any DevHub, crawler, extraction, or agent-readiness domain retry.

For repeated LLM termination loops, prefer a repair prompt that changes only daemon supervision, daemon operations documentation, or task planning. Do not keep selecting the same blocked domain task when the worker cannot produce a patch.
