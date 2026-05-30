from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import json
import unittest

from ppd.agent_readiness.draft_preview_bridge_v1_user_gap_analysis import (
    build_user_gap_analysis_from_packet,
    load_fixture_packet,
    validate_user_gap_analysis_bridge_v1_output,
    validate_user_gap_analysis_bridge_v1_packet,
)


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "agent_readiness" / "draft_preview_bridge_v1_validation_packet.json"


class DraftPreviewBridgeV1ValidationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.packet = load_fixture_packet(FIXTURE_PATH)

    def test_valid_fixture_builds_cited_offline_analysis(self) -> None:
        analysis = build_user_gap_analysis_from_packet(self.packet)

        self.assertEqual(analysis["bridge_version"], "draft_preview_bridge_v1")
        self.assertEqual(analysis["process_id"], "single_pdf_process")
        self.assertTrue(analysis["cited_missing_fact_prompts"])
        self.assertTrue(analysis["field_level_draft_blockers"])
        validate_user_gap_analysis_bridge_v1_output(analysis)

    def test_rejects_uncited_prompt_source(self) -> None:
        packet = deepcopy(self.packet)
        packet["process_model_fixture"]["required_user_facts"][0]["citation_ids"] = []

        with self.assertRaisesRegex(ValueError, "uncited required fact"):
            validate_user_gap_analysis_bridge_v1_packet(packet)

    def test_rejects_unsupported_process_id(self) -> None:
        packet = deepcopy(self.packet)
        packet["handoff_packet_v4"]["process_id"] = "unsupported_private_process"

        with self.assertRaisesRegex(ValueError, "unsupported process id"):
            validate_user_gap_analysis_bridge_v1_packet(packet)

    def test_rejects_missing_blocker_explanation_in_output(self) -> None:
        analysis = build_user_gap_analysis_from_packet(self.packet)
        analysis["field_level_draft_blockers"][0]["reasons"] = []

        with self.assertRaisesRegex(ValueError, "missing blocker explanation"):
            validate_user_gap_analysis_bridge_v1_output(analysis)

    def test_rejects_ungrounded_draft_value(self) -> None:
        packet = deepcopy(self.packet)
        packet["handoff_packet_v4"]["draft_fields"][1] = {
            "field_id": "project_description",
            "label": "Project description",
            "requires_fact_ids": ["project_description"],
            "proposed_value": "Detached garage conversion",
            "value_source_fact_ids": ["missing_fact"],
        }

        with self.assertRaisesRegex(ValueError, "references unknown fact"):
            validate_user_gap_analysis_bridge_v1_packet(packet)

    def test_rejects_private_or_authenticated_facts_and_raw_artifacts(self) -> None:
        packet = deepcopy(self.packet)
        packet["user_gap_fixture"]["known_facts"]["private_upload"] = {
            "value": "/home/alex/private-plan.pdf",
            "privacy_classification": "private",
        }
        packet["handoff_packet_v4"]["screenshot_path"] = "trace.zip"

        with self.assertRaisesRegex(ValueError, "private|raw"):
            validate_user_gap_analysis_bridge_v1_packet(packet)

    def test_rejects_guarantees_official_action_language_and_mutation_flags(self) -> None:
        packet = deepcopy(self.packet)
        packet["guardrail_fixture"]["next_safe_read_only_actions"][0]["label"] = "Submit the application and permit will issue"
        packet["guardrail_fixture"]["active_guardrail_mutation"] = True

        with self.assertRaisesRegex(ValueError, "official-action|guarantee|mutation"):
            validate_user_gap_analysis_bridge_v1_packet(packet)

    def test_fixture_file_is_json_object(self) -> None:
        with FIXTURE_PATH.open("r", encoding="utf-8") as handle:
            self.assertIsInstance(json.load(handle), dict)


if __name__ == "__main__":
    unittest.main()
