from __future__ import annotations

import copy
import unittest

from ppd.public_freshness_scheduler_rehearsal_v4_validation import (
    SchedulerRehearsalSafetyValidationError,
    require_public_freshness_scheduler_rehearsal_v4_safety,
    validate_public_freshness_scheduler_rehearsal_v4_safety,
)


def valid_packet() -> dict[str, object]:
    return {
        "schema": "ppd.public_freshness_scheduler_rehearsal.v4",
        "cited_metadata_only_recrawl_schedule_candidates": [
            {
                "source_id": "portland-zoning-code",
                "affected_source_ids": ["portland-zoning-code"],
                "affected_requirement_ids": ["REQ-ZONING-CODE-FRESHNESS"],
                "metadata_fields": {"public_url": "https://www.portland.gov/code/33"},
                "citations": [{"label": "scheduler-rehearsal:portland-zoning-code"}],
            }
        ],
        "skip_defer_reasons": [
            {
                "source_id": "portland-building-code",
                "affected_source_ids": ["portland-building-code"],
                "affected_requirement_ids": ["REQ-BUILDING-CODE-FRESHNESS"],
                "reason": "awaiting reviewer confirmation",
                "citations": [{"label": "scheduler-rehearsal:portland-building-code"}],
            }
        ],
    }


def error_codes(packet: dict[str, object]) -> set[str]:
    result = validate_public_freshness_scheduler_rehearsal_v4_safety(packet)
    assert result["ok"] is False
    return {str(error["code"]) for error in result["errors"]}


class PublicFreshnessSchedulerRehearsalV4ValidationTest(unittest.TestCase):
    def test_accepts_minimal_safe_packet(self) -> None:
        packet = valid_packet()

        self.assertEqual(validate_public_freshness_scheduler_rehearsal_v4_safety(packet), {"ok": True, "errors": []})
        require_public_freshness_scheduler_rehearsal_v4_safety(packet)

    def test_require_raises_stable_error(self) -> None:
        packet = valid_packet()
        packet["cited_metadata_only_recrawl_schedule_candidates"][0]["citations"] = []

        with self.assertRaises(SchedulerRehearsalSafetyValidationError):
            require_public_freshness_scheduler_rehearsal_v4_safety(packet)

    def test_rejects_uncited_schedule_candidates(self) -> None:
        packet = valid_packet()
        packet["cited_metadata_only_recrawl_schedule_candidates"][0]["citations"] = []

        self.assertIn("missing_citations", error_codes(packet))

    def test_rejects_non_allowlisted_and_authenticated_urls(self) -> None:
        packet = valid_packet()
        outside = copy.deepcopy(packet["cited_metadata_only_recrawl_schedule_candidates"][0])
        outside["source_id"] = "outside-host"
        outside["metadata_fields"]["public_url"] = "https://example.com/ppd"
        auth = copy.deepcopy(packet["cited_metadata_only_recrawl_schedule_candidates"][0])
        auth["source_id"] = "authenticated-devhub"
        auth["metadata_fields"]["public_url"] = "https://devhub.portlandoregon.gov/account/my-permits"
        auth["requires_auth"] = True
        packet["cited_metadata_only_recrawl_schedule_candidates"] = [outside, auth]

        codes = error_codes(packet)

        self.assertIn("non_allowlisted_url", codes)
        self.assertIn("authenticated_url", codes)

    def test_rejects_missing_skip_defer_rationale(self) -> None:
        packet = valid_packet()
        packet["skip_defer_reasons"][0].pop("reason")

        self.assertIn("missing_skip_defer_rationale", error_codes(packet))

    def test_rejects_missing_affected_source_or_requirement_ids(self) -> None:
        packet = valid_packet()
        row = packet["cited_metadata_only_recrawl_schedule_candidates"][0]
        row["affected_source_ids"] = []
        row["affected_requirement_ids"] = []

        codes = error_codes(packet)

        self.assertIn("missing_affected_source", codes)
        self.assertIn("missing_affected_requirement", codes)

    def test_rejects_raw_body_download_archive_and_browser_artifacts(self) -> None:
        packet = valid_packet()
        row = packet["cited_metadata_only_recrawl_schedule_candidates"][0]
        row["raw_body"] = "raw public body must not be committed"
        row["artifact_refs"] = {"download_path": "ppd/tmp/file.pdf", "browser_trace": "trace.zip"}

        self.assertIn("raw_or_browser_artifact", error_codes(packet))

    def test_rejects_live_crawler_or_processor_completion_claims(self) -> None:
        packet = valid_packet()
        packet["cited_metadata_only_recrawl_schedule_candidates"][0]["claims"] = ["crawler_completed", "processor_completed"]

        self.assertIn("live_completion_claim", error_codes(packet))

    def test_rejects_legal_or_permitting_outcome_guarantees(self) -> None:
        packet = valid_packet()
        packet["cited_metadata_only_recrawl_schedule_candidates"][0]["claims"] = ["permit_guaranteed"]

        self.assertIn("outcome_guarantee", error_codes(packet))

    def test_rejects_active_state_and_model_mutation_flags(self) -> None:
        packet = valid_packet()
        packet["cited_metadata_only_recrawl_schedule_candidates"][0]["mutation_flags"] = {
            "active_source_mutation": True,
            "active_schedule_mutation": True,
            "active_requirement_mutation": True,
            "active_process_mutation": True,
            "active_guardrail_mutation": True,
            "active_prompt_mutation": True,
            "active_monitoring_mutation": True,
            "active_release_state_mutation": True,
            "active_agent_state_mutation": True,
        }

        self.assertIn("active_mutation_flag", error_codes(packet))


if __name__ == "__main__":
    unittest.main()
