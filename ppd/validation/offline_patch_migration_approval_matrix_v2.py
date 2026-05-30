"""Validation for offline patch migration approval matrix v2.

The validator is intentionally data-shape tolerant because supervisor outputs and
fixtures may use either a top-level mapping with rows or a direct list of rows.
It returns structured errors and performs no IO, network access, live execution,
or repository mutation.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Iterable, Mapping, Sequence


_DECISIONS = frozenset({"approve", "defer", "reject"})
_MUTATION_AREAS = (
    "source",
    "surface_registry",
    "surface-registry",
    "guardrail",
    "prompt",
    "monitoring",
    "release_state",
    "release-state",
    "agent_state",
    "agent-state",
)
_ARTIFACT_PATTERNS = (
    re.compile(r"\braw\s+(?:crawl|pdf|browser|session)\b", re.IGNORECASE),
    re.compile(r"\b(?:trace|har|screenshot|auth(?:enticated)?\s+state|cookie|session\s+state)\b", re.IGNORECASE),
    re.compile(r"\b(?:downloaded\s+document|raw\s+download|browser\s+artifact)\b", re.IGNORECASE),
)
_PRIVATE_FACT_PATTERNS = (
    re.compile(r"\bprivate\b", re.IGNORECASE),
    re.compile(r"\bauthenticated\b", re.IGNORECASE),
    re.compile(r"\bcredentials?\b", re.IGNORECASE),
    re.compile(r"\bpassword\b", re.IGNORECASE),
    re.compile(r"\btoken\b", re.IGNORECASE),
    re.compile(r"\bpayment\s+(?:detail|card|method)s?\b", re.IGNORECASE),
)
_LIVE_CLAIM_PATTERNS = (
    re.compile(r"\b(?:executed|ran|promoted|deployed|published|released)\s+(?:live|in\s+production|to\s+production)\b", re.IGNORECASE),
    re.compile(r"\blive\s+(?:crawl|execution|promotion|deployment|release)\b", re.IGNORECASE),
    re.compile(r"\bproduction\s+(?:promotion|deployment|release)\b", re.IGNORECASE),
)
_GUARANTEE_PATTERNS = (
    re.compile(r"\bguarantee(?:d|s)?\b.*\b(?:approval|permit|issuance|legal|compliance|outcome)\b", re.IGNORECASE),
    re.compile(r"\b(?:approval|permit|issuance|legal|compliance|outcome)\b.*\bguarantee(?:d|s)?\b", re.IGNORECASE),
    re.compile(r"\bwill\s+(?:be\s+)?(?:approved|issued|legal|permitted|accepted)\b", re.IGNORECASE),
)
_CONSEQUENTIAL_ACTION_PATTERNS = (
    re.compile(r"\b(?:submit|certify|upload|schedule|cancel|withdraw|pay|purchase|execute|promote)\b", re.IGNORECASE),
    re.compile(r"\b(?:final\s+payment|official\s+record|official\s+action)\b", re.IGNORECASE),
)
_TASK_REF_PATTERN = re.compile(r"\b(?:task|supervisor)-\d{8}-\d+\b|\bcheckbox-\d+\b", re.IGNORECASE)
_CITATION_KEYS = ("citations", "citation_ids", "source_evidence_ids", "evidence", "source_refs")
_OWNER_KEYS = ("reviewer_owner", "reviewer_owners", "owner", "owners")
_RATIONALE_KEYS = ("rationale", "approve_rationale", "defer_rationale", "reject_rationale")


@dataclass(frozen=True)
class MatrixValidationError:
    """One deterministic matrix validation failure."""

    code: str
    message: str
    row: int | None = None


@dataclass(frozen=True)
class MatrixValidationResult:
    """Validation result for an approval matrix."""

    ok: bool
    errors: tuple[MatrixValidationError, ...]

    def codes(self) -> tuple[str, ...]:
        return tuple(error.code for error in self.errors)


def validate_offline_patch_migration_approval_matrix_v2(matrix: Any) -> MatrixValidationResult:
    """Validate an offline patch migration approval matrix v2 payload."""

    errors: list[MatrixValidationError] = []
    rows = _approval_rows(matrix)

    if not rows:
        errors.append(MatrixValidationError("approval_rows_missing", "approval matrix v2 must contain approval rows"))

    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            errors.append(MatrixValidationError("approval_row_not_object", "approval row must be an object", index))
            continue

        decision = str(row.get("decision", "")).strip().lower()
        row_text = _stringify(row)

        if decision not in _DECISIONS:
            errors.append(MatrixValidationError("decision_missing", "approval row must choose approve, defer, or reject", index))

        if not _has_nonempty_any(row, _CITATION_KEYS):
            errors.append(MatrixValidationError("uncited_approval_row", "approval row must cite source evidence", index))

        if not _has_nonempty_any(row, _RATIONALE_KEYS):
            errors.append(MatrixValidationError("rationale_missing", "approval row must include approve/defer/reject rationale", index))

        if not _has_nonempty_any(row, _OWNER_KEYS):
            errors.append(MatrixValidationError("reviewer_owner_missing", "approval row must name reviewer owner", index))

        blockers = _as_sequence(row.get("blockers") or row.get("unresolved_blockers"))
        for blocker in blockers:
            if _is_unresolved_blocker(blocker) and not _has_follow_up_task_ref(blocker):
                errors.append(MatrixValidationError("unresolved_blocker_missing_follow_up_task", "unresolved blocker must include follow-up task reference", index))

        rollback = row.get("rollback_verification") or row.get("rollback") or row.get("rollback_verified")
        if not _rollback_verified(rollback):
            errors.append(MatrixValidationError("rollback_verification_missing", "approval row must include rollback verification", index))

        if _matches_any(row_text, _PRIVATE_FACT_PATTERNS):
            errors.append(MatrixValidationError("private_or_authenticated_fact", "approval row must not include private or authenticated facts", index))

        if _matches_any(row_text, _ARTIFACT_PATTERNS):
            errors.append(MatrixValidationError("raw_or_browser_artifact", "approval row must not include raw crawl, PDF, session, or browser artifacts", index))

        if _matches_any(row_text, _LIVE_CLAIM_PATTERNS):
            errors.append(MatrixValidationError("live_execution_or_promotion_claim", "approval row must not claim live execution or promotion", index))

        if _matches_any(row_text, _GUARANTEE_PATTERNS):
            errors.append(MatrixValidationError("legal_or_permitting_guarantee", "approval row must not guarantee legal or permitting outcomes", index))

        if _matches_any(row_text, _CONSEQUENTIAL_ACTION_PATTERNS):
            errors.append(MatrixValidationError("consequential_action_language", "approval row must not contain consequential action language", index))

        if _has_active_mutation_flag(row):
            errors.append(MatrixValidationError("active_mutation_flag", "approval row must not set active source, surface-registry, guardrail, prompt, monitoring, release-state, or agent-state mutation flags", index))

    return MatrixValidationResult(ok=not errors, errors=tuple(errors))


def _approval_rows(matrix: Any) -> list[Any]:
    if isinstance(matrix, Sequence) and not isinstance(matrix, (str, bytes, bytearray)):
        return list(matrix)
    if not isinstance(matrix, Mapping):
        return []
    for key in ("approval_rows", "approvals", "rows", "matrix"):
        value = matrix.get(key)
        if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
            return list(value)
    return []


def _has_nonempty_any(row: Mapping[str, Any], keys: Iterable[str]) -> bool:
    return any(_is_nonempty(row.get(key)) for key in keys)


def _is_nonempty(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, Mapping):
        return any(_is_nonempty(item) for item in value.values())
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        return any(_is_nonempty(item) for item in value)
    return bool(value)


def _as_sequence(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return list(value)
    return [value]


def _is_unresolved_blocker(blocker: Any) -> bool:
    if isinstance(blocker, Mapping):
        status = str(blocker.get("status", "")).strip().lower()
        resolved = blocker.get("resolved")
        if resolved is False or status in {"open", "unresolved", "blocked", "pending"}:
            return True
        return bool(blocker) and status not in {"resolved", "closed"}
    return bool(str(blocker).strip())


def _has_follow_up_task_ref(blocker: Any) -> bool:
    if isinstance(blocker, Mapping):
        for key in ("follow_up_task", "follow_up_task_ref", "task_ref", "task", "reference"):
            if _TASK_REF_PATTERN.search(str(blocker.get(key, ""))):
                return True
    return bool(_TASK_REF_PATTERN.search(_stringify(blocker)))


def _rollback_verified(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, Mapping):
        verified = value.get("verified")
        evidence = value.get("evidence") or value.get("citation") or value.get("checked_at")
        return verified is True and _is_nonempty(evidence)
    if isinstance(value, str):
        text = value.strip().lower()
        return bool(text) and text not in {"missing", "none", "false", "no", "unverified"}
    return False


def _has_active_mutation_flag(row: Mapping[str, Any]) -> bool:
    candidates = [row]
    flags = row.get("mutation_flags")
    if isinstance(flags, Mapping):
        candidates.append(flags)
    for candidate in candidates:
        for key, value in candidate.items():
            normalized_key = str(key).strip().lower().replace(" ", "_")
            if any(area in normalized_key for area in _MUTATION_AREAS) and _truthy_mutation_value(value):
                return True
    return False


def _truthy_mutation_value(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"active", "true", "yes", "mutate", "mutation", "write", "enabled"}
    return False


def _matches_any(text: str, patterns: Iterable[re.Pattern[str]]) -> bool:
    return any(pattern.search(text) for pattern in patterns)


def _stringify(value: Any) -> str:
    if isinstance(value, Mapping):
        return " ".join(f"{key} {_stringify(item)}" for key, item in sorted(value.items(), key=lambda pair: str(pair[0])))
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return " ".join(_stringify(item) for item in value)
    return str(value)
