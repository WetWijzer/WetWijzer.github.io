from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from ppd.devhub.read_only_observation_reviewer_disposition_packet_v1 import (
    OFFLINE_VALIDATION_COMMANDS,
    PACKET_SCHEMA_VERSION,
    build_disposition_packet_v1,
    load_json,
    packet_to_json,
    validate_disposition_packet_v1,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "devhub"
DRY_RUN_MANIFEST = FIXTURE_DIR / "read_only_observation_dry_run_manifest_v1.json"
DISPOSITION_PACKET = FIXTURE_DIR / "read_only_observation_reviewer_disposition_packet_v1.json"


def test_fixture_packet_is_valid() -> None:
    packet = load_json(DISPOSITION_PACKET)

    validate_disposition_packet_v1(packet)

    assert packet["schema_version"] == PACKET_SCHEMA_VERSION
    assert packet["mode"] == "offline_fixture_only"
    assert packet["devhub_opened"] is False
    assert packet["browser_or_session_artifacts_created"] is False
    assert packet["private_values_stored"] is False
    assert packet["official_actions_allowed"] is False
    assert packet["surface_map_mutation_allowed"] is False
    assert packet["offline_validation_commands"] == OFFLINE_VALIDATION_COMMANDS


def test_build_packet_consumes_dry_run_manifest_into_ordered_observations() -> None:
    manifest = load_json(DRY_RUN_MANIFEST)
    packet = build_disposition_packet_v1(manifest)

    validate_disposition_packet_v1(packet)

    observations = packet["ordered_reviewer_observations"]
    assert [item["observation_order"] for item in observations] == [1, 2, 3]
    assert [item["source_manifest_step_id"] for item in observations] == [
        "synthetic_observation_step_01",
        "synthetic_observation_step_02",
        "synthetic_observation_step_03",
    ]
    for item in observations:
        assert item["reviewer_disposition"] == "approve_read_only_with_placeholders"
        assert "APPROVED_READ_ONLY_ACTION_REFS_ONLY" in item["approved_reason_codes"]
        assert "HOLD_PENDING_HUMAN_REDACTION_CONFIRMATION" in item["hold_reason_codes"]
        assert all(ref.startswith("read_only:") for ref in item["read_only_action_classification_refs"])


def test_packet_contains_placeholders_for_redaction_surface_delta_blocked_actions_and_follow_up() -> None:
    packet = build_disposition_packet_v1(load_json(DRY_RUN_MANIFEST))

    redactions = packet["redaction_confirmation_placeholders"]
    assert len(redactions) == len(load_json(DRY_RUN_MANIFEST)["redacted_field_inventory_placeholders"])
    assert all(item["confirmation_status"] == "pending_human_confirmation" for item in redactions)
    assert all(item["stored_value"] is None for item in redactions)
    assert all(item["reviewer_confirmation"] is None for item in redactions)

    deltas = packet["read_only_surface_map_delta_placeholders"]
    assert len(deltas) == 3
    assert all(item["delta_status"] == "placeholder_only_no_active_surface_map_change" for item in deltas)
    assert all(item["registry_mutation_allowed"] is False for item in deltas)
    assert all(item["proposed_delta"] is None for item in deltas)

    blocked = packet["blocked_consequential_action_confirmations"][0]
    assert blocked["confirmation_status"] == "blocked_by_policy"
    assert blocked["official_action_allowed"] is False
    assert {"certification", "payment", "purchase", "schedule", "submit", "upload", "withdraw"}.issubset(
        set(blocked["blocked_action_categories"])
    )

    follow_ups = packet["manual_follow_up_notes"]
    assert len(follow_ups) == 3
    assert all(item["note_status"] == "placeholder_only_pending_reviewer" for item in follow_ups)
    assert all(item["reviewer_notes"] is None for item in follow_ups)


def test_packet_serializes_deterministically() -> None:
    packet = build_disposition_packet_v1(load_json(DRY_RUN_MANIFEST))

    rendered = packet_to_json(packet)

    assert json.loads(rendered) == packet
    assert rendered.endswith("\n")


@pytest.mark.parametrize(
    "section",
    [
        "ordered_reviewer_observations",
        "redaction_confirmation_placeholders",
        "read_only_surface_map_delta_placeholders",
        "blocked_consequential_action_confirmations",
        "manual_follow_up_notes",
        "offline_validation_commands",
    ],
)
def test_validate_rejects_missing_required_sections(section: str) -> None:
    packet = build_disposition_packet_v1(load_json(DRY_RUN_MANIFEST))
    packet.pop(section)

    with pytest.raises(ValueError, match=section):
        validate_disposition_packet_v1(packet)


def test_validate_rejects_non_read_only_action_refs() -> None:
    packet = build_disposition_packet_v1(load_json(DRY_RUN_MANIFEST))
    packet["ordered_reviewer_observations"][0]["read_only_action_classification_refs"] = ["official:submit"]

    with pytest.raises(ValueError, match="read_only_action_classification_refs"):
        validate_disposition_packet_v1(packet)


def test_validate_rejects_private_values_artifacts_mutations_and_official_actions() -> None:
    packet = build_disposition_packet_v1(load_json(DRY_RUN_MANIFEST))
    packet["redaction_confirmation_placeholders"][0]["stored_value"] = "private@example.test"
    with pytest.raises(ValueError, match="stored values"):
        validate_disposition_packet_v1(packet)

    packet = build_disposition_packet_v1(load_json(DRY_RUN_MANIFEST))
    packet["read_only_surface_map_delta_placeholders"][0]["registry_mutation_allowed"] = True
    with pytest.raises(ValueError, match="registry_mutation_allowed"):
        validate_disposition_packet_v1(packet)

    packet = build_disposition_packet_v1(load_json(DRY_RUN_MANIFEST))
    packet["official_actions_allowed"] = True
    with pytest.raises(ValueError, match="official_actions_allowed"):
        validate_disposition_packet_v1(packet)

    packet = build_disposition_packet_v1(load_json(DRY_RUN_MANIFEST))
    packet["trace_path"] = "trace.zip"
    with pytest.raises(ValueError, match="trace_path"):
        validate_disposition_packet_v1(packet)


def test_validate_rejects_validation_command_drift() -> None:
    packet = build_disposition_packet_v1(load_json(DRY_RUN_MANIFEST))
    packet["offline_validation_commands"] = deepcopy(OFFLINE_VALIDATION_COMMANDS)
    packet["offline_validation_commands"].append(["python3", "unexpected.py"])

    with pytest.raises(ValueError, match="offline_validation_commands"):
        validate_disposition_packet_v1(packet)
