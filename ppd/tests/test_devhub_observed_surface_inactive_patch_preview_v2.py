from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from ppd.agent_readiness.devhub_observed_surface_inactive_patch_preview_v2 import (
    assert_valid_inactive_patch_preview_v2,
    validate_inactive_patch_preview_v2,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "devhub_observed_surface_inactive_patch_preview_v2"


def load_valid_packet() -> dict:
    return json.loads((FIXTURE_DIR / "valid_packet.json").read_text(encoding="utf-8"))


class DevHubObservedSurfaceInactivePatchPreviewV2Test(unittest.TestCase):
    def violation_codes(self, packet: dict) -> set[str]:
        return {violation.code for violation in validate_inactive_patch_preview_v2(packet)}

    def test_valid_fixture_passes(self) -> None:
        assert_valid_inactive_patch_preview_v2(load_valid_packet())

    def test_rejects_missing_before_after_rows_and_uncited_evidence(self) -> None:
        packet = load_valid_packet()
        packet["rows"] = [{"row_id": "missing-fields"}]
        packet["observation_evidence"] = []

        codes = self.violation_codes(packet)

        self.assertIn("missing_before_after_rows", codes)
        self.assertIn("uncited_observation_evidence", codes)

    def test_rejects_missing_selector_notes_gates_blocked_rows_and_inventory(self) -> None:
        packet = load_valid_packet()
        packet.pop("selector_confidence_notes")
        packet.pop("gates")
        packet["blocked_rows"] = []
        packet["validation_inventory"] = []

        codes = self.violation_codes(packet)

        self.assertIn("missing_selector_confidence_notes", codes)
        self.assertIn("missing_redaction_gate", codes)
        self.assertIn("missing_attendance_gate", codes)
        self.assertIn("missing_blocked_row_explanations", codes)
        self.assertIn("missing_validation_inventory", codes)

    def test_rejects_private_session_browser_and_raw_download_artifacts(self) -> None:
        packet = load_valid_packet()
        packet["artifact_manifest"] = [
            {"kind": "playwright_trace", "path": "private_devhub_session/trace.zip"},
            {"kind": "raw_pdf", "path": "downloaded_data/application.pdf"},
        ]

        codes = self.violation_codes(packet)

        self.assertIn("private_or_session_artifact", codes)
        self.assertIn("raw_crawl_or_download_artifact", codes)

    def test_rejects_live_execution_promotion_guarantees_and_consequential_language(self) -> None:
        packet = load_valid_packet()
        packet["summary"] = (
            "Live DevHub execution completed and promoted to active. "
            "Permit will be approved after the agent can submit application."
        )

        codes = self.violation_codes(packet)

        self.assertIn("live_devhub_execution_or_promotion_claim", codes)
        self.assertIn("legal_or_permitting_outcome_guarantee", codes)
        self.assertIn("consequential_action_language", codes)

    def test_rejects_active_surface_process_guardrail_release_fixture_and_agent_mutations(self) -> None:
        base_packet = load_valid_packet()
        flag_names = tuple(base_packet["mutation_flags"].keys())

        for flag_name in flag_names:
            with self.subTest(flag_name=flag_name):
                packet = copy.deepcopy(base_packet)
                packet["mutation_flags"][flag_name] = True
                self.assertIn("active_mutation_flag", self.violation_codes(packet))

    def test_rejects_active_preview_metadata(self) -> None:
        packet = load_valid_packet()
        packet["surface_state"] = "active"
        packet["devhub_execution"] = "live"
        packet["promotion_claim"] = "released"

        codes = self.violation_codes(packet)

        self.assertIn("invalid_surface_state", codes)
        self.assertIn("invalid_devhub_execution", codes)
        self.assertIn("invalid_promotion_claim", codes)


if __name__ == "__main__":
    unittest.main()
