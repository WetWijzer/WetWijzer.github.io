from __future__ import annotations

import copy
import unittest

from ppd.devhub.reversible_draft_contract_v2 import (
    EXACT_CONFIRMATION_PHRASE,
    REQUIRED_CONSEQUENTIAL_EXAMPLES,
    REQUIRED_VALIDATION_COMMANDS,
    assert_valid_reversible_draft_contract_v2,
    validate_reversible_draft_contract_v2,
)


def _valid_packet() -> dict:
    return {
        "packet_type": "ppd.reversible_draft_executor_dry_run_contract.v2",
        "contract_version": 2,
        "request_response_rows": [
            {
                "row_id": "dry-run-contract-v2-001",
                "request": {"request_kind": "synthetic_preview_mapping_request", "preview_only": True},
                "response": {
                    "response_kind": "synthetic_preview_mapping_response",
                    "preview_only": True,
                    "executed_devhub_actions": [],
                    "saved_official_draft": False,
                    "submitted": False,
                },
                "preview_only_field_mapping_requirements": [
                    {"field_key": "project_address", "value_placeholder": "USER_FACT_PROJECT_ADDRESS_PLACEHOLDER", "preview_only": True}
                ],
                "user_fact_traces": [
                    {"trace_kind": "user_fact", "placeholder_id": "USER_FACT_PROJECT_ADDRESS_PLACEHOLDER"}
                ],
                "source_evidence_traces": [
                    {"trace_kind": "source_evidence", "placeholder_id": "SOURCE_EVIDENCE_ADDRESS_PLACEHOLDER"}
                ],
                "selector_confidence_placeholder": {"placeholder": True, "value": None, "reason": "offline contract does not inspect live selectors"},
                "exact_confirmation_stop_gate": {"requires_exact_confirmation": True, "confirmation_phrase": EXACT_CONFIRMATION_PHRASE},
            }
        ],
        "refused_consequential_action_examples": sorted(REQUIRED_CONSEQUENTIAL_EXAMPLES),
        "validation_commands": [list(command) for command in REQUIRED_VALIDATION_COMMANDS],
        "active_mutation_flags": {
            "active_prompt_mutated": False,
            "active_guardrail_mutated": False,
            "active_devhub_surface_mutated": False,
            "active_source_mutated": False,
            "active_contract_mutated": False,
            "active_release_state_mutated": False,
        },
    }


class ReversibleDraftContractV2Tests(unittest.TestCase):
    def test_valid_packet_passes(self) -> None:
        packet = _valid_packet()
        self.assertEqual([], validate_reversible_draft_contract_v2(packet))
        assert_valid_reversible_draft_contract_v2(packet)

    def test_rejects_missing_request_response_rows(self) -> None:
        packet = _valid_packet()
        packet["request_response_rows"] = []
        self.assertIssue(packet, "request_response_rows")

    def test_rejects_missing_row_contract_requirements(self) -> None:
        for field, expected in (
            ("preview_only_field_mapping_requirements", "field_mapping"),
            ("user_fact_traces", "user_fact_traces"),
            ("source_evidence_traces", "source_evidence_traces"),
            ("selector_confidence_placeholder", "selector_confidence_placeholder"),
            ("exact_confirmation_stop_gate", "exact_confirmation_stop_gate"),
        ):
            with self.subTest(field=field):
                packet = _valid_packet()
                del packet["request_response_rows"][0][field]
                self.assertIssue(packet, expected)

    def test_rejects_non_preview_mapping_selector_and_stop_gate(self) -> None:
        packet = _valid_packet()
        row = packet["request_response_rows"][0]
        row["preview_only_field_mapping_requirements"][0]["preview_only"] = False
        row["selector_confidence_placeholder"] = {"placeholder": False, "value": 0.95}
        row["exact_confirmation_stop_gate"]["confirmation_phrase"] = "continue"
        issues = "\n".join(validate_reversible_draft_contract_v2(packet))
        self.assertIn("preview_only", issues)
        self.assertIn("selector_confidence_placeholder", issues)
        self.assertIn("confirmation_phrase", issues)

    def test_rejects_missing_refusals_and_validation_commands(self) -> None:
        packet = _valid_packet()
        packet["refused_consequential_action_examples"] = ["submit_application"]
        packet["validation_commands"] = []
        issues = "\n".join(validate_reversible_draft_contract_v2(packet))
        self.assertIn("refused_consequential_action_examples", issues)
        self.assertIn("validation_commands", issues)

    def test_rejects_private_artifacts_live_claims_official_claims_and_guarantees(self) -> None:
        for value in (
            "browser trace stored for replay",
            "downloaded artifact in Downloads/file.pdf",
            "raw DevHub session payload",
            "opened live DevHub and filled live form",
            "saved official draft and submitted application",
            "permit approved with guaranteed approval",
        ):
            with self.subTest(value=value):
                packet = _valid_packet()
                packet["notes"] = value
                self.assertIssue(packet, "forbidden dry-run contract content")

    def test_rejects_active_mutation_flags(self) -> None:
        for flag in _valid_packet()["active_mutation_flags"]:
            with self.subTest(flag=flag):
                packet = _valid_packet()
                packet["active_mutation_flags"][flag] = True
                self.assertIssue(packet, flag)

    def test_rejects_execution_response_claims(self) -> None:
        packet = _valid_packet()
        packet["request_response_rows"][0]["response"]["executed_devhub_actions"] = ["click-submit"]
        packet["request_response_rows"][0]["response"]["saved_official_draft"] = True
        packet["request_response_rows"][0]["response"]["submitted"] = True
        issues = "\n".join(validate_reversible_draft_contract_v2(packet))
        self.assertIn("executed_devhub_actions", issues)
        self.assertIn("saved_official_draft", issues)
        self.assertIn("submitted", issues)

    def assertIssue(self, packet: dict, expected: str) -> None:
        issues = validate_reversible_draft_contract_v2(copy.deepcopy(packet))
        self.assertTrue(issues, "expected validation issues")
        self.assertIn(expected, "\n".join(issues))


if __name__ == "__main__":
    unittest.main()
