from __future__ import annotations

import json
from pathlib import Path

import pytest

from ppd.public_source_refresh_reviewer_queue import (
    QueueInputError,
    build_public_source_refresh_reviewer_queue,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "public_source_refresh_reviewer_queue"


def _load_fixture(name: str) -> dict:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def test_builds_metadata_only_queue_items_from_fixtures() -> None:
    evidence_packet = _load_fixture("public_source_refresh_evidence_intake_packet_v1.json")
    decision_matrix = _load_fixture("release_gate_decision_matrix_v1.json")

    queue = build_public_source_refresh_reviewer_queue(evidence_packet, decision_matrix)

    assert queue["queue_version"] == "public_source_refresh_reviewer_queue_v1"
    assert queue["metadata_only"] is True
    assert queue["attestations"] == {
        "no_recrawl": True,
        "no_download": True,
        "no_processor": True,
        "no_raw_body": True,
        "no_registry_mutation": True,
    }
    assert len(queue["items"]) == 2

    first = queue["items"][0]
    assert first["queue_item_id"] == "psrrq-v1-portland-bds-title-33"
    assert first["source_id"] == "portland-bds-title-33"
    assert first["requirement_ids"] == ["PCC-33.110.215", "PCC-33.110.220"]
    assert first["reviewer_owner"] == "ppd-zoning-reviewer"
    assert first["public_page_title_check"] == {
        "expected_title": "Title 33 Planning and Zoning",
        "observed_title": "Title 33 Planning and Zoning",
        "status": "matches_fixture_metadata",
    }
    assert first["visible_updated_date_review"] == {
        "visible": True,
        "observed_text": "Updated May 15, 2026",
        "status": "visible_in_fixture_metadata",
    }
    assert first["affected_source_ids"] == ["portland-bds-title-33"]
    assert first["affected_requirement_ids"] == ["PCC-33.110.215", "PCC-33.110.220"]
    assert first["defer_reason"] is None
    assert "current public corpus metadata" in first["rollback_notes"]
    assert first["offline_validation_commands"][0] == [
        "python3",
        "-m",
        "py_compile",
        "ppd/public_source_refresh_reviewer_queue.py",
    ]
    assert first["citations"][0]["kind"] == "public_source_refresh_evidence_intake_packet_v1"
    assert first["citations"][1]["kind"] == "release_gate_decision_matrix_v1"
    assert first["attestations"] == queue["attestations"]

    second = queue["items"][1]
    assert second["source_id"] == "portland-transportation-trn-10"
    assert second["review_status"] == "deferred"
    assert second["public_page_title_check"]["status"] == "needs_review"
    assert second["visible_updated_date_review"]["status"] == "needs_review"
    assert second["defer_reason"] == "Fixture metadata lacks a visible updated date and title match."


def test_rejects_raw_body_fields() -> None:
    evidence_packet = _load_fixture("public_source_refresh_evidence_intake_packet_v1.json")
    decision_matrix = _load_fixture("release_gate_decision_matrix_v1.json")
    evidence_packet["sources"][0]["evidence"]["raw_body"] = "not allowed"

    with pytest.raises(QueueInputError, match="raw body field is not allowed"):
        build_public_source_refresh_reviewer_queue(evidence_packet, decision_matrix)
