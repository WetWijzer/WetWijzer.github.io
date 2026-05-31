from __future__ import annotations

import copy
import unittest
from pathlib import Path

from ppd.agent_readiness.inactive_guardrail_promotion_gate_packet_v2 import (
    MUTATION_FLAGS,
    OFFLINE_VALIDATION_COMMANDS,
    PACKET_TYPE,
    InactiveGuardrailPromotionGatePacketV2Error,
    build_inactive_guardrail_promotion_gate_packet_v2,
    load_synthetic_inactive_guardrail_migration_preview_rows_v2,
    validate_inactive_guardrail_promotion_gate_packet_v2,
    validate_synthetic_inactive_guardrail_migration_preview_rows_v2,
)

FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "inactive_guardrail_promotion_gate_packet_v2"
    / "migration_preview_rows_v2.json"
)


class InactiveGuardrailPromotionGatePacketV2Test(unittest.TestCase):
    def setUp(self) -> None:
        self.preview = load_synthetic_inactive_guardrail_migration_preview_rows_v2(FIXTURE_PATH)
        self.packet = build_inactive_guardrail_promotion_gate_packet_v2(self.preview)

    def test_builds_recommendations_only_packet_from_fixture(self) -> None:
        self.assertEqual(PACKET_TYPE, self.packet["packet_type"])
        self.assertTrue(self.packet["fixture_first"])
        self.assertTrue(self.packet["inactive_gate_only"])
        self.assertTrue(self.packet["recommendations_only"])
        self.assertFalse(self.packet["active_guardrail_mutation"])
        self.assertFalse(self.packet["active_prompt_mutation"])
        self.assertFalse(self.packet["active_source_registry_mutation"])
        self.assertFalse(self.packet["devhub_access_performed"])
        self.assertEqual(OFFLINE_VALIDATION_COMMANDS, self.packet["offline_validation_commands"])
        self.assertEqual([], validate_inactive_guardrail_promotion_gate_packet_v2(self.packet))

    def test_emits_promote_hold_and_reject_recommendations_only(self) -> None:
        recommendations = {row["source_row_id"]: row["recommendation"] for row in self.packet["promotion_recommendations"]}

        self.assertEqual("promote", recommendations["predicate.readonly.preview"])
        self.assertEqual("hold", recommendations["temporal.stale.source.hold"])
        self.assertEqual("reject", recommendations["refused.unattended.payment"])
        self.assertEqual({"promote", "hold", "reject"}, set(self.packet["recommendation_counts"]))
        self.assertGreater(self.packet["recommendation_counts"]["promote"], 0)
        self.assertGreater(self.packet["recommendation_counts"]["hold"], 0)
        self.assertGreater(self.packet["recommendation_counts"]["reject"], 0)
        for row in self.packet["promotion_recommendations"]:
            self.assertTrue(row["source_evidence_trace_ids"])
            self.assertEqual(OFFLINE_VALIDATION_COMMANDS, row["validation_commands"])

    def test_validates_source_fixture_sections_and_commands(self) -> None:
        self.assertEqual([], validate_synthetic_inactive_guardrail_migration_preview_rows_v2(self.preview))
        for section in (
            "deterministic_predicates",
            "deontic_rules",
            "temporal_rules",
            "reversible_action_predicates",
            "exact_confirmation_predicates",
            "refused_action_predicates",
            "stale_source_holds",
            "source_evidence_traces",
            "explanation_template_placeholders",
            "reviewer_dispositions",
            "offline_validation_commands",
        ):
            with self.subTest(section=section):
                preview = copy.deepcopy(self.preview)
                preview[section] = []
                errors = validate_synthetic_inactive_guardrail_migration_preview_rows_v2(preview)
                self.assertTrue(any(section in error for error in errors), errors)

    def test_rejects_missing_required_gate_row_fields_and_evidence(self) -> None:
        cases = (
            ("deterministic_predicates", "deterministic_predicate"),
            ("deontic_rules", "deontic_rule"),
            ("temporal_rules", "temporal_rule"),
            ("reversible_action_predicates", "reversible_action"),
            ("exact_confirmation_predicates", "requires_exact_confirmation"),
            ("refused_action_predicates", "refuses_prohibited_action"),
            ("stale_source_holds", "stale_source_hold"),
            ("deterministic_predicates", "source_evidence_trace_ids"),
        )
        for section, field in cases:
            with self.subTest(section=section, field=field):
                preview = copy.deepcopy(self.preview)
                preview[section][0].pop(field, None)
                errors = validate_synthetic_inactive_guardrail_migration_preview_rows_v2(preview)
                self.assertTrue(any(field in error for error in errors), errors)

    def test_rejects_missing_source_trace_reviewer_disposition_and_commands(self) -> None:
        preview = copy.deepcopy(self.preview)
        preview["source_evidence_traces"] = preview["source_evidence_traces"][1:]
        errors = validate_synthetic_inactive_guardrail_migration_preview_rows_v2(preview)
        self.assertTrue(any("source_evidence_trace_ids" in error for error in errors), errors)

        preview = copy.deepcopy(self.preview)
        preview["reviewer_dispositions"] = preview["reviewer_dispositions"][1:]
        errors = validate_synthetic_inactive_guardrail_migration_preview_rows_v2(preview)
        self.assertTrue(any("reviewer disposition" in error for error in errors), errors)

        preview = copy.deepcopy(self.preview)
        preview["offline_validation_commands"] = []
        errors = validate_synthetic_inactive_guardrail_migration_preview_rows_v2(preview)
        self.assertTrue(any("offline_validation_commands" in error for error in errors), errors)

    def test_rejects_private_live_devhub_official_action_and_guarantee_claims(self) -> None:
        packet = copy.deepcopy(self.packet)
        packet["browser_trace_path"] = "trace.har"
        packet["downloaded_artifact_path"] = "permit.pdf"
        packet["private_session_note"] = "DevHub session"
        packet["notes"] = "Opened DevHub session, live crawl completed, application submitted, and permit guaranteed."

        errors = validate_inactive_guardrail_promotion_gate_packet_v2(packet)

        self.assertTrue(any("browser_trace_path" in error for error in errors), errors)
        self.assertTrue(any("downloaded_artifact_path" in error for error in errors), errors)
        self.assertTrue(any("private_session_note" in error for error in errors), errors)
        self.assertTrue(any("legal or permitting guarantees" in error for error in errors), errors)
        self.assertTrue(any("official action" in error or "DevHub access" in error for error in errors), errors)

    def test_rejects_active_mutation_and_promotion_flags(self) -> None:
        for flag in MUTATION_FLAGS:
            with self.subTest(flag=flag):
                packet = copy.deepcopy(self.packet)
                packet[flag] = True
                errors = validate_inactive_guardrail_promotion_gate_packet_v2(packet)
                self.assertTrue(any(flag in error for error in errors), errors)

    def test_builder_fails_closed_on_bad_fixture(self) -> None:
        preview = copy.deepcopy(self.preview)
        preview["offline_validation_commands"] = [["python3", "not-offline.py"]]

        with self.assertRaises(InactiveGuardrailPromotionGatePacketV2Error):
            build_inactive_guardrail_promotion_gate_packet_v2(preview)


if __name__ == "__main__":
    unittest.main()
