"""Validation for DevHub observed surface inactive patch preview v1.

This module is fixture-first and offline-only. It validates review preview
packets for inactive DevHub observed surface deltas before any registry,
guardrail, prompt, or release-state mutation can be considered.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

PREVIEW_VERSION = "devhub_observed_surface_inactive_patch_preview_v1"

_ALLOWED_DISPOSITIONS = {"approved"}
_ALLOWED_MUTATION_FLAGS = {
    "inactive_preview_only",
    "fixture_first",
    "no_live_devhub_access",
    "no_active_surface_mutation",
    "no_guardrail_mutation",
    "no_prompt_mutation",
    "no_release_state_mutation",
}
_REQUIRED_TOP_LEVEL_SEQUENCES = (
    ("disposition_rows", "missing_disposition_rows", "approved reviewer disposition rows are required"),
    ("inactive_surface_map_delta_previews", "missing_inactive_surface_map_delta_previews", "inactive surface-map delta previews are required"),
    ("selector_confidence_placeholders", "missing_selector_confidence_placeholders", "selector-confidence placeholders are required"),
    ("accessible_role_name_evidence_placeholders", "missing_accessible_role_name_evidence_placeholders", "accessible role/name evidence placeholders are required"),
    ("redacted_field_inventory_placeholders", "missing_redacted_field_inventory_placeholders", "redacted field inventory placeholders are required"),
    ("action_classification_references", "missing_action_classification_references", "action classification references are required"),
    ("reviewer_signoff_placeholders", "missing_reviewer_signoff_placeholders", "reviewer signoff placeholders are required"),
    ("validation_commands", "missing_validation_commands", "validation commands are required"),
)

_ARTIFACT_KEY_TERMS = (
    "credential",
    "password",
    "secret",
    "token",
    "cookie",
    "session",
    "auth_state",
    "storage_state",
    "browser_artifact",
    "browser_profile",
    "trace",
    "har",
    "screenshot",
)
_PRIVATE_VALUE_KEY_TERMS = (
    "account_id",
    "address",
    "applicant",
    "case_number",
    "email",
    "license_number",
    "permit_number",
    "phone",
    "private_page_value",
    "private_value",
    "username",
)
_ARTIFACT_TEXT_TERMS = (
    "auth.json",
    "browser profile",
    "cookie:",
    "credentials",
    "har file",
    ".har",
    "password=",
    "playwright trace",
    "screenshot",
    "session state",
    "storage-state.json",
    "trace.zip",
)
_PRIVATE_VALUE_TEXT_TERMS = (
    "private page value",
    "private applicant",
    "real permit number",
    "unredacted field value",
)
_LIVE_ACCESS_CLAIMS = (
    "live devhub access",
    "live devhub run",
    "observed in live devhub",
    "authenticated devhub session",
    "browser automation completed",
    "playwright clicked",
)
_CONSEQUENTIAL_ACTION_TERMS = (
    "cancel permit",
    "certify application",
    "complete payment",
    "final submit",
    "make payment",
    "purchase permit",
    "schedule inspection",
    "submit application",
    "submit permit",
    "upload correction",
    "upload plans",
)
_OUTCOME_TERMS = (
    "approval guaranteed",
    "guaranteed approval",
    "legally sufficient",
    "permit will be approved",
    "will be issued",
)
_FORBIDDEN_MUTATION_KEYS = (
    "active_surface_mutation",
    "active_surface_registry_mutation",
    "guardrail_mutation",
    "mutates_guardrails",
    "prompt_mutation",
    "mutates_prompts",
    "release_state_mutation",
    "mutates_release_state",
)


@dataclass(frozen=True)
class PreviewValidationFinding:
    """A deterministic validation finding for inactive patch preview packets."""

    code: str
    message: str


def validate_devhub_observed_surface_inactive_patch_preview_v1(
    packet: Mapping[str, Any],
) -> list[PreviewValidationFinding]:
    """Return validation findings for a v1 inactive observed-surface preview."""

    findings: list[PreviewValidationFinding] = []

    if packet.get("preview_version") != PREVIEW_VERSION:
        findings.append(
            PreviewValidationFinding(
                "wrong_preview_version",
                f"preview_version must be {PREVIEW_VERSION}",
            )
        )

    if packet.get("scope") != "inactive_observed_surface_patch_preview":
        findings.append(
            PreviewValidationFinding(
                "outside_inactive_preview_scope",
                "scope must be inactive_observed_surface_patch_preview",
            )
        )

    for key, code, message in _REQUIRED_TOP_LEVEL_SEQUENCES:
        _require_non_empty_list(packet, key, code, message, findings)

    _validate_disposition_rows(packet.get("disposition_rows"), findings)
    _validate_surface_delta_previews(packet.get("inactive_surface_map_delta_previews"), findings)
    _validate_surface_referenced_lists(packet, findings)
    _validate_validation_commands(packet.get("validation_commands"), findings)
    _validate_mutation_flags(packet.get("mutation_flags"), findings)
    _reject_forbidden_keys_and_values(packet, "$", findings)
    _reject_forbidden_text(packet, findings)

    return findings


def assert_valid_devhub_observed_surface_inactive_patch_preview_v1(packet: Mapping[str, Any]) -> None:
    """Raise ValueError when a preview packet is invalid."""

    findings = validate_devhub_observed_surface_inactive_patch_preview_v1(packet)
    if findings:
        detail = "; ".join(f"{finding.code}: {finding.message}" for finding in findings)
        raise ValueError(detail)


def _require_non_empty_list(
    packet: Mapping[str, Any],
    key: str,
    code: str,
    message: str,
    findings: list[PreviewValidationFinding],
) -> None:
    value = packet.get(key)
    if not isinstance(value, list) or not value:
        findings.append(PreviewValidationFinding(code, message))


def _validate_disposition_rows(value: Any, findings: list[PreviewValidationFinding]) -> None:
    if not isinstance(value, list):
        return
    for index, row in enumerate(value):
        path = f"disposition_rows[{index}]"
        if not isinstance(row, Mapping):
            findings.append(PreviewValidationFinding("invalid_disposition_row", f"{path} must be an object"))
            continue
        if not _non_empty_string(row.get("surface_id")):
            findings.append(PreviewValidationFinding("invalid_disposition_row", f"{path}.surface_id is required"))
        disposition = str(row.get("disposition", "")).strip().lower()
        if disposition not in _ALLOWED_DISPOSITIONS:
            findings.append(
                PreviewValidationFinding(
                    "unapproved_disposition_row",
                    f"{path}.disposition must be approved before preview is accepted",
                )
            )
        if not _non_empty_string(row.get("reviewer")):
            findings.append(PreviewValidationFinding("missing_disposition_reviewer", f"{path}.reviewer is required"))
        if not _non_empty_string(row.get("evidence_ref")):
            findings.append(PreviewValidationFinding("missing_disposition_evidence", f"{path}.evidence_ref is required"))


def _validate_surface_delta_previews(value: Any, findings: list[PreviewValidationFinding]) -> None:
    if not isinstance(value, list):
        return
    for index, row in enumerate(value):
        path = f"inactive_surface_map_delta_previews[{index}]"
        if not isinstance(row, Mapping):
            findings.append(PreviewValidationFinding("invalid_surface_delta_preview", f"{path} must be an object"))
            continue
        if row.get("surface_state") != "inactive":
            findings.append(PreviewValidationFinding("surface_delta_not_inactive", f"{path}.surface_state must be inactive"))
        if row.get("read_only") is not True:
            findings.append(PreviewValidationFinding("surface_delta_not_read_only", f"{path}.read_only must be true"))
        for key in ("surface_id", "before", "after", "delta_summary", "evidence_ref"):
            if not _present(row.get(key)):
                findings.append(PreviewValidationFinding("invalid_surface_delta_preview", f"{path}.{key} is required"))


def _validate_surface_referenced_lists(packet: Mapping[str, Any], findings: list[PreviewValidationFinding]) -> None:
    checks = (
        ("selector_confidence_placeholders", "selector_confidence", "missing_selector_confidence_placeholder"),
        ("accessible_role_name_evidence_placeholders", "role_name_evidence", "missing_accessible_role_name_evidence_placeholder"),
        ("redacted_field_inventory_placeholders", "redacted_field_inventory", "missing_redacted_field_inventory_placeholder"),
        ("action_classification_references", "action_classification", "missing_action_classification_reference"),
        ("reviewer_signoff_placeholders", "reviewer_signoff", "missing_reviewer_signoff_placeholder"),
    )
    for key, evidence_key, code in checks:
        value = packet.get(key)
        if not isinstance(value, list):
            continue
        for index, row in enumerate(value):
            path = f"{key}[{index}]"
            if not isinstance(row, Mapping):
                findings.append(PreviewValidationFinding(code, f"{path} must be an object"))
                continue
            if not _non_empty_string(row.get("surface_id")):
                findings.append(PreviewValidationFinding(code, f"{path}.surface_id is required"))
            if not _present(row.get(evidence_key)) and not _present(row.get("placeholder")):
                findings.append(PreviewValidationFinding(code, f"{path} must include {evidence_key} or placeholder"))
            if not _non_empty_string(row.get("evidence_ref")):
                findings.append(PreviewValidationFinding(code, f"{path}.evidence_ref is required"))


def _validate_validation_commands(value: Any, findings: list[PreviewValidationFinding]) -> None:
    if not isinstance(value, list):
        return
    for index, command in enumerate(value):
        if not isinstance(command, list) or not command or not all(isinstance(part, str) and part for part in command):
            findings.append(
                PreviewValidationFinding(
                    "invalid_validation_command",
                    f"validation_commands[{index}] must be a non-empty argv list of strings",
                )
            )


def _validate_mutation_flags(value: Any, findings: list[PreviewValidationFinding]) -> None:
    if value is None:
        findings.append(PreviewValidationFinding("missing_mutation_flags", "mutation_flags must declare inactive preview-only flags"))
        return
    if not isinstance(value, list) or not value:
        findings.append(PreviewValidationFinding("invalid_mutation_flags", "mutation_flags must be a non-empty list"))
        return
    for flag in value:
        if flag not in _ALLOWED_MUTATION_FLAGS:
            findings.append(
                PreviewValidationFinding(
                    "mutation_flag_outside_inactive_preview_scope",
                    f"mutation flag {flag!r} is outside inactive preview scope",
                )
            )


def _reject_forbidden_keys_and_values(value: Any, path: str, findings: list[PreviewValidationFinding]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key).lower()
            child_path = f"{path}.{key}"
            if any(term in key_text for term in _ARTIFACT_KEY_TERMS):
                findings.append(
                    PreviewValidationFinding(
                        "credential_session_auth_or_browser_artifact_key",
                        f"{child_path} references credentials, session/auth state, screenshots, traces, HAR, or browser artifacts",
                    )
                )
            if any(term in key_text for term in _PRIVATE_VALUE_KEY_TERMS):
                findings.append(
                    PreviewValidationFinding(
                        "private_page_value_key",
                        f"{child_path} references private DevHub page values",
                    )
                )
            if key_text in _FORBIDDEN_MUTATION_KEYS and child is True:
                findings.append(
                    PreviewValidationFinding(
                        "active_mutation_flag_enabled",
                        f"{child_path} enables active surface, guardrail, prompt, or release-state mutation",
                    )
                )
            _reject_forbidden_keys_and_values(child, child_path, findings)
        return
    if isinstance(value, list):
        for index, child in enumerate(value):
            _reject_forbidden_keys_and_values(child, f"{path}[{index}]", findings)


def _reject_forbidden_text(packet: Mapping[str, Any], findings: list[PreviewValidationFinding]) -> None:
    text = "\n".join(_walk_text(packet)).lower()
    checks = (
        (_ARTIFACT_TEXT_TERMS, "credential_session_auth_or_browser_artifact_text", "credential/session/auth/browser artifacts, screenshots, traces, or HAR files are not allowed"),
        (_PRIVATE_VALUE_TEXT_TERMS, "private_page_value_text", "private DevHub page values are not allowed"),
        (_LIVE_ACCESS_CLAIMS, "live_devhub_access_claim", "live DevHub access claims are not allowed"),
        (_CONSEQUENTIAL_ACTION_TERMS, "consequential_official_action_language", "consequential official action language is not allowed"),
        (_OUTCOME_TERMS, "consequential_outcome_language", "official approval or legal outcome language is not allowed"),
    )
    for terms, code, message in checks:
        if any(term in text for term in terms):
            findings.append(PreviewValidationFinding(code, message))


def _walk_text(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
        return
    if isinstance(value, Mapping):
        for key, child in value.items():
            yield str(key)
            yield from _walk_text(child)
        return
    if isinstance(value, list):
        for child in value:
            yield from _walk_text(child)


def _present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)
    return True


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())
