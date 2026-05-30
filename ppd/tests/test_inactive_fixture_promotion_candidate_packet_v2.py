from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from ppd.agent_readiness.inactive_fixture_promotion_candidate_packet_v2 import (
    PACKET_TYPE,
    VALIDATION_COMMANDS,
    load_inactive_fixture_promotion_candidate_packet_v2,
    validate_inactive_fixture_promotion_candidate_packet_v2,
)

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "inactive_fixture_promotion_candidate_packet_v2" / "valid_packet.json"


class InactiveFixturePromotionCandidatePacketV2Tests(unittest.TestCase):
    def test_valid_fixture_loads(self) -> None:
        packet = load_inactive_fixture_promotion_candidate_packet_v2(FIXTURE_PATH)
        result = validate_inactive_fixture_promotion_candidate_packet_v2(packet)
        self.assertTrue(result.valid, result.problems)

    def test_rejects_missing_required_packet_sections(self) -> None:
        packet = self._valid_packet()
        for key in (
            "promotion_candidate_rows",
            "fixture_family_ownership_assignments",
            "prerequisite_validation_replay_inventory",
            "reviewer_approval_placeholders",
            "rollback_plan_references",
            "validation_commands",
        ):
            mutated = copy.deepcopy(packet)
            mutated.pop(key)
            result = validate_inactive_fixture_promotion_candidate_packet_v2(mutated)
            self.assertFalse(result.valid)
            self.assertTrue(any(key in problem for problem in result.problems), result.problems)

    def test_rejects_missing_candidate_row_fields(self) -> None:
        for field in (
            "no_go_reason",
            "rollback_plan_ref",
            "validation_commands",
            "owner_assignment_ref",
            "prerequisite_validation_ref",
            "reviewer_approval_placeholder_ref",
        ):
            packet = self._valid_packet()
            packet["promotion_candidate_rows"][0].pop(field)
            result = validate_inactive_fixture_promotion_candidate_packet_v2(packet)
            self.assertFalse(result.valid)
            self.assertTrue(any(field in problem for problem in result.problems), result.problems)

    def test_rejects_missing_validation_command_replay_inventory(self) -> None:
        packet = self._valid_packet()
        packet["prerequisite_validation_replay_inventory"] = []
        result = validate_inactive_fixture_promotion_candidate_packet_v2(packet)
        self.assertFalse(result.valid)
        self.assertIn("prerequisite_validation_replay_inventory must be a non-empty list", result.problems)

    def test_rejects_private_raw_live_guarantee_and_consequential_language(self) -> None:
        forbidden_examples = (
            ("auth_state", {"cookies": ["not-committable"]}),
            ("raw_pdf", "downloaded pdf bytes"),
            ("status_note", "live execution completed"),
            ("outcome_note", "permit will be approved"),
            ("action_note", "agent will submit permit"),
        )
        for key, value in forbidden_examples:
            packet = self._valid_packet()
            packet[key] = value
            result = validate_inactive_fixture_promotion_candidate_packet_v2(packet)
            self.assertFalse(result.valid, key)

    def test_rejects_active_mutation_flags(self) -> None:
        for key in (
            "active_artifact_mutation",
            "active_prompt_mutation",
            "active_release_state_mutation",
            "active_fixture_mutation",
            "active_agent_state_mutation",
        ):
            packet = self._valid_packet()
            packet[key] = True
            result = validate_inactive_fixture_promotion_candidate_packet_v2(packet)
            self.assertFalse(result.valid)
            self.assertTrue(any(key in problem for problem in result.problems), result.problems)

    def _valid_packet(self) -> dict[str, object]:
        return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
