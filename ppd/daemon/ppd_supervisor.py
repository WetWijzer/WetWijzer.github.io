#!/usr/bin/env python3
"""Agentic supervisor for the isolated PP&D daemon.

The worker daemon advances PP&D implementation tasks. The supervisor watches the
worker's health and can ask Codex for a narrow daemon/supervisor patch when the
worker is stuck, repeatedly blocked, or no longer making meaningful progress.
"""

from __future__ import annotations

import argparse
import atexit
import json
import os
import re
import signal
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Optional

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ppd.daemon.ppd_daemon import (  # noqa: E402
    CommandResult,
    Config as DaemonConfig,
    Proposal,
    Task,
    apply_files_with_validation,
    atomic_write_json,
    compact_message,
    cleanup_stale_validation_worktrees,
    has_open_deterministic_task_fallback,
    is_private_write_path,
    parse_proposal,
    parse_tasks,
    read_text,
    run_validation,
    select_task_for_config,
    utc_now,
)
from ppd.daemon.recovery_note_compaction import compact_task_board_repair_notes
from ipfs_datasets_py.optimizers.todo_daemon.diagnostics import (  # noqa: E402
    exception_diagnostic as todo_exception_diagnostic,
)
from ipfs_datasets_py.optimizers.todo_daemon.status import (  # noqa: E402
    build_ready_after_supervisor_repair_status,
)

FORBIDDEN_ABSENCE_MARKERS = (
    "cookie",
    "cookies",
    "screenshot",
    "screenshots",
    "auth-state",
    "storage-state",
    "trace.zip",
    ".har",
)

SYNTAX_OR_COMPILE_FAILURE_MARKERS = (
    "syntaxerror",
    "failed py_compile",
    "py_compile",
    "invalid syntax",
    "unterminated string literal",
    "unmatched ')'",
    "unexpected indent",
    "expected an indented block",
    "ts1005",
    "ts1109",
    "ts1128",
    "declaration or statement expected",
    "expression expected",
)

MALFORMED_PYTHON_PROPOSAL_MARKERS = (
    "confidence 1",
    "confidence 1.0",
    "return 0.0 list[str]",
)

TASK_TITLE_RE = re.compile(r"Task checkbox-\d+:\s*")
CHECKBOX_ID_RE = re.compile(r"checkbox-(\d+)")
REPLENISHMENT_HEADING_RE = re.compile(r"^## Built-In Goal Replenishment Tranche(?:\s+(\d+))?\s*$")
AUTONOMOUS_PLATFORM_HEADING_RE = re.compile(r"^## Built-In Autonomous PP&D Platform Tranche(?:\s+(\d+))?\s*$")
AUTONOMOUS_EXECUTION_HEADING_RE = re.compile(r"^## Built-In Autonomous PP&D Execution Capability Tranche(?:\s+(\d+))?\s*$")
SOURCE_BACKED_EXECUTION_CONTINUATION_HEADING_RE = re.compile(
    r"^## Built-In Source-Backed Execution Continuation Tranche(?:\s+(\d+))?\s*$"
)
BLOCKED_CASCADE_HEADING_RE = re.compile(r"^## Built-In Blocked Cascade Recovery Tranche(?:\s+(\d+))?\s*$")
TASK_LINE_RE = re.compile(r"^(?P<prefix>- \[[ xX~!]\] Task checkbox-\d+: )(?P<title>.+)$")
GENERATED_BLOCKED_CASCADE_TITLE_RE = re.compile(
    r"^Add generated blocked-cascade daemon-repair coverage for tranche \d+ item \d+ "
    r"proving blocked PP&D work stays parked until a fresh daemon repair task validates\.?$"
)
GENERATED_BLOCKED_CASCADE_QUARANTINE_HEADING = "## Built-In Generated Blocked-Cascade Quarantine Notes"
GENERATED_BLOCKED_CASCADE_QUARANTINE_NOTE = (
    "- Parked open generated blocked-cascade daemon-repair tasks after a systemic termination storm. "
    "The supervisor will not grow generated fallback tranches again until the resource policy is hardened "
    "or a vetted human-authored task is reopened."
)
MAX_GENERATED_BLOCKED_CASCADE_TASKS = 16
MAX_SOURCE_BACKED_EXECUTION_CONTINUATION_TRANCHES = 1
MANUAL_COMPREHENSIVE_GOAL_HEADING = "## Manual Comprehensive PP&D Goal Handoff Tranche"
MANUAL_GOAL_REOPEN_LIMIT = 4
FAST_SUPERVISOR_FOLLOWUP_SECONDS = 1.0
ACTIVE_WORK_SUPERVISOR_FOLLOWUP_SECONDS = 5.0
FAST_SUPERVISOR_FOLLOWUP_ACTIONS = frozenset(
    {
        "plan_next_tasks",
        "restart_daemon",
        "recover_termination_storm_and_restart",
        "recover_termination_storm",
        "reconcile_repeated_llm_loop_and_restart",
        "reconcile_stalled_worker_and_restart",
        "reconcile_dead_worker_with_recent_failures_and_restart",
        "reconcile_blocked_cascade_and_restart",
        "reconcile_dead_worker_and_restart",
        "reconcile_supersession_task_board",
        "repair_daemon_programming",
    }
)

SANITIZED_REPLENISHMENT_TITLES = (
    "Add supervisor deterministic-replenishment sanitization coverage proving agentic planner output with duplicate tranche headings or previously completed broad titles is rewritten to the next numbered non-duplicate tranche before the daemon starts.",
    "Add daemon LLM result-durability coverage proving parse failures, validation interruption, child timeout, and vanished-child states write progress and result-log diagnostics before restart.",
    "Add a fixture-only cross-permit guardrail reuse scenario plus focused validation that reuses common stop gates across two PP&D permit types while preserving process-specific citations and exact-confirmation requirements.",
    "Add a fixture-only human-review packet scenario plus focused validation bundling conflicting evidence, stale answers, upload readiness, fee notices, and blocked DevHub transitions into one redacted review handoff.",
)

FOLLOWUP_REPLENISHMENT_TITLES = (
    "Add supervisor task-board de-duplication coverage proving deterministic replenishment uses the highest existing tranche number and skips any task titles already completed anywhere on the board.",
    "Add daemon stale-worker recovery coverage proving a dead child recorded as calling_llm or applying_files is converted into a selectable pending task with a durable diagnostic before restart.",
    "Add a fixture-only processor archival-suite readiness scenario plus focused validation that routes PP&D public URLs through ipfs_datasets_py processor handoff metadata, content-hash placeholders, and source-linked extraction batches without live crawling.",
    "Add a fixture-only Playwright autonomous-form planning scenario plus focused validation that future agents may fill reversible draft fields from redacted user facts while refusing upload, submit, payment, certification, cancellation, MFA, CAPTCHA, and inspection scheduling without exact confirmation.",
)

SECOND_FOLLOWUP_REPLENISHMENT_TITLES = (
    "Add daemon compact-prompt retry coverage proving repeated durable parse or LLM diagnostics produce a smaller task-focused JSON prompt instead of resending the broad PP&D workspace context.",
    "Add daemon JSON-output recovery coverage proving compact retry mode includes strict one-object schema guidance, minimal fixture/test scope, and no extra prose allowance for llm_router backends.",
    "Add supervisor replenishment coverage proving completed recovery tranches rotate into fresh PP&D archival, formal-logic, and Playwright planning tasks instead of reusing already satisfied supervisor hardening titles.",
    "Add a fixture-only evidence-to-guardrail trace matrix plus focused validation linking processor handoff IDs, extracted requirement nodes, user document-store facts, missing facts, and exact-confirmation stop gates.",
)

THIRD_FOLLOWUP_REPLENISHMENT_TITLES = (
    "Add daemon llm_router prompt-budget enforcement coverage proving compact retry prompts stay under a strict character cap before the child process is invoked.",
    "Add supervisor repair-prompt compaction coverage proving repeated daemon parse diagnostics produce a bounded self-heal prompt with recent diagnostics, task board summary, and no accepted-work dump.",
    "Add a fixture-only formal-logic export bundle plus focused validation mapping PP&D requirement nodes into obligations, prerequisites, stop gates, and exact-confirmation predicates for downstream agents.",
    "Add a fixture-only autonomous-assistance dry-run transcript plus focused validation showing known user document-store facts, missing fact questions, reversible draft actions, and refused official actions in order.",
)

AUTONOMOUS_PLATFORM_REPLENISHMENT_TITLES = (
    "Add a side-effect-free whole-site PP&D archival plan under ppd/crawler that models full public-site discovery, processor-suite handoff, PDF normalization, requirement extraction, and formal-logic outputs without live crawling or private artifacts.",
    "Add validation coverage for the whole-site PP&D archival plan proving it uses the ipfs_datasets_py processor suite, public allowlists, robots preflight, bounded retries, and no raw crawl, browser, or private DevHub artifacts.",
    "Add a side-effect-free Playwright and PDF draft automation plan under ppd/devhub that models user-authorized draft form fills, local PDF field fills, audit events, and exact-confirmation checkpoints without live login or official actions.",
    "Add validation coverage for Playwright and PDF draft automation proving reversible draft fills are allowed while upload, submit, payment, certification, cancellation, inspection scheduling, MFA, CAPTCHA, and account creation remain refused by default.",
    "Add supervisor completed-board regression coverage proving an all-complete PP&D board appends the autonomous platform tranche and restarts the daemon instead of idling with no available work.",
    "Add daemon/supervisor operations coverage proving watch mode starts the next cycle immediately after each task, relies on LLM and validation timeouts to avoid hangs, and leaves supervisor replanning responsible for empty boards.",
)

AUTONOMOUS_EXECUTION_CAPABILITY_TITLES = (
    "Add a supervised live whole-site public crawl runner under ppd/crawler that resumes an allowlisted PP&D frontier, delegates archival capture to the ipfs_datasets_py processor suite, records robots and content-type decisions, and persists metadata manifests instead of raw bodies or downloaded documents.",
    "Add processor-suite execution integration under ppd/crawler proving public PP&D pages and PDFs flow through archive manifests, normalized document records, PDF metadata, requirement batches, and formal-logic source evidence IDs before agent reuse.",
    "Add an attended Playwright DevHub worker runner under ppd/devhub that supports manual login handoff, journal replay, reversible draft field fills from redacted facts, and mandatory pauses before upload, submit, certification, cancellation, inspection, security, or payment transitions.",
    "Add a local PDF draft-fill work queue under ppd/pdf that maps public PP&D form field manifests to redacted user facts, invokes the pypdf draft filler for previews, and never uploads, submits, or stores private source documents.",
    "Add a formal-logic guardrail extraction pipeline under ppd/logic that converts processor-backed requirement batches into obligations, prerequisites, missing-fact questions, reversible-action predicates, exact-confirmation predicates, and refused official-action stop gates.",
    "Add supervisor execution-capability recovery coverage proving stale calling_llm or applying_files status on old platform slices parks the stale tranche, appends this comprehensive execution tranche, validates the daemon, and restarts with PPD_LLM_BACKEND=llm_router.",
)

CIRCUIT_BREAKER_RECOVERY_TITLES = (
    "Add supervisor circuit-breaker recovery coverage proving expired termination storms append vetted non-generated recovery tasks and restart without reopening generated blocked-cascade work.",
    "Add daemon circuit-breaker resume coverage proving blocked generated cascade tasks stay skipped while a fresh vetted recovery task is selected first.",
    "Add PP&D supervisor operations documentation for persistent user-unit recovery, explicit daemon resume gates, and no live DevHub or official-action side effects.",
    "Add a fixture-only circuit-breaker status scenario proving paused daemon state records quarantine, restart eligibility, and source-safe recovery boundaries before autonomous work resumes.",
)

CIRCUIT_BREAKER_RECOVERY_CONTINUATION_TITLES = (
    "Add supervisor blocked-cascade compaction coverage proving repeated generated repair tranches collapse into one quarantine note and never create more accepted-work sidecar panels.",
    "Add daemon promotion-mismatch coverage proving temporary-worktree files are byte-checked after promotion and failed promotions are persisted without marking tasks complete.",
    "Add accepted-work ledger-only migration coverage proving new accepted rounds append one JSONL ledger row by default and leave legacy sidecar artifacts ignored unless explicitly enabled.",
    "Add source-backed recovery continuation coverage proving all closed circuit-breaker recovery tasks synthesize this vetted non-generated tranche before restarting the daemon.",
)


@dataclass(frozen=True)
class SupervisorConfig:
    repo_root: Path
    pid_file: Path = Path("ppd/daemon/ppd-daemon.pid")
    status_file: Path = Path("ppd/daemon/status.json")
    progress_file: Path = Path("ppd/daemon/progress.json")
    result_log: Path = Path("ppd/daemon/ppd-daemon.jsonl")
    task_board: Path = Path("ppd/daemon/task-board.md")
    plan_doc: Path = Path("docs/PORTLAND_PPD_SCRAPING_AUTOMATION_LOGIC_PLAN.md")
    supervisor_status_file: Path = Path("ppd/daemon/supervisor-status.json")
    supervisor_log: Path = Path("ppd/daemon/supervisor-actions.jsonl")
    supervisor_pid_file: Path = Path("ppd/daemon/ppd-supervisor.pid")
    supervisor_child_pid_file: Path = Path("ppd/daemon/ppd-supervisor.child.pid")
    circuit_breaker_file: Path = Path("ppd/daemon/supervisor-circuit-breaker.json")
    control_script: Path = Path("ppd/daemon/control.sh")
    stall_seconds: int = 900
    blocked_task_threshold: int = 1
    repeated_failure_threshold: int = 3
    termination_storm_threshold: int = 8
    termination_storm_backoff_seconds: int = 900
    active_state_timeout_seconds: int = 420
    max_prompt_chars: int = 50000
    max_repair_prompt_chars: int = 9000
    llm_timeout_seconds: int = 300
    model_name: str = "gpt-5.5"
    provider: Optional[str] = None
    apply: bool = False
    self_heal: bool = False
    restart_daemon: bool = False
    exception_backoff_seconds: float = 5.0
    honor_supervisor_term: bool = False
    revisit_blocked_tasks: bool = False
    reassess_blocked_llm_termination_gates: bool = False

    def resolve(self, path: Path) -> Path:
        return path if path.is_absolute() else self.repo_root / path


_WATCH_CONFIG: Optional[SupervisorConfig] = None


def supervisor_stop_sentinel(config: SupervisorConfig) -> Path:
    return Path(str(config.resolve(config.supervisor_pid_file)) + ".stop")


def append_supervisor_runtime_event(config: SupervisorConfig, event: str, **payload: Any) -> None:
    row = {"event": event, "updated_at": utc_now(), "pid": os.getpid(), **payload}
    append_jsonl(config.resolve(config.supervisor_log), row)


def handle_supervisor_signal(signum: int, _frame: object) -> None:
    config = _WATCH_CONFIG
    if config is None:
        raise SystemExit(128 + signum)
    signal_name = signal.Signals(signum).name
    if supervisor_stop_sentinel(config).exists():
        append_supervisor_runtime_event(config, "supervisor_signal_stop", signal=signal_name)
        raise SystemExit(128 + signum)
    if config.honor_supervisor_term:
        append_supervisor_runtime_event(
            config,
            "supervisor_signal_honored",
            signal=signal_name,
            message="honored supervisor signal so the service manager can restart or stop the unit cleanly",
        )
        raise SystemExit(128 + signum)
    append_supervisor_runtime_event(
        config,
        "supervisor_signal_ignored",
        signal=signal_name,
        message="ignored supervisor signal because the stop sentinel was absent",
    )


def record_supervisor_watch_exit() -> None:
    if _WATCH_CONFIG is not None:
        try:
            append_supervisor_runtime_event(_WATCH_CONFIG, "supervisor_watch_exit")
        except Exception:
            pass


def install_supervisor_runtime_guards(config: SupervisorConfig) -> None:
    global _WATCH_CONFIG
    _WATCH_CONFIG = config
    signal.signal(signal.SIGTERM, handle_supervisor_signal)
    signal.signal(signal.SIGHUP, handle_supervisor_signal)
    atexit.register(record_supervisor_watch_exit)


def supervisor_process_is_superseded(config: SupervisorConfig) -> bool:
    """Return true when this watch process is no longer the managed supervisor child."""

    current_pid = os.getpid()
    watchdog_pid = read_pid(config.resolve(config.supervisor_pid_file))
    child_pid = read_pid(config.resolve(config.supervisor_child_pid_file))
    if watchdog_pid == current_pid:
        return False
    if child_pid == current_pid:
        return not process_running(watchdog_pid)
    if child_pid is not None and process_running(child_pid):
        return True
    if watchdog_pid is not None and process_running(watchdog_pid):
        return True
    return False


def exit_if_superseded_supervisor(config: SupervisorConfig) -> None:
    if not supervisor_process_is_superseded(config):
        return
    append_supervisor_runtime_event(
        config,
        "supervisor_superseded_exit",
        message="exiting because another watchdog/child pair owns the supervisor pid files",
    )
    raise SystemExit(0)


@dataclass(frozen=True)
class SupervisorDecision:
    action: str
    reason: str
    severity: str
    should_invoke_codex: bool = False
    should_restart_daemon: bool = False


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"_invalid_json": True}
    return parsed if isinstance(parsed, dict) else {}


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{os.getpid()}.{time.time_ns()}.tmp")
    try:
        tmp.write_text(text, encoding="utf-8")
        tmp.replace(path)
    finally:
        if tmp.exists():
            tmp.unlink()


def exception_diagnostic(exc: BaseException, *, limit: int = 5000) -> str:
    return todo_exception_diagnostic(exc, limit=limit)


def read_supervisor_result_rows(path: Path) -> list[dict[str, Any]]:
    """Read daemon proposal rows plus durable diagnostic-only rows."""

    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload.get("proposal"), dict):
            rows.append(payload["proposal"])
        elif isinstance(payload.get("diagnostic"), dict):
            diagnostic = dict(payload["diagnostic"])
            diagnostic["_diagnostic_stage"] = payload.get("stage", "")
            rows.append(diagnostic)
    return rows


