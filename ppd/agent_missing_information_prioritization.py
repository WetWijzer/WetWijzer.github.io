"""Agent-facing prioritization for PP&D missing-information prompts.

The fixture API is deterministic and side-effect free. It returns only facts that
are missing, stale, ambiguous, or conflicting and are needed before the next safe
action. Private values and local paths are never returned to the agent prompt.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

_ALLOWED_STATUSES = {"missing", "stale", "ambiguous", "conflicting"}
_STATUS_PRIORITY = {"missing": 0, "stale": 1, "ambiguous": 2, "conflicting": 3}
_STAGE_ORDER = {
    "pre-application research": 0,
    "account setup or manual login": 1,
    "property lookup": 2,
    "permit type selection": 3,
    "eligibility screening": 4,
    "document preparation": 5,
    "application data entry": 6,
    "upload staging": 7,
    "acknowledgement/certification review": 8,
    "submission": 9,
    "prescreen/intake": 10,
    "fee payment": 11,
    "plan review": 12,
    "corrections/checksheets": 13,
    "approval/issuance": 14,
    "inspections": 15,
    "closeout, cancellation, expiration, extension, or reactivation": 16,
}
_LOCAL_PATH_PATTERNS = (
    re.compile(r"(?:^|\s)/(?:home|Users|tmp|var|private|mnt|Volumes)/"),
    re.compile(r"[A-Za-z]:\\\\"),
    re.compile(r"file://"),
)
_PRIVATE_VALUE_KEYS = {
    "current_value",
    "observed_value",
    "raw_value",
    "private_value",
    "local_path",
    "file_path",
    "absolute_path",
}
_DEFAULT_FIXTURE = (
    Path(__file__).parent
    / "tests"
    / "fixtures"
    / "missing_information_prioritization"
    / "blocking_dependency_stage_fixture.json"
)


class MissingInformationPrioritizationError(ValueError):
    """Raised when a missing-information prioritization fixture is invalid."""


@dataclass(frozen=True)
class PrioritizedPrompt:
    """A single redacted agent-facing prompt for the next safe action."""

    prompt_id: str
    fact_id: str
    status: str
    blocking_dependency_stage: str
    prompt: str
    reason: str
    source_requirement_ids: tuple[str, ...]
    blocked_next_safe_action: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "prompt_id": self.prompt_id,
            "fact_id": self.fact_id,
            "status": self.status,
            "blocking_dependency_stage": self.blocking_dependency_stage,
            "prompt": self.prompt,
            "reason": self.reason,
            "source_requirement_ids": list(self.source_requirement_ids),
            "blocked_next_safe_action": self.blocked_next_safe_action,
        }


def load_prioritized_missing_information_fixture(
    *,
    fixture_path: Path | None = None,
) -> dict[str, Any]:
    """Load and return the redacted prioritized prompt fixture."""

    path = fixture_path or _DEFAULT_FIXTURE
    payload = json.loads(path.read_text(encoding="utf-8"))
    return prioritize_missing_information_prompts(payload)


def prioritize_missing_information_prompts(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Return only unresolved facts needed for the next safe action.

    Facts are sorted first by the PP&D process dependency stage that blocks the
    next action, then by status priority, then by fixture order. Returned prompt
    dictionaries intentionally omit private value fields.
    """

    _validate_payload_shape(payload)
    prompts: list[tuple[int, int, int, PrioritizedPrompt]] = []

    for index, fact in enumerate(_sequence(payload.get("facts"))):
        fact_map = _mapping(fact)
        status = _text(fact_map.get("status"))
        if status not in _ALLOWED_STATUSES:
            continue
        if not _bool(fact_map.get("needed_for_next_safe_action")):
            continue

        stage = _text(fact_map.get("blocking_dependency_stage"))
        prompt = PrioritizedPrompt(
            prompt_id=_text(fact_map.get("prompt_id")) or f"ask_{_text(fact_map.get('fact_id'))}",
            fact_id=_text(fact_map.get("fact_id")),
            status=status,
            blocking_dependency_stage=stage,
            prompt=_text(fact_map.get("prompt")),
            reason=_text(fact_map.get("reason")),
            source_requirement_ids=tuple(
                _text(value) for value in _sequence(fact_map.get("source_requirement_ids")) if _text(value)
            ),
            blocked_next_safe_action=_text(fact_map.get("blocked_next_safe_action")),
        )
        prompts.append((
            _STAGE_ORDER.get(stage, 10_000),
            _STATUS_PRIORITY[status],
            index,
            prompt,
        ))

    ordered_prompts = [item[3].to_dict() for item in sorted(prompts, key=lambda item: item[:3])]
    _validate_redacted_output(ordered_prompts)
    return {
        "fixture_id": _text(payload.get("fixture_id")),
        "case_id": _text(payload.get("case_id")),
        "process_id": _text(payload.get("process_id")),
        "next_safe_action": _text(payload.get("next_safe_action")),
        "prioritization": "blocking_dependency_stage_then_status",
        "prompts": ordered_prompts,
    }


