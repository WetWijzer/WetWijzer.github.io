"""Fixture-first surface-registry refresh acceptance packet v2 builder.

This module consumes committed packet fixtures only. It does not open DevHub,
read or create auth state, capture screenshots, traces, HAR files, or mutate the
surface registry. The output is a deterministic acceptance packet with cited
accepted, deferred, and rejected surface/action updates.
"""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any, Mapping

from ppd.devhub_attended_readonly_operator_transcript import validate_operator_transcript_packet
from ppd.surfaces.surface_registry_refresh_review_packet_v2 import (
    validate_surface_registry_refresh_review_packet_v2,
)

REQUIRED_ATTESTATIONS = (
    "no_live_devhub_observation",
    "no_auth_state_created_or_read",
    "no_screenshot_captured_or_stored",
    "no_trace_captured_or_stored",
    "no_har_captured_or_stored",
    "no_surface_registry_mutation",
)

OFFLINE_VALIDATION_COMMANDS = (
    ("python3", "-m", "pytest", "ppd/tests/test_surface_registry_refresh_acceptance_packet_v2.py"),
    ("python3", "ppd/daemon/ppd_daemon.py", "--self-test"),
)

_ALLOWED_DECISIONS = {"accepted", "deferred", "rejected"}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def build_from_fixture_paths(
    surface_registry_refresh_review_packet_path: Path,
    devhub_attended_readonly_observation_packet_path: Path,
    guardrail_bundle_refresh_candidate_path: Path,
) -> dict[str, Any]:
    return build_surface_registry_refresh_acceptance_packet_v2(
        load_json(surface_registry_refresh_review_packet_path),
        load_json(devhub_attended_readonly_observation_packet_path),
        load_json(guardrail_bundle_refresh_candidate_path),
    )


