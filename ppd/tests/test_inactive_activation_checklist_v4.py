from __future__ import annotations

import copy
from pathlib import Path

import pytest

from ppd.agent_readiness.inactive_activation_checklist_v4 import (
    EXACT_OFFLINE_VALIDATION_COMMANDS,
    PACKET_TYPE,
    assert_valid_inactive_activation_checklist_v4,
    build_inactive_activation_checklist_v4,
    load_inactive_activation_checklist_v4_fixture,
    validate_inactive_activation_checklist_v4,
)

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "inactive_activation_checklist_v4" / "source_fixture.json"


def _packet() -> dict[str, object]:
    return load_inactive_activation_checklist_v4_fixture(FIXTURE_PATH)


def test_builds_fixture_first_inactive_activation_checklist_v4() -> None:
    packet = _packet()

    assert packet["packet_type"] == PACKET_TYPE
    assert packet["mode"] == "fixture_first_inactive_activation_checklist_v4"
    assert packet["consumes_only"] == {"post_decision_smoke_replay_v4_fixtures": True}
    assert packet["required_source_references"]["post_decision_smoke_replay_v4_refs"]
    assert packet["exact_offline_validation_commands"] == EXACT_OFFLINE_VALIDATION_COMMANDS
    assert packet["validation_commands"] == EXACT_OFFLINE_VALIDATION_COMMANDS
    assert validate_inactive_activation_checklist_v4(packet).valid
    assert_valid_inactive_activation_checklist_v4(packet)


def test_assembles_reviewer_controlled_rows_from_replay_fixture() -> None:
    packet = _packet()

    assert any(row["prerequisite_id"] == "no-go-replay-remains-blocking" for row in packet["reviewer_controlled_activation_prerequisites"])
    assert all(row["status"] == "pending_reviewer_control" for row in packet["reviewer_controlled_activation_prerequisites"])
    assert all(row["signoff_status"] == "placeholder_pending_manual_signoff" for row in packet["required_signoff_placeholders"])
    assert all(row["signed_by"] is None for row in packet["required_signoff_placeholders"])
    assert all(row["clearance_status"] == "pending_reviewer_clearance" for row in packet["source_freshness_hold_clearance_criteria"])
    assert all(row["checkpoint_status"] == "pending_reviewer_confirmation" for row in packet["rollback_checkpoint_rows"])


def test_keeps_post_activation_smoke_checks_and_agent_notes_inactive() -> None:
    packet = _packet()

    assert all(row["check_status"] == "placeholder_pending_future_activation" for row in packet["post_activation_smoke_checks"])
    assert all(row["requires_separate_activation_authorization"] is True for row in packet["post_activation_smoke_checks"])
    assert all(row["activation_allowed_by_this_packet"] is False for row in packet["post_activation_smoke_checks"])
    assert all(row["notification_status"] == "placeholder_pending_manual_release_notice" for row in packet["agent_notification_notes"])
    assert all(row["activation_allowed"] is False for row in packet["agent_notification_notes"])


def test_rejects_missing_required_sections() -> None:
    for field in (
        "reviewer_controlled_activation_prerequisites",
        "required_signoff_placeholders",
        "source_freshness_hold_clearance_criteria",
        "rollback_checkpoint_rows",
        "post_activation_smoke_checks",
        "agent_notification_notes",
    ):
        packet = _packet()
        packet[field] = []

        result = validate_inactive_activation_checklist_v4(packet)

        assert not result.valid, field
        assert f"{field} must be a non-empty list" in result.problems


def test_rejects_missing_replay_refs_and_non_exact_validation_commands() -> None:
    packet = _packet()
    packet["required_source_references"] = {"post_decision_smoke_replay_v4_refs": []}
    packet["validation_commands"] = [["python3", "-m", "pytest"]]

    result = validate_inactive_activation_checklist_v4(packet)

    assert not result.valid
    assert "required_source_references.post_decision_smoke_replay_v4_refs must be non-empty" in result.problems
    assert "validation_commands must contain only the daemon self-test command" in result.problems


def test_rejects_activation_private_official_or_guarantee_payloads() -> None:
    for key, value in (
        ("session_state", {"path": "state.json"}),
        ("auth_token", "secret"),
        ("claim", "approval guaranteed"),
        ("official_claim", "submitted permit"),
        ("activation_claim", "activated guardrails"),
        ("active_guardrail_mutation", True),
        ("active_release_state_mutation", True),
    ):
        packet = _packet()
        packet[key] = value

        result = validate_inactive_activation_checklist_v4(packet)

        assert not result.valid, key


def test_source_fixture_must_contain_valid_post_decision_smoke_replay_packets_only() -> None:
    import json

    source = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    bad_source = copy.deepcopy(source)
    bad_source["post_decision_smoke_replay_v4_fixtures"] = []
    with pytest.raises(ValueError, match="post_decision_smoke_replay_v4_fixtures must be non-empty"):
        build_inactive_activation_checklist_v4(bad_source)

    bad_source = copy.deepcopy(source)
    bad_source["post_decision_smoke_replay_v4_fixtures"][0]["packet_type"] = "wrong"
    with pytest.raises(ValueError, match="invalid post-decision smoke replay v4"):
        build_inactive_activation_checklist_v4(bad_source)
