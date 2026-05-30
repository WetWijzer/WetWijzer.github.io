from __future__ import annotations

import pytest

from ppd.validation.devhub_observed_surface_update_plan_v2 import (
    assert_valid_devhub_observed_surface_update_plan_v2,
    validate_devhub_observed_surface_update_plan_v2,
)


def valid_plan() -> dict[str, object]:
    return {
        "plan_version": "devhub-observed-surface-update-plan-v2",
        "reviewer_owner": "ppd-reviewer",
        "rollback_note": "Revert the proposed fixture-only selector update and rerun validation.",
        "selector_confidence_review_rows": [
            {
                "id": "row-address-search-button",
                "selector": "button[data-testid='address-search']",
                "confidence": "high",
                "review_note": "Observed in a deterministic fixture screenshot.",
            }
        ],
        "redaction_checks": [
            {"name": "no private session state", "passed": True},
            {"name": "no raw crawl or downloaded document payloads", "passed": True},
        ],
        "manual_attendance_gates": [
            {"name": "human review before any DevHub interaction", "required": True}
        ],
        "mutation_flags": {
            "mutates_active_devhub_surface": False,
            "mutates_active_devhub_process": False,
            "mutates_active_devhub_guardrails": False,
            "mutates_active_devhub_prompt": False,
            "mutates_active_devhub_release_state": False,
            "mutates_active_agent_state": False,
        },
        "candidates": [
            {
                "id": "candidate-address-search-button",
                "description": "Fixture-backed selector observation for review only.",
                "selector_confidence_review_row_id": "row-address-search-button",
                "citations": [
                    {
                        "kind": "fixture",
                        "path": "ppd/tests/fixtures/devhub_observed_surface_update_plan_v2/address_search_fixture.html",
                    }
                ],
                "mutation_flags": {
                    "mutates_active_devhub_surface": False,
                    "mutates_active_devhub_process": False,
                    "mutates_active_devhub_guardrails": False,
                    "mutates_active_devhub_prompt": False,
                    "mutates_active_devhub_release_state": False,
                    "mutates_active_agent_state": False,
                },
            }
        ],
    }


def issue_codes(plan: dict[str, object]) -> set[str]:
    return {issue.code for issue in validate_devhub_observed_surface_update_plan_v2(plan)}


def test_valid_plan_passes() -> None:
    assert validate_devhub_observed_surface_update_plan_v2(valid_plan()) == []
    assert_valid_devhub_observed_surface_update_plan_v2(valid_plan())


@pytest.mark.parametrize(
    ("field", "code"),
    [
        ("selector_confidence_review_rows", "missing_selector_confidence_review_rows"),
        ("redaction_checks", "missing_redaction_checks"),
        ("manual_attendance_gates", "missing_manual_attendance_gates"),
        ("reviewer_owner", "missing_required_field"),
        ("rollback_note", "missing_required_field"),
    ],
)
def test_missing_required_plan_controls_fail_closed(field: str, code: str) -> None:
    plan = valid_plan()
    plan[field] = [] if field.endswith("s") else ""

    assert code in issue_codes(plan)


def test_uncited_candidate_is_rejected() -> None:
    plan = valid_plan()
    candidates = plan["candidates"]
    assert isinstance(candidates, list)
    candidates[0]["citations"] = []

    assert "uncited_candidate" in issue_codes(plan)


def test_candidate_missing_selector_confidence_review_row_is_rejected() -> None:
    plan = valid_plan()
    candidates = plan["candidates"]
    assert isinstance(candidates, list)
    candidates[0]["selector_confidence_review_row_id"] = ""

    assert "missing_selector_confidence_review_row" in issue_codes(plan)


@pytest.mark.parametrize(
    ("text", "code"),
    [
        ("contains private DevHub session file", "private_or_raw_artifact"),
        ("references raw crawl payload", "private_or_raw_artifact"),
        ("executed in DevHub yesterday", "live_devhub_execution_claim"),
        ("permit will be approved", "legal_or_permitting_outcome_guarantee"),
        ("submit application after selector update", "consequential_action_language"),
    ],
)
def test_forbidden_language_is_rejected(text: str, code: str) -> None:
    plan = valid_plan()
    plan["notes"] = text

    assert code in issue_codes(plan)


@pytest.mark.parametrize(
    "flag",
    [
        "mutates_active_devhub_surface",
        "mutates_active_devhub_process",
        "mutates_active_devhub_guardrails",
        "mutates_active_devhub_prompt",
        "mutates_active_devhub_release_state",
        "mutates_active_agent_state",
    ],
)
def test_active_mutation_flags_are_rejected(flag: str) -> None:
    plan = valid_plan()
    mutation_flags = plan["mutation_flags"]
    assert isinstance(mutation_flags, dict)
    mutation_flags[flag] = True

    assert "active_mutation_flag" in issue_codes(plan)


def test_assert_valid_raises_for_invalid_plan() -> None:
    plan = valid_plan()
    plan["rollback_note"] = ""

    with pytest.raises(ValueError, match="rollback_note"):
        assert_valid_devhub_observed_surface_update_plan_v2(plan)
