from __future__ import annotations

import json
from pathlib import Path

import pytest

from ppd.logic.guardrail_refresh_regression_review_packet import (
    GuardrailRefreshRegressionReviewPacketError,
    build_guardrail_refresh_regression_review_packet,
    validate_guardrail_refresh_regression_review_packet,
)

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "guardrail_refresh_regression_review_packet" / "source_packets.json"


def _source_packets() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def test_builds_fixture_first_guardrail_refresh_regression_review_packet() -> None:
    bundle = _source_packets()

    packet = build_guardrail_refresh_regression_review_packet(bundle)

    assert packet["packet_type"] == "ppd.guardrail_refresh_regression_review_packet.v1"
    assert packet["packet_status"] == "review_required_no_state_mutation"
    assert packet["source_packet_ids"] == {
        "process_and_guardrail_refresh_candidate_packet": "process-guardrail-refresh-candidate-20260529",
        "agent_regression_refresh_packet": "agent-regression-refresh-20260529-fixture-first",
        "source_refresh_result_reconciliation_packet": "source-refresh-result-reconciliation-20260529",
    }
    assert packet["affected_guardrail_bundle_ids"] == [
        "guardrail-bundle-devhub-actions-v4",
        "guardrail-bundle-source-refresh-v2",
    ]
    assert packet["attestations"] == {
        "fixture_first": True,
        "no_live_llm": True,
        "no_devhub": True,
        "no_prompt_mutation": True,
        "no_guardrail_mutation": True,
        "no_release_state_mutation": True,
    }
    validate_guardrail_refresh_regression_review_packet(packet)


def test_expectations_are_cited_pass_fail_review_items() -> None:
    packet = build_guardrail_refresh_regression_review_packet(_source_packets())

    expectations = packet["guardrail_predicate_expectations"]
    assert {expectation["expected_result"] for expectation in expectations} == {"pass", "fail"}
    assert all(expectation["predicate_id"] for expectation in expectations)
    assert all(expectation["source_evidence_ids"] for expectation in expectations)
    assert all(expectation["affected_guardrail_bundle_ids"] for expectation in expectations)
    assert all(expectation["reviewer_owner"] for expectation in expectations)
    assert any(expectation["predicate_id"] == "devhub_submit_requires_exact_confirmation" for expectation in expectations)
    assert any(expectation["predicate_id"] == "source_refresh_reconciliation.ppd-devhub-submit-guide" for expectation in expectations)


def test_includes_rollback_reviewer_owner_fields_and_offline_commands() -> None:
    packet = build_guardrail_refresh_regression_review_packet(_source_packets())

    assert packet["rollback_notes"]
    assert any(note["note_id"] == "rollback.keep-current-guardrail-bundles" for note in packet["rollback_notes"])
    owner_ids = {owner["reviewer_owner_id"] for owner in packet["reviewer_owner_fields"]}
    assert owner_ids == {
        "PP&D agent readiness reviewer",
        "PP&D guardrail reviewer",
        "PP&D process reviewer",
        "ppd-reviewer:source-refresh",
    }
    assert ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"] in packet["offline_validation_commands"]
    assert ["python3", "-m", "pytest", "ppd/tests/test_guardrail_refresh_regression_review_packet.py"] in packet["offline_validation_commands"]


def test_validation_rejects_uncited_expectation_and_mutation_flag() -> None:
    packet = build_guardrail_refresh_regression_review_packet(_source_packets())
    packet["guardrail_predicate_expectations"][0]["source_evidence_ids"] = []
    packet["attestations"]["active_guardrail_mutation"] = True

    with pytest.raises(GuardrailRefreshRegressionReviewPacketError) as excinfo:
        validate_guardrail_refresh_regression_review_packet(packet)

    message = str(excinfo.value)
    assert "source_evidence_ids is required" in message
    assert "active_guardrail_mutation must not enable mutation" in message


def test_missing_source_packet_is_rejected() -> None:
    source_packets = _source_packets()
    source_packets.pop("agent_regression_refresh_packet")

    with pytest.raises(GuardrailRefreshRegressionReviewPacketError, match="missing source packet"):
        build_guardrail_refresh_regression_review_packet(source_packets)
