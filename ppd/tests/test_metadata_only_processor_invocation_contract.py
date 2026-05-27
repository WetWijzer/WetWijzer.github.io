from __future__ import annotations

import json
import unittest
from pathlib import Path
from typing import Any, Mapping

from ppd.contracts.crawl_processor_handoff import assert_valid_crawl_processor_handoff_manifest


FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "processor_invocation_contract"
    / "metadata_only_public_crawl.json"
)

REQUIRED_POLICY_REASONS = {
    "public_ppd_allowlisted",
    "robots_allowed",
    "no_persist_approved",
}

FORBIDDEN_KEYS = {
    "body",
    "rawBody",
    "raw_body",
    "responseBody",
    "response_body",
    "html",
    "text",
    "content",
    "bytes",
    "archivePath",
    "archive_path",
    "warcPath",
    "warc_path",
    "downloadPath",
    "download_path",
    "documentPath",
    "document_path",
    "pdfPath",
    "pdf_path",
}


def load_fixture() -> dict[str, Any]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def walk_mappings(value: Any) -> list[tuple[str, Any]]:
    found: list[tuple[str, Any]] = []

    def visit(current: Any, path: str) -> None:
        if isinstance(current, Mapping):
            for key, child in current.items():
                child_path = f"{path}.{key}" if path else str(key)
                found.append((child_path, child))
                visit(child, child_path)
        elif isinstance(current, list):
            for index, child in enumerate(current):
                child_path = f"{path}.{index}" if path else str(index)
                visit(child, child_path)

    visit(value, "")
    return found


class MetadataOnlyProcessorInvocationContractTest(unittest.TestCase):
    def test_fixture_conforms_to_existing_handoff_manifest_contract(self) -> None:
        fixture = load_fixture()
        assert_valid_crawl_processor_handoff_manifest(fixture)

    def test_intentions_map_to_exact_adapter_inputs(self) -> None:
        fixture = load_fixture()
        mappings = fixture["intentToAdapterMappings"]
        jobs_by_id = {job["id"]: job for job in fixture["processorJobs"]}

        self.assertEqual(2, len(mappings))
        for mapping in mappings:
            intent = mapping["intent"]
            adapter_inputs = mapping["adapterInputs"]
            invocation = adapter_inputs["processorInvocation"]
            capability = adapter_inputs["processorCapability"]
            job = jobs_by_id[intent["id"]]

            self.assertTrue(intent["approved"])
            self.assertEqual("metadata_only_public_crawl", intent["kind"])
            self.assertEqual(intent["sourceUrl"], invocation["url"])
            self.assertEqual(intent["canonicalUrl"], invocation["canonicalUrl"])
            self.assertEqual(job["sourceUrl"], invocation["url"])
            self.assertEqual(job["canonicalUrl"], invocation["canonicalUrl"])
            self.assertEqual(job["operation"], invocation["operation"])
            self.assertEqual(job["outputManifestRef"], invocation["outputManifestRef"])
            self.assertEqual(job["processor"]["name"], capability["name"])
            self.assertEqual(job["processor"]["family"], capability["family"])
            self.assertEqual(job["processor"]["module"], capability["moduleRef"])
            self.assertEqual(job["processor"]["backendPath"], capability["backendPath"])
            self.assertEqual(job["arguments"]["url"], invocation["url"])

    def test_policy_preflight_and_rate_limit_bucket_are_explicit(self) -> None:
        fixture = load_fixture()
        for mapping in fixture["intentToAdapterMappings"]:
            adapter_inputs = mapping["adapterInputs"]
            policy = adapter_inputs["policyPreflight"]
            bucket = adapter_inputs["rateLimitBucket"]

            self.assertEqual("allow", policy["decision"])
            self.assertTrue(REQUIRED_POLICY_REASONS.issubset(set(policy["reasons"])))
            self.assertEqual("allow", policy["robotsPolicy"])
            self.assertGreater(bucket["maxRequestsPerMinute"], 0)
            self.assertLessEqual(bucket["maxRequestsPerMinute"], 6)
            self.assertGreaterEqual(bucket["minDelaySeconds"], 10)
            self.assertEqual(1, bucket["burstLimit"])
            self.assertTrue(bucket["scope"].startswith("host:"))

    def test_processor_capability_is_metadata_only_without_importing_processors(self) -> None:
        fixture = load_fixture()
        for mapping in fixture["intentToAdapterMappings"]:
            capability = mapping["adapterInputs"]["processorCapability"]
            self.assertIn(
                capability["family"],
                {"web_archiving", "legal_scraper"},
            )
            self.assertTrue(
                capability["moduleRef"].startswith(
                    "ipfs_datasets_py.processors.web_archiving"
                )
                or capability["moduleRef"].startswith(
                    "ipfs_datasets_py.processors.legal_scrapers"
                )
            )
            self.assertEqual(
                "metadata_capture_without_raw_body_persistence",
                capability["requiredCapability"],
            )
            self.assertFalse(capability["importPermittedInFixture"])

    def test_no_raw_body_or_private_artifact_inputs_are_present(self) -> None:
        fixture = load_fixture()
        for path, value in walk_mappings(fixture):
            field_name = path.rsplit(".", 1)[-1]
            self.assertNotIn(field_name, FORBIDDEN_KEYS, path)
            if isinstance(value, str):
                lowered = value.lower()
                self.assertNotIn("/home/", lowered, path)
                self.assertNotIn("/tmp/", lowered, path)
                self.assertNotIn("cookie", lowered, path)
                self.assertNotIn("password", lowered, path)

        for mapping in fixture["intentToAdapterMappings"]:
            invocation = mapping["adapterInputs"]["processorInvocation"]
            guarantee = mapping["adapterInputs"]["rawBodyGuarantee"]
            self.assertTrue(invocation["metadataOnly"])
            self.assertTrue(invocation["manifestOnly"])
            self.assertFalse(invocation["persistRawBody"])
            self.assertFalse(invocation["storeRawResponse"])
            self.assertFalse(invocation["downloadDocuments"])
            self.assertTrue(guarantee["noRawBodyPersisted"])
            self.assertTrue(guarantee["noDownloadedDocuments"])
            self.assertTrue(guarantee["noBrowserTrace"])
            self.assertTrue(guarantee["noAuthenticatedState"])
            self.assertTrue(guarantee["commitSafe"])


if __name__ == "__main__":
    unittest.main()
