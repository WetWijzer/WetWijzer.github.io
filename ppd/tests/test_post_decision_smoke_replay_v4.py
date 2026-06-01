from __future__ import annotations

import copy
from pathlib import Path

import pytest

from ppd.agent_readiness.post_decision_smoke_replay_v4 import (
    EXACT_OFFLINE_VALIDATION_COMMANDS,
    PACKET_TYPE,
    assert_valid_post_decision_smoke_replay_v4,
    load_post_decision_smoke_replay_v4_fixture,
    validate_post_decision_smoke_replay_v4,
)

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "post_decision_smoke_replay_v4" / "source_fixture.json"


def _packet() -> dict[str, object]:
    return load_post_decision_smoke_replay_v4_fixture(FIXTURE_PATH)


def test_builds_fixture_first_post_decision_smoke_replay_v4() -> None:
    packet = _packet()

    assert packet["packet_type"] == PACKET_TYPE
    assert packet["mode"] == "fixture_first_post_decision_smoke_replay_v4"
    assert packet["consumes_only"] == {
        "release_decision_packet_v4_fixtures": True,
        "inactive_guardrail_placeholder_fixtures": True,
    }
    assert packet["required_source_references"]["release_decision_packet_v4_refs"]
    assert packet["required_source_references"]["inactive_guardrail_placeholder_fixture_refs"]
    assert packet["release_outcome_handling"]["go_no_go_outcome"] == "NO_GO"
    assert packet["release_outcome_handling"]["activation_allowed"] is False
    assert packet["exact_offline_validation_commands"] == EXACT_OFFLINE_VALIDATION_COMMANDS
    assert packet["validation_commands"] == EXACT_OFFLINE_VALIDATION_COMMANDS
    assert validate_post_decision_smoke_replay_v4(packet).valid
    assert_valid_post_decision_smoke_replay_v4(packet)


def test_propagates_unresolved_holds_and_displays_required_notes() -> None:
    packet = _packet()

    assert packet["unresolved_hold_propagation"] == [
        {
            "candidate_id": "candidate-v4-inactive-zoning-crosscheck",
            "hold_id": "hold-source-freshness-review",
            "reason": "Reviewer has not accepted the fixture source freshness caveat.",
            "owner_placeholder": "TBD_SOURCE_REVIEWER",
            "hold_status": "unresolved_hold_propagated",
            "blocks_go": True,
        }
    ]
    assert all(row["display_required"] is True for row in packet["source_freshness_caveat_display"])
    assert all(row["display_required"] is True for row in packet["agent_api_compatibility_notes"])
    assert any("source freshness" in row["display_text"] for row in packet["source_freshness_caveat_display"])
    assert packet["manual_handoff_reminders"]


def test_keeps_guardrail_placeholders_inactive_and_rollback_owners_pending() -> None:
    packet = _packet()

    assert all(row["placeholder_status"] == "inactive_placeholder_only" for row in packet["guardrail_placeholder_checks"])
    assert all(row["activation_allowed"] is False for row in packet["guardrail_placeholder_checks"])
    assert all(row["rollback_owner_placeholder"] == "TBD_ROLLBACK_OWNER" for row in packet["rollback_owner_placeholders"])
    assert all(row["owner_assignment_status"] == "placeholder_pending_manual_assignment" for row in packet["rollback_owner_placeholders"])
    assert all(row["active_state_changed"] is False for row in packet["rollback_owner_placeholders"])


def test_requires_all_named_smoke_expectation_checks() -> None:
    packet = _packet()
    expectation_ids = {row["expectation_id"] for row in packet["smoke_expectations"]}

    assert {
        "go-no-go-outcome-handling",
        "inactive-guardrail-placeholder-checks",
        "unresolved-hold-propagation",
        "source-freshness-caveat-display",
        "agent-api-compatibility-checks",
        "rollback-owner-placeholder-checks",
        "manual-handoff-reminders",
        "offline-validation-command-exactness",
    }.issubset(expectation_ids)

    packet["smoke_expectations"] = [row for row in packet["smoke_expectations"] if row["expectation_id"] != "agent-api-compatibility-checks"]
    result = validate_post_decision_smoke_replay_v4(packet)

    assert not result.valid
    assert any("smoke_expectations missing required expectation ids" in problem for problem in result.problems)