def parse_timestamp(value: Any) -> Optional[datetime]:
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def age_seconds(value: Any, *, now: Optional[datetime] = None) -> Optional[float]:
    parsed = parse_timestamp(value)
    if parsed is None:
        return None
    current = now or datetime.now(timezone.utc)
    return max(0.0, (current - parsed).total_seconds())


def read_pid(path: Path) -> Optional[int]:
    if not path.exists():
        return None
    try:
        return int(path.read_text(encoding="utf-8").strip())
    except ValueError:
        return None


def process_running(pid: Optional[int]) -> bool:
    if pid is None:
        return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def target_matches_any_label(target_task: str, labels: set[str]) -> bool:
    """Match task labels even when older diagnostics nested checkbox prefixes."""

    if target_task in labels:
        return True
    target_title = title_from_task_label(target_task)
    return bool(target_title and any(target_title == title_from_task_label(label) for label in labels))


def latest_repeated_failure_count(rows: list[dict[str, Any]], *, completed_task_labels: Optional[set[str]] = None) -> int:
    completed = completed_task_labels or set()
    count = 0
    for proposal in reversed(rows):
        if target_matches_any_label(str(proposal.get("target_task") or ""), completed):
            continue
        if proposal.get("applied") and proposal.get("validation_passed") and not proposal.get("errors"):
            break
        count += 1
    return count


def recent_parse_or_llm_diagnostic_failure_count(
    rows: list[dict[str, Any]], *, completed_task_labels: Optional[set[str]] = None
) -> int:
    completed = completed_task_labels or set()
    count = 0
    target = ""
    for proposal in reversed(rows):
        proposal_target = str(proposal.get("target_task") or "")
        if target_matches_any_label(proposal_target, completed):
            continue
        if proposal.get("applied") and proposal.get("validation_passed") and not proposal.get("errors"):
            break
        failure_kind = str(proposal.get("failure_kind") or "")
        if failure_kind not in {"parse", "llm"}:
            break
        if target and proposal_target != target:
            break
        target = proposal_target
        count += 1
    return count


def recent_parse_or_llm_failure_target(
    rows: list[dict[str, Any]], *, minimum: int = 3, completed_task_labels: Optional[set[str]] = None
) -> str:
    completed = completed_task_labels or set()
    count = 0
    target = ""
    for proposal in reversed(rows):
        proposal_target = str(proposal.get("target_task") or "")
        if target_matches_any_label(proposal_target, completed):
            continue
        if proposal.get("applied") and proposal.get("validation_passed") and not proposal.get("errors"):
            break
        if str(proposal.get("failure_kind") or "") not in {"parse", "llm"}:
            break
        if target and proposal_target != target:
            break
        target = proposal_target
        count += 1
    return target if count >= minimum else ""


TERMINATION_ERROR_MARKERS = (
    "143",
    "137",
    "code -15",
    "code -9",
    "signal 15",
    "signal 9",
    "sigterm",
    "sigkill",
)


def is_llm_termination_failure(proposal: dict[str, Any]) -> bool:
    if str(proposal.get("failure_kind") or "") != "llm":
        return False
    text = " ".join(str(error).lower() for error in proposal.get("errors", []) or [])
    return bool(text and any(marker in text for marker in TERMINATION_ERROR_MARKERS))


def recent_llm_termination_storm_count(rows: list[dict[str, Any]]) -> tuple[int, int]:
    """Return recent termination count and distinct targets since the last accepted green row."""

    count = 0
    targets: set[str] = set()
    for proposal in reversed(rows):
        if proposal.get("applied") and proposal.get("validation_passed") and not proposal.get("errors"):
            break
        if not is_llm_termination_failure(proposal):
            if count:
                break
            continue
        count += 1
        target = str(proposal.get("target_task") or "")
        if target:
            targets.add(title_from_task_label(target))
    return count, len(targets)


def daemon_has_fresh_active_work(
    *,
    running: bool,
    heartbeat_age: Optional[float],
    active_state: str,
    active_state_age: Optional[float],
    config: SupervisorConfig,
) -> bool:
    if not running or heartbeat_age is None or heartbeat_age > config.stall_seconds:
        return False
    if active_state not in {"selecting_task", "calling_llm", "applying_files", "heartbeat"}:
        return False
    if active_state in {"selecting_task", "calling_llm", "applying_files"}:
        return active_state_age is None or active_state_age <= config.active_state_timeout_seconds
    return True


def is_generated_blocked_cascade_task(task: Task) -> bool:
    return bool(GENERATED_BLOCKED_CASCADE_TITLE_RE.match(task.title.strip()))


def generated_blocked_cascade_task_counts(tasks: list[Task]) -> tuple[int, int]:
    generated = [task for task in tasks if is_generated_blocked_cascade_task(task)]
    open_generated = [task for task in generated if task.status in {"needed", "in-progress"}]
    return len(generated), len(open_generated)


def generated_blocked_cascade_budget_exhausted(tasks: list[Task]) -> bool:
    total, _open = generated_blocked_cascade_task_counts(tasks)
    return total >= MAX_GENERATED_BLOCKED_CASCADE_TASKS


def is_circuit_breaker_recovery_task(task: Task) -> bool:
    return task.title.strip() in CIRCUIT_BREAKER_RECOVERY_TITLES + CIRCUIT_BREAKER_RECOVERY_CONTINUATION_TITLES


def has_open_circuit_breaker_recovery_task(tasks: list[Task]) -> bool:
    return any(is_circuit_breaker_recovery_task(task) and task.status in {"needed", "in-progress"} for task in tasks)


def has_closed_circuit_breaker_recovery_task(tasks: list[Task]) -> bool:
    return any(is_circuit_breaker_recovery_task(task) and task.status in {"complete", "blocked"} for task in tasks)


def active_termination_storm_circuit_breaker(
    config: SupervisorConfig,
    *,
    now: Optional[datetime] = None,
) -> tuple[dict[str, Any], Optional[float]]:
    payload = load_json(config.resolve(config.circuit_breaker_file))
    if payload.get("repairKind") != "termination_storm_circuit_breaker":
        return {}, None
    age = age_seconds(payload.get("createdAt"), now=now)
    if age is None or age > config.termination_storm_backoff_seconds:
        return {}, None
    return payload, max(0.0, float(config.termination_storm_backoff_seconds) - age)


def append_circuit_breaker_recovery_tasks(markdown: str) -> tuple[str, tuple[str, ...]]:
    tasks = parse_tasks(markdown)
    open_labels = tuple(
        f"checkbox-{task.checkbox_id}"
        for task in tasks
        if is_circuit_breaker_recovery_task(task) and task.status in {"needed", "in-progress"}
    )
    if open_labels:
        return markdown, open_labels

    titles = existing_task_titles(markdown)
    templates = [
        title
        for title in CIRCUIT_BREAKER_RECOVERY_TITLES
        if not task_title_already_covered(title, titles)
    ]
    if not templates:
        templates = [
            title
            for title in CIRCUIT_BREAKER_RECOVERY_CONTINUATION_TITLES
            if not task_title_already_covered(title, titles)
        ]
    if not templates:
        return markdown, ()

    start = next_checkbox_number(markdown)
    labels = tuple(f"checkbox-{start + offset}" for offset in range(len(templates)))
    lines = ["", "## Built-In Circuit Breaker Recovery Tranche", ""]
    for offset, title in enumerate(templates):
        lines.append(f"- [ ] Task checkbox-{start + offset}: {title}")
    note = (
        "\n"
        "## Built-In Circuit Breaker Recovery Notes\n\n"
        "- Appended vetted non-generated recovery tasks after generated blocked-cascade work was quarantined. "
        "These tasks keep recovery inside PP&D daemon/supervisor fixtures, lifecycle handling, and documentation; "
        "they do not authorize live DevHub actions, uploads, submissions, payments, or real PDF filling.\n"
    )
    return markdown.rstrip() + "\n" + "\n".join(lines) + note, labels


def quarantine_generated_blocked_cascade_tasks(markdown: str) -> tuple[str, tuple[str, ...]]:
    """Park generated blocked-cascade tasks so a storm cannot keep selecting them."""

    changed_labels: list[str] = []
    repaired_lines: list[str] = []
    for line in markdown.splitlines(keepends=True):
        stripped = line.rstrip("\n")
        match = TASK_LINE_RE.match(stripped)
        if match and GENERATED_BLOCKED_CASCADE_TITLE_RE.match(match.group("title").strip()):
            checkbox = CHECKBOX_ID_RE.search(match.group("prefix"))
            if checkbox and ("- [ ]" in match.group("prefix") or "- [~]" in match.group("prefix")):
                changed_labels.append(f"checkbox-{checkbox.group(1)}")
                line = line.replace("- [ ]", "- [!]", 1).replace("- [~]", "- [!]", 1)
        repaired_lines.append(line)

    repaired, removed_existing_notes = compact_generated_blocked_cascade_quarantine_notes(
        "".join(repaired_lines)
    )
    if not changed_labels and not removed_existing_notes:
        return markdown, ()

    return append_generated_blocked_cascade_quarantine_note(repaired), tuple(changed_labels)


def compact_generated_blocked_cascade_quarantine_notes(markdown: str) -> tuple[str, bool]:
    """Remove any existing generated blocked-cascade quarantine-note sections."""

    cleaned: list[str] = []
    removed = False
    skipping = False
    for line in markdown.splitlines(keepends=True):
        stripped = line.strip()
        if stripped == GENERATED_BLOCKED_CASCADE_QUARANTINE_HEADING:
            removed = True
            skipping = True
            continue
        if skipping and stripped.startswith("## "):
            skipping = False
        if skipping:
            continue
        cleaned.append(line)
    return "".join(cleaned).rstrip(), removed


def append_generated_blocked_cascade_quarantine_note(markdown: str) -> str:
    """Append exactly one generated blocked-cascade quarantine-note section."""

    return (
        markdown.rstrip()
        + "\n\n"
        + GENERATED_BLOCKED_CASCADE_QUARANTINE_HEADING
        + "\n\n"
        + GENERATED_BLOCKED_CASCADE_QUARANTINE_NOTE
        + "\n"
    )


def recent_failure_count_for_target(
    rows: list[dict[str, Any]],
    target_task: str,
    *,
    kinds: Optional[set[str]] = None,
) -> int:
    count = 0
    for proposal in reversed(rows):
        if str(proposal.get("target_task") or "") != target_task:
            if count:
                break
            continue
        if proposal.get("applied") and proposal.get("validation_passed") and not proposal.get("errors"):
            break
        failure_kind = str(proposal.get("failure_kind") or "")
        if kinds is None or failure_kind in kinds:
            count += 1
    return count


def should_compact_supervisor_repair_prompt(decision: SupervisorDecision) -> bool:
    if decision.action != "repair_daemon_programming":
        return False
    reason = decision.reason.casefold()
    return "durable llm parse/runtime diagnostics" in reason or "before the daemon exited" in reason


def task_board_summary(markdown: str) -> str:
    tasks = parse_tasks(markdown)
    counts = {
        "needed": sum(1 for task in tasks if task.status == "needed"),
        "in_progress": sum(1 for task in tasks if task.status == "in-progress"),
        "complete": sum(1 for task in tasks if task.status == "complete"),
        "blocked": sum(1 for task in tasks if task.status == "blocked"),
    }
    selectable = [task.label for task in tasks if task.status in {"needed", "in-progress"}][-6:]
    return json.dumps(
        {
            "counts": counts,
            "recentSelectable": selectable,
            "repairNoteSummary": compact_task_board_repair_notes(markdown),
        },
        indent=2,
        sort_keys=True,
    )


def proposal_validation_text(proposal: dict[str, Any]) -> str:
    parts: list[str] = []
    for error in proposal.get("errors", []) or []:
        parts.append(str(error))
    for result in proposal.get("validation_results", []) or []:
        if not isinstance(result, dict):
            continue
        parts.append(" ".join(str(part) for part in result.get("command", []) or []))
        parts.append(str(result.get("stdout", "")))
        parts.append(str(result.get("stderr", "")))
    return "\n".join(parts).lower()


def is_forbidden_absence_marker_validation_failure(proposal: dict[str, Any]) -> bool:
    """Detect fixtures/tests that self-trigger forbidden artifact marker checks."""

    if str(proposal.get("failure_kind") or "") != "validation":
        return False
    text = proposal_validation_text(proposal)
    if "unexpectedly found" not in text and "assertnotin" not in text:
        return False
    return any(marker in text for marker in FORBIDDEN_ABSENCE_MARKERS)


def recent_forbidden_absence_marker_failure_count(
    rows: list[dict[str, Any]], *, completed_task_labels: Optional[set[str]] = None
) -> int:
    completed = completed_task_labels or set()
    count = 0
    latest_task = ""
    for proposal in reversed(rows):
        target = str(proposal.get("target_task") or "")
        if target_matches_any_label(target, completed):
            continue
        if proposal.get("applied") and proposal.get("validation_passed") and not proposal.get("errors"):
            break
        if not latest_task:
            latest_task = target
        if target != latest_task:
            break
        if not is_forbidden_absence_marker_validation_failure(proposal):
            break
        count += 1
    return count


def is_syntax_or_compile_failure(proposal: dict[str, Any]) -> bool:
    if str(proposal.get("failure_kind") or "") not in {"validation", "syntax_preflight"}:
        return False
    text = proposal_validation_text(proposal)
    return any(marker in text for marker in SYNTAX_OR_COMPILE_FAILURE_MARKERS)


def has_malformed_python_proposal_syntax(proposal: dict[str, Any]) -> bool:
    text = proposal_validation_text(proposal)
    return any(marker in text for marker in MALFORMED_PYTHON_PROPOSAL_MARKERS)


def recent_syntax_failure_count(
    rows: list[dict[str, Any]], *, limit: int = 6, completed_task_labels: Optional[set[str]] = None
) -> int:
    completed = completed_task_labels or set()
    count = 0
    inspected = 0
    for proposal in reversed(rows):
        if target_matches_any_label(str(proposal.get("target_task") or ""), completed):
            continue
        if proposal.get("applied") and proposal.get("validation_passed") and not proposal.get("errors"):
            break
        inspected += 1
        if not is_syntax_or_compile_failure(proposal):
            break
        count += 1
        if inspected >= limit:
            break
    return count


def repeated_malformed_syntax_count(
    rows: list[dict[str, Any]], *, completed_task_labels: Optional[set[str]] = None
) -> int:
    completed = completed_task_labels or set()
    latest_task = ""
    count = 0
    for proposal in reversed(rows):
        target = str(proposal.get("target_task") or "")
        if target_matches_any_label(target, completed):
            continue
        if proposal.get("applied") and proposal.get("validation_passed") and not proposal.get("errors"):
            break
        if not latest_task:
            latest_task = target
        if target != latest_task:
            break
        if not is_syntax_or_compile_failure(proposal):
            break
        if has_malformed_python_proposal_syntax(proposal):
            count += 1
    return count


def is_private_session_preflight_false_positive(proposal: dict[str, Any]) -> bool:
    if str(proposal.get("failure_kind") or "") != "preflight":
        return False
    errors = [str(error).lower() for error in proposal.get("errors", []) or []]
    if not any("private/session artifacts" in error for error in errors):
        return False
    files = [str(path) for path in proposal.get("files", []) or [] if isinstance(path, str)]
    return any("session" in path.lower() and not is_private_write_path(path) for path in files)


def is_empty_task_board_truncation_proposal(proposal: dict[str, Any]) -> bool:
    """Detect a worker no-op caused by truncated task-board context."""

    if proposal.get("applied"):
        return False
    if proposal.get("files") or proposal.get("changed_files") or proposal.get("errors"):
        return False
    target = str(proposal.get("target_task") or "").lower()
    if "checkbox-133" not in target or "task-board-only supersession note" not in target:
        return False
    text = " ".join(
        str(proposal.get(field) or "")
        for field in ("summary", "impact", "failure_kind")
    ).lower()
    return "task-board.md" in text and "truncated" in text


def is_checkbox_133_no_file_stall(proposal: dict[str, Any]) -> bool:
    if proposal.get("applied"):
        return False
    if proposal.get("files") or proposal.get("changed_files"):
        return False
    target = str(proposal.get("target_task") or "").lower()
    if "checkbox-133" not in target or "task-board-only supersession note" not in target:
        return False
    if is_empty_task_board_truncation_proposal(proposal):
        return True
    return str(proposal.get("failure_kind") or "") in {"parse", "llm", "no_change", ""}


def has_recent_checkbox_133_no_file_stall(rows: list[dict[str, Any]], latest: dict[str, Any]) -> bool:
    candidates = [latest] if latest else []
    candidates.extend(reversed(rows[-4:]))
    return any(is_checkbox_133_no_file_stall(candidate) for candidate in candidates)


def has_checkbox_108_supersession_prerequisites(rows: list[dict[str, Any]]) -> bool:
    """Return True when accepted work covers the checkbox-133 prerequisites."""

    accepted_text = "\n".join(
        " ".join(
            str(row.get(field) or "")
            for field in ("target_task", "summary", "impact")
        ).lower()
        for row in rows
        if row.get("applied") and row.get("validation_passed") and not row.get("errors")
    )
    required_markers = (
        "checkbox-130",
        "checkbox-131",
        "checkbox-109",
        "queued",
        "accepted",
        "skipped",
        "deferred",
        "allowlist",
        "robots/no-persist",
        "content-type",
        "timeout",
        "processor-handoff",
    )
    return all(marker in accepted_text for marker in required_markers)


