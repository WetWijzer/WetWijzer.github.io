from __future__ import annotations

import json
from pathlib import Path

from ppd.logic.combined_inactive_patch_preview_rehearsal import (
    assert_valid_combined_inactive_patch_preview_rehearsal_v1,
    validate_combined_inactive_patch_preview_rehearsal_v1,
)


_FIXTURES = Path(__file__).parent / "fixtures" / "combined_inactive_patch_preview_rehearsal_v1"


def _load_fixture(name: str) -> dict:
    return json.loads((_FIXTURES / name).read_text(encoding="utf-8"))


def test_valid_combined_inactive_rehearsal_fixture_has_no_findings() -> None:
    artifact = _load_fixture("valid_rehearsal.json")

    findings = validate_combined_inactive_patch_preview_rehearsal_v1(artifact)

    assert findings == []
    assert_valid_combined_inactive_patch_preview_rehearsal_v1(artifact)


def test_invalid_combined_inactive_rehearsal_rejects_required_guardrail_gaps() -> None:
    artifact = _load_fixture("invalid_rehearsal.json")

    codes = {finding.code for finding in validate_combined_inactive_patch_preview_rehearsal_v1(artifact)}

    assert "outside_combined_inactive_fixture_preview_rehearsal_scope" in codes
    assert "missing_cross_family_dependency_rows" in codes
    assert "missing_unchanged_family_inventory" in codes
    assert "missing_blocked_promotion_carry_forward_notes" in codes
    assert "missing_reviewer_signoff_placeholders" in codes
    assert "missing_rollback_checkpoints" in codes
    assert "missing_validation_commands" in codes
    assert "uncited_public_source_evidence" in codes
    assert "uncited_devhub_observation_evidence" in codes
    assert "forbidden_capture_or_raw_data_artifact" in codes
    assert "live_execution_or_applied_promotion_claim" in codes
    assert "legal_or_permitting_outcome_guarantee" in codes
    assert "payment_submission_scheduling_cancellation_certification_or_upload_language" in codes
    assert "mutation_flag_outside_combined_inactive_fixture_preview_rehearsal_scope" in codes


def test_cross_family_dependency_rows_must_cite_evidence() -> None:
    artifact = _load_fixture("valid_rehearsal.json")
    artifact["cross_family_dependency_rows"] = [
        {
            "source_family": "public_source_registry",
            "dependent_family": "devhub_observation_fixture",
            "dependency": "missing citations are not acceptable",
            "evidence_ids": [],
        }
    ]

    codes = {finding.code for finding in validate_combined_inactive_patch_preview_rehearsal_v1(artifact)}

    assert "invalid_cross_family_dependency_row" in codes
    assert "uncited_cross_family_dependency_row" in codes


def test_private_or_authenticated_session_artifacts_are_rejected() -> None:
    artifact = _load_fixture("valid_rehearsal.json")
    artifact["notes"] = ["Do not attach an auth_state file, token, cookie, or browser profile."]

    codes = {finding.code for finding in validate_combined_inactive_patch_preview_rehearsal_v1(artifact)}

    assert "private_authenticated_session_or_browser_artifact" in codes
