"""Validation for public source refresh plan v2 proposals.

The v2 public refresh plan is intentionally a planning artifact only. It may
identify public sources to review, but it must not carry private browser state,
raw downloaded material, live-crawl assertions, legal guarantees, consequential
action instructions, or any flag that mutates PP&D state.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any


MUTATION_FLAG_NAMES = {
    "mutate_active_sources",
    "mutate_active_documents",
    "mutate_active_requirements",
    "mutate_active_processes",
    "mutate_active_guardrails",
    "mutate_active_prompts",
    "mutate_release_state",
    "mutate_agent_state",
    "write_active_sources",
    "write_active_documents",
    "write_active_requirements",
    "write_active_processes",
    "write_active_guardrails",
    "write_active_prompts",
    "write_release_state",
    "write_agent_state",
    "commit_sources",
    "commit_documents",
    "commit_requirements",
    "commit_processes",
    "commit_guardrails",
    "publish_release_state",
    "update_agent_state",
}

PRIVATE_ARTIFACT_KEYS = {
    "auth_state",
    "authenticated_session",
    "browser_context",
    "browser_profile",
    "cookies",
    "devhub_session",
    "local_storage",
    "mfa_token",
    "password",
    "session",
    "session_file",
    "session_storage",
    "trace",
    "user_profile",
}

RAW_DATA_KEYS = {
    "downloaded_data",
    "downloaded_documents",
    "downloaded_pdf",
    "html_dump",
    "pdf_bytes",
    "raw_crawl",
    "raw_download",
    "raw_html",
    "raw_pdf",
    "response_body",
    "screenshot",
}

LIVE_CRAWL_TERMS = (
    "live crawl",
    "live-crawl",
    "crawled live",
    "fetched live",
    "downloaded live",
    "browser observed",
)

GUARANTEE_TERMS = (
    "guarantee approval",
    "guaranteed approval",
    "guarantee permit",
    "guaranteed permit",
    "will be approved",
    "permit will issue",
    "legal advice",
    "legally ensures",
    "ensures compliance",
)

CONSEQUENTIAL_ACTION_TERMS = (
    "submit the application",
    "file the permit",
    "certify compliance",
    "pay the fee",
    "cancel the permit",
    "upload the document",
    "create an account",
    "sign the form",
)


@dataclass(frozen=True)
class ValidationError:
    code: str
    message: str
    path: str


def validate_public_source_refresh_plan_v2(plan: Mapping[str, Any]) -> list[ValidationError]:
    """Return validation errors for a public source refresh plan v2 object."""

    errors: list[ValidationError] = []

    candidates = _sequence(plan.get("source_refresh_candidates"))
    if not candidates:
        errors.append(ValidationError("missing_source_refresh_candidates", "plan must include source_refresh_candidates", "source_refresh_candidates"))
    else:
        for index, candidate in enumerate(candidates):
            candidate_path = f"source_refresh_candidates[{index}]"
            if not isinstance(candidate, Mapping):
                errors.append(ValidationError("invalid_source_refresh_candidate", "source refresh candidate must be an object", candidate_path))
                continue
            citations = _sequence(candidate.get("citations"))
            if not citations:
                errors.append(ValidationError("uncited_source_refresh_candidate", "source refresh candidate must include at least one citation", f"{candidate_path}.citations"))
            for field_name in ("affected_requirement_ids", "affected_process_ids", "affected_guardrail_ids"):
                if not _sequence(candidate.get(field_name)):
                    errors.append(ValidationError("missing_affected_ids", f"candidate must include {field_name}", f"{candidate_path}.{field_name}"))

    freshness_rows = _sequence(plan.get("freshness_priority_rows"))
    if not freshness_rows:
        errors.append(ValidationError("missing_freshness_priority_rows", "plan must include freshness_priority_rows", "freshness_priority_rows"))

    if not _text(plan.get("reviewer_owner")):
        errors.append(ValidationError("missing_reviewer_owner", "plan must include reviewer_owner", "reviewer_owner"))
    if not _text(plan.get("rollback_note")):
        errors.append(ValidationError("missing_rollback_note", "plan must include rollback_note", "rollback_note"))

    _walk(plan, "$", errors)
    return errors


def assert_valid_public_source_refresh_plan_v2(plan: Mapping[str, Any]) -> None:
    errors = validate_public_source_refresh_plan_v2(plan)
    if errors:
        detail = "; ".join(f"{error.code} at {error.path}" for error in errors)
        raise ValueError(f"invalid public source refresh plan v2: {detail}")


def _walk(value: Any, path: str, errors: list[ValidationError]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            child_path = f"{path}.{key_text}"
            lowered_key = key_text.lower()
            if lowered_key in PRIVATE_ARTIFACT_KEYS:
                errors.append(ValidationError("private_or_authenticated_artifact", "plan must not include private/authenticated/session/browser artifacts", child_path))
            if lowered_key in RAW_DATA_KEYS:
                errors.append(ValidationError("raw_crawl_or_downloaded_data", "plan must not include raw crawl, PDF, or downloaded data", child_path))
            if lowered_key in MUTATION_FLAG_NAMES and bool(child):
                errors.append(ValidationError("active_state_mutation_flag", "plan must not set active state mutation flags", child_path))
            _walk(child, child_path, errors)
        return

    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            _walk(child, f"{path}[{index}]", errors)
        return

    if isinstance(value, str):
        lowered = value.lower()
        if any(term in lowered for term in LIVE_CRAWL_TERMS):
            errors.append(ValidationError("live_crawl_claim", "plan must not claim live crawl results", path))
        if any(term in lowered for term in GUARANTEE_TERMS):
            errors.append(ValidationError("legal_or_permitting_guarantee", "plan must not include legal or permitting outcome guarantees", path))
        if any(term in lowered for term in CONSEQUENTIAL_ACTION_TERMS):
            errors.append(ValidationError("consequential_action_language", "plan must not direct consequential actions", path))


def _sequence(value: Any) -> Sequence[Any]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return value
    return ()


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""
