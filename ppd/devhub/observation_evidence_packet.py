"""Reviewer-safe DevHub observation evidence intake packet v1.

This module converts an attended DevHub observation dry-run runbook into
synthetic evidence rows. It intentionally does not drive a browser, persist
session state, store screenshots, or record authenticated page values.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

PACKET_VERSION = "devhub_observation_evidence_intake_packet_v1"
RUNBOOK_VERSION = "attended_devhub_observation_dry_run_runbook_v1"

REQUIRED_ATTESTATIONS = (
    "no_login_automation",
    "no_session_state",
    "no_screenshot",
    "no_trace",
    "no_har",
    "no_click_through",
    "no_upload",
    "no_submit",
    "no_payment",
    "no_scheduling",
)

REQUIRED_ROW_FIELDS = (
    "evidence_id",
    "source_runbook_id",
    "surface_id",
    "surface_label",
    "auth_scope",
    "page_heading_expectations",
    "accessible_landmark_expectations",
    "validation_message_expectations",
    "redaction_status",
    "stop_before_action_gates",
    "owner_fields",
    "offline_validation_commands",
    "attestations",
    "review_status",
)

FORBIDDEN_ARTIFACT_KEYS = frozenset(
    {
        "auth_state",
        "browser_context_storage_state",
        "cookies",
        "credential",
        "credentials",
        "downloaded_document",
        "har",
        "local_private_path",
        "password",
        "payment_details",
        "raw_authenticated_values",
        "screenshot",
        "session_state",
        "trace",
        "upload_payload",
    }
)


def build_observation_evidence_packet(runbook: Mapping[str, Any]) -> dict[str, Any]:
    """Convert a dry-run runbook into a reviewer-safe synthetic packet."""

    version = runbook.get("version")
    if version != RUNBOOK_VERSION:
        raise ValueError(f"expected runbook version {RUNBOOK_VERSION!r}, got {version!r}")

    runbook_id = _required_text(runbook, "runbook_id")
    targets = runbook.get("observation_targets")
    if not isinstance(targets, list) or not targets:
        raise ValueError("runbook must contain at least one observation target")

    packet = {
        "version": PACKET_VERSION,
        "source_runbook_id": runbook_id,
        "generated_from": RUNBOOK_VERSION,
        "evidence_mode": "synthetic_fixture_from_attended_dry_run",
        "artifact_policy": {
            "stores_credentials": False,
            "stores_session_state": False,
            "stores_screenshots": False,
            "stores_traces": False,
            "stores_har": False,
            "stores_raw_authenticated_values": False,
            "stores_downloads": False,
        },
        "packet_attestations": {name: True for name in REQUIRED_ATTESTATIONS},
        "evidence_rows": [_row_from_target(runbook_id, index, target) for index, target in enumerate(targets, 1)],
    }
    validate_observation_evidence_packet(packet)
    return packet


def validate_observation_evidence_packet(packet: Mapping[str, Any]) -> None:
    """Validate the packet shape and safety attestations."""

    version = packet.get("version")
    if version != PACKET_VERSION:
        raise ValueError(f"expected packet version {PACKET_VERSION!r}, got {version!r}")

    artifact_policy = packet.get("artifact_policy")
    if not isinstance(artifact_policy, Mapping):
        raise ValueError("packet artifact_policy must be an object")
    for key, value in artifact_policy.items():
        if key.startswith("stores_") and value is not False:
            raise ValueError(f"artifact_policy.{key} must be false")

    attestations = packet.get("packet_attestations")
    _validate_attestations(attestations, "packet_attestations")

    rows = packet.get("evidence_rows")
    if not isinstance(rows, list) or not rows:
        raise ValueError("packet must contain at least one evidence row")

    seen_ids: set[str] = set()
    for row in rows:
        _validate_row(row, seen_ids)

    _reject_forbidden_artifacts(packet, path="packet")


def _row_from_target(runbook_id: str, index: int, target: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(target, Mapping):
        raise ValueError("observation target must be an object")

    surface_id = _required_text(target, "surface_id")
    row = {
        "evidence_id": f"devhub-observation-evidence-v1-{index:03d}",
        "source_runbook_id": runbook_id,
        "surface_id": surface_id,
        "surface_label": _required_text(target, "surface_label"),
        "auth_scope": target.get("auth_scope", "attended_user_owned_read_only"),
        "page_heading_expectations": _string_list(target, "page_heading_expectations"),
        "accessible_landmark_expectations": _string_list(target, "accessible_landmark_expectations"),
        "validation_message_expectations": _string_list(target, "validation_message_expectations"),
        "redaction_status": target.get("redaction_status", "synthetic_fixture_only_no_private_values"),
        "stop_before_action_gates": _string_list(target, "stop_before_action_gates"),
        "owner_fields": _owner_fields(target.get("owner_fields")),
        "offline_validation_commands": _offline_commands(target.get("offline_validation_commands")),
        "attestations": {name: True for name in REQUIRED_ATTESTATIONS},
        "review_status": "needs_human_review_before_use_with_live_devhub",
    }
    _validate_row(row, set())
    return row


def _validate_row(row: Any, seen_ids: set[str]) -> None:
    if not isinstance(row, Mapping):
        raise ValueError("evidence row must be an object")

    missing = [field for field in REQUIRED_ROW_FIELDS if field not in row]
    if missing:
        raise ValueError(f"evidence row missing required fields: {', '.join(missing)}")

    evidence_id = _required_text(row, "evidence_id")
    if evidence_id in seen_ids:
        raise ValueError(f"duplicate evidence_id: {evidence_id}")
    seen_ids.add(evidence_id)

    for field in (
        "page_heading_expectations",
        "accessible_landmark_expectations",
        "validation_message_expectations",
        "stop_before_action_gates",
    ):
        values = row.get(field)
        if not isinstance(values, list) or not values or not all(isinstance(value, str) and value for value in values):
            raise ValueError(f"{evidence_id}.{field} must be a non-empty list of strings")

    if row.get("redaction_status") != "synthetic_fixture_only_no_private_values":
        raise ValueError(f"{evidence_id}.redaction_status must confirm synthetic-only redaction")

    owner_fields = row.get("owner_fields")
    if not isinstance(owner_fields, Mapping):
        raise ValueError(f"{evidence_id}.owner_fields must be an object")
    for field in ("surface_owner", "review_owner", "evidence_owner"):
        if not isinstance(owner_fields.get(field), str) or not owner_fields[field]:
            raise ValueError(f"{evidence_id}.owner_fields.{field} is required")

    commands = row.get("offline_validation_commands")
    if not isinstance(commands, list) or not commands:
        raise ValueError(f"{evidence_id}.offline_validation_commands must be a non-empty list")
    for command in commands:
        if not isinstance(command, list) or not command or not all(isinstance(part, str) and part for part in command):
            raise ValueError(f"{evidence_id}.offline_validation_commands must contain argv arrays")

    _validate_attestations(row.get("attestations"), f"{evidence_id}.attestations")


def _validate_attestations(attestations: Any, label: str) -> None:
    if not isinstance(attestations, Mapping):
        raise ValueError(f"{label} must be an object")
    for name in REQUIRED_ATTESTATIONS:
        if attestations.get(name) is not True:
            raise ValueError(f"{label}.{name} must be true")


def _reject_forbidden_artifacts(value: Any, path: str) -> None:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            text_key = str(key).lower()
            if text_key in FORBIDDEN_ARTIFACT_KEYS:
                raise ValueError(f"forbidden DevHub artifact key at {path}.{key}")
            _reject_forbidden_artifacts(nested, f"{path}.{key}")
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            _reject_forbidden_artifacts(nested, f"{path}[{index}]")


def _required_text(source: Mapping[str, Any], field: str) -> str:
    value = source.get(field)
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field} is required")
    return value


def _string_list(source: Mapping[str, Any], field: str) -> list[str]:
    value = source.get(field)
    if not isinstance(value, list) or not value or not all(isinstance(item, str) and item for item in value):
        raise ValueError(f"{field} must be a non-empty list of strings")
    return list(value)


def _owner_fields(value: Any) -> dict[str, str]:
    if value is None:
        return {
            "surface_owner": "ppd-devhub-observation",
            "review_owner": "ppd-human-reviewer",
            "evidence_owner": "ppd-fixture-curator",
        }
    if not isinstance(value, Mapping):
        raise ValueError("owner_fields must be an object")
    return {key: _required_text(value, key) for key in ("surface_owner", "review_owner", "evidence_owner")}


def _offline_commands(value: Any) -> list[list[str]]:
    if value is None:
        return [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]]
    if not isinstance(value, list) or not value:
        raise ValueError("offline_validation_commands must be a non-empty list")
    return deepcopy(value)
