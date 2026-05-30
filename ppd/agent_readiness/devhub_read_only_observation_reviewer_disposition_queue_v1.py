"""Validation for DevHub read-only observation reviewer disposition queue v1.

The queue is an offline review artifact. It may describe planned, redacted,
safe-read-only DevHub observations, but it must not carry browser/session
artifacts, raw crawled or downloaded data, live execution claims, permitting
outcome guarantees, consequential action instructions, or active mutation flags.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

QUEUE_VERSION = "devhub_read_only_observation_reviewer_disposition_queue_v1"
SAFE_READ_ONLY_CLASSIFICATIONS = frozenset(
    {"safe_read_only", "safe-read-only", "read_only_observation", "read-only-observation"}
)
ALLOWED_REVIEWER_DECISIONS = frozenset({"approve_read_only", "defer", "reject", "needs_revision"})

_REQUIRED_TOP_LEVEL_SEQUENCES = (
    "reviewer_decision_rows",
    "safe_read_only_surface_buckets",
    "redaction_confirmation_placeholders",
    "blocked_action_carry_forward_notes",
    "rollback_checkpoints",
    "validation_commands",
)

_PRIVATE_ARTIFACT_TERMS = (
    "auth state",
    "authenticated artifact",
    "browser artifact",
    "browser profile",
    "browser state",
    "cookie",
    "credential",
    "devhub session",
    "local private path",
    "localstorage",
    "password",
    "private artifact",
    "private value",
    "session artifact",
    "session state",
    "session storage",
    "session_state",
    "storage state",
    "storage_state",
    "token",
)

_CAPTURE_ARTIFACT_TERMS = (
    ".har",
    ".png",
    "auth file",
    "auth.json",
    "har file",
    "network trace",
    "screenshot",
    "storage_state.json",
    "trace file",
    "trace.zip",
)

_RAW_DATA_TERMS = (
    "downloaded data",
    "downloaded document",
    "downloaded pdf",
    "pdf dump",
    "raw authenticated html",
    "raw body",
    "raw capture",
    "raw crawl",
    "raw download",
    "raw pdf",
)

_LIVE_EXECUTION_OR_PROMOTION_TERMS = (
    "completed authenticated run",
    "executed in devhub",
    "live authenticated execution",
    "logged into devhub and ran",
    "observation promoted",
    "observation-promoted",
    "promoted observation",
    "ran against live devhub",
)

_OUTCOME_GUARANTEE_TERMS = (
    "approval guaranteed",
    "guarantee approval",
    "guaranteed approval",
    "guaranteed issuance",
    "guaranteed permit",
    "legal advice",
    "permit approved",
    "permit issued",
    "permit will be approved",
    "permit will be issued",
    "will be approved",
    "will be issued",
    "will satisfy the city",
)

_CONSEQUENTIAL_ACTION_TERMS = (
    "cancel",
    "cancellation",
    "certification",
    "certify",
    "payment",
    "pay fee",
    "pay the fee",
    "schedule",
    "scheduling",
    "submit",
    "submission",
    "upload",
)

_MUTATION_FLAG_KEYS = frozenset(
    {
        "active_agent_state_mutation",
        "active_fixture_mutation",
        "active_guardrail_mutation",
        "active_prompt_mutation",
        "active_release_state_mutation",
        "active_source_mutation",
        "active_surface_mutation",
        "active_surface_registry_mutation",
        "agent_state_mutation",
        "agent_state_mutation_enabled",
        "fixture_mutation",
        "fixture_mutation_enabled",
        "guardrail_mutation",
        "guardrail_mutation_enabled",
        "mutates_agent_state",
        "mutates_fixtures",
        "mutates_guardrails",
        "mutates_prompt",
        "mutates_prompts",
        "mutates_release_state",
        "mutates_source",
        "mutates_sources",
        "mutates_surface",
        "mutates_surface_registry",
        "prompt_mutation",
        "prompt_mutation_enabled",
        "release_state_mutation",
        "release_state_mutation_enabled",
        "source_mutation",
        "source_mutation_enabled",
        "surface_mutation",
        "surface_mutation_enabled",
        "surface_registry_mutation",
    }
)

_ARTIFACT_POLICY_KEYS = (
    "captures_auth_files",
    "captures_browser_artifacts",
    "captures_har_files",
    "captures_private_values",
    "captures_screenshots",
    "captures_session_state",
    "captures_traces",
    "creates_auth_files",
    "creates_browser_artifacts",
    "creates_har_files",
    "creates_screenshots",
    "creates_session_state",
    "creates_traces",
    "stores_downloads",
    "stores_raw_crawl_output",
    "stores_raw_pdf_output",
)


@dataclass(frozen=True)
class DevHubReadOnlyObservationReviewerDispositionQueueIssue:
    """Machine-readable validation issue."""

    code: str
    path: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "path": self.path, "message": self.message}


def validate_devhub_read_only_observation_reviewer_disposition_queue_v1(
    queue: Mapping[str, Any],
) -> list[DevHubReadOnlyObservationReviewerDispositionQueueIssue]:
    """Return deterministic fail-closed validation issues for a queue candidate."""

    issues: list[DevHubReadOnlyObservationReviewerDispositionQueueIssue] = []
    if not isinstance(queue, Mapping):
        return [
            DevHubReadOnlyObservationReviewerDispositionQueueIssue(
                "invalid_queue",
                "$",
                "queue must be an object",
            )
        ]

    version = queue.get("queue_version") or queue.get("packet_version")
    if version != QUEUE_VERSION:
        _add_issue(issues, "invalid_queue_version", "queue_version", f"queue_version must be {QUEUE_VERSION}")

    for key in _REQUIRED_TOP_LEVEL_SEQUENCES:
        _require_non_empty_sequence(queue, key, issues)

    surface_bucket_ids = _validate_safe_read_only_surface_buckets(
        queue.get("safe_read_only_surface_buckets"),
        issues,
    )
    redaction_placeholder_ids = _validate_redaction_confirmation_placeholders(
        queue.get("redaction_confirmation_placeholders"),
        issues,
    )
    blocked_note_ids = _validate_blocked_action_carry_forward_notes(
        queue.get("blocked_action_carry_forward_notes"),
        issues,
    )
    rollback_checkpoint_ids = _validate_rollback_checkpoints(queue.get("rollback_checkpoints"), issues)
    _validate_validation_commands(queue.get("validation_commands"), issues)
    _validate_artifact_policy(queue.get("artifact_policy", {}), issues)
    _validate_mutation_flags(queue.get("mutation_flags", {}), "mutation_flags", issues)
    _validate_reviewer_decision_rows(
        queue.get("reviewer_decision_rows"),
        surface_bucket_ids,
        redaction_placeholder_ids,
        blocked_note_ids,
        rollback_checkpoint_ids,
        issues,
    )
    _scan_for_rejected_content(queue, issues)
    return _dedupe_issues(issues)


def validate_queue(queue: Mapping[str, Any]) -> list[DevHubReadOnlyObservationReviewerDispositionQueueIssue]:
    """Compatibility alias for generic packet validators."""

    return validate_devhub_read_only_observation_reviewer_disposition_queue_v1(queue)


def assert_valid_devhub_read_only_observation_reviewer_disposition_queue_v1(queue: Mapping[str, Any]) -> None:
    """Raise AssertionError if the queue is not valid."""

    issues = validate_devhub_read_only_observation_reviewer_disposition_queue_v1(queue)
    if issues:
        formatted = "; ".join(f"{issue.code} at {issue.path}" for issue in issues)
        raise AssertionError("invalid DevHub read-only observation reviewer disposition queue v1: " + formatted)


def _validate_reviewer_decision_rows(
    value: Any,
    surface_bucket_ids: set[str],
    redaction_placeholder_ids: set[str],
    blocked_note_ids: set[str],
    rollback_checkpoint_ids: set[str],
    issues: list[DevHubReadOnlyObservationReviewerDispositionQueueIssue],
) -> None:
    if not _is_non_empty_sequence(value):
        return

    seen_ids: set[str] = set()
    for index, row in enumerate(value):
        path = f"reviewer_decision_rows[{index}]"
        if not isinstance(row, Mapping):
            _add_issue(issues, "invalid_reviewer_decision_row", path, "reviewer decision rows must be objects")
            continue

        row_id = _string_value(row.get("row_id") or row.get("id"))
        if not row_id:
            _add_issue(issues, "missing_reviewer_decision_row_id", f"{path}.row_id", "row_id is required")
        elif row_id in seen_ids:
            _add_issue(issues, "duplicate_reviewer_decision_row_id", f"{path}.row_id", "row_id must be unique")
        else:
            seen_ids.add(row_id)

        decision = _string_value(row.get("reviewer_decision") or row.get("decision"))
        if decision not in ALLOWED_REVIEWER_DECISIONS:
            _add_issue(
                issues,
                "invalid_reviewer_decision",
                f"{path}.reviewer_decision",
                "reviewer_decision must be approve_read_only, defer, reject, or needs_revision",
            )

        for key in ("reviewer_owner", "rationale"):
            if not _string_value(row.get(key)):
                _add_issue(issues, f"missing_{key}", f"{path}.{key}", f"{key} is required")

        if not _has_citation(row.get("citations")) and not _has_non_empty_string_sequence(row.get("source_evidence_ids")):
            _add_issue(
                issues,
                "uncited_reviewer_decision_row",
                f"{path}.citations",
                "reviewer decision rows must cite public source evidence",
            )

        _require_known_ref(
            row,
            "safe_read_only_surface_bucket_id",
            surface_bucket_ids,
            path,
            "missing_safe_read_only_surface_bucket_ref",
            issues,
        )
        _require_known_ref(
            row,
            "redaction_confirmation_placeholder_id",
            redaction_placeholder_ids,
            path,
            "missing_redaction_confirmation_placeholder_ref",
            issues,
        )
        _require_known_ref(
            row,
            "blocked_action_carry_forward_note_id",
            blocked_note_ids,
            path,
            "missing_blocked_action_carry_forward_note_ref",
            issues,
        )
        _require_known_ref(
            row,
            "rollback_checkpoint_id",
            rollback_checkpoint_ids,
            path,
            "missing_rollback_checkpoint_ref",
            issues,
        )


def _validate_safe_read_only_surface_buckets(
    value: Any,
    issues: list[DevHubReadOnlyObservationReviewerDispositionQueueIssue],
) -> set[str]:
    ids: set[str] = set()
    if not _is_non_empty_sequence(value):
        return ids
    for index, bucket in enumerate(value):
        path = f"safe_read_only_surface_buckets[{index}]"
        if not isinstance(bucket, Mapping):
            _add_issue(issues, "invalid_safe_read_only_surface_bucket", path, "surface buckets must be objects")
            continue
        bucket_id = _string_value(bucket.get("bucket_id") or bucket.get("id"))
        if not bucket_id:
            _add_issue(issues, "missing_safe_read_only_surface_bucket_id", f"{path}.bucket_id", "bucket_id is required")
        else:
            ids.add(bucket_id)
        classification = _string_value(bucket.get("classification") or bucket.get("action_classification"))
        if classification not in SAFE_READ_ONLY_CLASSIFICATIONS:
            _add_issue(
                issues,
                "unsafe_surface_bucket_classification",
                f"{path}.classification",
                "surface bucket classification must be safe_read_only",
            )
        if not _has_non_empty_string_sequence(bucket.get("surface_ids")):
            _add_issue(issues, "missing_surface_ids", f"{path}.surface_ids", "surface_ids must be a non-empty list")
    return ids


def _validate_redaction_confirmation_placeholders(
    value: Any,
    issues: list[DevHubReadOnlyObservationReviewerDispositionQueueIssue],
) -> set[str]:
    ids: set[str] = set()
    if not _is_non_empty_sequence(value):
        return ids
    for index, placeholder in enumerate(value):
        path = f"redaction_confirmation_placeholders[{index}]"
        if not isinstance(placeholder, Mapping):
            _add_issue(issues, "invalid_redaction_confirmation_placeholder", path, "redaction placeholders must be objects")
            continue
        placeholder_id = _string_value(placeholder.get("placeholder_id") or placeholder.get("id"))
        if not placeholder_id:
            _add_issue(issues, "missing_redaction_confirmation_placeholder_id", f"{path}.placeholder_id", "placeholder_id is required")
        else:
            ids.add(placeholder_id)
        if _string_value(placeholder.get("status")) not in {"placeholder_only", "pending_human_confirmation"}:
            _add_issue(
                issues,
                "invalid_redaction_confirmation_placeholder_status",
                f"{path}.status",
                "redaction placeholders must remain placeholder_only or pending_human_confirmation",
            )
    return ids


def _validate_blocked_action_carry_forward_notes(
    value: Any,
    issues: list[DevHubReadOnlyObservationReviewerDispositionQueueIssue],
) -> set[str]:
    ids: set[str] = set()
    if not _is_non_empty_sequence(value):
        return ids
    for index, note in enumerate(value):
        path = f"blocked_action_carry_forward_notes[{index}]"
        if not isinstance(note, Mapping):
            _add_issue(issues, "invalid_blocked_action_carry_forward_note", path, "blocked-action notes must be objects")
            continue
        note_id = _string_value(note.get("note_id") or note.get("id"))
        if not note_id:
            _add_issue(issues, "missing_blocked_action_carry_forward_note_id", f"{path}.note_id", "note_id is required")
        else:
            ids.add(note_id)
        if not _string_value(note.get("note")):
            _add_issue(issues, "missing_blocked_action_carry_forward_note", f"{path}.note", "note is required")
    return ids


def _validate_rollback_checkpoints(
    value: Any,
    issues: list[DevHubReadOnlyObservationReviewerDispositionQueueIssue],
) -> set[str]:
    ids: set[str] = set()
    if not _is_non_empty_sequence(value):
        return ids
    for index, checkpoint in enumerate(value):
        path = f"rollback_checkpoints[{index}]"
        if not isinstance(checkpoint, Mapping):
            _add_issue(issues, "invalid_rollback_checkpoint", path, "rollback checkpoints must be objects")
            continue
        checkpoint_id = _string_value(checkpoint.get("checkpoint_id") or checkpoint.get("id"))
        if not checkpoint_id:
            _add_issue(issues, "missing_rollback_checkpoint_id", f"{path}.checkpoint_id", "checkpoint_id is required")
        else:
            ids.add(checkpoint_id)
        if not _string_value(checkpoint.get("restore_note")):
            _add_issue(issues, "missing_rollback_restore_note", f"{path}.restore_note", "restore_note is required")
    return ids


def _validate_validation_commands(
    value: Any,
    issues: list[DevHubReadOnlyObservationReviewerDispositionQueueIssue],
) -> None:
    if not _is_non_empty_sequence(value):
        return
    for index, command in enumerate(value):
        path = f"validation_commands[{index}]"
        if not _is_non_empty_sequence(command) or not all(isinstance(part, str) and part for part in command):
            _add_issue(issues, "invalid_validation_command", path, "validation commands must be non-empty argv lists")


def _validate_artifact_policy(
    value: Any,
    issues: list[DevHubReadOnlyObservationReviewerDispositionQueueIssue],
) -> None:
    if not isinstance(value, Mapping):
        _add_issue(issues, "invalid_artifact_policy", "artifact_policy", "artifact_policy must be an object")
        return
    for key in _ARTIFACT_POLICY_KEYS:
        if value.get(key) is not False:
            _add_issue(issues, "artifact_policy_not_false", f"artifact_policy.{key}", f"artifact_policy.{key} must be false")


def _validate_mutation_flags(
    value: Any,
    path: str,
    issues: list[DevHubReadOnlyObservationReviewerDispositionQueueIssue],
) -> None:
    if not isinstance(value, Mapping):
        _add_issue(issues, "invalid_mutation_flags", path, "mutation_flags must be an object")
        return
    for key, child in value.items():
        child_path = f"{path}.{key}"
        if key in _MUTATION_FLAG_KEYS and _active_flag(child):
            _add_issue(issues, "active_mutation_flag", child_path, "mutation flags must be false or absent")
        if isinstance(child, Mapping):
            _validate_mutation_flags(child, child_path, issues)


def _scan_for_rejected_content(
    value: Any,
    issues: list[DevHubReadOnlyObservationReviewerDispositionQueueIssue],
) -> None:
    for path, text in _walk_text(value):
        searchable = _normalize_search_text(text)
        if _contains_any(searchable, _PRIVATE_ARTIFACT_TERMS):
            _add_issue(issues, "private_or_session_artifact_language", path, "queue must not reference private/authenticated/session/browser artifacts")
        if _contains_any(searchable, _CAPTURE_ARTIFACT_TERMS):
            _add_issue(issues, "browser_capture_artifact_language", path, "queue must not reference screenshots, traces, HAR, or auth files")
        if _contains_any(searchable, _RAW_DATA_TERMS):
            _add_issue(issues, "raw_or_downloaded_data_language", path, "queue must not reference raw crawl, raw PDF, or downloaded data")
        if _contains_any(searchable, _LIVE_EXECUTION_OR_PROMOTION_TERMS):
            _add_issue(issues, "live_execution_or_observation_promotion_claim", path, "queue must not claim live authenticated execution or observation promotion")
        if _contains_any(searchable, _OUTCOME_GUARANTEE_TERMS):
            _add_issue(issues, "legal_or_permitting_outcome_guarantee", path, "queue must not guarantee legal or permitting outcomes")
        if _contains_any(searchable, _CONSEQUENTIAL_ACTION_TERMS):
            _add_issue(issues, "consequential_action_language", path, "queue must not include payment, submission, scheduling, cancellation, certification, or upload language")


def _require_known_ref(
    row: Mapping[str, Any],
    key: str,
    known_ids: set[str],
    row_path: str,
    code: str,
    issues: list[DevHubReadOnlyObservationReviewerDispositionQueueIssue],
) -> None:
    value = _string_value(row.get(key))
    if not value:
        _add_issue(issues, code, f"{row_path}.{key}", f"{key} is required")
    elif value not in known_ids:
        _add_issue(issues, code, f"{row_path}.{key}", f"{key} must reference a declared queue item")


def _require_non_empty_sequence(
    mapping: Mapping[str, Any],
    key: str,
    issues: list[DevHubReadOnlyObservationReviewerDispositionQueueIssue],
) -> None:
    if not _is_non_empty_sequence(mapping.get(key)):
        _add_issue(issues, f"missing_{key}", key, f"{key} must be a non-empty list")


def _has_citation(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if not isinstance(value, Sequence) or isinstance(value, (bytes, bytearray, str)):
        return False
    for item in value:
        if isinstance(item, str) and item.strip():
            return True
        if isinstance(item, Mapping):
            if _string_value(item.get("source_id") or item.get("source_evidence_id")):
                return True
            url = _string_value(item.get("url") or item.get("canonical_url"))
            if url.startswith("https://www.portland.gov/"):
                return True
    return False


def _has_non_empty_string_sequence(value: Any) -> bool:
    return _is_non_empty_sequence(value) and any(isinstance(item, str) and item.strip() for item in value)


def _is_non_empty_sequence(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray, str)) and len(value) > 0


def _walk_text(value: Any, path: str = "$.") -> list[tuple[str, str]]:
    if isinstance(value, str):
        return [(path.rstrip("."), value)]
    if isinstance(value, Mapping):
        rows: list[tuple[str, str]] = []
        for key, child in value.items():
            rows.extend(_walk_text(child, f"{path}{key}."))
        return rows
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray, str)):
        rows = []
        for index, child in enumerate(value):
            rows.extend(_walk_text(child, f"{path.rstrip('.')}[{index}]."))
        return rows
    return []


def _normalize_search_text(text: str) -> str:
    lowered = text.lower().replace("_", " ").replace("-", " ")
    normalized = " ".join(lowered.split())
    return normalized + " " + normalized.replace(" ", "_")


def _contains_any(text: str, terms: tuple[str, ...]) -> bool:
    return any(term in text for term in terms)


def _active_flag(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"1", "active", "enabled", "true", "yes"}
    return False


def _string_value(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _add_issue(
    issues: list[DevHubReadOnlyObservationReviewerDispositionQueueIssue],
    code: str,
    path: str,
    message: str,
) -> None:
    issues.append(DevHubReadOnlyObservationReviewerDispositionQueueIssue(code, path, message))


def _dedupe_issues(
    issues: list[DevHubReadOnlyObservationReviewerDispositionQueueIssue],
) -> list[DevHubReadOnlyObservationReviewerDispositionQueueIssue]:
    seen: set[tuple[str, str, str]] = set()
    result: list[DevHubReadOnlyObservationReviewerDispositionQueueIssue] = []
    for issue in issues:
        key = (issue.code, issue.path, issue.message)
        if key not in seen:
            seen.add(key)
            result.append(issue)
    return result
