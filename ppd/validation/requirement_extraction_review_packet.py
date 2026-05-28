"""Validate PP&D requirement extraction review packets before promotion."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence

DEFAULT_LOW_CONFIDENCE_THRESHOLD = 0.75

SUPPORTED_REQUIREMENT_TYPES = frozenset(
    {
        "action_gate",
        "deadline",
        "document_requirement",
        "exception",
        "fee_trigger",
        "license_requirement",
        "obligation",
        "permission",
        "precondition",
        "prohibition",
    }
)

HUMAN_REVIEW_STATUSES = frozenset(
    {
        "approved",
        "fixture_reviewed",
        "human_reviewed",
        "needs_human_review",
        "reviewed",
    }
)

REVIEWED_STATUSES = frozenset(
    {
        "approved",
        "fixture_reviewed",
        "human_reviewed",
        "reviewed",
    }
)

RAW_DOCUMENT_BODY_KEYS = frozenset(
    {
        "body",
        "body_html",
        "body_text",
        "document_body",
        "full_text",
        "html",
        "page_body",
        "pdf_text",
        "raw_body",
        "raw_document_body",
        "raw_html",
        "raw_text",
    }
)

PRIVATE_VALUE_KEYS = frozenset(
    {
        "account_number",
        "auth_state",
        "card_number",
        "cookie",
        "cookies",
        "cvv",
        "file_contents",
        "known_value",
        "password",
        "payment_details",
        "private_value",
        "raw_value",
        "routing_number",
        "session_state",
        "ssn",
        "storage_state",
        "token",
    }
)

PRIVATE_STRING_MARKERS = (
    "/data/private/",
    "/devhub/.auth/",
    "/devhub/downloads/",
    "/devhub/screenshots/",
    "/devhub/traces/",
    ".har",
    "auth-state",
    "bearer ",
    "card_number",
    "cookie=",
    "cvv",
    "password=",
    "real user",
    "routing_number",
    "storage-state",
    "token=",
    "trace.zip",
)


@dataclass(frozen=True)
class RequirementExtractionReviewFinding:
    """A deterministic reason a review packet cannot be accepted."""

    code: str
    requirement_id: str
    path: str
    message: str


@dataclass(frozen=True)
class RequirementExtractionReviewValidation:
    """Validation result for a requirement extraction review packet."""

    ok: bool
    findings: tuple[RequirementExtractionReviewFinding, ...]


class RequirementExtractionReviewPacketError(ValueError):
    """Raised when a requirement extraction review packet is unsafe."""

    def __init__(self, findings: Sequence[RequirementExtractionReviewFinding]) -> None:
        self.findings = tuple(findings)
        codes = ", ".join(finding.code for finding in self.findings)
        super().__init__(f"requirement extraction review packet rejected: {codes}")


def validate_requirement_extraction_review_packet(
    packet: Mapping[str, object],
    *,
    low_confidence_threshold: float = DEFAULT_LOW_CONFIDENCE_THRESHOLD,
    supported_requirement_types: Iterable[str] = SUPPORTED_REQUIREMENT_TYPES,
) -> RequirementExtractionReviewValidation:
    """Return all blockers found in a requirement extraction review packet."""

    findings: list[RequirementExtractionReviewFinding] = []
    supported_types = {_text(item) for item in supported_requirement_types if _text(item)}

    findings.extend(_privacy_findings(packet))

    for index, requirement in enumerate(_requirements(packet)):
        path = f"$.requirements[{index}]"
        requirement_id = _requirement_id(requirement)

        if not _has_citation(requirement):
            findings.append(
                RequirementExtractionReviewFinding(
                    "uncited_requirement",
                    requirement_id,
                    path,
                    "requirement review nodes must include source evidence or citation spans",
                )
            )

        if _low_confidence_without_human_review(requirement, low_confidence_threshold):
            findings.append(
                RequirementExtractionReviewFinding(
                    "low_confidence_without_human_review_status",
                    requirement_id,
                    path,
                    "low-confidence requirement nodes must carry a human-review status",
                )
            )

        requirement_type = _text(requirement.get("requirement_type") or requirement.get("type"))
        if not requirement_type or requirement_type not in supported_types:
            findings.append(
                RequirementExtractionReviewFinding(
                    "unsupported_requirement_type",
                    requirement_id,
                    path,
                    "requirement type is not supported for PP&D extraction review packets",
                )
            )

        if not _sequence(requirement.get("permit_types") or requirement.get("permit_type_ids") or requirement.get("permitTypeIds")):
            findings.append(
                RequirementExtractionReviewFinding(
                    "missing_permit_link",
                    requirement_id,
                    path,
                    "requirement nodes must link to at least one permit type",
                )
            )

        if not _sequence(requirement.get("process_stage") or requirement.get("process_stages") or requirement.get("processStageIds")):
            findings.append(
                RequirementExtractionReviewFinding(
                    "missing_process_stage_link",
                    requirement_id,
                    path,
                    "requirement nodes must link to a process stage",
                )
            )

        if _formalization_ready_before_review(requirement):
            findings.append(
                RequirementExtractionReviewFinding(
                    "formalization_ready_before_review",
                    requirement_id,
                    path,
                    "formalization_status cannot be ready until human review is complete",
                )
            )

    return RequirementExtractionReviewValidation(ok=not findings, findings=tuple(findings))


def require_requirement_extraction_review_packet(
    packet: Mapping[str, object],
    *,
    low_confidence_threshold: float = DEFAULT_LOW_CONFIDENCE_THRESHOLD,
    supported_requirement_types: Iterable[str] = SUPPORTED_REQUIREMENT_TYPES,
) -> None:
    """Raise when a requirement extraction review packet is not safe to accept."""

    result = validate_requirement_extraction_review_packet(
        packet,
        low_confidence_threshold=low_confidence_threshold,
        supported_requirement_types=supported_requirement_types,
    )
    if result.findings:
        raise RequirementExtractionReviewPacketError(result.findings)


def _requirements(packet: Mapping[str, object]) -> tuple[Mapping[str, object], ...]:
    value = packet.get("requirements") or packet.get("requirement_nodes") or packet.get("nodes")
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return ()
    return tuple(item for item in value if isinstance(item, Mapping))


def _requirement_id(requirement: Mapping[str, object]) -> str:
    return _text(requirement.get("requirement_id") or requirement.get("id")) or "unknown-requirement"


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


def _has_citation(requirement: Mapping[str, object]) -> bool:
    if _sequence(requirement.get("source_evidence_ids") or requirement.get("sourceEvidenceIds")):
        return True
    for key in ("citation_spans", "citations", "source_evidence"):
        value = requirement.get(key)
        if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
            if any(isinstance(item, Mapping) for item in value):
                return True
    return False


def _low_confidence_without_human_review(requirement: Mapping[str, object], threshold: float) -> bool:
    try:
        confidence = float(requirement.get("confidence"))
    except (TypeError, ValueError):
        return True
    if confidence >= threshold:
        return False
    review_status = _text(requirement.get("human_review_status") or requirement.get("review_status")).lower()
    return review_status not in HUMAN_REVIEW_STATUSES


def _formalization_ready_before_review(requirement: Mapping[str, object]) -> bool:
    formalization_status = _text(requirement.get("formalization_status") or requirement.get("formalizationStatus")).lower()
    if formalization_status != "ready":
        return False
    review_status = _text(requirement.get("human_review_status") or requirement.get("review_status")).lower()
    return review_status not in REVIEWED_STATUSES


def _privacy_findings(value: object, path: str = "$", requirement_id: str = "packet") -> tuple[RequirementExtractionReviewFinding, ...]:
    findings: list[RequirementExtractionReviewFinding] = []
    if isinstance(value, Mapping):
        current_requirement_id = _requirement_id(value) if ("requirement_id" in value or "id" in value) else requirement_id
        for key, child in value.items():
            key_text = str(key)
            normalized_key = _normalize_key(key_text)
            child_path = f"{path}.{key_text}"
            if normalized_key in RAW_DOCUMENT_BODY_KEYS:
                findings.append(
                    RequirementExtractionReviewFinding(
                        "raw_document_body_present",
                        current_requirement_id,
                        child_path,
                        "review packets must carry citations and excerpts, not raw document bodies",
                    )
                )
            if normalized_key in PRIVATE_VALUE_KEYS:
                findings.append(
                    RequirementExtractionReviewFinding(
                        "private_value_present",
                        current_requirement_id,
                        child_path,
                        "review packets must not include private values or runtime secrets",
                    )
                )
            findings.extend(_privacy_findings(child, child_path, current_requirement_id))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(_privacy_findings(child, f"{path}[{index}]", requirement_id))
    elif isinstance(value, str):
        lowered = value.lower()
        if any(marker in lowered for marker in PRIVATE_STRING_MARKERS):
            findings.append(
                RequirementExtractionReviewFinding(
                    "private_value_present",
                    requirement_id,
                    path,
                    "review packets must not include private values or runtime artifacts",
                )
            )
    return tuple(findings)


def _normalize_key(value: str) -> str:
    chars: list[str] = []
    for character in value:
        if character.isalnum():
            chars.append(character.lower())
        else:
            chars.append("_")
    normalized = "".join(chars)
    while "__" in normalized:
        normalized = normalized.replace("__", "_")
    return normalized.strip("_")


validate_packet = validate_requirement_extraction_review_packet
require_packet = require_requirement_extraction_review_packet

__all__ = [
    "DEFAULT_LOW_CONFIDENCE_THRESHOLD",
    "HUMAN_REVIEW_STATUSES",
    "RAW_DOCUMENT_BODY_KEYS",
    "REVIEWED_STATUSES",
    "RequirementExtractionReviewFinding",
    "RequirementExtractionReviewPacketError",
    "RequirementExtractionReviewValidation",
    "SUPPORTED_REQUIREMENT_TYPES",
    "require_packet",
    "require_requirement_extraction_review_packet",
    "validate_packet",
    "validate_requirement_extraction_review_packet",
]
