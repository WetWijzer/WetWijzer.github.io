"""Fixture-first DevHub read-only surface-map candidate v2.

This module consumes an accepted DevHub observation redaction packet v2 and
produces inactive surface-map candidate rows for reviewer intake. It is strictly
offline: it does not open DevHub, create auth state, store browser artifacts,
retain private page values, or modify active surface maps.
"""

from __future__ import annotations

from collections.abc import Sequence
from copy import deepcopy
import re
from typing import Any, Mapping

from ppd.devhub.observation_redaction_acceptance_packet_v2 import validate_acceptance_packet

CANDIDATE_SCHEMA_VERSION = "devhub_read_only_surface_map_candidate_v2"
SOURCE_SCHEMA_VERSION = "devhub_observation_redaction_acceptance_packet_v2"

OFFLINE_VALIDATION_COMMANDS = [
    ["python3", "-m", "py_compile", "ppd/devhub/surface_map_candidate_v2.py"],
    ["python3", "-m", "pytest", "ppd/tests/test_devhub_surface_map_candidate_v2.py"],
    ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
]

PROHIBITED_ARTIFACT_KEYS = {
    "screenshot",
    "screenshots",
    "trace",
    "traces",
    "har",
    "har_file",
    "auth_state",
    "storage_state",
    "cookie",
    "cookies",
    "credential",
    "credentials",
    "password",
    "private_page_value",
    "private_page_values",
    "account_identifier",
    "account_identifiers",
    "upload",
    "uploads",
    "submission",
    "submissions",
    "payment",
    "payments",
    "schedule",
    "scheduling",
    "cancellation",
    "cancellations",
    "raw_artifact",
    "raw_artifacts",
    "raw_crawl_output",
    "download",
    "downloads",
    "downloaded_artifact",
    "downloaded_artifacts",
    "browser_trace",
    "browser_artifact",
    "session_file",
    "session_files",
}

PRIVATE_OR_ARTIFACT_RE = re.compile(
    r"(password|passwd|secret|token|bearer\s+[a-z0-9._-]+|authorization:|session[_ -]?id|cookie[_ -]?jar|"
    r"storage[_ -]?state|auth[_ -]?state|\.har\b|\.trace\b|trace\.zip\b|screenshot\.(png|jpg|jpeg)|"
    r"raw crawl|raw downloaded|downloaded artifact|browser artifact|private page value)",
    re.IGNORECASE,
)
AUTOMATED_LOGIN_OR_MFA_RE = re.compile(
    r"(automated|automation|scripted|headless|worker)\s+(login|sign[- ]?in|mfa|multi[- ]?factor|captcha)|"
    r"(login|sign[- ]?in|mfa|multi[- ]?factor|captcha)\s+(was|is|will be)\s+(automated|scripted|bypassed)",
    re.IGNORECASE,
)
CONSEQUENTIAL_ENABLEMENT_RE = re.compile(
    r"\b(agent|worker|automation|script|packet)\s+(may|can|will|should|is allowed to|is authorized to)\s+"
    r"(submit|certify|upload|pay|purchase|schedule|cancel|withdraw|file)\b|"
    r"\b(submit|certify|upload|pay|purchase|schedule|cancel|withdraw|file)\s+"
    r"(the\s+)?(permit|application|inspection|payment|official record)\s+(automatically|without user)",
    re.IGNORECASE,
)
LEGAL_OR_PERMIT_GUARANTEE_RE = re.compile(
    r"\b(legal advice|legally sufficient|guaranteed approval|approval guaranteed|permit will be approved|"
    r"permit is guaranteed|guarantees? issuance|guarantees? compliance|compliant with all law)\b",
    re.IGNORECASE,
)
ACTIVE_MUTATION_KEY_PARTS = (
    "active_devhub_surface",
    "active_surface",
    "active_guardrail",
    "active_source",
    "active_prompt",
    "active_contract",
    "active_release_state",
    "surface_mutation",
    "guardrail_mutation",
    "source_mutation",
    "prompt_mutation",
    "contract_mutation",
    "release_state_mutation",
)
ACTIVE_MUTATION_VALUE_RE = re.compile(
    r"\b(active|applied|committed|mutated|published)\s+"
    r"(devhub surface|surface map|surface|guardrail|source|prompt|contract|release state)\b",
    re.IGNORECASE,
)


class SurfaceMapCandidateError(ValueError):
    """Raised when a candidate packet is incomplete or unsafe."""


