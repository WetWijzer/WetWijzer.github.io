from __future__ import annotations

from copy import deepcopy
import unittest
from pathlib import Path

from ppd.source_requirement_traceability_packet_v1 import (
    SAFETY_ATTESTATIONS,
    assert_valid_traceability_packet,
    build_traceability_packet,
    load_json,
    validate_traceability_packet,
)


class SourceRequirementTraceabilityPacketV1Test(unittest.TestCase):
    def setUp(self) -> None:
        fixtures = Path(__file__).parent / "fixtures"
        self.packet = build_traceability_packet(
            source_registry=load_json(fixtures / "change_impact" / "current_sources.json"),
            document_registry=load_json(fixtures / "citation_integrity" / "document_records.json"),
            normalized_document=load_json(
                fixtures / "html_extraction" / "synthetic_ppd_guidance_normalized.json"
            ),
            process_packet=load_json(
                fixtures / "process_model" / "fixture_first_assembly_packet.json"
            ),
        )

    def test_packet_contains_reviewed_requirement_trace_rows(self) -> None:
        rows = self.packet["rows"]
        requirement_ids = {row["requirement_id"] for row in rows}

        self.assertEqual(self.packet["packet_version"], "source_to_requirement_traceability_packet_v1")
        self.assertEqual(self.packet["row_count"], 8)
        self.assertIn("req-action-submit-confirmation", requirement_ids)
        self.assertIn("req-doc-complete-plans", requirement_ids)
        self.assertNotIn("req-draft-unreviewed-note", requirement_ids)
        self.assertEqual(validate_traceability_packet(self.packet), [])

    def test_rows_link_sources_documents_requirements_stages_and_guardrails(self) -> None:
        for row in self.packet["rows"]:
            self.assertTrue(row["source_id"])
            self.assertIn(row["source_id"], self.packet["known_source_ids"])
            self.assertTrue(row["source_evidence_id"])
            self.assertTrue(row["citations"])
            self.assertTrue(row["document_id"])
            self.assertTrue(row["document_section_id"])
            self.assertTrue(row["requirement_id"])
            self.assertIn(row["requirement_id"], self.packet["known_requirement_ids"])
            self.assertTrue(row["process_stage"])
            self.assertEqual(
                self.packet["requirement_process_stage_links"][row["requirement_id"]],
                row["process_stage"],
            )
            self.assertEqual(
                row["affected_guardrail_bundle_ids"],
                ["guardrail-synthetic-residential-plan-review-intake"],
            )
            self.assertEqual(row["freshness_status"], "fixture_current")
            self.assertNotIn("/download", row["canonical_url"])
            self.assertEqual(
                row["reviewer_owner_fields"]["human_review_status"], "reviewed"
            )

    def test_packet_is_offline_and_commit_safe(self) -> None:
        self.assertEqual(self.packet["attestations"], SAFETY_ATTESTATIONS)
        self.assertIn(
            ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
            self.packet["offline_validation_commands"],
        )
        for row in self.packet["rows"]:
            self.assertEqual(row["attestations"], SAFETY_ATTESTATIONS)
            self.assertTrue(row["attestations"]["no_live_crawl"])
            self.assertTrue(row["attestations"]["no_download"])
            self.assertTrue(row["attestations"]["no_raw_body"])
            self.assertTrue(row["attestations"]["no_active_registry_mutation"])

    def test_validation_rejects_missing_links_and_unknown_ids(self) -> None:
        mutations = {
            "uncited": lambda packet: packet["rows"][0].pop("citations"),
            "unknown_source": lambda packet: packet["rows"][0].update(source_id="unknown-source"),
            "unknown_requirement": lambda packet: packet["rows"][0].update(requirement_id="unknown-requirement"),
            "missing_stage": lambda packet: packet["rows"][0].pop("process_stage"),
            "missing_freshness": lambda packet: packet["rows"][0].pop("freshness_status"),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name):
                packet = deepcopy(self.packet)
                mutate(packet)
                self.assertTrue(validate_traceability_packet(packet))

    def test_validation_rejects_private_download_raw_guarantee_and_mutation_content(self) -> None:
        mutations = {
            "private_url": lambda packet: packet["rows"][0].update(canonical_url="https://www.portland.gov/ppd/private/case/123"),
            "download_url": lambda packet: packet["rows"][0].update(canonical_url="https://www.portland.gov/ppd/documents/how-pay-fees/download"),
            "raw_body": lambda packet: packet["rows"][0].update(raw_body="raw response"),
            "guarantee": lambda packet: packet["rows"][0].update(note="permit will be approved"),
            "source_mutation": lambda packet: packet.update(active_source_mutation=True),
            "requirement_mutation": lambda packet: packet["rows"][0].update(active_requirement_mutation=True),
            "process_mutation": lambda packet: packet["rows"][0].update(active_process_mutation=True),
            "guardrail_mutation": lambda packet: packet["rows"][0].update(active_guardrail_mutation=True),
            "monitoring_mutation": lambda packet: packet["rows"][0].update(active_monitoring_mutation=True),
            "release_state_mutation": lambda packet: packet["rows"][0].update(active_release_state_mutation=True),
            "agent_state_mutation": lambda packet: packet["rows"][0].update(active_agent_state_mutation=True),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name):
                packet = deepcopy(self.packet)
                mutate(packet)
                self.assertTrue(validate_traceability_packet(packet))
                with self.assertRaises(ValueError):
                    assert_valid_traceability_packet(packet)


if __name__ == "__main__":
    unittest.main()
