"""Validation for source freshness drift triage v2 packets.

The validator is intentionally side-effect free. It accepts already-materialized
packet dictionaries and rejects packet content that would imply private facts,
raw crawl artifacts, live execution, legal/permitting guarantees, or active state
mutation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence


BLOCKED_MUTATION_AREAS = (
    "source",
    "schedule",
    "requirement",
    "process",
    "guardrail",
    "prompt",
    "monitoring",
    "release_state",
    "agent_state",
)

RAW_REFERENCE_TOKENS = (
    "raw_crawl_output",
    "raw_crawler_output",
    "raw_body",
    "raw_html",
    "raw_response",
    "raw_payload",
    "downloaded_document",
    "downloaded_documents",
    "downloaded_pdf",
    "download_path",
    "local_path",
    "private_path",
    "screenshot",
    "trace",
    "har",
    "warc",
    "file://",
    ".har",
    ".warc",
)

LIVE_EXECUTION_TOKENS = (
    "live crawl",
    "live crawler",
    "live processor",
    "live devhub",
    "live llm",
    "ran crawler",
    "ran processor",
    "ran devhub",
    "ran llm",
    "executed crawler",
    "executed processor",
    "executed devhub",
    "executed llm",
    "devhub execution",
    "llm execution",
)

OUTCOME_GUARANTEE_TOKENS = (
    "guaranteed approval",
    "guarantees approval",
    "guaranteed permit",
    "permit will be approved",
    "approval is certain",
    "legal outcome guaranteed",
    "permitting outcome guaranteed",
    "will pass inspection",
    "will be issued",
)

PRIVATE_FACT_TOKENS = (
    "private",
    "authenticated",
    "credential",
    "cookie",
    "session",
    "mfa",
    "captcha",
    "payment",
    "password",
    "ssn",
)


@dataclass(frozen=True)
class TriageValidationIssue:
    """A deterministic validation issue for a triage packet."""

    code: str
    path: str
    message: str


class TriageValidationError(ValueError):
    """Raised when a triage packet is invalid."""

    def __init__(self, issues: Sequence[TriageValidationIssue]) -> None:
        self.issues = tuple(issues)
        detail = "; ".join(f"{issue.path}: {issue.code}" for issue in self.issues)
        super().__init__(detail)


def validate_source_freshness_drift_triage_v2_packet(packet: Mapping[str, Any]) -> None:
    """Validate a source freshness drift triage v2 packet.

    A valid packet must be fully cited, artifact-scoped, owner-assigned, and
    limited to offline triage evidence. It must not carry private facts, raw
    crawl/download references, live execution claims, legal/permitting outcome
    guarantees, or active mutation flags.
    """

    issues: list[TriageValidationIssue] = []
    _validate_packet_shape(packet, issues)
    _reject_private_or_authenticated_facts(packet, issues)
    _reject_raw_references(packet, issues)
    _reject_live_execution_claims(packet, issues)
    _reject_outcome_guarantees(packet, issues)
    _reject_mutation_flags(packet, issues)
    if issues:
        raise TriageValidationError(issues)


def is_valid_source_freshness_drift_triage_v2_packet(packet: Mapping[str, Any]) -> bool:
    """Return True when the packet passes validation."""

    try:
        validate_source_freshness_drift_triage_v2_packet(packet)
    except TriageValidationError:
        return False
    return True


def _validate_packet_shape(packet: Mapping[str, Any], issues: list[TriageValidationIssue]) -> None:
    classifications = packet.get("classifications")
    if not isinstance(classifications, list) or not classifications:
        issues.append(
            TriageValidationIssue(
                "missing_classifications",
                "classifications",
                "packet must include at least one triage classification",
            )
        )
        return

    for index, classification in enumerate(classifications):
        path = f"classifications[{index}]"
        if not isinstance(classification, Mapping):
            issues.append(TriageValidationIssue("invalid_classification", path, "classification must be an object"))
            continue
        if not _has_non_empty_text(classification.get("classification")):
            issues.append(TriageValidationIssue("missing_classification", f"{path}.classification", "classification is required"))
        if not _has_non_empty_sequence(classification.get("citations")) and not _has_non_empty_sequence(
            classification.get("source_evidence_ids")
        ):
            issues.append(
                TriageValidationIssue(
                    "uncited_classification",
                    path,
                    "classification must include citations or source_evidence_ids",
                )
            )
        if not _has_non_empty_sequence(classification.get("affected_artifact_ids")):
            issues.append(
                TriageValidationIssue(
                    "missing_affected_artifact_ids",
                    f"{path}.affected_artifact_ids",
                    "classification must name affected artifact IDs",
                )
            )
        if not _has_non_empty_text(classification.get("escalation_owner")):
            issues.append(
                TriageValidationIssue(
                    "missing_escalation_owner",
                    f"{path}.escalation_owner",
                    "classification must name an escalation owner",
                )
            )


def _reject_private_or_authenticated_facts(packet: Mapping[str, Any], issues: list[TriageValidationIssue]) -> None:
    for path, value in _walk(packet):
        normalized_path = path.lower()
        if isinstance(value, bool) and value and any(
            token in normalized_path for token in ("private_fact", "authenticated_fact", "contains_private", "contains_authenticated")
        ):
            issues.append(TriageValidationIssue("private_or_authenticated_fact", path, "packet must not include private or authenticated facts"))
        if isinstance(value, str):
            normalized_value = value.lower()
            if any(token in normalized_path for token in ("privacy_classification", "auth_scope", "fact_scope")) and any(
                token in normalized_value for token in PRIVATE_FACT_TOKENS
            ):
                issues.append(TriageValidationIssue("private_or_authenticated_fact", path, "packet must use public offline facts only"))


def _reject_raw_references(packet: Mapping[str, Any], issues: list[TriageValidationIssue]) -> None:
    for path, value in _walk(packet):
        normalized_path = path.lower()
        normalized_value = value.lower() if isinstance(value, str) else ""
        if any(token in normalized_path or token in normalized_value for token in RAW_REFERENCE_TOKENS):
            issues.append(TriageValidationIssue("raw_or_downloaded_reference", path, "packet must not reference raw crawl output or downloaded documents"))


def _reject_live_execution_claims(packet: Mapping[str, Any], issues: list[TriageValidationIssue]) -> None:
    for path, value in _walk(packet):
        normalized_path = path.lower()
        if isinstance(value, bool) and value and any(token in normalized_path for token in ("executed", "live_execution", "ran_live")):
            issues.append(TriageValidationIssue("live_execution_claim", path, "packet must not claim live crawler, processor, DevHub, or LLM execution"))
        if isinstance(value, str):
            normalized_value = value.lower()
            if any(token in normalized_value for token in LIVE_EXECUTION_TOKENS):
                issues.append(TriageValidationIssue("live_execution_claim", path, "packet must be fixture/offline evidence only"))


def _reject_outcome_guarantees(packet: Mapping[str, Any], issues: list[TriageValidationIssue]) -> None:
    for path, value in _walk(packet):
        normalized_path = path.lower()
        if isinstance(value, bool) and value and any(token in normalized_path for token in ("guarantee", "guaranteed_outcome")):
            issues.append(TriageValidationIssue("outcome_guarantee", path, "packet must not guarantee legal or permitting outcomes"))
        if isinstance(value, str):
            normalized_value = value.lower()
            if any(token in normalized_value for token in OUTCOME_GUARANTEE_TOKENS):
                issues.append(TriageValidationIssue("outcome_guarantee", path, "packet must not guarantee legal or permitting outcomes"))


def _reject_mutation_flags(packet: Mapping[str, Any], issues: list[TriageValidationIssue]) -> None:
    mutation_flags = packet.get("mutation_flags")
    if _has_non_empty_sequence(mutation_flags) or (isinstance(mutation_flags, Mapping) and bool(mutation_flags)):
        issues.append(TriageValidationIssue("active_mutation_flag", "mutation_flags", "packet must not carry active mutation flags"))

    for path, value in _walk(packet):
        normalized_path = path.lower().replace("-", "_")
        if isinstance(value, bool) and value:
            for area in BLOCKED_MUTATION_AREAS:
                if (
                    f"mutate_{area}" in normalized_path
                    or f"{area}_mutation" in normalized_path
                    or f"update_{area}" in normalized_path
                    or f"active_{area}" in normalized_path
                ):
                    issues.append(TriageValidationIssue("active_mutation_flag", path, "packet must be triage-only and must not mutate active state"))
                    break


def _walk(value: Any, path: str = "$") -> Iterable[tuple[str, Any]]:
    yield path, value
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            yield from _walk(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            child_path = f"{path}[{index}]"
            yield from _walk(child, child_path)


def _has_non_empty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _has_non_empty_sequence(value: Any) -> bool:
    return isinstance(value, list) and any(item for item in value)
