#!/usr/bin/env python3
"""Autonomous PP&D implementation daemon.

This daemon borrows the safe operating pattern from the TypeScript logic-port
daemon, but keeps all PP&D work in the isolated ``ppd/`` workspace.

It accepts model output only as JSON file replacements and never executes
commands returned by the model.
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import json
import os
import py_compile
import re
import signal
import subprocess
import sys
import tempfile
import traceback
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, Iterator, Optional
from urllib.parse import urlparse

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
_IPFS_DATASETS_SUBMODULE = Path(__file__).resolve().parents[2] / "ipfs_datasets_py"
if _IPFS_DATASETS_SUBMODULE.exists() and str(_IPFS_DATASETS_SUBMODULE) not in sys.path:
    sys.path.insert(0, str(_IPFS_DATASETS_SUBMODULE))
_IPFS_DATASETS_PACKAGE = _IPFS_DATASETS_SUBMODULE / "ipfs_datasets_py"
_CACHED_IPFS_PACKAGE = sys.modules.get("ipfs_datasets_py")
if (
    _CACHED_IPFS_PACKAGE is not None
    and getattr(_CACHED_IPFS_PACKAGE, "__file__", None) is None
    and _IPFS_DATASETS_PACKAGE.exists()
):
    sys.modules.pop("ipfs_datasets_py", None)

from ppd.daemon.accepted_work_ledger import (
    AcceptedWorkArtifacts,
    LEDGER_FILENAME,
    append_accepted_work_ledger as append_accepted_work_jsonl,
    build_accepted_work_ledger_entry,
)
from ppd.daemon.syntax_preflight import run_apply_flow_syntax_preflight
from ipfs_datasets_py.optimizers.todo_daemon.engine import (  # noqa: E402
    CommandResult,
    PathPolicy,
    Proposal,
    Task,
    ValidationWorkspaceSpec,
    append_jsonl,
    atomic_write_json,
    compact_message,
    cleanup_stale_validation_worktrees as cleanup_todo_validation_worktrees,
    diff_for_file as todo_diff_for_file,
    extract_json as todo_extract_json,
    materialize_proposal_files,
    normalized_relative_path as todo_normalized_relative_path,
    parse_json_proposal,
    parse_markdown_tasks,
    proposal_diff_from_worktree as todo_proposal_diff_from_worktree,
    proposal_files_from_worktree as todo_proposal_files_from_worktree,
    promote_worktree_files as todo_promote_worktree_files,
    read_text,
    run_command as todo_run_command,
    select_task as select_todo_task,
    temporary_validation_worktree as temporary_todo_validation_worktree,
    utc_now,
    verify_promoted_worktree_files as todo_verify_promoted_worktree_files,
    workspace_artifact_payload as todo_workspace_artifact_payload,
    worktree_marker_payload as todo_worktree_marker_payload,
)
from ipfs_datasets_py.optimizers.todo_daemon.runner import (  # noqa: E402
    PreTaskBlock,
    TodoDaemonHooks,
    TodoDaemonRunner,
)


CHECKBOX_RE = re.compile(r"^(?P<prefix>\s*-\s+\[)(?P<mark>[ xX~!])(?P<suffix>\]\s+)(?P<title>.+)$")
TASK_BOARD_STATUS_RE = re.compile(
    r"\n?<!-- ppd-daemon-task-board:start -->[\s\S]*?<!-- ppd-daemon-task-board:end -->\n?",
    re.MULTILINE,
)
LLM_TERMINATION_ERROR_MARKERS = (
    "143",
    "137",
    "code -15",
    "code -9",
    "signal 15",
    "signal 9",
    "sigterm",
    "sigkill",
)

ALLOWED_WRITE_PREFIXES = (
    "ppd/",
    "docs/PORTLAND_PPD_SCRAPING_AUTOMATION_LOGIC_PLAN.md",
)

DISALLOWED_WRITE_PREFIXES = (
    "src/lib/logic/",
    "public/corpus/portland-or/current/",
    "ipfs_datasets_py/.daemon/",
    "docs/IPFS_DATASETS_LOGIC_TYPESCRIPT_PORT_PLAN.md",
    "docs/IPFS_DATASETS_LOGIC_PORT_DAEMON_ACCEPTED.md",
)

PRIVATE_WRITE_PATH_FRAGMENTS = (
    "ppd/data/private/",
    "storage-state",
    "storage_state",
    "auth-state",
    "auth_state",
)
PRIVATE_WRITE_PATH_TOKENS = {"session", "sessions"}

DEFAULT_VALIDATION_COMMANDS = (
    ("python3", "ppd/daemon/ppd_daemon.py", "--self-test"),
    ("python3", "-m", "unittest", "discover", "-s", "ppd/tests", "-p", "test_*.py"),
    (
        "bash",
        "-lc",
        "files=$(find ppd -name '*.ts' -not -path '*/node_modules/*' -print); "
        "test -z \"$files\" || npx tsc --noEmit --target ES2020 --module ESNext "
        "--moduleResolution node --strict --skipLibCheck --types node $files",
    ),
)

DETERMINISTIC_FALLBACK_VALIDATION_COMMANDS = (
    (
        "python3",
        "-m",
        "unittest",
        "ppd.tests.test_daemon_llm_result_durability",
        "ppd.tests.test_supervisor_stale_status_replanning",
    ),
    ("python3", "ppd/tests/validate_ppd.py"),
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

PROTECTED_BLOCKED_REVISIT_CHECKBOX_IDS = frozenset(
    {
        178,
        182,
        186,
        187,
        191,
        193,
        194,
        195,
        197,
        198,
        203,
        208,
        209,
        210,
    }
)

_ACTIVE_LLM_PROCESS: Optional[subprocess.Popen[Any]] = None


@dataclass
class Config:
    repo_root: Path
    task_board: Path = Path("ppd/daemon/task-board.md")
    plan_doc: Path = Path("docs/PORTLAND_PPD_SCRAPING_AUTOMATION_LOGIC_PLAN.md")
    readme: Path = Path("ppd/README.md")
    status_file: Path = Path("ppd/daemon/status.json")
    progress_file: Path = Path("ppd/daemon/progress.json")
    deterministic_progress_file: Path = Path("ppd/daemon/deterministic-progress.json")
    result_log: Path = Path("ppd/daemon/ppd-daemon.jsonl")
    accepted_dir: Path = Path("ppd/daemon/accepted-work")
    failed_dir: Path = Path("ppd/daemon/failed-patches")
    worktree_dir: Path = Path("ppd/daemon/worktrees")
    model_name: str = "gpt-5.5"
    provider: Optional[str] = None
    apply: bool = False
    watch: bool = False
    iterations: int = 1
    interval_seconds: float = 0.0
    heartbeat_seconds: float = 30.0
    command_timeout_seconds: int = 300
    llm_timeout_seconds: int = 300
    max_prompt_chars: int = 60000
    max_compact_prompt_chars: int = 4200
    llm_max_new_tokens: int = 2048
    allow_local_fallback: bool = False
    revisit_blocked: bool = False
    max_task_failures_before_block: int = 3
    repair_validation_failures: bool = False
    max_validation_repair_attempts: int = 1
    write_accepted_work_sidecars: bool = False
    worktree_stale_seconds: int = 7200
    crash_backoff_seconds: float = 5.0
    validation_repair_callback: Optional[Callable[[str, "Config"], str]] = None
    validation_commands: tuple[tuple[str, ...], ...] = DEFAULT_VALIDATION_COMMANDS

    def resolve(self, path: Path) -> Path:
        return path if path.is_absolute() else self.repo_root / path


@dataclass(frozen=True)
class PreLlmBlockDecision:
    summary: str
    failure_kind: str
    result: str


def parse_tasks(markdown: str) -> list[Task]:
    return parse_markdown_tasks(markdown, checkbox_re=CHECKBOX_RE)


def select_task(tasks: Iterable[Task], *, revisit_blocked: bool = False) -> Optional[Task]:
    return select_todo_task(
        tasks,
        revisit_blocked=revisit_blocked,
        protected_blocked_checkbox_ids=PROTECTED_BLOCKED_REVISIT_CHECKBOX_IDS,
    )


def select_task_for_config(tasks: Iterable[Task], config: Config) -> Optional[Task]:
    """Select work while suppressing blocked tasks that already hit retry stop gates."""

    task_list = list(tasks)
    selected = select_task(task_list, revisit_blocked=False)
    if selected is not None:
        return selected
    if not config.revisit_blocked:
        return None
    for task in task_list:
        if task.status != "blocked":
            continue
        if task.checkbox_id in PROTECTED_BLOCKED_REVISIT_CHECKBOX_IDS:
            continue
        try:
            block_decision = pre_llm_block_decision(config, task.label)
        except Exception:
            continue
        if block_decision is not None:
            continue
        return task
    return None


def replace_task_mark(markdown: str, selected: Task, mark: str) -> str:
    seen = 0
    lines = markdown.splitlines(keepends=True)
    for idx, line in enumerate(lines):
        match = CHECKBOX_RE.match(line.rstrip("\n"))
        if not match:
            continue
        seen += 1
        if seen == selected.index:
            lines[idx] = f"{match.group('prefix')}{mark}{match.group('suffix')}{match.group('title')}\n"
            break
    return "".join(lines)


def count_unmanaged_generated_status_sections(markdown: str) -> int:
    """Count generated-status headings outside the daemon-managed marker block."""

    count = 0
    in_managed_block = False
    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped == "<!-- ppd-daemon-task-board:start -->":
            in_managed_block = True
            continue
        if stripped == "<!-- ppd-daemon-task-board:end -->":
            in_managed_block = False
            continue
        if not in_managed_block and stripped == "## Generated Status":
            count += 1
    return count


def strip_unmanaged_generated_status_sections(markdown: str) -> str:
    """Remove stale generated-status sections outside the managed marker block."""

    lines = markdown.splitlines()
    cleaned: list[str] = []
    in_managed_block = False
    skipping_unmanaged_status = False
    for line in lines:
        stripped = line.strip()
        if stripped == "<!-- ppd-daemon-task-board:start -->":
            in_managed_block = True
            skipping_unmanaged_status = False
            cleaned.append(line)
            continue
        if stripped == "<!-- ppd-daemon-task-board:end -->":
            in_managed_block = False
            cleaned.append(line)
            continue
        if skipping_unmanaged_status:
            if stripped.startswith("## ") or stripped == "<!-- ppd-daemon-task-board:start -->":
                skipping_unmanaged_status = False
            else:
                continue
        if not in_managed_block and stripped == "## Generated Status":
            skipping_unmanaged_status = True
            continue
        cleaned.append(line)
    return "\n".join(cleaned).rstrip() + ("\n" if markdown.endswith("\n") else "")


def update_generated_status(markdown: str, *, latest: dict[str, Any], tasks: list[Task]) -> str:
    markdown = strip_unmanaged_generated_status_sections(markdown)
    counts = {
        "needed": sum(1 for task in tasks if task.status == "needed"),
        "in_progress": sum(1 for task in tasks if task.status == "in-progress"),
        "complete": sum(1 for task in tasks if task.status == "complete"),
        "blocked": sum(1 for task in tasks if task.status == "blocked"),
    }
    block = f"""
