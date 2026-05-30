from __future__ import annotations

import unittest
from copy import deepcopy
from pathlib import Path

from ppd.source_observation_refresh_candidate_v2 import (
    ATTESTATIONS,
    build_source_observation_refresh_candidate_v2,
    load_json,
    validate_source_observation_refresh_candidate_v2,
)


FIXTURES = Path(__file__).parent / "fixtures" / "source_observation_refresh_candidate_v2"


class SourceObservationRefreshCandidateV2Test(unittest.TestCase):
    def _valid_result(self) -> dict:
        return build_source_observation_refresh_candidate_v2(
            load_json(FIXTURES / "live_dry_run_acceptance_review_packet_v2.json"),
            load_json(FIXTURES / "public_recrawl_dry_run_evidence_envelope_v2.json"),
            load_json(FIXTURES / "source_freshness_drift_triage_v2.json"),
        )

    def test_builds_metadata_only_candidate_with_citations_and_guardrails(self) -> None:
        result = self._valid_result()

        self.assertEqual(result["schema_version"], "public_source_observation_refresh_candidate_v2")
        self.assertEqual(result["attestations"], ATTESTATIONS)
        self.assertEqual(result["affected_source_ids"], ["permit-center-fees"])
        self.assertEqual(len(result["candidates"]), 1)
        self.assertTrue(validate_source_observation_refresh_candidate_v2(result).ok)

        candidate = result["candidates"][0]
        self.assertEqual(candidate["source_id"], "permit-center-fees")
        self.assertEqual(candidate["affected_source_ids"], ["permit-center-fees"])
        self.assertEqual(candidate["reviewer_owner"], "ppd-fees-reviewer")
        self.assertTrue(candidate["metadata_only"])
        self.assertEqual(candidate["candidate_metadata"]["freshness_state"], "stale_metadata")
        self.assertEqual(candidate["candidate_metadata"]["evidence_count"], 1)
        self.assertEqual(
            {citation["packet"] for citation in candidate["citations"]},
            {"public_recrawl_dry_run_evidence_envelope_v2", "source_freshness_drift_triage_v2"},
        )

    def test_records_skip_and_defer_reasons(self) -> None:
        result = self._valid_result()

        skipped = {item["source_id"]: item["reason"] for item in result["skipped"] if item.get("source_id")}
        deferred = {item["source_id"]: item["reason"] for item in result["deferred"] if item.get("source_id")}

        self.assertEqual(skipped["legacy-zoning-cache"], "superseded_by_current_public_source")
        self.assertIn("building-code-summary", deferred)
        self.assertIn(deferred["building-code-summary"], {"needs_manual_publication_date_check", "publication_date_conflict"})

    def test_validator_rejects_uncited_source_observation(self) -> None:
        packet = self._valid_result()
        packet["candidates"][0]["citations"] = []
        result = validate_source_observation_refresh_candidate_v2(packet)
        self.assertFalse(result.ok)
        self.assertTrue(any("citations" in error for error in result.errors))

    def test_validator_rejects_non_allowlisted_or_authenticated_urls(self) -> None:
        packet = self._valid_result()
        packet["candidates"][0]["citations"] = [
            {"packet": "fixture", "source_id": "permit-center-fees", "url": "https://example.com/public"},
            {"packet": "fixture", "source_id": "permit-center-fees", "url": "https://user:secret@www.portland.gov/ppd"},
            {"packet": "fixture", "source_id": "permit-center-fees", "url": "https://www.portland.gov/ppd?token=secret"},
        ]
        result = validate_source_observation_refresh_candidate_v2(packet)
        self.assertFalse(result.ok)
        self.assertTrue(any("not allowlisted" in error for error in result.errors))
        self.assertTrue(any("authentication material" in error for error in result.errors))

    def test_validator_rejects_missing_skip_or_defer_rationale(self) -> None:
        packet = self._valid_result()
        packet["skipped"].append({"source_id": "unclear-source", "citation": {"packet": "fixture"}})
        packet["deferred"].append({"source_id": "later-source", "citation": {"packet": "fixture"}})
        result = validate_source_observation_refresh_candidate_v2(packet)
        self.assertFalse(result.ok)
        self.assertTrue(any("skipped" in error and "reason" in error for error in result.errors))
        self.assertTrue(any("deferred" in error and "reason" in error for error in result.errors))

    def test_validator_rejects_missing_affected_source_ids(self) -> None:
        packet = self._valid_result()
        packet["affected_source_ids"] = []
        packet["candidates"][0]["affected_source_ids"] = []
        result = validate_source_observation_refresh_candidate_v2(packet)
        self.assertFalse(result.ok)
        self.assertTrue(any("affected_source_ids" in error for error in result.errors))

    def test_validator_rejects_raw_download_archive_and_browser_artifacts(self) -> None:
        packet = self._valid_result()
        packet["raw_body"] = "raw"
        packet["candidates"][0]["download_path"] = "/tmp/source.pdf"
        packet["candidates"][0]["archive_url"] = "https://www.portland.gov/archive"
        packet["candidates"][0]["browser_artifacts"] = {"screenshot_path": "/tmp/page.png", "har_path": "/tmp/page.har"}
        result = validate_source_observation_refresh_candidate_v2(packet)
        self.assertFalse(result.ok)
        self.assertTrue(any("raw_body" in error for error in result.errors))
        self.assertTrue(any("download_path" in error for error in result.errors))
        self.assertTrue(any("archive_url" in error for error in result.errors))
        self.assertTrue(any("browser_artifacts" in error for error in result.errors))

    def test_validator_rejects_live_completion_and_outcome_claims(self) -> None:
        packet = self._valid_result()
        packet["candidates"][0]["note"] = "The live crawler completed, the processor completed, and permit approval is guaranteed."
        result = validate_source_observation_refresh_candidate_v2(packet)
        self.assertFalse(result.ok)
        self.assertTrue(any("prohibited live completion" in error for error in result.errors))

    def test_validator_rejects_active_mutation_flags(self) -> None:
        for flag in (
            "active_source_mutation",
            "schedule_mutation",
            "requirement_mutation",
            "process_mutation",
            "guardrail_mutation",
            "prompt_mutation",
            "monitoring_mutation",
            "release_state_mutation",
            "agent_state_mutation",
        ):
            packet = deepcopy(self._valid_result())
            packet["mutation_flags"] = {flag: True}
            result = validate_source_observation_refresh_candidate_v2(packet)
            self.assertFalse(result.ok)
            self.assertTrue(any(flag in error for error in result.errors))


if __name__ == "__main__":
    unittest.main()
