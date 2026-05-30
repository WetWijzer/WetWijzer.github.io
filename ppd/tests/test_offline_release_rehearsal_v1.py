from __future__ import annotations

import unittest
from pathlib import Path

from ppd.offline_release_rehearsal_v1 import (
    REQUIRED_PACKET_IDS,
    REQUIRED_STEP_IDS,
    OfflineReleaseRehearsalError,
    build_offline_release_rehearsal,
    load_offline_release_rehearsal_fixture,
    rehearsal_from_fixture,
    validate_offline_release_rehearsal_input,
    validate_offline_release_rehearsal_output,
)


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "offline_release_rehearsal_v1" / "rehearsal_input.json"


class OfflineReleaseRehearsalV1Test(unittest.TestCase):
    def test_builds_cited_fixture_only_release_rehearsal(self) -> None:
        rehearsal = rehearsal_from_fixture(FIXTURE_PATH)

        self.assertEqual(rehearsal["packet_type"], "ppd.offline_release_rehearsal.v1")
        self.assertTrue(rehearsal["fixture_only"])
        self.assertTrue(rehearsal["supervised"])
        self.assertEqual(tuple(rehearsal["consumed_packet_ids"]), REQUIRED_PACKET_IDS)
        self.assertEqual(
            tuple(step["step_id"] for step in rehearsal["cited_dry_run_release_steps"]),
            REQUIRED_STEP_IDS,
        )
        self.assertTrue(rehearsal["expected_fixture_only_artifacts"])
        self.assertTrue(all(artifact["fixture_only"] for artifact in rehearsal["expected_fixture_only_artifacts"]))
        self.assertTrue(rehearsal["manual_review_blockers"])
        self.assertTrue(all(blocker["requires_manual_review"] for blocker in rehearsal["manual_review_blockers"]))
        self.assertTrue(rehearsal["rollback_checkpoints"])
        self.assertIn(["python3", "-m", "py_compile", "ppd/offline_release_rehearsal_v1.py"], rehearsal["validation_command_inventory"])
        self.assertEqual(validate_offline_release_rehearsal_output(rehearsal), [])

    def test_fixture_loader_returns_input_packet(self) -> None:
        packet = load_offline_release_rehearsal_fixture(FIXTURE_PATH)

        self.assertEqual(packet["packet_type"], "ppd.offline_release_rehearsal_input.v1")
        self.assertEqual(validate_offline_release_rehearsal_input(packet), [])

    def test_rejects_missing_attestation(self) -> None:
        packet = load_offline_release_rehearsal_fixture(FIXTURE_PATH)
        packet["attestations"] = dict(packet["attestations"])
        packet["attestations"]["no_devhub"] = False

        with self.assertRaises(OfflineReleaseRehearsalError):
            build_offline_release_rehearsal(packet)

    def test_rejects_private_artifact_keys(self) -> None:
        packet = load_offline_release_rehearsal_fixture(FIXTURE_PATH)
        packet["consumed_packets"][0]["raw_body"] = "fixture text"

        problems = validate_offline_release_rehearsal_input(packet)

        self.assertTrue(any("forbidden private or raw artifact key" in problem for problem in problems))

    def test_rejects_consequential_action_text(self) -> None:
        packet = load_offline_release_rehearsal_fixture(FIXTURE_PATH)
        packet["consumed_packets"][0]["summary"] = "Operator may click submit after review."

        problems = validate_offline_release_rehearsal_input(packet)

        self.assertTrue(any("consequential official-action text" in problem for problem in problems))


if __name__ == "__main__":
    unittest.main()
