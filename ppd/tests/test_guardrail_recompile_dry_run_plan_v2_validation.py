from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from ppd.guardrail_recompile_dry_run_plan_v2 import compile_guardrail_recompile_dry_run_plan_v2
from ppd.guardrail_recompile_dry_run_plan_v2_validation import (
    assert_valid_guardrail_recompile_dry_run_plan_v2,
    validate_guardrail_recompile_dry_run_plan_v2,
)

FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "guardrail_recompile_dry_run_plan_v2"
    / "requirement_reextraction_dry_run_packet_v2.json"
)


def _valid_plan() -> dict:
    packet = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    return compile_guardrail_recompile_dry_run_plan_v2(packet)


def _codes(plan: dict) -> set[str]:
    return {issue.code for issue in validate_guardrail_recompile_dry_run_plan_v2(plan)}


def _without_first_row_field(field: str) -> dict:
    plan = copy.deepcopy(_valid_plan())
    del plan["ordered_synthetic_guardrail_bundle_delta_rows"][0][field]
    return plan


def _empty_first_row_field(field: str) -> dict:
    plan = copy.deepcopy(_valid_plan())
    plan["ordered_synthetic_guardrail_bundle_delta_rows"][0][field] = []
    return plan


def test_valid_guardrail_recompile_dry_run_plan_has_no_issues() -> None:
    plan = _valid_plan()

    assert validate_guardrail_recompile_dry_run_plan_v2(plan) == []
    assert_valid_guardrail_recompile_dry_run_plan_v2(plan)


def test_rejects_missing_guardrail_delta_rows() -> None:
    plan = _valid_plan()
    plan["ordered_synthetic_guardrail_bundle_delta_rows"] = []

    assert "missing_guardrail_delta_rows" in _codes(plan)


@pytest.mark.parametrize(
    ("field", "expected_code"),
    [
        ("deterministic_predicate_impact_placeholders", "missing_deterministic_predicate_impact_placeholders"),
        ("deontic_rule_placeholders", "missing_deontic_rule_placeholders"),
        ("temporal_rule_placeholders", "missing_temporal_rule_placeholders"),
        ("reversible_action_predicate_placeholders", "missing_reversible_action_predicate_placeholders"),
        ("exact_confirmation_predicate_placeholders", "missing_exact_confirmation_predicate_placeholders"),
        ("refused_action_predicate_placeholders", "missing_refused_action_predicate_placeholders"),
        ("migration_risk_notes", "missing_migration_risk_notes"),
    ],
)
def test_rejects_missing_placeholder_lists(field: str, expected_code: str) -> None:
    assert expected_code in _codes(_without_first_row_field(field))
    assert expected_code in _codes(_empty_first_row_field(field))


def test_rejects_missing_reviewer_dispositions() -> None:
    assert "missing_reviewer_dispositions" in _codes(_without_first_row_field("reviewer_disposition_placeholders"))


def test_rejects_missing_validation_commands() -> None:
    plan = _valid_plan()
    del plan["offline_validation_commands"]

    assert "missing_validation_commands" in _codes(plan)


def test_rejects_validation_commands_that_touch_forbidden_targets() -> None:
    plan = _valid_plan()
    plan["offline_validation_commands"] = [["python3", "ppd/release_state/apply.py"]]

    codes = _codes(plan)
    assert "invalid_validation_commands" in codes
    assert "mutation_flag" in codes


@pytest.mark.parametrize(
    ("field", "value", "expected_code"),
    [
        ("raw_body", "raw", "private_artifact_reference"),
        ("session_file", "ppd/tests/fixtures/session.json", "private_artifact_reference"),
        ("browser_trace_path", "trace.zip", "private_artifact_reference"),
        ("downloaded_document_path", "downloaded permit.pdf", "private_artifact_reference"),
        ("live_crawl_completed", True, "live_crawl_or_devhub_claim"),
        ("devhub_completed", True, "live_crawl_or_devhub_claim"),
        ("legal_advice", True, "outcome_guarantee"),
        ("permit_approved", True, "outcome_guarantee"),
        ("active_source_mutation", True, "mutation_flag"),
        ("update_requirements", True, "mutation_flag"),
        ("mutate_process_models", True, "mutation_flag"),
        ("mutate_guardrails", True, "mutation_flag"),
        ("update_prompts", True, "mutation_flag"),
        ("update_contracts", True, "mutation_flag"),
        ("update_devhub_surfaces", True, "mutation_flag"),
        ("update_release_state", True, "mutation_flag"),
    ],
)
def test_rejects_artifacts_live_claims_guarantees_and_mutation_flags(field: str, value: object, expected_code: str) -> None:
    plan = _valid_plan()
    plan[field] = value

    assert expected_code in _codes(plan)


def test_rejects_active_bundle_mutation_not_forbidden() -> None:
    plan = _valid_plan()
    plan["active_bundle_mutation"] = "allowed"

    assert "mutation_flag" in _codes(plan)


def test_assert_helper_raises_with_issue_details() -> None:
    plan = _valid_plan()
    plan["devhub_completed"] = True

    with pytest.raises(ValueError, match="live_crawl_or_devhub_claim"):
        assert_valid_guardrail_recompile_dry_run_plan_v2(plan)
