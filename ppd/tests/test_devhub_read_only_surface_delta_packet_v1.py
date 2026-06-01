from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from ppd.devhub.read_only_surface_delta_packet_v1 import (
    validate_devhub_read_only_surface_delta_packet_v1,
)

_FIXTURE = Path(__file__).parent / "fixtures" / "devhub_read_only_surface_delta_packet_v1" / "valid_packet.json"


def _valid_packet() -> dict:
    return json.loads(_FIXTURE.read_text(encoding="utf-8"))


def _codes(packet: dict) -> set[str]:
    return {issue.code for issue in validate_devhub_read_only_surface_delta_packet_v1(packet)}


class DevHubReadOnlySurfaceDeltaPacketV1Tests(unittest.TestCase):
    def test_valid_fixture_has_no_issues(self) -> None:
        self.assertEqual(validate_devhub_read_only_surface_delta_packet_v1(_valid_packet()), [])

    def test_rejects_missing_required_packet_sections(self) -> None:
        required = {
            "observation_evidence_refs": "missing_observation_evidence_refs",
            "candidate_surface_map_change_rows": "missing_candidate_surface_map_change_rows",
            "selector_confidence_notes": "missing_selector_confidence_notes",
            "action_classification_checks": "missing_action_classification_checks",
            "redaction_policy_impacts": "missing_redaction_policy_impacts",
            "attendance_or_exact_confirmation_requirements": "missing_attendance_or_exact_confirmation_requirements",
            "unsupported_or_manual_handoff_paths": "missing_unsupported_or_manual_handoff_paths",
            "reviewer_holds": "missing_reviewer_holds",
            "validation_commands": "missing_validation_commands",
        }
        for key, expected in required.items():
            with self.subTest(key=key):
                packet = _valid_packet()
                packet[key] = []
                self.assertIn(expected, _codes(packet))

    def test_rejects_candidate_row_missing_required_references(self) -> None:
        packet = _valid_packet()
        row = packet["candidate_surface_map_change_rows"][0]
        row["observation_evidence_ref_ids"] = []
        row["selector_confidence_note_ids"] = []
        row["action_classification_check_ids"] = []
        row["redaction_policy_impact_ids"] = []
        row["attendance_or_exact_confirmation_requirement_ids"] = []
        row["unsupported_or_manual_handoff_path_ids"] = []
        row["reviewer_hold_ids"] = []

        codes = _codes(packet)

        self.assertIn("missing_observation_evidence_refs", codes)
        self.assertIn("missing_selector_confidence_notes", codes)
        self.assertIn("missing_action_classification_checks", codes)
        self.assertIn("missing_redaction_policy_impacts", codes)
        self.assertIn("missing_attendance_or_exact_confirmation_requirements", codes)
        self.assertIn("missing_unsupported_or_manual_handoff_paths", codes)
        self.assertIn("missing_reviewer_holds", codes)

    def test_rejects_action_redaction_attendance_handoff_and_hold_regressions(self) -> None:
        packet = _valid_packet()
        packet["action_classification_checks"][0]["classification"] = "reversible_draft"
        packet["action_classification_checks"][0]["consequential_action_blocked"] = False
        packet["redaction_policy_impacts"][0]["private_values_retained"] = True
        packet["attendance_or_exact_confirmation_requirements"][0]["requires_attendance"] = False
        packet["attendance_or_exact_confirmation_requirements"][0]["requires_exact_confirmation"] = False
        packet["unsupported_or_manual_handoff_paths"][0]["disposition"] = "automated"
        packet["reviewer_holds"][0]["hold_active"] = False

        codes = _codes(packet)

        self.assertIn("action_classification_not_read_only", codes)
        self.assertIn("consequential_action_not_blocked", codes)
        self.assertIn("redaction_policy_retains_private_values", codes)
        self.assertIn("missing_attendance_or_exact_confirmation_requirement", codes)
        self.assertIn("missing_unsupported_or_manual_handoff_path", codes)
        self.assertIn("reviewer_hold_not_active", codes)

    def test_rejects_credentials_session_browser_screenshot_trace_har_private_and_raw_artifacts(self) -> None:
        packet = _valid_packet()
        packet["reviewer_holds"][0]["note"] = "Includes credentials, session state, browser state, screenshot, trace.zip, HAR file, private artifact, and raw crawl output."

        codes = _codes(packet)

        self.assertIn("private_or_session_artifact_language", codes)
        self.assertIn("browser_screenshot_trace_har_or_raw_artifact_language", codes)

    def test_rejects_live_devhub_crawl_official_consequential_and_promotion_claims(self) -> None:
        packet = _valid_packet()
        packet["action_classification_checks"][0]["note"] = "Ran against live DevHub during a live crawl, submitted successfully, submit permit next, and promotion complete."

        codes = _codes(packet)

        self.assertIn("live_devhub_or_crawl_claim", codes)
        self.assertIn("official_action_completion_claim", codes)
        self.assertIn("consequential_action_claim", codes)
        self.assertIn("promotion_claim", codes)

    def test_rejects_artifact_policy_and_active_mutation_flags(self) -> None:
        base = _valid_packet()
        packet = copy.deepcopy(base)
        packet["artifact_policy"]["captures_session_state"] = True
        self.assertIn("artifact_policy_not_false", _codes(packet))

        for key in (
            "active_registry_mutation",
            "active_surface_map_mutation",
            "active_devhub_surface_mutation",
            "surface_map_mutation_enabled",
            "devhub_surface_mutation_enabled",
            "registry_mutation_enabled",
        ):
            with self.subTest(key=key):
                packet = copy.deepcopy(base)
                packet["mutation_flags"][key] = True
                self.assertIn("active_mutation_flag", _codes(packet))

    def test_rejects_unexpected_validation_commands(self) -> None:
        packet = _valid_packet()
        packet["validation_commands"] = [["python3", "-m", "pytest"]]

        self.assertIn("unexpected_validation_commands", _codes(packet))


if __name__ == "__main__":
    unittest.main()
