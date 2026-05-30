from __future__ import annotations

import unittest

from ppd.draft_preview import HandoffPacketV2ValidationError, validate_handoff_packet_v2


def valid_packet() -> dict[str, object]:
    return {
        "version": "draft_preview_agent_handoff_packet_v2",
        "handoff_notes": [
            {
                "text": "Draft preview can compare user-supplied facts with cited PP&D guidance.",
                "source_evidence_ids": ["ppd-devhub-guide-submit-permit-application"],
            }
        ],
        "supported_scenario_refs": ["draft-preview-local-pdf-field-mapping"],
        "blocked_scenario_refs": ["official-submit-payment-upload-schedule-cancel"],
        "exact_confirmation_reminders": [
            "Require user attendance and exact confirmation before any consequential official action."
        ],
        "mutation_flags": {
            "active_prompt_mutation": False,
            "active_guardrail_mutation": False,
            "active_pdf_mutation": False,
            "active_gap_analysis_mutation": False,
            "active_monitoring_mutation": False,
            "active_release_state_mutation": False,
            "active_agent_state_mutation": False,
        },
    }


class HandoffPacketV2ValidationTests(unittest.TestCase):
    def test_accepts_cited_preview_scoped_packet(self) -> None:
        result = validate_handoff_packet_v2(valid_packet())
        self.assertEqual(result["validation_status"], "accepted")
        self.assertEqual(result["handoff_note_count"], 1)

    def test_rejects_uncited_handoff_notes(self) -> None:
        packet = valid_packet()
        packet["handoff_notes"] = [{"text": "This note has no citation."}]
        with self.assertRaises(HandoffPacketV2ValidationError) as raised:
            validate_handoff_packet_v2(packet)
        self.assertIn("handoff_notes[0].missing_citation", raised.exception.errors)

    def test_rejects_missing_supported_and_blocked_refs(self) -> None:
        packet = valid_packet()
        packet["supported_scenario_refs"] = []
        packet["blocked_scenario_refs"] = []
        with self.assertRaises(HandoffPacketV2ValidationError) as raised:
            validate_handoff_packet_v2(packet)
        self.assertIn("missing_supported_scenario_refs", raised.exception.errors)
        self.assertIn("missing_blocked_scenario_refs", raised.exception.errors)

    def test_rejects_missing_exact_confirmation_reminder(self) -> None:
        packet = valid_packet()
        packet["exact_confirmation_reminders"] = ["Ask the user before risky actions."]
        with self.assertRaises(HandoffPacketV2ValidationError) as raised:
            validate_handoff_packet_v2(packet)
        self.assertIn("missing_exact_confirmation_reminders", raised.exception.errors)

    def test_rejects_private_raw_live_guarantee_and_consequential_language(self) -> None:
        packet = valid_packet()
        packet["handoff_notes"] = [
            {
                "text": (
                    "The authenticated fact from My Permits proves the raw PDF value is correct; "
                    "I opened DevHub in a browser session, so the permit will be approved after final submission."
                ),
                "source_evidence_ids": ["fixture-source"],
            }
        ]
        with self.assertRaises(HandoffPacketV2ValidationError) as raised:
            validate_handoff_packet_v2(packet)
        joined = "\n".join(raised.exception.errors)
        self.assertIn("private_or_authenticated_fact", joined)
        self.assertIn("raw_pdf_value", joined)
        self.assertIn("live_execution_claim", joined)
        self.assertIn("outcome_guarantee", joined)
        self.assertIn("consequential_action_language", joined)

    def test_rejects_active_mutation_flags(self) -> None:
        packet = valid_packet()
        packet["mutation_flags"] = {"active_guardrail_mutation": True}
        with self.assertRaises(HandoffPacketV2ValidationError) as raised:
            validate_handoff_packet_v2(packet)
        self.assertIn("packet.mutation_flags.active_guardrail_mutation.active_mutation_flag", raised.exception.errors)


if __name__ == "__main__":
    unittest.main()
