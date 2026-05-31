"""Validation for PP&D agent API contract packet v2.

The validator is intentionally structural and deterministic. It rejects packets that
omit required safety examples or that include claims/artifacts/mutation flags that
would make an implementation unsafe for isolated PP&D planning work.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Any

_REQUIRED_NON_EMPTY_SEQUENCES = {
    "synthetic_request_examples": "missing synthetic request examples",
    "response_examples": "missing response examples",
    "citation_requirements": "missing citation requirements",
    "reversible_draft_preview_references": "missing reversible draft preview references",
    "validation_commands": "missing validation commands",
}

_REQUIRED_RESPONSES = {
    "stale_or_conflicting_evidence_response": "missing stale or conflicting evidence responses",
    "refused_consequential_action_response": "missing refused consequential-action responses",
}

_FORBIDDEN_TEXT = {
    "private artifact": (
        "private artifact",
        "private/session",
        "private_session",
        "auth state",
        "auth_state",
        "session cookie",
        "session storage",
        "browser trace",
        "browser artifact",
        "raw crawl",
        "raw_crawl",
        "downloaded document",
        "downloaded artifact",
    ),
    "live DevHub claim": (
        "live devhub",
        "queried devhub live",
        "fetched from devhub",
        "authenticated devhub",
    ),
    "official-action completion claim": (
        "permit submitted",
        "application submitted",
        "official action completed",
        "inspection scheduled",
        "fee paid",
        "certification filed",
    ),
    "legal or permitting guarantee": (
        "guarantee approval",
        "guaranteed approval",
        "legally valid",
        "legal guarantee",
        "permit will be approved",
        "will be approved",
    ),
}

_MUTATION_FLAG_FIELDS = (
    "active_prompt_mutation",
    "active_guardrail_mutation",
    "active_source_mutation",
    "active_requirement_mutation",
    "active_process_model_mutation",
    "active_contract_mutation",
    "active_devhub_surface_mutation",
    "active_release_state_mutation",
)

_MUTATION_TEXT = (
    "active prompt mutation",
    "active guardrail mutation",
    "active source mutation",
    "active requirement mutation",
    "active process-model mutation",
    "active process model mutation",
    "active contract mutation",
    "active devhub surface mutation",
    "active release-state mutation",
    "active release state mutation",
)


def validate_agent_api_contract_packet_v2(packet: Mapping[str, Any]) -> list[str]:
    """Return validation errors for an agent API contract packet v2."""
    errors: list[str] = []

    if packet.get("version") != 2:
        errors.append("packet version must be 2")

    for field, message in _REQUIRED_NON_EMPTY_SEQUENCES.items():
        if not _is_non_empty_sequence(packet.get(field)):
            errors.append(message)

    for field, message in _REQUIRED_RESPONSES.items():
        if not _is_non_empty_value(packet.get(field)):
            errors.append(message)

    validation_commands = packet.get("validation_commands")
    if _is_non_empty_sequence(validation_commands):
        for index, command in enumerate(validation_commands):
            if not _is_command(command):
                errors.append(f"validation command {index} must be a non-empty list of strings")

    for field in _MUTATION_FLAG_FIELDS:
        if packet.get(field) is True:
            errors.append(f"{field} must not be active")

    for path, value in _walk_values(packet):
        if isinstance(value, str):
            lowered = value.lower()
            for label, needles in _FORBIDDEN_TEXT.items():
                if any(needle in lowered for needle in needles):
                    errors.append(f"forbidden {label} at {path}")
            if any(needle in lowered for needle in _MUTATION_TEXT):
                errors.append(f"forbidden active mutation flag at {path}")

    return sorted(set(errors))


def assert_valid_agent_api_contract_packet_v2(packet: Mapping[str, Any]) -> None:
    """Raise ValueError when a packet is not valid."""
    errors = validate_agent_api_contract_packet_v2(packet)
    if errors:
        raise ValueError("; ".join(errors))


def _is_non_empty_sequence(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes)) and len(value) > 0


def _is_non_empty_value(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, Mapping):
        return bool(value)
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return len(value) > 0
    return value is not None


def _is_command(value: Any) -> bool:
    return (
        isinstance(value, Sequence)
        and not isinstance(value, (str, bytes))
        and len(value) > 0
        and all(isinstance(part, str) and part for part in value)
    )


def _walk_values(value: Any, path: str = "$.") -> Iterable[tuple[str, Any]]:
    yield path, value
    if isinstance(value, Mapping):
        for key, child in value.items():
            yield from _walk_values(child, f"{path}{key}.")
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child in enumerate(value):
            yield from _walk_values(child, f"{path}[{index}].")
