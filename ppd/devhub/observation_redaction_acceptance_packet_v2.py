"""Fixture-first DevHub observation redaction acceptance packets.

This module intentionally works from synthetic, already-redacted observation plans.
It produces reviewer packets that can be committed and tested offline without
capturing screenshots, traces, HAR files, auth state, private page values,
account identifiers, uploads, submissions, payments, scheduling, cancellations,
or active surface-map changes.
"""

from __future__ import annotations

from collections.abc import Sequence
from copy import deepcopy
from datetime import datetime, timezone
import re
from typing import Any, Mapping

PACKET_SCHEMA_VERSION = "devhub_observation_redaction_acceptance_packet_v2"
PLAN_SCHEMA_VERSION = "attended_devhub_read_only_observation_plan_v2"

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
    "active_surface_map_change",
    "active_surface_map_changes",
}

PRIVATE_FIELD_CLASSES = {
    "account_identifier",
    "address",
    "applicant_name",
    "case_number",
    "contractor_license",
    "email",
    "financial",
    "full_name",
    "government_id",
    "phone",
    "private_page_value",
    "property_identifier",
    "tax_lot",
    "upload_filename",
}

CONSEQUENTIAL_ACTIONS = {
    "account_creation",
    "cancel",
    "certify",
    "final_payment",
    "mfa",
    "password_recovery",
    "payment_detail_entry",
    "purchase",
    "schedule_inspection",
    "submit",
    "upload",
    "withdraw",
}

SAFE_READ_ONLY_ACTIONS = {
    "observe_heading",
    "observe_landmark",
    "observe_link_label",
    "observe_status_label",
    "observe_table_headers",
    "review_attachment_list_labels",
    "review_fee_notice_labels",
    "review_permit_status_labels",
    "review_validation_message_labels",
}

OFFLINE_VALIDATION_COMMANDS = [
    ["python3", "-m", "py_compile", "ppd/devhub/observation_redaction_acceptance_packet_v2.py"],
    ["python3", "-m", "pytest", "ppd/tests/test_devhub_observation_redaction_acceptance_packet_v2.py"],
    ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
]

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
    r"(devhub surface|surface|guardrail|source|prompt|contract|release state)\b",
    re.IGNORECASE,
)


class ObservationPacketError(ValueError):
    """Raised when an observation plan cannot produce a commit-safe packet."""


def build_acceptance_packet(plan: Mapping[str, Any]) -> dict[str, Any]:
    """Build a deterministic reviewer packet from an attended read-only plan v2."""

    normalized_plan = _normalize_plan(plan)
    observations = normalized_plan["observations"]
    actions = normalized_plan["actions"]

    field_decisions = [_field_decision(observation) for observation in observations]
    action_confirmations = [_action_confirmation(action) for action in actions]
    reviewer_checks = _reviewer_checks(field_decisions, action_confirmations)
    exclusion_attestations = _private_value_exclusion_attestations(normalized_plan, field_decisions)
    unresolved_risks = _unresolved_risks(field_decisions, action_confirmations)

    packet = {
        "schema_version": PACKET_SCHEMA_VERSION,
        "packet_id": f"redaction-packet-v2-{normalized_plan['plan_id']}",
        "source_plan": {
            "schema_version": normalized_plan["schema_version"],
            "plan_id": normalized_plan["plan_id"],
            "mode": normalized_plan["mode"],
            "surface_id": normalized_plan["surface_id"],
            "synthetic_fixture_only": normalized_plan["synthetic_fixture_only"],
        },
        "generated_at": "1970-01-01T00:00:00Z",
        "reviewer_redaction_checks": reviewer_checks,
        "field_level_decisions": field_decisions,
        "private_value_exclusion_attestations": exclusion_attestations,
        "action_boundary_confirmations": action_confirmations,
        "unresolved_risk_notes": unresolved_risks,
        "offline_validation_commands": deepcopy(OFFLINE_VALIDATION_COMMANDS),
    }
    assert_acceptance_packet(packet)
    return packet