def build_surface_map_candidate(packet: Mapping[str, Any]) -> dict[str, Any]:
    """Build inactive surface-map candidate rows from redaction acceptance v2."""

    normalized = _normalize_source_packet(packet)
    rows = _candidate_rows(normalized)
    selector_placeholders = [_selector_placeholder(row) for row in rows]
    role_placeholders = [_accessible_role_placeholder(row) for row in rows]
    message_placeholders = [_validation_message_placeholder(row) for row in rows]
    classifications = [_action_boundary_classification(row) for row in rows]
    dispositions = [_reviewer_disposition_placeholder(row) for row in rows]

    candidate = {
        "schema_version": CANDIDATE_SCHEMA_VERSION,
        "candidate_id": f"surface-map-candidate-v2-{normalized['packet_id']}",
        "source_redaction_packet": {
            "schema_version": normalized["schema_version"],
            "packet_id": normalized["packet_id"],
            "surface_id": normalized["surface_id"],
            "synthetic_fixture_only": normalized["synthetic_fixture_only"],
        },
        "mode": "offline_fixture_inactive_candidate",
        "generated_at": "1970-01-01T00:00:00Z",
        "candidate_rows": rows,
        "selector_stability_placeholders": selector_placeholders,
        "accessible_role_evidence_placeholders": role_placeholders,
        "redacted_validation_message_placeholders": message_placeholders,
        "action_boundary_classifications": classifications,
        "reviewer_disposition_placeholders": dispositions,
        "surface_map_safety_attestations": [
            {
                "attestation_id": "inactive-candidate-only",
                "status": "confirmed",
                "statement": "Rows are inactive candidates for reviewer intake and do not alter a deployed surface map.",
            },
            {
                "attestation_id": "fixture-redaction-source-only",
                "status": "confirmed",
                "statement": "Candidate rows derive only from the accepted redaction packet fixture.",
            },
        ],
        "offline_validation_commands": deepcopy(OFFLINE_VALIDATION_COMMANDS),
    }
    assert_surface_map_candidate(candidate)
    return candidate


def validate_surface_map_candidate(candidate: Mapping[str, Any]) -> list[str]:
    """Return deterministic rejection codes for unsafe candidate packets."""

    errors: list[str] = []
    if not isinstance(candidate, Mapping):
        return ["candidate_not_object"]
    if candidate.get("schema_version") != CANDIDATE_SCHEMA_VERSION:
        errors.append("unsupported_schema_version")

    required_sections = {
        "candidate_rows": "missing_inactive_surface_map_candidate_rows",
        "selector_stability_placeholders": "missing_selector_stability_placeholders",
        "accessible_role_evidence_placeholders": "missing_accessible_role_evidence_placeholders",
        "redacted_validation_message_placeholders": "missing_redacted_validation_message_placeholders",
        "action_boundary_classifications": "missing_action_boundary_classifications",
        "reviewer_disposition_placeholders": "missing_reviewer_disposition_placeholders",
        "offline_validation_commands": "missing_validation_commands",
    }
    for field, code in required_sections.items():
        if not _non_empty_sequence(candidate.get(field)):
            errors.append(code)

    rows = _sequence_or_empty(candidate.get("candidate_rows"))
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            errors.append(f"candidate_row_{index}_not_object")
            continue
        if row.get("activation_state") != "inactive_surface_map_candidate":
            errors.append("candidate_row_not_inactive")
        if not row.get("selector_stability_placeholder_id"):
            errors.append("missing_selector_stability_placeholders")
        if not row.get("accessible_role_evidence_placeholder_id"):
            errors.append("missing_accessible_role_evidence_placeholders")
        if not row.get("redacted_validation_message_placeholder_id"):
            errors.append("missing_redacted_validation_message_placeholders")
        if not row.get("action_boundary_classification_id"):
            errors.append("missing_action_boundary_classifications")
        if not row.get("reviewer_disposition_placeholder_id"):
            errors.append("missing_reviewer_disposition_placeholders")

    if _contains_prohibited_key(candidate) or _contains_private_or_artifact_claim(candidate):
        errors.append("private_session_browser_raw_or_downloaded_artifact")
    if _contains_automated_login_or_mfa_claim(candidate):
        errors.append("automated_login_or_mfa_claim")
    if _contains_consequential_enablement(candidate):
        errors.append("consequential_official_action_language")
    if _contains_legal_or_permit_guarantee(candidate):
        errors.append("legal_or_permitting_guarantee")
    if _contains_active_mutation_flag(candidate):
        errors.append("active_devhub_surface_guardrail_source_prompt_contract_or_release_state_mutation_flag")

    return sorted(set(errors))


