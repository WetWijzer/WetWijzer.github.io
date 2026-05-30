from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest

from ppd.agent_readiness.inactive_release_activation_checklist_v2 import (
    assert_valid_inactive_release_activation_checklist_v2,
    validate_inactive_release_activation_checklist_v2,
)

FIXTURES = Path(__file__).parent / "fixtures" / "inactive_release_activation_checklist_v2"


def _valid_packet() -> dict[str, Any]:
    return json.loads((FIXTURES / "valid_checklist.json").read_text(encoding="utf-8"))


def _assert_rejected(packet: dict[str, Any], code: str) -> None:
    issues = validate_inactive_release_activation_checklist_v2(packet)
    assert any(issue["code"] == code for issue in issues), issues
    with pytest.raises(ValueError, match=code):
        assert_valid_inactive_release_activation_checklist_v2(packet)


def test_accepts_valid_inactive_release_activation_checklist_v2_fixture() -> None:
    packet = _valid_packet()

    assert validate_inactive_release_activation_checklist_v2(packet) == []
    assert_valid_inactive_release_activation_checklist_v2(packet)


@pytest.mark.parametrize(
    ("field", "code"),
    [
        ("activation_prerequisites", "missing_activation_prerequisites"),
        ("human_approval_placeholders", "missing_human_approval_placeholders"),
        ("rollback_confirmations", "missing_rollback_confirmations"),
        ("validation_transcript_placeholders", "missing_validation_transcript_placeholders"),
        ("no_live_access_attestations", "missing_no_live_access_attestations"),
        ("validation_commands", "missing_validation_commands"),
    ],
)
def test_rejects_missing_required_activation_checklist_sections(field: str, code: str) -> None:
    packet = _valid_packet()
    packet[field] = []

    _assert_rejected(packet, code)


@pytest.mark.parametrize(
    ("mutator", "code"),
    [
        (lambda packet: packet.update({"downloaded_document_path": "/tmp/private/raw.pdf"}), "private_or_raw_artifact_field"),
        (lambda packet: packet.update({"notes": "Downloaded document file was attached."}), "private_or_raw_artifact_text"),
        (lambda packet: packet.update({"notes": "Live execution completed against DevHub."}), "live_execution_claim"),
        (lambda packet: packet.update({"notes": "Submission completed for the permit."}), "consequential_official_action_language"),
        (lambda packet: packet.update({"notes": "Permit will be approved after activation."}), "legal_or_permitting_guarantee"),
        (lambda packet: packet.update({"active_promotion": True}), "active_mutation_flag"),
        (lambda packet: packet.update({"active_release_state_mutation": True}), "active_mutation_flag"),
        (lambda packet: packet.update({"validation_commands": [["python3", "ppd/crawler/live_run.py"]]}), "unsafe_validation_command"),
        (lambda packet: packet["human_approval_placeholders"][0].update({"status": "approved"}), "invalid_human_approval_placeholder"),
        (lambda packet: packet["rollback_confirmations"][0].update({"confirmation_status": "confirmed"}), "invalid_rollback_confirmation"),
        (lambda packet: packet["validation_transcript_placeholders"][0].update({"transcript": "passed"}), "invalid_validation_transcript_placeholder"),
        (lambda packet: packet["no_live_access_attestations"][0].update({"attested": False}), "invalid_no_live_access_attestation"),
    ],
)
def test_rejects_inactive_release_activation_checklist_v2_safety_violations(mutator: Any, code: str) -> None:
    packet = copy.deepcopy(_valid_packet())
    mutator(packet)

    _assert_rejected(packet, code)
