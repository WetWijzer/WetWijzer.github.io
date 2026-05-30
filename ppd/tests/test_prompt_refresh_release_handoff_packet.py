from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from ppd.agent_readiness.prompt_refresh_release_handoff_packet import (
    PACKET_TYPE,
    PromptRefreshReleaseHandoffPacketError,
    build_prompt_refresh_release_handoff_packet,
    validate_prompt_refresh_release_handoff_packet,
)


_FIXTURE_PATH = Path(__file__).parent / "fixtures" / "agent_readiness" / "prompt_refresh_release_handoff_packet.json"


class PromptRefreshReleaseHandoffPacketTests(unittest.TestCase):
    def load_fixture(self) -> dict:
        return json.loads(_FIXTURE_PATH.read_text(encoding="utf-8"))

    def test_builds_candidate_prompt_version_manifest_from_source_packets(self) -> None:
        fixture = self.load_fixture()
        packet = build_prompt_refresh_release_handoff_packet(
            fixture["acceptance_packet"],
            fixture["consumer_handoff_packet"],
            candidate_prompt_version_id="candidate-prompt-version-fixture-v1",
        )

        self.assertEqual(packet["packet_type"], PACKET_TYPE)
        self.assertTrue(packet["fixture_first"])
        self.assertEqual(packet["candidate_prompt_version_manifest"]["candidate_prompt_version_id"], "candidate-prompt-version-fixture-v1")
        self.assertEqual(packet["candidate_prompt_version_manifest"]["accepted_decision_ids"], ["accept-safe-refusal-copy"])
        self.assertEqual(
            packet["guardrail_bundle_compatibility_notes"][0]["guardrail_bundle_id"],
            "guardrail-bundle-single-pdf-process-v1",
        )
        self.assertTrue(all(packet["attestations"].values()))
        self.assertTrue(validate_prompt_refresh_release_handoff_packet(packet).valid)

    def test_rejects_missing_no_mutation_attestation(self) -> None:
        fixture = self.load_fixture()
        packet = build_prompt_refresh_release_handoff_packet(fixture["acceptance_packet"], fixture["consumer_handoff_packet"])
        packet["attestations"] = dict(packet["attestations"])
        packet["attestations"]["no_guardrail_mutation"] = False

        result = validate_prompt_refresh_release_handoff_packet(packet)

        self.assertFalse(result.valid)
        self.assertIn("attestations.no_guardrail_mutation must be true", result.problems)

    def test_rejects_invalid_source_packets_before_handoff_build(self) -> None:
        fixture = self.load_fixture()
        invalid_acceptance = copy.deepcopy(fixture["acceptance_packet"])
        invalid_acceptance["fixture_first"] = False

        with self.assertRaises(PromptRefreshReleaseHandoffPacketError):
            build_prompt_refresh_release_handoff_packet(invalid_acceptance, fixture["consumer_handoff_packet"])


if __name__ == "__main__":
    unittest.main()
