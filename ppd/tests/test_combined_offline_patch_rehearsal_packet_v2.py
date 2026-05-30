import copy
import unittest
from pathlib import Path

from ppd.agent_readiness.combined_offline_patch_rehearsal_packet_v2 import (
    build_combined_offline_patch_rehearsal_packet,
    load_fixture_packet,
    validate_combined_offline_patch_rehearsal_packet,
)


class CombinedOfflinePatchRehearsalPacketV2Test(unittest.TestCase):
    def fixture_path(self) -> Path:
        return Path(__file__).parent / "fixtures" / "combined_offline_patch_rehearsal_v2" / "rehearsal_inputs.json"

    def fixture_input(self) -> dict:
        import json

        with self.fixture_path().open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def test_fixture_packet_is_dependency_ordered_and_offline_only(self) -> None:
        packet = load_fixture_packet(self.fixture_path())

        self.assertEqual(packet["packet_version"], "2")
        self.assertEqual(packet["mode"], "fixture-first-offline")
        self.assertEqual(packet["validation_status"], "pass")
        self.assertEqual(
            packet["reviewer_owner_fields"],
            {
                "source_owner": "public-source-reviewer",
                "devhub_surface_owner": "devhub-surface-reviewer",
                "guardrail_owner": "guardrail-reviewer",
                "rollback_owner": "rollback-reviewer",
            },
        )

        steps = packet["dependency_ordered_rehearsal_steps"]
        self.assertEqual(
            [step["step_id"] for step in steps],
            [
                "step-source-src-submit-plans-online",
                "step-devhub-devhub-upload-staging",
                "step-guardrail-guardrail-upload-confirmation-gate",
            ],
        )
        self.assertEqual(steps[1]["depends_on"], ["step-source-src-submit-plans-online"])
        self.assertEqual(
            steps[2]["depends_on"],
            ["step-source-src-submit-plans-online", "step-devhub-devhub-upload-staging"],
        )
        self.assertTrue(all(step["offline_only"] for step in steps))
        self.assertTrue(all(step["citations"] for step in steps))

        attestations = packet["attestations"]
        self.assertTrue(attestations["no_live_crawl"])
        self.assertTrue(attestations["no_auth"])
        self.assertTrue(attestations["no_official_action"])
        self.assertTrue(attestations["no_release_state_mutation"])

    def test_packet_contains_checks_fixture_diffs_rollback_and_validation_commands(self) -> None:
        packet = load_fixture_packet(self.fixture_path())

        checks = packet["cross_artifact_consistency_checks"]
        self.assertTrue(checks)
        self.assertTrue(all(check["status"] == "pass" for check in checks))
        self.assertEqual({check["check_id"] for check in checks}, {
            "devhub-source-dependencies-devhub-upload-staging",
            "guardrail-preview-dependencies-guardrail-upload-confirmation-gate",
            "citation-coverage",
            "combined-preview-presence",
        })

        expected_diffs = packet["expected_fixture_diffs"]
        self.assertEqual(len(expected_diffs), 3)
        self.assertTrue(all(diff["fixture_path"].startswith("ppd/tests/fixtures/") for diff in expected_diffs))
        self.assertTrue(all(diff["before_hash"] and diff["after_hash"] for diff in expected_diffs))
        self.assertEqual(len(packet["rollback_verification"]), 3)
        self.assertIn(
            ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
            packet["offline_validation_commands"],
        )

    def test_missing_required_attestation_is_rejected(self) -> None:
        bad_input = self.fixture_input()
        bad_input["attestations"]["no_live_crawl"] = False

        with self.assertRaisesRegex(ValueError, "attestation no_live_crawl"):
            build_combined_offline_patch_rehearsal_packet(bad_input)

    def test_rejects_uncited_rehearsal_steps(self) -> None:
        packet = load_fixture_packet(self.fixture_path())
        packet["dependency_ordered_rehearsal_steps"][0]["citations"] = []

        with self.assertRaisesRegex(ValueError, "lacks citations"):
            validate_combined_offline_patch_rehearsal_packet(packet)

    def test_rejects_missing_dependency_ordering(self) -> None:
        bad_input = self.fixture_input()
        bad_input["devhub_surface_previews"][0].pop("depends_on")

        with self.assertRaisesRegex(ValueError, "lacks explicit source dependency ordering"):
            build_combined_offline_patch_rehearsal_packet(bad_input)

    def test_rejects_out_of_order_packet_dependencies(self) -> None:
        packet = load_fixture_packet(self.fixture_path())
        steps = packet["dependency_ordered_rehearsal_steps"]
        packet["dependency_ordered_rehearsal_steps"] = [steps[1], steps[0], steps[2]]

        with self.assertRaisesRegex(ValueError, "out of order"):
            validate_combined_offline_patch_rehearsal_packet(packet)

    def test_rejects_missing_cross_artifact_checks_fixture_diffs_and_rollback(self) -> None:
        packet = load_fixture_packet(self.fixture_path())
        for key, message in (
            ("cross_artifact_consistency_checks", "cross_artifact_consistency_checks are required"),
            ("expected_fixture_diffs", "expected_fixture_diffs are required"),
            ("rollback_verification", "rollback_verification is required"),
        ):
            broken = copy.deepcopy(packet)
            broken[key] = []
            with self.assertRaisesRegex(ValueError, message):
                validate_combined_offline_patch_rehearsal_packet(broken)

    def test_rejects_missing_expected_fixture_diff_fields(self) -> None:
        bad_input = self.fixture_input()
        bad_input["source_patch_previews"][0].pop("after_hash")

        with self.assertRaisesRegex(ValueError, "missing after_hash"):
            build_combined_offline_patch_rehearsal_packet(bad_input)

    def test_rejects_rollback_without_manual_verification(self) -> None:
        packet = load_fixture_packet(self.fixture_path())
        packet["rollback_verification"][0]["requires_manual_confirmation"] = False

        with self.assertRaisesRegex(ValueError, "must require manual confirmation"):
            validate_combined_offline_patch_rehearsal_packet(packet)

    def test_rejects_private_auth_raw_live_guarantee_consequential_and_mutation_content(self) -> None:
        bad_cases = [
            ({"private_fact": "owner email"}, "private or authenticated facts"),
            ({"raw_pdf": "binary"}, "raw crawl/PDF/session/browser artifacts"),
            ({"live_execution": True}, "live execution or promotion claims"),
            ({"summary": "permit will be approved after this packet"}, "legal or permitting outcome guarantees"),
            ({"next_action": "submit permit in DevHub"}, "consequential action language"),
            ({"active_guardrail_mutation": True}, "active mutation flags"),
            ({"apply_to_active_surface_registry": True}, "active mutation flags"),
            ({"active_prompt_mutation": True}, "active mutation flags"),
            ({"active_monitoring_mutation": True}, "active mutation flags"),
            ({"active_release_state_mutation": True}, "active mutation flags"),
            ({"active_agent_state_mutation": True}, "active mutation flags"),
            ({"active_source_mutation": True}, "active mutation flags"),
        ]

        for injected, message in bad_cases:
            bad_input = self.fixture_input()
            bad_input["unsafe_test_field"] = injected
            with self.subTest(injected=injected):
                with self.assertRaisesRegex(ValueError, message):
                    build_combined_offline_patch_rehearsal_packet(bad_input)


if __name__ == "__main__":
    unittest.main()
