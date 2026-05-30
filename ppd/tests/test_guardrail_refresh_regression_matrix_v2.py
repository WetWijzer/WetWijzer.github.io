from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import unittest

from ppd.agent_readiness.guardrail_refresh_regression_matrix_v2 import (
    load_guardrail_refresh_regression_matrix_v2_packet,
    validate_guardrail_refresh_regression_matrix_v2_packet,
)

FIXTURE = Path(__file__).parent / "fixtures" / "agent_readiness" / "guardrail_refresh_regression_matrix_v2_valid.json"


class GuardrailRefreshRegressionMatrixV2ValidationTests(unittest.TestCase):
    def packet(self) -> dict[str, object]:
        return load_guardrail_refresh_regression_matrix_v2_packet(FIXTURE)

    def problem_text(self, packet: dict[str, object]) -> str:
        result = validate_guardrail_refresh_regression_matrix_v2_packet(packet)
        self.assertFalse(result.valid)
        return "; ".join(result.problems)

    def test_valid_fixture_loads(self) -> None:
        result = validate_guardrail_refresh_regression_matrix_v2_packet(self.packet())
        self.assertTrue(result.valid, result.problems)

    def test_rejects_uncited_scenario_expectations(self) -> None:
        packet = self.packet()
        scenarios = packet["scenario_expectations"]
        assert isinstance(scenarios, list)
        scenario = scenarios[0]
        assert isinstance(scenario, dict)
        scenario["source_evidence_ids"] = []

        self.assertIn("source_evidence_ids must cite scenario expectations", self.problem_text(packet))

    def test_rejects_missing_pass_fail_disposition(self) -> None:
        packet = self.packet()
        scenarios = packet["scenario_expectations"]
        assert isinstance(scenarios, list)
        scenario = scenarios[0]
        assert isinstance(scenario, dict)
        scenario.pop("expected_disposition")

        self.assertIn("expected_disposition must be pass or fail", self.problem_text(packet))

    def test_rejects_missing_rollback_notes(self) -> None:
        packet = self.packet()
        packet["rollback_notes"] = ""
        scenarios = packet["scenario_expectations"]
        assert isinstance(scenarios, list)
        scenario = scenarios[0]
        assert isinstance(scenario, dict)
        scenario["rollback_notes"] = ""

        problems = self.problem_text(packet)
        self.assertIn("rollback_notes must be present", problems)
        self.assertIn("scenario_expectations[0].rollback_notes must be present", problems)

    def test_rejects_missing_reviewer_owner(self) -> None:
        packet = self.packet()
        scenarios = packet["scenario_expectations"]
        assert isinstance(scenarios, list)
        scenario = scenarios[0]
        assert isinstance(scenario, dict)
        scenario["reviewer_owner"] = ""

        self.assertIn("reviewer_owner must be present", self.problem_text(packet))

    def test_rejects_private_authenticated_facts_and_local_paths(self) -> None:
        packet = self.packet()
        packet["diagnostics"] = {
            "auth_scope": "devhub_authenticated",
            "email": "resident@example.test",
            "local_file_path": "/home/resident/private/devhub-note.txt",
        }

        problems = self.problem_text(packet)
        self.assertIn("private or authenticated facts", problems)
        self.assertIn("local private paths", problems)

    def test_rejects_raw_session_browser_and_download_artifacts(self) -> None:
        packet = self.packet()
        packet["artifacts"] = {
            "browser_trace": "trace.zip",
            "session_artifact": "session artifact redacted.zip",
            "download_path": "/tmp/downloads/devhub.pdf",
        }

        self.assertIn("raw session, browser, crawl, download, WARC, or local artifacts", self.problem_text(packet))

    def test_rejects_live_execution_claims(self) -> None:
        packet = self.packet()
        packet["notes"] = "The live LLM called LLM tools, opened DevHub, ran browser steps, executed a live crawl, and ran processor execution."

        self.assertIn("must not claim live LLM, DevHub, browser, crawler, or processor execution", self.problem_text(packet))

    def test_rejects_outcome_guarantees(self) -> None:
        packet = self.packet()
        packet["notes"] = "This guarantees approval and the permit will issue with no legal risk."

        self.assertIn("must not guarantee legal or permitting outcomes", self.problem_text(packet))

    def test_rejects_final_consequential_action_language(self) -> None:
        blocked_phrases = [
            "final submit",
            "pay the fee",
            "upload corrections",
            "schedule inspection",
            "cancel permit",
        ]
        for phrase in blocked_phrases:
            with self.subTest(phrase=phrase):
                packet = self.packet()
                packet["notes"] = f"The packet says to {phrase}."
                self.assertIn(
                    "must not include final submission, payment, upload, scheduling, or cancellation language",
                    self.problem_text(packet),
                )

    def test_rejects_active_mutation_flags(self) -> None:
        base = self.packet()
        cases = [
            ("active_guardrail_mutation", True),
            ("active_prompt_mutation", True),
            ("active_surface_registry_mutation", True),
            ("active_monitoring_mutation", True),
            ("active_release_state_mutation", True),
            ("active_agent_state_mutation", True),
        ]
        for key, value in cases:
            with self.subTest(key=key):
                packet = deepcopy(base)
                packet[key] = value
                self.assertIn("must not set active mutation flags", self.problem_text(packet))

    def test_rejects_nested_mutation_flags(self) -> None:
        packet = self.packet()
        packet["candidate"] = {"mutation_flags": {"guardrail_mutation": True}}

        self.assertIn("mutation_flags.guardrail_mutation must be false", self.problem_text(packet))


if __name__ == "__main__":
    unittest.main()
