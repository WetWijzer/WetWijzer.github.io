from __future__ import annotations

import copy
import unittest
from pathlib import Path

from ppd.agent_readiness.supervised_offline_release_rehearsal_v1 import (
    SupervisedOfflineReleaseRehearsalV1Error,
    build_supervised_offline_release_rehearsal,
    load_supervised_offline_release_rehearsal_fixture,
    validate_supervised_offline_release_rehearsal_v1,
)


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "supervised_offline_release_rehearsal_v1" / "source_packet.json"


class SupervisedOfflineReleaseRehearsalV1Test(unittest.TestCase):
    def _packet(self) -> dict:
        return load_supervised_offline_release_rehearsal_fixture(FIXTURE_PATH)

    def test_accepts_valid_fixture_packet(self) -> None:
        packet = self._packet()

        self.assertEqual(validate_supervised_offline_release_rehearsal_v1(packet), [])
        self.assertEqual(build_supervised_offline_release_rehearsal(packet), packet)

    def test_rejects_uncited_step(self) -> None:
        packet = self._packet()
        packet["rehearsal_steps"][0]["citations"] = []

        problems = validate_supervised_offline_release_rehearsal_v1(packet)

        self.assertTrue(any("rehearsal_steps[0].citations" in problem for problem in problems))

    def test_rejects_missing_required_sections(self) -> None:
        packet = self._packet()
        for key in ("blocker_handling", "expected_fixture_artifacts", "rollback_checkpoints", "validation_command_inventory"):
            candidate = copy.deepcopy(packet)
            candidate.pop(key)
            problems = validate_supervised_offline_release_rehearsal_v1(candidate)
            self.assertTrue(problems, key)

    def test_rejects_private_raw_and_live_content(self) -> None:
        packet = self._packet()
        packet["raw_pdf"] = "fixture text"
        packet["rehearsal_steps"][0]["instruction"] = "Live execution completed and release promoted to production."

        problems = validate_supervised_offline_release_rehearsal_v1(packet)

        self.assertTrue(any("forbidden private" in problem for problem in problems))
        self.assertTrue(any("live execution or promotion claim" in problem for problem in problems))

    def test_rejects_guarantees_consequential_actions_and_mutations(self) -> None:
        packet = self._packet()
        packet["rehearsal_steps"][0]["instruction"] = "Submit the permit because approval is guaranteed."
        packet["mutation_flags"] = {"active_guardrail_mutation": True}

        problems = validate_supervised_offline_release_rehearsal_v1(packet)

        self.assertTrue(any("outcome guarantee" in problem for problem in problems))
        self.assertTrue(any("consequential action" in problem for problem in problems))
        self.assertTrue(any("must not be true" in problem for problem in problems))

    def test_build_raises_on_invalid_packet(self) -> None:
        packet = self._packet()
        packet["validation_command_inventory"] = []

        with self.assertRaises(SupervisedOfflineReleaseRehearsalV1Error):
            build_supervised_offline_release_rehearsal(packet)


if __name__ == "__main__":
    unittest.main()
