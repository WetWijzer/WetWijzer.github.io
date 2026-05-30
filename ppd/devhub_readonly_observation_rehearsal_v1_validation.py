"""Validation for DevHub read-only observation rehearsal v1 packets.

These packets are offline review artifacts. They may describe redacted, cited UI
observations, but they must not contain private account values, browser/session
artifacts, write-capable actions, consequential action language, or active state
mutation flags.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import re
from typing import Any


PUBLIC_CITATION_RE = re.compile(r"^https://", re.IGNORECASE)

REQUIRED_REDACTION_REQUIREMENTS = frozenset(
    {
        "no_private_account_values",
        "no_session_files",
        "no_screenshots",
        "no_traces",
        "no_har_artifacts",
        "redact_visible_identifiers",
    }
)

REQUIRED_ATTENDANCE_CHECKPOINTS = frozenset(
    {
        "operator_present_before_observation",
        "read_only_scope_review",
        "manual_handoff_on_consequential_control",
        "user_visible_completion_review",
    }
)

SESSION_KEY_PARTS = (
    "session_file",
    "session_path",
    "storage_state",
    "auth_state",
    "cookie",
    "cookies",
    "local_storage",
    "session_storage",
    "playwright_auth",
)

SCREENSHOT_KEY_PARTS = ("screenshot", "screen_capture", "image_capture")
TRACE_KEY_PARTS = ("trace", "trace_path", "playwright_trace")
HAR_KEY_PARTS = ("har", "network_har", "har_path")

PRIVATE_VALUE_KEY_PARTS = (
    "private_account_value",
    "account_value",
    "raw_account_value",
    "authenticated_value",
    "raw_authenticated_value",
    "visible_private_value",
    "field_value",
    "permit_number",
    "ivr_number",
    "license_number",
    "email",
    "phone",
)

PRIVATE_VALUE_PATTERNS = (
    re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE),
    re.compile(r"\b(?:\+?1[-. ]?)?\(?\d{3}\)?[-. ]\d{3}[-. ]\d{4}\b"),
    re.compile(r"\b(?:permit|account|ivr|license)\s*(?:number|#|id)?\s*[:=]\s*[A-Za-z0-9-]{4,}\b", re.IGNORECASE),
)

ARTIFACT_PATH_PATTERNS = (
    re.compile(r"\b\S+\.har\b", re.IGNORECASE),
    re.compile(r"\btrace\.zip\b", re.IGNORECASE),
    re.compile(r"\b\S+\.(?:png|jpe?g|webp)\b", re.IGNORECASE),
    re.compile(r"\b(?:storage_state|auth_state|cookies)\.json\b", re.IGNORECASE),
    re.compile(r"file://", re.IGNORECASE),
    re.compile(r"/(?:home|Users|private|tmp|var/folders)/[^\s]+"),
    re.compile(r"[A-Za-z]:\\\\(?:Users|Temp|Windows|ProgramData)\\\\[^\s]+"),
)

WRITE_ACTION_CLASSES = frozenset(
    {
        "write",
        "write_capable",
        "write-capable",
        "mutation",
        "mutating",
        "form_fill",
        "fill",
        "click",
        "official_action",
        "consequential",
    }
)

WRITE_ACTION_PATTERNS = (
    re.compile(r"\b(?:click|press|fill|type|select|change|save|continue)\b.{0,40}\b(?:button|field|form|devhub|page)\b", re.IGNORECASE),
    re.compile(r"\bwrite[-_ ]?capable\b", re.IGNORECASE),
)

OFFICIAL_ACTION_LANGUAGE_RE = re.compile(
    r"\b(?:certif(?:y|ies|ication)|acknowledg(?:e|ement)|submit|submission|submitted|payment|pay|paid|purchase|upload|attach|schedule|scheduling|cancel|cancellation|withdraw|reactivate|inspection)\b",
    re.IGNORECASE,
)

MUTATION_KEY_RE = re.compile(
    r"(?:active_)?(?:devhub|surface[_-]?registry|guardrail|prompt|release[_-]?state|agent[_-]?state).*?(?:mutation|mutate|write|apply|enable|enabled|active)|(?:mutation|mutate|write|apply|enable|enabled|active).*?(?:devhub|surface[_-]?registry|guardrail|prompt|release[_-]?state|agent[_-]?state)",
    re.IGNORECASE,
)

MUTATION_TEXT_RE = re.compile(
    r"\b(?:active|enable|apply|write|mutate|mutation)\b.{0,48}\b(?:DevHub|surface[-_ ]registry|guardrail|prompt|release[-_ ]state|agent[-_ ]state)\b|\b(?:DevHub|surface[-_ ]registry|guardrail|prompt|release[-_ ]state|agent[-_ ]state)\b.{0,48}\b(?:active|enable|apply|write|mutate|mutation)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ObservationRehearsalViolation:
    """A deterministic packet validation finding."""

    code: str
    path: str
    message: str


class ObservationRehearsalValidationError(ValueError):
    """Raised when a read-only observation rehearsal packet is unsafe."""

    def __init__(self, violations: Sequence[ObservationRehearsalViolation]) -> None:
        self.violations = tuple(violations)
        rendered = "; ".join(f"{item.code} at {item.path}: {item.message}" for item in self.violations)
        super().__init__(rendered)


def validate_devhub_readonly_observation_rehearsal_v1(packet: Mapping[str, Any]) -> list[ObservationRehearsalViolation]:
    """Return all validation violations for a rehearsal packet."""

    violations: list[ObservationRehearsalViolation] = []
    if not isinstance(packet, Mapping):
        return [ObservationRehearsalViolation("invalid_packet", "$", "packet must be a mapping")]

    _validate_ui_observations(packet, violations)
    _validate_redaction_requirements(packet, violations)
    _validate_attendance_checkpoints(packet, violations)
    _scan_value(packet, "$", violations)
    return violations


def assert_valid_devhub_readonly_observation_rehearsal_v1(packet: Mapping[str, Any]) -> None:
    """Raise when a packet is not safe read-only rehearsal evidence."""

    violations = validate_devhub_readonly_observation_rehearsal_v1(packet)
    if violations:
        raise ObservationRehearsalValidationError(violations)


def packet_is_valid_devhub_readonly_observation_rehearsal_v1(packet: Mapping[str, Any]) -> bool:
    """Return True only for packets accepted by the v1 validator."""

    return not validate_devhub_readonly_observation_rehearsal_v1(packet)


def _validate_ui_observations(packet: Mapping[str, Any], violations: list[ObservationRehearsalViolation]) -> None:
    observations = packet.get("ui_observations", packet.get("observations"))
    if not _is_sequence(observations):
        violations.append(
            ObservationRehearsalViolation(
                "uncited_ui_evidence",
                "$.ui_observations",
                "read-only rehearsals require cited UI observation evidence",
            )
        )
        return

    for index, observation in enumerate(observations):
        path = f"$.ui_observations[{index}]"
        if not isinstance(observation, Mapping):
            violations.append(ObservationRehearsalViolation("uncited_ui_evidence", path, "UI observation must be a mapping"))
            continue
        summary = observation.get("evidence_summary", observation.get("ui_evidence", observation.get("observation")))
        if not isinstance(summary, str) or not summary.strip():
            violations.append(ObservationRehearsalViolation("uncited_ui_evidence", path, "UI observation requires a non-empty evidence summary"))
        if not _has_public_citation(observation.get("citations", observation.get("source_citations", observation.get("evidence_citations")))):
            violations.append(ObservationRehearsalViolation("uncited_ui_evidence", path, "UI observation lacks a public HTTPS citation"))


def _validate_redaction_requirements(packet: Mapping[str, Any], violations: list[ObservationRehearsalViolation]) -> None:
    requirements = packet.get("redaction_requirements", packet.get("redaction_checklist"))
    if not _is_sequence(requirements):
        violations.append(
            ObservationRehearsalViolation(
                "missing_redaction_requirement",
                "$.redaction_requirements",
                "packet requires redaction requirements for private values and browser artifacts",
            )
        )
        return

    seen: set[str] = set()
    for index, requirement in enumerate(requirements):
        path = f"$.redaction_requirements[{index}]"
        if not isinstance(requirement, Mapping):
            violations.append(ObservationRehearsalViolation("missing_redaction_requirement", path, "redaction requirement must be a mapping"))
            continue
        requirement_id = str(requirement.get("requirement_id", requirement.get("check_id", ""))).strip()
        if requirement_id:
            seen.add(requirement_id)
        if requirement.get("required") is not True or requirement.get("enforced") is not True:
            violations.append(ObservationRehearsalViolation("missing_redaction_requirement", path, "redaction requirement must be required and enforced"))
        if requirement.get("allows_private_values") is not False or requirement.get("allows_artifacts") is not False:
            violations.append(ObservationRehearsalViolation("missing_redaction_requirement", path, "redaction requirement must disallow private values and artifacts"))
        if not _has_public_citation(requirement.get("citations", requirement.get("source_citations"))):
            violations.append(ObservationRehearsalViolation("missing_redaction_requirement", path, "redaction requirement must cite source evidence"))

    missing = REQUIRED_REDACTION_REQUIREMENTS - seen
    if missing:
        violations.append(
            ObservationRehearsalViolation(
                "missing_redaction_requirement",
                "$.redaction_requirements",
                "missing required redaction requirements: " + ", ".join(sorted(missing)),
            )
        )


def _validate_attendance_checkpoints(packet: Mapping[str, Any], violations: list[ObservationRehearsalViolation]) -> None:
    checkpoints = packet.get("attendance_checkpoints")
    if not _is_sequence(checkpoints):
        violations.append(
            ObservationRehearsalViolation(
                "missing_attendance_checkpoint",
                "$.attendance_checkpoints",
                "packet requires cited attendance checkpoints",
            )
        )
        return

    seen: set[str] = set()
    for index, checkpoint in enumerate(checkpoints):
        path = f"$.attendance_checkpoints[{index}]"
        if not isinstance(checkpoint, Mapping):
            violations.append(ObservationRehearsalViolation("missing_attendance_checkpoint", path, "attendance checkpoint must be a mapping"))
            continue
        checkpoint_id = str(checkpoint.get("checkpoint_id", "")).strip()
        if checkpoint_id:
            seen.add(checkpoint_id)
        if checkpoint.get("requires_user_attendance") is not True:
            violations.append(ObservationRehearsalViolation("missing_attendance_checkpoint", path, "attendance checkpoint must require user attendance"))
        if checkpoint.get("write_action_allowed") is not False:
            violations.append(ObservationRehearsalViolation("missing_attendance_checkpoint", path, "attendance checkpoint must disallow write-capable action"))
        if not _has_public_citation(checkpoint.get("citations", checkpoint.get("source_citations"))):
            violations.append(ObservationRehearsalViolation("missing_attendance_checkpoint", path, "attendance checkpoint must cite source evidence"))

    missing = REQUIRED_ATTENDANCE_CHECKPOINTS - seen
    if missing:
        violations.append(
            ObservationRehearsalViolation(
                "missing_attendance_checkpoint",
                "$.attendance_checkpoints",
                "missing required attendance checkpoints: " + ", ".join(sorted(missing)),
            )
        )


def _scan_value(value: Any, path: str, violations: list[ObservationRehearsalViolation], key_hint: str = "") -> None:
    if isinstance(value, Mapping):
        for raw_key, child in value.items():
            key = str(raw_key)
            child_path = f"{path}.{key}"
            normalized = _normalized_key(key)
            _scan_key_value(normalized, child, child_path, violations)
            _scan_value(child, child_path, violations, normalized)
        return

    if _is_sequence(value):
        for index, child in enumerate(value):
            _scan_value(child, f"{path}[{index}]", violations, key_hint)
        return

    if isinstance(value, str):
        _scan_string(value, path, violations, key_hint)


def _scan_key_value(key: str, value: Any, path: str, violations: list[ObservationRehearsalViolation]) -> None:
    if any(part in key for part in SESSION_KEY_PARTS) and _is_present(value):
        violations.append(ObservationRehearsalViolation("session_file_artifact", path, "session files and auth state are not allowed"))
    if any(part in key for part in SCREENSHOT_KEY_PARTS) and _is_present(value):
        violations.append(ObservationRehearsalViolation("screenshot_artifact", path, "screenshots are not allowed in committed rehearsal packets"))
    if any(part in key for part in TRACE_KEY_PARTS) and _is_present(value):
        violations.append(ObservationRehearsalViolation("trace_artifact", path, "browser traces are not allowed in committed rehearsal packets"))
    if any(part in key for part in HAR_KEY_PARTS) and _is_present(value):
        violations.append(ObservationRehearsalViolation("har_artifact", path, "HAR artifacts are not allowed in committed rehearsal packets"))
    if any(part in key for part in PRIVATE_VALUE_KEY_PARTS) and _is_present(value) and not _is_redacted_marker(value):
        violations.append(ObservationRehearsalViolation("private_account_value", path, "private account values must be absent or redacted"))
    if key in {"action_class", "action_type", "control_class"} and str(value).strip().lower() in WRITE_ACTION_CLASSES:
        violations.append(ObservationRehearsalViolation("write_capable_action", path, "write-capable actions are not allowed"))
    if key in {"write_action_allowed", "write_capable", "can_write", "can_click", "can_fill", "official_action_allowed"} and value is not False:
        violations.append(ObservationRehearsalViolation("write_capable_action", path, "write-capable action flags must be absent or false"))
    if MUTATION_KEY_RE.search(key) and value is not False and value is not None:
        violations.append(ObservationRehearsalViolation("active_mutation_flag", path, "active DevHub, surface-registry, guardrail, prompt, release-state, or agent-state mutation flags are not allowed"))


def _scan_string(value: str, path: str, violations: list[ObservationRehearsalViolation], key_hint: str) -> None:
    stripped = value.strip()
    if not stripped:
        return

    if not _is_redacted_marker(stripped):
        for pattern in PRIVATE_VALUE_PATTERNS:
            if pattern.search(stripped):
                violations.append(ObservationRehearsalViolation("private_account_value", path, "string appears to contain a private account value"))
                break

    for pattern in ARTIFACT_PATH_PATTERNS:
        if pattern.search(stripped):
            lowered = stripped.lower()
            if ".har" in lowered:
                code = "har_artifact"
            elif "trace" in lowered:
                code = "trace_artifact"
            elif any(ext in lowered for ext in (".png", ".jpg", ".jpeg", ".webp")):
                code = "screenshot_artifact"
            else:
                code = "session_file_artifact"
            violations.append(ObservationRehearsalViolation(code, path, "string references a prohibited browser/session artifact"))
            break

    if key_hint in {"action", "action_name", "action_summary", "control", "selector", "step"}:
        if any(pattern.search(stripped) for pattern in WRITE_ACTION_PATTERNS):
            violations.append(ObservationRehearsalViolation("write_capable_action", path, "string describes a write-capable action"))

    if OFFICIAL_ACTION_LANGUAGE_RE.search(stripped):
        violations.append(
            ObservationRehearsalViolation(
                "prohibited_official_action_language",
                path,
                "certification, submission, payment, upload, scheduling, cancellation, or related official-action language is not allowed",
            )
        )

    if MUTATION_TEXT_RE.search(stripped):
        violations.append(ObservationRehearsalViolation("active_mutation_flag", path, "string references active DevHub or state mutation"))


def _has_public_citation(citations: Any) -> bool:
    if isinstance(citations, str):
        return bool(PUBLIC_CITATION_RE.match(citations.strip()))
    if isinstance(citations, Mapping):
        url = citations.get("url", citations.get("href", citations.get("source_url")))
        if isinstance(url, str) and PUBLIC_CITATION_RE.match(url.strip()):
            return True
        source_id = citations.get("source_id")
        return isinstance(source_id, str) and source_id.startswith("ppd-")
    if _is_sequence(citations):
        return any(_has_public_citation(citation) for citation in citations)
    return False


def _is_sequence(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray))


def _normalized_key(key: str) -> str:
    return key.replace("-", "_").replace(" ", "_").lower()


def _is_present(value: Any) -> bool:
    if value is None or value is False:
        return False
    if isinstance(value, str) and not value.strip():
        return False
    if _is_sequence(value) and not value:
        return False
    if isinstance(value, Mapping) and not value:
        return False
    return True


def _is_redacted_marker(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    normalized = value.strip().lower()
    return normalized in {"[redacted]", "redacted", "", "***redacted***"}
