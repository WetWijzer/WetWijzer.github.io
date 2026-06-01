"""Validation for attended DevHub read-only observation renewal authorization packet v1.

The packet is a committed, fixture-first authorization artifact. It authorizes
only attended, read-only observation renewal planning and must not contain live
DevHub execution claims, login automation claims, private browser artifacts,
official-action completion claims, consequential-action claims, or active
mutation flags.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

PACKET_VERSION = "attended_devhub_read_only_observation_renewal_authorization_packet_v1"

_REQUIRED_TOP_LEVEL_SEQUENCES = (
    "attendance_prerequisites",
    "allowed_read_only_surfaces",
    "redaction_requirements",
    "stop_conditions",
    "manual_handoff_points",
    "observation_evidence_placeholders",
    "authorization_rows",
    "validation_commands",
)

_ALLOWED_READ_ONLY_CLASSIFICATIONS = frozenset(
    {
        "safe_read_only",
        "safe-read-only",
        "read_only_observation",
        "read-only-observation",
    }
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
        "active_authorization_mutation",
        "active_guardrail_mutation",
        "active_prompt_mutation",
        "active_release_state_mutation",
        "active_surface_mutation",
        "agent_state_mutation_enabled",
        "authorization_mutation_enabled",
        "guardrail_mutation_enabled",
        "mutates_agent_state",
        "mutates_authorization",
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
    "auth file",
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
    "har file",
    "network trace",
    "screenshot",
    "storage_state.json",
    "trace file",
    "trace.zip",
)

_LOGIN_AUTOMATION_TERMS = (
    "automated login",
    "automated sign in",
    "bypass captcha",
    "bypass mfa",
    "completed login",
    "completed sign in",
    "entered password",
    "logged into devhub",
    "login automation",
    "programmatic login",
    "scripted login",
)

_OFFICIAL_ACTION_COMPLETION_TERMS = (
    "completed official action",
    "official action completed",
    "payment completed",
    "permit submitted",
    "request submitted",
    "scheduled inspection",
    "submission completed",
    "upload completed",
)

_CONSEQUENTIAL_ACTION_TERMS = (
    "cancel permit",
    "certify",
    "certification",
    "make payment",
    "pay fee",
    "purchase permit",
    "schedule inspection",
    "submit application",
    "submit permit",
    "upload correction",
    "upload document",
)

_ALLOWED_CONSEQUENTIAL_CONTEXT_PATH_PARTS = (
    ".stop_conditions[",
    ".manual_handoff_points[",
)


@dataclass(frozen=True)
class DevHubReadOnlyObservationRenewalAuthorizationIssue:
    code: str
    path: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "path": self.path, "message": self.message}


def validate_devhub_read_only_observation_renewal_authorization_packet_v1(
    packet: Mapping[str, Any],
) -> list[DevHubReadOnlyObservationRenewalAuthorizationIssue]:
    """Return deterministic fail-closed validation issues for the packet."""

    issues: list[DevHubReadOnlyObservationRenewalAuthorizationIssue] = []
    if not isinstance(packet, Mapping):
        return [
            DevHubReadOnlyObservationRenewalAuthorizationIssue(
                "invalid_packet",
                "$",
                "packet must be an object",
            )
        ]

    version = packet.get("packet_version") or packet.get("authorization_packet_version")
    if version != PACKET_VERSION:
        _add_issue(issues, "invalid_packet_version", "packet_version", f"packet_version must be {PACKET_VERSION}")

    for key in _REQUIRED_TOP_LEVEL_SEQUENCES:
        _require_non_empty_sequence(packet, key, issues)

    attendance_ids = _collect_ids(
        packet.get("attendance_prerequisites"),
        "attendance_prerequisites",
        "attendance_prerequisite_id",
        issues,
        required_statuses={"placeholder_only", "pending_attended_confirmation", "required"},
    )
    surface_ids = _collect_allowed_surface_ids(packet.get("allowed_read_only_surfaces"), issues)
    redaction_ids = _collect_ids(
        packet.get("redaction_requirements"),
        "redaction_requirements",
        "redaction_requirement_id",
        issues,
        require_note=True,
    )
    stop_ids = _collect_ids(packet.get("stop_conditions"), "stop_conditions", "stop_condition_id", issues, require_note=True)
    handoff_ids = _collect_ids(
        packet.get("manual_handoff_points"),
        "manual_handoff_points",
        "manual_handoff_point_id",
        issues,
        require_note=True,
    )
    evidence_ids = _collect_ids(
        packet.get("observation_evidence_placeholders"),
        "observation_evidence_placeholders",
        "evidence_placeholder_id",
        issues,
        required_statuses={"placeholder_only", "pending_observation", "metadata_only"},
    )

    _validate_authorization_rows(
        packet.get("authorization_rows"),
        attendance_ids,
        surface_ids,
        redaction_ids,
        stop_ids,
        handoff_ids,
        evidence_ids,
        issues,
    )
    _validate_validation_commands(packet.get("validation_commands"), issues)
    _validate_artifact_policy(packet.get("artifact_policy", {}), issues)
    _validate_mutation_flags(packet.get("mutation_flags", {}), "mutation_flags", issues)
    _scan_rejected_text(packet, issues)
    return _dedupe_issues(issues)


def validate_packet(packet: Mapping[str, Any]) -> list[DevHubReadOnlyObservationRenewalAuthorizationIssue]:
    return validate_devhub_read_only_observation_renewal_authorization_packet_v1(packet)


def assert_valid_devhub_read_only_observation_renewal_authorization_packet_v1(packet: Mapping[str, Any]) -> None:
    issues = validate_devhub_read_only_observation_renewal_authorization_packet_v1(packet)
    if issues:
        formatted = "; ".join(f"{issue.code} at {issue.path}" for issue in issues)
        raise AssertionError("invalid DevHub read-only observation renewal authorization packet v1: " + formatted)


def _validate_authorization_rows(
    value: Any,
    attendance_ids: set[str],
    surface_ids: set[str],
    redaction_ids: set[str],
    stop_ids: set[str],
    handoff_ids: set[str],
    evidence_ids: set[str],
    issues: list[DevHubReadOnlyObservationRenewalAuthorizationIssue],
) -> None:
    if not _is_non_empty_sequence(value):
        return

    seen_ids: set[str] = set()
    for index, row in enumerate(value):
        path = f"authorization_rows[{index}]"
        if not isinstance(row, Mapping):
            _add_issue(issues, "invalid_authorization_row", path, "authorization rows must be objects")
            continue

        row_id = _string_value(row.get("authorization_row_id") or row.get("row_id") or row.get("id"))
        if not row_id:
            _add_issue(issues, "missing_authorization_row_id", f"{path}.authorization_row_id", "authorization_row_id is required")
        elif row_id in seen_ids:
            _add_issue(issues, "duplicate_authorization_row_id", f"{path}.authorization_row_id", "authorization_row_id must be unique")
        else:
            seen_ids.add(row_id)

        for key in ("authorization_scope", "reviewer_owner", "renewal_reason"):
            if not _string_value(row.get(key)):
                _add_issue(issues, f"missing_{key}", f"{path}.{key}", f"{key} is required")

        _require_known_ref(row, "attendance_prerequisite_id", attendance_ids, path, issues)
        _require_known_ref(row, "surface_id", surface_ids, path, issues)
        _require_known_ref(row, "redaction_requirement_id", redaction_ids, path, issues)
        _require_known_ref(row, "stop_condition_id", stop_ids, path, issues)
        _require_known_ref(row, "manual_handoff_point_id", handoff_ids, path, issues)
        _require_known_ref(row, "evidence_placeholder_id", evidence_ids, path, issues)

        if not _has_citation(row.get("source_evidence_ids")) and not _has_citation(row.get("citations")):
            _add_issue(
                issues,
                "uncited_authorization_row",
                f"{path}.source_evidence_ids",
                "authorization rows must cite public source evidence or offline fixture evidence",
            )


def _collect_allowed_surface_ids(
    value: Any,
    issues: list[DevHubReadOnlyObservationRenewalAuthorizationIssue],
) -> set[str]:
    ids: set[str] = set()
    if not _is_non_empty_sequence(value):
        return ids
    for index, item in enumerate(value):
        path = f"allowed_read_only_surfaces[{index}]"
        if not isinstance(item, Mapping):
            _add_issue(issues, "invalid_allowed_read_only_surface", path, "allowed read-only surfaces must be objects")
            continue
        surface_id = _string_value(item.get("surface_id") or item.get("id"))
        if not surface_id:
            _add_issue(issues, "missing_surface_id", f"{path}.surface_id", "surface_id is required")
        else:
            ids.add(surface_id)
        classification = _string_value(item.get("classification") or item.get("action_classification"))
        if classification not in _ALLOWED_READ_ONLY_CLASSIFICATIONS:
            _add_issue(issues, "surface_not_read_only", f"{path}.classification", "surface classification must be safe read-only")
        if item.get("requires_attendance") is not True:
            _add_issue(issues, "surface_missing_attendance_requirement", f"{path}.requires_attendance", "read-only observation renewal requires attendance")
        if item.get("allows_mutation") is not False:
            _add_issue(issues, "surface_allows_mutation", f"{path}.allows_mutation", "read-only surfaces must explicitly disallow mutation")
    return ids


def _collect_ids(
    value: Any,
    path_name: str,
    id_key: str,
    issues: list[DevHubReadOnlyObservationRenewalAuthorizationIssue],
    *,
    required_statuses: set[str] | None = None,
    require_note: bool = False,
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
        if required_statuses is not None and _string_value(item.get("status")) not in required_statuses:
            _add_issue(issues, f"invalid_{path_name}_status", f"{path}.status", "entry status is not allowed")
        if require_note and not _string_value(item.get("note") or item.get("requirement") or item.get("condition")):
            _add_issue(issues, f"missing_{path_name}_note", path, "entry note, requirement, or condition is required")
    return ids


def _validate_validation_commands(
    value: Any,
    issues: list[DevHubReadOnlyObservationRenewalAuthorizationIssue],
) -> None:
    if not _is_non_empty_sequence(value):
        return
    for index, command in enumerate(value):
        path = f"validation_commands[{index}]"
        if not _is_non_empty_sequence(command) or not all(isinstance(part, str) and part for part in command):
            _add_issue(issues, "invalid_validation_command", path, "validation commands must be non-empty argv lists")
            continue
        command_text = " ".join(part.lower() for part in command)
        if any(token in command_text for token in ("playwright", "browser", "devhub", "login", "auth", "crawl")):
            _add_issue(issues, "unsafe_validation_command", path, "validation commands must remain offline and fixture-only")


def _validate_artifact_policy(
    value: Any,
    issues: list[DevHubReadOnlyObservationRenewalAuthorizationIssue],
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
    issues: list[DevHubReadOnlyObservationRenewalAuthorizationIssue],
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


def _scan_rejected_text(value: Any, issues: list[DevHubReadOnlyObservationRenewalAuthorizationIssue]) -> None:
    for path, text in _walk_text(value):
        searchable = _normalize_search_text(text)
        if _contains_any(searchable, _PRIVATE_ARTIFACT_TERMS):
            _add_issue(issues, "private_or_session_artifact_language", path, "packet must not reference credentials, session state, browser artifacts, or private values")
        if _contains_any(searchable, _BROWSER_CAPTURE_TERMS):
            _add_issue(issues, "browser_capture_artifact_language", path, "packet must not reference screenshots, traces, HAR files, or auth files")
        if _contains_any(searchable, _LOGIN_AUTOMATION_TERMS):
            _add_issue(issues, "devhub_login_automation_claim", path, "packet must not claim DevHub login automation")
        if _contains_any(searchable, _OFFICIAL_ACTION_COMPLETION_TERMS):
            _add_issue(issues, "official_action_completion_claim", path, "packet must not claim official-action completion")
        if _contains_any(searchable, _CONSEQUENTIAL_ACTION_TERMS) and not _path_allows_consequential_context(path):
            _add_issue(issues, "consequential_action_claim", path, "packet must not include consequential-action claims outside stop and handoff safeguards")


def _path_allows_consequential_context(path: str) -> bool:
    return any(part in path for part in _ALLOWED_CONSEQUENTIAL_CONTEXT_PATH_PARTS)


def _require_known_ref(
    row: Mapping[str, Any],
    key: str,
    known_ids: set[str],
    row_path: str,
    issues: list[DevHubReadOnlyObservationRenewalAuthorizationIssue],
) -> None:
    value = _string_value(row.get(key))
    if not value:
        _add_issue(issues, f"missing_{key}", f"{row_path}.{key}", f"{key} is required")
    elif value not in known_ids:
        _add_issue(issues, f"unknown_{key}", f"{row_path}.{key}", f"{key} must reference a declared packet item")


def _require_non_empty_sequence(
    mapping: Mapping[str, Any],
    key: str,
    issues: list[DevHubReadOnlyObservationRenewalAuthorizationIssue],
) -> None:
    if not _is_non_empty_sequence(mapping.get(key)):
        _add_issue(issues, f"missing_{key}", key, f"{key} must be a non-empty list")


def _has_citation(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if not _is_non_empty_sequence(value):
        return False
    for item in value:
        if isinstance(item, str) and item.strip():
            return True
        if isinstance(item, Mapping) and _string_value(item.get("source_id") or item.get("source_evidence_id") or item.get("fixture")):
            return True
    return False


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
    issues: list[DevHubReadOnlyObservationRenewalAuthorizationIssue],
    code: str,
    path: str,
    message: str,
) -> None:
    issues.append(DevHubReadOnlyObservationRenewalAuthorizationIssue(code, path, message))


def _dedupe_issues(
    issues: list[DevHubReadOnlyObservationRenewalAuthorizationIssue],
) -> list[DevHubReadOnlyObservationRenewalAuthorizationIssue]:
    seen: set[tuple[str, str, str]] = set()
    result: list[DevHubReadOnlyObservationRenewalAuthorizationIssue] = []
    for issue in issues:
        key = (issue.code, issue.path, issue.message)
        if key not in seen:
            seen.add(key)
            result.append(issue)
    return result
