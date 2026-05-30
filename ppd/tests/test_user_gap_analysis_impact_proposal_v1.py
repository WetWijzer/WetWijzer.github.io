from __future__ import annotations

import copy
from pathlib import Path

from ppd.logic.user_gap_analysis_impact_proposal_v1 import (
    IMPACT_CATEGORIES,
    build_from_fixture_paths,
    build_user_gap_analysis_impact_proposal_v1,
    finding_codes,
    load_json_fixture,
    validate_user_gap_analysis_impact_proposal_v1,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "user_gap_analysis_impact_proposal_v1"


def _valid_proposal() -> dict:
    return build_from_fixture_paths(
        process_model_impact_proposal_path=FIXTURE_DIR / "process_model_impact_proposal_v1.json",
        guardrail_bundle_impact_proposal_path=FIXTURE_DIR / "guardrail_bundle_impact_proposal_v1.json",
        user_gap_analysis_path=FIXTURE_DIR / "user_gap_analysis.json",
        reviewer_owner="fixture-reviewer",
    )


def test_builds_cited_impacts_for_all_required_categories() -> None:
    proposal = _valid_proposal()

    assert proposal["proposal_version"] == "v1"
    assert proposal["fixture_first"] is True
    assert proposal["affected_case_ids"] == ["case-demo-adu-001"]
    assert proposal["affected_process_ids"] == ["process-detached-adu-devhub-v1"]
    assert proposal["affected_guardrail_bundle_ids"] == ["guardrail-detached-adu-devhub-v1"]

    categories = [impact["category"] for impact in proposal["proposed_impacts"]]
    assert categories == list(IMPACT_CATEGORIES)

    for expected_order, impact in enumerate(proposal["proposed_impacts"], start=1):
        assert impact["dependency_order"] == expected_order
        assert impact["reviewer_owner"] == "fixture-reviewer"
        assert impact["rollback_note"]
        assert impact["offline_validation_commands"]
        assert impact["citations"]
        assert impact["affected_case_ids"] == ["case-demo-adu-001"]
        assert impact["affected_process_ids"] == ["process-detached-adu-devhub-v1"]
        assert impact["affected_guardrail_bundle_ids"] == ["guardrail-detached-adu-devhub-v1"]

    blocked = next(impact for impact in proposal["proposed_impacts"] if impact["category"] == "blocked_actions")
    assert blocked["proposed_impacts"][0]["action"] == "submit_permit_request"
    assert "guardrail:exact-confirmation-submit" in blocked["citations"]
    assert validate_user_gap_analysis_impact_proposal_v1(proposal).ok is True


def test_builder_does_not_mutate_input_fixtures() -> None:
    process_model = load_json_fixture(FIXTURE_DIR / "process_model_impact_proposal_v1.json")
    guardrail_bundle = load_json_fixture(FIXTURE_DIR / "guardrail_bundle_impact_proposal_v1.json")
    user_gap = load_json_fixture(FIXTURE_DIR / "user_gap_analysis.json")
    original_process_model = copy.deepcopy(process_model)
    original_guardrail_bundle = copy.deepcopy(guardrail_bundle)
    original_user_gap = copy.deepcopy(user_gap)

    proposal = build_user_gap_analysis_impact_proposal_v1(
        process_model_impact_proposal=process_model,
        guardrail_bundle_impact_proposal=guardrail_bundle,
        user_gap_analysis=user_gap,
    )

    assert proposal["mutation_policy"] == {
        "mutates_active_user_gap_fixtures": False,
        "mutates_sources": False,
        "mutates_documents": False,
        "mutates_requirements": False,
        "mutates_process_models": False,
        "mutates_guardrails": False,
        "mutates_prompts": False,
        "mutates_release_state": False,
        "mutates_agent_state": False,
    }
    assert process_model == original_process_model
    assert guardrail_bundle == original_guardrail_bundle
    assert user_gap == original_user_gap


def test_validator_rejects_uncited_and_incomplete_impact_rows() -> None:
    proposal = _valid_proposal()
    row = proposal["proposed_impacts"][0]
    row.pop("citations")
    row.pop("affected_case_ids")
    row.pop("affected_process_ids")
    row.pop("affected_guardrail_bundle_ids")
    row.pop("category")
    row.pop("dependency_order")
    row.pop("reviewer_owner")
    row.pop("rollback_note")

    codes = set(finding_codes(validate_user_gap_analysis_impact_proposal_v1(proposal)))

    assert "uncited_impact_row" in codes
    assert "missing_affected_case_ids" in codes
    assert "missing_affected_process_ids" in codes
    assert "missing_affected_guardrail_bundle_ids" in codes
    assert "missing_gap_or_action_expectation_category" in codes
    assert "missing_dependency_order" in codes
    assert "missing_reviewer_owner" in codes
    assert "missing_rollback_note" in codes


def test_validator_rejects_missing_top_level_review_and_dependency_metadata() -> None:
    proposal = _valid_proposal()
    proposal["dependency_order"] = []
    proposal["reviewer_owner"] = ""
    proposal["rollback_note"] = ""

    codes = set(finding_codes(validate_user_gap_analysis_impact_proposal_v1(proposal)))

    assert "missing_dependency_order" in codes
    assert "missing_reviewer_owner" in codes
    assert "missing_rollback_note" in codes


def test_validator_rejects_private_authenticated_session_browser_and_raw_artifacts() -> None:
    cases = [
        ("private applicant-specific artifact", "private_artifact"),
        ("authenticated page snapshot", "authenticated_artifact"),
        ("session cookie value", "session_artifact"),
        ("Playwright trace archive", "browser_artifact"),
        ("raw PDF download artifact", "raw_crawl_or_download_artifact"),
    ]

    for text, expected_code in cases:
        proposal = _valid_proposal()
        proposal["proposed_impacts"][0]["summary"] = text
        codes = set(finding_codes(validate_user_gap_analysis_impact_proposal_v1(proposal)))
        assert expected_code in codes


def test_validator_rejects_outcome_guarantees_and_consequential_execution_language() -> None:
    proposal = _valid_proposal()
    proposal["proposed_impacts"][0]["summary"] = "Approval guaranteed after this review."
    proposal["proposed_impacts"][1]["summary"] = "Agent will submit the permit request."

    codes = set(finding_codes(validate_user_gap_analysis_impact_proposal_v1(proposal)))

    assert "outcome_guarantee" in codes
    assert "consequential_action_execution_language" in codes


def test_validator_rejects_active_mutation_flags_for_all_blocked_targets() -> None:
    blocked_flags = {
        "mutates_active_user_gap_fixtures": True,
        "mutates_sources": True,
        "mutates_documents": True,
        "mutates_requirements": True,
        "mutates_process_models": True,
        "mutates_guardrails": True,
        "mutates_prompts": True,
        "mutates_release_state": True,
        "mutates_agent_state": True,
    }

    for key, value in blocked_flags.items():
        proposal = _valid_proposal()
        proposal["mutation_policy"][key] = value
        codes = set(finding_codes(validate_user_gap_analysis_impact_proposal_v1(proposal)))
        assert "active_mutation_flag" in codes
