from __future__ import annotations

import json
from pathlib import Path

from ppd.devhub.manual_handoff_validation import (
    assert_valid_manual_handoff_decision_packet,
    validate_manual_handoff_decision_packet,
)


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "manual_handoff_decision_packets.json"


def _fixtures() -> dict[str, object]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def test_valid_manual_handoff_packet_passes() -> None:
    packet = _fixtures()["valid_manual_handoff"]

    result = validate_manual_handoff_decision_packet(packet)

    assert result.ok
    assert result.issues == ()
    assert_valid_manual_handoff_decision_packet(packet)


def test_invalid_manual_handoff_packet_reports_required_guardrail_failures() -> None:
    packet = _fixtures()["invalid_manual_handoff"]

    result = validate_manual_handoff_decision_packet(packet)

    assert not result.ok
    codes = {issue.code for issue in result.issues}
    assert "credential_prompt" in codes
    assert "automated_account_security_step" in codes
    assert "payment_entry_instruction" in codes
    assert "official_action_claim" in codes
    assert "uncited_handoff_reason" in codes
    assert "missing_blocked_action_link" in codes
    assert "private_value" in codes
    assert "local_private_path" in codes
    assert "consequential_alternative" in codes


def test_non_manual_packet_is_ignored_by_manual_handoff_validator() -> None:
    packet = {
        "decision": "safe_read_only",
        "summary": "Review public PP&D source titles only.",
    }

    result = validate_manual_handoff_decision_packet(packet)

    assert result.ok
    assert result.issues == ()
