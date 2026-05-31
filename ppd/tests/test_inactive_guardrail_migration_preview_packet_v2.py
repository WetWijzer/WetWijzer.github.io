from __future__ import annotations

import copy
import unittest
from pathlib import Path

from ppd.agent_readiness.inactive_guardrail_migration_preview_packet_v2 import (
    load_inactive_guardrail_migration_preview_packet_v2,
    validate_inactive_guardrail_migration_preview_packet_v2,
)

FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "inactive_guardrail_migration_preview_packet_v2"
    / "valid_packet.json"
)


class InactiveGuardrailMigrationPreviewPacketV2Test(unittest.TestCase):
    def setUp(self) -> None:
        self.packet = load_inactive_guardrail_migration_preview_packet_v2(FIXTURE_PATH)

    def test_valid_packet_passes(self) -> None:
        self.assertEqual([], validate_inactive_guardrail_migration_preview_packet_v2(self.packet))

    def test_rejects_missing_required_sections(self) -> None:
        required_sections = (
            "predicate_rows",
            "deontic_rule_rows",
            "temporal_rule_rows",
            "reversible_action_predicates",
            "exact_confirmation_predicates",
            "refused_action_predicates",
            "stale_source_holds",
            "source_evidence_traces",
            "reviewer_dispositions",
            "validation_commands",
        )
        for section in required_sections:
            with self.subTest(section=section):
                packet = copy.deepcopy(self.packet)
                packet[section] = []
                problems = validate_inactive_guardrail_migration_preview_packet_v2(packet)
                self.assertTrue(any(section in problem for problem in problems), problems)

    def test_rejects_rows_without_source_evidence_traces(self) -> None:
        packet = copy.deepcopy(self.packet)
        packet["predicate_rows"][0]["source_evidence_trace_ids"] = ["missing.trace"]
        problems = validate_inactive_guardrail_migration_preview_packet_v2(packet)
        self.assertTrue(any("missing traces" in problem for problem in problems), problems)

    def test_rejects_private_browser_raw_and_downloaded_artifacts(self) -> None:
        bad_fields = {
            "private_file_path": "/home/user/private.pdf",
            "browser_trace_path": "browser-trace.har",
            "raw_crawl_output": "raw",
            "downloaded_document_path": "/Users/example/Downloads/form.pdf",
        }
        for key, value in bad_fields.items():
            with self.subTest(key=key):
                packet = copy.deepcopy(self.packet)
                packet[key] = value
                problems = validate_inactive_guardrail_migration_preview_packet_v2(packet)
                self.assertTrue(any("artifacts" in problem or "downloaded" in problem for problem in problems), problems)

    def test_rejects_official_live_and_guarantee_claims(self) -> None:
        bad_values = (
            "official action completed",
            "live crawl completed",
            "opened DevHub session",
            "legal guarantee",
            "permit guaranteed",
        )
        for value in bad_values:
            with self.subTest(value=value):
                packet = copy.deepcopy(self.packet)
                packet["claim"] = value
                problems = validate_inactive_guardrail_migration_preview_packet_v2(packet)
                self.assertTrue(any("forbidden official/live/legal claim" in problem for problem in problems), problems)

    def test_rejects_active_mutation_flags(self) -> None:
        mutation_flags = (
            "active_guardrail_mutation_allowed",
            "active_prompt_mutation_allowed",
            "active_requirement_mutation_allowed",
            "active_process_model_mutation_allowed",
            "active_contract_mutation_allowed",
            "active_source_mutation_allowed",
            "active_devhub_surface_mutation_allowed",
            "active_release_state_mutation_allowed",
        )
        for flag in mutation_flags:
            with self.subTest(flag=flag):
                packet = copy.deepcopy(self.packet)
                packet[flag] = True
                problems = validate_inactive_guardrail_migration_preview_packet_v2(packet)
                self.assertTrue(any(flag in problem or "active mutation flag" in problem for problem in problems), problems)


if __name__ == "__main__":
    unittest.main()
