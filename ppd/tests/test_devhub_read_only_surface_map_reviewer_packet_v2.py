from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from ppd.agent_readiness.devhub_read_only_surface_map_reviewer_packet_v2 import (
    validate_devhub_read_only_surface_map_reviewer_packet_v2,
)

_FIXTURE = Path(__file__).parent / "fixtures" / "devhub_read_only_surface_map_reviewer_packet_v2_valid.json"


def _valid_packet() -> dict:
    return json.loads(_FIXTURE.read_text(encoding="utf-8"))


def _codes(packet: dict) -> set[str]:
    return {issue.code for issue in validate_devhub_read_only_surface_map_reviewer_packet_v2(packet)}


class DevHubReadOnlySurfaceMapReviewerPacketV2Tests(unittest.TestCase):
    def test_valid_fixture_has_no_issues(self) -> None:
        self.assertEqual(validate_devhub_read_only_surface_map_reviewer_packet_v2(_valid_packet()), [])

    def test_rejects_unreviewed_candidate_row(self) -> None:
        packet = _valid_packet()
        packet["candidate_rows"][0]["review_status"] = "unreviewed"
        self.assertIn("unreviewed_candidate_row", _codes(packet))

    def test_rejects_missing_observation_to_candidate_trace(self) -> None:
        packet = _valid_packet()
        packet["candidate_rows"][0]["observation_trace_ids"] = []
        self.assertIn("missing_observation_to_candidate_trace", _codes(packet))

    def test_rejects_missing_redaction_selector_and_blocked_refs(self) -> None:
        packet = _valid_packet()
        row = packet["candidate_rows"][0]
        row.pop("redaction_acceptance_ref")
        row["unresolved_selector_risk_note_ids"] = []
        row["blocked_action_confirmation_ids"] = []
        codes = _codes(packet)
        self.assertIn("missing_redaction_acceptance_ref", codes)
        self.assertIn("missing_unresolved_selector_risk_note", codes)
        self.assertIn("missing_blocked_action_confirmation", codes)

    def test_rejects_missing_validation_commands(self) -> None:
        packet = _valid_packet()
        packet["validation_commands"] = []
        self.assertIn("missing_validation_commands", _codes(packet))

    def test_rejects_private_browser_raw_and_downloaded_artifacts(self) -> None:
        packet = _valid_packet()
        packet["candidate_rows"][0]["review_rationale"] = "Includes browser state, screenshot, raw crawl, and downloaded PDF."
        codes = _codes(packet)
        self.assertIn("private_or_session_artifact_language", codes)
        self.assertIn("browser_raw_or_downloaded_artifact_language", codes)

    def test_rejects_live_devhub_and_automated_login_or_mfa_claims(self) -> None:
        packet = _valid_packet()
        packet["candidate_rows"][0]["review_rationale"] = "Ran against live DevHub after automated login and automated MFA."
        codes = _codes(packet)
        self.assertIn("live_devhub_claim", codes)
        self.assertIn("automated_login_or_mfa_claim", codes)

    def test_rejects_consequential_action_and_guarantee_language(self) -> None:
        packet = _valid_packet()
        packet["candidate_rows"][0]["review_rationale"] = "Submit permit and guarantee approval."
        codes = _codes(packet)
        self.assertIn("consequential_official_action_language", codes)
        self.assertIn("legal_or_permitting_guarantee", codes)

    def test_rejects_active_mutation_flags(self) -> None:
        base_packet = _valid_packet()
        for key in (
            "active_surface_map_mutation",
            "active_guardrail_mutation",
            "active_prompt_mutation",
            "active_source_mutation",
            "active_contract_mutation",
            "active_release_state_mutation",
        ):
            packet = copy.deepcopy(base_packet)
            packet["mutation_flags"][key] = True
            self.assertIn("active_mutation_flag", _codes(packet), key)


if __name__ == "__main__":
    unittest.main()
