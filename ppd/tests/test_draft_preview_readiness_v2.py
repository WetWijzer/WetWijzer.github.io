from __future__ import annotations

import json
from pathlib import Path
import unittest

from ppd.draft_preview_readiness_v2 import build_draft_preview_readiness_packet_v2


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "draft_preview_readiness_v2" / "source_packets.json"


class DraftPreviewReadinessPacketV2Test(unittest.TestCase):
    def test_builds_blocked_packet_with_cited_gaps_and_attestations(self) -> None:
        source_packets = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

        packet = build_draft_preview_readiness_packet_v2(source_packets)

        self.assertEqual(packet["packet_id"], "draft_preview_readiness_packet_v2")
        self.assertFalse(packet["ready_for_local_draft_preview"])
        self.assertEqual(packet["readiness_decisions"][0]["outcome"], "block")
        self.assertEqual(len(packet["readiness_decisions"][0]["citations"]), 3)
        self.assertEqual(packet["required_user_facts"][0]["field"], "applicant_legal_name")
        self.assertEqual(packet["missing_document_checks"][0]["document"], "site_plan")
        self.assertEqual(packet["reversible_action_predicates"][0]["predicate"], "preview_writes_only_ephemeral_fixture_output")
        self.assertEqual(packet["exact_confirmation_checkpoints"][0]["checkpoint"], "before_any_non_fixture_document_use")
        self.assertEqual(packet["reviewer_owner_fields"][0]["field"], "readiness_reviewer")
        self.assertTrue(packet["attestations"]["no_live_devhub"])
        self.assertTrue(packet["attestations"]["no_private_documents"])
        self.assertTrue(packet["attestations"]["no_pdf_write"])
        self.assertTrue(packet["attestations"]["no_upload"])
        self.assertTrue(packet["attestations"]["no_guardrail_mutation"])

    def test_allows_local_preview_when_required_inputs_are_complete(self) -> None:
        source_packets = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        gaps = source_packets["process_to_gap_analysis_refresh_packet_v2"]
        gaps["required_user_facts"] = []
        gaps["missing_document_checks"] = []

        packet = build_draft_preview_readiness_packet_v2(source_packets)

        self.assertTrue(packet["ready_for_local_draft_preview"])
        self.assertEqual(packet["readiness_decisions"][0]["outcome"], "allow")


if __name__ == "__main__":
    unittest.main()
