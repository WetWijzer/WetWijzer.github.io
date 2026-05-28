"""Commit-safe attended DevHub handoff checklist validation.

The checklist is fixture-first: committed artifacts describe the session
handoff policy, not a user's browser state, credentials, or private case data.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


class HandoffValidationError(ValueError):
    """Raised when an attended handoff checklist is incomplete or unsafe."""


class ScopeKind(str, Enum):
    READ_ONLY = "read_only"
    REVERSIBLE_DRAFT = "reversible_draft"


FORBIDDEN_STORAGE_KEYS = {
    "auth_state",
    "browser_state",
    "captcha",
    "cookie",
    "cookies",
    "credential",
    "credentials",
    "har",
    "local_private_path",
    "mfa_secret",
    "password",
    "payment_detail",
    "payment_details",
    "private_value",
    "private_values",
    "raw_authenticated_html",
    "raw_crawl_output",
    "screenshot",
    "session_storage",
    "trace",
    "upload_content",
}

PRIVATE_ARTIFACT_FORBIDDEN_STORAGE_KEYS = {
    "auth_state",
    "cookie",
    "cookies",
    "har",
    "local_private_path",
    "screenshot",
    "trace",
}

PROHIBITED_PERMITTED_SCOPE_TERMS = {
    "account_creation": "account creation",
    "auth_state": "auth state",
    "cancel": "cancellation",
    "cancellation": "cancellation",
    "captcha": "CAPTCHA",
    "certification": "certification",
    "certify": "certification",
    "cookie": "cookies",
    "cookies": "cookies",
    "har": "HAR data",
    "mfa": "MFA",
    "password_recovery": "password recovery",
    "payment": "payment",
    "schedule": "scheduling",
    "scheduling": "scheduling",
    "screenshot": "screenshots",
    "submission": "submission",
    "submit": "submission",
    "trace": "traces",
    "upload": "upload",
}

REQUIRED_MANUAL_LOGIN_PREREQUISITES = {
    "user_attended_visible_browser",
    "user_completes_portlandoregon_login",
    "user_completes_mfa_captcha_or_security_prompts",
    "no_credentials_requested_or_stored",
    "no_account_creation_or_password_recovery",
}

REQUIRED_REDACTION_REQUIREMENTS = {
    "credentials",
    "cookies_and_tokens",
    "mfa_captcha_security_answers",
    "private_form_values",
    "payment_details",
    "uploaded_document_contents",
    "local_private_file_paths",
    "screenshots_traces_har",
}

REQUIRED_EXACT_CONFIRMATION_BOUNDARIES = {
    "submit_permit_request",
    "certify_acknowledgement",
    "upload_to_official_record",
    "purchase_trade_permit",
    "schedule_inspection",
    "cancel_withdraw_extend_or_reactivate",
    "enter_or_submit_payment_details",
    "change_account_or_security_settings",
}

REQUIRED_ABORT_CONDITIONS = {
    "captcha_or_mfa_needs_user_action",
    "credentials_or_private_values_requested_by_worker",
    "scope_or_consequence_unclear",
    "official_submission_or_payment_boundary_reached",
    "unexpected_upload_or_certification_prompt",
    "robot_terms_or_access_control_conflict",
    "user_absent_or_confirmation_missing",
}


@dataclass(frozen=True)
class AttendedHandoffChecklist:
    """Validated attended-session handoff policy for DevHub automation."""

    checklist_id: str
    manual_login_prerequisites: tuple[str, ...]
    permitted_read_only_scopes: tuple[str, ...]
    permitted_reversible_draft_scopes: tuple[str, ...]
    redaction_requirements: tuple[str, ...]
    exact_confirmation_boundaries: tuple[str, ...]
    abort_conditions: tuple[str, ...]
    forbidden_storage: tuple[str, ...]
    stores_browser_state: bool
    stores_private_values: bool

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any]) -> "AttendedHandoffChecklist":
        checklist = cls(
            checklist_id=_required_string(payload, "checklist_id"),
            manual_login_prerequisites=_required_string_tuple(payload, "manual_login_prerequisites"),
            permitted_read_only_scopes=_required_string_tuple(payload, "permitted_read_only_scopes"),
            permitted_reversible_draft_scopes=_required_string_tuple(payload, "permitted_reversible_draft_scopes"),
            redaction_requirements=_required_string_tuple(payload, "redaction_requirements"),
            exact_confirmation_boundaries=_required_string_tuple(payload, "exact_confirmation_boundaries"),
            abort_conditions=_required_string_tuple(payload, "abort_conditions"),
            forbidden_storage=_required_string_tuple(payload, "forbidden_storage"),
            stores_browser_state=_required_bool(payload, "stores_browser_state"),
            stores_private_values=_required_bool(payload, "stores_private_values"),
        )
        checklist.validate()
        return checklist

    @classmethod
    def from_json_file(cls, path: Path) -> "AttendedHandoffChecklist":
        with path.open("r", encoding="utf-8") as fixture_file:
            payload = json.load(fixture_file)
        if not isinstance(payload, Mapping):
            raise HandoffValidationError("handoff checklist fixture must contain a JSON object")
        return cls.from_mapping(payload)

    def validate(self) -> None:
        _reject_local_private_paths(self)
        _require_subset(
            REQUIRED_MANUAL_LOGIN_PREREQUISITES,
            self.manual_login_prerequisites,
            "manual_login_prerequisites",
        )
        _require_subset(
            REQUIRED_REDACTION_REQUIREMENTS,
            self.redaction_requirements,
            "redaction_requirements",
        )
        _require_subset(
            REQUIRED_EXACT_CONFIRMATION_BOUNDARIES,
            self.exact_confirmation_boundaries,
            "exact_confirmation_boundaries",
        )
        _require_subset(REQUIRED_ABORT_CONDITIONS, self.abort_conditions, "abort_conditions")
        _require_subset(FORBIDDEN_STORAGE_KEYS, self.forbidden_storage, "forbidden_storage")
        _require_subset(
            PRIVATE_ARTIFACT_FORBIDDEN_STORAGE_KEYS,
            self.forbidden_storage,
            "forbidden_storage",
        )
        _reject_prohibited_permitted_scopes("permitted_read_only_scopes", self.permitted_read_only_scopes)
        _reject_prohibited_permitted_scopes(
            "permitted_reversible_draft_scopes",
            self.permitted_reversible_draft_scopes,
        )

        if self.stores_browser_state:
            raise HandoffValidationError("attended handoff checklist must not store browser state")
        if self.stores_private_values:
            raise HandoffValidationError("attended handoff checklist must not store private values")
        if not self.permitted_read_only_scopes:
            raise HandoffValidationError("at least one read-only scope is required")
        if not self.permitted_reversible_draft_scopes:
            raise HandoffValidationError("at least one reversible-draft scope is required")

    def permitted_scopes(self, kind: ScopeKind) -> tuple[str, ...]:
        if kind is ScopeKind.READ_ONLY:
            return self.permitted_read_only_scopes
        if kind is ScopeKind.REVERSIBLE_DRAFT:
            return self.permitted_reversible_draft_scopes
        raise HandoffValidationError(f"unsupported scope kind: {kind!r}")


def load_default_attended_handoff_checklist() -> AttendedHandoffChecklist:
    fixture_path = Path(__file__).parents[1] / "tests" / "fixtures" / "devhub" / "attended_handoff_checklist.json"
    return AttendedHandoffChecklist.from_json_file(fixture_path)


def _required_string(payload: Mapping[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise HandoffValidationError(f"{key} must be a non-empty string")
    return value


def _required_bool(payload: Mapping[str, Any], key: str) -> bool:
    value = payload.get(key)
    if not isinstance(value, bool):
        raise HandoffValidationError(f"{key} must be a boolean")
    return value


def _required_string_tuple(payload: Mapping[str, Any], key: str) -> tuple[str, ...]:
    value = payload.get(key)
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise HandoffValidationError(f"{key} must be a list of strings")
    values: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise HandoffValidationError(f"{key} must contain only non-empty strings")
        values.append(item)
    if not values:
        raise HandoffValidationError(f"{key} must not be empty")
    return tuple(values)


def _require_subset(required: set[str], actual: Sequence[str], field_name: str) -> None:
    actual_set = set(actual)
    missing = sorted(required - actual_set)
    if missing:
        raise HandoffValidationError(f"{field_name} is missing required entries: {', '.join(missing)}")


def _reject_local_private_paths(checklist: AttendedHandoffChecklist) -> None:
    for field_name, values in _string_sequence_fields(checklist):
        for value in values:
            lowered = value.lower()
            if "file://" in lowered or "/users/" in lowered or "/home/" in lowered:
                raise HandoffValidationError(f"{field_name} contains a local private path")


def _reject_prohibited_permitted_scopes(field_name: str, scopes: Sequence[str]) -> None:
    for scope in scopes:
        normalized_scope = scope.replace("-", "_").lower()
        for term, label in PROHIBITED_PERMITTED_SCOPE_TERMS.items():
            if term in normalized_scope:
                raise HandoffValidationError(f"{field_name} must reject {label}: {scope}")


def _string_sequence_fields(checklist: AttendedHandoffChecklist) -> tuple[tuple[str, tuple[str, ...]], ...]:
    return (
        ("manual_login_prerequisites", checklist.manual_login_prerequisites),
        ("permitted_read_only_scopes", checklist.permitted_read_only_scopes),
        ("permitted_reversible_draft_scopes", checklist.permitted_reversible_draft_scopes),
        ("redaction_requirements", checklist.redaction_requirements),
        ("exact_confirmation_boundaries", checklist.exact_confirmation_boundaries),
        ("abort_conditions", checklist.abort_conditions),
        ("forbidden_storage", checklist.forbidden_storage),
    )
