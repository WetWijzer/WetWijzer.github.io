from __future__ import annotations

import pytest
from pathlib import Path

from ppd.devhub.attended_readonly_live_dry_run_plan_v2 import (
    REQUIRED_ATTESTATIONS,
    build_from_fixture_paths,
    validate_attended_readonly_live_dry_run_plan_v2,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures"
LIVE_DRY_RUN_DIR = FIXTURE_DIR / "devhub_attended_readonly_live_dry_run_plan_v2"
RUNBOOK_REFRESH_DIR = FIXTURE_DIR / "devhub_attended_readonly_runbook_refresh_packet_v2"
OBSERVATION_DIR = FIXTURE_DIR / "surface_registry_refresh_acceptance_packet_v2"


def _build_plan() -> dict:
    return build_from_fixture_paths(
        LIVE_DRY_RUN_DIR / "live_readiness_authorization_checklist_packet_v2.json",
        RUNBOOK_REFRESH_DIR / "expected_packet.json",
        OBSERVATION_DIR / "devhub_attended_readonly_observation_packet_v2.json",
    )


def test_builds_fixture_first_attended_devhub_readonly_live_dry_run_plan_v2() -> None:
    plan = _build_plan()

    validate_attended_readonly_live_dry_run_plan_v2(plan)

    assert plan["plan_id"] == "devhub-attended-readonly-live-dry-run-plan-v2-fixture-20260529"
    assert plan["mode"] == "fixture_first_attended_devhub_readonly_live_dry_run_plan"
    assert plan["consumes"] == {
        "live_readiness_authorization_checklist_packet_v2": "live-readiness-authorization-checklist-packet-v2",
        "attended_devhub_readonly_runbook_refresh_packet_v2": "devhub-attended-readonly-runbook-refresh-packet-v2-fixture-20260529",
        "devhub_attended_readonly_observation_packet_v2": "devhub-attended-readonly-observation-packet-v2-fixture-20260529",
    }
    assert plan["attestations"] == REQUIRED_ATTESTATIONS


def test_plan_contains_cited_manual_boundaries_verification_steps_redactions_and_abort_conditions() -> None:
    plan = _build_plan()

    assert len(plan["manual_login_mfa_captcha_boundaries"]) == 4
    assert len(plan["allowed_read_only_verification_steps"]) == 2
    assert len(plan["redaction_checklist_items"]) == 7
    assert len(plan["operator_abort_conditions"]) == 7

    assert all(item["citations"] for item in plan["manual_login_mfa_captcha_boundaries"])
    assert all(item["citations"] for item in plan["allowed_read_only_verification_steps"])
    assert all(item["citations"] for item in plan["redaction_checklist_items"])
    assert all(item["citations"] for item in plan["operator_abort_conditions"])


def test_plan_keeps_devhub_run_read_only_and_offline_only() -> None:
    plan = _build_plan()

    for boundary in plan["manual_login_mfa_captcha_boundaries"]:
        assert boundary["human_operator_required"] is True
        assert boundary["agent_may_request_credentials"] is False
        assert boundary["agent_may_store_credentials"] is False
        assert boundary["agent_may_automate_mfa_or_captcha"] is False
        assert boundary["official_action_allowed_after_handoff"] is False

    for step in plan["allowed_read_only_verification_steps"]:
        assert step["read_only"] is True
        assert step["official_action_allowed"] is False
        assert step["browser_automation_allowed"] is False
        assert step["auth_state_allowed"] is False
        assert step["private_values_allowed"] is False
        assert step["screenshot_trace_har_allowed"] is False

    for item in plan["redaction_checklist_items"]:
        assert item["required"] is True
        assert item["private_values_allowed"] is False
        assert item["raw_authenticated_values_allowed"] is False
        assert item["browser_artifacts_allowed"] is False


def test_validator_rejects_weakened_attestations_or_uncited_steps() -> None:
    plan = _build_plan()
    plan["attestations"]["no_live_devhub"] = False

    with pytest.raises(ValueError, match="attestations"):
        validate_attended_readonly_live_dry_run_plan_v2(plan)

    plan = _build_plan()
    plan["allowed_read_only_verification_steps"][0]["citations"] = []

    with pytest.raises(ValueError, match="citations"):
        validate_attended_readonly_live_dry_run_plan_v2(plan)


def test_validator_rejects_boundary_that_allows_credential_or_mfa_automation() -> None:
    plan = _build_plan()
    plan["manual_login_mfa_captcha_boundaries"][0]["agent_may_automate_mfa_or_captcha"] = True

    with pytest.raises(ValueError, match="agent_may_automate_mfa_or_captcha"):
        validate_attended_readonly_live_dry_run_plan_v2(plan)
