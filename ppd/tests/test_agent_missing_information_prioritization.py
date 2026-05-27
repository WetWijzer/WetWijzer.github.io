from __future__ import annotations

import json
from pathlib import Path

import pytest

from ppd.agent_missing_information_prioritization import (
    MissingInformationPrioritizationError,
    load_prioritized_missing_information_fixture,
    prioritize_missing_information_prompts,
    validate_missing_information_prioritization_fixture,
)


def _fixture_path() -> Path:
    return (
        Path(__file__).parent
        / "fixtures"
        / "missing_information_prioritization"
        / "blocking_dependency_stage_fixture.json"
    )


def _load_fixture() -> dict:
    return json.loads(_fixture_path().read_text(encoding="utf-8"))


def test_prioritization_orders_only_next_blocking_unresolved_prompts_by_stage() -> None:
    result = load_prioritized_missing_information_fixture(fixture_path=_fixture_path())

    assert result["case_id"] == "synthetic-residential-addition-redacted"
    assert result["next_safe_action"] == "prepare_reversible_local_draft_plan"
    assert result["prioritization"] == "blocking_dependency_stage_then_status"
    assert [prompt["fact_id"] for prompt in result["prompts"]] == [
        "property_tax_account",
        "contractor_license_status",
        "prepared_plan_set_status",
        "owner_authorization",
    ]
    assert [prompt["status"] for prompt in result["prompts"]] == [
        "ambiguous",
        "stale",
        "missing",
        "conflicting",
    ]
    assert "applicant_email" not in json.dumps(result)
    assert "future_fee_confirmation" not in json.dumps(result)


def test_prioritization_redacts_private_values_and_omits_local_paths() -> None:
    result = prioritize_missing_information_prompts(_load_fixture())
    rendered = json.dumps(result, sort_keys=True)

    assert "current_value" not in rendered
    assert "observed_value" not in rendered
    assert "private_value" not in rendered
    assert "local_path" not in rendered
    assert "file://" not in rendered
    assert "/home/" not in rendered
    assert "[REDACTED]" not in rendered


def test_prioritization_rejects_fixture_with_local_path() -> None:
    fixture = _load_fixture()
    fixture["facts"][0]["local_path"] = "/home/example/private-plan.pdf"

    with pytest.raises(MissingInformationPrioritizationError):
        prioritize_missing_information_prompts(fixture)


def test_prioritization_validation_reports_valid_fixture_cleanly() -> None:
    assert validate_missing_information_prioritization_fixture(_load_fixture()) == []
