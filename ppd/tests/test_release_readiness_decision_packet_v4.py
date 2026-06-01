from __future__ import annotations

import copy

from ppd.release_readiness_decision_packet_v4 import (
    OFFLINE_VALIDATION_COMMANDS,
    build_release_readiness_decision_packet_v4,
    validate_release_readiness_decision_packet_v4,
)


def _codes(packet: dict[str, object]) -> set[str]:
    return {issue.code for issue in validate_release_readiness_decision_packet_v4(packet)}


def test_release_readiness_decision_packet_v4_builds_valid_offline_packet() -> None:
    packet = build_release_readiness_decision_packet_v4()

    assert packet["packet_version"] == "release-readiness-decision-packet-v4"
    assert packet["release_state_changed"] is False
    assert packet["activation_performed"] is False
    assert packet["active_mutation_performed"] is False
    assert packet["validation_commands"] == [list(command) for command in OFFLINE_VALIDATION_COMMANDS]
    assert validate_release_readiness_decision_packet_v4(packet) == []


def test_v4_rejects_missing_required_sections() -> None:
    packet = build_release_readiness_decision_packet_v4()
    expected = {
        "promotion_candidate_references": "missing_promotion_candidate_references",
        "go_no_go_recommendation": "missing_go_no_go_recommendation",
        "unresolved_hold_inventory": "missing_unresolved_hold_inventory",
        "source_freshness_caveats": "missing_source_freshness_caveats",
        "agent_api_compatibility_notes": "missing_agent_api_compatibility_notes",
        "rollback_owner_placeholders": "missing_rollback_owner_placeholders",
        "post_decision_smoke_replay_plan": "missing_post_decision_smoke_replay_plan",
        "validation_commands": "missing_validation_commands",
    }

    for field, code in expected.items():
        broken = copy.deepcopy(packet)
        broken[field] = []
        assert code in _codes(broken)


def test_v4_rejects_active_activation_claims() -> None:
    packet = build_release_readiness_decision_packet_v4()

    broken = copy.deepcopy(packet)
    broken["activation_performed"] = True
    assert "active_activation_claim" in _codes(broken)

    broken = copy.deepcopy(packet)
    broken["go_no_go_recommendation"]["activation_allowed"] = True
    assert "active_activation_claim" in _codes(broken)

    broken = copy.deepcopy(packet)
    broken["review_note"] = "Active release enabled after reviewer approval."
    assert "active_activation_claim" in _codes(broken)


def test_v4_rejects_private_session_and_auth_artifacts() -> None:
    packet = build_release_readiness_decision_packet_v4()

    for field in ("auth_state", "session_state", "browser_state", "cookie", "private_artifact", "screenshot_path", "trace_path", "har_path"):
        broken = copy.deepcopy(packet)
        broken[field] = "artifact.json"
        assert "private_session_auth_artifact" in _codes(broken)

    broken = copy.deepcopy(packet)
    broken["review_note"] = "A session state file was stored for later review."
    assert "private_session_auth_artifact_text" in _codes(broken)


def test_v4_rejects_official_action_completion_claims_and_guarantees() -> None:
    packet = build_release_readiness_decision_packet_v4()

    broken = copy.deepcopy(packet)
    broken["review_note"] = "Submitted the application and paid the fee."
    assert "official_action_completion_claim" in _codes(broken)

    broken = copy.deepcopy(packet)
    broken["review_note"] = "Permit will be issued; approval is guaranteed."
    assert "legal_or_permitting_guarantee" in _codes(broken)


def test_v4_rejects_active_mutation_flags() -> None:
    packet = build_release_readiness_decision_packet_v4()

    for field in ("active_mutation_performed", "active_guardrail_mutation", "mutates_release_state", "promotes_fixtures"):
        broken = copy.deepcopy(packet)
        broken[field] = True
        assert "active_mutation_flag" in _codes(broken)


def test_v4_rejects_invalid_or_unsafe_validation_commands() -> None:
    packet = build_release_readiness_decision_packet_v4()

    broken = copy.deepcopy(packet)
    broken["validation_commands"] = [["python3", "-m", "pytest", "ppd/tests/test_release_readiness_decision_packet_v4.py"], "pytest"]
    assert "invalid_validation_command" in _codes(broken)

    broken = copy.deepcopy(packet)
    broken["validation_commands"] = [["python3", "ppd/crawler/live_crawl.py"]]
    assert "unsafe_validation_command" in _codes(broken)


def test_v4_allows_negated_safety_text() -> None:
    packet = build_release_readiness_decision_packet_v4()
    packet["post_decision_smoke_replay_plan"].append(
        {
            "smoke_replay_id": "negated-safety-note",
            "command_ref": "offline-validation-only",
            "expected_result": "No session state, screenshots, traces, uploads, payment, legal guarantee, or active release enabled claim is present.",
            "requires_network": False,
        }
    )

    assert validate_release_readiness_decision_packet_v4(packet) == []
