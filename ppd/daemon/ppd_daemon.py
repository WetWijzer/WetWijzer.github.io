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
import difflib
import json
import os
import py_compile
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
import traceback
import uuid
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, Iterator, Optional
from urllib.parse import urlparse

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ppd.daemon.accepted_work_ledger import (
    AcceptedWorkArtifacts,
    append_accepted_work_ledger as append_accepted_work_jsonl,
    build_accepted_work_ledger_entry,
)
from ppd.daemon.syntax_preflight import run_apply_flow_syntax_preflight


CHECKBOX_RE = re.compile(r"^(?P<prefix>\s*-\s+\[)(?P<mark>[ xX~!])(?P<suffix>\]\s+)(?P<title>.+)$")
JSON_BLOCK_RE = re.compile(r"```json\s*([\s\S]*?)\s*```", re.IGNORECASE)
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


@dataclass(frozen=True)
class Task:
    index: int
    title: str
    status: str
    checkbox_id: int

    @property
    def label(self) -> str:
        return f"Task checkbox-{self.checkbox_id}: {self.title}"


@dataclass(frozen=True)
class CommandResult:
    command: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0

    def compact(self, limit: int = 5000) -> dict[str, Any]:
        return {
            "command": list(self.command),
            "returncode": self.returncode,
            "stdout": compact_message(self.stdout, limit=limit),
            "stderr": compact_message(self.stderr, limit=limit),
        }


@dataclass
class Proposal:
    summary: str = ""
    impact: str = ""
    files: list[dict[str, str]] = field(default_factory=list)
    validation_commands: list[list[str]] = field(default_factory=list)
    raw_response: str = ""
    errors: list[str] = field(default_factory=list)
    failure_kind: str = ""
    target_task: str = ""
    changed_files: list[str] = field(default_factory=list)
    validation_results: list[CommandResult] = field(default_factory=list)
    applied: bool = False
    dry_run: bool = True

    @property
    def valid(self) -> bool:
        return self.applied and not self.errors and all(result.ok for result in self.validation_results)

    def to_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "impact": self.impact,
            "target_task": self.target_task,
            "files": [item.get("path", "") for item in self.files],
            "changed_files": self.changed_files,
            "applied": self.applied,
            "dry_run": self.dry_run,
            "validation_passed": bool(self.validation_results) and all(result.ok for result in self.validation_results),
            "validation_results": [result.compact() for result in self.validation_results],
            "errors": [compact_message(error) for error in self.errors],
            "failure_kind": self.failure_kind,
        }


@dataclass
class Config:
    repo_root: Path
    task_board: Path = Path("ppd/daemon/task-board.md")
    plan_doc: Path = Path("docs/PORTLAND_PPD_SCRAPING_AUTOMATION_LOGIC_PLAN.md")
    readme: Path = Path("ppd/README.md")
    status_file: Path = Path("ppd/daemon/status.json")
    progress_file: Path = Path("ppd/daemon/progress.json")
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


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def read_text(path: Path, limit: Optional[int] = None) -> str:
    text = path.read_text(encoding="utf-8")
    if limit is not None and len(text) > limit:
        return text[:limit] + "\n\n[truncated]\n"
    return text


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")


def parse_tasks(markdown: str) -> list[Task]:
    tasks: list[Task] = []
    for line in markdown.splitlines():
        match = CHECKBOX_RE.match(line)
        if not match:
            continue
        mark = match.group("mark")
        raw_title = match.group("title").strip()
        checkbox_id = len(tasks) + 1
        title = raw_title
        id_match = re.match(r"Task checkbox-(?P<id>\d+):\s*(?P<title>.+)$", raw_title)
        if id_match:
            checkbox_id = int(id_match.group("id"))
            title = id_match.group("title").strip()
        status = "needed"
        if mark.lower() == "x":
            status = "complete"
        elif mark == "~":
            status = "in-progress"
        elif mark == "!":
            status = "blocked"
        tasks.append(Task(index=len(tasks) + 1, title=title, status=status, checkbox_id=checkbox_id))
    return tasks


