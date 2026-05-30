"""Validation for attended review disposition summary v3 artifacts."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

_ALLOWED_DISPOSITIONS = {"accept", "defer", "reject"}
_MUTATION_FLAG_NAMES = {
    "active_source_mutation",
    "source_mutation",
    "surface_registry_mutation",
    "guardrail_mutation",
    "prompt_mutation",
    "monitoring_mutation",
    "release_state_mutation",
    "agent_state_mutation",
    "mutates_active_source",
    "mutates_surface_registry",
    "mutates_guardrails",
    "mutates_prompts",
    "mutates_monitoring",
    "mutates_release_state",
    "mutates_agent_state",
}
_PRIVATE_FACT_PATTERNS = (
    re.compile(r"\b(authenticated|logged[- ]?in|private|non[- ]?public|session[- ]?only)\b", re.I),
    re.compile(r"\b(cookie|bearer token|authorization header|csrf|mfa|captcha)\b", re.I),
)
_RAW_ARTIFACT_PATTERNS = (
    re.compile(r"\b(raw crawl|crawl dump|browser trace|session trace|playwright trace)\b", re.I),
    re.compile(r"\b(downloaded pdf|raw pdf|pdf artifact|har file|\.har\b|\.zip\b)\b", re.I),
)
_LIVE_EXECUTION_PATTERNS = (
    re.compile(r"\b(live execution|executed live|ran against production|submitted|uploaded|certified|paid)\b", re.I),
)
_LEGAL_GUARANTEE_PATTERNS = (
    re.compile(r"\b(guarantee[sd]?|ensure[sd]?|will be approved|permit approval|legal outcome)\b", re.I),
)
_CONSEQUENTIAL_ACTION_PATTERNS = (
    re.compile(r"\b(file the permit|submit the application|pay the fee|cancel the permit|certify compliance)\b", re.I),
)
_TASK_REF_RE = re.compile(r"\b(?:task|ticket|issue|follow[- ]?up)[:# -]*[A-Za-z0-9_.-]+\b", re.I)


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str
    row: int | None = None

    def as_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {"code": self.code, "message": self.message}
        if self.row is not None:
            result["row"] = self.row
        return result


def validate_attended_review_disposition_summary_v3(summary: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Return validation issues for an attended review disposition summary v3."""
    issues: list[ValidationIssue] = []

    rows = _rows(summary)
    if not rows:
        issues.append(ValidationIssue("missing_disposition_rows", "summary must include at least one disposition row"))

    for index, row in enumerate(rows):
        row_number = index + 1
        disposition = _text(row.get("disposition") or row.get("decision")).lower()
        if disposition not in _ALLOWED_DISPOSITIONS:
            issues.append(ValidationIssue("invalid_disposition", "row disposition must be accept, defer, or reject", row_number))

        if not _has_citation(row):
            issues.append(ValidationIssue("uncited_disposition_row", "row must cite the reviewed source or evidence", row_number))

        if not _text(row.get("rationale") or row.get(f"{disposition}_rationale")):
            issues.append(ValidationIssue("missing_disposition_rationale", "row must include accept/defer/reject rationale", row_number))

        owners = row.get("reviewer_owners") or row.get("reviewers") or row.get("owners")
        if not _has_nonempty_sequence_or_text(owners):
            issues.append(ValidationIssue("missing_reviewer_owners", "row must identify reviewer owners", row_number))

        if disposition == "defer" and not _has_follow_up_reference(row):
            issues.append(ValidationIssue("unresolved_deferral_without_follow_up", "deferred rows must reference a follow-up task", row_number))

        row_text = _flatten_text(row)
        issues.extend(_prohibited_text_issues(row_text, row_number))
        issues.extend(_mutation_flag_issues(row, row_number))

    if not _has_rollback_verification(summary):
        issues.append(ValidationIssue("missing_rollback_verification", "summary must include rollback verification"))

    summary_text = _flatten_text({key: value for key, value in summary.items() if key not in {"rows", "disposition_rows", "dispositions"}})
    issues.extend(_prohibited_text_issues(summary_text, None))
    issues.extend(_mutation_flag_issues(summary, None))

    return [issue.as_dict() for issue in issues]


def assert_attended_review_disposition_summary_v3(summary: Mapping[str, Any]) -> None:
    issues = validate_attended_review_disposition_summary_v3(summary)
    if issues:
        codes = ", ".join(issue["code"] for issue in issues)
        raise ValueError(f"invalid attended review disposition summary v3: {codes}")


def _rows(summary: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    value = summary.get("rows") or summary.get("disposition_rows") or summary.get("dispositions")
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [row for row in value if isinstance(row, Mapping)]


def _has_citation(row: Mapping[str, Any]) -> bool:
    citation = row.get("citation") or row.get("citations") or row.get("source_citation") or row.get("evidence")
    return _has_nonempty_sequence_or_text(citation)


def _has_follow_up_reference(row: Mapping[str, Any]) -> bool:
    value = row.get("follow_up_task") or row.get("follow_up") or row.get("task_reference") or row.get("deferral_reference")
    return _has_nonempty_sequence_or_text(value) and bool(_TASK_REF_RE.search(_flatten_text(value)))


def _has_rollback_verification(summary: Mapping[str, Any]) -> bool:
    value = summary.get("rollback_verification") or summary.get("rollback") or summary.get("rollback_verified")
    if isinstance(value, bool):
        return value
    if isinstance(value, Mapping):
        verified = value.get("verified")
        evidence = value.get("evidence") or value.get("citation") or value.get("checked_by")
        return verified is True and _has_nonempty_sequence_or_text(evidence)
    return _has_nonempty_sequence_or_text(value)


def _mutation_flag_issues(value: Any, row: int | None) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if isinstance(value, Mapping):
        for key, item in value.items():
            normalized = str(key).strip().lower().replace("-", "_").replace(" ", "_")
            if normalized in _MUTATION_FLAG_NAMES and bool(item):
                issues.append(ValidationIssue("mutation_flag_present", f"mutation flag is not allowed: {key}", row))
            issues.extend(_mutation_flag_issues(item, row))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for item in value:
            issues.extend(_mutation_flag_issues(item, row))
    return issues


def _prohibited_text_issues(text: str, row: int | None) -> list[ValidationIssue]:
    checks = (
        ("private_or_authenticated_fact", _PRIVATE_FACT_PATTERNS, "private or authenticated facts are not allowed"),
        ("raw_artifact_reference", _RAW_ARTIFACT_PATTERNS, "raw crawl/PDF/session/browser artifacts are not allowed"),
        ("live_execution_claim", _LIVE_EXECUTION_PATTERNS, "live execution claims are not allowed"),
        ("legal_or_permitting_guarantee", _LEGAL_GUARANTEE_PATTERNS, "legal or permitting outcome guarantees are not allowed"),
        ("consequential_action_language", _CONSEQUENTIAL_ACTION_PATTERNS, "consequential action language is not allowed"),
    )
    issues: list[ValidationIssue] = []
    for code, patterns, message in checks:
        if any(pattern.search(text) for pattern in patterns):
            issues.append(ValidationIssue(code, message, row))
    return issues


def _has_nonempty_sequence_or_text(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, Mapping):
        return any(_has_nonempty_sequence_or_text(item) for item in value.values())
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return any(_has_nonempty_sequence_or_text(item) for item in value)
    return value is not None


def _flatten_text(value: Any) -> str:
    if isinstance(value, Mapping):
        return " ".join(_flatten_text(item) for item in value.values())
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return " ".join(_flatten_text(item) for item in value)
    return _text(value)


def _text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()
