import copy
import json
import unittest
from pathlib import Path

from ppd.crawler.source_refresh_result_reconciliation_validation import (
    validate_source_refresh_result_reconciliation_packet,
)

FIXTURE = Path(__file__).parent / "fixtures" / "source_refresh_result_reconciliation" / "valid_packet.json"


class SourceRefreshResultReconciliationValidationTest(unittest.TestCase):
    def setUp(self):
        self.packet = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def assertInvalid(self, packet, expected_fragment):
        errors = validate_source_refresh_result_reconciliation_packet(packet)
        self.assertTrue(errors, "expected validation errors")
        self.assertIn(expected_fragment, "; ".join(errors))

    def test_valid_packet_passes(self):
        self.assertEqual([], validate_source_refresh_result_reconciliation_packet(self.packet))

    def test_rejects_uncited_reconciliation_decision(self):
        packet = copy.deepcopy(self.packet)
        packet["source_decisions"][0]["citations"] = []
        self.assertInvalid(packet, "citations must contain at least one public citation")

    def test_rejects_missing_affected_artifact_ids(self):
        for field in ("affected_requirement_ids", "affected_process_ids", "affected_guardrail_ids"):
            packet = copy.deepcopy(self.packet)
            packet["source_decisions"][0][field] = []
            self.assertInvalid(packet, f"{field} must contain at least one affected artifact id")

    def test_rejects_missing_reviewer_owners(self):
        packet = copy.deepcopy(self.packet)
        packet["reviewer_owner"] = ""
        self.assertInvalid(packet, "reviewer_owner is required")

        packet = copy.deepcopy(self.packet)
        packet["source_decisions"][0]["reviewer_owner"] = ""
        self.assertInvalid(packet, "source_decisions[0].reviewer_owner is required")

    def test_rejects_missing_offline_validation_commands(self):
        packet = copy.deepcopy(self.packet)
        packet["offline_validation_commands"] = []
        self.assertInvalid(packet, "offline_validation_commands must contain at least one offline command")

    def test_rejects_non_allowlisted_urls(self):
        packet = copy.deepcopy(self.packet)
        packet["source_decisions"][0]["citations"][0]["href"] = "https://example.com/not-allowed"
        self.assertInvalid(packet, "host is not allowlisted")

    def test_rejects_authenticated_urls(self):
        packet = copy.deepcopy(self.packet)
        packet["source_decisions"][0]["citations"][0]["href"] = "https://user:pass@www.portland.gov/code/33"
        self.assertInvalid(packet, "authenticated URL credentials")

        packet = copy.deepcopy(self.packet)
        packet["source_decisions"][0]["citations"][0]["href"] = "https://www.portland.gov/code/33?token=secret"
        self.assertInvalid(packet, "authenticated URL query parameters")

    def test_rejects_raw_body_download_archive_references(self):
        packet = copy.deepcopy(self.packet)
        packet["source_decisions"][0]["raw_body"] = "raw response"
        self.assertInvalid(packet, "raw body/download/archive reference")

        packet = copy.deepcopy(self.packet)
        packet["source_decisions"][0]["decision_basis"].append("downloaded document stored for review")
        self.assertInvalid(packet, "raw body/download/archive reference")

    def test_rejects_private_or_session_artifacts(self):
        packet = copy.deepcopy(self.packet)
        packet["source_decisions"][0]["artifact_path"] = "/tmp/private/session/crawl.json"
        self.assertInvalid(packet, "private/session artifact reference")

    def test_rejects_live_crawler_or_processor_execution_claims(self):
        packet = copy.deepcopy(self.packet)
        packet["source_decisions"][0]["decision_basis"].append("live crawler executed and completed")
        self.assertInvalid(packet, "live crawler or processor execution claim")

        packet = copy.deepcopy(self.packet)
        packet["source_decisions"][0]["decision_basis"].append("processor execution completed during intake")
        self.assertInvalid(packet, "live crawler or processor execution claim")

    def test_rejects_legal_or_permitting_outcome_guarantees(self):
        packet = copy.deepcopy(self.packet)
        packet["source_decisions"][0]["decision_basis"].append("permit approval is guaranteed")
        self.assertInvalid(packet, "legal or permitting outcome guarantee")

    def test_rejects_active_mutation_flags(self):
        mutation_fields = (
            "active_source_mutation",
            "schedule_mutation_enabled",
            "requirement_mutation_allowed",
            "active_process_mutation",
            "guardrail_mutation_enabled",
            "active_prompt_mutation",
            "monitoring_mutation_allowed",
            "active_release_state_mutation",
        )
        for field in mutation_fields:
            packet = copy.deepcopy(self.packet)
            packet[field] = True
            self.assertInvalid(packet, "active mutation flag")


if __name__ == "__main__":
    unittest.main()
