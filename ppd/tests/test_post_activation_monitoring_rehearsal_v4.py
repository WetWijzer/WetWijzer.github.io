from __future__ import annotations

import copy
import unittest
from pathlib import Path
from typing import Any

from ppd.agent_readiness.post_activation_monitoring_rehearsal_v4 import (
    load_post_activation_monitoring_rehearsal_v4,
    validate_post_activation_monitoring_rehearsal_v4,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "post_activation_monitoring_rehearsal_v4"
VALID_FIXTURE = FIXTURE_DIR / "valid_rehearsal.json"


class PostActivationMonitoringRehearsalV4Test(unittest.TestCase):
    def setUp(self) -> None:
        self.packet = load_post_activation_monitoring_rehearsal_v4(VALID_FIXTURE)

    def assert_problem_contains(self, packet: dict[str, Any], expected: str) -> None:
        result = validate_post_activation_monitoring_rehearsal_v4(packet)
        self.assertFalse(result.ready)
        self.assertTrue(
            any(expected in problem for problem in result.problems),
            msg=f"expected {expected!r} in {result.problems!r}",
        )

    def test_valid_fixture_is_ready(self) -> None:
        result = validate_post_activation_monitoring_rehearsal_v4(self.packet)
        self.assertTrue(result.ready, result.problems)

    def test_rejects_missing_activation_checklist_references(self) -> None:
        packet = copy.deepcopy(self.packet)
        packet["activation_checklist_references"] = []
        self.assert_problem_contains(packet, "activation_checklist_references must be a non-empty list")

    def test_rejects_missing_guardrail_lookup_health_rows(self) -> None:
        packet = copy.deepcopy(self.packet)
        packet["guardrail_lookup_health_rows"] = []
        self.assert_problem_contains(packet, "guardrail_lookup_health_rows must be a non-empty list")

    def test_rejects_missing_stale_source_stop_gate_checks(self) -> None:
        packet = copy.deepcopy(self.packet)
        packet["stale_source_stop_gate_checks"] = []
        self.assert_problem_contains(packet, "stale_source_stop_gate_checks must be a non-empty list")

    def test_rejects_missing_exact_confirmation_gate_checks(self) -> None:
        packet = copy.deepcopy(self.packet)
        packet["exact_confirmation_gate_checks"] = []
        self.assert_problem_contains(packet, "exact_confirmation_gate_checks must be a non-empty list")

    def test_rejects_missing_refused_consequential_or_financial_action_checks(self) -> None:
        packet = copy.deepcopy(self.packet)
        packet["refused_consequential_or_financial_action_checks"] = []
        self.assert_problem_contains(packet, "refused_consequential_or_financial_action_checks must be a non-empty list")

    def test_rejects_missing_rollback_trigger_thresholds(self) -> None:
        packet = copy.deepcopy(self.packet)
        packet["rollback_trigger_thresholds"] = []
        self.assert_problem_contains(packet, "rollback_trigger_thresholds must be a non-empty list")

    def test_rejects_missing_reviewer_escalation_routing(self) -> None:
        packet = copy.deepcopy(self.packet)
        packet["reviewer_escalation_routing"] = []
        self.assert_problem_contains(packet, "reviewer_escalation_routing must be a non-empty list")

    def test_rejects_missing_validation_commands(self) -> None:
        packet = copy.deepcopy(self.packet)
        packet["validation_commands"] = []
        self.assert_problem_contains(packet, "validation_commands must contain only the daemon self-test command")

    def test_rejects_missing_section_reference_to_activation_checklist(self) -> None:
        packet = copy.deepcopy(self.packet)
        packet["guardrail_lookup_health_rows"][0]["source_activation_checklist_reference"] = ""
        self.assert_problem_contains(packet, "source_activation_checklist_reference must be non-empty")

    def test_rejects_live_monitoring_claims(self) -> None:
        packet = copy.deepcopy(self.packet)
        packet["notes"] = "live monitoring is now running"
        self.assert_problem_contains(packet, "forbidden live/mutation/official/guarantee/private claim")

    def test_rejects_active_mutation_claims_and_flags(self) -> None:
        packet = copy.deepcopy(self.packet)
        packet["active_mutation_enabled"] = True
        self.assert_problem_contains(packet, "active mutation flag is not allowed")

    def test_rejects_private_session_auth_artifacts(self) -> None:
        packet = copy.deepcopy(self.packet)
        packet["session_state"] = "state.json"
        self.assert_problem_contains(packet, "forbidden private/session/auth/raw artifact field")

    def test_rejects_official_action_completion_claims(self) -> None:
        packet = copy.deepcopy(self.packet)
        packet["notes"] = "official action completed"
        self.assert_problem_contains(packet, "forbidden live/mutation/official/guarantee/private claim")

    def test_rejects_legal_or_permitting_guarantees(self) -> None:
        packet = copy.deepcopy(self.packet)
        packet["notes"] = "permit approval guaranteed"
        self.assert_problem_contains(packet, "forbidden live/mutation/official/guarantee/private claim")


if __name__ == "__main__":
    unittest.main()
