from __future__ import annotations

import json
from pathlib import Path

from ppd.validation.prompt_refresh_monitoring_smoke import validate_packet

_FIXTURE_PATH = Path(__file__).parent / "fixtures" / "prompt_refresh_monitoring_smoke_packets.json"


def _fixtures() -> dict:
    return json.loads(_FIXTURE_PATH.read_text(encoding="utf-8"))


def test_prompt_refresh_monitoring_smoke_accepts_valid_fixture() -> None:
    errors = validate_packet(_fixtures()["valid"])

    assert errors == []


def test_prompt_refresh_monitoring_smoke_rejects_required_invalid_packets() -> None:
    invalid_packets = _fixtures()["invalid"]

    expected_fragments = {
        "uncited_observation": "missing citations",
        "missing_escalation": "escalation_decision is required",
        "missing_rollback": "rollback_trigger_checks must be a non-empty list",
        "missing_allowed_commands": "allowed_validation_commands must be a non-empty list",
        "private_authenticated_fact": "private or authenticated fact",
        "raw_crawl_output": "raw crawl output",
        "live_execution_claim": "live execution claim",
        "outcome_guarantee": "legal or permitting outcome guarantee",
        "mutation_flag": "active_prompt_mutation must not be true",
    }

    for name, expected_fragment in expected_fragments.items():
        errors = validate_packet(invalid_packets[name])
        assert any(expected_fragment in error for error in errors), name


def test_prompt_refresh_monitoring_smoke_rejects_unapproved_validation_command() -> None:
    packet = dict(_fixtures()["valid"])
    packet["allowed_validation_commands"] = [["python3", "ppd/tools/live_crawler.py"]]

    errors = validate_packet(packet)

    assert any("not an approved deterministic command" in error for error in errors)


def test_prompt_refresh_monitoring_smoke_rejects_all_active_mutation_surfaces() -> None:
    base_packet = _fixtures()["valid"]
    surfaces = (
        "source",
        "schedule",
        "prompt",
        "guardrail",
        "surface_registry",
        "monitoring",
        "release_state",
        "agent_state",
    )

    for surface in surfaces:
        packet = dict(base_packet)
        packet["mutation_flags"] = dict(base_packet["mutation_flags"])
        packet["mutation_flags"][surface] = True

        errors = validate_packet(packet)

        assert any(f"mutation_flags.{surface} must not be true" in error for error in errors), surface