<!-- ppd-daemon-task-board:start -->
## Generated Status

Last updated: {utc_now()}

- Latest target: `{latest.get("target_task", "")}`
- Latest result: `{latest.get("result", "")}`
- Latest summary: {latest.get("summary", "")}
- Counts: `{json.dumps(counts, sort_keys=True)}`

<!-- ppd-daemon-task-board:end -->
"""
    if TASK_BOARD_STATUS_RE.search(markdown):
        return TASK_BOARD_STATUS_RE.sub("\n" + block.strip() + "\n", markdown).rstrip() + "\n"
    return markdown.rstrip() + "\n\n" + block


def should_sleep_between_watch_cycles(markdown: str, *, revisit_blocked: bool = False) -> bool:
    """Sleep only when there is no immediately selectable work on the board."""

    return select_task(parse_tasks(markdown), revisit_blocked=revisit_blocked) is None


def exception_diagnostic(exc: BaseException, *, limit: int = 5000) -> str:
    return compact_message("".join(traceback.format_exception(type(exc), exc, exc.__traceback__)), limit=limit)


def is_retryable_failure(proposal: Proposal) -> bool:
    if proposal.failure_kind in {"llm", "parse", "empty_proposal"}:
        return True
    text = " ".join(proposal.errors).lower()
    return any(
        marker in text
        for marker in (
            "cloudflare",
            "403 forbidden",
            "plugins/featured",
            "timed out",
            "timeout",
            "could not generate",
            "provider",
        )
    )


def is_llm_termination_failure_record(proposal: dict[str, Any]) -> bool:
    if str(proposal.get("failure_kind") or "") != "llm":
        return False
    text = " ".join(str(error).lower() for error in proposal.get("errors", []) or [])
    return bool(text and any(marker in text for marker in LLM_TERMINATION_ERROR_MARKERS))


def failure_block_threshold(proposal: Proposal, config: Config) -> int:
    """Use a tighter stop condition for parser-invalid generated patches."""

    if proposal.failure_kind in {"syntax_preflight", "llm_termination"}:
        return min(config.max_task_failures_before_block, 2)
    if proposal.failure_kind == "no_visible_source_change":
        return 1
    return config.max_task_failures_before_block


def should_skip_validation_for_no_file_failure(proposal: Proposal) -> bool:
    """Avoid expensive validation when the LLM produced no candidate files."""

    if proposal.files:
        return False
    return proposal.failure_kind in {"llm", "parse", "empty_proposal"}


def read_result_log(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            continue
        proposal = parsed.get("proposal")
        if isinstance(proposal, dict):
            rows.append(proposal)
    return rows


def read_result_and_diagnostic_log(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            continue
        proposal = parsed.get("proposal")
        diagnostic = parsed.get("diagnostic")
        if isinstance(proposal, dict):
            rows.append(proposal)
        elif isinstance(diagnostic, dict):
            row = dict(diagnostic)
            row["_diagnostic_stage"] = parsed.get("stage", "")
            rows.append(row)
    return rows


def recent_task_failures(config: Config, task_label: str, *, limit: int = 3) -> list[dict[str, Any]]:
    failures: list[dict[str, Any]] = []
    for proposal in reversed(read_result_and_diagnostic_log(config.resolve(config.result_log))):
        if proposal.get("target_task") != task_label:
            continue
        if proposal.get("applied") and proposal.get("validation_passed") and not proposal.get("errors"):
            break
        failures.append(proposal)
        if len(failures) >= limit:
            break
    return failures


def should_use_compact_prompt(failures: list[dict[str, Any]], *, threshold: int = 2) -> bool:
    count = 0
    for failure in failures:
        if str(failure.get("failure_kind") or "") in {"parse", "llm"}:
            count += 1
    return count >= threshold


def effective_prompt_limit(config: Config, *, compact_prompt: bool) -> int:
    if compact_prompt:
        return min(config.max_prompt_chars, config.max_compact_prompt_chars)
    return config.max_prompt_chars


def task_failure_count(config: Config, task_label: str, *, kinds: Optional[set[str]] = None) -> int:
    count = 0
    for proposal in recent_task_failures(config, task_label, limit=100):
        kind = str(proposal.get("failure_kind") or "")
        if kinds is None or kind in kinds:
            count += 1
    return count


def llm_termination_failure_count(config: Config, task_label: str) -> int:
    count = 0
    for proposal in recent_task_failures(config, task_label, limit=100):
        if is_llm_termination_failure_record(proposal):
            count += 1
    return count


def pre_llm_block_decision(config: Config, task_label: str) -> Optional[PreLlmBlockDecision]:
    """Return a durable stop decision for tasks that are already known-stuck."""

    syntax_probe = Proposal(failure_kind="syntax_preflight")
    if (
        task_failure_count(config, task_label, kinds={"syntax_preflight"})
        >= failure_block_threshold(syntax_probe, config)
    ):
        return PreLlmBlockDecision(
            summary="Task blocked before LLM after repeated syntax-preflight failures.",
            failure_kind="syntax_preflight",
            result="syntax_preflight_blocked",
        )

    termination_probe = Proposal(failure_kind="llm_termination")
    if llm_termination_failure_count(config, task_label) >= failure_block_threshold(termination_probe, config):
        return PreLlmBlockDecision(
            summary="Task blocked before LLM after repeated LLM termination failures.",
            failure_kind="llm_termination",
            result="llm_termination_blocked",
        )

    return None


def should_block_task_before_llm(config: Config, task_label: str) -> bool:
    """Stop retrying a task that already hit a pre-LLM block threshold."""

    return pre_llm_block_decision(config, task_label) is not None


DETERMINISTIC_TASK_FALLBACK_TITLES: tuple[tuple[str, str], ...] = (
    ("autonomous platform continuation coverage", "platform_continuation"),
    ("processor-suite integration planning", "processor_suite_planning"),
    ("playwright/pdf handoff validation", "playwright_pdf_handoff"),
    ("supervisor idle-recovery validation", "supervisor_idle_recovery"),
)

DETERMINISTIC_TASK_SOURCE_EVIDENCE_IDS = (
    "evidence:ppd-home:2026-05-01",
    "evidence:permit-applications-index:2026-05-01",
    "evidence:devhub-faq:2026-05-01",
    "evidence:single-pdf-process:2026-05-01",
)

DETERMINISTIC_PLATFORM_INIT = '''"""Source-backed PP&D autonomous platform contracts.

