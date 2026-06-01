"""Validation for DevHub read-only surface delta packet v1.

This module is intentionally fixture-first. It validates offline, redacted
candidate delta packets for DevHub read-only surfaces and rejects packets that
omit required evidence/control rows or that claim live DevHub/crawl execution,
official action completion, promotion, consequential action handling, private
artifacts, or active mutation.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

PACKET_VERSION = "devhub_read_only_surface_delta_packet_v1"
VALIDATION_COMMANDS = [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]]

_REQUIRED_SEQUENCES = (
    "observation_evidence_refs",
    "candidate_surface_map_change_rows",
    "selector_confidence_notes",
    "action_classification_checks",
    "redaction_policy_impacts",
    "attendance_or_exact_confirmation_requirements",
    "unsupported_or_manual_handoff_paths",
    "reviewer_holds",
    "validation_commands",
)

_PRIVATE_ARTIFACT_TERMS = (
    "auth state",
    "browser artifact",
    "browser context",
    "browser state",
    "cookie",
    "credential",
    "credentials",
    "devhub session",
    "local private path",
    "password",
    "private artifact",
    "private file",
    "private value",
    "session artifact",
    "session file",
    "session state",
    "storage state",
    "token",
)

_BROWSER_RAW_TERMS = (
    ".har",
    "downloaded document",
    "downloaded pdf",
    "har file",
    "network trace",
    "raw authenticated",
    "raw crawl",
    "raw download",
    "raw html",
    "screenshot",
    "trace file",
    "trace.zip",
)

_LIVE_CLAIM_TERMS = (
    "crawled live",
    "executed in devhub",
    "launched devhub",
    "live crawl",
    "live devhub",
    "opened devhub",
    "ran against devhub",
    "real devhub account",
)

_OFFICIAL_COMPLETION_TERMS = (
    "application submitted",
    "certification completed",
    "inspection scheduled",
    "official action completed",
    "payment completed",
    "permit approved",
    "permit issued",
    "submitted successfully",
    "upload completed",
)

_CONSEQUENTIAL_ACTION_TERMS = (
    "cancel inspection",
    "cancel permit",
    "certify acknowledgement",
    "pay fee",
    "purchase permit",
    "schedule inspection",
    "submit application",
    "submit permit",
    "upload correction",
    "withdraw application",
)

_PROMOTION_CLAIM_TERMS = (
    "active promotion",
    "approved for promotion",
    "promote to active",
    "promoted surface map",
    "promotion complete",
    "promotion completed",
    "ready for release",
)

_MUTATION_FLAG_KEYS = frozenset(
    {
        "active_mutation",
        "active_registry_mutation",
        "active_surface_map_mutation",
        "active_devhub_surface_mutation",
        "surface_map_mutation_enabled",
        "devhub_surface_mutation_enabled",
        "registry_mutation_enabled",
        "mutates_active_surface_map",
        "mutates_surface_map",
        "mutates_registry",
        "writes_active_surface_map",
        "writes_surface_registry",
    }
)

_ARTIFACT_POLICY_KEYS = (
    "captures_credentials",
    "captures_session_state",
    "captures_browser_artifacts",
    "captures_screenshots",
    "captures_traces",
    "captures_har_files",
    "captures_private_values",
    "stores_raw_crawl_output",
    "stores_raw_devhub_output",
    "stores_downloaded_documents",
)


@dataclass(frozen=True)
class DevHubReadOnlySurfaceDeltaPacketV1Issue:
    code: str
    path: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "path": self.path, "message": self.message}


def validate_devhub_read_only_surface_delta_packet_v1(
    packet: Mapping[str, Any],
) -> list[DevHubReadOnlySurfaceDeltaPacketV1Issue]:
    """Return deterministic validation issues for a read-only delta packet."""

    issues: list[DevHubReadOnlySurfaceDeltaPacketV1Issue] = []
    if not isinstance(packet, Mapping):
        return [DevHubReadOnlySurfaceDeltaPacketV1Issue("invalid_packet", "$", "packet must be an object")]

    if packet.get("packet_version") != PACKET_VERSION:
        _add(issues, "invalid_packet_version", "packet_version", f"packet_version must be {PACKET_VERSION}")

    for key in _REQUIRED_SEQUENCES:
        if not _is_non_empty_sequence(packet.get(key)):
            _add(issues, f"missing_{key}", key, f"{key} must be a non-empty list")

    evidence_ids = _validate_id_rows(packet.get("observation_evidence_refs"), "observation_evidence_refs", "evidence_ref_id", issues)
    selector_note_ids = _validate_id_rows(packet.get("selector_confidence_notes"), "selector_confidence_notes", "note_id", issues)
    action_check_ids = _validate_id_rows(packet.get("action_classification_checks"), "action_classification_checks", "check_id", issues)
    redaction_impact_ids = _validate_id_rows(packet.get("redaction_policy_impacts"), "redaction_policy_impacts", "impact_id", issues)
    attendance_ids = _validate_id_rows(packet.get("attendance_or_exact_confirmation_requirements"), "attendance_or_exact_confirmation_requirements", "requirement_id", issues)
    handoff_ids = _validate_id_rows(packet.get("unsupported_or_manual_handoff_paths"), "unsupported_or_manual_handoff_paths", "path_id", issues)
    hold_ids = _validate_id_rows(packet.get("reviewer_holds"), "reviewer_holds", "hold_id", issues)

    _validate_candidate_rows(
        packet.get("candidate_surface_map_change_rows"),
        evidence_ids,
        selector_note_ids,
        action_check_ids,
        redaction_impact_ids,
        attendance_ids,
        handoff_ids,
        hold_ids,
        issues,
    )
    _validate_action_checks(packet.get("action_classification_checks"), issues)
    _validate_redaction_impacts(packet.get("redaction_policy_impacts"), issues)
    _validate_attendance_requirements(packet.get("attendance_or_exact_confirmation_requirements"), issues)
    _validate_handoff_paths(packet.get("unsupported_or_manual_handoff_paths"), issues)
    _validate_reviewer_holds(packet.get("reviewer_holds"), issues)
    _validate_validation_commands(packet.get("validation_commands"), issues)
    _validate_artifact_policy(packet.get("artifact_policy", {}), issues)
    _validate_mutation_flags(packet.get("mutation_flags", {}), "mutation_flags", issues)
    _scan_rejected_text(packet, issues)
    return _dedupe(issues)


def validate_packet(packet: Mapping[str, Any]) -> list[DevHubReadOnlySurfaceDeltaPacketV1Issue]:
    return validate_devhub_read_only_surface_delta_packet_v1(packet)


def assert_valid_devhub_read_only_surface_delta_packet_v1(packet: Mapping[str, Any]) -> None:
    issues = validate_devhub_read_only_surface_delta_packet_v1(packet)
    if issues:
        formatted = "; ".join(f"{issue.code} at {issue.path}" for issue in issues)
        raise AssertionError("invalid DevHub read-only surface delta packet v1: " + formatted)


def _validate_candidate_rows(
    value: Any,
    evidence_ids: set[str],
    selector_note_ids: set[str],
    action_check_ids: set[str],
    redaction_impact_ids: set[str],
    attendance_ids: set[str],
    handoff_ids: set[str],
    hold_ids: set[str],
    issues: list[DevHubReadOnlySurfaceDeltaPacketV1Issue],
) -> None:
    if not _is_non_empty_sequence(value):
        return
    seen: set[str] = set()
    for index, row in enumerate(value):
        path = f"candidate_surface_map_change_rows[{index}]"
        if not isinstance(row, Mapping):
            _add(issues, "invalid_candidate_surface_map_change_row", path, "candidate rows must be objects")
            continue
        row_id = _text(row.get("candidate_row_id") or row.get("row_id"))
        if not row_id:
            _add(issues, "missing_candidate_row_id", f"{path}.candidate_row_id", "candidate_row_id is required")
        elif row_id in seen:
            _add(issues, "duplicate_candidate_row_id", f"{path}.candidate_row_id", "candidate_row_id must be unique")
        else:
            seen.add(row_id)
        if row.get("candidate_only") is not True:
            _add(issues, "candidate_row_not_candidate_only", f"{path}.candidate_only", "candidate rows must remain candidate_only")
        if row.get("active_mutation") is not False:
            _add(issues, "active_mutation_flag", f"{path}.active_mutation", "candidate rows must not enable active mutation")
        for key in ("surface_id", "change_type", "reviewer_owner", "review_status"):
            if not _text(row.get(key)):
                _add(issues, f"missing_{key}", f"{path}.{key}", f"{key} is required")
        _require_refs(row, "observation_evidence_ref_ids", evidence_ids, path, "missing_observation_evidence_refs", issues)
        _require_refs(row, "selector_confidence_note_ids", selector_note_ids, path, "missing_selector_confidence_notes", issues)
        _require_refs(row, "action_classification_check_ids", action_check_ids, path, "missing_action_classification_checks", issues)
        _require_refs(row, "redaction_policy_impact_ids", redaction_impact_ids, path, "missing_redaction_policy_impacts", issues)
        _require_refs(row, "attendance_or_exact_confirmation_requirement_ids", attendance_ids, path, "missing_attendance_or_exact_confirmation_requirements", issues)
        _require_refs(row, "unsupported_or_manual_handoff_path_ids", handoff_ids, path, "missing_unsupported_or_manual_handoff_paths", issues)
        _require_refs(row, "reviewer_hold_ids", hold_ids, path, "missing_reviewer_holds", issues)


def _validate_action_checks(value: Any, issues: list[DevHubReadOnlySurfaceDeltaPacketV1Issue]) -> None:
    for index, row in enumerate(_sequence(value)):
        path = f"action_classification_checks[{index}]"
        if not isinstance(row, Mapping):
            continue
        if _text(row.get("classification")) != "read_only":
            _add(issues, "action_classification_not_read_only", f"{path}.classification", "action checks must classify the row as read_only")
        if row.get("consequential_action_blocked") is not True:
            _add(issues, "consequential_action_not_blocked", f"{path}.consequential_action_blocked", "consequential actions must be blocked")
        if row.get("official_action_completed") is not False:
            _add(issues, "official_action_completion_claim", f"{path}.official_action_completed", "official action completion must be false")


def _validate_redaction_impacts(value: Any, issues: list[DevHubReadOnlySurfaceDeltaPacketV1Issue]) -> None:
    for index, row in enumerate(_sequence(value)):
        path = f"redaction_policy_impacts[{index}]"
        if not isinstance(row, Mapping):
            continue
        if row.get("redaction_required") is not True:
            _add(issues, "redaction_policy_impact_missing_required_redaction", f"{path}.redaction_required", "redaction_required must be true")
        if row.get("private_values_retained") is not False:
            _add(issues, "redaction_policy_retains_private_values", f"{path}.private_values_retained", "private_values_retained must be false")


def _validate_attendance_requirements(value: Any, issues: list[DevHubReadOnlySurfaceDeltaPacketV1Issue]) -> None:
    for index, row in enumerate(_sequence(value)):
        path = f"attendance_or_exact_confirmation_requirements[{index}]"
        if not isinstance(row, Mapping):
            continue
        if row.get("requires_attendance") is not True and row.get("requires_exact_confirmation") is not True:
            _add(issues, "missing_attendance_or_exact_confirmation_requirement", path, "each requirement must require attendance or exact confirmation")
        if row.get("automation_can_proceed_unattended") is not False:
            _add(issues, "unattended_automation_not_blocked", f"{path}.automation_can_proceed_unattended", "unattended automation must be false")


def _validate_handoff_paths(value: Any, issues: list[DevHubReadOnlySurfaceDeltaPacketV1Issue]) -> None:
    for index, row in enumerate(_sequence(value)):
        path = f"unsupported_or_manual_handoff_paths[{index}]"
        if not isinstance(row, Mapping):
            continue
        if _text(row.get("disposition")) not in {"manual_handoff", "unsupported_deferred", "refused"}:
            _add(issues, "missing_unsupported_or_manual_handoff_path", f"{path}.disposition", "handoff paths must defer, hand off, or refuse unsupported work")


def _validate_reviewer_holds(value: Any, issues: list[DevHubReadOnlySurfaceDeltaPacketV1Issue]) -> None:
    for index, row in enumerate(_sequence(value)):
        path = f"reviewer_holds[{index}]"
        if not isinstance(row, Mapping):
            continue
        if row.get("hold_active") is not True:
            _add(issues, "reviewer_hold_not_active", f"{path}.hold_active", "reviewer holds must be active")
        if not _text(row.get("reviewer_role")):
            _add(issues, "missing_reviewer_role", f"{path}.reviewer_role", "reviewer_role is required")


def _validate_validation_commands(value: Any, issues: list[DevHubReadOnlySurfaceDeltaPacketV1Issue]) -> None:
    if not _is_non_empty_sequence(value):
        return
    if value != VALIDATION_COMMANDS:
        _add(issues, "unexpected_validation_commands", "validation_commands", "validation_commands must contain only the PP&D daemon self-test command")


def _validate_artifact_policy(value: Any, issues: list[DevHubReadOnlySurfaceDeltaPacketV1Issue]) -> None:
    if not isinstance(value, Mapping):
        _add(issues, "invalid_artifact_policy", "artifact_policy", "artifact_policy must be an object")
        return
    for key in _ARTIFACT_POLICY_KEYS:
        if value.get(key) is not False:
            _add(issues, "artifact_policy_not_false", f"artifact_policy.{key}", f"artifact_policy.{key} must be false")


def _validate_mutation_flags(value: Any, path: str, issues: list[DevHubReadOnlySurfaceDeltaPacketV1Issue]) -> None:
    if not isinstance(value, Mapping):
        _add(issues, "invalid_mutation_flags", path, "mutation_flags must be an object")
        return
    for key, child in value.items():
        child_path = f"{path}.{key}"
        if key in _MUTATION_FLAG_KEYS and _active_flag(child):
            _add(issues, "active_mutation_flag", child_path, "active mutation flags must be false or absent")
        if isinstance(child, Mapping):
            _validate_mutation_flags(child, child_path, issues)


def _validate_id_rows(
    value: Any,
    path: str,
    id_key: str,
    issues: list[DevHubReadOnlySurfaceDeltaPacketV1Issue],
) -> set[str]:
    ids: set[str] = set()
    for index, row in enumerate(_sequence(value)):
        row_path = f"{path}[{index}]"
        if not isinstance(row, Mapping):
            _add(issues, f"invalid_{path}", row_path, "rows must be objects")
            continue
        row_id = _text(row.get(id_key) or row.get("id"))
        if not row_id:
            _add(issues, f"missing_{id_key}", f"{row_path}.{id_key}", f"{id_key} is required")
        else:
            ids.add(row_id)
        if not _text(row.get("note") or row.get("rationale") or row.get("description")):
            _add(issues, f"missing_{path}_note", row_path, "row note, rationale, or description is required")
    return ids


def _require_refs(
    row: Mapping[str, Any],
    key: str,
    known_ids: set[str],
    row_path: str,
    code: str,
    issues: list[DevHubReadOnlySurfaceDeltaPacketV1Issue],
) -> None:
    refs = _string_sequence(row.get(key))
    if not refs:
        _add(issues, code, f"{row_path}.{key}", f"{key} must be a non-empty list")
        return
    for ref in refs:
        if ref not in known_ids:
            _add(issues, code, f"{row_path}.{key}", f"{key} must reference declared rows")


def _scan_rejected_text(value: Any, issues: list[DevHubReadOnlySurfaceDeltaPacketV1Issue]) -> None:
    for path, text in _walk_text(value):
        searchable = _normalize(text)
        if _contains_any(searchable, _PRIVATE_ARTIFACT_TERMS):
            _add(issues, "private_or_session_artifact_language", path, "packet must not reference credentials, sessions, browser state, or private artifacts")
        if _contains_any(searchable, _BROWSER_RAW_TERMS):
            _add(issues, "browser_screenshot_trace_har_or_raw_artifact_language", path, "packet must not reference screenshots, traces, HAR files, raw crawl output, or downloads")
        if _contains_any(searchable, _LIVE_CLAIM_TERMS):
            _add(issues, "live_devhub_or_crawl_claim", path, "packet must not claim live DevHub or live crawl execution")
        if _contains_any(searchable, _OFFICIAL_COMPLETION_TERMS):
            _add(issues, "official_action_completion_claim", path, "packet must not claim official-action completion")
        if _contains_any(searchable, _CONSEQUENTIAL_ACTION_TERMS):
            _add(issues, "consequential_action_claim", path, "packet must not include consequential-action claims")
        if _contains_any(searchable, _PROMOTION_CLAIM_TERMS):
            _add(issues, "promotion_claim", path, "packet must not claim promotion or release readiness")


def _sequence(value: Any) -> list[Any]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return list(value)
    return []


def _is_non_empty_sequence(value: Any) -> bool:
    return bool(_sequence(value))


def _text(value: Any) -> str:
    if isinstance(value, str):
        return value.strip()
    return ""


def _string_sequence(value: Any) -> list[str]:
    return [item.strip() for item in _sequence(value) if isinstance(item, str) and item.strip()]


def _active_flag(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"1", "active", "enabled", "true", "yes"}
    if isinstance(value, int) and not isinstance(value, bool):
        return value != 0
    return False


def _walk_text(value: Any, path: str = "$") -> list[tuple[str, str]]:
    if isinstance(value, str):
        return [(path, value)]
    if isinstance(value, Mapping):
        rows: list[tuple[str, str]] = []
        for key, child in value.items():
            rows.extend(_walk_text(child, f"{path}.{key}"))
        return rows
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        rows = []
        for index, child in enumerate(value):
            rows.extend(_walk_text(child, f"{path}[{index}]"))
        return rows
    return []


def _normalize(value: str) -> str:
    return " ".join(value.lower().replace("_", " ").replace("-", " ").split())


def _contains_any(value: str, terms: Sequence[str]) -> bool:
    return any(_normalize(term) in value for term in terms)


def _add(issues: list[DevHubReadOnlySurfaceDeltaPacketV1Issue], code: str, path: str, message: str) -> None:
    issues.append(DevHubReadOnlySurfaceDeltaPacketV1Issue(code, path, message))


def _dedupe(
    issues: Sequence[DevHubReadOnlySurfaceDeltaPacketV1Issue],
) -> list[DevHubReadOnlySurfaceDeltaPacketV1Issue]:
    seen: set[tuple[str, str, str]] = set()
    result: list[DevHubReadOnlySurfaceDeltaPacketV1Issue] = []
    for issue in issues:
        key = (issue.code, issue.path, issue.message)
        if key not in seen:
            seen.add(key)
            result.append(issue)
    return result
