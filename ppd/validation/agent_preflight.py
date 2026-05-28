"""Agent preflight decision-matrix validation.

The validator is intentionally small and deterministic so it can run in tests,
self-checks, and daemon preflight paths without live network access.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Any, Mapping, Sequence

STALE_PROCESS_EVIDENCE_DAYS = 30


@dataclass(frozen=True)
class PreflightIssue:
    """A single preflight validation failure."""

    code: str
    message: str


@dataclass(frozen=True)
class PreflightValidationResult:
    """Validation result for an agent preflight decision matrix."""

    accepted: bool
    issues: tuple[PreflightIssue, ...]

    def raise_for_issues(self) -> None:
        if self.issues:
            details = "; ".join(issue.code for issue in self.issues)
            raise ValueError(f"agent preflight decision matrix rejected: {details}")


def validate_agent_preflight_decision_matrix(
    matrix: Mapping[str, Any],
    *,
    today: date | None = None,
    max_evidence_age_days: int = STALE_PROCESS_EVIDENCE_DAYS,
) -> PreflightValidationResult:
    """Validate that a decision matrix includes required PP&D safety gates."""

    current_date = today or datetime.now(timezone.utc).date()
    issues: list[PreflightIssue] = []

    recommendations = _as_sequence(matrix.get("recommendations"))
    for index, recommendation in enumerate(recommendations):
        if not isinstance(recommendation, Mapping):
            issues.append(_issue("invalid_recommendation", f"recommendation {index} must be an object"))
            continue
        if not _has_citation(recommendation):
            issues.append(
                _issue(
                    "uncited_recommendation",
                    f"recommendation {index} must include at least one public citation",
                )
            )

    evidence_items = _as_sequence(matrix.get("process_evidence"))
    for index, evidence in enumerate(evidence_items):
        if not isinstance(evidence, Mapping):
            issues.append(_issue("invalid_process_evidence", f"process evidence {index} must be an object"))
            continue
        observed_on = _parse_date(evidence.get("observed_on") or evidence.get("date"))
        if observed_on is None:
            issues.append(
                _issue(
                    "missing_process_evidence_date",
                    f"process evidence {index} must include observed_on as YYYY-MM-DD",
                )
            )
            continue
        if (current_date - observed_on).days > max_evidence_age_days:
            issues.append(
                _issue(
                    "stale_process_evidence",
                    f"process evidence {index} is older than {max_evidence_age_days} days",
                )
            )

    human_review = matrix.get("human_review")
    if not isinstance(human_review, Mapping) or human_review.get("required") is not True:
        issues.append(
            _issue(
                "missing_human_review_gate",
                "matrix must require human review before consequential or filing activity",
            )
        )

    artifacts = _as_sequence(matrix.get("artifacts"))
    for index, artifact in enumerate(artifacts):
        if not isinstance(artifact, Mapping):
            issues.append(_issue("invalid_artifact", f"artifact {index} must be an object"))
            continue
        if _is_private_artifact(artifact):
            issues.append(
                _issue(
                    "private_artifact",
                    f"artifact {index} must not reference private sessions, auth state, traces, or raw downloads",
                )
            )

    actions = _as_sequence(matrix.get("actions"))
    for index, action in enumerate(actions):
        if not isinstance(action, Mapping):
            issues.append(_issue("invalid_action", f"action {index} must be an object"))
            continue
        consequential = bool(action.get("consequential") or action.get("requires_human_confirmation"))
        if consequential and action.get("confirmation") != "exact":
            issues.append(
                _issue(
                    "missing_exact_confirmation",
                    f"consequential action {index} must require exact confirmation",
                )
            )
        financial = bool(action.get("financial") or action.get("payment") or action.get("fee"))
        if financial and action.get("classification") != "manual_handoff":
            issues.append(
                _issue(
                    "financial_action_without_manual_handoff",
                    f"financial action {index} must be classified as manual_handoff",
                )
            )

    return PreflightValidationResult(accepted=not issues, issues=tuple(issues))


def _issue(code: str, message: str) -> PreflightIssue:
    return PreflightIssue(code=code, message=message)


def _as_sequence(value: Any) -> Sequence[Any]:
    if value is None:
        return ()
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return value
    return (value,)


def _has_citation(recommendation: Mapping[str, Any]) -> bool:
    citations = recommendation.get("citations") or recommendation.get("sources")
    for citation in _as_sequence(citations):
        if isinstance(citation, Mapping):
            url = str(citation.get("url") or "")
            if url.startswith("http://") or url.startswith("https://"):
                return True
        elif isinstance(citation, str) and citation.startswith(("http://", "https://")):
            return True
    return False


def _parse_date(value: Any) -> date | None:
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    if not isinstance(value, str):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _is_private_artifact(artifact: Mapping[str, Any]) -> bool:
    visibility = str(artifact.get("visibility") or artifact.get("scope") or "").lower()
    if visibility in {"private", "secret", "auth", "session"}:
        return True
    path = str(artifact.get("path") or artifact.get("uri") or artifact.get("url") or "").lower()
    private_markers = (
        ".daemon/",
        "auth",
        "session",
        "trace",
        "raw_crawl",
        "raw-crawl",
        "downloaded_documents",
        "downloaded-documents",
    )
    return any(marker in path for marker in private_markers)