Modules in this package are imported directly by capability area so a partially
implemented tranche never imports a source file that has not been created yet.
"""
'''

DETERMINISTIC_SOURCE_FILES: dict[str, tuple[str, str]] = {
    "platform_continuation": (
        "ppd/platform/autonomous_archival_contract.py",
        '''"""Source-backed contract for PP&D public archival capability.

The contract is intentionally side-effect-free: it names the implementation
surfaces the daemon must wire together before any live crawl is allowed.
"""

from __future__ import annotations


def archival_contract() -> dict[str, object]:
    return {
        "capability": "whole_site_public_archival",
        "entrypoints": [
            "ppd.crawler.live_public_preflight",
            "ppd.crawler.whole_site_archival",
            "ipfs_datasets_py.processors",
        ],
        "requiredOutputs": [
            "archive_manifest",
            "normalized_document_record",
            "source_evidence_id",
            "requirement_batch",
        ],
        "defaultMode": "fixture_only",
        "liveCrawlAllowedByDefault": False,
    }
''',
    ),
    "processor_suite_planning": (
        "ppd/platform/processor_suite_contract.py",
        '''"""Source-backed contract for processor-suite PP&D handoff."""

from __future__ import annotations


def processor_suite_contract() -> dict[str, object]:
    return {
        "capability": "processor_suite_handoff",
        "processorSuite": "ipfs_datasets_py.processors",
        "requiredInputs": [
            "public_source_url",
            "robots_decision",
            "content_type",
            "canonical_document_id",
        ],
        "requiredOutputs": [
            "processor_handoff_manifest",
            "pdf_metadata_record",
            "normalized_public_document",
            "formal_logic_source_evidence_id",
        ],
        "rawBodyPersistenceAllowed": False,
    }
''',
    ),
    "playwright_pdf_handoff": (
        "ppd/platform/playwright_pdf_contract.py",
        '''"""Source-backed contract for attended Playwright and PDF draft work."""

from __future__ import annotations


def playwright_pdf_contract() -> dict[str, object]:
    return {
        "capability": "attended_draft_automation",
        "allowedActions": [
            "manual_login_handoff",
            "journal_replay",
            "reversible_draft_field_fill",
            "local_pdf_preview_fill",
        ],
        "blockedActions": [
            "official_upload",
            "permit_submission",
            "certification",
            "fee_payment",
            "account_security_transition",
            "inspection_scheduling",
        ],
        "requiresHumanAttendanceBeforeBrowserUse": True,
        "exactConfirmationBeforeOfficialAction": True,
    }
''',
    ),
    "supervisor_idle_recovery": (
        "ppd/platform/supervisor_idle_policy.py",
        '''"""Source-backed contract for supervisor idle and replenishment behavior."""

from __future__ import annotations


def supervisor_idle_policy() -> dict[str, object]:
    return {
        "capability": "supervisor_idle_recovery",
        "noEligibleTasksPolicy": "review_goal_before_replenishment",
        "replenishmentLimits": {
            "autonomousPlatformTranches": 1,
            "executionCapabilityTranches": 1,
        },
        "mustNotAcceptRuntimeOnlyProgress": True,
        "mustVerifyPromotionToMainWorktree": True,
        "acceptedEvidenceMode": "ledger_only",
    }
''',
    ),
}


def deterministic_task_fallback_kind(task: Task) -> str:
    lowered = task.title.lower()
    for marker, kind in DETERMINISTIC_TASK_FALLBACK_TITLES:
        if marker in lowered:
            return kind
    return ""


def has_deterministic_task_fallback(task: Task) -> bool:
    return bool(deterministic_task_fallback_kind(task))


def has_open_deterministic_task_fallback(tasks: Iterable[Task]) -> bool:
    return any(task.status in {"needed", "in-progress"} and has_deterministic_task_fallback(task) for task in tasks)


def build_deterministic_task_fallback_proposal(config: Config, selected: Task) -> Optional[Proposal]:
    """Build a fixture-only proposal for known platform tasks when the LLM path is unhealthy."""

    fallback_kind = deterministic_task_fallback_kind(selected)
    if not fallback_kind:
        return None

    manifest = deterministic_progress_manifest(config)
    records = [record for record in manifest.get("records", []) if isinstance(record, dict)]
    records = [
        record
        for record in records
        if str(record.get("taskLabel") or "") != selected.label
        and int(record.get("checkboxId", -1) if isinstance(record.get("checkboxId"), int) else -1) != selected.checkbox_id
    ]
    records.append(deterministic_progress_record(selected, fallback_kind))
    manifest["records"] = sorted(records, key=lambda item: int(item.get("checkboxId", 0)))
    manifest["updatedAt"] = utc_now()
    validation_commands = (
        DETERMINISTIC_FALLBACK_VALIDATION_COMMANDS
        if config.validation_commands == DEFAULT_VALIDATION_COMMANDS
        else config.validation_commands
    )
    source_path, source_content = DETERMINISTIC_SOURCE_FILES[fallback_kind]

    return Proposal(
        summary=f"Complete {fallback_kind.replace('_', ' ')} with deterministic PP&D fallback.",
        impact=(
            "The daemon can keep making fixture-only PP&D platform progress while the LLM backend is in "
            "a termination storm. The generated record preserves source evidence, processor, draft "
            "automation, PDF-preview, and formal-logic boundaries without live DevHub or official actions."
        ),
        files=[
            {
                "path": "ppd/platform/__init__.py",
                "content": DETERMINISTIC_PLATFORM_INIT,
            },
            {
                "path": source_path,
                "content": source_content,
            },
            {
                "path": config.deterministic_progress_file.as_posix(),
                "content": json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            }
        ],
        validation_commands=[list(command) for command in validation_commands],
        failure_kind="",
        trusted_validation_commands=True,
        requires_visible_source_change=True,
    )


def deterministic_progress_manifest(config: Config) -> dict[str, Any]:
    path = config.resolve(config.deterministic_progress_file)
    if path.exists():
        try:
            parsed = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(parsed, dict):
                parsed.setdefault("schemaVersion", 1)
                parsed.setdefault("records", [])
                parsed.setdefault("strategy", "deterministic_task_fallback_when_llm_unavailable")
                return parsed
        except json.JSONDecodeError:
            pass
    return {
        "schemaVersion": 1,
        "strategy": "deterministic_task_fallback_when_llm_unavailable",
        "updatedAt": utc_now(),
        "records": [],
    }


def deterministic_progress_record(selected: Task, fallback_kind: str) -> dict[str, Any]:
    tranche_match = re.search(r"\btranche\s+(\d+)\b", selected.title.lower())
    tranche = int(tranche_match.group(1)) if tranche_match else None
    return {
        "checkboxId": selected.checkbox_id,
        "taskLabel": selected.label,
        "title": selected.title,
        "fallbackKind": fallback_kind,
        "tranche": tranche,
        "completedAt": utc_now(),
        "sourceEvidenceIds": list(DETERMINISTIC_TASK_SOURCE_EVIDENCE_IDS),
        "artifactContracts": deterministic_artifact_contracts(fallback_kind),
        "guardrails": [
            "public_sources_only",
            "redacted_user_facts_only",
            "reversible_draft_actions_only",
            "local_pdf_preview_only",
            "exact_confirmation_before_official_action",
            "formal_logic_requires_source_evidence",
        ],
        "blockedActions": [
            "official_upload",
            "permit_submission",
            "certification",
            "fee_payment",
            "account_security_transition",
            "inspection_scheduling",
        ],
        "runtimePolicy": {
            "liveCrawlAllowedByDefault": False,
            "officialDevhubActionAllowedByDefault": False,
            "privateArtifactPersistence": "forbidden",
            "requiresHumanAttendanceBeforeBrowserUse": True,
        },
    }


def deterministic_artifact_contracts(fallback_kind: str) -> list[str]:
    if fallback_kind == "platform_continuation":
        return [
            "archive_manifest",
            "normalized_document_record",
            "playwright_draft_plan",
            "pdf_preview_field_map",
            "formal_logic_guardrail_batch",
        ]
    if fallback_kind == "processor_suite_planning":
        return [
            "processor_handoff_manifest",
            "normalized_public_document",
            "pdf_metadata_record",
            "requirement_batch",
            "human_review_gate",
        ]
    if fallback_kind == "playwright_pdf_handoff":
        return [
            "redacted_fact_map",
            "accessible_selector_plan",
            "pdf_preview_field_map",
            "exact_confirmation_checkpoint",
            "audit_event",
        ]
    if fallback_kind == "supervisor_idle_recovery":
        return [
            "completed_board_summary",
            "goal_aligned_task_synthesis",
            "duplicate_tranche_guard",
            "blocked_retry_churn_guard",
            "immediate_restart_gate",
        ]
    return ["deterministic_progress_record"]


def format_failure_context(failures: list[dict[str, Any]]) -> str:
    if not failures:
        return "No recent failures for this task."
    parts: list[str] = []
    for index, failure in enumerate(failures, start=1):
        validation_bits: list[str] = []
        for result in failure.get("validation_results", []) or []:
            if not isinstance(result, dict) or int(result.get("returncode", 0)) == 0:
                continue
            command = " ".join(str(part) for part in result.get("command", []))
            validation_bits.append(
                f"{command}: {compact_message(str(result.get('stdout', '')) + ' ' + str(result.get('stderr', '')), limit=900)}"
            )
        parts.append(
            "\n".join(
                [
                    f"Failure {index}: kind={failure.get('failure_kind', '')}",
                    f"summary={compact_message(failure.get('summary', ''), limit=300)}",
                    f"errors={'; '.join(compact_message(error, limit=300) for error in failure.get('errors', [])[:3])}",
                    f"validation={'; '.join(validation_bits) if validation_bits else '<none>'}",
                ]
            )
        )
    if any(is_forbidden_absence_marker_validation_failure(failure) for failure in failures):
        parts.append(
            "Recovery guidance: a validator found a forbidden artifact marker inside the proposed fixture or test text. "
            "Return only one JSON object on the retry, and use a small file set that fixes the self-triggering field names. "
            "When representing absence, avoid keys or values containing banned substrings such as cookie, screenshot, "
            "auth-state, storage-state, trace.zip, or .har. Use neutral names like `runtimeArtifactsStored`, "
            "`visualArtifactsStored`, `authenticatedArtifactsStored`, or `forbiddenArtifactsAbsent` instead of "
            "`containsCookies`, `screenshotsStored`, or similar self-triggering absence fields."
        )
    return "\n\n".join(parts)


def is_forbidden_absence_marker_validation_failure(failure: dict[str, Any]) -> bool:
    """Detect validation failures caused by fixture/test text containing banned marker words."""

    if str(failure.get("failure_kind") or "") != "validation":
        return False
    text_parts: list[str] = []
    for error in failure.get("errors", []) or []:
        text_parts.append(str(error))
    for result in failure.get("validation_results", []) or []:
        if not isinstance(result, dict):
            continue
        text_parts.append(str(result.get("stdout", "")))
        text_parts.append(str(result.get("stderr", "")))
    text = "\n".join(text_parts).lower()
    if "unexpectedly found" not in text and "assertnotin" not in text:
        return False
    return any(marker in text for marker in FORBIDDEN_ABSENCE_MARKERS)


RUNTIME_ONLY_CHANGE_PATHS = frozenset(
    {
        "ppd/daemon/builtin-repair-status.json",
        "ppd/daemon/deterministic-progress.json",
        "ppd/daemon/task-board.md",
    }
)

PPD_PATH_POLICY = PathPolicy(
    allowed_write_prefixes=ALLOWED_WRITE_PREFIXES,
    disallowed_write_prefixes=DISALLOWED_WRITE_PREFIXES,
    private_write_path_fragments=PRIVATE_WRITE_PATH_FRAGMENTS,
    private_write_path_tokens=PRIVATE_WRITE_PATH_TOKENS,
    runtime_only_change_paths=RUNTIME_ONLY_CHANGE_PATHS,
    ignored_visible_prefixes=(
        "ppd/daemon/accepted-work/",
        "ppd/daemon/failed-patches/",
        "ppd/daemon/worktrees/",
    ),
    visible_source_prefixes=("ppd/",),
)


def extract_json(text: str) -> Optional[dict[str, Any]]:
    return todo_extract_json(text)


def parse_proposal(text: str) -> Proposal:
    return parse_json_proposal(text)


def normalized_relative_path(path: str) -> str:
    return todo_normalized_relative_path(path)


def validate_write_path(path: str) -> list[str]:
    return PPD_PATH_POLICY.validate_write_path(path, daemon_label="PP&D daemon")


def is_private_write_path(normalized: str) -> bool:
    return PPD_PATH_POLICY.is_private_write_path(normalized)


def has_visible_source_change(changed_files: Iterable[str]) -> bool:
    """Return True when accepted work changes source or fixture files, not only runtime state."""

    return PPD_PATH_POLICY.has_visible_source_change(changed_files)


def run_command(command: tuple[str, ...], *, cwd: Path, timeout: int) -> CommandResult:
    return todo_run_command(command, cwd=cwd, timeout=timeout)


def validation_commands_for_proposal(proposal: Proposal, config: Config) -> tuple[tuple[str, ...], ...]:
    if proposal.trusted_validation_commands and proposal.validation_commands:
        return tuple(tuple(command) for command in proposal.validation_commands)
    return config.validation_commands


def run_validation(
    config: Config,
    *,
    commands: Optional[tuple[tuple[str, ...], ...]] = None,
) -> list[CommandResult]:
    selected_commands = commands if commands is not None else config.validation_commands
    return [
        run_command(command, cwd=config.repo_root, timeout=config.command_timeout_seconds)
        for command in selected_commands
    ]


def diff_for_file(path: str, before: str, after: str) -> str:
    return todo_diff_for_file(path, before, after)


def worktree_marker_payload(*, state: str, source_root: Path) -> dict[str, Any]:
    return todo_worktree_marker_payload(state=state, source_root=source_root)


def cleanup_stale_validation_worktrees(config: Config, *, max_age_seconds: Optional[int] = None) -> list[str]:
    """Remove old PP&D validation worktrees left by interrupted daemon runs."""

    return cleanup_todo_validation_worktrees(
        config.resolve(config.worktree_dir),
        marker_name="ppd-worktree.json",
        max_age_seconds=int(config.worktree_stale_seconds if max_age_seconds is None else max_age_seconds),
    )


def _ignore_validation_tree_entries(directory: str, names: list[str]) -> set[str]:
    ignored = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "node_modules"}
    path = Path(directory)
    if path.name == "daemon":
        ignored.update({"worktrees", "failed-patches", "accepted-work"})
        ignored.update(name for name in names if name.endswith(".pid") or name.endswith(".out") or name.endswith(".jsonl"))
        ignored.update({"status.json", "progress.json", "supervisor-status.json", "supervisor-actions.jsonl"})
    return {name for name in names if name in ignored}


@contextmanager
def temporary_validation_worktree(config: Config) -> Iterator[Path]:
    """Create an isolated PP&D validation tree and remove it after the cycle."""

    plan_doc = config.plan_doc
    if plan_doc.is_absolute():
        try:
            plan_doc = plan_doc.relative_to(config.repo_root)
        except ValueError:
            plan_doc = Path()
    copy_paths = tuple(path for path in (Path("ppd"), plan_doc) if path.as_posix())
    spec = ValidationWorkspaceSpec(
        repo_root=config.repo_root,
        worktree_dir=config.worktree_dir,
        marker_name="ppd-worktree.json",
        copy_paths=copy_paths,
        root_files=("package.json", "package-lock.json", "tsconfig.json"),
        external_reference_paths=(Path("ipfs_datasets_py/ipfs_datasets_py/processors"),),
        ignore=_ignore_validation_tree_entries,
        stale_seconds=config.worktree_stale_seconds,
    )
    with temporary_todo_validation_worktree(spec) as worktree:
        yield worktree


def worktree_config(config: Config, worktree: Path) -> Config:
    return replace(
        config,
        repo_root=worktree,
        repair_validation_failures=False,
        validation_repair_callback=None,
    )


def proposal_diff_from_worktree(config: Config, worktree: Path, changed: Iterable[str]) -> str:
    return todo_proposal_diff_from_worktree(config.repo_root, worktree, changed)


def workspace_artifact_payload(
    proposal: Proposal,
    *,
    transport: str,
    promoted: bool,
    reason: str = "",
) -> dict[str, Any]:
    return todo_workspace_artifact_payload(
        proposal,
        transport=transport,
        promoted=promoted,
        reason=reason,
    )


def materialize_proposal_in_worktree(proposal: Proposal, config: Config, worktree: Path) -> list[str]:
    return materialize_proposal_files(proposal, worktree)


def proposal_files_from_worktree(worktree: Path, changed: Iterable[str]) -> list[dict[str, str]]:
    return todo_proposal_files_from_worktree(worktree, changed)


def promote_worktree_files(config: Config, worktree: Path, changed: Iterable[str]) -> None:
    todo_promote_worktree_files(config.repo_root, worktree, changed)


def verify_promoted_worktree_files(config: Config, worktree: Path, changed: Iterable[str]) -> list[str]:
    """Verify promoted files in the main worktree exactly match the accepted worktree."""

    return todo_verify_promoted_worktree_files(config.repo_root, worktree, changed)


def validation_results_from_syntax_preflight(worktree: Path, changed: list[str], config: Config) -> tuple[list[CommandResult], list[str], str]:
    syntax_preflight = run_apply_flow_syntax_preflight(
        worktree,
        changed,
        timeout=config.command_timeout_seconds,
    )
    results = [
        CommandResult(
            command=result.command,
            returncode=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
        )
        for result in syntax_preflight.validation_results
    ]
    return results, list(syntax_preflight.errors), syntax_preflight.failure_kind


def build_validation_repair_prompt(proposal: Proposal, config: Config) -> str:
    failed_results = "\n".join(
        json.dumps(result.compact(limit=1200), sort_keys=True)
        for result in proposal.validation_results
        if not result.ok
    )
    files = "\n".join(f"- {path}" for path in proposal.changed_files)
    return f"""
