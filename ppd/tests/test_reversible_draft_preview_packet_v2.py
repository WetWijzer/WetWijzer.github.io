from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path
from typing import Any

from ppd.reversible_draft_preview_packet_v2_validation import (
    REQUIRED_NONEMPTY_SECTIONS,
    validate_reversible_draft_preview_packet_v2,
)


_FIXTURE_DIR = Path(__file__).parent / "fixtures"
_PACKET_PATH = _FIXTURE_DIR / "reversible_draft_preview_packet_v2.json"
_MATRIX_PATH = _FIXTURE_DIR / "reversible_draft_action_readiness_matrix_v2.json"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


class ReversibleDraftPreviewPacketV2Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.packet = _load(_PACKET_PATH)
        self.matrix = _load(_MATRIX_PATH)

    def test_packet_consumes_reversible_draft_action_readiness_matrix_v2(self) -> None:
        consumption = self.packet["source_matrix_consumption"]
        self.assertEqual(consumption["matrix_id"], self.matrix["matrix_id"])
        self.assertEqual(consumption["matrix_version"], self.matrix["matrix_version"])
        self.assertEqual(
            consumption["consumed_scenario_ids"],
            [scenario["scenario_id"] for scenario in self.matrix["synthetic_reversible_draft_scenarios"]],
        )
        self.assertEqual(
            set(consumption["consumed_field_mapping_ids"]),
            {mapping["mapping_id"] for mapping in self.matrix["preview_only_field_mapping_placeholders"]},
        )
        self.assertEqual(
            set(consumption["consumed_stop_gate_ids"]),
            {gate["gate_id"] for gate in self.matrix["exact_confirmation_stop_gates"]},
        )

    def test_preview_rows_are_ordered_from_matrix_scenarios(self) -> None:
        rows = self.packet["synthetic_preview_rows"]
        scenarios = self.matrix["synthetic_reversible_draft_scenarios"]
        self.assertEqual([row["order"] for row in rows], [1, 2, 3, 4])
        self.assertEqual([row["scenario_id"] for row in rows], [scenario["scenario_id"] for scenario in scenarios])
        self.assertEqual([row["classification"] for row in rows], [scenario["classification"] for scenario in scenarios])
        self.assertEqual([row["action_fixture_id"] for row in rows], [scenario["action_fixture_id"] for scenario in scenarios])

    def test_valid_fixture_passes_reusable_validator(self) -> None:
        self.assertEqual([], validate_reversible_draft_preview_packet_v2(self.packet))

    def test_validator_rejects_missing_required_sections_and_preview_rows(self) -> None:
        for section in REQUIRED_NONEMPTY_SECTIONS:
            with self.subTest(section=section):
                candidate = copy.deepcopy(self.packet)
                candidate[section] = [] if section != "source_matrix_consumption" else {}
                self.assertTrue(any(section in issue for issue in validate_reversible_draft_preview_packet_v2(candidate)))

    def test_validator_rejects_missing_row_placeholders_traces_redactions_reasons_and_stop_gates(self) -> None:
        cases = (
            ("draft_only_field_value_placeholder_ids", [], "draft-only field/value placeholders"),
            ("user_fact_trace_placeholder_ids", [], "user-fact traces"),
            ("source_evidence_trace_placeholder_ids", [], "source-evidence traces"),
            ("redaction_note_id", "missing-redaction-note", "redaction note"),
            ("not_ready_reason_ids", [], "not-ready reasons"),
            ("stop_gate_summary_ids", [], "exact-confirmation stop gate summary"),
        )
        for key, value, expected in cases:
            with self.subTest(key=key):
                candidate = copy.deepcopy(self.packet)
                row = candidate["synthetic_preview_rows"][2]
                row[key] = value
                self.assertTrue(any(expected in issue for issue in validate_reversible_draft_preview_packet_v2(candidate)))

    def test_validator_rejects_unknown_row_references(self) -> None:
        cases = (
            ("draft_only_field_value_placeholder_ids", ["missing-draft-placeholder"], "unknown draft placeholder"),
            ("user_fact_trace_placeholder_ids", ["missing-user-trace"], "unknown user-fact trace"),
            ("source_evidence_trace_placeholder_ids", ["missing-evidence-trace"], "unknown source-evidence trace"),
            ("not_ready_reason_ids", ["missing-not-ready-reason"], "unknown not-ready reason"),
            ("stop_gate_summary_ids", ["missing-stop-gate"], "unknown stop gate summary"),
        )
        for key, value, expected in cases:
            with self.subTest(key=key):
                candidate = copy.deepcopy(self.packet)
                candidate["synthetic_preview_rows"][2][key] = value
                self.assertTrue(any(expected in issue for issue in validate_reversible_draft_preview_packet_v2(candidate)))

    def test_validator_rejects_broken_placeholders_traces_redactions_gates_and_commands(self) -> None:
        cases = (
            ("draft_only_field_value_placeholders", "field_placeholder", "Project Description", "placeholder-only"),
            ("draft_only_field_value_placeholders", "value_placeholder", "real value", "placeholder-only"),
            ("draft_only_field_value_placeholders", "writes_devhub_state", True, "must not write"),
            ("draft_only_field_value_placeholders", "saves_official_draft", True, "save official drafts"),
            ("user_fact_trace_placeholders", "actual_user_value", "private value", "actual user value"),
            ("source_evidence_trace_placeholders", "live_url_fetched", True, "live fetch"),
            ("redaction_notes", "contains_private_values", True, "private values are absent"),
            ("exact_confirmation_stop_gate_summaries", "allowed_without_exact_confirmation", True, "fail closed"),
        )
        for section, key, value, expected in cases:
            with self.subTest(section=section, key=key):
                candidate = copy.deepcopy(self.packet)
                candidate[section][0][key] = value
                self.assertTrue(any(expected in issue for issue in validate_reversible_draft_preview_packet_v2(candidate)))

        candidate = copy.deepcopy(self.packet)
        candidate["offline_validation_commands"] = []
        self.assertTrue(any("validation command" in issue for issue in validate_reversible_draft_preview_packet_v2(candidate)))

    def test_validator_rejects_private_artifacts_live_claims_official_claims_guarantees_and_mutations(self) -> None:
        cases = (
            ("artifact", lambda p: p.update({"operator_note": "private session browser artifact raw crawl downloaded document"}), "artifact"),
            ("live", lambda p: p.update({"operator_note": "live DevHub execution completed"}), "forbidden live"),
            ("official", lambda p: p.update({"operator_note": "official draft saved"}), "official completion"),
            ("guarantee", lambda p: p.update({"operator_note": "permit will issue and approval is guaranteed"}), "guarantee"),
        )
        for label, mutate, expected in cases:
            with self.subTest(label=label):
                candidate = copy.deepcopy(self.packet)
                mutate(candidate)
                self.assertTrue(any(expected in issue for issue in validate_reversible_draft_preview_packet_v2(candidate)))

        mutation_flags = self.packet["mutation_flags"].keys()
        for flag_name in mutation_flags:
            with self.subTest(flag_name=flag_name):
                candidate = copy.deepcopy(self.packet)
                candidate[flag_name] = True
                self.assertTrue(any("active mutation flag" in issue for issue in validate_reversible_draft_preview_packet_v2(candidate)))

    def test_validator_rejects_policy_claim_or_prohibition_truthy_flags(self) -> None:
        cases = (
            ("artifact_policy", "captures_browser_artifacts"),
            ("claim_policy", "claims_live_devhub_execution"),
            ("claim_policy", "claims_official_draft_saved"),
            ("claim_policy", "claims_official_submission"),
            ("claim_policy", "makes_legal_guarantees"),
            ("mutation_flags", "active_prompt_mutation"),
            ("mutation_flags", "active_guardrail_mutation"),
            ("mutation_flags", "active_devhub_surface_mutation"),
            ("mutation_flags", "active_source_mutation"),
            ("mutation_flags", "active_contract_mutation"),
            ("mutation_flags", "active_release_state_mutation"),
            ("prohibition_attestations", "saves_official_drafts"),
        )
        for section, key in cases:
            with self.subTest(section=section, key=key):
                candidate = copy.deepcopy(self.packet)
                candidate[section][key] = True
                self.assertTrue(any(key in issue or "active mutation flag" in issue for issue in validate_reversible_draft_preview_packet_v2(candidate)))


if __name__ == "__main__":
    unittest.main()
