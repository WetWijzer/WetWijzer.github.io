"""Validation for prompt refresh release handoff packets.

This module is intentionally narrow and deterministic. It validates release
handoff packet dictionaries without contacting live services or mutating prompt,
guardrail, release, monitoring, or agent state.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


MUTATION_FLAG_NAMES = {
    "active_prompt_mutation",
    "active_guardrail_mutation",
    "active_release_state_mutation",
    "active_monitoring_mutation",
    "active_agent_state_mutation",
    "mutate_prompts",
    "mutate_guardrails",
    "mutate_release_state",
    "mutate_monitoring",
    "mutate_agent_state",
    "enable_prompt_write",
    "enable_guardrail_write",
    "enable_release_write",
    "enable_monitoring_write",
    "enable_agent_state_write",
}

PRIVATE_FACT_MARKERS = (
    "authenticated",
    "private devhub",
    "session cookie",
    "bearer token",
    "api key",
    "password",
    "mfa",
    "captcha",
    "non-public",
    "private fact",
)

RAW_INJECTION_MARKERS = (
    "ignore previous instructions",
    "ignore all previous instructions",
    "system prompt",
    "developer message",
    "jailbreak",
    "prompt injection",
)

LIVE_EXECUTION_MARKERS = (
    "live llm",
    "called llm",
    "devhub execution",
    "live devhub",
    "crawler ran",
    "live crawler",
    "processor ran",
    "live processor",
    "executed crawler",
    "executed processor",
)

GUARANTEE_MARKERS = (
    "permit will be approved",
    "approval guaranteed",
    "guaranteed approval",
    "legal outcome guaranteed",
    "permitting outcome guaranteed",
    "will pass inspection",
    "will be issued",
)

CONSEQUENTIAL_CONTROL_KEYS = (
    "submit",
    "certify",
    "cancel",
    "pay",
    "upload",
    "schedule_inspection",
    "issue_permit",
    "approve_permit",
)


class HandoffValidationError(ValueError):
    """Raised when a handoff packet fails validation."""

    def __init__(self, errors: list[str]) -> None:
        super().__init__("; ".join(errors))
        self.errors = errors


def load_packet(path: str | Path) -> dict[str, Any]:
    """Load a JSON handoff packet from disk."""

    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise HandoffValidationError(["packet must be a JSON object"])
    return data


def assert_valid_handoff_packet(packet: dict[str, Any]) -> None:
    """Raise HandoffValidationError if the packet is not safe to accept."""

    errors = validate_handoff_packet(packet)
    if errors:
        raise HandoffValidationError(errors)


def validate_handoff_packet(packet: dict[str, Any]) -> list[str]:
    """Return deterministic validation errors for a handoff packet."""

    errors: list[str] = []
    if not isinstance(packet, dict):
        return ["packet must be a dictionary"]

    _validate_prompt_versions(packet, errors)
    _require_non_empty_list(packet, "compatibility_notes", errors)
    _require_non_empty_list(packet, "migration_checklist", errors)
    _require_non_empty_string(packet, "rollback_owner", errors)
    _require_non_empty_list(packet, "offline_validation_commands", errors)
    _validate_offline_commands(packet.get("offline_validation_commands"), errors)
    _reject_private_or_authenticated_facts(packet, errors)
    _reject_unlabelled_raw_injection_text(packet, errors)
    _reject_live_execution_claims(packet, errors)
    _reject_outcome_guarantees(packet, errors)
    _reject_enabled_consequential_controls(packet, errors)
    _reject_active_mutation_flags(packet, errors)

    return errors


def _validate_prompt_versions(packet: dict[str, Any], errors: list[str]) -> None:
    entries = packet.get("prompt_versions")
    if not isinstance(entries, list) or not entries:
        errors.append("prompt_versions must be a non-empty list")
        return

    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            errors.append(f"prompt_versions[{index}] must be an object")
            continue
        citations = entry.get("citations")
        if not isinstance(citations, list) or not citations:
            errors.append(f"prompt_versions[{index}] must include at least one citation")
            continue
        for citation_index, citation in enumerate(citations):
            if not isinstance(citation, dict):
                errors.append(f"prompt_versions[{index}].citations[{citation_index}] must be an object")
                continue
            source = citation.get("source") or citation.get("url") or citation.get("path")
            if not isinstance(source, str) or not source.strip():
                errors.append(f"prompt_versions[{index}].citations[{citation_index}] must include a source")


def _require_non_empty_list(packet: dict[str, Any], key: str, errors: list[str]) -> None:
    value = packet.get(key)
    if not isinstance(value, list) or not value:
        errors.append(f"{key} must be a non-empty list")


def _require_non_empty_string(packet: dict[str, Any], key: str, errors: list[str]) -> None:
    value = packet.get(key)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{key} must be a non-empty string")


def _validate_offline_commands(value: Any, errors: list[str]) -> None:
    if not isinstance(value, list):
        return
    for index, command in enumerate(value):
        if isinstance(command, list):
            if not command or not all(isinstance(part, str) and part.strip() for part in command):
                errors.append(f"offline_validation_commands[{index}] must contain non-empty string arguments")
            continue
        if not isinstance(command, str) or not command.strip():
            errors.append(f"offline_validation_commands[{index}] must be a non-empty command")


def _reject_private_or_authenticated_facts(packet: dict[str, Any], errors: list[str]) -> None:
    for path, value in _walk(packet):
        if isinstance(value, str) and _contains_any(value, PRIVATE_FACT_MARKERS):
            errors.append(f"{path} contains private or authenticated fact material")


def _reject_unlabelled_raw_injection_text(packet: dict[str, Any], errors: list[str]) -> None:
    for path, value in _walk(packet):
        if not isinstance(value, str) or not _contains_any(value, RAW_INJECTION_MARKERS):
            continue
        parent = _parent_for_path(packet, path)
        if not _is_fixture_labelled(parent):
            errors.append(f"{path} contains raw prompt injection text without fixture_label")


def _reject_live_execution_claims(packet: dict[str, Any], errors: list[str]) -> None:
    for path, value in _walk(packet):
        if isinstance(value, str) and _contains_any(value, LIVE_EXECUTION_MARKERS):
            errors.append(f"{path} claims live LLM, DevHub, crawler, or processor execution")


def _reject_outcome_guarantees(packet: dict[str, Any], errors: list[str]) -> None:
    for path, value in _walk(packet):
        if isinstance(value, str) and _contains_any(value, GUARANTEE_MARKERS):
            errors.append(f"{path} contains legal or permitting outcome guarantee")


def _reject_enabled_consequential_controls(packet: dict[str, Any], errors: list[str]) -> None:
    controls = packet.get("consequential_controls")
    if controls is None:
        return
    if not isinstance(controls, dict):
        errors.append("consequential_controls must be an object when present")
        return
    for key, value in controls.items():
        key_text = str(key).lower()
        if any(marker in key_text for marker in CONSEQUENTIAL_CONTROL_KEYS) and value is True:
            errors.append(f"consequential_controls.{key} must not be enabled")


def _reject_active_mutation_flags(packet: dict[str, Any], errors: list[str]) -> None:
    for path, value in _walk(packet):
        name = path.rsplit(".", 1)[-1].lower()
        if name in MUTATION_FLAG_NAMES and value is True:
            errors.append(f"{path} must not be active")


def _walk(value: Any, path: str = "packet") -> list[tuple[str, Any]]:
    items: list[tuple[str, Any]] = [(path, value)]
    if isinstance(value, dict):
        for key, child in value.items():
            items.extend(_walk(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            items.extend(_walk(child, f"{path}[{index}]"))
    return items


def _contains_any(value: str, markers: tuple[str, ...]) -> bool:
    lower_value = value.lower()
    return any(marker in lower_value for marker in markers)


def _is_fixture_labelled(value: Any) -> bool:
    if not isinstance(value, dict):
        return False
    label = value.get("fixture_label")
    if isinstance(label, str) and label.strip():
        return True
    return value.get("source_type") == "fixture"


def _parent_for_path(packet: dict[str, Any], path: str) -> Any:
    if path == "packet":
        return None
    current: Any = packet
    parts = path.removeprefix("packet.").split(".")
    for part in parts[:-1]:
        while "[" in part and part.endswith("]"):
            name, index_text = part[:-1].split("[", 1)
            if name:
                current = current[name]
            current = current[int(index_text)]
            part = ""
        if part:
            current = current[part]
    return current


__all__ = [
    "HandoffValidationError",
    "assert_valid_handoff_packet",
    "load_packet",
    "validate_handoff_packet",
]