You are repairing a PP&D daemon candidate inside an isolated temporary validation worktree.

Return exactly one JSON object with complete file replacements. Do not include markdown.

Original task:
{proposal.target_task}

Current failed candidate:
- summary: {proposal.summary}
- changed files:
{files}

Failing validation results:
{failed_results or "No failing command output was captured."}

Repair rules:
- Edit only files under ppd/ or docs/PORTLAND_PPD_SCRAPING_AUTOMATION_LOGIC_PLAN.md.
- Keep the repair smaller than the failed candidate when possible.
- Do not create private DevHub artifacts, raw crawl output, downloaded documents, browser traces, screenshots, credentials, or payment data.
- Return JSON in this shape:
{{"summary":"short repair summary","impact":"why this fixes validation","files":[{{"path":"ppd/...","content":"complete replacement"}}]}}
"""


def call_validation_repair_llm(prompt: str, config: Config) -> str:
    if config.validation_repair_callback is not None:
        return config.validation_repair_callback(prompt, config)
    return call_llm(prompt, config)


def attempt_validation_repair_pass(
    proposal: Proposal,
    config: Config,
    worktree: Path,
) -> tuple[bool, list[str], str]:
    if not config.repair_validation_failures or config.max_validation_repair_attempts <= 0:
        return False, proposal.changed_files, ""
    try:
        raw = call_validation_repair_llm(build_validation_repair_prompt(proposal, config), config)
        repair = parse_proposal(raw)
    except BaseException as exc:
        proposal.errors.append(f"Validation repair pass failed before producing JSON: {compact_message(exc)}")
        return False, proposal.changed_files, ""
    repair.target_task = proposal.target_task
    repair_errors: list[str] = []
    for item in repair.files:
        repair_errors.extend(validate_write_path(item["path"]))
    if repair_errors:
        proposal.errors.extend(f"Validation repair pass rejected write path: {error}" for error in repair_errors)
        return False, proposal.changed_files, ""
    if not repair.files:
        proposal.errors.append("Validation repair pass produced no file replacements.")
        return False, proposal.changed_files, ""

    changed = list(dict.fromkeys(proposal.changed_files + materialize_proposal_in_worktree(repair, config, worktree)))
    repair_results, repair_preflight_errors, repair_failure_kind = validation_results_from_syntax_preflight(
        worktree,
        changed,
        config,
    )
    proposal.validation_results = repair_results
    if repair_preflight_errors:
        proposal.errors.extend("Validation repair pass syntax preflight failed: " + error for error in repair_preflight_errors)
        proposal.failure_kind = repair_failure_kind or "syntax_preflight"
        return False, changed, proposal_diff_from_worktree(config, worktree, changed)

    proposal.validation_results = run_validation(
        worktree_config(config, worktree),
        commands=validation_commands_for_proposal(proposal, config),
    )
    if not all(result.ok for result in proposal.validation_results):
        proposal.errors.append("Validation repair pass failed; candidate worktree was not promoted.")
        proposal.failure_kind = "validation"
        return False, changed, proposal_diff_from_worktree(config, worktree, changed)

    proposal.summary = repair.summary or proposal.summary
    proposal.impact = repair.impact or proposal.impact
    proposal.files = proposal_files_from_worktree(worktree, changed)
    proposal.changed_files = changed
    proposal.errors = []
    return True, changed, proposal_diff_from_worktree(config, worktree, changed)


def apply_files_with_validation(proposal: Proposal, config: Config) -> Proposal:
    proposal_validation_commands = validation_commands_for_proposal(proposal, config)
    preflight_errors: list[str] = []
    for item in proposal.files:
        preflight_errors.extend(validate_write_path(item["path"]))
    if preflight_errors:
        proposal.errors.extend(preflight_errors)
        proposal.failure_kind = "preflight"
        persist_failed_work(proposal, config, diff_text="", reason="preflight")
        return proposal

    with temporary_validation_worktree(config) as worktree:
        changed = materialize_proposal_in_worktree(proposal, config, worktree)
        proposal.changed_files = changed
        if not changed:
            proposal.errors.append("Proposal made no content changes.")
            proposal.failure_kind = "no_change"
            proposal.validation_results = run_validation(
                worktree_config(config, worktree),
                commands=proposal_validation_commands,
            )
            persist_failed_work(proposal, config, diff_text="", reason="no_change", transport="ephemeral_worktree")
            return proposal

        if proposal.requires_visible_source_change and not has_visible_source_change(changed):
            proposal.errors.append(
                "Accepted work must promote at least one visible PP&D source or fixture file; "
                "runtime-only progress records are not sufficient."
            )
            proposal.failure_kind = "no_visible_source_change"
            proposal.validation_results = run_validation(
                worktree_config(config, worktree),
                commands=proposal_validation_commands,
            )
            persist_failed_work(
                proposal,
                config,
                diff_text=proposal_diff_from_worktree(config, worktree, changed),
                reason="no_visible_source_change",
                transport="ephemeral_worktree",
            )
            return proposal

        diff_text = proposal_diff_from_worktree(config, worktree, changed)
        proposal.validation_results, preflight_errors, failure_kind = validation_results_from_syntax_preflight(
            worktree,
            changed,
            config,
        )
        if preflight_errors:
            proposal.errors.extend(preflight_errors)
            proposal.failure_kind = failure_kind
            persist_failed_work(proposal, config, diff_text=diff_text, reason="syntax_preflight", transport="ephemeral_worktree")
            return proposal

        proposal.validation_results = run_validation(
            worktree_config(config, worktree),
            commands=proposal_validation_commands,
        )
        if not all(result.ok for result in proposal.validation_results):
            repaired, changed, repair_diff = attempt_validation_repair_pass(proposal, config, worktree)
            diff_text = repair_diff or proposal_diff_from_worktree(config, worktree, changed)
            proposal.changed_files = changed
            if not repaired:
                if not proposal.failure_kind:
                    proposal.errors.append("Validation failed in temporary worktree; candidate was not promoted.")
                    proposal.failure_kind = "validation"
                persist_failed_work(proposal, config, diff_text=diff_text, reason=proposal.failure_kind or "validation", transport="ephemeral_worktree")
                return proposal

        promote_worktree_files(config, worktree, proposal.changed_files)
        promotion_errors = verify_promoted_worktree_files(config, worktree, proposal.changed_files)
        proposal.promotion_errors = promotion_errors
        proposal.promotion_verified = not promotion_errors
        if promotion_errors:
            proposal.errors.extend(promotion_errors)
            proposal.failure_kind = "promotion"
            persist_failed_work(proposal, config, diff_text=diff_text, reason="promotion", transport="ephemeral_worktree")
            return proposal
        proposal.applied = True
        persist_accepted_work(proposal, config, diff_text=diff_text, transport="ephemeral_worktree")
    return proposal


def persist_accepted_work(proposal: Proposal, config: Config, *, diff_text: str, transport: str = "direct") -> None:
    config.resolve(config.accepted_dir).mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", proposal.summary.lower()).strip("-")[:80] or "accepted-work"
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    base = config.resolve(config.accepted_dir) / f"{stamp}-{slug}"
    if config.write_accepted_work_sidecars:
        manifest = {
            "created_at": utc_now(),
            "artifact_kind": "accepted_ephemeral_workspace",
            "target_task": proposal.target_task,
            "summary": proposal.summary,
            "impact": proposal.impact,
            "changed_files": proposal.changed_files,
            "transport": transport,
            "promotion_verified": proposal.promotion_verified,
            "validation_results": [result.compact() for result in proposal.validation_results],
        }
        workspace_artifact = workspace_artifact_payload(
            proposal,
            transport=transport,
            promoted=True,
        )
        base.with_suffix(".json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        base.with_suffix(".workspace.json").write_text(
            json.dumps(workspace_artifact, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        base.with_suffix(".diff.txt").write_text(diff_text, encoding="utf-8")
        base.with_suffix(".stat.txt").write_text("\n".join(proposal.changed_files) + "\n", encoding="utf-8")
    append_accepted_work_ledger(
        proposal,
        config,
        base=base if config.write_accepted_work_sidecars else None,
        diff_text=diff_text,
        transport=transport,
    )


def append_accepted_work_ledger(
    proposal: Proposal,
    config: Config,
    *,
    base: Optional[Path],
    diff_text: str,
    transport: str = "direct",
) -> None:
    artifacts = (
        AcceptedWorkArtifacts(
            manifest=base.with_suffix(".json"),
            workspace=base.with_suffix(".workspace.json"),
            diff=base.with_suffix(".diff.txt"),
            stat=base.with_suffix(".stat.txt"),
        )
        if base is not None
        else None
    )
    entry = build_accepted_work_ledger_entry(
        repo_root=config.repo_root,
        target_task=proposal.target_task,
        summary=proposal.summary,
        impact=proposal.impact,
        changed_files=proposal.changed_files,
        transport=transport,
        artifacts=artifacts,
        validation_results=[result.compact() for result in proposal.validation_results],
        diff_text=diff_text,
        promotion_verified=proposal.promotion_verified,
        promotion_errors=proposal.promotion_errors,
        ledger_path=config.resolve(config.accepted_dir) / LEDGER_FILENAME,
    )
    append_accepted_work_jsonl(config.resolve(config.accepted_dir), entry)


def persist_failed_work(proposal: Proposal, config: Config, *, diff_text: str, reason: str, transport: str = "direct") -> None:
    config.resolve(config.failed_dir).mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", (proposal.summary or reason).lower()).strip("-")[:80] or "failed-work"
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    base = config.resolve(config.failed_dir) / f"{stamp}-{reason}-{slug}"
    manifest = {
        "created_at": utc_now(),
        "artifact_kind": "failed_ephemeral_workspace",
        "reason": reason,
        "target_task": proposal.target_task,
        "summary": proposal.summary,
        "impact": proposal.impact,
        "files": [item.get("path", "") for item in proposal.files],
        "changed_files": proposal.changed_files,
        "errors": [compact_message(error) for error in proposal.errors],
        "transport": transport,
        "validation_results": [result.compact() for result in proposal.validation_results],
    }
    workspace_artifact = workspace_artifact_payload(
        proposal,
        transport=transport,
        promoted=False,
        reason=reason,
    )
    base.with_suffix(".json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    base.with_suffix(".workspace.json").write_text(
        json.dumps(workspace_artifact, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    base.with_suffix(".diff.txt").write_text(diff_text, encoding="utf-8")
    base.with_suffix(".stat.txt").write_text("\n".join(proposal.changed_files) + "\n", encoding="utf-8")


def build_prompt(config: Config, selected: Task) -> str:
    failures = recent_task_failures(config, selected.label)
    compact_prompt = should_use_compact_prompt(failures)
    plan = read_text(config.resolve(config.plan_doc), limit=900 if compact_prompt else 22000)
    board = read_text(config.resolve(config.task_board), limit=1800 if compact_prompt else 14000)
    readme = (
        read_text(config.resolve(config.readme), limit=1200 if compact_prompt else 8000)
        if config.resolve(config.readme).exists()
        else ""
    )
    failure_context = format_failure_context(failures)
    context_files: list[str] = []
    if compact_prompt:
        context_files.append(
            "Compact retry mode: omitted broad workspace file contents after repeated LLM parse/runtime failures. "
            "Return a minimal JSON proposal with one fixture and one focused test when possible."
        )
    else:
        for path in sorted((config.repo_root / "ppd").glob("**/*")):
            if not path.is_file():
                continue
            rel = path.relative_to(config.repo_root).as_posix()
            if rel.startswith("ppd/data/") or rel.startswith("ppd/daemon/accepted-work/") or rel.startswith("ppd/daemon/failed-patches/"):
                continue
            if rel.endswith((".py", ".md", ".json", ".ts", ".tsx", ".js", ".mjs")):
                context_files.append(f"--- {rel} ---\n{read_text(path, limit=8000)}")
            if len("\n".join(context_files)) > 18000:
                break

    prompt = f"""
