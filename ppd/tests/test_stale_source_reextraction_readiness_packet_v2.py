from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from ppd.stale_source_reextraction_readiness_packet_v2 import (
    assert_valid_stale_source_reextraction_readiness_packet_v2,
    validate_stale_source_reextraction_readiness_packet_v2,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "stale_source_reextraction_readiness_packet_v2"


class StaleSourceReextractionReadinessPacketV2Test(unittest.TestCase):
    def load_valid_packet(self) -> dict:
        with (FIXTURE_DIR / "valid_packet.json").open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def test_valid_fixture_passes(self) -> None:
        packet = self.load_valid_packet()
        self.assertEqual([], validate_stale_source_reextraction_readiness_packet_v2(packet))
        assert_valid_stale_source_reextraction_readiness_packet_v2(packet)

    def test_rejects_missing_required_packet_sections(self) -> None:
        for section in (
            "candidate_rows",
            "source_evidence_refresh_placeholders",
            "stale_hold_carry_forward_notes",
            "requirement_review_placeholders",
            "guardrail_recompile_prerequisites",
            "reviewer_dispositions",
            "validation_commands",
        ):
            packet = self.load_valid_packet()
            packet[section] = []
            issues = validate_stale_source_reextraction_readiness_packet_v2(packet)
            self.assertIn("missing or empty " + section, issues)

    def test_candidate_row_references_are_required(self) -> None:
        packet = self.load_valid_packet()
        row = packet["candidate_rows"][0]
        row["source_evidence_refresh_placeholder_ids"] = []
        row["stale_hold_carry_forward_note_ids"] = []
        row["requirement_review_placeholder_ids"] = []
        row["guardrail_recompile_prerequisite_ids"] = []
        row["reviewer_disposition_ids"] = []

        issues = validate_stale_source_reextraction_readiness_packet_v2(packet)

        self.assertIn("missing source-evidence refresh placeholder references for candidate-single-pdf-guidance-stale", issues)
        self.assertIn("missing stale-hold carry-forward note references for candidate-single-pdf-guidance-stale", issues)
        self.assertIn("missing requirement-review placeholder references for candidate-single-pdf-guidance-stale", issues)
        self.assertIn("missing guardrail-recompile prerequisite references for candidate-single-pdf-guidance-stale", issues)
        self.assertIn("missing reviewer disposition references for candidate-single-pdf-guidance-stale", issues)

    def test_rejects_placeholder_and_disposition_claims_that_do_not_fail_closed(self) -> None:
        packet = self.load_valid_packet()
        packet["source_evidence_refresh_placeholders"][0]["live_fetch_allowed"] = True
        packet["source_evidence_refresh_placeholders"][0]["raw_body_persistence_allowed"] = True
        packet["stale_hold_carry_forward_notes"][0]["hold_carries_forward"] = False
        packet["requirement_review_placeholders"][0]["human_review_required"] = False
        packet["guardrail_recompile_prerequisites"][0]["satisfied"] = True
        packet["reviewer_dispositions"][0]["disposition"] = "approved"
        packet["reviewer_dispositions"][0]["mutation_allowed"] = True

        joined = "\n".join(validate_stale_source_reextraction_readiness_packet_v2(packet))

        self.assertIn("must disable live fetch", joined)
        self.assertIn("must disable raw body persistence", joined)
        self.assertIn("must carry the hold forward", joined)
        self.assertIn("must require human review", joined)
        self.assertIn("must remain unsatisfied", joined)
        self.assertIn("must remain pending", joined)
        self.assertIn("must not allow mutation", joined)

    def test_rejects_raw_artifacts_live_claims_guarantees_and_mutation_flags(self) -> None:
        packet = self.load_valid_packet()
        packet["notes"] = [
            "raw downloaded body artifact was retained",
            "live crawl completed for this packet",
            "permit will be issued after this review",
            "enable active guardrail update now",
        ]
        packet["mutation_flags"]["active_source_mutation"] = True
        packet["active_requirement_mutation"] = True
        packet["active_guardrail_mutation"] = True
        packet["active_prompt_mutation"] = True
        packet["active_contract_mutation"] = True
        packet["active_devhub_surface_mutation"] = True
        packet["active_release_state_mutation"] = True

        joined = "\n".join(validate_stale_source_reextraction_readiness_packet_v2(packet))

        self.assertIn("raw downloaded body artifact rejected", joined)
        self.assertIn("live crawl or DevHub claim rejected", joined)
        self.assertIn("legal or permitting guarantee rejected", joined)
        self.assertIn("active mutation language rejected", joined)
        self.assertIn("active mutation flag must be false at packet.mutation_flags.active_source_mutation", joined)
        self.assertIn("active mutation flag must be false at packet.active_requirement_mutation", joined)
        self.assertIn("active mutation flag must be false at packet.active_guardrail_mutation", joined)
        self.assertIn("active mutation flag must be false at packet.active_prompt_mutation", joined)
        self.assertIn("active mutation flag must be false at packet.active_contract_mutation", joined)
        self.assertIn("active mutation flag must be false at packet.active_devhub_surface_mutation", joined)
        self.assertIn("active mutation flag must be false at packet.active_release_state_mutation", joined)

    def test_rejects_missing_required_validation_commands(self) -> None:
        packet = self.load_valid_packet()
        packet["validation_commands"] = [["python3", "-m", "unittest", "discover", "-s", "ppd/tests", "-p", "test_*.py"]]

        joined = "\n".join(validate_stale_source_reextraction_readiness_packet_v2(packet))

        self.assertIn("missing validation command: python3 -m unittest ppd.tests.test_stale_source_reextraction_readiness_packet_v2", joined)
        self.assertIn("missing validation command: python3 ppd/daemon/ppd_daemon.py --self-test", joined)

    def test_rejects_live_or_browser_validation_commands(self) -> None:
        packet = self.load_valid_packet()
        packet["validation_commands"] = copy.deepcopy(packet["validation_commands"])
        packet["validation_commands"].append(["python3", "-m", "playwright", "open", "https://devhub.portlandoregon.gov"])

        issues = validate_stale_source_reextraction_readiness_packet_v2(packet)

        self.assertIn("validation commands must remain offline and fixture-first", issues)


if __name__ == "__main__":
    unittest.main()
