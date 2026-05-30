from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from ppd.agent_readiness.human_review_disposition_summary_v2 import (
    REQUIRED_ATTESTATIONS,
    build_human_review_disposition_summary_v2,
    build_human_review_disposition_summary_v2_from_fixture,
    validate_human_review_disposition_summary_v2,
)
from ppd.agent_readiness.human_review_handoff_packet_v2 import build_human_review_handoff_packet_v2_from_fixture

FIXTURE = Path(__file__).parent / "fixtures" / "human_review_disposition_summary_v2" / "source_packets.json"
HANDOFF_FIXTURE = Path(__file__).parent / "fixtures" / "human_review_handoff_packet_v2" / "source_packets.json"


def _packet() -> dict:
    return build_human_review_disposition_summary_v2_from_fixture(FIXTURE)


def test_builds_fixture_first_human_review_disposition_summary_v2() -> None:
    packet = _packet()
    result = validate_human_review_disposition_summary_v2(packet)

    assert result.ok, result.errors
    assert packet["packet_type"] == "ppd.human_review_disposition_summary.v2"
    assert packet["packet_version"] == 2
    assert packet["consumes"] == {
        "human_review_handoff_packet_v2": "ppd.human_review_handoff_packet.v2",
    }
    assert packet["attestations"] == {key: True for key in sorted(REQUIRED_ATTESTATIONS)}


def test_summary_contains_accepted_deferred_and_rejected_cited_decisions() -> None:
    packet = _packet()
    decisions = packet["checklist_decisions"]

    assert {row["decision"] for row in decisions} == {"accepted", "deferred", "rejected"}
    assert all(row["citations"] for row in decisions)
    assert all(row["reviewer_owner"] for row in decisions)
    assert all(row["dependency_after"] for row in decisions)
    assert all(row["rollback_note"] for row in decisions)
    assert all(row["validation_note"] for row in decisions)

    rejected = [row for row in decisions if row["decision"] == "rejected"]
    assert rejected
    assert all("official-action boundary" in row["rationale"] for row in rejected)


def test_summary_includes_required_disposition_rationales_and_deferral_next_tasks() -> None:
    packet = _packet()

    assert {row["decision"] for row in packet["disposition_rationales"]} == {"accepted", "deferred", "rejected"}
    for row in packet["disposition_rationales"]:
        assert row["rationale"]
        assert row["citations"]

    deferred_decisions = [row for row in packet["checklist_decisions"] if row["decision"] == "deferred"]
    deferred_follow_ups = [row for row in packet["implementation_follow_up_order"] if row["decision"] == "deferred"]
    assert deferred_decisions
    assert all(row["next_task_ref"] for row in deferred_decisions)
    assert all(row["next_task_ref"] for row in deferred_follow_ups)


def test_summary_includes_owner_fields_dependency_ordering_rollback_and_validation_notes() -> None:
    packet = _packet()

    assert packet["reviewer_owner_fields"]
    assert packet["dependency_ordering"]
    assert packet["implementation_follow_up_order"]
    assert packet["rollback_notes"]
    assert packet["validation_notes"]
    assert packet["offline_validation_commands"]

    dependency_ids = {row["dependency_id"] for row in packet["dependency_ordering"]}
    assert "validate-human-review-handoff-packet-v2" in dependency_ids
    assert "rollback-and-validation-readiness" in dependency_ids
    assert "rejected-official-action-boundary" in dependency_ids

    for field in ("reviewer_owner_fields", "dependency_ordering", "implementation_follow_up_order", "rollback_notes", "validation_notes"):
        for row in packet[field]:
            assert row["citations"], field


def test_builder_consumes_valid_handoff_packet_v2() -> None:
    handoff_packet = build_human_review_handoff_packet_v2_from_fixture(HANDOFF_FIXTURE)
    packet = build_human_review_disposition_summary_v2(handoff_packet)

    assert validate_human_review_disposition_summary_v2(packet).ok
    assert len(packet["checklist_decisions"]) >= len(handoff_packet["reviewer_checklist_items"])


def test_rejects_missing_citation_owner_dependency_and_notes() -> None:
    packet = _packet()
    broken = deepcopy(packet)
    broken["checklist_decisions"][0]["citations"] = []
    broken["checklist_decisions"][0]["reviewer_owner"] = ""
    broken["checklist_decisions"][0]["dependency_after"] = []
    broken["checklist_decisions"][0]["rollback_note"] = ""
    broken["checklist_decisions"][0]["validation_note"] = ""

    result = validate_human_review_disposition_summary_v2(broken)

    assert not result.ok
    joined = "; ".join(result.errors)
    assert "checklist_decisions[0].citations must be non-empty" in joined
    assert "checklist_decisions[0].reviewer_owner must be present" in joined
    assert "checklist_decisions[0].dependency_after must be non-empty" in joined
    assert "checklist_decisions[0].rollback_note must be present" in joined
    assert "checklist_decisions[0].validation_note must be present" in joined


