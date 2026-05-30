from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from ppd.offline_release_reviewer_disposition_packet_v2 import (
    PACKET_VERSION,
    build_offline_release_reviewer_disposition_packet_v2,
    build_offline_release_reviewer_disposition_packet_v2_from_fixture,
    validate_offline_release_reviewer_disposition_packet_v2,
)

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "offline_release_reviewer_disposition_packet_v2" / "release_rehearsal_gate_v2.json"


def _packet() -> dict:
    return build_offline_release_reviewer_disposition_packet_v2_from_fixture(FIXTURE_PATH)


def test_builds_ordered_approve_hold_reject_decisions_from_rehearsal_gate() -> None:
    packet = _packet()

    assert packet["packet_version"] == PACKET_VERSION
    assert packet["consumes"]["offline_release_rehearsal_gate_v2"] == "release_rehearsal_gate_v2"
    assert packet["decision_order"] == ["approve", "hold", "reject"]
    assert [row["artifact_id"] for row in packet["reviewer_decisions"]] == [
        "inactive-preview-alpha",
        "inactive-preview-beta",
        "inactive-preview-gamma",
    ]
    assert [row["reviewer_decision"] for row in packet["reviewer_decisions"]] == ["approve", "hold", "reject"]
    assert validate_offline_release_reviewer_disposition_packet_v2(packet).ok


def test_includes_evidence_refs_transcript_placeholders_rollbacks_risks_and_commands() -> None:
    packet = _packet()

    assert len(packet["evidence_bundle_references"]) == 3
    assert all(ref["citation_refs"] for ref in packet["evidence_bundle_references"])
    assert all(ref["contains_private_or_raw_artifacts"] is False for ref in packet["evidence_bundle_references"])
    assert all(
        row["validation_transcript_review_placeholder"]["status"] == "pending_human_review"
        for row in packet["reviewer_decisions"]
    )
    assert all(
        row["validation_transcript_review_placeholder"]["no_transcript_artifact_stored"] is True
        for row in packet["reviewer_decisions"]
    )
    assert all(ref["ready_for_future_manual_release_review"] is True for ref in packet["rollback_readiness_confirmations"])
    assert all(ref["active_release_state_changed"] is False for ref in packet["rollback_readiness_confirmations"])
    assert {note["reviewer_decision"] for note in packet["unresolved_risk_notes"]} == {"hold", "reject"}
    assert ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"] in packet["exact_offline_validation_commands"]
    assert ["python3", "-m", "pytest", "ppd/tests/test_offline_release_reviewer_disposition_packet_v2.py"] in packet["exact_offline_validation_commands"]


def test_attests_offline_only_no_devhub_no_private_artifacts_no_release_state_change() -> None:
    packet = _packet()

    assert packet["attestations"] == {
        "fixture_first": True,
        "no_live_network_access": True,
        "no_devhub_opened": True,
        "no_private_artifacts": True,
        "no_official_actions": True,
        "no_active_promotion": True,
        "no_release_state_change": True,
    }


def test_rejects_missing_required_review_sections_and_order_drift() -> None:
    packet = _packet()
    broken = deepcopy(packet)
    broken["decision_order"] = ["approve", "reject", "hold"]
    broken["reviewer_decisions"][1]["validation_transcript_review_placeholder"] = {}
    broken["evidence_bundle_references"] = []
    broken["rollback_readiness_confirmations"] = []
    broken["unresolved_risk_notes"] = []
    broken["exact_offline_validation_commands"] = []

    result = validate_offline_release_reviewer_disposition_packet_v2(broken)

    assert not result.ok
    joined = "; ".join(result.errors)
    assert "decision_order must exactly match reviewer_decisions order" in joined
    assert "evidence_bundle_references must be non-empty" in joined
    assert "rollback_readiness_confirmations must be non-empty" in joined
    assert "unresolved_risk_notes must be non-empty" in joined
    assert "exact_offline_validation_commands must be a non-empty list of command lists" in joined
    assert "validation_transcript_review_placeholder.placeholder_id must be present" in joined


def test_rejects_missing_evidence_rollback_and_unresolved_risk_coverage() -> None:
    packet = _packet()
    broken = deepcopy(packet)
    broken["reviewer_decisions"][1]["evidence_bundle_ref"] = "missing-evidence-ref"
    broken["reviewer_decisions"][2]["rollback_readiness_ref"] = "missing-rollback-ref"
    broken["unresolved_risk_notes"] = [note for note in broken["unresolved_risk_notes"] if note["reviewer_decision"] != "reject"]

    result = validate_offline_release_reviewer_disposition_packet_v2(broken)

    assert not result.ok
    joined = "; ".join(result.errors)
    assert "reviewer_decisions[1].evidence_bundle_ref must reference evidence_bundle_references" in joined
    assert "reviewer_decisions[2].rollback_readiness_ref must reference rollback_readiness_confirmations" in joined
    assert "unresolved_risk_notes must cover every held or rejected reviewer decision" in joined


def test_rejects_wrong_input_packet_version() -> None:
    with pytest.raises(ValueError, match="requires release_rehearsal_gate_v2 input"):
        build_offline_release_reviewer_disposition_packet_v2({"packet_version": "other", "gate_rows": []})


def test_rejects_live_devhub_private_raw_official_promotion_and_release_state_material() -> None:
    unsafe_cases = [
        ("auth_state", "state.json"),
        ("authenticated_artifact", "account value"),
        ("browser_artifact", "trace.zip"),
        ("devhub_session", "session"),
        ("downloaded_document", "document.pdf"),
        ("private_artifact", "artifact.json"),
        ("raw_crawl_output", "body html"),
        ("raw_pdf", "%PDF"),
        ("session_state", "state"),
        ("storage_state", "storage.json"),
        ("trace_file", "trace.zip"),
        ("active_promotion", True),
        ("promotion_executed", True),
        ("release_state_changed", True),
        ("official_action_performed", True),
        ("live_network_access", True),
        ("note", "active promotion completed"),
        ("note", "opened DevHub for review"),
        ("note", "submit the permit application"),
        ("note", "approval guaranteed"),
    ]

    for key, value in unsafe_cases:
        packet = _packet()
        packet[key] = value
        result = validate_offline_release_reviewer_disposition_packet_v2(packet)
        assert not result.ok, key
