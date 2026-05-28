from __future__ import annotations

import json
from pathlib import Path
import unittest

from ppd.action_journal_compliance import (
    ALLOWED_COMPLIANCE_EVENT_TYPES,
    assert_action_journal_compliance_packet,
    validate_action_journal_compliance_packet,
)


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "action_journal" / "compliance_packet.json"


class ActionJournalCompliancePacketTest(unittest.TestCase):
    def load_packet(self) -> dict:
        return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    def test_fixture_packet_is_commit_safe(self) -> None:
        packet = self.load_packet()

        result = validate_action_journal_compliance_packet(packet)

        self.assertTrue(result.ok, result.problems)
        self.assertEqual(result.event_count, 8)
        self.assertEqual(set(result.event_types), ALLOWED_COMPLIANCE_EVENT_TYPES)
        assert_action_journal_compliance_packet(packet)

    def test_packet_rejects_private_artifact_policy(self) -> None:
        packet = self.load_packet()
        packet["commit_policy"]["private_artifacts_committed"] = True

        result = validate_action_journal_compliance_packet(packet)

        self.assertFalse(result.ok)
        self.assertIn("commit_policy.private_artifacts_committed must be False", result.problems)

    def test_packet_rejects_sensitive_event_material(self) -> None:
        packet = self.load_packet()
        packet["events"][0]["synthetic_metadata"]["cookie"] = "set-cookie: private"

        result = validate_action_journal_compliance_packet(packet)

        self.assertFalse(result.ok)
        self.assertTrue(any("prohibited sensitive key" in problem for problem in result.problems))
        self.assertTrue(any("credential material" in problem for problem in result.problems))

    def test_packet_rejects_all_blocked_private_artifact_categories(self) -> None:
        blocked_cases = [
            ("credentials", "redacted"),
            ("cookies", "redacted"),
            ("auth_state", "redacted"),
            ("screenshot", "devhub.png"),
            ("trace", "devhub.trace"),
            ("har_data", "devhub.har"),
            ("payment_details", "4111 1111 1111 1111"),
            ("private_field_value", "actual user value"),
            ("local_private_path", "/home/person/private.pdf"),
            ("raw_crawl_output", "raw crawl output"),
        ]
        for key, value in blocked_cases:
            packet = self.load_packet()
            packet["events"][0]["synthetic_metadata"][key] = value

            result = validate_action_journal_compliance_packet(packet)

            self.assertFalse(result.ok, key)
            self.assertTrue(any("prohibited" in problem for problem in result.problems), key)

    def test_packet_rejects_official_completion_claims(self) -> None:
        packet = self.load_packet()
        packet["events"][-1]["user_visible_summary"] = "Official upload completed and payment receipt saved."

        result = validate_action_journal_compliance_packet(packet)

        self.assertFalse(result.ok)
        self.assertTrue(any("official completion claim" in problem for problem in result.problems))

    def test_each_event_requires_source_and_guardrail_evidence(self) -> None:
        packet = self.load_packet()
        packet["events"][0]["source_evidence_ids"] = []
        packet["events"][1]["guardrail_evidence_ids"] = []

        result = validate_action_journal_compliance_packet(packet)

        self.assertFalse(result.ok)
        self.assertIn("events[0].source_evidence_ids must be a non-empty list of strings", result.problems)
        self.assertIn("events[1].guardrail_evidence_ids must be a non-empty list of strings", result.problems)

    def test_completion_evidence_requires_user_visible_evidence_ids(self) -> None:
        packet = self.load_packet()
        packet["events"][-1]["synthetic_metadata"]["completion_evidence_ids"] = []

        result = validate_action_journal_compliance_packet(packet)

        self.assertFalse(result.ok)
        self.assertTrue(any("completion_evidence_ids" in problem for problem in result.problems))


if __name__ == "__main__":
    unittest.main()
