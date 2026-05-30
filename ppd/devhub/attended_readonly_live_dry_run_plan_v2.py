"""Fixture-first attended DevHub read-only live-dry-run plan v2.

This module builds an offline plan from committed fixtures only. It does not
open DevHub, launch a browser, read or write authentication state, create
screenshots, traces, HAR files, or mutate the DevHub surface registry.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

from ppd.devhub.attended_readonly_runbook_refresh_packet_v2 import (
    validate_devhub_attended_readonly_runbook_refresh_packet_v2,
)
from ppd.devhub_attended_readonly_operator_transcript import validate_operator_transcript_packet


REQUIRED_ATTESTATIONS = {
    "no_live_devhub": True,
    "no_auth_state": True,
    "no_screenshot": True,
    "no_trace": True,
    "no_har": True,
    "no_surface_registry_mutation": True,
}

OFFLINE_VALIDATION_COMMANDS = [
    ["python3", "-m", "py_compile", "ppd/devhub/attended_readonly_live_dry_run_plan_v2.py"],
    ["python3", "-m", "pytest", "ppd/tests/test_devhub_attended_readonly_live_dry_run_plan_v2.py"],
]

DEFAULT_ABORT_CONDITIONS = [
    "Abort before any live DevHub navigation or browser launch.",
    "Abort if a credential, MFA, CAPTCHA, password recovery, account creation, or security prompt is encountered.",
    "Abort if a step would read, copy, persist, or summarize private account, permit, property, license, invoice, payment, or contact values.",
    "Abort if any screenshot, trace, HAR, video, browser profile, storage state, cookie, download, or private session file would be created or referenced.",
    "Abort before submission, certification, upload, payment, purchase, scheduling, cancellation, withdrawal, reactivation, save-draft, account setting, or other official action.",
    "Abort if an operator proposes a surface-registry, guardrail, prompt, monitoring, release-state, or agent-state mutation during this plan.",
]


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def build_from_fixture_paths(
    live_readiness_authorization_checklist_path: Path,
    attended_readonly_runbook_refresh_packet_path: Path,
    attended_readonly_observation_packet_path: Path,
) -> dict[str, Any]:
    return build_attended_readonly_live_dry_run_plan_v2(
        load_json(live_readiness_authorization_checklist_path),
        load_json(attended_readonly_runbook_refresh_packet_path),
        load_json(attended_readonly_observation_packet_path),
    )


def build_attended_readonly_live_dry_run_plan_v2(
    live_readiness_authorization_checklist: Mapping[str, Any],
    attended_readonly_runbook_refresh_packet: Mapping[str, Any],
    attended_readonly_observation_packet: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a deterministic attended DevHub read-only live-dry-run plan."""

    _validate_authorization_fixture(live_readiness_authorization_checklist)
    validate_devhub_attended_readonly_runbook_refresh_packet_v2(attended_readonly_runbook_refresh_packet)
    validate_operator_transcript_packet(attended_readonly_observation_packet)

    readiness_id = _packet_id(live_readiness_authorization_checklist, "live readiness authorization checklist")
    runbook_id = _packet_id(attended_readonly_runbook_refresh_packet, "runbook refresh packet")
    observation_id = _packet_id(attended_readonly_observation_packet, "observation packet")

    verification_steps = _verification_steps(attended_readonly_runbook_refresh_packet, runbook_id, observation_id)
    manual_boundaries = _manual_login_boundaries(attended_readonly_runbook_refresh_packet, readiness_id, runbook_id)
    redaction_items = _redaction_checklist_items(attended_readonly_runbook_refresh_packet, runbook_id)

    plan = {
        "plan_type": "devhub_attended_readonly_live_dry_run_plan_v2",
        "plan_version": 2,
        "plan_id": "devhub-attended-readonly-live-dry-run-plan-v2-fixture-20260529",
        "mode": "fixture_first_attended_devhub_readonly_live_dry_run_plan",
        "consumes": {
            "live_readiness_authorization_checklist_packet_v2": readiness_id,
            "attended_devhub_readonly_runbook_refresh_packet_v2": runbook_id,
            "devhub_attended_readonly_observation_packet_v2": observation_id,
        },
        "manual_login_mfa_captcha_boundaries": manual_boundaries,
        "allowed_read_only_verification_steps": verification_steps,
        "redaction_checklist_items": redaction_items,
        "operator_abort_conditions": _operator_abort_conditions(attended_readonly_runbook_refresh_packet, readiness_id, runbook_id),
        "offline_validation_commands": list(OFFLINE_VALIDATION_COMMANDS),
        "attestations": dict(REQUIRED_ATTESTATIONS),
        "source_packet_snapshots_redacted": {
            "live_readiness_authorization_checklist_packet_v2": {
                "packet_id": readiness_id,
                "authorization_prerequisite_count": len(_sequence(live_readiness_authorization_checklist.get("authorization_prerequisites"))),
                "live_boundary_decision_count": len(_sequence(live_readiness_authorization_checklist.get("live_boundary_decisions"))),
            },
            "attended_devhub_readonly_runbook_refresh_packet_v2": {
                "packet_id": runbook_id,
                "read_only_verification_step_count": len(verification_steps),
                "manual_boundary_count": len(manual_boundaries),
                "redaction_check_count": len(redaction_items),
            },
            "devhub_attended_readonly_observation_packet_v2": {
                "packet_id": observation_id,
                "observation_count": len(_sequence(attended_readonly_observation_packet.get("ordered_operator_observations"))),
            },
        },
        "validation_status": "fixture_live_dry_run_plan_pending_operator_authorization",
    }
    validate_attended_readonly_live_dry_run_plan_v2(plan)
    return plan


