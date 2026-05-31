"""Tests for fixture-first PP&D action journal retention/redaction audit packet v1."""

from __future__ import annotations

import copy
from pathlib import Path
import unittest

from ppd.action_journal_retention_redaction_audit_packet_v1 import (
    EXPECTED_OFFLINE_VALIDATION_COMMANDS,
    REQUIRED_EVENT_TYPES,
    assert_action_journal_retention_redaction_audit_packet_v1,
    load_action_journal_retention_redaction_audit_packet_v1,
    validate_action_journal_retention_redaction_audit_packet_v1,
)


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "action_journal_retention_redaction_audit_v1" / "packet.json"


class ActionJournalRetentionRedactionAuditPacketV1Test(unittest.TestCase):
    def load_packet(self) -> dict:
        return load_action_journal_retention_redaction_audit_packet_v1(FIXTURE_PATH)

    def test_fixture_packet_is_valid_and_complete(self) -> None:
        packet = self.load_packet()

        result = validate_action_journal_retention_redaction_audit_packet_v1(packet)

        self.assertTrue(result.ok, result.problems)
        self.assertEqual(result.event_types, REQUIRED_EVENT_TYPES)
        self.assertEqual(result.event_count, len(REQUIRED_EVENT_TYPES))
        self.assertEqual(packet["offline_validation_commands"], EXPECTED_OFFLINE_VALIDATION_COMMANDS)
        assert_action_journal_retention_redaction_audit_packet_v1(packet)

    def test_fixture_paths_are_test_local(self) -> None:
        self.assertIn("ppd/tests/fixtures/action_journal_retention_redaction_audit_v1", FIXTURE_PATH.as_posix())

    def test_rejects_unredacted_values(self) -> None:
        packet = self.load_packet()
        bad_packet = copy.deepcopy(packet)
        bad_packet["journal_events"][0]["redacted_values"]["canonical_url_sample"] = "123 Example Street"

        result = validate_action_journal_retention_redaction_audit_packet_v1(bad_packet)

        self.assertFalse(result.ok)
        self.assertTrue(any("explicit redaction marker" in problem for problem in result.problems), result.problems)

    def test_rejects_unknown_event_type(self) -> None:
        packet = self.load_packet()
        bad_packet = copy.deepcopy(packet)
        bad_packet["journal_events"][3]["event_type"] = "draft_real_form"

        result = validate_action_journal_retention_redaction_audit_packet_v1(bad_packet)

        self.assertFalse(result.ok)
        self.assertTrue(any("event_type is unsupported" in problem for problem in result.problems), result.problems)

    def test_rejects_missing_retention_label(self) -> None:
        packet = self.load_packet()
        bad_packet = copy.deepcopy(packet)
        del bad_packet["journal_events"][0]["retention_label"]

        result = validate_action_journal_retention_redaction_audit_packet_v1(bad_packet)

        self.assertFalse(result.ok)
        self.assertTrue(any("retention_label" in problem for problem in result.problems), result.problems)

    def test_rejects_missing_citation_reference(self) -> None:
        packet = self.load_packet()
        bad_packet = copy.deepcopy(packet)
        bad_packet["journal_events"][1]["citation_refs"] = ["fixture-citation:missing"]

        result = validate_action_journal_retention_redaction_audit_packet_v1(bad_packet)

        self.assertFalse(result.ok)
        self.assertTrue(any("unknown citation ref" in problem for problem in result.problems), result.problems)

    def test_rejects_missing_validation_commands(self) -> None:
        packet = self.load_packet()
        bad_packet = copy.deepcopy(packet)
        del bad_packet["journal_events"][7]["offline_validation_commands"]

        result = validate_action_journal_retention_redaction_audit_packet_v1(bad_packet)

        self.assertFalse(result.ok)
        self.assertTrue(any("offline_validation_commands" in problem for problem in result.problems), result.problems)

    def test_rejects_wrong_offline_validation_command(self) -> None:
        packet = self.load_packet()
        bad_packet = copy.deepcopy(packet)
        bad_packet["journal_events"][7]["offline_validation_commands"] = [["python3", "-m", "pytest"]]

        result = validate_action_journal_retention_redaction_audit_packet_v1(bad_packet)

        self.assertFalse(result.ok)
        self.assertTrue(any("offline_validation_commands" in problem for problem in result.problems), result.problems)

    def test_rejects_browser_artifact_reference(self) -> None:
        packet = self.load_packet()
        bad_packet = copy.deepcopy(packet)
        bad_packet["journal_events"][4]["commit_safe_reason"] = "Synthetic trace.zip was saved."

        result = validate_action_journal_retention_redaction_audit_packet_v1(bad_packet)

        self.assertFalse(result.ok)
        self.assertTrue(any("browser artifact" in problem for problem in result.problems), result.problems)

    def test_rejects_sensitive_keys_and_values(self) -> None:
        cases = (
            ("credentials", "not stored", "prohibited sensitive key"),
            ("cookies", "not stored", "prohibited sensitive key"),
            ("auth_state", "not stored", "prohibited sensitive key"),
            ("screenshot", "not stored", "prohibited sensitive key"),
            ("trace", "not stored", "prohibited sensitive key"),
            ("har_data", "not stored", "prohibited sensitive key"),
            ("private_values", "not stored", "prohibited sensitive key"),
            ("payment_details", "not stored", "prohibited sensitive key"),
            ("local_private_path", "not stored", "prohibited sensitive key"),
            ("raw_crawl_output", "not stored", "prohibited sensitive key"),
            ("downloaded_document_references", "not stored", "prohibited sensitive key"),
            ("safe_note", "Bearer abc123", "credential material"),
            ("safe_note", "/home/example/private.pdf", "local private path"),
            ("safe_note", "4111 1111 1111 1111", "payment number"),
            ("safe_note", "raw crawl output was retained", "raw material"),
            ("safe_note", "downloaded document reference was retained", "downloaded document reference"),
        )
        for key, value, expected_problem in cases:
            with self.subTest(key=key, value=value):
                packet = self.load_packet()
                bad_packet = copy.deepcopy(packet)
                bad_packet["journal_events"][0][key] = value

                result = validate_action_journal_retention_redaction_audit_packet_v1(bad_packet)

                self.assertFalse(result.ok)
                self.assertTrue(any(expected_problem in problem for problem in result.problems), result.problems)

    def test_rejects_live_devhub_official_and_guarantee_claims(self) -> None:
        cases = (
            ("Live crawl performed against Portland.gov." , "live crawl claim"),
            ("Opened DevHub and authenticated DevHub session." , "DevHub access claim"),
            ("The permit application was submitted." , "official completion claim"),
            ("Permit approval is certain and legally valid." , "legal or permitting guarantee"),
        )
        for claim, expected_problem in cases:
            with self.subTest(claim=claim):
                packet = self.load_packet()
                bad_packet = copy.deepcopy(packet)
                bad_packet["journal_events"][5]["commit_safe_reason"] = claim

                result = validate_action_journal_retention_redaction_audit_packet_v1(bad_packet)

                self.assertFalse(result.ok)
                self.assertTrue(any(expected_problem in problem for problem in result.problems), result.problems)

    def test_rejects_active_mutation_flags(self) -> None:
        packet = self.load_packet()
        bad_packet = copy.deepcopy(packet)
        bad_packet["active_journal_mutated"] = True
        bad_packet["journal_events"][0]["redaction_audit"]["active_export_state_mutated"] = True

        result = validate_action_journal_retention_redaction_audit_packet_v1(bad_packet)

        self.assertFalse(result.ok)
        self.assertTrue(any("active_journal_mutated must be False" in problem for problem in result.problems), result.problems)
        self.assertTrue(any("active_export_state_mutated must be False" in problem for problem in result.problems), result.problems)


if __name__ == "__main__":
    unittest.main()
