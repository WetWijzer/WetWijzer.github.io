import json
import unittest
from pathlib import Path
from typing import Any


FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "devhub_recorder"
    / "synthetic_authenticated_surface_state_packet.json"
)

FORBIDDEN_TOP_LEVEL_KEYS = {
    "auth_state",
    "storage_state",
    "browser_state",
    "cookies",
    "local_storage",
    "session_storage",
    "screenshot",
    "screenshots",
    "trace",
    "traces",
    "har",
    "credentials",
    "password",
    "token",
    "raw_crawl_output",
    "downloaded_documents",
}

FORBIDDEN_VALUE_KEYS = {
    "value",
    "raw_value",
    "current_value",
    "input_value",
    "private_value",
    "file_path",
    "local_path",
}

REQUIRED_SURFACE_KEYS = {
    "page_title",
    "url_pattern",
    "page_heading",
    "accessible_roles",
    "stable_labels",
    "validation_messages",
    "dropdown_options",
    "conditional_question_triggers",
    "upload_controls",
    "timeout_and_save_text",
    "official_action_button_labels",
}


def _load_fixture() -> dict[str, Any]:
    with FIXTURE_PATH.open(encoding="utf-8") as fixture_file:
        data = json.load(fixture_file)
    if not isinstance(data, dict):
        raise AssertionError("surface-state packet fixture must be a JSON object")
    return data


def _walk_keys(value: Any) -> list[str]:
    keys: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            keys.append(key)
            keys.extend(_walk_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.extend(_walk_keys(child))
    return keys


class DevHubRecorderSurfaceStatePacketTest(unittest.TestCase):
    def test_fixture_is_metadata_only_and_synthetic(self) -> None:
        packet = _load_fixture()

        self.assertEqual(packet["fixture_schema"], "ppd.devhub.recorder.surface_state_packet.v1")
        self.assertEqual(packet["capture_mode"], "fixture_first_metadata_only")
        self.assertEqual(packet["source"]["captured_from"], "synthetic-fixture")
        self.assertFalse(packet["source"]["live_browser_used"])
        self.assertFalse(packet["source"]["playwright_launched"])
        self.assertFalse(packet["source"]["authenticated_session_material_saved"])
        self.assertEqual(packet["source"]["artifacts_saved"], [])

        contract = packet["recorder_contract"]
        for key, included in contract.items():
            self.assertIs(included, False, key)

    def test_surface_packet_covers_required_recorder_state_fields(self) -> None:
        packet = _load_fixture()
        surface = packet["surface"]

        self.assertGreaterEqual(set(surface), REQUIRED_SURFACE_KEYS)
        self.assertEqual(surface["auth_scope"], "authenticated_attended")
        self.assertIn("{redacted_application_id}", surface["url_pattern"])
        self.assertTrue(surface["page_title"].strip())
        self.assertTrue(surface["page_heading"].strip())

    def test_accessible_roles_stable_labels_and_required_markers_are_present(self) -> None:
        surface = _load_fixture()["surface"]

        roles = {(item["role"], item["name"]) for item in surface["accessible_roles"]}
        self.assertIn(("main", "Review permit application"), roles)
        self.assertIn(("combobox", "Permit request type"), roles)
        self.assertIn(("button", "Submit request"), roles)

        required_labels = [label for label in surface["stable_labels"] if label["required"]]
        self.assertGreaterEqual(len(required_labels), 3)
        for label in surface["stable_labels"]:
            self.assertTrue(label["label_text"].strip())
            self.assertTrue(label["selector_basis"].strip())
            self.assertIn("role", label["selector_basis"])
            if label["required"]:
                self.assertTrue(label["required_marker"].strip())

    def test_validation_dropdown_conditional_upload_and_save_text_are_recorded(self) -> None:
        surface = _load_fixture()["surface"]

        validation_ids = {message["message_id"] for message in surface["validation_messages"]}
        self.assertGreaterEqual(
            validation_ids,
            {
                "project_description_required",
                "permit_request_type_required",
                "plan_pdf_required",
                "acknowledgement_required",
            },
        )
        for message in surface["validation_messages"]:
            self.assertEqual(message["severity"], "blocking")
            self.assertTrue(message["linked_label_id"].strip())
            self.assertNotIn("[PRIVATE", message["text"])

        dropdowns = {dropdown["field_id"]: dropdown for dropdown in surface["dropdown_options"]}
        self.assertIn("permit_request_type", dropdowns)
        self.assertIn("Building Permit", dropdowns["permit_request_type"]["options"])
        self.assertEqual(dropdowns["permit_request_type"]["selected_option"], "[REDACTED]")

        triggers = {trigger["trigger_id"]: trigger for trigger in surface["conditional_question_triggers"]}
        self.assertIn("exterior_work_yes", triggers)
        self.assertIn("plan_review_request_type", triggers)
        self.assertTrue(triggers["plan_review_request_type"]["reveals_labels"])

        for control in surface["upload_controls"]:
            self.assertIn("application/pdf", control["accepted_file_types"])
            self.assertFalse(control["stores_file_path"])
            self.assertEqual(control["sample_file_name"], "[REDACTED]")
            self.assertTrue(control["hint_text"].strip())

        timeout = surface["timeout_and_save_text"]
        self.assertEqual(timeout["save_for_later_button_label"], "Save for later")
        self.assertIn("Save for later", timeout["timeout_warning"])
        self.assertTrue(timeout["resume_link_label"].strip())

    def test_official_actions_are_labels_only_and_confirmation_gated(self) -> None:
        actions = _load_fixture()["surface"]["official_action_button_labels"]
        labels = {action["label"] for action in actions}

        self.assertGreaterEqual(
            labels,
            {
                "Submit request",
                "I certify the information is accurate",
                "Upload documents",
            },
        )
        for action in actions:
            self.assertIn(
                action["action_class"],
                {"consequential_official", "certification_gate", "official_record_upload"},
            )
            self.assertIs(action["requires_attendance"], True)
            self.assertIs(action["requires_exact_confirmation"], True)
            self.assertNotIn("selector", action)
            self.assertNotIn("execute", action)

    def test_packet_omits_private_browser_state_artifacts_and_values(self) -> None:
        packet = _load_fixture()
        keys = set(_walk_keys(packet))

        self.assertTrue(keys.isdisjoint(FORBIDDEN_TOP_LEVEL_KEYS))
        self.assertTrue(keys.isdisjoint(FORBIDDEN_VALUE_KEYS))
        self.assertNotIn("raw_crawl_output", packet)
        self.assertNotIn("downloaded_documents", packet)

        privacy = packet["privacy"]
        self.assertEqual(privacy["classification"], "authenticated_redacted_metadata_only")
        self.assertFalse(privacy["private_values_persisted"])


if __name__ == "__main__":
    unittest.main()
