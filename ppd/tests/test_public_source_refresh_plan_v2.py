from __future__ import annotations

from ppd.validators.public_source_refresh_plan_v2 import validate_public_source_refresh_plan_v2


def _valid_plan() -> dict[str, object]:
    return {
        "reviewer_owner": "ppd-reviewer",
        "rollback_note": "Discard this planning artifact and keep the current active corpus unchanged.",
        "freshness_priority_rows": [
            {"source_id": "ppd-permits", "priority": "high", "reason": "Public permit pages change frequently."}
        ],
        "source_refresh_candidates": [
            {
                "source_id": "ppd-permits",
                "public_url": "https://www.portland.gov/ppd/permits",
                "citations": [{"url": "https://www.portland.gov/ppd/permits", "title": "Permits"}],
                "affected_requirement_ids": ["REQ-PPD-PERMIT-001"],
                "affected_process_ids": ["PROC-PPD-REVIEW-001"],
                "affected_guardrail_ids": ["GR-PPD-PUBLIC-SOURCES-001"],
            }
        ],
    }


def _codes(plan: dict[str, object]) -> set[str]:
    return {error.code for error in validate_public_source_refresh_plan_v2(plan)}


def test_accepts_minimal_cited_non_mutating_plan() -> None:
    assert validate_public_source_refresh_plan_v2(_valid_plan()) == []


def test_rejects_missing_required_review_and_freshness_fields() -> None:
    plan = _valid_plan()
    plan.pop("reviewer_owner")
    plan.pop("rollback_note")
    plan.pop("freshness_priority_rows")

    assert {
        "missing_reviewer_owner",
        "missing_rollback_note",
        "missing_freshness_priority_rows",
    }.issubset(_codes(plan))


def test_rejects_uncited_candidate_and_missing_affected_ids() -> None:
    plan = _valid_plan()
    candidate = plan["source_refresh_candidates"][0]  # type: ignore[index]
    assert isinstance(candidate, dict)
    candidate.pop("citations")
    candidate.pop("affected_requirement_ids")
    candidate.pop("affected_process_ids")
    candidate.pop("affected_guardrail_ids")

    assert {
        "uncited_source_refresh_candidate",
        "missing_affected_ids",
    }.issubset(_codes(plan))


def test_rejects_private_artifacts_raw_data_claims_guarantees_actions_and_mutations() -> None:
    plan = _valid_plan()
    plan.update(
        {
            "session_file": "private/devhub-session.json",
            "raw_pdf": "bytes would go here",
            "notes": "Fetched live in a browser observed run. This will be approved. Submit the application.",
            "mutate_active_sources": True,
            "write_active_documents": True,
            "publish_release_state": True,
            "update_agent_state": True,
        }
    )

    assert {
        "private_or_authenticated_artifact",
        "raw_crawl_or_downloaded_data",
        "live_crawl_claim",
        "legal_or_permitting_guarantee",
        "consequential_action_language",
        "active_state_mutation_flag",
    }.issubset(_codes(plan))
