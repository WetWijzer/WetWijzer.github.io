from pathlib import Path
import copy
import unittest

from ppd.logic.requirement_process_coverage_matrix import (
    load_json_file,
    validate_coverage_matrix,
    validate_coverage_matrix_file,
)


FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "requirement_process_coverage_matrix"
    / "synthetic_permit_workflow_matrix.json"
)


class RequirementProcessCoverageMatrixTest(unittest.TestCase):
    def test_synthetic_workflow_matrix_covers_process_model_guardrail_inputs(self):
        report = validate_coverage_matrix_file(FIXTURE_PATH)

        self.assertTrue(report.passed)
        self.assertEqual("synthetic-alteration-devhub-draft-v1", report.workflow_id)
        self.assertEqual(6, report.checked_requirement_count)
        self.assertEqual(6, report.checked_matrix_row_count)
        self.assertEqual([], report.to_dict()["issues"])

    def test_matrix_rejects_missing_stage_link(self):
        fixture = load_json_file(FIXTURE_PATH)
        mutated = copy.deepcopy(fixture)
        mutated["coverage_matrix"][0]["stage_ids"] = []

        issues = validate_coverage_matrix(mutated).to_dict()["issues"]

        self.assertIn("missing_stage_link", {issue["issue_type"] for issue in issues})

    def test_matrix_rejects_evidence_not_present_on_requirement_node(self):
        fixture = load_json_file(FIXTURE_PATH)
        mutated = copy.deepcopy(fixture)
        mutated["coverage_matrix"][1]["evidence_ids"] = ["EVIDENCE-NOT-ON-REQ"]

        issues = validate_coverage_matrix(mutated).to_dict()["issues"]

        self.assertIn("unknown_row_evidence", {issue["issue_type"] for issue in issues})

    def test_matrix_rejects_unknown_process_model_reference(self):
        fixture = load_json_file(FIXTURE_PATH)
        mutated = copy.deepcopy(fixture)
        mutated["coverage_matrix"][2]["file_rule_ids"] = ["missing-file-rule"]

        issues = validate_coverage_matrix(mutated).to_dict()["issues"]

        self.assertIn("unknown_process_model_reference", {issue["issue_type"] for issue in issues})

    def test_matrix_rejects_uncited_requirement(self):
        fixture = load_json_file(FIXTURE_PATH)
        mutated = copy.deepcopy(fixture)
        mutated["requirement_nodes"][0]["source_evidence_ids"] = []

        issues = validate_coverage_matrix(mutated).to_dict()["issues"]

        self.assertIn("uncited_requirement", {issue["issue_type"] for issue in issues})

    def test_matrix_rejects_orphan_process_stage(self):
        fixture = load_json_file(FIXTURE_PATH)
        mutated = copy.deepcopy(fixture)
        mutated["process_model"]["stages"].append({"id": "stage-orphan", "name": "orphan stage"})

        issues = validate_coverage_matrix(mutated).to_dict()["issues"]

        self.assertIn("orphan_process_stage", {issue["issue_type"] for issue in issues})

    def test_matrix_rejects_low_confidence_requirement_without_human_review(self):
        fixture = load_json_file(FIXTURE_PATH)
        mutated = copy.deepcopy(fixture)
        mutated["requirement_nodes"][0]["confidence"] = 0.42
        mutated["requirement_nodes"][0]["human_review_status"] = "machine_only"

        issues = validate_coverage_matrix(mutated).to_dict()["issues"]

        self.assertIn("low_confidence_without_human_review", {issue["issue_type"] for issue in issues})

    def test_matrix_rejects_missing_unsupported_path_handling(self):
        fixture = load_json_file(FIXTURE_PATH)
        mutated = copy.deepcopy(fixture)
        mutated["coverage_matrix"][5]["unsupported_path_ids"] = []
        mutated["coverage_matrix"][3]["unsupported_path_ids"] = []

        issues = validate_coverage_matrix(mutated).to_dict()["issues"]

        self.assertIn("missing_unsupported_path_handling", {issue["issue_type"] for issue in issues})

    def test_matrix_rejects_consequential_stage_without_action_gate(self):
        fixture = load_json_file(FIXTURE_PATH)
        mutated = copy.deepcopy(fixture)
        for row in mutated["coverage_matrix"]:
            if "stage-submission" in row["stage_ids"]:
                row["action_gate_ids"] = []

        issues = validate_coverage_matrix(mutated).to_dict()["issues"]

        self.assertIn("consequential_stage_without_action_gate", {issue["issue_type"] for issue in issues})


if __name__ == "__main__":
    unittest.main()
