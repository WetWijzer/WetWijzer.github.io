import json
import unittest
from pathlib import Path


FIXTURE = (
    Path(__file__).resolve().parent
    / "fixtures"
    / "agent_api_contract_v2"
    / "contract_packet_v2.json"
)


class AgentApiContractV2Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_packet_is_fixture_first_and_inactive(self):
        packet = self.packet
        self.assertEqual(packet["packet_version"], 2)
        self.assertEqual(packet["mode"], "fixture_first")
        self.assertEqual(packet["status"], "inactive_validation_only")
        scope = packet["scope"]
        self.assertEqual(scope["apis"], ["missing_information", "action_validation"])
        for key in (
            "uses_private_user_data",
            "opens_devhub",
            "performs_live_crawl",
            "changes_active_prompts",
            "changes_guardrails",
            "changes_devhub_surfaces",
            "changes_process_models",
            "changes_release_state",
        ):
            self.assertIs(scope[key], False, key)

    def test_contracts_cover_missing_information_and_action_validation(self):
        contracts = {item["api_name"]: item for item in self.packet["api_contracts"]}
        self.assertEqual(set(contracts), {"missing_information", "action_validation"})
        self.assertIn("needs_user_information", contracts["missing_information"]["response_schema"]["allowed_statuses"])
        self.assertIn("hold_stale_evidence", contracts["missing_information"]["response_schema"]["allowed_statuses"])
        self.assertIn("hold_conflicting_evidence", contracts["missing_information"]["response_schema"]["allowed_statuses"])
        self.assertIn("allow_reversible_preview_only", contracts["action_validation"]["response_schema"]["allowed_decisions"])
        self.assertIn("refuse_consequential_action", contracts["action_validation"]["response_schema"]["allowed_decisions"])

    def test_examples_cover_required_response_paths(self):
        cases = {example["case_type"] for example in self.packet["synthetic_examples"]}
        self.assertTrue(
            {
                "missing_information",
                "stale_evidence_response",
                "conflicting_evidence_response",
                "refused_consequential_action_response",
                "reversible_draft_preview_reference",
            }.issubset(cases)
        )

    def test_examples_have_request_and_response_citations(self):
        prefixes = tuple(self.packet["citation_requirements"]["allowed_citation_prefixes"])
        for example in self.packet["synthetic_examples"]:
            with self.subTest(example=example["example_id"]):
                request = example["request"]
                self.assertTrue(request["requirement_ids"])
                self.assertTrue(request["source_evidence_ids"])
                for citation in request["requirement_ids"] + request["source_evidence_ids"]:
                    self.assertTrue(citation.startswith(prefixes), citation)

                response_citations = _collect_response_citations(example["response"])
                self.assertGreaterEqual(
                    len(response_citations),
                    self.packet["citation_requirements"]["minimum_citations_per_response"],
                )
                for citation in response_citations:
                    self.assertTrue(citation.startswith(prefixes), citation)

    def test_stale_and_conflicting_examples_hold_instead_of_resolving(self):
        examples = {example["case_type"]: example for example in self.packet["synthetic_examples"]}
        self.assertEqual(
            examples["stale_evidence_response"]["response"]["status"],
            "hold_stale_evidence",
        )
        self.assertIn(
            "do not choose a winner automatically",
            examples["conflicting_evidence_response"]["response"]["answer"]["summary"],
        )
        self.assertEqual(
            examples["conflicting_evidence_response"]["response"]["status"],
            "hold_conflicting_evidence",
        )

    def test_refused_consequential_action_and_reversible_preview_boundaries(self):
        examples = {example["case_type"]: example for example in self.packet["synthetic_examples"]}
        refused = examples["refused_consequential_action_response"]["response"]["decision"]
        self.assertEqual(refused["outcome"], "refuse_consequential_action")
        self.assertIn("Refuse", refused["summary"])

        preview = examples["reversible_draft_preview_reference"]["response"]["decision"]
        self.assertEqual(preview["outcome"], "allow_reversible_preview_only")
        self.assertIn("fixture:preview:local-pdf-draft-preview", preview["citations"])
        for forbidden in ("payment", "scheduling", "release-state change"):
            self.assertIn(forbidden, preview["summary"])

    def test_no_active_mutation_or_prohibited_artifacts(self):
        for key, value in self.packet["mutation_flags"].items():
            self.assertIs(value, False, key)
        for key, value in self.packet["prohibited_artifacts"].items():
            self.assertEqual(value, [], key)

    def test_exact_offline_validation_commands_are_present(self):
        commands = self.packet["offline_validation_commands"]
        self.assertIn(
            ["python3", "-m", "unittest", "ppd.tests.test_agent_api_contract_v2"],
            commands,
        )
        self.assertIn(
            ["python3", "-m", "unittest", "discover", "-s", "ppd/tests", "-p", "test_*.py"],
            commands,
        )


def _collect_response_citations(response):
    citations = []
    answer = response.get("answer", {})
    citations.extend(answer.get("citations", []))
    decision = response.get("decision", {})
    citations.extend(decision.get("citations", []))
    for question in response.get("questions", []):
        citations.extend(question.get("citations", []))
    citations.extend(response.get("review_packet_refs", []))
    return citations


if __name__ == "__main__":
    unittest.main()
