import json
import unittest
from pathlib import Path

from ppd.agent_readiness.agent_regression_refresh_packet import (
    REQUIRED_ATTESTATIONS,
    build_agent_regression_refresh_packet,
    load_source_packets,
    validate_agent_regression_refresh_packet,
)


FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "agent_regression_refresh_packet"
    / "source_packets.json"
)


class AgentRegressionRefreshPacketTest(unittest.TestCase):
    def setUp(self):
        self.source_packets = load_source_packets(FIXTURE_PATH)
        self.packet = build_agent_regression_refresh_packet(self.source_packets)

    def test_consumes_three_named_source_packets(self):
        self.assertEqual(
            self.packet["source_packet_ids"],
            [
                "process-guardrail-refresh-candidate-20260529",
                "agent-freshness-regression-acceptance-20260529",
                "agent-consumer-post-release-smoke-20260529",
            ],
        )

    def test_builds_cited_offline_user_scenarios(self):
        scenarios = self.packet["offline_user_scenarios"]
        self.assertEqual(len(scenarios), 2)
        for scenario in scenarios:
            self.assertIn("Portland", scenario["user_scenario"])
            self.assertEqual(len(scenario["cited_offline_evidence"]), 3)
            self.assertEqual(
                scenario["source_packet_ids"],
                [citation["source_packet_id"] for citation in scenario["cited_offline_evidence"]],
            )
            for citation in scenario["cited_offline_evidence"]:
                self.assertTrue(citation["source_packet_id"])
                self.assertTrue(citation["locator"])

    def test_includes_missing_fact_refusal_and_boundary_messages(self):
        for scenario in self.packet["offline_user_scenarios"]:
            self.assertTrue(scenario["expected_missing_fact_prompts"])
            self.assertIn("missing", scenario["refusal_explanation"].lower())
            self.assertIn("Draft previews", scenario["reversible_draft_preview_boundary"])
            self.assertIn("Blocked", scenario["blocked_consequential_action_message"])
            self.assertTrue(scenario["reviewer_owner"])

    def test_attests_no_live_or_mutating_dependencies(self):
        self.assertEqual(
            self.packet["attestations"],
            {key: True for key in REQUIRED_ATTESTATIONS},
        )

    def test_packet_is_json_serializable_and_valid(self):
        encoded = json.dumps(self.packet, sort_keys=True)
        decoded = json.loads(encoded)
        validate_agent_regression_refresh_packet(decoded)

    def test_missing_source_packet_is_rejected(self):
        incomplete = dict(self.source_packets)
        incomplete.pop("agent_consumer_post_release_smoke_transcript_packet")
        with self.assertRaisesRegex(ValueError, "missing source packet"):
            build_agent_regression_refresh_packet(incomplete)


if __name__ == "__main__":
    unittest.main()
