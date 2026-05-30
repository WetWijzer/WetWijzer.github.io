import copy
import json
import unittest
from pathlib import Path

from ppd.action_journal_acceptance_packet_v1 import (
    REQUIRED_ATTESTATIONS,
    REQUIRED_EVENT_TYPES,
    assert_action_journal_acceptance_packet_v1,
    validate_action_journal_acceptance_packet_v1,
)


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "action_journal_acceptance_packet_v1.json"


def load_packet():
    with FIXTURE_PATH.open(encoding="utf-8") as fixture_file:
        return json.load(fixture_file)


class ActionJournalAcceptancePacketV1Tests(unittest.TestCase):
    def test_fixture_packet_is_valid(self):
        packet = load_packet()

        result = validate_action_journal_acceptance_packet_v1(packet)

        self.assertTrue(result.ok, result.problems)
        self.assertEqual(result.event_count, 6)
        self.assertEqual(set(result.event_types), set(REQUIRED_EVENT_TYPES))
        assert_action_journal_acceptance_packet_v1(packet)

    def test_packet_has_required_identity_and_offline_validation(self):
        packet = load_packet()

        self.assertEqual(packet["packet_version"], "action-journal-acceptance-packet-v1")
        self.assertIs(packet["fixture_first"], True)
        self.assertIs(packet["commit_safe"], True)
        self.assertEqual(
            packet["offline_validation_commands"],
            [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]],
        )

    def test_attestations_are_explicitly_true(self):
        packet = load_packet()

        attestations = packet["attestations"]
        self.assertLessEqual(set(REQUIRED_ATTESTATIONS), set(attestations))
        for name in REQUIRED_ATTESTATIONS:
            self.assertIs(attestations[name], True)

    def test_event_type_coverage_matches_acceptance_packet_scope(self):
        packet = load_packet()

        declared_coverage = set(packet["event_type_coverage"])
        event_types = {event["event_type"] for event in packet["journal_events"]}

        self.assertEqual(declared_coverage, set(REQUIRED_EVENT_TYPES))
        self.assertEqual(event_types, set(REQUIRED_EVENT_TYPES))

    def test_each_event_is_commit_safe_and_reviewable(self):
        packet = load_packet()

        for event in packet["journal_events"]:
            self.assertTrue(event["event_id"].startswith("aj-v1-"))
            self.assertTrue(event["source_fixture"].startswith("ppd/tests/fixtures/"))
            self.assertTrue(event["owner"])
            self.assertTrue(event["reviewer"])
            self.assertTrue(event["commit_safe_reason"])
            self.assertTrue(event["citations"])
            self.assertTrue(event["redacted_evidence_summary"]["summary"])
            self.assertTrue(event["redacted_evidence_summary"]["redactions_applied"])
            self.assertIs(event["redacted_evidence_summary"]["raw_evidence_included"], False)

            for citation in event["citations"]:
                self.assertTrue(citation["label"])
                self.assertTrue(citation["url"].startswith("https://"))

    def test_reviewer_owner_packet_fields_are_present(self):
        packet = load_packet()
        reviewer_owner_fields = packet["reviewer_owner_fields"]

        self.assertTrue(reviewer_owner_fields["packet_owner"])
        self.assertTrue(reviewer_owner_fields["technical_reviewer"])
        self.assertTrue(reviewer_owner_fields["policy_reviewer"])

    def test_rejects_sensitive_keys_and_values(self):
        cases = [
            ("credentials", {"username": "fixture-user"}),
            ("cookies", ["set-cookie: abc=123"]),
            ("auth_state", {"storage": "fixture"}),
            ("screenshots", ["devhub-home.png"]),
            ("traces", ["run.trace"]),
            ("har_data", "network.har"),
            ("private_value", "actual user value"),
            ("payment_details", "card number 4111 1111 1111 1111"),
            ("local_private_path", "/home/example/private.pdf"),
            ("raw_pdf_body", "full pdf text"),
            ("raw_crawl_body", "raw crawl output"),
        ]

        for key, value in cases:
            with self.subTest(key=key):
                packet = load_packet()
                packet["journal_events"][0][key] = value

                result = validate_action_journal_acceptance_packet_v1(packet)

                self.assertFalse(result.ok)

    def test_rejects_uncited_event_evidence(self):
        packet = load_packet()
        packet["journal_events"][0]["citations"] = []

        result = validate_action_journal_acceptance_packet_v1(packet)

        self.assertFalse(result.ok)
        self.assertTrue(any("citations" in problem for problem in result.problems))

    def test_rejects_unsupported_event_type(self):
        packet = load_packet()
        packet["journal_events"][0]["event_type"] = "submit_payment"

        result = validate_action_journal_acceptance_packet_v1(packet)

        self.assertFalse(result.ok)
        self.assertTrue(any("unsupported" in problem for problem in result.problems))

    def test_rejects_legal_or_permitting_outcome_guarantees(self):
        packet = load_packet()
        packet["journal_events"][1]["commit_safe_reason"] = "Permit approval is assured by this packet."

        result = validate_action_journal_acceptance_packet_v1(packet)

        self.assertFalse(result.ok)
        self.assertTrue(any("outcome guarantee" in problem for problem in result.problems))

    def test_rejects_active_mutation_flags(self):
        mutation_cases = [
            {"source_mutation": True},
            {"source_registry_mutation": True},
            {"surface_registry_mutation": True},
            {"guardrail_mutation": True},
            {"prompt_mutation": True},
            {"release_state_mutation": True},
            {"agent_state_mutation": True},
            {"active_mutation_flags": ["update source registry"]},
        ]

        for mutation_flags in mutation_cases:
            with self.subTest(mutation_flags=mutation_flags):
                packet = load_packet()
                packet["mutation_flags"] = mutation_flags

                result = validate_action_journal_acceptance_packet_v1(packet)

                self.assertFalse(result.ok)

    def test_rejects_mutation_language_inside_event_evidence(self):
        packet = load_packet()
        packet["journal_events"][0]["commit_safe_reason"] = "Update source registry after accepting this event."

        result = validate_action_journal_acceptance_packet_v1(packet)

        self.assertFalse(result.ok)
        self.assertTrue(any("mutation" in problem for problem in result.problems))

    def test_rejects_missing_required_attestation(self):
        packet = load_packet()
        packet["attestations"] = copy.deepcopy(packet["attestations"])
        packet["attestations"]["no_har"] = False

        result = validate_action_journal_acceptance_packet_v1(packet)

        self.assertFalse(result.ok)
        self.assertTrue(any("attestations.no_har" in problem for problem in result.problems))


if __name__ == "__main__":
    unittest.main()
