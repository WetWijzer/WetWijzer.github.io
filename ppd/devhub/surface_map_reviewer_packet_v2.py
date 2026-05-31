"""Fixture-first DevHub read-only surface-map reviewer packet v2.

This module consumes DevHub read-only surface-map candidate v2 packets and
produces an offline reviewer packet. It creates ordered accept/hold/reject rows,
observation-to-candidate trace placeholders, redaction acceptance references,
unresolved selector-risk notes, blocked-action confirmation notes, and exact
offline validation commands. It never opens DevHub, stores private artifacts, or
applies active surface-map changes.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
import re
from typing import Any

from ppd.devhub.surface_map_candidate_v2 import validate_surface_map_candidate

REVIEWER_PACKET_SCHEMA_VERSION = "devhub_read_only_surface_map_reviewer_packet_v2"
SOURCE_CANDIDATE_SCHEMA_VERSION = "devhub_read_only_surface_map_candidate_v2"

OFFLINE_VALIDATION_COMMANDS: list[list[str]] = [
    ["python3", "-m", "py_compile", "ppd/devhub/surface_map_reviewer_packet_v2.py"],
    ["python3", "-m", "pytest", "ppd/tests/test_devhub_surface_map_reviewer_packet_v2.py"],
    ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
]

DISPOSITION_OPTIONS = ["accept", "hold", "reject"]

FORBIDDEN_KEYS = frozenset(
    {
        "auth_state",
        "browser_context",
        "browser_trace",
        "cookie",
        "cookies",
        "credential",
        "credentials",
        "har",
        "har_file",
        "password",
        "private_page_value",
        "private_page_values",
        "private_value",
        "raw_authenticated_value",
        "raw_crawl_output",
        "raw_dom",
        "screenshot",
        "screenshots",
        "session_file",
        "session_files",
        "storage_state",
        "trace",
        "traces",
    }
)

PRIVATE_OR_ARTIFACT_RE = re.compile(
    r"(password|passwd|secret|token|bearer\s+[a-z0-9._-]+|authorization:|session[_ -]?id|"
    r"cookie[_ -]?jar|storage[_ -]?state|auth[_ -]?state|\.har\b|\.trace\b|trace\.zip\b|"
    r"screenshot\.(png|jpg|jpeg)|private page value)",
    re.IGNORECASE,
)
CONSEQUENTIAL_ENABLEMENT_RE = re.compile(
    r"\b(agent|worker|automation|script|packet)\s+(may|can|will|should|is allowed to|is authorized to)\s+"
    r"(submit|certify|upload|pay|purchase|schedule|cancel|withdraw|file)\b|"
    r"\b(submit|certify|upload|pay|purchase|schedule|cancel|withdraw|file)\s+"
    r"(the\s+)?(permit|application|inspection|payment|official record)\s+(automatically|without user)",
    re.IGNORECASE,
)
ONLINE_COMMAND_MARKERS = ("curl", "wget", "playwright", "devhub.portlandoregon.gov", "http://", "https://")


class SurfaceMapReviewerPacketError(ValueError):
    """Raised when a reviewer packet is incomplete or unsafe."""


def build_surface_map_reviewer_packet_v2(candidate: Mapping[str, Any]) -> dict[str, Any]:
    """Build an offline reviewer packet from a surface-map candidate v2."""

    candidate_errors = validate_surface_map_candidate(candidate)
    if candidate_errors:
        raise SurfaceMapReviewerPacketError("source surface-map candidate v2 is invalid: " + ", ".join(candidate_errors))
    if candidate.get("schema_version") != SOURCE_CANDIDATE_SCHEMA_VERSION:
        raise SurfaceMapReviewerPacketError("unsupported source candidate schema")

    rows = sorted(_required_sequence(candidate, "candidate_rows"), key=lambda row: (int(row.get("order", 0)), str(row.get("row_id", ""))))
    selector_by_row = _index_by_row(candidate.get("selector_stability_placeholders"), "placeholder_id")
    classification_by_row = _index_by_row(candidate.get("action_boundary_classifications"), "classification_id")

    reviewer_rows: list[dict[str, Any]] = []
    trace_placeholders: list[dict[str, Any]] = []
    redaction_refs: list[dict[str, Any]] = []
    selector_risks: list[dict[str, Any]] = []
    blocked_notes: list[dict[str, Any]] = []

    for expected_order, row in enumerate(rows, start=1):
        if not isinstance(row, Mapping):
            raise SurfaceMapReviewerPacketError("candidate rows must be objects")
        row_id = _required_text(row, "row_id")
        classification = classification_by_row.get(row_id, {})
        selector_placeholder = selector_by_row.get(row_id, {})
        trace_id = f"trace-placeholder-{row_id}"
        redaction_ref_id = f"redaction-reference-{row_id}"
        selector_risk_id = f"selector-risk-{row_id}"
        blocked_note_id = None
        blocked = classification.get("classification") == "consequential_official_blocked"
        if blocked:
            blocked_note_id = f"blocked-action-confirmation-{row_id}"
            blocked_notes.append(_blocked_action_note(str(blocked_note_id), row, classification))

        trace_placeholders.append(_trace_placeholder(trace_id, row))
        redaction_refs.append(_redaction_reference(redaction_ref_id, candidate, row))
        selector_risks.append(_selector_risk_note(selector_risk_id, row, selector_placeholder))
        reviewer_rows.append(
            {
                "review_row_id": f"surface-map-review-v2-{expected_order:03d}",
                "order": expected_order,
                "candidate_row_id": row_id,
                "surface_id": _required_text(row, "surface_id"),
                "row_kind": _required_text(row, "row_kind"),
                "candidate_label": _required_text(row, "candidate_label"),
                "allowed_reviewer_dispositions": list(DISPOSITION_OPTIONS),
                "reviewer_disposition": None,
                "recommended_initial_disposition": _recommended_disposition(classification),
                "observation_to_candidate_trace_placeholder_id": trace_id,
                "redaction_acceptance_reference_id": redaction_ref_id,
                "selector_risk_note_id": selector_risk_id,
                "blocked_action_confirmation_note_id": blocked_note_id,
                "surface_map_change_applied": False,
                "official_action_allowed": False,
            }
        )

    packet = {
        "schema_version": REVIEWER_PACKET_SCHEMA_VERSION,
        "packet_id": f"surface-map-reviewer-packet-v2-{candidate['candidate_id']}",
        "source_candidate": {
            "schema_version": candidate["schema_version"],
            "candidate_id": candidate["candidate_id"],
            "source_redaction_packet": deepcopy(candidate.get("source_redaction_packet", {})),
        },
        "mode": "offline_fixture_reviewer_packet",
        "generated_at": "1970-01-01T00:00:00Z",
        "devhub_opened": False,
        "no_private_artifacts_stored": True,
        "no_surface_map_changes": True,
        "accept_hold_reject_disposition_options": list(DISPOSITION_OPTIONS),
        "reviewer_accept_hold_reject_rows": reviewer_rows,
        "observation_to_candidate_trace_placeholders": trace_placeholders,
        "redaction_acceptance_references": redaction_refs,
        "unresolved_selector_risk_notes": selector_risks,
        "blocked_action_confirmation_notes": blocked_notes,
        "blocked_action_categories_confirmed": [
            "account_change",
            "certification",
            "cancellation",
            "official_record_attachment",
            "payment",
            "scheduling",
            "submission",
        ],
        "offline_validation_commands": deepcopy(OFFLINE_VALIDATION_COMMANDS),
    }
    assert_surface_map_reviewer_packet_v2(packet)
    return packet


def validate_surface_map_reviewer_packet_v2(packet: Mapping[str, Any]) -> list[str]:
    """Return deterministic rejection codes for unsafe reviewer packets."""

    errors: list[str] = []
    if not isinstance(packet, Mapping):
        return ["packet_not_object"]
    if packet.get("schema_version") != REVIEWER_PACKET_SCHEMA_VERSION:
        errors.append("unsupported_schema_version")
    if packet.get("mode") != "offline_fixture_reviewer_packet":
        errors.append("mode_must_be_offline_fixture_reviewer_packet")
    if packet.get("devhub_opened") is not False:
        errors.append("devhub_must_not_be_opened")
    if packet.get("no_private_artifacts_stored") is not True:
        errors.append("private_artifact_exclusion_not_confirmed")
    if packet.get("no_surface_map_changes") is not True:
        errors.append("surface_map_changes_must_not_be_applied")
    if packet.get("accept_hold_reject_disposition_options") != DISPOSITION_OPTIONS:
        errors.append("accept_hold_reject_options_must_be_exact")
    if packet.get("offline_validation_commands") != OFFLINE_VALIDATION_COMMANDS:
        errors.append("offline_validation_commands_must_be_exact")

    rows = packet.get("reviewer_accept_hold_reject_rows")
    if not isinstance(rows, list) or not rows:
        errors.append("reviewer_accept_hold_reject_rows_required")
        rows = []

    trace_ids = _ids(packet.get("observation_to_candidate_trace_placeholders"), "trace_placeholder_id")
    redaction_ids = _ids(packet.get("redaction_acceptance_references"), "redaction_reference_id")
    selector_ids = _ids(packet.get("unresolved_selector_risk_notes"), "selector_risk_note_id")
    blocked_ids = _ids(packet.get("blocked_action_confirmation_notes"), "blocked_action_confirmation_note_id")

    seen_row_ids: set[str] = set()
    for expected_order, row in enumerate(rows, start=1):
        if not isinstance(row, Mapping):
            errors.append(f"reviewer_accept_hold_reject_rows[{expected_order - 1}]_not_object")
            continue
        row_id = str(row.get("review_row_id", "")).strip()
        if not row_id:
            errors.append(f"reviewer_accept_hold_reject_rows[{expected_order - 1}].review_row_id_required")
        elif row_id in seen_row_ids:
            errors.append("review_row_ids_must_be_unique")
        else:
            seen_row_ids.add(row_id)
        if row.get("order") != expected_order:
            errors.append("reviewer_rows_must_be_ordered")
        if row.get("allowed_reviewer_dispositions") != DISPOSITION_OPTIONS:
            errors.append("reviewer_row_dispositions_must_be_accept_hold_reject")
        if row.get("reviewer_disposition") is not None:
            errors.append("reviewer_disposition_must_remain_empty_for_fixture_packet")
        if row.get("recommended_initial_disposition") not in DISPOSITION_OPTIONS:
            errors.append("recommended_initial_disposition_invalid")
        if row.get("surface_map_change_applied") is not False:
            errors.append("reviewer_row_surface_map_change_applied_must_be_false")
        if row.get("official_action_allowed") is not False:
            errors.append("reviewer_row_official_action_allowed_must_be_false")
        if row.get("observation_to_candidate_trace_placeholder_id") not in trace_ids:
            errors.append("missing_observation_to_candidate_trace_placeholder")
        if row.get("redaction_acceptance_reference_id") not in redaction_ids:
            errors.append("missing_redaction_acceptance_reference")
        if row.get("selector_risk_note_id") not in selector_ids:
            errors.append("missing_unresolved_selector_risk_note")
        blocked_note_id = row.get("blocked_action_confirmation_note_id")
        if blocked_note_id is not None and blocked_note_id not in blocked_ids:
            errors.append("missing_blocked_action_confirmation_note")

    if not isinstance(packet.get("observation_to_candidate_trace_placeholders"), list) or not packet.get("observation_to_candidate_trace_placeholders"):
        errors.append("observation_to_candidate_trace_placeholders_required")
    if not isinstance(packet.get("redaction_acceptance_references"), list) or not packet.get("redaction_acceptance_references"):
        errors.append("redaction_acceptance_references_required")
    if not isinstance(packet.get("unresolved_selector_risk_notes"), list) or not packet.get("unresolved_selector_risk_notes"):
        errors.append("unresolved_selector_risk_notes_required")
    if not isinstance(packet.get("blocked_action_confirmation_notes"), list):
        errors.append("blocked_action_confirmation_notes_required")

    _scan_forbidden(packet, "$", errors)
    _validate_commands(packet.get("offline_validation_commands"), errors)
    return sorted(set(errors))


def assert_surface_map_reviewer_packet_v2(packet: Mapping[str, Any]) -> None:
    errors = validate_surface_map_reviewer_packet_v2(packet)
    if errors:
        raise SurfaceMapReviewerPacketError("DevHub surface-map reviewer packet v2 rejected: " + ", ".join(errors))


def _trace_placeholder(trace_id: str, row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "trace_placeholder_id": trace_id,
        "candidate_row_id": row["row_id"],
        "source_candidate_ref": row.get("source_ref"),
        "status": "pending_reviewer_trace_confirmation",
        "retained_evidence": "fixture_identifiers_only",
    }


def _redaction_reference(reference_id: str, candidate: Mapping[str, Any], row: Mapping[str, Any]) -> dict[str, Any]:
    payload = row.get("candidate_payload", {})
    if not isinstance(payload, Mapping):
        payload = {}
    return {
        "redaction_reference_id": reference_id,
        "candidate_row_id": row["row_id"],
        "source_redaction_packet_id": candidate.get("source_redaction_packet", {}).get("packet_id"),
        "source_ref": row.get("source_ref"),
        "redaction_decision": payload.get("redaction_decision", "action_boundary_reference"),
        "stored_representation": payload.get("stored_representation", "action_boundary_only"),
    }


def _selector_risk_note(note_id: str, row: Mapping[str, Any], selector_placeholder: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "selector_risk_note_id": note_id,
        "candidate_row_id": row["row_id"],
        "selector_placeholder_id": selector_placeholder.get("placeholder_id", row.get("selector_stability_placeholder_id")),
        "risk_status": "unresolved_hold_for_reviewer",
        "note": "Selector stability evidence remains unresolved; reviewer must hold promotion until a redacted selector strategy is supplied.",
    }


def _blocked_action_note(note_id: str, row: Mapping[str, Any], classification: Mapping[str, Any]) -> dict[str, Any]:
    payload = row.get("candidate_payload", {})
    if not isinstance(payload, Mapping):
        payload = {}
    return {
        "blocked_action_confirmation_note_id": note_id,
        "candidate_row_id": row["row_id"],
        "action_id": payload.get("action_id", row.get("source_ref")),
        "classification_id": classification.get("classification_id"),
        "confirmation_status": "blocked_pending_human_review",
        "official_action_allowed": False,
        "requires_exact_confirmation": True,
        "note": "Official action remains blocked. This reviewer packet does not permit execution.",
    }


def _recommended_disposition(classification: Mapping[str, Any]) -> str:
    if classification.get("classification") == "consequential_official_blocked":
        return "reject"
    return "hold"


def _index_by_row(value: Any, id_key: str) -> dict[str, Mapping[str, Any]]:
    indexed: dict[str, Mapping[str, Any]] = {}
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for item in value:
            if isinstance(item, Mapping) and isinstance(item.get("row_id"), str) and isinstance(item.get(id_key), str):
                indexed[item["row_id"]] = item
    return indexed


def _ids(value: Any, key: str) -> set[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return set()
    return {str(item.get(key)) for item in value if isinstance(item, Mapping) and isinstance(item.get(key), str)}


def _required_sequence(mapping: Mapping[str, Any], key: str) -> list[Mapping[str, Any]]:
    value = mapping.get(key)
    if not isinstance(value, list) or not value:
        raise SurfaceMapReviewerPacketError(f"required sequence missing or empty: {key}")
    return value


def _required_text(mapping: Mapping[str, Any], key: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        raise SurfaceMapReviewerPacketError(f"required text field missing or empty: {key}")
    return value


def _validate_commands(value: Any, errors: list[str]) -> None:
    if value != OFFLINE_VALIDATION_COMMANDS:
        errors.append("offline_validation_commands_must_be_exact")
        return
    for command in value:
        for part in command:
            lowered = str(part).lower()
            if any(marker in lowered for marker in ONLINE_COMMAND_MARKERS):
                errors.append("offline_validation_commands_must_not_open_devhub_or_network")


def _scan_forbidden(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            if key_text.lower() in FORBIDDEN_KEYS:
                errors.append(f"forbidden_private_or_browser_artifact_key:{path}.{key_text}")
            _scan_forbidden(child, f"{path}.{key_text}", errors)
    elif isinstance(value, str):
        if PRIVATE_OR_ARTIFACT_RE.search(value):
            errors.append(f"private_session_browser_or_artifact_text:{path}")
        if CONSEQUENTIAL_ENABLEMENT_RE.search(value):
            errors.append(f"consequential_official_action_enablement_text:{path}")
    elif isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        for index, child in enumerate(value):
            _scan_forbidden(child, f"{path}[{index}]", errors)
