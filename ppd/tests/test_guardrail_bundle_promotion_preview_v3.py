from __future__ import annotations

import unittest
from pathlib import Path

from ppd.agent_readiness.guardrail_bundle_promotion_preview_v3 import (
    PREVIEW_TYPE,
    REQUIRED_ATTESTATIONS,
    build_guardrail_bundle_promotion_preview_v3_from_manifest,
    validate_guardrail_bundle_promotion_preview_v3,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "guardrail_bundle_promotion_preview_v3"
MANIFEST = FIXTURE_DIR / "input_manifest.json"


class GuardrailBundlePromotionPreviewV3Test(unittest.TestCase):
    def setUp(self) -> None:
        self.preview = build_guardrail_bundle_promotion_preview_v3_from_manifest(MANIFEST)

    def test_builds_fixture_first_preview_from_disposition_summary_and_replay_matrix(self) -> None:
        self.assertEqual(self.preview["preview_type"], PREVIEW_TYPE)
        self.assertEqual(self.preview["preview_version"], 3)
        self.assertEqual(self.preview["mode"], "fixture_first_guardrail_bundle_promotion_preview_only")
        self.assertIn("attended_review_disposition_summary_v3", self.preview["consumes"])
        self.assertIn("guardrail_regression_replay_matrix_v3", self.preview["consumes"])
        self.assertEqual(self.preview["attestations"], REQUIRED_ATTESTATIONS)
        self.assertEqual(validate_guardrail_bundle_promotion_preview_v3(self.preview), [])

    def test_patch_candidates_have_citations_predicate_rows_template_deltas_and_rollback(self) -> None:
        candidates = self.preview["guardrail_fixture_patch_candidates"]
        self.assertEqual(len(candidates), 5)
        rollback_ids = {row["candidate_id"] for row in self.preview["rollback_checkpoints"]}
        self.assertEqual(self.preview["dependency_order"], [candidate["candidate_id"] for candidate in candidates])
        for candidate in candidates:
            self.assertIn(candidate["candidate_id"], rollback_ids)
            self.assertTrue(candidate["citations"])
            self.assertTrue(candidate["before_after_predicate_rows"])
            self.assertTrue(candidate["explanation_template_deltas"])
            predicate = candidate["before_after_predicate_rows"][0]
            self.assertTrue(predicate["before"])
            self.assertTrue(predicate["after"])
            self.assertTrue(predicate["citations"])

    def test_blocked_consequential_action_replay_has_regression_check(self) -> None:
        blocked = [
            candidate
            for candidate in self.preview["guardrail_fixture_patch_candidates"]
            if candidate["next_action_classification"] == "refuse_consequential_action"
        ]
        self.assertEqual(len(blocked), 1)
        self.assertEqual(
            blocked[0]["blocked_consequential_action_regression_checks"][0]["expected_result"],
            "blocked_until_user_attended_exact_confirmation",
        )

    def test_validator_rejects_missing_citations_dependency_rollback_and_attestation_gap(self) -> None:
        broken = dict(self.preview)
        candidates = [dict(candidate) for candidate in self.preview["guardrail_fixture_patch_candidates"]]
        candidates[0]["citations"] = []
        broken["guardrail_fixture_patch_candidates"] = candidates
        broken["dependency_order"] = []
        broken["rollback_checkpoints"] = []
        broken["attestations"] = dict(self.preview["attestations"])
        broken["attestations"]["no_live_llm"] = False

        errors = validate_guardrail_bundle_promotion_preview_v3(broken)

        self.assertIn("guardrail_fixture_patch_candidates[0].citations must be non-empty", errors)
        self.assertIn("dependency_order must be non-empty", errors)
        self.assertIn("rollback_checkpoints must be non-empty", errors)
        self.assertIn("attestations.no_live_llm must be true", errors)

    def test_validator_rejects_active_guardrail_or_prompt_mutation_flags(self) -> None:
        broken = dict(self.preview)
        broken["active_guardrail_mutation"] = True
        broken["guardrail_fixture_patch_candidates"] = [dict(candidate) for candidate in self.preview["guardrail_fixture_patch_candidates"]]
        broken["guardrail_fixture_patch_candidates"][0]["prompt_mutation"] = True

        errors = validate_guardrail_bundle_promotion_preview_v3(broken)

        self.assertIn("$.active_guardrail_mutation mutation flags must be absent or false", errors)
        self.assertIn("$.guardrail_fixture_patch_candidates[0].prompt_mutation mutation flags must be absent or false", errors)

    def test_fixture_path_is_local_to_ppd_tests(self) -> None:
        self.assertEqual(FIXTURE_DIR, Path(__file__).parent / "fixtures" / "guardrail_bundle_promotion_preview_v3")


if __name__ == "__main__":
    unittest.main()
