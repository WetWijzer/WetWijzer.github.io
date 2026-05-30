from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from ppd.agent_readiness.combined_promotion_rehearsal_v3 import (
    PACKET_TYPE,
    REQUIRED_ATTESTATIONS,
    build_combined_promotion_rehearsal_v3,
    load_fixture_packet,
    validate_combined_promotion_rehearsal_v3,
)

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "combined_promotion_rehearsal_v3" / "rehearsal_inputs.json"


class CombinedPromotionRehearsalV3Test(unittest.TestCase):
    def fixture_input(self) -> dict[str, object]:
        return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    def test_builds_dependency_ordered_fixture_first_packet(self) -> None:
        packet = load_fixture_packet(FIXTURE_PATH)

        self.assertEqual(packet["packet_type"], PACKET_TYPE)
        self.assertEqual(packet["packet_version"], 3)
        self.assertEqual(packet["mode"], "fixture_first_combined_promotion_rehearsal_only")
        self.assertEqual(packet["attestations"], REQUIRED_ATTESTATIONS)
        self.assertEqual(validate_combined_promotion_rehearsal_v3(packet), [])

        steps = packet["dependency_ordered_rehearsal_steps"]
        self.assertEqual(
            [step["step_id"] for step in steps],
            [
                "step-source-src-preview-submit-plans-online",
                "step-devhub-devhub-preview-upload-surface",
                "step-guardrail-guardrail-preview-upload-confirmation",
            ],
        )
        self.assertEqual(steps[1]["depends_on"], ["step-source-src-preview-submit-plans-online"])
        self.assertEqual(
            steps[2]["depends_on"],
            ["step-source-src-preview-submit-plans-online", "step-devhub-devhub-preview-upload-surface"],
        )
        self.assertTrue(all(step["offline_only"] for step in steps))
        self.assertTrue(all(step["citations"] for step in steps))

    def test_contains_consistency_checks_fixture_diffs_rollback_and_reviewer_owners(self) -> None:
        packet = load_fixture_packet(FIXTURE_PATH)

        self.assertEqual(
            packet["reviewer_owner_fields"],
            {
                "source_registry_owner": "public-source-reviewer",
                "devhub_surface_map_owner": "devhub-surface-reviewer",
                "guardrail_bundle_owner": "guardrail-reviewer",
                "rollback_owner": "rollback-reviewer",
            },
        )
        self.assertEqual({check["check_id"] for check in packet["cross_artifact_consistency_checks"]}, {
            "combined-preview-presence",
            "source-requirement-coverage",
            "devhub-after-source-ordering",
            "guardrail-after-source-and-devhub-ordering",
        })
        self.assertTrue(all(check["status"] == "pass" for check in packet["cross_artifact_consistency_checks"]))
        self.assertEqual(len(packet["expected_fixture_diffs"]), 3)
        self.assertTrue(all(diff["fixture_path"].startswith("ppd/tests/fixtures/") for diff in packet["expected_fixture_diffs"]))
        self.assertEqual(len(packet["rollback_verification"]), 3)
        self.assertTrue(all(row["requires_manual_confirmation"] for row in packet["rollback_verification"]))
        self.assertIn(["python3", "ppd/daemon/ppd_daemon.py", "--self-test"], packet["offline_validation_commands"])

    def test_rejects_missing_preview_family(self) -> None:
        data = self.fixture_input()
        data.pop("guardrail_bundle_promotion_preview_v3")

        with self.assertRaisesRegex(ValueError, "promotion previews v3 are required"):
            build_combined_promotion_rehearsal_v3(data)

    def test_validator_rejects_uncited_steps_missing_checks_diffs_rollback_and_attestation(self) -> None:
        packet = load_fixture_packet(FIXTURE_PATH)
        broken = copy.deepcopy(packet)
        broken["dependency_ordered_rehearsal_steps"][0]["citations"] = []
        broken["cross_artifact_consistency_checks"] = []
        broken["expected_fixture_diffs"] = []
        broken["rollback_verification"] = []
        broken["attestations"]["no_live"] = False

        errors = validate_combined_promotion_rehearsal_v3(broken)

        self.assertIn("dependency_ordered_rehearsal_steps[0].citations must be non-empty", errors)
        self.assertIn("cross_artifact_consistency_checks must be non-empty", errors)
        self.assertIn("expected_fixture_diffs must be non-empty", errors)
        self.assertIn("rollback_verification must be non-empty", errors)
        self.assertIn("attestations.no_live must be true", errors)

    def test_validator_rejects_out_of_order_dependencies(self) -> None:
        packet = load_fixture_packet(FIXTURE_PATH)
        steps = packet["dependency_ordered_rehearsal_steps"]
        packet["dependency_ordered_rehearsal_steps"] = [steps[1], steps[0], steps[2]]

        errors = validate_combined_promotion_rehearsal_v3(packet)

        self.assertTrue(any("dependency is missing or out of order" in error for error in errors))

    def test_rejects_private_raw_live_guarantee_consequential_and_mutation_content(self) -> None:
        cases = [
            ({"private_fact": "owner email"}, "private or authenticated facts"),
            ({"raw_pdf": "binary"}, "raw crawl/PDF/session/browser artifacts"),
            ({"live_execution": True}, "live execution or promotion claims"),
            ({"summary": "permit will be approved"}, "legal or permitting outcome guarantees"),
            ({"next_step": "submit permit"}, "consequential action language"),
            ({"active_guardrail_mutation": True}, "active registry or guardrail mutation flags"),
            ({"active_surface_registry_mutation": True}, "active registry or guardrail mutation flags"),
        ]

        for injected, message in cases:
            data = self.fixture_input()
            data["unsafe_test_field"] = injected
            with self.subTest(injected=injected):
                with self.assertRaisesRegex(ValueError, message):
                    build_combined_promotion_rehearsal_v3(data)


if __name__ == "__main__":
    unittest.main()
