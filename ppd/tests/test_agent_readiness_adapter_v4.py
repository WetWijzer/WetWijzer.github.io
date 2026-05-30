from __future__ import annotations

import unittest
from pathlib import Path

from ppd.agent_readiness_adapter_v4 import (
    ADAPTER_VERSION,
    build_offline_agent_readiness_examples,
    evaluate_offline_agent_readiness,
)
from ppd.agent_readiness_expectation_packet_v4 import build_expectation_packet


FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "agent_readiness_packet_v4"
BASE_REQUEST = {
    "workflow_id": "fixture-workflow",
    "agent_goal": "Prepare readiness output from fixtures.",
    "requested_action": "continue_safely",
    "evidence_refs": [
        "agent-facing-readiness-contract-coverage-packet-v3",
        "process-model-fixtures-v1",
        "user-gap-analysis-fixtures-v1",
        "guardrail-bundle-fixtures-v1",
    ],
}


class OfflineAgentReadinessAdapterV4Test(unittest.TestCase):
    def setUp(self) -> None:
        self.packet = build_expectation_packet(FIXTURE_ROOT)
        self.consumed_refs = set(self.packet["consumes"].values())

    def test_builds_all_fixture_backed_outputs(self) -> None:
        examples = build_offline_agent_readiness_examples(FIXTURE_ROOT)

        self.assertEqual(
            set(examples),
            {
                "missing_information_prompt",
                "stale_or_conflicting_evidence_notice",
                "reversible_draft_preview",
                "blocked_action_explanation",
                "next_safe_read_only_action",
            },
        )
        for kind, response in examples.items():
            with self.subTest(kind=kind):
                self.assertEqual(response["example_kind"], kind)
                self.assertTrue(response["citations"])
                self.assertTrue(set(response["citations"]).issubset(self.consumed_refs))
                self.assertTrue(set(response["process_refs"]).issubset(self.consumed_refs))
                self.assertTrue(set(response["gap_refs"]).issubset(self.consumed_refs))
                self.assertTrue(set(response["guardrail_refs"]).issubset(self.consumed_refs))

    def test_routes_missing_fact_requests_to_cited_prompt(self) -> None:
        response = evaluate_offline_agent_readiness(
            {
                **BASE_REQUEST,
                "requested_action": "collect_missing_facts",
                "missing_facts": ["permit address", "applicant role"],
            },
            FIXTURE_ROOT,
        )

        self.assert_cited_fail_closed(response, "missing_information_prompt")
        self.assertIn("ask_missing_information", response["safe_next_action_classes"])
        self.assertEqual(response["adapter"]["adapter_version"], ADAPTER_VERSION)

    def test_routes_stale_conflicting_or_unknown_evidence_to_notice(self) -> None:
        requests = [
            {**BASE_REQUEST, "requested_action": "summarize_evidence_status"},
            {**BASE_REQUEST, "requested_action": "continue_safely", "evidence_status": "stale"},
            {**BASE_REQUEST, "requested_action": "continue_safely", "conflicting_evidence": ["fixture conflict"]},
            {**BASE_REQUEST, "requested_action": "continue_safely", "evidence_refs": ["unknown-fixture-ref"]},
        ]

        for request in requests:
            with self.subTest(request=request):
                response = evaluate_offline_agent_readiness(request, FIXTURE_ROOT)
                self.assert_cited_fail_closed(response, "stale_or_conflicting_evidence_notice")
                self.assertIn("surface_conflict", response["safe_next_action_classes"])

    def test_routes_reversible_preview_requests_to_local_preview(self) -> None:
        response = evaluate_offline_agent_readiness(
            {**BASE_REQUEST, "requested_action": "preview_draft_only"},
            FIXTURE_ROOT,
        )

        self.assertTrue(response["ready"])
        self.assertEqual(response["example_kind"], "reversible_draft_preview")
        self.assertIn("draft_local_preview", response["safe_next_action_classes"])
        self.assertIn("guardrail_refs", response)

    def test_blocks_official_actions_without_echoing_request_values(self) -> None:
        response = evaluate_offline_agent_readiness(
            {
                **BASE_REQUEST,
                "requested_action": "submit_application",
                "private_user_fact": "do not echo this applicant value",
                "document_path": "/home/example/private-upload.pdf",
            },
            FIXTURE_ROOT,
        )

        serialized = repr(response)
        self.assert_cited_fail_closed(response, "blocked_action_explanation")
        self.assertIn("explain_block", response["safe_next_action_classes"])
        self.assertNotIn("do not echo", serialized)
        self.assertNotIn("private-upload", serialized)

    def test_default_and_next_safe_requests_require_cited_evidence(self) -> None:
        for request in ({}, {**BASE_REQUEST, "requested_action": "continue_safely"}, {**BASE_REQUEST, "requested_action": "read_only_summary"}):
            with self.subTest(request=request):
                response = evaluate_offline_agent_readiness(request, FIXTURE_ROOT)
                if request:
                    self.assertTrue(response["ready"])
                    self.assertEqual(response["example_kind"], "next_safe_read_only_action")
                    self.assertIn("read_only_summary", response["safe_next_action_classes"])
                else:
                    self.assert_cited_fail_closed(response, "missing_information_prompt")
                self.assertTrue(response["adapter"]["attestations"]["no_live_llm"])
                self.assertTrue(response["adapter"]["attestations"]["no_devhub"])
                self.assertTrue(response["adapter"]["attestations"]["no_user_data"])
                self.assertTrue(response["adapter"]["attestations"]["no_official_action"])

    def test_fails_closed_on_missing_citations_unsupported_processes_and_missing_required_facts(self) -> None:
        cases = [
            ({**BASE_REQUEST, "evidence_refs": []}, "missing_information_prompt"),
            ({**BASE_REQUEST, "process_id": "unsupported-process"}, "blocked_action_explanation"),
            ({**BASE_REQUEST, "required_user_facts": ["permit_address"], "user_facts": {}}, "missing_information_prompt"),
        ]

        for request, kind in cases:
            with self.subTest(kind=kind, request=request):
                response = evaluate_offline_agent_readiness(request, FIXTURE_ROOT)
                self.assert_cited_fail_closed(response, kind)

    def test_fails_closed_on_private_raw_guarantee_final_or_mutating_inputs(self) -> None:
        cases = [
            {**BASE_REQUEST, "private_user_fact": "123 Main"},
            {**BASE_REQUEST, "authenticated_devhub_value": "account scoped"},
            {**BASE_REQUEST, "raw_html": "private session"},
            {**BASE_REQUEST, "agent_goal": "Guarantee the permit will be approved."},
            {**BASE_REQUEST, "agent_goal": "I submitted the application."},
            {**BASE_REQUEST, "mutate_prompt": True},
            {**BASE_REQUEST, "agent_goal": "Patch the source registry for this release."},
            {**BASE_REQUEST, "next_action_class": "submit_application"},
        ]

        for request in cases:
            with self.subTest(request=request):
                response = evaluate_offline_agent_readiness(request, FIXTURE_ROOT)
                self.assert_cited_fail_closed(response, "blocked_action_explanation")

    def assert_cited_fail_closed(self, response: dict[str, object], kind: str) -> None:
        self.assertFalse(response["ready"])
        self.assertEqual(response["example_kind"], kind)
        self.assertTrue(response["citations"])
        self.assertTrue(set(response["citations"]).issubset(self.consumed_refs))
        self.assertTrue(response["process_refs"])
        self.assertTrue(response["gap_refs"])
        self.assertTrue(response["guardrail_refs"])


if __name__ == "__main__":
    unittest.main()