def builtin_supersession_repair_task_board(markdown: str, rows: list[dict[str, Any]]) -> tuple[str, tuple[str, ...]]:
    """Append checkbox-108 supersession note and complete the board-only repair task."""

    if "## Checkbox-108 Supersession Note" in markdown:
        return markdown, ()
    if not has_checkbox_108_supersession_prerequisites(rows):
        return markdown, ()

    changed_labels: list[str] = []
    repaired_lines: list[str] = []
    for line in markdown.splitlines(keepends=True):
        stripped = line.rstrip("\n")
        if stripped.startswith("- [!] Task checkbox-108:") or stripped.startswith("- [~] Task checkbox-108:"):
            line = line.replace("- [!]", "- [x]", 1).replace("- [~]", "- [x]", 1)
            changed_labels.append("checkbox-108")
        elif stripped.startswith("- [!] Task checkbox-132:") or stripped.startswith("- [~] Task checkbox-132:") or stripped.startswith("- [ ] Task checkbox-132:"):
            line = line.replace("- [!]", "- [x]", 1).replace("- [~]", "- [x]", 1).replace("- [ ]", "- [x]", 1)
            changed_labels.append("checkbox-132")
        elif stripped.startswith("- [~] Task checkbox-133:") or stripped.startswith("- [ ] Task checkbox-133:"):
            line = line.replace("- [~]", "- [x]", 1).replace("- [ ]", "- [x]", 1)
            changed_labels.append("checkbox-133")
        repaired_lines.append(line)

    if not {"checkbox-108", "checkbox-133"}.issubset(set(changed_labels)):
        return markdown, ()

    note = (
        "\n"
        "## Checkbox-108 Supersession Note\n\n"
        "- Checkbox-108 is superseded on the task board only. Accepted checkbox-109, checkbox-130, "
        "checkbox-131, and checkbox-132 evidence covers queued, accepted, skipped, deferred, allowlist, "
        "robots/no-persist, content-type, timeout, and processor-handoff behavior. No crawler contracts, "
        "crawler code, public fixtures, crawl output, live automation, or authenticated DevHub artifacts were added for this supersession.\n"
    )
    return "".join(repaired_lines).rstrip() + note, tuple(changed_labels)


def next_checkbox_number(markdown: str) -> int:
    values = [int(match.group(1)) for match in CHECKBOX_ID_RE.finditer(markdown)]
    return (max(values) + 1) if values else 1


def recent_accepted_streak(rows: list[dict[str, Any]], *, limit: int = 8) -> int:
    streak = 0
    for row in reversed(rows):
        if row.get("applied") and row.get("validation_passed") and not row.get("errors"):
            streak += 1
            if streak >= limit:
                break
            continue
        break
    return streak


def should_use_broader_goal_slices(rows: list[dict[str, Any]]) -> bool:
    """Allow wider fallback tasks only after the daemon has proven stability."""

    return recent_accepted_streak(rows, limit=4) >= 4


def replenishment_heading_number(line: str) -> Optional[int]:
    match = REPLENISHMENT_HEADING_RE.match(line.strip())
    if not match:
        return None
    value = match.group(1)
    return int(value) if value else 1


def sanitize_agentic_replenishment_board(markdown: str) -> tuple[str, bool]:
    """Normalize duplicate agentic replenishment headings and repeated titles.

    Agentic planner patches have occasionally appended a new tranche with an old
    heading such as "Tranche 2" and repeated broad titles. This sanitizer rewrites
    only the newest replenishment section to the next heading number and swaps
    repeated task titles for deterministic hardening titles before the daemon is
    restarted on stale work.
    """

    lines = markdown.splitlines()
    heading_indexes = [
        index for index, line in enumerate(lines) if replenishment_heading_number(line) is not None
    ]
    if len(heading_indexes) < 2:
        return markdown, False

    latest_heading_index = heading_indexes[-1]
    previous_heading_numbers = [
        replenishment_heading_number(lines[index]) or 1 for index in heading_indexes[:-1]
    ]
    expected_heading_number = max(previous_heading_numbers) + 1
    changed = False

    if replenishment_heading_number(lines[latest_heading_index]) != expected_heading_number:
        lines[latest_heading_index] = f"## Built-In Goal Replenishment Tranche {expected_heading_number}"
        changed = True

    previous_titles: set[str] = set()
    for line in lines[:latest_heading_index]:
        match = TASK_LINE_RE.match(line)
        if match:
            previous_titles.add(" ".join(match.group("title").casefold().split()))

    task_indexes: list[int] = []
    for index in range(latest_heading_index + 1, len(lines)):
        if index != latest_heading_index + 1 and lines[index].startswith("## "):
            break
        if TASK_LINE_RE.match(lines[index]):
            task_indexes.append(index)

    latest_titles = []
    for index in task_indexes:
        match = TASK_LINE_RE.match(lines[index])
        if match:
            latest_titles.append(" ".join(match.group("title").casefold().split()))
    repeated_title = any(title in previous_titles for title in latest_titles)
    if repeated_title:
        for offset, index in enumerate(task_indexes):
            if offset >= len(SANITIZED_REPLENISHMENT_TITLES):
                break
            match = TASK_LINE_RE.match(lines[index])
            if not match:
                continue
            lines[index] = match.group("prefix") + SANITIZED_REPLENISHMENT_TITLES[offset]
        changed = True

    if not changed:
        return markdown, False
    return "\n".join(lines) + ("\n" if markdown.endswith("\n") else ""), True


def normalized_task_title(title: str) -> str:
    normalized = " ".join(str(title or "").casefold().split())
    return normalized.rstrip(".")


def existing_task_titles(markdown: str) -> set[str]:
    titles: set[str] = set()
    for line in markdown.splitlines():
        match = TASK_LINE_RE.match(line)
        if match:
            titles.add(normalized_task_title(match.group("title")))
    return titles


def task_title_already_covered(candidate: str, titles: set[str]) -> bool:
    normalized = normalized_task_title(candidate)
    if normalized in titles:
        return True
    return any(
        len(title) >= 40 and (title in normalized or normalized in title)
        for title in titles
    )


def next_replenishment_heading(markdown: str) -> str:
    numbers = [
        replenishment_heading_number(line)
        for line in markdown.splitlines()
        if replenishment_heading_number(line) is not None
    ]
    if not numbers:
        return "## Built-In Goal Replenishment Tranche"
    return f"## Built-In Goal Replenishment Tranche {max(numbers) + 1}"


def autonomous_platform_heading_number(line: str) -> Optional[int]:
    match = AUTONOMOUS_PLATFORM_HEADING_RE.match(line.strip())
    if not match:
        return None
    if match.group(1) is None:
        return 1
    return int(match.group(1))


def next_autonomous_platform_heading(markdown: str) -> str:
    numbers = [
        autonomous_platform_heading_number(line)
        for line in markdown.splitlines()
        if autonomous_platform_heading_number(line) is not None
    ]
    if not numbers:
        return "## Built-In Autonomous PP&D Platform Tranche"
    return f"## Built-In Autonomous PP&D Platform Tranche {max(numbers) + 1}"


def autonomous_execution_heading_number(line: str) -> Optional[int]:
    match = AUTONOMOUS_EXECUTION_HEADING_RE.match(line.strip())
    if not match:
        return None
    if match.group(1) is None:
        return 1
    return int(match.group(1))


def next_autonomous_execution_heading(markdown: str) -> str:
    numbers = [
        autonomous_execution_heading_number(line)
        for line in markdown.splitlines()
        if autonomous_execution_heading_number(line) is not None
    ]
    if not numbers:
        return "## Built-In Autonomous PP&D Execution Capability Tranche"
    return f"## Built-In Autonomous PP&D Execution Capability Tranche {max(numbers) + 1}"


def source_backed_execution_continuation_heading_number(line: str) -> Optional[int]:
    match = SOURCE_BACKED_EXECUTION_CONTINUATION_HEADING_RE.match(line.strip())
    if not match:
        return None
    if match.group(1) is None:
        return 1
    return int(match.group(1))


def next_source_backed_execution_continuation_heading(markdown: str) -> str:
    numbers = [
        source_backed_execution_continuation_heading_number(line)
        for line in markdown.splitlines()
        if source_backed_execution_continuation_heading_number(line) is not None
    ]
    if not numbers:
        return "## Built-In Source-Backed Execution Continuation Tranche"
    return f"## Built-In Source-Backed Execution Continuation Tranche {max(numbers) + 1}"


def source_backed_execution_continuation_count(markdown: str) -> int:
    """Return how many generated source-backed continuation tranches exist."""

    return sum(
        1
        for line in markdown.splitlines()
        if source_backed_execution_continuation_heading_number(line) is not None
    )


def should_append_autonomous_platform_tranche(markdown: str) -> bool:
    """Return True when completed recovery work should advance to platform work."""

    if any(autonomous_platform_heading_number(line) is not None for line in markdown.splitlines()):
        return False
    lowered = markdown.casefold()
    markers = (
        "manual recovery tranche 20",
        "built-in blocked cascade recovery tranche",
        "checkbox-218",
    )
    if not any(marker in lowered for marker in markers):
        return False
    return (
        "portland permitting" in lowered
        or "pp&d" in lowered
        or "devhub" in lowered
        or "processor" in lowered
    )


def has_autonomous_execution_tranche(markdown: str) -> bool:
    return any(autonomous_execution_heading_number(line) is not None for line in markdown.splitlines())


def compact_repeated_autonomous_platform_tranches(markdown: str) -> tuple[str, int]:
    """Remove repeated generated platform tranches while preserving the first one."""

    lines = markdown.splitlines()
    output: list[str] = []
    seen_platform_tranches = 0
    removed_tranches = 0
    index = 0
    while index < len(lines):
        line = lines[index]
        if autonomous_platform_heading_number(line) is None:
            output.append(line)
            index += 1
            continue

        seen_platform_tranches += 1
        if seen_platform_tranches == 1:
            output.append(line)
            index += 1
            continue

        removed_tranches += 1
        index += 1
        while index < len(lines):
            current = lines[index]
            if current.startswith("## "):
                if current.strip() == "## Built-In Supervisor Planning Notes":
                    index += 1
                    while index < len(lines) and not lines[index].startswith("## "):
                        index += 1
                    continue
                break
            index += 1

    if not removed_tranches:
        return markdown, 0
    compacted = "\n".join(output).rstrip()
    if "## Built-In Autonomous Platform Compaction Notes" not in compacted:
        compacted += (
            "\n\n## Built-In Autonomous Platform Compaction Notes\n\n"
            f"- Compacted {removed_tranches} repeated generated Autonomous PP&D Platform tranches. "
            "The supervisor now caps platform tranches at one and escalates once to source-backed "
            "execution-capability work instead of accepting runtime-only progress.\n"
        )
    else:
        compacted += "\n"
    return compacted, removed_tranches


def generated_autonomous_platform_templates(markdown: str, tranche_number: int) -> list[str]:
    """Build unique platform continuation work after the static tranche validates."""

    return [
        f"Add autonomous platform continuation coverage for tranche {tranche_number} proving whole-site archival, Playwright draft automation, PDF field filling, and formal-logic outputs stay connected through source evidence IDs.",
        f"Add processor-suite integration planning for tranche {tranche_number} proving PP&D public documents flow through archive manifests, normalized document records, PDF metadata, and requirement batches before agents use them.",
        f"Add Playwright/PDF handoff validation for tranche {tranche_number} proving redacted user facts can fill draft fields and PDF previews while official DevHub transitions stay behind exact confirmation checkpoints.",
        f"Add supervisor idle-recovery validation for tranche {tranche_number} proving completed boards synthesize new goal-aligned platform tasks without sleeping, duplicate tranche reuse, or blocked-task retry churn.",
    ]


def next_source_backed_execution_continuation_templates(markdown: str) -> tuple[list[str], int]:
    """Return non-duplicate deterministic continuation titles for the next tranche."""

    heading = next_source_backed_execution_continuation_heading(markdown)
    start_number = source_backed_execution_continuation_heading_number(heading) or 1
    titles = existing_task_titles(markdown)
    for tranche_number in range(start_number, start_number + 50):
        templates = generated_autonomous_platform_templates(markdown, tranche_number)
        if all(not task_title_already_covered(title, titles) for title in templates):
            return templates, tranche_number
    tranche_number = start_number + 50
    return generated_autonomous_platform_templates(markdown, tranche_number), tranche_number


def builtin_source_backed_execution_continuation_task_board(markdown: str) -> tuple[str, tuple[str, ...]]:
    """Append deterministic source-backed continuation when historical repair work is parked."""

    if source_backed_execution_continuation_count(markdown) >= MAX_SOURCE_BACKED_EXECUTION_CONTINUATION_TRANCHES:
        return markdown, ()

    templates, tranche_number = next_source_backed_execution_continuation_templates(markdown)
    start = next_checkbox_number(markdown)
    labels = tuple(f"checkbox-{start + offset}" for offset in range(len(templates)))
    lines = ["", next_source_backed_execution_continuation_heading(markdown), ""]
    for offset, text in enumerate(templates):
        lines.append(f"- [ ] Task checkbox-{start + offset}: {text}")
    note = (
        "\n"
        "## Built-In Supervisor Planning Notes\n\n"
        "- The supervisor found no selectable work after generated blocked-cascade tasks were already parked. "
        "It appended source-backed deterministic continuation tasks instead of opening another generated repair tranche or sleeping on a historical circuit breaker.\n"
        f"- Slice policy: `source_backed_execution_continuation_{tranche_number}`. These tasks are matched by deterministic daemon fallbacks and keep progress inside public archival, processor handoff, attended Playwright/PDF planning, formal-logic, and idle-recovery contracts.\n"
    )
    return markdown.rstrip() + "\n" + "\n".join(lines) + note, labels


def reopen_blocked_manual_goal_tasks(
    markdown: str,
    *,
    limit: int = MANUAL_GOAL_REOPEN_LIMIT,
) -> tuple[str, tuple[str, ...]]:
    """Reopen a bounded slice from the human-authored comprehensive PP&D tranche."""

    lines = markdown.splitlines(keepends=True)
    in_manual_tranche = False
    reopened: list[str] = []
    repaired_lines: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped == MANUAL_COMPREHENSIVE_GOAL_HEADING:
            in_manual_tranche = True
        elif in_manual_tranche and stripped.startswith("## "):
            in_manual_tranche = False

        if in_manual_tranche and len(reopened) < limit and line.lstrip().startswith("- [!] Task checkbox-"):
            checkbox = CHECKBOX_ID_RE.search(line)
            if checkbox:
                line = line.replace("- [!]", "- [ ]", 1)
                reopened.append(f"checkbox-{checkbox.group(1)}")
        repaired_lines.append(line)

    if not reopened:
        return markdown, ()

    note = (
        "\n"
        "## Built-In Manual Goal Reopen Notes\n\n"
        "- Reopened a bounded slice of the human-authored comprehensive PP&D goal tranche after every "
        "selectable task was blocked. The daemon should prefer these source-backed tasks over adding "
        "more generated continuation tranches, and consequential live DevHub actions remain gated by "
        "user attendance and exact confirmation.\n"
    )
    return "".join(repaired_lines).rstrip() + note, tuple(reopened)


def should_escalate_stale_platform_slice(markdown: str, target_task: str) -> bool:
    """Return True when old narrow platform slices should yield to execution work."""

    lowered_board = markdown.casefold()
    lowered_target = str(target_task or "").casefold()
    target_markers = (
        "checkbox-225",
        "autonomous platform continuation",
        "tranche 2 proving whole-site archival",
        "playwright draft automation",
        "pdf field filling",
    )
    capability_markers = (
        "manual live execution boundary tranche",
        "manual attended worker hardening tranche",
        "manual attended worker journal tranche",
        "manual attended worker resume tranche",
    )
    return (
        "built-in autonomous pp&d platform tranche 2" in lowered_board
        and any(marker in lowered_target for marker in target_markers)
        and any(marker in lowered_board for marker in capability_markers)
    )


def builtin_autonomous_execution_replenish_task_board(markdown: str) -> tuple[str, tuple[str, ...]]:
    """Append comprehensive execution-capability work when old slices stall."""

    if any(autonomous_execution_heading_number(line) is not None for line in markdown.splitlines()):
        return markdown, ()
    templates = choose_non_duplicate_replenishment_templates(
        markdown,
        [list(AUTONOMOUS_EXECUTION_CAPABILITY_TITLES)],
        tuple(
            f"Add generated autonomous execution capability coverage for item {offset} proving live public archival, attended Playwright, PDF draft filling, formal logic guardrails, and supervisor recovery remain connected without private artifacts or official DevHub actions."
            for offset in range(1, 7)
        ),
    )
    start = next_checkbox_number(markdown)
    labels = tuple(f"checkbox-{start + offset}" for offset in range(len(templates)))
    lines = ["", next_autonomous_execution_heading(markdown), ""]
    for offset, text in enumerate(templates):
        lines.append(f"- [ ] Task checkbox-{start + offset}: {text}")
    note = (
        "\n"
        "## Built-In Supervisor Planning Notes\n\n"
        "- The supervisor detected stale narrow autonomous-platform work after live public scraping, attended Playwright, and PDF filling boundaries were added. "
        "It appended a broader execution-capability tranche aligned to the current goal: whole-site public archival, processor-suite execution, attended DevHub draft automation, local PDF previews, and formal-logic guardrails.\n"
        "- Slice policy: `autonomous_execution_capability_after_goal_drift`. These tasks are larger than parser-recovery slices but still keep live/authenticated work behind allowlists, user attendance, exact confirmations, and no-private-artifact persistence.\n"
    )
    return markdown.rstrip() + "\n" + "\n".join(lines) + note, labels


def builtin_autonomous_execution_goal_repair_task_board(
    markdown: str,
    target_task: str,
) -> tuple[str, tuple[str, ...], tuple[str, ...]]:
    """Park stale narrow platform tasks and append comprehensive execution work."""

    repaired, parked = builtin_stalled_worker_task_board(markdown, target_task)
    if not should_escalate_stale_platform_slice(markdown, target_task):
        return repaired, parked, ()

    stale_labels: list[str] = []
    repaired_lines: list[str] = []
    for line in repaired.splitlines(keepends=True):
        stripped = line.rstrip("\n")
        stale_match = re.match(r"- \[(?P<mark>[ ~!])\] Task (?P<label>checkbox-22[5-8]):", stripped)
        if stale_match and stale_match.group("mark") != "!":
            line = line.replace("- [~]", "- [!]", 1).replace("- [ ]", "- [!]", 1)
            stale_labels.append(stale_match.group("label"))
        repaired_lines.append(line)
    repaired = "".join(repaired_lines)
    if stale_labels and "## Built-In Autonomous Execution Supersession Notes" not in repaired:
        repaired = (
            repaired.rstrip()
            + "\n\n## Built-In Autonomous Execution Supersession Notes\n\n"
            + "- Parked stale Autonomous PP&D Platform Tranche 2 tasks because the goal has moved from fixture-only continuation slices to supervised execution capabilities for whole-site archival, attended Playwright draft work, local PDF previews, and formal-logic guardrails.\n"
        )

    repaired, replenished = builtin_autonomous_execution_replenish_task_board(repaired)
    return repaired, tuple(stale_labels) or parked, replenished


