"""Validation for inactive fixture promotion diff ledger v1 artifacts.

The ledger is intentionally evidence-only. It may describe fixture diffs and
readiness evidence, but it must not claim live execution, promote active state,
or preserve private/raw browser or crawl artifacts.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence


SCHEMA_VERSION = "inactive-fixture-promotion-diff-ledger-v1"

_PRIVATE_ARTIFACT_TERMS = (
    "auth",
    "authenticated",
    "cookie",
    "cookies",
    "credential",
    "credentials",
    "devhub-session",
    "har",
    "localstorage",
    "mfa",
    "password",
    "playwright-report",
    "private-devhub",
    "session",
    "screenshot",
    "storage_state",
    "trace",
    "video.webm",
)

_RAW_ARTIFACT_TERMS = (
    "downloaded",
    "downloaded-data",
    "pdf-bytes",
    "raw-crawl",
    "raw-crawl-output",
    "raw-download",
    "raw-html",
    "raw-pdf",
    "response-body",
    "warc",
)

_LIVE_CLAIM_TERMS = (
    "applied promotion",
    "executed live",
    "live crawl completed",
    "live execution",
    "promoted fixtures",
    "promotion completed",
    "ran browser",
    "submitted to devhub",
)

_GUARANTEE_TERMS = (
    "approval is guaranteed",
    "guaranteed approval",
    "guaranteed permit",
    "legal advice",
    "legally sufficient",
    "permit will be approved",
    "will pass inspection",
)

_CONSEQUENTIAL_TERMS = (
    "cancel inspection",
    "certify acknowledgement",
    "certify application",
    "make payment",
    "pay fee",
    "purchase permit",
    "schedule inspection",
    "submit application",
    "submit permit",
    "upload correction",
    "withdraw permit",
)

_MUTATION_FLAG_TERMS = (
    "active_agent_state_mutation",
    "active_fixture_mutation",
    "active_guardrail_mutation",
    "active_process_mutation",
    "active_prompt_mutation",
    "active_release_state_mutation",
    "agent_state_mutation_enabled",
    "fixture_mutation_enabled",
    "guardrail_mutation_enabled",
    "process_mutation_enabled",
    "prompt_mutation_enabled",
    "release_state_mutation_enabled",
)


@dataclass(frozen=True)
class LedgerValidationResult:
    """Result returned by the inactive fixture promotion ledger validator."""

    valid: bool
    errors: tuple[str, ...]

    def require_valid(self) -> None:
        if not self.valid:
            raise ValueError("; ".join(self.errors))


def validate_inactive_fixture_promotion_diff_ledger_v1(
    ledger: Mapping[str, Any],
) -> LedgerValidationResult:
    """Validate an inactive fixture promotion diff ledger v1 mapping."""

    errors: list[str] = []

    if ledger.get("schema_version") != SCHEMA_VERSION:
        errors.append("schema_version must be inactive-fixture-promotion-diff-ledger-v1")

    if ledger.get("ledger_state") != "inactive":
        errors.append("ledger_state must be inactive")

    if ledger.get("promotion_state") not in ("blocked", "review_only", "inactive_review"):
        errors.append("promotion_state must be blocked, review_only, or inactive_review")

    file_diffs = _sequence(ledger.get("file_diffs"))
    if not file_diffs:
        errors.append("file_diffs must include at least one file-level diff summary")
    else:
        seen_families: set[str] = set()
        for index, diff in enumerate(file_diffs):
            if not isinstance(diff, Mapping):
                errors.append(f"file_diffs[{index}] must be an object")
                continue
            path = _string(diff.get("path"))
            summary = _string(diff.get("file_level_diff_summary"))
            family = _string(diff.get("fixture_family"))
            if not path:
                errors.append(f"file_diffs[{index}].path is required")
            elif not path.startswith("ppd/tests/fixtures/"):
                errors.append(f"file_diffs[{index}].path must stay under ppd/tests/fixtures/")
            if not summary:
                errors.append(f"file_diffs[{index}].file_level_diff_summary is required")
            if not family:
                errors.append(f"file_diffs[{index}].fixture_family is required")
            else:
                seen_families.add(family)
    readiness_rows = _sequence(ledger.get("fixture_family_readiness"))
    readiness_by_family: dict[str, Mapping[str, Any]] = {}
    if not readiness_rows:
        errors.append("fixture_family_readiness must include one row per fixture family")
    else:
        for index, row in enumerate(readiness_rows):
            if not isinstance(row, Mapping):
                errors.append(f"fixture_family_readiness[{index}] must be an object")
                continue
            family = _string(row.get("fixture_family"))
            if not family:
                errors.append(f"fixture_family_readiness[{index}].fixture_family is required")
                continue
            readiness_by_family[family] = row
            evidence = _sequence(row.get("readiness_evidence"))
            if not evidence:
                errors.append(f"fixture_family_readiness[{index}].readiness_evidence is required")
            for evidence_index, item in enumerate(evidence):
                if not isinstance(item, Mapping):
                    errors.append(
                        f"fixture_family_readiness[{index}].readiness_evidence[{evidence_index}] must be an object"
                    )
                    continue
                if not _string(item.get("summary")):
                    errors.append(
                        f"fixture_family_readiness[{index}].readiness_evidence[{evidence_index}].summary is required"
                    )
                if not _sequence(item.get("citations")):
                    errors.append(
                        f"fixture_family_readiness[{index}].readiness_evidence[{evidence_index}].citations is required"
                    )
    for family in sorted(seen_families if file_diffs else set()):
        if family not in readiness_by_family:
            errors.append(f"fixture_family_readiness is missing row for {family}")

    blocked_promotions = _sequence(ledger.get("blocked_promotions"))
    if not blocked_promotions:
        errors.append("blocked_promotions must explain why promotion remains blocked")
    for index, blocked in enumerate(blocked_promotions):
        if not isinstance(blocked, Mapping):
            errors.append(f"blocked_promotions[{index}] must be an object")
            continue
        if not _string(blocked.get("explanation")):
            errors.append(f"blocked_promotions[{index}].explanation is required")

    review = ledger.get("review")
    if not isinstance(review, Mapping):
        errors.append("review object is required")
    else:
        if not _string(review.get("reviewer_owner")):
            errors.append("review.reviewer_owner is required")
        if not _string(review.get("rollback_note")):
            errors.append("review.rollback_note is required")

    _reject_terms(errors, ledger, _PRIVATE_ARTIFACT_TERMS, "private/authenticated/session/browser artifact")
    _reject_terms(errors, ledger, _RAW_ARTIFACT_TERMS, "raw crawl/PDF/downloaded data artifact")
    _reject_terms(errors, ledger, _LIVE_CLAIM_TERMS, "live execution or promotion claim")
    _reject_terms(errors, ledger, _GUARANTEE_TERMS, "legal or permitting outcome guarantee")
    _reject_terms(errors, ledger, _CONSEQUENTIAL_TERMS, "consequential action language")
    _reject_terms(errors, ledger, _MUTATION_FLAG_TERMS, "active mutation flag")

    mutation_flags = ledger.get("mutation_flags")
    if isinstance(mutation_flags, Mapping):
        for name, value in mutation_flags.items():
            if bool(value):
                errors.append(f"active mutation flag must be false: mutation_flags.{name}")

    return LedgerValidationResult(valid=not errors, errors=tuple(errors))


def _reject_terms(
    errors: list[str],
    value: Any,
    terms: Iterable[str],
    label: str,
) -> None:
    lowered_terms = tuple(term.lower() for term in terms)
    for path, text in _walk_strings(value):
        lowered = text.lower()
        for term in lowered_terms:
            if term in lowered:
                errors.append(f"reject {label} at {path}: {term}")
                break


def _walk_strings(value: Any, path: str = "$.") -> Iterable[tuple[str, str]]:
    if isinstance(value, str):
        yield path.rstrip("."), value
    elif isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            yield from _walk_strings(key_text, f"{path}{key_text}#key.")
            yield from _walk_strings(child, f"{path}{key_text}.")
    elif isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray, str)):
        for index, child in enumerate(value):
            yield from _walk_strings(child, f"{path}[{index}].")


def _sequence(value: Any) -> tuple[Any, ...]:
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray, str)):
        return tuple(value)
    return ()


def _string(value: Any) -> str:
    if isinstance(value, str):
        return value.strip()
    return ""
