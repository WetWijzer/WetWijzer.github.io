from __future__ import annotations

import json
from pathlib import Path

from ppd.live_dry_run_operator_briefing_v2 import (
    assert_live_dry_run_operator_briefing_packet_v2,
    validate_live_dry_run_operator_briefing_packet_v2,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "live_dry_run_operator_briefing_v2"


def _valid_packet() -> dict:
    return json.loads((FIXTURE_DIR / "valid_packet.json").read_text(encoding="utf-8"))


def _issue_codes(packet: dict) -> set[str]:
    return {issue.code for issue in validate_live_dry_run_operator_briefing_packet_v2(packet).issues}


def test_valid_fixture_passes() -> None:
    packet = _valid_packet()

    result = validate_live_dry_run_operator_briefing_packet_v2(packet)

    assert result.valid is True
    assert result.issues == ()
    assert_live_dry_run_operator_briefing_packet_v2(packet)


def test_rejects_uncited_go_no_go_notes() -> None:
    packet = _valid_packet()
    packet["go_no_go_notes"] = [{"decision": "go", "note": "Proceed with dry-run review."}]

    assert "uncited_go_no_go_note" in _issue_codes(packet)


def test_rejects_missing_attendance_checkpoints_and_stop_conditions() -> None:
    packet = _valid_packet()
    packet.pop("attendance_checkpoints")
    packet["stop_conditions"] = []

    codes = _issue_codes(packet)

    assert "missing_attendance_checkpoints" in codes
    assert "missing_stop_conditions" in codes


def test_rejects_private_authenticated_facts_and_raw_artifacts() -> None:
    packet = _valid_packet()
    packet["operator_notes"] = [
        "Use the applicant email address from the logged-in DevHub account.",
        "Review the Playwright trace.zip and HAR before continuing.",
    ]

    codes = _issue_codes(packet)

    assert "private_or_authenticated_fact" in codes
    assert "raw_artifact_reference" in codes


def test_rejects_live_execution_claims_and_credential_or_captcha_automation() -> None:
    packet = _valid_packet()
    packet["operator_notes"] = [
        "The worker clicked submit in DevHub during the live run.",
        "Script the MFA prompt and solve CAPTCHA automatically.",
    ]

    codes = _issue_codes(packet)

    assert "live_execution_claim" in codes
    assert "credential_mfa_captcha_automation" in codes


def test_rejects_outcome_guarantees_and_consequential_action_language() -> None:
    packet = _valid_packet()
    packet["operator_notes"] = [
        "This guarantees the permit will issue.",
        "Click submit and pay the fee after review.",
    ]

    codes = _issue_codes(packet)

    assert "outcome_guarantee" in codes
    assert "consequential_action_language" in codes


def test_rejects_active_mutation_flags() -> None:
    packet = _valid_packet()
    packet["controls"] = {
        "active_source_mutation": True,
        "update_surface_registry": "enabled",
        "prompt_mutation": "off",
    }

    result = validate_live_dry_run_operator_briefing_packet_v2(packet)
    mutation_issues = [issue for issue in result.issues if issue.code == "active_mutation_flag"]

    assert len(mutation_issues) == 2
