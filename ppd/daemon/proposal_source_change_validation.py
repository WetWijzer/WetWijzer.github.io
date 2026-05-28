"""Validation helpers for PP&D daemon task-board completion proposals."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Any, Iterable, Mapping, Sequence


@dataclass(frozen=True)
class ProposalSourceChangeFinding:
    """A deterministic validation finding for a proposed file replacement."""

    code: str
    message: str
    path: str | None = None


_TASK_BOARD_PATH_PARTS = {
    "task_board",
    "task-board",
    "tasks",
    "supervisor",
    "backlog",
}

_SOURCE_SUFFIXES = {
    ".py",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".json",
    ".toml",
    ".yaml",
    ".yml",
}

_PARSER_CLEAN_SUFFIXES = {".py", ".ts", ".tsx"}

_COMPLETION_MARKERS = (
    "[x]",
    "[X]",
    "status: complete",
    "status: completed",
    "status=complete",
    "status=completed",
    "\"status\": \"complete\"",
    "\"status\": \"completed\"",
    "'status': 'complete'",
    "'status': 'completed'",
)

_BACKLOG_ONLY_MARKERS = (
    "plan_next_tasks",
    "next_tasks",
    "backlog",
)

_TIMEOUT_DIAGNOSTIC_MARKERS = (
    "worker_llm_timeout",
    "daemon_llm_timeout",
    "llm_timeout",
    "timed_out",
    "timeout_diagnostic",
)

_PROPOSAL_SIZE_GUARD_MARKERS = (
    "proposal_size_guard",
    "proposal-size guard",
    "size_guard",
    "proposal_retry_envelope",
    "retry_envelope",
    "one-core-file plus one-test",
    "max_total_files",
)

_SUPERVISOR_METADATA_PATHS = frozenset(
    {
        "ppd/daemon/status.json",
        "ppd/daemon/progress.json",
        "ppd/daemon/supervisor-status.json",
        "ppd/daemon/supervisor-actions.jsonl",
        "ppd/daemon/deterministic-progress.json",
        "ppd/daemon/builtin-repair-status.json",
    }
)


def validate_task_board_completion_source_changes(
    proposal: Mapping[str, Any],
) -> list[ProposalSourceChangeFinding]:
    """Reject task-board completion proposals that contain no committed source change.

    The daemon receives proposed complete file replacements. This validator keeps the
    rule intentionally simple and deterministic: if a proposal visibly marks work
    complete in a task-board-like file, it must also include at least one committed
    application/domain source replacement outside task-board, docs-plan, and fixture
    files. Supervisor-only backlog planning updates remain allowed when they are
    confined to plan_next_tasks-style content and do not mark new work complete.
    """

    files = _proposal_files(proposal)
    if not files:
        return []

    task_board_files = [file for file in files if _is_task_board_file(file[0])]
    if not task_board_files:
        return []

    marks_complete = any(_content_marks_work_complete(content) for _, content in task_board_files)
    if not marks_complete:
        return []

    if _is_supervisor_only_backlog_update(proposal, files):
        if _plan_next_tasks_marks_completion(proposal, task_board_files):
            return [
                ProposalSourceChangeFinding(
                    code="task_board_completion_in_plan_next_tasks",
                    message="plan_next_tasks updates may add or reorder backlog work, but may not mark application/domain work complete.",
                    path=task_board_files[0][0],
                )
            ]
        return []

    if _has_visible_committed_source_change(files):
        return []

    return [
        ProposalSourceChangeFinding(
            code="task_board_completion_without_source_change",
            message="Task-board completion proposals must include a visible committed application/domain source change.",
            path=task_board_files[0][0],
        )
    ]


def validate_daemon_timeout_diagnostic_boundaries(
    proposal: Mapping[str, Any],
) -> list[ProposalSourceChangeFinding]:
    """Validate that daemon timeout diagnostics stay supervisor-only metadata.

    Timeout diagnostics explain worker health. They must not become evidence that
    PP&D domain work completed, and they must not edit domain implementation files.
    A later supervisor ``plan_next_tasks`` proposal may still append ordered backlog
    items when those additions are unchecked and planning-only.
    """

    return _validate_supervisor_diagnostic_boundaries(
        proposal,
        contains_diagnostic=_contains_timeout_diagnostic,
        code_prefix="timeout_diagnostic",
        diagnostic_label="Daemon timeout diagnostics",
    )


def validate_proposal_size_guard_diagnostic_boundaries(
    proposal: Mapping[str, Any],
) -> list[ProposalSourceChangeFinding]:
    """Validate proposal-size guard diagnostics remain supervisor metadata only.

    The proposal-size guard recommends a smaller retry envelope after repeated
    syntax-preflight or timeout failures. It is supervisor metadata: it must not
    complete PP&D domain tasks, alter eligible task selection, or block a later
    ``plan_next_tasks`` proposal that appends unchecked backlog work only.
    """

    findings = _validate_supervisor_diagnostic_boundaries(
        proposal,
        contains_diagnostic=_contains_proposal_size_guard_diagnostic,
        code_prefix="proposal_size_guard",
        diagnostic_label="Proposal-size guard diagnostics",
    )
    findings.extend(validate_parser_clean_validation_commands(proposal))
    return _deduplicate_findings(findings)


def validate_supervisor_diagnostic_boundaries(
    proposal: Mapping[str, Any],
) -> list[ProposalSourceChangeFinding]:
    """Validate all known supervisor-only daemon diagnostic boundaries."""

    findings: list[ProposalSourceChangeFinding] = []
    findings.extend(validate_daemon_timeout_diagnostic_boundaries(proposal))
    findings.extend(validate_proposal_size_guard_diagnostic_boundaries(proposal))
    return _deduplicate_findings(findings)


def validate_parser_clean_validation_commands(
    proposal: Mapping[str, Any],
) -> list[ProposalSourceChangeFinding]:
    """Require parser-clean validation commands for changed Python or TypeScript files."""

    files = _proposal_files(proposal)
    parser_clean_paths = [path for path, _content in files if _is_parser_clean_file(path)]
    if not parser_clean_paths:
        return []

    commands = proposal.get("validation_commands", [])
    findings: list[ProposalSourceChangeFinding] = []
    for path in parser_clean_paths:
        if not _has_parser_clean_command_for_path(commands, path):
            findings.append(
                ProposalSourceChangeFinding(
                    code="missing_parser_clean_validation_command",
                    message="Changed Python or TypeScript files must have a parser-clean validation command in validation_commands.",
                    path=path,
                )
            )
    return findings


def _validate_supervisor_diagnostic_boundaries(
    proposal: Mapping[str, Any],
    *,
    contains_diagnostic: Any,
    code_prefix: str,
    diagnostic_label: str,
) -> list[ProposalSourceChangeFinding]:
    findings = list(validate_task_board_completion_source_changes(proposal))
    if not contains_diagnostic(proposal):
        return findings

    files = _proposal_files(proposal)
    task_board_files = [file for file in files if _is_task_board_file(file[0])]
    if task_board_files:
        plan_next_tasks = _is_supervisor_only_backlog_update(proposal, files)
        if any(_content_marks_work_complete(content) for _, content in task_board_files):
            if not plan_next_tasks or _plan_next_tasks_marks_completion(proposal, task_board_files):
                findings.append(
                    ProposalSourceChangeFinding(
                        code=f"{code_prefix}_marks_domain_task_complete",
                        message=f"{diagnostic_label} are supervisor-only metadata and cannot mark PP&D domain tasks complete.",
                        path=task_board_files[0][0],
                    )
                )

    for path, _content in files:
        if _is_supervisor_metadata_path(path):
            continue
        if _is_task_board_file(path) and _is_supervisor_only_backlog_update(proposal, files):
            continue
        findings.append(
            ProposalSourceChangeFinding(
                code=f"{code_prefix}_not_supervisor_only",
                message=f"{diagnostic_label} may only update supervisor metadata or planning-only task-board backlog entries.",
                path=path,
            )
        )

    return _deduplicate_findings(findings)


def _proposal_files(proposal: Mapping[str, Any]) -> list[tuple[str, str]]:
    raw_files = proposal.get("files", [])
    if not isinstance(raw_files, Sequence) or isinstance(raw_files, (str, bytes)):
        return []

    files: list[tuple[str, str]] = []
    for raw_file in raw_files:
        if not isinstance(raw_file, Mapping):
            continue
        path = raw_file.get("path")
        content = raw_file.get("content")
        if isinstance(path, str) and isinstance(content, str):
            files.append((path, content))
    return files


def _is_task_board_file(path: str) -> bool:
    posix = PurePosixPath(path)
    lowered_parts = {part.lower() for part in posix.parts}
    lowered_name = posix.name.lower()
    if lowered_parts & _TASK_BOARD_PATH_PARTS:
        return True
    return "task" in lowered_name and "board" in lowered_name


def _content_marks_work_complete(content: str) -> bool:
    return any(marker in content for marker in _COMPLETION_MARKERS)


def _has_visible_committed_source_change(files: Iterable[tuple[str, str]]) -> bool:
    for path, content in files:
        if not content.strip():
            continue
        if not path.startswith("ppd/"):
            continue
        if _is_task_board_file(path):
            continue
        if _is_fixture_path(path):
            continue
        if _is_docs_plan_path(path):
            continue
        suffix = PurePosixPath(path).suffix.lower()
        if suffix in _SOURCE_SUFFIXES:
            return True
    return False


def _is_fixture_path(path: str) -> bool:
    return "/fixtures/" in path or path.startswith("ppd/tests/fixtures/")


def _is_docs_plan_path(path: str) -> bool:
    return path == "docs/PORTLAND_PPD_SCRAPING_AUTOMATION_LOGIC_PLAN.md"


def _is_supervisor_only_backlog_update(
    proposal: Mapping[str, Any], files: Sequence[tuple[str, str]]
) -> bool:
    if "plan_next_tasks" in proposal:
        return True

    summary = proposal.get("summary", "")
    impact = proposal.get("impact", "")
    text_fields = "\n".join(
        value for value in (summary, impact) if isinstance(value, str)
    )
    file_text = "\n".join(content for _, content in files)
    combined = f"{text_fields}\n{file_text}"
    return any(marker in combined for marker in _BACKLOG_ONLY_MARKERS)


def _plan_next_tasks_marks_completion(
    proposal: Mapping[str, Any], task_board_files: Sequence[tuple[str, str]]
) -> bool:
    raw_plan = proposal.get("plan_next_tasks")
    if isinstance(raw_plan, Sequence) and not isinstance(raw_plan, (str, bytes)):
        for item in raw_plan:
            if isinstance(item, str) and _content_marks_work_complete(item):
                return True
            if isinstance(item, Mapping):
                status = item.get("status")
                mark = item.get("mark")
                if isinstance(status, str) and status.lower() in {"complete", "completed"}:
                    return True
                if isinstance(mark, str) and mark.lower() == "x":
                    return True

    for _path, content in task_board_files:
        in_plan_next_tasks = False
        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("plan_next_tasks") or stripped.startswith("## plan_next_tasks"):
                in_plan_next_tasks = True
                continue
            if in_plan_next_tasks and stripped.startswith("## "):
                in_plan_next_tasks = False
            if in_plan_next_tasks and stripped.startswith("- [") and _content_marks_work_complete(stripped):
                return True
    return False


def _contains_timeout_diagnostic(value: Any) -> bool:
    return _contains_any_marker(value, _TIMEOUT_DIAGNOSTIC_MARKERS)


def _contains_proposal_size_guard_diagnostic(value: Any) -> bool:
    return _contains_any_marker(value, _PROPOSAL_SIZE_GUARD_MARKERS)


def _contains_any_marker(value: Any, markers: Sequence[str]) -> bool:
    if isinstance(value, Mapping):
        return any(
            _contains_any_marker(key, markers) or _contains_any_marker(item, markers)
            for key, item in value.items()
        )
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return any(_contains_any_marker(item, markers) for item in value)
    if isinstance(value, str):
        lowered = value.lower()
        return any(marker in lowered for marker in markers)
    return False


def _is_supervisor_metadata_path(path: str) -> bool:
    if path in _SUPERVISOR_METADATA_PATHS:
        return True
    if path.startswith("ppd/daemon/") and path.endswith(".jsonl"):
        return True
    return False


def _is_timeout_supervisor_metadata_path(path: str) -> bool:
    return _is_supervisor_metadata_path(path)


def _is_parser_clean_file(path: str) -> bool:
    return PurePosixPath(path).suffix.lower() in _PARSER_CLEAN_SUFFIXES


def _has_parser_clean_command_for_path(commands: Any, path: str) -> bool:
    if not isinstance(commands, Sequence) or isinstance(commands, (str, bytes)):
        return False
    suffix = PurePosixPath(path).suffix.lower()
    for command in commands:
        if not isinstance(command, Sequence) or isinstance(command, (str, bytes)):
            continue
        parts = tuple(str(part) for part in command)
        if path not in parts:
            continue
        if suffix == ".py" and "py_compile" in parts:
            return True
        if suffix in {".ts", ".tsx"} and any(part.endswith("tsc") or part == "tsc" for part in parts):
            return True
    return False


def _deduplicate_findings(
    findings: Iterable[ProposalSourceChangeFinding],
) -> list[ProposalSourceChangeFinding]:
    deduped: list[ProposalSourceChangeFinding] = []
    seen: set[tuple[str, str | None]] = set()
    for finding in findings:
        key = (finding.code, finding.path)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(finding)
    return deduped


__all__ = [
    "ProposalSourceChangeFinding",
    "validate_daemon_timeout_diagnostic_boundaries",
    "validate_parser_clean_validation_commands",
    "validate_proposal_size_guard_diagnostic_boundaries",
    "validate_supervisor_diagnostic_boundaries",
    "validate_task_board_completion_source_changes",
]
