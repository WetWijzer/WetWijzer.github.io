from __future__ import annotations

import unittest

from ppd.crawler.public_freshness_reviewer_handoff_v1 import (
    PACKET_TYPE,
    PACKET_VERSION,
    require_valid_public_freshness_reviewer_handoff_v1,
    validate_public_freshness_reviewer_handoff_v1,
)


def _valid_packet() -> dict:
    return {
        "packet_type": PACKET_TYPE,
        "packet_version": PACKET_VERSION,
        "fixture_first": True,
        "metadata_only": True,
        "live_crawler_executed": False,
        "processor_completed": False,
        "registry_mutation_active": False,
        "guardrail_mutation_active": False,
        "monitoring_mutation_active": False,
        "release_state_mutation_active": False,
        "agent_state_mutation_active": False,
        "handoff_rows": [
            {
                "row_id": "freshness-review-row-001",
                "canonical_url": "https://www.portland.gov/ppd/devhub-faqs",
                "source_citations": ["source:ppd-devhub-faqs#updated-date"],
                "affected_ids": {
                    "source_ids": ["source:ppd-devhub-faqs"],
                    "requirement_ids": ["requirement:devhub-public-faq-refresh"],
                },
                "reviewer_owner_fields": {
                    "reviewer_owner_id": "public-freshness-reviewer",
                    "reviewer_role": "public_source_freshness_reviewer",
                    "review_queue": "ppd-public-refresh-review",
                },
                "skip_defer_rationale": "Fixture handoff defers live refresh until operator approves public crawl preflight.",
                "validation_evidence": [
                    {
                        "evidence_id": "validation-evidence-001",
                        "summary": "Metadata-only fixture cites source freshness evidence and no execution state.",
                        "source_citations": ["source:ppd-devhub-faqs#updated-date"],
                    }
                ],
                "rollback_notes": [
                    {
                        "rollback_note_id": "rollback-note-001",
                        "reason": "No state mutation is performed; discard this fixture handoff row if rejected.",
                    }
                ],
            }
        ],
    }


class PublicFreshnessReviewerHandoffV1Tests(unittest.TestCase):
    def test_accepts_complete_fixture_first_handoff(self) -> None:
        require_valid_public_freshness_reviewer_handoff_v1(_valid_packet())

    def test_rejects_rows_missing_required_reviewer_handoff_fields(self) -> None:
        packet = _valid_packet()
        packet["handoff_rows"] = [{"row_id": "incomplete-row"}]

        codes = {issue.code for issue in validate_public_freshness_reviewer_handoff_v1(packet)}

        self.assertIn("missing_source_citations", codes)
        self.assertIn("missing_affected_ids", codes)
        self.assertIn("missing_reviewer_owner_fields", codes)
        self.assertIn("missing_skip_defer_rationale", codes)
        self.assertIn("missing_validation_evidence", codes)
        self.assertIn("missing_rollback_notes", codes)

    def test_rejects_authenticated_urls_raw_bodies_execution_claims_guarantees_and_mutations(self) -> None:
        packet = _valid_packet()
        row = packet["handoff_rows"][0]
        row["canonical_url"] = "https://devhub.portlandoregon.gov/account/my-permits?token=secret"
        row["raw_body_ref"] = "raw_crawl/devhub-faq.html"
        row["live_crawl_status"] = "live crawl completed"
        row["processor_completed"] = True
        row["reviewer_note"] = "Permit approved and legal outcome guaranteed."
        row["registry_mutation_active"] = True
        row["guardrail_mutation_active"] = True
        row["monitoring_mutation_active"] = True
        row["release_state_mutation_active"] = True
        row["agent_state_mutation_active"] = True

        codes = {issue.code for issue in validate_public_freshness_reviewer_handoff_v1(packet)}

        self.assertIn("authenticated_url", codes)
        self.assertIn("raw_body_reference", codes)
        self.assertIn("live_crawler_claim", codes)
        self.assertIn("processor_completion_claim", codes)
        self.assertIn("legal_outcome_guarantee", codes)
        self.assertIn("active_state_mutation", codes)


if __name__ == "__main__":
    unittest.main()
