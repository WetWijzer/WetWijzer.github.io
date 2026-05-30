import unittest

from ppd.extraction.impact_precheck import (
    ImpactPrecheckValidationError,
    assert_valid_requirement_extraction_impact_precheck_packet,
    is_valid_requirement_extraction_impact_precheck_packet,
    validate_requirement_extraction_impact_precheck_packet,
)


def valid_packet():
    return {
        "packet_id": "impact-precheck-fixture",
        "rerun_scopes": [
            {
                "scope_id": "rerun:devhub-guide-submit-permit-application",
                "source_evidence_ids": ["evidence:ppd-devhub-guide-submit-permit-application"],
                "reason": "metadata-only stale citation review",
            }
        ],
        "affected_requirement_ids": ["req:application-data-entry"],
        "affected_process_ids": ["process:building-permit-application"],
        "affected_guardrail_ids": ["guardrail:submission-exact-confirmation"],
        "expected_outputs": {
            "metadata_only": True,
            "artifact_types": ["impact_report", "review_queue_item"],
        },
        "reviewer_owners": ["ppd-requirements-review"],
        "notes": "Precheck only; no processor or extraction execution is performed.",
    }


class RequirementExtractionImpactPrecheckTests(unittest.TestCase):
    def test_accepts_metadata_only_cited_precheck_packet(self):
        packet = valid_packet()

        self.assertTrue(is_valid_requirement_extraction_impact_precheck_packet(packet))
        self.assertEqual(validate_requirement_extraction_impact_precheck_packet(packet), [])
        assert_valid_requirement_extraction_impact_precheck_packet(packet)

    def test_rejects_uncited_rerun_scope(self):
        packet = valid_packet()
        packet["rerun_scopes"] = [{"scope_id": "rerun:uncited"}]

        codes = {violation.code for violation in validate_requirement_extraction_impact_precheck_packet(packet)}

        self.assertIn("uncited_rerun_scope", codes)

    def test_rejects_missing_affected_ids_metadata_outputs_and_reviewers(self):
        packet = valid_packet()
        packet["affected_requirement_ids"] = []
        packet.pop("affected_process_ids")
        packet["affected_guardrail_ids"] = []
        packet["expected_outputs"] = {"artifact_types": ["report"]}
        packet["reviewer_owners"] = []

        codes = [violation.code for violation in validate_requirement_extraction_impact_precheck_packet(packet)]

        self.assertGreaterEqual(codes.count("missing_affected_ids"), 3)
        self.assertIn("missing_metadata_only_outputs", codes)
        self.assertIn("missing_reviewer_owners", codes)

    def test_rejects_raw_references_private_facts_execution_claims_guarantees_and_mutations(self):
        packet = valid_packet()
        packet.update(
            {
                "archive_ref": "warc://raw-capture",
                "private_case_facts": {"site_address": "123 Private St"},
                "operator_claim": "Ran extraction and processor executed successfully.",
                "legal_claim": "Approval guaranteed and permit will be approved.",
                "mutates_requirements": True,
                "active_process_mutation": True,
                "writes_guardrails": True,
                "active_prompt_mutation": True,
                "mutates_surface_registry": True,
                "mutates_monitoring": True,
                "mutates_release_state": True,
            }
        )

        codes = {violation.code for violation in validate_requirement_extraction_impact_precheck_packet(packet)}

        self.assertIn("raw_reference", codes)
        self.assertIn("private_case_facts", codes)
        self.assertIn("live_execution_claim", codes)
        self.assertIn("outcome_guarantee", codes)
        self.assertIn("active_mutation_flag", codes)

    def test_assert_valid_raises_with_codes(self):
        packet = valid_packet()
        packet["rerun_scopes"] = [{"scope_id": "rerun:uncited"}]

        with self.assertRaises(ImpactPrecheckValidationError) as context:
            assert_valid_requirement_extraction_impact_precheck_packet(packet)

        self.assertIn("uncited_rerun_scope", str(context.exception))


if __name__ == "__main__":
    unittest.main()
