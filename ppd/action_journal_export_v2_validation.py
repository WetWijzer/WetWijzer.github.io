"""Validation for PP&D action journal export packet v2.

The validator is intentionally schema-tolerant: packets may come from fixtures,
daemon proposals, or future export code, but the required safety evidence and
forbidden content rules are enforced consistently.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
import re
from typing import Any


REQUIRED_EVENT_TYPES = frozenset(
    {
        "export_started",
        "source_evidence_recorded",
        "redaction_checked",
        "validation_command_recorded",
        "manual_handoff_or_refusal_recorded",
        "export_finalized",
    }
)

SOURCE_REQUIRED_EVENT_TYPES = frozenset(
    {
        "source_evidence_recorded",
        "official_source_observed",
        "policy_source_observed",
        "requirement_source_observed",
        "manual_handoff_or_refusal_recorded",
        "refusal_recorded",
        "manual_handoff_recorded",
    }
)

FORBIDDEN_KEY_FRAGMENTS = tuple(
    fragment.lower()
    for fragment in (
        "credential",
        "password",
        "passwd",
        "secret",
        "token",
        "api_key",
        "apikey",
        "cookie",
        "auth_state",
        "storage_state",
        "session_state",
        "screenshot",
        "trace",
        "har",
        "payment",
        "card_number",
        "cvv",
        "private_value",
        "raw_download",
        "downloaded_document",
        "local_private_path",
    )
)

FORBIDDEN_STRING_PATTERNS = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\bBearer\s+[A-Za-z0-9._~+/=-]+",
        r"\bapi[_-]?key\s*[:=]",
        r"\bpassword\s*[:=]",
        r"\bsecret\s*[:=]",
        r"\bSet-Cookie\b",
        r"\bCookie\s*:",
        r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13})\b",
        r"(?:^|\s)/(?:home|Users)/[^\s]+",
        r"[A-Za-z]:\\\\Users\\\\[^\s]+",
        r"\b(?:screenshot|trace|har)\b[^\n]*(?:attached|captured|included|saved)",
        r"\braw download\b",
        r"\blive DevHub execution\b",
        r"\bofficial action (?:completed|submitted|filed|certified|approved)\b",
        r"\bguarantee(?:d|s)?\b[^\n]*(?:permit|permitting|legal|approval)",
    )
)

FORBIDDEN_CLAIM_PATTERNS = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\blive DevHub execution\b",
        r"\bsubmitted\s+(?:to|through)\s+DevHub\b",
        r"\bofficial action (?:completed|submitted|filed|certified|approved)\b",
        r"\bpermit(?:ting)?\s+(?:approval|issuance)\s+(?:is\s+)?guaranteed\b",
        r"\blegal\s+guarantee\b",
    )
)

MUTATION_FLAG_KEYS = frozenset(
    key.lower()
    for key in (
        "active_prompt_mutation",
        "prompt_mutation",
        "mutates_prompt",
        "active_guardrail_mutation",
        "guardrail_mutation",
        "mutates_guardrail",
        "active_source_mutation",
        "source_mutation",
        "mutates_source",
        "active_requirement_mutation",
        "requirement_mutation",
        "mutates_requirement",
        "active_process_model_mutation",
        "process_model_mutation",
        "mutates_process_model",
        "active_contract_mutation",
        "contract_mutation",
        "mutates_contract",
        "active_devhub_surface_mutation",
        "devhub_surface_mutation",
        "mutates_devhub_surface",
        "active_release_state_mutation",
        "release_state_mutation",
        "mutates_release_state",
    )
)


@dataclass(frozen=True)
class ValidationResult:
    ok: bool
    errors: tuple[str, ...]


def validate_action_journal_export_packet_v2(packet: Mapping[str, Any]) -> ValidationResult:
    """Return validation errors for an action journal export packet v2."""

    errors: list[str] = []

    if not isinstance(packet, Mapping):
        return ValidationResult(False, ("packet must be a mapping",))

    if packet.get("packet_version") != 2 and packet.get("version") != 2:
        errors.append("packet must declare version 2")

    events = _list_of_mappings(packet.get("events"))
    if not events:
        errors.append("packet must include events")
    else:
        present_event_types = {str(event.get("type", "")) for event in events}
        missing_event_types = sorted(REQUIRED_EVENT_TYPES - present_event_types)
        for event_type in missing_event_types:
            errors.append(f"missing required event type: {event_type}")

    evidence = _list_of_mappings(packet.get("source_evidence"))
    evidence_ids = {str(item.get("id")) for item in evidence if item.get("id")}
    if not evidence:
        errors.append("packet must include source_evidence")

    redaction_checks = _list_of_mappings(packet.get("redaction_checks"))
    if not redaction_checks:
        errors.append("packet must include redaction_checks")
    for index, check in enumerate(redaction_checks):
        if check.get("passed") is not True:
            errors.append(f"redaction check {index} must pass")

    validation_commands = packet.get("validation_commands")
    if not _valid_validation_commands(validation_commands):
        errors.append("packet must include non-empty validation_commands as argv lists")

    if not _has_manual_handoff_or_refusal_evidence(packet, events, evidence):
        errors.append("packet must include manual handoff or refusal evidence")

    for index, event in enumerate(events):
        event_type = str(event.get("type", ""))
        refs = _string_list(event.get("source_evidence_refs"))
        source_required = bool(event.get("requires_source_evidence")) or event_type in SOURCE_REQUIRED_EVENT_TYPES
        if source_required and not refs:
            errors.append(f"event {index} ({event_type}) is missing source_evidence_refs")
        for ref in refs:
            if ref not in evidence_ids:
                errors.append(f"event {index} ({event_type}) references unknown source evidence: {ref}")

    errors.extend(_find_forbidden_content(packet))
    errors.extend(_find_mutation_flags(packet))

    return ValidationResult(not errors, tuple(errors))


def assert_valid_action_journal_export_packet_v2(packet: Mapping[str, Any]) -> None:
    """Raise ValueError when a packet fails v2 validation."""

    result = validate_action_journal_export_packet_v2(packet)
    if not result.ok:
        raise ValueError("action journal export packet v2 validation failed: " + "; ".join(result.errors))


def _list_of_mappings(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str) and item]


def _valid_validation_commands(value: Any) -> bool:
    if not isinstance(value, list) or not value:
        return False
    for command in value:
        if not isinstance(command, list) or not command:
            return False
        if not all(isinstance(part, str) and part for part in command):
            return False
    return True


def _has_manual_handoff_or_refusal_evidence(
    packet: Mapping[str, Any], events: Sequence[Mapping[str, Any]], evidence: Sequence[Mapping[str, Any]]
) -> bool:
    direct = packet.get("manual_handoff_or_refusal_evidence")
    if isinstance(direct, Mapping) and direct:
        return True
    if isinstance(direct, list) and direct:
        return True

    evidence_types = {str(item.get("type", "")) for item in evidence}
    if evidence_types & {"manual_handoff", "refusal", "manual_handoff_or_refusal"}:
        return True

    event_types = {str(event.get("type", "")) for event in events}
    return bool(event_types & {"manual_handoff_recorded", "refusal_recorded", "manual_handoff_or_refusal_recorded"})


def _find_forbidden_content(value: Any) -> list[str]:
    errors: list[str] = []
    for path, item in _walk(value):
        if path:
            key = path[-1].lower()
            if any(fragment in key for fragment in FORBIDDEN_KEY_FRAGMENTS):
                errors.append(f"forbidden sensitive field present: {'.'.join(path)}")
        if isinstance(item, str):
            for pattern in FORBIDDEN_STRING_PATTERNS:
                if pattern.search(item):
                    errors.append(f"forbidden sensitive value or claim at: {'.'.join(path) or ''}")
                    break
            for pattern in FORBIDDEN_CLAIM_PATTERNS:
                if pattern.search(item):
                    errors.append(f"forbidden DevHub, official-action, legal, or permitting claim at: {'.'.join(path) or ''}")
                    break
    return errors


def _find_mutation_flags(value: Any) -> list[str]:
    errors: list[str] = []
    for path, item in _walk(value):
        if not path:
            continue
        key = path[-1].lower()
        if key in MUTATION_FLAG_KEYS and _truthy_flag(item):
            errors.append(f"forbidden active mutation flag: {'.'.join(path)}")
        if key == "active_mutation_flags" and isinstance(item, list) and item:
            errors.append(f"forbidden active mutation flags list: {'.'.join(path)}")
    return errors


def _truthy_flag(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "active", "enabled"}
    if isinstance(value, int):
        return value != 0
    return False


def _walk(value: Any, path: tuple[str, ...] = ()) -> Iterable[tuple[tuple[str, ...], Any]]:
    yield path, value
    if isinstance(value, Mapping):
        for key, child in value.items():
            yield from _walk(child, path + (str(key),))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk(child, path + (str(index),))