def validate_missing_information_prioritization_fixture(payload: Mapping[str, Any]) -> list[str]:
    """Return validation errors for a prioritization fixture."""

    try:
        prioritize_missing_information_prompts(payload)
    except MissingInformationPrioritizationError as exc:
        return [str(exc)]
    return []


def _validate_payload_shape(payload: Mapping[str, Any]) -> None:
    required_top_level = ("fixture_id", "case_id", "process_id", "next_safe_action", "facts")
    for key in required_top_level:
        if key not in payload or payload.get(key) in (None, ""):
            raise MissingInformationPrioritizationError(f"{key} is required")

    facts = _sequence(payload.get("facts"))
    if not facts:
        raise MissingInformationPrioritizationError("facts must include at least one fixture fact")

    emitted_count = 0
    for fact in facts:
        fact_map = _mapping(fact)
        fact_id = _text(fact_map.get("fact_id"))
        status = _text(fact_map.get("status"))
        if not fact_id:
            raise MissingInformationPrioritizationError("each fact requires fact_id")
        if status and status not in _ALLOWED_STATUSES and status != "complete":
            raise MissingInformationPrioritizationError(f"fact {fact_id} has unsupported status {status}")
        if status in _ALLOWED_STATUSES and _bool(fact_map.get("needed_for_next_safe_action")):
            emitted_count += 1
            for key in ("blocking_dependency_stage", "prompt", "reason", "blocked_next_safe_action"):
                if not _text(fact_map.get(key)):
                    raise MissingInformationPrioritizationError(f"fact {fact_id} requires {key}")
            if _text(fact_map.get("blocking_dependency_stage")) not in _STAGE_ORDER:
                raise MissingInformationPrioritizationError(
                    f"fact {fact_id} has unknown blocking_dependency_stage"
                )

    if emitted_count == 0:
        raise MissingInformationPrioritizationError("fixture must emit at least one blocking unresolved fact")
    _reject_private_paths(payload)


def _validate_redacted_output(prompts: Sequence[Mapping[str, Any]]) -> None:
    serialized = json.dumps(prompts, sort_keys=True)
    for private_key in _PRIVATE_VALUE_KEYS:
        if private_key in serialized:
            raise MissingInformationPrioritizationError(f"output includes private field {private_key}")
    _reject_private_paths(prompts)


def _reject_private_paths(value: Any) -> None:
    serialized = json.dumps(value, sort_keys=True)
    for pattern in _LOCAL_PATH_PATTERNS:
        if pattern.search(serialized):
            raise MissingInformationPrioritizationError("fixture includes a local path")


def _mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    return {}


def _sequence(value: Any) -> Sequence[Any]:
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return value
    return ()


def _text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _bool(value: Any) -> bool:
    return value is True


__all__ = [
    "MissingInformationPrioritizationError",
    "PrioritizedPrompt",
    "load_prioritized_missing_information_fixture",
    "prioritize_missing_information_prompts",
    "validate_missing_information_prioritization_fixture",
]
