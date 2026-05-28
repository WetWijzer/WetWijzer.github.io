from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from ppd.agent_readiness.guardrail_export import (
    GuardrailExportReadinessError,
    build_guardrail_export_readiness_packet,
    load_guardrail_export_fixture,
    validate_guardrail_export_readiness_packet,
)


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "guardrail_export" / "single_bundle_gap_packet.json"


def _fixture() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def test_loads_fixture_first_guardrail_export_packet() -> None:
    packet = load_guardrail_export_fixture(FIXTURE_PATH)

    assert packet["packet_type"] == "ppd.guardrail_export_readiness.v1"
    assert packet["fixture_first"] is True
    assert packet["live_services_called"] is False
    assert packet["metadata_only"] is True
    assert packet["case_id"] == "case-synthetic-single-pdf-gap"
    assert packet["guardrail_bundle_id"] == "guardrail-single-pdf-upload-staging-v1"
    assert packet["predicate_counts"] == {
        "missing_information": 3,
        "reversible_actions": 1,
        "refused_actions": 5,
        "exact_confirmations": 5,
    }
    assert validate_guardrail_export_readiness_packet(packet) == []


def test_packet_exposes_agent_facing_missing_information_predicates() -> None:
    packet = load_guardrail_export_fixture(FIXTURE_PATH)

    by_id = {predicate["predicate_id"]: predicate for predicate in packet["missing_information_predicates"]}

    assert set(by_id) == {
        "deterministic-missing:3",
        "missing-document:single_pdf_plan_set",
        "missing-fact:project_scope_summary",
    }
    assert by_id["missing-fact:project_scope_summary"]["predicate"] == "requires_missing_fact_answer"
    assert by_id["missing-document:single_pdf_plan_set"]["predicate"] == "requires_missing_document_match"
    assert "do not upload" in by_id["missing-document:single_pdf_plan_set"]["agent_instruction"].lower()


def test_packet_keeps_reversible_and_refused_actions_separate() -> None:
    packet = load_guardrail_export_fixture(FIXTURE_PATH)

    reversible = packet["reversible_action_predicates"][0]
    assert reversible["action_id"] == "prepare-local-upload-staging-checklist"
    assert reversible["available_as_next_safe_action"] is True
    assert reversible["blocked_by_missing_information"] == ["project_scope_summary", "single_pdf_plan_set"]

    refused_actions = {predicate["action_id"]: predicate for predicate in packet["refused_action_predicates"]}
    assert set(refused_actions) == {
        "certify-application",
        "pay-review-fees",
        "schedule-inspection",
        "submit-permit-request",
        "upload-plans-to-official-record",
    }
    for predicate in refused_actions.values():
        assert predicate["default_outcome"] == "refuse"
        assert predicate["requires_manual_handoff"] is True
        assert predicate["requires_exact_confirmation"] is True


def test_packet_marks_exact_confirmation_requirements_from_gap_analysis() -> None:
    packet = load_guardrail_export_fixture(FIXTURE_PATH)

    confirmations = {predicate["confirmation_id"]: predicate for predicate in packet["exact_confirmation_predicates"]}
    assert confirmations["submit-permit-request"]["required_by_gap_analysis"] is True
    assert confirmations["upload-plans-to-official-record"]["required_by_gap_analysis"] is True
    assert confirmations["pay-review-fees"]["required_by_gap_analysis"] is True
    assert confirmations["schedule-inspection"]["required_by_gap_analysis"] is True
    assert confirmations["submit-permit-request"]["confirmation_text"].startswith("I confirm that I am ready")


def test_export_rejects_private_or_live_artifact_fields() -> None:
    fixture = _fixture()
    fixture["user_gap_analysis"]["known_facts"] = [{"fact_id": "site_address", "value": "123 private street"}]

    with pytest.raises(GuardrailExportReadinessError) as excinfo:
        build_guardrail_export_readiness_packet(fixture["guardrail_bundle"], fixture["user_gap_analysis"])

    assert any("private value field" in problem for problem in excinfo.value.problems)


def test_export_rejects_local_private_paths() -> None:
    fixture = _fixture()
    fixture["user_gap_analysis"]["matched_documents"] = [
        {"document_id": "plans", "artifact_ref": "/home/person/private/plans.pdf"}
    ]

    with pytest.raises(GuardrailExportReadinessError) as excinfo:
        build_guardrail_export_readiness_packet(fixture["guardrail_bundle"], fixture["user_gap_analysis"])

    assert any("private or local artifact reference" in problem for problem in excinfo.value.problems)


def test_export_rejects_mismatched_bundle_and_gap_analysis() -> None:
    fixture = deepcopy(_fixture())
    fixture["user_gap_analysis"]["guardrail_bundle_id"] = "other-guardrail-bundle"

    with pytest.raises(GuardrailExportReadinessError) as excinfo:
        build_guardrail_export_readiness_packet(fixture["guardrail_bundle"], fixture["user_gap_analysis"])

    assert any("guardrail_bundle_id values must match" in problem for problem in excinfo.value.problems)


def test_export_rejects_stale_bundles_and_stale_gap_evidence() -> None:
    fixture = _fixture()
    fixture["guardrail_bundle"]["validation_status"] = "stale"
    fixture["user_gap_analysis"]["stale_evidence"] = ["ev-devhub-submit-application-guide"]

    with pytest.raises(GuardrailExportReadinessError) as excinfo:
        build_guardrail_export_readiness_packet(fixture["guardrail_bundle"], fixture["user_gap_analysis"])

    assert any("stale bundle" in problem for problem in excinfo.value.problems)
    assert any("stale evidence" in problem for problem in excinfo.value.problems)


def test_export_rejects_missing_predicate_citation_evidence() -> None:
    fixture = _fixture()
    fixture["guardrail_bundle"]["refused_action_predicates"][0].pop("source_evidence_ids")

    with pytest.raises(GuardrailExportReadinessError) as excinfo:
        build_guardrail_export_readiness_packet(fixture["guardrail_bundle"], fixture["user_gap_analysis"])

    assert any("must cite source_evidence_ids" in problem for problem in excinfo.value.problems)


def test_export_rejects_omitted_payment_submission_upload_or_scheduling_refusals() -> None:
    fixture = _fixture()
    fixture["guardrail_bundle"]["refused_action_predicates"] = [
        predicate
        for predicate in fixture["guardrail_bundle"]["refused_action_predicates"]
        if predicate["action_id"] != "pay-review-fees"
    ]

    with pytest.raises(GuardrailExportReadinessError) as excinfo:
        build_guardrail_export_readiness_packet(fixture["guardrail_bundle"], fixture["user_gap_analysis"])

    assert any("blocked consequential action pay-review-fees" in problem for problem in excinfo.value.problems)


def test_export_rejects_generic_exact_confirmation_language() -> None:
    fixture = _fixture()
    fixture["guardrail_bundle"]["exact_confirmation_predicates"][0]["confirmation_text"] = "I confirm."

    with pytest.raises(GuardrailExportReadinessError) as excinfo:
        build_guardrail_export_readiness_packet(fixture["guardrail_bundle"], fixture["user_gap_analysis"])

    assert any("action-specific confirmation language" in problem for problem in excinfo.value.problems)
