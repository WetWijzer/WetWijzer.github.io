from __future__ import annotations

import json
import unittest
from pathlib import Path

from ppd.crawler.public_recrawl_post_run_metadata_intake_v2 import (
    PublicRecrawlPostRunMetadataIntakeV2PacketError,
    build_public_recrawl_post_run_metadata_intake_v2_packet,
    require_valid_public_recrawl_post_run_metadata_intake_v2_packet,
    validate_public_recrawl_post_run_metadata_intake_v2_packet,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "public_recrawl_post_run_metadata_intake_v2"


def _load_inputs() -> dict:
    with (FIXTURE_DIR / "input_packets.json").open(encoding="utf-8") as handle:
        return json.load(handle)


def _build_packet() -> dict:
    inputs = _load_inputs()
    return build_public_recrawl_post_run_metadata_intake_v2_packet(
        inputs["operator_packet_v2"],
        inputs["source_refresh_runbook"],
        inputs["source_refresh_metadata_intake_fixture"],
    )


class PublicRecrawlPostRunMetadataIntakeV2Test(unittest.TestCase):
    def test_builds_cited_metadata_only_post_run_decisions(self) -> None:
        packet = _build_packet()

        result = validate_public_recrawl_post_run_metadata_intake_v2_packet(packet)

        self.assertTrue(result.valid, result.errors)
        self.assertEqual("ppd_public_recrawl_post_run_metadata_intake_v2_packet", packet["packet_type"])
        self.assertEqual(2, packet["packet_version"])
        self.assertEqual(2, len(packet["captured_url_decisions"]))
        first_decision = packet["captured_url_decisions"][0]
        self.assertEqual("metadata_placeholder_captured", first_decision["decision"])
        self.assertIn("content_hash", first_decision["capture_placeholder"])
        self.assertIn("ppd-plan-official-source-anchors-20260508", first_decision["source_evidence_ids"])
        self.assertIn("robots-evidence:www.portland.gov:2026-05-08", first_decision["source_evidence_ids"])
        self.assertEqual(1, len(packet["skipped_source_reasons"]))
        self.assertEqual(
            "operator_not_selected_for_metadata_only_capture",
            packet["skipped_source_reasons"][0]["skipped_reason"],
        )
        self.assertTrue(packet["attestations"]["no_live_crawl"])
        self.assertTrue(packet["attestations"]["no_processor"])
        self.assertTrue(packet["attestations"]["no_raw_body"])
        self.assertTrue(packet["attestations"]["no_download"])
        self.assertTrue(packet["attestations"]["no_source_registry_mutation"])
        require_valid_public_recrawl_post_run_metadata_intake_v2_packet(packet)

    def test_rejects_uncited_captured_url_decision(self) -> None:
        packet = _build_packet()
        packet["captured_url_decisions"][0]["source_evidence_ids"] = []

        result = validate_public_recrawl_post_run_metadata_intake_v2_packet(packet)

        self.assertFalse(result.valid)
        self.assertIn(
            "captured_url_decisions[0].source_evidence_ids must cite at least one source",
            result.errors,
        )

    def test_rejects_side_effect_claims(self) -> None:
        packet = _build_packet()
        packet["side_effects"]["processor_invoked"] = True

        result = validate_public_recrawl_post_run_metadata_intake_v2_packet(packet)

        self.assertFalse(result.valid)
        self.assertIn("$.side_effects.processor_invoked must be false", result.errors)

    def test_rejects_unsafe_operator_packet_before_build(self) -> None:
        inputs = _load_inputs()
        inputs["operator_packet_v2"]["operator_controls"]["processor_invoked"] = True

        with self.assertRaises(PublicRecrawlPostRunMetadataIntakeV2PacketError):
            build_public_recrawl_post_run_metadata_intake_v2_packet(
                inputs["operator_packet_v2"],
                inputs["source_refresh_runbook"],
                inputs["source_refresh_metadata_intake_fixture"],
            )


if __name__ == "__main__":
    unittest.main()