def blocked_cascade_heading_number(line: str) -> Optional[int]:
    match = BLOCKED_CASCADE_HEADING_RE.match(line.strip())
    if not match:
        return None
    if match.group(1) is None:
        return 1
    return int(match.group(1))


def next_blocked_cascade_heading(markdown: str) -> str:
    numbers = [
        blocked_cascade_heading_number(line)
        for line in markdown.splitlines()
        if blocked_cascade_heading_number(line) is not None
    ]
    if not numbers:
        return "## Built-In Blocked Cascade Recovery Tranche"
    return f"## Built-In Blocked Cascade Recovery Tranche {max(numbers) + 1}"


def choose_non_duplicate_replenishment_templates(
    markdown: str, candidate_tranches: list[list[str]], fallback: tuple[str, ...]
) -> list[str]:
    titles = existing_task_titles(markdown)
    for templates in candidate_tranches:
        if all(not task_title_already_covered(title, titles) for title in templates):
            return templates
    return list(fallback)


def generated_nonduplicate_replenishment_templates(markdown: str, tranche_number: int) -> list[str]:
    """Build deterministic continuation tasks that remain unique after static rotations."""

    return [
        f"Add daemon generated-replenishment continuation coverage for tranche {tranche_number} proving fallback task titles include the tranche number and do not repeat completed supervisor hardening titles.",
        f"Add a fixture-only PP&D requirement-risk register scenario for tranche {tranche_number} plus focused validation linking source evidence, requirement IDs, risk categories, and fail-closed guardrail responses.",
        f"Add a fixture-only agent handoff readiness report for tranche {tranche_number} plus focused validation summarizing known user facts, missing facts, source freshness, and exact-confirmation blockers.",
        f"Add a fixture-only formal-logic regression pack for tranche {tranche_number} plus focused validation checking obligation predicates, prerequisite predicates, reversible action predicates, and refused official-action predicates.",
    ]


def builtin_replenish_goal_tasks(markdown: str, rows: Optional[list[dict[str, Any]]] = None) -> tuple[str, tuple[str, ...]]:
    """Append a deterministic fixture-first tranche when agentic planning fails.

    The fallback starts with small recovery-safe slices after failures, then uses
    broader implementation-plus-validation slices after a healthy accepted streak.
    """

    markdown, _removed_platform_tranches = compact_repeated_autonomous_platform_tranches(markdown)
    tasks = parse_tasks(markdown)
    if not tasks or any(task.status in {"needed", "in-progress"} for task in tasks):
        return markdown, ()

    reopened_board, reopened_labels = reopen_blocked_manual_goal_tasks(markdown)
    if reopened_labels:
        return reopened_board, reopened_labels

    start = next_checkbox_number(markdown)
    if any(autonomous_platform_heading_number(line) is not None for line in markdown.splitlines()):
        if not has_autonomous_execution_tranche(markdown):
            return builtin_autonomous_execution_replenish_task_board(markdown)
        return builtin_source_backed_execution_continuation_task_board(markdown)
    if should_append_autonomous_platform_tranche(markdown):
        heading = next_autonomous_platform_heading(markdown)
        heading_number = autonomous_platform_heading_number(heading) or 1
        templates = choose_non_duplicate_replenishment_templates(
            markdown,
            [list(AUTONOMOUS_PLATFORM_REPLENISHMENT_TITLES)],
            tuple(generated_autonomous_platform_templates(markdown, heading_number)),
        )
        labels = tuple(f"checkbox-{start + offset}" for offset in range(len(templates)))
        lines = ["", heading, ""]
        for offset, text in enumerate(templates):
            lines.append(f"- [ ] Task checkbox-{start + offset}: {text}")
        note = (
            "\n"
            "## Built-In Supervisor Planning Notes\n\n"
            "- The completed PP&D recovery board now advances into autonomous platform work. "
            "This tranche is aligned to whole-site public archival, ipfs_datasets_py processor-suite handoff, "
            "guarded Playwright draft automation, local PDF field filling, and formal-logic guardrail extraction.\n"
            "- Slice policy: `autonomous_platform_after_completed_recovery`. The supervisor uses this deterministic tranche "
            "when an all-complete PP&D board would otherwise leave the daemon with no work.\n"
        )
        return markdown.rstrip() + "\n" + "\n".join(lines) + note, labels

    existing_tranche_numbers = [
        replenishment_heading_number(line)
        for line in markdown.splitlines()
        if replenishment_heading_number(line) is not None
    ]
    heading = next_replenishment_heading(markdown)
    broader = should_use_broader_goal_slices(rows or []) or bool(existing_tranche_numbers)
    if broader:
        broad_tranches = [
            [
                "Add an end-to-end fixture-only handoff scenario plus focused validation linking processor archival evidence, extracted requirement nodes, formal-logic guardrails, and draft-only Playwright planning without live crawling, authenticated automation, raw browser state, or official DevHub actions.",
                "Add a fixture-only user gap-resolution scenario plus focused validation that turns missing PP&D facts, stale evidence flags, and document placeholders into source-linked user questions and refuses autonomous completion while gaps remain.",
                "Add supervisor adaptive-slice regression coverage proving completed board-level recovery tranches enable broader non-duplicate goal slices even when accepted daemon ledger rows lag behind manual validated recovery work.",
                "Add an offline Playwright draft transcript fixture plus focused validation proving future agents can plan accessible-selector fills from redacted state while preserving exact-confirmation gates for upload, submit, payment, certification, cancellation, MFA, CAPTCHA, and inspection scheduling.",
            ],
            [
                "Add a fixture-only source-change impact scenario plus focused validation that routes updated PP&D public evidence through archival provenance, affected requirement IDs, stale guardrail invalidation, and human-review flags before agents reuse old answers.",
                "Add a fixture-only agent work-order scenario plus focused validation that composes user document-store facts, missing PP&D facts, formal stop gates, and draft-only Playwright previews into an ordered autonomous-assistance plan without official DevHub actions.",
                "Add daemon parse-failure recovery coverage proving repeated non-JSON LLM responses for a completed or manually satisfied task are parked or superseded instead of being retried indefinitely.",
                "Add a fixture-only permit-process comparison scenario plus focused validation that contrasts two PP&D process types and preserves separate legal obligations, operational UI hints, document placeholders, fee notices, and exact-confirmation gates.",
            ],
            [
                "Add a fixture-only audit export scenario plus focused validation that records source evidence, user-question decisions, redacted draft previews, guardrail outcomes, and refused official actions for downstream human review.",
                "Add a fixture-only stale-answer reconciliation scenario plus focused validation that compares user document-store facts against newer PP&D evidence and fails closed when citations, timestamps, or requirement IDs conflict.",
                "Add supervisor replenishment rotation coverage proving third and later completed tranches do not duplicate the previous broad tranche titles.",
                "Add a fixture-only Playwright selector drift scenario plus focused validation that detects changed accessible names, refuses low-confidence selectors, and asks for human review before draft-preview automation continues.",
            ],
            [
                "Add supervisor validation-failure classification coverage proving forbidden-marker self-triggering fixture fields are detected and converted into neutral absence-field repair guidance.",
                "Add daemon prompt-repair coverage proving validation failures from forbidden marker substrings produce a JSON-only retry instruction with neutral artifact field names.",
                "Add supervisor stale-status reconciliation coverage proving a no-eligible or calling_llm status with a completed board triggers deterministic replanning instead of observe or restart churn.",
                "Add daemon LLM result-persistence coverage proving parse, timeout, validation-interrupted, and vanished-child failures are recorded before the worker exits or restarts.",
            ],
        ]
        max_tranche_number = max((number or 0 for number in existing_tranche_numbers), default=0)
        if max_tranche_number >= len(broad_tranches) + 2:
            next_tranche_number = max_tranche_number + 1
            generated_templates = generated_nonduplicate_replenishment_templates(markdown, next_tranche_number)
            templates = choose_non_duplicate_replenishment_templates(
                markdown,
                [
                    list(FOLLOWUP_REPLENISHMENT_TITLES),
                    list(SECOND_FOLLOWUP_REPLENISHMENT_TITLES),
                    list(THIRD_FOLLOWUP_REPLENISHMENT_TITLES),
                    generated_templates,
                    *broad_tranches,
                ],
                tuple(generated_templates),
            )
        else:
            templates = choose_non_duplicate_replenishment_templates(
                markdown, broad_tranches, FOLLOWUP_REPLENISHMENT_TITLES
            )
        policy = "broad_integrated_after_green_streak"
    else:
        templates = [
            "Add a fixture-only processor archive integration manifest that maps PP&D public source URLs, canonical document IDs, content-hash placeholders, and processor handoff IDs without crawling, downloading documents, or storing raw bodies.",
            "Add validation for the processor archive integration manifest proving every archived public source has citation-backed provenance, no private DevHub data, no raw crawl output, and a deterministic handoff ID for formal-logic extraction.",
            "Add a mocked Playwright draft-fill plan fixture for one PP&D form that ranks selectors by evidence confidence, maps missing user facts to questions, and limits automation to reversible draft-only field previews.",
            "Add validation for the Playwright draft-fill plan fixture proving low-confidence selectors, uploads, submissions, payments, certifications, cancellations, MFA, CAPTCHA, and inspection scheduling remain refused by default.",
            "Add a fixture-only formal-logic guardrail bundle that translates one archived PP&D requirement set into obligations, prerequisites, stop gates, reversible actions, and exact-confirmation requirements.",
            "Add validation for formal-logic guardrail bundles proving missing citations, stale evidence, private values, and consequential or financial actions fail closed before any LLM agent may plan autonomous completion.",
        ]
        policy = "small_recovery_safe_after_failures"
    labels = tuple(f"checkbox-{start + offset}" for offset in range(len(templates)))
    lines = ["", heading, ""]
    for offset, text in enumerate(templates):
        lines.append(f"- [ ] Task checkbox-{start + offset}: {text}")
    note = (
        "\n"
        "## Built-In Supervisor Planning Notes\n\n"
        "- The agentic planner did not return an acceptable task-board replacement, so the supervisor appended a deterministic tranche aligned to the original PP&D archival, Playwright draft automation, and formal-logic guardrail goals.\n"
        f"- Slice policy: `{policy}`. Small slices are used after parse, syntax, validation, or task-board repair failures; broader integrated slices are used after a green accepted streak.\n"
    )
    return markdown.rstrip() + "\n" + "\n".join(lines) + note, labels


def should_blocked_tasks_interrupt(blocked_count: int, selectable_count: int, threshold: int) -> bool:
    return blocked_count >= threshold and selectable_count == 0


def has_blocked_recovery_cascade(tasks: list[Task], *, blocked_threshold: int = 2) -> bool:
    blocked = [task for task in tasks if task.status == "blocked"]
    selectable = [task for task in tasks if task.status in {"needed", "in-progress"}]
    return len(blocked) >= blocked_threshold and not selectable


def builtin_blocked_cascade_replenish_task_board(markdown: str) -> tuple[str, tuple[str, ...]]:
    """Append deterministic daemon-repair tasks when all selectable work is blocked."""

    tasks = parse_tasks(markdown)
    if generated_blocked_cascade_budget_exhausted(tasks):
        return markdown, ()

    start = next_checkbox_number(markdown)
    heading = next_blocked_cascade_heading(markdown)
    heading_number = blocked_cascade_heading_number(heading) or 1
    candidate_tranches = [
        [
            "Add supervisor blocked-cascade recovery coverage proving a board with only blocked domain/recovery tasks gets deterministic daemon-repair tasks without invoking the LLM repair path.",
            "Add daemon blocked-task prompt-budget fixture coverage proving repeated llm_router exits summarize the target, compact errors, and next daemon-repair hint without retrying blocked domain work.",
            "Add daemon task-selection coverage proving blocked tasks are skipped until a new non-blocked repair task is accepted or a human explicitly reopens the blocked task.",
            "Add supervisor recovery-note compaction coverage proving repeated repair notes are summarized before future prompt construction so task-board context stays bounded.",
        ],
        [
            "Add one daemon-only unittest proving `select_task` does not choose blocked checkbox-178 when a fresh unchecked daemon-repair task exists, even if `revisit_blocked` is enabled.",
            "Add one supervisor regression proving a blocked-only PP&D board appends a fresh daemon-repair tranche before restarting a worker with blocked revisits enabled.",
            "Add one parser-clean prompt-scope unittest proving checkbox-178 retries stay blocked after three syntax_preflight failures until a daemon-repair task passes validation.",
            "Add one task-board accounting unittest proving duplicate generated-status sections outside the managed marker are detected before daemon task selection.",
        ],
    ]
    fallback = tuple(
        f"Add generated blocked-cascade daemon-repair coverage for tranche {heading_number} item {offset} proving blocked PP&D work stays parked until a fresh daemon repair task validates."
        for offset in range(1, 5)
    )
    templates = choose_non_duplicate_replenishment_templates(markdown, candidate_tranches, fallback)
    labels = tuple(f"checkbox-{start + offset}" for offset in range(len(templates)))
    lines = ["", heading, ""]
    for offset, text in enumerate(templates):
        lines.append(f"- [ ] Task checkbox-{start + offset}: {text}")
    note = (
        "\n"
        "## Built-In Supervisor Repair Notes\n\n"
        "- Appended deterministic blocked-cascade recovery tasks because all selectable work was blocked. "
        "The supervisor avoided the LLM repair path and created daemon-repair tasks that can run independently before blocked domain work is retried.\n"
    )
    return markdown.rstrip() + "\n" + "\n".join(lines) + note, labels


def title_from_task_label(label: str) -> str:
    """Return the innermost checkbox task title from a daemon target label."""

    text = str(label or "").strip()
    while True:
        replaced = TASK_TITLE_RE.sub("", text, count=1).strip()
        if replaced == text:
            return text
        text = replaced


def task_matching_target(tasks: list[Task], target_task: str) -> Optional[Task]:
    target_title = title_from_task_label(target_task)
    for task in tasks:
        if task.label == target_task or (target_title and task.title == target_title):
            return task
    return None


def rows_for_current_task_board(rows: list[dict[str, Any]], tasks: list[Task]) -> list[dict[str, Any]]:
    """Keep failure-history decisions scoped to tasks still present on the board."""

    labels = {task.label for task in tasks}
    titles = {task.title for task in tasks}
    filtered: list[dict[str, Any]] = []
    for row in rows:
        target = str(row.get("target_task") or "")
        target_title = title_from_task_label(target)
        if target in labels or (target_title and target_title in titles):
            filtered.append(row)
    return filtered


def builtin_repair_task_board(markdown: str, rows: list[dict[str, Any]]) -> tuple[str, tuple[str, ...]]:
    """Park a repeated syntax-loop task so the daemon can advance autonomously."""

    parse_loop_target = recent_parse_or_llm_failure_target(rows)
    if parse_loop_target:
        target_title = title_from_task_label(parse_loop_target)
        changed = False
        repaired_lines: list[str] = []
        for line in markdown.splitlines(keepends=True):
            stripped = line.rstrip("\n")
            if target_title and target_title in stripped and ("- [~]" in stripped or "- [ ]" in stripped):
                line = line.replace("- [~]", "- [!]", 1).replace("- [ ]", "- [!]", 1)
                changed = True
            repaired_lines.append(line)
        if changed:
            note = (
                "\n"
                "## Built-In Supervisor Repair Notes\n\n"
                f"- Parked repeated LLM parse/runtime loop for `{target_title}` so the daemon can continue with the next independent selectable task. "
                "Resume only after prompt, parser, or retry policy has been updated.\n"
            )
            repaired = "".join(repaired_lines).rstrip() + note
            return repaired + "\n", (target_title,)

    syntax_failures = []
    for row in reversed(rows):
        if row.get("applied") and row.get("validation_passed") and not row.get("errors"):
            break
        if not is_syntax_or_compile_failure(row):
            break
        syntax_failures.append(row)
    if len(syntax_failures) < 2:
        return markdown, ()

    target_title = title_from_task_label(str(syntax_failures[0].get("target_task") or ""))
    if not target_title:
        return markdown, ()

    changed = False
    repaired_lines: list[str] = []
    for line in markdown.splitlines(keepends=True):
        match = None
        stripped = line.rstrip("\n")
        if target_title in stripped:
            match = stripped
        if match and "- [~]" in stripped:
            line = line.replace("- [~]", "- [!]", 1)
            changed = True
        elif match and "- [ ]" in stripped:
            line = line.replace("- [ ]", "- [!]", 1)
            changed = True
        repaired_lines.append(line)

    if not changed:
        return markdown, ()

    note = (
        "\n"
        "## Built-In Supervisor Repair Notes\n\n"
        f"- Parked repeated syntax-preflight loop for `{target_title}` so the daemon can continue with independent selectable work. "
        "The task should be resumed only after a narrow syntax-valid fixture/test repair is available.\n"
    )
    repaired = "".join(repaired_lines).rstrip() + note
    return repaired + "\n", (target_title,)


def builtin_dead_worker_task_board(markdown: str, target_task: str) -> tuple[str, tuple[str, ...]]:
    """Reset an in-progress task when the worker process died mid-cycle."""

    target_title = title_from_task_label(target_task)
    if not target_title:
        return markdown, ()

    changed = False
    repaired_lines: list[str] = []
    for line in markdown.splitlines(keepends=True):
        stripped = line.rstrip("\n")
        if target_title in stripped and "- [~]" in stripped:
            line = line.replace("- [~]", "- [ ]", 1)
            changed = True
        repaired_lines.append(line)

    if not changed:
        return markdown, ()

    note = (
        "\n"
        "## Built-In Supervisor Repair Notes\n\n"
        f"- Reset dead-worker in-progress task `{target_title}` to pending after the daemon process exited mid-cycle. "
        "The supervisor will restart the worker and let the task be selected again with a fresh timeout window.\n"
    )
    repaired = "".join(repaired_lines).rstrip() + note
    return repaired + "\n", (target_title,)


