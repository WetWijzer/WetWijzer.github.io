from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "process_model_impact_candidate_v4.py"
FIXTURE_PATH = Path(__file__).parent / "fixtures" / "process_model_impact_candidate_v4" / "fixture.json"

spec = importlib.util.spec_from_file_location("process_model_impact_candidate_v4", MODULE_PATH)
assert spec is not None
candidate = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(candidate)


class ProcessModelImpactCandidateV4Tests(unittest.TestCase):
    def _fixture(self) -> dict:
        return candidate.load_fixture(FIXTURE_PATH)

    def _packet(self) -> dict:
        return candidate.build_process_model_impact_candidate_v4(self._fixture())

    def assertValidationFails(self, packet: dict, expected: str) -> None:
        with self.assertRaises(ValueError) as context:
            candidate.validate_candidate_packet(packet)
        self.assertIn(expected, str(context.exception))

    def test_fixture_builds_valid_inactive_packet(self) -> None:
        packet = self._packet()

        candidate.validate_candidate_packet(packet)
        self.assertEqual(packet["packet_version"], "process_model_impact_candidate_v4")
        self.assertEqual(packet["status"], "inactive_candidate")
        self.assertTrue(packet["fixture_first"])
        self.assertEqual(packet["source_mode"], "fixture_only_requirement_reextraction_delta_queue_v4")
        self.assertTrue(all(value is False for value in packet["side_effects"].values()))

    def test_packet_covers_all_required_process_model_impact_labels(self) -> None:
        packet = self._packet()
        impact_areas = {row["impact_area"] for row in packet["inactive_changes"]}
        impact_labels = {row["impact_label"] for row in packet["inactive_changes"]}

        self.assertEqual(impact_areas, candidate.IMPACT_AREAS)
        self.assertEqual(impact_labels, set(candidate.REQUIRED_IMPACT_LABELS.values()))
        self.assertTrue(all(row["status"] == "inactive_candidate" for row in packet["inactive_changes"]))
        self.assertTrue(
            all(
                row["activation_policy"] == "do_not_apply_without_human_review_and_separate_activation"
                for row in packet["inactive_changes"]
            )
        )

    def test_packet_includes_requirement_queue_and_prior_placeholder_refs(self) -> None:
        packet = self._packet()

        self.assertTrue(packet["input_fixture_refs"]["requirement_queue_refs"])
        for row in packet["inactive_changes"]:
            self.assertTrue(row["requirement_queue_ref"].startswith(candidate.REQUIREMENT_QUEUE_PREFIX))
            self.assertEqual(row["prior_process_model_placeholder_ref"], row["process_model_id"])

    def test_packet_includes_unsupported_path_and_devhub_surface_handling(self) -> None:
        packet = self._packet()
        by_area = {row["impact_area"]: row for row in packet["inactive_changes"]}

        self.assertEqual(
            by_area["unsupported_paths"]["unsupported_path_handling"],
            "block_or_route_to_human_review_until_placeholder_is_promoted",
        )
        self.assertEqual(
            by_area["devhub_surface_refs"]["devhub_surface_ref_handling"],
            "reference_only_no_authenticated_observation_claim",
        )
        self.assertTrue(by_area["devhub_surface_refs"]["devhub_surface_ref"])

    def test_packet_includes_reviewer_holds_and_rollback_notes_for_each_change(self) -> None:
        packet = self._packet()
        change_ids = {row["change_id"] for row in packet["inactive_changes"]}
        hold_ids = {row["change_id"] for row in packet["reviewer_holds"]}
        rollback_ids = {row["change_id"] for row in packet["rollback_notes"]}

        self.assertEqual(hold_ids, change_ids)
        self.assertEqual(rollback_ids, change_ids)
        self.assertTrue(all(row["status"] == "held_for_review" for row in packet["reviewer_holds"]))
        self.assertTrue(all(row["rollback_scope"] == "inactive_candidate_only" for row in packet["rollback_notes"]))

    def test_packet_embeds_exact_offline_validation_commands(self) -> None:
        packet = self._packet()
        commands = packet["exact_offline_validation_commands"]

        self.assertIn(["python3", "ppd/daemon/ppd_daemon.py", "--self-test"], commands)
        self.assertIn(["python3", "-m", "unittest", "ppd.tests.test_process_model_impact_candidate_v4"], commands)
        self.assertTrue(all(isinstance(command, list) for command in commands))

    def test_rejects_unknown_placeholder_reference(self) -> None:
        fixture = self._fixture()
        fixture["requirement_reextraction_delta_queue_v4"][0]["process_model_id"] = "missing-placeholder"

        with self.assertRaises(ValueError) as context:
            candidate.build_process_model_impact_candidate_v4(fixture)
        self.assertIn("unknown process_model_id", str(context.exception))

    def test_rejects_missing_requirement_queue_reference(self) -> None:
        fixture = self._fixture()
        del fixture["requirement_reextraction_delta_queue_v4"][0]["requirement_queue_ref"]

        with self.assertRaises(ValueError) as context:
            candidate.build_process_model_impact_candidate_v4(fixture)
        self.assertIn("missing keys", str(context.exception))

    def test_rejects_missing_prior_process_model_placeholder_reference(self) -> None:
        fixture = self._fixture()
        fixture["requirement_reextraction_delta_queue_v4"][0]["prior_process_model_placeholder_ref"] = "other-placeholder"

        with self.assertRaises(ValueError) as context:
            candidate.build_process_model_impact_candidate_v4(fixture)
        self.assertIn("missing prior process model placeholder reference", str(context.exception))

    def test_rejects_missing_inactive_change_rows(self) -> None:
        packet = self._packet()
        packet["inactive_changes"] = []

        self.assertValidationFails(packet, "missing inactive change rows")

    def test_rejects_missing_impact_label_coverage(self) -> None:
        packet = self._packet()
        removed_change_id = "inactive-pm-impact-v4-eligibility-building-001"
        packet["inactive_changes"] = [row for row in packet["inactive_changes"] if row["impact_area"] != "eligibility_rules"]
        packet["reviewer_holds"] = [row for row in packet["reviewer_holds"] if row["change_id"] != removed_change_id]
        packet["rollback_notes"] = [row for row in packet["rollback_notes"] if row["change_id"] != removed_change_id]

        self.assertValidationFails(packet, "missing impact labels")

    def test_rejects_missing_unsupported_path_handling(self) -> None:
        packet = self._packet()
        for row in packet["inactive_changes"]:
            if row["impact_area"] == "unsupported_paths":
                del row["unsupported_path_handling"]

        self.assertValidationFails(packet, "missing unsupported-path handling")

    def test_rejects_missing_devhub_surface_reference_handling(self) -> None:
        packet = self._packet()
        for row in packet["inactive_changes"]:
            if row["impact_area"] == "devhub_surface_refs":
                del row["devhub_surface_ref_handling"]

        self.assertValidationFails(packet, "unsafe DevHub surface reference handling")

    def test_rejects_side_effects_and_active_mutation_flags(self) -> None:
        packet = self._packet()
        packet["side_effects"]["devhub_opened"] = True
        self.assertValidationFails(packet, "side_effects.devhub_opened must be false")

        packet = self._packet()
        packet["inactive_changes"][0]["active_process_model_mutation"] = True
        self.assertValidationFails(packet, "must not claim active process-model mutation")

    def test_rejects_missing_reviewer_hold(self) -> None:
        packet = self._packet()
        packet["reviewer_holds"].pop()

        self.assertValidationFails(packet, "each inactive change must have a reviewer hold")

    def test_rejects_missing_rollback_note(self) -> None:
        packet = self._packet()
        packet["rollback_notes"].pop()

        self.assertValidationFails(packet, "each inactive change must have a rollback note")

    def test_rejects_missing_validation_commands(self) -> None:
        packet = self._packet()
        packet["exact_offline_validation_commands"] = [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]]

        self.assertValidationFails(packet, "missing validation commands")

    def test_rejects_private_live_financial_or_browser_artifacts(self) -> None:
        packet = self._packet()
        packet["browser_state_path"] = "state.json"

        self.assertValidationFails(packet, "must not include private, live, financial, or browser artifacts")

    def test_rejects_live_action_or_guarantee_text(self) -> None:
        packet = self._packet()
        packet["inactive_changes"][0]["candidate_text"] = "permit will be approved"

        self.assertValidationFails(packet, "forbidden live-action or guarantee text")

    def test_rejects_official_action_completion_claims(self) -> None:
        packet = self._packet()
        packet["limitations"].append("completed official action")

        self.assertValidationFails(packet, "forbidden live-action or guarantee text")

    def test_rejects_non_placeholder_process_model_inputs(self) -> None:
        fixture = copy.deepcopy(self._fixture())
        fixture["process_model_placeholders"][0]["placeholder_only"] = False

        with self.assertRaises(ValueError) as context:
            candidate.build_process_model_impact_candidate_v4(fixture)
        self.assertIn("must be placeholder_only", str(context.exception))


if __name__ == "__main__":
    unittest.main()
