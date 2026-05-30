from __future__ import annotations

from copy import deepcopy

import pytest

from ppd.daemon.implementation_patch_staging_plan_v2 import (
    StagingPlanValidationError,
    assert_valid_implementation_patch_staging_plan_v2,
    validate_implementation_patch_staging_plan_v2,
)


def valid_plan() -> dict[str, object]:
    return {
        "version": "implementation_patch_staging_plan_v2",
        "patch_candidates": [
            {
                "target_id": "validator-contract",
                "citations": ["PPD plan: Non-Negotiable Boundaries"],
                "depends_on": [],
                "fixture_migration_notes": "No fixture format migration required; existing deterministic fixtures remain valid.",
                "rollback_checkpoints": ["Remove validator module and its focused tests."],
                "summary": "Add deterministic checks for patch staging metadata.",
                "mutation_flags": {
                    "registry": False,
                    "source": False,
                    "surface": False,
                    "guardrail": False,
                    "prompt": False,
                    "monitoring": False,
                    "release_state": False,
                    "agent_state": False,
                },
            },
            {
                "target_id": "validator-tests",
                "citations": ["PPD plan: Tests in ppd/tests/ should use deterministic fixtures."],
                "depends_on": ["validator-contract"],
                "fixture_migration_notes": "Adds only in-memory deterministic test plans.",
                "rollback_checkpoints": ["Remove the focused validator test module."],
                "summary": "Cover rejection cases for implementation patch staging plan v2.",
                "mutation_flags": {},
            },
        ],
    }


def issue_codes(plan: dict[str, object]) -> set[str]:
    return {issue.code for issue in validate_implementation_patch_staging_plan_v2(plan)}


def test_valid_plan_has_no_issues() -> None:
    assert validate_implementation_patch_staging_plan_v2(valid_plan()) == []
    assert_valid_implementation_patch_staging_plan_v2(valid_plan())


@pytest.mark.parametrize(
    ("field", "value", "expected_code"),
    [
        ("citations", [], "uncited_patch_candidate"),
        ("target_id", "", "missing_target_id"),
        ("fixture_migration_notes", "", "missing_fixture_migration_notes"),
        ("rollback_checkpoints", [], "missing_rollback_checkpoints"),
    ],
)
def test_rejects_missing_required_candidate_metadata(field: str, value: object, expected_code: str) -> None:
    plan = valid_plan()
    candidates = plan["patch_candidates"]
    assert isinstance(candidates, list)
    first = candidates[0]
    assert isinstance(first, dict)
    first[field] = value

    assert expected_code in issue_codes(plan)


def test_rejects_missing_dependency_ordering_field() -> None:
    plan = valid_plan()
    candidates = plan["patch_candidates"]
    assert isinstance(candidates, list)
    first = candidates[0]
    assert isinstance(first, dict)
    first.pop("depends_on")

    assert "missing_dependency_ordering" in issue_codes(plan)


def test_rejects_dependency_that_appears_after_dependent_candidate() -> None:
    plan = valid_plan()
    candidates = plan["patch_candidates"]
    assert isinstance(candidates, list)
    candidates.reverse()

    assert "missing_dependency_ordering" in issue_codes(plan)


def test_rejects_unknown_dependency_target() -> None:
    plan = valid_plan()
    candidates = plan["patch_candidates"]
    assert isinstance(candidates, list)
    second = candidates[1]
    assert isinstance(second, dict)
    second["depends_on"] = ["not-present"]

    assert "unknown_dependency_target" in issue_codes(plan)


@pytest.mark.parametrize(
    ("text", "expected_code"),
    [
        ("Use authenticated DevHub account facts captured from the session token.", "private_or_authenticated_fact"),
        ("Attach raw_crawl_dump/page.html and storage_state.json as evidence.", "raw_crawl_pdf_session_or_browser_artifact"),
        ("This was executed live against DevHub and promoted to production.", "live_execution_or_promotion_claim"),
        ("The permit will be approved after this patch.", "legal_or_permitting_outcome_guarantee"),
        ("Click submit for the final official submission.", "final_official_action_language"),
    ],
)
def test_rejects_prohibited_claims_and_artifacts(text: str, expected_code: str) -> None:
    plan = valid_plan()
    candidates = plan["patch_candidates"]
    assert isinstance(candidates, list)
    first = candidates[0]
    assert isinstance(first, dict)
    first["summary"] = text

    assert expected_code in issue_codes(plan)


@pytest.mark.parametrize(
    "flag_name",
    [
        "registry",
        "source",
        "surface",
        "guardrail",
        "prompt",
        "monitoring",
        "release_state",
        "agent_state",
    ],
)
def test_rejects_active_mutation_flags(flag_name: str) -> None:
    plan = valid_plan()
    candidates = plan["patch_candidates"]
    assert isinstance(candidates, list)
    first = candidates[0]
    assert isinstance(first, dict)
    first["mutation_flags"] = {flag_name: True}

    assert "active_mutation_flag" in issue_codes(plan)


def test_rejects_active_prefixed_mutation_flag_names() -> None:
    plan = valid_plan()
    candidates = plan["patch_candidates"]
    assert isinstance(candidates, list)
    first = candidates[0]
    assert isinstance(first, dict)
    first["active_registry_mutation"] = "enabled"

    assert "active_mutation_flag" in issue_codes(plan)


def test_assert_helper_raises_with_issue_details() -> None:
    plan = valid_plan()
    broken = deepcopy(plan)
    candidates = broken["patch_candidates"]
    assert isinstance(candidates, list)
    first = candidates[0]
    assert isinstance(first, dict)
    first["citations"] = []

    with pytest.raises(StagingPlanValidationError) as exc_info:
        assert_valid_implementation_patch_staging_plan_v2(broken)

    assert exc_info.value.issues[0].code == "uncited_patch_candidate"
