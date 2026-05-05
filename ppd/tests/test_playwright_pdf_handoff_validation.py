from __future__ import annotations

from pathlib import Path
import unittest

from ppd.devhub.playwright_pdf_handoff_validation import (
    load_handoff_fixture,
    validate_playwright_pdf_handoff,
)


FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "devhub_pdf_handoff"
    / "tranche2_redacted_handoff.json"
)


class PlaywrightPdfHandoffValidationTests(unittest.TestCase):
    def test_redacted_facts_fill_draft_and_pdf_preview_fields(self) -> None:
        payload = load_handoff_fixture(FIXTURE_PATH)

        result = validate_playwright_pdf_handoff(payload)

        self.assertTrue(result.ok, result.findings)
        self.assertEqual(result.draft_fields["draft.applicant.name"], "[REDACTED_APPLICANT_NAME]")
        self.assertEqual(result.draft_fields["draft.project.site_address"], "[REDACTED_SITE_ADDRESS]")
        self.assertEqual(result.pdf_preview_fields["ApplicantName"], "[REDACTED_APPLICANT_NAME]")
        self.assertEqual(result.pdf_preview_fields["ProjectSiteAddress"], "[REDACTED_SITE_ADDRESS]")
        self.assertIn("fill reversible DevHub draft fields", result.allowed_transitions)
        self.assertIn("render local PDF preview", result.allowed_transitions)

    def test_official_devhub_transitions_remain_behind_exact_confirmation(self) -> None:
        payload = load_handoff_fixture(FIXTURE_PATH)

        result = validate_playwright_pdf_handoff(payload)

        self.assertTrue(result.ok, result.findings)
        self.assertIn("upload plans to official DevHub record", result.blocked_transitions)
        self.assertIn("submit permit request", result.blocked_transitions)
        self.assertIn("certify application statements", result.blocked_transitions)
        self.assertIn("pay reviewed fees", result.blocked_transitions)
        self.assertNotIn("submit permit request", result.allowed_transitions)

    def test_exact_checkpoint_can_allow_only_the_named_official_transition(self) -> None:
        payload = dict(load_handoff_fixture(FIXTURE_PATH))
        transitions = [dict(item) for item in payload["devhub_transitions"]]
        transitions[2]["confirmation_provided"] = transitions[2]["exact_confirmation"]
        payload["devhub_transitions"] = transitions

        result = validate_playwright_pdf_handoff(payload)

        self.assertTrue(result.ok, result.findings)
        self.assertIn("upload plans to official DevHub record", result.allowed_transitions)
        self.assertIn("submit permit request", result.blocked_transitions)
        self.assertIn("certify application statements", result.blocked_transitions)
        self.assertIn("pay reviewed fees", result.blocked_transitions)

    def test_unredacted_fact_is_rejected_before_any_handoff_is_trusted(self) -> None:
        payload = dict(load_handoff_fixture(FIXTURE_PATH))
        facts = dict(payload["redacted_user_facts"])
        facts["applicant_name"] = "Jane Permit Applicant"
        payload["redacted_user_facts"] = facts

        result = validate_playwright_pdf_handoff(payload)

        self.assertFalse(result.ok)
        self.assertIn("fact 'applicant_name' must be present as a redacted token", result.findings)
        self.assertNotIn("draft.applicant.name", result.draft_fields)
        self.assertNotIn("ApplicantName", result.pdf_preview_fields)


if __name__ == "__main__":
    unittest.main()
