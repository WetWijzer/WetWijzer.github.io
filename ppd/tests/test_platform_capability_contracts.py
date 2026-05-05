from __future__ import annotations

import unittest

from ppd.platform.autonomous_archival_contract import archival_contract
from ppd.platform.playwright_pdf_contract import playwright_pdf_contract
from ppd.platform.processor_suite_contract import processor_suite_contract
from ppd.platform.supervisor_idle_policy import supervisor_idle_policy


class PlatformCapabilityContractsTest(unittest.TestCase):
    def test_archival_contract_is_source_backed_and_fixture_first(self) -> None:
        contract = archival_contract()

        self.assertEqual("whole_site_public_archival", contract["capability"])
        self.assertIn("ipfs_datasets_py.processors", contract["entrypoints"])
        self.assertIn("archive_manifest", contract["requiredOutputs"])
        self.assertFalse(contract["liveCrawlAllowedByDefault"])
        self.assertEqual("fixture_only", contract["defaultMode"])

    def test_processor_suite_contract_keeps_raw_bodies_out_of_default_storage(self) -> None:
        contract = processor_suite_contract()

        self.assertEqual("processor_suite_handoff", contract["capability"])
        self.assertEqual("ipfs_datasets_py.processors", contract["processorSuite"])
        self.assertIn("formal_logic_source_evidence_id", contract["requiredOutputs"])
        self.assertFalse(contract["rawBodyPersistenceAllowed"])

    def test_playwright_pdf_contract_requires_attendance_and_blocks_official_actions(self) -> None:
        contract = playwright_pdf_contract()

        self.assertEqual("attended_draft_automation", contract["capability"])
        self.assertIn("reversible_draft_field_fill", contract["allowedActions"])
        self.assertIn("local_pdf_preview_fill", contract["allowedActions"])
        self.assertIn("official_upload", contract["blockedActions"])
        self.assertIn("fee_payment", contract["blockedActions"])
        self.assertTrue(contract["requiresHumanAttendanceBeforeBrowserUse"])
        self.assertTrue(contract["exactConfirmationBeforeOfficialAction"])

    def test_supervisor_idle_policy_caps_generated_tranches_and_requires_promotion_checks(self) -> None:
        policy = supervisor_idle_policy()

        self.assertEqual("review_goal_before_replenishment", policy["noEligibleTasksPolicy"])
        self.assertEqual(1, policy["replenishmentLimits"]["autonomousPlatformTranches"])
        self.assertEqual(1, policy["replenishmentLimits"]["executionCapabilityTranches"])
        self.assertTrue(policy["mustNotAcceptRuntimeOnlyProgress"])
        self.assertTrue(policy["mustVerifyPromotionToMainWorktree"])
        self.assertEqual("ledger_only", policy["acceptedEvidenceMode"])


if __name__ == "__main__":
    unittest.main()
