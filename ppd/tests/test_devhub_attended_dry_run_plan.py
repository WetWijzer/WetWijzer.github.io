from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from ppd.devhub.attended_dry_run_plan import (
    AttendedDryRunPlanError,
    validate_plan,
    validate_plan_file,
)


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "devhub" / "attended_dry_run_plan.json"
REQUIRED_REFUSED_ACTION_CLASSES = {
    "account_creation_automation",
    "cancellation",
    "captcha_automation",
    "certification",
    "final_payment_execution",
    "inspection_scheduling",
    "login_automation",
    "mfa_automation",
    "official_upload",
    "payment_detail_entry",
    "submission",
}


def _fixture() -> dict[str, object]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def test_fixture_first_attended_dry_run_plan_passes() -> None:
    result = validate_plan_file(FIXTURE_PATH)

    assert result.plan_id == "devhub_attended_read_only_reversible_draft_plan"
    assert result.surface_count == 2
    assert result.action_count == 3
    assert result.missing_fact_count == 2
    assert result.missing_document_count == 1
    assert result.preview_count == 3
    assert set(result.refused_action_classes) == REQUIRED_REFUSED_ACTION_CLASSES
    assert result.journal_event_types == (
        "DevHub attended preflight",
        "local PDF preview",
        "manual handoff",
        "reversible draft plan",
        "user gap analysis",
    )


@pytest.mark.parametrize("action_class", sorted(REQUIRED_REFUSED_ACTION_CLASSES))
def test_rejects_required_refused_action_decision_classes(action_class: str) -> None:
    plan = _fixture()
    mutated = copy.deepcopy(plan)
    actions = mutated["action_decisions"]
    assert isinstance(actions, list)
    actions.append(
        {
            "action_id": f"unsafe_{action_class}",
            "label": f"Unsafe {action_class}",
            "action_class": action_class,
            "decision": "allow_reversible_draft",
            "may_execute_in_dry_run": True,
            "changes_official_state": True,
            "requires_exact_confirmation": True,
        }
    )

    with pytest.raises(AttendedDryRunPlanError, match="read_only or reversible_draft only"):
        validate_plan(mutated)


def test_rejects_missing_required_blocked_action_class() -> None:
    plan = _fixture()
    mutated = copy.deepcopy(plan)
    gaps = mutated["user_case_gap_analysis"]
    assert isinstance(gaps, dict)
    blocked_actions = gaps["blocked_actions"]
    assert isinstance(blocked_actions, list)
    gaps["blocked_actions"] = [
        item
        for item in blocked_actions
        if isinstance(item, dict) and item.get("action_class") != "payment_detail_entry"
    ]

    with pytest.raises(AttendedDryRunPlanError, match="missing required refused action classes"):
        validate_plan(mutated)


def test_rejects_blocked_action_without_refusal_decision() -> None:
    plan = _fixture()
    mutated = copy.deepcopy(plan)
    gaps = mutated["user_case_gap_analysis"]
    assert isinstance(gaps, dict)
    blocked_actions = gaps["blocked_actions"]
    assert isinstance(blocked_actions, list)
    first_action = blocked_actions[0]
    assert isinstance(first_action, dict)
    first_action["decision"] = "allow_reversible_draft"

    with pytest.raises(AttendedDryRunPlanError, match="must be refused"):
        validate_plan(mutated)


def test_rejects_low_confidence_surface_map() -> None:
    plan = _fixture()
    mutated = copy.deepcopy(plan)
    surfaces = mutated["surface_map_readiness"]
    assert isinstance(surfaces, list)
    first_surface = surfaces[0]
    assert isinstance(first_surface, dict)
    first_surface["selector_confidence"] = 0.62

    with pytest.raises(AttendedDryRunPlanError, match="selector confidence is too low"):
        validate_plan(mutated)


def test_rejects_missing_preview_requirement_kind() -> None:
    plan = _fixture()
    mutated = copy.deepcopy(plan)
    previews = mutated["preview_requirements"]
    assert isinstance(previews, list)
    mutated["preview_requirements"] = [
        item for item in previews if isinstance(item, dict) and item.get("preview_kind") != "user_case_gap"
    ]

    with pytest.raises(AttendedDryRunPlanError, match="preview requirements missing required kind"):
        validate_plan(mutated)


def test_rejects_private_session_artifact_markers() -> None:
    plan = _fixture()
    mutated = copy.deepcopy(plan)
    journal_events = mutated["journal_event_expectations"]
    assert isinstance(journal_events, list)
    first_event = journal_events[0]
    assert isinstance(first_event, dict)
    first_event["storage_state"] = "redacted"

    with pytest.raises(AttendedDryRunPlanError, match="forbidden private field"):
        validate_plan(mutated)
