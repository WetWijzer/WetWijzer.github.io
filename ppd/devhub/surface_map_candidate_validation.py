"""Validate DevHubSurfaceMap candidates before reversible draft use.

This module is deterministic and fixture-only. It does not open DevHub, launch a
browser, authenticate, upload, submit, certify, schedule, cancel, or pay.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Mapping, Sequence

MINIMUM_REVERSIBLE_SELECTOR_CONFIDENCE = 0.85
REVERSIBLE_CLASSIFICATIONS = frozenset(
    {
        "reversible",
        "reversible_draft",
        "reversible_draft_edit",
        "reversible_draft_fill",
        "draft_edit",
    }
)
CONSEQUENTIAL_CONTROL_TOKENS = frozenset(
    {
        "upload",
        "submit",
        "certify",
        "certification",
        "acknowledgment",
        "schedule",
        "inspection",
        "cancel",
        "payment",
        "pay",
        "fee",
    }
)
CONTROL_COLLECTIONS = (
    "actions",
    "controls",
    "upload_controls",
    "submit_controls",
    "certification_controls",
    "schedule_controls",
    "cancel_controls",
    "payment_controls",
)
V2_ROW_COLLECTIONS = ("candidate_rows", "surface_rows", "rows")
REQUIRED_V2_ROW_FIELDS = (
    ("selector_stability_placeholder", "missing_selector_stability_placeholder"),
    ("accessible_role_evidence_placeholder", "missing_accessible_role_evidence_placeholder"),
    ("redacted_validation_message_placeholder", "missing_redacted_validation_message_placeholder"),
    ("action_boundary_classification", "missing_action_boundary_classification"),
    ("reviewer_disposition", "missing_reviewer_disposition"),
)
SAFE_ACTION_BOUNDARY_CLASSIFICATIONS = frozenset(
    {
        "safe_read_only",
        "read_only",
        "reversible_draft_blocked",
        "manual_handoff_required",
        "consequential_blocked",
    }
)
SAFE_REVIEWER_DISPOSITIONS = frozenset({"pending_review", "needs_review", "approved_read_only", "rejected", "blocked"})

_PRIVATE_OR_SESSION_KEY_RE = re.compile(
    r"(password|passwd|secret|credential|cookie|cookies|csrf|token|bearer|oauth|session|storage[_-]?state|auth[_-]?state|local[_-]?storage|session[_-]?storage|account[_-]?id|username|email|phone|permit[_-]?number|license[_-]?number|invoice)",
    re.IGNORECASE,
)
_ARTIFACT_KEY_RE = re.compile(
    r"(screenshot|screen[_-]?capture|trace|har|raw[_-]?(?:crawl|dom|html|output)|downloaded[_-]?(?:document|artifact)s?|browser[_-]?(?:artifact|state|context))",
    re.IGNORECASE,
)
_MUTATION_KEY_RE = re.compile(
    r"(?:active[_-]?)?(?:devhub[_-]?surface|surface[_-]?registry|guardrail|prompt|contract|source|release[_-]?state).*?(?:mutation|mutate|write|apply|enable|enabled|active)|(?:mutation|mutate|write|apply|enable|enabled|active).*?(?:devhub[_-]?surface|surface[_-]?registry|guardrail|prompt|contract|source|release[_-]?state)",
    re.IGNORECASE,
)
_PRIVATE_VALUE_RE = re.compile(
    r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}|\b(?:\+?1[-. ]?)?\(?\d{3}\)?[-. ]\d{3}[-. ]\d{4}\b|\b(?:permit|invoice|account|license)\s*(?:number|no\.|#)?\s*[:#]\s*[A-Z0-9-]{4,}\b|\b(?:password|secret|token|authorization|set-cookie)\s*[:=]",
    re.IGNORECASE,
)
_ARTIFACT_TEXT_RE = re.compile(
    r"\b(screenshot|screen shot|trace\.zip|playwright trace|browser trace|har file|\.har\b|storage state|auth state|session state|raw crawl|raw dom|downloaded document)\b|(/home/|/users/|c:\\\\users\\\\|file://|storage[_ -]?state\.json|auth[_ -]?state\.json|screenshot\.(?:png|jpe?g|webp))",
    re.IGNORECASE,
)
_AUTH_AUTOMATION_RE = re.compile(
    r"\b(?:automate|automated|auto[- ]?complete|script|bypass|solve|handle|perform)\b.{0,60}\b(?:login|sign[- ]?in|captcha|mfa|multi[- ]?factor|one[- ]?time code|otp|account creation|password recovery)\b|\b(?:login|sign[- ]?in|captcha|mfa|multi[- ]?factor|one[- ]?time code|otp|account creation|password recovery)\b.{0,60}\b(?:automate|automated|auto[- ]?complete|script|bypass|solve|handle|perform)\b",
    re.IGNORECASE,
)
_OFFICIAL_ACTION_RE = re.compile(
    r"\b(?:certif(?:y|ies|ication)|acknowledg(?:e|ement)|submit|submission|submitted|payment|pay|paid|purchase|upload|attach|schedule|scheduling|cancel|cancellation|withdraw|reactivate|inspection)\b",
    re.IGNORECASE,
)
_GUARANTEE_RE = re.compile(
    r"\b(?:guarantee[sd]?|ensure[sd]?|will|shall)\b.{0,80}\b(?:approval|approved|code compliant|compliance|issuance|issued|legal|permit outcome|pass inspection)\b|\b(?:approval|approved|issuance|issued|legal compliance|permit outcome|pass inspection)\b.{0,80}\b(?:guarantee[sd]?|certain|assured|will|shall)\b",
    re.IGNORECASE,
)
_MUTATION_TEXT_RE = re.compile(
    r"\b(?:active|enable|apply|write|mutate|mutation)\b.{0,60}\b(?:DevHub surface|surface registry|guardrail|prompt|contract|source|release state)\b|\b(?:DevHub surface|surface registry|guardrail|prompt|contract|source|release state)\b.{0,60}\b(?:active|enable|apply|write|mutate|mutation)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class SurfaceMapCandidateViolation:
    candidate_id: str
    code: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {
            "candidate_id": self.candidate_id,
            "code": self.code,
            "message": self.message,
        }


@dataclass(frozen=True)
class SurfaceMapCandidateValidationResult:
    candidate_id: str
    reversible_draft_allowed: bool
    violations: tuple[SurfaceMapCandidateViolation, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "reversible_draft_allowed": self.reversible_draft_allowed,
            "violations": [violation.as_dict() for violation in self.violations],
        }


@dataclass(frozen=True)
class SurfaceMapCandidateBatchValidationResult:
    reversible_draft_allowed: bool
    results: tuple[SurfaceMapCandidateValidationResult, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "reversible_draft_allowed": self.reversible_draft_allowed,
            "results": [result.as_dict() for result in self.results],
        }


def validate_surface_map_candidate(
    candidate: Mapping[str, Any],
    *,
    minimum_selector_confidence: float = MINIMUM_REVERSIBLE_SELECTOR_CONFIDENCE,
) -> SurfaceMapCandidateValidationResult:
    """Return fail-closed reversible draft validation for one candidate."""

    candidate_id = _candidate_id(candidate)
    violations: list[SurfaceMapCandidateViolation] = []

    confidence = candidate.get("selector_confidence")
    if not _confidence_at_or_above(confidence, minimum_selector_confidence):
        violations.append(
            _violation(
                candidate_id,
                "low_selector_confidence",
                f"selector_confidence must be numeric and at least {minimum_selector_confidence}",
            )
        )

    if not _has_route_evidence(candidate):
        violations.append(
            _violation(
                candidate_id,
                "missing_route_evidence",
                "route or url_pattern evidence is required before reversible draft actions",
            )
        )

    if not _has_heading_evidence(candidate):
        violations.append(
            _violation(
                candidate_id,
                "missing_heading_evidence",
                "page heading or heading evidence is required before reversible draft actions",
            )
        )

    violations.extend(_required_label_violations(candidate_id, candidate))
    violations.extend(_consequential_reversible_control_violations(candidate_id, candidate))

    return SurfaceMapCandidateValidationResult(
        candidate_id=candidate_id,
        reversible_draft_allowed=not violations,
        violations=tuple(violations),
    )


def validate_surface_map_candidates(
    candidates: Sequence[Mapping[str, Any]],
    *,
    minimum_selector_confidence: float = MINIMUM_REVERSIBLE_SELECTOR_CONFIDENCE,
) -> SurfaceMapCandidateBatchValidationResult:
    results = tuple(
        validate_surface_map_candidate(
            candidate,
            minimum_selector_confidence=minimum_selector_confidence,
        )
        for candidate in candidates
    )
    return SurfaceMapCandidateBatchValidationResult(
        reversible_draft_allowed=all(result.reversible_draft_allowed for result in results),
        results=results,
    )


def validate_readonly_surface_map_candidate_v2(packet: Mapping[str, Any]) -> SurfaceMapCandidateValidationResult:
    """Validate a fixture-first DevHub read-only surface map candidate v2 packet."""

    candidate_id = _candidate_id(packet)
    violations: list[SurfaceMapCandidateViolation] = []

    if packet.get("schema_version", packet.get("schemaVersion")) not in (2, "2", "devhub_readonly_surface_map_candidate_v2"):
        violations.append(_violation(candidate_id, "invalid_schema_version", "candidate v2 packet must declare schema version 2"))

    rows = _candidate_rows(packet)
    if not rows:
        violations.append(_violation(candidate_id, "missing_candidate_rows", "candidate v2 packet requires candidate_rows"))
    for index, row in enumerate(rows):
        row_id = _item_id(row, f"candidate_rows[{index}]")
        for field_name, code in REQUIRED_V2_ROW_FIELDS:
            if not _present(row.get(field_name)):
                violations.append(_violation(candidate_id, code, f"candidate row {row_id!r} requires {field_name}"))
        classification = row.get("action_boundary_classification")
        if _present(classification) and _normalize(str(classification)) not in SAFE_ACTION_BOUNDARY_CLASSIFICATIONS:
            violations.append(_violation(candidate_id, "unsafe_action_boundary_classification", f"candidate row {row_id!r} has unsafe action boundary classification"))
        disposition = row.get("reviewer_disposition")
        if _present(disposition) and _normalize(str(disposition)) not in SAFE_REVIEWER_DISPOSITIONS:
            violations.append(_violation(candidate_id, "unsafe_reviewer_disposition", f"candidate row {row_id!r} has unsupported reviewer disposition"))

    if not _valid_validation_commands(packet.get("validation_commands")):
        violations.append(_violation(candidate_id, "missing_validation_commands", "candidate v2 packet requires deterministic validation_commands"))

    _scan_v2_value(packet, "$", candidate_id, violations)
    return SurfaceMapCandidateValidationResult(
        candidate_id=candidate_id,
        reversible_draft_allowed=False,
        violations=tuple(dict.fromkeys(violations)),
    )


def readonly_surface_map_candidate_v2_is_valid(packet: Mapping[str, Any]) -> bool:
    return not validate_readonly_surface_map_candidate_v2(packet).violations


def _candidate_id(candidate: Mapping[str, Any]) -> str:
    for key in ("candidate_id", "surface_id", "id"):
        value = candidate.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return "unknown_surface_candidate"


def _violation(candidate_id: str, code: str, message: str) -> SurfaceMapCandidateViolation:
    return SurfaceMapCandidateViolation(candidate_id=candidate_id, code=code, message=message)


def _confidence_at_or_above(value: Any, minimum: float) -> bool:
    if isinstance(value, bool):
        return False
    try:
        return float(value) >= minimum
    except (TypeError, ValueError):
        return False


def _has_route_evidence(candidate: Mapping[str, Any]) -> bool:
    route_values = _string_values(
        candidate.get("route_evidence"),
        candidate.get("routes"),
        candidate.get("url_pattern"),
    )
    return bool(route_values)


def _has_heading_evidence(candidate: Mapping[str, Any]) -> bool:
    heading_values = _string_values(
        candidate.get("heading_evidence"),
        candidate.get("headings"),
        candidate.get("page_heading"),
    )
    return bool(heading_values)


def _required_label_violations(
    candidate_id: str,
    candidate: Mapping[str, Any],
) -> tuple[SurfaceMapCandidateViolation, ...]:
    violations: list[SurfaceMapCandidateViolation] = []
    labels_by_value: dict[str, list[str]] = {}

    for field in _mapping_items(candidate.get("fields")):
        if field.get("required") is not True:
            continue
        field_id = _item_id(field, "field")
        labels = _label_values(field)
        if len(labels) != 1:
            violations.append(
                _violation(
                    candidate_id,
                    "ambiguous_required_label",
                    f"required field {field_id!r} must have exactly one non-empty label",
                )
            )
            continue
        labels_by_value.setdefault(_normalize(labels[0]), []).append(field_id)

    for label, field_ids in sorted(labels_by_value.items()):
        if len(field_ids) > 1:
            joined = ", ".join(sorted(field_ids))
            violations.append(
                _violation(
                    candidate_id,
                    "ambiguous_required_label",
                    f"required label {label!r} is shared by fields: {joined}",
                )
            )

    return tuple(violations)


def _consequential_reversible_control_violations(
    candidate_id: str,
    candidate: Mapping[str, Any],
) -> tuple[SurfaceMapCandidateViolation, ...]:
    violations: list[SurfaceMapCandidateViolation] = []

    for collection_name in CONTROL_COLLECTIONS:
        for control in _mapping_items(candidate.get(collection_name)):
            if not _is_reversible_control(control):
                continue
            if collection_name != "actions" or _looks_consequential(control):
                control_id = _item_id(control, "control")
                violations.append(
                    _violation(
                        candidate_id,
                        "consequential_control_marked_reversible",
                        f"{collection_name} item {control_id!r} must not be classified as reversible",
                    )
                )

    return tuple(violations)


def _is_reversible_control(control: Mapping[str, Any]) -> bool:
    if control.get("reversible") is True:
        return True
    for key in ("classification", "action_class", "actionClass", "class"):
        value = control.get(key)
        if isinstance(value, str) and _normalize(value) in REVERSIBLE_CLASSIFICATIONS:
            return True
    return False


def _looks_consequential(control: Mapping[str, Any]) -> bool:
    values = _string_values(
        control.get("id"),
        control.get("kind"),
        control.get("type"),
        control.get("label"),
        control.get("name"),
        control.get("text"),
        control.get("aria_label"),
        control.get("ariaLabel"),
    )
    tokens = " ".join(values).replace("_", "-").replace("/", "-").split()
    expanded: set[str] = set()
    for token in tokens:
        expanded.update(part for part in token.split("-") if part)
    return bool(expanded.intersection(CONSEQUENTIAL_CONTROL_TOKENS))


def _candidate_rows(packet: Mapping[str, Any]) -> tuple[Mapping[str, Any], ...]:
    for key in V2_ROW_COLLECTIONS:
        rows = _mapping_items(packet.get(key))
        if rows:
            return rows
    return ()


def _valid_validation_commands(value: Any) -> bool:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)) or not value:
        return False
    for command in value:
        if not isinstance(command, Sequence) or isinstance(command, (str, bytes, bytearray)) or not command:
            return False
        if not all(isinstance(part, str) and part.strip() for part in command):
            return False
    return True


def _scan_v2_value(value: Any, path: str, candidate_id: str, violations: list[SurfaceMapCandidateViolation]) -> None:
    if isinstance(value, Mapping):
        for raw_key, child in value.items():
            key = str(raw_key)
            child_path = f"{path}.{key}"
            if _PRIVATE_OR_SESSION_KEY_RE.search(key) and _present(child) and not _redacted(child):
                violations.append(_violation(candidate_id, "private_session_or_auth_value", f"{child_path} must not contain private, session, browser auth, or raw account values"))
            if _ARTIFACT_KEY_RE.search(key) and _present(child):
                violations.append(_violation(candidate_id, "prohibited_artifact_reference", f"{child_path} must not reference browser, raw, or downloaded artifacts"))
            if _MUTATION_KEY_RE.search(key) and _present(child) and child is not False:
                violations.append(_violation(candidate_id, "active_mutation_flag", f"{child_path} must not enable active DevHub surface, guardrail, prompt, contract, source, or release-state mutation"))
            _scan_v2_value(child, child_path, candidate_id, violations)
        return
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            _scan_v2_value(child, f"{path}[{index}]", candidate_id, violations)
        return
    if isinstance(value, str):
        if not _redacted(value) and _PRIVATE_VALUE_RE.search(value):
            violations.append(_violation(candidate_id, "private_session_or_auth_value", f"{path} must not contain private, session, browser auth, or raw account values"))
        if _ARTIFACT_TEXT_RE.search(value):
            violations.append(_violation(candidate_id, "prohibited_artifact_reference", f"{path} must not reference browser, raw, or downloaded artifacts"))
        if _AUTH_AUTOMATION_RE.search(value):
            violations.append(_violation(candidate_id, "automated_login_or_mfa_claim", f"{path} must not claim automated login, CAPTCHA, MFA, account creation, or password recovery"))
        if _OFFICIAL_ACTION_RE.search(value):
            violations.append(_violation(candidate_id, "consequential_official_action_language", f"{path} must not include consequential official action language"))
        if _GUARANTEE_RE.search(value):
            violations.append(_violation(candidate_id, "legal_or_permitting_guarantee", f"{path} must not guarantee legal compliance or permitting outcomes"))
        if _MUTATION_TEXT_RE.search(value):
            violations.append(_violation(candidate_id, "active_mutation_flag", f"{path} must not reference active DevHub surface, guardrail, prompt, contract, source, or release-state mutation"))


def _mapping_items(raw: Any) -> tuple[Mapping[str, Any], ...]:
    if isinstance(raw, Mapping):
        return (raw,)
    if isinstance(raw, Sequence) and not isinstance(raw, (str, bytes, bytearray)):
        return tuple(item for item in raw if isinstance(item, Mapping))
    return ()


def _item_id(item: Mapping[str, Any], fallback: str) -> str:
    for key in ("id", "field_id", "action_id", "control_id", "name", "row_id"):
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return fallback


def _label_values(item: Mapping[str, Any]) -> tuple[str, ...]:
    return _string_values(
        item.get("label"),
        item.get("labels"),
        item.get("label_evidence"),
        item.get("accessible_name"),
        item.get("aria_label"),
        item.get("ariaLabel"),
    )


def _string_values(*raw_values: Any) -> tuple[str, ...]:
    values: list[str] = []
    for raw in raw_values:
        values.extend(_flatten_strings(raw))
    return tuple(value for value in (_clean(value) for value in values) if value)


def _flatten_strings(raw: Any) -> list[str]:
    if isinstance(raw, str):
        return [raw]
    if isinstance(raw, Mapping):
        values: list[str] = []
        for key in ("text", "label", "name", "title", "heading", "path", "href", "route", "value"):
            value = raw.get(key)
            if isinstance(value, str):
                values.append(value)
        return values
    if isinstance(raw, Sequence) and not isinstance(raw, (str, bytes, bytearray)):
        values = []
        for item in raw:
            values.extend(_flatten_strings(item))
        return values
    return []


def _present(value: Any) -> bool:
    if value is None or value is False:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, Mapping):
        return bool(value)
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return bool(value)
    return True


def _redacted(value: Any) -> bool:
    return isinstance(value, str) and value.strip().lower() in {"redacted", "[redacted]", "***redacted***"}


def _clean(value: str) -> str:
    return " ".join(value.strip().split())


def _normalize(value: str) -> str:
    return _clean(value).casefold()