def assert_surface_map_candidate(candidate: Mapping[str, Any]) -> None:
    errors = validate_surface_map_candidate(candidate)
    if errors:
        raise SurfaceMapCandidateError("DevHub surface-map candidate v2 rejected: " + ", ".join(errors))


def _normalize_source_packet(packet: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(packet, Mapping):
        raise SurfaceMapCandidateError("redaction packet must be a mapping")
    packet_errors = validate_acceptance_packet(packet)
    if packet_errors:
        raise SurfaceMapCandidateError("source redaction packet is invalid: " + ", ".join(packet_errors))
    if packet.get("schema_version") != SOURCE_SCHEMA_VERSION:
        raise SurfaceMapCandidateError("unsupported source redaction packet schema")

    source_plan = packet.get("source_plan")
    if not isinstance(source_plan, Mapping):
        raise SurfaceMapCandidateError("source_plan must be present")

    return {
        "schema_version": str(packet["schema_version"]),
        "packet_id": _required_text(packet, "packet_id"),
        "surface_id": _required_text(source_plan, "surface_id"),
        "synthetic_fixture_only": source_plan.get("synthetic_fixture_only") is True,
        "field_level_decisions": _required_list(packet, "field_level_decisions"),
        "action_boundary_confirmations": _required_list(packet, "action_boundary_confirmations"),
    }


def _candidate_rows(packet: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    order = 1
    surface_id = str(packet["surface_id"])

    for decision in sorted(packet["field_level_decisions"], key=lambda item: (item.get("order", 0), item.get("field_id", ""))):
        field_id = _required_text(decision, "field_id")
        rows.append(
            {
                "order": order,
                "row_id": f"surface-row-{order:03d}-field-{field_id}",
                "surface_id": surface_id,
                "row_kind": "field",
                "source_ref": field_id,
                "candidate_label": _required_text(decision, "label"),
                "activation_state": "inactive_surface_map_candidate",
                "candidate_payload": {
                    "field_id": field_id,
                    "field_class": _required_text(decision, "field_class"),
                    "stored_representation": _required_text(decision, "stored_representation"),
                    "redaction_decision": _required_text(decision, "decision"),
                },
                "selector_stability_placeholder_id": f"selector-stability-{field_id}",
                "accessible_role_evidence_placeholder_id": f"accessible-role-{field_id}",
                "redacted_validation_message_placeholder_id": f"validation-message-{field_id}",
                "action_boundary_classification_id": f"action-boundary-field-{field_id}",
                "reviewer_disposition_placeholder_id": f"reviewer-disposition-field-{field_id}",
                "commit_safety": "fixture_only_no_devhub_access",
            }
        )
        order += 1

    for action in sorted(packet["action_boundary_confirmations"], key=lambda item: (item.get("order", 0), item.get("action_id", ""))):
        action_id = _required_text(action, "action_id")
        rows.append(
            {
                "order": order,
                "row_id": f"surface-row-{order:03d}-action-{action_id}",
                "surface_id": surface_id,
                "row_kind": "action",
                "source_ref": action_id,
                "candidate_label": action_id.replace("_", " "),
                "activation_state": "inactive_surface_map_candidate",
                "candidate_payload": {
                    "action_id": action_id,
                    "action_type": _required_text(action, "action_type"),
                    "read_only_confirmed": bool(action.get("read_only_confirmed")),
                    "consequential_action_blocked": bool(action.get("consequential_action_blocked")),
                },
                "selector_stability_placeholder_id": f"selector-stability-{action_id}",
                "accessible_role_evidence_placeholder_id": f"accessible-role-{action_id}",
                "redacted_validation_message_placeholder_id": f"validation-message-{action_id}",
                "action_boundary_classification_id": f"action-boundary-action-{action_id}",
                "reviewer_disposition_placeholder_id": f"reviewer-disposition-action-{action_id}",
                "commit_safety": "fixture_only_no_devhub_access",
            }
        )
        order += 1

    return rows


def _selector_placeholder(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "placeholder_id": row["selector_stability_placeholder_id"],
        "row_id": row["row_id"],
        "status": "pending_reviewer_evidence",
        "candidate_selector": None,
        "stability_evidence": [],
        "review_instruction": "Record only a future redacted selector strategy after reviewer approval; no selector was captured in this fixture.",
    }


def _accessible_role_placeholder(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "placeholder_id": row["accessible_role_evidence_placeholder_id"],
        "row_id": row["row_id"],
        "status": "pending_reviewer_evidence",
        "role": None,
        "name_source": "redacted_or_not_observed",
        "review_instruction": "Add accessible role evidence only from a later approved redacted observation.",
    }


def _validation_message_placeholder(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "placeholder_id": row["redacted_validation_message_placeholder_id"],
        "row_id": row["row_id"],
        "status": "pending_or_not_observed",
        "message_text": None,
        "redaction": "redacted_or_not_observed",
        "review_instruction": "Keep validation messages redacted unless a future reviewer marks label-only text as safe.",
    }


def _action_boundary_classification(row: Mapping[str, Any]) -> dict[str, Any]:
    payload = row["candidate_payload"]
    if row["row_kind"] == "field":
        classification = "read_only_evidence_placeholder"
        requires_exact_confirmation = False
    elif payload.get("consequential_action_blocked") is True:
        classification = "consequential_official_blocked"
        requires_exact_confirmation = True
    elif payload.get("read_only_confirmed") is True:
        classification = "safe_read_only_observation"
        requires_exact_confirmation = False
    else:
        classification = "review_required"
        requires_exact_confirmation = True

    return {
        "classification_id": row["action_boundary_classification_id"],
        "row_id": row["row_id"],
        "classification": classification,
        "official_action_allowed": False,
        "requires_attendance": True,
        "requires_exact_confirmation": requires_exact_confirmation,
    }


def _reviewer_disposition_placeholder(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "placeholder_id": row["reviewer_disposition_placeholder_id"],
        "row_id": row["row_id"],
        "status": "pending_reviewer_disposition",
        "allowed_dispositions": ["accept_inactive", "revise_fixture", "reject"],
        "reviewer_notes": None,
    }


def _required_text(mapping: Mapping[str, Any], key: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        raise SurfaceMapCandidateError(f"required text field missing or empty: {key}")
    return value


def _required_list(mapping: Mapping[str, Any], key: str) -> list[Any]:
    value = mapping.get(key)
    if not isinstance(value, list) or not value:
        raise SurfaceMapCandidateError(f"required list field missing or empty: {key}")
    return value


def _non_empty_sequence(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)) and bool(value)


def _sequence_or_empty(value: Any) -> Sequence[Any]:
    if _non_empty_sequence(value):
        return value
    return []


def _walk_text(value: Any) -> list[str]:
    out: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            out.append(str(key))
            out.extend(_walk_text(child))
    elif isinstance(value, str):
        out.append(value)
    elif isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        for child in value:
            out.extend(_walk_text(child))
    elif value is not None:
        out.append(str(value))
    return out


def _contains_prohibited_key(value: Any) -> bool:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if str(key).lower() in PROHIBITED_ARTIFACT_KEYS:
                return True
            if _contains_prohibited_key(child):
                return True
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return any(_contains_prohibited_key(child) for child in value)
    return False


def _contains_private_or_artifact_claim(candidate: Mapping[str, Any]) -> bool:
    return any(PRIVATE_OR_ARTIFACT_RE.search(text) for text in _walk_text(candidate))


def _contains_automated_login_or_mfa_claim(candidate: Mapping[str, Any]) -> bool:
    return any(AUTOMATED_LOGIN_OR_MFA_RE.search(text) for text in _walk_text(candidate))


def _contains_consequential_enablement(candidate: Mapping[str, Any]) -> bool:
    return any(CONSEQUENTIAL_ENABLEMENT_RE.search(text) for text in _walk_text(candidate))


def _contains_legal_or_permit_guarantee(candidate: Mapping[str, Any]) -> bool:
    return any(LEGAL_OR_PERMIT_GUARANTEE_RE.search(text) for text in _walk_text(candidate))


def _contains_active_mutation_flag(value: Any) -> bool:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key).lower()
            if any(part in key_text for part in ACTIVE_MUTATION_KEY_PARTS) and child is not False:
                return True
            if _contains_active_mutation_flag(child):
                return True
    elif isinstance(value, str):
        return bool(ACTIVE_MUTATION_VALUE_RE.search(value))
    elif isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        return any(_contains_active_mutation_flag(child) for child in value)
    return False
