from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from ppd.agent_readiness.devhub_read_only_observation_reviewer_disposition_queue_v1 import (
    assert_valid_devhub_read_only_observation_reviewer_disposition_queue_v1,
    validate_devhub_read_only_observation_reviewer_disposition_queue_v1,
)


_FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "devhub_read_only_observation_reviewer_disposition_queue_v1_valid.json"
)


def _load_valid_queue() -> dict:
    return json.loads(_FIXTURE_PATH.read_text(encoding="utf-8"))


def _issue_codes(queue: dict) -> set[str]:
    return {issue.code for issue in validate_devhub_read_only_observation_reviewer_disposition_queue_v1(queue)}


class DevHubReadOnlyObservationReviewerDispositionQueueV1Tests(unittest.TestCase):
    def test_valid_fixture_passes(self) -> None:
        queue = _load_valid_queue()

        self.assertEqual(validate_devhub_read_only_observation_reviewer_disposition_queue_v1(queue), [])
        assert_valid_devhub_read_only_observation_reviewer_disposition_queue_v1(queue)

    def test_rejects_missing_required_queue_sections(self) -> None:
        required_sections = (
            "reviewer_decision_rows",
            "safe_read_only_surface_buckets",
            "redaction_confirmation_placeholders",
            "blocked_action_carry_forward_notes",
            "rollback_checkpoints",
            "validation_commands",
        )

        for section in required_sections:
            with self.subTest(section=section):
                queue = _load_valid_queue()
                queue.pop(section)

                self.assertIn(f"missing_{section}", _issue_codes(queue))

    def test_rejects_reviewer_rows_missing_required_cross_references(self) -> None:
        required_refs = (
            "safe_read_only_surface_bucket_id",
            "redaction_confirmation_placeholder_id",
            "blocked_action_carry_forward_note_id",
            "rollback_checkpoint_id",
        )

        for ref_key in required_refs:
            with self.subTest(ref_key=ref_key):
                queue = _load_valid_queue()
                queue["reviewer_decision_rows"][0].pop(ref_key)

                codes = _issue_codes(queue)
                self.assertTrue(any(code.startswith("missing_") and code.endswith("_ref") for code in codes))

    def test_rejects_private_browser_raw_capture_and_auth_artifact_language(self) -> None:
        forbidden_examples = {
            "private_or_session_artifact_language": "Store the DevHub session state for later review.",
            "browser_capture_artifact_language": "Attach the trace.zip file to the queue.",
            "raw_or_downloaded_data_language": "Keep the raw PDF dump as reviewer evidence.",
        }

        for expected_code, text in forbidden_examples.items():
            with self.subTest(expected_code=expected_code):
                queue = _load_valid_queue()
                queue["reviewer_decision_rows"][0]["rationale"] = text

                self.assertIn(expected_code, _issue_codes(queue))

    def test_rejects_live_claims_outcome_guarantees_and_consequential_language(self) -> None:
        forbidden_examples = {
            "live_execution_or_observation_promotion_claim": "The observation promoted after live authenticated execution.",
            "legal_or_permitting_outcome_guarantee": "The permit will be issued after this review.",
            "consequential_action_language": "Reviewer should submit the application next.",
        }

        for expected_code, text in forbidden_examples.items():
            with self.subTest(expected_code=expected_code):
                queue = _load_valid_queue()
                queue["reviewer_decision_rows"][0]["rationale"] = text

                self.assertIn(expected_code, _issue_codes(queue))

    def test_rejects_artifact_policy_that_allows_sensitive_outputs(self) -> None:
        queue = _load_valid_queue()
        queue["artifact_policy"]["creates_screenshots"] = True

        self.assertIn("artifact_policy_not_false", _issue_codes(queue))

    def test_rejects_active_mutation_flags(self) -> None:
        mutation_flags = (
            "active_source_mutation",
            "active_surface_mutation",
            "active_guardrail_mutation",
            "active_release_state_mutation",
            "active_prompt_mutation",
            "active_fixture_mutation",
            "active_agent_state_mutation",
        )

        for flag in mutation_flags:
            with self.subTest(flag=flag):
                queue = _load_valid_queue()
                queue["mutation_flags"][flag] = True

                self.assertIn("active_mutation_flag", _issue_codes(queue))

    def test_rejects_unknown_or_unsafe_surface_bucket(self) -> None:
        queue = _load_valid_queue()
        queue["safe_read_only_surface_buckets"] = copy.deepcopy(queue["safe_read_only_surface_buckets"])
        queue["safe_read_only_surface_buckets"][0]["classification"] = "reversible_draft"

        self.assertIn("unsafe_surface_bucket_classification", _issue_codes(queue))


if __name__ == "__main__":
    unittest.main()
