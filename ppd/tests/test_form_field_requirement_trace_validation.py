"""Fixture-only validation for PP&D form-field requirement trace packets."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from ppd.validation.form_field_requirement_trace import (
    FormFieldRequirementTraceError,
    require_form_field_requirement_trace_packet,
    validate_form_field_requirement_trace_packet,
)


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "devhub" / "form_field_requirement_trace_packets.json"


class FormFieldRequirementTraceValidationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    def test_valid_packet_passes_without_findings(self) -> None:
        result = validate_form_field_requirement_trace_packet(self.fixture["valid_packet"])

        self.assertTrue(result.ok)
        self.assertEqual((), result.findings)

    def test_invalid_packet_rejects_all_required_risk_classes(self) -> None:
        result = validate_form_field_requirement_trace_packet(self.fixture["invalid_packet"])

        self.assertFalse(result.ok)
        self.assertEqual(
            {
                "ambiguous_selector",
                "credential_value",
                "irreversible_action_marked_reversible",
                "payment_detail",
                "private_value",
                "stale_evidence",
                "uncited_field",
                "unsupported_requirement_type",
            },
            {finding.code for finding in result.findings},
        )

    def test_require_helper_raises_with_finding_codes(self) -> None:
        with self.assertRaises(FormFieldRequirementTraceError) as context:
            require_form_field_requirement_trace_packet(self.fixture["invalid_packet"])

        self.assertIn("uncited_field", str(context.exception))
        self.assertTrue(context.exception.findings)

    def test_certification_and_submission_fields_cannot_be_reversible(self) -> None:
        packet = json.loads(json.dumps(self.fixture["valid_packet"]))
        packet["fields"][1]["reversible"] = True

        result = validate_form_field_requirement_trace_packet(packet)

        self.assertIn("irreversible_action_marked_reversible", {finding.code for finding in result.findings})


if __name__ == "__main__":
    unittest.main()
