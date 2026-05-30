"""Fixture-first authorization checklist packet validation for PP&D live readiness.

This module is intentionally side-effect free. It validates committed checklist
fixtures and does not crawl, open browsers, read DevHub state, or create auth
artifacts.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence


PACKET_TYPE = "live-readiness-authorization-checklist"
PACKET_VERSION = "v2"
REQUIRED_CONSUMED_PACKET_IDS = frozenset(
    {
        "live-readiness-gate-review-packet-v2",
        "public-recrawl-operator-packet-v2",
        "attended-devhub-read-only-runbook-refresh-packet-v2",
    }
)
REQUIRED_ATTESTATION_IDS = frozenset(
    {
        "no-live-crawl",
        "no-live-devhub",
        "no-auth-state",
        "no-browser-artifact",
        "no-official-action",
    }
)
REQUIRED_TOP_LEVEL_LISTS = (
    "consumes",
    "authorization_prerequisites",
    "fixture_gap_closures",
    "live_boundary_decisions",
    "operator_signoff_fields",
    "offline_validation_commands",
    "attestations",
)


@dataclass(frozen=True)
class ValidationResult:
    """Deterministic validation result for a committed checklist packet."""

    ok: bool
    errors: tuple[str, ...]


def validate_authorization_checklist_packet(packet: Mapping[str, Any]) -> ValidationResult:
    """Validate the live-readiness authorization checklist packet contract."""

    errors: list[str] = []

    if packet.get("packet_type") != PACKET_TYPE:
        errors.append("packet_type must be live-readiness-authorization-checklist")
    if packet.get("version") != PACKET_VERSION:
        errors.append("version must be v2")

    for key in REQUIRED_TOP_LEVEL_LISTS:
        if not isinstance(packet.get(key), list) or not packet.get(key):
            errors.append(f"{key} must be a non-empty list")

    consumed_ids = _ids_from(packet.get("consumes", []), "packet_id")
    missing_consumed = REQUIRED_CONSUMED_PACKET_IDS.difference(consumed_ids)
    if missing_consumed:
        errors.append("missing consumed packets: " + ", ".join(sorted(missing_consumed)))

    _validate_cited_prerequisites(packet.get("authorization_prerequisites", []), errors)
    _validate_fixture_gap_closures(packet.get("fixture_gap_closures", []), consumed_ids, errors)
    _validate_live_boundary_decisions(packet.get("live_boundary_decisions", []), errors)
    _validate_operator_signoff_fields(packet.get("operator_signoff_fields", []), errors)
    _validate_offline_validation_commands(packet.get("offline_validation_commands", []), errors)
    _validate_attestations(packet.get("attestations", []), errors)

    return ValidationResult(ok=not errors, errors=tuple(errors))


def required_authorization_prerequisite_ids(packet: Mapping[str, Any]) -> tuple[str, ...]:
    """Return prerequisite ids in fixture order for reviewer checklists."""

    return tuple(
        str(item.get("id"))
        for item in packet.get("authorization_prerequisites", [])
        if isinstance(item, Mapping) and item.get("id")
    )


def required_signoff_field_ids(packet: Mapping[str, Any]) -> tuple[str, ...]:
    """Return required operator signoff field ids in fixture order."""

    return tuple(
        str(item.get("field_id"))
        for item in packet.get("operator_signoff_fields", [])
        if isinstance(item, Mapping) and item.get("required") is True and item.get("field_id")
    )


def _ids_from(items: Any, key: str) -> set[str]:
    if not isinstance(items, Iterable) or isinstance(items, (str, bytes)):
        return set()
    ids: set[str] = set()
    for item in items:
        if isinstance(item, Mapping) and item.get(key):
            ids.add(str(item[key]))
    return ids


def _non_empty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _non_empty_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value)


def _validate_cited_prerequisites(items: Any, errors: list[str]) -> None:
    if not isinstance(items, Sequence) or isinstance(items, (str, bytes)):
        return
    for index, item in enumerate(items):
        if not isinstance(item, Mapping):
            errors.append(f"authorization_prerequisites[{index}] must be an object")
            continue
        if not _non_empty_text(item.get("id")):
            errors.append(f"authorization_prerequisites[{index}] missing id")
        if not _non_empty_text(item.get("reviewer_action")):
            errors.append(f"authorization_prerequisites[{index}] missing reviewer_action")
        if not _non_empty_list(item.get("citation_refs")):
            errors.append(f"authorization_prerequisites[{index}] must include citation_refs")
        if not _non_empty_list(item.get("required_evidence_ids")):
            errors.append(f"authorization_prerequisites[{index}] must include required_evidence_ids")


def _validate_fixture_gap_closures(items: Any, consumed_ids: set[str], errors: list[str]) -> None:
    if not isinstance(items, Sequence) or isinstance(items, (str, bytes)):
        return
    covered: set[str] = set()
    for index, item in enumerate(items):
        if not isinstance(item, Mapping):
            errors.append(f"fixture_gap_closures[{index}] must be an object")
            continue
        covered_packet = item.get("covers_consumed_packet")
        if isinstance(covered_packet, str):
            covered.add(covered_packet)
        if not _non_empty_text(item.get("closure_fixture")):
            errors.append(f"fixture_gap_closures[{index}] missing closure_fixture")
        if item.get("review_status") != "ready_for_reviewer_authorization":
            errors.append(f"fixture_gap_closures[{index}] must be ready_for_reviewer_authorization")
    missing = consumed_ids.difference(covered)
    if missing:
        errors.append("fixture gaps do not cover consumed packets: " + ", ".join(sorted(missing)))


def _validate_live_boundary_decisions(items: Any, errors: list[str]) -> None:
    if not isinstance(items, Sequence) or isinstance(items, (str, bytes)):
        return
    allowed_decisions = {"fixture_only", "reviewer_authorization_required", "prohibited_without_new_packet"}
    for index, item in enumerate(items):
        if not isinstance(item, Mapping):
            errors.append(f"live_boundary_decisions[{index}] must be an object")
            continue
        if item.get("decision") not in allowed_decisions:
            errors.append(f"live_boundary_decisions[{index}] has unsupported decision")
        if not _non_empty_list(item.get("prohibited_scope")):
            errors.append(f"live_boundary_decisions[{index}] must list prohibited_scope")
        if not _non_empty_list(item.get("citation_refs")):
            errors.append(f"live_boundary_decisions[{index}] must include citation_refs")


def _validate_operator_signoff_fields(items: Any, errors: list[str]) -> None:
    if not isinstance(items, Sequence) or isinstance(items, (str, bytes)):
        return
    required_count = 0
    for index, item in enumerate(items):
        if not isinstance(item, Mapping):
            errors.append(f"operator_signoff_fields[{index}] must be an object")
            continue
        if item.get("required") is True:
            required_count += 1
        if item.get("blank_value") not in (None, ""):
            errors.append(f"operator_signoff_fields[{index}] must keep blank_value empty in fixture")
        if not _non_empty_text(item.get("confirmation_text")):
            errors.append(f"operator_signoff_fields[{index}] missing confirmation_text")
    if required_count == 0:
        errors.append("at least one required operator signoff field is needed")


def _validate_offline_validation_commands(items: Any, errors: list[str]) -> None:
    if not isinstance(items, Sequence) or isinstance(items, (str, bytes)):
        return
    for index, command in enumerate(items):
        if not isinstance(command, list) or not command:
            errors.append(f"offline_validation_commands[{index}] must be a non-empty argv list")
            continue
        command_text = " ".join(str(part).lower() for part in command)
        forbidden = ("crawl", "playwright", "browser", "devhub", "login", "auth")
        if any(token in command_text for token in forbidden):
            errors.append(f"offline_validation_commands[{index}] must remain offline and fixture-only")


def _validate_attestations(items: Any, errors: list[str]) -> None:
    attestation_ids = _ids_from(items, "id")
    missing = REQUIRED_ATTESTATION_IDS.difference(attestation_ids)
    if missing:
        errors.append("missing attestations: " + ", ".join(sorted(missing)))
    if not isinstance(items, Sequence) or isinstance(items, (str, bytes)):
        return
    for index, item in enumerate(items):
        if not isinstance(item, Mapping):
            errors.append(f"attestations[{index}] must be an object")
            continue
        if item.get("status") != "attested_in_fixture":
            errors.append(f"attestations[{index}] must be attested_in_fixture")
        if not _non_empty_text(item.get("statement")):
            errors.append(f"attestations[{index}] missing statement")
