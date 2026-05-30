"""Validation for DevHub attended observation renewal queue v1.

The queue is an offline renewal planning artifact only. It must describe
candidate read-only observations with placeholder attendance and reviewer gates,
without authenticated browser artifacts, private values, live DevHub access
claims, consequential workflow language, or active mutation flags.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

QUEUE_VERSION = "devhub_attended_observation_renewal_queue_v1"
SAFE_READ_ONLY_CLASSIFICATIONS = frozenset(
    {"safe_read_only", "safe-read-only", "read_only_observation", "read-only-observation"}
)

_REQUIRED_TOP_LEVEL_SEQUENCES = (
    "observation_candidate_rows",
    "attendance_preflight_placeholders",
    "redaction_checklist_references",
    "safe_read_only_action_classifications",
    "blocked_consequential_action_reminders",
    "reviewer_approval_placeholders",
    "validation_commands",
)

_ARTIFACT_POLICY_KEYS = (
    "captures_auth_files",
    "captures_browser_artifacts",
    "captures_har_files",
    "captures_private_page_values",
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
    "stores_raw_private_output",
)

_MUTATION_FLAG_KEYS = frozenset(
    {
        "active_agent_state_mutation",
        "active_guardrail_mutation",
        "active_prompt_mutation",
        "active_release_state_mutation",
        "active_surface_mutation",
        "agent_state_mutation_enabled",
        "guardrail_mutation_enabled",
        "mutates_agent_state",
        "mutates_guardrails",
        "mutates_prompts",
        "mutates_release_state",
        "mutates_surfaces",
        "prompt_mutation_enabled",
        "release_state_mutation_enabled",
        "surface_mutation_enabled",
    }
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
    "private page value",
    "private value",
    "session artifact",
    "session state",
    "session storage",
    "session_state",
    "storage state",
    "storage_state",
    "token",
)

_BROWSER_CAPTURE_TERMS = (
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

_LIVE_DEVHUB_ACCESS_TERMS = (
    "accessed live devhub",
    "completed authenticated run",
    "executed in devhub",
    "live authenticated execution",
    "live devhub access",
    "logged into devhub",
    "ran against live devhub",
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


@dataclass(frozen=True)
class DevHubAttendedObservationRenewalQueueIssue:
    code: str
    path: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "path": self.path, "message": self.message}


def validate_devhub_attended_observation_renewal_queue_v1(
    queue: Mapping[str, Any],
) -> list[DevHubAttendedObservationRenewalQueueIssue]:
    """Return deterministic fail-closed validation issues for a renewal queue."""

    issues: list[DevHubAttendedObservationRenewalQueueIssue] = []
    if not isinstance(queue, Mapping):
        return [DevHubAttendedObservationRenewalQueueIssue("invalid_queue", "$", "queue must be an object")]

    version = queue.get("queue_version") or queue.get("packet_version")
    if version != QUEUE_VERSION:
        _add_issue(issues, "invalid_queue_version", "queue_version", f"queue_version must be {QUEUE_VERSION}")

    for key in _REQUIRED_TOP_LEVEL_SEQUENCES:
        _require_non_empty_sequence(queue, key, issues)

    attendance_ids = _collect_placeholder_ids(
        queue.get("attendance_preflight_placeholders"),
        "attendance_preflight_placeholders",
        "attendance_preflight_placeholder_id",
        {"placeholder_only", "pending_attended_preflight"},
        issues,
    )
    redaction_ids = _collect_reference_ids(
        queue.get("redaction_checklist_references"),
        "redaction_checklist_references",
        "redaction_checklist_reference_id",
        issues,
    )
    classification_ids = _validate_safe_read_only_action_classifications(
        queue.get("safe_read_only_action_classifications"),
        issues,
    )
    blocked_ids = _collect_reference_ids(
        queue.get("blocked_consequential_action_reminders"),
        "blocked_consequential_action_reminders",
        "blocked_consequential_action_reminder_id",
        issues,
    )
    reviewer_ids = _collect_placeholder_ids(
        queue.get("reviewer_approval_placeholders"),
        "reviewer_approval_placeholders",
        "reviewer_approval_placeholder_id",
        {"placeholder_only", "pending_reviewer_approval"},
        issues,
    )

    _validate_observation_candidate_rows(
        queue.get("observation_candidate_rows"),
        attendance_ids,
        redaction_ids,
        classification_ids,
        blocked_ids,
        reviewer_ids,
        issues,
    )
    _validate_validation_commands(queue.get("validation_commands"), issues)
    _validate_artifact_policy(queue.get("artifact_policy", {}), issues)
    _validate_mutation_flags(queue.get("mutation_flags", {}), "mutation_flags", issues)
    _scan_rejected_text(queue, issues)
    return _dedupe_issues(issues)


def validate_queue(queue: Mapping[str, Any]) -> list[DevHubAttendedObservationRenewalQueueIssue]:
    return validate_devhub_attended_observation_renewal_queue_v1(queue)


def assert_valid_devhub_attended_observation_renewal_queue_v1(queue: Mapping[str, Any]) -> None:
    issues = validate_devhub_attended_observation_renewal_queue_v1(queue)
    if issues:
        formatted = "; ".join(f"{issue.code} at {issue.path}" for issue in issues)
        raise AssertionError("invalid DevHub attended observation renewal queue v1: " + formatted)


def _validate_observation_candidate_rows(
    value: Any,
    attendance_ids: set[str],
    redaction_ids: set[str],
    classification_ids: set[str],
    blocked_ids: set[str],
    reviewer_ids: set[str],
    issues: list[DevHubAttendedObservationRenewalQueueIssue],
) -> None:
    if not _is_non_empty_sequence(value):
        return
    seen_ids: set[str] = set()
    for index, row in enumerate(value):
        path = f"observation_candidate_rows[{index}]"
        if not isinstance(row, Mapping):
            _add_issue(issues, "invalid_observation_candidate_row", path, "observation candidate rows must be objects")
            continue

        row_id = _string_value(row.get("candidate_id") or row.get("row_id") or row.get("id"))
        if not row_id:
            _add_issue(issues, "missing_observation_candidate_row_id", f"{path}.candidate_id", "candidate_id is required")
        elif row_id in seen_ids:
            _add_issue(issues, "duplicate_observation_candidate_row_id", f"{path}.candidate_id", "candidate_id must be unique")
        else:
            seen_ids.add(row_id)

        for key in ("surface_id", "renewal_reason", "reviewer_owner"):
            if not _string_value(row.get(key)):
                _add_issue(issues, f"missing_{key}", f"{path}.{key}", f"{key} is required")

        if not _has_citation(row.get("citations")) and not _has_non_empty_string_sequence(row.get("source_evidence_ids")):
            _add_issue(
                issues,
                "uncited_observation_candidate_row",
                f"{path}.citations",
                "observation candidates must cite public source evidence or offline fixture evidence",
            )

        _require_known_ref(row, "attendance_preflight_placeholder_id", attendance_ids, path, issues)
        _require_known_ref(row, "redaction_checklist_reference_id", redaction_ids, path, issues)
        _require_known_ref(row, "safe_read_only_action_classification_id", classification_ids, path, issues)
        _require_known_ref(row, "blocked_consequential_action_reminder_id", blocked_ids, path, issues)
        _require_known_ref(row, "reviewer_approval_placeholder_id", reviewer_ids, path, issues)


def _collect_placeholder_ids(
    value: Any,
    path_name: str,
    id_key: str,
    allowed_statuses: set[str],
    issues: list[DevHubAttendedObservationRenewalQueueIssue],
) -> set[str]:
    ids: set[str] = set()
    if not _is_non_empty_sequence(value):
        return ids
    for index, item in enumerate(value):
        path = f"{path_name}[{index}]"
        if not isinstance(item, Mapping):
            _add_issue(issues, f"invalid_{path_name}", path, f"{path_name} entries must be objects")
            continue
        item_id = _string_value(item.get(id_key) or item.get("id"))
        if not item_id:
            _add_issue(issues, f"missing_{id_key}", f"{path}.{id_key}", f"{id_key} is required")
        else:
            ids.add(item_id)
        if _string_value(item.get("status")) not in allowed_statuses:
            _add_issue(issues, f"invalid_{path_name}_status", f"{path}.status", "placeholder status is not allowed")
    return ids


def _collect_reference_ids(
    value: Any,
    path_name: str,
    id_key: str,
    issues: list[DevHubAttendedObservationRenewalQueueIssue],
) -> set[str]:
    ids: set[str] = set()
    if not _is_non_empty_sequence(value):
        return ids
    for index, item in enumerate(value):
        path = f"{path_name}[{index}]"
        if not isinstance(item, Mapping):
            _add_issue(issues, f"invalid_{path_name}", path, f"{path_name} entries must be objects")
            continue
        item_id = _string_value(item.get(id_key) or item.get("id"))
        if not item_id:
            _add_issue(issues, f"missing_{id_key}", f"{path}.{id_key}", f"{id_key} is required")
        else:
            ids.add(item_id)
        if not _string_value(item.get("note") or item.get("checklist_ref") or item.get("reminder")):
            _add_issue(issues, f"missing_{path_name}_note", path, "reference note is required")
    return ids


def _validate_safe_read_only_action_classifications(
    value: Any,
    issues: list[DevHubAttendedObservationRenewalQueueIssue],
) -> set[str]:
    ids: set[str] = set()
    if not _is_non_empty_sequence(value):
        return ids
    for index, item in enumerate(value):
        path = f"safe_read_only_action_classifications[{index}]"
        if not isinstance(item, Mapping):
            _add_issue(issues, "invalid_safe_read_only_action_classification", path, "classification entries must be objects")
            continue
        item_id = _string_value(item.get("classification_id") or item.get("id"))
        if not item_id:
            _add_issue(issues, "missing_safe_read_only_action_classification_id", f"{path}.classification_id", "classification_id is required")
        else:
            ids.add(item_id)
        classification = _string_value(item.get("classification") or item.get("action_classification"))
        if classification not in SAFE_READ_ONLY_CLASSIFICATIONS:
            _add_issue(issues, "unsafe_action_classification", f"{path}.classification", "classification must be safe_read_only")
    return ids


def _validate_validation_commands(value: Any, issues: list[DevHubAttendedObservationRenewalQueueIssue]) -> None:
    if not _is_non_empty_sequence(value):
        return
    for index, command in enumerate(value):
        path = f"validation_commands[{index}]"
        if not _is_non_empty_sequence(command) or not all(isinstance(part, str) and part for part in command):
            _add_issue(issues, "invalid_validation_command", path, "validation commands must be non-empty argv lists")


def _validate_artifact_policy(value: Any, issues: list[DevHubAttendedObservationRenewalQueueIssue]) -> None:
    if not isinstance(value, Mapping):
        _add_issue(issues, "invalid_artifact_policy", "artifact_policy", "artifact_policy must be an object")
        return
    for key in _ARTIFACT_POLICY_KEYS:
        if value.get(key) is not False:
            _add_issue(issues, "artifact_policy_not_false", f"artifact_policy.{key}", f"artifact_policy.{key} must be false")


def _validate_mutation_flags(
    value: Any,
    path: str,
    issues: list[DevHubAttendedObservationRenewalQueueIssue],
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


def _scan_rejected_text(value: Any, issues: list[DevHubAttendedObservationRenewalQueueIssue]) -> None:
    for path, text in _walk_text(value):
        searchable = _normalize_search_text(text)
        if _contains_any(searchable, _PRIVATE_ARTIFACT_TERMS):
            _add_issue(issues, "private_or_session_artifact_language", path, "queue must not reference credentials, session/auth state, browser artifacts, or private values")
        if _contains_any(searchable, _BROWSER_CAPTURE_TERMS):
            _add_issue(issues, "browser_capture_artifact_language", path, "queue must not reference screenshots, traces, HAR files, or auth files")
        if _contains_any(searchable, _LIVE_DEVHUB_ACCESS_TERMS):
            _add_issue(issues, "live_devhub_access_claim", path, "queue must not claim live DevHub access or authenticated execution")
        if _contains_any(searchable, _CONSEQUENTIAL_ACTION_TERMS) and "blocked_consequential_action_reminders" not in path:
            _add_issue(issues, "consequential_action_language", path, "queue must not include payment, submission, scheduling, cancellation, certification, or upload language outside blocked reminders")


def _require_known_ref(
    row: Mapping[str, Any],
    key: str,
    known_ids: set[str],
    row_path: str,
    issues: list[DevHubAttendedObservationRenewalQueueIssue],
) -> None:
    value = _string_value(row.get(key))
    if not value:
        _add_issue(issues, f"missing_{key}", f"{row_path}.{key}", f"{key} is required")
    elif value not in known_ids:
        _add_issue(issues, f"unknown_{key}", f"{row_path}.{key}", f"{key} must reference a declared queue item")


def _require_non_empty_sequence(
    mapping: Mapping[str, Any],
    key: str,
    issues: list[DevHubAttendedObservationRenewalQueueIssue],
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
            if _string_value(item.get("source_id") or item.get("source_evidence_id") or item.get("fixture")):
                return True
            url = _string_value(item.get("url") or item.get("canonical_url"))
            if url.startswith("https://www.portland.gov/"):
                return True
    return False


def _has_non_empty_string_sequence(value: Any) -> bool:
    return _is_non_empty_sequence(value) and any(isinstance(item, str) and item.strip() for item in value)


def _is_non_empty_sequence(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray, str)) and len(value) > 0


def _walk_text(value: Any, path: str = "$") -> list[tuple[str, str]]:
    if isinstance(value, str):
        return [(path, value)]
    if isinstance(value, Mapping):
        rows: list[tuple[str, str]] = []
        for key, child in value.items():
            rows.extend(_walk_text(child, f"{path}.{key}"))
        return rows
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray, str)):
        rows = []
        for index, child in enumerate(value):
            rows.extend(_walk_text(child, f"{path}[{index}]"))
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
    issues: list[DevHubAttendedObservationRenewalQueueIssue],
    code: str,
    path: str,
    message: str,
) -> None:
    issues.append(DevHubAttendedObservationRenewalQueueIssue(code, path, message))


def _dedupe_issues(
    issues: list[DevHubAttendedObservationRenewalQueueIssue],
) -> list[DevHubAttendedObservationRenewalQueueIssue]:
    seen: set[tuple[str, str, str]] = set()
    result: list[DevHubAttendedObservationRenewalQueueIssue] = []
    for issue in issues:
        key = (issue.code, issue.path, issue.message)
        if key not in seen:
            seen.add(key)
            result.append(issue)
    return result
