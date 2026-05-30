"""Validation for PP&D process model impact proposal v1 packets.

The validator is intentionally side-effect free. It accepts an already-loaded
mapping and returns deterministic findings that callers can use before a
proposal is promoted into any review or implementation workflow.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Iterable, Mapping, Sequence


@dataclass(frozen=True)
class ProposalValidationFinding:
    """A single process model impact proposal validation finding."""

    code: str
    message: str
    path: str


@dataclass(frozen=True)
class ProposalValidationResult:
    """Deterministic validation result for a proposal packet."""

    ok: bool
    findings: tuple[ProposalValidationFinding, ...]


_BLOCKED_ARTIFACT_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("private_artifact", re.compile(r"\b(private|account|customer|applicant|case[-_ ]?specific)\b", re.IGNORECASE)),
    ("authenticated_artifact", re.compile(r"\b(authenticated|auth|login|signed[-_ ]?in|devhub[-_ ]?home)\b", re.IGNORECASE)),
    ("session_artifact", re.compile(r"\b(session|cookie|storage[-_ ]?state|local[-_ ]?storage|token|credential|password)\b", re.IGNORECASE)),
    ("browser_artifact", re.compile(r"\b(trace|har|screenshot|video|playwright|browser[-_ ]?state|cdp)\b", re.IGNORECASE)),
    ("raw_crawl_artifact", re.compile(r"\b(raw[-_ ]?(crawl|html|body|response|capture)|warc|downloaded[-_ ]?(data|document)|pdf[-_ ]?download|raw[-_ ]?pdf)\b", re.IGNORECASE)),
)

_GUARANTEE_PATTERN = re.compile(
    r"\b(guarantee[sd]?|assure[sd]?|ensure[sd]?|will be approved|will receive|"
    r"approval guaranteed|permit guaranteed|issuance guaranteed|legal compliance guaranteed|"
    r"legally compliant|no legal risk|definitely qualifies)\b",
    re.IGNORECASE,
)

_CONSEQUENTIAL_ACTION_PATTERN = re.compile(
    r"\b("
    r"submit|certify|attest|acknowledge|upload corrections?|upload to official record|"
    r"pay|enter payment|purchase|schedule inspection|cancel|withdraw|request extension|"
    r"reactivate|create account|reset password|complete mfa|solve captcha|finalize"
    r")\b",
    re.IGNORECASE,
)

_MUTATION_FLAG_NAMES = frozenset(
    {
        "source",
        "document",
        "requirement",
        "process",
        "guardrail",
        "prompt",
        "release_state",
        "agent_state",
    }
)


class ProcessModelImpactProposalValidationError(ValueError):
    """Raised by ``assert_valid_process_model_impact_proposal_v1``."""

    def __init__(self, result: ProposalValidationResult) -> None:
        self.result = result
        details = "; ".join(f"{finding.path}: {finding.code}" for finding in result.findings)
        super().__init__(details or "invalid process model impact proposal v1")


def validate_process_model_impact_proposal_v1(proposal: Mapping[str, Any]) -> ProposalValidationResult:
    """Validate a process model impact proposal v1 packet.

    Required top-level review gates:
    - ``impact_rows``: each row must be cited and name affected process and requirement IDs.
    - ``dependency_order``: non-empty ordered dependency list.
    - ``reviewer_owner`` and ``rollback_note``: non-empty human review and rollback metadata.

    Safety gates reject private/authenticated/session/browser artifacts, raw crawl or
    downloaded data references, legal or permitting outcome guarantees,
    consequential action execution language, and active mutation flags for PP&D
    source, document, requirement, process, guardrail, prompt, release-state, or
    agent-state assets.
    """

    findings: list[ProposalValidationFinding] = []

    if not isinstance(proposal, Mapping):
        findings.append(ProposalValidationFinding("proposal_not_mapping", "Proposal must be a mapping.", "$"))
        return ProposalValidationResult(ok=False, findings=tuple(findings))

    impact_rows = proposal.get("impact_rows")
    if not isinstance(impact_rows, Sequence) or isinstance(impact_rows, (str, bytes)) or not impact_rows:
        findings.append(
            ProposalValidationFinding(
                "missing_impact_rows",
                "Proposal must include at least one impact row.",
                "$.impact_rows",
            )
        )
    else:
        for index, row in enumerate(impact_rows):
            row_path = f"$.impact_rows[{index}]"
            if not isinstance(row, Mapping):
                findings.append(ProposalValidationFinding("impact_row_not_mapping", "Impact row must be a mapping.", row_path))
                continue
            if not _non_empty_list(row, "citations", "source_evidence_ids"):
                findings.append(
                    ProposalValidationFinding(
                        "uncited_impact_row",
                        "Impact row must include at least one citation or source evidence ID.",
                        row_path,
                    )
                )
            if not _non_empty_list(row, "affected_process_ids", "affected_processes", "process_ids"):
                findings.append(
                    ProposalValidationFinding(
                        "missing_affected_process_ids",
                        "Impact row must name affected process IDs.",
                        row_path,
                    )
                )
            if not _non_empty_list(row, "affected_requirement_ids", "affected_requirements", "requirement_ids"):
                findings.append(
                    ProposalValidationFinding(
                        "missing_affected_requirement_ids",
                        "Impact row must name affected requirement IDs.",
                        row_path,
                    )
                )

    if not _non_empty_list(proposal, "dependency_order", "dependencies"):
        findings.append(
            ProposalValidationFinding(
                "missing_dependency_order",
                "Proposal must include a non-empty dependency order.",
                "$.dependency_order",
            )
        )

    if not _non_empty_text(proposal.get("reviewer_owner")):
        findings.append(
            ProposalValidationFinding(
                "missing_reviewer_owner",
                "Proposal must include a reviewer owner.",
                "$.reviewer_owner",
            )
        )

    if not _non_empty_text(proposal.get("rollback_note")):
        findings.append(
            ProposalValidationFinding(
                "missing_rollback_note",
                "Proposal must include a rollback note.",
                "$.rollback_note",
            )
        )

    _find_blocked_artifacts(proposal, "$", findings)
    _find_blocked_text(proposal, "$", findings)
    _find_active_mutation_flags(proposal, findings)

    return ProposalValidationResult(ok=not findings, findings=tuple(findings))


def assert_valid_process_model_impact_proposal_v1(proposal: Mapping[str, Any]) -> None:
    """Raise when ``proposal`` fails process model impact proposal v1 validation."""

    result = validate_process_model_impact_proposal_v1(proposal)
    if not result.ok:
        raise ProcessModelImpactProposalValidationError(result)


def finding_codes(result: ProposalValidationResult) -> tuple[str, ...]:
    """Return finding codes in deterministic order for tests and callers."""

    return tuple(finding.code for finding in result.findings)


def _non_empty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _non_empty_list(mapping: Mapping[str, Any], *keys: str) -> bool:
    for key in keys:
        value = mapping.get(key)
        if isinstance(value, Sequence) and not isinstance(value, (str, bytes)) and len(value) > 0:
            return True
    return False


def _iter_text_leaves(value: Any, path: str) -> Iterable[tuple[str, str]]:
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, Mapping):
        for key, child in value.items():
            yield from _iter_text_leaves(child, f"{path}.{key}")
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child in enumerate(value):
            yield from _iter_text_leaves(child, f"{path}[{index}]")


def _find_blocked_artifacts(value: Any, path: str, findings: list[ProposalValidationFinding]) -> None:
    for text_path, text in _iter_text_leaves(value, path):
        for code, pattern in _BLOCKED_ARTIFACT_PATTERNS:
            if pattern.search(text):
                findings.append(
                    ProposalValidationFinding(
                        code,
                        "Proposal must not reference private, authenticated, session, browser, raw crawl, PDF, or downloaded artifacts.",
                        text_path,
                    )
                )
                break


def _find_blocked_text(value: Any, path: str, findings: list[ProposalValidationFinding]) -> None:
    for text_path, text in _iter_text_leaves(value, path):
        if _GUARANTEE_PATTERN.search(text):
            findings.append(
                ProposalValidationFinding(
                    "outcome_guarantee",
                    "Proposal must not guarantee legal, permitting, approval, issuance, or risk outcomes.",
                    text_path,
                )
            )
        if _CONSEQUENTIAL_ACTION_PATTERN.search(text):
            findings.append(
                ProposalValidationFinding(
                    "consequential_action_execution_language",
                    "Proposal must not direct execution of consequential official, financial, account, upload, scheduling, cancellation, or certification actions.",
                    text_path,
                )
            )


def _find_active_mutation_flags(proposal: Mapping[str, Any], findings: list[ProposalValidationFinding]) -> None:
    mutation_flags = proposal.get("mutation_flags", {})
    if mutation_flags is None:
        return
    if not isinstance(mutation_flags, Mapping):
        findings.append(
            ProposalValidationFinding(
                "mutation_flags_not_mapping",
                "Mutation flags must be a mapping when present.",
                "$.mutation_flags",
            )
        )
        return

    for raw_name, raw_value in mutation_flags.items():
        name = str(raw_name).strip().lower().replace("-", "_")
        normalized_name = name.removesuffix("_mutation").removeprefix("active_")
        is_blocked_name = normalized_name in _MUTATION_FLAG_NAMES
        is_active = raw_value is True or (isinstance(raw_value, str) and raw_value.strip().lower() in {"true", "active", "yes", "1"})
        if is_blocked_name and is_active:
            findings.append(
                ProposalValidationFinding(
                    "active_mutation_flag",
                    "Proposal must not carry active source, document, requirement, process, guardrail, prompt, release-state, or agent-state mutation flags.",
                    f"$.mutation_flags.{raw_name}",
                )
            )
