from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from ppd.devhub.reversible_draft_plan import (
    ReversibleDraftPlanError,
    validate_plan,
    validate_plan_file,
)


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "devhub" / "attended_reversible_draft_plan.json"


class DevHubReversibleDraftPlanTests(unittest.TestCase):
    def _fixture(self) -> dict[str, object]:
        return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    def test_fixture_first_reversible_draft_plan_passes(self) -> None:
        result = validate_plan_file(FIXTURE_PATH)

        self.assertEqual(result.plan_id, "devhub_attended_address_property_permit_form_save_plan")
        self.assertEqual(result.step_count, 4)
        self.assertEqual(result.case_fact_count, 4)
        self.assertEqual(result.surface_fixture_count, 3)
        self.assertEqual(result.source_evidence_count, 3)
        self.assertEqual(result.blocked_action_count, 9)
        self.assertEqual(
            result.step_kinds,
            (
                "address_property_search",
                "form_field_entry",
                "permit_type_selection",
                "save_for_later",
            ),
        )

    def test_rejects_missing_manual_login_prerequisite(self) -> None:
        plan = self._fixture()
        mutated = copy.deepcopy(plan)
        handoff = mutated["manual_login_handoff"]
        self.assertIsInstance(handoff, dict)
        handoff["prerequisites"] = ["user_owned_devhub_account"]

        with self.assertRaisesRegex(ReversibleDraftPlanError, "manual_login_handoff missing"):
            validate_plan(mutated)

    def test_rejects_private_session_artifact_fields(self) -> None:
        plan = self._fixture()
        mutated = copy.deepcopy(plan)
        mutated["storage_state"] = "redacted"

        with self.assertRaisesRegex(ReversibleDraftPlanError, "forbidden private field"):
            validate_plan(mutated)

    def test_rejects_non_synthetic_case_fact(self) -> None:
        plan = self._fixture()
        mutated = copy.deepcopy(plan)
        facts = mutated["synthetic_case_facts"]
        self.assertIsInstance(facts, list)
        first_fact = facts[0]
        self.assertIsInstance(first_fact, dict)
        first_fact["value_class"] = "private"

        with self.assertRaisesRegex(ReversibleDraftPlanError, "must be synthetic"):
            validate_plan(mutated)

    def test_rejects_unredacted_accessible_structure_fixture(self) -> None:
        plan = self._fixture()
        mutated = copy.deepcopy(plan)
        surfaces = mutated["accessible_structure_fixtures"]
        self.assertIsInstance(surfaces, list)
        first_surface = surfaces[0]
        self.assertIsInstance(first_surface, dict)
        first_surface["contains_private_values"] = True

        with self.assertRaisesRegex(ReversibleDraftPlanError, "must not contain private values"):
            validate_plan(mutated)

    def test_rejects_missing_save_for_later_coverage(self) -> None:
        plan = self._fixture()
        mutated = copy.deepcopy(plan)
        steps = mutated["workflow_steps"]
        self.assertIsInstance(steps, list)
        mutated["workflow_steps"] = [
            step for step in steps if isinstance(step, dict) and step.get("step_kind") != "save_for_later"
        ]

        with self.assertRaisesRegex(ReversibleDraftPlanError, "missing required reversible draft coverage"):
            validate_plan(mutated)

    def test_rejects_form_field_entry_without_redacted_value(self) -> None:
        plan = self._fixture()
        mutated = copy.deepcopy(plan)
        steps = mutated["workflow_steps"]
        self.assertIsInstance(steps, list)
        form_step = next(step for step in steps if isinstance(step, dict) and step.get("step_kind") == "form_field_entry")
        entries = form_step["field_entries"]
        self.assertIsInstance(entries, list)
        first_entry = entries[0]
        self.assertIsInstance(first_entry, dict)
        first_entry["field_value_redacted"] = False

        with self.assertRaisesRegex(ReversibleDraftPlanError, "must redact the field value"):
            validate_plan(mutated)

    def test_rejects_unknown_source_evidence_reference(self) -> None:
        plan = self._fixture()
        mutated = copy.deepcopy(plan)
        steps = mutated["workflow_steps"]
        self.assertIsInstance(steps, list)
        first_step = steps[0]
        self.assertIsInstance(first_step, dict)
        first_step["source_evidence_ids"] = ["missing-source-evidence"]

        with self.assertRaisesRegex(ReversibleDraftPlanError, "unknown source evidence id"):
            validate_plan(mutated)


if __name__ == "__main__":
    unittest.main()
