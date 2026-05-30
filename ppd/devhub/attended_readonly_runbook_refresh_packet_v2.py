"""Fixture-first DevHub attended read-only runbook refresh packet v2.

This module consumes committed fixtures only. It does not open DevHub, launch a
browser, read or write auth state, persist browser artifacts, or mutate any
runbook. The resulting packet is an operator-facing refresh proposal for the
attended read-only runbook.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from ppd.acceptance.surface_registry_refresh_acceptance_packet_v2 import (
    validate_surface_registry_refresh_acceptance_packet_v2,
)
from ppd.agent_readiness.devhub_attended_read_only_pilot import validate_launch_readiness_packet
from ppd.devhub_attended_readonly_operator_transcript import validate_operator_transcript_packet

REQUIRED_ATTESTATIONS = (
    "no_live_devhub_access",
    "no_auth_state_created_read_or_stored",
    "no_browser_artifact_created_or_stored",
    "no_runbook_mutation",
)

OFFLINE_VALIDATION_COMMANDS = (
    ("python3", "-m", "pytest", "ppd/tests/test_devhub_attended_readonly_runbook_refresh_packet_v2.py"),
    ("python3", "ppd/daemon/ppd_daemon.py", "--self-test"),
)

_ALLOWED_DELTA_DECISIONS = {"accepted", "deferred", "rejected"}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def build_from_fixture_paths(
    surface_registry_refresh_acceptance_packet_path: Path,
    devhub_attended_readonly_observation_packet_path: Path,
    launch_readiness_packet_path: Path,
) -> dict[str, Any]:
    return build_devhub_attended_readonly_runbook_refresh_packet_v2(
        load_json(surface_registry_refresh_acceptance_packet_path),
        load_json(devhub_attended_readonly_observation_packet_path),
        load_json(launch_readiness_packet_path),
    )


def build_devhub_attended_readonly_runbook_refresh_packet_v2(
    surface_registry_refresh_acceptance_packet: Mapping[str, Any],
    devhub_attended_readonly_observation_packet: Mapping[str, Any],
    launch_readiness_packet: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a deterministic runbook refresh packet from committed fixtures."""

    validate_surface_registry_refresh_acceptance_packet_v2(surface_registry_refresh_acceptance_packet)
    validate_operator_transcript_packet(devhub_attended_readonly_observation_packet)
    validate_launch_readiness_packet(launch_readiness_packet)

    reviewer_owner_fields = _merge_reviewer_owner_fields(
        surface_registry_refresh_acceptance_packet,
        devhub_attended_readonly_observation_packet,
        launch_readiness_packet,
    )
    grouped_updates = _require_mapping(
        surface_registry_refresh_acceptance_packet.get("surface_action_updates"),
        "surface_action_updates",
    )
    redaction_gate_decisions = _require_list(
        surface_registry_refresh_acceptance_packet.get("redaction_gate_decisions"),
        "redaction_gate_decisions",
    )
    manual_handoff_decisions = _require_list(
        surface_registry_refresh_acceptance_packet.get("manual_handoff_decisions"),
        "manual_handoff_decisions",
    )
    redaction_checklist_items = _require_list(
        launch_readiness_packet.get("redaction_checklist_items"),
        "redaction_checklist_items",
    )
    manual_stop_points = _require_list(launch_readiness_packet.get("manual_stop_points"), "manual_stop_points")

    packet = {
        "packet_type": "devhub_attended_readonly_runbook_refresh_packet_v2",
        "packet_version": 2,
        "packet_id": "devhub-attended-readonly-runbook-refresh-packet-v2-fixture-20260529",
        "mode": "fixture_first_offline_runbook_refresh",
        "consumes": {
            "surface_registry_refresh_acceptance_packet_v2": _require_string(
                surface_registry_refresh_acceptance_packet.get("packet_id"),
                "surface acceptance packet_id",
            ),
            "devhub_attended_readonly_observation_packet_v2": _require_string(
                devhub_attended_readonly_observation_packet.get("packet_id")
                or devhub_attended_readonly_observation_packet.get("pilot_id"),
                "observation packet_id",
            ),
            "devhub_attended_readonly_launch_readiness_packet": _require_string(
                launch_readiness_packet.get("packet_id"),
                "launch readiness packet_id",
            ),
        },
        "operator_checklist_deltas": _operator_checklist_deltas(grouped_updates),
        "allowed_read_only_verification_steps": _allowed_read_only_verification_steps(grouped_updates),
        "manual_login_mfa_captcha_handoff_boundaries": _manual_handoff_boundaries(
            manual_stop_points,
            manual_handoff_decisions,
        ),
        "redaction_requirements": _redaction_requirements(redaction_checklist_items, redaction_gate_decisions),
        "reviewer_owner_fields": reviewer_owner_fields,
        "offline_validation_commands": [list(command) for command in OFFLINE_VALIDATION_COMMANDS],
        "attestations": {name: True for name in REQUIRED_ATTESTATIONS},
        "source_packet_snapshots_redacted": {
            "surface_registry_refresh_acceptance_packet": {
                "packet_id": surface_registry_refresh_acceptance_packet.get("packet_id"),
                "surface_action_update_counts": {
                    decision: len(_require_list(grouped_updates.get(decision), f"surface_action_updates.{decision}"))
                    for decision in sorted(_ALLOWED_DELTA_DECISIONS)
                },
            },
            "devhub_attended_readonly_observation_packet": {
                "packet_id": devhub_attended_readonly_observation_packet.get("packet_id")
                or devhub_attended_readonly_observation_packet.get("pilot_id"),
                "observation_count": len(
                    _require_list(
                        devhub_attended_readonly_observation_packet.get("ordered_operator_observations"),
                        "ordered_operator_observations",
                    )
                ),
            },
            "launch_readiness_packet": {
                "packet_id": launch_readiness_packet.get("packet_id"),
                "manual_stop_point_count": len(manual_stop_points),
                "redaction_check_count": len(redaction_checklist_items),
            },
        },
        "validation_status": "fixture_runbook_refresh_packet_pending_reviewer_application",
    }
    validate_devhub_attended_readonly_runbook_refresh_packet_v2(packet)
    return packet


