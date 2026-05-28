from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from ppd.devhub.guarded_action_preview import evaluate_guarded_action_preview

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "devhub_guarded_action_preview.json"


def load_fixture() -> dict[str, Any]:
    with FIXTURE_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def test_reversible_draft_fill_preview_is_allowed_with_all_guardrails() -> None:
    fixture = load_fixture()

    decision = evaluate_guarded_action_preview(fixture["reversible_draft_fill"])

    assert decision.allowed is True
    assert decision.status == "preview_ready"
    assert decision.action_type == "reversible_draft_fill"
    assert decision.reasons == ()


def test_preflight_requires_classification_source_surface_attendance_confidence_and_preview_metadata() -> None:
    fixture = load_fixture()
    base_plan = fixture["reversible_draft_fill"]
    invalid_values = {
        "action_classification": "",
        "source_evidence": [],
        "surface_evidence": {},
        "selector_confidence": 0.4,
        "attendance": False,
        "devhub_attended": False,
        "preview_metadata": None,
    }

    for required_name, invalid_value in invalid_values.items():
        plan = deepcopy(base_plan)
        plan[required_name] = invalid_value

        decision = evaluate_guarded_action_preview(plan)

        assert decision.allowed is False
        assert decision.status == "blocked_missing_guardrails"
        assert required_name in decision.required


def test_private_values_credentials_and_payment_details_are_refused() -> None:
    fixture = load_fixture()
    base_plan = fixture["reversible_draft_fill"]

    for sensitive_patch in fixture["sensitive_packet_patches"]:
        plan = deepcopy(base_plan)
        plan.update(sensitive_patch)

        decision = evaluate_guarded_action_preview(plan)

        assert decision.allowed is False
        assert decision.status == "refused_sensitive_packet"
        assert decision.required == ("redacted_preflight_packet",)


def test_side_effect_requests_fail_closed_even_when_requested_as_preview() -> None:
    fixture = load_fixture()
    base_plan = fixture["reversible_draft_fill"]

    for side_effect_patch in fixture["side_effect_request_patches"]:
        plan = deepcopy(base_plan)
        plan.update(side_effect_patch)

        decision = evaluate_guarded_action_preview(plan)

        assert decision.allowed is False
        assert decision.status == "refused_side_effect_request"
        assert "manual_user_handoff" in decision.required
        assert "action_specific_confirmation" in decision.required


def test_explicit_fail_closed_action_types_are_refused() -> None:
    fixture = load_fixture()
    reversible_plan = fixture["reversible_draft_fill"]

    for action_type in fixture["fail_closed_action_types"]:
        plan = deepcopy(reversible_plan)
        plan["action_type"] = action_type

        decision = evaluate_guarded_action_preview(plan)

        assert decision.allowed is False
        assert decision.status == "refused_side_effect_request"
        assert decision.action_type == action_type


def test_unknown_non_side_effect_action_type_is_refused() -> None:
    fixture = load_fixture()
    plan = deepcopy(fixture["reversible_draft_fill"])
    plan["action_type"] = "delete_permit_record"

    decision = evaluate_guarded_action_preview(plan)

    assert decision.allowed is False
    assert decision.status == "refused_unknown_action"
    assert "supported_action_type" in decision.required
