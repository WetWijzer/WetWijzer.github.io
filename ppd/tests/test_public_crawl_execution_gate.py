from __future__ import annotations

import copy
import json
import unittest
from datetime import datetime, timezone
from pathlib import Path

from ppd.crawler.public_crawl_execution_gate import evaluate_public_crawl_execution_gate


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "public_crawl_execution_gate" / "readiness_handoff_packet.json"
NOW = datetime(2026, 5, 27, tzinfo=timezone.utc)


def _fixture() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _decision(packet: dict) -> dict:
    return evaluate_public_crawl_execution_gate(packet, now=NOW).to_dict()


def _errors(decision: dict) -> str:
    return "\n".join(error for check in decision["checks"] for error in check["errors"])


class PublicCrawlExecutionGateTest(unittest.TestCase):
    def test_safe_fixture_is_eligible_for_dry_run_only(self) -> None:
        decision = _decision(_fixture())

        self.assertEqual(decision["decision"], "eligible_dry_run_only")
        self.assertTrue(decision["eligible"])
        self.assertTrue(decision["dry_run_only"])
        self.assertFalse(decision["live_network_permitted"])
        self.assertEqual(decision["planned_execution"]["network_requests"], 0)
        self.assertEqual(decision["planned_execution"]["processor_invocations"], 0)
        self.assertEqual(decision["planned_execution"]["raw_artifacts_written"], 0)
        self.assertEqual(decision["planned_execution"]["downloaded_documents_written"], 0)
        self.assertEqual({check["name"] for check in decision["checks"]}, {
            "dry_run_only",
            "readiness_handoff",
            "allowlist",
            "robots_and_policy",
            "rate_limit",
            "processor_contract",
            "metadata_only_outputs",
        })
        self.assertTrue(all(check["passed"] for check in decision["checks"]))

    def test_gate_refuses_live_network_and_raw_output_evidence(self) -> None:
        packet = copy.deepcopy(_fixture())
        packet["live_network"] = True
        packet["planned_outputs"][0]["raw_body"] = "not permitted"

        decision = _decision(packet)

        self.assertEqual(decision["decision"], "ineligible")
        self.assertFalse(decision["eligible"])
        errors = _errors(decision)
        self.assertIn("live", errors)
        self.assertIn("raw body", errors)

    def test_gate_refuses_stale_readiness_packets(self) -> None:
        packet = copy.deepcopy(_fixture())
        packet["source_anchors"][0]["observed_at"] = "2026-04-01T00:00:00Z"

        decision = _decision(packet)

        self.assertEqual(decision["decision"], "ineligible")
        errors = _errors(decision)
        self.assertIn("source_anchors[0] timestamp is stale", errors)

    def test_gate_refuses_downloaded_document_paths(self) -> None:
        packet = copy.deepcopy(_fixture())
        packet["planned_outputs"][0]["downloaded_document_path"] = "ppd/data/downloaded-public-documents/form.pdf"

        decision = _decision(packet)

        self.assertEqual(decision["decision"], "ineligible")
        errors = _errors(decision)
        self.assertIn("downloaded document", errors)
        self.assertIn("planned_outputs[0].downloaded_document_path", errors)

    def test_gate_refuses_private_or_authenticated_urls(self) -> None:
        packet = copy.deepcopy(_fixture())
        packet["urls"].append("https://devhub.portlandoregon.gov/login")

        decision = _decision(packet)

        self.assertEqual(decision["decision"], "ineligible")
        errors = _errors(decision)
        self.assertIn("authenticated or private", errors)
        self.assertIn("private_or_authenticated", errors)

    def test_gate_refuses_missing_rate_limit_bucket(self) -> None:
        packet = copy.deepcopy(_fixture())
        packet.pop("rate_limit")

        decision = _decision(packet)

        self.assertEqual(decision["decision"], "ineligible")
        errors = _errors(decision)
        self.assertIn("positive crawl rate limit", errors)
        self.assertIn("rate_limit must be a mapping", errors)

    def test_gate_refuses_missing_processor_contract_evidence(self) -> None:
        packet = copy.deepcopy(_fixture())
        packet.pop("processor_handoff_manifest")

        decision = _decision(packet)

        self.assertEqual(decision["decision"], "ineligible")
        errors = _errors(decision)
        self.assertIn("processor_handoff_manifest is required", errors)

    def test_gate_refuses_non_allowlisted_processor_url(self) -> None:
        packet = copy.deepcopy(_fixture())
        job = packet["processor_handoff_manifest"]["processorJobs"][0]
        job["sourceUrl"] = "https://example.com/ppd"
        job["canonicalUrl"] = "https://example.com/ppd"
        job["arguments"]["url"] = "https://example.com/ppd"

        decision = _decision(packet)

        self.assertEqual(decision["decision"], "ineligible")
        errors = _errors(decision)
        self.assertIn("host_not_allowlisted", errors)
        self.assertIn("not PP&D allowlisted", errors)


if __name__ == "__main__":
    unittest.main()
