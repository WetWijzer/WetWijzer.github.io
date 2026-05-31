import copy
import json
import unittest
from pathlib import Path

from ppd.action_journal_export_packet_v2 import (
    EXPECTED_OFFLINE_VALIDATION_COMMANDS,
    REQUIRED_ATTESTATIONS,
    REQUIRED_EVENT_TYPES,
    assert_action_journal_export_packet_v2,
    validate_action_journal_export_packet_v2,
)


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "action_journal_export_packet_v2.json"


def load_packet():
    with FIXTURE_PATH.open(encoding="utf-8") as fixture_file:
        return json.load(fixture_file)


class ActionJournalExportPacketV2Tests(unittest.TestCase):
    def test_fixture_packet_is_valid(self):
        packet = load_packet()

        result = validate_action_journal_export_packet_v2(packet)

        self.assertTrue(result.ok, result.problems)
        self.assertEqual(result.row_count, len(REQUIRED_EVENT_TYPES))
        self.assertEqual(result.event_types, REQUIRED_EVENT_TYPES)
        assert_action_journal_export_packet_v2(packet)

    def test_packet_declares_exact_offline_validation_command(self):
        packet = load_packet()

        self.assertEqual(packet["offline_validation_commands"], EXPECTED_OFFLINE_VALIDATION_COMMANDS)
        for row in packet["event_rows"]:
            self.assertEqual(row["offline_validation_commands"], EXPECTED_OFFLINE_VALIDATION_COMMANDS)

    def test_packet_flags_remain_fixture_first_and_non_operational(self):
        packet = load_packet()

        self.assertIs(packet["fixture_first"], True)
        self.assertIs(packet["commit_safe"], True)
        self.assertIs(packet["live_crawl_performed"], False)
        self.assertIs(packet["browser_automation_performed"], False)
        self.assertIs(packet["official_action_performed"], False)

    def test_attestations_are_explicitly_true(self):
        packet = load_packet()

        attestations = packet["attestations"]
        self.assertLessEqual(set(REQUIRED_ATTESTATIONS), set(attestations))
        for name in REQUIRED_ATTESTATIONS:
            self.assertIs(attestations[name], True)

    def test_each_event_row_has_redaction_check_and_citations(self):
        packet = load_packet()

        for row in packet["event_rows"]:
            self.assertTrue(row["row_id"].startswith("aj-v2-"))
            self.assertIn(row["event_type"], REQUIRED_EVENT_TYPES)
            self.assertTrue(row["source_evidence_ids"])
            self.assertTrue(row["guardrail_refs"])
            self.assertTrue(row["redacted_summary"])
            self.assertTrue(row["commit_safe_reason"])
            self.assertIs(row["redaction_check"]["passed"], True)
            self.assertIs(row["redaction_check"]["raw_values_committed"], False)
            self.assertTrue(row["redaction_check"]["checks"])

    def test_rejects_missing_required_event_type_order(self):
        packet = load_packet()
        packet["event_rows"] = list(reversed(packet["event_rows"]))

        result = validate_action_journal_export_packet_v2(packet)

        self.assertFalse(result.ok)
        self.assertTrue(any("deterministic order" in problem for problem in result.problems))

    def test_rejects_sensitive_keys_and_values(self):
        cases = [
            ("credentials", {"redacted": False}),
            ("cookies", ["set-cookie: abc=123"]),
            ("auth_state", {"storage": "fixture"}),
            ("screenshots", ["devhub-home.png"]),
            ("traces", ["browser.trace"]),
            ("har_data", "network.har"),
            ("private_value", "actual user value"),
            ("payment_details", "card number 4111 1111 1111 1111"),
            ("local_private_path", "/home/example/private.pdf"),
            ("raw_download", "raw download"),
        ]

        for key, value in cases:
            with self.subTest(key=key):
                packet = load_packet()
                packet["event_rows"][0][key] = value

                result = validate_action_journal_export_packet_v2(packet)

                self.assertFalse(result.ok)

    def test_rejects_official_completion_claims(self):
        packet = load_packet()
        packet["event_rows"][-1]["redacted_summary"] = "Official upload was submitted and receipt was issued."

        result = validate_action_journal_export_packet_v2(packet)

        self.assertFalse(result.ok)
        self.assertTrue(any("official completion claim" in problem for problem in result.problems))

    def test_rejects_failed_redaction_check(self):
        packet = load_packet()
        packet["event_rows"][0]["redaction_check"] = copy.deepcopy(packet["event_rows"][0]["redaction_check"])
        packet["event_rows"][0]["redaction_check"]["passed"] = False

        result = validate_action_journal_export_packet_v2(packet)

        self.assertFalse(result.ok)
        self.assertTrue(any("redaction_check.passed" in problem for problem in result.problems))

    def test_rejects_validation_command_drift(self):
        packet = load_packet()
        packet["event_rows"][0]["offline_validation_commands"] = [["python3", "-m", "pytest"]]

        result = validate_action_journal_export_packet_v2(packet)

        self.assertFalse(result.ok)
        self.assertTrue(any("offline_validation_commands" in problem for problem in result.problems))


if __name__ == "__main__":
    unittest.main()
