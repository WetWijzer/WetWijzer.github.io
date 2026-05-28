from __future__ import annotations

import json
import unittest
from pathlib import Path

from ppd.devhub.guarded_action_preflight_packet import (
    REQUIRED_STOP_BEFORE_ACTIONS,
    require_valid_guarded_action_preflight_packet,
    validate_guarded_action_preflight_packet,
)


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "devhub" / "guarded_action_preflight_packet.json"


class GuardedActionPreflightPacketTests(unittest.TestCase):
    def load_fixture(self) -> dict[str, object]:
        with FIXTURE_PATH.open("r", encoding="utf-8") as handle:
            value = json.load(handle)
        self.assertIsInstance(value, dict)
        return value

    def test_fixture_links_draft_action_surface_evidence_and_stop_checkpoints(self) -> None:
        packet = self.load_fixture()

        result = require_valid_guarded_action_preflight_packet(packet)

        self.assertTrue(result.valid)
        self.assertEqual("synthetic-devhub-draft-fill-contact-phone", result.action_id)
        self.assertEqual("devhub_draft", result.surface_id)
        self.assertEqual("reversible_draft", result.action_kind)
        self.assertEqual("reversible_draft", result.action_class)
        self.assertGreaterEqual(result.selector_confidence, 0.85)
        self.assertTrue(REQUIRED_STOP_BEFORE_ACTIONS.issubset(set(result.stop_before_actions)))

    def test_missing_consequential_checkpoint_fails_closed(self) -> None:
        packet = self.load_fixture()
        checkpoints = list(packet["stop_before_consequential_checkpoints"])
        packet["stop_before_consequential_checkpoints"] = [
            checkpoint for checkpoint in checkpoints if checkpoint["action_kind"] != "submit_application"
        ]

        result = validate_guarded_action_preflight_packet(packet)

        self.assertFalse(result.valid)
        self.assertIn("missing stop-before checkpoints: submit_application", result.issues)

    def test_private_session_artifact_marker_is_rejected(self) -> None:
        packet = self.load_fixture()
        packet["preview_metadata"] = dict(packet["preview_metadata"], storage_state="forbidden marker")

        result = validate_guarded_action_preflight_packet(packet)

        self.assertFalse(result.valid)
        self.assertTrue(any("private or authenticated artifact" in issue for issue in result.issues))


if __name__ == "__main__":
    unittest.main()
