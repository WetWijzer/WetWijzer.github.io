"""Gate refreshed requirement packets before formal guardrail ingestion."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence

DEFAULT_MIN_FORMAL_GUARDRAIL_CONFIDENCE = 0.75
SUPPORTED_FORMAL_REQUIREMENT_TYPES = frozenset(
    {
        "action_gate",
        "deadline",
        "document_requirement",
        "fee_trigger",
        "precondition",
    }
)
HUMAN_REVIEWED_STATUSES = frozenset(
    {
        "approved",
        "fixture_reviewed",
        "human_reviewed",
        "reviewed",
    }
)


@dataclass(frozen=True)
class RefreshedRequirementPacketFinding:
    """A reason a refreshed requirement cannot feed formal guardrails."""

    code: str
    requirement_id: str
    message: str


@dataclass(frozen=True)
class RefreshedRequirementPacketValidation:
    """Formal guardrail feed validation result."""

    ok: bool
    findings: tuple[RefreshedRequirementPacketFinding, ...]


class RefreshedRequirementPacketGateError(ValueError):
    """Raised when a refreshed requirement packet is not safe to ingest."""

    def __init__(self, findings: Sequence[RefreshedRequirementPacketFinding]) -> None:
        self.findings = tuple(findings)
        codes = ", ".join(finding.code for finding in self.findings)
        super().__init__(f"refreshed requirement packet cannot feed formal guardrails: {codes}")


def validate_refreshed_requirement_packet_for_formal_guardrails(
    packet: Mapping[str, object],
    *,
    current_source_hashes: Mapping[str, str] | None = None,
    min_confidence: float = DEFAULT_MIN_FORMAL_GUARDRAIL_CONFIDENCE,
    supported_requirement_types: Iterable[str] = SUPPORTED_FORMAL_REQUIREMENT_TYPES,
) -> RefreshedRequirementPacketValidation:
    """Return blockers for formal guardrail ingestion of refreshed requirements."""

    supported_types = {_text(item) for item in supported_requirement_types if _text(item)}
    expected_hashes = {_text(key): _text(value) for key, value in (current_source_hashes or {}).items()}
    findings: list[RefreshedRequirementPacketFinding] = []

    for record in _records(packet):
        source_key = _source_key(record)
        record_guardrail_ids = _sequence(record.get("affected_guardrail_ids") or record.get("guardrail_ids"))
        record_process_ids = _sequence(record.get("affected_process_ids") or record.get("process_ids"))
        stale_source = _has_stale_source_hash(record, expected_hashes, source_key)

        for requirement in _requirements(record):
            requirement_id = _requirement_id(requirement)

            if not _has_citation_spans(requirement):
                findings.append(
                    RefreshedRequirementPacketFinding(
                        "missing_citation_spans",
                        requirement_id,
                        "citation spans are required before formal guardrail ingestion",
                    )
                )

            if stale_source:
                findings.append(
                    RefreshedRequirementPacketFinding(
                        "stale_source_hash",
                        requirement_id,
                        "refreshed source hash must match the current source hash registry",
                    )
                )

            if _low_confidence_without_human_review(requirement, min_confidence):
                findings.append(
                    RefreshedRequirementPacketFinding(
                        "low_confidence_without_human_review",
                        requirement_id,
                        "low-confidence refreshed requirements need human review before formal guardrails",
                    )
                )

            requirement_type = _text(requirement.get("requirement_type") or requirement.get("type"))
            if not requirement_type or requirement_type not in supported_types:
                findings.append(
                    RefreshedRequirementPacketFinding(
                        "unsupported_requirement_type",
                        requirement_id,
                        "requirement type is not supported by the formal guardrail compiler",
                    )
                )

            if not _sequence(requirement.get("affected_process_ids") or requirement.get("process_ids")) and not record_process_ids:
                findings.append(
                    RefreshedRequirementPacketFinding(
                        "missing_affected_process_ids",
                        requirement_id,
                        "affected process identifiers are required for formal guardrail routing",
                    )
                )

            if not _sequence(requirement.get("affected_guardrail_ids") or requirement.get("guardrail_ids")) and not record_guardrail_ids:
                findings.append(
                    RefreshedRequirementPacketFinding(
                        "missing_affected_guardrail_ids",
                        requirement_id,
                        "affected guardrail identifiers are required for formal guardrail routing",
                    )
                )

    return RefreshedRequirementPacketValidation(ok=not findings, findings=tuple(findings))


def require_refreshed_requirement_packet_for_formal_guardrails(
    packet: Mapping[str, object],
    *,
    current_source_hashes: Mapping[str, str] | None = None,
    min_confidence: float = DEFAULT_MIN_FORMAL_GUARDRAIL_CONFIDENCE,
    supported_requirement_types: Iterable[str] = SUPPORTED_FORMAL_REQUIREMENT_TYPES,
) -> None:
    """Raise when a refreshed requirement packet is blocked from formal guardrails."""

    result = validate_refreshed_requirement_packet_for_formal_guardrails(
        packet,
        current_source_hashes=current_source_hashes,
        min_confidence=min_confidence,
        supported_requirement_types=supported_requirement_types,
    )
    if result.findings:
        raise RefreshedRequirementPacketGateError(result.findings)


def _records(packet: Mapping[str, object]) -> tuple[Mapping[str, object], ...]:
    records = packet.get("records")
    if not isinstance(records, Sequence) or isinstance(records, (str, bytes, bytearray)):
        return ()
    return tuple(record for record in records if isinstance(record, Mapping))


def _requirements(record: Mapping[str, object]) -> tuple[Mapping[str, object], ...]:
    requirements = record.get("requirements")
    if not isinstance(requirements, Sequence) or isinstance(requirements, (str, bytes, bytearray)):
        return ()
    return tuple(requirement for requirement in requirements if isinstance(requirement, Mapping))


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


def _requirement_id(requirement: Mapping[str, object]) -> str:
    return _text(requirement.get("id") or requirement.get("requirement_id")) or "unknown-requirement"


def _source_key(record: Mapping[str, object]) -> str:
    return _text(record.get("canonical_url") or record.get("source_id") or record.get("document_id"))


def _has_citation_spans(requirement: Mapping[str, object]) -> bool:
    spans = requirement.get("citation_spans") or requirement.get("citations")
    if not isinstance(spans, Sequence) or isinstance(spans, (str, bytes, bytearray)):
        return False
    return any(isinstance(span, Mapping) for span in spans)


def _has_stale_source_hash(record: Mapping[str, object], expected_hashes: Mapping[str, str], source_key: str) -> bool:
    refreshed_hash = _text(record.get("refreshed_source_hash") or record.get("source_hash") or record.get("content_hash"))
    expected_hash = _text(record.get("current_source_hash") or record.get("expected_source_hash"))
    if not expected_hash and source_key:
        expected_hash = expected_hashes.get(source_key, "")
    return bool(expected_hash and refreshed_hash and refreshed_hash != expected_hash)


def _low_confidence_without_human_review(requirement: Mapping[str, object], minimum: float) -> bool:
    try:
        confidence = float(requirement.get("confidence"))
    except (TypeError, ValueError):
        return True
    if confidence >= minimum:
        return False
    review_status = _text(requirement.get("human_review_status") or requirement.get("review_status")).lower()
    return review_status not in HUMAN_REVIEWED_STATUSES


validate_packet_for_formal_guardrails = validate_refreshed_requirement_packet_for_formal_guardrails
require_packet_for_formal_guardrails = require_refreshed_requirement_packet_for_formal_guardrails

__all__ = [
    "DEFAULT_MIN_FORMAL_GUARDRAIL_CONFIDENCE",
    "HUMAN_REVIEWED_STATUSES",
    "RefreshedRequirementPacketFinding",
    "RefreshedRequirementPacketGateError",
    "RefreshedRequirementPacketValidation",
    "SUPPORTED_FORMAL_REQUIREMENT_TYPES",
    "require_packet_for_formal_guardrails",
    "require_refreshed_requirement_packet_for_formal_guardrails",
    "validate_packet_for_formal_guardrails",
    "validate_refreshed_requirement_packet_for_formal_guardrails",
]
