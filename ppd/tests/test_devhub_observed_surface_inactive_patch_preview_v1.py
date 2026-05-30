from __future__ import annotations

import json
import unittest
from pathlib import Path

from ppd.devhub_observed_surface_inactive_patch_preview_v1 import (
    assert_valid_devhub_observed_surface_inactive_patch_preview_v1,
    validate_devhub_observed_surface_inactive_patch_preview_v1,
)

_FIXTURE_DIR = Path(__file__).parent / "fixtures" / "devhub_observed_surface_inactive_patch_preview_v1"


def _valid_packet() -> dict[str, object]:
    with (_FIXTURE_DIR / "valid_preview.json").open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise AssertionError("valid preview fixture must be a JSON object")
    return data


class DevHubObservedSurfaceInactivePatchPreviewV1Tests(unittest.TestCase):
    def test_valid_fixture_has_no_findings(self) -> None:
        packet = _valid_packet()
        self.assertEqual(validate_devhub_observed_surface_inactive_patch_preview_v1(packet), [])
        assert_valid_devhub_observed_surface_inactive_patch_preview_v1(packet)

    def test_rejects_missing_required_preview_sections(self) -> None:
        packet = _valid_packet()
        packet.pop("inactive_surface_map_delta_previews")
        packet["selector_confidence_placeholders"] = []
        packet.pop("validation_commands")

        codes = {finding.code for finding in validate_devhub_observed_surface_inactive_patch_preview_v1(packet)}

        self.assertIn("missing_inactive_surface_map_delta_previews", codes)
        self.assertIn("missing_selector_confidence_placeholders", codes)
        self.assertIn("missing_validation_commands", codes)

    def test_rejects_unapproved_disposition_rows(self) -> None:
        packet = _valid_packet()
        packet["disposition_rows"] = [
            {
                "surface_id": "devhub-home-inactive-readonly-v1",
                "disposition": "pending",
                "reviewer": "fixture-reviewer",
                "evidence_ref": "fixture:reviewer-disposition:devhub-home-inactive-readonly-v1",
            }
        ]

        codes = {finding.code for finding in validate_devhub_observed_surface_inactive_patch_preview_v1(packet)}

        self.assertIn("unapproved_disposition_row", codes)

    def test_rejects_missing_surface_specific_placeholders(self) -> None:
        packet = _valid_packet()
        packet["accessible_role_name_evidence_placeholders"] = [
            {
                "surface_id": "devhub-home-inactive-readonly-v1",
                "evidence_ref": "fixture:accessible-role-name:devhub-home-inactive-readonly-v1",
            }
        ]
        packet["redacted_field_inventory_placeholders"] = [
            {
                "surface_id": "devhub-home-inactive-readonly-v1",
                "evidence_ref": "fixture:redacted-field-inventory:devhub-home-inactive-readonly-v1",
            }
        ]
        packet["action_classification_references"] = [
            {
                "surface_id": "devhub-home-inactive-readonly-v1",
                "evidence_ref": "fixture:action-classification:devhub-home-inactive-readonly-v1",
            }
        ]
        packet["reviewer_signoff_placeholders"] = [
            {
                "surface_id": "devhub-home-inactive-readonly-v1",
                "evidence_ref": "fixture:reviewer-signoff:devhub-home-inactive-readonly-v1",
            }
        ]

        codes = {finding.code for finding in validate_devhub_observed_surface_inactive_patch_preview_v1(packet)}

        self.assertIn("missing_accessible_role_name_evidence_placeholder", codes)
        self.assertIn("missing_redacted_field_inventory_placeholder", codes)
        self.assertIn("missing_action_classification_reference", codes)
        self.assertIn("missing_reviewer_signoff_placeholder", codes)

    def test_rejects_private_artifacts_live_claims_consequential_language_and_mutation_flags(self) -> None:
        packet = _valid_packet()
        packet["browser_artifact"] = "screenshot path from browser profile"
        packet["private_page_value"] = "private page value from an account page"
        packet["operator_note"] = "observed in live DevHub; submit application next"
        packet["active_surface_mutation"] = True
        packet["guardrail_mutation"] = True
        packet["prompt_mutation"] = True
        packet["release_state_mutation"] = True
        packet["mutation_flags"] = ["inactive_preview_only", "promote_active_surface"]

        codes = {finding.code for finding in validate_devhub_observed_surface_inactive_patch_preview_v1(packet)}

        self.assertIn("credential_session_auth_or_browser_artifact_key", codes)
        self.assertIn("credential_session_auth_or_browser_artifact_text", codes)
        self.assertIn("private_page_value_key", codes)
        self.assertIn("private_page_value_text", codes)
        self.assertIn("live_devhub_access_claim", codes)
        self.assertIn("consequential_official_action_language", codes)
        self.assertIn("active_mutation_flag_enabled", codes)
        self.assertIn("mutation_flag_outside_inactive_preview_scope", codes)


if __name__ == "__main__":
    unittest.main()
