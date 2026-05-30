from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

import pytest

from ppd.requirement_regeneration_work_order_v2 import (
    REQUIRED_ATTESTATIONS,
    RequirementRegenerationWorkOrderV2Error,
    assert_valid_requirement_regeneration_work_order_v2,
    build_requirement_regeneration_work_order_v2,
    validate_requirement_regeneration_work_order_v2,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "requirement_regeneration_work_order_v2"


def _input() -> dict[str, object]:
    return json.loads((FIXTURE_DIR / "input.json").read_text(encoding="utf-8"))


def _codes(packet: dict[str, object]) -> set[str]:
    return {issue.code for issue in validate_requirement_regeneration_work_order_v2(packet)}


def test_builds_fixture_first_requirement_regeneration_work_order_v2() -> None:
    packet = build_requirement_regeneration_work_order_v2(_input())

    assert packet["packet_type"] == "ppd.requirement_regeneration_work_order_v2"
    assert packet["fixture_only"] is True
    assert packet["source_packets"] == {
        "source_freshness_drift_triage_v2": "source-freshness-drift-triage-v2-fixture",
        "prior_requirement_rerun_work_queues": ["fixture-requirement-rerun-work-queue-20260529"],
        "requirement_extraction_fixture_ids": [
            "fixture-req-devhub-upload-corrections-attended",
            "fixture-req-plan-set-single-pdf",
            "fixture-req-standard-trade-unchanged",
        ],
    }


def test_queues_unchanged_review_and_regenerate_decisions_with_citations() -> None:
    packet = build_requirement_regeneration_work_order_v2(_input())
    decisions = {item["requirement_id"]: item for item in packet["queued_requirement_decisions"]}

    assert decisions["req-devhub-upload-corrections-attended"]["decision"] == "regenerate"
    assert decisions["req-plan-set-single-pdf"]["decision"] == "review"
    assert decisions["req-standard-trade-license-profile"]["decision"] == "unchanged"
    assert decisions["req-devhub-upload-corrections-attended"]["source_evidence_ids"] == [
        "ev-devhub-faq-upload-corrections",
        "ppd-devhub-faq",
    ]
    blocked_fields = (
        "live_extraction_allowed",
        "crawler_invocation_allowed",
        "processor_invocation_allowed",
        "devhub_invocation_allowed",
        "llm_invocation_allowed",
        "requirement_mutation_allowed",
        "process_mutation_allowed",
        "guardrail_mutation_allowed",
        "prompt_mutation_allowed",
        "source_mutation_allowed",
        "schedule_mutation_allowed",
        "monitoring_mutation_allowed",
        "release_state_mutation_allowed",
        "agent_state_mutation_allowed",
    )
    for field in blocked_fields:
        assert all(item[field] is False for item in decisions.values())


def test_records_source_evidence_expectations_and_reviewer_owner_fields() -> None:
    packet = build_requirement_regeneration_work_order_v2(_input())

    expectation = {
        row["requirement_id"]: row for row in packet["source_evidence_expectations"]
    }["req-plan-set-single-pdf"]
    assert expectation["decision"] == "review"
    assert expectation["reviewer_owner"] == "ppd-document-reviewer"
    assert expectation["expectations"] == [
        "confirm Single PDF guidance still supports one plan-set PDF plus separate supporting documents"
    ]

    owners = {row["requirement_id"]: row for row in packet["reviewer_owner_fields"]}
    assert owners["req-devhub-upload-corrections-attended"] == {
        "requirement_id": "req-devhub-upload-corrections-attended",
        "reviewer_owner": "ppd-human-review",
        "decision_owner_scope": "regenerate",
        "owner_must_confirm_citations_before_regeneration": True,
    }


def test_valid_packet_has_offline_validation_commands_and_attestations() -> None:
    packet = build_requirement_regeneration_work_order_v2(_input())

    assert packet["offline_validation_commands"] == [
        ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
        ["python3", "-m", "pytest", "ppd/tests/test_requirement_regeneration_work_order_v2.py"],
    ]
    assert packet["attestations"] == dict(REQUIRED_ATTESTATIONS)
    assert validate_requirement_regeneration_work_order_v2(packet) == []
    assert_valid_requirement_regeneration_work_order_v2(packet)


@pytest.mark.parametrize(
    ("mutator", "expected_code"),
    [
        (lambda packet: packet.update({"fixture_only": False}), "not_fixture_only"),
        (lambda packet: packet.update({"queued_requirement_decisions": []}), "missing_queued_requirement_decisions"),
        (lambda packet: packet["queued_requirement_decisions"][0].update({"source_evidence_ids": []}), "uncited_requirement_decision"),
        (lambda packet: packet["queued_requirement_decisions"][0].update({"source_evidence_expectations": []}), "missing_source_evidence_expectations"),
        (lambda packet: packet["queued_requirement_decisions"][0].update({"reviewer_owner": ""}), "missing_reviewer_owner"),
        (lambda packet: packet["queued_requirement_decisions"][0].update({"decision": "approve"}), "invalid_decision"),
        (lambda packet: packet["queued_requirement_decisions"][0].update({"live_extraction_allowed": True}), "forbidden_live_or_mutating_claim"),
        (lambda packet: packet["queued_requirement_decisions"][0].update({"devhub_invocation_allowed": True}), "forbidden_live_or_mutating_claim"),
        (lambda packet: packet["queued_requirement_decisions"][0].update({"llm_invocation_allowed": True}), "forbidden_live_or_mutating_claim"),
        (lambda packet: packet["queued_requirement_decisions"][0].update({"requirement_mutation_allowed": True}), "forbidden_live_or_mutating_claim"),
        (lambda packet: packet["queued_requirement_decisions"][0].update({"prompt_mutation_allowed": True}), "forbidden_live_or_mutating_claim"),
        (lambda packet: packet["queued_requirement_decisions"][0].update({"source_mutation_allowed": True}), "forbidden_live_or_mutating_claim"),
        (lambda packet: packet["queued_requirement_decisions"][0].update({"schedule_mutation_allowed": True}), "forbidden_live_or_mutating_claim"),
        (lambda packet: packet["queued_requirement_decisions"][0].update({"monitoring_mutation_allowed": True}), "forbidden_live_or_mutating_claim"),
        (lambda packet: packet["queued_requirement_decisions"][0].update({"release_state_mutation_allowed": True}), "forbidden_live_or_mutating_claim"),
        (lambda packet: packet["queued_requirement_decisions"][0].update({"agent_state_mutation_allowed": True}), "forbidden_live_or_mutating_claim"),
        (lambda packet: packet["attestations"].update({"no_processor_invocation": False}), "missing_attestation"),
        (lambda packet: packet["attestations"].update({"no_llm_invocation": False}), "missing_attestation"),
        (lambda packet: packet["attestations"].update({"no_agent_state_mutation": False}), "missing_attestation"),
        (lambda packet: packet.update({"raw_pdf_reference": "sanitized fixture pointer"}), "forbidden_private_raw_or_live_reference"),
        (lambda packet: packet.update({"private_fact": "fixture-only applicant private value"}), "forbidden_private_raw_or_live_reference"),
        (lambda packet: packet.update({"notes": "permit will be approved"}), "forbidden_private_raw_or_live_reference"),
    ],
)
def test_validation_rejects_incomplete_or_unsafe_packets(mutator, expected_code: str) -> None:
    packet = build_requirement_regeneration_work_order_v2(_input())
    mutator(packet)

    assert expected_code in _codes(packet)


def test_validation_rejects_missing_cross_table_evidence_and_owners() -> None:
    packet = build_requirement_regeneration_work_order_v2(_input())
    packet["source_evidence_expectations"][0]["expected_source_evidence_ids"] = []
    packet["reviewer_owner_fields"][0]["reviewer_owner"] = ""

    assert {"uncited_requirement_decision", "missing_reviewer_owner"}.issubset(_codes(packet))


def test_builder_rejects_unsafe_prerequisite_inputs() -> None:
    packet = deepcopy(_input())
    packet["source_freshness_drift_triage_v2"]["notes"] = "live crawler executed"

    with pytest.raises(RequirementRegenerationWorkOrderV2Error) as excinfo:
        build_requirement_regeneration_work_order_v2(packet)

    assert {issue.code for issue in excinfo.value.issues} == {"forbidden_private_raw_or_live_reference"}