def validate_devhub_attended_readonly_runbook_refresh_packet_v2(packet: Mapping[str, Any]) -> None:
    if packet.get("packet_type") != "devhub_attended_readonly_runbook_refresh_packet_v2":
        raise ValueError("unexpected packet_type")
    if packet.get("packet_version") != 2:
        raise ValueError("packet_version must be 2")
    if packet.get("mode") != "fixture_first_offline_runbook_refresh":
        raise ValueError("mode must be fixture_first_offline_runbook_refresh")

    consumes = _require_mapping(packet.get("consumes"), "consumes")
    for key in (
        "surface_registry_refresh_acceptance_packet_v2",
        "devhub_attended_readonly_observation_packet_v2",
        "devhub_attended_readonly_launch_readiness_packet",
    ):
        _require_string(consumes.get(key), f"consumes.{key}")

    attestations = _require_mapping(packet.get("attestations"), "attestations")
    for attestation in REQUIRED_ATTESTATIONS:
        if attestations.get(attestation) is not True:
            raise ValueError(f"required attestation missing or false: {attestation}")

    for field in (
        "operator_checklist_deltas",
        "allowed_read_only_verification_steps",
        "manual_login_mfa_captcha_handoff_boundaries",
        "redaction_requirements",
        "offline_validation_commands",
    ):
        if not _require_list(packet.get(field), field):
            raise ValueError(f"{field} must not be empty")

    _require_mapping(packet.get("reviewer_owner_fields"), "reviewer_owner_fields")
    _validate_cited_entries(packet["operator_checklist_deltas"], "operator_checklist_deltas")
    _validate_cited_entries(packet["allowed_read_only_verification_steps"], "allowed_read_only_verification_steps")
    _validate_cited_entries(packet["manual_login_mfa_captcha_handoff_boundaries"], "manual_login_mfa_captcha_handoff_boundaries")
    _validate_cited_entries(packet["redaction_requirements"], "redaction_requirements")

    for step in packet["allowed_read_only_verification_steps"]:
        step_map = _require_mapping(step, "allowed_read_only_verification_steps[]")
        if step_map.get("read_only") is not True:
            raise ValueError("allowed read-only verification steps must be marked read_only")
        if step_map.get("official_action_allowed") is not False:
            raise ValueError("allowed read-only verification steps cannot allow official actions")

    for boundary in packet["manual_login_mfa_captcha_handoff_boundaries"]:
        boundary_map = _require_mapping(boundary, "manual_login_mfa_captcha_handoff_boundaries[]")
        if boundary_map.get("human_operator_required") is not True:
            raise ValueError("manual handoff boundaries must require a human operator")
        if boundary_map.get("agent_may_request_credentials") is not False:
            raise ValueError("manual handoff boundaries cannot allow credential requests")
        if boundary_map.get("agent_may_automate_mfa_or_captcha") is not False:
            raise ValueError("manual handoff boundaries cannot allow MFA or CAPTCHA automation")

    for requirement in packet["redaction_requirements"]:
        requirement_map = _require_mapping(requirement, "redaction_requirements[]")
        if requirement_map.get("required") is not True:
            raise ValueError("redaction requirements must be required")
        if requirement_map.get("private_values_allowed") is not False:
            raise ValueError("redaction requirements cannot allow private values")
        if requirement_map.get("browser_artifacts_allowed") is not False:
            raise ValueError("redaction requirements cannot allow browser artifacts")


