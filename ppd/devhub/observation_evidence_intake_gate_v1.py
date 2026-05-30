"""Fixture-first DevHub read-only observation evidence intake gate v1.

The gate accepts only synthetic or redacted metadata rows for safe read-only
DevHub observations. It rejects credentials, session state, browser artifacts,
screenshots, traces, HAR files, auth files, private page values, raw crawl/PDF
or downloaded data, live execution claims, observation-promotion claims,
outcome guarantees, consequential-action language, and active mutation flags.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Mapping, Sequence

PACKET_VERSION = "devhub_read_only_observation_evidence_intake_gate_v1"
SAFE_CLASSIFICATIONS = frozenset({"safe_read_only", "safe-read-only", "read_only_observation"})
ALLOWED_METADATA_ORIGINS = frozenset({"synthetic_fixture", "redacted_observation_metadata"})
REVIEWER_PLACEHOLDERS = frozenset({"pending_review", "needs_reviewer_disposition", "not_reviewed"})

REQUIRED_PACKET_FALSE_FLAGS = (
    "stores_credentials",
    "stores_session_state",
    "stores_browser_artifacts",
    "stores_auth_files",
    "stores_screenshots",
    "stores_traces",
    "stores_har",
    "stores_private_page_values",
    "stores_raw_crawl_data",
    "stores_raw_pdf_data",
    "stores_downloaded_data",
    "stores_payment_details",
    "stores_uploaded_documents",
    "stores_official_action_artifacts",
)

REQUIRED_REDACTION_ATTESTATIONS = (
    "credentials_absent",
    "session_state_absent",
    "browser_artifacts_absent",
    "auth_files_absent",
    "screenshots_absent",
    "traces_absent",
    "har_absent",
    "private_page_values_absent",
    "raw_crawl_data_absent",
    "raw_pdf_data_absent",
    "downloaded_data_absent",
    "payment_details_absent",
    "uploaded_documents_absent",
    "official_action_artifacts_absent",
    "only_synthetic_or_redacted_metadata",
)

FORBIDDEN_KEY_MARKERS = (
    "auth_file",
    "auth_state",
    "browser_artifact",
    "browser_context",
    "card_number",
    "cookie",
    "credential",
    "cvv",
    "downloaded_data",
    "downloaded_document",
    "har",
    "local_storage",
    "password",
    "payment_detail",
    "private_page_value",
    "raw_authenticated",
    "raw_crawl",
    "raw_dom",
    "raw_field_value",
    "raw_pdf",
    "screenshot",
    "session_state",
    "storage_state",
    "trace",
    "upload_payload",
    "uploaded_document",
)

MUTATION_FLAG_MARKERS = (
    "active_agent_state_mutation",
    "active_fixture_mutation",
    "active_guardrail_mutation",
    "active_prompt_mutation",
    "active_release_state_mutation",
    "active_source_mutation",
    "active_surface_mutation",
    "agent_state_mutation",
    "apply_fixture_update",
    "apply_guardrail_update",
    "apply_prompt_update",
    "apply_release_update",
    "apply_source_update",
    "apply_surface_update",
    "mutates_agent_state",
    "mutates_fixture",
    "mutates_guardrail",
    "mutates_prompt",
    "mutates_release_state",
    "mutates_source",
    "mutates_surface",
)

FORBIDDEN_TEXT_RE = re.compile(
    r"\b(password|credential|cookie|bearer\s+[A-Za-z0-9._-]+|token=|session[-_ ]?state|storage[-_ ]?state|"
    r"auth[-_ ]?file|browser[-_ ]?artifact|screenshot|trace\.zip|\bhar\b|\.har\b|raw authenticated|"
    r"raw private|raw crawl|raw pdf|downloaded data|downloaded document|private page value|card number|cvv|"
    r"payment details?|uploaded document|official action artifact)\b",
    re.IGNORECASE,
)

LIVE_OR_PROMOTION_CLAIM_RE = re.compile(
    r"\b(live authenticated|live execution|executed in devhub|observed in production|real devhub session|"
    r"authenticated capture|observation promoted|promotion complete|promoted observation|accepted into registry)\b",
    re.IGNORECASE,
)

OUTCOME_GUARANTEE_RE = re.compile(
    r"\b(guarantee[sd]?|will be approved|permit approved|approval assured|legal conclusion|legally sufficient|"
    r"permit will issue|inspection will pass|fee is final|deadline guaranteed)\b",
    re.IGNORECASE,
)

CONSEQUENTIAL_ACTION_RE = re.compile(
    r"\b(upload|submit|submission|certify|certification|pay|payment|schedule|scheduling|cancel|cancellation|"
    r"withdraw|purchase|create account|password recovery|mfa|captcha)\b",
    re.IGNORECASE,
)

BLOCKING_LANGUAGE_RE = re.compile(r"\b(stop before|block|blocked|refuse|do not|must not|manual handoff|required confirmation)\b", re.IGNORECASE)

MUTATION_TEXT_RE = re.compile(
    r"\b(mutate|write|patch|update|apply|promote|activate)\b.*\b(source|surface|guardrail|prompt|release state|fixture|agent state)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class IntakeGateFinding:
    code: str
    path: str
    message: str


@dataclass(frozen=True)
class IntakeGateResult:
    findings: tuple[IntakeGateFinding, ...]

    @property
    def ok(self) -> bool:
        return not self.findings

    def messages(self) -> list[str]:
        return [f"{finding.path}: {finding.message}" for finding in self.findings]

    def require_ok(self) -> None:
        if self.findings:
            raise ValueError("DevHub observation evidence intake gate rejected packet: " + "; ".join(self.messages()))


def validate_observation_evidence_intake_gate_v1(packet: Mapping[str, Any]) -> IntakeGateResult:
    """Validate a fixture-first read-only DevHub observation evidence packet."""

    findings: list[IntakeGateFinding] = []
    if not isinstance(packet, Mapping):
        return IntakeGateResult((IntakeGateFinding("invalid_packet", "$", "packet must be an object"),))

    if packet.get("packet_version") != PACKET_VERSION:
        findings.append(IntakeGateFinding("invalid_packet_version", "$.packet_version", f"must be {PACKET_VERSION}"))

    if packet.get("fixture_first") is not True:
        findings.append(IntakeGateFinding("not_fixture_first", "$.fixture_first", "must be true"))
    if packet.get("read_only_only") is not True:
        findings.append(IntakeGateFinding("not_read_only_only", "$.read_only_only", "must be true"))
    if packet.get("metadata_only") is not True:
        findings.append(IntakeGateFinding("not_metadata_only", "$.metadata_only", "must be true"))

    _validate_artifact_policy(packet.get("artifact_policy"), findings)
    _validate_rows(packet.get("observation_rows"), findings)
    _walk_for_forbidden_payload(packet, "$", findings)
    return IntakeGateResult(tuple(findings))


def assert_observation_evidence_intake_gate_v1(packet: Mapping[str, Any]) -> None:
    validate_observation_evidence_intake_gate_v1(packet).require_ok()


def accepted_observation_rows(packet: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Return accepted rows after validation for downstream fixture consumers."""

    assert_observation_evidence_intake_gate_v1(packet)
    rows = packet.get("observation_rows")
    if not isinstance(rows, Sequence) or isinstance(rows, (str, bytes, bytearray)):
        return []
    return [dict(row) for row in rows if isinstance(row, Mapping)]


