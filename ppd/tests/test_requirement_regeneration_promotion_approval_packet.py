from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from ppd.agent_readiness.requirement_regeneration_promotion_approval_packet import (
    assert_valid_requirement_regeneration_promotion_approval_packet,
    validate_requirement_regeneration_promotion_approval_packet,
)


_FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "agent_readiness"
    / "requirement_regeneration_promotion_approval_packet.json"
)


def _fixture_packet() -> dict[str, object]:
    return json.loads(_FIXTURE_PATH.read_text(encoding="utf-8"))


class RequirementRegenerationPromotionApprovalPacketTest(unittest.TestCase):
    def test_fixture_packet_is_valid(self) -> None:
        packet = _fixture_packet()

        result = validate_requirement_regeneration_promotion_approval_packet(packet)

        self.assertTrue(result.valid, result.problems)
        assert_valid_requirement_regeneration_promotion_approval_packet(packet)

    def test_rejects_uncited_approve_and_defer_decisions(self) -> None:
        packet = _fixture_packet()
        decisions = packet["promotion_decisions"]
        assert isinstance(decisions, list)
        for decision in decisions:
            assert isinstance(decision, dict)
            decision["source_evidence_ids"] = []

        result = validate_requirement_regeneration_promotion_approval_packet(packet)

        self.assertFalse(result.valid)
        joined = "\n".join(result.problems)
        self.assertIn("approve decision must cite source_evidence_ids", joined)
        self.assertIn("defer decision must cite source_evidence_ids", joined)

    def test_rejects_missing_affected_artifact_ids(self) -> None:
        packet = _fixture_packet()
        decisions = packet["promotion_decisions"]
        assert isinstance(decisions, list)
        first = decisions[0]
        assert isinstance(first, dict)
        first["affected_requirement_ids"] = []
        first["affected_process_ids"] = []
        first["affected_guardrail_ids"] = []

        result = validate_requirement_regeneration_promotion_approval_packet(packet)

        self.assertFalse(result.valid)
        self.assertIn("promotion_decisions[0] lacks affected_requirement_ids", result.problems)
        self.assertIn("promotion_decisions[0] lacks affected_process_ids", result.problems)
        self.assertIn("promotion_decisions[0] lacks affected_guardrail_ids", result.problems)

    def test_rejects_missing_rollback_signoff_and_offline_commands(self) -> None:
        packet = _fixture_packet()
        packet["rollback_notes"] = []
        packet.pop("reviewer_signoff")
        packet["expected_offline_validation_commands"] = []

        result = validate_requirement_regeneration_promotion_approval_packet(packet)

        self.assertFalse(result.valid)
        self.assertIn("rollback_notes must be a non-empty list", result.problems)
        self.assertIn("reviewer_signoff is required", result.problems)
        self.assertIn("expected_offline_validation_commands must be a non-empty list", result.problems)

    def test_rejects_private_raw_live_outcome_and_mutation_content(self) -> None:
        packet = _fixture_packet()
        packet["private_case_fact"] = "private case fact: owner phone number"
        packet["raw_body"] = "file:///tmp/raw/archive.warc"
        packet["live_claim"] = "processor executed live extraction"
        packet["outcome_claim"] = "permit will be approved"
        packet["promotion_policy"] = copy.deepcopy(packet["promotion_policy"])
        policy = packet["promotion_policy"]
        assert isinstance(policy, dict)
        policy["mutates_active_requirements"] = True
        packet["active_prompt_write"] = "replace active prompt"

        result = validate_requirement_regeneration_promotion_approval_packet(packet)

        self.assertFalse(result.valid)
        joined = "\n".join(result.problems)
        self.assertIn("private case facts", joined)
        self.assertIn("raw body, download, archive", joined)
        self.assertIn("claims live extraction", joined)
        self.assertIn("legal or permitting outcome guarantee", joined)
        self.assertIn("mutates_active_requirements must be false", joined)
        self.assertIn("active_prompt_write", joined)

    def test_rejects_live_or_processor_validation_commands(self) -> None:
        packet = _fixture_packet()
        packet["expected_offline_validation_commands"] = [
            ["python3", "ppd/crawler/live_public_scrape.py", "--live"],
        ]

        result = validate_requirement_regeneration_promotion_approval_packet(packet)

        self.assertFalse(result.valid)
        self.assertIn(
            "expected_offline_validation_commands[0] must remain offline and must not invoke processors, downloads, archives, DevHub, or live extraction",
            result.problems,
        )


if __name__ == "__main__":
    unittest.main()