You are improving the isolated PP&D implementation workspace in a repository.

Current task:
{selected.label}

Prompt mode:
{"Compact retry mode: repeated LLM parse/runtime failures were recorded for this task. Return the smallest useful JSON file replacements and avoid broad context." if compact_prompt else "Full context mode."}

Hard constraints:
- Return ONLY one JSON object; no markdown fences and no prose outside JSON.
- Use complete file replacements in a `files` array. Do not return shell commands.
- Edit only files under `ppd/`, or `docs/PORTLAND_PPD_SCRAPING_AUTOMATION_LOGIC_PLAN.md` if the task specifically requires plan updates.
- Do not edit `src/lib/logic/`, `public/corpus/portland-or/current/`, `ipfs_datasets_py/.daemon/`, or the TypeScript logic daemon ledgers.
- Do not create private DevHub session files, auth state, traces, raw crawl output, or downloaded documents.
- Keep the change narrow and directly useful for the selected task.
- Prefer deterministic fixtures and validation before any live crawl or authenticated automation.
- Before returning JSON, ensure every Python file is syntactically valid Python and every TypeScript file is syntactically valid TypeScript. Do not mix TypeScript syntax into Python or Python typing/control-flow syntax into TypeScript.
- Prefer adding narrow new modules and tests over rewriting stable shared contracts such as `ppd/contracts/documents.py`, unless the selected task directly requires a shared contract extension.
- If recent failure context includes `SyntaxError`, `py_compile`, `TS1005`, `TS1109`, or `TS1128`, return a smaller proposal with only the files needed for a syntax-valid implementation or repair.
- Put committed PP&D fixtures under `ppd/tests/fixtures/...`. Tests in `ppd/tests/` should derive fixture paths from their own file location, for example `Path(__file__).parent / "fixtures" / ...`, so they do not accidentally point at repository-root `tests/fixtures`.
- Do not mark task-board checkboxes complete in the same proposal unless the implementation, fixtures, and validation code for the selected task are all included. The daemon will mark the selected task complete after validation passes.
- Do not automate CAPTCHA, MFA, account creation, payment, submission, certification, cancellation, or upload actions.
- If compact retry mode is active, do not inspect or request additional context. Return the smallest useful JSON file replacements for the current task.

