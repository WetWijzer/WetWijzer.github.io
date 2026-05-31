"""Fail-closed validation for guardrail recompile dry-run plan v2."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from ppd.guardrail_recompile_dry_run_plan_v2 import OFFLINE_VALIDATION_COMMANDS, PLAN_VERSION, REQUIRED_ROW_KEYS

_REQUIRED_PLACEHOLDER_LISTS = {
    "deterministic_predicate_impact_placeholders": "missing_deterministic_predicate_impact_placeholders",
    "deontic_rule_placeholders": "missing_deontic_rule_placeholders",
    "temporal_rule_placeholders": "missing_temporal_rule_placeholders",
    "reversible_action_predicate_placeholders": "missing_reversible_action_predicate_placeholders",
    "exact_confirmation_predicate_placeholders": "missing_exact_confirmation_predicate_placeholders",
    "refused_action_predicate_placeholders": "missing_refused_action_predicate_placeholders",
    "migration_risk_notes": "missing_migration_risk_notes",
}

_PRIVATE_ARTIFACT_KEY_MARKERS = (
    "auth_state",
    "browser",
    "cookie",
    "credential",
    "download",
    "downloaded",
    "har",
    "private_artifact",
    "private_path",
    "raw_body",
    "raw_crawl",
    "raw_download",
    "raw_html",
    "screenshot",
    "session",
    "storage_state",
    "trace",
)

_PRIVATE_ARTIFACT_TEXT_MARKERS = (
    ".har",
    ".trace",
    "auth-state",
    "auth_state",
    "browser artifact",
    "downloaded document",
    "raw crawl output",
    "session storage",
    "storage_state",
)

_LIVE_CLAIM_KEY_MARKERS = (
    "crawl_completed",
    "crawled_live",
    "devhub_claim",
    "devhub_completed",
    "devhub_surface_observed",
    "live_crawl",
    "live_devhub",
    "processor_completed",
)

_LIVE_CLAIM_TEXT_MARKERS = (
    "completed live crawl",
    "devhub observed live",
    "live crawl completed",
    "live devhub completed",
    "logged in to devhub",
)

_OUTCOME_GUARANTEE_KEY_MARKERS = (
    "approval_guaranteed",
    "guarantees_outcome",
    "legal_advice",
    "legal_conclusion",
    "permit_approved",
    "permitting_guarantee",
)

_MUTATION_FLAG_KEY_MARKERS = (
    "active_contract_mutation",
    "active_devhub_surface_mutation",
    "active_guardrail_mutation",
    "active_prompt_mutation",
    "active_requirement_mutation",
    "active_source_mutation",
    "mutate_contract",
    "mutate_devhub_surface",
    "mutate_guardrail",
    "mutate_process_model",
    "mutate_prompt",
    "mutate_release_state",
    "mutate_requirement",
    "mutate_source",
    "release_state_mutation",
    "update_contract",
    "update_devhub_surface",
    "update_guardrail",
    "update_process_model",
    "update_prompt",
    "update_release_state",
    "update_requirement",
    "update_source",
    "write_active_contract",
    "write_active_devhub_surface",
    "write_active_guardrail",
    "write_active_process_model",
    "write_active_prompt",
    "write_active_release_state",
    "write_active_requirement",
    "write_active_source",
)

_FORBIDDEN_COMMAND_TARGETS = (
    "src/lib/logic/",
    "public/corpus/portland-or/current/",
    "ipfs_datasets_py/.daemon/",
    "ppd/contracts/active",
    "ppd/devhub/surfaces/active",
    "ppd/guardrails/active",
    "ppd/process_models/active",
    "ppd/prompts/",
    "ppd/release_state/",
    "ppd/requirements/active",
    "ppd/source_registries/active",
    "ppd/surfaces/active",
)

_SAFE_FALSE_TEXT = {"", "false", "forbidden", "no", "none", "not_applicable", "prohibited"}


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    path: str
    message: str


def validate_guardrail_recompile_dry_run_plan_v2(plan: Mapping[str, Any]) -> list[ValidationIssue]:
    """Return validation issues for incomplete or unsafe dry-run plans."""

    if not isinstance(plan, Mapping):
        return [ValidationIssue("invalid_plan", "$", "plan must be a mapping")]

    issues: list[ValidationIssue] = []
    if plan.get("plan_version") != PLAN_VERSION:
        issues.append(ValidationIssue("invalid_plan_version", "$.plan_version", "unexpected plan version"))
    if plan.get("mode") != "fixture_first_offline_dry_run":
        issues.append(ValidationIssue("invalid_mode", "$.mode", "plan must remain fixture-first and offline"))
    if plan.get("active_bundle_mutation") != "forbidden":
        issues.append(ValidationIssue("mutation_flag", "$.active_bundle_mutation", "active guardrail bundle mutation must be forbidden"))

    _validate_delta_rows(plan, issues)
    _validate_validation_commands(plan, issues)
    _scan_prohibited_content(plan, "$", issues)
    return issues


def assert_valid_guardrail_recompile_dry_run_plan_v2(plan: Mapping[str, Any]) -> None:
    """Raise ValueError when a dry-run plan is incomplete or unsafe."""

    issues = validate_guardrail_recompile_dry_run_plan_v2(plan)
    if issues:
        details = "; ".join(f"{issue.code} at {issue.path}: {issue.message}" for issue in issues)
        raise ValueError(details)


def _validate_delta_rows(plan: Mapping[str, Any], issues: list[ValidationIssue]) -> None:
    rows = plan.get("ordered_synthetic_guardrail_bundle_delta_rows")
    if not isinstance(rows, Sequence) or isinstance(rows, (str, bytes, bytearray)) or not rows:
        issues.append(ValidationIssue("missing_guardrail_delta_rows", "$.ordered_synthetic_guardrail_bundle_delta_rows", "at least one synthetic guardrail delta row is required"))
        return

    observed_orders: list[Any] = []
    for index, row in enumerate(rows):
        path = f"$.ordered_synthetic_guardrail_bundle_delta_rows[{index}]"
        if not isinstance(row, Mapping):
            issues.append(ValidationIssue("invalid_guardrail_delta_row", path, "delta row must be a mapping"))
            continue
        observed_orders.append(row.get("row_order"))
        for key in REQUIRED_ROW_KEYS:
            if key not in row:
                issues.append(ValidationIssue("missing_guardrail_delta_row_field", f"{path}.{key}", "required delta row field is missing"))
        for key, code in _REQUIRED_PLACEHOLDER_LISTS.items():
            _require_non_empty_sequence(row.get(key), f"{path}.{key}", code, issues)
        disposition = row.get("reviewer_disposition_placeholders")
        if not isinstance(disposition, Mapping) or not disposition.get("review_status") or not disposition.get("decision"):
            issues.append(ValidationIssue("missing_reviewer_dispositions", f"{path}.reviewer_disposition_placeholders", "reviewer disposition placeholders must include review_status and decision"))
        delta = row.get("synthetic_guardrail_bundle_delta")
        if not isinstance(delta, Mapping) or delta.get("writes_active_bundle") != "false":
            issues.append(ValidationIssue("mutation_flag", f"{path}.synthetic_guardrail_bundle_delta", "synthetic delta must explicitly refuse active bundle writes"))

    if observed_orders != list(range(1, len(rows) + 1)):
        issues.append(ValidationIssue("invalid_guardrail_delta_row_order", "$.ordered_synthetic_guardrail_bundle_delta_rows", "row_order values must be sequential from 1"))


def _require_non_empty_sequence(value: Any, path: str, code: str, issues: list[ValidationIssue]) -> None:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)) or not value:
        issues.append(ValidationIssue(code, path, "required placeholder list must be non-empty"))


def _validate_validation_commands(plan: Mapping[str, Any], issues: list[ValidationIssue]) -> None:
    commands = plan.get("offline_validation_commands")
    if not isinstance(commands, Sequence) or isinstance(commands, (str, bytes, bytearray)) or not commands:
        issues.append(ValidationIssue("missing_validation_commands", "$.offline_validation_commands", "offline validation commands are required"))
        return
    if commands != OFFLINE_VALIDATION_COMMANDS:
        issues.append(ValidationIssue("invalid_validation_commands", "$.offline_validation_commands", "validation commands must match the exact offline command set"))
    for index, command in enumerate(commands):
        path = f"$.offline_validation_commands[{index}]"
        if not isinstance(command, Sequence) or isinstance(command, (str, bytes, bytearray)) or not command:
            issues.append(ValidationIssue("invalid_validation_command", path, "each validation command must be a token list"))
            continue
        if command[0] != "python3":
            issues.append(ValidationIssue("invalid_validation_command", path, "validation commands must use python3"))
        command_text = " ".join(str(part) for part in command)
        if any(target in command_text for target in _FORBIDDEN_COMMAND_TARGETS):
            issues.append(ValidationIssue("mutation_flag", path, "validation command targets a forbidden active workspace path"))


def _scan_prohibited_content(value: Any, path: str, issues: list[ValidationIssue]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            _validate_key_value(str(key), child, child_path, issues)
            _scan_prohibited_content(child, child_path, issues)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            _scan_prohibited_content(child, f"{path}[{index}]", issues)
    elif isinstance(value, str):
        _validate_text_value(value, path, issues)


def _validate_key_value(key: str, value: Any, path: str, issues: list[ValidationIssue]) -> None:
    normalized = _normalize_key(key)
    if _contains_marker(normalized, _PRIVATE_ARTIFACT_KEY_MARKERS) and _is_present(value):
        issues.append(ValidationIssue("private_artifact_reference", path, "private, session, browser, raw, or downloaded artifacts are not allowed"))
    if _contains_marker(normalized, _LIVE_CLAIM_KEY_MARKERS) and _is_truthy_unsafe(value):
        issues.append(ValidationIssue("live_crawl_or_devhub_claim", path, "live crawl or DevHub claims are not allowed"))
    if _contains_marker(normalized, _OUTCOME_GUARANTEE_KEY_MARKERS) and _is_truthy_unsafe(value):
        issues.append(ValidationIssue("outcome_guarantee", path, "legal or permitting guarantees are not allowed"))
    if _contains_marker(normalized, _MUTATION_FLAG_KEY_MARKERS) and _is_truthy_unsafe(value):
        issues.append(ValidationIssue("mutation_flag", path, "active source, requirement, process-model, guardrail, prompt, contract, DevHub surface, or release-state mutation flags are not allowed"))


def _validate_text_value(value: str, path: str, issues: list[ValidationIssue]) -> None:
    lowered = value.lower()
    if any(marker in lowered for marker in _PRIVATE_ARTIFACT_TEXT_MARKERS):
        issues.append(ValidationIssue("private_artifact_reference", path, "private, session, browser, raw, or downloaded artifact text is not allowed"))
    if any(marker in lowered for marker in _LIVE_CLAIM_TEXT_MARKERS):
        issues.append(ValidationIssue("live_crawl_or_devhub_claim", path, "live crawl or DevHub claim text is not allowed"))


def _normalize_key(key: str) -> str:
    parts: list[str] = []
    previous_lower = False
    for char in key:
        if char.isupper() and previous_lower:
            parts.append("_")
        if char in {"-", " ", "."}:
            parts.append("_")
            previous_lower = False
            continue
        parts.append(char.lower())
        previous_lower = char.islower() or char.isdigit()
    return "".join(parts)


def _contains_marker(key: str, markers: tuple[str, ...]) -> bool:
    return any(marker in key for marker in markers)


def _is_present(value: Any) -> bool:
    if value is None or value is False:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, Mapping):
        return bool(value)
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return bool(value)
    return True


def _is_truthy_unsafe(value: Any) -> bool:
    if value is True:
        return True
    if value is None or value is False:
        return False
    if isinstance(value, str):
        return value.strip().lower() not in _SAFE_FALSE_TEXT
    if isinstance(value, Mapping):
        return bool(value)
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return bool(value)
    return bool(value)


__all__ = [
    "ValidationIssue",
    "assert_valid_guardrail_recompile_dry_run_plan_v2",
    "validate_guardrail_recompile_dry_run_plan_v2",
]
