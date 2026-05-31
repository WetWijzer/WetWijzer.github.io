"""Validation for reversible draft executor review packet v2.

The packet is intentionally represented as plain JSON-compatible data.  This
module keeps validation deterministic and side-effect free so review packets can
be checked in tests and daemon self-tests without opening a browser, touching
DevHub, or reading private artifacts.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any


class ReversibleDraftExecutorReviewPacketV2Error(ValueError):
    """Raised when a v2 reversible draft executor review packet is invalid."""


@dataclass(frozen=True)
class ValidationIssue:
    """A single packet validation issue."""

    code: str
    message: str
    path: str


_REQUIRED_TOP_LEVEL_SECTIONS = (
    "reviewer_rows",
    "dry_run_request_acceptance",
    "preview_only_response_review",
    "trace_review",
    "selector_confidence_review",
    "exact_confirmation_stop_gate_review",
    "refused_consequential_action_review",
    "validation_commands",
    "mutation_flags",
)

_REVIEWER_ROW_FIELDS = ("reviewer_id", "role", "reviewed_at", "decision")
_DRY_RUN_ACCEPTANCE_FIELDS = (
    "accepted",
    "accepted_at",
    "request_id",
    "scope",
    "dry_run_only",
)
_PREVIEW_ONLY_RESPONSE_FIELDS = (
    "reviewed_by",
    "reviewed_at",
    "response_artifact_id",
    "preview_only",
    "private_artifacts_absent",
)
_TRACE_REVIEW_FIELDS = ("user_fact_trace_review", "source_evidence_trace_review")
_TRACE_ENTRY_FIELDS = ("trace_id", "reviewed_by", "reviewed_at", "decision")
_SELECTOR_ENTRY_FIELDS = ("selector", "confidence", "hold_reason")
_STOP_GATE_FIELDS = (
    "reviewed_by",
    "reviewed_at",
    "stop_gate_present",
    "exact_confirmation_required",
    "consequential_actions_blocked",
)
_REFUSED_ACTION_FIELDS = (
    "reviewed_by",
    "reviewed_at",
    "refused_actions",
    "consequential_action_policy_checked",
)
_MUTATION_FLAG_FIELDS = (
    "prompt_mutation_active",
    "guardrail_mutation_active",
    "devhub_surface_mutation_active",
    "source_mutation_active",
    "contract_mutation_active",
    "release_state_mutation_active",
)

_FORBIDDEN_ARTIFACT_TERMS = (
    "private_artifact",
    "session_file",
    "auth_state",
    "storage_state",
    "browser_trace",
    "playwright_trace",
    "har_file",
    "raw_crawl_output",
    "raw_download",
    "downloaded_document",
    "downloaded_artifact",
    "screenshot_artifact",
)

_FORBIDDEN_CLAIM_TERMS = (
    "live devhub execution completed",
    "live devhub action completed",
    "executed in devhub",
    "official draft saved",
    "official save completed",
    "permit submitted",
    "application submitted",
    "official submission completed",
    "submission confirmed",
    "guaranteed approval",
    "permit guaranteed",
    "legal advice",
    "legally sufficient",
    "compliance guaranteed",
    "permitting outcome guaranteed",
)


def validate_reversible_draft_executor_review_packet_v2(
    packet: Mapping[str, Any],
) -> list[ValidationIssue]:
    """Return validation issues for a reversible draft executor review packet v2."""

    issues: list[ValidationIssue] = []

    if not isinstance(packet, Mapping):
        return [
            ValidationIssue(
                "packet_not_mapping",
                "review packet v2 must be a JSON object",
                "$",
            )
        ]

    for section in _REQUIRED_TOP_LEVEL_SECTIONS:
        if section not in packet:
            issues.append(
                ValidationIssue(
                    "missing_section",
                    f"missing required section: {section}",
                    f"$.{section}",
                )
            )

    issues.extend(_validate_reviewer_rows(packet.get("reviewer_rows")))
    issues.extend(_validate_dry_run_request_acceptance(packet.get("dry_run_request_acceptance")))
    issues.extend(_validate_preview_only_response_review(packet.get("preview_only_response_review")))
    issues.extend(_validate_trace_review(packet.get("trace_review")))
    issues.extend(_validate_selector_confidence_review(packet.get("selector_confidence_review")))
    issues.extend(_validate_exact_confirmation_stop_gate_review(packet.get("exact_confirmation_stop_gate_review")))
    issues.extend(_validate_refused_consequential_action_review(packet.get("refused_consequential_action_review")))
    issues.extend(_validate_validation_commands(packet.get("validation_commands")))
    issues.extend(_validate_mutation_flags(packet.get("mutation_flags")))
    issues.extend(_validate_forbidden_artifacts(packet))
    issues.extend(_validate_forbidden_claims(packet))

    return issues


def assert_valid_reversible_draft_executor_review_packet_v2(packet: Mapping[str, Any]) -> None:
    """Raise when a reversible draft executor review packet v2 is invalid."""

    issues = validate_reversible_draft_executor_review_packet_v2(packet)
    if issues:
        detail = "; ".join(f"{issue.code} at {issue.path}: {issue.message}" for issue in issues)
        raise ReversibleDraftExecutorReviewPacketV2Error(detail)


def _validate_reviewer_rows(value: Any) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if not _is_non_empty_sequence(value):
        return [ValidationIssue("missing_reviewer_rows", "reviewer_rows must contain at least one reviewer row", "$.reviewer_rows")]

    for index, row in enumerate(value):
        path = f"$.reviewer_rows[{index}]"
        if not isinstance(row, Mapping):
            issues.append(ValidationIssue("invalid_reviewer_row", "reviewer row must be an object", path))
            continue
        for field in _REVIEWER_ROW_FIELDS:
            if not _has_text(row.get(field)):
                issues.append(ValidationIssue("missing_reviewer_row_field", f"reviewer row missing {field}", f"{path}.{field}"))
        if row.get("decision") not in {"approved", "rejected", "changes_requested"}:
            issues.append(ValidationIssue("invalid_reviewer_decision", "reviewer decision must be approved, rejected, or changes_requested", f"{path}.decision"))
    return issues


def _validate_dry_run_request_acceptance(value: Any) -> list[ValidationIssue]:
    issues = _require_mapping_with_fields(value, _DRY_RUN_ACCEPTANCE_FIELDS, "$.dry_run_request_acceptance", "dry_run_request_acceptance")
    if issues:
        return issues
    if value.get("accepted") is not True:
        issues.append(ValidationIssue("dry_run_request_not_accepted", "dry-run request acceptance must be true", "$.dry_run_request_acceptance.accepted"))
    if value.get("dry_run_only") is not True:
        issues.append(ValidationIssue("dry_run_only_not_confirmed", "dry-run request must be marked dry_run_only", "$.dry_run_request_acceptance.dry_run_only"))
    return issues


def _validate_preview_only_response_review(value: Any) -> list[ValidationIssue]:
    issues = _require_mapping_with_fields(value, _PREVIEW_ONLY_RESPONSE_FIELDS, "$.preview_only_response_review", "preview_only_response_review")
    if issues:
        return issues
    if value.get("preview_only") is not True:
        issues.append(ValidationIssue("preview_only_not_confirmed", "response review must confirm preview_only", "$.preview_only_response_review.preview_only"))
    if value.get("private_artifacts_absent") is not True:
        issues.append(ValidationIssue("private_artifacts_not_absent", "response review must confirm private artifacts are absent", "$.preview_only_response_review.private_artifacts_absent"))
    return issues


def _validate_trace_review(value: Any) -> list[ValidationIssue]:
    issues = _require_mapping_with_fields(value, _TRACE_REVIEW_FIELDS, "$.trace_review", "trace_review")
    if issues:
        return issues

    for field in _TRACE_REVIEW_FIELDS:
        entries = value.get(field)
        path = f"$.trace_review.{field}"
        if not _is_non_empty_sequence(entries):
            issues.append(ValidationIssue("missing_trace_review", f"{field} must contain at least one reviewed trace", path))
            continue
        for index, entry in enumerate(entries):
            entry_path = f"{path}[{index}]"
            if not isinstance(entry, Mapping):
                issues.append(ValidationIssue("invalid_trace_review", "trace review entry must be an object", entry_path))
                continue
            for required_field in _TRACE_ENTRY_FIELDS:
                if not _has_text(entry.get(required_field)):
                    issues.append(ValidationIssue("missing_trace_review_field", f"trace review missing {required_field}", f"{entry_path}.{required_field}"))
            if entry.get("decision") not in {"accepted", "rejected", "needs_review"}:
                issues.append(ValidationIssue("invalid_trace_review_decision", "trace review decision must be accepted, rejected, or needs_review", f"{entry_path}.decision"))
    return issues


def _validate_selector_confidence_review(value: Any) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if not isinstance(value, Mapping):
        return [ValidationIssue("missing_selector_confidence_review", "selector_confidence_review must be an object", "$.selector_confidence_review")]

    selectors = value.get("selectors")
    if not _is_non_empty_sequence(selectors):
        issues.append(ValidationIssue("missing_selector_rows", "selector confidence review must contain selector rows", "$.selector_confidence_review.selectors"))
        return issues

    for index, selector in enumerate(selectors):
        path = f"$.selector_confidence_review.selectors[{index}]"
        if not isinstance(selector, Mapping):
            issues.append(ValidationIssue("invalid_selector_row", "selector confidence row must be an object", path))
            continue
        for field in _SELECTOR_ENTRY_FIELDS:
            if field == "confidence":
                if not isinstance(selector.get(field), (int, float)):
                    issues.append(ValidationIssue("missing_selector_confidence", "selector row missing numeric confidence", f"{path}.confidence"))
            elif not _has_text(selector.get(field)):
                issues.append(ValidationIssue("missing_selector_hold_reason", f"selector row missing {field}", f"{path}.{field}"))
        if isinstance(selector.get("confidence"), (int, float)) and selector["confidence"] >= 1.0 and not _has_text(selector.get("verification_note")):
            issues.append(ValidationIssue("missing_selector_verification_note", "high-confidence selectors still require a verification note", f"{path}.verification_note"))
    return issues


def _validate_exact_confirmation_stop_gate_review(value: Any) -> list[ValidationIssue]:
    issues = _require_mapping_with_fields(value, _STOP_GATE_FIELDS, "$.exact_confirmation_stop_gate_review", "exact_confirmation_stop_gate_review")
    if issues:
        return issues
    for field in ("stop_gate_present", "exact_confirmation_required", "consequential_actions_blocked"):
        if value.get(field) is not True:
            issues.append(ValidationIssue("stop_gate_not_confirmed", f"{field} must be true", f"$.exact_confirmation_stop_gate_review.{field}"))
    return issues


def _validate_refused_consequential_action_review(value: Any) -> list[ValidationIssue]:
    issues = _require_mapping_with_fields(value, _REFUSED_ACTION_FIELDS, "$.refused_consequential_action_review", "refused_consequential_action_review")
    if issues:
        return issues
    if value.get("consequential_action_policy_checked") is not True:
        issues.append(ValidationIssue("consequential_policy_not_checked", "consequential action policy check must be true", "$.refused_consequential_action_review.consequential_action_policy_checked"))
    refused_actions = value.get("refused_actions")
    if not _is_non_empty_sequence(refused_actions):
        issues.append(ValidationIssue("missing_refused_actions", "refused consequential action review must list refused actions", "$.refused_consequential_action_review.refused_actions"))
    elif any(not _has_text(action) for action in refused_actions):
        issues.append(ValidationIssue("invalid_refused_action", "refused actions must be non-empty strings", "$.refused_consequential_action_review.refused_actions"))
    return issues


def _validate_validation_commands(value: Any) -> list[ValidationIssue]:
    if not _is_non_empty_sequence(value):
        return [ValidationIssue("missing_validation_commands", "validation_commands must contain at least one command", "$.validation_commands")]

    issues: list[ValidationIssue] = []
    for index, command in enumerate(value):
        path = f"$.validation_commands[{index}]"
        if not _is_non_empty_sequence(command) or any(not _has_text(part) for part in command):
            issues.append(ValidationIssue("invalid_validation_command", "validation command must be a non-empty list of strings", path))
    return issues


def _validate_mutation_flags(value: Any) -> list[ValidationIssue]:
    issues = _require_mapping_with_fields(value, _MUTATION_FLAG_FIELDS, "$.mutation_flags", "mutation_flags")
    if issues:
        return issues
    for field in _MUTATION_FLAG_FIELDS:
        if value.get(field) is not False:
            issues.append(ValidationIssue("active_mutation_flag", f"{field} must be false", f"$.mutation_flags.{field}"))
    return issues


def _validate_forbidden_artifacts(packet: Mapping[str, Any]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for path, text in _walk_text(packet):
        normalized = _normalize_text(text)
        for term in _FORBIDDEN_ARTIFACT_TERMS:
            if term in normalized:
                issues.append(ValidationIssue("forbidden_artifact_reference", f"packet references forbidden artifact term: {term}", path))
    return issues


def _validate_forbidden_claims(packet: Mapping[str, Any]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for path, text in _walk_text(packet):
        normalized = _normalize_text(text)
        for term in _FORBIDDEN_CLAIM_TERMS:
            if term in normalized:
                issues.append(ValidationIssue("forbidden_claim", f"packet contains forbidden claim: {term}", path))
    return issues


def _require_mapping_with_fields(value: Any, fields: Iterable[str], path: str, label: str) -> list[ValidationIssue]:
    if not isinstance(value, Mapping):
        return [ValidationIssue(f"missing_{label}", f"{label} must be an object", path)]

    issues: list[ValidationIssue] = []
    for field in fields:
        field_value = value.get(field)
        if isinstance(field_value, bool):
            if field not in value:
                issues.append(ValidationIssue(f"missing_{label}_field", f"{label} missing {field}", f"{path}.{field}"))
        elif not _has_text(field_value) and not _is_non_empty_sequence(field_value):
            issues.append(ValidationIssue(f"missing_{label}_field", f"{label} missing {field}", f"{path}.{field}"))
    return issues


def _is_non_empty_sequence(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)) and len(value) > 0


def _has_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _normalize_text(value: str) -> str:
    return " ".join(value.lower().replace("-", "_").split())


def _walk_text(value: Any, path: str = "$") -> Iterable[tuple[str, str]]:
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f"{path}.{key}" if isinstance(key, str) and key.isidentifier() else f"{path}[{key!r}]"
            yield from _walk_text(child, child_path)
    elif isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        for index, child in enumerate(value):
            yield from _walk_text(child, f"{path}[{index}]")
