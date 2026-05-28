"""Fixture-backed tests for PP&D agent safe-action transcripts."""

from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from ppd.agent_safe_action_transcript import (
    build_safe_action_transcript,
    validate_safe_action_transcript,
)


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "agent_safe_action_transcript" / "synthetic_safe_action_case.json"


class AgentSafeActionTranscriptTests(unittest.TestCase):
    def setUp(self) -> None:
        with FIXTURE_PATH.open("r", encoding="utf-8") as fixture_file:
            self.case = json.load(fixture_file)

    def test_builds_required_cited_safe_action_sequence(self) -> None:
        transcript = build_safe_action_transcript(self.case)

        self.assertEqual(
            [message["message_type"] for message in transcript["messages"]],
            [
                "ask-user",
                "local-preview",
                "reversible-draft",
                "manual-handoff",
                "refused-action",
            ],
        )
        self.assertEqual((), validate_safe_action_transcript(transcript))

    def test_transcript_preserves_preflight_outcomes_and_citations(self) -> None:
        transcript = build_safe_action_transcript(self.case)
        outcomes = [message["preflight_outcome"] for message in transcript["messages"]]
        citation_sets = [message["citations"] for message in transcript["messages"]]

        self.assertEqual(
            outcomes,
            [
                "blocked",
                "local-preview",
                "reversible-draft",
                "manual-handoff",
                "refused",
            ],
        )
        self.assertTrue(all(citations for citations in citation_sets))
        self.assertIn("ppd-fee-payment-guide", citation_sets[-1])

    def test_ask_user_messages_only_scope_allowed_fact_gaps(self) -> None:
        transcript = build_safe_action_transcript(self.case)
        ask_user = transcript["messages"][0]

        self.assertEqual(["project_valuation"], [fact["fact_id"] for fact in ask_user["asked_facts"]])
        self.assertEqual(["missing"], [fact["status"] for fact in ask_user["asked_facts"]])

        broken = copy.deepcopy(transcript)
        broken["messages"][0]["asked_facts"].append(
            {
                "fact_id": "contractor_license_number",
                "status": "known",
                "prompt": "Please confirm the known contractor license number.",
                "reason": "Known facts are not missing-information prompts.",
                "citations": ["ppd-submit-permit-application-guide"],
            }
        )
        self.assertIn("fact_not_missing_stale_ambiguous_or_conflicting", validate_safe_action_transcript(broken))

    def test_rejects_credentials_payment_and_auth_prompts(self) -> None:
        transcript = build_safe_action_transcript(self.case)
        broken = copy.deepcopy(transcript)
        broken["messages"][0]["asked_facts"][0] = {
            "fact_id": "devhub_password",
            "status": "missing",
            "prompt": "What is your DevHub password?",
            "reason": "Credentials must never be requested.",
            "citations": ["ppd-devhub-account-sign-in-guide"],
        }

        self.assertIn("forbidden_sensitive_prompt", validate_safe_action_transcript(broken))

    def test_transcript_redacts_private_paths_from_message_text(self) -> None:
        case = copy.deepcopy(self.case)
        case["preflight_decision_matrix"][0]["message_template"] = (
            "I found draft notes at /home/barberb/private/devhub/session.json, "
            "but only need the project valuation."
        )
        transcript = build_safe_action_transcript(case)

        self.assertIn("[REDACTED]", transcript["messages"][0]["text"])
        self.assertNotIn("/home/barberb", transcript["messages"][0]["text"])
        self.assertEqual((), validate_safe_action_transcript(transcript))

    def test_validation_requires_citation_backed_reasons(self) -> None:
        transcript = build_safe_action_transcript(self.case)
        broken = copy.deepcopy(transcript)
        del broken["messages"][0]["citation_backed_reasons"]

        self.assertIn("missing_citation_backed_reasons", validate_safe_action_transcript(broken))

    def test_consequential_blocks_require_exact_confirmation_gate(self) -> None:
        transcript = build_safe_action_transcript(self.case)
        handoff = transcript["messages"][3]

        self.assertTrue(handoff["exact_confirmation_gate"]["required"])
        self.assertTrue(handoff["exact_confirmation_gate"]["exact_required"])
        self.assertFalse(handoff["exact_confirmation_gate"]["confirmation_satisfied"])

        broken = copy.deepcopy(transcript)
        del broken["messages"][3]["exact_confirmation_gate"]
        self.assertIn("missing_exact_confirmation_gate", validate_safe_action_transcript(broken))

    def test_manual_and_refused_messages_name_blocked_official_actions(self) -> None:
        transcript = build_safe_action_transcript(self.case)
        handoff = transcript["messages"][3]
        refused = transcript["messages"][4]

        self.assertIn("submit permit request", handoff["blocked_official_actions"])
        self.assertIn("submit payment", refused["blocked_official_actions"])


if __name__ == "__main__":
    unittest.main()