def build_surface_registry_refresh_acceptance_packet_v2(
    surface_registry_refresh_review_packet: Mapping[str, Any],
    devhub_attended_readonly_observation_packet: Mapping[str, Any],
    guardrail_bundle_refresh_candidate: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a deterministic acceptance packet from three reviewed fixtures."""

    review_errors = validate_surface_registry_refresh_review_packet_v2(surface_registry_refresh_review_packet)
    if review_errors:
        raise ValueError("surface-registry refresh review packet is invalid: " + "; ".join(review_errors))
    validate_operator_transcript_packet(devhub_attended_readonly_observation_packet)
    _validate_guardrail_candidate(guardrail_bundle_refresh_candidate)

    review_items = _require_list(surface_registry_refresh_review_packet.get("review_items"), "review_items")
    grouped_updates: dict[str, list[dict[str, Any]]] = {
        "accepted": [],
        "deferred": [],
        "rejected": [],
    }
    selector_dispositions: list[dict[str, Any]] = []
    manual_handoff_decisions: list[dict[str, Any]] = []
    redaction_gate_decisions: list[dict[str, Any]] = []

    reviewer_owner_fields = _merge_reviewer_owner_fields(
        surface_registry_refresh_review_packet,
        devhub_attended_readonly_observation_packet,
        guardrail_bundle_refresh_candidate,
    )

    for item in review_items:
        item_map = _require_mapping(item, "review_items[]")
        decision = _decision_for_item(item_map)
        update = {
            "update_id": _require_string(item_map.get("update_id") or item_map.get("item_id"), "update_id"),
            "surface_id": _require_string(item_map.get("surface_id"), "surface_id"),
            "action_id": _require_string(item_map.get("action_id"), "action_id"),
            "item_type": _require_string(item_map.get("item_type") or item_map.get("type"), "item_type"),
            "decision": decision,
            "rationale": _require_string(item_map.get("acceptance_rationale"), "acceptance_rationale"),
            "citations": _require_string_list(item_map.get("citations"), "citations"),
            "reviewer_owner": _require_string(item_map.get("reviewer_owner"), "reviewer_owner"),
            "implementation_owner": _require_string(item_map.get("implementation_owner"), "implementation_owner"),
            "rollback_note": _require_string(item_map.get("rollback_note"), "rollback_note"),
        }
        grouped_updates[decision].append(update)
        selector_dispositions.append(_selector_disposition_for_item(item_map, decision))
        manual_handoff_decisions.append(_manual_handoff_decision_for_item(item_map, decision))
        redaction_gate_decisions.append(_redaction_gate_decision_for_item(item_map, decision))

    packet = {
        "packet_type": "surface_registry_refresh_acceptance_packet_v2",
        "packet_version": 2,
        "packet_id": _packet_id(surface_registry_refresh_review_packet),
        "mode": "fixture_first_offline_acceptance",
        "consumes": {
            "surface_registry_refresh_review_packet_v2": _require_string(
                surface_registry_refresh_review_packet.get("packet_id"),
                "review packet_id",
            ),
            "devhub_attended_readonly_observation_packet_v2": _require_string(
                devhub_attended_readonly_observation_packet.get("packet_id")
                or devhub_attended_readonly_observation_packet.get("pilot_id"),
                "observation packet_id",
            ),
            "guardrail_bundle_refresh_candidate_v2": _require_string(
                guardrail_bundle_refresh_candidate.get("packet_id"),
                "guardrail candidate packet_id",
            ),
        },
        "surface_action_updates": grouped_updates,
        "selector_confidence_dispositions": selector_dispositions,
        "manual_handoff_decisions": manual_handoff_decisions,
        "redaction_gate_decisions": redaction_gate_decisions,
        "reviewer_owner_fields": reviewer_owner_fields,
        "rollback_notes": [update["rollback_note"] for updates in grouped_updates.values() for update in updates],
        "offline_validation_commands": [list(command) for command in OFFLINE_VALIDATION_COMMANDS],
        "attestations": {name: True for name in REQUIRED_ATTESTATIONS},
        "source_packets_redacted_snapshot": {
            "surface_registry_refresh_review_packet": deepcopy(dict(surface_registry_refresh_review_packet)),
            "devhub_attended_readonly_observation_packet": deepcopy(dict(devhub_attended_readonly_observation_packet)),
            "guardrail_bundle_refresh_candidate": deepcopy(dict(guardrail_bundle_refresh_candidate)),
        },
        "validation_status": "fixture_acceptance_packet_pending_reviewer_application",
    }
    validate_surface_registry_refresh_acceptance_packet_v2(packet)
    return packet


def validate_surface_registry_refresh_acceptance_packet_v2(packet: Mapping[str, Any]) -> None:
    if packet.get("packet_type") != "surface_registry_refresh_acceptance_packet_v2":
        raise ValueError("unexpected packet_type")
    if packet.get("packet_version") != 2:
        raise ValueError("packet_version must be 2")
    attestations = _require_mapping(packet.get("attestations"), "attestations")
    for attestation in REQUIRED_ATTESTATIONS:
        if attestations.get(attestation) is not True:
            raise ValueError(f"required attestation missing or false: {attestation}")
    updates = _require_mapping(packet.get("surface_action_updates"), "surface_action_updates")
    for decision in _ALLOWED_DECISIONS:
        _require_list(updates.get(decision), f"surface_action_updates.{decision}")
    if not any(updates[decision] for decision in _ALLOWED_DECISIONS):
        raise ValueError("surface_action_updates must include at least one update")
    for field in (
        "selector_confidence_dispositions",
        "manual_handoff_decisions",
        "redaction_gate_decisions",
        "rollback_notes",
        "offline_validation_commands",
    ):
        if not _require_list(packet.get(field), field):
            raise ValueError(f"{field} must not be empty")


def _validate_guardrail_candidate(packet: Mapping[str, Any]) -> None:
    if packet.get("packet_type") != "guardrail_bundle_refresh_candidate_v2":
        raise ValueError("guardrail candidate packet_type must be guardrail_bundle_refresh_candidate_v2")
    attestations = _require_mapping(packet.get("attestations"), "guardrail attestations")
    for key in (
        "no_live_llm",
        "no_devhub",
        "no_guardrail_state_mutation",
        "no_prompt_state_mutation",
        "no_release_state_mutation",
    ):
        if attestations.get(key) is not True:
            raise ValueError(f"guardrail candidate missing attestation: {key}")
    _require_list(packet.get("predicate_update_candidates"), "predicate_update_candidates")


def _decision_for_item(item: Mapping[str, Any]) -> str:
    decision = _require_string(item.get("acceptance_decision"), "acceptance_decision")
    if decision not in _ALLOWED_DECISIONS:
        raise ValueError(f"unsupported acceptance_decision: {decision}")
    return decision


def _selector_disposition_for_item(item: Mapping[str, Any], decision: str) -> dict[str, Any]:
    return {
        "selector_id": _require_string(item.get("selector_id"), "selector_id"),
        "surface_id": _require_string(item.get("surface_id"), "surface_id"),
        "confidence": _require_string(item.get("selector_confidence"), "selector_confidence"),
        "disposition": _require_string(item.get("selector_confidence_disposition"), "selector_confidence_disposition"),
        "acceptance_decision": decision,
        "citations": _require_string_list(item.get("citations"), "citations"),
    }


def _manual_handoff_decision_for_item(item: Mapping[str, Any], decision: str) -> dict[str, Any]:
    return {
        "surface_id": _require_string(item.get("surface_id"), "surface_id"),
        "action_id": _require_string(item.get("action_id"), "action_id"),
        "decision": _require_string(item.get("manual_handoff_decision"), "manual_handoff_decision"),
        "requires_attendance": item.get("requires_attendance") is True,
        "acceptance_decision": decision,
        "citations": _require_string_list(item.get("citations"), "citations"),
    }


def _redaction_gate_decision_for_item(item: Mapping[str, Any], decision: str) -> dict[str, Any]:
    return {
        "surface_id": _require_string(item.get("surface_id"), "surface_id"),
        "action_id": _require_string(item.get("action_id"), "action_id"),
        "decision": _require_string(item.get("redaction_gate_decision"), "redaction_gate_decision"),
        "private_values_allowed": False,
        "browser_artifacts_allowed": False,
        "acceptance_decision": decision,
        "citations": _require_string_list(item.get("citations"), "citations"),
    }


def _merge_reviewer_owner_fields(*packets: Mapping[str, Any]) -> dict[str, Any]:
    merged: dict[str, Any] = {}
    for packet in packets:
        fields = packet.get("reviewer_owner_fields")
        if isinstance(fields, Mapping):
            merged.update(dict(fields))
    for packet in packets:
        if packet.get("reviewer_owner"):
            merged.setdefault("reviewer_owner", packet["reviewer_owner"])
        if packet.get("implementation_owner"):
            merged.setdefault("implementation_owner", packet["implementation_owner"])
    if not merged.get("reviewer_owner"):
        raise ValueError("reviewer_owner_fields.reviewer_owner is required")
    if not merged.get("implementation_owner"):
        raise ValueError("reviewer_owner_fields.implementation_owner is required")
    return merged


def _packet_id(packet: Mapping[str, Any]) -> str:
    review_id = _require_string(packet.get("packet_id"), "review packet_id")
    return review_id.replace("review", "acceptance")


def _require_mapping(value: Any, field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field} must be a mapping")
    return value


def _require_list(value: Any, field: str) -> list[Any]:
    if not isinstance(value, list):
        raise ValueError(f"{field} must be a list")
    return value


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value


def _require_string_list(value: Any, field: str) -> list[str]:
    values = _require_list(value, field)
    strings = [_require_string(entry, f"{field}[]") for entry in values]
    if not strings:
        raise ValueError(f"{field} must not be empty")
    return strings