def _validate_artifact_policy(value: Any, findings: list[IntakeGateFinding]) -> None:
    if not isinstance(value, Mapping):
        findings.append(IntakeGateFinding("missing_artifact_policy", "$.artifact_policy", "must be an object"))
        return
    for flag in REQUIRED_PACKET_FALSE_FLAGS:
        if value.get(flag) is not False:
            findings.append(IntakeGateFinding("unsafe_artifact_policy", f"$.artifact_policy.{flag}", "must be false"))


def _validate_rows(value: Any, findings: list[IntakeGateFinding]) -> None:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)) or not value:
        findings.append(IntakeGateFinding("missing_rows", "$.observation_rows", "must be a non-empty list"))
        return

    seen: set[str] = set()
    for index, row in enumerate(value):
        path = f"$.observation_rows[{index}]"
        if not isinstance(row, Mapping):
            findings.append(IntakeGateFinding("invalid_row", path, "row must be an object"))
            continue
        row_id = _required_text(row, "row_id", path, findings)
        if row_id:
            if row_id in seen:
                findings.append(IntakeGateFinding("duplicate_row_id", f"{path}.row_id", "must be unique"))
            seen.add(row_id)
        _required_text(row, "surface_id", path, findings)
        if _text(row.get("classification")) not in SAFE_CLASSIFICATIONS:
            findings.append(IntakeGateFinding("unsafe_classification", f"{path}.classification", "must be safe read-only"))
        if _text(row.get("metadata_origin")) not in ALLOWED_METADATA_ORIGINS:
            findings.append(IntakeGateFinding("unsafe_metadata_origin", f"{path}.metadata_origin", "must be synthetic or redacted metadata"))
        _validate_evidence_refs(row, path, findings)
        _validate_redaction_attestations(row.get("redaction_attestations"), path, findings)
        _validate_blocked_notes(row.get("blocked_action_notes"), path, findings)
        _validate_reviewer_disposition(row.get("reviewer_disposition"), path, findings)
        _validate_offline_commands(row.get("offline_validation_commands"), path, findings)


