from __future__ import annotations

import json
from pathlib import Path

import pytest

from ppd.release.inactive_reviewer_packet_v1 import validate_inactive_release_application_reviewer_packet_v1
from ppd.release_review.inactive_application_dry_run_plan_v1 import (
    INACTIVE_RELEASE_APPLICATION_DRY_RUN_PLAN_V1_PACKET_TYPE,
    build_inactive_release_application_dry_run_plan_v1,
)
from ppd.release_review.inactive_promotion_application_patch_plan_v1 import (
    INACTIVE_PROMOTION_APPLICATION_PATCH_PLAN_V1_PACKET_TYPE,
    build_inactive_promotion_application_patch_plan_v1,
    validate_inactive_promotion_application_patch_plan_v1,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "release_review"


def _dry_run_plan() -> dict[str, object]:
    checklist = json.loads((FIXTURE_DIR / "checklist_v1_valid.json").read_text(encoding="utf-8"))
    plan = build_inactive_release_application_dry_run_plan_v1(checklist)
    plan["fixture_family_change_inventory"] = [
        {
            "family_id": "release-application",
            "planned_change": "none",
            "active_fixture_change": False,
            "candidate_refs": [
                "ppd/tests/fixtures/release_review/checklist_v1_valid.json",
                "ppd/tests/fixtures/release_review/checklist_v1_valid.json#evidence-citation-coverage",
            ],
            "review_status": "pending_manual_review",
        }
    ]
    return plan


def _reviewer_packet() -> dict[str, object]:
    packet: dict[str, object] = {
        "packet_version": "inactive-release-application-reviewer-packet-v1",
        "release_activity": "inactive",
        "reviewer_comparison_rows": [
            {
                "reviewer": "fixture-reviewer",
                "baseline": "inactive packet fixture",
                "candidate": "current packet fixture",
                "finding": "no active release claim",
            }
        ],
        "prerequisite_gate_acknowledgements": [
            {"gate": "fixtures-only", "acknowledged": True},
            {"gate": "validation-replay", "acknowledged": True},
        ],
        "fixture_family_risk_notes": [
            {"fixture_family": "release-application", "risk_note": "deterministic fixture only"},
        ],
        "rollback_checkpoint_confirmations": [
            {"checkpoint": "no state mutation", "confirmed": True},
        ],
        "unresolved_hold_carry_forward": [
            {
                "hold_id": "hold-001",
                "source": "supervisor",
                "carry_forward_reason": "requires later human review",
                "next_review_action": "compare deterministic reviewer rows",
            }
        ],
        "validation_commands": [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]],
        "notes": "Inactive reviewer packet based on deterministic committed fixtures.",
    }
    result = validate_inactive_release_application_reviewer_packet_v1(packet)
    assert result.ok, result.errors
    return packet


def _codes(plan: dict[str, object]) -> set[str]:
    return {finding.code for finding in validate_inactive_promotion_application_patch_plan_v1(plan)}


def test_builds_fixture_first_inactive_promotion_application_patch_plan_v1() -> None:
    plan = build_inactive_promotion_application_patch_plan_v1(_dry_run_plan(), _reviewer_packet())

    assert plan["packet_type"] == INACTIVE_PROMOTION_APPLICATION_PATCH_PLAN_V1_PACKET_TYPE
    assert plan["fixture_first"] is True
    assert plan["dry_run_only"] is True
    assert plan["metadata_only"] is True
    assert plan["patch_application_status"] == "not_applied"
    assert plan["consumed_input_packet_refs"] == {
        "inactive_release_application_dry_run_plan_v1": INACTIVE_RELEASE_APPLICATION_DRY_RUN_PLAN_V1_PACKET_TYPE,
        "inactive_release_application_reviewer_packet_v1": "inactive-release-application-reviewer-packet-v1",
    }
    assert plan["file_family_patch_rows"] == [
        {
            "order": 1,
            "patch_row_id": "patch-row-001-release-application",
            "file_family_id": "release-application",
            "operation": "complete_file_replacement_candidate",
            "patch_scope": "inactive_fixture_family_only",
            "application_status": "not_applied",
            "active_patch_applied": False,
            "source_fixture_refs": [
                "ppd/tests/fixtures/release_review/checklist_v1_valid.json",
                "ppd/tests/fixtures/release_review/checklist_v1_valid.json#evidence-citation-coverage",
            ],
            "source_dry_run_plan_refs": [
                "fixture_family_change_inventory",
                "gate-checklist-validation-clean",
                "gate-rollback-confirmations-present",
                "gate-validation-replay-commands-present",
                "gate-unresolved-risk-placeholders-present",
            ],
            "reviewer_packet_refs": ["reviewer-comparison-row-1"],
            "expected_before_checksum": "sha256:pending-before-release-application",
            "expected_after_checksum": "sha256:pending-after-release-application",
            "prerequisite_validation_refs": [
                "gate-checklist-validation-clean",
                "gate-rollback-confirmations-present",
                "gate-validation-replay-commands-present",
                "gate-unresolved-risk-placeholders-present",
            ],
            "reviewer_approval_ref": "reviewer-approval-001-release-application",
            "rollback_plan_refs": ["rollback-discard-dry-run-plan", "rollback-fixture-family-1"],
        }
    ]
    assert plan["source_fixture_references"]
    assert plan["prerequisite_validation_replay_inventory"][0]["command"] == ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]
    assert plan["reviewer_approval_placeholders"][0]["approval_status"] == "pending_reviewer_approval"
    assert plan["rollback_plan_references"][0]["active_changes_to_rollback"] is False
    assert plan["non_application_attestations"] == {
        "applies_patches": False,
        "edits_active_artifacts": False,
        "changes_prompts": False,
        "updates_release_state": False,
        "uses_live_sources": False,
        "uses_devhub": False,
        "performs_official_actions": False,
    }
    assert validate_inactive_promotion_application_patch_plan_v1(plan) == []


