from __future__ import annotations

import json
from pathlib import Path

from ppd.offline_release_reviewer_disposition_intake_v2 import build_disposition_intake_packet


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "offline_release_reviewer_disposition_intake_v2"


def test_builds_ordered_reviewer_decision_rows_without_side_effect_flags() -> None:
    gate = json.loads((FIXTURE_DIR / "gate_v2.json").read_text(encoding="utf-8"))

    packet = build_disposition_intake_packet(gate)

    assert packet["schema_version"] == "ppd.offline_release_reviewer_disposition_intake.v2"
    assert packet["offline_only"] is True
    assert packet["official_action"] is False
    assert packet["fixture_changes_applied"] is False
    assert packet["active_artifacts_mutated"] is False
    assert packet["release_state_updated"] is False
    assert packet["live_sources_crawled"] is False
    assert packet["devhub_accessed"] is False

    rows = packet["reviewer_decision_rows"]
    assert [row["source_gate_id"] for row in rows] == ["evidence", "rollback"]
    assert [row["decision_row_order"] for row in rows] == [1, 2]
    assert all(row["reviewer_decision_placeholder"] == "pending_reviewer_decision" for row in rows)
    assert all(row["no_go_reason_placeholder"] == "" for row in rows)


def test_carries_forward_blockers_and_acknowledgement_placeholders() -> None:
    gate = json.loads((FIXTURE_DIR / "gate_v2.json").read_text(encoding="utf-8"))

    packet = build_disposition_intake_packet(gate)

    blockers = packet["unresolved_blockers_carried_forward"]
    assert blockers == [
        {
            "carry_forward_order": 1,
            "blocker_id": "blocker-001",
            "severity": "high",
            "owner": "release_manager",
            "description": "Final no-go rationale has not been selected.",
            "required_resolution": "Reviewer must either clear the blocker or enter a no-go reason.",
            "carried_forward": True,
        }
    ]

    first_row = packet["reviewer_decision_rows"][0]
    assert first_row["unresolved_blocker_ids"] == ["blocker-001"]
    for key in (
        "evidence_summary_acknowledgement",
        "rollback_readiness_acknowledgement",
        "validation_replay_acknowledgement",
    ):
        acknowledgement = first_row[key]
        assert acknowledgement["acknowledgement_required"] is True
        assert acknowledgement["acknowledged"] is False
        assert isinstance(acknowledgement["summary"], str)
        assert isinstance(acknowledgement["evidence_ids"], list)
