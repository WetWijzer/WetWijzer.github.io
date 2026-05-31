from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from ppd.validation.post_recompile_release_decision_packet_v2 import (
    build_packet_from_replay,
    validate_packet,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures"
SOURCE_REPLAY_FIXTURE = FIXTURE_DIR / "post_recompile_agent_readiness_replay_v2" / "valid_manifest.json"
PACKET_FIXTURE = FIXTURE_DIR / "post_recompile_release_decision_packet_v2" / "valid_packet.json"


class PostRecompileReleaseDecisionPacketV2Tests(unittest.TestCase):
    def _source_replay(self) -> dict:
        return json.loads(SOURCE_REPLAY_FIXTURE.read_text(encoding="utf-8"))

    def _valid_packet(self) -> dict:
        return json.loads(PACKET_FIXTURE.read_text(encoding="utf-8"))

    def test_builds_expected_packet_from_approved_replay_fixture(self) -> None:
        packet = build_packet_from_replay(self._source_replay())

        self.assertEqual(packet, self._valid_packet())
        self.assertEqual(validate_packet(packet), [])
        self.assertEqual(
            [row["sequence"] for row in packet["decision_rows"]],
            [1, 2, 3, 4, 5, 6],
        )
        self.assertEqual(
            [row["release_decision"] for row in packet["decision_rows"]],
            [
                "ready-for-review",
                "hold-inactive",
                "ready-for-review",
                "ready-for-review",
                "hold-inactive",
                "hold-inactive",
            ],
        )

    def test_packet_contains_required_release_review_surfaces(self) -> None:
        packet = self._valid_packet()

        self.assertEqual(validate_packet(packet), [])
        self.assertEqual(packet["stale_source_hold_outcomes"][0]["outcome"], "manual-source-review-required")
        self.assertTrue(all(item["status"] == "pending-human-review" for item in packet["reviewer_signoff_placeholders"]))
        self.assertEqual(len(packet["rollback_references"]), len(packet["decision_rows"]))
        self.assertTrue(all("separate operator release decision" in item["note"] for item in packet["inactive_to_active_eligibility_notes"]))
        self.assertTrue(all("Do not upload, submit, certify, pay, schedule, cancel" in item["reminder"] for item in packet["blocked_consequential_action_reminders"]))

    def test_rejects_missing_or_unordered_decision_rows(self) -> None:
        packet = self._valid_packet()
        packet["decision_rows"][1]["sequence"] = 9

        errors = validate_packet(packet)

        self.assertIn("decision row release-decision-row-002 sequence must be 2", errors)

    def test_rejects_live_claims_mutation_flags_and_private_artifacts(self) -> None:
        packet = self._valid_packet()
        packet["guardrail_activation"] = True
        packet["decision_rows"][0]["decision_basis"] = "Executed in DevHub and release activated."
        packet["artifact"] = "private/raw/downloaded/result.pdf"

        errors = validate_packet(packet)

        self.assertIn("forbidden active flag at $.guardrail_activation", errors)
        self.assertTrue(any("forbidden live or official-action claim" in error for error in errors))
        self.assertTrue(any("forbidden private, browser, raw, or downloaded artifact" in error for error in errors))

    def test_rejects_source_replay_without_required_approved_evidence_types(self) -> None:
        replay = self._source_replay()
        replay["replay_cases"] = [case for case in replay["replay_cases"] if case["type"] != "reviewer_disposition"]

        with self.assertRaisesRegex(ValueError, "source replay missing case type: reviewer_disposition"):
            build_packet_from_replay(replay)

    def test_rejects_validation_command_drift(self) -> None:
        packet = copy.deepcopy(self._valid_packet())
        packet["offline_validation_commands"] = [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]]

        errors = validate_packet(packet)

        self.assertIn("offline_validation_commands must exactly match release decision packet v2 commands", errors)


if __name__ == "__main__":
    unittest.main()
