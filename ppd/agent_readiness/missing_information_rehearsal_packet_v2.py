from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

PACKET_TYPE = "ppd.fixture_first_agent_missing_information_rehearsal.v2"
REQUIRED_WORKFLOWS = {"building", "trade", "solar", "demolition", "sign", "urban_forestry", "corrections"}
REQUIRED_CASE_FIELDS = (
    "case_id",
    "workflow",
    "synthetic_user_case",
    "known_fact_keys",
    "missing_facts",
    "missing_documents",
    "stale_evidence",
    "conflicting_evidence",
    "required_confirmations",
    "blocked_actions",
    "next_safe_actions",
    "citation_references",
    "reviewer_disposition_placeholder",
    "offline_validation_commands",
)
REQUIRED_BOUNDARY_FLAGS = (
    "no_private_user_facts",
    "no_live_devhub_access",
    "no_form_filling",
    "no_uploads",
    "no_submissions",
    "no_certifications",
    "no_payments",
    "no_inspection_scheduling",
    "no_active_prompt_changes",
    "no_active_guardrail_changes",
    "no_active_process_model_changes",
    "no_active_requirement_changes",
    "no_active_contract_changes",
    "no_active_source_changes",
    "no_devhub_surface_changes",
    "no_release_state_changes",
)
REQUIRED_COMMAND = ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]
PRIVATE_KEYS = {
    "address",
    "applicant_name",
    "auth_state",
    "card_number",
    "cookie",
    "credential",
    "cvv",
    "devhub_session",
    "email",
    "owner_name",
    "password",
    "payment_detail",
    "permit_number",
    "phone",
    "private_path",
    "session_state",
    "site_address",
    "storage_state",
    "tax_account",
    "token",
    "trace",
}
PRIVATE_MARKERS = ("/home/", "/Users/", "C:/Users/", "C:\\Users\\", "auth_state", "cookie", "password", "trace.zip")
UNSAFE_SAFE_ACTION_FLAGS = ("requires_devhub", "fills_form", "uploads", "submits", "pays_fee", "schedules_inspection")


class MissingInformationRehearsalPacketV2Error(ValueError):
    def __init__(self, errors: Sequence[str]) -> None:
        self.errors = tuple(errors)
        super().__init__("invalid missing-information rehearsal packet v2: " + "; ".join(self.errors))


def load_missing_information_rehearsal_packet_v2(path: Path) -> dict[str, Any]:
    packet = json.loads(path.read_text(encoding="utf-8"))
    assert_valid_missing_information_rehearsal_packet_v2(packet)
    return packet


def assert_valid_missing_information_rehearsal_packet_v2(packet: Mapping[str, Any]) -> None:
    errors = validate_missing_information_rehearsal_packet_v2(packet)
    if errors:
        raise MissingInformationRehearsalPacketV2Error(errors)


def validate_missing_information_rehearsal_packet_v2(packet: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if packet.get("packet_type") != PACKET_TYPE:
        errors.append(f"packet_type must be {PACKET_TYPE}")
    if packet.get("packet_version") != "v2":
        errors.append("packet_version must be v2")
    if packet.get("mode") != "offline_fixture_rehearsal_only":
        errors.append("mode must be offline_fixture_rehearsal_only")
    if packet.get("fixture_first") is not True:
        errors.append("fixture_first must be true")

    boundaries = packet.get("boundaries")
    if not isinstance(boundaries, Mapping):
        errors.append("boundaries must be an object")
    else:
        for flag in REQUIRED_BOUNDARY_FLAGS:
            if boundaries.get(flag) is not True:
                errors.append(f"boundaries.{flag} must be true")

    if packet.get("validation_commands") != [REQUIRED_COMMAND]:
        errors.append("validation_commands must contain the exact offline self-test command")

    cases = packet.get("synthetic_user_cases")
    if not isinstance(cases, list) or not cases:
        errors.append("synthetic_user_cases must be a non-empty list")
        cases = []

    workflows_seen: set[str] = set()
    for index, case in enumerate(cases):
        path = f"synthetic_user_cases[{index}]"
        if not isinstance(case, Mapping):
            errors.append(f"{path} must be an object")
            continue
        workflows_seen.add(str(case.get("workflow")))
        errors.extend(_validate_case(case, path))

    missing_workflows = REQUIRED_WORKFLOWS - workflows_seen
    if missing_workflows:
        errors.append("missing required workflows: " + ", ".join(sorted(missing_workflows)))
    errors.extend(_scan_for_private_content(packet))
    return errors


def _validate_case(case: Mapping[str, Any], path: str) -> list[str]:
    errors: list[str] = []
    for field in REQUIRED_CASE_FIELDS:
        if field not in case:
            errors.append(f"{path}.{field} is required")
    if case.get("workflow") not in REQUIRED_WORKFLOWS:
        errors.append(f"{path}.workflow must be one of the required workflows")
    for field in ("known_fact_keys", "missing_facts", "missing_documents", "required_confirmations", "blocked_actions", "next_safe_actions", "citation_references"):
        if not isinstance(case.get(field), list) or not case.get(field):
            errors.append(f"{path}.{field} must be a non-empty list")
    for field in ("stale_evidence", "conflicting_evidence"):
        if not isinstance(case.get(field), list):
            errors.append(f"{path}.{field} must be a list")
    for index, action in enumerate(case.get("blocked_actions", [])):
        if not isinstance(action, Mapping):
            errors.append(f"{path}.blocked_actions[{index}] must be an object")
        elif action.get("blocked") is not True or action.get("requires_confirmation_before_unblock") is not True:
            errors.append(f"{path}.blocked_actions[{index}] must stay blocked and confirmation-gated")
    for index, action in enumerate(case.get("next_safe_actions", [])):
        if not isinstance(action, Mapping):
            errors.append(f"{path}.next_safe_actions[{index}] must be an object")
            continue
        for flag in UNSAFE_SAFE_ACTION_FLAGS:
            if action.get(flag) is not False:
                errors.append(f"{path}.next_safe_actions[{index}].{flag} must be false")
    placeholder = case.get("reviewer_disposition_placeholder")
    if not isinstance(placeholder, Mapping) or placeholder.get("status") != "pending_human_review":
        errors.append(f"{path}.reviewer_disposition_placeholder.status must be pending_human_review")
    if case.get("offline_validation_commands") != [REQUIRED_COMMAND]:
        errors.append(f"{path}.offline_validation_commands must contain the exact offline self-test command")
    return errors


def _scan_for_private_content(value: Any, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(value, Mapping):
        for key, nested in value.items():
            key_text = str(key)
            nested_path = f"{path}.{key_text}"
            if key_text.lower() in PRIVATE_KEYS:
                errors.append(f"{nested_path} contains a private-data key")
            errors.extend(_scan_for_private_content(nested, nested_path))
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            errors.extend(_scan_for_private_content(nested, f"{path}[{index}]"))
    elif isinstance(value, str):
        lowered = value.lower()
        if any(marker.lower() in lowered for marker in PRIVATE_MARKERS):
            errors.append(f"{path} contains a private-data marker")
    return errors
