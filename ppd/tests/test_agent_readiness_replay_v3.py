from __future__ import annotations

import json
from pathlib import Path

from ppd.validation.agent_readiness_replay_v3 import (
    assert_agent_readiness_regression_replay_packet_v3,
    validate_agent_readiness_regression_replay_packet_v3,
)

_FIXTURE = Path(__file__).parent / "fixtures" / "agent_readiness_replay_v3" / "invalid_packets.json"


def _valid_packet() -> dict[str, object]:
    return {
        "version": "v3",
        "workflow_coverage": ["search", "review", "hold"],
        "expected_asks": ["Ask for missing permit number before lookup."],
        "holds_or_refusals": ["Hold when CAPTCHA, auth, payment, or submission is requested."],
        "next_safe_action_rows": [{"trigger": "missing address", "action": "ask clarifying question"}],
        "citation_references": [{"label": "PP&D public guidance", "url": "https://www.portland.gov/"}],
        "reviewer_dispositions": [{"reviewer": "fixture", "disposition": "reject unsafe actions"}],
        "validation_commands": [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]],
        "artifacts": [{"kind": "fixture", "path": "ppd/tests/fixtures/agent_readiness_replay_v3/packet.json"}],
        "claims": ["Fixture-only regression replay; no official action is performed."],
        "active_mutation_flags": [],
    }


def test_accepts_complete_fixture_packet() -> None:
    assert validate_agent_readiness_regression_replay_packet_v3(_valid_packet()) == []
    assert_agent_readiness_regression_replay_packet_v3(_valid_packet())


def test_rejects_invalid_fixture_packets() -> None:
    packets = json.loads(_FIXTURE.read_text(encoding="utf-8"))
    for name, packet in packets.items():
        errors = validate_agent_readiness_regression_replay_packet_v3(packet)
        assert errors, name


def test_rejects_each_required_evidence_row_when_missing() -> None:
    required = [
        "workflow_coverage",
        "expected_asks",
        "holds_or_refusals",
        "next_safe_action_rows",
        "citation_references",
        "reviewer_dispositions",
        "validation_commands",
    ]
    for field in required:
        packet = _valid_packet()
        packet.pop(field)
        errors = validate_agent_readiness_regression_replay_packet_v3(packet)
        assert f"missing {field}" in errors


def test_rejects_prohibited_artifacts_claims_and_mutations() -> None:
    packet = _valid_packet()
    packet["artifacts"] = [{"kind": "raw", "path": "private/session/browser/raw/downloaded.pdf"}]
    packet["claims"] = ["The live crawl completed official action and guarantees permit approval."]
    packet["active_mutation_flags"] = {"submit": True}

    errors = validate_agent_readiness_regression_replay_packet_v3(packet)

    assert any("prohibited artifact" in error for error in errors)
    assert any("prohibited claim" in error for error in errors)
    assert "active mutation flags are not allowed" in errors
