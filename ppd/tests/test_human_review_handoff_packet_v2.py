from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from ppd.agent_readiness.human_review_handoff_packet_v2 import (
    ALLOWED_DEFERRAL_DISPOSITIONS,
    REQUIRED_ATTESTATIONS,
    build_human_review_handoff_packet_v2,
    build_human_review_handoff_packet_v2_from_fixture,
    load_json,
    validate_human_review_handoff_packet_v2,
)

FIXTURE = Path(__file__).parent / "fixtures" / "human_review_handoff_packet_v2" / "source_packets.json"


def _source_packets() -> tuple[dict, dict]:
    source = load_json(FIXTURE)["source_packets"]
    return source["refresh_implementation_proposal_v2"], source["agent_readiness_replay_packet_v2"]


def _packet() -> dict:
    return build_human_review_handoff_packet_v2_from_fixture(FIXTURE)


def test_builds_fixture_first_human_review_handoff_packet_v2() -> None:
    packet = _packet()
    result = validate_human_review_handoff_packet_v2(packet)

    assert result.ok, result.errors
    assert packet["packet_type"] == "ppd.human_review_handoff_packet.v2"
    assert packet["packet_version"] == 2
    assert packet["consumes"] == {
        "refresh_implementation_proposal_v2": "refresh_implementation_proposal_v2",
        "agent_readiness_replay_packet_v2": "ppd.agent_readiness_replay_packet.v2",
    }
    assert packet["attestations"] == {key: True for key in sorted(REQUIRED_ATTESTATIONS)}


def test_handoff_contains_cited_checklist_deferrals_acceptance_and_rollback() -> None:
    packet = _packet()

    assert packet["reviewer_checklist_items"]
    assert packet["unresolved_deferrals"]
    assert packet["acceptance_criteria"]
    assert packet["rollback_verification"]
    assert packet["offline_validation_commands"]

    for field in ("reviewer_checklist_items", "unresolved_deferrals", "acceptance_criteria", "rollback_verification"):
        for row in packet[field]:
            assert row["citations"], field
            assert row["summary"]
            assert row["status"]

    for row in packet["unresolved_deferrals"]:
        assert row["disposition"] in ALLOWED_DEFERRAL_DISPOSITIONS

    deferral_ids = {row["deferral_id"] for row in packet["unresolved_deferrals"]}
    assert "stale-evidence-stale-evidence-1" in deferral_ids
    assert "conflicting-evidence-conflict-1" in deferral_ids
    assert "blocked-action-official-record-change" in deferral_ids


def test_builder_consumes_refresh_proposal_and_agent_readiness_replay() -> None:
    proposal, replay = _source_packets()

    packet = build_human_review_handoff_packet_v2(proposal, replay)

    checklist_roles = {role for item in packet["reviewer_checklist_items"] for role in item["source_packet_roles"]}
    assert "refresh_implementation_proposal_v2" in checklist_roles
    assert "agent_readiness_replay_packet_v2" in checklist_roles
    assert validate_human_review_handoff_packet_v2(packet).ok


def test_rejects_missing_citations_and_attestations() -> None:
    packet = _packet()
    broken = deepcopy(packet)
    broken["reviewer_checklist_items"][0]["citations"] = []
    broken["attestations"]["no_live"] = False

    result = validate_human_review_handoff_packet_v2(broken)

    assert not result.ok
    joined = "; ".join(result.errors)
    assert "reviewer_checklist_items[0].citations must be non-empty" in joined
    assert "attestations.no_live must be true" in joined


def test_rejects_missing_acceptance_deferral_disposition_and_rollback_sections() -> None:
    packet = _packet()
    broken = deepcopy(packet)
    broken["acceptance_criteria"] = []
    broken["rollback_verification"] = []
    broken["unresolved_deferrals"][0].pop("disposition")

    result = validate_human_review_handoff_packet_v2(broken)

    assert not result.ok
    joined = "; ".join(result.errors)
    assert "acceptance_criteria must be non-empty" in joined
    assert "rollback_verification must be non-empty" in joined
    assert "unresolved_deferrals[0].disposition must record a reviewer deferral disposition" in joined


def test_rejects_private_or_live_artifact_fields() -> None:
    packet = _packet()
    packet["auth_state"] = "not allowed"
    packet["reviewer_checklist_items"][0]["summary"] = "A live browser completed this review."

    result = validate_human_review_handoff_packet_v2(packet)

    assert not result.ok
    joined = "; ".join(result.errors)
    assert "auth_state is not allowed" in joined
    assert "contains unsafe live" in joined


def test_rejects_unsafe_handoff_content_classes() -> None:
    unsafe_cases = [
        ("private_fact", "owner name from DevHub"),
        ("raw_pdf", "%PDF raw body"),
        ("browser_artifact", "trace.zip"),
        ("note", "The permit will be approved."),
        ("note", "Finally submit the application."),
        ("note", "The raw crawl output is attached."),
        ("note", "This includes authenticated facts from the account."),
    ]

    for key, value in unsafe_cases:
        packet = _packet()
        packet[key] = value
        result = validate_human_review_handoff_packet_v2(packet)
        assert not result.ok, key


def test_rejects_active_mutation_flags_without_rejecting_negative_attestations() -> None:
    packet = _packet()
    assert validate_human_review_handoff_packet_v2(packet).ok

    for key in (
        "source_mutation_enabled",
        "surface_registry_mutation_enabled",
        "active_guardrail_mutation",
        "prompt_mutation_enabled",
        "active_monitoring_mutation",
        "release_state_mutation_enabled",
        "agent_state_mutation_enabled",
    ):
        broken = deepcopy(packet)
        broken[key] = True
        result = validate_human_review_handoff_packet_v2(broken)
        assert not result.ok, key
        assert "active source, surface-registry, guardrail, prompt, monitoring, release-state, or agent-state mutation flag" in "; ".join(result.errors)


def test_rejects_invalid_source_packets() -> None:
    proposal, replay = _source_packets()
    broken_proposal = deepcopy(proposal)
    broken_proposal["proposed_source_patch_rows"][0]["citations"] = []

    with pytest.raises(ValueError, match="invalid refresh implementation proposal v2"):
        build_human_review_handoff_packet_v2(broken_proposal, replay)

    broken_replay = deepcopy(replay)
    broken_replay["reviewer_owner_fields"] = []

    with pytest.raises(ValueError, match="invalid agent readiness replay packet v2"):
        build_human_review_handoff_packet_v2(proposal, broken_replay)
