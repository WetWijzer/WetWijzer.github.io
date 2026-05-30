from __future__ import annotations

import copy
from pathlib import Path

import pytest

from ppd.agent_readiness.draft_preview_post_release_monitoring_readiness_packet_v2 import (
    assert_valid_draft_preview_post_release_monitoring_readiness_v2_packet,
    load_draft_preview_post_release_monitoring_readiness_v2_fixture,
    validate_draft_preview_post_release_monitoring_readiness_v2_packet,
)

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "draft_preview_post_release_monitoring_readiness_packet_v2" / "valid_packet.json"


def _valid_packet() -> dict:
    return load_draft_preview_post_release_monitoring_readiness_v2_fixture(FIXTURE_PATH)


def _problem_text(packet: dict) -> str:
    result = validate_draft_preview_post_release_monitoring_readiness_v2_packet(packet)
    assert not result.valid
    return "; ".join(result.problems)


def test_valid_draft_preview_post_release_monitoring_readiness_v2_fixture_passes() -> None:
    packet = _valid_packet()

    assert_valid_draft_preview_post_release_monitoring_readiness_v2_packet(packet)


def test_rejects_uncited_monitor_check() -> None:
    packet = _valid_packet()
    packet["monitoring_checks"][0]["source_evidence_ids"] = []

    assert "lacks source evidence citations" in _problem_text(packet)


def test_rejects_unknown_monitor_check_citation() -> None:
    packet = _valid_packet()
    packet["monitoring_checks"][0]["source_evidence_ids"] = ["missing-source"]

    assert "cites unknown source evidence missing-source" in _problem_text(packet)


@pytest.mark.parametrize(
    ("field", "expected"),
    [
        ("drift_signals", "lacks drift_signals"),
        ("escalation_owner", "lacks escalation owner"),
        ("rollback_trigger_ref", "lacks rollback trigger reference"),
    ],
)
def test_rejects_monitor_check_missing_required_readiness_fields(field: str, expected: str) -> None:
    packet = _valid_packet()
    packet["monitoring_checks"][0].pop(field)

    assert expected in _problem_text(packet)


def test_rejects_missing_rollback_triggers() -> None:
    packet = _valid_packet()
    packet["rollback_triggers"] = []

    assert "rollback_triggers must be a non-empty list" in _problem_text(packet)


def test_rejects_missing_allowed_validation_commands() -> None:
    packet = _valid_packet()
    packet["allowed_validation_commands"] = []

    assert "allowed_validation_commands must be a non-empty list of commands" in _problem_text(packet)


def test_rejects_offline_command_not_allowlisted() -> None:
    packet = _valid_packet()
    packet["offline_validation_commands"].append(["python3", "ppd/crawler/live_public_scrape.py"])

    assert "is not listed in allowed_validation_commands" in _problem_text(packet)


@pytest.mark.parametrize(
    ("field", "value", "expected"),
    [
        ("private_fact", "Applicant phone 503-555-0100", "private or authenticated facts"),
        ("raw_pdf_path", "/home/example/downloads/application.pdf", "raw crawl, PDF, session"),
        ("session_artifact", "trace.zip", "raw crawl, PDF, session"),
        ("monitoring_claim", "live monitoring executed against production", "live monitoring, DevHub, browser, LLM, crawler, or processor execution"),
        ("devhub_claim", "opened DevHub and checked the permit", "live monitoring, DevHub, browser, LLM, crawler, or processor execution"),
        ("llm_claim", "live LLM called for release judgment", "live monitoring, DevHub, browser, LLM, crawler, or processor execution"),
        ("crawler_claim", "crawler ran and downloaded the updated PDF", "live monitoring, DevHub, browser, LLM, crawler, or processor execution"),
        ("processor_claim", "processor executed on a live PDF", "live monitoring, DevHub, browser, LLM, crawler, or processor execution"),
        ("outcome_claim", "permit will be approved", "legal or permitting outcomes"),
        ("active_prompt_mutation", True, "active prompt, guardrail, PDF, surface-registry, monitoring, release-state, or agent-state mutation"),
        ("active_guardrail_mutation", True, "active prompt, guardrail, PDF, surface-registry, monitoring, release-state, or agent-state mutation"),
        ("active_pdf_mutation", True, "active prompt, guardrail, PDF, surface-registry, monitoring, release-state, or agent-state mutation"),
        ("active_surface_registry_mutation", True, "active prompt, guardrail, PDF, surface-registry, monitoring, release-state, or agent-state mutation"),
        ("active_monitoring_mutation", True, "active prompt, guardrail, PDF, surface-registry, monitoring, release-state, or agent-state mutation"),
        ("release_state_mutation", True, "active prompt, guardrail, PDF, surface-registry, monitoring, release-state, or agent-state mutation"),
        ("active_agent_state_mutation", True, "active prompt, guardrail, PDF, surface-registry, monitoring, release-state, or agent-state mutation"),
    ],
)
def test_rejects_unsafe_packet_values(field: str, value: object, expected: str) -> None:
    packet = _valid_packet()
    packet["unsafe_probe"] = {field: value}

    assert expected in _problem_text(packet)


def test_rejects_private_authenticated_classification() -> None:
    packet = _valid_packet()
    packet["source_evidence"].append(
        {
            "source_evidence_id": "private-auth-source",
            "privacy_classification": "devhub_authenticated",
            "quote_or_fact": "redacted",
        }
    )

    assert "private or authenticated facts" in _problem_text(packet)


def test_rejects_nested_mutation_flags() -> None:
    packet = _valid_packet()
    packet["nested"] = {"mutation_flags": {"surface_registry": True}}

    assert "mutation_flags.surface_registry must be false" in _problem_text(packet)


def test_validation_does_not_mutate_input_packet() -> None:
    packet = _valid_packet()
    before = copy.deepcopy(packet)

    assert validate_draft_preview_post_release_monitoring_readiness_v2_packet(packet).valid
    assert packet == before