def builtin_stalled_worker_task_board(markdown: str, target_task: str) -> tuple[str, tuple[str, ...]]:
    """Park an actively stalled worker task so restart advances to independent work."""

    target_title = title_from_task_label(target_task)
    if not target_title:
        return markdown, ()

    changed = False
    repaired_lines: list[str] = []
    for line in markdown.splitlines(keepends=True):
        stripped = line.rstrip("\n")
        if target_title in stripped and ("- [~]" in stripped or "- [ ]" in stripped):
            line = line.replace("- [~]", "- [!]", 1).replace("- [ ]", "- [!]", 1)
            changed = True
        repaired_lines.append(line)

    if not changed:
        return markdown, ()

    note = (
        "\n"
        "## Built-In Supervisor Repair Notes\n\n"
        f"- Parked stalled worker task `{target_title}` after it exceeded the active-state timeout. "
        "The supervisor restarted the daemon on the next independent selectable task instead of reselecting the same stalled work.\n"
    )
    repaired = "".join(repaired_lines).rstrip() + note
    return repaired + "\n", (target_title,)


def diagnose(config: SupervisorConfig, *, now: Optional[datetime] = None) -> SupervisorDecision:
    pid = read_pid(config.resolve(config.pid_file))
    running = process_running(pid)
    status = load_json(config.resolve(config.status_file))
    progress = load_json(config.resolve(config.progress_file))
    board = read_text(config.resolve(config.task_board)) if config.resolve(config.task_board).exists() else ""
    tasks = parse_tasks(board)
    completed_task_labels = {task.label for task in tasks if task.status == "complete"}
    inactive_task_labels = {task.label for task in tasks if task.status in {"complete", "blocked"}}
    rows = read_supervisor_result_rows(config.resolve(config.result_log))
    current_rows = rows_for_current_task_board(rows, tasks)
    latest = progress.get("latest") if isinstance(progress.get("latest"), dict) else {}
    heartbeat_age = age_seconds(status.get("updated_at"), now=now)
    active_state = str(status.get("active_state") or status.get("state") or "")
    active_state_age = age_seconds(status.get("active_state_started_at"), now=now)
    termination_storm_count, termination_storm_targets = recent_llm_termination_storm_count(current_rows)
    active_breaker, breaker_remaining = active_termination_storm_circuit_breaker(config, now=now)
    generated_blocked_total, generated_blocked_open = generated_blocked_cascade_task_counts(tasks)
    has_recovery_work = has_open_circuit_breaker_recovery_task(tasks)
    has_closed_recovery_work = has_closed_circuit_breaker_recovery_task(tasks)
    has_deterministic_work = has_open_deterministic_task_fallback(tasks)
    has_selectable_work = any(task.status in {"needed", "in-progress"} for task in tasks)
    revisit_candidate = None
    if config.revisit_blocked_tasks and tasks and not has_selectable_work:
        revisit_candidate = select_task_for_config(
            tasks,
            DaemonConfig(
                repo_root=config.repo_root,
                result_log=config.result_log,
                revisit_blocked=True,
                revisit_blocked_ignore_failure_gates=True,
                revisit_blocked_reassess_llm_termination_gates=config.reassess_blocked_llm_termination_gates,
            ),
        )
    continuation_count = source_backed_execution_continuation_count(board)
    generated_budget_parked = generated_blocked_total >= MAX_GENERATED_BLOCKED_CASCADE_TASKS and generated_blocked_open == 0
    has_source_backed_continuation_context = (
        has_closed_recovery_work
        or has_autonomous_execution_tranche(board)
        or any(autonomous_platform_heading_number(line) is not None for line in board.splitlines())
    )

    if (
        not running
        and config.revisit_blocked_tasks
        and tasks
        and not has_selectable_work
        and revisit_candidate is not None
    ):
        return SupervisorDecision(
            action="restart_daemon",
            reason=(
                "no unchecked tasks remain, but blocked PP&D tasks are present; restart the daemon "
                "with blocked-task revisiting enabled instead of appending more generated work"
            ),
            severity="warning",
            should_restart_daemon=True,
        )

    if (
        not running
        and config.revisit_blocked_tasks
        and tasks
        and not has_selectable_work
        and any(task.status == "blocked" for task in tasks)
        and revisit_candidate is None
    ):
        return SupervisorDecision(
            action="observe",
            reason=(
                "blocked PP&D tasks remain, but every blocked task is behind a fresh failure gate; "
                "do not restart the daemon until new source-backed work is added or a task is explicitly reopened"
            ),
            severity="warning",
            should_restart_daemon=False,
        )

    if (
        not running
        and tasks
        and not has_selectable_work
        and continuation_count >= MAX_SOURCE_BACKED_EXECUTION_CONTINUATION_TRANCHES
        and generated_budget_parked
    ):
        return SupervisorDecision(
            action="plan_next_tasks",
            reason=(
                "source-backed deterministic continuation limit has been reached; stop appending "
                "placeholder tranches and require agentic or human-authored PP&D work"
            ),
            severity="warning",
            should_invoke_codex=True,
        )

    if (
        not running
        and not active_breaker
        and not has_recovery_work
        and has_closed_recovery_work
        and not generated_budget_parked
        and active_state == "paused_by_supervisor_circuit_breaker"
    ):
        return SupervisorDecision(
            action="recover_termination_storm_and_restart",
            reason=(
                "termination storm circuit breaker has expired after vetted recovery tasks were closed; "
                "append the next source-backed recovery continuation tranche before restarting the daemon"
            ),
            severity="critical",
            should_restart_daemon=True,
        )

    if (
        not running
        and tasks
        and not has_selectable_work
        and not has_recovery_work
        and generated_budget_parked
        and has_source_backed_continuation_context
    ):
        return SupervisorDecision(
            action="plan_next_tasks",
            reason=(
                "generated blocked-cascade repair budget is exhausted but all generated repair tasks are already "
                "parked; review the original PP&D goal and append source-backed deterministic continuation work "
                "instead of opening another circuit breaker"
            ),
            severity="warning",
            should_invoke_codex=True,
        )

    if tasks and all(task.status == "complete" for task in tasks) and has_autonomous_execution_tranche(board):
        return SupervisorDecision(
            action="observe",
            reason=(
                "all PP&D execution-capability tasks are complete; wait for a human-authored or agentic "
                "source-backed tranche instead of appending more generated platform placeholders"
            ),
            severity="info",
        )

    if tasks and all(task.status == "complete" for task in tasks):
        return SupervisorDecision(
            action="plan_next_tasks",
            reason="all PP&D daemon tasks are complete; review the original PP&D goal and add the next task-board tranche",
            severity="info",
            should_invoke_codex=True,
        )

    if latest.get("failure_kind") == "no_eligible_tasks" and tasks and all(task.status == "complete" for task in tasks):
        return SupervisorDecision(
            action="plan_next_tasks",
            reason="daemon has no eligible tasks; review completed work against the PP&D plan and add the next backlog tranche",
            severity="info",
            should_invoke_codex=True,
        )

    if (
        latest.get("failure_kind") == "no_eligible_tasks"
        and tasks
        and not has_selectable_work
        and any(task.status == "blocked" for task in tasks)
        and termination_storm_count < config.termination_storm_threshold
        and generated_blocked_total < MAX_GENERATED_BLOCKED_CASCADE_TASKS
    ):
        return SupervisorDecision(
            action="plan_next_tasks",
            reason=(
                "daemon has no eligible unblocked tasks; review blocked work against the PP&D goal "
                "and append a fresh goal-aligned tranche instead of retrying parked tasks"
            ),
            severity="warning",
            should_invoke_codex=True,
        )

    if (
        "## Checkbox-108 Supersession Note" not in board
        and has_recent_checkbox_133_no_file_stall(rows, latest)
        and has_checkbox_108_supersession_prerequisites(rows)
    ):
        return SupervisorDecision(
            action="reconcile_supersession_task_board",
            reason=(
                "checkbox-133 returned repeated no-file task-board proposals even though accepted "
                "checkbox-109/130/131/132 evidence is sufficient; apply deterministic task-board-only supersession repair"
            ),
            severity="warning",
            should_restart_daemon=True,
        )

    if is_private_session_preflight_false_positive(latest):
        return SupervisorDecision(
            action="repair_daemon_programming",
            reason=(
                "daemon private/session write-path preflight rejected an allowed non-private path; "
                "patch the path classifier before retrying the worker"
            ),
            severity="warning",
            should_invoke_codex=True,
            should_restart_daemon=True,
        )

    if daemon_has_fresh_active_work(
        running=running,
        heartbeat_age=heartbeat_age,
        active_state=active_state,
        active_state_age=active_state_age,
        config=config,
    ):
        return SupervisorDecision(
            action="observe",
            reason=(
                f"daemon is actively working in {active_state}; defer historical repair decisions "
                "until the worker exits, stalls, or records a fresh result"
            ),
            severity="info",
        )

    if has_deterministic_work and not running:
        if active_breaker:
            reason = (
                "deterministic fixture-only PP&D fallback work is available while the termination-storm "
                "circuit breaker is active; restart daemon on the no-LLM progress path"
            )
        elif termination_storm_count >= config.termination_storm_threshold:
            reason = (
                "deterministic fixture-only PP&D fallback work is available despite historical llm_router "
                "termination diagnostics; restart daemon on the no-LLM progress path before opening another breaker"
            )
        elif generated_blocked_total >= MAX_GENERATED_BLOCKED_CASCADE_TASKS:
            reason = (
                "deterministic fixture-only PP&D fallback work is available despite exhausted generated-repair "
                "budget; restart daemon on the no-LLM progress path instead of growing repair tasks"
            )
        else:
            reason = (
                "deterministic fixture-only PP&D fallback work is available; restart daemon so safe "
                "processor, Playwright-draft, PDF-preview, and formal-logic planning can continue without LLM"
            )
        return SupervisorDecision(
            action="restart_daemon",
            reason=reason,
            severity="warning",
            should_restart_daemon=True,
        )

    if (
        active_breaker
        and generated_blocked_open == 0
        and active_state == "paused_by_supervisor_circuit_breaker"
    ):
        return SupervisorDecision(
            action="observe_circuit_breaker",
            reason=(
                "termination storm circuit breaker is active; "
                f"daemon remains paused for about {int(breaker_remaining or 0)} more seconds"
            ),
            severity="critical",
            should_restart_daemon=False,
        )

    if has_recovery_work and not running:
        return SupervisorDecision(
            action="restart_daemon",
            reason="vetted circuit-breaker recovery tasks are available; restart daemon on non-generated recovery work",
            severity="warning",
            should_restart_daemon=True,
        )

    if (
        not has_recovery_work
        and generated_blocked_open == 0
        and active_state == "paused_by_supervisor_circuit_breaker"
        and (termination_storm_count >= config.termination_storm_threshold or generated_blocked_total >= MAX_GENERATED_BLOCKED_CASCADE_TASKS)
    ):
        return SupervisorDecision(
            action="recover_termination_storm_and_restart",
            reason=(
                "termination storm circuit breaker has quarantined generated work; append vetted non-generated "
                "recovery tasks and restart the daemon instead of refreshing the breaker"
            ),
            severity="critical",
            should_restart_daemon=True,
        )

    if termination_storm_count >= config.termination_storm_threshold:
        return SupervisorDecision(
            action="enter_termination_storm_circuit_breaker",
            reason=(
                f"{termination_storm_count} recent llm_router termination diagnostics across "
                f"{termination_storm_targets} target(s) indicate a systemic termination storm; "
                "pause worker restarts and task-board growth until daemon/supervisor resource policy is hardened"
            ),
            severity="critical",
            should_restart_daemon=False,
        )

    if generated_blocked_total >= MAX_GENERATED_BLOCKED_CASCADE_TASKS and (
        generated_blocked_open > 0 or not has_source_backed_continuation_context
    ):
        return SupervisorDecision(
            action="enter_termination_storm_circuit_breaker",
            reason=(
                f"{generated_blocked_total} generated blocked-cascade daemon-repair tasks exhausted the "
                "fallback budget; pause worker restarts and task-board growth until the generated repair "
                "pile is quarantined or a vetted task is reopened"
            ),
            severity="critical",
            should_restart_daemon=False,
        )

    if has_blocked_recovery_cascade(tasks):
        return SupervisorDecision(
            action="reconcile_blocked_cascade_and_restart",
            reason=(
                "all selectable PP&D tasks are blocked after repeated daemon recovery attempts; "
                "append deterministic daemon-repair tasks before retrying blocked domain work"
            ),
            severity="warning",
            should_restart_daemon=True,
        )

    parse_or_llm_diagnostic_failures = recent_parse_or_llm_diagnostic_failure_count(
        current_rows,
        completed_task_labels=inactive_task_labels,
    )
    if parse_or_llm_diagnostic_failures >= config.repeated_failure_threshold:
        return SupervisorDecision(
            action="reconcile_repeated_llm_loop_and_restart",
            reason=(
                f"{parse_or_llm_diagnostic_failures} recent durable LLM parse/runtime diagnostics were recorded "
                "for the same task before the daemon exited; park the looping task and restart on the next "
                "independent task without invoking the LLM repair path"
            ),
            severity="warning",
            should_restart_daemon=True,
        )

    if not running:
        active_target = str(status.get("active_target_task") or status.get("target_task") or "")
        if active_state in {"calling_llm", "applying_files"} and active_target:
            active_task = task_matching_target(tasks, active_target)
            selectable = [task for task in tasks if task.status in {"needed", "in-progress"}]
            if active_task and active_task.status == "blocked" and selectable:
                return SupervisorDecision(
                    action="restart_daemon",
                    reason=(
                        f"daemon process is not running and stale active target {active_target} is already parked; "
                        f"restart on next selectable task {selectable[0].label}"
                    ),
                    severity="warning",
                    should_restart_daemon=True,
                )
            recent_active_failures = recent_failure_count_for_target(
                rows,
                active_target,
                kinds={"parse", "llm", "syntax_preflight", "validation", "preflight"},
            )
            if recent_active_failures >= 1:
                return SupervisorDecision(
                    action="reconcile_dead_worker_with_recent_failures_and_restart",
                    reason=(
                        f"daemon process is not running but status is still {active_state} on {active_target}, "
                        f"and {recent_active_failures} recent failure diagnostic(s) already exist for that target; "
                        "park the task before restart instead of resetting it into another immediate retry"
                    ),
                    severity="warning",
                    should_restart_daemon=True,
                )
            return SupervisorDecision(
                action="reconcile_dead_worker_and_restart",
                reason=(
                    f"daemon process is not running but status is still {active_state} on {active_target}; "
                    "reset the in-progress task before restart"
                ),
                severity="warning",
                should_restart_daemon=True,
            )
        return SupervisorDecision(
            action="restart_daemon",
            reason="daemon process is not running",
            severity="warning",
            should_restart_daemon=True,
        )

    if heartbeat_age is None:
        return SupervisorDecision(
            action="invoke_codex",
            reason="daemon status timestamp is missing or invalid",
            severity="warning",
            should_invoke_codex=True,
        )
    if heartbeat_age > config.stall_seconds:
        return SupervisorDecision(
            action="invoke_codex",
            reason=f"daemon heartbeat is stale for {int(heartbeat_age)} seconds in state {active_state or ''}",
            severity="critical",
            should_invoke_codex=True,
            should_restart_daemon=True,
        )
    if active_state in {"calling_llm", "applying_files"} and active_state_age is not None:
        if active_state_age > config.active_state_timeout_seconds:
            target = status.get("active_target_task") or status.get("target_task") or ""
            return SupervisorDecision(
                action="reconcile_stalled_worker_and_restart",
                reason=(
                    f"daemon has been in {active_state} for {int(active_state_age)} seconds "
                    f"on {target}; reset the in-progress task and restart the worker with a fresh timeout window"
                ),
                severity="warning",
                should_restart_daemon=True,
            )

    malformed_count = repeated_malformed_syntax_count(current_rows, completed_task_labels=inactive_task_labels)
    if malformed_count >= 2:
        return SupervisorDecision(
            action="repair_daemon_programming",
            reason=(
                f"{malformed_count} recent validation rollbacks for the same target contained malformed Python "
                "comparison or annotation-like syntax; stop retrying that target until a syntax-first guard passes"
            ),
            severity="warning",
            should_invoke_codex=True,
            should_restart_daemon=True,
        )

    forbidden_marker_count = recent_forbidden_absence_marker_failure_count(
        current_rows,
        completed_task_labels=inactive_task_labels,
    )
    if forbidden_marker_count >= 1:
        return SupervisorDecision(
            action="repair_daemon_programming",
            reason=(
                f"{forbidden_marker_count} recent validation rollback(s) self-triggered forbidden artifact marker checks; "
                "patch daemon failure guidance so absence fields avoid banned words like cookie, screenshot, auth-state, "
                "storage-state, trace.zip, and .har"
            ),
            severity="warning",
            should_invoke_codex=True,
            should_restart_daemon=True,
        )

    blocked = [task for task in tasks if task.status == "blocked"]
    selectable = [task for task in tasks if task.status in {"needed", "in-progress"}]
    if should_blocked_tasks_interrupt(len(blocked), len(selectable), config.blocked_task_threshold):
        return SupervisorDecision(
            action="invoke_codex",
            reason=f"{len(blocked)} task(s) are blocked and no independent selectable task remains: "
            + "; ".join(task.label for task in blocked[:3]),
            severity="warning",
            should_invoke_codex=True,
        )

    syntax_failures = recent_syntax_failure_count(current_rows, completed_task_labels=inactive_task_labels)
    if syntax_failures >= 2:
        return SupervisorDecision(
            action="repair_daemon_programming",
            reason=(
                f"{syntax_failures} recent validation rollbacks were syntax or compile failures; "
                "patch daemon prompt, preflight, or repair guidance before more worker attempts"
            ),
            severity="warning",
            should_invoke_codex=True,
            should_restart_daemon=True,
        )

    repeated_failures = latest_repeated_failure_count(current_rows, completed_task_labels=inactive_task_labels)
    if repeated_failures >= config.repeated_failure_threshold:
        return SupervisorDecision(
            action="invoke_codex",
            reason=f"{repeated_failures} consecutive daemon rounds failed without an accepted patch",
            severity="warning",
            should_invoke_codex=True,
        )

    if active_state == "sleeping" and latest and not latest.get("applied") and not latest.get("validation_passed"):
        return SupervisorDecision(
            action="invoke_codex",
            reason="daemon is sleeping after a non-accepted latest proposal",
            severity="info",
            should_invoke_codex=True,
        )

    return SupervisorDecision(action="observe", reason="daemon appears healthy", severity="info")


