from pathlib import Path

import pytest

from ppd.devhub.manual_observation_reviewer_queue import (
    REQUIRED_ATTESTATIONS,
    ReviewerQueueError,
    build_reviewer_queue,
    build_reviewer_queue_from_files,
    load_json,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "devhub"
EVIDENCE_PACKET = FIXTURE_DIR / "manual_observation_evidence_intake_packet_v1.json"
RELEASE_GATE_MATRIX = FIXTURE_DIR / "release_gate_decision_matrix_v1.json"


def test_builds_cited_synthetic_read_only_observation_queue_items() -> None:
    queue = build_reviewer_queue_from_files(EVIDENCE_PACKET, RELEASE_GATE_MATRIX)

    assert [item["queue_item_id"] for item in queue] == [
        "devhub-manual-observation-review-v1-001",
        "devhub-manual-observation-review-v1-002",
    ]
    for item in queue:
        assert item["read_only_scope"] is True
        assert item["synthetic_fixture"] is True
        assert item["release_gate_decision"] == "manual_review_required_read_only"
        assert item["page_heading"]
        assert item["accessible_landmarks"]
        assert item["validation_message_expectations"]
        assert item["redaction_checks"]
        assert item["stop_before_action_gates"]
        assert item["reviewer_owner"] == "ppd-devhub-manual-reviewer"
        assert item["rollback_notes"]
        assert item["offline_validation_commands"]
        assert item["citations"]
        assert all(item["attestations"][name] is True for name in REQUIRED_ATTESTATIONS)


def test_queue_items_include_no_consequential_action_attestations() -> None:
    queue = build_reviewer_queue_from_files(EVIDENCE_PACKET, RELEASE_GATE_MATRIX)

    for item in queue:
        attestation_names = set(item["attestations"])
        assert set(REQUIRED_ATTESTATIONS).issubset(attestation_names)
        joined_gates = " ".join(item["stop_before_action_gates"]).lower()
        for blocked_word in ("login", "session", "screenshot", "trace", "har", "upload", "submit", "payment", "schedule"):
            assert blocked_word in joined_gates


def test_rejects_missing_release_gate_for_observation() -> None:
    packet = load_json(EVIDENCE_PACKET)
    matrix = load_json(RELEASE_GATE_MATRIX)
    packet["observations"][0]["surface_id"] = "missing-surface"

    with pytest.raises(ReviewerQueueError, match="missing release gate decision"):
        build_reviewer_queue(packet, matrix)


def test_rejects_failed_required_attestation() -> None:
    packet = load_json(EVIDENCE_PACKET)
    matrix = load_json(RELEASE_GATE_MATRIX)
    packet["observations"][0]["attestations"]["no_upload"] = False

    with pytest.raises(ReviewerQueueError, match="failed attestations"):
        build_reviewer_queue(packet, matrix)
