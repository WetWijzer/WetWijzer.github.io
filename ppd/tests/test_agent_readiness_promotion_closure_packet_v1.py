from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from ppd.agent_readiness_promotion_closure_packet_v1 import build_closure_packet, validate_closure_packet


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "agent_readiness_promotion_closure_packet_v1"


def _load(name: str) -> dict:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def _packet() -> dict:
    return build_closure_packet(
        _load("active_promotion_application_manifest_v1.json"),
        _load("post_promotion_guarded_agent_replay_result_ledger_v1.json"),
    )


def test_closure_packet_orders_decisions_and_keeps_side_effects_disabled() -> None:
    packet = _packet()

    assert packet["packet_version"] == "agent_readiness_promotion_closure_packet_v1"
    assert packet["source_manifest_id"] == "manifest_fixture_active_001"
    assert packet["source_replay_ledger_id"] == "replay_ledger_fixture_post_guarded_001"
    assert [row["application_id"] for row in packet["decision_rows"]] == [
        "agent_readiness_smoke",
        "agent_readiness_release_guard",
    ]
    assert packet["decision_rows"][0]["decision"] == "ready_for_reviewer_signoff"
    assert packet["decision_rows"][1]["decision"] == "no_go"
    assert packet["side_effects"] == {
        "promotion_changes_applied": False,
        "prompts_changed": False,
        "active_artifacts_mutated": False,
        "release_state_updated": False,
        "live_sources_crawled": False,
        "devhub_accessed": False,
        "official_actions_performed": False,
    }


def test_closure_packet_summarizes_evidence_mismatches_signoff_and_rollback() -> None:
    packet = _packet()

    summary = packet["evidence_coverage_summary"]
    assert summary["applications_total"] == 2
    assert summary["applications_ready_for_signoff"] == 1
    assert summary["applications_no_go"] == 1
    assert summary["missing_evidence_ids"] == ["ev_rollback_drill"]
    assert summary["coverage_ratio"] == 0.75
    assert summary["citations"] == [
        {"packet": "manifest_fixture_active_001", "section": "applications.required_evidence_ids"},
        {"packet": "replay_ledger_fixture_post_guarded_001", "section": "replay_results.evidence_ids"},
    ]

    assert packet["unresolved_mismatch_inventory"] == [
        {
            "application_id": "agent_readiness_release_guard",
            "observed_replay_status": "failed",
            "mismatch_codes": ["guarded_replay_policy_delta"],
            "missing_evidence_ids": ["ev_rollback_drill"],
        }
    ]
    assert packet["no_go_reasons"] == [
        {
            "application_id": "agent_readiness_release_guard",
            "reason_codes": [
                "unexpected_replay_status",
                "required_evidence_missing",
                "unresolved_replay_mismatch",
                "rollback_readiness_unconfirmed",
            ],
        }
    ]
    assert packet["reviewer_signoff_placeholders"][0] == {
        "application_id": "agent_readiness_smoke",
        "reviewer": "",
        "decision": "",
        "signed_at": "",
        "notes": "",
    }
    assert packet["rollback_readiness_confirmations"] == [
        {
            "application_id": "agent_readiness_smoke",
            "confirmed": True,
            "method": "fixture_rollback_plan_review",
            "evidence_id": "ev_rollback_plan",
        },
        {
            "application_id": "agent_readiness_release_guard",
            "confirmed": False,
            "method": "fixture_rollback_drill_required",
            "evidence_id": "ev_rollback_drill",
        },
    ]


class AgentReadinessPromotionClosurePacketV1ValidationTests(unittest.TestCase):
    def test_validator_accepts_builder_output(self) -> None:
        result = validate_closure_packet(_packet())
        self.assertTrue(result.ok, result.errors)

    def test_validator_rejects_missing_required_sections(self) -> None:
        packet = _packet()
        for field in (
            "decision_rows",
            "unresolved_mismatch_inventory",
            "reviewer_signoff_placeholders",
            "rollback_readiness_confirmations",
            "no_go_reasons",
        ):
            candidate = deepcopy(packet)
            candidate.pop(field)
            result = validate_closure_packet(candidate)
            self.assertFalse(result.ok)
            self.assertIn(field, "; ".join(result.errors))

    def test_validator_rejects_uncited_evidence_coverage_summary(self) -> None:
        packet = _packet()
        packet["evidence_coverage_summary"].pop("citations")
        result = validate_closure_packet(packet)
        self.assertFalse(result.ok)
        self.assertIn("evidence_coverage_summary.citations", "; ".join(result.errors))

    def test_validator_rejects_private_browser_raw_and_downloaded_artifacts(self) -> None:
        unsafe_fields = {
            "session_state": {"cookie": "secret"},
            "screenshot_path": "trace screenshot artifact",
            "har_file": "devhub.har",
            "auth_file": "auth state file",
            "raw_crawl_output": "raw crawl body",
            "downloaded_pdf": "downloaded document",
        }
        for key, value in unsafe_fields.items():
            packet = _packet()
            packet[key] = value
            result = validate_closure_packet(packet)
            self.assertFalse(result.ok, key)

    def test_validator_rejects_live_claims_guarantees_and_consequential_action_language(self) -> None:
        unsafe_values = [
            "live execution completed",
            "promotion completed",
            "release complete",
            "permit will be approved",
            "approval guaranteed",
            "submit the application",
            "upload the correction package",
            "schedule the inspection",
            "certify the permit filing",
            "cancel the permit",
        ]
        for value in unsafe_values:
            packet = _packet()
            packet["decision_rows"][0]["notes"] = value
            result = validate_closure_packet(packet)
            self.assertFalse(result.ok, value)

    def test_validator_rejects_active_mutation_flags(self) -> None:
        mutation_flags = (
            "active_artifact_mutation",
            "prompt_changes",
            "release_state_mutation",
            "fixture_mutation",
            "agent_state_mutation",
        )
        for flag in mutation_flags:
            packet = _packet()
            packet[flag] = True
            result = validate_closure_packet(packet)
            self.assertFalse(result.ok, flag)


if __name__ == "__main__":
    unittest.main()
