"""Validation for post-dry-run guardrail impact review v2 artifacts.

The validator is intentionally side-effect free. It accepts an already-loaded
mapping and reports deterministic findings instead of reading crawl output,
browser state, PDFs, sessions, or other local artifacts.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence


REVIEW_SCHEMA_VERSION = "post-dry-run-guardrail-impact-review-v2"

_MUTATION_FLAG_KEYS = frozenset(
    {
        "active_guardrail_mutation",
        "active_prompt_mutation",
        "active_source_mutation",
        "active_surface_registry_mutation",
        "active_monitoring_mutation",
        "active_release_state_mutation",
        "active_agent_state_mutation",
        "mutates_active_guardrails",
        "mutates_active_prompts",
        "mutates_active_sources",
        "mutates_active_surface_registry",
        "mutates_active_monitoring",
        "mutates_active_release_state",
        "mutates_active_agent_state",
    }
)

_RAW_ARTIFACT_KEYS = frozenset(
    {
        "auth_state",
        "browser_artifact",
        "browser_session",
        "crawl_output",
        "downloaded_document",
        "har",
        "pdf_bytes",
        "pdf_path",
        "raw_crawl",
        "raw_pdf",
        "session_file",
        "screenshot",
        "storage_state",
        "trace",
        "trace_zip",
    }
)

_RAW_ARTIFACT_SUFFIXES = (
    ".har",
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".zip",
    ".trace",
    "storage_state.json",
)

_PRIVATE_FACT_MARKERS = (
    "authenticated",
    "private",
    "credential",
    "cookie",
    "password",
    "session",
    "token",
    "mfa",
    "captcha",
)

_LIVE_EXECUTION_CLAIMS = (
    "called devhub",
    "clicked devhub",
    "crawled live",
    "executed crawler",
    "executed devhub",
    "executed llm",
    "executed processor",
    "filled devhub",
    "live crawler",
    "live devhub",
    "live llm",
    "live processor",
    "ran crawler",
    "ran devhub",
    "ran llm",
    "ran processor",
    "submitted to devhub",
)

_OUTCOME_GUARANTEES = (
    "approval guaranteed",
    "guarantee approval",
    "guaranteed approval",
    "guaranteed permit",
    "legal advice",
    "permit will be approved",
    "will be approved",
    "will pass inspection",
)

_FINAL_ACTION_LANGUAGE = (
    "cancel inspection",
    "cancel permit",
    "cancellation completed",
    "final payment",
    "final submit",
    "paid fee",
    "payment submitted",
    "schedule inspection",
    "scheduled inspection",
    "submit application",
    "submitted application",
    "submitted permit",
    "upload corrections",
    "uploaded correction",
    "uploaded documents",
)


@dataclass(frozen=True)
class ValidationFinding:
    """A deterministic validation finding for a review artifact."""

    code: str
    path: str
    message: str


def validate_post_dry_run_guardrail_impact_review_v2(
    review: Mapping[str, Any],
) -> list[ValidationFinding]:
    """Return validation findings for a post-dry-run impact review v2 artifact."""

    findings: list[ValidationFinding] = []

    if not isinstance(review, Mapping):
        return [
            ValidationFinding(
                "review_not_mapping",
                "$",
                "review must be a mapping",
            )
        ]

    if review.get("schema_version") != REVIEW_SCHEMA_VERSION:
        findings.append(
            ValidationFinding(
                "invalid_schema_version",
                "$.schema_version",
                f"schema_version must be {REVIEW_SCHEMA_VERSION!r}",
            )
        )

    _require_non_empty_string(review, "guardrail_bundle_id", "$", findings)
    _require_non_empty_string(review, "rollback_notes", "$", findings)
    _require_non_empty_sequence(review, "predicate_ids", "$", findings)
    _require_non_empty_sequence(review, "blocked_action_checks", "$", findings)
    _require_non_empty_sequence(review, "reviewer_owners", "$", findings)

    decisions = review.get("impact_decisions")
    if not isinstance(decisions, Sequence) or isinstance(decisions, (str, bytes)) or not decisions:
        findings.append(
            ValidationFinding(
                "missing_impact_decisions",
                "$.impact_decisions",
                "impact_decisions must be a non-empty list",
            )
        )
    else:
        for index, decision in enumerate(decisions):
            path = f"$.impact_decisions[{index}]"
            if not isinstance(decision, Mapping):
                findings.append(
                    ValidationFinding(
                        "impact_decision_not_mapping",
                        path,
                        "impact decision must be a mapping",
                    )
                )
                continue
            _require_non_empty_string(decision, "decision_id", path, findings)
            citation_ids = decision.get("citation_ids") or decision.get("source_evidence_ids")
            if not _is_non_empty_string_sequence(citation_ids):
                findings.append(
                    ValidationFinding(
                        "uncited_impact_decision",
                        f"{path}.citation_ids",
                        "each impact decision must include one or more citation_ids or source_evidence_ids",
                    )
                )
            if not _is_non_empty_string_sequence(decision.get("predicate_ids")):
                findings.append(
                    ValidationFinding(
                        "impact_decision_missing_predicate_ids",
                        f"{path}.predicate_ids",
                        "each impact decision must identify impacted predicate_ids",
                    )
                )

    blocked_checks = review.get("blocked_action_checks")
    if isinstance(blocked_checks, Sequence) and not isinstance(blocked_checks, (str, bytes)):
        for index, check in enumerate(blocked_checks):
            path = f"$.blocked_action_checks[{index}]"
            if not isinstance(check, Mapping):
                findings.append(
                    ValidationFinding(
                        "blocked_action_check_not_mapping",
                        path,
                        "blocked action check must be a mapping",
                    )
                )
                continue
            _require_non_empty_string(check, "action_id", path, findings)
            if check.get("blocked") is not True:
                findings.append(
                    ValidationFinding(
                        "blocked_action_check_not_blocked",
                        f"{path}.blocked",
                        "blocked action checks must explicitly record blocked=true",
                    )
                )
            citations = check.get("citation_ids") or check.get("source_evidence_ids")
            if not _is_non_empty_string_sequence(citations):
                findings.append(
                    ValidationFinding(
                        "blocked_action_check_uncited",
                        f"{path}.citation_ids",
                        "blocked action checks must be cited",
                    )
                )

    owners = review.get("reviewer_owners")
    if isinstance(owners, Sequence) and not isinstance(owners, (str, bytes)):
        for index, owner in enumerate(owners):
            path = f"$.reviewer_owners[{index}]"
            if not isinstance(owner, Mapping):
                findings.append(
                    ValidationFinding(
                        "reviewer_owner_not_mapping",
                        path,
                        "reviewer owner must be a mapping",
                    )
                )
                continue
            if not any(_is_non_empty_string(owner.get(key)) for key in ("owner_id", "name", "team")):
                findings.append(
                    ValidationFinding(
                        "reviewer_owner_missing_identifier",
                        path,
                        "reviewer owner must include owner_id, name, or team",
                    )
                )
            _require_non_empty_string(owner, "role", path, findings)

    for path, key, value in _walk(review):
        normalized_key = key.lower() if key else ""
        if normalized_key in _MUTATION_FLAG_KEYS and value is True:
            findings.append(
                ValidationFinding(
                    "active_mutation_flag",
                    path,
                    "post-dry-run review artifacts must not enable active mutation flags",
                )
            )
        if normalized_key == "mutation_flags" and _contains_truthy_mutation_flag(value):
            findings.append(
                ValidationFinding(
                    "active_mutation_flag",
                    path,
                    "mutation_flags must not contain enabled active mutation entries",
                )
            )
        if normalized_key in _RAW_ARTIFACT_KEYS and _has_value(value):
            findings.append(
                ValidationFinding(
                    "raw_artifact_reference",
                    path,
                    "raw crawl, PDF, session, browser, HAR, trace, or screenshot artifacts are not allowed",
                )
            )
        if _looks_like_raw_artifact_path(value):
            findings.append(
                ValidationFinding(
                    "raw_artifact_reference",
                    path,
                    "raw artifact paths or downloadable document references are not allowed",
                )
            )
        if normalized_key in {"privacy_classification", "auth_scope"} and _is_private_or_authenticated(value):
            findings.append(
                ValidationFinding(
                    "private_or_authenticated_fact",
                    path,
                    "private or authenticated facts are not allowed in committed review artifacts",
                )
            )
        if normalized_key in {"claim", "summary", "notes", "rationale", "decision", "outcome"} and isinstance(value, str):
            lowered = value.lower()
            if _contains_any(lowered, _PRIVATE_FACT_MARKERS):
                findings.append(
                    ValidationFinding(
                        "private_or_authenticated_fact",
                        path,
                        "review text must not include private, credential, session, MFA, CAPTCHA, or authenticated facts",
                    )
                )
            if _contains_any(lowered, _LIVE_EXECUTION_CLAIMS):
                findings.append(
                    ValidationFinding(
                        "live_execution_claim",
                        path,
                        "post-dry-run review must not claim live LLM, DevHub, crawler, or processor execution",
                    )
                )
            if _contains_any(lowered, _OUTCOME_GUARANTEES):
                findings.append(
                    ValidationFinding(
                        "outcome_guarantee",
                        path,
                        "legal, permitting, approval, or inspection outcome guarantees are not allowed",
                    )
                )
            if _contains_any(lowered, _FINAL_ACTION_LANGUAGE):
                findings.append(
                    ValidationFinding(
                        "final_action_language",
                        path,
                        "final submission, payment, upload, scheduling, or cancellation language is not allowed",
                    )
                )

    return findings


def assert_valid_post_dry_run_guardrail_impact_review_v2(review: Mapping[str, Any]) -> None:
    """Raise ValueError if the review has validation findings."""

    findings = validate_post_dry_run_guardrail_impact_review_v2(review)
    if findings:
        detail = "; ".join(f"{finding.code} at {finding.path}" for finding in findings)
        raise ValueError(detail)


def _require_non_empty_string(
    mapping: Mapping[str, Any],
    key: str,
    path: str,
    findings: list[ValidationFinding],
) -> None:
    if not _is_non_empty_string(mapping.get(key)):
        findings.append(
            ValidationFinding(
                f"missing_{key}",
                f"{path}.{key}",
                f"{key} must be a non-empty string",
            )
        )


def _require_non_empty_sequence(
    mapping: Mapping[str, Any],
    key: str,
    path: str,
    findings: list[ValidationFinding],
) -> None:
    if not _is_non_empty_sequence(mapping.get(key)):
        findings.append(
            ValidationFinding(
                f"missing_{key}",
                f"{path}.{key}",
                f"{key} must be a non-empty list",
            )
        )


def _is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_non_empty_sequence(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes)) and bool(value)


def _is_non_empty_string_sequence(value: Any) -> bool:
    return _is_non_empty_sequence(value) and all(_is_non_empty_string(item) for item in value)


def _has_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (Sequence, Mapping)):
        return bool(value)
    return True


def _is_private_or_authenticated(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    lowered = value.lower()
    return "private" in lowered or "authenticated" in lowered


def _contains_any(value: str, markers: Iterable[str]) -> bool:
    return any(marker in value for marker in markers)


def _contains_truthy_mutation_flag(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, Mapping):
        return any(_contains_truthy_mutation_flag(item) for item in value.values())
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return any(_contains_truthy_mutation_flag(item) for item in value)
    return False


def _looks_like_raw_artifact_path(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    lowered = value.lower().strip()
    return lowered.endswith(_RAW_ARTIFACT_SUFFIXES) or "/.auth/" in lowered or "/traces/" in lowered


def _walk(value: Any, path: str = "$", key: str = "") -> Iterable[tuple[str, str, Any]]:
    yield path, key, value
    if isinstance(value, Mapping):
        for child_key, child_value in value.items():
            child_key_text = str(child_key)
            child_path = f"{path}.{child_key_text}"
            yield from _walk(child_value, child_path, child_key_text)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child_value in enumerate(value):
            yield from _walk(child_value, f"{path}[{index}]", key)
