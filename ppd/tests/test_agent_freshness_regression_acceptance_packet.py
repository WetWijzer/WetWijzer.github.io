from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from ppd.agent_freshness_regression_acceptance_packet import (
    build_agent_freshness_regression_acceptance_packet,
    require_valid_agent_freshness_regression_acceptance_packet,
    validate_agent_freshness_regression_acceptance_packet,
)
from ppd.agent_prompt_update_candidate_packet import build_prompt_regression_dry_run_packet
from ppd.agent_safe_action_freshness_regression_packet import build_safe_action_freshness_regression_packet


FIXTURE_DIR = Path(__file__).parent / "fixtures"
ACCEPTANCE_FIXTURE = FIXTURE_DIR / "agent_freshness_regression_acceptance" / "source_packet_refs.json"
SAFE_ACTION_SOURCE_FIXTURE = FIXTURE_DIR / "agent_safe_action_freshness_regression" / "source_packets.json"
RELEASE_CLOSURE_FIXTURE = FIXTURE_DIR / "release_blocker_closure" / "review_packet.json"


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _safe_action_packet() -> dict:
    source = _json(SAFE_ACTION_SOURCE_FIXTURE)
    return build_safe_action_freshness_regression_packet(
        source["safe_read_only_action_transcript_packet"],
        source["evidence_freshness_watchlist_reviewer_disposition_packet"],
        source["agent_prompt_regression_dry_run_packet"],
    )


def _packet() -> dict:
    return build_agent_freshness_regression_acceptance_packet(
        _safe_action_packet(),
        build_prompt_regression_dry_run_packet(),
        _json(RELEASE_CLOSURE_FIXTURE),
    )


def _codes(packet: dict) -> list[str]:
    return [issue.code for issue in validate_agent_freshness_regression_acceptance_packet(packet)]


def test_builds_fixture_first_agent_freshness_regression_acceptance_packet() -> None:
    packet = _packet()

    assert packet["packet_type"] == "ppd.agent_freshness_regression_acceptance_packet.v1"
    assert packet["mode"] == "fixture_first_agent_freshness_regression_acceptance"
    assert packet["fixture_first"] is True
    assert packet["metadata_only"] is True
    assert packet["input_packet_refs"]["agent_safe_action_freshness_regression_packet_id"] == "safe-action-freshness-regression-for-freshness-watchlist-disposition-20260529-fixture"
    assert packet["input_packet_refs"]["agent_prompt_regression_dry_run_packet_id"] == "agent_prompt_regression_dry_run_fixture_first_v1"
    assert packet["input_packet_refs"]["release_blocker_closure_review_packet_id"] == "release-blocker-closure-review-20260529-469"
    assert validate_agent_freshness_regression_acceptance_packet(packet) == []
    require_valid_agent_freshness_regression_acceptance_packet(packet)


def test_acceptance_packet_has_required_cited_expectation_types() -> None:
    fixture = _json(ACCEPTANCE_FIXTURE)
    packet = _packet()
    expectation_types = sorted({item["expectation_type"] for item in packet["acceptance_expectations"]})

    assert expectation_types == sorted(fixture["expected_expectation_types"])
    for expectation in packet["acceptance_expectations"]:
        assert expectation["expected_result"] in ["pass", "fail"]
        assert expectation["pass_criteria"]
        assert expectation["fail_criteria"]
        assert expectation["citations"]
        assert expectation["source_packet_refs"]


def test_acceptance_packet_preserves_stale_prompts_refusals_and_blocked_actions() -> None:
    fixture = _json(ACCEPTANCE_FIXTURE)
    packet = _packet()

    stale_prompt_rows = [item for item in packet["acceptance_expectations"] if item["expectation_type"] == "stale_evidence_prompt"]
    refusal_rows = [item for item in packet["acceptance_expectations"] if item["expectation_type"] == "refusal_explanation"]
    blocked_rows = [item for item in packet["acceptance_expectations"] if item["expectation_type"] == "blocked_consequential_action"]

    assert len(stale_prompt_rows) == 2
    assert len(refusal_rows) == 2
    assert len(blocked_rows) == 1
    assert stale_prompt_rows[0]["expected_result"] == "pass"
    assert refusal_rows[0]["expected_result"] == "pass"
    assert blocked_rows[0]["expected_result"] == "pass"
    assert blocked_rows[0]["observed_values"]["blocked_actions"] == sorted(fixture["expected_blocked_actions"])


def test_acceptance_packet_carries_reviewer_owner_and_no_mutation_attestations() -> None:
    fixture = _json(ACCEPTANCE_FIXTURE)
    packet = _packet()
    owner_rows = [item for item in packet["acceptance_expectations"] if item["expectation_type"] == "reviewer_owner_field"]
    attestation_rows = [item for item in packet["acceptance_expectations"] if item["expectation_type"] == "no_mutation_attestation"]

    assert len(owner_rows) == 1
    assert "ppd-release-reviewer" in owner_rows[0]["observed_values"]["reviewer_owners"]
    assert "ppd_prompt_review" in owner_rows[0]["observed_values"]["reviewer_owners"]
    assert len(attestation_rows) == 1
    for key in fixture["required_attestations"]:
        assert packet["attestations"][key] is True
        assert attestation_rows[0]["observed_values"][key] is True
    assert packet["attestations"]["live_llm_executed"] is False
    assert packet["attestations"]["devhub_executed"] is False
    assert packet["attestations"]["prompt_mutation_enabled"] is False
    assert packet["attestations"]["guardrail_mutation_enabled"] is False
    assert packet["attestations"]["agent_state_mutation_enabled"] is False


@pytest.mark.parametrize(
    ("mutation", "expected_code"),
    [
        (lambda packet: packet.__setitem__("fixture_first", False), "not_fixture_first_metadata_only"),
        (lambda packet: packet.__setitem__("acceptance_expectations", []), "missing_acceptance_expectations"),
        (lambda packet: packet["acceptance_expectations"][0].__setitem__("citations", []), "uncited_acceptance_expectation"),
        (lambda packet: packet["attestations"].__setitem__("no_agent_state_mutation", False), "missing_true_attestation"),
        (lambda packet: packet["attestations"].__setitem__("guardrail_mutation_enabled", True), "execution_or_mutation_flag_enabled"),
        (lambda packet: packet.__setitem__("session_state", "auth_state/private.json"), "private_or_raw_artifact_reference"),
    ],
)
def test_validation_rejects_unsafe_or_incomplete_acceptance_packets(mutation: object, expected_code: str) -> None:
    packet = copy.deepcopy(_packet())
    mutation(packet)

    assert expected_code in _codes(packet)
