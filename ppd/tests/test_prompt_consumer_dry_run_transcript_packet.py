from __future__ import annotations

import json
import unittest
from pathlib import Path

from ppd.prompt_consumer_dry_run_transcript_packet import (
    REQUIRED_RESPONSE_IDS,
    build_prompt_consumer_dry_run_transcript_packet,
    validate_prompt_consumer_dry_run_transcript_packet,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "prompt_consumer_dry_run"


class PromptConsumerDryRunTranscriptPacketTest(unittest.TestCase):
    def test_builds_expected_transcript_from_fixture_packets(self) -> None:
        release = _load_json("prompt_refresh_release_handoff_packet.json")
        gap = _load_json("user_gap_analysis_fixture.json")
        guarded = _load_json("guarded_action_fixture.json")
        drafts = _load_json("reversible_draft_preview_fixture.json")
        expected = _load_json("expected_prompt_consumer_dry_run_transcript_packet.json")

        actual = build_prompt_consumer_dry_run_transcript_packet(
            release,
            gap,
            guarded,
            drafts,
        )

        self.assertEqual(actual, expected)
        self.assertEqual(validate_prompt_consumer_dry_run_transcript_packet(actual), [])

    def test_transcript_covers_required_prompt_consumer_behaviors(self) -> None:
        packet = _load_json("expected_prompt_consumer_dry_run_transcript_packet.json")
        responses = packet["expected_agent_responses"]
        by_id = {response["response_id"]: response for response in responses}

        self.assertEqual(tuple(by_id), REQUIRED_RESPONSE_IDS)
        self.assertIn("missing information", by_id["missing_information_prompt"]["expected_agent_response"])
        self.assertIn("read-only", by_id["safe_read_only_summary"]["expected_agent_response"])
        self.assertIn("not an upload", by_id["draft_preview_boundaries"]["expected_agent_response"])
        self.assertIn("cannot perform", by_id["refusal_explanation"]["expected_agent_response"])
        self.assertIn("exact-confirmation checkpoint", by_id["exact_confirmation_checkpoint"]["expected_agent_response"])
        self.assertIn("python3 -m py_compile", by_id["offline_validation_commands"]["expected_agent_response"])
        self.assertIn("no live LLM call", by_id["side_effect_attestations"]["expected_agent_response"])

    def test_attestations_remain_side_effect_free(self) -> None:
        packet = _load_json("expected_prompt_consumer_dry_run_transcript_packet.json")

        self.assertEqual(
            packet["side_effects"],
            {
                "live_llm_used": False,
                "devhub_accessed": False,
                "private_documents_loaded": False,
                "system_prompt_disclosed": False,
                "agent_state_mutated": False,
            },
        )
        for response in packet["expected_agent_responses"]:
            self.assertTrue(response["citations"])
            self.assertTrue(all("#" in citation for citation in response["citations"]))

    def test_validator_rejects_mutating_or_live_packet_claims(self) -> None:
        packet = _load_json("expected_prompt_consumer_dry_run_transcript_packet.json")
        packet["side_effects"]["devhub_accessed"] = True

        errors = validate_prompt_consumer_dry_run_transcript_packet(packet)

        self.assertIn("devhub_accessed must be false", errors)


def _load_json(name: str) -> dict:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
