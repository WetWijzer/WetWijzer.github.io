from pathlib import Path

import pytest

from ppd.release_decision_packet_v4 import (
    CANDIDATE_VERSION,
    OFFLINE_VALIDATION_COMMANDS,
    PACKET_VERSION,
    build_packet,
    build_packet_from_fixture,
    load_candidates,
)

FIXTURE = Path(__file__).parent / "fixtures" / "release_decision_packet_v4" / "inactive_guardrail_promotion_candidates_v4.json"


def test_build_packet_from_inactive_candidate_fixtures_only():
    packet = build_packet_from_fixture(FIXTURE)

    assert packet["packet_version"] == PACKET_VERSION
    assert packet["input_candidate_version"] == CANDIDATE_VERSION
    assert packet["source_mode"] == "fixtures_only"
    assert packet["guardrail_activation"] == "not_performed"
    assert packet["devhub_access"] == "not_performed"
    assert packet["legal_or_permitting_guarantee"] == "not_provided"
    assert packet["recommendation"] == "NO_GO"
    assert packet["unresolved_hold_inventory"] == [
        {
            "candidate_id": "candidate-v4-inactive-zoning-crosscheck",
            "hold_id": "hold-source-freshness-review",
            "reason": "Reviewer has not accepted the fixture source freshness caveat.",
            "owner_placeholder": "TBD_SOURCE_REVIEWER",
        }
    ]
    assert packet["offline_validation_commands"] == OFFLINE_VALIDATION_COMMANDS


def test_packet_includes_reviewer_operational_sections():
    packet = build_packet_from_fixture(FIXTURE)

    assert packet["source_freshness_caveats"]
    assert packet["agent_api_compatibility_notes"]
    assert packet["rollback_owner_placeholders"] == [
        {
            "candidate_id": "candidate-v4-inactive-zoning-crosscheck",
            "rollback_owner_placeholder": "TBD_ROLLBACK_OWNER",
            "rollback_decision_placeholder": "TBD_AFTER_REVIEW",
        },
        {
            "candidate_id": "candidate-v4-inactive-intake-smoke",
            "rollback_owner_placeholder": "TBD_ROLLBACK_OWNER",
            "rollback_decision_placeholder": "TBD_AFTER_REVIEW",
        },
    ]
    assert packet["post_decision_smoke_replay_plan"] == [
        "Keep guardrails inactive while replaying fixture-backed smoke checks.",
        "Run release packet tests against ppd/tests/fixtures/release_decision_packet_v4 only.",
        "Run daemon self-test offline after packet generation.",
        "Require a human reviewer to assign rollback owners before any separate activation change.",
    ]


def test_rejects_active_or_wrong_version_candidates():
    candidates = load_candidates(FIXTURE)

    active_candidate = dict(candidates[0])
    active_candidate["guardrails_active"] = True
    with pytest.raises(ValueError, match="must not activate guardrails"):
        build_packet([active_candidate])

    wrong_version = dict(candidates[0])
    wrong_version["candidate_version"] = "promotion_candidate_v3"
    with pytest.raises(ValueError, match="inactive_guardrail_promotion_candidate_v4"):
        build_packet([wrong_version])
