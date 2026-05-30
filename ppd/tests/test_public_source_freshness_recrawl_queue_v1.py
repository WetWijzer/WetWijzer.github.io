from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from ppd.source_freshness.public_source_freshness_recrawl_queue_v1 import validate_public_source_freshness_recrawl_queue_v1

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "source_freshness" / "public_source_freshness_recrawl_queue_v1_valid.json"


class PublicSourceFreshnessRecrawlQueueV1Test(unittest.TestCase):
    def setUp(self) -> None:
        self.packet = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def assertInvalidContains(self, packet: dict, expected: str) -> None:
        result = validate_public_source_freshness_recrawl_queue_v1(packet)
        self.assertFalse(result.valid)
        self.assertTrue(any(expected in error for error in result.errors), result.errors)

    def test_valid_fixture_passes(self) -> None:
        result = validate_public_source_freshness_recrawl_queue_v1(self.packet)
        self.assertTrue(result.valid, result.errors)

    def test_rejects_missing_recrawl_candidate_rows(self) -> None:
        packet = deepcopy(self.packet)
        packet["recrawl_candidate_rows"] = []
        self.assertInvalidContains(packet, "recrawl_candidate_rows must be a non-empty list")

    def test_rejects_required_row_references(self) -> None:
        required_fields = [
            "official_source_anchor_ref",
            "source_family_priority",
            "stale_or_changed_evidence_placeholders",
            "robots_policy_preflight_placeholders",
            "processor_handoff_dry_run_refs",
            "reviewer_approval_placeholders",
        ]
        for field in required_fields:
            with self.subTest(field=field):
                packet = deepcopy(self.packet)
                packet["recrawl_candidate_rows"][0].pop(field)
                self.assertInvalidContains(packet, field)

    def test_rejects_private_raw_live_guarantee_action_and_mutation_content(self) -> None:
        cases = [
            ({"session_state": "state.json"}, "private/authenticated/session/browser artifact"),
            ({"raw_pdf": "bytes"}, "raw crawl/PDF/downloaded data"),
            ({"note": "live recrawl completed successfully"}, "live crawl execution claim"),
            ({"note": "permit will issue after this review"}, "legal or permitting outcome guarantee"),
            ({"note": "submit the DevHub application"}, "consequential DevHub action language"),
            ({"active_prompt_update": True}, "active source/process/guardrail/prompt/release-state mutation"),
        ]
        for extra, expected in cases:
            with self.subTest(expected=expected):
                packet = deepcopy(self.packet)
                packet["recrawl_candidate_rows"][0]["unsafe_probe"] = extra
                self.assertInvalidContains(packet, expected)


if __name__ == "__main__":
    unittest.main()
