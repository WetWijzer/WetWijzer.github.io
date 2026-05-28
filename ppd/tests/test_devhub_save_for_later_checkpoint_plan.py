from __future__ import annotations

import copy
from pathlib import Path

import pytest

from ppd.devhub.save_for_later_checkpoint_plan import (
    SaveForLaterCheckpointPlanError,
    load_plan,
    validate_plan,
    validate_plan_file,
)


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "devhub" / "save_for_later_checkpoint_plan.json"


def test_save_for_later_checkpoint_fixture_passes() -> None:
    result = validate_plan_file(FIXTURE_PATH)

    assert result.plan_id == "devhub_save_for_later_checkpoint_plan_fixture"
    assert result.checkpoint_count == 2
    assert result.source_evidence_count == 2
    assert result.excluded_action_count == 7
    assert result.journal_expectation_count == 3


def test_field_entry_and_save_for_later_control_must_remain_distinct() -> None:
    plan = copy.deepcopy(load_plan(FIXTURE_PATH))
    plan["checkpoints"][0]["uses_save_for_later_control"] = True

    with pytest.raises(SaveForLaterCheckpointPlanError, match="field-entry checkpoint"):
        validate_plan(plan)


def test_save_for_later_control_must_not_enter_field_values() -> None:
    plan = copy.deepcopy(load_plan(FIXTURE_PATH))
    plan["checkpoints"][1]["enters_field_values"] = True

    with pytest.raises(SaveForLaterCheckpointPlanError, match="save-for-later checkpoint"):
        validate_plan(plan)


def test_preview_metadata_is_required_and_redacted() -> None:
    plan = copy.deepcopy(load_plan(FIXTURE_PATH))
    del plan["checkpoints"][0]["preview_metadata"]

    with pytest.raises(SaveForLaterCheckpointPlanError, match="preview_metadata"):
        validate_plan(plan)

    plan = copy.deepcopy(load_plan(FIXTURE_PATH))
    plan["checkpoints"][0]["preview_metadata"]["redacted"] = False

    with pytest.raises(SaveForLaterCheckpointPlanError, match="must be redacted"):
        validate_plan(plan)


def test_ambiguous_selectors_are_rejected() -> None:
    plan = copy.deepcopy(load_plan(FIXTURE_PATH))
    plan["checkpoints"][0]["selector_metadata"]["ambiguous_matches"] = 2

    with pytest.raises(SaveForLaterCheckpointPlanError, match="ambiguous selectors"):
        validate_plan(plan)

    plan = copy.deepcopy(load_plan(FIXTURE_PATH))
    plan["checkpoints"][0]["selector_metadata"]["matched_element_count"] = 2

    with pytest.raises(SaveForLaterCheckpointPlanError, match="exactly one element"):
        validate_plan(plan)


def test_manual_attendance_and_manual_login_handoff_are_required() -> None:
    plan = copy.deepcopy(load_plan(FIXTURE_PATH))
    plan["manual_attendance"]["requires_user_present"] = False

    with pytest.raises(SaveForLaterCheckpointPlanError, match="requires_user_present"):
        validate_plan(plan)

    plan = copy.deepcopy(load_plan(FIXTURE_PATH))
    del plan["manual_attendance"]["manual_login_handoff"]

    with pytest.raises(SaveForLaterCheckpointPlanError, match="manual_login_handoff"):
        validate_plan(plan)

    plan = copy.deepcopy(load_plan(FIXTURE_PATH))
    plan["manual_attendance"]["manual_login_handoff"]["automation_creates_account"] = True

    with pytest.raises(SaveForLaterCheckpointPlanError, match="automation_creates_account"):
        validate_plan(plan)


def test_source_evidence_ids_are_required() -> None:
    plan = copy.deepcopy(load_plan(FIXTURE_PATH))
    plan["checkpoints"][1]["source_evidence_ids"] = ["SRC-UNKNOWN"]

    with pytest.raises(SaveForLaterCheckpointPlanError, match="unknown source evidence id"):
        validate_plan(plan)


def test_action_journal_expectations_must_be_redacted() -> None:
    plan = copy.deepcopy(load_plan(FIXTURE_PATH))
    plan["action_journal_expectations"][0]["contains_private_values"] = True

    with pytest.raises(SaveForLaterCheckpointPlanError, match="must not contain private values"):
        validate_plan(plan)


def test_private_browser_artifacts_are_rejected() -> None:
    plan = copy.deepcopy(load_plan(FIXTURE_PATH))
    plan["browser_artifact_policy"]["stores_traces"] = True

    with pytest.raises(SaveForLaterCheckpointPlanError, match="stores_traces"):
        validate_plan(plan)

    plan = copy.deepcopy(load_plan(FIXTURE_PATH))
    plan["checkpoints"][0]["screenshot_path"] = "/tmp/private.png"

    with pytest.raises(SaveForLaterCheckpointPlanError, match="forbidden private field"):
        validate_plan(plan)


def test_consequential_actions_are_excluded() -> None:
    plan = copy.deepcopy(load_plan(FIXTURE_PATH))
    plan["excluded_actions"] = [
        action for action in plan["excluded_actions"] if action["action_class"] != "final_payment_execution"
    ]

    with pytest.raises(SaveForLaterCheckpointPlanError, match="missing required consequential action classes"):
        validate_plan(plan)

    plan = copy.deepcopy(load_plan(FIXTURE_PATH))
    plan["excluded_actions"][0]["may_execute"] = True

    with pytest.raises(SaveForLaterCheckpointPlanError, match="must not execute"):
        validate_plan(plan)

    plan = copy.deepcopy(load_plan(FIXTURE_PATH))
    plan["excluded_actions"][0]["requires_separate_exact_confirmation"] = False

    with pytest.raises(SaveForLaterCheckpointPlanError, match="separate exact confirmation"):
        validate_plan(plan)