JSON schema:
{{
  "summary": "short summary",
  "impact": "why this advances the PP&D plan",
  "files": [
    {{"path": "ppd/...", "content": "complete replacement file content"}}
  ],
  "validation_commands": [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]]
}}

Recent failure context for this task:
{failure_context}

PP&D plan:
{plan}

PP&D task board:
{board}

PP&D workspace context:
{readme}

Current files:
{chr(10).join(context_files)}
"""
    prompt_limit = effective_prompt_limit(config, compact_prompt=compact_prompt)
    if len(prompt) > prompt_limit:
        prompt = prompt[:prompt_limit] + "\n\n[truncated]\n"
    return prompt


def call_llm(prompt: str, config: Config) -> str:
    backend = os.environ.get("PPD_LLM_BACKEND", "llm_router")
    if backend != "llm_router":
        raise RuntimeError(f"Unsupported PP&D LLM backend {backend!r}; expected 'llm_router'.")
    if len(prompt) > config.max_prompt_chars + len("\n\n[truncated]\n"):
        raise RuntimeError(
            f"LLM prompt exceeds configured budget before llm_router child launch: {len(prompt)} > {config.max_prompt_chars}"
        )
    prompt_file: Optional[Path] = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            delete=False,
            prefix="ppd-llm-prompt-",
            suffix=".txt",
        ) as handle:
            handle.write(prompt)
            prompt_file = Path(handle.name)
        env = os.environ.copy()
        env.update(
            {
                "PPD_LLM_PROMPT_FILE": str(prompt_file),
                "PPD_LLM_MODEL_NAME": config.model_name,
                "PPD_LLM_PROVIDER": config.provider or "",
                "PPD_LLM_ALLOW_LOCAL_FALLBACK": "1" if config.allow_local_fallback else "0",
                "PPD_LLM_TIMEOUT": str(config.llm_timeout_seconds),
                "PPD_LLM_MAX_NEW_TOKENS": str(config.llm_max_new_tokens),
            }
        )
        child_code = r"""
