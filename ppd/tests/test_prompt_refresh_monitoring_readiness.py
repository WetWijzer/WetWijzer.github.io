from __future__ import annotations

import json
from pathlib import Path

from ppd.prompt_refresh.readiness import validate_monitoring_readiness_packet


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "prompt_refresh_monitoring_readiness"


def load_valid_packet() -> dict[str, object]:
    return json.loads((FIXTURE_DIR / "valid_packet.json").read_text(encoding="utf-8"))


def finding_codes(packet: dict[str, object]) -> set[str]:
    return {finding.code for finding in validate_monitoring_readiness_packet(packet)}


def test_valid_monitoring_readiness_packet_has_no_findings() -> None:
    assert validate_monitoring_readiness_packet(load_valid_packet()) == []


def test_rejects_uncited_checks() -> None:
    packet = load_valid_packet()
    packet["checks"] = [{"check_id": "uncited", "description": "No evidence."}]

    assert "uncited_check" in finding_codes(packet)


def test_rejects_missing_required_readiness_sections() -> None:
    for key, code in {
        "drift_signals": "missing_drift_signals",
        "escalation_owners": "missing_escalation_owners",
        "rollback_triggers": "missing_rollback_triggers",
        "offline_validation_commands": "missing_offline_validation_commands",
    }.items():
        packet = load_valid_packet()
        packet[key] = []

        assert code in finding_codes(packet)


def test_rejects_private_or_authenticated_facts() -> None:
    packet = load_valid_packet()
    packet["notes"] = "Includes an authenticated fact from a private account page."

    assert "private_or_authenticated_fact" in finding_codes(packet)


def test_rejects_raw_crawl_output() -> None:
    packet = load_valid_packet()
    packet["raw_html"] = "raw crawl output"

    assert "raw_crawl_output" in finding_codes(packet)


def test_rejects_live_execution_claims() -> None:
    packet = load_valid_packet()
    packet["notes"] = "The live crawler ran and processor executed successfully."

    assert "live_execution_claim" in finding_codes(packet)


def test_rejects_legal_or_permitting_outcome_guarantees() -> None:
    packet = load_valid_packet()
    packet["notes"] = "This prompt refresh means the permit will be approved."

    assert "legal_or_permitting_outcome_guarantee" in finding_codes(packet)


def test_rejects_active_mutation_flags() -> None:
    packet = load_valid_packet()
    packet["state"] = {"active_prompt_mutation": True}

    assert "active_mutation_flag" in finding_codes(packet)


def test_inactive_mutation_flags_do_not_fail() -> None:
    packet = load_valid_packet()
    packet["state"] = {"active_prompt_mutation": False}

    assert finding_codes(packet) == set()
