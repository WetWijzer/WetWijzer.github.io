from __future__ import annotations

import json
import unittest
from pathlib import Path

from ppd.crawler.public_recrawl_operator_packet_v2 import (
    assert_public_recrawl_operator_packet_v2_is_safe,
    issue_codes,
    validate_public_recrawl_operator_packet_v2,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "public_recrawl_operator_packet_v2"


def _load_fixture(name: str) -> dict:
    with (FIXTURE_DIR / name).open(encoding="utf-8") as handle:
        return json.load(handle)


class PublicRecrawlOperatorPacketV2Test(unittest.TestCase):
    def test_accepts_fixture_first_safe_packet(self) -> None:
        packet = _load_fixture("safe_packet.json")

        issues = validate_public_recrawl_operator_packet_v2(packet)

        self.assertEqual([], issues)
        assert_public_recrawl_operator_packet_v2_is_safe(packet)

    def test_rejects_unsafe_public_recrawl_packet_content(self) -> None:
        packet = _load_fixture("unsafe_packet.json")

        codes = issue_codes(validate_public_recrawl_operator_packet_v2(packet))

        self.assertIn("uncited_seed_batch", codes)
        self.assertIn("uncited_seed", codes)
        self.assertIn("missing_robots_or_skip_decision", codes)
        self.assertIn("outside_allowlist_url", codes)
        self.assertIn("authenticated_or_private_url", codes)
        self.assertIn("raw_body_download_or_archive_reference", codes)
        self.assertIn("live_crawl_or_processor_execution_claim", codes)
        self.assertIn("legal_or_permitting_outcome_guarantee", codes)
        self.assertIn("active_state_mutation_flag", codes)

    def test_rejects_direct_authenticated_urls_even_on_allowlisted_hosts(self) -> None:
        packet = _load_fixture("safe_packet.json")
        packet["seed_batches"][0]["seeds"][0]["url"] = "https://www.portland.gov/account?session=abc"

        codes = issue_codes(validate_public_recrawl_operator_packet_v2(packet))

        self.assertIn("authenticated_or_private_url", codes)

    def test_rejects_state_mutation_flags_by_domain(self) -> None:
        packet = _load_fixture("safe_packet.json")
        packet["operator_controls"]["mutate_guardrails"] = "enabled"

        codes = issue_codes(validate_public_recrawl_operator_packet_v2(packet))

        self.assertIn("active_state_mutation_flag", codes)


if __name__ == "__main__":
    unittest.main()
