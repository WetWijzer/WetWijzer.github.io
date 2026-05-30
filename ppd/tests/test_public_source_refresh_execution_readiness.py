from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from ppd.crawler.public_source_refresh_execution_readiness import (
    PublicSourceRefreshExecutionReadinessError,
    require_public_source_refresh_execution_readiness_packet,
    validate_public_source_refresh_execution_readiness_packet,
)


FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "public_source_refresh_execution_readiness"
    / "readiness_packet.json"
)


def _fixture() -> dict[str, object]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _codes(packet: dict[str, object]) -> set[str]:
    return set(validate_public_source_refresh_execution_readiness_packet(packet))


class PublicSourceRefreshExecutionReadinessTests(unittest.TestCase):
    def test_accepts_fixture_first_metadata_only_readiness_packet(self) -> None:
        packet = _fixture()

        self.assertEqual(validate_public_source_refresh_execution_readiness_packet(packet), [])
        require_public_source_refresh_execution_readiness_packet(packet)

    def test_rejects_uncited_launch_gate_go_no_go_and_missing_consumed_packet_refs(self) -> None:
        packet = _fixture()
        packet["consumed_packet_refs"] = []
        launch_gates = packet["launch_gates"]
        decisions = packet["go_no_go_decisions"]
        assert isinstance(launch_gates, list)
        assert isinstance(decisions, list)
        launch_gates[0]["citation_refs"] = []
        decisions[0]["citation_refs"] = []

        codes = _codes(packet)
        self.assertIn("missing_consumed_packet_refs", codes)
        self.assertIn("uncited_launch_gate", codes)
        self.assertIn("uncited_go_no_go_decision", codes)
        with self.assertRaises(PublicSourceRefreshExecutionReadinessError):
            require_public_source_refresh_execution_readiness_packet(packet)

    def test_rejects_missing_prerequisites_abort_triggers_outputs_result_records_and_owners(self) -> None:
        packet = _fixture()
        packet["operator_prerequisites"] = []
        packet["abort_triggers"] = []
        packet["expected_metadata_only_outputs"] = []
        packet["expected_metadata_only_result_records"] = []
        packet["reviewer_owners"] = {"primary_reviewer": "", "execution_owner": ""}

        codes = _codes(packet)
        self.assertIn("missing_operator_prerequisites", codes)
        self.assertIn("missing_abort_triggers", codes)
        self.assertIn("missing_expected_metadata_only_outputs", codes)
        self.assertIn("missing_expected_metadata_only_result_records", codes)
        self.assertIn("missing_reviewer_owners", codes)

    def test_rejects_missing_allowlist_and_robots_evidence(self) -> None:
        packet = _fixture()
        sources = packet["source_scope"]
        assert isinstance(sources, list)
        sources[0]["allowlist_evidence_refs"] = []
        sources[0]["robots_evidence_refs"] = []

        codes = _codes(packet)
        self.assertIn("missing_allowlist_evidence", codes)
        self.assertIn("missing_robots_evidence", codes)

    def test_rejects_non_allowlisted_and_authenticated_urls(self) -> None:
        packet = _fixture()
        packet["source_scope"] = [
            {
                "source_id": "bad",
                "canonical_url": "https://example.com/ppd",
                "allowlist_evidence_refs": ["fixture://allowlist/bad"],
                "robots_evidence_refs": ["fixture://robots/bad"],
            },
            {
                "source_id": "auth",
                "canonical_url": "https://devhub.portlandoregon.gov/account/my-permits?token=abc",
                "allowlist_evidence_refs": ["fixture://allowlist/auth"],
                "robots_evidence_refs": ["fixture://robots/auth"],
            },
        ]

        codes = _codes(packet)
        self.assertIn("non_allowlisted_url", codes)
        self.assertIn("authenticated_url", codes)

    def test_rejects_live_fetch_download_or_processor_commands(self) -> None:
        packet = _fixture()
        packet["safe_operator_command"] = "python3 -m ppd.crawler.live_public_scrape --url https://www.portland.gov/ppd/devhub-faqs"

        self.assertIn(
            "command_string_fetches_downloads_or_processes_live_sources",
            _codes(packet),
        )

    def test_rejects_raw_artifacts_outcome_guarantees_and_all_active_mutation_flags(self) -> None:
        packet = _fixture()
        packet["archive_artifact_ref"] = "warc://public-refresh/devhub-faq.warc"
        packet["legal_note"] = "This packet guarantees issuance and the permit will be approved."
        packet["mutation_boundary"] = {
            "registry_update_enabled": "active",
            "activeScheduleMutation": True,
            "source_update_enabled": "apply",
            "requirement_update_enabled": "enabled",
            "guardrail_update_enabled": "mutate",
            "releaseStateUpdateEnabled": "live",
        }

        codes = _codes(packet)
        self.assertIn("raw_artifact_reference", codes)
        self.assertIn("legal_or_permitting_outcome_guarantee", codes)
        self.assertIn("active_state_mutation_flag", codes)

    def test_rejects_each_mutation_domain_independently(self) -> None:
        mutation_keys = [
            "registry_mutation_allowed",
            "schedule_mutation_allowed",
            "source_mutation_allowed",
            "requirement_mutation_allowed",
            "guardrail_mutation_allowed",
            "release_state_mutation_allowed",
        ]
        for key in mutation_keys:
            packet = copy.deepcopy(_fixture())
            packet[key] = True
            self.assertIn("active_state_mutation_flag", _codes(packet), key)


if __name__ == "__main__":
    unittest.main()