def test_build_rejects_invalid_dry_run_plan_input() -> None:
    dry_run_plan = _dry_run_plan()
    dry_run_plan["validation_commands"] = []

    with pytest.raises(ValueError, match="inactive release application dry-run plan v1 is not valid"):
        build_inactive_promotion_application_patch_plan_v1(dry_run_plan, _reviewer_packet())


def test_build_rejects_invalid_reviewer_packet_input() -> None:
    reviewer_packet = _reviewer_packet()
    reviewer_packet["prerequisite_gate_acknowledgements"] = []

    with pytest.raises(ValueError, match="inactive release application reviewer packet v1 is not valid"):
        build_inactive_promotion_application_patch_plan_v1(_dry_run_plan(), reviewer_packet)


def test_rejects_applied_patch_and_mutation_flags() -> None:
    plan = build_inactive_promotion_application_patch_plan_v1(_dry_run_plan(), _reviewer_packet())
    plan["patch_application_status"] = "applied"
    plan["file_family_patch_rows"][0]["active_patch_applied"] = True
    plan["active_fixture_mutation_enabled"] = True

    codes = _codes(plan)

    assert "patch-application-not-blocked" in codes
    assert "patch-row-applied" in codes
    assert "mutation-or-live-flag-enabled" in codes


def test_rejects_missing_checksum_placeholders_and_fixture_refs() -> None:
    plan = build_inactive_promotion_application_patch_plan_v1(_dry_run_plan(), _reviewer_packet())
    plan["file_family_patch_rows"][0]["expected_after_checksum"] = "sha256:real-digest"
    plan["file_family_patch_rows"][0]["source_fixture_refs"] = ["public/corpus/portland-or/current/active.json"]
    plan["source_fixture_references"][0]["fixture_path"] = "public/corpus/portland-or/current/active.json"

    codes = _codes(plan)

    assert "missing-expected-checksum-placeholder" in codes
    assert "source-fixture-outside-ppd-tests" in codes


def test_rejects_missing_validation_replay_reviewer_and_rollback_sections() -> None:
    plan = build_inactive_promotion_application_patch_plan_v1(_dry_run_plan(), _reviewer_packet())
    plan["prerequisite_validation_replay_inventory"] = []
    plan["reviewer_approval_placeholders"] = []
    plan["rollback_plan_references"] = []

    codes = _codes(plan)

    assert "missing-required-section" in codes
    assert "missing-self-test-replay" in codes


def test_rejects_private_raw_live_or_consequential_references() -> None:
    plan = build_inactive_promotion_application_patch_plan_v1(_dry_run_plan(), _reviewer_packet())
    plan["source_fixture_references"][0]["fixture_path"] = "ppd/tests/fixtures/raw/downloaded-pdf.har"
    plan["reviewer_approval_placeholders"][0]["source_refs"] = ["ppd/.auth/storage-state.json"]
    plan["rollback_plan_references"][0]["rollback_status"] = "release complete after live execution"

    codes = _codes(plan)

    assert "private-or-raw-artifact-reference" in codes
    assert "forbidden-release-or-official-action-language" in codes
