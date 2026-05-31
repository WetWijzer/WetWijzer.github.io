"""Validation for PP&D agent readiness regression replay packet v3."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


_REQUIRED_EVIDENCE = {
    "workflow_coverage": ("workflow_coverage", "workflowCoverage", "workflows"),
    "expected_asks": ("expected_asks", "expectedAsks"),
    "holds_or_refusals": ("holds_or_refusals", "holdsOrRefusals", "refusals", "holds"),
    "next_safe_action_rows": ("next_safe_action_rows", "nextSafeActionRows"),
    "citation_references": ("citation_references", "citationReferences", "citations"),
    "reviewer_dispositions": ("reviewer_dispositions", "reviewerDispositions"),
    "validation_commands": ("validation_commands", "validationCommands"),
}

_PROHIBITED_ARTIFACT_WORDS = (
    "private",
    "session",
    "browser",
    "raw",
    "downloaded",
    "auth_state",
    "trace",
    "cookies",
)

_PROHIBITED_CLAIM_WORDS = (
    "official action complete",
    "official-action completion",
    "official action completion",
    "completed official action",
    "live crawl",
    "devhub crawl",
    "devhub session",
    "legal guarantee",
    "permitting guarantee",
    "permit guaranteed",
    "approval guaranteed",
)


def validate_agent_readiness_regression_replay_packet_v3(packet: Mapping[str, Any]) -> list[str]:
    """Return validation errors for a replay packet v3 readiness payload."""
    errors: list[str] = []

    version = packet.get("version") or packet.get("packet_version") or packet.get("packetVersion")
    if str(version) not in {"3", "v3"}:
        errors.append("packet must declare replay packet version v3")

    for label, names in _REQUIRED_EVIDENCE.items():
        value = _first_present(packet, names)
        if _is_empty(value):
            errors.append(f"missing {label}")

    for path, value in _walk(packet):
        lowered_path = path.lower()
        lowered_value = str(value).lower() if isinstance(value, str) else ""
        combined = f"{lowered_path} {lowered_value}"

        if "artifact" in lowered_path and any(word in combined for word in _PROHIBITED_ARTIFACT_WORDS):
            errors.append(f"prohibited artifact reference at {path}")

        if isinstance(value, str) and any(word in lowered_value for word in _PROHIBITED_CLAIM_WORDS):
            errors.append(f"prohibited claim at {path}")

    mutation_flags = _first_present(packet, ("active_mutation_flags", "activeMutationFlags", "mutation_flags", "mutationFlags"))
    if _has_active_mutation(mutation_flags):
        errors.append("active mutation flags are not allowed")

    return _dedupe(errors)


def assert_agent_readiness_regression_replay_packet_v3(packet: Mapping[str, Any]) -> None:
    """Raise ValueError when the replay packet v3 payload is not acceptable."""
    errors = validate_agent_readiness_regression_replay_packet_v3(packet)
    if errors:
        raise ValueError("; ".join(errors))


def _first_present(packet: Mapping[str, Any], names: Sequence[str]) -> Any:
    for name in names:
        if name in packet:
            return packet[name]
    return None


def _is_empty(value: Any) -> bool:
    if value is None:
        return True
    if value is False:
        return True
    if isinstance(value, str):
        return value.strip() == ""
    if isinstance(value, Mapping):
        return len(value) == 0
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray, str)):
        return len(value) == 0
    return False


def _has_active_mutation(value: Any) -> bool:
    if _is_empty(value):
        return False
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() not in {"", "false", "none", "no", "inactive"}
    if isinstance(value, Mapping):
        return any(_has_active_mutation(item) for item in value.values())
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray, str)):
        return any(_has_active_mutation(item) for item in value)
    return bool(value)


def _walk(value: Any, prefix: str = "$") -> list[tuple[str, Any]]:
    rows: list[tuple[str, Any]] = [(prefix, value)]
    if isinstance(value, Mapping):
        for key, item in value.items():
            rows.extend(_walk(item, f"{prefix}.{key}"))
    elif isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray, str)):
        for index, item in enumerate(value):
            rows.extend(_walk(item, f"{prefix}[{index}]"))
    return rows


def _dedupe(values: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result