def _operator_checklist_deltas(grouped_updates: Mapping[str, Any]) -> list[dict[str, Any]]:
    deltas: list[dict[str, Any]] = []
    delta_by_decision = {
        "accepted": "add_read_only_operator_checklist_item",
        "deferred": "add_attended_selector_confirmation_checkpoint",
        "rejected": "add_refusal_boundary_for_consequential_control",
    }
    for decision in ("accepted", "deferred", "rejected"):
        for update in _require_list(grouped_updates.get(decision), f"surface_action_updates.{decision}"):
            update_map = _require_mapping(update, "surface_action_updates[]")
            deltas.append(
                {
                    "delta_id": f"runbook-delta:{_require_string(update_map.get('update_id'), 'update_id')}",
                    "decision": decision,
                    "delta_type": delta_by_decision[decision],
                    "surface_id": _require_string(update_map.get("surface_id"), "surface_id"),
                    "action_id": _require_string(update_map.get("action_id"), "action_id"),
                    "operator_checklist_text": _operator_delta_text(update_map, decision),
                    "reviewer_owner": _require_string(update_map.get("reviewer_owner"), "reviewer_owner"),
                    "implementation_owner": _require_string(update_map.get("implementation_owner"), "implementation_owner"),
                    "citations": _require_string_list(update_map.get("citations"), "citations"),
                }
            )
    return deltas


def _operator_delta_text(update: Mapping[str, Any], decision: str) -> str:
    surface_id = _require_string(update.get("surface_id"), "surface_id")
    action_id = _require_string(update.get("action_id"), "action_id")
    if decision == "accepted":
        return f"Add read-only verification for {surface_id} / {action_id}; record only cited redacted metadata."
    if decision == "deferred":
        return f"Add a reviewer checkpoint for {surface_id} / {action_id}; do not apply selector changes until attended confirmation is accepted."
    return f"Add a refusal boundary for {surface_id} / {action_id}; keep consequential controls outside runbook automation."


def _allowed_read_only_verification_steps(grouped_updates: Mapping[str, Any]) -> list[dict[str, Any]]:
    steps: list[dict[str, Any]] = []
    for decision in ("accepted", "deferred"):
        for update in _require_list(grouped_updates.get(decision), f"surface_action_updates.{decision}"):
            update_map = _require_mapping(update, "surface_action_updates[]")
            steps.append(
                {
                    "step_id": f"verify:{_require_string(update_map.get('update_id'), 'update_id')}",
                    "surface_id": _require_string(update_map.get("surface_id"), "surface_id"),
                    "action_id": _require_string(update_map.get("action_id"), "action_id"),
                    "read_only": True,
                    "official_action_allowed": False,
                    "allowed_operator_actions": [
                        "observe page heading or landmark label",
                        "compare redacted label against cited fixture expectation",
                        "record reviewer decision without private values",
                    ],
                    "requires_attended_reviewer": True,
                    "citations": _require_string_list(update_map.get("citations"), "citations"),
                }
            )
    return steps


