from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from ppd.logic.missing_information_prioritization import (
    MissingInformationPrioritizationError,
    prioritize_missing_information,
    validate_missing_information_prioritization,
)


def _fixture() -> dict:
    path = Path(__file__).parent / "fixtures" / "missing_information_prioritization" / "validation_guardrails_fixture.json"
    return json.loads(path.read_text(encoding="utf-8"))


def test_prioritization_preserves_citation_backed_reasons_and_blocks_consequential_actions() -> None:
    result = prioritize_missing_information(_fixture())

    assert [prompt["fact_id"] for prompt in result["prompts"]] == ["prepared_plan_set_status"]
    prompt = result["prompts"][0]
    assert prompt["reason"]
    assert prompt["source_requirement_ids"] == ["req-single-pdf-plan-set"]
    assert prompt["reason_citation_ids"] == ["cite-submit-plans-online-single-pdf"]
    assert result["blocked_actions"] == ["submit_permit_application"]
    assert result["required_confirmations"] == [
        {
            "action": "submit_permit_application",
            "required_exact_text": "CONFIRM submit_permit_application",
        }
    ]


def test_prioritization_refuses_to_ask_known_fresh_facts() -> None:
    fixture = _fixture()
    fixture["facts"][1]["needed_for_next_safe_action"] = True

    with pytest.raises(MissingInformationPrioritizationError, match="known and fresh"):
        prioritize_missing_information(fixture)


def test_prioritization_refuses_credentials_payment_details_and_auth_state() -> None:
    fixture = _fixture()
    fixture["facts"].append(
        {
            "fact_id": "devhub_password",
            "status": "missing",
            "needed_for_next_safe_action": True,
            "prompt": "What is your DevHub password?",
            "reason": "Credentials must never be requested by missing-information prioritization.",
            "source_requirement_ids": ["req-devhub-sign-in-attended"],
            "reason_citation_ids": ["cite-devhub-sign-in-guide"],
            "blocked_next_safe_action": "account setup or manual login",
        }
    )

    errors = validate_missing_information_prioritization(fixture)

    assert errors
    assert "refused sensitive information" in errors[0]


def test_prioritization_requires_reason_citations_for_emitted_prompts() -> None:
    fixture = _fixture()
    fixture["facts"][0].pop("reason_citation_ids")

    with pytest.raises(MissingInformationPrioritizationError, match="reason_citation_ids"):
        prioritize_missing_information(fixture)


def test_exact_confirmation_unblocks_the_matching_consequential_action_only() -> None:
    fixture = copy.deepcopy(_fixture())
    fixture["required_confirmations"] = [
        {
            "action": "submit_permit_application",
            "explicit": True,
            "confirmation_text": "CONFIRM submit_permit_application",
        }
    ]

    result = prioritize_missing_information(fixture)

    assert result["blocked_actions"] == []
    assert result["required_confirmations"] == []
