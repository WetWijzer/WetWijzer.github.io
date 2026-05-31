from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from ppd.validation.missing_information_packet_v2 import validate_missing_information_packet_v2


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "missing_information_packet_v2_valid.json"


class MissingInformationPacketV2ValidationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.packet = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    def assert_rejected(self, packet: dict, expected_fragment: str) -> None:
        result = validate_missing_information_packet_v2(packet)
        self.assertFalse(result.valid)
        self.assertTrue(
            any(expected_fragment in error for error in result.errors),
            msg=f"missing {expected_fragment!r} in {result.errors!r}",
        )

    def test_valid_fixture_is_accepted(self) -> None:
        result = validate_missing_information_packet_v2(self.packet)
        self.assertTrue(result.valid, result.errors)

    def test_rejects_missing_required_row_sections(self) -> None:
        for section in (
            "workflow_cases",
            "missing_fact_rows",
            "missing_document_rows",
            "stale_or_conflicting_evidence_rows",
            "blocked_actions",
            "next_safe_action_rows",
            "citation_references",
            "reviewer_dispositions",
            "validation_commands",
        ):
            with self.subTest(section=section):
                packet = copy.deepcopy(self.packet)
                packet[section] = []
                self.assert_rejected(packet, f"{section} must contain at least one row")

    def test_rejects_missing_required_confirmations(self) -> None:
        for confirmation in (
            "dry_run_only",
            "no_private_session_artifacts",
            "no_official_action_completion_claims",
            "no_legal_or_permitting_guarantees",
            "no_live_crawl_or_devhub_claims",
            "no_active_mutation_flags",
        ):
            with self.subTest(confirmation=confirmation):
                packet = copy.deepcopy(self.packet)
                packet["required_confirmations"][confirmation] = False
                self.assert_rejected(packet, f"required_confirmations.{confirmation} must be true")

    def test_rejects_private_session_browser_raw_or_downloaded_artifacts(self) -> None:
        blocked_paths = (
            "ppd/private/devhub_session.json",
            "ppd/tests/fixtures/auth_state.json",
            "ppd/tests/fixtures/browser_state.json",
            "ppd/tests/fixtures/raw_crawl/result.json",
            "ppd/tests/fixtures/downloaded/permit.pdf",
            "ppd/tests/fixtures/traces/trace.zip",
        )
        for blocked_path in blocked_paths:
            with self.subTest(path=blocked_path):
                packet = copy.deepcopy(self.packet)
                packet["artifact_paths"] = [blocked_path]
                self.assert_rejected(packet, "private/session/browser/raw/downloaded artifact")

    def test_rejects_official_action_completion_claims(self) -> None:
        packet = copy.deepcopy(self.packet)
        packet["reviewer_dispositions"][0]["reason"] = "Official action completed by PP&D."
        self.assert_rejected(packet, "official action completed")

    def test_rejects_legal_or_permitting_guarantees(self) -> None:
        packet = copy.deepcopy(self.packet)
        packet["next_safe_action_rows"][0]["action"] = "Tell applicant the permit guaranteed approval."
        self.assert_rejected(packet, "permit guaranteed")

    def test_rejects_live_crawl_or_devhub_claims(self) -> None:
        packet = copy.deepcopy(self.packet)
        packet["workflow_cases"][0]["workflow"] = "DevHub live crawl rehearsal"
        self.assert_rejected(packet, "devhub live crawl")

    def test_rejects_active_mutation_flags(self) -> None:
        packet = copy.deepcopy(self.packet)
        packet["active_mutation_flags"] = {"submit": True}
        self.assert_rejected(packet, "active_mutation_flags enables or requests an active mutation")


if __name__ == "__main__":
    unittest.main()
