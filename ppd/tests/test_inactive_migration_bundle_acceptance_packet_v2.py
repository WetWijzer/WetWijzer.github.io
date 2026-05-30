from __future__ import annotations

import copy
import unittest
from pathlib import Path
from typing import Any

from ppd.inactive_migration_bundle_acceptance_packet_v2 import (
    assert_inactive_migration_bundle_acceptance_packet_v2,
    load_inactive_migration_bundle_acceptance_packet_v2,
    validate_inactive_migration_bundle_acceptance_packet_v2,
)


FIXTURE = Path(__file__).parent / "fixtures" / "inactive_migration_bundle_acceptance_packet_v2" / "valid_packet.json"


class InactiveMigrationBundleAcceptancePacketV2Tests(unittest.TestCase):
    def packet(self) -> dict[str, Any]:
        return load_inactive_migration_bundle_acceptance_packet_v2(FIXTURE)

    def assert_rejects(self, packet: dict[str, Any], expected: str) -> None:
        errors = validate_inactive_migration_bundle_acceptance_packet_v2(packet)
        self.assertTrue(errors, "packet unexpectedly validated")
        self.assertIn(expected, "; ".join(errors))

    def test_valid_fixture_is_accepted(self) -> None:
        assert_inactive_migration_bundle_acceptance_packet_v2(self.packet())

    def test_rejects_uncited_bundle_rows(self) -> None:
        packet = self.packet()
        packet["bundle_acceptance_rows"][0]["citations"] = []
        self.assert_rejects(packet, "citations must be non-empty")

    def test_rejects_missing_decision_rationale(self) -> None:
        packet = self.packet()
        packet["bundle_acceptance_rows"][0]["rationale"] = ""
        self.assert_rejects(packet, "rationale is required")

    def test_rejects_missing_target_ids(self) -> None:
        for target_key in ("source_ids", "surface_ids", "guardrail_ids"):
            packet = self.packet()
            packet["bundle_acceptance_rows"][0]["target_ids"][target_key] = []
            self.assert_rejects(packet, f"target_ids.{target_key} must be non-empty")

    def test_rejects_missing_cross_artifact_consistency_checks(self) -> None:
        packet = self.packet()
        packet["cross_artifact_consistency_checks"] = []
        self.assert_rejects(packet, "cross_artifact_consistency_checks must not be empty")

    def test_rejects_missing_reviewer_owner_and_rollback_checkpoint(self) -> None:
        packet = self.packet()
        packet["bundle_acceptance_rows"][0]["reviewer_owner"] = ""
        packet["bundle_acceptance_rows"][0]["rollback_checkpoint"] = ""
        errors = "; ".join(validate_inactive_migration_bundle_acceptance_packet_v2(packet))
        self.assertIn("reviewer_owner is required", errors)
        self.assertIn("rollback_checkpoint is required", errors)

    def test_rejects_private_authenticated_and_raw_artifacts(self) -> None:
        packet = self.packet()
        packet["bundle_acceptance_rows"][0]["private_case_fact"] = "owner phone from account"
        packet["bundle_acceptance_rows"][0]["raw_pdf"] = "%PDF-raw bytes"
        errors = "; ".join(validate_inactive_migration_bundle_acceptance_packet_v2(packet))
        self.assertIn("private or authenticated facts", errors)
        self.assertIn("raw crawl/PDF/session/browser artifacts", errors)

    def test_rejects_textual_raw_session_browser_artifacts(self) -> None:
        packet = self.packet()
        packet["notes"] = "Includes storage-state.json and playwright trace from a browser session."
        errors = "; ".join(validate_inactive_migration_bundle_acceptance_packet_v2(packet))
        self.assertIn("private/authenticated facts or raw artifacts", errors)

    def test_rejects_live_execution_promotion_guarantees_and_consequential_language(self) -> None:
        cases = (
            ("live_note", "live DevHub run completed for this packet", "live execution or promotion claims"),
            ("promotion_note", "promoted to active release", "live execution or promotion claims"),
            ("guarantee_note", "permit will be approved", "legal or permitting outcome guarantees"),
            ("action_note", "submit application after accepting this row", "consequential action language"),
        )
        for key, value, expected in cases:
            packet = self.packet()
            packet[key] = value
            self.assert_rejects(packet, expected)

    def test_rejects_active_mutation_flags(self) -> None:
        mutation_keys = (
            "active_source_mutation",
            "active_surface_registry_mutation",
            "active_guardrail_mutation",
            "active_prompt_mutation",
            "active_monitoring_mutation",
            "active_release_state_mutation",
            "active_agent_state_mutation",
        )
        for key in mutation_keys:
            packet = self.packet()
            packet[key] = True
            self.assert_rejects(packet, "declares an active mutation flag")

    def test_rejects_bad_cross_artifact_check_rows(self) -> None:
        packet = self.packet()
        bad_check = copy.deepcopy(packet["cross_artifact_consistency_checks"][0])
        bad_check["guardrail_id"] = ""
        bad_check["citations"] = []
        packet["cross_artifact_consistency_checks"] = [bad_check]
        errors = "; ".join(validate_inactive_migration_bundle_acceptance_packet_v2(packet))
        self.assertIn("guardrail_id is required", errors)
        self.assertIn("citations must be non-empty", errors)


if __name__ == "__main__":
    unittest.main()
