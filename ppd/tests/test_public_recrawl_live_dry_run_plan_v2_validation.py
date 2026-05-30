from __future__ import annotations

import pytest

from ppd.public_recrawl_live_dry_run_plan_v2_validation import (
    assert_public_recrawl_live_dry_run_plan_v2,
    validate_public_recrawl_live_dry_run_plan_v2,
)


def _valid_plan() -> dict[str, object]:
    return {
        "seed_selections": [
            {
                "url": "https://www.portland.gov/bds/permit-review-process",
                "citations": ["public fixture citation"],
            }
        ],
        "robots_decision": {"decision": "allowed", "citations": ["robots fixture"]},
        "rate_limit_decision": {"decision": "allowed", "citations": ["rate fixture"]},
        "dry_run": True,
    }


def _codes(plan: dict[str, object]) -> set[str]:
    return {issue.code for issue in validate_public_recrawl_live_dry_run_plan_v2(plan)}


def test_valid_public_dry_run_plan_has_no_issues() -> None:
    assert validate_public_recrawl_live_dry_run_plan_v2(_valid_plan()) == []
    assert_public_recrawl_live_dry_run_plan_v2(_valid_plan())


@pytest.mark.parametrize(
    ("field", "value", "expected_code"),
    [
        ("raw_body", "raw", "raw_artifact_reference"),
        ("download_url", "https://www.portland.gov/file.pdf", "raw_artifact_reference"),
        ("archive_url", "https://www.portland.gov/archive/page", "raw_artifact_reference"),
        ("live_crawl_completed", True, "completion_claim"),
        ("processor_completed", True, "completion_claim"),
        ("guarantees_outcome", True, "outcome_guarantee"),
        ("permit_approved", True, "outcome_guarantee"),
        ("mutate_sources", True, "mutation_flag"),
        ("update_schedule", True, "mutation_flag"),
        ("mutate_requirements", True, "mutation_flag"),
        ("update_process", True, "mutation_flag"),
        ("mutate_guardrails", True, "mutation_flag"),
        ("update_prompts", True, "mutation_flag"),
        ("mutate_monitoring", True, "mutation_flag"),
        ("update_release_state", True, "mutation_flag"),
        ("mutate_agent_state", True, "mutation_flag"),
    ],
)
def test_rejects_unsafe_claims_references_and_mutation_flags(field: str, value: object, expected_code: str) -> None:
    plan = _valid_plan()
    plan[field] = value
    assert expected_code in _codes(plan)


def test_rejects_uncited_seed_selection() -> None:
    plan = _valid_plan()
    plan["seed_selections"] = [{"url": "https://www.portland.gov/bds"}]
    assert "uncited_seed_selection" in _codes(plan)


@pytest.mark.parametrize(
    ("url", "expected_code"),
    [
        ("http://www.portland.gov/bds", "non_https_url"),
        ("https://example.com/bds", "non_allowlisted_url"),
        ("https://www.portland.gov/login", "authenticated_url"),
        ("https://www.portland.gov/admin", "authenticated_url"),
    ],
)
def test_rejects_non_public_or_non_allowlisted_seed_urls(url: str, expected_code: str) -> None:
    plan = _valid_plan()
    plan["seed_selections"] = [{"url": url, "citations": ["fixture citation"]}]
    assert expected_code in _codes(plan)


def test_rejects_missing_robots_and_rate_limit_decisions() -> None:
    plan = _valid_plan()
    del plan["robots_decision"]
    del plan["rate_limit_decision"]
    codes = _codes(plan)
    assert "missing_robots_decision" in codes
    assert "missing_rate_limit_decision" in codes


def test_assert_helper_raises_with_issue_details() -> None:
    plan = _valid_plan()
    plan["mutate_sources"] = True
    with pytest.raises(ValueError, match="mutation_flag"):
        assert_public_recrawl_live_dry_run_plan_v2(plan)
