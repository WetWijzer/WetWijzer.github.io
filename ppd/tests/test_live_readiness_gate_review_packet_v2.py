from __future__ import annotations

from pathlib import Path

import pytest

from ppd.release.live_readiness_gate_review_packet_v2 import (
    build_from_fixture_path,
    validate_live_readiness_gate_review_packet_v2,
)

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "live_readiness_gate_review_packet_v2" / "source_packets.json"


def test_live_readiness_gate_review_packet_consumes_required_packets() -> None:
    packet = build_from_fixture_path(FIXTURE_PATH)

    assert packet["packet_type"] == "live_readiness_gate_review_packet_v2"
    assert packet["packet_version"] == 2
    assert packet["mode"] == "fixture_first_preflight_only_gate_review"
    assert packet["consumes"] == {
        "public_recrawl_operator_packet_v2": "public-recrawl-operator-packet-v2-fixture",
        "devhub_attended_readonly_runbook_refresh_packet_v2": "devhub-attended-readonly-runbook-refresh-packet-v2-fixture",
        "offline_safe_assist_release_candidate_packet_v2": "offline-safe-assist-release-candidate-packet-v2",
    }


def test_readiness_decisions_are_cited_preflight_only_blocks() -> None:
    packet = build_from_fixture_path(FIXTURE_PATH)

    assert {decision["domain"] for decision in packet["readiness_decisions"]} == {
        "public_recrawl",
        "attended_devhub_readonly",
        "offline_safe_assist_release_candidate",
    }
    for decision in packet["readiness_decisions"]:
        assert decision["preflight_only"] is True
        assert decision["live_execution_allowed"] is False
        assert decision["citations"]


def test_human_authorization_checkpoints_block_live_and_official_actions() -> None:
    packet = build_from_fixture_path(FIXTURE_PATH)
    checkpoints = {checkpoint["checkpoint_id"]: checkpoint for checkpoint in packet["required_human_authorization_checkpoints"]}

    assert set(checkpoints) == {
        "authorize-specific-public-recrawl-run",
        "authorize-attended-devhub-readonly-observation",
        "authorize-official-action-separately",
    }
    for checkpoint in checkpoints.values():
        assert checkpoint["human_authorization_required"] is True
        assert checkpoint["agent_may_proceed_without_authorization"] is False
        assert checkpoint["citations"]


def test_fixture_gaps_and_disallowed_actions_are_cited_and_fail_closed() -> None:
    packet = build_from_fixture_path(FIXTURE_PATH)

    assert {gap["gap_id"] for gap in packet["fixture_gaps"]} == {
        "no-live-recrawl-result-fixture",
        "no-authenticated-devhub-state-fixture",
        "no-official-action-authorization-fixture",
    }
    for gap in packet["fixture_gaps"]:
        assert gap["disposition"]
        assert gap["citations"]

    disallowed = {entry["action"]: entry for entry in packet["disallowed_live_consequential_actions"]}
    for action in [
        "public crawl run",
        "DevHub browser launch",
        "auth state creation, reading, or storage",
        "permit submission",
        "official attachment",
        "fee payment or purchase",
        "inspection scheduling",
    ]:
        assert disallowed[action]["allowed_by_this_packet"] is False
        assert disallowed[action]["citations"]


def test_owner_fields_validation_commands_attestations_and_mutation_flags_are_present() -> None:
    packet = build_from_fixture_path(FIXTURE_PATH)

    assert packet["reviewer_owner_fields"]["live_readiness_reviewer"] == "ppd-live-readiness-reviewer"
    assert packet["reviewer_owner_fields"]["public_recrawl_owner"] == "ppd-public-recrawl-operator"
    assert packet["reviewer_owner_fields"]["devhub_readonly_owner"] == "ppd-devhub-attended-operator"
    assert packet["offline_validation_commands"] == [
        ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
        ["python3", "-m", "pytest", "ppd/tests/test_live_readiness_gate_review_packet_v2.py"],
    ]
    assert packet["attestations"] == {
        "no_live_crawl": True,
        "no_live_devhub": True,
        "no_auth_state": True,
        "no_browser_artifact": True,
        "no_official_action": True,
    }
    assert packet["mutation_flags"]["agent_state_mutation_active"] is False
    assert all(value is False for value in packet["mutation_flags"].values())


def test_validation_rejects_uncited_readiness_decision() -> None:
    packet = build_from_fixture_path(FIXTURE_PATH)
    packet["readiness_decisions"][0]["citations"] = []

    with pytest.raises(ValueError, match="citations"):
        validate_live_readiness_gate_review_packet_v2(packet)