def validate_attended_readonly_live_dry_run_plan_v2(plan: Mapping[str, Any]) -> None:
    if plan.get("plan_type") != "devhub_attended_readonly_live_dry_run_plan_v2":
        raise ValueError("unexpected plan_type")
    if plan.get("plan_version") != 2:
        raise ValueError("plan_version must be 2")
    if plan.get("mode") != "fixture_first_attended_devhub_readonly_live_dry_run_plan":
        raise ValueError("unexpected plan mode")

    consumes = _mapping(plan.get("consumes"), "consumes")
    for key in (
        "live_readiness_authorization_checklist_packet_v2",
        "attended_devhub_readonly_runbook_refresh_packet_v2",
        "devhub_attended_readonly_observation_packet_v2",
    ):
        _non_empty_text(consumes.get(key), f"consumes.{key}")

    if _mapping(plan.get("attestations"), "attestations") != REQUIRED_ATTESTATIONS:
        raise ValueError("required DevHub live-dry-run attestations are missing or changed")

    for field in (
        "manual_login_mfa_captcha_boundaries",
        "allowed_read_only_verification_steps",
        "redaction_checklist_items",
        "operator_abort_conditions",
        "offline_validation_commands",
    ):
        if not _sequence(plan.get(field)):
            raise ValueError(f"{field} must be a non-empty list")

    for index, boundary in enumerate(_sequence(plan.get("manual_login_mfa_captcha_boundaries"))):
        item = _mapping(boundary, f"manual_login_mfa_captcha_boundaries[{index}]")
        if item.get("human_operator_required") is not True:
            raise ValueError("manual-login boundaries must require a human operator")
        for flag in ("agent_may_request_credentials", "agent_may_store_credentials", "agent_may_automate_mfa_or_captcha", "official_action_allowed_after_handoff"):
            if item.get(flag) is not False:
                raise ValueError(f"manual-login boundary must keep {flag} false")
        _require_citations(item, f"manual_login_mfa_captcha_boundaries[{index}]")

    for index, step in enumerate(_sequence(plan.get("allowed_read_only_verification_steps"))):
        item = _mapping(step, f"allowed_read_only_verification_steps[{index}]")
        if item.get("read_only") is not True:
            raise ValueError("verification steps must be read-only")
        for flag in ("official_action_allowed", "browser_automation_allowed", "auth_state_allowed", "private_values_allowed", "screenshot_trace_har_allowed"):
            if item.get(flag) is not False:
                raise ValueError(f"verification step must keep {flag} false")
        _require_citations(item, f"allowed_read_only_verification_steps[{index}]")

    for index, item_value in enumerate(_sequence(plan.get("redaction_checklist_items"))):
        item = _mapping(item_value, f"redaction_checklist_items[{index}]")
        if item.get("required") is not True:
            raise ValueError("redaction checklist items must be required")
        for flag in ("private_values_allowed", "raw_authenticated_values_allowed", "browser_artifacts_allowed"):
            if item.get(flag) is not False:
                raise ValueError(f"redaction checklist item must keep {flag} false")
        _require_citations(item, f"redaction_checklist_items[{index}]")

    for index, command in enumerate(_sequence(plan.get("offline_validation_commands"))):
        if not all(isinstance(part, str) and part for part in _sequence(command)):
            raise ValueError(f"offline_validation_commands[{index}] must be a list of strings")


