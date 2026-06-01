from __future__ import annotations

from pathlib import Path

from ppd.validation.activation_checklist_v4 import (
    finding_codes,
    validate_inactive_activation_checklist_v4_file,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "activation_checklist_v4"


def test_inactive_activation_checklist_v4_accepts_complete_placeholder_fixture() -> None:
    findings = validate_inactive_activation_checklist_v4_file(
        FIXTURE_DIR / "inactive_complete_placeholder.md"
    )

    assert findings == []


def test_inactive_activation_checklist_v4_rejects_missing_required_controls() -> None:
    findings = validate_inactive_activation_checklist_v4_file(
        FIXTURE_DIR / "inactive_missing_required_controls.md"
    )

    assert finding_codes(findings) >= {
        "missing_smoke_replay_reference",
        "missing_reviewer_prerequisites",
        "missing_signoff_placeholders",
        "missing_source_freshness_hold_clearance",
        "missing_rollback_checkpoint_rows",
        "missing_post_activation_smoke_checks",
        "missing_agent_notification_notes",
        "missing_validation_commands",
    }


def test_inactive_activation_checklist_v4_rejects_active_or_private_claims() -> None:
    findings = validate_inactive_activation_checklist_v4_file(
        FIXTURE_DIR / "inactive_with_prohibited_claims.md"
    )

    assert finding_codes(findings) >= {
        "active_activation_claim",
        "private_session_auth_artifact",
        "official_action_completion_claim",
        "legal_or_permitting_guarantee",
        "active_mutation_flag",
    }
