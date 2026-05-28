"""Fixture-backed tests for the PP&D agent preflight decision matrix."""

from __future__ import annotations

import json
from pathlib import Path
import unittest

from ppd.agent_preflight_decision_matrix import PreflightOutcome, evaluate_agent_preflight


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "agent_preflight" / "decision_matrix_cases.json"


class AgentPreflightDecisionMatrixTests(unittest.TestCase):
    def setUp(self) -> None:
        with FIXTURE_PATH.open("r", encoding="utf-8") as fixture_file:
            self.fixture = json.load(fixture_file)

    def test_fixture_covers_all_agent_preflight_outcomes(self) -> None:
        outcomes = {
            evaluate_agent_preflight(case["packet"]).outcome.value
            for case in self.fixture["cases"]
        }
        self.assertEqual(
            outcomes,
            {
                PreflightOutcome.BLOCKED.value,
                PreflightOutcome.READ_ONLY.value,
                PreflightOutcome.LOCAL_PREVIEW.value,
                PreflightOutcome.REVERSIBLE_DRAFT.value,
                PreflightOutcome.MANUAL_HANDOFF.value,
                PreflightOutcome.REFUSED.value,
            },
        )

    def test_each_fixture_case_matches_expected_outcome(self) -> None:
        for case in self.fixture["cases"]:
            with self.subTest(case_id=case["case_id"]):
                decision = evaluate_agent_preflight(case["packet"])
                self.assertEqual(case["expected_outcome"], decision.outcome.value)
                self.assertTrue(decision.reasons)
                self.assertTrue(decision.next_safe_actions)

    def test_case_gaps_block_before_reversible_drafting(self) -> None:
        packet = self._case_packet("reversible_draft_ready")
        packet["case_gaps"]["missing_documents"] = ["site_plan_pdf"]

        decision = evaluate_agent_preflight(packet)

        self.assertEqual(PreflightOutcome.BLOCKED, decision.outcome)
        self.assertIn("case gap report contains missing_documents", decision.reasons)

    def test_reversible_draft_without_devhub_handoff_fails_to_manual_handoff(self) -> None:
        packet = self._case_packet("reversible_draft_ready")
        packet["devhub_handoff"] = {"status": "not_started"}

        decision = evaluate_agent_preflight(packet)

        self.assertEqual(PreflightOutcome.MANUAL_HANDOFF, decision.outcome)
        self.assertIn("DevHub handoff is not ready", " ".join(decision.reasons))

    def test_private_or_raw_runtime_metadata_is_refused(self) -> None:
        packet = self._case_packet("read_only_ready")
        packet["devhub_handoff"] = {"session_state": "must-not-be-committed"}

        decision = evaluate_agent_preflight(packet)

        self.assertEqual(PreflightOutcome.REFUSED, decision.outcome)
        self.assertIn("private or raw runtime metadata", decision.reasons[0])

    def _case_packet(self, case_id: str) -> dict:
        for case in self.fixture["cases"]:
            if case["case_id"] == case_id:
                return json.loads(json.dumps(case["packet"]))
        raise AssertionError(f"missing fixture case {case_id}")


if __name__ == "__main__":
    unittest.main()
