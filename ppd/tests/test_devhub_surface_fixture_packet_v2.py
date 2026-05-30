import json
import unittest
from pathlib import Path

from ppd.devhub_surface_fixture_packet_v2 import validate_packet

_FIXTURES = Path(__file__).parent / "fixtures" / "devhub"


class DevHubSurfaceFixturePacketV2Tests(unittest.TestCase):
    def _load(self, name):
        with (_FIXTURES / name).open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def test_valid_inactive_packet_passes(self):
        packet = self._load("devhub_surface_packet_v2_valid_inactive.json")
        self.assertEqual([], validate_packet(packet))

    def test_invalid_packet_reports_required_rejections(self):
        packet = self._load("devhub_surface_packet_v2_invalid_unsafe.json")
        errors = validate_packet(packet)
        joined = "\n".join(errors)

        expected_fragments = [
            "missing a citation",
            "selector-confidence before/after",
            "manual-handoff or redaction",
            "private or authenticated",
            "credential, session, or auth artifact",
            "screenshots, traces, HAR",
            "browser automation or live DevHub completion",
            "outcome guarantee",
            "consequential permitting action",
            "enables active registry",
        ]
        for fragment in expected_fragments:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, joined)

    def test_active_packet_is_rejected(self):
        packet = self._load("devhub_surface_packet_v2_valid_inactive.json")
        packet["status"] = "active"
        self.assertIn("packet status must be inactive", validate_packet(packet))


if __name__ == "__main__":
    unittest.main()