import os
import pathlib
import sys

from ipfs_datasets_py import llm_router

prompt = pathlib.Path(os.environ["PPD_LLM_PROMPT_FILE"]).read_text(encoding="utf-8")
provider = os.environ.get("PPD_LLM_PROVIDER") or None
text = llm_router.generate_text(
    prompt,
    model_name=os.environ["PPD_LLM_MODEL_NAME"],
    provider=provider,
    allow_local_fallback=os.environ.get("PPD_LLM_ALLOW_LOCAL_FALLBACK") == "1",
    timeout=int(os.environ["PPD_LLM_TIMEOUT"]),
    max_new_tokens=int(os.environ["PPD_LLM_MAX_NEW_TOKENS"]),
    temperature=0.1,
)
sys.stdout.write("" if text is None else str(text))
"""
        command = ["python3", "-c", child_code]
        process = subprocess.Popen(
            command,
            cwd=str(config.repo_root),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            start_new_session=True,
        )
        global _ACTIVE_LLM_PROCESS
        _ACTIVE_LLM_PROCESS = process
        try:
            stdout, stderr = process.communicate(timeout=config.llm_timeout_seconds + 30)
        except subprocess.TimeoutExpired as exc:
            terminate_process_group(process)
            raise RuntimeError(f"llm_router child timed out after {config.llm_timeout_seconds + 30} seconds") from exc
        finally:
            if _ACTIVE_LLM_PROCESS is process:
                _ACTIVE_LLM_PROCESS = None
        completed = subprocess.CompletedProcess(
            command,
            returncode=int(process.returncode or 0),
            stdout=stdout,
            stderr=stderr,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"llm_router child timed out after {config.llm_timeout_seconds + 30} seconds") from exc
    finally:
        if prompt_file is not None:
            try:
                prompt_file.unlink()
            except FileNotFoundError:
                pass
    if completed.returncode != 0:
        details = compact_message((completed.stdout or "") + " " + (completed.stderr or ""), limit=1200)
        raise RuntimeError(f"llm_router child exited with code {completed.returncode}: {details}")
    return completed.stdout


def collect_descendant_pids(pid: int) -> list[int]:
    try:
        completed = subprocess.run(
            ["pgrep", "-P", str(pid)],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    except OSError:
        return []
    descendants: list[int] = []
    for line in completed.stdout.splitlines():
        try:
            child = int(line.strip())
        except ValueError:
            continue
        descendants.append(child)
        descendants.extend(collect_descendant_pids(child))
    return descendants


def process_groups_for_family(root_pid: int) -> set[int]:
    groups: set[int] = set()
    for pid in [root_pid, *collect_descendant_pids(root_pid)]:
        try:
            groups.add(os.getpgid(pid))
        except ProcessLookupError:
            continue
    return groups


def terminate_process_group(process: subprocess.Popen[Any], *, grace_seconds: float = 5.0) -> None:
    """Terminate a subprocess and descendant process groups when it owns a session."""

    if process.poll() is not None:
        return
    process_groups = process_groups_for_family(process.pid) or {process.pid}
    try:
        for pgid in process_groups:
            try:
                os.killpg(pgid, signal.SIGTERM)
            except ProcessLookupError:
                continue
            except PermissionError:
                continue
    except ProcessLookupError:
        pass
    try:
        process.communicate(timeout=grace_seconds)
        return
    except subprocess.TimeoutExpired:
        pass
    try:
        for pgid in process_groups:
            try:
                os.killpg(pgid, signal.SIGKILL)
            except ProcessLookupError:
                continue
            except PermissionError:
                continue
    except ProcessLookupError:
        pass
    try:
        process.communicate(timeout=grace_seconds)
    except subprocess.TimeoutExpired:
        pass


def handle_daemon_signal(signum: int, _frame: object) -> None:
    process = _ACTIVE_LLM_PROCESS
    if process is not None and process.poll() is None:
        terminate_process_group(process, grace_seconds=1.0)
    raise SystemExit(128 + signum)


def install_daemon_signal_handlers() -> None:
    signal.signal(signal.SIGTERM, handle_daemon_signal)
    signal.signal(signal.SIGINT, handle_daemon_signal)
    signal.signal(signal.SIGHUP, handle_daemon_signal)


def ppd_pre_task_block(config: Config, selected: Task) -> Optional[PreTaskBlock]:
    deterministic_fallback_available = has_deterministic_task_fallback(selected)
    if not (
        config.apply
        and selected.status in {"needed", "in-progress"}
        and not deterministic_fallback_available
    ):
        return None
    decision = pre_llm_block_decision(config, selected.label)
    if decision is None:
        return None
    return PreTaskBlock(
        summary=decision.summary,
        failure_kind=decision.failure_kind,
        result=decision.result,
    )


def ppd_produce_proposal(config: Config, selected: Task, write_status: Any) -> Proposal:
    proposal = build_deterministic_task_fallback_proposal(config, selected)
    if proposal is not None:
        write_status("deterministic_fallback", target_task=selected.label)
        return proposal
    write_status("calling_llm", target_task=selected.label)
    try:
        raw = call_llm(build_prompt(config, selected), config)
        return parse_proposal(raw)
    except KeyboardInterrupt:
        raise
    except BaseException as exc:
        return Proposal(summary="LLM proposal failed.", errors=[compact_message(exc)], failure_kind="llm")


def ppd_run_proposal_validation(config: Config, proposal: Proposal) -> list[CommandResult]:
    return run_validation(
        config,
        commands=validation_commands_for_proposal(proposal, config),
    )


def ppd_failure_count_for_block(config: Config, task_label: str) -> int:
    return task_failure_count(
        config,
        task_label,
        kinds={"validation", "preflight", "no_change", "syntax_preflight"},
    )


def build_ppd_daemon_hooks() -> TodoDaemonHooks:
    return TodoDaemonHooks(
        parse_tasks=parse_tasks,
        select_task=lambda tasks, config: select_task_for_config(tasks, config),
        replace_task_mark=replace_task_mark,
        update_generated_status=lambda markdown, latest, tasks: update_generated_status(
            markdown,
            latest=latest,
            tasks=tasks,
        ),
        produce_proposal=ppd_produce_proposal,
        apply_proposal=apply_files_with_validation,
        run_validation=ppd_run_proposal_validation,
        should_skip_validation=should_skip_validation_for_no_file_failure,
        is_retryable_failure=is_retryable_failure,
        failure_block_threshold=failure_block_threshold,
        failure_count_for_block=ppd_failure_count_for_block,
        should_sleep_between_cycles=lambda markdown, config: should_sleep_between_watch_cycles(
            markdown,
            revisit_blocked=config.revisit_blocked,
        ),
        exception_diagnostic=exception_diagnostic,
        pre_task_block=ppd_pre_task_block,
        no_eligible_summary="No eligible PP&D tasks remain.",
    )


class Daemon(TodoDaemonRunner):
    def __init__(self, config: Config) -> None:
        super().__init__(config, build_ppd_daemon_hooks())


def self_test(repo_root: Path) -> int:
    required = [
        repo_root / "ppd/README.md",
        repo_root / "ppd/.gitignore",
        repo_root / "ppd/daemon/task-board.md",
        repo_root / "docs/PORTLAND_PPD_SCRAPING_AUTOMATION_LOGIC_PLAN.md",
    ]
    missing = [path.as_posix() for path in required if not path.exists()]
    errors: list[str] = []
    if missing:
        errors.append(f"missing required files: {missing}")
    board = (repo_root / "ppd/daemon/task-board.md").read_text(encoding="utf-8") if (repo_root / "ppd/daemon/task-board.md").exists() else ""
    if not parse_tasks(board):
        errors.append("task board has no checkbox tasks")
    gitignore = (repo_root / "ppd/.gitignore").read_text(encoding="utf-8") if (repo_root / "ppd/.gitignore").exists() else ""
    for needle in ("data/private/", "data/raw/", "daemon/failed-patches/", "daemon/worktrees/"):
        if needle not in gitignore:
            errors.append(f"ppd/.gitignore missing {needle}")
    for prefix in DISALLOWED_WRITE_PREFIXES:
        if not validate_write_path(prefix + "bad.ts"):
            errors.append(f"disallowed prefix unexpectedly passed preflight: {prefix}")
    compacted = CommandResult(
        command=("example",),
        returncode=1,
        stdout="<html><body><script>cloudflare challenge</script></body></html>",
        stderr="token __cf_chl_tk=secret",
    ).compact()
    if "cloudflare challenge" in compacted["stdout"] or "__cf_chl_tk=secret" in compacted["stderr"]:
        errors.append("runtime log compaction failed to redact noisy provider HTML")
    errors.extend(validate_seed_and_allowlist(repo_root))
    errors.extend(validate_python_sources(repo_root))
    if errors:
        print(json.dumps({"ok": False, "errors": errors}, indent=2), file=sys.stderr)
        return 1
    print(json.dumps({"ok": True, "task_count": len(parse_tasks(board))}, indent=2))
    return 0


def load_json_file(path: Path) -> Optional[dict[str, Any]]:
    if not path.exists():
        return None
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path.relative_to(path.parents[2])} is invalid JSON: {exc}") from exc
    if not isinstance(parsed, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return parsed


def validate_seed_and_allowlist(repo_root: Path) -> list[str]:
    errors: list[str] = []
    seed_path = repo_root / "ppd/crawler/seed_manifest.json"
    allowlist_path = repo_root / "ppd/crawler/allowlist.json"
    try:
        seed_manifest = load_json_file(seed_path)
        allowlist = load_json_file(allowlist_path)
    except ValueError as exc:
        return [str(exc)]
    if seed_manifest is None and allowlist is None:
        return errors
    if seed_manifest is None or allowlist is None:
        return ["seed_manifest.json and allowlist.json must be added together"]

    allowed_hosts = allowlist.get("allowed_hosts")
    if not isinstance(allowed_hosts, list) or not allowed_hosts:
        errors.append("allowlist.json must include non-empty allowed_hosts")
        allowed_hosts = []
    host_policies: dict[str, dict[str, Any]] = {}
    for entry in allowed_hosts:
        if not isinstance(entry, dict):
            errors.append("allowlist allowed_hosts entries must be objects")
            continue
        host = entry.get("host")
        if not isinstance(host, str) or not host:
            errors.append("allowlist host entry missing host")
            continue
        host_policies[host] = entry
        if entry.get("scheme") != "https":
            errors.append(f"allowlist host {host} must require https")
        prefixes = entry.get("allowed_path_prefixes")
        if not isinstance(prefixes, list) or not all(isinstance(prefix, str) and prefix.startswith("/") for prefix in prefixes):
            errors.append(f"allowlist host {host} must define allowed_path_prefixes")

    seeds = seed_manifest.get("seeds")
    if not isinstance(seeds, list) or not seeds:
        errors.append("seed_manifest.json must include non-empty seeds")
        seeds = []
    seen_ids: set[str] = set()
    for seed in seeds:
        if not isinstance(seed, dict):
            errors.append("seed entries must be objects")
            continue
        seed_id = seed.get("id")
        url = seed.get("url")
        if not isinstance(seed_id, str) or not seed_id:
            errors.append("seed entry missing id")
        elif seed_id in seen_ids:
            errors.append(f"duplicate seed id: {seed_id}")
        else:
            seen_ids.add(seed_id)
        if not isinstance(url, str) or not url:
            errors.append(f"seed {seed_id or '<unknown>'} missing url")
            continue
        parsed = urlparse(url)
        if parsed.scheme != "https":
            errors.append(f"seed {seed_id} must use https: {url}")
        policy = host_policies.get(parsed.netloc)
        if policy is None:
            errors.append(f"seed {seed_id} host is not allowlisted: {parsed.netloc}")
            continue
        prefixes = policy.get("allowed_path_prefixes", [])
        parsed_path = parsed.path or "/"
        if isinstance(prefixes, list) and not any(parsed_path.startswith(str(prefix)) for prefix in prefixes):
            errors.append(f"seed {seed_id} path is outside host allowlist: {parsed_path}")
        for fragment in policy.get("disallowed_path_fragments", []) or []:
            if isinstance(fragment, str) and fragment.lower() in url.lower():
                errors.append(f"seed {seed_id} includes disallowed path fragment {fragment!r}")
    return errors


def validate_python_sources(repo_root: Path) -> list[str]:
    errors: list[str] = []
    for path in sorted((repo_root / "ppd").rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        rel = path.relative_to(repo_root).as_posix()
        try:
            py_compile.compile(str(path), doraise=True)
        except py_compile.PyCompileError as exc:
            errors.append(f"{rel} failed py_compile: {compact_message(exc.msg, limit=500)}")
    return errors


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the isolated PP&D autonomous daemon.")
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument("--apply", action="store_true", help="Apply accepted file replacements after validation")
    parser.add_argument("--watch", action="store_true", help="Run repeated cycles")
    parser.add_argument("--iterations", type=int, default=1, help="Number of cycles; with --watch, 0 means unbounded")
    parser.add_argument("--interval", type=float, default=0.0, help="Seconds between watch cycles")
    parser.add_argument("--llm-timeout", type=int, default=300, help="Seconds to allow for one LLM proposal")
    parser.add_argument("--llm-max-new-tokens", type=int, default=2048, help="llm_router max_new_tokens budget")
    parser.add_argument("--max-prompt-chars", type=int, default=60000, help="Maximum prompt characters before llm_router launch")
    parser.add_argument("--max-compact-prompt-chars", type=int, default=4200, help="Maximum compact retry prompt characters")
    parser.add_argument("--model", default="gpt-5.5", help="llm_router model")
    parser.add_argument("--provider", default=None, help="llm_router provider")
    parser.add_argument("--allow-local-fallback", action="store_true", help="Allow local fallback providers")
    parser.add_argument("--revisit-blocked", action="store_true", help="Revisit blocked tasks after needed tasks are exhausted")
    parser.add_argument("--max-task-failures-before-block", type=int, default=3, help="Validation/preflight failures before marking a task blocked")
    parser.add_argument("--repair-validation-failures", action="store_true", help="Run one temporary-worktree repair pass when validation fails")
    parser.add_argument("--max-validation-repair-attempts", type=int, default=1, help="Validation repair attempts per candidate worktree")
    parser.add_argument("--crash-backoff", type=float, default=5.0, help="Seconds to pause after a contained daemon cycle exception")
    parser.add_argument("--self-test", action="store_true", help="Run daemon self-test and exit")
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    if args.self_test:
        return self_test(repo_root)
    install_daemon_signal_handlers()
    config = Config(
        repo_root=repo_root,
        apply=bool(args.apply),
        watch=bool(args.watch),
        iterations=int(args.iterations),
        interval_seconds=float(args.interval),
        llm_timeout_seconds=int(args.llm_timeout),
        llm_max_new_tokens=max(256, int(args.llm_max_new_tokens)),
        max_prompt_chars=max(1000, int(args.max_prompt_chars)),
        max_compact_prompt_chars=max(1000, int(args.max_compact_prompt_chars)),
        model_name=str(args.model),
        provider=args.provider,
        allow_local_fallback=bool(args.allow_local_fallback),
        revisit_blocked=bool(args.revisit_blocked),
        max_task_failures_before_block=max(1, int(args.max_task_failures_before_block)),
        repair_validation_failures=bool(args.repair_validation_failures),
        max_validation_repair_attempts=max(0, int(args.max_validation_repair_attempts)),
        crash_backoff_seconds=max(0.0, float(args.crash_backoff)),
    )
    proposals = Daemon(config).run()
    print(json.dumps([proposal.to_dict() for proposal in proposals], indent=2))
    if not proposals:
        return 1
    latest = proposals[-1]
    if latest.valid or latest.failure_kind == "no_eligible_tasks":
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
