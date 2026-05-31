"""Offline validator for attended DevHub read-only authorization packet v2.

The packet is fixture-first by design: it describes what a user-attended,
read-only DevHub observation may prove before any live browser session exists.
It must not create browser state, screenshots, traces, HAR files, credentials, or
raw authenticated page captures.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


PACKET_VERSION = "devhub-attended-readonly-authorization-packet-v2"
_FORBIDDEN_ARTIFACT_TYPES = {
    "auth_state",
    "browser_context_storage",
    "browser_profile",
    "cookie_jar",
    "credential",
    "downloaded_document",
    "har",
    "local_private_file_path",
    "raw_authenticated_html",
    "screenshot",
    "session_recording",
    "storage_state",
    "trace",
}
_FORBIDDEN_AUTOMATION_ACTIONS = {
    "account_creation",
    "authentication",
    "captcha",
    "certification",
    "mfa",
    "payment",
    "schedule_inspection",
    "submission",
    "upload",
}
_ALLOWED_TARGET_MODES = {"read_only_observation"}
_REQUIRED_ATTENDANCE_EVIDENCE_IDS = {
    "synthetic-attendance-ack-v2",
    "synthetic-readonly-scope-v2",
    "synthetic-no-artifact-storage-v2",
}
_REQUIRED_SURFACE_IDS = {
    "devhub_home_readonly_v2",
    "my_permits_requests_readonly_v2",
    "permit_detail_status_readonly_v2",
    "attachment_list_readonly_v2",
    "inspection_results_readonly_v2",
}
_REQUIRED_POST_REVIEW_IDS = {
    "review-redaction-completeness-v2",
    "review-surface-classification-v2",
    "review-abort-handling-v2",
    "review-source-gap-followup-v2",
}
_REQUIRED_OFFLINE_COMMANDS = {
    (
        "python3",
        "-m",
        "py_compile",
        "ppd/devhub/attended_readonly_authorization_packet_v2.py",
        "ppd/tests/test_attended_readonly_authorization_packet_v2.py",
    ),
    (
        "python3",
        "-m",
        "pytest",
        "ppd/tests/test_attended_readonly_authorization_packet_v2.py",
    ),
    ("python3", "ppd/daemon/ppd_daemon.py", "--self-test"),
}
_REQUIRED_MANUAL_LOGIN_TERMS = (
    "credentials",
    "manually select sign-in",
    "manually complete mfa",
    "captcha",
    "account recovery",
    "must not create accounts",
    "bypass access controls",
)
_REQUIRED_REDACTION_TERMS = (
    "names",
    "addresses",
    "permit numbers",
    "payment details",
    "raw authenticated page text",
    "screenshots",
    "traces",
    "har files",
    "downloaded files",
    "cookies",
    "private local file paths",
    "synthetic",
)
_REQUIRED_ABORT_TERMS = (
    "credentials",
    "payment",
    "submit",
    "certify",
    "upload",
    "schedule",
    "cancel",
    "user is no longer present",
    "read-only observation",
    "auth state",
    "screenshots",
    "downloads",
)
_MUTATION_FLAG_KEYS = (
    "active_devhub_surface_mutation",
    "active_devhub_prompt_mutation",
    "active_devhub_guardrail_mutation",
    "active_devhub_source_mutation",
    "active_devhub_process_model_mutation",
    "active_devhub_contract_mutation",
    "active_devhub_release_state_mutation",
    "mutates_devhub_surface",
    "mutates_prompt",
    "mutates_guardrail",
    "mutates_source",
    "mutates_process_model",
    "mutates_contract",
    "mutates_release_state",
)
_CLAIM_LIST_KEYS = (
    "live_authenticated_claims",
    "official_action_completion_claims",
    "legal_or_permitting_guarantees",
)
_LIVE_AUTHENTICATED_PATTERNS = (
    re.compile(r"\blive authenticated\b", re.IGNORECASE),
    re.compile(r"\bauthenticated devhub (?:run|session|observation) (?:completed|captured|verified)\b", re.IGNORECASE),
    re.compile(r"\blogged in (?:successfully|and observed|and captured)\b", re.IGNORECASE),
)
_OFFICIAL_ACTION_PATTERNS = (
    re.compile(r"\bofficial action completed\b", re.IGNORECASE),
    re.compile(r"\bpermit (?:request |application )?submitted\b", re.IGNORECASE),
    re.compile(r"\bpayment (?:completed|submitted|paid)\b", re.IGNORECASE),
    re.compile(r"\binspection scheduled\b", re.IGNORECASE),
    re.compile(r"\b(?:certification|upload|cancellation|withdrawal) completed\b", re.IGNORECASE),
)
_GUARANTEE_PATTERNS = (
    re.compile(r"\bguarantee[sd]?\b", re.IGNORECASE),
    re.compile(r"\bwill be approved\b", re.IGNORECASE),
    re.compile(r"\bpermit issuance (?:is )?(?:certain|assured)\b", re.IGNORECASE),
    re.compile(r"\blegal advice\b", re.IGNORECASE),
)


class PacketValidationError(ValueError):
    """Raised when the authorization packet is not safe to use."""


def load_packet(path: str | Path) -> dict[str, Any]:
    """Load a JSON authorization packet from a fixture path."""

    packet_path = Path(path)
    with packet_path.open("r", encoding="utf-8") as handle:
        packet = json.load(handle)
    if not isinstance(packet, dict):
        raise PacketValidationError("packet root must be an object")
    return packet


def validate_packet(packet: dict[str, Any]) -> list[str]:
    """Return deterministic validation findings for packet v2.

    An empty list means the fixture is valid. Findings are stable strings so the
    daemon and tests can compare them without needing live DevHub access.
    """

    findings: list[str] = []

    if packet.get("packet_version") != PACKET_VERSION:
        findings.append("packet_version must be devhub-attended-readonly-authorization-packet-v2")

    if packet.get("authorization_mode") != "fixture_first_attended_read_only":
        findings.append("authorization_mode must be fixture_first_attended_read_only")

    if packet.get("live_devhub_access_permitted") is not False:
        findings.append("live_devhub_access_permitted must be false for this packet")

    if packet.get("creates_browser_state") is not False:
        findings.append("creates_browser_state must be false")

    _require_non_empty_list(packet, "synthetic_user_attended_preflight_evidence", findings)
    _require_non_empty_list(packet, "manual_login_boundaries", findings)
    _require_non_empty_list(packet, "read_only_target_surfaces", findings)
    _require_non_empty_list(packet, "redaction_expectations", findings)
    _require_non_empty_list(packet, "abort_conditions", findings)
    _require_non_empty_list(packet, "post_observation_review_placeholders", findings)
    _require_non_empty_list(packet, "offline_validation_commands", findings)

    _require_id_set(
        packet.get("synthetic_user_attended_preflight_evidence"),
        "evidence_id",
        _REQUIRED_ATTENDANCE_EVIDENCE_IDS,
        "synthetic_user_attended_preflight_evidence",
        findings,
    )
    _require_text_terms(packet.get("manual_login_boundaries"), _REQUIRED_MANUAL_LOGIN_TERMS, "manual_login_boundaries", findings)
    _require_text_terms(packet.get("redaction_expectations"), _REQUIRED_REDACTION_TERMS, "redaction_expectations", findings)
    _require_text_terms(packet.get("abort_conditions"), _REQUIRED_ABORT_TERMS, "abort_conditions", findings)
    _require_id_set(
        packet.get("read_only_target_surfaces"),
        "surface_id",
        _REQUIRED_SURFACE_IDS,
        "read_only_target_surfaces",
        findings,
    )
    _require_id_set(
        packet.get("post_observation_review_placeholders"),
        "placeholder_id",
        _REQUIRED_POST_REVIEW_IDS,
        "post_observation_review_placeholders",
        findings,
    )
    _require_offline_validation_commands(packet.get("offline_validation_commands"), findings)
    _reject_claim_lists(packet, findings)
    _reject_mutation_flags(packet, findings)
    _reject_forbidden_claim_text(packet, findings)
    _reject_private_artifact_outputs(packet, findings)

    artifact_types = set()
    for artifact in packet.get("prohibited_artifacts", []):
        artifact_type = artifact.get("artifact_type") if isinstance(artifact, dict) else None
        if artifact_type not in _FORBIDDEN_ARTIFACT_TYPES:
            findings.append(f"prohibited_artifacts contains unsupported artifact_type: {artifact_type}")
        elif artifact_type in artifact_types:
            findings.append(f"prohibited_artifacts contains duplicate artifact_type: {artifact_type}")
        else:
            artifact_types.add(artifact_type)
    missing_artifacts = sorted(_FORBIDDEN_ARTIFACT_TYPES - artifact_types)
    if missing_artifacts:
        findings.append("prohibited_artifacts missing forbidden artifact types: " + ", ".join(missing_artifacts))

    for action in packet.get("prohibited_automation_actions", []):
        if action not in _FORBIDDEN_AUTOMATION_ACTIONS:
            findings.append(f"prohibited_automation_actions contains unsupported action: {action}")
    missing_actions = sorted(_FORBIDDEN_AUTOMATION_ACTIONS - set(packet.get("prohibited_automation_actions", [])))
    if missing_actions:
        findings.append("prohibited_automation_actions missing actions: " + ", ".join(missing_actions))

    for surface in packet.get("read_only_target_surfaces", []):
        if not isinstance(surface, dict):
            findings.append("read_only_target_surfaces entries must be objects")
            continue
        if surface.get("target_mode") not in _ALLOWED_TARGET_MODES:
            findings.append(f"surface {surface.get('surface_id')} must use read_only_observation mode")
        if surface.get("requires_user_attendance") is not True:
            findings.append(f"surface {surface.get('surface_id')} must require user attendance")
        if surface.get("allowed_actions") != ["observe_visible_text", "record_redacted_metadata"]:
            findings.append(f"surface {surface.get('surface_id')} has unsafe allowed_actions")

    for command in packet.get("offline_validation_commands", []):
        if not _is_offline_command(command):
            findings.append(f"offline_validation_commands contains non-offline command: {command}")

    return findings


def assert_valid_packet(packet: dict[str, Any]) -> None:
    """Raise PacketValidationError if packet validation finds any issue."""

    findings = validate_packet(packet)
    if findings:
        raise PacketValidationError("; ".join(findings))


def _require_non_empty_list(packet: dict[str, Any], key: str, findings: list[str]) -> None:
    value = packet.get(key)
    if not isinstance(value, list) or not value:
        findings.append(f"{key} must be a non-empty list")


def _require_id_set(value: Any, key: str, required: set[str], label: str, findings: list[str]) -> None:
    if not isinstance(value, list):
        return
    observed = {entry.get(key) for entry in value if isinstance(entry, dict)}
    missing = sorted(required - observed)
    if missing:
        findings.append(f"{label} missing required ids: " + ", ".join(missing))


def _require_text_terms(value: Any, required_terms: tuple[str, ...], label: str, findings: list[str]) -> None:
    if not isinstance(value, list):
        return
    text = "\n".join(item for item in value if isinstance(item, str)).lower()
    missing = [term for term in required_terms if term not in text]
    if missing:
        findings.append(f"{label} missing required terms: " + ", ".join(missing))


def _require_offline_validation_commands(value: Any, findings: list[str]) -> None:
    if not isinstance(value, list):
        return
    observed = {tuple(command) for command in value if isinstance(command, list)}
    missing = sorted(_REQUIRED_OFFLINE_COMMANDS - observed)
    if missing:
        rendered = [" ".join(command) for command in missing]
        findings.append("offline_validation_commands missing required commands: " + "; ".join(rendered))


def _reject_claim_lists(packet: dict[str, Any], findings: list[str]) -> None:
    for key in _CLAIM_LIST_KEYS:
        value = packet.get(key)
        if value not in (None, [], {}):
            findings.append(f"{key} must be absent or empty")


def _reject_mutation_flags(packet: dict[str, Any], findings: list[str]) -> None:
    for key in _MUTATION_FLAG_KEYS:
        if packet.get(key) is True:
            findings.append(f"{key} must not be true")


def _reject_forbidden_claim_text(packet: Any, findings: list[str]) -> None:
    for path, text in _walk_strings(packet):
        if path.startswith(("prohibited_artifacts", "prohibited_automation_actions", "abort_conditions")):
            continue
        for pattern in _LIVE_AUTHENTICATED_PATTERNS:
            if pattern.search(text):
                findings.append(f"live authenticated claim text is not allowed at {path}")
                break
        for pattern in _OFFICIAL_ACTION_PATTERNS:
            if pattern.search(text):
                findings.append(f"official-action completion claim text is not allowed at {path}")
                break
        for pattern in _GUARANTEE_PATTERNS:
            if pattern.search(text):
                findings.append(f"legal or permitting guarantee text is not allowed at {path}")
                break


def _reject_private_artifact_outputs(packet: dict[str, Any], findings: list[str]) -> None:
    for key in ("artifacts", "artifact_outputs", "created_artifacts", "persisted_artifacts", "session_artifacts"):
        value = packet.get(key)
        if value in (None, [], {}):
            continue
        if _contains_forbidden_artifact_type(value):
            findings.append(f"{key} must not include private/session/browser/raw/downloaded artifacts")
        else:
            findings.append(f"{key} must be absent or empty for fixture-first authorization")


def _contains_forbidden_artifact_type(value: Any) -> bool:
    if isinstance(value, dict):
        artifact_type = value.get("artifact_type") or value.get("type")
        if isinstance(artifact_type, str) and artifact_type in _FORBIDDEN_ARTIFACT_TYPES:
            return True
        return any(_contains_forbidden_artifact_type(item) for item in value.values())
    if isinstance(value, list):
        return any(_contains_forbidden_artifact_type(item) for item in value)
    if isinstance(value, str):
        normalized = value.lower().replace("-", "_").replace(" ", "_")
        return any(artifact_type in normalized for artifact_type in _FORBIDDEN_ARTIFACT_TYPES)
    return False


def _walk_strings(value: Any, path: str = "packet") -> list[tuple[str, str]]:
    if isinstance(value, str):
        return [(path, value)]
    if isinstance(value, dict):
        pairs: list[tuple[str, str]] = []
        for key, nested in value.items():
            pairs.extend(_walk_strings(nested, f"{path}.{key}"))
        return pairs
    if isinstance(value, list):
        pairs = []
        for index, nested in enumerate(value):
            pairs.extend(_walk_strings(nested, f"{path}[{index}]"))
        return pairs
    return []


def _is_offline_command(command: Any) -> bool:
    if not isinstance(command, list) or not command:
        return False
    if not all(isinstance(part, str) and part for part in command):
        return False

    joined = " ".join(command).lower()
    blocked_terms = (
        "devhub.portlandoregon.gov",
        "playwright",
        "browser",
        "crawl",
        "curl",
        "wget",
        "screenshot",
        "trace",
        "har",
        "login",
    )
    return not any(term in joined for term in blocked_terms)
