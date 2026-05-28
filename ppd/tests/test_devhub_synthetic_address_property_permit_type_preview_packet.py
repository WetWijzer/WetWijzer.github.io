from __future__ import annotations

import json
import re
import unittest
from pathlib import Path
from typing import Any


FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "devhub"
    / "synthetic_address_property_permit_type_preview_packet.json"
)

REQUIRED_LABELS = {
    "Address or property search",
    "Search",
    "Property search results",
    "Synthetic property match",
    "Permit request type",
    "Building permit request",
    "Continue",
}

PROHIBITED_ARTIFACT_KEYS = {
    "auth_state",
    "browser_context",
    "cookie",
    "cookies",
    "credential",
    "credentials",
    "download_path",
    "har",
    "password",
    "screenshot",
    "session_id",
    "storage_state",
    "trace",
    "video",
}

PRIVATE_VALUE_PATTERNS = (
    re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE),
    re.compile(r"\b(?:\+?1[-. ]?)?\(?\d{3}\)?[-. ]?\d{3}[-. ]?\d{4}\b"),
    re.compile(r"\b\d{1,6}\s+[A-Z][A-Za-z0-9.'-]*(?:\s+[A-Z][A-Za-z0-9.'-]*)?\s+(?:St|Street|Ave|Avenue|Rd|Road|Blvd|Drive|Dr|Court|Ct|Way)\b"),
    re.compile(r"(?:^|[\s:])/(?:home|Users|tmp|private|var/tmp)/"),
    re.compile(r"\b(?:visa|mastercard|amex|cvv|routing number|account number)\b", re.IGNORECASE),
)


def load_packet() -> dict[str, Any]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def walk(value: Any, path: str = "packet"):
    yield path, value
    if isinstance(value, dict):
        for key, child in value.items():
            yield from walk(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk(child, f"{path}[{index}]")


class DevHubSyntheticAddressPropertyPermitTypePreviewPacketTests(unittest.TestCase):
    def test_fixture_first_packet_covers_requested_preview_flow(self) -> None:
        packet = load_packet()

        self.assertEqual(packet["packet_type"], "devhub_reversible_draft_preview_packet")
        self.assertTrue(packet["fixture_first"])
        self.assertTrue(packet["synthetic_only"])
        self.assertFalse(packet["live_devhub_session"])
        self.assertFalse(packet["browser_launched"])

        step_kinds = {step["step_kind"] for step in packet["preview_steps"]}
        self.assertEqual(
            step_kinds,
            {"address_property_search_preview", "permit_type_selection_preview"},
        )

    def test_uses_only_mocked_roles_stable_labels_and_confidence(self) -> None:
        packet = load_packet()
        labels: set[str] = set()

        selector_confidence = packet["selector_confidence"]
        self.assertEqual(selector_confidence["strategy"], "accessible_role_and_stable_label")
        self.assertFalse(selector_confidence["uses_css_or_xpath_selectors"])
        self.assertFalse(selector_confidence["uses_pixel_coordinates"])

        for step in packet["preview_steps"]:
            self.assertTrue(step["requires_user_attendance"])
            self.assertTrue(step["reversible"])
            self.assertFalse(step["changes_official_record"])
            for control in step["mocked_accessible_controls"]:
                self.assertIn(control["role"], {"textbox", "button", "listbox", "option", "combobox"})
                self.assertTrue(control["label"])
                self.assertIn(control["selector_confidence"], {"stable_label_required", "mocked_label_only"})
                labels.add(control["label"])

        self.assertTrue(REQUIRED_LABELS.issubset(labels))

    def test_attendance_requirements_and_blocked_actions_are_explicit(self) -> None:
        packet = load_packet()
        attendance = packet["attendance_requirements"]

        self.assertTrue(attendance["requires_user_attendance"])
        self.assertTrue(attendance["user_controls_account_entry"])
        self.assertFalse(attendance["automation_may_enter_account_secrets"])
        self.assertFalse(attendance["automation_may_complete_security_challenges"])
        self.assertTrue(attendance["preview_may_run_without_live_site"])

        blocked = {action["action_class"]: action for action in packet["blocked_actions"]}
        for action_class in {
            "account_secret_entry",
            "security_challenge",
            "document_upload",
            "fee_payment",
            "inspection_scheduling",
            "certification",
            "submission",
        }:
            self.assertIn(action_class, blocked)
            self.assertFalse(blocked[action_class]["may_execute"])

    def test_no_authenticated_artifacts_or_private_values_are_committed(self) -> None:
        packet = load_packet()
        safety = packet["commit_safety"]

        self.assertEqual(safety["classification"], "commit_safe_mocked_metadata_only")
        for key, value in safety.items():
            if key.endswith("_committed"):
                self.assertFalse(value, key)

        for path, value in walk(packet):
            key = path.rsplit(".", 1)[-1].lower()
            self.assertNotIn(key, PROHIBITED_ARTIFACT_KEYS, path)
            if isinstance(value, str):
                for pattern in PRIVATE_VALUE_PATTERNS:
                    self.assertIsNone(pattern.search(value), f"{path}: {value}")

    def test_all_references_resolve_inside_packet(self) -> None:
        packet = load_packet()
        evidence_ids = {evidence["evidence_id"] for evidence in packet["source_evidence"]}
        fact_ids = {fact["fact_id"] for fact in packet["scenario"]["input_values"]}

        for step in packet["preview_steps"]:
            self.assertTrue(set(step["source_evidence_ids"]).issubset(evidence_ids))
            self.assertTrue(set(step["uses_fact_ids"]).issubset(fact_ids))
            preview = step["draft_preview"]
            self.assertTrue(preview["contains_only_synthetic_values"])
            self.assertFalse(preview["contains_raw_page_body"])
            self.assertFalse(preview["contains_browser_artifact"])


if __name__ == "__main__":
    unittest.main()
