from __future__ import annotations

import unittest

from ppd.devhub.surface_state_packet_validation import (
    assert_valid_surface_state_packet,
    validate_surface_state_packet,
)


def safe_packet() -> dict[str, object]:
    return {
        "surface_id": "devhub-permit-dashboard",
        "auth_scope": "authenticated_attended",
        "url_pattern": "https://devhub.portlandoregon.gov/permit/*",
        "page_heading": "Permits",
        "redaction_policy": {
            "private_values": "redact",
            "browser_state": "reject",
            "raw_text": "reject",
        },
        "selector_confidence": 0.91,
        "fields": [
            {
                "name": "permit_number",
                "label": "Permit number",
                "value": "[redacted]",
                "selector": "[data-testid='permit-number']",
                "selector_confidence": 0.88,
            }
        ],
        "actions": [
            {
                "name": "review_status",
                "kind": "read_only",
                "requires_attendance": True,
                "requires_exact_confirmation": False,
                "automation_notes": "Observed only; no consequential DevHub action was performed.",
            }
        ],
    }


class DevHubSurfaceStatePacketValidationTest(unittest.TestCase):
    def test_accepts_redacted_surface_metadata(self) -> None:
        result = validate_surface_state_packet(safe_packet())
        self.assertTrue(result.accepted, result.errors)
        assert_valid_surface_state_packet(safe_packet())

    def test_rejects_browser_state_and_cookies(self) -> None:
        packet = safe_packet()
        packet["browser_state"] = {"origins": []}
        packet["cookies"] = [{"name": "session", "value": "secret"}]

        result = validate_surface_state_packet(packet)

        self.assertFalse(result.accepted)
        self.assertTrue(any("browser_state" in error for error in result.errors))
        self.assertTrue(any("cookies" in error for error in result.errors))

    def test_rejects_credentials_screenshots_traces_and_har(self) -> None:
        for key in ("credentials", "screenshot", "trace", "har"):
            packet = safe_packet()
            packet[key] = "present"

            result = validate_surface_state_packet(packet)

            self.assertFalse(result.accepted, key)
            self.assertTrue(any(key in error for error in result.errors), result.errors)

    def test_rejects_private_field_values(self) -> None:
        packet = safe_packet()
        packet["fields"] = [{"name": "owner_email", "value": "owner@example.test"}]

        result = validate_surface_state_packet(packet)

        self.assertFalse(result.accepted)
        self.assertTrue(any("private field" in error for error in result.errors))

    def test_rejects_raw_authenticated_text_dumps(self) -> None:
        packet = safe_packet()
        packet["raw_authenticated_text"] = "Full authenticated page text should never be committed."

        result = validate_surface_state_packet(packet)

        self.assertFalse(result.accepted)
        self.assertTrue(any("raw authenticated text" in error for error in result.errors))

    def test_rejects_missing_redaction_policy(self) -> None:
        packet = safe_packet()
        del packet["redaction_policy"]

        result = validate_surface_state_packet(packet)

        self.assertFalse(result.accepted)
        self.assertTrue(any("redaction_policy" in error for error in result.errors))

    def test_rejects_low_confidence_selectors(self) -> None:
        packet = safe_packet()
        packet["selector_confidence"] = 0.5

        result = validate_surface_state_packet(packet)

        self.assertFalse(result.accepted)
        self.assertTrue(any("selector_confidence" in error for error in result.errors))

    def test_rejects_unactionable_url_patterns(self) -> None:
        for pattern in ("*", "http://devhub.portlandoregon.gov/*", "https://example.test/*"):
            packet = safe_packet()
            packet["url_pattern"] = pattern

            result = validate_surface_state_packet(packet)

            self.assertFalse(result.accepted, pattern)
            self.assertTrue(any("url_pattern" in error for error in result.errors), result.errors)

    def test_rejects_forbidden_automation_claims(self) -> None:
        forbidden_claims = (
            "login was automated",
            "MFA completed by agent",
            "captcha solved without user",
            "upload clicked by agent",
            "submit executed by agent",
            "payment was automated",
            "cancellation performed by agent",
            "scheduling completed by agent",
        )
        for claim in forbidden_claims:
            packet = safe_packet()
            packet["actions"] = [{"automation_notes": claim}]

            result = validate_surface_state_packet(packet)

            self.assertFalse(result.accepted, claim)
            self.assertTrue(any("prohibited DevHub action" in error for error in result.errors), result.errors)


if __name__ == "__main__":
    unittest.main()
