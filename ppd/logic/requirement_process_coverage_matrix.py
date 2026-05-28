"""Fixture-first requirement-to-process coverage matrix validation.

This module validates committed synthetic fixtures only. It does not crawl,
log in, upload, submit, pay fees, or touch private DevHub artifacts.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


LOW_CONFIDENCE_THRESHOLD = 0.8

HUMAN_REVIEWED_STATUSES = frozenset(
    {
        "approved",
        "human_reviewed",
        "reviewed",
        "source_reviewed",
        "synthetic_fixture_reviewed",
    }
)

CONSEQUENTIAL_STAGE_TERMS = frozenset(
    {
        "acknowledgement",
        "certification",
        "submission",
        "submit",
        "upload",
        "payment",
        "pay",
        "schedule",
        "cancel",
        "issuance",
    }
)

TARGET_COLUMNS = (
    "required_fact_ids",
    "required_document_ids",
    "file_rule_ids",
    "fee_trigger_ids",
    "exception_ids",
    "unsupported_path_ids",
    "action_gate_ids",
)

PROCESS_MODEL_COLLECTIONS = {
    "stage_ids": "stages",
    "required_fact_ids": "required_facts",
    "required_document_ids": "required_documents",
    "file_rule_ids": "file_rules",
    "fee_trigger_ids": "fee_triggers",
    "exception_ids": "exceptions",
    "unsupported_path_ids": "unsupported_paths",
    "action_gate_ids": "action_gates",
}


@dataclass(frozen=True, order=True)
class CoverageMatrixIssue:
    issue_type: str
    requirement_id: str
    field: str
    value: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {
            "issue_type": self.issue_type,
            "requirement_id": self.requirement_id,
            "field": self.field,
            "value": self.value,
            "message": self.message,
        }


@dataclass(frozen=True)
class CoverageMatrixReport:
    fixture_id: str
    workflow_id: str
    checked_requirement_count: int
    checked_matrix_row_count: int
    issues: tuple[CoverageMatrixIssue, ...]

    @property
    def passed(self) -> bool:
        return not self.issues

    def to_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "fixture_id": self.fixture_id,
            "workflow_id": self.workflow_id,
            "checked_requirement_count": self.checked_requirement_count,
            "checked_matrix_row_count": self.checked_matrix_row_count,
            "issues": [issue.to_dict() for issue in self.issues],
        }


def load_json_file(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"expected top-level JSON object in {path}")
    return value


def validate_coverage_matrix_file(path: Path) -> CoverageMatrixReport:
    return validate_coverage_matrix(load_json_file(path))


def validate_coverage_matrix(fixture: Mapping[str, Any]) -> CoverageMatrixReport:
    fixture_id = _text(fixture.get("fixture_id"))
    workflow_id = _text(fixture.get("workflow_id"))
    requirements = _as_sequence(fixture.get("requirement_nodes"), "requirement_nodes")
    process_model = _as_mapping(fixture.get("process_model"), "process_model")
    rows = _as_sequence(fixture.get("coverage_matrix"), "coverage_matrix")

    issues: list[CoverageMatrixIssue] = []
    requirement_index = _index_by_id(requirements, "requirement_id")
    row_index = _index_by_id(rows, "requirement_id")
    model_ids = {
        column: _ids_from_collection(process_model.get(collection))
        for column, collection in PROCESS_MODEL_COLLECTIONS.items()
    }
    consequential_stage_ids = _consequential_stage_ids(process_model.get("stages"))

    if not fixture_id:
        issues.append(_issue("missing_fixture_id", "", "fixture_id", "", "Fixture id is required."))
    if not workflow_id:
        issues.append(_issue("missing_workflow_id", "", "workflow_id", "", "Workflow id is required."))
    if not requirements:
        issues.append(_issue("missing_requirements", "", "requirement_nodes", "", "At least one RequirementNode is required."))
    if not rows:
        issues.append(_issue("missing_matrix", "", "coverage_matrix", "", "At least one coverage matrix row is required."))

    for requirement_id, requirement in requirement_index.items():
        evidence_ids = _string_set(requirement.get("source_evidence_ids"))
        if not evidence_ids:
            issues.append(_issue("uncited_requirement", requirement_id, "source_evidence_ids", "", "RequirementNode must cite source evidence before coverage can be accepted."))
        if _is_low_confidence_without_review(requirement):
            issues.append(_issue("low_confidence_without_human_review", requirement_id, "human_review_status", _text(requirement.get("human_review_status")), "Low-confidence requirements must carry a human-reviewed status."))
        if requirement_id not in row_index:
            issues.append(_issue("missing_matrix_row", requirement_id, "coverage_matrix", "", "RequirementNode has no coverage matrix row."))

    for requirement_id in row_index:
        if requirement_id not in requirement_index:
            issues.append(_issue("unknown_requirement", requirement_id, "requirement_id", requirement_id, "Coverage row references an unknown RequirementNode."))

    covered_stage_ids: set[str] = set()
    action_gated_stage_ids: set[str] = set()
    unsupported_path_rows = 0

    for row in rows:
        requirement_id = _text(row.get("requirement_id"))
        requirement = requirement_index.get(requirement_id, {})
        requirement_evidence_ids = _string_set(requirement.get("source_evidence_ids"))
        row_evidence_ids = _string_set(row.get("evidence_ids"))
        stage_ids = _string_set(row.get("stage_ids"))
        row_action_gate_ids = _string_set(row.get("action_gate_ids"))
        row_unsupported_path_ids = _string_set(row.get("unsupported_path_ids"))

        covered_stage_ids.update(stage_ids)
        if row_action_gate_ids:
            action_gated_stage_ids.update(stage_ids)
        if row_unsupported_path_ids:
            unsupported_path_rows += 1

        if not row_evidence_ids:
            issues.append(_issue("missing_row_evidence", requirement_id, "evidence_ids", "", "Coverage row must link at least one evidence id."))
        for evidence_id in sorted(row_evidence_ids):
            if evidence_id not in requirement_evidence_ids:
                issues.append(_issue("unknown_row_evidence", requirement_id, "evidence_ids", evidence_id, "Coverage row evidence must be present on the RequirementNode."))

        if not stage_ids:
            issues.append(_issue("missing_stage_link", requirement_id, "stage_ids", "", "Coverage row must link the requirement to at least one process stage."))

        for column, known_ids in model_ids.items():
            for value in sorted(_string_set(row.get(column))):
                if value not in known_ids:
                    issues.append(_issue("unknown_process_model_reference", requirement_id, column, value, "Coverage row references an id not present in the ProcessModel."))

        if _requires_unsupported_path(requirement, stage_ids, consequential_stage_ids) and not row_unsupported_path_ids:
            issues.append(_issue("missing_unsupported_path_handling", requirement_id, "unsupported_path_ids", "", "Consequential or refusal-oriented requirements must map to unsupported-path handling."))

    for stage_id in sorted(model_ids["stage_ids"] - covered_stage_ids):
        issues.append(_issue("orphan_process_stage", "", "stage_ids", stage_id, "ProcessModel stage is not covered by any requirement matrix row."))

    for stage_id in sorted(consequential_stage_ids - action_gated_stage_ids):
        issues.append(_issue("consequential_stage_without_action_gate", "", "action_gate_ids", stage_id, "Consequential process stages must have action-gate coverage."))

    if model_ids["unsupported_path_ids"] and unsupported_path_rows == 0:
        issues.append(_issue("missing_unsupported_path_handling", "", "unsupported_path_ids", "", "ProcessModel defines unsupported paths but no coverage row handles them."))
    if not model_ids["unsupported_path_ids"]:
        issues.append(_issue("missing_unsupported_path_handling", "", "unsupported_path_ids", "", "ProcessModel must define unsupported-path handling."))

    for column in TARGET_COLUMNS:
        if not any(_string_set(row.get(column)) for row in rows):
            issues.append(_issue("missing_required_coverage_column", "", column, "", "Synthetic workflow matrix must exercise this coverage column."))

    return CoverageMatrixReport(
        fixture_id=fixture_id,
        workflow_id=workflow_id,
        checked_requirement_count=len(requirements),
        checked_matrix_row_count=len(rows),
        issues=tuple(sorted(issues)),
    )


def _index_by_id(records: Sequence[Mapping[str, Any]], key: str) -> dict[str, Mapping[str, Any]]:
    indexed: dict[str, Mapping[str, Any]] = {}
    for record in records:
        record_id = _text(record.get(key))
        if record_id:
            indexed[record_id] = record
    return indexed


def _ids_from_collection(value: Any) -> set[str]:
    return {_text(item.get("id")) for item in _as_sequence(value, "collection") if _text(item.get("id"))}


def _string_set(value: Any) -> set[str]:
    if value is None:
        return set()
    if not isinstance(value, list):
        return set()
    return {_text(item) for item in value if _text(item)}


def _as_sequence(value: Any, name: str) -> tuple[Mapping[str, Any], ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise ValueError(f"{name} must be a list")
    records: list[Mapping[str, Any]] = []
    for item in value:
        if not isinstance(item, Mapping):
            raise ValueError(f"{name} entries must be objects")
        records.append(item)
    return tuple(records)


def _as_mapping(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{name} must be an object")
    return value


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError:
            return None
    return None


def _is_low_confidence_without_review(requirement: Mapping[str, Any]) -> bool:
    confidence = _number(requirement.get("confidence"))
    if confidence is None or confidence >= LOW_CONFIDENCE_THRESHOLD:
        return False
    return _text(requirement.get("human_review_status")) not in HUMAN_REVIEWED_STATUSES


def _consequential_stage_ids(stages: Any) -> set[str]:
    ids: set[str] = set()
    for stage in _as_sequence(stages, "stages"):
        stage_id = _text(stage.get("id"))
        if not stage_id:
            continue
        if stage.get("consequential") is True:
            ids.add(stage_id)
            continue
        searchable = " ".join([stage_id, _text(stage.get("name")), _text(stage.get("label"))]).lower()
        if any(term in searchable for term in CONSEQUENTIAL_STAGE_TERMS):
            ids.add(stage_id)
    return ids


def _requires_unsupported_path(requirement: Mapping[str, Any], stage_ids: set[str], consequential_stage_ids: set[str]) -> bool:
    requirement_type = _text(requirement.get("requirement_type"))
    action = _text(requirement.get("action")).lower()
    if requirement_type in {"action_gate", "prohibition"}:
        return True
    if "refuse" in action or "do not automate" in action:
        return True
    return bool(stage_ids & consequential_stage_ids)


def _issue(issue_type: str, requirement_id: str, field: str, value: str, message: str) -> CoverageMatrixIssue:
    return CoverageMatrixIssue(
        issue_type=issue_type,
        requirement_id=requirement_id,
        field=field,
        value=value,
        message=message,
    )
