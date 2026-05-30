from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from ppd.agent_readiness.agent_readiness_delta_packet_v1 import (
    DeltaPacketError,
    build_agent_readiness_delta_packet_v1,
    validate_agent_readiness_delta_packet_v1,
)

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "agent_readiness_delta_packet_v1" / "source_inputs.json"


def _source_inputs() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _packet() -> dict:
    return build_agent_readiness_delta_packet_v1(_source_inputs())


def _issue_codes(packet: dict) -> set[str]:
    return {issue.code for issue in validate_agent_readiness_delta_packet_v1(packet)}


def test_builds_cited_agent_readiness_delta_packet_v1() -> None:
    packet = _packet()

    assert packet["packet_version"] == "agent-readiness-delta-packet-v1"
    assert packet["consumes"] == [
        "public_source_refresh_patch_plan_v1",
        "devhub_read_only_observation_promotion_plan_v1",
        "guardrail_regression_replay_queue_v1",
    ]
    assert packet["source_freshness_notes"][0]["source_id"] == "src-ppd-apply-permits"
    assert packet["source_freshness_notes"][0]["affected_source_ids"] == ["src-ppd-apply-permits"]
    assert {link["requirement_id"] for link in packet["requirement_impact_links"]} == {
        "req-devhub-application-path",
        "req-unsupported-email-path-check",
    }
    assert {link["affected_requirement_ids"][0] for link in packet["requirement_impact_links"]} == {
        "req-devhub-application-path",
        "req-unsupported-email-path-check",
    }
    assert packet["surface_map_observation_notes"][0]["surface_id"] == "devhub-home-read-only"
    assert packet["surface_map_observation_notes"][0]["affected_surface_ids"] == ["devhub-home-read-only"]
    assert packet["next_safe_action_expectations"][0]["replay_case_id"] == "requirement-still-supported-pass"
    assert {item["replay_case_id"] for item in packet["blocked_action_expectations"]} == {
        "stale-evidence-block",
        "missing-exact-confirmation-block",
    }


def test_delta_packet_is_offline_only_and_does_not_change_prompts_or_agent_state() -> None:
    packet = _packet()

    assert packet["attestations"] == {
        "fixture_first": True,
        "offline_only": True,
        "no_prompt_changes": True,
        "no_agent_state_changes": True,
        "no_live_crawl": True,
        "no_devhub_session": True,
        "no_private_artifact": True,
        "no_official_action": True,
        "no_active_mutation": True,
    }
    assert packet["prompt_changes"] == []
    assert packet["agent_state_changes"] == []
    assert ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"] in packet["offline_validation_commands"]
    assert validate_agent_readiness_delta_packet_v1(packet) == []


def test_rejects_uncited_agent_facing_delta() -> None:
    packet = _packet()
    packet["source_freshness_notes"][0]["citations"] = []

    assert "missing_citations" in _issue_codes(packet)


def test_rejects_missing_affected_ids() -> None:
    packet = _packet()
    packet["source_freshness_notes"][0]["affected_source_ids"] = []
    packet["requirement_impact_links"][0]["requirement_id"] = ""
    packet["requirement_impact_links"][0]["affected_requirement_ids"] = []
    packet["surface_map_observation_notes"][0]["surface_id"] = ""
    packet["surface_map_observation_notes"][0]["affected_surface_ids"] = []

    codes = _issue_codes(packet)

    assert "missing_affected_source_id" in codes
    assert "missing_affected_requirement_id" in codes
    assert "missing_affected_surface_id" in codes


def test_rejects_missing_blocked_or_next_safe_expectations() -> None:
    packet = _packet()
    packet["next_safe_action_expectations"] = []
    packet["blocked_action_expectations"][0]["expectation"] = ""
    packet["blocked_action_expectations"][0]["blocked_action_check"] = {}

    codes = _issue_codes(packet)

    assert "missing_delta_section" in codes
    assert "missing_action_expectation" in codes
    assert "missing_blocked_action_check" in codes


def test_rejects_prompt_release_source_guardrail_and_agent_state_mutation_flags() -> None:
    base = _packet()
    for key in (
        "active_prompt_mutation",
        "active_release_state_mutation",
        "active_source_mutation",
        "active_guardrail_mutation",
        "active_agent_state_mutation",
    ):
        packet = copy.deepcopy(base)
        packet[key] = True
        assert "active_mutation_flag" in _issue_codes(packet)

    with pytest.raises(DeltaPacketError):
        build_agent_readiness_delta_packet_v1({})


def test_rejects_private_or_authenticated_artifacts() -> None:
    packet = _packet()
    packet["source_freshness_notes"][0]["auth_state"] = {"token": "redacted-but-still-forbidden"}
    packet["surface_map_observation_notes"][0]["authenticated_artifact"] = "browser-state.json"

    assert "private_or_live_artifact" in _issue_codes(packet)


def test_rejects_legal_permitting_guarantees_and_consequential_action_language() -> None:
    packet = _packet()
    packet["source_freshness_notes"][0]["agent_note"] = "This guarantee approval means the permit will be issued."
    packet["next_safe_action_expectations"][0]["expectation"] = "Submit permit after this cited delta."

    codes = _issue_codes(packet)

    assert "forbidden_outcome_guarantee_text" in codes
    assert "forbidden_consequential_action_text" in codes
