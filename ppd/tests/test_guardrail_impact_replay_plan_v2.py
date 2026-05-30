from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import pytest

from ppd.agent_readiness.guardrail_impact_replay_plan_v2 import (
    EXACT_OFFLINE_VALIDATION_COMMANDS,
    GuardrailImpactReplayPlanV2Error,
    assert_valid_guardrail_impact_replay_plan_v2,
    build_guardrail_impact_replay_plan_v2,
    build_guardrail_impact_replay_plan_v2_from_file,
    load_json_object,
    validate_guardrail_impact_replay_plan_v2,
)

FIXTURE = (
    Path(__file__).parent
    / "fixtures"
    / "guardrail_impact_replay_plan_v2"
    / "inactive_promotion_candidate_packet_v2.json"
)


def _plan() -> dict[str, Any]:
    return build_guardrail_impact_replay_plan_v2_from_file(FIXTURE)


def test_builds_ordered_synthetic_guardrail_replay_cases_from_inactive_candidate_packet_v2() -> None:
    plan = _plan()

    assert plan["plan_type"] == "ppd.guardrail_impact_replay_plan.v2"
    assert plan["fixture_only"] is True
    assert plan["source_packet"]["packet_type"] == "ppd.inactive_promotion_candidate_packet.v2"
    assert plan["case_order"] == [case["case_id"] for case in plan["ordered_replay_cases"]]
    assert [case["expected_outcome"] for case in plan["ordered_replay_cases"][:3]] == ["allow", "block", "escalate"]
    assert len(plan["ordered_replay_cases"]) == 6
    assert plan["exact_offline_validation_commands"] == EXACT_OFFLINE_VALIDATION_COMMANDS
    assert_valid_guardrail_impact_replay_plan_v2(plan)


def test_replay_cases_include_impacted_refs_placeholders_and_no_mutations() -> None:
    plan = _plan()
    first_case = plan["ordered_replay_cases"][0]

    assert first_case["dependency_row_id"] == "dependency-001-devhub-application-guide-draft-surface"
    assert first_case["impacted_requirement_refs"] == ["requirement:devhub-application-draft-save-for-later"]
    assert first_case["impacted_process_refs"] == ["process:devhub-permit-application"]
    assert first_case["impacted_surface_refs"] == ["devhub-permit-application-draft-surface"]
    assert first_case["citation_placeholders"] == [
        {
            "citation_id": "citation-placeholder:guardrail-impact-001-allow-reversible-review:001",
            "source_evidence_id": "source:ppd-devhub-guide-submit-permit-application#draft-save-for-later",
            "citation_status": "pending_replay_resolution",
        }
    ]
    assert first_case["gap_analysis_comparison_placeholders"] == {
        "baseline_gap_analysis_ref": "",
        "candidate_gap_analysis_ref": "",
        "comparison_status": "pending_offline_fixture_replay",
        "expected_comparison_result": "no_active_gap_analysis_mutation",
    }
    assert first_case["compiled_guardrail_mutation"] is False
    assert first_case["active_guardrail_mutation"] is False
    assert first_case["active_process_mutation"] is False
    assert first_case["active_requirement_mutation"] is False
    assert first_case["active_prompt_mutation"] is False
    assert first_case["active_release_state_mutation"] is False
    assert first_case["prompt_mutation"] is False


def test_reviewer_hold_placeholders_are_unsigned_and_match_cases() -> None:
    plan = _plan()

    expected_hold_ids = {case["reviewer_hold_ref"] for case in plan["ordered_replay_cases"]}
    actual_hold_ids = {hold["hold_id"] for hold in plan["reviewer_hold_placeholders"]}

    assert actual_hold_ids == expected_hold_ids
    assert plan["reviewer_hold_placeholders"][0] == {
        "hold_id": "reviewer-hold:guardrail-impact-001-allow-reversible-review",
        "case_id": "guardrail-impact-001-allow-reversible-review",
        "hold_reason": "pending_manual_guardrail_impact_review",
        "reviewer": "",
        "reviewed_at": "",
        "decision": "pending_manual_review",
        "notes": "",
    }


def test_rejects_non_inactive_candidate_packet_input() -> None:
    packet = load_json_object(FIXTURE)
    packet["packet_type"] = "wrong.packet"

    with pytest.raises(ValueError, match="packet_type"):
        build_guardrail_impact_replay_plan_v2(packet)


@pytest.mark.parametrize("outcome", ["allow", "block", "escalate"])
def test_requires_each_dependency_to_have_allow_block_and_escalate_cases(outcome: str) -> None:
    plan = _plan()
    plan["ordered_replay_cases"] = [
        case
        for case in plan["ordered_replay_cases"]
        if not (
            case["dependency_row_id"] == "dependency-001-devhub-application-guide-draft-surface"
            and case["expected_outcome"] == outcome
        )
    ]
    plan["case_order"] = [case["case_id"] for case in plan["ordered_replay_cases"]]
    plan["reviewer_hold_placeholders"] = [
        hold
        for hold in plan["reviewer_hold_placeholders"]
        if hold["case_id"] in set(plan["case_order"])
    ]

    result = validate_guardrail_impact_replay_plan_v2(plan)

    assert not result.valid
    assert "must have allow, block, and escalate replay cases" in "; ".join(result.problems)


