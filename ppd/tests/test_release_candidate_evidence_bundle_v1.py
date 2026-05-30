from __future__ import annotations

import unittest

from ppd.agent_readiness.release_candidate_evidence_bundle_v1 import (
    PACKET_TYPE,
    validate_release_candidate_evidence_bundle_v1,
)


class ReleaseCandidateEvidenceBundleV1Tests(unittest.TestCase):
    def test_accepts_cited_side_effect_free_bundle(self) -> None:
        result = validate_release_candidate_evidence_bundle_v1(_valid_bundle())

        self.assertTrue(result.valid, result.as_dict())

    def test_rejects_missing_required_release_evidence_inventories(self) -> None:
        bundle = {
            "packet_type": PACKET_TYPE,
            "fixture_only": True,
        }

        result = validate_release_candidate_evidence_bundle_v1(bundle)

        self.assertFalse(result.valid)
        self.assert_issue_codes(
            result.as_dict()["issues"],
            {
                "missing_evidence_rows",
                "missing_unresolved_blocker_summaries",
                "missing_rollback_checkpoints",
                "missing_validation_command_inventory",
            },
        )

    def test_rejects_uncited_rows_blockers_checkpoints_and_commands(self) -> None:
        bundle = _valid_bundle()
        bundle["evidence_rows"] = [{"row_id": "row-uncited", "summary": "No citation."}]
        bundle["unresolved_blocker_summaries"] = [{"summary": "No citation."}]
        bundle["rollback_checkpoints"] = [{"checkpoint": "No citation."}]
        bundle["validation_command_inventory"] = [
            {"command": ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"], "expected_result": "passes"}
        ]

        result = validate_release_candidate_evidence_bundle_v1(bundle)

        self.assertFalse(result.valid)
        self.assert_issue_codes(
            result.as_dict()["issues"],
            {
                "uncited_evidence_row",
                "uncited_unresolved_blocker_summary",
                "uncited_rollback_checkpoint",
                "uncited_validation_command",
            },
        )

    def test_rejects_private_authenticated_raw_browser_and_session_artifacts(self) -> None:
        bundle = _valid_bundle()
        bundle["evidence_rows"].extend(
            [
                {"row_id": "private", "summary": "Uses auth_state.json", "source_evidence_ids": ["ev-private"]},
                {"row_id": "raw", "summary": "References raw_pdf bytes", "source_evidence_ids": ["ev-raw"]},
                {"row_id": "browser", "summary": "Includes playwright trace.zip", "source_evidence_ids": ["ev-browser"]},
                {"row_id": "session", "summary": "Stores session_state data", "source_evidence_ids": ["ev-session"]},
            ]
        )

        result = validate_release_candidate_evidence_bundle_v1(bundle)

        self.assertFalse(result.valid)
        self.assert_issue_codes(
            result.as_dict()["issues"],
            {"private_or_authenticated_artifact", "raw_capture_or_browser_artifact"},
        )

    def test_rejects_live_claims_guarantees_and_consequential_action_language(self) -> None:
        bundle = _valid_bundle()
        bundle["evidence_rows"].extend(
            [
                {"row_id": "live", "summary": "The release was promoted live.", "source_evidence_ids": ["ev-live"]},
                {"row_id": "guarantee", "summary": "Permit will be approved.", "source_evidence_ids": ["ev-guarantee"]},
                {"row_id": "action", "summary": "Ready to submit the permit.", "source_evidence_ids": ["ev-action"]},
            ]
        )

        result = validate_release_candidate_evidence_bundle_v1(bundle)

        self.assertFalse(result.valid)
        self.assert_issue_codes(
            result.as_dict()["issues"],
            {
                "live_promotion_or_execution_claim",
                "legal_or_permitting_outcome_guarantee",
                "consequential_action_language",
            },
        )

    def test_rejects_active_mutation_flags_for_release_surfaces(self) -> None:
        bundle = _valid_bundle()
        bundle["mutation_flags"] = {
            "source_mutation_active": True,
            "surface_registry_mutation_enabled": True,
            "guardrail_mutation_active": True,
            "prompt_mutation_active": True,
            "release_state_mutation_active": True,
            "agent_state_mutation_active": True,
        }

        result = validate_release_candidate_evidence_bundle_v1(bundle)

        self.assertFalse(result.valid)
        active_flag_issues = [issue for issue in result.as_dict()["issues"] if issue["code"] == "active_mutation_flag"]
        self.assertGreaterEqual(len(active_flag_issues), 6)

    def assert_issue_codes(self, issues: list[dict[str, str]], expected: set[str]) -> None:
        found = {issue["code"] for issue in issues}
        self.assertTrue(expected.issubset(found), f"missing {expected - found}; found {found}")


def _valid_bundle() -> dict[str, object]:
    return {
        "packet_type": PACKET_TYPE,
        "packet_id": "fixture-release-candidate-evidence-bundle-v1",
        "fixture_only": True,
        "evidence_rows": [
            {
                "row_id": "evidence-offline-release-readiness",
                "summary": "Offline release readiness packet was reviewed from committed deterministic fixtures.",
                "source_evidence_ids": ["ev-offline-release-readiness"],
            }
        ],
        "unresolved_blocker_summaries": [
            {
                "blocker_id": "blocker-none-recorded",
                "summary": "No unresolved blocker is asserted by this fixture bundle; operator review still gates promotion.",
                "source_evidence_ids": ["ev-offline-release-readiness"],
            }
        ],
        "rollback_checkpoints": [
            {
                "checkpoint_id": "rollback-active-state-unchanged",
                "checkpoint": "Confirm active release state remains unchanged before operator signoff.",
                "source_evidence_ids": ["ev-rollback-checkpoint"],
            }
        ],
        "validation_command_inventory": [
            {
                "command_id": "validation-self-test",
                "command": ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
                "expected_result": "Command exits zero in deterministic validation.",
                "source_evidence_ids": ["ev-validation-self-test"],
            }
        ],
        "mutation_flags": {
            "source_mutation_active": False,
            "surface_registry_mutation_active": False,
            "guardrail_mutation_active": False,
            "prompt_mutation_active": False,
            "release_state_mutation_active": False,
            "agent_state_mutation_active": False,
        },
    }


if __name__ == "__main__":
    unittest.main()