def _validate_evidence_refs(row: Mapping[str, Any], path: str, findings: list[IntakeGateFinding]) -> None:
    refs = row.get("source_evidence_refs") or row.get("observation_evidence_refs")
    if not isinstance(refs, Sequence) or isinstance(refs, (str, bytes, bytearray)) or not refs:
        findings.append(IntakeGateFinding("missing_evidence_refs", path, "row must include source_evidence_refs or observation_evidence_refs"))
        return
    for index, ref in enumerate(refs):
        if not isinstance(ref, str) or not ref.strip():
            findings.append(IntakeGateFinding("invalid_evidence_ref", f"{path}.evidence_refs[{index}]", "must be text"))


def _validate_redaction_attestations(value: Any, path: str, findings: list[IntakeGateFinding]) -> None:
    if not isinstance(value, Mapping):
        findings.append(IntakeGateFinding("missing_redaction_attestations", f"{path}.redaction_attestations", "must be an object"))
        return
    for attestation in REQUIRED_REDACTION_ATTESTATIONS:
        if value.get(attestation) is not True:
            findings.append(IntakeGateFinding("failed_redaction_attestation", f"{path}.redaction_attestations.{attestation}", "must be true"))


def _validate_blocked_notes(value: Any, path: str, findings: list[IntakeGateFinding]) -> None:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)) or not value:
        findings.append(IntakeGateFinding("missing_blocked_action_notes", f"{path}.blocked_action_notes", "must be non-empty"))
        return
    joined = " ".join(str(item) for item in value)
    if not CONSEQUENTIAL_ACTION_RE.search(joined):
        findings.append(IntakeGateFinding("weak_blocked_action_notes", f"{path}.blocked_action_notes", "must name blocked official or private actions"))
    if not BLOCKING_LANGUAGE_RE.search(joined):
        findings.append(IntakeGateFinding("active_consequential_action_language", f"{path}.blocked_action_notes", "consequential language must be framed as blocked"))


