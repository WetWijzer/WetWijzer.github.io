from __future__ import annotations

import unittest
from datetime import date

from ppd.logic.process_model_assembly_validation import (
    assert_valid_process_model_assembly_packet,
    validate_process_model_assembly_packet,
)


class ProcessModelAssemblyValidationTests(unittest.TestCase):
    def _valid_packet(self) -> dict:
        return {
            "source_evidence": {
                "ev-file": {"source_evidence_id": "ev-file", "last_seen_at": "2026-05-01"},
                "ev-doc": {"source_evidence_id": "ev-doc", "last_seen_at": "2026-05-01"},
                "ev-stage": {"source_evidence_id": "ev-stage", "last_seen_at": "2026-05-01"},
            },
            "requirements": [
                {
                    "requirement_id": "req-doc",
                    "requirement_type": "document_requirement",
                    "source_evidence_ids": ["ev-doc"],
                }
            ],
            "process_model": {
                "process_id": "building-permit-fixture",
                "required_documents": [
                    {"document_id": "plans", "source_evidence_ids": ["ev-doc"]}
                ],
                "file_rules": [
                    {"rule_id": "single-pdf", "source_evidence_ids": ["ev-file"]}
                ],
                "unsupported_paths": [
                    {
                        "path_id": "email-only-paths",
                        "description": "Some permit types are not supported by DevHub.",
                        "source_evidence_ids": ["ev-stage"],
                    }
                ],
                "stages": [
                    {
                        "name": "document preparation",
                        "source_evidence_ids": ["ev-stage"],
                    },
                    {
                        "name": "submission",
                        "source_evidence_ids": ["ev-stage"],
                        "action_gate_id": "confirm-submit",
                    },
                ],
                "guardrail_bundle_id": "guard-building-permit-fixture",
            },
            "guardrail_bundles": {
                "guard-building-permit-fixture": {
                    "guardrail_bundle_id": "guard-building-permit-fixture",
                    "deterministic_predicates": ["has_required_documents"],
                }
            },
        }

    def test_accepts_source_grounded_packet(self) -> None:
        result = validate_process_model_assembly_packet(
            self._valid_packet(),
            now=date(2026, 5, 28),
            max_evidence_age_days=60,
        )
        self.assertTrue(result.ok)
        self.assertEqual((), result.issues)

    def test_rejects_required_failure_modes(self) -> None:
        packet = {
            "source_evidence": {
                "old": {"source_evidence_id": "old", "last_seen_at": "2025-01-01"}
            },
            "requirements": [
                {"requirement_id": "orphan", "source_evidence_ids": ["missing"]}
            ],
            "process_model": {
                "process_id": "bad-fixture",
                "required_documents": [{"document_id": "plans"}],
                "file_rules": [{"rule_id": "name-pdfs"}],
                "stages": [
                    {"name": "document preparation"},
                    {"name": "fee payment", "source_evidence_ids": ["old"]},
                ],
                "unsupported_paths": [],
                "guardrail_bundle_id": "asserted-only",
            },
            "guardrail_bundles": {
                "asserted-only": {
                    "guardrail_bundle_id": "asserted-only",
                    "deterministic_predicates": [],
                }
            },
        }

        result = validate_process_model_assembly_packet(
            packet,
            now=date(2026, 5, 28),
            max_evidence_age_days=90,
        )

        self.assertFalse(result.ok)
        codes = {issue.code for issue in result.issues}
        self.assertIn("orphan_requirement", codes)
        self.assertIn("stage_without_evidence", codes)
        self.assertIn("missing_unsupported_path_handling", codes)
        self.assertIn("file_rule_without_citation", codes)
        self.assertIn("document_rule_without_citation", codes)
        self.assertIn("consequential_stage_without_action_gate", codes)
        self.assertIn("stale_source_evidence", codes)
        self.assertIn("guardrail_bundle_without_compiled_predicates", codes)

    def test_assert_helper_raises_compact_error(self) -> None:
        packet = self._valid_packet()
        packet["process_model"]["stages"][1].pop("action_gate_id")

        with self.assertRaises(ValueError) as raised:
            assert_valid_process_model_assembly_packet(packet, now=date(2026, 5, 28))

        self.assertIn("consequential_stage_without_action_gate", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
