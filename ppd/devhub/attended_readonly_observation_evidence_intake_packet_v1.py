"""Fixture-first attended DevHub read-only observation evidence intake packet v1.

This module validates an offline intake packet that consumes only synthetic
renewal authorization rows and redacted observation placeholders. It records
read-only page metadata and stop/handoff notes without opening DevHub, storing
browser artifacts, preserving private values, or mutating active PP&D surfaces.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Mapping, Sequence

PACKET_VERSION = "attended_devhub_read_only_observation_evidence_intake_packet_v1"
ALLOWED_CLASSIFICATIONS = frozenset({"safe_read_only", "read_only_observation"})
ALLOWED_AUTHORIZATION_ORIGINS = frozenset({"synthetic_renewal_authorization_row"})
ALLOWED_PLACEHOLDER_ORIGINS = frozenset({"redacted_observation_placeholder"})

REQUIRED_FALSE_ARTIFACT_FLAGS = (
    "opens_devhub",
    "stores_credentials",
    "stores_session_state",
    "stores_browser_artifacts",
    "stores_auth_files",
    "stores_screenshots",
    "stores_traces",
    "stores_har_files",
    "stores_private_values",
    "stores_raw_crawl_output",
    "stores_downloaded_documents",
    "performs_form_filling",
    "performs_uploads",
    "performs_submissions",
    "performs_certifications",
    "performs_payments",
    "performs_inspection_scheduling",
    "performs_cancellations",
    "performs_account_changes",
    "performs_live_crawl",
)

MUTATION_FLAG_KEYS = frozenset(
    {
        "active_devhub_surface_mutation",
        "active_prompt_mutation",
        "active_guardrail_mutation",
        "active_process_model_mutation",
        "active_release_state_mutation",
        "active_crawler_mutation",
        "active_daemon_state_mutation",
        "mutates_devhub_surface",
        "mutates_prompt",
        "mutates_guardrail",
        "mutates_process_model",
        "mutates_release_state",
        "mutates_crawler",
        "mutates_daemon_state",
    }
)

FORBIDDEN_TEXT_RE = re.compile(
    r"\b(password|credential|cookie|token|session[-_ ]?state|storage[-_ ]?state|auth[-_ ]?state|"
    r"auth[-_ ]?file|browser[-_ ]?artifact|screenshot|trace\.zip|\bhar\b|\.har\b|private value|"
    r"private page value|raw authenticated|raw crawl|downloaded document|form fill|filled form|upload(ed)?|"
    r"submit|submission|certify|certification|pay fee|payment|schedule inspection|cancel|cancellation|"
    r"account change|live crawl|opened devhub|logged into devhub|active surface update|prompt update|"
    r"guardrail update|process model update|release update|daemon state update)\b",
    re.IGNORECASE,
)

OFFLINE_COMMAND_FORBIDDEN_RE = re.compile(
    r"\b(curl|wget|playwright|browser|login|signin|sign-in|auth|crawl|http://|https://)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class IntakePacketFinding:
    code: str
    path: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "path": self.path, "message": self.message}


@dataclass(frozen=True)
class IntakePacketResult:
    findings: tuple[IntakePacketFinding, ...]

    @property
    def ok(self) -> bool:
        return not self.findings

    def messages(self) -> list[str]:
        return [f"{finding.path}: {finding.message}" for finding in self.findings]

    def require_ok(self) -> None:
        if self.findings:
            raise ValueError("invalid attended DevHub read-only observation evidence intake packet v1: " + "; ".join(self.messages()))


def validate_attended_readonly_observation_evidence_intake_packet_v1(packet: Mapping[str, Any]) -> IntakePacketResult:
    """Return deterministic validation findings for an intake packet."""

    findings: list[IntakePacketFinding] = []
    if not isinstance(packet, Mapping):
        return IntakePacketResult((IntakePacketFinding("invalid_packet", "$", "packet must be an object"),))

    if packet.get("packet_version") != PACKET_VERSION:
        findings.append(IntakePacketFinding("invalid_packet_version", "$.packet_version", f"must be {PACKET_VERSION}"))
    if packet.get("fixture_first") is not True:
        findings.append(IntakePacketFinding("not_fixture_first", "$.fixture_first", "must be true"))
    if packet.get("read_only_only") is not True:
        findings.append(IntakePacketFinding("not_read_only_only", "$.read_only_only", "must be true"))
    if packet.get("metadata_only") is not True:
        findings.append(IntakePacketFinding("not_metadata_only", "$.metadata_only", "must be true"))

    _validate_artifact_policy(packet.get("artifact_policy"), findings)
    _validate_mutation_flags(packet.get("mutation_flags"), "$.mutation_flags", findings)
    authorization_ids = _validate_authorization_rows(packet.get("renewal_authorization_rows"), findings)
    placeholder_ids = _validate_observation_placeholders(packet.get("redacted_observation_placeholders"), findings)
    _validate_intake_rows(packet.get("intake_rows"), authorization_ids, placeholder_ids, findings)
    _validate_packet_commands(packet.get("validation_commands"), "$.validation_commands", findings)
    _scan_forbidden_text(packet, "$", findings)
    return IntakePacketResult(tuple(_dedupe(findings)))


def assert_attended_readonly_observation_evidence_intake_packet_v1(packet: Mapping[str, Any]) -> None:
    validate_attended_readonly_observation_evidence_intake_packet_v1(packet).require_ok()


def accepted_intake_rows(packet: Mapping[str, Any]) -> list[dict[str, Any]]:
    assert_attended_readonly_observation_evidence_intake_packet_v1(packet)
    rows = packet.get("intake_rows")
    if not _is_sequence(rows):
        return []
    return [dict(row) for row in rows if isinstance(row, Mapping)]


def _validate_artifact_policy(value: Any, findings: list[IntakePacketFinding]) -> None:
    if not isinstance(value, Mapping):
        findings.append(IntakePacketFinding("missing_artifact_policy", "$.artifact_policy", "must be an object"))
        return
    for flag in REQUIRED_FALSE_ARTIFACT_FLAGS:
        if value.get(flag) is not False:
            findings.append(IntakePacketFinding("unsafe_artifact_policy", f"$.artifact_policy.{flag}", "must be false"))


def _validate_authorization_rows(value: Any, findings: list[IntakePacketFinding]) -> set[str]:
    ids: set[str] = set()
    if not _is_sequence(value):
        findings.append(IntakePacketFinding("missing_authorization_rows", "$.renewal_authorization_rows", "must be a non-empty list"))
        return ids
    for index, row in enumerate(value):
        path = f"$.renewal_authorization_rows[{index}]"
        if not isinstance(row, Mapping):
            findings.append(IntakePacketFinding("invalid_authorization_row", path, "row must be an object"))
            continue
        row_id = _required_text(row, "authorization_row_id", path, findings)
        if row_id in ids:
            findings.append(IntakePacketFinding("duplicate_authorization_row_id", f"{path}.authorization_row_id", "must be unique"))
        ids.add(row_id)
        if _text(row.get("origin")) not in ALLOWED_AUTHORIZATION_ORIGINS:
            findings.append(IntakePacketFinding("unsafe_authorization_origin", f"{path}.origin", "must be synthetic renewal authorization"))
        if _text(row.get("classification")) not in ALLOWED_CLASSIFICATIONS:
            findings.append(IntakePacketFinding("unsafe_authorization_classification", f"{path}.classification", "must be safe read-only"))
        _required_text(row, "authorized_surface_id", path, findings)
        _require_sequence(row.get("authorized_evidence_categories"), f"{path}.authorized_evidence_categories", findings)
    return {row_id for row_id in ids if row_id}


def _validate_observation_placeholders(value: Any, findings: list[IntakePacketFinding]) -> set[str]:
    ids: set[str] = set()
    if not _is_sequence(value):
        findings.append(IntakePacketFinding("missing_observation_placeholders", "$.redacted_observation_placeholders", "must be a non-empty list"))
        return ids
    for index, row in enumerate(value):
        path = f"$.redacted_observation_placeholders[{index}]"
        if not isinstance(row, Mapping):
            findings.append(IntakePacketFinding("invalid_observation_placeholder", path, "placeholder must be an object"))
            continue
        placeholder_id = _required_text(row, "placeholder_id", path, findings)
        if placeholder_id in ids:
            findings.append(IntakePacketFinding("duplicate_placeholder_id", f"{path}.placeholder_id", "must be unique"))
        ids.add(placeholder_id)
        if _text(row.get("origin")) not in ALLOWED_PLACEHOLDER_ORIGINS:
            findings.append(IntakePacketFinding("unsafe_placeholder_origin", f"{path}.origin", "must be redacted observation placeholder"))
        if row.get("private_values_redacted") is not True:
            findings.append(IntakePacketFinding("placeholder_not_redacted", f"{path}.private_values_redacted", "must be true"))
        _required_text(row, "surface_id", path, findings)
        _require_sequence(row.get("placeholder_fields"), f"{path}.placeholder_fields", findings)
    return {placeholder_id for placeholder_id in ids if placeholder_id}


def _validate_intake_rows(value: Any, authorization_ids: set[str], placeholder_ids: set[str], findings: list[IntakePacketFinding]) -> None:
    if not _is_sequence(value):
        findings.append(IntakePacketFinding("missing_intake_rows", "$.intake_rows", "must be a non-empty list"))
        return
    seen: set[str] = set()
    required_sequences = (
        "observed_page_headings",
        "observed_url_patterns",
        "accessible_landmarks",
        "read_only_action_labels",
        "validation_messages",
        "attachment_list_metadata_placeholders",
        "fee_notice_status_placeholders",
        "stop_condition_hits",
        "manual_handoff_notes",
        "offline_validation_commands",
    )
    for index, row in enumerate(value):
        path = f"$.intake_rows[{index}]"
        if not isinstance(row, Mapping):
            findings.append(IntakePacketFinding("invalid_intake_row", path, "row must be an object"))
            continue
        row_id = _required_text(row, "intake_row_id", path, findings)
        if row_id in seen:
            findings.append(IntakePacketFinding("duplicate_intake_row_id", f"{path}.intake_row_id", "must be unique"))
        seen.add(row_id)
        if _text(row.get("classification")) not in ALLOWED_CLASSIFICATIONS:
            findings.append(IntakePacketFinding("unsafe_intake_classification", f"{path}.classification", "must be safe read-only"))
        _require_known_ref(row.get("authorization_row_id"), authorization_ids, f"{path}.authorization_row_id", findings)
        _require_known_ref(row.get("placeholder_id"), placeholder_ids, f"{path}.placeholder_id", findings)
        for key in required_sequences:
            _require_sequence(row.get(key), f"{path}.{key}", findings)
        _validate_packet_commands(row.get("offline_validation_commands"), f"{path}.offline_validation_commands", findings)


def _validate_packet_commands(value: Any, path: str, findings: list[IntakePacketFinding]) -> None:
    if not _is_sequence(value):
        findings.append(IntakePacketFinding("missing_offline_validation_commands", path, "must be a non-empty list of argv lists"))
        return
    for index, command in enumerate(value):
        command_path = f"{path}[{index}]"
        if not _is_sequence(command) or not all(isinstance(part, str) and part.strip() for part in command):
            findings.append(IntakePacketFinding("invalid_offline_validation_command", command_path, "must be a non-empty argv list"))
            continue
        command_text = " ".join(command)
        if OFFLINE_COMMAND_FORBIDDEN_RE.search(command_text):
            findings.append(IntakePacketFinding("online_or_browser_validation_command", command_path, "command must be offline and must not invoke browser, login, auth, crawl, or network tooling"))


def _validate_mutation_flags(value: Any, path: str, findings: list[IntakePacketFinding]) -> None:
    if not isinstance(value, Mapping):
        findings.append(IntakePacketFinding("missing_mutation_flags", path, "must be an object"))
        return
    for key, child in value.items():
        child_path = f"{path}.{key}"
        if key in MUTATION_FLAG_KEYS and _active(child):
            findings.append(IntakePacketFinding("active_mutation_flag", child_path, "must be false or absent"))
        if isinstance(child, Mapping):
            _validate_mutation_flags(child, child_path, findings)


def _scan_forbidden_text(value: Any, path: str, findings: list[IntakePacketFinding]) -> None:
    if isinstance(value, str):
        if _path_allows_blocked_language(path):
            return
        if FORBIDDEN_TEXT_RE.search(value):
            findings.append(IntakePacketFinding("forbidden_text", path, "contains live, private, artifact, mutation, or consequential-action language"))
        return
    if isinstance(value, Mapping):
        for key, child in value.items():
            _scan_forbidden_text(child, f"{path}.{key}", findings)
        return
    if _is_sequence(value):
        for index, child in enumerate(value):
            _scan_forbidden_text(child, f"{path}[{index}]", findings)


def _path_allows_blocked_language(path: str) -> bool:
    return any(part in path for part in (".stop_condition_hits", ".manual_handoff_notes", ".blocked_scope_notes"))


def _required_text(row: Mapping[str, Any], key: str, path: str, findings: list[IntakePacketFinding]) -> str:
    value = _text(row.get(key))
    if not value:
        findings.append(IntakePacketFinding("missing_text", f"{path}.{key}", "must be non-empty text"))
    return value


def _require_known_ref(value: Any, known_ids: set[str], path: str, findings: list[IntakePacketFinding]) -> None:
    ref = _text(value)
    if not ref:
        findings.append(IntakePacketFinding("missing_reference", path, "must reference a declared row"))
    elif ref not in known_ids:
        findings.append(IntakePacketFinding("unknown_reference", path, "must reference a declared row"))


def _require_sequence(value: Any, path: str, findings: list[IntakePacketFinding]) -> None:
    if not _is_sequence(value):
        findings.append(IntakePacketFinding("missing_sequence", path, "must be a non-empty list"))


def _is_sequence(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)) and len(value) > 0


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _active(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"1", "active", "enabled", "true", "yes"}
    return False


def _dedupe(findings: list[IntakePacketFinding]) -> list[IntakePacketFinding]:
    seen: set[tuple[str, str, str]] = set()
    result: list[IntakePacketFinding] = []
    for finding in findings:
        key = (finding.code, finding.path, finding.message)
        if key not in seen:
            seen.add(key)
            result.append(finding)
    return result