def build_supervisor_prompt(config: SupervisorConfig, decision: SupervisorDecision) -> str:
    compact_repair_prompt = should_compact_supervisor_repair_prompt(decision)
    board_text = read_text(config.resolve(config.task_board), limit=8000) if config.resolve(config.task_board).exists() else ""
    if compact_repair_prompt:
        files = {
            "ppd/daemon/task-board-summary.json": task_board_summary(board_text),
            "ppd/daemon/ppd_daemon.py excerpt": read_text(config.resolve(Path("ppd/daemon/ppd_daemon.py")), limit=3500),
            "ppd/daemon/ppd_supervisor.py excerpt": read_text(config.resolve(Path("ppd/daemon/ppd_supervisor.py")), limit=3500),
        }
        plan = read_text(config.resolve(config.plan_doc), limit=1200) if config.resolve(config.plan_doc).exists() else ""
    else:
        files = {
            "ppd/daemon/control.sh": read_text(config.resolve(Path("ppd/daemon/control.sh")), limit=8000),
            "ppd/daemon/ppd_daemon.py": read_text(config.resolve(Path("ppd/daemon/ppd_daemon.py")), limit=22000),
            "ppd/daemon/ppd_supervisor.py": read_text(config.resolve(Path("ppd/daemon/ppd_supervisor.py")), limit=16000),
            "ppd/daemon/task-board.md": board_text,
            "ppd/daemon/OPERATIONS.md": read_text(config.resolve(Path("ppd/daemon/OPERATIONS.md")), limit=8000)
            if config.resolve(Path("ppd/daemon/OPERATIONS.md")).exists()
            else "",
        }
        plan = read_text(config.resolve(config.plan_doc), limit=18000) if config.resolve(config.plan_doc).exists() else ""
    status = load_json(config.resolve(config.status_file))
    progress = load_json(config.resolve(config.progress_file))
    recent_results = read_supervisor_result_rows(config.resolve(config.result_log))[-5 if compact_repair_prompt else -8:]
    failed_manifests: list[str] = []
    failed_dir = config.resolve(Path("ppd/daemon/failed-patches"))
    if failed_dir.exists() and not compact_repair_prompt:
        for path in sorted(failed_dir.glob("*.json"))[-5:]:
            failed_manifests.append(f"--- {path.relative_to(config.repo_root).as_posix()} ---\n{read_text(path, limit=2500)}")

    if decision.action == "plan_next_tasks":
        goal = "Review completed work against the original PP&D goal and update `ppd/daemon/task-board.md` with the next narrow, ordered tranche of unfinished tasks. Do not implement those tasks in this proposal; create the backlog so the worker daemon can continue."
    elif decision.action == "repair_daemon_programming":
        goal = "Patch the PP&D daemon or supervisor programming so repeated validation failures are detected earlier and the worker is prompted toward smaller, syntactically valid, policy-compliant proposals."
    else:
        goal = "Improve the PP&D daemon or supervisor programming so the worker can resume meaningful autonomous progress."

    prompt = f"""
You are Codex acting as a supervisor repair agent for the isolated PP&D daemon.

Supervisor diagnosis:
- action: {decision.action}
- severity: {decision.severity}
- reason: {decision.reason}
- prompt mode: {"compact repair prompt" if compact_repair_prompt else "full repair prompt"}

Goal:
{goal}

Hard constraints:
- Return ONLY one JSON object; no markdown fences and no prose outside JSON.
- Use complete file replacements in a `files` array. Do not return shell commands.
- For `plan_next_tasks`, edit only `ppd/daemon/task-board.md` and optionally `ppd/daemon/SUPERVISOR_REPAIR_GUIDE.md`.
- For repair actions, edit only `ppd/daemon/`, `ppd/tests/`, `ppd/.gitignore`, or PP&D daemon operations docs.
- Do not edit application/domain artifacts just to mark progress. Fix supervision, validation, task selection, retry, recovery, or diagnostics.
- For `repair_daemon_programming`, focus on daemon prompt/preflight/retry logic and supervisor diagnostics; do not implement the selected PP&D domain task.
- When recent failures include Python `SyntaxError`, `py_compile`, or TypeScript `TS1005`/`TS1109`/`TS1128`, prefer smaller file sets and explicit syntactic-validity guardrails over broader contract rewrites.
- When planning next tasks, preserve completed tasks, append new `[ ]` tasks, keep each task narrow enough for one daemon cycle, and include fixture-first/validation-first work before live or authenticated automation.
- Do not create private DevHub session files, auth state, traces, raw crawl output, or downloaded documents.
- Do not automate CAPTCHA, MFA, account creation, payment, submission, certification, cancellation, official upload, or inspection scheduling.
- Keep the change narrow and deterministic.

JSON schema:
{{
  "summary": "short summary",
  "impact": "why this improves autonomous supervisor/daemon progress",
  "files": [
    {{"path": "ppd/daemon/...", "content": "complete replacement file content"}}
  ],
  "validation_commands": [["python3", "ppd/tests/validate_ppd.py"]]
}}

Runtime status:
{json.dumps(status, indent=2, sort_keys=True)}

Original PP&D plan:
{plan}

Progress:
{json.dumps(progress, indent=2, sort_keys=True)}

Recent daemon results:
{json.dumps(recent_results, indent=2, sort_keys=True)}

Recent failed manifests:
{chr(10).join(failed_manifests)}

Current source files:
{chr(10).join(f"--- {name} ---\\n{content}" for name, content in files.items())}
"""
    prompt_limit = min(config.max_prompt_chars, config.max_repair_prompt_chars) if compact_repair_prompt else config.max_prompt_chars
    if len(prompt) > prompt_limit:
        prompt = prompt[:prompt_limit] + "\n\n[truncated]\n"
    return prompt


def call_codex(prompt: str, config: SupervisorConfig) -> str:
    backend = os.environ.get("PPD_LLM_BACKEND", "llm_router")
    if backend != "llm_router":
        raise RuntimeError(f"Unsupported PP&D LLM backend {backend!r}; expected 'llm_router'.")
    try:
        from ipfs_datasets_py import llm_router
    except Exception as exc:  # pragma: no cover - environment-dependent
        raise RuntimeError(f"Could not import ipfs_datasets_py.llm_router: {exc}") from exc
    return llm_router.generate_text(
        prompt,
        model_name=config.model_name,
        provider=config.provider,
        allow_local_fallback=False,
        timeout=config.llm_timeout_seconds,
        max_new_tokens=4096,
        temperature=0.1,
    )


def run_control(config: SupervisorConfig, command: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(config.resolve(config.control_script)), command],
        cwd=config.repo_root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def stop_daemon_if_running(config: SupervisorConfig) -> Optional[subprocess.CompletedProcess[str]]:
    """Stop the daemon only when a live watchdog PID is recorded."""

    if process_running(read_pid(config.resolve(config.pid_file))):
        return run_control(config, "stop")
    return None


