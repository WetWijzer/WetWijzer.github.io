from __future__ import annotations

from ppd.validation.attended_review_disposition_summary_v3 import (
    assert_attended_review_disposition_summary_v3,
    validate_attended_review_disposition_summary_v3,
)


def valid_summary() -> dict[str, object]:
    return {
        "version": "attended-review-disposition-summary-v3",
        "rollback_verification": {"verified": True, "evidence": "reviewer checked no release-state changes"},
        "rows": [
            {
                "disposition": "accept",
                "citation": "City of Portland PP&D public page, captured fixture citation A",
                "rationale": "Public source text matches the extracted field.",
                "reviewer_owners": ["reviewer-a"],
            },
            {
                "disposition": "defer",
                "citation": "City of Portland PP&D public page, captured fixture citation B",
                "rationale": "Needs a later public-source check.",
                "reviewer_owners": ["reviewer-b"],
                "follow_up_task": "task:ppd-follow-up-001",
            },
            {
                "disposition": "reject",
                "citation": "City of Portland PP&D public page, captured fixture citation C",
                "rationale": "The extracted value is unsupported by the cited source.",
                "reviewer_owners": ["reviewer-c"],
            },
        ],
    }


def codes(summary: dict[str, object]) -> set[str]:
    return {issue["code"] for issue in validate_attended_review_disposition_summary_v3(summary)}


def test_valid_summary_has_no_issues() -> None:
    summary = valid_summary()
    assert validate_attended_review_disposition_summary_v3(summary) == []
    assert_attended_review_disposition_summary_v3(summary)


def test_rejects_missing_row_requirements_and_unresolved_deferral() -> None:
    summary = valid_summary()
    summary["rows"] = [
        {"disposition": "accept", "reviewer_owners": ["reviewer-a"]},
        {"disposition": "reject", "citation": "public citation", "rationale": "unsupported"},
        {"disposition": "defer", "citation": "public citation", "rationale": "needs more review", "reviewer_owners": ["reviewer-b"]},
    ]

    assert {
        "uncited_disposition_row",
        "missing_disposition_rationale",
        "missing_reviewer_owners",
        "unresolved_deferral_without_follow_up",
    }.issubset(codes(summary))


def test_rejects_missing_rollback_verification() -> None:
    summary = valid_summary()
    summary.pop("rollback_verification")

    assert "missing_rollback_verification" in codes(summary)


def test_rejects_prohibited_claims_and_artifacts() -> None:
    summary = valid_summary()
    rows = summary["rows"]
    assert isinstance(rows, list)
    rows[0]["rationale"] = "Authenticated session-only fact from a browser trace."
    rows[1]["rationale"] = "This guarantees permit approval and says to submit the application."
    rows[2]["rationale"] = "Operator claimed live execution ran against production."

    assert {
        "private_or_authenticated_fact",
        "raw_artifact_reference",
        "legal_or_permitting_guarantee",
        "consequential_action_language",
        "live_execution_claim",
    }.issubset(codes(summary))


def test_rejects_mutation_flags_anywhere() -> None:
    summary = valid_summary()
    summary["release_state_mutation"] = True
    rows = summary["rows"]
    assert isinstance(rows, list)
    rows[0]["guardrail_mutation"] = True

    issues = validate_attended_review_disposition_summary_v3(summary)
    assert [issue["code"] for issue in issues].count("mutation_flag_present") == 2
