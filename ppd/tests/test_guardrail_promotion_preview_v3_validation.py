from __future__ import annotations

import json
import unittest
from pathlib import Path

from ppd.logic.guardrail_promotion_preview_v3 import (
    assert_guardrail_bundle_promotion_preview_v3,
    validate_guardrail_bundle_promotion_preview_v3,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "guardrails"


def _load_fixture(name: str) -> dict:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


class GuardrailPromotionPreviewV3ValidationTest(unittest.TestCase):
    def test_valid_preview_passes(self) -> None:
        preview = _load_fixture("promotion_preview_v3_valid.json")

        result = validate_guardrail_bundle_promotion_preview_v3(preview)

        self.assertTrue(result.ok, result.to_dict())
        assert_guardrail_bundle_promotion_preview_v3(preview)

    def test_invalid_preview_rejects_required_guardrail_gaps_and_forbidden_content(self) -> None:
        preview = _load_fixture("promotion_preview_v3_invalid.json")

        result = validate_guardrail_bundle_promotion_preview_v3(preview)
        issue_codes = {issue.code for issue in result.issues}

        self.assertFalse(result.ok)
        self.assertIn("uncited_predicate_patch_candidate", issue_codes)
        self.assertIn("missing_before_predicate_rows", issue_codes)
        self.assertIn("missing_after_predicate_rows", issue_codes)
        self.assertIn("missing_explanation_template_deltas", issue_codes)
        self.assertIn("missing_blocked_action_regression_checks", issue_codes)
        self.assertIn("missing_dependency_order", issue_codes)
        self.assertIn("missing_rollback_checkpoints", issue_codes)
        self.assertIn("private_or_authenticated_fact", issue_codes)
        self.assertIn("raw_artifact_reference", issue_codes)
        self.assertIn("live_execution_claim", issue_codes)
        self.assertIn("outcome_guarantee", issue_codes)
        self.assertIn("consequential_action_language", issue_codes)
        self.assertIn("active_mutation_flag", issue_codes)

    def test_assertion_raises_with_stable_codes(self) -> None:
        preview = _load_fixture("promotion_preview_v3_invalid.json")

        with self.assertRaises(ValueError) as raised:
            assert_guardrail_bundle_promotion_preview_v3(preview)

        self.assertIn("uncited_predicate_patch_candidate", str(raised.exception))
        self.assertIn("active_mutation_flag", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
