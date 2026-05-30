from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from ppd.public_refresh.readiness_packet_v2 import (
    build_public_refresh_readiness_packet_v2,
    require_public_refresh_readiness_packet_v2,
    validate_public_refresh_readiness_packet_v2,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "public_refresh"


def _load_json(name: str) -> dict:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def _valid_packet() -> dict:
    return build_public_refresh_readiness_packet_v2(_load_json("inactive_release_activation_checklist_v2.json"))


def _problem_text(packet: dict) -> str:
    result = validate_public_refresh_readiness_packet_v2(packet)
    assert not result.valid
    return "; ".join(result.errors)


def test_build_public_refresh_readiness_packet_v2_matches_fixture() -> None:
    checklist = _load_json("inactive_release_activation_checklist_v2.json")
    expected = _load_json("expected_public_refresh_readiness_packet_v2.json")

    packet = build_public_refresh_readiness_packet_v2(checklist)

    assert packet == expected


def test_public_refresh_readiness_packet_v2_is_offline_and_non_persistent() -> None:
    packet = _valid_packet()

    assert packet["network_access"] == "not_requested"
    assert packet["devhub_scope"] == "not_touched"
    assert packet["active_source_registry_changes"] == "not_allowed"
    assert all(item["offline_only"] for item in packet["ordered_public_source_refresh_prerequisites"])
    assert all("raw" not in command for command in packet["exact_offline_validation_commands"] for command in command)
    require_public_refresh_readiness_packet_v2(packet)


def test_public_refresh_readiness_packet_v2_rejects_active_checklist() -> None:
    checklist = _load_json("inactive_release_activation_checklist_v2.json")
    checklist["status"] = "active"

    with pytest.raises(ValueError, match="only consumes inactive checklists"):
        build_public_refresh_readiness_packet_v2(checklist)


@pytest.mark.parametrize(
    ("field", "expected"),
    [
        ("ordered_public_source_refresh_prerequisites", "ordered_public_source_refresh_prerequisites must be a non-empty list"),
        ("allowlist_and_robots_review_placeholders", "allowlist_and_robots_review_placeholders must be a non-empty list"),
        ("source_freshness_comparison_placeholders", "source_freshness_comparison_placeholders must be a non-empty list"),
        ("raw_body_non_persistence_attestations", "raw_body_non_persistence_attestations must be a non-empty list"),
        ("affected_guardrail_review_placeholders", "affected_guardrail_review_placeholders must be a non-empty list"),
        ("exact_offline_validation_commands", "exact_offline_validation_commands must be a non-empty list"),
    ],
)
def test_public_refresh_readiness_packet_v2_rejects_missing_required_sections(field: str, expected: str) -> None:
    packet = _valid_packet()
    packet[field] = []

    assert expected in _problem_text(packet)


def test_public_refresh_readiness_packet_v2_rejects_missing_robots_placeholder() -> None:
    packet = _valid_packet()
    packet["allowlist_and_robots_review_placeholders"][0].pop("robots_review_status")

    assert "robots_review_status must be present" in _problem_text(packet)


def test_public_refresh_readiness_packet_v2_rejects_missing_source_freshness_comparison_field() -> None:
    packet = _valid_packet()
    packet["source_freshness_comparison_placeholders"][0]["expected_comparison_fields"] = ["content_hash"]

    problems = _problem_text(packet)

    assert "expected_comparison_fields missing" in problems
    assert "affected_guardrail_bundle_ids" in problems


def test_public_refresh_readiness_packet_v2_rejects_missing_raw_body_attestation() -> None:
    packet = _valid_packet()
    packet["raw_body_non_persistence_attestations"] = packet["raw_body_non_persistence_attestations"][:1]

    assert "missing raw-body non-persistence attestation: metadata_only_fixture_scope" in _problem_text(packet)


def test_public_refresh_readiness_packet_v2_rejects_missing_guardrail_review_placeholder_status() -> None:
    packet = _valid_packet()
    packet["affected_guardrail_review_placeholders"][0].pop("review_status")

    assert "review_status must be present" in _problem_text(packet)


def test_public_refresh_readiness_packet_v2_rejects_modified_validation_commands() -> None:
    packet = _valid_packet()
    packet["exact_offline_validation_commands"].append(["python3", "ppd/crawler/live_public_scrape.py"])

    assert "exact_offline_validation_commands must match" in _problem_text(packet)


@pytest.mark.parametrize(
    ("field", "value", "expected"),
    [
        ("session_state", "storage-state.json", "private, session, browser, raw, or downloaded artifacts"),
        ("browser_trace", "trace.zip", "private, session, browser, raw, or downloaded artifacts"),
        ("raw_body", "raw body", "private, session, browser, raw, or downloaded artifacts"),
        ("downloaded_document_path", "/home/example/downloads/permit.pdf", "private, session, browser, raw, or downloaded artifacts"),
        ("live_crawl_performed", True, "live crawl or network execution"),
        ("crawl_claim", "live crawl captured the updated source", "live crawl or network execution"),
        ("official_action_claim", "submit permit application after refresh", "consequential official action language"),
        ("guarantee_claim", "permit will be approved", "legal or permitting outcomes"),
        ("source_mutation", True, "active source, process, requirement, guardrail, or release-state mutation"),
        ("process_mutation", True, "active source, process, requirement, guardrail, or release-state mutation"),
        ("requirement_mutation", True, "active source, process, requirement, guardrail, or release-state mutation"),
        ("guardrail_mutation", True, "active source, process, requirement, guardrail, or release-state mutation"),
        ("release_state_mutation", True, "active source, process, requirement, guardrail, or release-state mutation"),
    ],
)
def test_public_refresh_readiness_packet_v2_rejects_unsafe_packet_values(field: str, value: object, expected: str) -> None:
    packet = _valid_packet()
    packet["unsafe_probe"] = {field: value}

    assert expected in _problem_text(packet)


def test_public_refresh_readiness_packet_v2_rejects_active_source_registry_changes() -> None:
    packet = _valid_packet()
    packet["active_source_registry_changes"] = "allowed"

    assert "active_source_registry_changes must be not_allowed" in _problem_text(packet)


def test_public_refresh_readiness_packet_v2_validation_does_not_mutate_input() -> None:
    packet = _valid_packet()
    before = copy.deepcopy(packet)

    assert validate_public_refresh_readiness_packet_v2(packet).valid
    assert packet == before