def _validate_authorization_fixture(packet: Mapping[str, Any]) -> None:
    packet_id = _packet_id(packet, "live readiness authorization checklist")
    if packet.get("packet_type") not in {"live-readiness-authorization-checklist", None}:
        raise ValueError("authorization packet must be a live-readiness authorization checklist")
    if packet.get("approved_for_fixture_dry_run") is False:
        raise ValueError("authorization packet does not approve fixture dry-run planning")

    boundary_ids = {_text(item.get("id")) for item in _sequence(packet.get("live_boundary_decisions")) if isinstance(item, Mapping)}
    attestation_ids = {_text(item.get("id")) for item in _sequence(packet.get("attestations")) if isinstance(item, Mapping)}
    if boundary_ids and "boundary-devhub-read-only" not in boundary_ids:
        raise ValueError(f"{packet_id} must cite the attended DevHub read-only boundary")
    if attestation_ids and not {"no-live-devhub", "no-auth-state", "no-browser-artifact"}.issubset(attestation_ids):
        raise ValueError(f"{packet_id} is missing required DevHub artifact attestations")


def _verification_steps(packet: Mapping[str, Any], runbook_id: str, observation_id: str) -> list[dict[str, Any]]:
    steps: list[dict[str, Any]] = []
    for source_step in _sequence(packet.get("allowed_read_only_verification_steps")):
        step = _mapping(source_step, "allowed_read_only_verification_steps[]")
        steps.append(
            {
                "step_id": f"live-dry-run:{_non_empty_text(step.get('step_id'), 'step_id')}",
                "surface_id": _non_empty_text(step.get("surface_id"), "surface_id"),
                "action_id": _non_empty_text(step.get("action_id"), "action_id"),
                "read_only": True,
                "official_action_allowed": False,
                "browser_automation_allowed": False,
                "auth_state_allowed": False,
                "private_values_allowed": False,
                "screenshot_trace_har_allowed": False,
                "operator_instruction": "Verify only the redacted page shape or accessible label described by fixture evidence; do not record account-scoped values.",
                "allowed_evidence": [
                    "redacted generic surface label",
                    "cited fixture expectation",
                    "operator yes/no readiness note without private values",
                ],
                "citations": _string_list(step.get("citations"), "allowed_read_only_verification_steps[].citations") + [runbook_id, observation_id],
            }
        )
    return steps


