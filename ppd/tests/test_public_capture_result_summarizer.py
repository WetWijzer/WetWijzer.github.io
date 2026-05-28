from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from ppd.crawler.public_capture_result_summarizer import (
    PublicCaptureSummaryError,
    summarize_public_capture_results,
)

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "public_capture_summary" / "approved_capture_metadata.json"


class PublicCaptureResultSummarizerTest(unittest.TestCase):
    def load_fixture(self) -> dict:
        return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    def test_summarizes_metadata_only_capture_results(self) -> None:
        summary = summarize_public_capture_results(self.load_fixture())

        self.assertEqual(summary["schema_version"], "ppd-public-capture-summary-v1")
        self.assertEqual(len(summary["source_index_update_candidates"]), 2)
        self.assertEqual(len(summary["extraction_work_items"]), 2)
        self.assertEqual(len(summary["freshness_changes"]), 2)

        candidates = {item["source_id"]: item for item in summary["source_index_update_candidates"]}
        self.assertEqual(candidates["ppd-devhub-faqs"]["update_action"], "upsert_metadata_only_record")
        self.assertTrue(candidates["ppd-devhub-faqs"]["no_raw_body_persisted"])
        self.assertEqual(candidates["ppd-spp-file-naming-standards"]["page_type"], "public_pdf")

        work_items = {item["source_id"]: item for item in summary["extraction_work_items"]}
        self.assertEqual(work_items["ppd-devhub-faqs"]["extraction_kind"], "html_metadata_and_requirement_extraction")
        self.assertEqual(work_items["ppd-spp-file-naming-standards"]["extraction_kind"], "pdf_metadata_and_requirement_extraction")
        self.assertIn("raw_public_page_body", work_items["ppd-spp-file-naming-standards"]["prohibited_inputs"])
        self.assertTrue(work_items["ppd-spp-file-naming-standards"]["human_review_required"])

        freshness = {item["source_id"]: item for item in summary["freshness_changes"]}
        self.assertEqual(freshness["ppd-devhub-faqs"]["status"], "content_hash_changed")
        self.assertEqual(freshness["ppd-devhub-faqs"]["recrawl_priority"], "high")
        self.assertEqual(freshness["ppd-spp-file-naming-standards"]["status"], "new_source")

        prompt_reasons = {item["reason"] for item in summary["human_review_prompts"]}
        self.assertIn("content_hash_changed", prompt_reasons)
        self.assertIn("document_extraction_review", prompt_reasons)

    def test_rejects_raw_body_or_downloaded_pdf_paths(self) -> None:
        fixture = self.load_fixture()
        fixture["captures"][0]["raw_body"] = "not allowed"
        with self.assertRaisesRegex(PublicCaptureSummaryError, "raw public body"):
            summarize_public_capture_results(fixture)

        fixture = self.load_fixture()
        fixture["captures"][1]["downloaded_pdf_path"] = "/tmp/public.pdf"
        with self.assertRaisesRegex(PublicCaptureSummaryError, "downloaded PDF"):
            summarize_public_capture_results(fixture)

    def test_requires_approved_fake_capture_metadata(self) -> None:
        fixture = self.load_fixture()
        fixture["captures"][0]["approved"] = False
        fixture["captures"][0]["approval"] = {"status": "pending"}
        with self.assertRaisesRegex(PublicCaptureSummaryError, "approved"):
            summarize_public_capture_results(fixture)

        fixture = self.load_fixture()
        fixture["captures"][0]["processor_metadata"]["network_requests_made"] = 1
        with self.assertRaisesRegex(PublicCaptureSummaryError, "zero network"):
            summarize_public_capture_results(fixture)

    def test_output_is_deterministic_for_input_order(self) -> None:
        fixture = self.load_fixture()
        reversed_fixture = copy.deepcopy(fixture)
        reversed_fixture["captures"] = list(reversed(reversed_fixture["captures"]))

        self.assertEqual(
            summarize_public_capture_results(fixture),
            summarize_public_capture_results(reversed_fixture),
        )


if __name__ == "__main__":
    unittest.main()