def validate_acceptance_packet(packet: Mapping[str, Any]) -> list[str]:
    """Return deterministic rejection codes for unsafe or incomplete packet v2 data."""

    errors: list[str] = []
    if not isinstance(packet, Mapping):
        return ["packet_not_object"]
    if packet.get("schema_version") != PACKET_SCHEMA_VERSION:
        errors.append("unsupported_schema_version")

    required_sections = {
        "reviewer_redaction_checks": "missing_reviewer_redaction_checks",
        "field_level_decisions": "missing_field_level_keep_drop_decisions",
        "private_value_exclusion_attestations": "missing_private_value_exclusion_attestations",
        "action_boundary_confirmations": "missing_action_boundary_confirmations",
        "unresolved_risk_notes": "missing_unresolved_risk_notes",
        "offline_validation_commands": "missing_validation_commands",
    }
    for field, code in required_sections.items():
        if not _non_empty_sequence(packet.get(field)):
            errors.append(code)

    for index, decision in enumerate(_sequence_or_empty(packet.get("field_level_decisions"))):
        if not isinstance(decision, Mapping):
            errors.append(f"field_decision_{index}_not_object")
            continue
        if decision.get("decision") not in {"keep", "drop"}:
            errors.append("missing_field_level_keep_drop_decisions")
        if not _present(decision.get("field_id")) or not _present(decision.get("stored_representation")):
            errors.append("incomplete_field_level_decision")

    for index, confirmation in enumerate(_sequence_or_empty(packet.get("action_boundary_confirmations"))):
        if not isinstance(confirmation, Mapping):
            errors.append(f"action_confirmation_{index}_not_object")
            continue
        if not isinstance(confirmation.get("read_only_confirmed"), bool):
            errors.append("missing_action_boundary_confirmations")
        if not isinstance(confirmation.get("consequential_action_blocked"), bool):
            errors.append("missing_action_boundary_confirmations")
        action_type = str(confirmation.get("action_type") or "")
        if action_type in CONSEQUENTIAL_ACTIONS and confirmation.get("consequential_action_blocked") is not True:
            errors.append("consequential_official_action_language")

    if _contains_prohibited_key(packet):
        errors.append("private_session_browser_raw_or_downloaded_artifact")
    if _contains_private_or_artifact_claim(packet):
        errors.append("private_session_browser_raw_or_downloaded_artifact")
    if _contains_automated_login_or_mfa_claim(packet):
        errors.append("automated_login_or_mfa_claim")
    if _contains_consequential_enablement(packet):
        errors.append("consequential_official_action_language")
    if _contains_legal_or_permit_guarantee(packet):
        errors.append("legal_or_permitting_guarantee")
    if _contains_active_mutation_flag(packet):
        errors.append("active_devhub_surface_guardrail_source_prompt_contract_or_release_state_mutation_flag")

    return sorted(set(errors))


def assert_acceptance_packet(packet: Mapping[str, Any]) -> None:
    errors = validate_acceptance_packet(packet)
    if errors:
        raise ObservationPacketError("DevHub observation redaction acceptance packet v2 rejected: " + ", ".join(errors))