def test_rejects_missing_required_sections() -> None:
    required_fields = (
        "unresolved_hold_propagation",
        "source_freshness_caveat_display",
        "agent_api_compatibility_notes",
        "guardrail_placeholder_checks",
        "rollback_owner_placeholders",
        "manual_handoff_reminders",
        "smoke_expectations",
    )
    for field in required_fields:
        packet = _packet()
        packet[field] = []

        result = validate_post_decision_smoke_replay_v4(packet)

        assert not result.valid, field
        assert f"{field} must be a non-empty list" in result.problems


def test_rejects_missing_release_decision_and_placeholder_references() -> None:
    packet = _packet()
    packet["required_source_references"] = {
        "release_decision_packet_v4_refs": [],
        "inactive_guardrail_placeholder_fixture_refs": [],
    }

    result = validate_post_decision_smoke_replay_v4(packet)

    assert not result.valid
    assert "required_source_references.release_decision_packet_v4_refs must be non-empty" in result.problems
    assert "required_source_references.inactive_guardrail_placeholder_fixture_refs must be non-empty" in result.problems


def test_rejects_missing_go_no_go_outcome() -> None:
    packet = _packet()
    packet["release_outcome_handling"]["go_no_go_outcome"] = ""

    result = validate_post_decision_smoke_replay_v4(packet)

    assert not result.valid
    assert "release_outcome_handling.go_no_go_outcome must be NO_GO or GO_WITH_CAVEATS" in result.problems


def test_rejects_non_exact_validation_commands_and_activation_claims() -> None:
    packet = _packet()
    packet["validation_commands"] = [["python3", "-m", "pytest"]]
    packet["guardrail_placeholder_checks"][0]["activation_allowed"] = True
    packet["attestations"]["guardrails_activated"] = True

    result = validate_post_decision_smoke_replay_v4(packet)

    assert not result.valid
    assert "validation_commands must contain only the daemon self-test command" in result.problems
    assert "guardrail_placeholder_checks[0].activation_allowed must be false" in result.problems
    assert "attestations must exactly deny guardrail activation, DevHub access, private document reads, official actions, and guarantees" in result.problems


def test_rejects_private_runtime_official_guarantee_or_mutation_payloads() -> None:
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

        result = validate_post_decision_smoke_replay_v4(packet)

        assert not result.valid, key


def test_source_fixture_must_use_release_decision_and_inactive_placeholder_inputs_only() -> None:
    import json

    source = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    bad_source = copy.deepcopy(source)
    bad_source["release_decision_packet_v4"]["source_mode"] = "live"
    with pytest.raises(ValueError, match="fixtures_only"):
        load_post_decision_smoke_replay_v4_fixture_from_mapping_for_test(bad_source)

    bad_source = copy.deepcopy(source)
    bad_source["inactive_guardrail_placeholder_fixtures"][0]["activation_allowed"] = True
    with pytest.raises(ValueError, match="activation_allowed must be false"):
        load_post_decision_smoke_replay_v4_fixture_from_mapping_for_test(bad_source)

    bad_source = copy.deepcopy(source)
    bad_source["inactive_guardrail_placeholder_fixtures"] = []
    with pytest.raises(ValueError, match="inactive_guardrail_placeholder_fixtures must be non-empty"):
        load_post_decision_smoke_replay_v4_fixture_from_mapping_for_test(bad_source)


def load_post_decision_smoke_replay_v4_fixture_from_mapping_for_test(source: dict[str, object]) -> dict[str, object]:
    from ppd.agent_readiness.post_decision_smoke_replay_v4 import build_post_decision_smoke_replay_v4

    return build_post_decision_smoke_replay_v4(source)
