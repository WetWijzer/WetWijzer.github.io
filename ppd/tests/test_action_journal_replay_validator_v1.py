import copy
import unittest

from ppd.devhub.action_journal_replay_validator import (
    EXPECTED_EVENT_REPLAY_ORDER,
    EXPECTED_OFFLINE_VALIDATION_COMMANDS,
    assert_action_journal_replay_report_v1,
    load_committed_action_journal_acceptance_packet_v1,
    replay_action_journal_acceptance_packet_v1,
    replay_committed_action_journal_acceptance_packet_v1,
)


class ActionJournalReplayValidatorV1Tests(unittest.TestCase):
    def test_committed_acceptance_packet_replays_with_deterministic_findings(self):
        report = replay_committed_action_journal_acceptance_packet_v1()

        self.assertTrue(report.ok, report.to_dict())
        self.assertEqual(report.event_count, 6)
        self.assertEqual(
            [finding.code for finding in report.findings],
            [
                "acceptance_packet_contract",
                "event_ordering",
                "citation_coverage",
                "redacted_evidence_summaries",
                "reviewer_owner_assignments",
                "offline_validation_commands",
                "safety_attestations",
            ],
        )
        assert_action_journal_replay_report_v1(report)

    def test_event_ordering_finding_uses_canonical_replay_order(self):
        report = replay_committed_action_journal_acceptance_packet_v1()
        finding = self._finding(report, "event_ordering")

        self.assertTrue(finding.ok)
        self.assertEqual(tuple(finding.details["expected_order"]), EXPECTED_EVENT_REPLAY_ORDER)
        self.assertEqual(tuple(finding.details["actual_order"]), EXPECTED_EVENT_REPLAY_ORDER)
        self.assertEqual(finding.details["duplicate_event_ids"], ())

    def test_citation_coverage_finding_counts_each_event(self):
        report = replay_committed_action_journal_acceptance_packet_v1()
        finding = self._finding(report, "citation_coverage")

        self.assertTrue(finding.ok)
        self.assertEqual(len(finding.details["citation_counts_by_event_id"]), 6)
        self.assertTrue(all(count >= 1 for count in finding.details["citation_counts_by_event_id"].values()))
        self.assertEqual(finding.details["uncited_event_ids"], ())
        self.assertEqual(finding.details["non_https_citation_refs"], ())

    def test_redacted_evidence_summary_finding_requires_redactions_and_no_raw_evidence(self):
        report = replay_committed_action_journal_acceptance_packet_v1()
        finding = self._finding(report, "redacted_evidence_summaries")

        self.assertTrue(finding.ok)
        self.assertEqual(len(finding.details["redaction_counts_by_event_id"]), 6)
        self.assertTrue(all(count >= 1 for count in finding.details["redaction_counts_by_event_id"].values()))
        self.assertEqual(finding.details["raw_evidence_event_ids"], ())

    def test_reviewer_owner_finding_reports_packet_and_event_assignments(self):
        report = replay_committed_action_journal_acceptance_packet_v1()
        finding = self._finding(report, "reviewer_owner_assignments")

        self.assertTrue(finding.ok)
        self.assertEqual(finding.details["packet_owner"], "ppd-fixture-maintainer")
        self.assertEqual(finding.details["technical_reviewer"], "ppd-reviewer")
        self.assertEqual(finding.details["policy_reviewer"], "ppd-policy-reviewer")
        self.assertEqual(len(finding.details["assignments_by_event_id"]), 6)
        self.assertEqual(finding.details["unassigned_event_ids"], ())

    def test_offline_validation_command_finding_accepts_only_self_test(self):
        report = replay_committed_action_journal_acceptance_packet_v1()
        finding = self._finding(report, "offline_validation_commands")

        self.assertTrue(finding.ok)
        self.assertEqual(tuple(finding.details["actual_commands"]), EXPECTED_OFFLINE_VALIDATION_COMMANDS)

    def test_safety_attestation_finding_covers_required_no_artifact_claims(self):
        report = replay_committed_action_journal_acceptance_packet_v1()
        finding = self._finding(report, "safety_attestations")

        self.assertTrue(finding.ok)
        self.assertEqual(finding.details["missing_or_false_attestations"], ())
        groups = finding.details["attestation_groups"]
        self.assertEqual(groups["no_credential"], "no_credentials")
        self.assertEqual(groups["no_cookie"], "no_cookies")
        self.assertEqual(groups["no_private_value"], "no_private_values")
        self.assertEqual(groups["no_payment"], "no_payment")
        self.assertEqual(groups["no_official_action"], "no_official_action")
        self.assertEqual(groups["no_browser_artifact"], ("no_screenshots", "no_traces", "no_har"))

    def test_replay_rejects_out_of_order_events(self):
        packet = load_committed_action_journal_acceptance_packet_v1()
        packet["journal_events"] = [packet["journal_events"][1], packet["journal_events"][0]] + packet["journal_events"][2:]

        report = replay_action_journal_acceptance_packet_v1(packet)

        self.assertFalse(report.ok)
        finding = self._finding(report, "event_ordering")
        self.assertFalse(finding.ok)

    def test_replay_rejects_uncited_event(self):
        packet = load_committed_action_journal_acceptance_packet_v1()
        packet["journal_events"][0]["citations"] = []

        report = replay_action_journal_acceptance_packet_v1(packet)

        self.assertFalse(report.ok)
        finding = self._finding(report, "citation_coverage")
        self.assertFalse(finding.ok)
        self.assertEqual(finding.details["uncited_event_ids"], ("aj-v1-public-crawl-preflight-001",))

    def test_replay_rejects_raw_evidence_summary(self):
        packet = load_committed_action_journal_acceptance_packet_v1()
        packet["journal_events"][0]["redacted_evidence_summary"] = copy.deepcopy(
            packet["journal_events"][0]["redacted_evidence_summary"]
        )
        packet["journal_events"][0]["redacted_evidence_summary"]["raw_evidence_included"] = True

        report = replay_action_journal_acceptance_packet_v1(packet)

        self.assertFalse(report.ok)
        finding = self._finding(report, "redacted_evidence_summaries")
        self.assertFalse(finding.ok)
        self.assertEqual(finding.details["raw_evidence_event_ids"], ("aj-v1-public-crawl-preflight-001",))

    def test_replay_rejects_missing_reviewer_assignment(self):
        packet = load_committed_action_journal_acceptance_packet_v1()
        packet["journal_events"][0]["reviewer"] = ""

        report = replay_action_journal_acceptance_packet_v1(packet)

        self.assertFalse(report.ok)
        finding = self._finding(report, "reviewer_owner_assignments")
        self.assertFalse(finding.ok)
        self.assertEqual(finding.details["unassigned_event_ids"], ("aj-v1-public-crawl-preflight-001",))

    def test_replay_rejects_extra_offline_validation_command(self):
        packet = load_committed_action_journal_acceptance_packet_v1()
        packet["offline_validation_commands"] = [
            ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
            ["python3", "-m", "pytest", "ppd/tests"],
        ]

        report = replay_action_journal_acceptance_packet_v1(packet)

        self.assertFalse(report.ok)
        finding = self._finding(report, "offline_validation_commands")
        self.assertFalse(finding.ok)

    def test_replay_rejects_missing_required_attestation(self):
        packet = load_committed_action_journal_acceptance_packet_v1()
        packet["attestations"] = copy.deepcopy(packet["attestations"])
        packet["attestations"]["no_official_action"] = False

        report = replay_action_journal_acceptance_packet_v1(packet)

        self.assertFalse(report.ok)
        finding = self._finding(report, "safety_attestations")
        self.assertFalse(finding.ok)
        self.assertEqual(finding.details["missing_or_false_attestations"], ("no_official_action",))

    def _finding(self, report, code):
        matches = [finding for finding in report.findings if finding.code == code]
        self.assertEqual(len(matches), 1)
        return matches[0]


if __name__ == "__main__":
    unittest.main()
