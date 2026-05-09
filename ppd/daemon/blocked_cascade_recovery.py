"""Deterministic recovery helpers for PP&D blocked-cascade daemon stalls.

This module is intentionally small and dependency-free. It is safe to import from
supervisor diagnostics, repair prompts, or tests when repeated daemon termination
prevents the LLM worker from producing a promotable patch.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence


TERMINATION_MARKERS = (
    "SystemExit: 143",
    "exit code -15",
    "SIGTERM",
    "terminated",
)

BLOCKED_CASCADE_MARKERS = (
    "blocked-cascade daemon-repair coverage",
    "blocked PP&D work stays parked",
    "fresh daemon repair task validates",
)


@dataclass(frozen=True)
class RecoveryDecision:
    """Supervisor-facing decision for a repeated blocked-cascade stall."""

    should_replan: bool
    keep_target_parked: bool
    reason: str
    next_tasks: tuple[str, ...]


def _joined_errors(results: Iterable[Mapping[str, object]]) -> str:
    chunks: list[str] = []
    for result in results:
        errors = result.get("errors", ())
        if isinstance(errors, str):
            chunks.append(errors)
        elif isinstance(errors, Sequence):
            chunks.extend(str(error) for error in errors)
        target = result.get("target_task")
        if target:
            chunks.append(str(target))
        summary = result.get("summary")
        if summary:
            chunks.append(str(summary))
    return "\n".join(chunks)


def classify_blocked_cascade_stall(
    *,
    active_target_task: str,
    consecutive_exceptions: int,
    recent_results: Iterable[Mapping[str, object]],
) -> RecoveryDecision:
    """Return a deterministic supervisor decision for blocked-cascade stalls.

    Repeated termination during replacement or validation should not cause the
    daemon to keep selecting the same blocked generated-coverage task. The safe
    response is to keep that PP&D work parked and ask for narrow validation-first
    daemon repair tasks.
    """

    evidence = "\n".join((active_target_task, _joined_errors(recent_results)))
    saw_termination = any(marker in evidence for marker in TERMINATION_MARKERS)
    saw_blocked_cascade = any(marker in evidence for marker in BLOCKED_CASCADE_MARKERS)

    if consecutive_exceptions < 2 or not saw_termination or not saw_blocked_cascade:
        return RecoveryDecision(
            should_replan=False,
            keep_target_parked=False,
            reason="No repeated blocked-cascade termination storm was detected.",
            next_tasks=(),
        )

    return RecoveryDecision(
        should_replan=True,
        keep_target_parked=True,
        reason=(
            "Repeated termination hit the same blocked-cascade generated coverage "
            "path; park that PP&D task until a smaller daemon repair validates."
        ),
        next_tasks=(
            "Add a fixture-only regression test proving repeated SystemExit 143 results cause the supervisor to replan instead of retrying the same blocked-cascade task.",
            "Add a deterministic supervisor diagnostic that converts repeated termination during file replacement or validation into a validation-first daemon repair task.",
            "Add a narrow preflight guard that rejects generated blocked-cascade coverage proposals unless their Python files py_compile before promotion.",
        ),
    )


__all__ = ["RecoveryDecision", "classify_blocked_cascade_stall"]
