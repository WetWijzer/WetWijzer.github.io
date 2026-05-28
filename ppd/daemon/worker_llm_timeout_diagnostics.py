"""Diagnostics for repeated worker LLM timeouts.

This module formats commit-safe daemon diagnostics only. It deliberately does not
read, rank, mutate, or select task-board work.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


SMALLER_WORKER_TIMEOUT_NEXT_ATTEMPT_GUIDANCE = (
    "Return a smaller next attempt for the same target task. Limit the proposal "
    "to the files needed for the daemon regression or repair, keep Python syntax "
    "valid, and preserve existing task-selection semantics."
)


@dataclass(frozen=True)
class WorkerLlmTimeoutEvent:
    """Commit-safe summary of one worker LLM timeout."""

    target_task: str
    elapsed_timeout_seconds: int
    summary: str = ""


def repeated_worker_llm_timeout_diagnostics(
    events: Iterable[WorkerLlmTimeoutEvent],
    *,
    repeat_threshold: int = 2,
) -> list[dict[str, object]]:
    """Return diagnostics for tasks with repeated worker LLM timeouts.

    The retry count is derived from repeated timeout events for the same target
    task. Output records avoid selection fields so callers can append them to
    daemon logs without changing task-selection behavior.
    """

    if repeat_threshold < 2:
        raise ValueError("repeat_threshold must be at least 2")

    grouped: dict[str, list[WorkerLlmTimeoutEvent]] = {}
    for event in events:
        if not event.target_task:
            raise ValueError("target_task must be non-empty")
        if event.elapsed_timeout_seconds < 1:
            raise ValueError("elapsed_timeout_seconds must be positive")
        grouped.setdefault(event.target_task, []).append(event)

    diagnostics: list[dict[str, object]] = []
    for target_task in sorted(grouped):
        task_events = grouped[target_task]
        if len(task_events) < repeat_threshold:
            continue
        latest_event = task_events[-1]
        diagnostics.append(
            {
                "kind": "worker_llm_timeout",
                "target_task": target_task,
                "elapsed_timeout_seconds": latest_event.elapsed_timeout_seconds,
                "retry_count": len(task_events),
                "latest_summary": latest_event.summary,
                "guidance": SMALLER_WORKER_TIMEOUT_NEXT_ATTEMPT_GUIDANCE,
            }
        )

    return diagnostics
