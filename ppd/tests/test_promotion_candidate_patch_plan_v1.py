from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

import pytest

from ppd.promotion_candidate_patch_plan_v1 import (
    PromotionCandidatePatchPlanV1ValidationError,
    assert_valid_promotion_candidate_patch_plan_v1,
    validate_promotion_candidate_patch_plan_v1,
)

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "promotion_candidate_patch_plan_v1.json"

REQUIRED_INPUTS = {
    "promotion-readiness-checklist-v2",
    "process-model-impact-proposal-v1",
    "guardrail-bundle-impact-proposal-v1",
    "user-gap-analysis-impact-proposal-v1",
    "agent-response-delta-proposal-v1",
}

FORBIDDEN_MUTATION_KEYS = {
    "active_process_models",
    "active_guardrail_bundles",
    "prompts",
    "release_state",
    "agent_state",
    "live_sources",
    "devhub_artifacts",
}


def load_fixture() -> dict[str, object]:
    with FIXTURE_PATH.open(encoding="utf-8") as fixture_file:
        fixture = json.load(fixture_file)
    assert isinstance(fixture, dict)
    return fixture


def issue_codes(plan: dict[str, object]) -> set[str]:
    return {issue.code for issue in validate_promotion_candidate_patch_plan_v1(plan)}


def first_row(plan: dict[str, object]) -> dict[str, object]:
    rows = plan["inactive_fixture_update_rows"]
    assert isinstance(rows, list)
    row = rows[0]
    assert isinstance(row, dict)
    return row


def test_promotion_candidate_patch_plan_consumes_required_inputs() -> None:
    fixture = load_fixture()

    assert fixture["status"] == "inactive_fixture_only"
    assert set(fixture["consumes"]) == REQUIRED_INPUTS
    assert_valid_promotion_candidate_patch_plan_v1(fixture)


def test_promotion_candidate_patch_plan_does_not_mutate_active_state() -> None:
    fixture = load_fixture()
    scope = fixture["non_mutation_scope"]
    assert isinstance(scope, dict)

    assert set(scope) == FORBIDDEN_MUTATION_KEYS
    assert all(value is False for value in scope.values())
    rows = fixture["inactive_fixture_update_rows"]
    assert isinstance(rows, list)
    assert all(isinstance(row, dict) and row["active_mutation"] is False for row in rows)


def test_inactive_fixture_rows_are_ordered_cited_owned_and_fixture_family_scoped() -> None:
    fixture = load_fixture()
    rows = fixture["inactive_fixture_update_rows"]
    assert isinstance(rows, list)
    orders = [row["order"] for row in rows if isinstance(row, dict)]

    assert orders == sorted(orders)
    assert orders == list(range(1, len(rows) + 1))

    gate_ids = {gate["id"] for gate in fixture["dependency_gates"] if isinstance(gate, dict)}
    for row in rows:
        assert isinstance(row, dict)
        assert row["id"]
        assert row["affected_fixture_family_id"]
        assert row["candidate_action"]
        assert str(row["reviewer_owner"]).startswith("ppd-")
        assert row["rollback_note"]
        assert row["citations"]
        assert all(":" in citation for citation in row["citations"])
        assert set(row["dependency_gates"]).issubset(gate_ids)


def test_dependency_gates_and_validation_commands_are_deterministic() -> None:
    fixture = load_fixture()

    for gate in fixture["dependency_gates"]:
        assert gate["state"].startswith("blocked_until_")
        assert gate["evidence"]

    assert fixture["validation_commands"] == [
        ["python3", "-m", "py_compile", "ppd/promotion_candidate_patch_plan_v1.py"],
        ["python3", "-m", "pytest", "ppd/tests/test_promotion_candidate_patch_plan_v1.py"],
        ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
    ]


@pytest.mark.parametrize(
    ("field", "value", "expected_code"),
    [
        ("citations", [], "uncited_patch_row"),
        ("affected_fixture_family_id", "", "missing_affected_fixture_family_id"),
        ("dependency_gates", [], "missing_dependency_gates"),
        ("reviewer_owner", "", "missing_reviewer_owner"),
        ("rollback_note", "", "missing_rollback_note"),
    ],
)
def test_validator_rejects_missing_row_metadata(field: str, value: object, expected_code: str) -> None:
    plan = load_fixture()
    first_row(plan)[field] = value

    assert expected_code in issue_codes(plan)


def test_validator_rejects_unknown_dependency_gate() -> None:
    plan = load_fixture()
    first_row(plan)["dependency_gates"] = ["gate-not-declared"]

    assert "unknown_dependency_gate" in issue_codes(plan)


@pytest.mark.parametrize(
    ("text", "expected_code"),
    [
        ("Use authenticated DevHub session browser state as evidence.", "private_authenticated_session_or_browser_artifact"),
        ("Attach raw crawl PDF data from downloaded_document.pdf.", "raw_crawl_pdf_or_downloaded_data"),
        ("This guarantees permit approval after review.", "legal_or_permitting_outcome_guarantee"),
        ("Click submit application and make payment once this row lands.", "consequential_action_execution_language"),
    ],
)
def test_validator_rejects_prohibited_claims_artifacts_and_action_language(text: str, expected_code: str) -> None:
    plan = load_fixture()
    first_row(plan)["candidate_action"] = text

    assert expected_code in issue_codes(plan)


@pytest.mark.parametrize(
    "flag_name",
    [
        "active_source_mutation",
        "active_document_mutation",
        "active_requirement_mutation",
        "active_process_mutation",
        "active_guardrail_mutation",
        "active_prompt_mutation",
        "active_release_state_mutation",
        "active_agent_state_mutation",
    ],
)
def test_validator_rejects_active_mutation_flags(flag_name: str) -> None:
    plan = load_fixture()
    first_row(plan)[flag_name] = True

    assert "active_mutation_flag" in issue_codes(plan)


def test_validator_rejects_non_mutation_scope_becoming_active() -> None:
    plan = load_fixture()
    scope = plan["non_mutation_scope"]
    assert isinstance(scope, dict)
    scope["release_state"] = True

    assert "active_mutation_flag" in issue_codes(plan)


def test_assert_helper_raises_with_issue_details() -> None:
    plan = load_fixture()
    broken = deepcopy(plan)
    first_row(broken)["citations"] = []

    with pytest.raises(PromotionCandidatePatchPlanV1ValidationError) as exc_info:
        assert_valid_promotion_candidate_patch_plan_v1(broken)

    assert exc_info.value.issues[0].code == "uncited_patch_row"
