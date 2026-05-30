from __future__ import annotations

import copy

import pytest

from ppd.logic.post_dry_run_guardrail_impact_review_v2 import (
    REVIEW_SCHEMA_VERSION,
    assert_valid_post_dry_run_guardrail_impact_review_v2,
    validate_post_dry_run_guardrail_impact_review_v2,
)


def valid_review() -> dict[str, object]:
    return {
        "schema_version": REVIEW_SCHEMA_VERSION,
        "review_id": "review-dry-run-001",
        "guardrail_bundle_id": "bundle-building-permit-draft-v1",
        "predicate_ids": ["predicate-requires-exact-confirmation-before-submit"],
        "rollback_notes": "No active state was changed. Keep the current compiled bundle and discard the dry-run candidate.",
        "reviewer_owners": [
            {
                "owner_id": "ppd-guardrail-review",
                "role": "policy reviewer",
            }
        ],
        "blocked_action_checks": [
            {
                "action_id": "submit-permit-request",
                "blocked": True,
                "citation_ids": ["src-devhub-submit-guide-certification-step"],
                "rationale": "Consequential actions require attendance and exact confirmation.",
            }
        ],
        "impact_decisions": [
            {
                "decision_id": "decision-001",
                "predicate_ids": ["predicate-requires-exact-confirmation-before-submit"],
                "citation_ids": ["src-devhub-submit-guide-certification-step"],
                "outcome": "Keep submit actions blocked during draft-only dry runs.",
            }
        ],
        "mutation_flags": {
            "active_guardrail_mutation": False,
            "active_prompt_mutation": False,
            "active_source_mutation": False,
            "active_surface_registry_mutation": False,
            "active_monitoring_mutation": False,
            "active_release_state_mutation": False,
            "active_agent_state_mutation": False,
        },
    }


def finding_codes(review: dict[str, object]) -> set[str]:
    return {finding.code for finding in validate_post_dry_run_guardrail_impact_review_v2(review)}


def test_valid_post_dry_run_review_v2_passes() -> None:
    review = valid_review()

    assert validate_post_dry_run_guardrail_impact_review_v2(review) == []
    assert_valid_post_dry_run_guardrail_impact_review_v2(review)


@pytest.mark.parametrize(
    ("mutate", "expected_code"),
    [
        (
            lambda review: review.update({"guardrail_bundle_id": ""}),
            "missing_guardrail_bundle_id",
        ),
        (
            lambda review: review.update({"predicate_ids": []}),
            "missing_predicate_ids",
        ),
        (
            lambda review: review["impact_decisions"][0].update({"citation_ids": []}),
            "uncited_impact_decision",
        ),
        (
            lambda review: review["impact_decisions"][0].update({"predicate_ids": []}),
            "impact_decision_missing_predicate_ids",
        ),
        (
            lambda review: review.update({"blocked_action_checks": []}),
            "missing_blocked_action_checks",
        ),
        (
            lambda review: review["blocked_action_checks"][0].update({"blocked": False}),
            "blocked_action_check_not_blocked",
        ),
        (
            lambda review: review.update({"rollback_notes": ""}),
            "missing_rollback_notes",
        ),
        (
            lambda review: review.update({"reviewer_owners": []}),
            "missing_reviewer_owners",
        ),
        (
            lambda review: review["reviewer_owners"][0].pop("role"),
            "missing_role",
        ),
        (
            lambda review: review.update({"privacy_classification": "authenticated_private"}),
            "private_or_authenticated_fact",
        ),
        (
            lambda review: review.update({"raw_pdf": "permit-guide.pdf"}),
            "raw_artifact_reference",
        ),
        (
            lambda review: review.update({"trace": "local-trace.zip"}),
            "raw_artifact_reference",
        ),
        (
            lambda review: review.update({"summary": "Ran DevHub and clicked DevHub during the review."}),
            "live_execution_claim",
        ),
        (
            lambda review: review.update({"summary": "The permit will be approved."}),
            "outcome_guarantee",
        ),
        (
            lambda review: review.update({"summary": "Submitted permit and payment submitted."}),
            "final_action_language",
        ),
        (
            lambda review: review.update({"active_guardrail_mutation": True}),
            "active_mutation_flag",
        ),
        (
            lambda review: review.update({"mutation_flags": {"active_prompt_mutation": True}}),
            "active_mutation_flag",
        ),
    ],
)
def test_post_dry_run_review_v2_rejects_invalid_cases(mutate, expected_code: str) -> None:
    review = copy.deepcopy(valid_review())
    mutate(review)

    assert expected_code in finding_codes(review)


def test_assert_valid_raises_with_finding_details() -> None:
    review = valid_review()
    review["impact_decisions"][0]["citation_ids"] = []

    with pytest.raises(ValueError, match="uncited_impact_decision"):
        assert_valid_post_dry_run_guardrail_impact_review_v2(review)
