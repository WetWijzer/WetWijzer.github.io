"""Daemon-local proposal-size guard rules for repeated PP&D failures.

The guard is intentionally fixture-first and side-effect free. It converts a
small daemon failure history into a retry envelope recommendation without
editing task order, changing task states, or marking domain work complete.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


_SYNTAX_FAILURE_KINDS = {"syntax_preflight", "py_compile", "typescript_syntax"}
_TIMEOUT_FAILURE_KINDS = {"timeout", "llm_timeout", "validation_timeout"}


@dataclass(frozen=True)
class ProposalRetryEnvelope:
    """Narrow retry envelope recommended after repeated daemon-local failures."""

    guard_active: bool
    target_task: str
    repeated_failure_kinds: tuple[str, ...]
    max_total_files: int
    allowed_file_roles: tuple[str, ...]
    recommendation: str
    preserves_task_ordering: bool
    marks_domain_tasks_complete: bool


def load_proposal_size_guard_fixture(path: str | Path) -> dict[str, Any]:
    """Load a proposal-size guard fixture from a committed test path."""

    with Path(path).open("r", encoding="utf-8") as fixture_file:
        payload = json.load(fixture_file)
    if not isinstance(payload, dict):
        raise ValueError("proposal-size guard fixture must be a JSON object")
    return payload


def build_proposal_retry_envelope(fixture: Mapping[str, Any]) -> ProposalRetryEnvelope:
    """Return the deterministic retry envelope for one daemon guard fixture."""

    target_task = _required_text(fixture, "target_task")
    threshold = int(fixture.get("repeat_threshold", 2))
    failure_history = _sequence(fixture.get("failure_history"))
    repeated_kinds = _repeated_failure_kinds(failure_history, target_task, threshold)
    envelope = _mapping(fixture.get("retry_envelope"))
    guard_active = bool(repeated_kinds)

    return ProposalRetryEnvelope(
        guard_active=guard_active,
        target_task=target_task,
        repeated_failure_kinds=repeated_kinds,
        max_total_files=int(envelope.get("max_total_files", 0)),
        allowed_file_roles=tuple(str(role) for role in _sequence(envelope.get("allowed_file_roles"))),
        recommendation=str(envelope.get("recommendation", "")),
        preserves_task_ordering=bool(fixture.get("preserves_task_ordering")),
        marks_domain_tasks_complete=bool(fixture.get("marks_domain_tasks_complete")),
    )


def validate_proposal_size_guard_fixture(fixture: Mapping[str, Any]) -> list[str]:
    """Return validation errors for a daemon proposal-size guard fixture."""

    errors: list[str] = []
    try:
        envelope = build_proposal_retry_envelope(fixture)
    except (TypeError, ValueError) as exc:
        return [str(exc)]

    if not envelope.guard_active:
        errors.append("guard must activate for repeated syntax-preflight or timeout failures")
    if set(envelope.repeated_failure_kinds).isdisjoint(_SYNTAX_FAILURE_KINDS | _TIMEOUT_FAILURE_KINDS):
        errors.append("guard must identify syntax-preflight or timeout failure kinds")
    if envelope.max_total_files != 2:
        errors.append("retry envelope must allow exactly two files")
    if envelope.allowed_file_roles != ("one_daemon_core_file", "one_daemon_unittest_file"):
        errors.append("retry envelope must be one daemon core file plus one daemon unittest file")
    if "one-core-file plus one-test" not in envelope.recommendation:
        errors.append("recommendation must name the one-core-file plus one-test envelope")
    if not envelope.preserves_task_ordering:
        errors.append("fixture must preserve daemon task ordering")
    if envelope.marks_domain_tasks_complete:
        errors.append("fixture must not mark domain tasks complete")
    if _sequence(fixture.get("task_order_changes")):
        errors.append("fixture must not include task order changes")
    if _sequence(fixture.get("completed_domain_tasks")):
        errors.append("fixture must not include completed domain tasks")
    return errors


def _repeated_failure_kinds(
    failure_history: Sequence[Any],
    target_task: str,
    threshold: int,
) -> tuple[str, ...]:
    counts: dict[str, int] = {}
    for item in failure_history:
        if not isinstance(item, Mapping):
            continue
        if str(item.get("target_task")) != target_task:
            continue
        failure_kind = str(item.get("failure_kind", ""))
        if failure_kind in _SYNTAX_FAILURE_KINDS or failure_kind in _TIMEOUT_FAILURE_KINDS:
            counts[failure_kind] = counts.get(failure_kind, 0) + 1
    return tuple(sorted(kind for kind, count in counts.items() if count >= threshold))


def _required_text(mapping: Mapping[str, Any], key: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"fixture missing required text field: {key}")
    return value


def _mapping(value: Any) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError("fixture retry_envelope must be an object")
    return value


def _sequence(value: Any) -> Sequence[Any]:
    if value is None:
        return ()
    if isinstance(value, Iterable) and not isinstance(value, (str, bytes, Mapping)):
        return tuple(value)
    raise ValueError("fixture field must be a sequence")