def _normalize_plan(plan: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(plan, Mapping):
        raise ObservationPacketError("plan must be a mapping")

    _reject_prohibited_keys(plan)

    schema_version = _required_text(plan, "schema_version")
    if schema_version != PLAN_SCHEMA_VERSION:
        raise ObservationPacketError(f"unsupported schema_version: {schema_version}")

    mode = _required_text(plan, "mode")
    if mode != "attended_read_only_observation":
        raise ObservationPacketError("plan mode must be attended_read_only_observation")

    if plan.get("synthetic_fixture_only") is not True:
        raise ObservationPacketError("plan must be marked synthetic_fixture_only")

    observations = plan.get("observations")
    if not isinstance(observations, list) or not observations:
        raise ObservationPacketError("plan observations must be a non-empty list")

    actions = plan.get("actions", [])
    if not isinstance(actions, list):
        raise ObservationPacketError("plan actions must be a list")

    return {
        "schema_version": schema_version,
        "plan_id": _required_text(plan, "plan_id"),
        "mode": mode,
        "surface_id": _required_text(plan, "surface_id"),
        "synthetic_fixture_only": True,
        "observations": [_normalize_observation(item, index) for index, item in enumerate(observations, start=1)],
        "actions": [_normalize_action(item, index) for index, item in enumerate(actions, start=1)],
    }


def _normalize_observation(item: Any, index: int) -> dict[str, Any]:
    if not isinstance(item, Mapping):
        raise ObservationPacketError(f"observation {index} must be a mapping")
    _reject_prohibited_keys(item)

    field_class = _required_text(item, "field_class")
    redaction = _required_text(item, "redaction")
    value_kind = _required_text(item, "value_kind")
    if value_kind != "synthetic":
        raise ObservationPacketError(f"observation {index} must use synthetic value_kind")
    if redaction not in {"keep_label_only", "drop_value", "drop_field", "keep_synthetic_literal"}:
        raise ObservationPacketError(f"observation {index} has unsupported redaction: {redaction}")

    return {
        "order": int(item.get("order", index)),
        "field_id": _required_text(item, "field_id"),
        "label": _required_text(item, "label"),
        "field_class": field_class,
        "value_kind": value_kind,
        "redaction": redaction,
        "review_reason": _required_text(item, "review_reason"),
    }


def _normalize_action(item: Any, index: int) -> dict[str, Any]:
    if not isinstance(item, Mapping):
        raise ObservationPacketError(f"action {index} must be a mapping")
    _reject_prohibited_keys(item)

    action_type = _required_text(item, "action_type")
    if action_type not in SAFE_READ_ONLY_ACTIONS and action_type not in CONSEQUENTIAL_ACTIONS:
        raise ObservationPacketError(f"action {index} has unknown action_type: {action_type}")

    return {
        "order": int(item.get("order", index)),
        "action_id": _required_text(item, "action_id"),
        "action_type": action_type,
        "boundary": _required_text(item, "boundary"),
        "confirmation": _required_text(item, "confirmation"),
    }


def _field_decision(observation: Mapping[str, Any]) -> dict[str, Any]:
    is_private_class = observation["field_class"] in PRIVATE_FIELD_CLASSES
    requested_redaction = observation["redaction"]
    decision = "drop" if is_private_class or requested_redaction in {"drop_value", "drop_field"} else "keep"
    stored_representation = "label_and_class_only" if decision == "drop" else "synthetic_literal_allowed"

    return {
        "order": observation["order"],
        "field_id": observation["field_id"],
        "label": observation["label"],
        "field_class": observation["field_class"],
        "decision": decision,
        "stored_representation": stored_representation,
        "reason": observation["review_reason"],
    }


def _action_confirmation(action: Mapping[str, Any]) -> dict[str, Any]:
    action_type = action["action_type"]
    is_safe_read_only = action_type in SAFE_READ_ONLY_ACTIONS
    blocks_consequential_action = action_type in CONSEQUENTIAL_ACTIONS or action["boundary"] != "read_only"

    return {
        "order": action["order"],
        "action_id": action["action_id"],
        "action_type": action_type,
        "read_only_confirmed": is_safe_read_only and action["boundary"] == "read_only",
        "consequential_action_blocked": blocks_consequential_action,
        "confirmation": action["confirmation"],
    }


def _reviewer_checks(field_decisions: list[Mapping[str, Any]], action_confirmations: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    order = 1

    for decision in sorted(field_decisions, key=lambda item: (item["order"], item["field_id"])):
        checks.append(
            {
                "order": order,
                "check_id": f"field-redaction-{decision['field_id']}",
                "check_type": "field_redaction",
                "expected_result": decision["decision"],
                "review_instruction": f"Confirm {decision['field_id']} stores {decision['stored_representation']}.",
            }
        )
        order += 1

    for confirmation in sorted(action_confirmations, key=lambda item: (item["order"], item["action_id"])):
        checks.append(
            {
                "order": order,
                "check_id": f"action-boundary-{confirmation['action_id']}",
                "check_type": "action_boundary",
                "expected_result": "read_only" if confirmation["read_only_confirmed"] else "blocked_or_review_required",
                "review_instruction": f"Confirm {confirmation['action_id']} does not cross the read-only boundary.",
            }
        )
        order += 1

    checks.append(
        {
            "order": order,
            "check_id": "artifact-exclusion",
            "check_type": "artifact_exclusion",
            "expected_result": "no_private_artifacts_stored",
            "review_instruction": "Confirm the packet contains no screenshots, traces, HAR files, auth state, private values, account identifiers, uploads, submissions, payments, scheduling, cancellations, or active surface-map changes.",
        }
    )
    return checks


def _private_value_exclusion_attestations(plan: Mapping[str, Any], field_decisions: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    dropped_private_fields = [item["field_id"] for item in field_decisions if item["decision"] == "drop"]
    return [
        {
            "attestation_id": "synthetic-fixture-only",
            "status": "confirmed",
            "statement": f"Plan {plan['plan_id']} is a synthetic fixture and contains no live DevHub page values.",
        },
        {
            "attestation_id": "private-field-values-excluded",
            "status": "confirmed",
            "statement": "Private or account-identifying fields are represented only by field id, label, class, and drop decision.",
            "covered_field_ids": dropped_private_fields,
        },
        {
            "attestation_id": "private-artifacts-excluded",
            "status": "confirmed",
            "statement": "No screenshots, traces, HAR files, auth state, uploads, submissions, payment artifacts, scheduling artifacts, cancellation artifacts, or active surface-map updates are included.",
        },
    ]


def _unresolved_risks(field_decisions: list[Mapping[str, Any]], action_confirmations: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    risks: list[dict[str, Any]] = []

    if not any(item["decision"] == "drop" for item in field_decisions):
        risks.append(
            {
                "risk_id": "no-private-field-example",
                "severity": "review",
                "note": "Fixture has no private-class field example; add one before using this packet shape for a broader review.",
            }
        )

    if any(item["consequential_action_blocked"] for item in action_confirmations):
        risks.append(
            {
                "risk_id": "consequential-action-present",
                "severity": "blocked",
                "note": "One or more planned actions are consequential or outside read-only scope and must remain blocked.",
            }
        )

    if not risks:
        risks.append(
            {
                "risk_id": "none-known-for-fixture",
                "severity": "info",
                "note": "No unresolved fixture risks remain after redaction and read-only boundary checks.",
            }
        )

    return risks


def _required_text(mapping: Mapping[str, Any], key: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ObservationPacketError(f"required text field missing or empty: {key}")
    return value


def _reject_prohibited_keys(value: Any, path: str = "plan") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            if key_text.lower() in PROHIBITED_ARTIFACT_KEYS:
                raise ObservationPacketError(f"prohibited private artifact key at {path}.{key_text}")
            _reject_prohibited_keys(child, f"{path}.{key_text}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_prohibited_keys(child, f"{path}[{index}]")


def _present(value: Any) -> bool:
    return value is not None and value != "" and value != [] and value != {}


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


def _contains_private_or_artifact_claim(packet: Mapping[str, Any]) -> bool:
    return any(PRIVATE_OR_ARTIFACT_RE.search(text) for text in _walk_text(packet))


def _contains_automated_login_or_mfa_claim(packet: Mapping[str, Any]) -> bool:
    return any(AUTOMATED_LOGIN_OR_MFA_RE.search(text) for text in _walk_text(packet))


def _contains_consequential_enablement(packet: Mapping[str, Any]) -> bool:
    return any(CONSEQUENTIAL_ENABLEMENT_RE.search(text) for text in _walk_text(packet))


def _contains_legal_or_permit_guarantee(packet: Mapping[str, Any]) -> bool:
    return any(LEGAL_OR_PERMIT_GUARANTEE_RE.search(text) for text in _walk_text(packet))


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


def utc_now_iso() -> str:
    """Return an ISO timestamp for callers that need runtime metadata outside fixtures."""

    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
