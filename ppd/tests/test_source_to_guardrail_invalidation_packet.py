"""Validate fixture-first source-to-guardrail invalidation packets."""

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from ppd.source_to_guardrail_invalidation import packet_from_dict


FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "source_to_guardrail_invalidation"
    / "single_pdf_source_change_packet.json"
)


class SourceToGuardrailInvalidationPacketTest(unittest.TestCase):
    def load_fixture(self) -> dict[str, object]:
        return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    def test_fixture_maps_reviewed_source_change_to_guardrail_invalidation(self) -> None:
        packet = packet_from_dict(self.load_fixture())

        self.assertEqual([], packet.validate())
        self.assertFalse(packet.regenerated_guardrails_marked_current)
        self.assertEqual(
            {
                "document-preparation": ("req-single-pdf-drawings-together",),
                "upload-staging": ("req-supporting-documents-separate-pdfs",),
            },
            packet.affected_requirement_ids_by_stage(),
        )
        self.assertEqual(
            {
                "pred-single-pdf-drawing-bundle-required": "blocked_pending_human_review",
                "pred-supporting-documents-not-in-plan-set": "blocked_pending_human_review",
            },
            packet.cache_status_by_predicate(),
        )

    def test_rejects_invented_source_change_kind(self) -> None:
        data = self.load_fixture()
        source_change = data["source_change"]
        assert isinstance(source_change, dict)
        source_change["change_kind"] = "llm_invented_change"
        source_change["reviewed_freshness_status"] = "invented_current"

        errors = packet_from_dict(data).validate()

        self.assertIn("source freshness change kind must be reviewed public evidence, not an invented change", errors)
        self.assertIn("source freshness change reviewed_freshness_status must be a reviewed public change status", errors)

    def test_rejects_missing_affected_requirement_and_predicate_coverage(self) -> None:
        data = self.load_fixture()
        stages = data["affected_process_stages"]
        prompts = data["human_review_prompts"]
        caches = data["agent_cache_statuses"]
        assert isinstance(stages, list)
        assert isinstance(prompts, list)
        assert isinstance(caches, list)
        stages.pop()
        prompts.pop()
        caches.pop()

        errors = packet_from_dict(data).validate()

        self.assertIn(
            "affected requirement req-supporting-documents-separate-pdfs is missing from affected_process_stages",
            errors,
        )
        self.assertIn(
            "affected requirement req-supporting-documents-separate-pdfs is missing from human review prompts",
            errors,
        )
        self.assertIn(
            "guardrail predicate pred-supporting-documents-not-in-plan-set is missing an agent cache status",
            errors,
        )

    def test_regenerated_guardrail_cannot_be_marked_current_before_review(self) -> None:
        data = self.load_fixture()
        mutated = copy.deepcopy(data)
        assert isinstance(mutated, dict)
        mutated["regenerated_guardrails_marked_current"] = True
        predicates = mutated["guardrail_predicate_invalidations"]
        assert isinstance(predicates, list)
        first_predicate = predicates[0]
        assert isinstance(first_predicate, dict)
        first_predicate["regenerated_guardrail_status"] = "current"

        errors = packet_from_dict(mutated).validate()

        self.assertIn("regenerated guardrails must not be marked current in an invalidation packet", errors)
        self.assertIn(
            "guardrail predicate pred-single-pdf-drawing-bundle-required regenerated guardrail must not be current before review",
            errors,
        )

    def test_rejects_stale_cache_status_marked_current(self) -> None:
        data = self.load_fixture()
        caches = data["agent_cache_statuses"]
        assert isinstance(caches, list)
        first_cache = caches[0]
        assert isinstance(first_cache, dict)
        first_cache["status"] = "current"

        errors = packet_from_dict(data).validate()

        self.assertIn(
            "agent cache status agent-cache:process-single-pdf-plan-review:document-preparation must not be marked current after source change",
            errors,
        )
        self.assertIn(
            "agent cache status agent-cache:process-single-pdf-plan-review:document-preparation must block current use",
            errors,
        )

    def test_fixture_rejects_raw_body_fields_and_downloaded_document_paths(self) -> None:
        raw_data = self.load_fixture()
        assert isinstance(raw_data, dict)
        raw_data["raw_body"] = "not commit safe"
        with self.assertRaisesRegex(ValueError, "forbidden field 'raw_body'"):
            packet_from_dict(raw_data)

        path_data = self.load_fixture()
        notes = path_data["safety_notes"]
        assert isinstance(notes, list)
        notes.append("downloaded to /home/example/Downloads/private-plan.pdf")
        with self.assertRaisesRegex(ValueError, "forbidden private or downloaded document path"):
            packet_from_dict(path_data)

    def test_rejects_private_or_authenticated_urls(self) -> None:
        data = self.load_fixture()
        source_change = data["source_change"]
        assert isinstance(source_change, dict)
        source_change["canonical_url"] = "https://devhub.portlandoregon.gov/permit/private-case-123"

        with self.assertRaisesRegex(ValueError, "forbidden private or authenticated URL"):
            packet_from_dict(data)

    def test_rejects_uncited_predicate_changes(self) -> None:
        data = self.load_fixture()
        predicates = data["guardrail_predicate_invalidations"]
        assert isinstance(predicates, list)
        first_predicate = predicates[0]
        assert isinstance(first_predicate, dict)
        first_predicate["source_evidence_ids"] = ["invented-evidence-id"]

        errors = packet_from_dict(data).validate()

        self.assertIn(
            "guardrail predicate pred-single-pdf-drawing-bundle-required cites unknown source_evidence_ids",
            errors,
        )

    def test_rejects_automatic_promotion_without_human_review(self) -> None:
        data = self.load_fixture()
        data["automatic_promotion_requested"] = True
        prompts = data["human_review_prompts"]
        assert isinstance(prompts, list)
        prompts.clear()

        errors = packet_from_dict(data).validate()

        self.assertIn("automatic promotion without human review is not allowed", errors)
        self.assertIn("packet requires human review prompts", errors)


if __name__ == "__main__":
    unittest.main()
