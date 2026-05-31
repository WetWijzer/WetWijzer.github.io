"""Validation for attended DevHub read-only observation runbook v2 packets."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any


REQUIRED_METADATA_ONLY_CAPTURE_FIELDS = frozenset(
    {
        "surface_id",
        "page_heading",
        "accessible_landmarks",
        "field_labels",
        "validation_message_placeholders",
        "redaction_notes",
    }
)

REQUIRED_STOP_BEFORE_ACTIONS = frozenset(
    {
        "submit",
        "certify",
        "upload",
        "pay",
        "schedule",
        "cancel",
        "withdraw",
    }
)

REQUIRED_REVIEWER_DISPOSITIONS = frozenset(
    {"approved", "rejected", "needs_revision"}
)

PRIVATE_ARTIFACT_TERMS = frozenset(
    {
        "auth_state",
        "browser_context",
        "cookie",
        "credentials",
        "download",
        "downloaded_document",
        "har",
        "local_private_path",
        "raw_html",
        "raw_private_value",
        "screenshot",
        "session_storage",
        "trace",
    }
)

LIVE_EXECUTION_TERMS = frozenset(
    {
        "executed_live_devhub",
        "live_devhub_completed",
        "live_devhub_run",
        "production_devhub_executed",
    }
)

OFFICIAL_COMPLETION_TERMS = frozenset(
    {
        "official_action_completed",
        "permit_submitted",
        "payment_completed",
        "inspection_scheduled",
        "correction_uploaded",
        "certification_completed",
    }
)

GUARANTEE_TERMS = frozenset(
    {
        "approval_guaranteed",
        "legal_advice",
        "permit_guaranteed",
        "permitting_outcome_guaranteed",
        "will_be_approved",
    }
)

MUTATION_FLAGS = frozenset(
    {
        "mutates_prompt",
        "mutates_guardrails",
        "mutates_devhub_surface",
        "mutates_sources",
        "mutates_contracts",
        "mutates_release_state",
        "active_prompt_mutation",
        "active_guardrail_mutation",
        "active_devhub_surface_mutation",
        "active_source_mutation",
        "active_contract_mutation",
        "active_release_state_mutation",
    }
)


@dataclass(frozen=True)
class ValidationIssue:
    """A deterministic validation issue for a runbook packet."""

    code: str
    message: str


def validate_runbook(packet: Mapping[str, Any]) -> list[ValidationIssue]:
    """Return all validation issues for an attended read-only runbook v2 packet."""

    issues: list[ValidationIssue] = []

    if packet.get("runbook_version") != "v2":
        issues.append(ValidationIssue("runbook_version", "runbook_version must be v2"))

    if packet.get("mode") != "attended_devhub_read_only_observation":
        issues.append(
            ValidationIssue(
                "mode",
                "mode must be attended_devhub_read_only_observation",
            )
        )

    _validate_observation_steps(packet, issues)
    _validate_metadata_capture_fields(packet, issues)
    _validate_placeholders(packet, issues)
    _validate_redacted_journal_examples(packet, issues)
    _validate_stop_before_action_checkpoints(packet, issues)
    _validate_reviewer_dispositions(packet, issues)
    _validate_validation_commands(packet, issues)
    _validate_forbidden_terms(packet, issues)
    _validate_mutation_flags(packet, issues)

    return issues


def assert_valid_runbook(packet: Mapping[str, Any]) -> None:
    """Raise ValueError when the runbook packet is not valid."""

    issues = validate_runbook(packet)
    if issues:
        details = "; ".join(f"{issue.code}: {issue.message}" for issue in issues)
        raise ValueError(details)


def validation_error_codes(packet: Mapping[str, Any]) -> set[str]:
    """Return only deterministic error codes for tests and daemon checks."""

    return {issue.code for issue in validate_runbook(packet)}


def _validate_observation_steps(
    packet: Mapping[str, Any], issues: list[ValidationIssue]
) -> None:
    steps = packet.get("observation_steps")
    if not _is_non_empty_sequence(steps):
        issues.append(
            ValidationIssue(
                "missing_observation_steps",
                "observation_steps must contain at least one read-only observation step",
            )
        )
        return

    for index, step in enumerate(steps):
        if not isinstance(step, Mapping):
            issues.append(
                ValidationIssue(
                    "invalid_observation_step",
                    f"observation step {index} must be an object",
                )
            )
            continue
        if step.get("intent") != "observe_read_only":
            issues.append(
                ValidationIssue(
                    "invalid_observation_step_intent",
                    f"observation step {index} must use observe_read_only intent",
                )
            )
        if step.get("capture_scope") != "metadata_only":
            issues.append(
                ValidationIssue(
                    "non_metadata_only_observation_step",
                    f"observation step {index} must capture metadata only",
                )
            )


def _validate_metadata_capture_fields(
    packet: Mapping[str, Any], issues: list[ValidationIssue]
) -> None:
    fields = _string_set(packet.get("metadata_only_capture_fields"))
    missing = REQUIRED_METADATA_ONLY_CAPTURE_FIELDS - fields
    if missing:
        issues.append(
            ValidationIssue(
                "missing_metadata_only_capture_fields",
                "metadata_only_capture_fields is missing: " + ", ".join(sorted(missing)),
            )
        )


def _validate_placeholders(
    packet: Mapping[str, Any], issues: list[ValidationIssue]
) -> None:
    placeholders = packet.get("placeholders")
    if not isinstance(placeholders, Mapping):
        issues.append(
            ValidationIssue(
                "missing_placeholders",
                "placeholders must include accessible_roles and validation_messages",
            )
        )
        return

    if not _is_non_empty_sequence(placeholders.get("accessible_roles")):
        issues.append(
            ValidationIssue(
                "missing_accessible_role_placeholders",
                "placeholders.accessible_roles must be non-empty",
            )
        )
    if not _is_non_empty_sequence(placeholders.get("validation_messages")):
        issues.append(
            ValidationIssue(
                "missing_validation_message_placeholders",
                "placeholders.validation_messages must be non-empty",
            )
        )


def _validate_redacted_journal_examples(
    packet: Mapping[str, Any], issues: list[ValidationIssue]
) -> None:
    examples = packet.get("redacted_journal_examples")
    if not _is_non_empty_sequence(examples):
        issues.append(
            ValidationIssue(
                "missing_redacted_journal_examples",
                "redacted_journal_examples must contain at least one redacted example",
            )
        )
        return

    for index, example in enumerate(examples):
        if not isinstance(example, Mapping) or example.get("redacted") is not True:
            issues.append(
                ValidationIssue(
                    "unredacted_journal_example",
                    f"redacted_journal_examples[{index}] must be marked redacted",
                )
            )


def _validate_stop_before_action_checkpoints(
    packet: Mapping[str, Any], issues: list[ValidationIssue]
) -> None:
    checkpoints = packet.get("stop_before_action_checkpoints")
    if not _is_non_empty_sequence(checkpoints):
        issues.append(
            ValidationIssue(
                "missing_stop_before_action_checkpoints",
                "stop_before_action_checkpoints must be non-empty",
            )
        )
        return

    actions: set[str] = set()
    for checkpoint in checkpoints:
        if isinstance(checkpoint, Mapping):
            actions.update(_string_set(checkpoint.get("actions")))
            action = checkpoint.get("action")
            if isinstance(action, str):
                actions.add(action)
        elif isinstance(checkpoint, str):
            actions.add(checkpoint)

    missing = REQUIRED_STOP_BEFORE_ACTIONS - actions
    if missing:
        issues.append(
            ValidationIssue(
                "incomplete_stop_before_action_checkpoints",
                "stop-before-action checkpoints are missing: " + ", ".join(sorted(missing)),
            )
        )


def _validate_reviewer_dispositions(
    packet: Mapping[str, Any], issues: list[ValidationIssue]
) -> None:
    dispositions = _string_set(packet.get("reviewer_dispositions"))
    missing = REQUIRED_REVIEWER_DISPOSITIONS - dispositions
    if missing:
        issues.append(
            ValidationIssue(
                "missing_reviewer_dispositions",
                "reviewer_dispositions is missing: " + ", ".join(sorted(missing)),
            )
        )


def _validate_validation_commands(
    packet: Mapping[str, Any], issues: list[ValidationIssue]
) -> None:
    commands = packet.get("validation_commands")
    if not _is_non_empty_sequence(commands):
        issues.append(
            ValidationIssue(
                "missing_validation_commands",
                "validation_commands must contain at least one deterministic command",
            )
        )
        return

    for index, command in enumerate(commands):
        if not _is_non_empty_sequence(command) or not all(
            isinstance(part, str) and part for part in command
        ):
            issues.append(
                ValidationIssue(
                    "invalid_validation_command",
                    f"validation_commands[{index}] must be a non-empty list of strings",
                )
            )


def _validate_forbidden_terms(
    packet: Mapping[str, Any], issues: list[ValidationIssue]
) -> None:
    flattened = _flatten(packet)
    _append_forbidden_issue(
        flattened,
        PRIVATE_ARTIFACT_TERMS,
        issues,
        "forbidden_private_or_raw_artifacts",
        "runbook must not include private, session, browser, raw, or downloaded artifacts",
    )
    _append_forbidden_issue(
        flattened,
        LIVE_EXECUTION_TERMS,
        issues,
        "forbidden_live_devhub_execution_claim",
        "runbook must not claim live DevHub execution",
    )
    _append_forbidden_issue(
        flattened,
        OFFICIAL_COMPLETION_TERMS,
        issues,
        "forbidden_official_action_completion_claim",
        "runbook must not claim official-action completion",
    )
    _append_forbidden_issue(
        flattened,
        GUARANTEE_TERMS,
        issues,
        "forbidden_legal_or_permitting_guarantee",
        "runbook must not include legal or permitting guarantees",
    )


def _validate_mutation_flags(
    packet: Mapping[str, Any], issues: list[ValidationIssue]) -> None:
    flattened = _flatten(packet)
    present_flags = sorted(term for term in MUTATION_FLAGS if term in flattened)
    true_flags = sorted(
        key
        for key in MUTATION_FLAGS
        if _lookup_nested_bool(packet, key) is True
    )
    if present_flags or true_flags:
        issues.append(
            ValidationIssue(
                "forbidden_active_mutation_flags",
                "runbook must not include active mutation flags: "
                + ", ".join(sorted(set(present_flags + true_flags))),
            )
        )


def _append_forbidden_issue(
    flattened: set[str],
    forbidden: frozenset[str],
    issues: list[ValidationIssue],
    code: str,
    message: str,
) -> None:
    matches = sorted(term for term in forbidden if term in flattened)
    if matches:
        issues.append(ValidationIssue(code, message + ": " + ", ".join(matches)))


def _lookup_nested_bool(packet: Mapping[str, Any], key: str) -> bool | None:
    value = packet.get(key)
    if isinstance(value, bool):
        return value
    flags = packet.get("mutation_flags")
    if isinstance(flags, Mapping):
        nested_value = flags.get(key)
        if isinstance(nested_value, bool):
            return nested_value
    return None


def _is_non_empty_sequence(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes)) and len(value) > 0


def _string_set(value: Any) -> set[str]:
    if not _is_non_empty_sequence(value):
        return set()
    return {item for item in value if isinstance(item, str) and item}


def _flatten(value: Any) -> set[str]:
    terms: set[str] = set()
    if isinstance(value, Mapping):
        for key, item in value.items():
            terms.add(str(key))
            terms.update(_flatten(item))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for item in value:
            terms.update(_flatten(item))
    elif isinstance(value, str):
        terms.add(value)
    return terms
