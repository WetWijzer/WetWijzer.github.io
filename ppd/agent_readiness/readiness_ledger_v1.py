"""Validation helpers for PP&D readiness ledger v1.

The ledger validator is intentionally fixture-first and side-effect free. It is
used to reject readiness promotion records that would otherwise imply agent
readiness without source citations, validation references, manual review
blockers, fresh fixture claims, and commit-safe artifact metadata.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping

_STALE_FIXTURE_STATUSES = {"expired", "needs_refresh", "stale", "unknown", "unknown_stale"}
_MUTATION_FLAG_KEYS = {
    "source_mutation_enabled",
    "surface_registry_mutation_enabled",
    "guardrail_mutation_enabled",
    "prompt_mutation_enabled",
    "release_state_mutation_enabled",
    "agent_state_mutation_enabled",
    "mutates_sources",
    "mutates_surface_registry",
    "mutates_guardrails",
    "mutates_prompts",
    "mutates_release_state",
    "mutates_agent_state",
}
_MUTATION_FLAG_VALUES = {
    "active_source_mutation",
    "active_surface_registry_mutation",
    "active_guardrail_mutation",
    "active_prompt_mutation",
    "active_release_state_mutation",
    "active_agent_state_mutation",
    "source",
    "surface_registry",
    "guardrail",
    "prompt",
    "release_state",
    "agent_state",
}
_PRIVATE_KEY_TOKENS = {
    "auth",
    "authorization",
    "bearer",
    "cookie",
    "credential",
    "devhub_private",
    "mfa",
    "password",
    "private_value",
    "secret",
    "session",
    "token",
}
_PRIVATE_VALUE_TOKENS = {
    "authorization:",
    "bearer ",
    "cookie=",
    "devhub-authenticated",
    "private-artifact",
    "session-storage",
    "set-cookie",
}
_RAW_ARTIFACT_KEY_TOKENS = {
    "browser_context",
    "crawl_body",
    "downloaded_pdf",
    "har",
    "html_body",
    "page_content",
    "pdf_bytes",
    "raw_body",
    "raw_crawl",
    "raw_html",
    "raw_pdf",
    "session_storage",
    "screenshot",
    "trace",
}
_RAW_ARTIFACT_VALUE_TOKENS = {
    ".har",
    ".trace",
    "browser-context",
    "crawl/raw",
    "data:application/pdf",
    "raw-crawl",
    "raw-pdf",
    "session-storage",
    "storage-state.json",
    "trace.zip",
}
_GUARANTEE_PHRASES = {
    "approved permit is guaranteed",
    "ensure approval",
    "ensures approval",
    "guarantee approval",
    "guaranteed approval",
    "legal advice",
    "permit approval is guaranteed",
    "permit will be approved",
    "permit will issue",
    "permitting outcome is guaranteed",
    "will be approved",
    "will pass inspection",
}


@dataclass(frozen=True)
class ReadinessLedgerV1ValidationResult:
    """Machine-readable validation result for a readiness ledger v1 payload."""

    ready: bool
    problems: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {"ready": self.ready, "problems": list(self.problems)}


def validate_readiness_ledger_v1(
    ledger: Mapping[str, Any],
    *,
    now: datetime | None = None,
    max_fixture_age_days: int = 45,
) -> ReadinessLedgerV1ValidationResult:
    """Return fail-closed validation for a PP&D readiness ledger v1 payload."""

    check_time = _normalize_now(now)
    problems: list[str] = []

    if str(ledger.get("ledger_version") or "") != "ppd-readiness-ledger-v1":
        problems.append("ledger_version must be ppd-readiness-ledger-v1")

    rows = _rows(ledger)
    if not rows:
        problems.append("readiness ledger v1 must include readiness_rows")
    for index, row in enumerate(rows):
        row_id = _row_id(row, index)
        problems.extend(_row_reference_problems(row, row_id))
        problems.extend(_manual_review_blocker_problems(row, row_id))
        problems.extend(_fixture_claim_problems(row.get("fixture_version_claim"), row_id, check_time, max_fixture_age_days))

    top_level_claims = ledger.get("fixture_version_claims")
    if isinstance(top_level_claims, list):
        for index, claim in enumerate(top_level_claims):
            problems.extend(
                _fixture_claim_problems(claim, f"fixture_version_claims[{index}]", check_time, max_fixture_age_days)
            )

    problems.extend(_privacy_and_raw_artifact_problems(ledger))
    problems.extend(_guarantee_problems(ledger))
    problems.extend(_mutation_flag_problems(ledger))

    return ReadinessLedgerV1ValidationResult(ready=not problems, problems=tuple(problems))


def require_readiness_ledger_v1_ready(
    ledger: Mapping[str, Any],
    *,
    now: datetime | None = None,
    max_fixture_age_days: int = 45,
) -> None:
    """Raise ValueError when a readiness ledger v1 payload is not ready."""

    result = validate_readiness_ledger_v1(ledger, now=now, max_fixture_age_days=max_fixture_age_days)
    if not result.ready:
        raise ValueError("invalid_ppd_readiness_ledger_v1: " + "; ".join(result.problems))


def _rows(ledger: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    raw = ledger.get("readiness_rows") or ledger.get("rows") or []
    if not isinstance(raw, list):
        return []
    return [row for row in raw if isinstance(row, Mapping)]


def _row_reference_problems(row: Mapping[str, Any], row_id: str) -> list[str]:
    problems: list[str] = []
    if not _collect_citations(row):
        problems.append(f"readiness row {row_id} must cite source_evidence_ids or citations")
    if not _has_text(row, "readiness_packet_ref", "packet_ref", "packet_id"):
        problems.append(f"readiness row {row_id} is missing readiness packet reference")
    if not _has_text(row, "validator_ref", "validation_ref", "validator_id"):
        problems.append(f"readiness row {row_id} is missing validator reference")
    return problems


def _manual_review_blocker_problems(row: Mapping[str, Any], row_id: str) -> list[str]:
    blockers = row.get("manual_review_blockers") or row.get("manual_review_blocker_ids")
    if not isinstance(blockers, list) or not blockers:
        return [f"readiness row {row_id} must include manual_review_blockers"]
    if not all(isinstance(blocker, str) and blocker for blocker in blockers):
        return [f"readiness row {row_id} manual_review_blockers must be non-empty strings"]
    return []


def _fixture_claim_problems(claim: Any, row_id: str, now: datetime, max_fixture_age_days: int) -> list[str]:
    if not isinstance(claim, Mapping):
        return [f"{row_id} is missing fixture_version_claim"]

    problems: list[str] = []
    if not _has_text(claim, "fixture_id", "fixture_path"):
        problems.append(f"{row_id} fixture_version_claim is missing fixture_id or fixture_path")
    if not _has_text(claim, "fixture_version", "version"):
        problems.append(f"{row_id} fixture_version_claim is missing fixture_version")

    status = str(claim.get("freshness_status") or claim.get("status") or "current").lower()
    if status in _STALE_FIXTURE_STATUSES:
        problems.append(f"{row_id} fixture_version_claim is stale: freshness_status={status}")

    verified_at = _parse_datetime(claim.get("last_verified_at") or claim.get("verified_at") or claim.get("updated_at"))
    if verified_at is None:
        problems.append(f"{row_id} fixture_version_claim is missing last_verified_at")
    elif (now - verified_at).days > max_fixture_age_days:
        problems.append(f"{row_id} fixture_version_claim is stale at {(now - verified_at).days} days old")
    return problems


def _privacy_and_raw_artifact_problems(value: Any, path: str = "$") -> list[str]:
    problems: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key).lower()
            child_path = f"{path}.{key}"
            if any(token in key_text for token in _PRIVATE_KEY_TOKENS):
                problems.append(f"private or authenticated artifact field is not allowed at {child_path}")
            if any(token in key_text for token in _RAW_ARTIFACT_KEY_TOKENS):
                problems.append(f"raw crawl, PDF, session, or browser artifact field is not allowed at {child_path}")
            problems.extend(_privacy_and_raw_artifact_problems(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            problems.extend(_privacy_and_raw_artifact_problems(child, f"{path}[{index}]"))
    elif isinstance(value, str):
        normalized = value.lower()
        if any(token in normalized for token in _PRIVATE_VALUE_TOKENS):
            problems.append(f"private or authenticated artifact reference is not allowed at {path}")
        if any(token in normalized for token in _RAW_ARTIFACT_VALUE_TOKENS):
            problems.append(f"raw crawl, PDF, session, or browser artifact reference is not allowed at {path}")
    return problems


def _guarantee_problems(value: Any, path: str = "$") -> list[str]:
    problems: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            problems.extend(_guarantee_problems(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            problems.extend(_guarantee_problems(child, f"{path}[{index}]"))
    elif isinstance(value, str):
        normalized = " ".join(value.lower().split())
        if any(phrase in normalized for phrase in _GUARANTEE_PHRASES):
            problems.append(f"legal or permitting outcome guarantee is not allowed at {path}")
    return problems


def _mutation_flag_problems(value: Any, path: str = "$") -> list[str]:
    problems: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key).lower()
            child_path = f"{path}.{key}"
            if key_text in _MUTATION_FLAG_KEYS and child is True:
                problems.append(f"active mutation flag is not allowed at {child_path}")
            if key_text in {"active_mutation_flags", "mutation_flags"} and _non_empty_list(child):
                problems.append(f"active mutation flags are not allowed at {child_path}")
            problems.extend(_mutation_flag_problems(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            problems.extend(_mutation_flag_problems(child, f"{path}[{index}]"))
    elif isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in _MUTATION_FLAG_VALUES:
            problems.append(f"active mutation flag is not allowed at {path}")
    return problems


def _collect_citations(value: Any) -> set[str]:
    citations: set[str] = set()
    if isinstance(value, Mapping):
        for key in ("source_evidence_ids", "citations", "citation_ids"):
            raw = value.get(key)
            if isinstance(raw, list):
                citations.update(item for item in raw if isinstance(item, str) and item)
        raw_one = value.get("source_evidence_id") or value.get("citation_id")
        if isinstance(raw_one, str) and raw_one:
            citations.add(raw_one)
    return citations


def _has_text(value: Mapping[str, Any], *keys: str) -> bool:
    return any(isinstance(value.get(key), str) and bool(value.get(key)) for key in keys)


def _row_id(row: Mapping[str, Any], index: int) -> str:
    raw = row.get("row_id") or row.get("readiness_id")
    if isinstance(raw, str) and raw:
        return raw
    return f"index-{index}"


def _non_empty_list(value: Any) -> bool:
    return isinstance(value, list) and len(value) > 0


def _normalize_now(now: datetime | None) -> datetime:
    if now is None:
        return datetime.now(timezone.utc)
    if now.tzinfo is None:
        return now.replace(tzinfo=timezone.utc)
    return now.astimezone(timezone.utc)


def _parse_datetime(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)
