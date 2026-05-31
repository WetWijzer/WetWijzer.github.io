from __future__ import annotations

import json
import unittest
from pathlib import Path

from ppd.agent_api_smoke_rehearsal_packet_v1 import (
    assert_agent_api_smoke_rehearsal_packet_v1,
    validate_agent_api_smoke_rehearsal_packet_v1,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "agent_api_smoke_rehearsal_packet_v1"


class AgentApiSmokeRehearsalPacketV1Tests(unittest.TestCase):
    def load_packet(self, name: str) -> dict:
        return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))

    def test_valid_packet_passes(self) -> None:
        packet = self.load_packet("valid_packet.json")

        result = validate_agent_api_smoke_rehearsal_packet_v1(packet)

        self.assertTrue(result.valid, result.errors)
        assert_agent_api_smoke_rehearsal_packet_v1(packet)

    def test_invalid_packet_reports_required_coverage_and_safety_errors(self) -> None:
        packet = self.load_packet("invalid_packet.json")

        result = validate_agent_api_smoke_rehearsal_packet_v1(packet)

        self.assertFalse(result.valid)
        joined = "\n".join(result.errors)
        self.assertIn("scenario coverage", joined)
        self.assertIn("expected response rows", joined)
        self.assertIn("citation references", joined)
        self.assertIn("stale-source holds", joined)
        self.assertIn("exact-confirmation gates", joined)
        self.assertIn("refusal rows", joined)
        self.assertIn("validation commands", joined)
        self.assertIn("private/session/browser/raw/downloaded artifact", joined)
        self.assertIn("official-action completion claim", joined)
        self.assertIn("live crawl or DevHub claim", joined)
        self.assertIn("legal or permitting guarantee", joined)
        self.assertIn("active mutation flag", joined)

    def test_expected_response_rows_must_reference_known_citations(self) -> None:
        packet = self.load_packet("valid_packet.json")
        packet["expected_response_rows"][0]["citations"] = ["missing-reference"]

        result = validate_agent_api_smoke_rehearsal_packet_v1(packet)

        self.assertFalse(result.valid)
        self.assertIn("unknown reference", "\n".join(result.errors))

    def test_citation_references_must_use_official_ppd_urls(self) -> None:
        packet = self.load_packet("valid_packet.json")
        packet["citation_references"]["ppd-online-tools"]["url"] = "https://example.com/not-official"

        result = validate_agent_api_smoke_rehearsal_packet_v1(packet)

        self.assertFalse(result.valid)
        self.assertIn("official PP&D https URL", "\n".join(result.errors))


if __name__ == "__main__":
    unittest.main()
