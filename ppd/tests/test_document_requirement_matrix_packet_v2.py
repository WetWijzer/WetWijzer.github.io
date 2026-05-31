from __future__ import annotations

import copy
import unittest
from pathlib import Path

from ppd.document_requirement_matrix_packet_v2 import EXPECTED_OFFLINE_COMMANDS, load_packet, validate_packet


class DocumentRequirementMatrixPacketV2Test(unittest.TestCase):
    def fixture_path(self) -> Path:
        return Path(__file__).parent / "fixtures" / "document_requirement_matrix_v2" / "packet.json"

    def valid_packet(self) -> dict:
        return load_packet(self.fixture_path())

    def assert_invalid(self, packet: dict, expected_fragment: str) -> None:
        errors = validate_packet(packet)
        self.assertTrue(errors)
        self.assertTrue(
            any(expected_fragment in error for error in errors),
            f"expected fragment {expected_fragment!r} in errors {errors!r}",
        )

    def test_fixture_packet_validates(self) -> None:
        packet = self.valid_packet()
        self.assertEqual([], validate_packet(packet))

    def test_fixture_uses_exact_offline_validation_commands(self) -> None:
        packet = self.valid_packet()
        self.assertEqual(EXPECTED_OFFLINE_COMMANDS, packet["offline_validation_commands"])

    def test_all_rows_remain_fixture_only_reviewer_holds(self) -> None:
        packet = self.valid_packet()
        self.assertTrue(packet["fixture_first"])
        self.assertTrue(packet["synthetic_only"])
        self.assertTrue(packet["does_not_mutate_active_requirements"])
        self.assertTrue(all(row["status"] == "fixture_only_reviewer_hold" for row in packet["workflows"]))
        self.assertTrue(all(row["may_promote_to_active"] is False for row in packet["reviewer_hold_rows"]))

    def test_source_placeholders_are_not_promoted_citations(self) -> None:
        packet = self.valid_packet()
        for source in packet["source_evidence_placeholders"]:
            self.assertEqual("official_public_source_pending_capture", source["placeholder_kind"])
            self.assertFalse(source["private_or_authenticated"])
            self.assertEqual("placeholder_not_promoted", source["citation_status"])

    def test_rejects_missing_required_workflow_rows(self) -> None:
        packet = self.valid_packet()
        packet["workflows"] = [row for row in packet["workflows"] if row["workflow_id"] != "synthetic_sign"]
        self.assert_invalid(packet, "workflow coverage mismatch")

    def test_rejects_missing_required_document_labels(self) -> None:
        packet = self.valid_packet()
        packet["workflows"][0]["required_document_labels"] = []
        self.assert_invalid(packet, "must list at least two required document labels")

    def test_rejects_missing_upload_grouping_expectations(self) -> None:
        packet = self.valid_packet()
        packet["workflows"][0]["upload_grouping_expectation"] = ""
        self.assert_invalid(packet, "missing upload grouping expectation")

    def test_rejects_missing_single_pdf_or_file_naming_references(self) -> None:
        packet = self.valid_packet()
        packet["workflows"][0]["single_pdf_reference"] = "plans placeholder only"
        packet["workflows"][1]["file_naming_reference"] = "attachment standards placeholder"
        errors = validate_packet(packet)
        self.assertTrue(any("missing Single PDF reference" in error for error in errors))
        self.assertTrue(any("missing file naming reference" in error for error in errors))

    def test_rejects_missing_source_evidence_placeholders(self) -> None:
        packet = self.valid_packet()
        packet["workflows"][0]["source_evidence_placeholders"] = []
        self.assert_invalid(packet, "missing source evidence placeholders")

    def test_rejects_missing_reviewer_hold_rows(self) -> None:
        packet = self.valid_packet()
        packet["reviewer_hold_rows"] = packet["reviewer_hold_rows"][:-1]
        self.assert_invalid(packet, "reviewer hold rows must cover every workflow")

    def test_rejects_missing_or_unsafe_validation_commands(self) -> None:
        missing_commands = self.valid_packet()
        missing_commands["offline_validation_commands"] = []
        self.assert_invalid(missing_commands, "offline validation commands do not match")

        unsafe_command = self.valid_packet()
        unsafe_command["offline_validation_commands"] = copy.deepcopy(EXPECTED_OFFLINE_COMMANDS)
        unsafe_command["offline_validation_commands"][0] = ["python3", "-m", "playwright", "open", "devhub"]
        errors = validate_packet(unsafe_command)
        self.assertTrue(any("offline validation commands do not match" in error for error in errors))
        self.assertTrue(any("offline command contains prohibited token" in error for error in errors))

    def test_rejects_private_or_local_document_paths(self) -> None:
        packet = self.valid_packet()
        packet["workflows"][0]["private_document_path"] = "/home/alex/private/site-plan.pdf"
        self.assert_invalid(packet, "private or local document path")

    def test_rejects_raw_or_downloaded_pdfs(self) -> None:
        packet = self.valid_packet()
        packet["raw_pdf_artifact"] = "downloaded PDF retained from a local crawl"
        self.assert_invalid(packet, "raw or downloaded PDFs")

    def test_rejects_upload_staging_claims(self) -> None:
        packet = self.valid_packet()
        packet["workflows"][0]["upload_staging_claim"] = "upload staging completed"
        self.assert_invalid(packet, "must not claim upload staging")

    def test_rejects_live_devhub_claims(self) -> None:
        packet = self.valid_packet()
        packet["live_devhub_claim"] = "opened DevHub browser session"
        self.assert_invalid(packet, "must not claim live DevHub access")

    def test_rejects_legal_or_permitting_guarantees(self) -> None:
        packet = self.valid_packet()
        packet["permitting_guarantee"] = "permit approval guaranteed"
        self.assert_invalid(packet, "legal or permitting guarantee")

    def test_rejects_active_mutation_flags(self) -> None:
        for flag in [
            "mutates_active_requirements",
            "mutates_active_process_models",
            "mutates_active_guardrails",
            "mutates_active_prompts",
            "mutates_active_contracts",
            "mutates_active_sources",
            "mutates_active_devhub_surfaces",
            "mutates_active_release_state",
        ]:
            packet = self.valid_packet()
            packet[flag] = True
            self.assert_invalid(packet, "active mutation flag")


if __name__ == "__main__":
    unittest.main()
