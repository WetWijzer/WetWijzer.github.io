from __future__ import annotations

import json
from pathlib import Path

from ppd.validation.requirement_formalization_candidate_packet_v1 import is_valid_packet, validate_packet


FIXTURES = Path(__file__).parent / "fixtures" / "requirement_formalization_candidate_packet_v1"


def _load_fixture(name: str) -> dict:
    with (FIXTURES / name).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def test_valid_packet_has_no_issues() -> None:
    packet = _load_fixture("valid_packet.json")

    assert validate_packet(packet) == []
    assert is_valid_packet(packet) is True


def test_invalid_packet_rejects_required_failure_modes() -> None:
    packet = _load_fixture("invalid_packet.json")

    issues = validate_packet(packet)
    codes = {issue.code for issue in issues}

    assert is_valid_packet(packet) is False
    assert "missing_packet_metadata" in codes
    assert "missing_candidate_field" in codes
    assert "uncited_candidate_row" in codes
    assert "private_or_authenticated_artifact" in codes
    assert "raw_or_downloaded_artifact" in codes
    assert "legal_or_permitting_outcome_guarantee" in codes
    assert "consequential_action_language" in codes
    assert "active_mutation_flag" in codes


def test_all_active_mutation_flags_are_rejected() -> None:
    packet = _load_fixture("valid_packet.json")
    row = packet["candidate_rows"][0]

    for flag in (
        "active_source_mutation",
        "active_document_mutation",
        "active_requirement_mutation",
        "active_process_mutation",
        "active_guardrail_mutation",
        "active_release_state_mutation",
        "active_agent_state_mutation",
    ):
        flagged = json.loads(json.dumps(packet))
        flagged["candidate_rows"][0][flag] = True
        codes = {issue.code for issue in validate_packet(flagged)}
        assert "active_mutation_flag" in codes, flag