def _manual_login_boundaries(packet: Mapping[str, Any], readiness_id: str, runbook_id: str) -> list[dict[str, Any]]:
    boundaries: list[dict[str, Any]] = []
    for source_boundary in _sequence(packet.get("manual_login_mfa_captcha_handoff_boundaries")):
        boundary = _mapping(source_boundary, "manual_login_mfa_captcha_handoff_boundaries[]")
        boundaries.append(
            {
                "boundary_id": f"live-dry-run:{_non_empty_text(boundary.get('boundary_id'), 'boundary_id')}",
                "trigger": _non_empty_text(boundary.get("trigger"), "trigger"),
                "human_operator_required": True,
                "agent_may_request_credentials": False,
                "agent_may_store_credentials": False,
                "agent_may_automate_mfa_or_captcha": False,
                "account_creation_allowed": False,
                "official_action_allowed_after_handoff": False,
                "operator_instruction": "Stop and keep the user in control of login, MFA, CAPTCHA, and any security prompt; this plan does not authorize continuing into live DevHub.",
                "citations": _string_list(boundary.get("citations"), "manual boundary citations") + [readiness_id, runbook_id],
            }
        )
    return boundaries


def _redaction_checklist_items(packet: Mapping[str, Any], runbook_id: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for source_item in _sequence(packet.get("redaction_requirements")):
        item = _mapping(source_item, "redaction_requirements[]")
        items.append(
            {
                "item_id": f"live-dry-run:{_non_empty_text(item.get('requirement_id'), 'requirement_id')}",
                "required": True,
                "private_values_allowed": False,
                "raw_authenticated_values_allowed": False,
                "browser_artifacts_allowed": False,
                "passes_when": _non_empty_text(item.get("passes_when") or item.get("decision"), "passes_when_or_decision"),
                "citations": _string_list(item.get("citations"), "redaction requirement citations") + [runbook_id],
            }
        )
    return items


def _operator_abort_conditions(packet: Mapping[str, Any], readiness_id: str, runbook_id: str) -> list[dict[str, Any]]:
    conditions = [
        {
            "condition_id": f"abort-default-{index:02d}",
            "condition": condition,
            "operator_action": "stop_and_record_redacted_offline_note_only",
            "citations": [readiness_id, runbook_id],
        }
        for index, condition in enumerate(DEFAULT_ABORT_CONDITIONS, start=1)
    ]
    for delta in _sequence(packet.get("operator_checklist_deltas")):
        item = _mapping(delta, "operator_checklist_deltas[]")
        if item.get("decision") == "rejected":
            conditions.append(
                {
                    "condition_id": f"abort-rejected:{_non_empty_text(item.get('action_id'), 'action_id')}",
                    "surface_id": _non_empty_text(item.get("surface_id"), "surface_id"),
                    "action_id": _non_empty_text(item.get("action_id"), "action_id"),
                    "condition": _non_empty_text(item.get("operator_checklist_text"), "operator_checklist_text"),
                    "operator_action": "stop_before_consequential_control",
                    "citations": _string_list(item.get("citations"), "rejected delta citations") + [runbook_id],
                }
            )
    return conditions


def _packet_id(packet: Mapping[str, Any], label: str) -> str:
    return _non_empty_text(packet.get("packet_id") or packet.get("pilot_id"), f"{label} packet_id")


def _mapping(value: Any, field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field} must be a mapping")
    return value


def _sequence(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    return []


def _string_list(value: Any, field: str) -> list[str]:
    values = [_non_empty_text(item, f"{field}[]") for item in _sequence(value)]
    if not values:
        raise ValueError(f"{field} must not be empty")
    return values


def _require_citations(item: Mapping[str, Any], field: str) -> None:
    _string_list(item.get("citations"), f"{field}.citations")


def _non_empty_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value


def _text(value: Any) -> str:
    return value if isinstance(value, str) else ""


def main() -> int:
    parser = argparse.ArgumentParser(description="Build fixture-first attended DevHub read-only live-dry-run plan v2")
    parser.add_argument("--authorization", required=True, type=Path)
    parser.add_argument("--runbook-refresh", required=True, type=Path)
    parser.add_argument("--observation", required=True, type=Path)
    args = parser.parse_args()
    plan = build_from_fixture_paths(args.authorization, args.runbook_refresh, args.observation)
    print(json.dumps(plan, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
