import json
import unittest
from pathlib import Path

from ppd.guardrail_bundle_refresh import (
    REQUIRED_CHANGE_TYPES,
    build_guardrail_bundle_refresh_plan,
)

FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "guardrail_bundle_refresh"
    / "changed_requirement_refresh_fixture.json"
)


class GuardrailBundleRefreshPlanTests(unittest.TestCase):
    def load_fixture(self):
        return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    def test_builds_versioned_draft_deltas_for_all_high_risk_change_types(self):
        plan = build_guardrail_bundle_refresh_plan(self.load_fixture())

        self.assertEqual(plan["fixture_id"], "changed_requirement_guardrail_refresh_v1")
        self.assertEqual(plan["current_guardrail_bundle_id"], "guardrail-bundle-single-pdf-v3")
        self.assertEqual(plan["draft_guardrail_bundle_id"], "guardrail-bundle-single-pdf-v4-draft")
        self.assertEqual(plan["draft_version"], "v4-draft-2026-05-27")
        self.assertEqual(set(plan["covered_change_types"]), REQUIRED_CHANGE_TYPES)
        self.assertEqual(len(plan["deltas"]), len(REQUIRED_CHANGE_TYPES))

        for delta in plan["deltas"]:
            self.assertTrue(delta["delta_id"].startswith("delta-v4-draft-2026-05-27-"))
            self.assertEqual(delta["target_guardrail_bundle_id"], "guardrail-bundle-single-pdf-v4-draft")
            self.assertEqual(delta["draft_version"], "v4-draft-2026-05-27")
            self.assertGreaterEqual(len(delta["source_evidence_ids"]), 1)
            self.assertGreaterEqual(len(delta["required_guardrail_updates"]), 1)
            self.assertGreaterEqual(len(delta["predicate_deltas"]), 1)
            for predicate_delta in delta["predicate_deltas"]:
                self.assertGreaterEqual(len(predicate_delta["source_evidence_ids"]), 1)

    def test_keeps_bundle_readiness_blocked_until_review_is_complete(self):
        plan = build_guardrail_bundle_refresh_plan(self.load_fixture())

        self.assertEqual(plan["readiness_status"], "blocked_pending_review")
        self.assertFalse(plan["publish_allowed"])
        self.assertEqual(len(plan["blocked_reasons"]), len(REQUIRED_CHANGE_TYPES))
        for delta in plan["deltas"]:
            self.assertEqual(delta["review_status"], "needs_review")
            self.assertEqual(delta["readiness_status"], "blocked_pending_review")
            self.assertTrue(delta["blocked_reason"].endswith("_change_requires_human_review"))

    def test_reviewed_fixture_can_become_publish_ready_without_live_crawl(self):
        fixture = self.load_fixture()
        for item in fixture["changed_requirements"]:
            item["review_status"] = "reviewed"

        plan = build_guardrail_bundle_refresh_plan(fixture)

        self.assertEqual(plan["readiness_status"], "ready_for_bundle_publish")
        self.assertTrue(plan["publish_allowed"])
        self.assertEqual(plan["blocked_reasons"], [])
        self.assertTrue(all(delta["readiness_status"] == "ready_after_review" for delta in plan["deltas"]))

    def test_rejects_refresh_fixtures_missing_a_required_change_type(self):
        fixture = self.load_fixture()
        fixture["changed_requirements"] = [
            item
            for item in fixture["changed_requirements"]
            if item["change_type"] != "fee"
        ]

        with self.assertRaises(ValueError) as error:
            build_guardrail_bundle_refresh_plan(fixture)

        self.assertIn("fee", str(error.exception))

    def test_rejects_uncited_predicate_deltas(self):
        fixture = self.load_fixture()
        fixture["changed_requirements"][0]["predicate_deltas"][0]["source_evidence_ids"] = []

        with self.assertRaises(ValueError) as error:
            build_guardrail_bundle_refresh_plan(fixture)

        self.assertIn("source_evidence_ids", str(error.exception))

    def test_rejects_unsupported_requirement_types(self):
        fixture = self.load_fixture()
        fixture["changed_requirements"][0]["requirement_type"] = "policy_guess"

        with self.assertRaises(ValueError) as error:
            build_guardrail_bundle_refresh_plan(fixture)

        self.assertIn("unsupported requirement_type", str(error.exception))

    def test_rejects_changed_requirements_missing_source_evidence_ids(self):
        fixture = self.load_fixture()
        fixture["changed_requirements"][0]["source_evidence_ids"] = []

        with self.assertRaises(ValueError) as error:
            build_guardrail_bundle_refresh_plan(fixture)

        self.assertIn("source_evidence_ids", str(error.exception))

    def test_rejects_consequential_devhub_gates_without_manual_handoff(self):
        fixture = self.load_fixture()
        gate = next(item for item in fixture["changed_requirements"] if item["change_type"] == "devhub_action_gate")
        gate["manual_handoff_predicates"] = []

        with self.assertRaises(ValueError) as error:
            build_guardrail_bundle_refresh_plan(fixture)

        self.assertIn("manual_handoff_predicates", str(error.exception))

    def test_rejects_consequential_devhub_gates_without_exact_confirmation(self):
        fixture = self.load_fixture()
        gate = next(item for item in fixture["changed_requirements"] if item["change_type"] == "devhub_action_gate")
        gate["exact_confirmation_predicates"] = []

        with self.assertRaises(ValueError) as error:
            build_guardrail_bundle_refresh_plan(fixture)

        self.assertIn("exact_confirmation_predicates", str(error.exception))

    def test_rejects_ready_status_before_human_review(self):
        fixture = self.load_fixture()
        fixture["changed_requirements"][0]["validation_status"] = "ready"

        with self.assertRaises(ValueError) as error:
            build_guardrail_bundle_refresh_plan(fixture)

        self.assertIn("before human review", str(error.exception))

    def test_rejects_ready_predicate_delta_before_human_review(self):
        fixture = self.load_fixture()
        fixture["changed_requirements"][0]["predicate_deltas"][0]["readiness_status"] = "ready_after_review"

        with self.assertRaises(ValueError) as error:
            build_guardrail_bundle_refresh_plan(fixture)

        self.assertIn("before human review", str(error.exception))


if __name__ == "__main__":
    unittest.main()