@pytest.mark.parametrize(
    ("field", "expected"),
    [
        ("impacted_requirement_refs", "impacted_requirement_refs must be non-empty"),
        ("impacted_process_refs", "impacted_process_refs must be non-empty"),
        ("impacted_surface_refs", "impacted_surface_refs must be non-empty"),
    ],
)
def test_rejects_missing_impacted_refs(field: str, expected: str) -> None:
    plan = _plan()
    plan["ordered_replay_cases"][0][field] = []

    result = validate_guardrail_impact_replay_plan_v2(plan)

    assert not result.valid
    assert expected in "; ".join(result.problems)


@pytest.mark.parametrize(
    ("outcome", "decision", "expected"),
    [
        ("pass", "ALLOW", "expected_outcome must be allow, block, or escalate"),
        ("allow", "BLOCK", "expected_guardrail_decision must be ALLOW"),
        ("block", "ALLOW", "expected_guardrail_decision must be BLOCK"),
        ("escalate", "ALLOW", "expected_guardrail_decision must be ESCALATE"),
    ],
)
def test_rejects_missing_or_mismatched_expected_outcomes(outcome: str, decision: str, expected: str) -> None:
    plan = _plan()
    plan["ordered_replay_cases"][0]["expected_outcome"] = outcome
    plan["ordered_replay_cases"][0]["expected_guardrail_decision"] = decision

    result = validate_guardrail_impact_replay_plan_v2(plan)

    assert not result.valid
    assert expected in "; ".join(result.problems)


def test_rejects_missing_citation_gap_and_reviewer_hold_placeholders() -> None:
    plan = _plan()
    plan["ordered_replay_cases"][0]["citation_placeholders"] = []
    del plan["ordered_replay_cases"][0]["gap_analysis_comparison_placeholders"]["baseline_gap_analysis_ref"]
    plan["ordered_replay_cases"][0]["gap_analysis_comparison_placeholders"]["comparison_status"] = "complete"
    plan["reviewer_hold_placeholders"] = plan["reviewer_hold_placeholders"][1:]

    result = validate_guardrail_impact_replay_plan_v2(plan)

    assert not result.valid
    problems = "; ".join(result.problems)
    assert "citation_placeholders must be non-empty" in problems
    assert "baseline_gap_analysis_ref is required" in problems
    assert "comparison_status must be pending_offline_fixture_replay" in problems
    assert "reviewer_hold_placeholders must match" in problems


def test_rejects_signed_or_mismatched_reviewer_hold_placeholders() -> None:
    plan = _plan()
    plan["reviewer_hold_placeholders"][0]["case_id"] = "missing-case"
    plan["reviewer_hold_placeholders"][1]["reviewer"] = "reviewer@example.test"

    result = validate_guardrail_impact_replay_plan_v2(plan)

    assert not result.valid
    problems = "; ".join(result.problems)
    assert "case_id must reference an ordered replay case" in problems
    assert "must remain an unsigned reviewer hold placeholder" in problems


def test_rejects_attestation_or_validation_command_drift() -> None:
    plan = _plan()
    plan["attestations"]["compiled_guardrails_changed"] = True
    plan["attestations"]["active_guardrails_changed"] = True
    plan["exact_offline_validation_commands"] = []

    result = validate_guardrail_impact_replay_plan_v2(plan)

    assert not result.valid
    problems = "; ".join(result.problems)
    assert "attestations.compiled_guardrails_changed must be False" in problems
    assert "attestations.active_guardrails_changed must be False" in problems
    assert "exact_offline_validation_commands must match" in problems


@pytest.mark.parametrize(
    ("key", "value", "expected"),
    [
        ("browser_state_path", "state.json", "must not include private, raw"),
        ("raw_crawl_output_path", "capture.html", "must not include private, raw"),
        ("private_note", "private value", "must not include private, raw"),
        ("session_artifact", "session storage", "must not include private, raw"),
        ("live_note", "live DevHub access completed", "must not reference private, raw"),
        ("crawl_note", "live crawl completed", "must not reference private, raw"),
        ("action_note", "agent may submit permit", "must not include consequential official-action"),
        ("guarantee_note", "permit will be approved", "must not include legal or permitting guarantees"),
        ("active_guardrail_mutation", True, "must be false"),
        ("active_prompt_mutation", True, "must be false"),
        ("active_process_mutation", True, "must be false"),
        ("active_requirement_mutation", True, "must be false"),
        ("active_release_state_mutation", True, "must be false"),
    ],
)
def test_rejects_private_live_official_action_guarantee_and_mutation_content(
    key: str,
    value: Any,
    expected: str,
) -> None:
    plan = _plan()
    plan[key] = value

    result = validate_guardrail_impact_replay_plan_v2(plan)

    assert not result.valid
    assert expected in "; ".join(result.problems)


def test_assert_raises_with_validation_problems() -> None:
    plan = copy.deepcopy(_plan())
    plan["ordered_replay_cases"][0]["expected_outcome"] = "pass"

    with pytest.raises(GuardrailImpactReplayPlanV2Error, match="expected_outcome"):
        assert_valid_guardrail_impact_replay_plan_v2(plan)