def daemon_worker_processes(config: SupervisorConfig) -> list[str]:
    result = subprocess.run(
        ["ps", "-eo", "pid=,ppid=,sid=,etime=,cmd="],
        cwd=config.repo_root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        return []
    lines: list[str] = []
    for line in result.stdout.splitlines():
        if "python3 ppd/daemon/ppd_daemon.py --apply --watch" in line:
            lines.append(line.strip())
    return lines


def start_daemon_unless_running(config: SupervisorConfig) -> subprocess.CompletedProcess[str]:
    """Start the daemon without interrupting a live worker/LLM attempt."""

    live_workers = daemon_worker_processes(config)
    if live_workers:
        return subprocess.CompletedProcess(
            args=["bash", str(config.control_script), "start"],
            returncode=0,
            stdout="PP&D daemon already running; start suppressed to avoid interrupting live reassessment work. "
            + " ".join(live_workers[:2]),
            stderr="",
        )
    return run_control(config, "start")


def control_command_result(
    config: SupervisorConfig,
    command: str,
    result: subprocess.CompletedProcess[str],
) -> CommandResult:
    return CommandResult(
        command=("bash", str(config.control_script), command),
        returncode=int(result.returncode),
        stdout=result.stdout or "",
        stderr=result.stderr or "",
    )


def attach_daemon_start_result(
    proposal: Proposal,
    config: SupervisorConfig,
    result: subprocess.CompletedProcess[str],
) -> Proposal:
    """Persist daemon start outcome so restart failures are visible in supervisor status."""

    command_result = control_command_result(config, "start", result)
    proposal.validation_results.append(command_result)
    restart_summary = compact_message((result.stdout or "") + " " + (result.stderr or ""), limit=900).strip()
    if result.returncode == 0:
        if restart_summary and "daemon restart result" not in proposal.impact.lower():
            proposal.impact = (proposal.impact.rstrip() + f" Daemon restart result: {restart_summary}").strip()
        return proposal
    proposal.failure_kind = proposal.failure_kind or "restart"
    proposal.errors.append(f"daemon restart failed: {restart_summary or result.returncode}")
    return proposal


def supervisor_daemon_config(config: SupervisorConfig) -> DaemonConfig:
    return DaemonConfig(
        repo_root=config.repo_root,
        apply=True,
        llm_timeout_seconds=config.llm_timeout_seconds,
        model_name=config.model_name,
        provider=config.provider,
        repair_validation_failures=False,
    )


def should_apply_builtin_repair(decision: SupervisorDecision, proposal: Proposal) -> bool:
    """Return True when agentic repair failed and deterministic fallback is useful."""

    if proposal.valid:
        return False
    return decision.action in {
        "invoke_codex",
        "repair_daemon_programming",
        "plan_next_tasks",
        "reconcile_supersession_task_board",
    }


def build_builtin_repair_status_payload(
    decision: SupervisorDecision,
    failed_proposal: Proposal,
) -> dict[str, Any]:
    """Build a small runtime-safe repair record for failed self-heal attempts."""

    return {
        "schemaVersion": 1,
        "createdAt": utc_now(),
        "repairKind": "builtin_supervisor_fallback",
        "llmBackend": os.environ.get("PPD_LLM_BACKEND", "llm_router"),
        "decision": {
            "action": decision.action,
            "reason": decision.reason,
            "severity": decision.severity,
        },
        "failedAgenticRepair": {
            "summary": failed_proposal.summary,
            "failureKind": failed_proposal.failure_kind or "not_applied",
            "errors": [compact_message(error) for error in failed_proposal.errors],
            "changedFiles": list(failed_proposal.changed_files),
            "validationResults": [result.compact(limit=900) for result in failed_proposal.validation_results],
        },
        "fallbackActions": [
            "preserve failed repair diagnostics without accepting the invalid patch",
            "run full PP&D daemon validation before restarting unattended worker attempts",
            "restart the worker with PPD_LLM_BACKEND=llm_router after fallback validation passes",
            "keep future retry scope narrow and fixture-first",
        ],
        "safetyBoundaries": [
            "no private DevHub session artifacts",
            "no raw crawl output",
            "no downloaded documents",
            "no browser traces or screenshots",
            "no consequential DevHub actions",
        ],
    }


def invoke_builtin_repair(
    config: SupervisorConfig,
    decision: SupervisorDecision,
    failed_proposal: Proposal,
) -> Proposal:
    """Apply deterministic supervisor fallback when Codex self-heal fails."""

    rows = read_supervisor_result_rows(config.resolve(config.result_log))
    board_path = config.resolve(config.task_board)
    board = read_text(board_path) if board_path.exists() else ""
    repaired_board, parked_titles = builtin_repair_task_board(board, rows)
    repaired_board, superseded_labels = builtin_supersession_repair_task_board(repaired_board, rows)
    replenished_labels: tuple[str, ...] = ()
    if decision.action == "plan_next_tasks":
        repaired_board, replenished_labels = builtin_replenish_goal_tasks(repaired_board, rows)
    payload = build_builtin_repair_status_payload(decision, failed_proposal)
    payload["taskBoardRepair"] = {
        "parkedRepeatedSyntaxLoopTasks": list(parked_titles),
        "supersededTaskBoardOnlyLabels": list(superseded_labels),
        "replenishedGoalTaskLabels": list(replenished_labels),
        "taskBoardUpdated": repaired_board != board,
    }
    files = [
        {
            "path": "ppd/daemon/builtin-repair-status.json",
            "content": json.dumps(payload, indent=2, sort_keys=True) + "\n",
        }
    ]
    if (
        decision.action == "plan_next_tasks"
        and "generated blocked-cascade repair budget is exhausted" in decision.reason
    ):
        breaker_payload = {
            "schemaVersion": 1,
            "createdAt": utc_now(),
            "repairKind": "termination_storm_recovered",
            "decision": {
                "action": decision.action,
                "reason": decision.reason,
                "severity": decision.severity,
            },
            "recoveryTaskLabels": list(replenished_labels),
            "operatorAction": (
                "The supervisor found generated blocked-cascade work already parked and converted the "
                "old circuit-breaker state into source-backed deterministic continuation tasks."
            ),
        }
        files.append(
            {
                "path": "ppd/daemon/supervisor-circuit-breaker.json",
                "content": json.dumps(breaker_payload, indent=2, sort_keys=True) + "\n",
            }
        )
    if repaired_board != board:
        files.append({"path": "ppd/daemon/task-board.md", "content": repaired_board})
    proposal = Proposal(
        summary="Apply built-in supervisor fallback after failed agentic repair.",
        impact=(
            "The supervisor now records the failed self-heal diagnostics, validates the daemon "
            "without accepting the invalid patch, parks repeated syntax-loop tasks when needed, "
            "and can restart the worker on the explicit llm_router path instead of waiting for manual intervention."
        ),
        files=files,
    )
    proposal.target_task = f"Built-in supervisor fallback: {decision.reason}"
    proposal.dry_run = not config.apply
    if config.apply:
        return apply_files_with_validation(proposal, supervisor_daemon_config(config))
    proposal.validation_results = run_validation(supervisor_daemon_config(config))
    return proposal


def build_dead_worker_ready_status(
    created_at: str,
    previous_status: dict[str, Any],
    decision: SupervisorDecision,
    reset_labels: Iterable[str],
) -> dict[str, Any]:
    return build_ready_after_supervisor_repair_status(
        created_at=created_at,
        previous_status=previous_status,
        repair_state="ready_after_supervisor_dead_worker_repair",
        supervisor_action=decision.action,
        supervisor_reason=decision.reason,
        reset_task_labels=reset_labels,
    )


def invoke_dead_worker_repair(config: SupervisorConfig, decision: SupervisorDecision) -> Proposal:
    board_path = config.resolve(config.task_board)
    board = read_text(board_path) if board_path.exists() else ""
    status = load_json(config.resolve(config.status_file))
    repaired_board, reset_labels = builtin_dead_worker_task_board(
        board,
        str(status.get("active_target_task") or status.get("target_task") or ""),
    )
    created_at = utc_now()
    payload = {
        "schemaVersion": 1,
        "createdAt": created_at,
        "repairKind": "dead_worker_task_reset",
        "decision": {
            "action": decision.action,
            "reason": decision.reason,
            "severity": decision.severity,
        },
        "resetInProgressTaskLabels": list(reset_labels),
        "statusBeforeRepair": status,
    }
    files = [
        {
            "path": "ppd/daemon/builtin-repair-status.json",
            "content": json.dumps(payload, indent=2, sort_keys=True) + "\n",
        },
        {
            "path": "ppd/daemon/status.json",
            "content": json.dumps(
                build_dead_worker_ready_status(created_at, status, decision, reset_labels),
                indent=2,
                sort_keys=True,
            )
            + "\n",
        },
    ]
    if repaired_board != board:
        files.append({"path": "ppd/daemon/task-board.md", "content": repaired_board})
    proposal = Proposal(
        summary="Reset dead-worker in-progress task before restart.",
        impact=(
            "The supervisor reconciles stale calling_llm/applying_files status with the dead worker process, "
            "returns the task to pending, clears stale runtime status, and restarts the daemon without waiting for manual cleanup."
        ),
        files=files,
    )
    proposal.target_task = f"Built-in supervisor fallback: {decision.reason}"
    proposal.dry_run = not config.apply
    if config.apply:
        return apply_files_with_validation(proposal, supervisor_daemon_config(config))
    proposal.validation_results = run_validation(supervisor_daemon_config(config))
    return proposal


def invoke_stalled_worker_repair(config: SupervisorConfig, decision: SupervisorDecision) -> Proposal:
    board_path = config.resolve(config.task_board)
    board = read_text(board_path) if board_path.exists() else ""
    status = load_json(config.resolve(config.status_file))
    repaired_board, parked_labels, replenished_labels = builtin_autonomous_execution_goal_repair_task_board(
        board,
        str(status.get("active_target_task") or status.get("target_task") or ""),
    )
    payload = {
        "schemaVersion": 1,
        "createdAt": utc_now(),
        "repairKind": "stalled_worker_task_parked",
        "decision": {
            "action": decision.action,
            "reason": decision.reason,
            "severity": decision.severity,
        },
        "parkedStalledTaskLabels": list(parked_labels),
        "replenishedExecutionTaskLabels": list(replenished_labels),
        "statusBeforeRepair": status,
    }
    files = [
        {
            "path": "ppd/daemon/builtin-repair-status.json",
            "content": json.dumps(payload, indent=2, sort_keys=True) + "\n",
        }
    ]
    if repaired_board != board:
        files.append({"path": "ppd/daemon/task-board.md", "content": repaired_board})
    proposal = Proposal(
        summary="Park stalled worker task before restart.",
        impact=(
            "The supervisor handles an active-state timeout deterministically by parking the stalled task, "
            "recording the repair, appending execution-capability work when old platform slices are stale, "
            "validating, and restarting on the next independent task."
        ),
        files=files,
    )
    proposal.target_task = f"Built-in supervisor fallback: {decision.reason}"
    proposal.dry_run = not config.apply
    if config.apply:
        return apply_files_with_validation(proposal, supervisor_daemon_config(config))
    proposal.validation_results = run_validation(supervisor_daemon_config(config))
    return proposal


def invoke_blocked_cascade_repair(config: SupervisorConfig, decision: SupervisorDecision) -> Proposal:
    board_path = config.resolve(config.task_board)
    board = read_text(board_path) if board_path.exists() else ""
    repaired_board, labels = builtin_blocked_cascade_replenish_task_board(board)
    payload = {
        "schemaVersion": 1,
        "createdAt": utc_now(),
        "repairKind": "blocked_cascade_replenishment",
        "decision": {
            "action": decision.action,
            "reason": decision.reason,
            "severity": decision.severity,
        },
        "replenishedTaskLabels": list(labels),
    }
    files = [
        {
            "path": "ppd/daemon/builtin-repair-status.json",
            "content": json.dumps(payload, indent=2, sort_keys=True) + "\n",
        }
    ]
    if repaired_board != board:
        files.append({"path": "ppd/daemon/task-board.md", "content": repaired_board})
    proposal = Proposal(
        summary="Append deterministic blocked-cascade daemon repair tasks.",
        impact=(
            "The supervisor can recover when every selectable task is blocked by appending narrow daemon-repair work, "
            "validating it, and restarting without invoking the LLM repair path."
        ),
        files=files,
    )
    proposal.target_task = f"Built-in supervisor fallback: {decision.reason}"
    proposal.dry_run = not config.apply
    if config.apply:
        return apply_files_with_validation(proposal, supervisor_daemon_config(config))
    proposal.validation_results = run_validation(supervisor_daemon_config(config))
    return proposal


def invoke_termination_storm_circuit_breaker(config: SupervisorConfig, decision: SupervisorDecision) -> Proposal:
    created_at = utc_now()
    board_path = config.resolve(config.task_board)
    status_path = config.resolve(config.status_file)
    board = read_text(board_path) if board_path.exists() else ""
    repaired_board, quarantined_labels = quarantine_generated_blocked_cascade_tasks(board)
    previous_status = load_json(status_path)
    paused_status = {
        "schemaVersion": 1,
        "updated_at": created_at,
        "state": "paused_by_supervisor_circuit_breaker",
        "active_state": "paused_by_supervisor_circuit_breaker",
        "active_state_started_at": created_at,
        "active_target_task": previous_status.get("active_target_task") or previous_status.get("target_task") or "",
        "supervisor_action": decision.action,
        "supervisor_reason": decision.reason,
        "previous_state": previous_status.get("active_state") or previous_status.get("state") or "",
    }
    payload = {
        "schemaVersion": 1,
        "createdAt": created_at,
        "repairKind": "termination_storm_circuit_breaker",
        "decision": {
            "action": decision.action,
            "reason": decision.reason,
            "severity": decision.severity,
        },
        "quarantinedGeneratedTaskLabels": list(quarantined_labels),
        "operatorAction": (
            "The supervisor paused daemon restarts because repeated llm_router terminations "
            "were systemic. Harden resource limits or deterministic task handling before resuming."
        ),
    }
    if config.apply:
        if repaired_board != board:
            atomic_write_text(board_path, repaired_board)
        atomic_write_json(status_path, paused_status)
        atomic_write_json(config.resolve(config.circuit_breaker_file), payload)
    changed_files = ["ppd/daemon/status.json", "ppd/daemon/supervisor-circuit-breaker.json"]
    if repaired_board != board:
        changed_files.insert(0, "ppd/daemon/task-board.md")
    proposal = Proposal(
        summary="Pause daemon restarts after systemic llm_router termination storm.",
        impact=(
            "The supervisor wrote a circuit-breaker diagnostic and avoided appending more tasks, "
            "running full validation, or restarting the worker into another termination loop. "
            f"Quarantined {len(quarantined_labels)} open generated blocked-cascade task(s)."
        ),
        failure_kind="termination_storm",
        changed_files=changed_files if config.apply else [],
        applied=config.apply,
        dry_run=not config.apply,
    )
    proposal.target_task = f"Supervisor circuit breaker: {decision.reason}"
    return proposal


def invoke_termination_storm_recovery(config: SupervisorConfig, decision: SupervisorDecision) -> Proposal:
    created_at = utc_now()
    board_path = config.resolve(config.task_board)
    status_path = config.resolve(config.status_file)
    board = read_text(board_path) if board_path.exists() else ""
    repaired_board, labels = append_circuit_breaker_recovery_tasks(board)
    payload = {
        "schemaVersion": 1,
        "createdAt": created_at,
        "repairKind": "termination_storm_recovery_tranche",
        "decision": {
            "action": decision.action,
            "reason": decision.reason,
            "severity": decision.severity,
        },
        "recoveryTaskLabels": list(labels),
        "recoveryPolicy": "append_vetted_non_generated_recovery_tasks_after_quarantine",
    }
    breaker_payload = {
        "schemaVersion": 1,
        "createdAt": created_at,
        "repairKind": "termination_storm_recovered",
        "decision": {
            "action": decision.action,
            "reason": decision.reason,
            "severity": decision.severity,
        },
        "recoveryTaskLabels": list(labels),
        "operatorAction": (
            "The supervisor converted the termination-storm pause into vetted non-generated recovery work. "
            "The daemon may resume on those tasks, while generated blocked-cascade tasks remain blocked."
        ),
    }
    ready_status = {
        "schemaVersion": 1,
        "updated_at": created_at,
        "state": "ready_after_supervisor_circuit_breaker_recovery",
        "active_state": "ready_after_supervisor_circuit_breaker_recovery",
        "active_state_started_at": created_at,
        "active_target_task": "",
        "supervisor_action": decision.action,
        "supervisor_reason": decision.reason,
        "recovery_task_labels": list(labels),
    }
    files = [
        {
            "path": "ppd/daemon/builtin-repair-status.json",
            "content": json.dumps(payload, indent=2, sort_keys=True) + "\n",
        },
        {
            "path": "ppd/daemon/supervisor-circuit-breaker.json",
            "content": json.dumps(breaker_payload, indent=2, sort_keys=True) + "\n",
        },
        {
            "path": "ppd/daemon/status.json",
            "content": json.dumps(ready_status, indent=2, sort_keys=True) + "\n",
        },
    ]
    if repaired_board != board:
        files.append({"path": "ppd/daemon/task-board.md", "content": repaired_board})
    proposal = Proposal(
        summary="Append vetted recovery work after termination-storm circuit breaker.",
        impact=(
            "The supervisor can move from a paused circuit-breaker state back to useful daemon work by "
            "appending non-generated recovery tasks, marking the breaker recovered, and restarting on that "
            "safe recovery tranche."
        ),
        files=files,
    )
    proposal.target_task = f"Built-in supervisor fallback: {decision.reason}"
    proposal.dry_run = not config.apply
    if config.apply:
        return apply_files_with_validation(proposal, supervisor_daemon_config(config))
    proposal.validation_results = run_validation(supervisor_daemon_config(config))
    return proposal


def invoke_codex_repair(config: SupervisorConfig, decision: SupervisorDecision) -> Proposal:
    if config.apply:
        stop_daemon_if_running(config)
    try:
        raw = call_codex(build_supervisor_prompt(config, decision), config)
        proposal = parse_proposal(raw)
    except Exception as exc:
        proposal = Proposal(
            summary="Supervisor Codex repair failed.",
            errors=[compact_message(exc)],
            failure_kind="llm",
        )
    proposal.target_task = f"Supervisor repair: {decision.reason}"
    proposal.dry_run = not config.apply

    if config.apply and proposal.files:
        if decision.action == "plan_next_tasks":
            for item in proposal.files:
                if item.get("path") == "ppd/daemon/task-board.md":
                    sanitized, changed = sanitize_agentic_replenishment_board(item.get("content", ""))
                    if changed:
                        item["content"] = sanitized
        proposal = apply_files_with_validation(proposal, supervisor_daemon_config(config))
    else:
        proposal.validation_results = run_validation(supervisor_daemon_config(config))

    if should_apply_builtin_repair(decision, proposal):
        proposal = invoke_builtin_repair(config, decision, proposal)

    if config.apply and config.restart_daemon:
        attach_daemon_start_result(proposal, config, start_daemon_unless_running(config))
    return proposal


def write_supervisor_status(config: SupervisorConfig, decision: SupervisorDecision, proposal: Optional[Proposal]) -> None:
    payload = {
        "updated_at": utc_now(),
        "pid": os.getpid(),
        "decision": {
            "action": decision.action,
            "reason": decision.reason,
            "severity": decision.severity,
            "should_invoke_codex": decision.should_invoke_codex,
            "should_restart_daemon": decision.should_restart_daemon,
        },
        "proposal": proposal.to_dict() if proposal else None,
    }
    atomic_write_json(config.resolve(config.supervisor_status_file), payload)
    append_jsonl(config.resolve(config.supervisor_log), payload)


def record_supervisor_exception(config: SupervisorConfig, exc: BaseException) -> SupervisorDecision:
    diagnostic = exception_diagnostic(exc)
    decision = SupervisorDecision(
        action="supervisor_exception",
        reason=f"supervisor cycle raised an exception: {diagnostic}",
        severity="critical",
        should_invoke_codex=True,
        should_restart_daemon=False,
    )
    proposal = Proposal(
        summary="Supervisor cycle crashed before completion.",
        impact="The supervisor caught the exception, wrote diagnostics, and can continue in watch mode.",
        errors=[diagnostic],
        failure_kind="supervisor_exception",
    )
    proposal.dry_run = not config.apply
    try:
        write_supervisor_status(config, decision, proposal)
    except Exception as status_exc:
        fallback = {
            "updated_at": utc_now(),
            "pid": os.getpid(),
            "decision": {
                "action": decision.action,
                "reason": compact_message(decision.reason, limit=1200),
                "severity": decision.severity,
                "should_invoke_codex": decision.should_invoke_codex,
                "should_restart_daemon": decision.should_restart_daemon,
            },
            "status_error": exception_diagnostic(status_exc, limit=1200),
        }
        try:
            append_jsonl(config.resolve(config.supervisor_log), fallback)
        except Exception:
            pass
        print(json.dumps(fallback, sort_keys=True), file=sys.stderr)
    return decision


def run_once_safely(config: SupervisorConfig) -> SupervisorDecision:
    try:
        return run_once(config)
    except KeyboardInterrupt:
        raise
    except SystemExit:
        raise
    except BaseException as exc:
        return record_supervisor_exception(config, exc)


def run_once(config: SupervisorConfig) -> SupervisorDecision:
    cleanup_stale_validation_worktrees(supervisor_daemon_config(config))
    decision = diagnose(config)
    proposal: Optional[Proposal] = None
    if decision.action == "enter_termination_storm_circuit_breaker" and config.apply:
        if config.restart_daemon:
            stop_daemon_if_running(config)
        proposal = invoke_termination_storm_circuit_breaker(config, decision)
    elif decision.action == "recover_termination_storm_and_restart" and config.apply:
        if config.restart_daemon:
            stop_daemon_if_running(config)
        proposal = invoke_termination_storm_recovery(config, decision)
        if config.restart_daemon and proposal.valid:
            attach_daemon_start_result(proposal, config, start_daemon_unless_running(config))
    elif decision.action == "reconcile_repeated_llm_loop_and_restart" and config.apply:
        if config.restart_daemon:
            stop_daemon_if_running(config)
        proposal = invoke_builtin_repair(
            config,
            decision,
            Proposal(summary="Repeated LLM parse/runtime diagnostic loop detected.", failure_kind="llm"),
        )
        if config.restart_daemon:
            attach_daemon_start_result(proposal, config, start_daemon_unless_running(config))
    elif decision.action in {"reconcile_stalled_worker_and_restart", "reconcile_dead_worker_with_recent_failures_and_restart"} and config.apply:
        if config.restart_daemon:
            stop_daemon_if_running(config)
        proposal = invoke_stalled_worker_repair(config, decision)
        if config.restart_daemon:
            attach_daemon_start_result(proposal, config, start_daemon_unless_running(config))
    elif decision.action == "reconcile_blocked_cascade_and_restart" and config.apply:
        if config.restart_daemon:
            stop_daemon_if_running(config)
        proposal = invoke_blocked_cascade_repair(config, decision)
        if config.restart_daemon:
            attach_daemon_start_result(proposal, config, start_daemon_unless_running(config))
    elif decision.action == "reconcile_dead_worker_and_restart" and config.apply:
        if config.restart_daemon:
            stop_daemon_if_running(config)
        proposal = invoke_dead_worker_repair(config, decision)
        if config.restart_daemon:
            attach_daemon_start_result(proposal, config, start_daemon_unless_running(config))
    elif decision.action == "reconcile_supersession_task_board" and config.apply:
        if config.restart_daemon:
            stop_daemon_if_running(config)
        proposal = invoke_builtin_repair(
            config,
            decision,
            Proposal(summary="Worker returned empty task-board truncation proposal.", failure_kind="no_change"),
        )
        if config.restart_daemon:
            attach_daemon_start_result(proposal, config, start_daemon_unless_running(config))
    elif decision.action == "plan_next_tasks" and config.apply and config.self_heal:
        proposal = invoke_codex_repair(config, decision)
    elif decision.action == "plan_next_tasks" and config.apply:
        if config.restart_daemon:
            stop_daemon_if_running(config)
        proposal = invoke_builtin_repair(
            config,
            decision,
            Proposal(
                summary="All currently planned PP&D tasks are complete.",
                impact="Supervisor used deterministic goal review to append the next daemon tranche.",
                failure_kind="no_eligible_tasks",
            ),
        )
        if config.restart_daemon:
            attach_daemon_start_result(proposal, config, start_daemon_unless_running(config))
    elif decision.should_restart_daemon and config.apply and config.restart_daemon and not decision.should_invoke_codex:
        result = start_daemon_unless_running(config)
        proposal = Proposal(
            summary="Supervisor restarted daemon.",
            impact=compact_message(result.stdout + " " + result.stderr),
            applied=result.returncode == 0,
            dry_run=False,
            failure_kind="" if result.returncode == 0 else "restart",
            errors=[] if result.returncode == 0 else [compact_message(result.stderr or result.stdout)],
            validation_results=[control_command_result(config, "start", result), *run_validation(supervisor_daemon_config(config))],
        )
    elif decision.should_invoke_codex and config.self_heal:
        proposal = invoke_codex_repair(config, decision)
    write_supervisor_status(config, decision, proposal)
    return decision


def supervisor_watch_sleep_seconds(
    decision: SupervisorDecision,
    config: SupervisorConfig,
    *,
    interval_seconds: float,
) -> float:
    """Choose the next watch delay without idling after progress-producing work."""

    if decision.action == "supervisor_exception":
        return max(1.0, float(config.exception_backoff_seconds))
    if decision.action in {"enter_termination_storm_circuit_breaker", "observe_circuit_breaker"}:
        return max(1.0, float(config.termination_storm_backoff_seconds))
    if decision.action in FAST_SUPERVISOR_FOLLOWUP_ACTIONS or decision.should_restart_daemon:
        return FAST_SUPERVISOR_FOLLOWUP_SECONDS
    if decision.action == "observe" and "actively working" in decision.reason:
        return min(max(1.0, float(interval_seconds)), ACTIVE_WORK_SUPERVISOR_FOLLOWUP_SECONDS)
    return max(1.0, float(interval_seconds))


def self_test(repo_root: Path) -> int:
    config = SupervisorConfig(repo_root=repo_root)
    errors: list[str] = []
    sample_status = {"updated_at": "2026-05-01T00:00:00Z"}
    if age_seconds(sample_status["updated_at"], now=datetime(2026, 5, 1, 0, 1, tzinfo=timezone.utc)) != 60:
        errors.append("timestamp age calculation failed")
    if latest_repeated_failure_count([{"applied": False}, {"applied": False}]) != 2:
        errors.append("repeated failure count failed")
    completed_failure = {"applied": False, "target_task": "Task checkbox-1: Done"}
    if latest_repeated_failure_count([completed_failure], completed_task_labels={"Task checkbox-1: Done"}) != 0:
        errors.append("completed-task failure filtering failed")
    if age_seconds("2026-05-01T00:00:00Z", now=datetime(2026, 5, 1, 0, 7, 1, tzinfo=timezone.utc)) != 421:
        errors.append("active-state age calculation failed")
    syntax_failure = {
        "failure_kind": "validation",
        "target_task": "Task checkbox-80: syntax fixture",
        "validation_results": [
            {
                "command": ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
                "returncode": 1,
                "stderr": "SyntaxError: invalid syntax",
            }
        ],
    }
    malformed_confidence_failure = {
        "failure_kind": "validation",
        "target_task": "Task checkbox-80: syntax fixture",
        "validation_results": [
            {
                "command": ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
                "returncode": 1,
                "stderr": "SyntaxError: invalid syntax near confidence 1.0",
            }
        ],
    }
    malformed_return_failure = {
        "failure_kind": "validation",
        "target_task": "Task checkbox-80: syntax fixture",
        "validation_results": [
            {
                "command": ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
                "returncode": 1,
                "stderr": "SyntaxError: invalid syntax near return 0.0 list[str]",
            }
        ],
    }
    if not is_syntax_or_compile_failure(syntax_failure):
        errors.append("syntax failure classification failed")
    syntax_preflight_failure = dict(syntax_failure)
    syntax_preflight_failure["failure_kind"] = "syntax_preflight"
    if not is_syntax_or_compile_failure(syntax_preflight_failure):
        errors.append("syntax_preflight failure classification failed")
    if recent_syntax_failure_count([syntax_failure, syntax_failure]) != 2:
        errors.append("recent syntax failure count failed")
    if not has_malformed_python_proposal_syntax(malformed_confidence_failure):
        errors.append("malformed confidence syntax marker classification failed")
    if not has_malformed_python_proposal_syntax(malformed_return_failure):
        errors.append("malformed return annotation-like syntax marker classification failed")
    if repeated_malformed_syntax_count([malformed_confidence_failure, malformed_return_failure]) != 2:
        errors.append("repeated malformed syntax count failed")
    forbidden_marker_failure = {
        "failure_kind": "validation",
        "target_task": "Task checkbox-148: audit export fixture",
        "validation_results": [
            {
                "command": ["python3", "-m", "unittest"],
                "returncode": 1,
                "stderr": "AssertionError: 'cookie' unexpectedly found in containsCookies",
            }
        ],
    }
    if not is_forbidden_absence_marker_validation_failure(forbidden_marker_failure):
        errors.append("forbidden marker validation failure classification failed")
    if recent_forbidden_absence_marker_failure_count([forbidden_marker_failure]) != 1:
        errors.append("forbidden marker validation failure count failed")
    false_positive_preflight = {
        "failure_kind": "preflight",
        "errors": [
            "private/session artifacts may not be generated by daemon proposals: "
            "ppd/tests/fixtures/daemon/checkbox_130_checkbox_108_supersession_decision.json"
        ],
        "files": ["ppd/tests/fixtures/daemon/checkbox_130_checkbox_108_supersession_decision.json"],
    }
    if not is_private_session_preflight_false_positive(false_positive_preflight):
        errors.append("private/session preflight false-positive classification failed")
    true_private_preflight = {
        "failure_kind": "preflight",
        "errors": ["private/session artifacts may not be generated by daemon proposals: ppd/data/private/devhub/session.json"],
        "files": ["ppd/data/private/devhub/session.json"],
    }
    if is_private_session_preflight_false_positive(true_private_preflight):
        errors.append("true private/session preflight rejection must not be classified as a false positive")
    empty_board_truncation = {
        "applied": False,
        "target_task": "Task checkbox-133: Append a task-board-only supersession note",
        "summary": "Unable to safely replace ppd/daemon/task-board.md because the available task-board content is truncated.",
        "impact": "The task-board content was truncated.",
        "files": [],
        "changed_files": [],
        "errors": [],
    }
    if not is_empty_task_board_truncation_proposal(empty_board_truncation):
        errors.append("empty task-board truncation proposal classification failed")
    parse_board_stall = {
        "applied": False,
        "target_task": "Task checkbox-133: Append a task-board-only supersession note",
        "failure_kind": "parse",
        "files": [],
        "changed_files": [],
    }
    if not is_checkbox_133_no_file_stall(parse_board_stall):
        errors.append("checkbox-133 parse/no-file stall classification failed")
    if not has_recent_checkbox_133_no_file_stall([], parse_board_stall):
        errors.append("recent checkbox-133 no-file stall detection failed")
    accepted_supersession_rows = [
        {
            "applied": True,
            "validation_passed": True,
            "target_task": "Task checkbox-109: processor handoff evidence",
            "summary": "Accepted checkbox-109 evidence names queued accepted skipped deferred allowlist robots/no-persist content-type timeout processor-handoff coverage.",
            "impact": "",
        },
        {
            "applied": True,
            "validation_passed": True,
            "target_task": "Task checkbox-130: supersession decision fixture",
            "summary": "checkbox-130 validates queued accepted skipped deferred allowlist robots/no-persist content-type timeout processor-handoff.",
            "impact": "",
        },
        {
            "applied": True,
            "validation_passed": True,
            "target_task": "Task checkbox-131: supersession decision validation",
            "summary": "checkbox-131 keeps missing evidence parked and complete evidence recommends task-board supersession.",
            "impact": "",
        },
        {
            "applied": True,
            "validation_passed": True,
            "target_task": "Supervisor repair for checkbox-132",
            "summary": "checkbox-132 task selection validation keeps parked blocked domain tasks out of selection.",
            "impact": "",
        },
    ]
    if not has_checkbox_108_supersession_prerequisites(accepted_supersession_rows):
        errors.append("checkbox-108 supersession prerequisite detection failed")
    supersession_board = (
        "- [!] Task checkbox-108: Add frontier checkpoint.\n"
        "- [!] Task checkbox-132: Add daemon task-selection validation.\n"
        "- [~] Task checkbox-133: Append a task-board-only supersession note.\n"
    )
    supersession_repaired, supersession_labels = builtin_supersession_repair_task_board(
        supersession_board,
        accepted_supersession_rows,
    )
    if "- [x] Task checkbox-108: Add frontier checkpoint." not in supersession_repaired:
        errors.append("supersession board repair did not complete checkbox-108")
    if "- [x] Task checkbox-133: Append a task-board-only supersession note." not in supersession_repaired:
        errors.append("supersession board repair did not complete checkbox-133")
    if "## Checkbox-108 Supersession Note" not in supersession_repaired:
        errors.append("supersession board repair did not append evidence note")
    if not {"checkbox-108", "checkbox-133"}.issubset(set(supersession_labels)):
        errors.append("supersession board repair did not report changed labels")
    complete_goal_board = "- [x] Task checkbox-1: Done.\n- [x] Task checkbox-2: Done too.\n"
    replenished_board, replenished_labels = builtin_replenish_goal_tasks(complete_goal_board)
    if "## Built-In Goal Replenishment Tranche" not in replenished_board:
        errors.append("built-in goal replenishment tranche was not appended")
    if replenished_labels != ("checkbox-3", "checkbox-4", "checkbox-5", "checkbox-6", "checkbox-7", "checkbox-8"):
        errors.append(f"unexpected replenished labels: {replenished_labels}")
    if builtin_replenish_goal_tasks(replenished_board)[1]:
        errors.append("built-in goal replenishment should not append while new tasks remain selectable")
    completed_first_tranche = replenished_board.replace("- [ ] Task checkbox-3:", "- [x] Task checkbox-3:")
    completed_first_tranche = completed_first_tranche.replace("- [ ] Task checkbox-4:", "- [x] Task checkbox-4:")
    completed_first_tranche = completed_first_tranche.replace("- [ ] Task checkbox-5:", "- [x] Task checkbox-5:")
    completed_first_tranche = completed_first_tranche.replace("- [ ] Task checkbox-6:", "- [x] Task checkbox-6:")
    completed_first_tranche = completed_first_tranche.replace("- [ ] Task checkbox-7:", "- [x] Task checkbox-7:")
    completed_first_tranche = completed_first_tranche.replace("- [ ] Task checkbox-8:", "- [x] Task checkbox-8:")
    second_tranche, second_labels = builtin_replenish_goal_tasks(completed_first_tranche)
    if second_labels != ("checkbox-9", "checkbox-10", "checkbox-11", "checkbox-12"):
        errors.append(f"unexpected second replenishment labels: {second_labels}")
    if "## Built-In Goal Replenishment Tranche 2" not in second_tranche:
        errors.append("second built-in replenishment should use a numbered heading")
    accepted_rows = [
        {"applied": True, "validation_passed": True},
        {"applied": True, "validation_passed": True},
        {"applied": True, "validation_passed": True},
        {"applied": True, "validation_passed": True},
    ]
    if not should_use_broader_goal_slices(accepted_rows):
        errors.append("green accepted streak should enable broader goal slices")
    broad_board, broad_labels = builtin_replenish_goal_tasks(complete_goal_board, accepted_rows)
    if broad_labels != ("checkbox-3", "checkbox-4", "checkbox-5", "checkbox-6"):
        errors.append(f"unexpected broader replenished labels: {broad_labels}")
    if "broad_integrated_after_green_streak" not in broad_board:
        errors.append("broader replenishment should record adaptive slice policy")
    continuation_source_board = (
        "## Built-In Autonomous PP&D Platform Tranche\n\n"
        "- [x] Task checkbox-1: Done.\n\n"
        "## Built-In Autonomous PP&D Execution Capability Tranche\n\n"
        "- [x] Task checkbox-2: Done too.\n"
    )
    continuation_board, continuation_labels = builtin_replenish_goal_tasks(continuation_source_board)
    if continuation_labels != ("checkbox-3", "checkbox-4", "checkbox-5", "checkbox-6"):
        errors.append(f"unexpected source-backed continuation labels: {continuation_labels}")
    capped_continuation_board = continuation_board
    capped_continuation_board = capped_continuation_board.replace("- [ ] Task checkbox-3:", "- [x] Task checkbox-3:")
    capped_continuation_board = capped_continuation_board.replace("- [ ] Task checkbox-4:", "- [x] Task checkbox-4:")
    capped_continuation_board = capped_continuation_board.replace("- [ ] Task checkbox-5:", "- [x] Task checkbox-5:")
    capped_continuation_board = capped_continuation_board.replace("- [ ] Task checkbox-6:", "- [x] Task checkbox-6:")
    if builtin_replenish_goal_tasks(capped_continuation_board)[1]:
        errors.append("source-backed continuation fallback must be capped after one generated tranche")
    execution_board = (
        "## Built-In Autonomous PP&D Platform Tranche 2\n\n"
        "- [~] Task checkbox-225: Add autonomous platform continuation coverage for tranche 2 proving whole-site archival, Playwright draft automation, PDF field filling, and formal-logic outputs stay connected through source evidence IDs.\n"
        "- [ ] Task checkbox-226: Add processor-suite integration planning for tranche 2 proving PP&D public documents flow through archive manifests, normalized document records, PDF metadata, and requirement batches before agents use them.\n"
        "\n## Manual Attended Worker Resume Tranche\n\n"
        "- [x] Task checkbox-240: Add attended worker resume coverage.\n"
    )
    execution_target = "Task checkbox-225: Add autonomous platform continuation coverage for tranche 2 proving whole-site archival, Playwright draft automation, PDF field filling, and formal-logic outputs stay connected through source evidence IDs."
    if not should_escalate_stale_platform_slice(execution_board, execution_target):
        errors.append("stale platform-slice goal drift was not detected")
    execution_repaired, _execution_parked, execution_labels = builtin_autonomous_execution_goal_repair_task_board(
        execution_board,
        execution_target,
    )
    if not execution_labels:
        errors.append("execution capability tranche was not appended during stale platform repair")
    if "Built-In Autonomous PP&D Execution Capability Tranche" not in execution_repaired:
        errors.append("execution capability repair did not add the expected tranche")
    invalid_repair = Proposal(summary="bad repair", errors=["Validation failed"], failure_kind="validation")
    repair_decision = SupervisorDecision(
        action="repair_daemon_programming",
        reason="synthetic failed self-heal",
        severity="warning",
        should_invoke_codex=True,
        should_restart_daemon=True,
    )
    if not should_apply_builtin_repair(repair_decision, invalid_repair):
        errors.append("failed agentic repair should trigger built-in fallback")
    accepted_repair = Proposal(summary="accepted repair", applied=True)
    accepted_repair.validation_results = []
    if should_apply_builtin_repair(repair_decision, accepted_repair):
        errors.append("accepted repair must not trigger built-in fallback")
    payload = build_builtin_repair_status_payload(repair_decision, invalid_repair)
    if payload.get("llmBackend") != os.environ.get("PPD_LLM_BACKEND", "llm_router"):
        errors.append("built-in repair payload must preserve llm_router backend")
    if "failedAgenticRepair" not in payload:
        errors.append("built-in repair payload missing failed repair diagnostics")
    plan_decision = SupervisorDecision(
        action="plan_next_tasks",
        reason="synthetic complete board",
        severity="info",
        should_invoke_codex=True,
    )
    if not should_apply_builtin_repair(plan_decision, invalid_repair):
        errors.append("plan-next-tasks fallback should remain available")
    nested_title = title_from_task_label("Task checkbox-113: Task checkbox-108: Add frontier checkpoint.")
    if nested_title != "Add frontier checkpoint.":
        errors.append(f"nested task title parsing failed: {nested_title}")
    loop_board = "- [~] Task checkbox-108: Add frontier checkpoint.\n- [ ] Task checkbox-109: Next task.\n"
    loop_rows = [
        {
            "target_task": "Task checkbox-113: Task checkbox-108: Add frontier checkpoint.",
            "failure_kind": "syntax_preflight",
            "validation_results": [{"stderr": "SyntaxError: invalid syntax"}],
        },
        {
            "target_task": "Task checkbox-113: Task checkbox-108: Add frontier checkpoint.",
            "failure_kind": "syntax_preflight",
            "validation_results": [{"stderr": "SyntaxError: invalid syntax"}],
        },
    ]
    repaired_board, parked = builtin_repair_task_board(loop_board, loop_rows)
    if "- [!] Task checkbox-108: Add frontier checkpoint." not in repaired_board:
        errors.append("built-in board repair did not park repeated syntax-loop task")
    if parked != ("Add frontier checkpoint.",):
        errors.append("built-in board repair did not report parked task title")
    non_syntax_failure = {
        "failure_kind": "validation",
        "validation_results": [{"command": ["python3", "-m", "unittest"], "returncode": 1, "stderr": "AssertionError"}],
    }
    if recent_syntax_failure_count([syntax_failure, non_syntax_failure]) != 0:
        errors.append("syntax failure streak should stop at newer non-syntax validation failures")
    if should_blocked_tasks_interrupt(2, 1, 1):
        errors.append("blocked tasks must not interrupt while independent selectable work remains")
    if not should_blocked_tasks_interrupt(2, 0, 1):
        errors.append("blocked tasks should interrupt when no selectable work remains")
    complete_board = "- [x] Finished\n"
    if parse_tasks(complete_board)[0].status != "complete":
        errors.append("task parsing failed for completed board")
    target_tasks = parse_tasks(
        "- [!] Task checkbox-225: Stale active task.\n"
        "- [ ] Task checkbox-241: Next execution task.\n"
    )
    if task_matching_target(target_tasks, "Task checkbox-225: Stale active task.") is None:
        errors.append("active target task matching failed")
    synthetic = SupervisorConfig(repo_root=repo_root)
    if synthetic.plan_doc != Path("docs/PORTLAND_PPD_SCRAPING_AUTOMATION_LOGIC_PLAN.md"):
        errors.append("supervisor plan document path changed unexpectedly")
    if not config.resolve(config.task_board).exists():
        errors.append("supervisor task board path is missing")
    if errors:
        print(json.dumps({"ok": False, "errors": errors}, indent=2), file=sys.stderr)
        return 1
    print(json.dumps({"ok": True, "supervisor": "ppd"}, indent=2))
    return 0


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Supervise and optionally repair the PP&D daemon.")
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument("--once", action="store_true", help="Run one supervision cycle")
    parser.add_argument("--watch", action="store_true", help="Run repeated supervision cycles")
    parser.add_argument("--interval", type=float, default=300.0, help="Seconds between supervisor cycles")
    parser.add_argument("--stall-seconds", type=int, default=900, help="Heartbeat age before the daemon is considered stuck")
    parser.add_argument("--apply", action="store_true", help="Allow restart or validated self-healing edits")
    parser.add_argument("--self-heal", action="store_true", help="Invoke Codex for daemon/supervisor programming repairs")
    parser.add_argument("--restart-daemon", action="store_true", help="Start/restart the worker daemon when appropriate")
    parser.add_argument("--llm-timeout", type=int, default=300, help="Seconds to allow for one Codex repair proposal")
    parser.add_argument("--termination-storm-threshold", type=int, default=8, help="Recent llm_router terminations before pausing worker restarts")
    parser.add_argument("--termination-storm-backoff", type=int, default=900, help="Supervisor sleep seconds while termination circuit breaker is active")
    parser.add_argument("--model", default="gpt-5.5", help="llm_router model")
    parser.add_argument("--provider", default=None, help="llm_router provider (default: auto-select with fallback)")
    parser.add_argument("--exception-backoff", type=float, default=5.0, help="Seconds to pause after a contained supervisor exception")
    parser.add_argument("--honor-term", action="store_true", help="Exit on TERM/HUP when an external service manager owns restart policy")
    parser.add_argument("--revisit-blocked-tasks", action="store_true", help="Restart the daemon in blocked-task revisit mode when only blocked tasks remain")
    parser.add_argument(
        "--reassess-blocked-llm-termination-gates",
        action="store_true",
        help="Treat blocked tasks with repeated LLM terminations as eligible for explicit reassessment",
    )
    parser.add_argument("--self-test", action="store_true", help="Run supervisor self-test and exit")
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    if args.self_test:
        return self_test(repo_root)
    config = SupervisorConfig(
        repo_root=repo_root,
        stall_seconds=max(1, int(args.stall_seconds)),
        llm_timeout_seconds=max(1, int(args.llm_timeout)),
        termination_storm_threshold=max(1, int(args.termination_storm_threshold)),
        termination_storm_backoff_seconds=max(1, int(args.termination_storm_backoff)),
        model_name=str(args.model),
        provider=args.provider,
        apply=bool(args.apply),
        self_heal=bool(args.self_heal),
        restart_daemon=bool(args.restart_daemon),
        exception_backoff_seconds=max(0.0, float(args.exception_backoff)),
        honor_supervisor_term=bool(args.honor_term or os.environ.get("PPD_SUPERVISOR_HONOR_TERM") == "1"),
        revisit_blocked_tasks=bool(args.revisit_blocked_tasks),
        reassess_blocked_llm_termination_gates=bool(args.reassess_blocked_llm_termination_gates),
    )
    if args.watch:
        install_supervisor_runtime_guards(config)
        while True:
            exit_if_superseded_supervisor(config)
            decision = run_once_safely(config)
            exit_if_superseded_supervisor(config)
            sleep_seconds = supervisor_watch_sleep_seconds(
                decision,
                config,
                interval_seconds=float(args.interval),
            )
            append_supervisor_runtime_event(
                config,
                "supervisor_watch_sleep",
                action=decision.action,
                sleep_seconds=sleep_seconds,
            )
            time.sleep(sleep_seconds)
    decision = run_once_safely(config)
    print(json.dumps({"action": decision.action, "reason": decision.reason, "severity": decision.severity}, indent=2))
    return 1 if decision.action == "supervisor_exception" else 0


if __name__ == "__main__":
    raise SystemExit(main())
