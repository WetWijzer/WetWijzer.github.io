"""Validation for regenerated PP&D agent regression matrices and refresh packets.

The validator is intentionally schema-tolerant because generated matrices may be
represented as rows, cases, scenarios, tests, or refresh packets while the
regression contract stabilizes. It rejects unsafe claims and missing evidence
before a packet can be promoted into committed regression coverage.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import PurePosixPath, PureWindowsPath
import json
import re
from typing import Any, Iterable, Mapping, Sequence


_CURRENT_SOURCE_MAX_AGE_DAYS = 45
_CASE_KEYS = ("cases", "rows", "scenarios", "tests", "regressions", "refresh_scenarios", "refresh_cases")
_EXPECTED_KEYS = (
    "expected_outcome",
    "expected_outcomes",
    "expected",
    "outcome",
    "then",
    "assertions",
    "expectations",
)
_CITATION_KEYS = (
    "citation",
    "citations",
    "citation_ids",
    "source_id",
    "source_ids",
    "source_evidence_id",
    "source_evidence_ids",
    "evidence",
    "evidence_ids",
    "sources",
)
_PROMPT_EXPECTATION_KEYS = (
    "expected_prompt",
    "expected_prompts",
    "expected_missing_information_prompt",
    "expected_missing_information_prompts",
    "missing_information_prompt",
    "missing_information_prompts",
    "manual_handoff_prompt",
    "manual_handoff_prompts",
)
_REFUSAL_EXPECTATION_KEYS = (
    "expected_refusal",
    "expected_refusals",
    "refusal_reason",
    "refusal_reasons",
    "refused_consequential_action_response",
    "safe_alternatives",
)
_PREVIEW_EXPECTATION_KEYS = (
    "expected_preview",
    "expected_previews",
    "preview_expectation",
    "preview_expectations",
    "local_pdf_preview",
    "draft_preview",
    "expected_pdf_preview",
)
_BLOCK_EXPLANATION_KEYS = (
    "blocked_action_explanation",
    "blocked_action_explanations",
    "explanation",
    "explanations",
    "refusal_reason",
    "manual_handoff_reason",
)
_REVIEWER_OWNER_KEYS = ("reviewer_owner", "reviewer_owners", "owner", "owners", "review_owner", "reviewer")
_CONSEQUENTIAL_WORDS = {
    "submit",
    "submission",
    "certify",
    "certification",
    "upload",
    "attach",
    "schedule",
    "cancel",
    "withdraw",
    "payment",
    "pay",
    "purchase",
    "finalize",
    "official",
    "reactivate",
    "extension",
    "inspection",
    "acknowledge",
}
_MANUAL_HANDOFF_WORDS = {
    "manual_handoff",
    "manual handoff",
    "human_handoff",
    "human handoff",
    "requires_attendance",
    "attended",
    "user_present",
    "exact_confirmation",
    "exact confirmation",
}
_BLOCK_WORDS = {"block", "blocked", "refuse", "refused", "deny", "denied", "stop", "manual_handoff"}
_ALLOW_WORDS = {"allowed", "allow", "autonomous", "execute", "executed", "complete", "completed", "enabled"}
_PROMPT_WORDS = {"missing information", "ask", "prompt", "question", "clarify", "gap"}
_REFUSAL_WORDS = {"refuse", "refusal", "blocked", "deny", "denied", "cannot", "must not"}
_PREVIEW_WORDS = {"preview", "pdf preview", "draft preview", "local pdf", "render"}
_LIVE_EXECUTION_KEYS = {
    "use_live_llm",
    "live_llm",
    "execute_live_llm",
    "run_live_llm",
    "llm_execution",
    "invoke_llm",
    "call_llm",
    "llm_executed",
    "agent_consumer_invoked",
    "agent_consumers_invoked",
    "devhub_executed",
    "devhub_browser_executed",
    "live_devhub_executed",
    "browser_automation_executed",
    "crawler_executed",
    "live_crawler_executed",
    "crawl_executed",
    "processor_executed",
    "processor_run_executed",
    "live_processor_executed",
}
_LIVE_EXECUTION_PHRASES = (
    "live llm",
    "llm executed",
    "called the llm",
    "agent consumer invoked",
    "agent consumer executed",
    "live devhub",
    "devhub executed",
    "devhub browser ran",
    "opened devhub",
    "browser automation ran",
    "live crawler",
    "crawler executed",
    "crawler ran",
    "live crawl completed",
    "processor executed",
    "processor ran",
    "processor suite executed",
)
_PRIVATE_KEY_PARTS = {
    "password",
    "passwd",
    "secret",
    "token",
    "cookie",
    "credential",
    "auth_state",
    "session_state",
    "payment_detail",
    "card_number",
    "cvv",
    "ssn",
    "tax_id",
    "driver_license",
}
_PRIVATE_CASE_KEY_PARTS = {
    "private_case_fact",
    "private_case_facts",
    "case_fact",
    "case_facts",
    "known_private_fact",
    "known_private_facts",
    "observed_private_values",
    "private_values",
    "applicant_name",
    "owner_name",
    "email_address",
    "phone_number",
    "permit_number",
    "project_address",
    "tax_account_number",
}
_RAW_AUTH_KEY_PARTS = {
    "raw_authenticated",
    "authenticated_value",
    "authenticated_values",
    "raw_devhub",
    "devhub_private_value",
    "devhub_field_value",
    "raw_account_value",
}
_PRIVATE_CLASSIFICATIONS = {
    "private",
    "confidential",
    "restricted",
    "user_private",
    "case_private",
    "authenticated",
    "devhub_authenticated_private",
}
_MUTATION_KEY_PARTS = {
    "prompt_mutation",
    "guardrail_mutation",
    "surface_registry_mutation",
    "monitoring_mutation",
    "agent_state_mutation",
    "mutate_prompt",
    "mutate_guardrail",
    "mutate_surface_registry",
    "mutate_monitoring",
    "mutate_agent_state",
    "prompt_update_enabled",
    "guardrail_update_enabled",
    "surface_registry_update_enabled",
    "monitoring_update_enabled",
    "agent_state_update_enabled",
}
_MUTATION_TARGET_WORDS = {"prompt", "guardrail", "surface-registry", "surface_registry", "monitoring", "agent-state", "agent_state"}
_OUTCOME_GUARANTEE_PHRASES = (
    "guarantee approval",
    "guaranteed approval",
    "permit will be approved",
    "application will be approved",
    "approval is guaranteed",
    "permit will issue",
    "permit issuance guaranteed",
    "will receive the permit",
    "legally valid",
    "no legal risk",
    "cannot be denied",
)
_LOCAL_PATH_PATTERNS = (
    re.compile(r"file://", re.IGNORECASE),
    re.compile(r"(?:^|[\s'\"])/Users/[A-Za-z0-9._-]+/"),
    re.compile(r"(?:^|[\s'\"])/home/[A-Za-z0-9._-]+/"),
    re.compile(r"(?:^|[\s'\"])/private/"),
    re.compile(r"[A-Za-z]:\\\\Users\\\\[^\\\s]+", re.IGNORECASE),
)
_PRIVATE_VALUE_PATTERNS = (
    re.compile(r"PRIVATE[_ -]?VALUE", re.IGNORECASE),
    re.compile(r"BEGIN (?:RSA |OPENSSH |PRIVATE )?PRIVATE KEY", re.IGNORECASE),
    re.compile(r"(?:password|secret|token|cookie)\s*[:=]\s*[^\s,;]+", re.IGNORECASE),
    re.compile(r"bearer\s+[A-Za-z0-9._\-]+", re.IGNORECASE),
    re.compile(r"sk-[A-Za-z0-9]{12,}"),
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    re.compile(r"\b\d{13,19}\b"),
)


@dataclass(frozen=True)
class MatrixValidationIssue:
    """A deterministic matrix or refresh-packet validation failure."""

    code: str
    path: str
    message: str


class MatrixValidationError(ValueError):
    """Raised when a regenerated regression artifact violates PP&D policy."""

    def __init__(self, issues: Sequence[MatrixValidationIssue]) -> None:
        self.issues = tuple(issues)
        details = "; ".join(f"{issue.code} at {issue.path}: {issue.message}" for issue in issues)
        super().__init__(details or "agent regression artifact is invalid")


def validate_agent_regression_matrix(matrix: Mapping[str, Any]) -> None:
    """Validate a regenerated PP&D agent regression matrix."""

    issues = collect_agent_regression_matrix_issues(matrix)
    if issues:
        raise MatrixValidationError(issues)


def validate_agent_regression_refresh_packet(packet: Mapping[str, Any]) -> None:
    """Validate a fixture-first agent regression refresh packet."""

    issues = collect_agent_regression_refresh_packet_issues(packet)
    if issues:
        raise MatrixValidationError(issues)


def collect_agent_regression_matrix_issues(matrix: Mapping[str, Any]) -> list[MatrixValidationIssue]:
    """Return deterministic validation issues for a matrix."""

    return collect_agent_regression_refresh_packet_issues(matrix)


def collect_agent_regression_refresh_packet_issues(packet: Mapping[str, Any]) -> list[MatrixValidationIssue]:
    """Return deterministic validation issues for an agent refresh packet."""

    issues: list[MatrixValidationIssue] = []
    if not isinstance(packet, Mapping):
        return [MatrixValidationIssue("invalid_packet", "$", "agent regression refresh packet root must be an object")]

    generated_at = _parse_datetime(_first_present(packet, ("generated_at", "matrix_generated_at", "created_at")))
    issues.extend(_collect_recursive_safety_issues(packet))

    cases = list(_iter_cases(packet))
    if not cases:
        issues.append(MatrixValidationIssue("missing_scenarios", "$.scenarios", "refresh packets require at least one scenario or case"))

    for case_path, case in cases:
        issues.extend(_collect_case_issues(case_path, case))

    for source_path, source in _iter_sources(packet):
        freshness = str(_first_present(source, ("freshness_status", "status", "freshness")) or "").lower()
        if freshness == "current" and _source_is_stale(source, generated_at):
            issues.append(MatrixValidationIssue("stale_source_marked_current", source_path, "stale or superseded source evidence cannot be marked current"))

    return issues


def load_and_validate_agent_regression_matrix(path: str) -> Mapping[str, Any]:
    """Load a JSON matrix file and validate it."""

    return load_and_validate_agent_regression_refresh_packet(path)


def load_and_validate_agent_regression_refresh_packet(path: str) -> Mapping[str, Any]:
    """Load a JSON refresh packet file and validate it."""

    with open(path, "r", encoding="utf-8") as handle:
        packet = json.load(handle)
    if not isinstance(packet, Mapping):
        raise MatrixValidationError([MatrixValidationIssue("invalid_packet", "$", "packet root must be a JSON object")])
    validate_agent_regression_refresh_packet(packet)
    return packet


def _collect_case_issues(case_path: str, case: Mapping[str, Any]) -> list[MatrixValidationIssue]:
    issues: list[MatrixValidationIssue] = []
    expected = _expected_payload(case)
    expected_path = f"{case_path}.expected" if expected is not None else case_path
    case_text = _compact_text(case).lower()
    action_text = _action_text(case)
    expected_text = _compact_text(expected if expected is not None else case).lower()

    if not _has_reviewer_owner(case):
        issues.append(MatrixValidationIssue("missing_reviewer_owner", case_path, "each regression refresh scenario requires a reviewer owner"))

    if not _has_citation(case, expected):
        issues.append(MatrixValidationIssue("uncited_scenario", case_path, "each regression refresh scenario must cite source evidence"))

    if _needs_prompt_expectation(case_text, action_text) and not _has_any_key(case, _PROMPT_EXPECTATION_KEYS):
        issues.append(MatrixValidationIssue("missing_expected_prompt", case_path, "prompt scenarios require expected prompt text or prompt assertions"))

    if _needs_refusal_expectation(case_text, action_text, expected_text) and not _has_refusal_expectation(case):
        issues.append(MatrixValidationIssue("missing_expected_refusal", expected_path, "refusal or blocked-action scenarios require expected refusal details"))

    if _needs_preview_expectation(case_text, action_text) and not _has_any_key(case, _PREVIEW_EXPECTATION_KEYS):
        issues.append(MatrixValidationIssue("missing_expected_preview", case_path, "draft preview scenarios require expected preview assertions"))

    if _has_blocked_action(case, expected_text) and not _has_any_key(case, _BLOCK_EXPLANATION_KEYS):
        issues.append(MatrixValidationIssue("missing_blocked_action_explanation", case_path, "blocked actions require an explanation for the reviewer and user"))

    if _is_consequential(case, action_text) and _is_downgraded_to_allowed(expected_text):
        issues.append(MatrixValidationIssue("blocked_action_downgrade", expected_path, "consequential or financial actions must remain blocked or handoff-gated"))

    if _requires_manual_handoff(case, action_text) and not _mentions_any(expected_text, _MANUAL_HANDOFF_WORDS):
        issues.append(MatrixValidationIssue("missing_manual_handoff_expectation", expected_path, "blocked DevHub or unsupported actions must expect manual handoff"))

    if _claims_devhub_automation(case, action_text, expected_text):
        issues.append(MatrixValidationIssue("devhub_automation_claim", expected_path, "committed packets must not claim autonomous DevHub consequential execution"))

    return issues


def _collect_recursive_safety_issues(value: Any, path: str = "$", key: object | None = None) -> list[MatrixValidationIssue]:
    issues: list[MatrixValidationIssue] = []
    key_text = str(key).lower() if key is not None else ""

    if key_text in _LIVE_EXECUTION_KEYS and _truthy(value):
        issues.append(MatrixValidationIssue("live_execution_claim", path, "live LLM, DevHub, crawler, and processor execution must be disabled in committed packets"))

    if any(part in key_text for part in _PRIVATE_KEY_PARTS) and value not in (None, "", False, [], {}):
        issues.append(MatrixValidationIssue("private_value", path, "private values and authentication material are not allowed in committed packets"))

    if any(part in key_text for part in _PRIVATE_CASE_KEY_PARTS) and _non_empty(value):
        issues.append(MatrixValidationIssue("private_case_facts", path, "regression refresh packets must not include private case facts"))

    if any(part in key_text for part in _RAW_AUTH_KEY_PARTS) and _non_empty(value):
        issues.append(MatrixValidationIssue("raw_authenticated_value", path, "raw authenticated DevHub values are not allowed in committed packets"))

    if any(part in key_text for part in _MUTATION_KEY_PARTS) and _truthy(value):
        issues.append(MatrixValidationIssue("active_mutation_flag", path, "prompt, guardrail, surface-registry, monitoring, and agent-state mutations must be inactive"))

    if key_text in {"privacy", "privacy_classification", "case_fact_privacy"} and str(value).lower() in _PRIVATE_CLASSIFICATIONS:
        issues.append(MatrixValidationIssue("private_case_facts", path, "private or authenticated case material is not allowed in committed packets"))

    if isinstance(value, Mapping):
        if _control_is_enabled_consequential(value):
            issues.append(MatrixValidationIssue("enabled_consequential_control", path, "consequential, financial, or official controls must not be enabled in regression expectations"))
        if _mapping_has_active_mutation(value):
            issues.append(MatrixValidationIssue("active_mutation_flag", path, "mutation controls for prompts, guardrails, surface registry, monitoring, or agent state must be inactive"))
        for child_key, child_value in value.items():
            issues.extend(_collect_recursive_safety_issues(child_value, f"{path}.{child_key}", child_key))
    elif isinstance(value, list):
        for index, child_value in enumerate(value):
            issues.extend(_collect_recursive_safety_issues(child_value, f"{path}[{index}]", key))
    elif isinstance(value, str):
        lowered = value.lower()
        if any(pattern.search(value) for pattern in _LOCAL_PATH_PATTERNS):
            issues.append(MatrixValidationIssue("local_private_path", path, "local private file paths are not allowed in committed packets"))
        if any(pattern.search(value) for pattern in _PRIVATE_VALUE_PATTERNS):
            issues.append(MatrixValidationIssue("private_value", path, "private values are not allowed in committed packets"))
        if any(phrase in lowered for phrase in _LIVE_EXECUTION_PHRASES):
            issues.append(MatrixValidationIssue("live_execution_claim", path, "packets must not claim live LLM, DevHub, crawler, or processor execution"))
        if any(phrase in lowered for phrase in _OUTCOME_GUARANTEE_PHRASES):
            issues.append(MatrixValidationIssue("outcome_guarantee", path, "packets must not guarantee legal or permitting outcomes"))

    return issues


def _iter_cases(matrix: Mapping[str, Any]) -> Iterable[tuple[str, Mapping[str, Any]]]:
    for key in _CASE_KEYS:
        value = matrix.get(key)
        if isinstance(value, list):
            for index, item in enumerate(value):
                if isinstance(item, Mapping):
                    yield f"$.{key}[{index}]", item
        elif isinstance(value, Mapping):
            for case_key, item in value.items():
                if isinstance(item, Mapping):
                    yield f"$.{key}.{case_key}", item
    if any(key in matrix for key in _EXPECTED_KEYS):
        yield "$", matrix


def _iter_sources(matrix: Mapping[str, Any]) -> Iterable[tuple[str, Mapping[str, Any]]]:
    for key in ("sources", "source_registry", "source_evidence", "evidence"):
        value = matrix.get(key)
        if isinstance(value, list):
            for index, item in enumerate(value):
                if isinstance(item, Mapping):
                    yield f"$.{key}[{index}]", item
        elif isinstance(value, Mapping):
            for source_key, item in value.items():
                if isinstance(item, Mapping):
                    yield f"$.{key}.{source_key}", item


def _expected_payload(case: Mapping[str, Any]) -> Any:
    return _first_present(case, _EXPECTED_KEYS)


def _has_citation(case: Mapping[str, Any], expected: Any) -> bool:
    for container in (case, expected):
        if isinstance(container, Mapping):
            for key in _CITATION_KEYS:
                if _has_nonempty_value(container.get(key)):
                    return True
    return False


def _has_reviewer_owner(case: Mapping[str, Any]) -> bool:
    return any(_has_nonempty_value(case.get(key)) for key in _REVIEWER_OWNER_KEYS)


def _has_any_key(case: Mapping[str, Any], keys: Iterable[str]) -> bool:
    for key in keys:
        if _has_nonempty_value(case.get(key)):
            return True
    expected = _expected_payload(case)
    if isinstance(expected, Mapping):
        return any(_has_nonempty_value(expected.get(key)) for key in keys)
    return False


def _has_refusal_expectation(case: Mapping[str, Any]) -> bool:
    if _has_any_key(case, _REFUSAL_EXPECTATION_KEYS):
        return True
    response = case.get("refused_consequential_action_response")
    if isinstance(response, Mapping):
        return _has_nonempty_value(response.get("refusal_reason")) and _has_nonempty_value(response.get("safe_alternatives"))
    return False


def _has_blocked_action(case: Mapping[str, Any], expected_text: str) -> bool:
    if _has_nonempty_value(case.get("blocked_actions")) or _has_nonempty_value(case.get("blocked_action")):
        return True
    if _has_any_key(case, ("blocked_predicates", "refused_action_predicates")):
        return True
    return _mentions_any(expected_text, _BLOCK_WORDS)


def _needs_prompt_expectation(case_text: str, action_text: str) -> bool:
    combined = f"{case_text} {action_text}"
    return _mentions_any(combined, _PROMPT_WORDS)


def _needs_refusal_expectation(case_text: str, action_text: str, expected_text: str) -> bool:
    combined = f"{case_text} {action_text} {expected_text}"
    return _mentions_any(combined, _REFUSAL_WORDS) or _mentions_any(combined, _CONSEQUENTIAL_WORDS)


def _needs_preview_expectation(case_text: str, action_text: str) -> bool:
    combined = f"{case_text} {action_text}"
    return _mentions_any(combined, _PREVIEW_WORDS)


def _action_text(case: Mapping[str, Any]) -> str:
    parts: list[str] = []
    for key in ("action", "action_name", "requested_action", "user_request", "workflow", "surface", "classification", "action_policy", "action_class", "risk"):
        value = case.get(key)
        if value is not None:
            parts.append(_compact_text(value))
    return " ".join(parts).lower()


def _is_consequential(case: Mapping[str, Any], action_text: str) -> bool:
    classification = _compact_text(_first_present(case, ("classification", "action_class", "action_policy", "risk"))).lower()
    if any(word in classification for word in ("consequential", "financial", "official")):
        return True
    return _mentions_any(action_text, _CONSEQUENTIAL_WORDS)


def _is_downgraded_to_allowed(expected_text: str) -> bool:
    return _mentions_any(expected_text, _ALLOW_WORDS) and not _mentions_any(expected_text, _BLOCK_WORDS | _MANUAL_HANDOFF_WORDS)


def _requires_manual_handoff(case: Mapping[str, Any], action_text: str) -> bool:
    unsupported = _compact_text(_first_present(case, ("unsupported", "requires_attendance", "requires_manual_handoff"))).lower()
    if any(word in unsupported for word in ("true", "manual", "attended", "unsupported")):
        return True
    return _mentions_any(action_text, {"mfa", "captcha", "account creation", "password recovery", "payment", "submit", "upload", "schedule", "certify", "cancel"})


def _claims_devhub_automation(case: Mapping[str, Any], action_text: str, expected_text: str) -> bool:
    combined = f"{action_text} {expected_text} {_compact_text(case)}".lower()
    if "devhub" not in combined:
        return False
    if not _mentions_any(combined, _CONSEQUENTIAL_WORDS):
        return False
    return _mentions_any(combined, {"completed", "executed", "automated", "submitted", "uploaded", "scheduled", "paid", "purchased"})


def _source_is_stale(source: Mapping[str, Any], generated_at: datetime | None) -> bool:
    explicit_stale = _first_present(source, ("stale", "is_stale", "superseded", "superseded_by", "stale_as_of"))
    if explicit_stale not in (None, "", False, [], {}):
        return True
    reference_time = generated_at or datetime.now(timezone.utc)
    seen_at = _parse_datetime(_first_present(source, ("last_seen_at", "last_verified_at", "verified_at", "captured_at")))
    if seen_at is None:
        return False
    return (reference_time - seen_at).days > _CURRENT_SOURCE_MAX_AGE_DAYS


def _control_is_enabled_consequential(control: Mapping[str, Any]) -> bool:
    enabled = _truthy(_first_present(control, ("enabled", "is_enabled", "active")))
    status = str(_first_present(control, ("status", "state")) or "").lower()
    if not enabled and status not in {"enabled", "active", "allowed"}:
        return False
    text = _compact_text(control).lower()
    return _mentions_any(text, _CONSEQUENTIAL_WORDS) or _mentions_any(text, {"consequential", "financial", "official"})


def _mapping_has_active_mutation(value: Mapping[str, Any]) -> bool:
    target = _compact_text(_first_present(value, ("mutation_target", "target", "surface", "component"))).lower()
    enabled = _truthy(_first_present(value, ("enabled", "active", "mutation_enabled", "allow_mutation")))
    if not enabled:
        return False
    return _mentions_any(target, _MUTATION_TARGET_WORDS)


def _first_present(mapping: Mapping[str, Any], keys: Iterable[str]) -> Any:
    for key in keys:
        if key in mapping:
            return mapping[key]
    return None


def _truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "enabled", "active", "on", "allowed"}
    return bool(value)


def _non_empty(value: Any) -> bool:
    if value in (None, False, "", [], {}):
        return False
    if isinstance(value, Mapping):
        return any(_non_empty(item) for item in value.values())
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return any(_non_empty(item) for item in value)
    return True


def _has_nonempty_value(value: Any) -> bool:
    return _non_empty(value)


def _compact_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, Mapping):
        return " ".join(f"{key} {_compact_text(child)}" for key, child in value.items())
    if isinstance(value, list):
        return " ".join(_compact_text(child) for child in value)
    return str(value)


def _mentions_any(text: str, words: Iterable[str]) -> bool:
    lowered = text.lower()
    return any(word in lowered for word in words)


def _parse_datetime(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip()
    if text.endswith("Z"):
        text = f"{text[:-1]}+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def public_path_name(path: str) -> str:
    """Return a stable public basename without exposing private path parents."""

    if "\\" in path:
        return PureWindowsPath(path).name
    return PurePosixPath(path).name


__all__ = [
    "MatrixValidationError",
    "MatrixValidationIssue",
    "collect_agent_regression_matrix_issues",
    "collect_agent_regression_refresh_packet_issues",
    "load_and_validate_agent_regression_matrix",
    "load_and_validate_agent_regression_refresh_packet",
    "public_path_name",
    "validate_agent_regression_matrix",
    "validate_agent_regression_refresh_packet",
]
