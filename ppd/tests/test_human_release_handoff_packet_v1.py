import json
import unittest
from pathlib import Path

from ppd.agent_readiness.human_release_handoff_packet_v1 import (
    NO_ACTION_STATEMENTS,
    SCHEMA_VERSION,
    build_human_release_handoff_packet_v1,
    render_human_release_handoff_packet_v1,
)


FIXTURE = Path(__file__).parent / "fixtures" / "human_release_handoff_packet_v1" / "source_inputs.json"


class HumanReleaseHandoffPacketV1Tests(unittest.TestCase):
    def load_inputs(self):
        return json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_builds_apply_packet_from_fixture_inputs(self):
        packet = build_human_release_handoff_packet_v1(self.load_inputs())

        self.assertEqual(packet["schema_version"], SCHEMA_VERSION)
        self.assertEqual(packet["recommendation"], "APPLY")
        self.assertIn("offline_acceptance_rehearsal_summary_v1:fixture", packet["recommendation_citations"])
        self.assertIn("reviewer_disposition_ledger_v1:fixture", packet["recommendation_citations"])
        self.assertEqual(packet["unresolved_blockers"], [])
        self.assertIn("ppd/tests/fixtures/offline_acceptance_rehearsal_summary_v1", packet["fixture_families_to_inspect"])
        self.assertIn("ppd/tests/fixtures/reviewer_disposition_ledger_v1", packet["fixture_families_to_inspect"])

    def test_hold_packet_lists_blockers_with_citations(self):
        source_inputs = self.load_inputs()
        source_inputs["reviewer_disposition_ledger_v1"]["status"] = "hold"
        source_inputs["reviewer_disposition_ledger_v1"]["dispositions"] = [
            {
                "disposition": "hold",
                "reason": "Reviewer requested fixture family inspection before apply.",
                "citation": "reviewer_disposition_ledger_v1:dispositions:hold-review"
            }
        ]

        packet = build_human_release_handoff_packet_v1(source_inputs)

        self.assertEqual(packet["recommendation"], "HOLD")
        self.assertEqual(packet["unresolved_blockers"][0]["blocker"], "Reviewer requested fixture family inspection before apply.")
        self.assertEqual(packet["unresolved_blockers"][0]["citation"], "reviewer_disposition_ledger_v1:dispositions:hold-review")

    def test_rendered_packet_contains_required_human_handoff_sections(self):
        packet = build_human_release_handoff_packet_v1(self.load_inputs())
        rendered = render_human_release_handoff_packet_v1(packet)

        self.assertIn("Recommendation: APPLY", rendered)
        self.assertIn("Fixture families to inspect:", rendered)
        self.assertIn("Unresolved blockers:", rendered)
        self.assertIn("Rollback note:", rendered)
        self.assertIn("Post-apply validation checklist:", rendered)
        for statement in NO_ACTION_STATEMENTS:
            self.assertIn(statement, rendered)
            self.assertIn(statement, packet["no_action_statements"])


if __name__ == "__main__":
    unittest.main()
