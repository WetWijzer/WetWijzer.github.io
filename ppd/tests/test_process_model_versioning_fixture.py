from __future__ import annotations

import copy
import unittest
from pathlib import Path

from ppd.process_model_versioning import (
    load_process_model_version_fixture,
    validate_process_model_version,
)

FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "process_model_versioning"
    / "standard_electrical_trade_permit_version.json"
)


class ProcessModelVersioningFixtureTest(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = load_process_model_version_fixture(FIXTURE_PATH)

    def test_fixture_is_valid_process_model_version(self) -> None:
        self.assertEqual([], validate_process_model_version(self.fixture))

    def test_fixture_records_no_live_source_reads(self) -> None:
        policy = self.fixture["fixture_policy"]
        self.assertTrue(policy["fixture_only"])
        self.assertFalse(policy["live_source_reads_allowed"])
        self.assertFalse(policy["authenticated_devhub_reads_allowed"])

        for evidence in self.fixture["source_evidence_hashes"]:
            self.assertTrue(evidence["synthetic_excerpt"])
            self.assertFalse(evidence["live_read_performed"])

    def test_fixture_links_requirements_guardrails_and_evidence(self) -> None:
        requirement_ids = set(self.fixture["requirement_ids"])
        linked_requirement_ids = set(self.fixture["linked_requirement_evidence"].keys())
        evidence_ids = {
            evidence["source_evidence_id"]
            for evidence in self.fixture["source_evidence_hashes"]
        }

        self.assertEqual(requirement_ids, linked_requirement_ids)
        self.assertGreaterEqual(len(self.fixture["guardrail_bundle_ids"]), 2)

        for linked_evidence_ids in self.fixture["linked_requirement_evidence"].values():
            self.assertTrue(set(linked_evidence_ids).issubset(evidence_ids))

    def test_fixture_has_blocked_readiness_reasons(self) -> None:
        self.assertEqual("blocked_pending_human_review", self.fixture["readiness_status"])
        self.assertGreaterEqual(len(self.fixture["blocked_reasons"]), 3)
        self.assertTrue(
            any("Payment" in reason or "payment" in reason for reason in self.fixture["blocked_reasons"])
        )

    def test_rejects_uncited_process_stage(self) -> None:
        record = copy.deepcopy(self.fixture)
        record["process_stages"][0].pop("source_evidence_ids")

        errors = validate_process_model_version(record)

        self.assertTrue(any("process_stages[0] must cite" in error for error in errors))

    def test_rejects_stale_source_hash(self) -> None:
        record = copy.deepcopy(self.fixture)
        evidence_id = record["source_evidence_hashes"][0]["source_evidence_id"]
        record["current_source_hashes"][evidence_id] = "f" * 64

        errors = validate_process_model_version(record)

        self.assertTrue(any("stale content_sha256" in error for error in errors))

    def test_rejects_unsupported_devhub_path_marked_automatable(self) -> None:
        record = copy.deepcopy(self.fixture)
        record["devhub_paths"][1]["automatable"] = True

        errors = validate_process_model_version(record)

        self.assertTrue(any("unsupported path" in error and "automatable" in error for error in errors))

    def test_rejects_required_document_without_links(self) -> None:
        record = copy.deepcopy(self.fixture)
        record["required_documents"][0]["requirement_ids"] = []
        record["required_documents"][0]["source_evidence_ids"] = []

        errors = validate_process_model_version(record)

        self.assertTrue(any("required_documents[0] must link to at least one requirement_id" in error for error in errors))
        self.assertTrue(any("required_documents[0] must link to source evidence" in error for error in errors))

    def test_rejects_fee_action_without_financial_boundary(self) -> None:
        record = copy.deepcopy(self.fixture)
        record["actions"][1].pop("financial_boundary_classification")

        errors = validate_process_model_version(record)

        self.assertTrue(any("fee/payment action" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
