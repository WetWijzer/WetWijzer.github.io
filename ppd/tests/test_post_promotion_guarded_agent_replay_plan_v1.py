from __future__ import annotations

from pathlib import Path

from ppd.post_promotion_guarded_agent_replay_plan_v1 import validate_replay_plan_file


FIXTURES = Path(__file__).parent / "fixtures" / "post_promotion_guarded_agent_replay_plan_v1"


def test_valid_guarded_replay_plan_v1_is_accepted() -> None:
    result = validate_replay_plan_file(FIXTURES / "valid_replay_plan.json")

    assert result.valid, result.errors


def test_uncited_replay_scenario_is_rejected() -> None:
    result = validate_replay_plan_file(FIXTURES / "invalid_uncited_replay_plan.json")

    assert not result.valid
    assert any("citation" in error for error in result.errors)


def test_missing_expected_outcome_is_rejected() -> None:
    result = validate_replay_plan_file(FIXTURES / "invalid_missing_expected_outcome.json")

    assert not result.valid
    assert any("expected_outcome" in error for error in result.errors)


def test_missing_safety_expectations_are_rejected() -> None:
    result = validate_replay_plan_file(FIXTURES / "invalid_missing_safety_expectations.json")

    assert not result.valid
    joined = "\n".join(result.errors)
    assert "missing_information_prompt_expectation" in joined
    assert "reversible_draft_boundary_checks" in joined
    assert "blocked_action_expectations" in joined
    assert "devhub_attendance_gate_checks" in joined
    assert "journal_safety_checks" in joined
    assert "rollback_verification" in joined


def test_prohibited_artifacts_claims_language_and_mutations_are_rejected() -> None:
    result = validate_replay_plan_file(FIXTURES / "invalid_prohibited_content.json")

    assert not result.valid
    joined = "\n".join(result.errors)
    assert "private/auth/session/browser" in joined
    assert "raw/download/PDF/screenshot/trace/HAR" in joined
    assert "live execution or release-state claim" in joined
    assert "legal or permitting outcome guarantee" in joined
    assert "consequential action language" in joined
    assert "mutation flag" in joined