def _validate_reviewer_disposition(value: Any, path: str, findings: list[IntakeGateFinding]) -> None:
    if not isinstance(value, Mapping):
        findings.append(IntakeGateFinding("missing_reviewer_disposition", f"{path}.reviewer_disposition", "must be an object"))
        return
    if _text(value.get("status")) not in REVIEWER_PLACEHOLDERS:
        findings.append(IntakeGateFinding("invalid_reviewer_disposition_status", f"{path}.reviewer_disposition.status", "must remain a placeholder"))
    _required_text(value, "reviewer_role", f"{path}.reviewer_disposition", findings)
    _required_text(value, "notes_placeholder", f"{path}.reviewer_disposition", findings)


def _validate_offline_commands(value: Any, path: str, findings: list[IntakeGateFinding]) -> None:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)) or not value:
        findings.append(IntakeGateFinding("missing_offline_validation_commands", f"{path}.offline_validation_commands", "must be non-empty"))
        return
    for index, command in enumerate(value):
        command_path = f"{path}.offline_validation_commands[{index}]"
        if not isinstance(command, Sequence) or isinstance(command, (str, bytes, bytearray)) or not command:
            findings.append(IntakeGateFinding("invalid_offline_command", command_path, "must be an argv array"))
            continue
        parts = [str(part) for part in command]
        if not all(part.strip() for part in parts):
            findings.append(IntakeGateFinding("blank_offline_command_part", command_path, "must not contain blank parts"))
        joined = " ".join(parts).lower()
        if any(term in joined for term in ("playwright", "curl", "wget", "devhub.portlandoregon.gov")):
            findings.append(IntakeGateFinding("online_validation_command", command_path, "must remain offline"))


def _walk_for_forbidden_payload(value: Any, path: str, findings: list[IntakeGateFinding]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            key_lower = key_text.lower()
            child_path = f"{path}.{key_text}"
            if any(marker in key_lower for marker in FORBIDDEN_KEY_MARKERS):
                findings.append(IntakeGateFinding("forbidden_key", child_path, "forbidden DevHub private artifact key"))
            if any(marker in key_lower for marker in MUTATION_FLAG_MARKERS) and child not in (False, None, "", [], {}):
                findings.append(IntakeGateFinding("active_mutation_flag", child_path, "active source, surface, guardrail, prompt, release-state, fixture, or agent-state mutation is forbidden"))
            _walk_for_forbidden_payload(child, child_path, findings)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            _walk_for_forbidden_payload(child, f"{path}[{index}]", findings)
    elif isinstance(value, str):
        _validate_forbidden_text(value, path, findings)


def _validate_forbidden_text(value: str, path: str, findings: list[IntakeGateFinding]) -> None:
    if FORBIDDEN_TEXT_RE.search(value):
        findings.append(IntakeGateFinding("forbidden_text", path, "forbidden DevHub private artifact text"))
    if LIVE_OR_PROMOTION_CLAIM_RE.search(value):
        findings.append(IntakeGateFinding("live_or_promoted_claim", path, "live execution and observation-promotion claims are forbidden"))
    if OUTCOME_GUARANTEE_RE.search(value):
        findings.append(IntakeGateFinding("outcome_guarantee", path, "legal or permitting outcome guarantees are forbidden"))
    if CONSEQUENTIAL_ACTION_RE.search(value) and ".blocked_action_notes" not in path:
        findings.append(IntakeGateFinding("active_consequential_action_language", path, "payment, submission, scheduling, cancellation, certification, upload, and similar language is allowed only in blocked-action notes"))
    if MUTATION_TEXT_RE.search(value):
        findings.append(IntakeGateFinding("active_mutation_flag", path, "active source, surface, guardrail, prompt, release-state, fixture, or agent-state mutation language is forbidden"))


def _required_text(source: Mapping[str, Any], key: str, path: str, findings: list[IntakeGateFinding]) -> str:
    value = _text(source.get(key))
    if not value:
        findings.append(IntakeGateFinding("missing_text", f"{path}.{key}", "must be non-empty text"))
    return value


def _text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()
