"""Validation for DevHub read-only surface map reviewer packet v2.

The packet is an offline review artifact for candidate read-only DevHub
surface-map rows. It must stay commit-safe: no browser/session artifacts, no
raw or downloaded private data, no live DevHub execution claims, no automated
login/MFA claims, no consequential official-action language, and no active
mutation flags for surface maps, guardrails, prompts, sources, contracts, or
release state.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

PACKET_VERSION = "devhub_read_only_surface_map_reviewer_packet_v2"

_REVIEWED_STATUSES = frozenset(
    {
        "human_reviewed",
        "reviewed_read_only",
        "accepted_read_only",
        "rejected_read_only",
        "needs_revision_reviewed",
    }
)

_REQUIRED_TOP_LEVEL_SEQUENCES = (
    "candidate_rows",
    "observation_to_candidate_traces",
    "redaction_acceptance_refs",
    "unresolved_selector_risk_notes",
    "blocked_action_confirmations",
    "validation_commands",
)

_PRIVATE_ARTIFACT_TERMS = (
    "auth state",
    "authenticated artifact",
    "browser artifact",
    "browser context",
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

_BROWSER_RAW_OR_DOWNLOADED_TERMS = (
    ".har",
    ".png",
    "downloaded artifact",
    "downloaded data",
    "downloaded document",
    "downloaded pdf",
    "har file",
    "network trace",
    "raw authenticated html",
    "raw body",
    "raw capture",
    "raw crawl",
    "raw download",
    "raw pdf",
    "screenshot",
    "trace file",
    "trace.zip",
)

_LIVE_DEVHUB_CLAIM_TERMS = (
    "completed authenticated run",
    "devhub was updated",
    "executed in devhub",
    "live authenticated execution",
    "live devhub confirmed",
    "live devhub observation",
    "logged into devhub and ran",
    "ran against live devhub",
)

_AUTOMATED_LOGIN_OR_MFA_TERMS = (
    "automated login",
    "automated mfa",
    "bypass captcha",
    "bypass mfa",
    "completed mfa automatically",
    "filled password",
    "handled captcha",
    "handled mfa",
    "login bot",
    "mfa automation",
    "password automation",
)

_CONSEQUENTIAL_OFFICIAL_ACTION_TERMS = (
    "cancel inspection",
    "cancel permit",
    "certification submitted",
    "certify acknowledgement",
    "official upload",
    "paid fee",
    "pay fee",
    "purchase permit",
    "schedule inspection",
    "submit application",
    "submit permit",
    "submitted application",
    "submitted permit",
    "upload correction",
    "withdraw application",
)

_LEGAL_OR_PERMITTING_GUARANTEE_TERMS = (
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

_MUTATION_FLAG_KEYS = frozenset(
    {
        "active_contract_mutation",
        "active_guardrail_mutation",
        "active_prompt_mutation",
        "active_release_state_mutation",
        "active_source_mutation",
        "active_surface_map_mutation",
        "contract_mutation",
        "contract_mutation_enabled",
        "guardrail_mutation",
        "guardrail_mutation_enabled",
        "mutates_contract",
        "mutates_contracts",
        "mutates_guardrail",
        "mutates_guardrails",
        "mutates_prompt",
        "mutates_prompts",
        "mutates_release_state",
        "mutates_source",
        "mutates_sources",
        "mutates_surface_map",
        "mutates_surface_maps",
        "prompt_mutation",
        "prompt_mutation_enabled",
        "release_state_mutation",
        "release_state_mutation_enabled",
        "source_mutation",
        "source_mutation_enabled",
        "surface_map_mutation",
        "surface_map_mutation_enabled",
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
    "stores_downloads",
    "stores_raw_crawl_output",
    "stores_raw_devhub_output",
    "stores_raw_pdf_output",
)


@dataclass(frozen=True)
class DevHubReadOnlySurfaceMapReviewerPacketV2Issue:
    """Machine-readable validation issue."""

    code: str
    path: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "path": self.path, "message": self.message}


def validate_devhub_read_only_surface_map_reviewer_packet_v2(
    packet: Mapping[str, Any],
) -> list[DevHubReadOnlySurfaceMapReviewerPacketV2Issue]:
    """Return deterministic fail-closed validation issues for a packet."""

    issues: list[DevHubReadOnlySurfaceMapReviewerPacketV2Issue] = []
    if not isinstance(packet, Mapping):
        return [
            DevHubReadOnlySurfaceMapReviewerPacketV2Issue(
                "invalid_packet",
                "$",
                "packet must be an object",
            )
        ]

    version = packet.get("packet_version") or packet.get("reviewer_packet_version")
    if version != PACKET_VERSION:
        _add_issue(issues, "invalid_packet_version", "packet_version", f"packet_version must be {PACKET_VERSION}")

    for key in _REQUIRED_TOP_LEVEL_SEQUENCES:
        _require_non_empty_sequence(packet, key, issues)

    trace_ids_by_candidate = _validate_observation_to_candidate_traces(
        packet.get("observation_to_candidate_traces"),
        issues,
    )
    redaction_ref_ids = _validate_redaction_acceptance_refs(packet.get("redaction_acceptance_refs"), issues)
    selector_note_ids = _validate_unresolved_selector_risk_notes(packet.get("unresolved_selector_risk_notes"), issues)
    blocked_confirmation_ids = _validate_blocked_action_confirmations(packet.get("blocked_action_confirmations"), issues)

    _validate_candidate_rows(
        packet.get("candidate_rows"),
        trace_ids_by_candidate,
        redaction_ref_ids,
        selector_note_ids,
        blocked_confirmation_ids,
        issues,
    )
    _validate_validation_commands(packet.get("validation_commands"), issues)
    _validate_artifact_policy(packet.get("artifact_policy", {}), issues)
    _validate_mutation_flags(packet.get("mutation_flags", {}), "mutation_flags", issues)
    _scan_for_rejected_content(packet, issues)
    return _dedupe_issues(issues)


def validate_packet(packet: Mapping[str, Any]) -> list[DevHubReadOnlySurfaceMapReviewerPacketV2Issue]:
    """Compatibility alias for generic packet validators."""

    return validate_devhub_read_only_surface_map_reviewer_packet_v2(packet)


def assert_valid_devhub_read_only_surface_map_reviewer_packet_v2(packet: Mapping[str, Any]) -> None:
    """Raise AssertionError when the packet is invalid."""

    issues = validate_devhub_read_only_surface_map_reviewer_packet_v2(packet)
    if issues:
        formatted = "; ".join(f"{issue.code} at {issue.path}" for issue in issues)
        raise AssertionError("invalid DevHub read-only surface map reviewer packet v2: " + formatted)


def _validate_candidate_rows(
    value: Any,
    trace_ids_by_candidate: Mapping[str, set[str]],
    redaction_ref_ids: set[str],
    selector_note_ids: set[str],
    blocked_confirmation_ids: set[str],
    issues: list[DevHubReadOnlySurfaceMapReviewerPacketV2Issue],
) -> None:
    if not _is_non_empty_sequence(value):
        return

    seen_ids: set[str] = set()
    for index, row in enumerate(value):
        path = f"candidate_rows[{index}]"
        if not isinstance(row, Mapping):
            _add_issue(issues, "invalid_candidate_row", path, "candidate rows must be objects")
            continue

        row_id = _string_value(row.get("candidate_row_id") or row.get("row_id") or row.get("id"))
        if not row_id:
            _add_issue(issues, "missing_candidate_row_id", f"{path}.candidate_row_id", "candidate_row_id is required")
        elif row_id in seen_ids:
            _add_issue(issues, "duplicate_candidate_row_id", f"{path}.candidate_row_id", "candidate_row_id must be unique")
        else:
            seen_ids.add(row_id)

        review_status = _string_value(row.get("review_status") or row.get("human_review_status"))
        if review_status not in _REVIEWED_STATUSES:
            _add_issue(
                issues,
                "unreviewed_candidate_row",
                f"{path}.review_status",
                "candidate rows must have a human-reviewed read-only review_status",
            )

        for key in ("surface_id", "reviewer", "review_rationale"):
            if not _string_value(row.get(key)):
                _add_issue(issues, f"missing_{key}", f"{path}.{key}", f"{key} is required")

        trace_ids = _string_sequence(row.get("observation_trace_ids"))
        if not trace_ids:
            _add_issue(
                issues,
                "missing_observation_to_candidate_trace",
                f"{path}.observation_trace_ids",
                "candidate rows must reference observation-to-candidate traces",
            )
        for trace_id in trace_ids:
            if trace_id not in trace_ids_by_candidate.get(row_id, set()):
                _add_issue(
                    issues,
                    "missing_observation_to_candidate_trace",
                    f"{path}.observation_trace_ids",
                    "observation_trace_ids must reference traces that point back to this candidate row",
                )

        _require_known_ref(row, "redaction_acceptance_ref", redaction_ref_ids, path, "missing_redaction_acceptance_ref", issues)
        _require_known_refs(
            row,
            "unresolved_selector_risk_note_ids",
            selector_note_ids,
            path,
            "missing_unresolved_selector_risk_note",
            issues,
        )
        _require_known_refs(
            row,
            "blocked_action_confirmation_ids",
            blocked_confirmation_ids,
            path,
            "missing_blocked_action_confirmation",
            issues,
        )


def _validate_observation_to_candidate_traces(
    value: Any,
    issues: list[DevHubReadOnlySurfaceMapReviewerPacketV2Issue],
) -> dict[str, set[str]]:
    trace_ids_by_candidate: dict[str, set[str]] = {}
    if not _is_non_empty_sequence(value):
        return trace_ids_by_candidate
    seen_ids: set[str] = set()
    for index, trace in enumerate(value):
        path = f"observation_to_candidate_traces[{index}]"
        if not isinstance(trace, Mapping):
            _add_issue(issues, "invalid_observation_to_candidate_trace", path, "traces must be objects")
            continue
        trace_id = _string_value(trace.get("trace_id") or trace.get("id"))
        candidate_id = _string_value(trace.get("candidate_row_id"))
        if not trace_id:
            _add_issue(issues, "missing_observation_to_candidate_trace_id", f"{path}.trace_id", "trace_id is required")
            continue
        if trace_id in seen_ids:
            _add_issue(issues, "duplicate_observation_to_candidate_trace_id", f"{path}.trace_id", "trace_id must be unique")
        seen_ids.add(trace_id)
        if not candidate_id:
            _add_issue(issues, "missing_trace_candidate_row_id", f"{path}.candidate_row_id", "candidate_row_id is required")
        else:
            trace_ids_by_candidate.setdefault(candidate_id, set()).add(trace_id)
        if not _string_value(trace.get("observation_id")):
            _add_issue(issues, "missing_trace_observation_id", f"{path}.observation_id", "observation_id is required")
        if not _string_value(trace.get("trace_note")):
            _add_issue(issues, "missing_trace_note", f"{path}.trace_note", "trace_note is required")
    return trace_ids_by_candidate


def _validate_redaction_acceptance_refs(
    value: Any,
    issues: list[DevHubReadOnlySurfaceMapReviewerPacketV2Issue],
) -> set[str]:
    ids: set[str] = set()
    if not _is_non_empty_sequence(value):
        return ids
    for index, ref in enumerate(value):
        path = f"redaction_acceptance_refs[{index}]"
        if not isinstance(ref, Mapping):
            _add_issue(issues, "invalid_redaction_acceptance_ref", path, "redaction acceptance refs must be objects")
            continue
        ref_id = _string_value(ref.get("ref_id") or ref.get("id"))
        if not ref_id:
            _add_issue(issues, "missing_redaction_acceptance_ref_id", f"{path}.ref_id", "ref_id is required")
        else:
            ids.add(ref_id)
        if ref.get("accepted") is not True:
            _add_issue(issues, "redaction_acceptance_not_true", f"{path}.accepted", "redaction acceptance must be true")
        if not _string_value(ref.get("reviewer")):
            _add_issue(issues, "missing_redaction_acceptance_reviewer", f"{path}.reviewer", "reviewer is required")
    return ids


def _validate_unresolved_selector_risk_notes(
    value: Any,
    issues: list[DevHubReadOnlySurfaceMapReviewerPacketV2Issue],
) -> set[str]:
    ids: set[str] = set()
    if not _is_non_empty_sequence(value):
        return ids
    for index, note in enumerate(value):
        path = f"unresolved_selector_risk_notes[{index}]"
        if not isinstance(note, Mapping):
            _add_issue(issues, "invalid_unresolved_selector_risk_note", path, "selector-risk notes must be objects")
            continue
        note_id = _string_value(note.get("note_id") or note.get("id"))
        if not note_id:
            _add_issue(issues, "missing_unresolved_selector_risk_note_id", f"{path}.note_id", "note_id is required")
        else:
            ids.add(note_id)
        if not _string_value(note.get("risk_note")):
            _add_issue(issues, "missing_unresolved_selector_risk_note", f"{path}.risk_note", "risk_note is required")
        status = _string_value(note.get("status"))
        if status not in {"unresolved", "deferred_to_human_review", "accepted_for_read_only_with_note"}:
            _add_issue(issues, "invalid_selector_risk_note_status", f"{path}.status", "selector-risk status must preserve unresolved review context")
    return ids


def _validate_blocked_action_confirmations(
    value: Any,
    issues: list[DevHubReadOnlySurfaceMapReviewerPacketV2Issue],
) -> set[str]:
    ids: set[str] = set()
    if not _is_non_empty_sequence(value):
        return ids
    for index, confirmation in enumerate(value):
        path = f"blocked_action_confirmations[{index}]"
        if not isinstance(confirmation, Mapping):
            _add_issue(issues, "invalid_blocked_action_confirmation", path, "blocked-action confirmations must be objects")
            continue
        confirmation_id = _string_value(confirmation.get("confirmation_id") or confirmation.get("id"))
        if not confirmation_id:
            _add_issue(issues, "missing_blocked_action_confirmation_id", f"{path}.confirmation_id", "confirmation_id is required")
        else:
            ids.add(confirmation_id)
        if confirmation.get("confirmed_blocked") is not True:
            _add_issue(issues, "blocked_action_not_confirmed", f"{path}.confirmed_blocked", "blocked actions must be confirmed blocked")
        if not _string_value(confirmation.get("blocked_action_note")):
            _add_issue(issues, "missing_blocked_action_note", f"{path}.blocked_action_note", "blocked_action_note is required")
    return ids


def _validate_validation_commands(
    value: Any,
    issues: list[DevHubReadOnlySurfaceMapReviewerPacketV2Issue],
) -> None:
    if not _is_non_empty_sequence(value):
        return
    for index, command in enumerate(value):
        path = f"validation_commands[{index}]"
        if not _is_non_empty_sequence(command) or not all(isinstance(part, str) and part for part in command):
            _add_issue(issues, "invalid_validation_command", path, "validation commands must be non-empty argv lists")


def _validate_artifact_policy(
    value: Any,
    issues: list[DevHubReadOnlySurfaceMapReviewerPacketV2Issue],
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
    issues: list[DevHubReadOnlySurfaceMapReviewerPacketV2Issue],
) -> None:
    if not isinstance(value, Mapping):
        _add_issue(issues, "invalid_mutation_flags", path, "mutation_flags must be an object")
        return
    for key, child in value.items():
        child_path = f"{path}.{key}"
        if key in _MUTATION_FLAG_KEYS and _active_flag(child):
            _add_issue(issues, "active_mutation_flag", child_path, "surface-map, guardrail, prompt, source, contract, and release-state mutation flags must be false or absent")
        if isinstance(child, Mapping):
            _validate_mutation_flags(child, child_path, issues)


def _scan_for_rejected_content(
    value: Any,
    issues: list[DevHubReadOnlySurfaceMapReviewerPacketV2Issue],
) -> None:
    for path, text in _walk_text(value):
        searchable = _normalize_search_text(text)
        if _contains_any(searchable, _PRIVATE_ARTIFACT_TERMS):
            _add_issue(issues, "private_or_session_artifact_language", path, "packet must not reference private, session, auth, or browser artifacts")
        if _contains_any(searchable, _BROWSER_RAW_OR_DOWNLOADED_TERMS):
            _add_issue(issues, "browser_raw_or_downloaded_artifact_language", path, "packet must not reference screenshots, traces, HAR, raw output, or downloaded artifacts")
        if _contains_any(searchable, _LIVE_DEVHUB_CLAIM_TERMS):
            _add_issue(issues, "live_devhub_claim", path, "packet must not claim live DevHub execution or live authenticated confirmation")
        if _contains_any(searchable, _AUTOMATED_LOGIN_OR_MFA_TERMS):
            _add_issue(issues, "automated_login_or_mfa_claim", path, "packet must not claim automated login, CAPTCHA, password, or MFA handling")
        if _contains_any(searchable, _CONSEQUENTIAL_OFFICIAL_ACTION_TERMS):
            _add_issue(issues, "consequential_official_action_language", path, "packet must not include consequential official-action language")
        if _contains_any(searchable, _LEGAL_OR_PERMITTING_GUARANTEE_TERMS):
            _add_issue(issues, "legal_or_permitting_guarantee", path, "packet must not guarantee legal or permitting outcomes")


def _require_known_ref(
    row: Mapping[str, Any],
    key: str,
    known_ids: set[str],
    row_path: str,
    code: str,
    issues: list[DevHubReadOnlySurfaceMapReviewerPacketV2Issue],
) -> None:
    value = _string_value(row.get(key))
    if not value:
        _add_issue(issues, code, f"{row_path}.{key}", f"{key} is required")
    elif value not in known_ids:
        _add_issue(issues, code, f"{row_path}.{key}", f"{key} must reference a declared packet item")


def _require_known_refs(
    row: Mapping[str, Any],
    key: str,
    known_ids: set[str],
    row_path: str,
    code: str,
    issues: list[DevHubReadOnlySurfaceMapReviewerPacketV2Issue],
) -> None:
    values = _string_sequence(row.get(key))
    if not values:
        _add_issue(issues, code, f"{row_path}.{key}", f"{key} must be a non-empty list")
        return
    for value in values:
        if value not in known_ids:
            _add_issue(issues, code, f"{row_path}.{key}", f"{key} must reference declared packet items")


def _require_non_empty_sequence(
    mapping: Mapping[str, Any],
    key: str,
    issues: list[DevHubReadOnlySurfaceMapReviewerPacketV2Issue],
) -> None:
    if not _is_non_empty_sequence(mapping.get(key)):
        _add_issue(issues, f"missing_{key}", key, f"{key} must be a non-empty list")


def _is_non_empty_sequence(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)) and len(value) > 0


def _string_value(value: Any) -> str:
    if isinstance(value, str):
        return value.strip()
    return ""


def _string_sequence(value: Any) -> list[str]:
    if not _is_non_empty_sequence(value):
        return []
    result: list[str] = []
    for item in value:
        item_value = _string_value(item)
        if item_value:
            result.append(item_value)
    return result


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
        result: list[tuple[str, str]] = []
        for key, child in value.items():
            result.extend(_walk_text(child, f"{path}.{key}"))
        return result
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        result = []
        for index, child in enumerate(value):
            result.extend(_walk_text(child, f"{path}[{index}]"))
        return result
    return []


def _normalize_search_text(value: str) -> str:
    return " ".join(value.lower().replace("_", " ").replace("-", " ").split())


def _contains_any(value: str, terms: Sequence[str]) -> bool:
    normalized_terms = (_normalize_search_text(term) for term in terms)
    return any(term in value for term in normalized_terms)


def _add_issue(
    issues: list[DevHubReadOnlySurfaceMapReviewerPacketV2Issue],
    code: str,
    path: str,
    message: str,
) -> None:
    issues.append(DevHubReadOnlySurfaceMapReviewerPacketV2Issue(code, path, message))


def _dedupe_issues(
    issues: Sequence[DevHubReadOnlySurfaceMapReviewerPacketV2Issue],
) -> list[DevHubReadOnlySurfaceMapReviewerPacketV2Issue]:
    seen: set[tuple[str, str, str]] = set()
    deduped: list[DevHubReadOnlySurfaceMapReviewerPacketV2Issue] = []
    for issue in issues:
        key = (issue.code, issue.path, issue.message)
        if key not in seen:
            seen.add(key)
            deduped.append(issue)
    return deduped
