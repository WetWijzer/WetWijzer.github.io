from __future__ import annotations

import unittest
from pathlib import Path

from ppd.agent_readiness.guardrail_bundle_recompile_candidate_v4 import (
    OFFLINE_VALIDATION_COMMANDS,
    REQUIRED_CHANGE_CATEGORIES,
    REQUIRED_ATTESTATIONS,
    load_guardrail_bundle_recompile_candidate_v4_manifest,
    validate_guardrail_bundle_recompile_candidate_v4,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "guardrail_bundle_recompile_candidate_v4"
MANIFEST = FIXTURE_DIR / "input_manifest.json"


class GuardrailBundleRecompileCandidateV4Test(unittest.TestCase):
    def setUp(self) -> None:
        self.packet = load_guardrail_bundle_recompile_candidate_v4_manifest(MANIFEST)

    def test_builds_inactive_candidate_from_process_impact_and_placeholder_fixtures_only(self) -> None:
        self.assertEqual(self.packet["packet_type"], "ppd.guardrail_bundle_recompile_candidate.v4")
        self.assertEqual(self.packet["packet_version"], "v4")
        self.assertEqual(self.packet["mode"], "fixture_first_inactive_guardrail_bundle_recompile_candidate_only")
        self.assertEqual(
            set(self.packet["consumes"]),
            {"process_model_impact_candidate_v4_fixture", "guardrail_bundle_placeholders_fixture"},
        )
        self.assertEqual(self.packet["attestations"], REQUIRED_ATTESTATIONS)
        result = validate_guardrail_bundle_recompile_candidate_v4(self.packet)
        self.assertTrue(result.valid, result.problems)

    def test_candidate_covers_required_guardrail_recompile_surfaces_in_order(self) -> None:
        rows = self.packet["inactive_deterministic_predicate_changes"]
        self.assertEqual(tuple(row["category"] for row in rows), REQUIRED_CHANGE_CATEGORIES)
        for row in rows:
            self.assertTrue(row["inactive"])
            self.assertTrue(row["deterministic"])
            self.assertEqual(row["proposed_change_kind"], "inactive_predicate_change_candidate")
            self.assertTrue(row["source_impact_refs"])
            self.assertTrue(row["placeholder_guardrail_bundle_id"])
            self.assertTrue(row["proposed_inactive_predicate"])

    def test_validation_status_reviewer_holds_rollback_and_commands_are_exact(self) -> None:
        self.assertEqual(self.packet["offline_validation_commands"], OFFLINE_VALIDATION_COMMANDS)
        self.assertEqual(self.packet["validation_status"]["validation_commands"], OFFLINE_VALIDATION_COMMANDS)
        self.assertFalse(self.packet["validation_status"]["active_bundle_mutation"])
        self.assertEqual(self.packet["reviewer_holds"][0]["release_state"], "held")
        self.assertEqual(self.packet["rollback_notes"][0]["action"], "discard_candidate_fixture_only")

    def test_validator_rejects_extra_consumed_fixture_missing_category_and_mutation_flag(self) -> None:
        broken = dict(self.packet)
        broken["consumes"] = dict(self.packet["consumes"])
        broken["consumes"]["live_devhub_snapshot"] = "not_allowed.json"
        broken["inactive_deterministic_predicate_changes"] = list(self.packet["inactive_deterministic_predicate_changes"][:-1])
        broken["active_guardrail_bundle_mutation"] = True

        result = validate_guardrail_bundle_recompile_candidate_v4(broken)

        self.assertFalse(result.valid)
        self.assertIn(
            "consumes must contain only process_model_impact_candidate_v4_fixture and guardrail_bundle_placeholders_fixture",
            result.problems,
        )
        self.assertIn(
            "inactive_deterministic_predicate_changes must cover required categories in deterministic order",
            result.problems,
        )
        self.assertIn("packet.active_guardrail_bundle_mutation must be false or absent", result.problems)

    def test_fixture_path_is_local_to_ppd_tests(self) -> None:
        self.assertEqual(FIXTURE_DIR, Path(__file__).parent / "fixtures" / "guardrail_bundle_recompile_candidate_v4")


if __name__ == "__main__":
    unittest.main()
