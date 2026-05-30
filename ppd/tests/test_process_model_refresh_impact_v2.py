from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

import pytest

from ppd.process_model_refresh_impact_v2 import (
    REQUIRED_ATTESTATIONS,
    ProcessModelRefreshImpactV2Error,
    assert_valid_process_model_refresh_impact_v2,
    build_process_model_refresh_impact_v2,
    validate_process_model_refresh_impact_v2,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "process_model_refresh_impact_v2"


def _input() -> dict[str, object]:
    return json.loads((FIXTURE_DIR / "input.json").read_text(encoding="utf-8"))


def _codes(packet: dict[str, object]) -> set[str]:
    return {issue.code for issue in validate_process_model_refresh_impact_v2(packet)}


def test_builds_fixture_first_process_model_refresh_impact_v2() -> None:
    packet = build_process_model_refresh_impact_v2(_input())

    assert packet["packet_type"] == "ppd.process_model_refresh_impact_v2"
    assert packet["fixture_only"] is True
    assert packet["source_packet_ids"] == {
        "requirement_regeneration_work_order_v2": "fixture-requirement-regeneration-work-order-v2",
        "process_model_impact_review_fixture": "fixture-process-impact-review-v2",
        "guardrail_bundle_update_candidate_fixture": "fixture-guardrail-bundle-update-candidate-v2",
    }


def test_converts_work_order_decisions_into_cited_process_stage_impacts() -> None:
    packet = build_process_model_refresh_impact_v2(_input())
    decisions = {item["requirement_id"]: item for item in packet["process_stage_impact_decisions"]}

    assert decisions["req-devhub-upload-corrections-attended"]["work_order_decision"] == "regenerate"
    assert decisions["req-devhub-upload-corrections-attended"]["impact_decision"] == "queue_process_stage_refresh_review"
    assert decisions["req-devhub-upload-corrections-attended"]["process_stage"] == "corrections/checksheets"
    assert decisions["req-plan-set-single-pdf"]["impact_decision"] == "queue_process_stage_human_review"
    assert decisions["req-standard-trade-license-profile"]["impact_decision"] == "retain_process_stage_without_active_mutation"
    assert decisions["req-devhub-upload-corrections-attended"]["source_evidence_ids"] == [
        "ev-devhub-faq-upload-corrections",
        "ppd-devhub-faq",
    ]
    assert all(decision["downstream_guardrail_bundle_ids"] for decision in decisions.values())
    assert all(decision["live_devhub_allowed"] is False for decision in decisions.values())
    assert all(decision["official_action_allowed"] is False for decision in decisions.values())
    assert all(decision["consequential_action_enabled"] is False for decision in decisions.values())
    assert all(decision["process_mutation_allowed"] is False for decision in decisions.values())
    assert all(decision["guardrail_mutation_allowed"] is False for decision in decisions.values())
    assert all(decision["prompt_mutation_allowed"] is False for decision in decisions.values())
    assert all(decision["surface_registry_mutation_allowed"] is False for decision in decisions.values())
    assert all(decision["monitoring_mutation_allowed"] is False for decision in decisions.values())
    assert all(decision["release_state_mutation_allowed"] is False for decision in decisions.values())
    assert all(decision["agent_state_mutation_allowed"] is False for decision in decisions.values())


def test_records_unsupported_paths_downstream_guardrails_reviewers_commands_and_attestations() -> None:
    packet = build_process_model_refresh_impact_v2(_input())

    unsupported = {item["path_id"]: item for item in packet["unsupported_path_notes"]}
    assert "unsupported-devhub-correction-official-upload" in unsupported
    assert "submit-or-certify-permit-request" in unsupported
    assert all(item["official_action_allowed"] is False for item in unsupported.values())
    assert all(item["consequential_action_enabled"] is False for item in unsupported.values())
    assert all(item["source_evidence_ids"] for item in unsupported.values())

    refs = {item["predicate_id"]: item for item in packet["downstream_guardrail_bundle_refs"]}
    assert set(refs) == {
        "predicate-devhub-correction-upload-attended",
        "predicate-single-pdf-human-review",
        "predicate-superseded-correction-upload-shortcut",
    }
    assert all(ref["guardrail_bundle_id"] == "guardrail-devhub-consequential-actions" for ref in refs.values())
    assert all(ref["activation_allowed"] is False for ref in refs.values())
    assert all(ref["consequential_action_enabled"] is False for ref in refs.values())
    assert all(ref["source_evidence_ids"] for ref in refs.values())

    owners = {item["reviewer_owner"] for item in packet["reviewer_owner_fields"]}
    assert {"ppd-human-review", "ppd-document-reviewer", "ppd-trade-permit-reviewer", "ppd-process-reviewer", "ppd-guardrail-reviewer"}.issubset(owners)
    assert packet["offline_validation_commands"] == [
        ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
        ["python3", "-m", "pytest", "ppd/tests/test_process_model_refresh_impact_v2.py"],
    ]
    assert packet["attestations"] == dict(REQUIRED_ATTESTATIONS)
    assert validate_process_model_refresh_impact_v2(packet) == []
    assert_valid_process_model_refresh_impact_v2(packet)


@pytest.mark.parametrize(
    ("mutator", "expected_code"),
    [
        (lambda packet: packet.update({"fixture_only": False}), "not_fixture_only"),
        (lambda packet: packet.update({"process_stage_impact_decisions": []}), "missing_process_stage_impact_decisions"),
        (lambda packet: packet["process_stage_impact_decisions"][0].update({"source_evidence_ids": []}), "uncited_process_stage_impact_decision"),
        (lambda packet: packet["process_stage_impact_decisions"][0].update({"reviewer_owner": ""}), "missing_reviewer_owner"),
        (lambda packet: packet["process_stage_impact_decisions"][0].update({"downstream_guardrail_bundle_ids": []}), "missing_decision_downstream_guardrail_refs"),
        (lambda packet: packet["process_stage_impact_decisions"][0].update({"downstream_guardrail_bundle_ids": ["missing-bundle"]}), "missing_downstream_guardrail_reference_for_decision"),
        (lambda packet: packet["process_stage_impact_decisions"][0].update({"live_devhub_allowed": True}), "forbidden_live_or_mutating_claim"),
        (lambda packet: packet["process_stage_impact_decisions"][0].update({"process_mutation_allowed": True}), "forbidden_live_or_mutating_claim"),
        (lambda packet: packet["process_stage_impact_decisions"][0].update({"guardrail_mutation_allowed": True}), "forbidden_live_or_mutating_claim"),
        (lambda packet: packet["process_stage_impact_decisions"][0].update({"prompt_mutation_allowed": True}), "forbidden_live_or_mutating_claim"),
        (lambda packet: packet["process_stage_impact_decisions"][0].update({"surface_registry_mutation_allowed": True}), "forbidden_live_or_mutating_claim"),
        (lambda packet: packet["process_stage_impact_decisions"][0].update({"monitoring_mutation_allowed": True}), "forbidden_live_or_mutating_claim"),
        (lambda packet: packet["process_stage_impact_decisions"][0].update({"release_state_mutation_allowed": True}), "forbidden_live_or_mutating_claim"),
        (lambda packet: packet["process_stage_impact_decisions"][0].update({"agent_state_mutation_allowed": True}), "forbidden_live_or_mutating_claim"),
        (lambda packet: packet["process_stage_impact_decisions"][0].update({"consequential_action_enabled": True}), "forbidden_live_or_mutating_claim"),
        (lambda packet: packet.update({"unsupported_path_notes": []}), "missing_unsupported_path_notes"),
        (lambda packet: packet.update({"unsupported_path_notes": packet["unsupported_path_notes"][1:]}), "missing_required_unsupported_path_disposition"),
        (lambda packet: packet["unsupported_path_notes"][0].update({"source_evidence_ids": []}), "uncited_unsupported_path_note"),
        (lambda packet: packet.update({"downstream_guardrail_bundle_refs": []}), "missing_downstream_guardrail_bundle_refs"),
        (lambda packet: packet["downstream_guardrail_bundle_refs"][0].update({"activation_allowed": True}), "forbidden_live_or_mutating_claim"),
        (lambda packet: packet["downstream_guardrail_bundle_refs"][0].update({"consequential_action_enabled": True}), "forbidden_live_or_mutating_claim"),
        (lambda packet: packet.update({"reviewer_owner_fields": []}), "missing_reviewer_owner_fields"),
        (lambda packet: packet["reviewer_owner_fields"][0].update({"owner_must_confirm_citations_before_refresh": False}), "missing_owner_confirmation_gate"),
        (lambda packet: packet["reviewer_owner_fields"][0].update({"owner_must_confirm_no_active_mutation": False}), "missing_owner_no_mutation_gate"),
        (lambda packet: packet.update({"offline_validation_commands": []}), "missing_offline_validation_commands"),
        (lambda packet: packet["attestations"].update({"no_live_devhub": False}), "missing_attestation"),
        (lambda packet: packet["attestations"].update({"no_live_browser": False}), "missing_attestation"),
        (lambda packet: packet["attestations"].update({"no_live_crawler": False}), "missing_attestation"),
        (lambda packet: packet["attestations"].update({"no_processor_invocation": False}), "missing_attestation"),
        (lambda packet: packet["attestations"].update({"no_llm_execution": False}), "missing_attestation"),
        (lambda packet: packet["attestations"].update({"no_process_mutation": False}), "missing_attestation"),
        (lambda packet: packet["attestations"].update({"no_guardrail_mutation": False}), "missing_attestation"),
        (lambda packet: packet["attestations"].update({"no_prompt_mutation": False}), "missing_attestation"),
        (lambda packet: packet["attestations"].update({"no_surface_registry_mutation": False}), "missing_attestation"),
        (lambda packet: packet["attestations"].update({"no_monitoring_mutation": False}), "missing_attestation"),
        (lambda packet: packet["attestations"].update({"no_release_state_mutation": False}), "missing_attestation"),
        (lambda packet: packet["attestations"].update({"no_agent_state_mutation": False}), "missing_attestation"),
        (lambda packet: packet.update({"notes": "live DevHub invoked"}), "forbidden_private_raw_or_live_reference"),
        (lambda packet: packet.update({"notes": "browser launched"}), "forbidden_private_raw_or_live_reference"),
        (lambda packet: packet.update({"notes": "crawler invoked"}), "forbidden_private_raw_or_live_reference"),
        (lambda packet: packet.update({"notes": "processor invoked"}), "forbidden_private_raw_or_live_reference"),
        (lambda packet: packet.update({"notes": "LLM executed"}), "forbidden_private_raw_or_live_reference"),
        (lambda packet: packet.update({"notes": "permit will be approved"}), "forbidden_private_raw_or_live_reference"),
        (lambda packet: packet.update({"notes": "submission enabled"}), "forbidden_private_raw_or_live_reference"),
        (lambda packet: packet.update({"private_fact": "owner phone number"}), "forbidden_private_or_authenticated_fact"),
        (lambda packet: packet.update({"authenticated_fact": "DevHub case status"}), "forbidden_private_or_authenticated_fact"),
        (lambda packet: packet.update({"active_surface_registry_mutated": True}), "forbidden_live_or_mutating_claim"),
        (lambda packet: packet.update({"active_monitoring_mutated": True}), "forbidden_live_or_mutating_claim"),
        (lambda packet: packet.update({"active_agent_state_mutated": True}), "forbidden_live_or_mutating_claim"),
    ],
)
def test_validation_rejects_incomplete_or_unsafe_packets(mutator, expected_code: str) -> None:
    packet = build_process_model_refresh_impact_v2(_input())
    mutator(packet)

    assert expected_code in _codes(packet)


def test_builder_rejects_unsafe_prerequisite_inputs() -> None:
    packet = deepcopy(_input())
    packet["process_model_impact_review_fixture"]["notes"] = "authenticated session"

    with pytest.raises(ProcessModelRefreshImpactV2Error) as excinfo:
        build_process_model_refresh_impact_v2(packet)

    assert {issue.code for issue in excinfo.value.issues} == {"forbidden_private_raw_or_live_reference"}
