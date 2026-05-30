"""Validation for combined promotion dependency packet v1.

The validator is intentionally schema-light: packets may evolve, but the safety
properties in this module must remain true before a packet is eligible for any
promotion workflow.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any


_MUTATION_KEYS = {
    "active_source_mutation",
    "active_source_mutation_requested",
    "mutate_active_source",
    "surface_registry_mutation",
    "surface_registry_mutation_requested",
    "mutate_surface_registry",
    "guardrail_mutation",
    "guardrail_mutation_requested",
    "mutate_guardrail",
    "prompt_mutation",
    "prompt_mutation_requested",
    "mutate_prompt",
    "release_state_mutation",
    "release_state_mutation_requested",
    "mutate_release_state",
    "agent_state_mutation",
    "agent_state_mutation_requested",
    "mutate_agent_state",
}

_ARTIFACT_MARKERS = (
    "private",
    "authenticated",
    "auth",
    "session",
    "browser",
    "trace",
    "raw",
    "downloaded",
    "download",
    "cookie",
    "token",
)

_LIVE_OR_PROMOTION_CLAIMS = (
    "live execution",
    "executed live",
    "live crawl",
    "live browser",
    "promoted",
    "promotion complete",
    "ready for production",
    "release complete",
)

_LEGAL_OR_PERMIT_GUARANTEES = (
    "guarantee",
    "guaranteed",
    "approved permit",
    "permit approved",
    "approval guaranteed",
    "legal advice",
    "legally compliant",
    "will be approved",
    "must be approved",
)

_CONSEQUENTIAL_ACTION_LANGUAGE = (
    "submit application",
    "file application",
    "pay fee",
    "make payment",
    "certify",
    "sign under penalty",
    "cancel permit",
    "schedule inspection",
    "book inspection",
    "upload document",
    "create account",
)


@dataclass(frozen=True)
class PacketValidationResult:
    valid: bool
    errors: tuple[str, ...]


def validate_combined_promotion_dependency_packet_v1(packet: Mapping[str, Any]) -> PacketValidationResult:
    """Return validation errors for a combined promotion dependency packet v1."""

    errors: list[str] = []

    if packet.get("packet_version") != "combined-promotion-dependency-packet-v1":
        errors.append("packet_version must be combined-promotion-dependency-packet-v1")

    _require_non_empty(packet, "owner", errors)
    _require_non_empty(packet, "dependency_order", errors)
    _require_non_empty(packet, "rollback_checkpoints", errors)
    _require_non_empty(packet, "validation_inventory", errors)

    prerequisites = _as_sequence(packet.get("prerequisites"))
    for index, prerequisite in enumerate(prerequisites):
        if not isinstance(prerequisite, Mapping):
            errors.append(f"prerequisites[{index}] must be an object")
            continue
        if not _has_citation(prerequisite):
            errors.append(f"prerequisites[{index}] must include at least one citation")

    for path, value in _walk(packet):
        key = path[-1] if path else ""
        normalized_key = _normalize(key)
        if normalized_key in _MUTATION_KEYS and bool(value):
            errors.append(f"{'.'.join(path)} must not request state mutation")

        if isinstance(value, str):
            normalized_value = _normalize(value)
            _reject_marker(path, normalized_value, _ARTIFACT_MARKERS, "private/authenticated/session/browser/raw/downloaded artifact", errors)
            _reject_marker(path, normalized_value, _LIVE_OR_PROMOTION_CLAIMS, "live execution or promotion claim", errors)
            _reject_marker(path, normalized_value, _LEGAL_OR_PERMIT_GUARANTEES, "legal or permitting outcome guarantee", errors)
            _reject_marker(path, normalized_value, _CONSEQUENTIAL_ACTION_LANGUAGE, "consequential action language", errors)

    return PacketValidationResult(valid=not errors, errors=tuple(errors))


def assert_valid_combined_promotion_dependency_packet_v1(packet: Mapping[str, Any]) -> None:
    """Raise ValueError when the packet violates v1 safety requirements."""

    result = validate_combined_promotion_dependency_packet_v1(packet)
    if not result.valid:
        raise ValueError("; ".join(result.errors))


def _require_non_empty(packet: Mapping[str, Any], key: str, errors: list[str]) -> None:
    value = packet.get(key)
    if value is None or value == "" or value == [] or value == {}:
        errors.append(f"{key} is required")


def _has_citation(item: Mapping[str, Any]) -> bool:
    citations = item.get("citations") or item.get("citation") or item.get("source_citations")
    if isinstance(citations, str):
        return bool(citations.strip())
    if isinstance(citations, Sequence) and not isinstance(citations, (str, bytes)):
        return any(bool(entry) for entry in citations)
    return False


def _as_sequence(value: Any) -> Sequence[Any]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return value
    return ()


def _walk(value: Any, path: tuple[str, ...] = ()) -> list[tuple[tuple[str, ...], Any]]:
    items: list[tuple[tuple[str, ...], Any]] = [(path, value)]
    if isinstance(value, Mapping):
        for key, child in value.items():
            items.extend(_walk(child, path + (str(key),)))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child in enumerate(value):
            items.extend(_walk(child, path + (str(index),)))
    return items


def _normalize(value: str) -> str:
    return value.strip().lower().replace("-", "_").replace(" ", "_")


def _reject_marker(path: tuple[str, ...], value: str, markers: tuple[str, ...], label: str, errors: list[str]) -> None:
    haystack = value.replace("_", " ")
    for marker in markers:
        normalized_marker = marker.replace("_", " ")
        if normalized_marker in haystack:
            location = ".".join(path) if path else "packet"
            errors.append(f"{location} contains prohibited {label}: {marker}")
            return