def test_validation_rejects_missing_human_authorization_checkpoint() -> None:
    packet = build_from_fixture_path(FIXTURE_PATH)
    packet["required_human_authorization_checkpoints"] = []

    with pytest.raises(ValueError, match="required_human_authorization_checkpoints"):
        validate_live_readiness_gate_review_packet_v2(packet)


def test_validation_rejects_missing_fixture_gap_disposition() -> None:
    packet = build_from_fixture_path(FIXTURE_PATH)
    packet["fixture_gaps"][0]["disposition"] = ""

    with pytest.raises(ValueError, match="disposition"):
        validate_live_readiness_gate_review_packet_v2(packet)


def test_validation_rejects_live_execution_allowance_or_missing_authorization() -> None:
    packet = build_from_fixture_path(FIXTURE_PATH)
    packet["readiness_decisions"][0]["live_execution_allowed"] = True

    with pytest.raises(ValueError, match="cannot allow live execution"):
        validate_live_readiness_gate_review_packet_v2(packet)

    packet = build_from_fixture_path(FIXTURE_PATH)
    packet["required_human_authorization_checkpoints"][0]["human_authorization_required"] = False

    with pytest.raises(ValueError, match="must require human authorization"):
        validate_live_readiness_gate_review_packet_v2(packet)


def test_validation_rejects_false_attestations_and_mutation_flags() -> None:
    packet = build_from_fixture_path(FIXTURE_PATH)
    packet["attestations"]["no_auth_state"] = False

    with pytest.raises(ValueError, match="attestations.no_auth_state"):
        validate_live_readiness_gate_review_packet_v2(packet)

    packet = build_from_fixture_path(FIXTURE_PATH)
    packet["mutation_flags"]["release_state_mutation_active"] = True

    with pytest.raises(ValueError, match="mutation_flags.release_state_mutation_active"):
        validate_live_readiness_gate_review_packet_v2(packet)


def test_validation_rejects_private_authenticated_facts_and_artifacts() -> None:
    packet = build_from_fixture_path(FIXTURE_PATH)
    packet["readiness_decisions"][0]["private_fact"] = "owner phone 503-555-0100"

    with pytest.raises(ValueError, match="private or authenticated fact"):
        validate_live_readiness_gate_review_packet_v2(packet)

    packet = build_from_fixture_path(FIXTURE_PATH)
    packet["fixture_gaps"][0]["screenshot"] = "devhub-home.png"

    with pytest.raises(ValueError, match="browser/session artifact"):
        validate_live_readiness_gate_review_packet_v2(packet)

    packet = build_from_fixture_path(FIXTURE_PATH)
    packet["fixture_gaps"][0]["gap"] = "Trace file is available at /tmp/trace.json"

    with pytest.raises(ValueError, match="artifact reference"):
        validate_live_readiness_gate_review_packet_v2(packet)


def test_validation_rejects_live_claims_identity_automation_guarantees_and_official_enablement() -> None:
    packet = build_from_fixture_path(FIXTURE_PATH)
    packet["readiness_decisions"][0]["rationale"] = "Ran the live crawl and processor successfully."

    with pytest.raises(ValueError, match="execution claim"):
        validate_live_readiness_gate_review_packet_v2(packet)

    packet = build_from_fixture_path(FIXTURE_PATH)
    packet["required_human_authorization_checkpoints"][1]["authorization_scope"] = "MFA automation completed by the agent."

    with pytest.raises(ValueError, match="automation language"):
        validate_live_readiness_gate_review_packet_v2(packet)

    packet = build_from_fixture_path(FIXTURE_PATH)
    packet["readiness_decisions"][2]["rationale"] = "Permit will be approved after this review."

    with pytest.raises(ValueError, match="outcome guarantee"):
        validate_live_readiness_gate_review_packet_v2(packet)

    packet = build_from_fixture_path(FIXTURE_PATH)
    packet["readiness_decisions"][2]["rationale"] = "Agent may submit the application in DevHub."

    with pytest.raises(ValueError, match="official action enablement"):
        validate_live_readiness_gate_review_packet_v2(packet)


def test_validation_rejects_active_source_schedule_surface_prompt_monitoring_release_or_agent_mutation_flags() -> None:
    for flag in (
        "source_mutation_active",
        "schedule_mutation_active",
        "surface_registry_mutation_active",
        "prompt_mutation_active",
        "monitoring_mutation_active",
        "release_state_mutation_active",
        "agent_state_mutation_active",
    ):
        packet = build_from_fixture_path(FIXTURE_PATH)
        packet["mutation_flags"][flag] = True

        with pytest.raises(ValueError, match=flag):
            validate_live_readiness_gate_review_packet_v2(packet)