def test_rejects_missing_required_decision_classes() -> None:
    packet = _packet()
    broken = deepcopy(packet)
    broken["checklist_decisions"] = [row for row in broken["checklist_decisions"] if row["decision"] != "rejected"]

    result = validate_human_review_disposition_summary_v2(broken)

    assert not result.ok
    assert "checklist_decisions must include accepted, deferred, and rejected decisions" in "; ".join(result.errors)


def test_rejects_missing_disposition_rationales() -> None:
    packet = _packet()
    broken = deepcopy(packet)
    broken["disposition_rationales"] = [row for row in broken["disposition_rationales"] if row["decision"] != "deferred"]
    broken["disposition_rationales"][0]["rationale"] = ""
    broken["disposition_rationales"][1]["citations"] = []

    result = validate_human_review_disposition_summary_v2(broken)

    assert not result.ok
    joined = "; ".join(result.errors)
    assert "disposition_rationales must include deferred rationale" in joined
    assert "disposition_rationales[accepted].rationale must be present" in joined
    assert "disposition_rationales[rejected].citations must be non-empty" in joined


def test_rejects_deferred_dispositions_without_next_task_refs() -> None:
    packet = _packet()
    broken = deepcopy(packet)
    deferred_index = next(index for index, row in enumerate(broken["checklist_decisions"]) if row["decision"] == "deferred")
    broken["checklist_decisions"][deferred_index].pop("next_task_ref", None)
    follow_up_index = next(index for index, row in enumerate(broken["implementation_follow_up_order"]) if row["decision"] == "deferred")
    broken["implementation_follow_up_order"][follow_up_index].pop("next_task_ref", None)

    result = validate_human_review_disposition_summary_v2(broken)

    assert not result.ok
    joined = "; ".join(result.errors)
    assert f"checklist_decisions[{deferred_index}].next_task_ref must be present for deferred dispositions" in joined
    assert f"implementation_follow_up_order[{follow_up_index}].next_task_ref must be present for deferred dispositions" in joined


def test_rejects_missing_rollup_sections_and_attestations() -> None:
    packet = _packet()
    broken = deepcopy(packet)
    broken["reviewer_owner_fields"] = []
    broken["dependency_ordering"] = []
    broken["rollback_notes"] = []
    broken["validation_notes"] = []
    broken["attestations"]["no_auth"] = False

    result = validate_human_review_disposition_summary_v2(broken)

    assert not result.ok
    joined = "; ".join(result.errors)
    assert "reviewer_owner_fields must be non-empty" in joined
    assert "dependency_ordering must be non-empty" in joined
    assert "rollback_notes must be non-empty" in joined
    assert "validation_notes must be non-empty" in joined
    assert "attestations.no_auth must be true" in joined


def test_rejects_unknown_dependency_reference() -> None:
    packet = _packet()
    broken = deepcopy(packet)
    broken["checklist_decisions"][0]["dependency_after"] = ["missing-dependency"]

    result = validate_human_review_disposition_summary_v2(broken)

    assert not result.ok
    assert "checklist_decisions[0].dependency_after references unknown dependency" in "; ".join(result.errors)


def test_rejects_private_live_artifact_official_action_and_mutation_content() -> None:
    unsafe_cases = [
        ("auth_state", "not allowed"),
        ("private_fact", "not allowed"),
        ("raw_pdf", "%PDF"),
        ("pdf_artifact", "public-form.pdf"),
        ("crawl_output", "body.html"),
        ("browser_artifact", "trace.zip"),
        ("session_artifact", "storage-state.json"),
        ("note", "A live browser completed this review."),
        ("note", "We ran a live crawl for this summary."),
        ("note", "The permit will be approved."),
        ("note", "This legal outcome is guaranteed."),
        ("note", "Finally submit the application."),
        ("note", "Click the submit button."),
        ("note", "Upload corrections in DevHub."),
        ("note", "The raw crawl output is attached."),
        ("note", "This includes authenticated facts from the account."),
        ("active_release_state_mutation", True),
        ("active_source", "enabled"),
        ("active_surface_registry", {"write": True}),
        ("active_guardrail", ["change"]),
        ("active_prompt", True),
        ("active_monitoring", True),
        ("active_agent_state", True),
    ]

    for key, value in unsafe_cases:
        packet = _packet()
        packet[key] = value
        result = validate_human_review_disposition_summary_v2(packet)
        assert not result.ok, key


def test_rejects_invalid_handoff_packet_before_summary_build() -> None:
    handoff_packet = build_human_review_handoff_packet_v2_from_fixture(HANDOFF_FIXTURE)
    handoff_packet["reviewer_checklist_items"][0]["citations"] = []

    with pytest.raises(ValueError, match="invalid human review handoff packet v2"):
        build_human_review_disposition_summary_v2(handoff_packet)
