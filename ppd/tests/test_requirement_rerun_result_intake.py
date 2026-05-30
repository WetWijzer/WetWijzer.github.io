import copy
import json
import unittest
from pathlib import Path

from ppd.extraction.requirement_rerun_result_intake import (
    assert_valid_requirement_rerun_result_intake_packet,
    validate_requirement_rerun_result_intake_packet,
)


FIXTURE = Path(__file__).parent / "fixtures" / "requirement_rerun_result_intake" / "valid_packet.json"


class RequirementRerunResultIntakeValidationTest(unittest.TestCase):
    def setUp(self):
        with FIXTURE.open("r", encoding="utf-8") as handle:
            self.packet = json.load(handle)

    def assert_invalid(self, packet, expected):
        errors = validate_requirement_rerun_result_intake_packet(packet)
        self.assertTrue(errors)
        self.assertIn(expected, "\n".join(errors))

    def test_valid_fixture_passes(self):
        self.assertEqual(validate_requirement_rerun_result_intake_packet(self.packet), [])
        assert_valid_requirement_rerun_result_intake_packet(self.packet)

    def test_rejects_uncited_result_decisions(self):
        packet = copy.deepcopy(self.packet)
        packet["result_decisions"][0]["citations"] = []
        self.assert_invalid(packet, "must include citations")

    def test_rejects_missing_affected_ids(self):
        for field in ("requirement_ids", "process_ids", "guardrail_ids"):
            packet = copy.deepcopy(self.packet)
            packet["affected"][field] = []
            self.assert_invalid(packet, field)

    def test_rejects_missing_reviewer_owners(self):
        packet = copy.deepcopy(self.packet)
        packet["reviewer_owners"] = []
        self.assert_invalid(packet, "reviewer owner")

    def test_rejects_missing_offline_validation_commands(self):
        packet = copy.deepcopy(self.packet)
        packet["offline_validation"]["commands"] = []
        self.assert_invalid(packet, "offline validation commands")

    def test_rejects_raw_body_download_and_archive_references(self):
        for text in ("raw body was reviewed", "downloaded document path", "archive reference"):
            packet = copy.deepcopy(self.packet)
            packet["result_decisions"][0]["notes"] = text
            self.assert_invalid(packet, "raw body, download, archive")

    def test_rejects_private_case_facts(self):
        packet = copy.deepcopy(self.packet)
        packet["result_decisions"][0]["notes"] = "Includes applicant name and permit number."
        self.assert_invalid(packet, "private case fact")

    def test_rejects_live_execution_claims(self):
        packet = copy.deepcopy(self.packet)
        packet["result_decisions"][0]["notes"] = "The live extraction was run again."
        self.assert_invalid(packet, "live extraction or processor execution")

    def test_rejects_legal_or_permitting_guarantees(self):
        packet = copy.deepcopy(self.packet)
        packet["result_decisions"][0]["notes"] = "This guarantees permit approval."
        self.assert_invalid(packet, "legal or permitting outcome guarantee")

    def test_rejects_active_mutation_flags(self):
        for field in (
            "requirements_mutated",
            "processes_mutated",
            "guardrails_mutated",
            "prompts_mutated",
            "monitoring_mutated",
            "release_state_mutated",
        ):
            packet = copy.deepcopy(self.packet)
            packet["mutation_flags"][field] = True
            self.assert_invalid(packet, "active mutation")


if __name__ == "__main__":
    unittest.main()
