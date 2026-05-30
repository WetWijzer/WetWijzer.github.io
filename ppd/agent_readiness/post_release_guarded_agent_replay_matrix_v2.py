"""Fixture-first guarded agent replay matrix v2 for inactive post-release plans.

This module is intentionally offline-only. It converts an inactive release
application dry-run plan v2 packet into deterministic synthetic replay scenarios
that reviewers can validate without live DevHub access or production prompt
changes.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence

SCHEMA_VERSION = "post_release_guarded_agent_replay_matrix_v2"
EXPECTED_INPUT_VERSION = "inactive_release_application_dry_run_plan_v2"

_EXPECTED_COMMANDS: tuple[tuple[str, ...], ...] = (
    ("python3", "-m", "py_compile", "ppd/agent_readiness/post_release_guarded_agent_replay_matrix_v2.py"),
    ("python3", "-m", "pytest", "ppd/tests/test_post_release_guarded_agent_replay_matrix_v2.py"),
    ("python3", "ppd/daemon/ppd_daemon.py", "--self-test"),
)

_REQUIRED_FALSE_FLAGS = (
    "active_prompt_changes",
    "production_contract_changes",
    "active_contract_changes",
    "active_guardrail_changes",
    "active_source_changes",
    "active_surface_changes",
    "active_release_state_changes",
    "devhub_surface_changes",
    "public_source_changes",
    "prompt_mutation",
    "contract_mutation",
    "guardrail_mutation",
    "source_mutation",
    "surface_mutation",
    "release_state_mutation",
)

_FORBIDDEN_FIELD_NAME_RE = re.compile(
    r"(auth[_-]?state|browser[_-]?(artifact|state)?|cookie|credential|download(ed)?|har|private|"
    r"raw[_-]?(artifact|body|capture|crawl|data|download|html|pdf)?|screenshot|"
    r"session[_-]?(artifact|state|storage)?|storage[_-]?state|token|trace)",
    re.IGNORECASE,
)

_UNSAFE_TEXT_RE = re.compile(
    r"(^file://)|(^/home/[^/]+/)|(^/Users/[^/]+/)|(^/tmp/)|"
    r"(auth[_ -]?state|browser[_ -]?state|cookie|credential|har\b|password|private[_ -]?(artifact|file|path|value)|"
    r"raw[_ -]?(artifact|body|capture|crawl|data|download|html|pdf)|downloaded[_ -]?(artifact|data|document|pdf)|"
    r"screenshot|session[_ -]?(artifact|state|storage)?|storage[_ -]?state|token|trace[_ -]?(file|zip)?)|"
    r"\b(live\s+(crawl|devhub|browser|execution|network|run)|crawl\s+live|opened\s+devhub|accessed\s+devhub|"
    r"devhub\s+(was\s+)?(opened|accessed|crawled)|crawl\s+(completed|ran)|"
    r"official\s+action\s+(performed|completed)|performed\s+official\s+action|"
    r"permit\s+will\s+be\s+(approved|issued)|approval\s+is\s+guaranteed|guaranteed\s+(approval|issuance|permit\s+outcome)|"
    r"legal\s+advice|legally\s+guaranteed|will\s+be\s+legal|"
    r"payment\s+(submitted|completed)|paid\s+the\s+fee|submitted\s+(the\s+)?permit|submit\s+the\s+permit\s+now|"
    r"scheduled\s+(the\s+)?inspection|cancelled\s+(the\s+)?inspection|certified\s+(the\s+)?application|uploaded\s+(the\s+)?corrections)\b",
    re.IGNORECASE,
)

_ACTIVE_MUTATION_NAME_RE = re.compile(
    r"(^|_)(active_)?(prompt|contract|guardrail|source|surface|release_state)_(mutation|mutating|update|change|write|enabled)(_|$)|"
    r"(^|_)(mutates|updates|changes|promotes|applies)_(prompt|contract|guardrail|source|surface|release_state)(_|$)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ReplayScenario:
    scenario_id: str
    order: int
    title: str
    synthetic_user_scenario: str
    expected_missing_fact_questions: List[str]
    expected_blocked_action_explanations: List[str]
    expected_reversible_draft_previews: List[Dict[str, Any]]
    citation_coverage_placeholders: List[Dict[str, str]]
    reviewer_acceptance_placeholders: List[Dict[str, str]]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scenario_id": self.scenario_id,
            "order": self.order,
            "title": self.title,
            "synthetic_user_scenario": self.synthetic_user_scenario,
            "expected_missing_fact_questions": list(self.expected_missing_fact_questions),
            "expected_blocked_action_explanations": list(self.expected_blocked_action_explanations),
            "expected_reversible_draft_previews": [dict(item) for item in self.expected_reversible_draft_previews],
            "citation_coverage_placeholders": [dict(item) for item in self.citation_coverage_placeholders],
            "reviewer_acceptance_placeholders": [dict(item) for item in self.reviewer_acceptance_placeholders],
        }


@dataclass(frozen=True)
class ReplayMatrixValidationIssue:
    code: str
    path: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "path": self.path, "message": self.message}


@dataclass(frozen=True)
class ReplayMatrixValidationResult:
    ok: bool
    issues: tuple[ReplayMatrixValidationIssue, ...]

    def as_dict(self) -> dict[str, Any]:
        return {"ok": self.ok, "issues": [issue.as_dict() for issue in self.issues]}


def load_inactive_release_application_dry_run_plan_v2(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        packet = json.load(handle)
    if not isinstance(packet, dict):
        raise ValueError("dry-run plan fixture must be a JSON object")
    return packet


def build_post_release_guarded_agent_replay_matrix_v2(packet: Mapping[str, Any]) -> Dict[str, Any]:
    _validate_packet(packet)
    plan_id = _required_string(packet, "plan_id")
    release_state = _required_string(packet, "release_state")
    workflows = _required_list(packet, "workflows")

    scenarios = [_scenario_from_workflow(plan_id, index + 1, workflow) for index, workflow in enumerate(workflows)]

    matrix = {
        "schema_version": SCHEMA_VERSION,
        "source_plan_id": plan_id,
        "source_plan_version": EXPECTED_INPUT_VERSION,
        "release_state": release_state,
        "mode": "fixture_first_offline_replay",
        "active_prompt_changes": False,
        "production_contract_changes": False,
        "active_contract_changes": False,
        "active_guardrail_changes": False,
        "active_source_changes": False,
        "active_surface_changes": False,
        "active_release_state_changes": False,
        "devhub_surface_changes": False,
        "public_source_changes": False,
        "scenarios": [scenario.to_dict() for scenario in scenarios],
        "offline_validation_commands": [list(command) for command in _EXPECTED_COMMANDS],
    }
    assert_valid_post_release_guarded_agent_replay_matrix_v2(matrix)
    return matrix


def validate_post_release_guarded_agent_replay_matrix_v2(matrix: Mapping[str, Any]) -> ReplayMatrixValidationResult:
    issues: list[ReplayMatrixValidationIssue] = []
    if matrix.get("schema_version") != SCHEMA_VERSION:
        issues.append(_issue("invalid_schema_version", "schema_version", f"schema_version must be {SCHEMA_VERSION}"))
    if matrix.get("source_plan_version") != EXPECTED_INPUT_VERSION:
        issues.append(_issue("invalid_source_plan_version", "source_plan_version", f"source_plan_version must be {EXPECTED_INPUT_VERSION}"))
    if matrix.get("release_state") != "inactive_post_release_dry_run":
        issues.append(_issue("invalid_release_state", "release_state", "release_state must remain inactive_post_release_dry_run"))
    if matrix.get("mode") != "fixture_first_offline_replay":
        issues.append(_issue("invalid_mode", "mode", "mode must be fixture_first_offline_replay"))
    for key in _REQUIRED_FALSE_FLAGS:
        if matrix.get(key, False) is not False:
            issues.append(_issue("active_mutation_flag", key, f"{key} must be false or absent"))
    _validate_scenarios(matrix.get("scenarios"), issues)
    _validate_validation_commands(matrix.get("offline_validation_commands"), issues)
    _scan_for_unsafe_content(matrix, "matrix", issues)
    return ReplayMatrixValidationResult(not issues, tuple(issues))


def assert_valid_post_release_guarded_agent_replay_matrix_v2(matrix: Mapping[str, Any]) -> None:
    result = validate_post_release_guarded_agent_replay_matrix_v2(matrix)
    if not result.ok:
        formatted = "; ".join(f"{issue.code} at {issue.path}" for issue in result.issues)
        raise ValueError(f"post-release guarded agent replay matrix v2 validation failed: {formatted}")


def matrix_json_from_fixture(path: Path) -> str:
    packet = load_inactive_release_application_dry_run_plan_v2(path)
    matrix = build_post_release_guarded_agent_replay_matrix_v2(packet)
    return json.dumps(matrix, indent=2, sort_keys=True)


def _scenario_from_workflow(plan_id: str, order: int, workflow: Any) -> ReplayScenario:
    if not isinstance(workflow, Mapping):
        raise ValueError("each workflow must be an object")

    workflow_id = _required_string(workflow, "workflow_id")
    title = _required_string(workflow, "title")
    user_goal = _required_string(workflow, "synthetic_user_goal")
    known_facts = _string_list(workflow.get("known_facts", []), "known_facts")
    missing_facts = _string_list(workflow.get("missing_facts", []), "missing_facts")
    blocked_actions = _required_list(workflow, "blocked_actions")
    reversible_drafts = _required_list(workflow, "reversible_drafts")
    source_evidence_ids = _string_list(workflow.get("source_evidence_ids", []), "source_evidence_ids")

    synthetic_user_scenario = _render_synthetic_user_scenario(user_goal, known_facts)
    expected_questions = [_missing_fact_question(fact) for fact in missing_facts]
    expected_blocked = [_blocked_action_explanation(action) for action in blocked_actions]
    expected_drafts = [_draft_preview(draft) for draft in reversible_drafts]
    citation_placeholders = [_citation_placeholder(evidence_id, workflow_id) for evidence_id in source_evidence_ids]
    reviewer_placeholders = _reviewer_placeholders(workflow_id)

    return ReplayScenario(
        scenario_id=f"{plan_id}:{workflow_id}",
        order=order,
        title=title,
        synthetic_user_scenario=synthetic_user_scenario,
        expected_missing_fact_questions=expected_questions,
        expected_blocked_action_explanations=expected_blocked,
        expected_reversible_draft_previews=expected_drafts,
        citation_coverage_placeholders=citation_placeholders,
        reviewer_acceptance_placeholders=reviewer_placeholders,
    )


def _render_synthetic_user_scenario(user_goal: str, known_facts: Sequence[str]) -> str:
    if not known_facts:
        return user_goal
    facts = "; ".join(known_facts)
    return f"{user_goal} Known facts supplied by the synthetic user: {facts}."


def _missing_fact_question(fact: str) -> str:
    return f"Please provide or confirm the missing fact before I draft or validate this step: {fact}."


def _blocked_action_explanation(action: Any) -> str:
    if not isinstance(action, Mapping):
        raise ValueError("blocked action entries must be objects")
    label = _required_string(action, "label")
    reason = _required_string(action, "reason")
    gate = _required_string(action, "required_gate")
    return f"I cannot perform '{label}' because {reason}. This requires {gate}."


def _draft_preview(draft: Any) -> Dict[str, Any]:
    if not isinstance(draft, Mapping):
        raise ValueError("reversible draft entries must be objects")
    draft_id = _required_string(draft, "draft_id")
    surface = _required_string(draft, "surface")
    fields = _required_list(draft, "fields")
    return {
        "draft_id": draft_id,
        "surface": surface,
        "preview_only": True,
        "requires_user_review_before_use": True,
        "fields": [_draft_field(field) for field in fields],
    }


def _draft_field(field: Any) -> Dict[str, str]:
    if not isinstance(field, Mapping):
        raise ValueError("draft fields must be objects")
    name = _required_string(field, "name")
    value_source = _required_string(field, "value_source")
    return {
        "name": name,
        "value_source": value_source,
        "preview_value": "",
    }


def _citation_placeholder(evidence_id: str, workflow_id: str) -> Dict[str, str]:
    return {
        "workflow_id": workflow_id,
        "source_evidence_id": evidence_id,
        "coverage_status": "placeholder_pending_reviewer_source_check",
    }


def _reviewer_placeholders(workflow_id: str) -> List[Dict[str, str]]:
    checks = [
        "missing_fact_questions_match_guardrails",
        "blocked_actions_stop_before_consequential_devhub_step",
        "reversible_drafts_are_preview_only",
        "citations_cover_each_material_requirement",
    ]
    return [
        {
            "workflow_id": workflow_id,
            "acceptance_check": check,
            "reviewer_status": "pending",
            "reviewer_notes": "",
        }
        for check in checks
    ]


def _validate_packet(packet: Mapping[str, Any]) -> None:
    version = _required_string(packet, "schema_version")
    if version != EXPECTED_INPUT_VERSION:
        raise ValueError(f"expected schema_version {EXPECTED_INPUT_VERSION!r}, got {version!r}")
    release_state = _required_string(packet, "release_state")
    if release_state != "inactive_post_release_dry_run":
        raise ValueError("replay matrix v2 only accepts inactive post-release dry-run plans")
    workflows = _required_list(packet, "workflows")
    if not workflows:
        raise ValueError("at least one workflow is required")


def _validate_scenarios(value: Any, issues: list[ReplayMatrixValidationIssue]) -> None:
    if not _non_empty_sequence(value):
        issues.append(_issue("missing_synthetic_user_scenarios", "scenarios", "at least one synthetic user scenario is required"))
        return
    expected_order = 1
    for index, scenario in enumerate(value):
        path = f"scenarios[{index}]"
        if not isinstance(scenario, Mapping):
            issues.append(_issue("invalid_synthetic_user_scenario", path, "scenario rows must be objects"))
            continue
        if scenario.get("order") != expected_order:
            issues.append(_issue("invalid_scenario_order", f"{path}.order", "scenario order must be contiguous from one"))
        expected_order += 1
        for key in ("scenario_id", "title", "synthetic_user_scenario"):
            if not _text(scenario.get(key)):
                issues.append(_issue("missing_synthetic_user_scenario", f"{path}.{key}", f"{key} is required"))
        _validate_string_list(scenario.get("expected_missing_fact_questions"), f"{path}.expected_missing_fact_questions", "missing_expected_missing_fact_questions", issues)
        _validate_string_list(scenario.get("expected_blocked_action_explanations"), f"{path}.expected_blocked_action_explanations", "missing_blocked_action_explanations", issues)
        _validate_draft_previews(scenario.get("expected_reversible_draft_previews"), f"{path}.expected_reversible_draft_previews", issues)
        _validate_citation_placeholders(scenario.get("citation_coverage_placeholders"), f"{path}.citation_coverage_placeholders", issues)
        _validate_reviewer_placeholders(scenario.get("reviewer_acceptance_placeholders"), f"{path}.reviewer_acceptance_placeholders", issues)


def _validate_string_list(value: Any, path: str, code: str, issues: list[ReplayMatrixValidationIssue]) -> None:
    if not _string_items(value):
        issues.append(_issue(code, path, "non-empty string entries are required"))


def _validate_draft_previews(value: Any, path: str, issues: list[ReplayMatrixValidationIssue]) -> None:
    if not _non_empty_sequence(value):
        issues.append(_issue("missing_reversible_draft_previews", path, "reversible draft previews are required"))
        return
    for index, preview in enumerate(value):
        row_path = f"{path}[{index}]"
        if not isinstance(preview, Mapping):
            issues.append(_issue("invalid_reversible_draft_preview", row_path, "draft previews must be objects"))
            continue
        if not _text(preview.get("draft_id")):
            issues.append(_issue("missing_reversible_draft_preview_id", f"{row_path}.draft_id", "draft_id is required"))
        if preview.get("preview_only") is not True:
            issues.append(_issue("draft_preview_not_preview_only", f"{row_path}.preview_only", "draft previews must be preview_only"))
        if preview.get("requires_user_review_before_use") is not True:
            issues.append(_issue("draft_preview_missing_user_review", f"{row_path}.requires_user_review_before_use", "draft previews must require user review"))
        if not _non_empty_sequence(preview.get("fields")):
            issues.append(_issue("missing_reversible_draft_preview_fields", f"{row_path}.fields", "draft preview fields are required"))


def _validate_citation_placeholders(value: Any, path: str, issues: list[ReplayMatrixValidationIssue]) -> None:
    if not _non_empty_sequence(value):
        issues.append(_issue("missing_citation_coverage_placeholders", path, "citation coverage placeholders are required"))
        return
    for index, row in enumerate(value):
        row_path = f"{path}[{index}]"
        if not isinstance(row, Mapping):
            issues.append(_issue("invalid_citation_coverage_placeholder", row_path, "citation placeholders must be objects"))
            continue
        if not _text(row.get("workflow_id")) or not _text(row.get("source_evidence_id")):
            issues.append(_issue("invalid_citation_coverage_placeholder", row_path, "workflow_id and source_evidence_id are required"))
        if row.get("coverage_status") != "placeholder_pending_reviewer_source_check":
            issues.append(_issue("invalid_citation_coverage_status", f"{row_path}.coverage_status", "coverage status must remain a reviewer placeholder"))


def _validate_reviewer_placeholders(value: Any, path: str, issues: list[ReplayMatrixValidationIssue]) -> None:
    if not _non_empty_sequence(value):
        issues.append(_issue("missing_reviewer_acceptance_placeholders", path, "reviewer acceptance placeholders are required"))
        return
    for index, row in enumerate(value):
        row_path = f"{path}[{index}]"
        if not isinstance(row, Mapping):
            issues.append(_issue("invalid_reviewer_acceptance_placeholder", row_path, "reviewer placeholders must be objects"))
            continue
        if not _text(row.get("workflow_id")) or not _text(row.get("acceptance_check")):
            issues.append(_issue("invalid_reviewer_acceptance_placeholder", row_path, "workflow_id and acceptance_check are required"))
        if row.get("reviewer_status") != "pending":
            issues.append(_issue("invalid_reviewer_acceptance_status", f"{row_path}.reviewer_status", "reviewer status must remain pending"))


def _validate_validation_commands(value: Any, issues: list[ReplayMatrixValidationIssue]) -> None:
    if not _non_empty_sequence(value):
        issues.append(_issue("missing_validation_commands", "offline_validation_commands", "offline validation commands are required"))
        return
    commands: list[tuple[str, ...]] = []
    for index, command in enumerate(value):
        path = f"offline_validation_commands[{index}]"
        if not _string_sequence(command):
            issues.append(_issue("invalid_validation_command", path, "validation commands must be argv string lists"))
            continue
        commands.append(tuple(command))
    if tuple(commands) != _EXPECTED_COMMANDS:
        issues.append(_issue("unexpected_validation_commands", "offline_validation_commands", "validation commands must match the exact offline command set"))


def _scan_for_unsafe_content(value: Any, path: str, issues: list[ReplayMatrixValidationIssue]) -> None:
    for child_path, child in _walk(value, path):
        name = _path_name(child_path).lower().replace("-", "_")
        if name in _REQUIRED_FALSE_FLAGS and child is not False:
            issues.append(_issue("active_mutation_flag", child_path, "active prompt, contract, guardrail, source, surface, or release-state mutation flags must be false"))
        if _ACTIVE_MUTATION_NAME_RE.search(name) and _active_flag(child):
            issues.append(_issue("active_mutation_flag", child_path, "active prompt, contract, guardrail, source, surface, or release-state mutation flags are not allowed"))
        if name and not name.startswith("no_") and _FORBIDDEN_FIELD_NAME_RE.search(name) and _present_value(child):
            issues.append(_issue("private_or_raw_artifact_field", child_path, "matrix fields must not carry private, session, browser, raw, or downloaded artifacts"))
        if isinstance(child, str) and _UNSAFE_TEXT_RE.search(child):
            issues.append(_issue("unsafe_matrix_text", child_path, "matrix text must not reference private artifacts, live DevHub/crawl claims, legal/permitting guarantees, consequential official actions, or active mutation"))


def _required_string(source: Mapping[str, Any], key: str) -> str:
    value = source.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a non-empty string")
    return value


def _required_list(source: Mapping[str, Any], key: str) -> List[Any]:
    value = source.get(key)
    if not isinstance(value, list):
        raise ValueError(f"{key} must be a list")
    return list(value)


def _string_list(value: Any, key: str) -> List[str]:
    if not isinstance(value, list):
        raise ValueError(f"{key} must be a list")
    strings: List[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise ValueError(f"{key} entries must be non-empty strings")
        strings.append(item)
    return strings


def _walk(value: Any, path: str) -> Iterable[tuple[str, Any]]:
    yield path, value
    if isinstance(value, Mapping):
        for key, child in value.items():
            yield from _walk(child, f"{path}.{key}")
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            yield from _walk(child, f"{path}[{index}]")


def _non_empty_sequence(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)) and bool(value)


def _string_sequence(value: Any) -> bool:
    return _non_empty_sequence(value) and all(isinstance(item, str) and item.strip() for item in value)


def _string_items(value: Any) -> list[str]:
    if not _non_empty_sequence(value):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


def _path_name(path: str) -> str:
    return path.rsplit(".", 1)[-1].split("[", 1)[0]


def _active_flag(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"1", "active", "enabled", "true", "yes", "mutate", "mutation"}
    if isinstance(value, Mapping):
        return bool(value)
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return bool(value)
    return False


def _present_value(value: Any) -> bool:
    if value is None or value is False:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, Mapping):
        return bool(value)
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return bool(value)
    return True


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _issue(code: str, path: str, message: str) -> ReplayMatrixValidationIssue:
    return ReplayMatrixValidationIssue(code=code, path=path, message=message)


__all__ = [
    "EXPECTED_INPUT_VERSION",
    "SCHEMA_VERSION",
    "ReplayMatrixValidationIssue",
    "ReplayMatrixValidationResult",
    "ReplayScenario",
    "assert_valid_post_release_guarded_agent_replay_matrix_v2",
    "build_post_release_guarded_agent_replay_matrix_v2",
    "load_inactive_release_application_dry_run_plan_v2",
    "matrix_json_from_fixture",
    "validate_post_release_guarded_agent_replay_matrix_v2",
]
