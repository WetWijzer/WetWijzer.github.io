from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest

from ppd.agent_readiness.devhub_read_only_agent_impact_packet_v1 import (
    EXACT_VALIDATION_COMMANDS,
    DevHubReadOnlyAgentImpactPacketV1Error,
    assert_valid_devhub_read_only_agent_impact_packet_v1,
    validate_devhub_read_only_agent_impact_packet_v1,
)

FIXTURE = Path(__file__).parent / "fixtures" / "devhub_read_only_agent_impact_packet_v1" / "valid_packet.json"


def _packet() -> dict[str, Any]:
    value = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _problems(packet: dict[str, Any]) -> str:
    return "; ".join(validate_devhub_read_only_agent_impact_packet_v1(packet).problems)


def test_valid_fixture_is_accepted() -> None:
    packet = _packet()

    result = validate_devhub_read_only_agent_impact_packet_v1(packet)

    assert result.valid
    assert result.problems == ()
    assert packet["validation_commands"] == EXACT_VALIDATION_COMMANDS
    assert_valid_devhub_read_only_agent_impact_packet_v1(packet)


@pytest.mark.parametrize(
    ("field", "expected"),
    [
        ("surface_delta_refs", "surface_delta_refs must be a non-empty list"),
        ("affected_missing_information_rows", "affected_missing_information_rows must be a non-empty list"),
        ("blocked_action_predicate_rows", "blocked_action_predicate_rows must be a non-empty list"),
        ("next_safe_action_rows", "next_safe_action_rows must be a non-empty list"),
        ("reversible_draft_eligibility_notes", "reversible_draft_eligibility_notes must be a non-empty list"),
        ("exact_confirmation_warnings", "exact_confirmation_warnings must be a non-empty list"),
        ("citation_source_placeholders", "citation_source_placeholders must be a non-empty list"),
        ("reviewer_holds", "reviewer_holds must be a non-empty list"),
    ],
)
def test_rejects_missing_required_packet_sections(field: str, expected: str) -> None:
    packet = _packet()
    packet[field] = []

    assert expected in _problems(packet)


def test_rejects_missing_surface_delta_references_on_impacted_rows() -> None:
    packet = _packet()
    del packet["affected_missing_information_rows"][0]["surface_delta_ref"]
    packet["next_safe_action_rows"][0]["surface_delta_ref"] = "surface-delta:unknown"

    problems = _problems(packet)

    assert "affected_missing_information_rows[0].surface_delta_ref is required" in problems
    assert "next_safe_action_rows[0].surface_delta_ref must reference surface_delta_refs" in problems


def test_rejects_missing_citation_source_placeholder_fields() -> None:
    packet = _packet()
    packet["citation_source_placeholders"][0]["source_id"] = ""
    packet["citation_source_placeholders"][0]["citation_status"] = "resolved"

    problems = _problems(packet)

    assert "citation_source_placeholders[0].source_id is required" in problems
    assert "citation_source_placeholders[0].citation_status must be pending_source_resolution" in problems


def test_rejects_missing_or_signed_reviewer_holds() -> None:
    packet = _packet()
    packet["reviewer_holds"] = packet["reviewer_holds"][:-1]
    packet["reviewer_holds"][0]["reviewer"] = "reviewer@example.test"
    packet["reviewer_holds"][1]["decision"] = "approved"

    problems = _problems(packet)

    assert "reviewer_holds must cover every impacted row" in problems
    assert "reviewer_holds[0] must remain an unsigned reviewer hold" in problems
    assert "reviewer_holds[1].decision must be pending_manual_review" in problems


def test_rejects_validation_command_drift() -> None:
    packet = _packet()
    packet["validation_commands"] = [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]]

    assert "validation_commands must match exact DevHub read-only agent impact packet v1 validation commands" in _problems(packet)


@pytest.mark.parametrize(
    ("key", "value", "expected"),
    [
        ("active_guardrail_mutation", True, "packet.active_guardrail_mutation must be false"),
        ("active_surface_map_mutation", True, "packet.active_surface_map_mutation must be false"),
        ("browser_state_path", "state.json", "must not include credentials, sessions, browser artifacts"),
        ("screenshot_path", "screen.png", "must not include credentials, sessions, browser artifacts"),
        ("trace_file", "trace.zip", "must not include credentials, sessions, browser artifacts"),
        ("har_file", "network.har", "must not include credentials, sessions, browser artifacts"),
        ("private_note", "private value", "must not reference credentials, sessions, browser artifacts"),
        ("live_note", "live DevHub observation completed", "must not include live DevHub or crawl claims"),
        ("crawl_note", "live crawl completed", "must not include live DevHub or crawl claims"),
        ("action_note", "official action completed", "must not include official-action completion or consequential-action claims"),
        ("submit_note", "agent may submit permit", "must not include official-action completion or consequential-action claims"),
        ("guarantee_note", "permit will be approved", "must not include legal or permitting guarantees"),
    ],
)
def test_rejects_forbidden_payload_terms(key: str, value: Any, expected: str) -> None:
    packet = _packet()
    packet[key] = value

    assert expected in _problems(packet)


def test_rejects_attestation_drift() -> None:
    packet = _packet()
    packet["attestations"]["devhub_accessed"] = True
    packet["attestations"]["official_action_completed"] = True

    problems = _problems(packet)

    assert "attestations.devhub_accessed must be false" in problems
    assert "attestations.official_action_completed must be false" in problems
    assert "packet.attestations.devhub_accessed must be false" in problems
    assert "packet.attestations.official_action_completed must be false" in problems


def test_assert_raises_with_validation_problems() -> None:
    packet = copy.deepcopy(_packet())
    packet["packet_version"] = "v2"

    with pytest.raises(DevHubReadOnlyAgentImpactPacketV1Error, match="packet_version"):
        assert_valid_devhub_read_only_agent_impact_packet_v1(packet)
