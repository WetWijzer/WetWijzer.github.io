from __future__ import annotations

import copy
import unittest
from pathlib import Path

from ppd.agent_readiness.guardrail_bundle_recompile_candidate_v4 import REQUIRED_CHANGE_CATEGORIES
from ppd.agent_readiness.guardrail_recompile_reviewer_packet_v4 import (
    OFFLINE_VALIDATION_COMMANDS,
    REQUIRED_ATTESTATIONS,
    load_guardrail_recompile_reviewer_packet_v4_manifest,
    validate_guardrail_recompile_reviewer_packet_v4,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "guardrail_recompile_reviewer_packet_v4"
MANIFEST = FIXTURE_DIR / "input_manifest.json"


class GuardrailRecompileReviewerPacketV4Test(unittest.TestCase):
    def setUp(self) -> None:
        self.packet = load_guardrail_recompile_reviewer_packet_v4_manifest(MANIFEST)

    def test_builds_review_packet_from_candidate_v4_fixture_only(self) -> None:
        self.assertEqual(self.packet["packet_type"], "ppd.guardrail_recompile_reviewer_packet.v4")
        self.assertEqual(self.packet["packet_version"], "v4")
        self.assertEqual(
            self.packet["mode"],
            "fixture_first_guardrail_bundle_recompile_candidate_v4_review_only",
        )
        self.assertEqual(
            set(self.packet["consumes"]),
            {"guardrail_bundle_recompile_candidate_v4_fixture"},
        )
        self.assertEqual(self.packet["candidate_packet_type"], "ppd.guardrail_bundle_recompile_candidate.v4")
        self.assertEqual(self.packet["attestations"], REQUIRED_ATTESTATIONS)
        result = validate_guardrail_recompile_reviewer_packet_v4(self.packet)
        self.assertTrue(result.valid, result.problems)

    def test_reviewer_rows_cover_candidate_categories_with_cited_process_impacts(self) -> None:
        rows = self.packet["reviewer_predicate_rows"]
        self.assertEqual(tuple(row["category"] for row in rows), REQUIRED_CHANGE_CATEGORIES)
        for row in rows:
            self.assertEqual(row["review_status"], "pending_human_review")
            self.assertEqual(row["reviewer_hold_status"], "unresolved")
            self.assertFalse(row["active_bundle_mutation"])
            self.assertTrue(row["reviewer_ready_predicate"])
            self.assertTrue(row["cited_process_impact_refs"])
            self.assertGreater(row["process_impact_reference_count"], 0)

    def test_packet_has_requested_review_sections(self) -> None:
        self.assertTrue(self.packet["candidate_guardrail_bundle_ids"])
        self.assertTrue(self.packet["cited_process_impact_references"])
        self.assertTrue(self.packet["stale_evidence_stop_gates"])
        self.assertTrue(self.packet["stale_evidence_stop_gates"][0]["blocked_until_resolved"])
        self.assertTrue(self.packet["reversible_action_summaries"])
        self.assertTrue(self.packet["exact_confirmation_summaries"])
        self.assertTrue(self.packet["refused_action_summaries"])
        self.assertTrue(self.packet["unresolved_reviewer_holds"])
        self.assertTrue(self.packet["rollback_notes"])

    def test_validation_commands_are_exact_offline_commands_only(self) -> None:
        self.assertEqual(self.packet["offline_validation_commands"], OFFLINE_VALIDATION_COMMANDS)
        self.assertEqual(self.packet["validation_status"]["validation_commands"], OFFLINE_VALIDATION_COMMANDS)
        self.assertFalse(self.packet["validation_status"]["active_bundle_mutation"])

    def test_validator_rejects_extra_consumed_fixture_missing_rows_and_forbidden_state(self) -> None:
        broken = copy.deepcopy(self.packet)
        broken["consumes"]["session_state"] = "session.json"
        broken["reviewer_predicate_rows"] = list(self.packet["reviewer_predicate_rows"][:-1])
        broken["opens_devhub"] = True

        result = validate_guardrail_recompile_reviewer_packet_v4(broken)

        self.assertFalse(result.valid)
        self.assertIn(
            "consumes must contain only guardrail_bundle_recompile_candidate_v4_fixture",
            result.problems,
        )
        self.assertIn(
            "reviewer_predicate_rows must cover candidate categories in deterministic order",
            result.problems,
        )
        self.assertIn("packet.opens_devhub must be false or absent", result.problems)

    def test_validator_rejects_missing_candidate_refs_and_review_sections(self) -> None:
        required_sections = (
            "candidate_guardrail_bundle_ids",
            "cited_process_impact_references",
            "stale_evidence_stop_gates",
            "reversible_action_summaries",
            "exact_confirmation_summaries",
            "refused_action_summaries",
            "unresolved_reviewer_holds",
            "rollback_notes",
            "offline_validation_commands",
        )
        for section in required_sections:
            with self.subTest(section=section):
                broken = copy.deepcopy(self.packet)
                broken[section] = []
                result = validate_guardrail_recompile_reviewer_packet_v4(broken)
                self.assertFalse(result.valid)

    def test_validator_rejects_incomplete_reviewer_predicate_rows(self) -> None:
        row_mutations = (
            ("reviewer_ready_predicate", ""),
            ("cited_process_impact_refs", []),
            ("reviewer_hold_status", "resolved"),
            ("active_bundle_mutation", True),
        )
        for key, value in row_mutations:
            with self.subTest(key=key):
                broken = copy.deepcopy(self.packet)
                broken["reviewer_predicate_rows"][0][key] = value
                result = validate_guardrail_recompile_reviewer_packet_v4(broken)
                self.assertFalse(result.valid)

    def test_validator_rejects_incomplete_cited_refs_stop_gates_summaries_holds_and_rollback(self) -> None:
        cases = (
            ("cited_process_impact_references", 0, "citation_refs", []),
            ("stale_evidence_stop_gates", 0, "blocked_until_resolved", False),
            ("reversible_action_summaries", 0, "predicate", ""),
            ("exact_confirmation_summaries", 0, "citation_refs", []),
            ("refused_action_summaries", 0, "boundary", ""),
            ("unresolved_reviewer_holds", 0, "release_state", "released"),
            ("rollback_notes", 0, "verification", ""),
        )
        for section, index, key, value in cases:
            with self.subTest(section=section, key=key):
                broken = copy.deepcopy(self.packet)
                broken[section][index][key] = value
                result = validate_guardrail_recompile_reviewer_packet_v4(broken)
                self.assertFalse(result.valid)

    def test_validator_rejects_forbidden_mutation_private_completion_and_guarantee_claims(self) -> None:
        cases = (
            ("active_guardrail_mutation", True),
            ("active_mutation", True),
            ("session_state_path", "private/session.json"),
            ("review_note", "official action completed"),
            ("legal_note", "permit will be approved"),
            ("mutation_note", "active guardrail mutation applied"),
        )
        for key, value in cases:
            with self.subTest(key=key):
                broken = copy.deepcopy(self.packet)
                broken[key] = value
                result = validate_guardrail_recompile_reviewer_packet_v4(broken)
                self.assertFalse(result.valid)

    def test_fixture_path_is_local_to_ppd_tests(self) -> None:
        self.assertEqual(FIXTURE_DIR, Path(__file__).parent / "fixtures" / "guardrail_recompile_reviewer_packet_v4")


if __name__ == "__main__":
    unittest.main()
