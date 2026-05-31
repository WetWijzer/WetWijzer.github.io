from __future__ import annotations

import json
import unittest
from pathlib import Path

from ppd.crawler.source_freshness_scheduler_packet_v2 import (
    require_valid_source_freshness_scheduler_packet_v2,
    validate_source_freshness_scheduler_packet_v2,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "source_freshness_scheduler_packet_v2"


class SourceFreshnessSchedulerPacketV2Test(unittest.TestCase):
    def test_valid_fixture_passes(self) -> None:
        packet = self._valid_packet()
        result = validate_source_freshness_scheduler_packet_v2(packet)
        self.assertTrue(result.valid, result.errors)
        require_valid_source_freshness_scheduler_packet_v2(packet)

    def test_rejects_missing_required_scheduler_fields(self) -> None:
        packet = self._valid_packet()
        row = packet["scheduler_rows"][0]
        row["source_anchor"] = ""
        row["recrawl_frequency"] = ""
        row["stale_source_hold_triggers"] = []
        row["affected_surface_categories"] = []
        row["skipped_authenticated_url_note"] = ""
        packet["validation_commands"] = []

        errors = validate_source_freshness_scheduler_packet_v2(packet).errors

        self.assertIn("scheduler_rows[0].source_anchor is required", errors)
        self.assertIn("scheduler_rows[0].recrawl_frequency is required", errors)
        self.assertIn("scheduler_rows[0].stale_source_hold_triggers must not be empty", errors)
        self.assertIn("scheduler_rows[0].affected_surface_categories must not be empty", errors)
        self.assertIn("scheduler_rows[0].skipped_authenticated_url_note is required", errors)
        self.assertIn("validation_commands must include at least one offline validation command", errors)

    def test_rejects_private_live_guarantee_and_mutation_content(self) -> None:
        packet = self._valid_packet()
        packet["live_crawl_claim"] = "live crawl completed"
        packet["artifact_ref"] = "private/session/storage_state/auth_state.json"
        packet["operator_note"] = "Permit will be issued after this packet is accepted."
        packet["side_effect_boundary"]["active_source_mutation"] = True
        packet["side_effect_boundary"]["active_requirement_mutation"] = True
        packet["side_effect_boundary"]["active_guardrail_mutation"] = True
        packet["side_effect_boundary"]["active_process_model_mutation"] = True
        packet["side_effect_boundary"]["active_contract_mutation"] = True
        packet["side_effect_boundary"]["active_prompt_mutation"] = True
        packet["side_effect_boundary"]["active_devhub_surface_mutation"] = True
        packet["side_effect_boundary"]["active_release_state_mutation"] = True
        packet["side_effect_boundary"]["live_crawl_performed"] = True
        packet["side_effect_boundary"]["downloaded_artifacts_committed"] = True

        errors = validate_source_freshness_scheduler_packet_v2(packet).errors
        joined = "\n".join(errors)

        self.assertIn("live_crawl_claim must be false or empty", joined)
        self.assertIn("auth_state", joined)
        self.assertIn("permit will be issued", joined)
        self.assertIn("side_effect_boundary.active_source_mutation must be false", errors)
        self.assertIn("side_effect_boundary.active_requirement_mutation must be false", errors)
        self.assertIn("side_effect_boundary.active_guardrail_mutation must be false", errors)
        self.assertIn("side_effect_boundary.active_process_model_mutation must be false", errors)
        self.assertIn("side_effect_boundary.active_contract_mutation must be false", errors)
        self.assertIn("side_effect_boundary.active_prompt_mutation must be false", errors)
        self.assertIn("side_effect_boundary.active_devhub_surface_mutation must be false", errors)
        self.assertIn("side_effect_boundary.active_release_state_mutation must be false", errors)
        self.assertIn("side_effect_boundary.live_crawl_performed must be false", errors)
        self.assertIn("side_effect_boundary.downloaded_artifacts_committed must be false", errors)

    def _valid_packet(self) -> dict[str, object]:
        return json.loads((FIXTURE_DIR / "valid_packet.json").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
