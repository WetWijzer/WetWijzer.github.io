from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from ppd.agent_readiness.guardrail_api_contract import (
    RESPONSE_TYPES,
    GuardrailApiContractError,
    build_guardrail_api_contract_packet,
    load_guardrail_api_contract_fixture,
    validate_guardrail_api_contract_packet,
)


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "guardrail_api_contract" / "synthetic_case_packet.json"


def _fixture() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _packet() -> dict:
    return load_guardrail_api_contract_fixture(FIXTURE_PATH)


def _build(fixture: dict) -> dict:
    return build_guardrail_api_contract_packet(
        compiled_guardrail_bundle=fixture["compiled_guardrail_bundle"],
        user_gap_analysis=fixture["user_gap_analysis"],
        source_evidence=fixture["source_evidence"],
    )


def test_loads_fixture_first_agent_guardrail_api_packet() -> None:
    packet = _packet()

    assert packet["packet_type"] == "ppd.guardrail_api_contract.v1"
    assert packet["fixture_first"] is True
    assert packet["live_services_called"] is False
    assert packet["metadata_only"] is True
    assert packet["response_order"] == list(RESPONSE_TYPES)
    assert packet["case_id"] == "case-synthetic-guardrail-api-contract"
    assert packet["guardrail_bundle_id"] == "guardrail-api-contract-single-pdf-v1"
    assert validate_guardrail_api_contract_packet(packet) == []


def test_packet_exposes_the_five_agent_response_contracts() -> None:
    packet = _packet()
    responses = {response["response_type"]: response for response in packet["responses"]}

    assert set(responses) == set(RESPONSE_TYPES)
    assert responses["missing_information"]["missing_facts"] == ["project_scope_summary"]
    assert responses["missing_information"]["missing_documents"] == ["single_pdf_plan_set"]
    assert responses["reversible_draft"]["actions"][0]["action_id"] == "prepare-local-upload-staging-checklist"
    assert responses["reversible_draft"]["actions"][0]["blocked_by_missing_documents"] == ["single_pdf_plan_set"]
    assert {action["action_id"] for action in responses["refused_action"]["actions"]} == {
        "pay-review-fees",
        "submit-permit-request",
        "upload-plans-to-official-record",
    }
    assert all(action["requires_manual_handoff"] is True for action in responses["refused_action"]["actions"])
    assert all(action["requires_exact_confirmation"] is True for action in responses["refused_action"]["actions"])
    assert all(action["exact_confirmation_blocks_execution"] is True for action in responses["refused_action"]["actions"])
    assert responses["exact_confirmation"]["confirmations"][0]["confirmation_text"]
    assert responses["citation_explanation"]["covered_outputs"] == list(RESPONSE_TYPES[:-1])


def test_each_agent_response_is_cited_from_committed_current_evidence() -> None:
    packet = _packet()

    for response in packet["responses"]:
        assert response["citations"]
        for citation in response["citations"]:
            assert citation["evidence_id"].startswith("ev-")
            assert citation["canonical_url"].startswith("https://www.portland.gov/ppd/")
            assert citation["last_verified_at"] == "2026-05-08T00:00:00Z"
            assert citation["freshness_status"] == "current"


def test_rejects_uncited_agent_response_packets() -> None:
    packet = _packet()
    packet["responses"][0]["citations"] = []

    errors = validate_guardrail_api_contract_packet(packet)

    assert any("must include citations" in error for error in errors)


def test_rejects_incomplete_or_stale_citations() -> None:
    packet = _packet()
    packet["responses"][1]["citations"][0]["freshness_status"] = "stale"
    packet["responses"][1]["citations"][0]["canonical_url"] = "https://example.test/not-ppd"

    errors = validate_guardrail_api_contract_packet(packet)

    assert any("freshness_status must not be stale" in error or "stale status" in error for error in errors)
    assert any("official PP&D URL" in error for error in errors)


