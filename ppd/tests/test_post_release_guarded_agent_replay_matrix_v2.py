from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from ppd.agent_readiness.post_release_guarded_agent_replay_matrix_v2 import (
    SCHEMA_VERSION,
    build_post_release_guarded_agent_replay_matrix_v2,
    load_inactive_release_application_dry_run_plan_v2,
    matrix_json_from_fixture,
    validate_post_release_guarded_agent_replay_matrix_v2,
)

FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "agent_readiness"
    / "inactive_release_application_dry_run_plan_v2.json"
)


def _valid_matrix() -> dict:
    packet = load_inactive_release_application_dry_run_plan_v2(FIXTURE_PATH)
    return build_post_release_guarded_agent_replay_matrix_v2(packet)


def _codes(matrix: dict) -> set[str]:
    result = validate_post_release_guarded_agent_replay_matrix_v2(matrix)
    return {issue.code for issue in result.issues}


def test_builds_ordered_guarded_replay_matrix_from_fixture() -> None:
    matrix = _valid_matrix()

    assert matrix["schema_version"] == SCHEMA_VERSION
    assert matrix["source_plan_id"] == "inactive-release-application-dry-run-plan-v2-fixture"
    assert matrix["release_state"] == "inactive_post_release_dry_run"
    assert matrix["mode"] == "fixture_first_offline_replay"
    assert matrix["active_prompt_changes"] is False
    assert matrix["production_contract_changes"] is False
    assert matrix["devhub_surface_changes"] is False
    assert matrix["public_source_changes"] is False

    scenarios = matrix["scenarios"]
    assert [scenario["order"] for scenario in scenarios] == [1, 2, 3]
    assert scenarios[0]["scenario_id"].endswith(":building-permit-plan-review")
    assert scenarios[1]["scenario_id"].endswith(":standard-trade-permit-readiness")
    assert scenarios[2]["scenario_id"].endswith(":corrections-upload-blocked")


def test_matrix_contains_expected_questions_blocks_drafts_and_placeholders() -> None:
    matrix = _valid_matrix()
    first = matrix["scenarios"][0]

    questions = first["expected_missing_fact_questions"]
    assert any("property address" in question for question in questions)
    assert any("applicant role" in question for question in questions)

    blocked = first["expected_blocked_action_explanations"]
    assert any("submit permit application" in explanation for explanation in blocked)
    assert any("exact action-specific confirmation" in explanation for explanation in blocked)

    drafts = first["expected_reversible_draft_previews"]
    assert drafts[0]["preview_only"] is True
    assert drafts[0]["requires_user_review_before_use"] is True
    assert drafts[0]["fields"][0]["preview_value"] == ""

    citations = first["citation_coverage_placeholders"]
    assert {item["coverage_status"] for item in citations} == {"placeholder_pending_reviewer_source_check"}

    acceptance = first["reviewer_acceptance_placeholders"]
    assert {item["reviewer_status"] for item in acceptance} == {"pending"}
    assert "citations_cover_each_material_requirement" in {
        item["acceptance_check"] for item in acceptance
    }


def test_matrix_exports_exact_offline_validation_commands() -> None:
    matrix = _valid_matrix()

    assert matrix["offline_validation_commands"] == [
        ["python3", "-m", "py_compile", "ppd/agent_readiness/post_release_guarded_agent_replay_matrix_v2.py"],
        ["python3", "-m", "pytest", "ppd/tests/test_post_release_guarded_agent_replay_matrix_v2.py"],
        ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
    ]


def test_rejects_active_or_wrong_version_packets() -> None:
    packet = load_inactive_release_application_dry_run_plan_v2(FIXTURE_PATH)

    wrong_version = dict(packet)
    wrong_version["schema_version"] = "release_application_dry_run_plan_v1"
    with pytest.raises(ValueError, match="expected schema_version"):
        build_post_release_guarded_agent_replay_matrix_v2(wrong_version)

    active_packet = dict(packet)
    active_packet["release_state"] = "active_release"
    with pytest.raises(ValueError, match="inactive post-release"):
        build_post_release_guarded_agent_replay_matrix_v2(active_packet)


def test_replay_matrix_v2_accepts_valid_matrix() -> None:
    result = validate_post_release_guarded_agent_replay_matrix_v2(_valid_matrix())

    assert result.ok is True
    assert result.issues == ()


