import json
from pathlib import Path

from ppd.promotion.active_preflight import build_active_promotion_preflight


def test_active_promotion_preflight_blocks_mutations_and_preserves_release_state():
    fixture_path = Path(__file__).parent / "fixtures" / "promotion" / "inactive_sandbox_rehearsal_packet_v1.json"
    packet = json.loads(fixture_path.read_text(encoding="utf-8"))

    report = build_active_promotion_preflight(packet)

    assert report["report_version"] == "active_promotion_preflight_gate_v1"
    assert report["source_packet_id"] == "inactive-sandbox-rehearsal-20260530-819"
    assert report["final_decision"] == "NO_GO_ACTIVE_MUTATION_BLOCKED"
    assert report["rollback_readiness_summary"]["release_state_before"] == "fixture-only-inactive"
    assert report["rollback_readiness_summary"]["release_state_after"] == "fixture-only-inactive"

    flags = report["nonmutation_flags"]
    assert flags == {
        "fixture_promotion_applied": False,
        "active_artifacts_mutated": False,
        "prompts_changed": False,
        "release_state_updated": False,
        "live_sources_crawled": False,
        "devhub_accessed": False,
        "official_actions_performed": False,
    }

    blocked_actions = {
        item["blocked_action"]
        for item in report["active_mutation_blocker_inventory"]
        if item["status"] == "BLOCKED"
    }
    assert blocked_actions == {
        "fixture_promotion_apply",
        "active_artifact_write",
        "release_state_update",
        "prompt_change",
        "live_source_crawl",
        "devhub_access",
        "official_action",
    }


def test_active_promotion_preflight_has_human_placeholders_and_replay_checks():
    fixture_path = Path(__file__).parent / "fixtures" / "promotion" / "inactive_sandbox_rehearsal_packet_v1.json"
    packet = json.loads(fixture_path.read_text(encoding="utf-8"))

    report = build_active_promotion_preflight(packet)

    approvals = report["human_approval_placeholders"]
    assert [approval["status"] for approval in approvals] == [
        "PENDING_HUMAN_REVIEW",
        "PENDING_HUMAN_REVIEW",
    ]

    replay_statuses = {item["check"]: item["status"] for item in report["validation_replay_checklist"]}
    assert replay_statuses == {
        "packet_schema_loaded_from_fixture": "PASS",
        "inactive_rehearsal_status_verified": "PASS",
        "planned_active_mutations_blocked": "PASS",
        "validation_evidence_replayed": "PASS",
        "rollback_inputs_present": "PASS",
        "release_state_left_unchanged": "PASS",
    }

    mutation_row = next(row for row in report["go_no_go_rows"] if row["gate"] == "active mutation boundary")
    assert mutation_row["decision"] == "BLOCKED"
    assert mutation_row["human_approval_required"] is True