def _manual_handoff_boundaries(
    manual_stop_points: list[Any],
    manual_handoff_decisions: list[Any],
) -> list[dict[str, Any]]:
    boundaries = [
        {
            "boundary_id": "manual-login-mfa-captcha-boundary",
            "trigger": "DevHub login, credentials, MFA, CAPTCHA, password recovery, account creation, or security prompts appear.",
            "human_operator_required": True,
            "agent_may_request_credentials": False,
            "agent_may_store_credentials": False,
            "agent_may_automate_mfa_or_captcha": False,
            "account_creation_allowed": False,
            "official_action_allowed_after_handoff": False,
            "citations": _collect_citations(manual_stop_points),
        }
    ]
    for decision in manual_handoff_decisions:
        decision_map = _require_mapping(decision, "manual_handoff_decisions[]")
        boundaries.append(
            {
                "boundary_id": f"handoff:{_require_string(decision_map.get('action_id'), 'action_id')}",
                "trigger": _require_string(decision_map.get("decision"), "manual_handoff_decision"),
                "surface_id": _require_string(decision_map.get("surface_id"), "surface_id"),
                "action_id": _require_string(decision_map.get("action_id"), "action_id"),
                "human_operator_required": True,
                "agent_may_request_credentials": False,
                "agent_may_store_credentials": False,
                "agent_may_automate_mfa_or_captcha": False,
                "account_creation_allowed": False,
                "official_action_allowed_after_handoff": False,
                "citations": _require_string_list(decision_map.get("citations"), "citations"),
            }
        )
    return boundaries


def _redaction_requirements(
    redaction_checklist_items: list[Any],
    redaction_gate_decisions: list[Any],
) -> list[dict[str, Any]]:
    requirements: list[dict[str, Any]] = []
    for item in redaction_checklist_items:
        item_map = _require_mapping(item, "redaction_checklist_items[]")
        requirements.append(
            {
                "requirement_id": f"redaction:{_require_string(item_map.get('check_id'), 'check_id')}",
                "required": True,
                "private_values_allowed": False,
                "browser_artifacts_allowed": False,
                "raw_authenticated_values_allowed": False,
                "passes_when": _require_string(item_map.get("passes_when"), "passes_when"),
                "citations": _require_string_list(item_map.get("citations"), "citations"),
            }
        )
    for decision in redaction_gate_decisions:
        decision_map = _require_mapping(decision, "redaction_gate_decisions[]")
        requirements.append(
            {
                "requirement_id": f"redaction-gate:{_require_string(decision_map.get('action_id'), 'action_id')}",
                "required": True,
                "surface_id": _require_string(decision_map.get("surface_id"), "surface_id"),
                "action_id": _require_string(decision_map.get("action_id"), "action_id"),
                "private_values_allowed": False,
                "browser_artifacts_allowed": False,
                "raw_authenticated_values_allowed": False,
                "decision": _require_string(decision_map.get("decision"), "redaction_gate_decision"),
                "citations": _require_string_list(decision_map.get("citations"), "citations"),
            }
        )
    return requirements


def _merge_reviewer_owner_fields(*packets: Mapping[str, Any]) -> dict[str, Any]:
    merged: dict[str, Any] = {}
    for packet in packets:
        fields = packet.get("reviewer_owner_fields")
        if isinstance(fields, Mapping):
            merged.update(dict(fields))
    for key in ("reviewer_owner", "implementation_owner", "safety_owner"):
        if not _require_string(merged.get(key), f"reviewer_owner_fields.{key}"):
            raise ValueError(f"reviewer_owner_fields.{key} is required")
    return merged


def _collect_citations(items: list[Any]) -> list[str]:
    citations: list[str] = []
    for item in items:
        if isinstance(item, Mapping):
            for citation in item.get("citations", []):
                if isinstance(citation, str) and citation not in citations:
                    citations.append(citation)
    if not citations:
        raise ValueError("manual handoff citations are required")
    return citations


def _validate_cited_entries(entries: list[Any], field: str) -> None:
    for index, entry in enumerate(entries):
        entry_map = _require_mapping(entry, f"{field}[]")
        _require_string_list(entry_map.get("citations"), f"{field}[{index}].citations")


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
