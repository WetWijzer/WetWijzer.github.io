import copy
import json
import unittest
from pathlib import Path

from ppd.agent_readiness.agent_prompt_refresh_candidate_packet import (
    REQUIRED_ATTESTATIONS,
    AgentPromptRefreshCandidatePacketError,
    build_agent_prompt_refresh_candidate_packet,
    load_source_packets,
    validate_agent_prompt_refresh_candidate_packet,
)


FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "agent_prompt_refresh_candidate_packet"
    / "source_packets.json"
)


class AgentPromptRefreshCandidatePacketTest(unittest.TestCase):
    def setUp(self):
        self.source_packets = load_source_packets(FIXTURE_PATH)
        self.packet = build_agent_prompt_refresh_candidate_packet(self.source_packets)

    def test_consumes_three_named_source_packets(self):
        self.assertEqual(
            self.packet["source_packet_ids"],
            {
                "guardrail_refresh_regression_review_packet": "guardrail-refresh-regression-review-20260529-fixture-first",
                "agent_regression_refresh_packet": "agent-regression-refresh-20260529-fixture-first",
                "agent_consumer_release_handoff_packet": "release-consumer-handoff-20260529-fixture-first",
            },
        )

    def test_builds_cited_prompt_change_candidates(self):
        changes = self.packet["prompt_change_candidates"]
        self.assertGreaterEqual(len(changes), 5)
        for change in changes:
            self.assertEqual(change["status"], "candidate_only")
            self.assertTrue(change["candidate_prompt_text"])
            self.assertTrue(change["source_evidence_ids"])
            self.assertTrue(change["reviewer_owner"])

    def test_includes_safe_read_only_scenarios_and_blocked_language(self):
        scenarios = self.packet["supported_safe_read_only_scenarios"]
        self.assertEqual(len(scenarios), 2)
        for scenario in scenarios:
            self.assertEqual(scenario["automation_boundary"], "safe_read_only_or_reversible_draft_only")
            self.assertTrue(scenario["source_evidence_ids"])
            self.assertIn("Blocked", scenario["blocked_follow_up"])

        blocked_messages = [row["message"] for row in self.packet["blocked_consequential_action_language"]]
        self.assertTrue(any("submit" in message.lower() for message in blocked_messages))
        self.assertTrue(any("payment" in message.lower() or "pay" in message.lower() for message in blocked_messages))

    def test_includes_rollback_reviewers_validation_and_attestations(self):
        self.assertTrue(self.packet["rollback_notes"])
        self.assertTrue(self.packet["reviewer_owner_fields"])
        self.assertIn(["python3", "ppd/daemon/ppd_daemon.py", "--self-test"], self.packet["offline_validation_commands"])
        self.assertIn(
            ["python3", "-m", "unittest", "ppd.tests.test_agent_prompt_refresh_candidate_packet"],
            self.packet["offline_validation_commands"],
        )
        self.assertEqual(self.packet["attestations"], {key: True for key in REQUIRED_ATTESTATIONS})

    def test_packet_is_json_serializable_and_valid(self):
        encoded = json.dumps(self.packet, sort_keys=True)
        decoded = json.loads(encoded)
        validate_agent_prompt_refresh_candidate_packet(decoded)

    def test_missing_source_packet_is_rejected(self):
        incomplete = dict(self.source_packets)
        incomplete.pop("agent_consumer_release_handoff_packet")
        with self.assertRaisesRegex(AgentPromptRefreshCandidatePacketError, "missing source packet"):
            build_agent_prompt_refresh_candidate_packet(incomplete)

    def test_validation_rejects_uncited_change_and_missing_review_controls(self):
        packet = copy.deepcopy(self.packet)
        packet["prompt_change_candidates"][0]["source_evidence_ids"] = []
        packet["supported_safe_read_only_scenarios"][0]["automation_boundary"] = "live_action_allowed"
        packet["rollback_notes"] = []
        packet["reviewer_owner_fields"] = []
        packet["offline_validation_commands"] = []

        with self.assertRaisesRegex(AgentPromptRefreshCandidatePacketError, "source_evidence_ids is required"):
            validate_agent_prompt_refresh_candidate_packet(packet)

    def test_validation_rejects_live_private_or_mutating_content(self):
        packet = copy.deepcopy(self.packet)
        packet["active_prompt_mutation"] = True

        with self.assertRaisesRegex(AgentPromptRefreshCandidatePacketError, "mutation"):
            validate_agent_prompt_refresh_candidate_packet(packet)

        packet = copy.deepcopy(self.packet)
        packet["note"] = "Opened DevHub and called the LLM."
        with self.assertRaisesRegex(AgentPromptRefreshCandidatePacketError, "live execution"):
            validate_agent_prompt_refresh_candidate_packet(packet)

        packet = copy.deepcopy(self.packet)
        packet["private_artifact"] = "file://auth_state/session_state.json"
        with self.assertRaisesRegex(AgentPromptRefreshCandidatePacketError, "private paths"):
            validate_agent_prompt_refresh_candidate_packet(packet)


if __name__ == "__main__":
    unittest.main()
