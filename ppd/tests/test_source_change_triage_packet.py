from __future__ import annotations

import json
from pathlib import Path

from ppd.source_change_triage import PACKET_SCHEMA_VERSION, build_triage_packet

FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "source_change_triage"
    / "freshness_queue_outcomes_v1.json"
)


def _load_fixture() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def test_fixture_first_triage_packet_has_expected_statuses() -> None:
    packet = build_triage_packet(_load_fixture(), fixture_name=FIXTURE_PATH.name)

    assert packet["schema_version"] == PACKET_SCHEMA_VERSION
    assert packet["summary_counts"] == {
        "changed": 1,
        "unchanged": 1,
        "needs-review": 1,
        "total": 3,
    }

    rows_by_source = {row["source_id"]: row for row in packet["rows"]}
    assert rows_by_source["ppd-devhub-faq"]["triage_status"] == "changed"
    assert rows_by_source["ppd-submit-plans-online"]["triage_status"] == "unchanged"
    assert rows_by_source["ppd-fee-payment-guide"]["triage_status"] == "needs-review"


def test_packet_preserves_impacted_references_and_citation_checks() -> None:
    packet = build_triage_packet(_load_fixture(), fixture_name=FIXTURE_PATH.name)
    rows_by_source = {row["source_id"]: row for row in packet["rows"]}

    changed = rows_by_source["ppd-devhub-faq"]
    assert changed["impacted_references"]["requirement_ids"] == [
        "req-devhub-account",
        "req-upload-corrections-gated",
    ]
    assert changed["impacted_references"]["process_ids"] == [
        "process-corrections",
        "process-devhub-account-setup",
    ]
    assert changed["citation_preservation_check"]["status"] == "passed"

    needs_review = rows_by_source["ppd-fee-payment-guide"]
    assert needs_review["citation_preservation_check"]["status"] == "failed"
    assert needs_review["citation_preservation_check"]["missing_evidence_ids"] == [
        "evidence-final-submit"
    ]
    assert "Human review required" in needs_review["blocked_promotion_explanation"]
    assert "retain the previously validated" in needs_review["rollback_notes"]


def test_packet_blocks_forbidden_side_effects_and_includes_replay_commands() -> None:
    packet = build_triage_packet(_load_fixture(), fixture_name=FIXTURE_PATH.name)

    assert packet["safety_invariants"] == {
        "live_source_access": False,
        "raw_body_persisted": False,
        "public_artifact_promotion": False,
        "official_action_claims": False,
    }
    assert packet["offline_validation_replay_commands"] == [
        ["python3", "-m", "pytest", "ppd/tests/test_source_change_triage_packet.py"],
        ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
    ]

    for row in packet["rows"]:
        assert row["safety_checks"] == {
            "live_source_access": False,
            "raw_body_persisted": False,
            "public_artifact_promotion_requested": False,
            "official_action_claimed": False,
        }
        assert row["blocked_promotion_explanation"].startswith("Promotion blocked:")
