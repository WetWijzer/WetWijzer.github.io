from __future__ import annotations

import copy
from pathlib import Path

import pytest

from ppd.devhub.attended_read_only_review_plan import (
    AttendedReadOnlyReviewPlanError,
    REQUIRED_BLOCKED_ACTIONS,
    REQUIRED_REJECTED_ARTIFACTS,
    validate_review_plan,
    validate_review_plan_file,
)


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "devhub" / "attended_read_only_review_plan.json"


def _valid_plan() -> dict:
    return copy.deepcopy(validate_review_plan_file.__globals__["load_review_plan"](FIXTURE_PATH))


def test_attended_read_only_review_plan_fixture_rejects_required_boundaries() -> None:
    result = validate_review_plan_file(FIXTURE_PATH)

    plan = _valid_plan()
    assert result.plan_id == "devhub_attended_read_only_account_review_plan"
    assert result.review_state_count == 5
    assert REQUIRED_REJECTED_ARTIFACTS == {item["artifact_kind"] for item in plan["rejected_artifacts"]}
    assert REQUIRED_BLOCKED_ACTIONS == {item["action_kind"] for item in plan["blocked_consequential_actions"]}


def test_attended_read_only_review_plan_rejects_private_capture_fields() -> None:
    plan = _valid_plan()
    plan["review_states"][0]["screenshot_path"] = "/tmp/private-devhub-status.png"

    with pytest.raises(AttendedReadOnlyReviewPlanError):
        validate_review_plan(plan)


@pytest.mark.parametrize(
    "artifact_kind",
    [
        "screenshots",
        "traces",
        "har_data",
        "cookies",
        "auth_state",
        "credentials",
        "private_values",
    ],
)
def test_attended_read_only_review_plan_requires_private_artifact_rejection(artifact_kind: str) -> None:
    plan = _valid_plan()
    plan["rejected_artifacts"] = [
        item for item in plan["rejected_artifacts"] if item["artifact_kind"] != artifact_kind
    ]

    with pytest.raises(AttendedReadOnlyReviewPlanError):
        validate_review_plan(plan)


@pytest.mark.parametrize(
    "action_kind",
    [
        "official_upload",
        "submission",
        "inspection_scheduling",
        "cancellation",
        "certification",
        "payment_detail_entry",
        "final_payment_execution",
    ],
)
def test_attended_read_only_review_plan_requires_consequential_action_refusal(action_kind: str) -> None:
    plan = _valid_plan()
    plan["blocked_consequential_actions"] = [
        item for item in plan["blocked_consequential_actions"] if item["action_kind"] != action_kind
    ]

    with pytest.raises(AttendedReadOnlyReviewPlanError):
        validate_review_plan(plan)


def test_attended_read_only_review_plan_rejects_executable_cancellation() -> None:
    plan = _valid_plan()
    for action in plan["blocked_consequential_actions"]:
        if action["action_kind"] == "cancellation":
            action["may_execute"] = True

    with pytest.raises(AttendedReadOnlyReviewPlanError):
        validate_review_plan(plan)
