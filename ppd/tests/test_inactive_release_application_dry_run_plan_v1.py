from __future__ import annotations

import json
from pathlib import Path

import pytest

from ppd.release_review.inactive_application_dry_run_plan_v1 import (
    INACTIVE_RELEASE_APPLICATION_DRY_RUN_PLAN_V1_PACKET_TYPE,
    build_inactive_release_application_dry_run_plan_v1,
    validate_inactive_release_application_dry_run_plan_v1,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "release_review"


def load_valid_checklist() -> dict:
    return json.loads((FIXTURE_DIR / "checklist_v1_valid.json").read_text(encoding="utf-8"))


def finding_codes(plan: dict) -> set[str]:
    return {finding.code for finding in validate_inactive_release_application_dry_run_plan_v1(plan)}


def test_builds_fixture_first_inactive_release_application_dry_run_plan_v1() -> None:
    plan = build_inactive_release_application_dry_run_plan_v1(load_valid_checklist())

    assert plan["packet_type"] == INACTIVE_RELEASE_APPLICATION_DRY_RUN_PLAN_V1_PACKET_TYPE
    assert plan["fixture_first"] is True
    assert plan["dry_run_only"] is True
    assert plan["metadata_only"] is True
    assert plan["active_artifact_mutation_enabled"] is False
    assert plan["active_fixture_mutation_enabled"] is False
    assert plan["active_prompt_mutation_enabled"] is False
    assert plan["active_release_state_mutation_enabled"] is False
    assert plan["active_agent_state_mutation_enabled"] is False
    assert plan["artifact_mutation_enabled"] is False
    assert plan["fixture_mutation_enabled"] is False
    assert plan["prompt_mutation_enabled"] is False
    assert plan["release_state_mutation_enabled"] is False
    assert plan["agent_state_mutation_enabled"] is False
    assert plan["live_source_crawl_enabled"] is False
    assert plan["devhub_access_enabled"] is False
    assert plan["official_action_enabled"] is False
    assert plan["ordered_dry_run_application_steps"]
    assert plan["fixture_family_change_inventory"]
    assert plan["preflight_validation_gates"]
    assert plan["rollback_checkpoints"]
    assert plan["reviewer_approval_placeholders"]
    assert plan["non_application_no_release_notes"]
    assert validate_inactive_release_application_dry_run_plan_v1(plan) == []


def test_build_rejects_invalid_release_reviewer_checklist() -> None:
    checklist = load_valid_checklist()
    checklist["validation_commands"] = []

    with pytest.raises(ValueError, match="release reviewer go/no-go checklist v1 is not valid"):
        build_inactive_release_application_dry_run_plan_v1(checklist)


def test_rejects_missing_required_sections_and_validation_commands() -> None:
    plan = build_inactive_release_application_dry_run_plan_v1(load_valid_checklist())
    plan["ordered_dry_run_application_steps"] = []
    plan["fixture_family_change_inventory"] = []
    plan["preflight_validation_gates"] = []
    plan["rollback_checkpoints"] = []
    plan["reviewer_approval_placeholders"] = []
    plan["non_application_no_release_notes"] = []
    plan["validation_commands"] = []

    codes = finding_codes(plan)

    assert "missing-required-section" in codes
    assert "missing-validation-command" in codes


def test_rejects_missing_named_dry_run_application_safeguards() -> None:
    plan = build_inactive_release_application_dry_run_plan_v1(load_valid_checklist())
    plan["ordered_dry_run_application_steps"] = [
        row for row in plan["ordered_dry_run_application_steps"] if row["step_id"] != "inventory-fixture-families"
    ]
    for index, row in enumerate(plan["ordered_dry_run_application_steps"], start=1):
        row["order"] = index
    plan["preflight_validation_gates"] = [
        row for row in plan["preflight_validation_gates"] if row["gate_id"] != "gate-validation-replay-commands-present"
    ]
    plan["non_application_no_release_notes"] = [
        row for row in plan["non_application_no_release_notes"] if row["note_id"] != "no-release-state-change"
    ]

    codes = finding_codes(plan)

    assert "missing-dry-run-application-step" in codes
    assert "missing-preflight-validation-gate" in codes
    assert "missing-non-application-no-release-note" in codes


def test_rejects_mutation_live_devhub_and_official_action_flags() -> None:
    plan = build_inactive_release_application_dry_run_plan_v1(load_valid_checklist())
    mutation_flags = (
        "active_artifact_mutation_enabled",
        "active_fixture_mutation_enabled",
        "active_prompt_mutation_enabled",
        "active_release_state_mutation_enabled",
        "active_agent_state_mutation_enabled",
        "artifact_mutation_enabled",
        "fixture_mutation_enabled",
        "prompt_mutation_enabled",
        "release_state_mutation_enabled",
        "agent_state_mutation_enabled",
        "live_source_crawl_enabled",
        "devhub_access_enabled",
        "official_action_enabled",
    )
    for flag in mutation_flags:
        plan[flag] = True

    assert finding_codes(plan) == {"mutation-or-live-flag-enabled"}


def test_rejects_private_raw_live_guarantee_and_consequential_references() -> None:
    plan = build_inactive_release_application_dry_run_plan_v1(load_valid_checklist())
    plan["reviewer_approval_placeholders"][0]["source_refs"] = ["ppd/.auth/storage-state.json"]
    plan["rollback_checkpoints"][0]["checkpoint"] = "The live execution completed."
    plan["non_application_no_release_notes"][0]["note"] = "This guarantees the permit will issue."
    plan["ordered_dry_run_application_steps"][0]["action"] = "Submit the permit."

    codes = finding_codes(plan)

    assert "private-or-raw-artifact-reference" in codes
    assert "forbidden-release-or-official-action-language" in codes


def test_rejects_artifact_keys_for_auth_session_browser_raw_pdf_downloads_and_traces() -> None:
    plan = build_inactive_release_application_dry_run_plan_v1(load_valid_checklist())
    plan["auth_state"] = {"path": "redacted"}
    plan["browser_artifact"] = True
    plan["session_artifact"] = "present"
    plan["screenshot_refs"] = ["redacted"]
    plan["trace_refs"] = ["redacted"]
    plan["har_refs"] = ["redacted"]
    plan["raw_pdf_data"] = "redacted"
    plan["downloaded_data"] = "redacted"

    assert "private-or-raw-artifact-reference" in finding_codes(plan)


def test_rejects_release_complete_applied_and_outcome_claims() -> None:
    plan = build_inactive_release_application_dry_run_plan_v1(load_valid_checklist())
    plan["non_application_no_release_notes"].append(
        {"note_id": "unsafe-claim", "note": "The release-complete artifact was applied to active fixtures and approval is assured."}
    )

    assert "forbidden-release-or-official-action-language" in finding_codes(plan)


def test_inventory_groups_fixture_family_from_checklist_citations() -> None:
    plan = build_inactive_release_application_dry_run_plan_v1(load_valid_checklist())

    family_ids = {row["family_id"] for row in plan["fixture_family_change_inventory"]}

    assert "release-review" in family_ids
    assert all(row["planned_change"] == "none" for row in plan["fixture_family_change_inventory"])
    assert all(row["active_fixture_change"] is False for row in plan["fixture_family_change_inventory"])
