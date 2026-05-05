"""PP&D daemon failure classification and retry policy."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from ipfs_datasets_py.optimizers.todo_daemon.diagnostics import (
    FailureBlockDecision,
    FailureBlockRule,
    count_proposal_records_with_failure_markers,
    count_recent_proposal_failures,
    exception_diagnostic as todo_exception_diagnostic,
    first_failure_block_decision,
    format_recent_failure_context,
    is_retryable_proposal_failure,
    prompt_limit_for_mode,
    proposal_block_threshold,
    proposal_record_has_failure_markers,
    should_skip_validation_for_empty_proposal,
)
from ipfs_datasets_py.optimizers.todo_daemon.engine import Proposal
from ipfs_datasets_py.optimizers.todo_daemon.history import (
    read_daemon_proposal_records,
    recent_proposal_failures,
    should_use_compact_prompt_for_failures,
)


PreLlmBlockDecision = FailureBlockDecision

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


def exception_diagnostic(exc: BaseException, *, limit: int = 5000) -> str:
    return todo_exception_diagnostic(exc, limit=limit)


def is_retryable_failure(proposal: Proposal) -> bool:
    return is_retryable_proposal_failure(
        proposal,
        retry_error_markers=frozenset(
            {
                "cloudflare",
                "403 forbidden",
                "plugins/featured",
                "timed out",
                "timeout",
                "could not generate",
                "provider",
            }
        ),
    )


def is_llm_termination_failure_record(proposal: dict[str, Any]) -> bool:
    return proposal_record_has_failure_markers(
        proposal,
        failure_kind="llm",
        markers=frozenset(LLM_TERMINATION_ERROR_MARKERS),
    )


def failure_block_threshold(proposal: Proposal, config: Any) -> int:
    """Use a tighter stop condition for parser-invalid generated patches."""

    return proposal_block_threshold(
        proposal,
        default_threshold=config.max_task_failures_before_block,
        capped_failure_kinds=frozenset({"syntax_preflight", "llm_termination"}),
        capped_threshold=2,
        exact_thresholds={"no_visible_source_change": 1},
    )


def should_skip_validation_for_no_file_failure(proposal: Proposal) -> bool:
    """Avoid expensive validation when the LLM produced no candidate files."""

    return should_skip_validation_for_empty_proposal(proposal)


def read_result_log(path: Path) -> list[dict[str, Any]]:
    return read_daemon_proposal_records(path)


def read_result_and_diagnostic_log(path: Path) -> list[dict[str, Any]]:
    return read_daemon_proposal_records(path, include_diagnostics=True)


def recent_task_failures(config: Any, task_label: str, *, limit: int = 3) -> list[dict[str, Any]]:
    return recent_proposal_failures(
        read_result_and_diagnostic_log(config.resolve(config.result_log)),
        task_label,
        limit=limit,
        normalize_task_labels=False,
    )


def should_use_compact_prompt(failures: list[dict[str, Any]], *, threshold: int = 2) -> bool:
    return should_use_compact_prompt_for_failures(failures, threshold=threshold)


def effective_prompt_limit(config: Any, *, compact_prompt: bool) -> int:
    return prompt_limit_for_mode(
        max_prompt_chars=config.max_prompt_chars,
        max_compact_prompt_chars=config.max_compact_prompt_chars,
        compact_prompt=compact_prompt,
    )


def task_failure_count(config: Any, task_label: str, *, kinds: Optional[set[str]] = None) -> int:
    return count_recent_proposal_failures(
        recent_task_failures(config, task_label, limit=100),
        failure_kinds=kinds,
    )


def llm_termination_failure_count(config: Any, task_label: str) -> int:
    return count_proposal_records_with_failure_markers(
        recent_task_failures(config, task_label, limit=100),
        failure_kind="llm",
        markers=frozenset(LLM_TERMINATION_ERROR_MARKERS),
    )


def pre_llm_block_decision(config: Any, task_label: str) -> Optional[PreLlmBlockDecision]:
    """Return a durable stop decision for tasks that are already known-stuck."""

    syntax_probe = Proposal(failure_kind="syntax_preflight")
    termination_probe = Proposal(failure_kind="llm_termination")
    return first_failure_block_decision(
        (
            FailureBlockRule(
                failure_kind="syntax_preflight",
                count=task_failure_count(config, task_label, kinds={"syntax_preflight"}),
                threshold=failure_block_threshold(syntax_probe, config),
                summary="Task blocked before LLM after repeated syntax-preflight failures.",
                result="syntax_preflight_blocked",
            ),
            FailureBlockRule(
                failure_kind="llm_termination",
                count=llm_termination_failure_count(config, task_label),
                threshold=failure_block_threshold(termination_probe, config),
                summary="Task blocked before LLM after repeated LLM termination failures.",
                result="llm_termination_blocked",
            ),
        )
    )


def should_block_task_before_llm(config: Any, task_label: str) -> bool:
    """Stop retrying a task that already hit a pre-LLM block threshold."""

    return pre_llm_block_decision(config, task_label) is not None


def format_failure_context(failures: list[dict[str, Any]]) -> str:
    return format_recent_failure_context(
        failures,
        guidance=lambda recent: (
            [
                "Recovery guidance: a validator found a forbidden artifact marker inside the proposed fixture or test text. "
                "Return only one JSON object on the retry, and use a small file set that fixes the self-triggering field names. "
                "When representing absence, avoid keys or values containing banned substrings such as cookie, screenshot, "
                "auth-state, storage-state, trace.zip, or .har. Use neutral names like `runtimeArtifactsStored`, "
                "`visualArtifactsStored`, `authenticatedArtifactsStored`, or `forbiddenArtifactsAbsent` instead of "
                "`containsCookies`, `screenshotsStored`, or similar self-triggering absence fields."
            ]
            if any(is_forbidden_absence_marker_validation_failure(dict(failure)) for failure in recent)
            else []
        ),
    )


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