def test_rejects_stale_guardrail_bundles() -> None:
    fixture = deepcopy(_fixture())
    fixture["compiled_guardrail_bundle"]["validation_status"] = "needs_refresh"

    with pytest.raises(GuardrailApiContractError) as excinfo:
        _build(fixture)

    assert any("validation_status" in problem for problem in excinfo.value.problems)


def test_rejects_private_values_and_raw_live_artifact_fields() -> None:
    fixture = deepcopy(_fixture())
    fixture["user_gap_analysis"]["known_facts"].append(
        {"fact_id": "site_address", "value": "123 private street"}
    )

    with pytest.raises(GuardrailApiContractError) as excinfo:
        _build(fixture)

    assert any("private value field" in problem for problem in excinfo.value.problems)


def test_rejects_local_private_paths_credentials_and_payment_details() -> None:
    fixture = deepcopy(_fixture())
    fixture["user_gap_analysis"]["matched_documents"].append(
        {"document_id": "plans", "document_ref": "/home/alex/private/plans.pdf"}
    )
    fixture["user_gap_analysis"]["known_facts"].append({"fact_id": "login", "password": "redacted"})
    fixture["user_gap_analysis"]["blocked_actions"][0]["payment_details"] = {"card_number": "4111111111111111"}

    with pytest.raises(GuardrailApiContractError) as excinfo:
        _build(fixture)

    problems = excinfo.value.problems
    assert any("private or live artifact reference" in problem for problem in problems)
    assert any("password" in problem for problem in problems)
    assert any("payment_details" in problem for problem in problems)


def test_rejects_mismatched_bundle_and_gap_analysis() -> None:
    fixture = deepcopy(_fixture())
    fixture["user_gap_analysis"]["process_id"] = "other-process"

    with pytest.raises(GuardrailApiContractError) as excinfo:
        _build(fixture)

    assert any("process_id values must match" in problem for problem in excinfo.value.problems)


def test_rejects_blocked_consequential_action_without_refusal_and_confirmation() -> None:
    fixture = deepcopy(_fixture())
    fixture["compiled_guardrail_bundle"]["refused_action_predicates"] = [
        item
        for item in fixture["compiled_guardrail_bundle"]["refused_action_predicates"]
        if item["action_id"] != "pay-review-fees"
    ]

    with pytest.raises(GuardrailApiContractError) as excinfo:
        _build(fixture)

    assert any("pay-review-fees" in problem for problem in excinfo.value.problems)


def test_rejects_consequential_next_safe_actions() -> None:
    fixture = deepcopy(_fixture())
    fixture["user_gap_analysis"]["next_safe_actions"].append(
        {
            "next_safe_action_id": "submit-permit-request",
            "action_id": "submit-permit-request",
            "classification": "submission",
        }
    )

    with pytest.raises(GuardrailApiContractError) as excinfo:
        _build(fixture)

    assert any("next_safe_actions cannot include consequential action" in problem for problem in excinfo.value.problems)


def test_rejects_unsupported_ready_to_submit_statuses() -> None:
    packet = _packet()
    packet["responses"][0]["status"] = "ready_to_submit"

    errors = validate_guardrail_api_contract_packet(packet)

    assert any("ready-to-submit" in error for error in errors)


def test_rejects_upload_submission_certification_payment_or_scheduling_without_exact_confirmation_block() -> None:
    packet = _packet()
    refused = next(response for response in packet["responses"] if response["response_type"] == "refused_action")
    refused["actions"][0]["requires_exact_confirmation"] = False
    refused["actions"][1]["exact_confirmation_blocks_execution"] = False
    exact = next(response for response in packet["responses"] if response["response_type"] == "exact_confirmation")
    exact["confirmations"] = [
        confirmation for confirmation in exact["confirmations"] if confirmation["action_id"] != refused["actions"][2]["action_id"]
    ]

    errors = validate_guardrail_api_contract_packet(packet)

    assert any("must require exact confirmation" in error for error in errors)
    assert any("must block execution until exact confirmation" in error for error in errors)
    assert any("must link to an exact-confirmation response" in error for error in errors)
