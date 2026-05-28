"""Validate PP&D form-field requirement trace packets.

The validator is intentionally fixture-friendly and side-effect free. It accepts
redacted semantic field traces only; private values, credentials, payment data,
stale evidence, ambiguous selectors, unsupported requirement types, and attempts
to treat certification or submission fields as reversible are blockers.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import re
from typing import Iterable, Mapping, Sequence

SUPPORTED_REQUIREMENT_TYPES = frozenset(
    {
        "required",
        "conditionally_required",
        "optional",
        "read_only",
        "computed",
    }
)

ALLOWED_REDACTION_TOKENS = frozenset(
    {
        "[REDACTED]",
        "[EMPTY]",
        "[NOT_CAPTURED]",
        "[SELECTED_OPTION_REDACTED]",
        "[CHECKED_REDACTED]",
    }
)

SENSITIVE_KEY_TERMS = (
    "account_number",
    "auth",
    "card",
    "cookie",
    "credential",
    "cvv",
    "password",
    "payment",
    "private_value",
    "routing_number",
    "secret",
    "session",
    "storage_state",
    "token",
)

PRIVATE_VALUE_RE = re.compile(
    r"("
    r"unsafe_private_value_sentinel|"
    r"[^@\s]+@[^@\s]+\.[^@\s]+|"
    r"\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b|"
    r"\b\d{3}-\d{2}-\d{4}\b|"
    r"\b\d{5}\s+[A-Za-z0-9 .'-]+\b"
    r")",
    re.IGNORECASE,
)

PAYMENT_VALUE_RE = re.compile(
    r"(unsafe_payment_detail_sentinel|\b(?:\d[ -]*?){13,19}\b|\b\d{3,4}\b\s*(?:cvv|cvc|security code))",
    re.IGNORECASE,
)

CREDENTIAL_VALUE_RE = re.compile(
    r"(unsafe_credential_sentinel|password|bearer\s+[A-Za-z0-9._-]+|api[_-]?key|secret|token)",
    re.IGNORECASE,
)

CERTIFICATION_OR_SUBMISSION_TERMS = (
    "acknowledge",
    "certification",
    "certify",
    "final submit",
    "signature",
    "submit application",
    "submission",
)


@dataclass(frozen=True)
class FormFieldRequirementTraceFinding:
    code: str
    field_id: str
    message: str


@dataclass(frozen=True)
class FormFieldRequirementTraceValidation:
    ok: bool
    findings: tuple[FormFieldRequirementTraceFinding, ...]


class FormFieldRequirementTraceError(ValueError):
    def __init__(self, findings: Sequence[FormFieldRequirementTraceFinding]) -> None:
        self.findings = tuple(findings)
        codes = ", ".join(finding.code for finding in self.findings)
        super().__init__(f"form-field requirement trace packet is unsafe: {codes}")


def validate_form_field_requirement_trace_packet(
    packet: Mapping[str, object],
    *,
    current_as_of: str | None = None,
    max_evidence_age_days: int = 365,
    supported_requirement_types: Iterable[str] = SUPPORTED_REQUIREMENT_TYPES,
) -> FormFieldRequirementTraceValidation:
    supported_types = {_text(item) for item in supported_requirement_types if _text(item)}
    as_of = _parse_datetime(current_as_of or _text(packet.get("current_as_of")) or _text(packet.get("generated_at")))
    evidence_index = _evidence_index(packet)
    findings: list[FormFieldRequirementTraceFinding] = []

    for field in _fields(packet):
        field_id = _field_id(field)
        evidence_ids = _sequence(field.get("evidence_ids") or field.get("source_evidence_ids"))
        citation_spans = _mappings(field.get("citation_spans") or field.get("citations"))

        if not evidence_ids or not citation_spans:
            findings.append(
                FormFieldRequirementTraceFinding(
                    "uncited_field",
                    field_id,
                    "field requirement traces must include evidence ids and citation spans",
                )
            )
        elif not all(evidence_id in evidence_index for evidence_id in evidence_ids):
            findings.append(
                FormFieldRequirementTraceFinding(
                    "uncited_field",
                    field_id,
                    "field requirement trace cites evidence that is absent from the packet evidence index",
                )
            )

        requirement_type = _text(field.get("requirement_type") or field.get("type"))
        if requirement_type not in supported_types:
            findings.append(
                FormFieldRequirementTraceFinding(
                    "unsupported_requirement_type",
                    field_id,
                    "field requirement type is not supported for form-field trace ingestion",
                )
            )

        if _has_stale_evidence(field, evidence_index, evidence_ids, as_of, max_evidence_age_days):
            findings.append(
                FormFieldRequirementTraceFinding(
                    "stale_evidence",
                    field_id,
                    "field evidence is older than the allowed freshness window or has a mismatched hash",
                )
            )

        if _selector_is_ambiguous(field):
            findings.append(
                FormFieldRequirementTraceFinding(
                    "ambiguous_selector",
                    field_id,
                    "field selector must resolve to exactly one accessible element with stable context",
                )
            )

        if _contains_private_value(field):
            findings.append(
                FormFieldRequirementTraceFinding(
                    "private_value",
                    field_id,
                    "field trace contains a concrete private value or unsafe private-value sentinel",
                )
            )

        if _contains_credentials(field):
            findings.append(
                FormFieldRequirementTraceFinding(
                    "credential_value",
                    field_id,
                    "field trace contains credential-like data or credential storage metadata",
                )
            )

        if _contains_payment_details(field):
            findings.append(
                FormFieldRequirementTraceFinding(
                    "payment_detail",
                    field_id,
                    "field trace contains payment-related data or payment-detail sentinels",
                )
            )

        if _is_certification_or_submission_field(field) and field.get("reversible") is True:
            findings.append(
                FormFieldRequirementTraceFinding(
                    "irreversible_action_marked_reversible",
                    field_id,
                    "certification and submission fields must not be marked reversible",
                )
            )

    return FormFieldRequirementTraceValidation(ok=not findings, findings=tuple(findings))


def require_form_field_requirement_trace_packet(
    packet: Mapping[str, object],
    *,
    current_as_of: str | None = None,
    max_evidence_age_days: int = 365,
    supported_requirement_types: Iterable[str] = SUPPORTED_REQUIREMENT_TYPES,
) -> None:
    result = validate_form_field_requirement_trace_packet(
        packet,
        current_as_of=current_as_of,
        max_evidence_age_days=max_evidence_age_days,
        supported_requirement_types=supported_requirement_types,
    )
    if result.findings:
        raise FormFieldRequirementTraceError(result.findings)


def _fields(packet: Mapping[str, object]) -> tuple[Mapping[str, object], ...]:
    return _mappings(packet.get("fields") or packet.get("field_traces") or packet.get("records"))


def _evidence_index(packet: Mapping[str, object]) -> dict[str, Mapping[str, object]]:
    evidence_items = _mappings(packet.get("evidence_index") or packet.get("source_evidence"))
    indexed: dict[str, Mapping[str, object]] = {}
    for evidence in evidence_items:
        evidence_id = _text(evidence.get("evidence_id") or evidence.get("id"))
        if evidence_id:
            indexed[evidence_id] = evidence
    return indexed


def _field_id(field: Mapping[str, object]) -> str:
    return _text(field.get("field_id") or field.get("id") or field.get("name")) or "unknown-field"


def _text(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _sequence(value: object) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        text = value.strip()
        return (text,) if text else ()
    if isinstance(value, Iterable):
        return tuple(text for item in value if (text := _text(item)))
    text = _text(value)
    return (text,) if text else ()


def _mappings(value: object) -> tuple[Mapping[str, object], ...]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return ()
    return tuple(item for item in value if isinstance(item, Mapping))


def _parse_datetime(value: str) -> datetime | None:
    if not value:
        return None
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _has_stale_evidence(
    field: Mapping[str, object],
    evidence_index: Mapping[str, Mapping[str, object]],
    evidence_ids: Sequence[str],
    as_of: datetime | None,
    max_age_days: int,
) -> bool:
    if as_of is None or not evidence_ids:
        return False
    expected_hash = _text(field.get("evidence_hash") or field.get("source_hash"))
    for evidence_id in evidence_ids:
        evidence = evidence_index.get(evidence_id)
        if evidence is None:
            continue
        captured = _parse_datetime(_text(evidence.get("captured_at") or evidence.get("last_verified_at")))
        if captured is not None and (as_of - captured).days > max_age_days:
            return True
        current_hash = _text(evidence.get("content_hash") or evidence.get("source_hash"))
        if expected_hash and current_hash and expected_hash != current_hash:
            return True
    return False


def _selector_is_ambiguous(field: Mapping[str, object]) -> bool:
    selector = field.get("selector")
    if not isinstance(selector, Mapping):
        return True
    match_count = selector.get("match_count")
    if match_count != 1:
        return True
    strategy = _text(selector.get("strategy"))
    name = _text(selector.get("name") or selector.get("accessible_name") or selector.get("label_text"))
    context = _text(selector.get("stable_context") or selector.get("nearby_heading"))
    return not strategy or not name or not context


def _contains_private_value(value: object, key_path: str = "") -> bool:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            key_text = _text(key).lower()
            if key_text in {"value", "raw_value", "private_value"} and _unsafe_private_scalar(nested):
                return True
            if _contains_private_value(nested, f"{key_path}.{key_text}" if key_path else key_text):
                return True
        return False
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return any(_contains_private_value(item, key_path) for item in value)
    return _unsafe_private_scalar(value)


def _unsafe_private_scalar(value: object) -> bool:
    text = _text(value)
    if not text or text in ALLOWED_REDACTION_TOKENS or text.startswith("[REDACTED:"):
        return False
    return bool(PRIVATE_VALUE_RE.search(text))


def _contains_credentials(value: object) -> bool:
    return _contains_sensitive(value, CREDENTIAL_VALUE_RE, {"credential", "password", "secret", "token", "cookie", "auth", "session", "storage_state"})


def _contains_payment_details(value: object) -> bool:
    return _contains_sensitive(value, PAYMENT_VALUE_RE, {"payment", "card", "cvv", "cvc", "routing_number", "account_number"})


def _contains_sensitive(value: object, value_pattern: re.Pattern[str], key_terms: set[str]) -> bool:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            key_text = _text(key).lower()
            if any(term in key_text for term in key_terms):
                nested_text = _text(nested)
                if nested_text and nested_text not in ALLOWED_REDACTION_TOKENS and not nested_text.startswith("[REDACTED:"):
                    return True
            if _contains_sensitive(nested, value_pattern, key_terms):
                return True
        return False
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return any(_contains_sensitive(item, value_pattern, key_terms) for item in value)
    text = _text(value)
    if not text or text in ALLOWED_REDACTION_TOKENS or text.startswith("[REDACTED:"):
        return False
    return bool(value_pattern.search(text))


def _is_certification_or_submission_field(field: Mapping[str, object]) -> bool:
    searchable = " ".join(
        _text(field.get(key)).lower()
        for key in ("field_id", "id", "name", "label", "purpose", "safety_class", "action_classification")
    )
    return any(term in searchable for term in CERTIFICATION_OR_SUBMISSION_TERMS)


validate_packet = validate_form_field_requirement_trace_packet
require_packet = require_form_field_requirement_trace_packet

__all__ = [
    "FormFieldRequirementTraceError",
    "FormFieldRequirementTraceFinding",
    "FormFieldRequirementTraceValidation",
    "SUPPORTED_REQUIREMENT_TYPES",
    "require_form_field_requirement_trace_packet",
    "require_packet",
    "validate_form_field_requirement_trace_packet",
    "validate_packet",
]
