import json
import subprocess
import sys
import unittest
from pathlib import Path

from ppd.agent_readiness.guardrail_regression_replay_queue_v1 import (
    AFFECTED_FIXTURE_KEYS,
    ATTESTATIONS,
    MUTATION_FLAGS,
    QUEUE_VERSION,
    build_queue,
    load_source_inputs,
    validate_queue,
)

FIXTURE = Path(__file__).parent / "fixtures" / "guardrail_regression_replay_queue_v1" / "source_inputs.json"


class GuardrailRegressionReplayQueueV1Test(unittest.TestCase):
    def setUp(self):
        self.source_inputs = load_source_inputs(FIXTURE)
        self.queue = build_queue(self.source_inputs)

    def _broken_queue(self):
        return json.loads(json.dumps(self.queue))

    def assertValidationContains(self, queue, expected):
        self.assertIn(expected, validate_queue(queue))

    def test_builds_fixture_first_queue_from_combined_packet_and_affected_fixture_ids(self):
        self.assertEqual(self.queue["version"], QUEUE_VERSION)
        self.assertTrue(self.queue["fixture_first"])
        self.assertEqual(
            self.queue["combined_promotion_dependency_packet_v1"]["id"],
            "combined-promotion-dependency-packet-v1.fixture",
        )
        for key in AFFECTED_FIXTURE_KEYS:
            self.assertIn(key, self.queue["affected_fixture_ids"])
            self.assertTrue(self.queue["affected_fixture_ids"][key])

    def test_replay_cases_have_citations_expected_outcomes_checks_and_rollback_notes(self):
        self.assertEqual(
            {case["id"] for case in self.queue["replay_cases"]},
            {
                "requirement-still-supported-pass",
                "stale-evidence-block",
                "missing-exact-confirmation-block",
                "conflicting-action-classification-block",
            },
        )
        outcomes = {case["expected_outcome"] for case in self.queue["replay_cases"]}
        self.assertEqual(outcomes, {"pass", "block"})
        for case in self.queue["replay_cases"]:
            sections = {citation["section"] for citation in case["citations"]}
            self.assertIn("combined_promotion_dependency_packet_v1", sections)
            self.assertIn("affected_requirement_fixture_ids", sections)
            self.assertIn("affected_process_fixture_ids", sections)
            self.assertIn("affected_guardrail_fixture_ids", sections)
            self.assertIn("affected_user_gap_fixture_ids", sections)
            self.assertIn("affected_devhub_action_classification_fixture_ids", sections)
            self.assertIn(case["stale_or_conflicting_evidence_check"]["expected"], {"clear", "block"})
            self.assertIn("required", case["exact_confirmation_gate_check"])
            self.assertIn(case["blocked_action_check"]["expected"], {"none", "block"})
            self.assertTrue(case["rollback_note"])

    def test_includes_offline_attestations_and_commands_without_active_bundle_changes(self):
        self.assertEqual(self.queue["attestations"], ATTESTATIONS)
        self.assertTrue(self.queue["attestations"]["no_active_guardrail_bundle_changes"])
        joined = "\n".join(self.queue["offline_validation_commands"])
        self.assertIn("unittest", joined)
        self.assertIn("--validate", joined)

    def test_validator_accepts_queue_and_rejects_attestation_gap(self):
        self.assertEqual(validate_queue(self.queue), [])
        broken = self._broken_queue()
        broken["attestations"]["no_active_guardrail_bundle_changes"] = False
        self.assertValidationContains(broken, "attestation no_active_guardrail_bundle_changes must be true")

    def test_validator_rejects_uncited_or_incomplete_replay_cases(self):
        broken = self._broken_queue()
        broken["replay_cases"][0]["citations"] = []
        self.assertValidationContains(
            broken,
            "replay case requirement-still-supported-pass must cite packet and affected fixture classes",
        )

        broken = self._broken_queue()
        del broken["replay_cases"][0]["fixture_refs"]["guardrail"]
        self.assertValidationContains(
            broken,
            "replay case requirement-still-supported-pass must reference all affected fixture classes",
        )

        broken = self._broken_queue()
        broken["affected_fixture_ids"]["affected_requirement_fixture_ids"] = []
        self.assertValidationContains(broken, "affected_requirement_fixture_ids must be present")

    def test_validator_rejects_missing_checks_rollback_notes_and_bad_outcomes(self):
        broken = self._broken_queue()
        broken["replay_cases"][0]["expected_outcome"] = "maybe"
        self.assertValidationContains(broken, "replay case requirement-still-supported-pass expected_outcome must be pass or block")

        broken = self._broken_queue()
        broken["replay_cases"][0]["stale_or_conflicting_evidence_check"] = {}
        self.assertValidationContains(broken, "replay case requirement-still-supported-pass needs stale-or-conflicting evidence check")

        broken = self._broken_queue()
        broken["replay_cases"][0]["exact_confirmation_gate_check"] = {}
        self.assertValidationContains(broken, "replay case requirement-still-supported-pass needs exact-confirmation gate check")

        broken = self._broken_queue()
        broken["replay_cases"][0]["blocked_action_check"] = {}
        self.assertValidationContains(broken, "replay case requirement-still-supported-pass needs blocked-action check")

        broken = self._broken_queue()
        broken["replay_cases"][1]["blocked_action_check"] = {"expected": "none"}
        self.assertValidationContains(broken, "replay case stale-evidence-block blocked-action check must expect block for block outcomes")

        broken = self._broken_queue()
        broken["replay_cases"][0]["rollback_note"] = ""
        self.assertValidationContains(broken, "replay case requirement-still-supported-pass needs rollback note")

    def test_validator_rejects_private_authenticated_and_local_artifacts(self):
        broken = self._broken_queue()
        broken["private_artifact"] = "private DevHub session file"
        errors = validate_queue(broken)
        self.assertIn("restricted private or authenticated artifact field private_artifact must be absent or empty", errors)
        self.assertIn("queue must not reference private/authenticated artifacts", errors)

        broken = self._broken_queue()
        broken["replay_cases"][0]["review_note"] = "Use the screenshot from the authenticated artifact."
        self.assertValidationContains(broken, "queue must not reference private/authenticated artifacts")

    def test_validator_rejects_outcome_guarantees_and_consequential_execution_language(self):
        broken = self._broken_queue()
        broken["replay_cases"][0]["review_note"] = "This permit will be approved after replay."
        self.assertValidationContains(broken, "queue must not contain legal or permitting outcome guarantees")

        broken = self._broken_queue()
        broken["replay_cases"][0]["review_note"] = "The agent may submit permit after this replay."
        self.assertValidationContains(broken, "queue must not contain consequential action execution language")

    def test_validator_rejects_active_mutation_flags(self):
        for flag in MUTATION_FLAGS:
            broken = self._broken_queue()
            broken[flag] = True
            self.assertValidationContains(broken, f"mutation flag {flag} must be absent or false")

    def test_validator_rejects_nested_mutation_flags_for_active_state(self):
        broken = self._broken_queue()
        broken["candidate"] = {"active_surface_registry_mutation": True}
        self.assertValidationContains(broken, "mutation flag active_surface_registry_mutation must be absent or false")

        broken = self._broken_queue()
        broken["candidate"] = {"mutates_agent_state": True}
        self.assertValidationContains(broken, "mutation flag mutates_agent_state must be absent or false")

    def test_cli_validate_is_offline_and_successful(self):
        module_path = Path("ppd/agent_readiness/guardrail_regression_replay_queue_v1.py")
        result = subprocess.run(
            [sys.executable, str(module_path), "--fixture", str(FIXTURE), "--validate"],
            check=False,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        rendered = json.loads(result.stdout)
        self.assertEqual(rendered["version"], QUEUE_VERSION)


if __name__ == "__main__":
    unittest.main()