def test_replay_matrix_v2_rejects_missing_required_replay_sections() -> None:
    required_section_cases = [
        ("scenarios", "missing_synthetic_user_scenarios"),
        ("offline_validation_commands", "missing_validation_commands"),
    ]
    for key, expected_code in required_section_cases:
        matrix = _valid_matrix()
        matrix[key] = []

        assert expected_code in _codes(matrix)


def test_replay_matrix_v2_rejects_missing_scenario_expectations() -> None:
    scenario_field_cases = [
        ("synthetic_user_scenario", "", "missing_synthetic_user_scenario"),
        ("expected_missing_fact_questions", [], "missing_expected_missing_fact_questions"),
        ("expected_blocked_action_explanations", [], "missing_blocked_action_explanations"),
        ("expected_reversible_draft_previews", [], "missing_reversible_draft_previews"),
        ("citation_coverage_placeholders", [], "missing_citation_coverage_placeholders"),
        ("reviewer_acceptance_placeholders", [], "missing_reviewer_acceptance_placeholders"),
    ]
    for key, value, expected_code in scenario_field_cases:
        matrix = _valid_matrix()
        matrix["scenarios"][0][key] = value

        assert expected_code in _codes(matrix)


def test_replay_matrix_v2_rejects_invalid_draft_citation_reviewer_and_command_placeholders() -> None:
    matrix = _valid_matrix()
    first = matrix["scenarios"][0]
    first["expected_reversible_draft_previews"][0]["preview_only"] = False
    first["expected_reversible_draft_previews"][0]["requires_user_review_before_use"] = False
    first["citation_coverage_placeholders"][0]["coverage_status"] = "accepted_without_review"
    first["reviewer_acceptance_placeholders"][0]["reviewer_status"] = "accepted"
    matrix["offline_validation_commands"] = [["python3", "ppd/crawler/live_public_scrape.py"]]

    codes = _codes(matrix)

    assert "draft_preview_not_preview_only" in codes
    assert "draft_preview_missing_user_review" in codes
    assert "invalid_citation_coverage_status" in codes
    assert "invalid_reviewer_acceptance_status" in codes
    assert "unexpected_validation_commands" in codes


def test_replay_matrix_v2_rejects_private_raw_downloaded_live_consequential_and_guarantee_content() -> None:
    unsafe_examples = [
        ("session_artifact", {"path": "state.json"}, "private_or_raw_artifact_field"),
        ("raw_downloaded_pdf", "raw downloaded pdf", "private_or_raw_artifact_field"),
        ("operator_note", "live DevHub run completed", "unsafe_matrix_text"),
        ("crawl_note", "live crawl completed", "unsafe_matrix_text"),
        ("action_note", "submitted the permit", "unsafe_matrix_text"),
        ("legal_note", "approval is guaranteed", "unsafe_matrix_text"),
    ]
    for key, value, expected_code in unsafe_examples:
        matrix = _valid_matrix()
        matrix[key] = value

        assert expected_code in _codes(matrix)


def test_replay_matrix_v2_rejects_active_prompt_contract_guardrail_source_surface_and_release_state_mutation_flags() -> None:
    for key in (
        "active_prompt_changes",
        "active_contract_changes",
        "active_guardrail_changes",
        "active_source_changes",
        "active_surface_changes",
        "active_release_state_changes",
        "prompt_mutation",
        "contract_mutation",
        "guardrail_mutation",
        "source_mutation",
        "surface_mutation",
        "release_state_mutation",
    ):
        matrix = _valid_matrix()
        matrix[key] = True

        assert "active_mutation_flag" in _codes(matrix)


def test_validation_does_not_mutate_replay_matrix() -> None:
    matrix = _valid_matrix()
    before = deepcopy(matrix)

    validate_post_release_guarded_agent_replay_matrix_v2(matrix)

    assert matrix == before


def test_fixture_matrix_json_is_deterministic_and_parseable() -> None:
    first = matrix_json_from_fixture(FIXTURE_PATH)
    second = matrix_json_from_fixture(FIXTURE_PATH)

    assert first == second
    assert "post_release_guarded_agent_replay_matrix_v2" in first
    assert "inactive-release-application-dry-run-plan-v2-fixture" in first
