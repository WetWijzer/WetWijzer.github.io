from __future__ import annotations

import copy
import unittest

from ppd.agent_readiness.inactive_promotion_sandbox_rehearsal_packet_v1 import (
    PACKET_TYPE,
    VALIDATION_COMMANDS,
    validate_inactive_promotion_sandbox_rehearsal_packet_v1,
)


def valid_packet() -> dict[str, object]:
    return {
        "packet_type": PACKET_TYPE,
        "packet_version": "v1",
        "fixture_first": True,
        "metadata_only": True,
        "sandbox_rehearsal_only": True,
        "validation_commands": VALIDATION_COMMANDS,
        "synthetic_sandbox_apply_steps": [
            {
                "step_id": "apply-step-1",
                "fixture_family": "agent-readiness",
                "synthetic_action": "synthetic sandbox apply of inactive fixture replacement proposal",
                "expected_result": "sandbox worktree receives only the expected fixture preview changes",
            }
        ],
        "expected_changed_fixture_family_inventory": [
            {
                "fixture_family": "agent-readiness",
                "expected_changed_paths": ["ppd/tests/fixtures/agent_readiness/inactive_preview_packet.json"],
                "change_reason": "exercise inactive promotion rehearsal fixture family coverage",
            }
        ],
        "pre_apply_validation_commands": [
            {
                "command_id": "pre-self-test",
                "command": ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
                "expected_result": "passes before synthetic sandbox apply",
            }
        ],
        "post_apply_validation_commands": [
            {
                "command_id": "post-self-test",
                "command": ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
                "expected_result": "passes after synthetic sandbox apply",
            }
        ],
        "rollback_rehearsal_commands": [
            {
                "command_id": "rollback-self-test",
                "command": ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
                "expected_result": "passes after discarding sandbox rehearsal output",
            }
        ],
        "no_main_worktree_change_notes": [
            {
                "note_id": "main-worktree-unchanged",
                "statement": "main worktree unchanged; rehearsal output remains sandbox metadata only",
            }
        ],
        "reviewer_signoff_placeholders": [
            {
                "placeholder_id": "reviewer-signoff-1",
                "reviewer_role": "PP&D fixture reviewer",
                "status": "pending_manual_review",
                "disposition": "pending",
            }
        ],
        "active_artifact_mutation": False,
        "active_prompt_mutation": False,
        "active_release_state_mutation": False,
        "active_fixture_mutation": False,
        "active_agent_state_mutation": False,
    }


class InactivePromotionSandboxRehearsalPacketV1Tests(unittest.TestCase):
    def assert_problem_contains(self, packet: dict[str, object], expected: str) -> None:
        result = validate_inactive_promotion_sandbox_rehearsal_packet_v1(packet)
        self.assertFalse(result.valid)
        self.assertTrue(
            any(expected in problem for problem in result.problems),
            f"expected problem containing {expected!r}, got {result.problems!r}",
        )

    def test_valid_packet_passes(self) -> None:
        result = validate_inactive_promotion_sandbox_rehearsal_packet_v1(valid_packet())
        self.assertTrue(result.valid, result.problems)

    def test_rejects_missing_required_rehearsal_sections(self) -> None:
        required_sections = (
            "synthetic_sandbox_apply_steps",
            "expected_changed_fixture_family_inventory",
            "pre_apply_validation_commands",
            "post_apply_validation_commands",
            "rollback_rehearsal_commands",
            "no_main_worktree_change_notes",
            "reviewer_signoff_placeholders",
        )
        for section in required_sections:
            with self.subTest(section=section):
                packet = valid_packet()
                packet.pop(section)
                self.assert_problem_contains(packet, f"{section} must be a non-empty list")

    def test_rejects_private_browser_auth_raw_and_download_artifacts(self) -> None:
        forbidden_values = (
            ("auth_state", "redacted auth state"),
            ("browser_artifact", "browser artifact"),
            ("session_storage", "session storage"),
            ("screenshot_path", "har file"),
            ("raw_crawl_output", "raw crawl output"),
            ("downloaded_pdf", "downloaded pdf"),
        )
        for key, value in forbidden_values:
            with self.subTest(key=key):
                packet = valid_packet()
                packet[key] = value
                result = validate_inactive_promotion_sandbox_rehearsal_packet_v1(packet)
                self.assertFalse(result.valid)

    def test_rejects_live_release_applied_claims_outcome_guarantees_and_consequential_language(self) -> None:
        forbidden_notes = (
            "live execution completed",
            "main worktree applied",
            "release complete",
            "permit will be approved",
            "automation will submit permit",
        )
        for note in forbidden_notes:
            with self.subTest(note=note):
                packet = valid_packet()
                packet["review_notes"] = note
                result = validate_inactive_promotion_sandbox_rehearsal_packet_v1(packet)
                self.assertFalse(result.valid)

    def test_rejects_active_mutation_flags(self) -> None:
        mutation_flags = (
            "active_artifact_mutation",
            "active_prompt_mutation",
            "active_release_state_mutation",
            "active_fixture_mutation",
            "active_agent_state_mutation",
        )
        for flag in mutation_flags:
            with self.subTest(flag=flag):
                packet = valid_packet()
                packet[flag] = True
                self.assert_problem_contains(packet, "must")

    def test_rejects_inventory_outside_ppd_fixture_tree(self) -> None:
        packet = valid_packet()
        inventory = copy.deepcopy(packet["expected_changed_fixture_family_inventory"])
        assert isinstance(inventory, list)
        inventory[0]["expected_changed_paths"] = ["tests/fixtures/outside.json"]
        packet["expected_changed_fixture_family_inventory"] = inventory
        self.assert_problem_contains(packet, "expected_changed_paths must stay under ppd/tests/fixtures")


if __name__ == "__main__":
    unittest.main()
