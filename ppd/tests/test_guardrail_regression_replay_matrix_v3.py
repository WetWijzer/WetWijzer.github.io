import json
import subprocess
import sys
import unittest
from pathlib import Path

from ppd.agent_readiness.guardrail_regression_replay_matrix_v3 import (
    ALLOWED_NEXT_ACTION_CLASSIFICATIONS,
    ATTESTATIONS,
    MATRIX_VERSION,
    MUTATION_FLAGS,
    REQUIRED_PACKET_IDS,
    build_matrix,
    load_source_packets,
    validate_matrix,
)

FIXTURE = Path(__file__).parent / "fixtures" / "guardrail_regression_replay_matrix_v3" / "source_packets.json"


class GuardrailRegressionReplayMatrixV3Test(unittest.TestCase):
    def setUp(self):
        self.source_packets = load_source_packets(FIXTURE)
        self.matrix = build_matrix(self.source_packets)

    def _broken_matrix(self):
        return json.loads(json.dumps(self.matrix))

    def assertValidationContains(self, broken, expected):
        self.assertIn(expected, validate_matrix(broken))

    def test_builds_fixture_first_v3_matrix_from_required_inactive_packets(self):
        self.assertEqual(self.matrix["version"], MATRIX_VERSION)
        self.assertTrue(self.matrix["fixture_first"])
        self.assertEqual([packet["id"] for packet in self.matrix["source_packets"]], list(REQUIRED_PACKET_IDS))
        self.assertTrue(all(packet["status"] == "inactive" for packet in self.matrix["source_packets"]))

    def test_contains_required_replay_families_with_reviewer_owners(self):
        scenario_ids = {scenario["id"] for scenario in self.matrix["scenarios"]}
        self.assertEqual(
            scenario_ids,
            {
                "missing-fact-prompts",
                "stale-conflicting-evidence-notices",
                "blocked-consequential-actions",
                "reversible-draft-previews",
                "explanation-templates",
            },
        )
        for scenario in self.matrix["scenarios"]:
            self.assertRegex(scenario["reviewer_owner"], r"reviewer$")
            self.assertIn(scenario["next_action_classification"], ALLOWED_NEXT_ACTION_CLASSIFICATIONS)
            self.assertTrue(scenario["gap_analysis_refs"])
            self.assertTrue(scenario["guardrail_refs"])
            self.assertIn("before_expected_outcome", scenario)
            self.assertIn("after_expected_outcome", scenario)

    def test_before_after_and_replay_rows_cite_all_source_packets(self):
        required = set(REQUIRED_PACKET_IDS)
        for scenario in self.matrix["scenarios"]:
            row_cited = {citation["packet_id"] for citation in scenario["replay_row_citations"]}
            self.assertEqual(row_cited, required)
            for key in ("before_expected_outcome", "after_expected_outcome"):
                outcome = scenario[key]
                cited = {citation["packet_id"] for citation in outcome["citations"]}
                self.assertEqual(cited, required)
                self.assertTrue(outcome["text"])

    def test_includes_offline_attestations_and_validation_commands(self):
        self.assertEqual(self.matrix["attestations"], ATTESTATIONS)
        joined = "\n".join(self.matrix["offline_validation_commands"])
        self.assertIn("unittest", joined)
        self.assertIn("--validate", joined)
        self.assertNotIn("devhub", joined.lower())
        self.assertNotIn("llm", joined.lower())

    def test_validator_accepts_matrix_and_rejects_live_llm_attestation_gap(self):
        self.assertEqual(validate_matrix(self.matrix), [])
        broken = self._broken_matrix()
        broken["attestations"]["no_live_llm"] = False
        self.assertValidationContains(broken, "attestation no_live_llm must be true")

    def test_validator_rejects_uncited_replay_rows_and_missing_expected_outcomes(self):
        broken = self._broken_matrix()
        broken["scenarios"][0]["replay_row_citations"] = []
        self.assertValidationContains(
            broken,
            "scenario missing-fact-prompts replay row must cite all required source packets",
        )

        broken = self._broken_matrix()
        del broken["scenarios"][0]["before_expected_outcome"]
        self.assertValidationContains(broken, "scenario missing-fact-prompts needs before_expected_outcome")

        broken = self._broken_matrix()
        del broken["scenarios"][0]["after_expected_outcome"]
        self.assertValidationContains(broken, "scenario missing-fact-prompts needs after_expected_outcome")

    def test_validator_rejects_missing_gap_analysis_or_guardrail_references(self):
        broken = self._broken_matrix()
        broken["scenarios"][0]["gap_analysis_refs"] = []
        self.assertValidationContains(broken, "scenario missing-fact-prompts needs gap_analysis_refs")

        broken = self._broken_matrix()
        broken["scenarios"][0]["guardrail_refs"] = []
        self.assertValidationContains(broken, "scenario missing-fact-prompts needs guardrail_refs")

    def test_validator_rejects_unsupported_next_action_classifications(self):
        broken = self._broken_matrix()
        broken["scenarios"][0]["next_action_classification"] = "perform_final_action"
        self.assertValidationContains(
            broken,
            "scenario missing-fact-prompts has unsupported next_action_classification",
        )

    def test_validator_rejects_private_authenticated_and_raw_artifact_payloads(self):
        forbidden_cases = [
            ("property_address", "123 Main St", "matrix must not contain private user facts"),
            ("devhub_record_id", "REC-123", "matrix must not contain authenticated DevHub values"),
            ("browser_trace", "trace.zip", "matrix must not contain raw document/session/browser artifacts"),
        ]
        for key, value, expected in forbidden_cases:
            broken = self._broken_matrix()
            broken["scenarios"][0][key] = value
            self.assertValidationContains(broken, expected)

    def test_validator_rejects_completion_claims_guarantees_and_final_action_language(self):
        forbidden_cases = [
            ("The live LLM completed this replay.", "matrix must not contain live LLM or DevHub completion claims"),
            ("Approval is certain for this permit.", "matrix must not contain legal or permitting outcome guarantees"),
            ("Click submit after reviewing this row.", "matrix must not contain final submission/payment/upload/scheduling/cancellation language"),
        ]
        for text, expected in forbidden_cases:
            broken = self._broken_matrix()
            broken["scenarios"][0]["after_expected_outcome"]["text"] = text
            self.assertValidationContains(broken, expected)

    def test_validator_rejects_active_mutation_flags(self):
        for flag in MUTATION_FLAGS:
            broken = self._broken_matrix()
            broken[flag] = True
            self.assertValidationContains(broken, f"mutation flag {flag} must be absent or false")

    def test_cli_validate_is_offline_and_successful(self):
        module_path = Path("ppd/agent_readiness/guardrail_regression_replay_matrix_v3.py")
        result = subprocess.run(
            [sys.executable, str(module_path), "--fixture", str(FIXTURE), "--validate"],
            check=False,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        rendered = json.loads(result.stdout)
        self.assertEqual(rendered["version"], MATRIX_VERSION)


if __name__ == "__main__":
    unittest.main()