def select_task(tasks: Iterable[Task], *, revisit_blocked: bool = False) -> Optional[Task]:
    task_list = list(tasks)
    for task in task_list:
        if task.status in {"needed", "in-progress"}:
            return task
    if revisit_blocked:
        for task in task_list:
            if task.status == "blocked" and task.checkbox_id not in PROTECTED_BLOCKED_REVISIT_CHECKBOX_IDS:
                return task
    return None


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


def compact_message(value: Any, limit: int = 700) -> str:
    text = str(value or "")
    text = re.sub(
        r"<!doctype html[\s\S]*",
        "[html response omitted]",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(
        r"<(?:html|head|body|script|style|svg|path|div|meta|noscript)\b[\s\S]*",
        "[html response omitted]",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(r"__cf_chl_[A-Za-z0-9_.=-]+", "__cf_chl_[omitted]", text)
    text = re.sub(r"c[A-Z][A-Za-z0-9_]*:\s*'[^']{80,}'", "cloudflare_token: '[omitted]'", text)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > limit:
        return text[:limit].rstrip() + "..."
    return text


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


def extract_json(text: str) -> Optional[dict[str, Any]]:
    match = JSON_BLOCK_RE.search(text)
    candidates = [match.group(1)] if match else []
    stripped = text.strip()
    if stripped.startswith("{") and stripped.endswith("}"):
        candidates.append(stripped)
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start >= 0 and end > start:
        candidates.append(stripped[start : end + 1])
    for candidate in candidates:
        try:
            parsed = json.loads(candidate)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            continue
    return None


def parse_proposal(text: str) -> Proposal:
    parsed = extract_json(text)
    if parsed is None:
        return Proposal(raw_response=text, errors=["LLM response did not contain a JSON object."], failure_kind="parse")
    files: list[dict[str, str]] = []
    raw_files = parsed.get("files", [])
    if isinstance(raw_files, list):
        for item in raw_files:
            if not isinstance(item, dict):
                continue
            path = item.get("path")
            content = item.get("content")
            if isinstance(path, str) and isinstance(content, str):
                files.append({"path": path, "content": content})
    commands: list[list[str]] = []
    raw_commands = parsed.get("validation_commands", [])
    if isinstance(raw_commands, list):
        for command in raw_commands:
            if isinstance(command, list) and all(isinstance(part, str) for part in command):
                commands.append(command)
    return Proposal(
        summary=str(parsed.get("summary", "")),
        impact=str(parsed.get("impact", "")),
        files=files,
        validation_commands=commands,
        raw_response=text,
    )


def normalized_relative_path(path: str) -> str:
    candidate = Path(path)
    if candidate.is_absolute():
        raise ValueError(f"absolute paths are not allowed: {path}")
    normalized = candidate.as_posix()
    if normalized.startswith("../") or "/../" in normalized or normalized == "..":
        raise ValueError(f"path traversal is not allowed: {path}")
    return normalized


def validate_write_path(path: str) -> list[str]:
    errors: list[str] = []
    try:
        normalized = normalized_relative_path(path)
    except ValueError as exc:
        return [str(exc)]
    if any(normalized.startswith(prefix) for prefix in DISALLOWED_WRITE_PREFIXES):
        errors.append(f"disallowed PP&D daemon write target: {normalized}")
    if not any(normalized.startswith(prefix) or normalized == prefix.rstrip("/") for prefix in ALLOWED_WRITE_PREFIXES):
        errors.append(f"write target is outside PP&D allowlist: {normalized}")
    if is_private_write_path(normalized):
        errors.append(f"private/session artifacts may not be generated by daemon proposals: {normalized}")
    return errors


def is_private_write_path(normalized: str) -> bool:
    lowered = normalized.lower()
    if any(fragment in lowered for fragment in PRIVATE_WRITE_PATH_FRAGMENTS):
        return True
    tokens = [token for token in re.split(r"[/._-]+", lowered) if token]
    return any(token in PRIVATE_WRITE_PATH_TOKENS for token in tokens)


def run_command(command: tuple[str, ...], *, cwd: Path, timeout: int) -> CommandResult:
    completed = subprocess.run(
        list(command),
        cwd=str(cwd),
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )
    return CommandResult(command=command, returncode=completed.returncode, stdout=completed.stdout, stderr=completed.stderr)


def run_validation(config: Config) -> list[CommandResult]:
    return [
        run_command(command, cwd=config.repo_root, timeout=config.command_timeout_seconds)
        for command in config.validation_commands
    ]


def diff_for_file(path: str, before: str, after: str) -> str:
    return "".join(
        difflib.unified_diff(
            before.splitlines(keepends=True),
            after.splitlines(keepends=True),
            fromfile=f"a/{path}",
            tofile=f"b/{path}",
        )
    )


def worktree_marker_payload(*, state: str, source_root: Path) -> dict[str, Any]:
    return {
        "created_at": utc_now(),
        "schema_version": 1,
        "source_root": source_root.as_posix(),
        "state": state,
        "transport": "ephemeral_worktree",
    }


def cleanup_stale_validation_worktrees(config: Config, *, max_age_seconds: Optional[int] = None) -> list[str]:
    """Remove old PP&D validation worktrees left by interrupted daemon runs."""

    root = config.resolve(config.worktree_dir)
    if not root.exists():
        return []
    cutoff = time.time() - float(config.worktree_stale_seconds if max_age_seconds is None else max_age_seconds)
    removed: list[str] = []
    for child in root.iterdir():
        marker = child / "ppd-worktree.json"
        if not child.is_dir() or not marker.exists():
            continue
        try:
            if child.stat().st_mtime > cutoff:
                continue
            shutil.rmtree(child)
            removed.append(child.name)
        except FileNotFoundError:
            continue
    return removed


def _copy_if_exists(source: Path, destination: Path, *, ignore: Optional[Callable[[str, list[str]], set[str]]] = None) -> None:
    if not source.exists():
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.is_dir():
        shutil.copytree(source, destination, symlinks=True, dirs_exist_ok=True, ignore=ignore)
    else:
        shutil.copy2(source, destination)


def _link_or_copy_if_exists(source: Path, destination: Path) -> None:
    if not source.exists():
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        destination.symlink_to(source.resolve(), target_is_directory=source.is_dir())
    except OSError:
        _copy_if_exists(source, destination)


def _copy_validation_external_references(config: Config, worktree: Path) -> None:
    """Expose read-only external metadata needed by PP&D validation tests."""

    processor_metadata = Path("ipfs_datasets_py/ipfs_datasets_py/processors")
    _link_or_copy_if_exists(
        config.repo_root / processor_metadata,
        worktree / processor_metadata,
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

    cleanup_stale_validation_worktrees(config)
    root = config.resolve(config.worktree_dir)
    root.mkdir(parents=True, exist_ok=True)
    worktree = root / f"cycle-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')}-{uuid.uuid4().hex[:8]}"
    worktree.mkdir(parents=True)
    marker = worktree / "ppd-worktree.json"
    marker.write_text(
        json.dumps(worktree_marker_payload(state="initializing", source_root=config.repo_root), indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    try:
        _copy_if_exists(config.repo_root / "ppd", worktree / "ppd", ignore=_ignore_validation_tree_entries)
        docs_plan = config.resolve(config.plan_doc)
        if docs_plan.exists():
            _copy_if_exists(docs_plan, worktree / config.plan_doc)
        for root_file in ("package.json", "package-lock.json", "tsconfig.json"):
            _copy_if_exists(config.repo_root / root_file, worktree / root_file)
        _copy_validation_external_references(config, worktree)
        marker.write_text(
            json.dumps(worktree_marker_payload(state="ready", source_root=config.repo_root), indent=2, sort_keys=True)
            + "\n",
            encoding="utf-8",
        )
        yield worktree
    finally:
        try:
            shutil.rmtree(worktree)
        except FileNotFoundError:
            pass


def worktree_config(config: Config, worktree: Path) -> Config:
    return replace(
        config,
        repo_root=worktree,
        repair_validation_failures=False,
        validation_repair_callback=None,
    )


def proposal_diff_from_worktree(config: Config, worktree: Path, changed: Iterable[str]) -> str:
    parts: list[str] = []
    for rel in changed:
        source = config.resolve(Path(rel))
        candidate = worktree / rel
        before = source.read_text(encoding="utf-8") if source.exists() else ""
        after = candidate.read_text(encoding="utf-8") if candidate.exists() else ""
        parts.append(diff_for_file(rel, before, after))
    return "".join(parts)


def workspace_artifact_payload(
    proposal: Proposal,
    *,
    transport: str,
    promoted: bool,
    reason: str = "",
) -> dict[str, Any]:
    return {
        "artifact_kind": "ephemeral-workspace",
        "schema_version": 1,
        "created_at": utc_now(),
        "transport": transport,
        "promoted_to_main_worktree": promoted,
        "reason": reason,
        "target_task": proposal.target_task,
        "summary": proposal.summary,
        "changed_files": list(proposal.changed_files),
        "validation_passed": bool(proposal.validation_results)
        and all(result.ok for result in proposal.validation_results),
        "validation_commands": [list(result.command) for result in proposal.validation_results],
    }


def materialize_proposal_in_worktree(proposal: Proposal, config: Config, worktree: Path) -> list[str]:
    changed: list[str] = []
    seen: set[str] = set()
    for item in proposal.files:
        rel = normalized_relative_path(item["path"])
        target = worktree / rel
        before = target.read_text(encoding="utf-8") if target.exists() else None
        after = item["content"]
        if before == after:
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(after, encoding="utf-8")
        if rel not in seen:
            seen.add(rel)
            changed.append(rel)
    return changed


def proposal_files_from_worktree(worktree: Path, changed: Iterable[str]) -> list[dict[str, str]]:
    files: list[dict[str, str]] = []
    for rel in changed:
        target = worktree / rel
        if target.exists():
            files.append({"path": rel, "content": target.read_text(encoding="utf-8")})
    return files


def promote_worktree_files(config: Config, worktree: Path, changed: Iterable[str]) -> None:
    for rel in changed:
        source = worktree / rel
        target = config.resolve(Path(rel))
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")


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

    proposal.validation_results = run_validation(worktree_config(config, worktree))
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
            proposal.validation_results = run_validation(worktree_config(config, worktree))
            persist_failed_work(proposal, config, diff_text="", reason="no_change", transport="ephemeral_worktree")
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

        proposal.validation_results = run_validation(worktree_config(config, worktree))
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
        proposal.applied = True
        persist_accepted_work(proposal, config, diff_text=diff_text, transport="ephemeral_worktree")
    return proposal


def persist_accepted_work(proposal: Proposal, config: Config, *, diff_text: str, transport: str = "direct") -> None:
    config.resolve(config.accepted_dir).mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", proposal.summary.lower()).strip("-")[:80] or "accepted-work"
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    base = config.resolve(config.accepted_dir) / f"{stamp}-{slug}"
    manifest = {
        "created_at": utc_now(),
        "artifact_kind": "accepted_ephemeral_workspace",
        "target_task": proposal.target_task,
        "summary": proposal.summary,
        "impact": proposal.impact,
        "changed_files": proposal.changed_files,
        "transport": transport,
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
    append_accepted_work_ledger(proposal, config, base=base, transport=transport)


def append_accepted_work_ledger(proposal: Proposal, config: Config, *, base: Path, transport: str = "direct") -> None:
    entry = build_accepted_work_ledger_entry(
        repo_root=config.repo_root,
        target_task=proposal.target_task,
        summary=proposal.summary,
        impact=proposal.impact,
        changed_files=proposal.changed_files,
        transport=transport,
        artifacts=AcceptedWorkArtifacts(
            manifest=base.with_suffix(".json"),
            workspace=base.with_suffix(".workspace.json"),
            diff=base.with_suffix(".diff.txt"),
            stat=base.with_suffix(".stat.txt"),
        ),
        validation_results=[result.compact() for result in proposal.validation_results],
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


class Daemon:
    def __init__(self, config: Config) -> None:
        self.config = config
        self._heartbeat_stop = threading.Event()
        self._active_state = "initializing"
        self._active_state_started_at = utc_now()
        self._active_target_task = ""

    def write_status(self, state: str, **extra: Any) -> None:
        if state != "heartbeat":
            target_task = str(extra.get("target_task") or self._active_target_task)
            if state != self._active_state or target_task != self._active_target_task:
                self._active_state_started_at = utc_now()
            self._active_state = state
            self._active_target_task = target_task
        payload = {
            "updated_at": utc_now(),
            "pid": os.getpid(),
            "state": state,
            "active_state": self._active_state,
            "active_state_started_at": self._active_state_started_at,
            "active_target_task": self._active_target_task,
            **extra,
        }
        atomic_write_json(self.config.resolve(self.config.status_file), payload)

    def heartbeat(self) -> None:
        while not self._heartbeat_stop.wait(self.config.heartbeat_seconds):
            self.write_status("heartbeat", active_state=self._active_state)

    def run_cycle(self) -> Proposal:
        board_path = self.config.resolve(self.config.task_board)
        board = read_text(board_path)
        tasks = parse_tasks(board)
        selected = select_task_for_config(tasks, self.config)
        if selected is None:
            proposal = Proposal(summary="No eligible PP&D tasks remain.", failure_kind="no_eligible_tasks")
            proposal.dry_run = not self.config.apply
            self.write_status("no_eligible_tasks")
            self.write_progress([proposal])
            self.write_cycle_diagnostic(proposal, stage="no_eligible_tasks")
            return proposal

        self.write_status("selected_task", target_task=selected.label)
        pre_llm_block = (
            pre_llm_block_decision(self.config, selected.label)
            if self.config.apply and selected.status in {"needed", "in-progress"}
            else None
        )
        if (
            self.config.apply
            and selected.status in {"needed", "in-progress"}
            and pre_llm_block is not None
        ):
            proposal = Proposal(
                summary=pre_llm_block.summary,
                failure_kind=pre_llm_block.failure_kind,
                target_task=selected.label,
            )
            proposal.dry_run = False
            board = replace_task_mark(board, selected, "!")
            tasks_after = parse_tasks(board)
            board = update_generated_status(
                board,
                latest={
                    "target_task": selected.label,
                    "result": pre_llm_block.result,
                    "summary": proposal.summary,
                },
                tasks=tasks_after,
            )
            board_path.write_text(board, encoding="utf-8")
            self.write_progress([proposal])
            append_jsonl(self.config.resolve(self.config.result_log), {"created_at": utc_now(), "proposal": proposal.to_dict()})
            self.write_status("cycle_completed", valid=False, artifact=proposal.to_dict())
            return proposal
        if selected.status == "needed" and self.config.apply:
            board = replace_task_mark(board, selected, "~")
            board_path.write_text(board, encoding="utf-8")

        self.write_status("calling_llm", target_task=selected.label)
        try:
            raw = call_llm(build_prompt(self.config, selected), self.config)
            proposal = parse_proposal(raw)
        except KeyboardInterrupt:
            raise
        except BaseException as exc:
            proposal = Proposal(summary="LLM proposal failed.", errors=[compact_message(exc)], failure_kind="llm")
        proposal.target_task = selected.label
        proposal.dry_run = not self.config.apply
        if proposal.failure_kind in {"parse", "llm"} or not proposal.files:
            self.write_progress([proposal])
            self.write_cycle_diagnostic(proposal, stage="before_validation")

        if self.config.apply and proposal.files:
            self.write_status("applying_files", target_task=selected.label)
            proposal = apply_files_with_validation(proposal, self.config)
        elif should_skip_validation_for_no_file_failure(proposal):
            proposal.validation_results = []
        else:
            proposal.validation_results = run_validation(self.config)

        board = read_text(board_path)
        if self.config.apply:
            if proposal.valid:
                board = replace_task_mark(board, selected, "x")
            elif selected.status in {"needed", "in-progress"} and not is_retryable_failure(proposal):
                prior_failures = task_failure_count(
                    self.config,
                    selected.label,
                    kinds={"validation", "preflight", "no_change", "syntax_preflight"},
                )
                mark = "!" if prior_failures + 1 >= failure_block_threshold(proposal, self.config) else " "
                board = replace_task_mark(board, selected, mark)
            elif selected.status in {"needed", "in-progress"}:
                board = replace_task_mark(board, selected, " ")
        tasks_after = parse_tasks(board)
        board = update_generated_status(
            board,
            latest={
                "target_task": selected.label,
                "result": "accepted" if proposal.valid else proposal.failure_kind or "not_applied",
                "summary": proposal.summary,
            },
            tasks=tasks_after,
        )
        board_path.write_text(board, encoding="utf-8")
        self.write_progress([proposal])
        append_jsonl(self.config.resolve(self.config.result_log), {"created_at": utc_now(), "proposal": proposal.to_dict()})
        self.write_status("cycle_completed", valid=proposal.valid, artifact=proposal.to_dict())
        return proposal

    def write_cycle_diagnostic(self, proposal: Proposal, *, stage: str) -> None:
        append_jsonl(
            self.config.resolve(self.config.result_log),
            {
                "created_at": utc_now(),
                "stage": stage,
                "diagnostic": proposal.to_dict(),
            },
        )

    def record_cycle_exception(self, exc: BaseException, *, consecutive_exceptions: int) -> Proposal:
        proposal = Proposal(
            summary="Daemon cycle crashed before completion.",
            impact=(
                "The exception was captured as a durable diagnostic so watch mode can continue "
                "and the supervisor can inspect the failure history."
            ),
            errors=[exception_diagnostic(exc)],
            failure_kind="daemon_exception",
            target_task=self._active_target_task,
        )
        proposal.dry_run = not self.config.apply
        proposal.applied = False
        artifact = proposal.to_dict()
        try:
            self.write_progress([proposal])
        except Exception as progress_exc:
            artifact["progress_error"] = exception_diagnostic(progress_exc, limit=1200)
        try:
            self.write_cycle_diagnostic(proposal, stage="cycle_exception")
        except Exception:
            pass
        try:
            self.write_status(
                "cycle_exception",
                valid=False,
                consecutive_exceptions=consecutive_exceptions,
                artifact=artifact,
            )
        except Exception:
            pass
        return proposal

    def write_progress(self, proposals: list[Proposal]) -> None:
        board = read_text(self.config.resolve(self.config.task_board))
        tasks = parse_tasks(board)
        payload = {
            "updated_at": utc_now(),
            "task_counts": {
                "needed": sum(1 for task in tasks if task.status == "needed"),
                "in_progress": sum(1 for task in tasks if task.status == "in-progress"),
                "complete": sum(1 for task in tasks if task.status == "complete"),
                "blocked": sum(1 for task in tasks if task.status == "blocked"),
            },
            "latest": proposals[-1].to_dict() if proposals else {},
        }
        atomic_write_json(self.config.resolve(self.config.progress_file), payload)

    def run(self) -> list[Proposal]:
        thread = threading.Thread(target=self.heartbeat, daemon=True)
        thread.start()
        proposals: list[Proposal] = []
        try:
            count = 0
            consecutive_exceptions = 0
            while True:
                count += 1
                try:
                    proposal = self.run_cycle()
                    consecutive_exceptions = 0
                except KeyboardInterrupt:
                    raise
                except BaseException as exc:
                    consecutive_exceptions += 1
                    proposal = self.record_cycle_exception(
                        exc,
                        consecutive_exceptions=consecutive_exceptions,
                    )
                proposals.append(proposal)
                if not self.config.watch:
                    break
                if proposal.failure_kind == "no_eligible_tasks":
                    break
                if self.config.iterations > 0 and count >= self.config.iterations:
                    break
                if proposal.failure_kind == "daemon_exception":
                    if self.config.crash_backoff_seconds > 0:
                        time.sleep(self.config.crash_backoff_seconds)
                    continue
                if self.config.interval_seconds > 0:
                    board_now = read_text(self.config.resolve(self.config.task_board))
                    if not should_sleep_between_watch_cycles(
                        board_now,
                        revisit_blocked=self.config.revisit_blocked,
                    ):
                        continue
                    self.write_status("sleeping", seconds=self.config.interval_seconds)
                    time.sleep(self.config.interval_seconds)
        finally:
            self._heartbeat_stop.set()
            thread.join(timeout=1)
        return proposals


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
    return 0 if proposals and proposals[-1].valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
