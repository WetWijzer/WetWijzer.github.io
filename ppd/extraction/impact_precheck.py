"""Validation for requirement extraction impact precheck packets.

The precheck packet is intentionally a metadata-only planning artifact.  It may
identify cited rerun scopes and affected IDs, but it must not carry raw bodies,
private case facts, live execution claims, outcome guarantees, or active mutation
flags.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence


class ImpactPrecheckValidationError(ValueError):
    """Raised when a requirement extraction impact precheck packet is unsafe."""

    def __init__(self, violations: Sequence[str]) -> None:
        self.violations = tuple(violations)
        super().__init__("; ".join(self.violations))


@dataclass(frozen=True)
class ImpactPrecheckViolation:
    code: str
    message: str


_REQUIRED_AFFECTED_ID_FIELDS = (
    "affected_requirement_ids",
    "affected_process_ids",
    "affected_guardrail_ids",
)

_REVIEWER_OWNER_FIELDS = (
    "reviewer_owners",
    "reviewers",
    "owner_reviewers",
)

_CITATION_FIELDS = (
    "citation_ids",
    "source_evidence_ids",
    "evidence_ids",
    "citations",
)

_RAW_REFERENCE_TERMS = (
    "raw_body",
    "raw_html",
    "raw_text",
    "body_ref",
    "body_path",
    "download_ref",
    "download_url",
    "downloaded_document",
    "archive_ref",
    "archive_url",
    "archive_path",
    "warc",
    "har",
    "trace",
    "screenshot",
)

_PRIVATE_FACT_TERMS = (
    "private_case_fact",
    "private_case_facts",
    "case_fact",
    "case_facts",
    "known_facts",
    "applicant_name",
    "owner_name",
    "phone_number",
    "email_address",
    "tax_account",
    "permit_number_private",
    "private_address",
    "site_address",
)

_LIVE_EXECUTION_TERMS = (
    "live extraction",
    "ran extraction",
    "run extraction",
    "executed extraction",
    "processor executed",
    "executed processor",
    "processor run completed",
    "crawl completed",
    "downloaded live",
    "fetched live",
)

_OUTCOME_GUARANTEE_TERMS = (
    "permit will be approved",
    "approval guaranteed",
    "guaranteed approval",
    "guaranteed issuance",
    "will issue",
    "will pass review",
    "no legal risk",
    "legally sufficient",
    "ensures compliance",
)

_MUTATION_FLAG_FIELDS = (
    "mutates_requirements",
    "mutates_processes",
    "mutates_guardrails",
    "mutates_prompts",
    "mutates_surface_registry",
    "mutates_monitoring",
    "mutates_release_state",
    "active_requirement_mutation",
    "active_process_mutation",
    "active_guardrail_mutation",
    "active_prompt_mutation",
    "active_surface_registry_mutation",
    "active_monitoring_mutation",
    "active_release_state_mutation",
    "writes_requirements",
    "writes_processes",
    "writes_guardrails",
    "writes_prompts",
    "writes_surface_registry",
    "writes_monitoring",
    "writes_release_state",
)

_MUTATION_SCOPE_TERMS = (
    "requirement",
    "process",
    "guardrail",
    "prompt",
    "surface-registry",
    "surface_registry",
    "monitoring",
    "release-state",
    "release_state",
)


def validate_requirement_extraction_impact_precheck_packet(packet: Mapping[str, Any]) -> list[ImpactPrecheckViolation]:
    """Return all validation violations for a precheck packet.

    The function is deliberately schema-tolerant so callers can evolve packet
    shape while preserving the same safety boundary.
    """

    violations: list[ImpactPrecheckViolation] = []

    if not isinstance(packet, Mapping):
        return [ImpactPrecheckViolation("packet_not_mapping", "precheck packet must be a mapping")]

    rerun_scopes = packet.get("rerun_scopes")
    if not _is_non_empty_sequence(rerun_scopes):
        violations.append(ImpactPrecheckViolation("missing_rerun_scopes", "rerun_scopes must be a non-empty list"))
    else:
        for index, scope in enumerate(rerun_scopes):
            if not isinstance(scope, Mapping):
                violations.append(ImpactPrecheckViolation("invalid_rerun_scope", f"rerun_scopes[{index}] must be a mapping"))
                continue
            if not _first_non_empty_sequence(scope, _CITATION_FIELDS):
                violations.append(ImpactPrecheckViolation("uncited_rerun_scope", f"rerun_scopes[{index}] must include citation or source evidence IDs"))

    for field in _REQUIRED_AFFECTED_ID_FIELDS:
        if not _is_non_empty_sequence(packet.get(field)):
            violations.append(ImpactPrecheckViolation("missing_affected_ids", f"{field} must be a non-empty list"))

    if not _has_expected_metadata_only_outputs(packet):
        violations.append(ImpactPrecheckViolation("missing_metadata_only_outputs", "expected outputs must explicitly be metadata-only"))

    if not _first_non_empty_sequence(packet, _REVIEWER_OWNER_FIELDS):
        violations.append(ImpactPrecheckViolation("missing_reviewer_owners", "reviewer owners must be provided"))

    for path, value in _walk(packet):
        path_text = ".".join(str(part) for part in path).lower()
        value_text = _stringify(value).lower()

        if _contains_any(path_text, _RAW_REFERENCE_TERMS) or _contains_any(value_text, _RAW_REFERENCE_TERMS):
            violations.append(ImpactPrecheckViolation("raw_reference", f"raw body/download/archive references are not allowed at {path_text or ''}"))

        if _contains_any(path_text, _PRIVATE_FACT_TERMS):
            violations.append(ImpactPrecheckViolation("private_case_facts", f"private case facts are not allowed at {path_text}"))

        if isinstance(value, str) and _contains_any(value_text, _PRIVATE_FACT_TERMS):
            violations.append(ImpactPrecheckViolation("private_case_facts", f"private case facts are not allowed at {path_text or ''}"))

        if isinstance(value, str) and _contains_any(value_text, _LIVE_EXECUTION_TERMS):
            violations.append(ImpactPrecheckViolation("live_execution_claim", f"live extraction or processor execution claims are not allowed at {path_text or ''}"))

        if isinstance(value, str) and _contains_any(value_text, _OUTCOME_GUARANTEE_TERMS):
            violations.append(ImpactPrecheckViolation("outcome_guarantee", f"legal or permitting outcome guarantees are not allowed at {path_text or ''}"))

        if _is_active_mutation_flag(path_text, value):
            violations.append(ImpactPrecheckViolation("active_mutation_flag", f"active mutation flags are not allowed at {path_text or ''}"))

    return _dedupe_violations(violations)


def assert_valid_requirement_extraction_impact_precheck_packet(packet: Mapping[str, Any]) -> None:
    """Raise if a requirement extraction impact precheck packet is invalid."""

    violations = validate_requirement_extraction_impact_precheck_packet(packet)
    if violations:
        raise ImpactPrecheckValidationError([f"{violation.code}: {violation.message}" for violation in violations])


def is_valid_requirement_extraction_impact_precheck_packet(packet: Mapping[str, Any]) -> bool:
    """Return True when the packet passes the impact precheck validator."""

    return not validate_requirement_extraction_impact_precheck_packet(packet)


def _has_expected_metadata_only_outputs(packet: Mapping[str, Any]) -> bool:
    expected_outputs = packet.get("expected_outputs")
    if isinstance(expected_outputs, Mapping):
        if expected_outputs.get("metadata_only") is True:
            return True
        outputs = expected_outputs.get("outputs")
        if _is_non_empty_sequence(outputs):
            return all(isinstance(item, Mapping) and item.get("metadata_only") is True for item in outputs)
    if _is_non_empty_sequence(expected_outputs):
        return all(isinstance(item, Mapping) and item.get("metadata_only") is True for item in expected_outputs)
    return False


def _is_active_mutation_flag(path_text: str, value: Any) -> bool:
    if not value:
        return False
    if any(field in path_text for field in _MUTATION_FLAG_FIELDS):
        return True
    if "mutation" in path_text and any(term in path_text for term in _MUTATION_SCOPE_TERMS):
        return True
    if "mutate" in path_text and any(term in path_text for term in _MUTATION_SCOPE_TERMS):
        return True
    return False


def _first_non_empty_sequence(mapping: Mapping[str, Any], fields: Iterable[str]) -> Sequence[Any] | None:
    for field in fields:
        value = mapping.get(field)
        if _is_non_empty_sequence(value):
            return value
    return None


def _is_non_empty_sequence(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)) and len(value) > 0


def _contains_any(text: str, terms: Iterable[str]) -> bool:
    return any(term in text for term in terms)


def _stringify(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float, bool)) or value is None:
        return str(value)
    return ""


def _walk(value: Any, path: tuple[Any, ...] = ()) -> Iterable[tuple[tuple[Any, ...], Any]]:
    yield path, value
    if isinstance(value, Mapping):
        for key, child in value.items():
            yield from _walk(child, path + (key,))
    elif _is_non_empty_sequence(value):
        for index, child in enumerate(value):
            yield from _walk(child, path + (index,))


def _dedupe_violations(violations: Sequence[ImpactPrecheckViolation]) -> list[ImpactPrecheckViolation]:
    seen: set[tuple[str, str]] = set()
    result: list[ImpactPrecheckViolation] = []
    for violation in violations:
        key = (violation.code, violation.message)
        if key in seen:
            continue
        seen.add(key)
        result.append(violation)
    return result
