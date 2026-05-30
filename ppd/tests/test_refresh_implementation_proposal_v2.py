from __future__ import annotations

import unittest
from copy import deepcopy
from pathlib import Path

from ppd.refresh_implementation_proposal_v2 import (
    ATTESTATIONS,
    build_refresh_implementation_proposal_v2_from_files,
    validate_refresh_implementation_proposal_v2,
)


FIXTURES = Path(__file__).parent / "fixtures" / "refresh_implementation_proposal_v2"


class RefreshImplementationProposalV2Test(unittest.TestCase):
    def _valid_proposal(self) -> dict:
        return build_refresh_implementation_proposal_v2_from_files(
            FIXTURES / "public_source_observation_refresh_candidate_v2.json",
            FIXTURES / "devhub_read_only_surface_observation_refresh_candidate_v2.json",
            FIXTURES / "post_dry_run_guardrail_impact_review_v2.json",
        )

    def test_builds_cited_patch_rows_with_dependency_order_and_attestations(self) -> None:
        proposal = self._valid_proposal()

        self.assertEqual(proposal["proposal_version"], "refresh_implementation_proposal_v2")
        self.assertEqual(proposal["attestations"], ATTESTATIONS)
        self.assertTrue(validate_refresh_implementation_proposal_v2(proposal).ok)
        self.assertEqual(
            proposal["dependency_ordering"],
            [
                "validate-input-fixtures",
                "review-source-patch-rows",
                "review-surface-patch-rows",
                "review-guardrail-patch-rows",
                "rollback-readiness-check",
            ],
        )

        source_row = proposal["proposed_source_patch_rows"][0]
        self.assertEqual(source_row["source_id"], "permit-center-fees")
        self.assertEqual(source_row["reviewer_owner"], "ppd-fees-reviewer")
        self.assertTrue(source_row["citations"])

        surface_row = proposal["proposed_surface_patch_rows"][0]
        self.assertEqual(surface_row["surface_id"], "devhub-home-read-only")
        self.assertEqual(surface_row["selector_confidence"], "medium")
        self.assertEqual(surface_row["redaction_disposition"], "synthetic-only")

        guardrail_rows = proposal["proposed_guardrail_patch_rows"]
        self.assertTrue(any(row["patch_kind"] == "blocked_consequential_action_review_row" for row in guardrail_rows))
        self.assertTrue(proposal["reviewer_owner_fields"])
        self.assertTrue(proposal["rollback_notes"])

    def test_validator_rejects_missing_citations_reviewer_owners_and_ordering(self) -> None:
        proposal = self._valid_proposal()
        proposal["proposed_source_patch_rows"][0]["citations"] = []
        proposal["proposed_surface_patch_rows"][0]["reviewer_owner"] = ""
        proposal["dependency_ordering"] = ["review-guardrail-patch-rows"]

        result = validate_refresh_implementation_proposal_v2(proposal)

        self.assertFalse(result.ok)
        self.assertTrue(any("citations" in error for error in result.errors))
        self.assertTrue(any("reviewer_owner" in error for error in result.errors))
        self.assertTrue(any("dependency_ordering" in error for error in result.errors))

    def test_validator_rejects_mutation_flags_and_artifacts(self) -> None:
        proposal = self._valid_proposal()
        proposal["active_guardrail_mutation"] = True
        proposal["trace"] = "local.trace"

        result = validate_refresh_implementation_proposal_v2(proposal)

        self.assertFalse(result.ok)
        self.assertTrue(any("active_guardrail_mutation" in error for error in result.errors))
        self.assertTrue(any("trace" in error for error in result.errors))

    def test_validator_requires_exact_attestations(self) -> None:
        proposal = deepcopy(self._valid_proposal())
        proposal["attestations"]["no_processor"] = False

        result = validate_refresh_implementation_proposal_v2(proposal)

        self.assertFalse(result.ok)
        self.assertTrue(any("attestations" in error for error in result.errors))


if __name__ == "__main__":
    unittest.main()
