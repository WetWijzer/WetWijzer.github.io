from __future__ import annotations

import copy
import json
from pathlib import Path

from ppd.action_journal_export_v2_validation import (
    assert_valid_action_journal_export_packet_v2,
    validate_action_journal_export_packet_v2,
)


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "action_journal_export_packet_v2_valid.json"


def load_valid_packet() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def test_valid_fixture_passes() -> None:
    packet = load_valid_packet()

    result = validate_action_journal_export_packet_v2(packet)

    assert result.ok, result.errors
    assert_valid_action_journal_export_packet_v2(packet)


def test_rejects_missing_required_event_types() -> None:
    packet = load_valid_packet()
    packet["events"] = [event for event in packet["events"] if event["type"] != "redaction_checked"]

    result = validate_action_journal_export_packet_v2(packet)

    assert not result.ok
    assert "missing required event type: redaction_checked" in result.errors


def test_rejects_missing_redaction_checks() -> None:
    packet = load_valid_packet()
    packet["redaction_checks"] = []

    result = validate_action_journal_export_packet_v2(packet)

    assert not result.ok
    assert "packet must include redaction_checks" in result.errors


def test_rejects_source_required_event_without_evidence_reference() -> None:
    packet = load_valid_packet()
    packet["events"][1].pop("source_evidence_refs")

    result = validate_action_journal_export_packet_v2(packet)

    assert not result.ok
    assert any("is missing source_evidence_refs" in error for error in result.errors)


def test_rejects_missing_manual_handoff_or_refusal_evidence() -> None:
    packet = load_valid_packet()
    packet.pop("manual_handoff_or_refusal_evidence")
    packet["source_evidence"] = [item for item in packet["source_evidence"] if item["type"] != "manual_handoff"]
    packet["events"] = [event for event in packet["events"] if event["type"] != "manual_handoff_or_refusal_recorded"]

    result = validate_action_journal_export_packet_v2(packet)

    assert not result.ok
    assert "packet must include manual handoff or refusal evidence" in result.errors


def test_rejects_missing_validation_commands() -> None:
    packet = load_valid_packet()
    packet["validation_commands"] = []

    result = validate_action_journal_export_packet_v2(packet)

    assert not result.ok
    assert "packet must include non-empty validation_commands as argv lists" in result.errors


def test_rejects_sensitive_fields_and_private_values() -> None:
    packet = load_valid_packet()
    packet["events"][0]["credentials"] = {"token": "Bearer abc123"}
    packet["events"][0]["note"] = "raw download saved at /home/example/private.pdf"

    result = validate_action_journal_export_packet_v2(packet)

    assert not result.ok
    assert any("forbidden sensitive field present" in error for error in result.errors)
    assert any("forbidden sensitive value or claim" in error for error in result.errors)


def test_rejects_live_devhub_official_action_and_guarantee_claims() -> None:
    packet = load_valid_packet()
    packet["events"][0]["claims"] = [
        "live DevHub execution completed",
        "official action submitted",
        "permitting approval is guaranteed",
    ]

    result = validate_action_journal_export_packet_v2(packet)

    assert not result.ok
    assert any("forbidden DevHub, official-action, legal, or permitting claim" in error for error in result.errors)


def test_rejects_active_mutation_flags() -> None:
    packet = load_valid_packet()
    packet["release_state_mutation"] = True
    packet["nested"] = {"active_mutation_flags": ["prompt"]}

    result = validate_action_journal_export_packet_v2(packet)

    assert not result.ok
    assert "forbidden active mutation flag: release_state_mutation" in result.errors
    assert "forbidden active mutation flags list: nested.active_mutation_flags" in result.errors


def test_validator_does_not_mutate_packet() -> None:
    packet = load_valid_packet()
    original = copy.deepcopy(packet)

    validate_action_journal_export_packet_v2(packet)

    assert packet == original
