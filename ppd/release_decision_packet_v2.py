"""Validation for PP&D post-recompile release decision packet v2.

The validator is intentionally conservative. A post-recompile release packet is a
commit-safe decision artifact, not evidence of live crawl completion, DevHub
access, legal sufficiency, official action completion, or active state mutation.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any


FORBIDDEN_ARTIFACT_TERMS = (
    "auth_state",
    "browser_context",
    "cookie",
    "credential",
    "downloaded",
    "har",
    "localstorage",
    "private artifact",
    "raw crawl",
    "session file",
    "session storage",
    "screenshot",
    "storage_state",
    "trace.zip",
    "video.webm",
)

FORBIDDEN_CLAIM_TERMS = (
    "completed official action",
    "devhub was crawled",
    "devhub was accessed",
    "devhub login completed",
    "guaranteed approval",
    "guaranteed permit",
    "legal advice",
    "legal guarantee",
    "live crawl completed",
    "official action completed",
    "permit guaranteed",
    "permitting guarantee",
    "submitted to devhub",
)

MUTATION_FLAG_FIELDS = (
    "active_prompt_mutation",
    "active_guardrail_mutation",
    "active_source_mutation",
    "active_requirement_mutation",
    "active_process_model_mutation",
    "active_contract_mutation",
    "active_devhub_surface_mutation",
    "active_release_state_mutation",
    "prompt_mutated",
    "guardrail_mutated",
    "source_mutated",
    "requirement_mutated",
    "process_model_mutated",
    "contract_mutated",
    "devhub_surface_mutated",
    "release_state_mutated",
)

REQUIRED_NON_EMPTY_FIELDS = (
    "release_decision_rows",
    "stale_source_hold_outcomes",
    "reviewer_signoff_placeholders",
    "rollback_references",
    "inactive_to_active_eligibility_notes",
    "blocked_consequential_action_reminders",
    "validation_commands",
)


@dataclass(frozen=True)
class ValidationIssue:
    """A deterministic validation issue for a release decision packet."""

    code: str
    message: str


def validate_post_recompile_release_decision_packet_v2(packet: Mapping[str, Any]) -> list[ValidationIssue]:
    """Return validation issues for a post-recompile release decision packet v2."""

    issues: list[ValidationIssue] = []

    if not isinstance(packet, Mapping):
        return [ValidationIssue("packet.not_mapping", "packet must be a mapping")]

    if packet.get("packet_version") != "post-recompile-release-decision-v2":
        issues.append(
            ValidationIssue(
                "packet.version",
                "packet_version must be post-recompile-release-decision-v2",
            )
        )

    for field in REQUIRED_NON_EMPTY_FIELDS:
        if _is_missing_or_empty(packet.get(field)):
            issues.append(ValidationIssue(f"packet.{field}.missing", f"{field} is required and must be non-empty"))

    issues.extend(_validate_release_decision_rows(packet.get("release_decision_rows")))
    issues.extend(_validate_stale_source_hold_outcomes(packet.get("stale_source_hold_outcomes")))
    issues.extend(_validate_signoff_placeholders(packet.get("reviewer_signoff_placeholders")))
    issues.extend(_validate_validation_commands(packet.get("validation_commands")))
    issues.extend(_validate_mutation_flags(packet))
    issues.extend(_validate_forbidden_strings(packet))

    return issues


def assert_valid_post_recompile_release_decision_packet_v2(packet: Mapping[str, Any]) -> None:
    """Raise ValueError when a packet fails v2 validation."""

    issues = validate_post_recompile_release_decision_packet_v2(packet)
    if issues:
        details = "; ".join(f"{issue.code}: {issue.message}" for issue in issues)
        raise ValueError(details)


def _validate_release_decision_rows(rows: Any) -> list[ValidationIssue]:
    if _is_missing_or_empty(rows):
        return []
    if not _is_non_string_sequence(rows):
        return [ValidationIssue("packet.release_decision_rows.type", "release_decision_rows must be a list")]

    issues: list[ValidationIssue] = []
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            issues.append(ValidationIssue("packet.release_decision_rows.item_type", f"row {index} must be a mapping"))
            continue
        if not str(row.get("decision", "")).strip():
            issues.append(ValidationIssue("packet.release_decision_rows.decision", f"row {index} is missing decision"))
        if not str(row.get("reason", "")).strip():
            issues.append(ValidationIssue("packet.release_decision_rows.reason", f"row {index} is missing reason"))
        if not str(row.get("status", "")).strip():
            issues.append(ValidationIssue("packet.release_decision_rows.status", f"row {index} is missing status"))
    return issues


def _validate_stale_source_hold_outcomes(outcomes: Any) -> list[ValidationIssue]:
    if _is_missing_or_empty(outcomes):
        return []
    if not _is_non_string_sequence(outcomes):
        return [ValidationIssue("packet.stale_source_hold_outcomes.type", "stale_source_hold_outcomes must be a list")]

    issues: list[ValidationIssue] = []
    for index, outcome in enumerate(outcomes):
        if not isinstance(outcome, Mapping):
            issues.append(ValidationIssue("packet.stale_source_hold_outcomes.item_type", f"outcome {index} must be a mapping"))
            continue
        if not str(outcome.get("source_id", "")).strip():
            issues.append(ValidationIssue("packet.stale_source_hold_outcomes.source_id", f"outcome {index} is missing source_id"))
        if not str(outcome.get("hold_outcome", "")).strip():
            issues.append(ValidationIssue("packet.stale_source_hold_outcomes.hold_outcome", f"outcome {index} is missing hold_outcome"))
    return issues


def _validate_signoff_placeholders(placeholders: Any) -> list[ValidationIssue]:
    if _is_missing_or_empty(placeholders):
        return []
    if not _is_non_string_sequence(placeholders):
        return [ValidationIssue("packet.reviewer_signoff_placeholders.type", "reviewer_signoff_placeholders must be a list")]

    issues: list[ValidationIssue] = []
    for index, placeholder in enumerate(placeholders):
        if not isinstance(placeholder, Mapping):
            issues.append(ValidationIssue("packet.reviewer_signoff_placeholders.item_type", f"placeholder {index} must be a mapping"))
            continue
        if not str(placeholder.get("reviewer_role", "")).strip():
            issues.append(ValidationIssue("packet.reviewer_signoff_placeholders.role", f"placeholder {index} is missing reviewer_role"))
        if placeholder.get("signed") is True:
            issues.append(ValidationIssue("packet.reviewer_signoff_placeholders.signed", f"placeholder {index} must not claim reviewer signoff"))
    return issues


def _validate_validation_commands(commands: Any) -> list[ValidationIssue]:
    if _is_missing_or_empty(commands):
        return []
    if not _is_non_string_sequence(commands):
        return [ValidationIssue("packet.validation_commands.type", "validation_commands must be a list of argv lists")]

    issues: list[ValidationIssue] = []
    for index, command in enumerate(commands):
        if not _is_non_string_sequence(command) or not all(isinstance(part, str) and part for part in command):
            issues.append(ValidationIssue("packet.validation_commands.item", f"command {index} must be a non-empty argv list of strings"))
    return issues


def _validate_mutation_flags(packet: Mapping[str, Any]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for field in MUTATION_FLAG_FIELDS:
        if packet.get(field) is True:
            issues.append(ValidationIssue("packet.mutation_flag", f"{field} must not be true in a release decision packet"))

    active_mutations = packet.get("active_mutation_flags")
    if active_mutations not in (None, [], {}, False):
        issues.append(ValidationIssue("packet.active_mutation_flags", "active_mutation_flags must be absent or empty"))
    return issues


def _validate_forbidden_strings(value: Any) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for path, text in _walk_strings(value):
        normalized = " ".join(text.lower().replace("_", " ").replace("-", " ").split())
        raw_normalized = text.lower()
        for term in FORBIDDEN_ARTIFACT_TERMS:
            comparable = " ".join(term.lower().replace("_", " ").replace("-", " ").split())
            if comparable in normalized or term.lower() in raw_normalized:
                issues.append(ValidationIssue("packet.forbidden_artifact", f"{path} references forbidden artifact term: {term}"))
        for term in FORBIDDEN_CLAIM_TERMS:
            comparable = " ".join(term.lower().replace("_", " ").replace("-", " ").split())
            if comparable in normalized:
                issues.append(ValidationIssue("packet.forbidden_claim", f"{path} contains forbidden claim: {term}"))
    return issues


def _walk_strings(value: Any, path: str = "packet") -> list[tuple[str, str]]:
    if isinstance(value, str):
        return [(path, value)]
    if isinstance(value, Mapping):
        strings: list[tuple[str, str]] = []
        for key, child in value.items():
            key_text = str(key)
            strings.extend(_walk_strings(key_text, f"{path}.{key_text}.__key__"))
            strings.extend(_walk_strings(child, f"{path}.{key_text}"))
        return strings
    if _is_non_string_sequence(value):
        strings = []
        for index, child in enumerate(value):
            strings.extend(_walk_strings(child, f"{path}[{index}]"))
        return strings
    return []


def _is_missing_or_empty(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, Mapping | Sequence):
        return len(value) == 0
    return False


def _is_non_string_sequence(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, str | bytes | bytearray)
