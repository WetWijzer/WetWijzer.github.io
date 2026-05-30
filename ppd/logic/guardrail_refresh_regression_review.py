"""Validation for guardrail refresh regression review packets.

The validator is intentionally schema-tolerant: review packets may come from
hand-authored JSON, daemon summaries, or supervisor handoff records. The rules
below fail closed for privacy, citation, offline-validation, and mutation risks.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Iterable, Mapping, Sequence


@dataclass(frozen=True)
class ReviewFinding:
    code: str
    path: str
    message: str


class GuardrailRefreshRegressionReviewError(ValueError):
    def __init__(self, findings: Sequence[ReviewFinding]) -> None:
        self.findings = tuple(findings)
        detail = "; ".join(f"{finding.path}: {finding.code}" for finding in findings)
        super().__init__(detail)


_BUNDLE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{2,}$")
_PRIVATE_PATH_RE = re.compile(r"(?:file://|~[/\\]|/Users/[^\s]+|/home/[^\s]+|[A-Za-z]:\\\\Users\\\\[^\s]+)")
_PRIVATE_FACT_RE = re.compile(
    r"\b(?:private case fact|applicant private|owner private|private address|"
    r"private permit|unredacted case|account-scoped fact|personal fact)\b",
    re.IGNORECASE,
)
_RAW_AUTH_RE = re.compile(
    r"\b(?:cookie|session[_ -]?token|auth[_ -]?state|bearer token|csrf|jwt|"
    r"access[_ -]?token|refresh[_ -]?token|raw authenticated|password)\b",
    re.IGNORECASE,
)
_LIVE_EXECUTION_RE = re.compile(
    r"\b(?:ran|executed|called|queried|invoked|launched|used)\b.{0,80}"
    r"\b(?:live\s+)?(?:llm|devhub|crawler|crawl|processor|playwright|browser automation)\b|"
    r"\b(?:live\s+devhub|live\s+crawl|live\s+processor|live\s+llm)\b",
    re.IGNORECASE,
)
_GUARANTEE_RE = re.compile(
    r"\b(?:guarantee(?:d|s)?|will\s+be\s+approved|approval\s+is\s+certain|"
    r"cannot\s+be\s+denied|legally\s+compliant|permit\s+outcome\s+guarantee)\b",
    re.IGNORECASE,
)

_MUTATION_FLAG_NAMES = {
    "active_prompt_mutation",
    "prompt_mutation_enabled",
    "mutate_prompts",
    "active_guardrail_mutation",
    "guardrail_mutation_enabled",
    "mutate_guardrails",
    "active_surface_registry_mutation",
    "surface_registry_mutation_enabled",
    "mutate_surface_registry",
    "active_monitoring_mutation",
    "monitoring_mutation_enabled",
    "mutate_monitoring",
    "active_release_state_mutation",
    "release_state_mutation_enabled",
    "mutate_release_state",
}

_CONSEQUENTIAL_CONTROL_NAMES = {
    "consequential_controls_enabled",
    "enable_consequential_controls",
    "allow_submit",
    "allow_submission",
    "allow_certification",
    "allow_upload",
    "allow_payment",
    "allow_schedule_inspection",
    "allow_cancellation",
    "allow_official_change",
    "submit_enabled",
    "payment_enabled",
    "upload_enabled",
    "certification_enabled",
    "scheduling_enabled",
}


def validate_guardrail_refresh_regression_review_packet(packet: Mapping[str, Any]) -> list[ReviewFinding]:
    """Return validation findings for a guardrail refresh review packet."""
    findings: list[ReviewFinding] = []

    affected_ids = _as_string_list(_first_present(packet, ("affected_guardrail_bundle_ids", "guardrail_bundle_ids", "affected_bundles")))
    if not affected_ids:
        findings.append(ReviewFinding("missing_affected_guardrail_bundle_ids", "$.affected_guardrail_bundle_ids", "At least one affected guardrail bundle ID is required."))
    for index, bundle_id in enumerate(affected_ids):
        if not _BUNDLE_ID_RE.match(bundle_id):
            findings.append(ReviewFinding("invalid_affected_guardrail_bundle_id", f"$.affected_guardrail_bundle_ids[{index}]", "Affected guardrail bundle IDs must be stable non-empty identifiers."))

    rollback_notes = _first_present(packet, ("rollback_notes", "rollback_plan", "rollback"))
    if not _has_text(rollback_notes):
        findings.append(ReviewFinding("missing_rollback_notes", "$.rollback_notes", "Rollback notes are required."))

    owners = _as_string_list(_first_present(packet, ("reviewer_owners", "review_owners", "owners", "reviewers")))
    if not owners:
        findings.append(ReviewFinding("missing_reviewer_owners", "$.reviewer_owners", "At least one reviewer owner is required."))

    commands = _first_present(packet, ("offline_validation_commands", "validation_commands"))
    if not _has_offline_command(commands):
        findings.append(ReviewFinding("missing_offline_validation_commands", "$.offline_validation_commands", "At least one offline validation command is required."))

    expectations = packet.get("expectations")
    if not isinstance(expectations, list) or not expectations:
        findings.append(ReviewFinding("missing_expectations", "$.expectations", "At least one cited expectation is required."))
    elif isinstance(expectations, list):
        for index, expectation in enumerate(expectations):
            citations = _first_present(expectation, ("citations", "source_evidence_ids", "evidence", "source_refs")) if isinstance(expectation, Mapping) else None
            if not _has_citation(citations):
                findings.append(ReviewFinding("uncited_expectation", f"$.expectations[{index}]", "Every expectation must carry at least one source citation or evidence ID."))

    for path, value in _walk(packet):
        lowered_key = _path_leaf(path).lower()
        if lowered_key in _MUTATION_FLAG_NAMES and value is True:
            findings.append(ReviewFinding("active_mutation_flag", path, "Prompt, guardrail, surface-registry, monitoring, and release-state mutation flags must be disabled."))
        if lowered_key in _CONSEQUENTIAL_CONTROL_NAMES and value is True:
            findings.append(ReviewFinding("enabled_consequential_control", path, "Consequential official-action controls must not be enabled in regression review packets."))
        if isinstance(value, str):
            _scan_text(path, value, findings)

    return findings


def assert_valid_guardrail_refresh_regression_review_packet(packet: Mapping[str, Any]) -> None:
    findings = validate_guardrail_refresh_regression_review_packet(packet)
    if findings:
        raise GuardrailRefreshRegressionReviewError(findings)


def _scan_text(path: str, value: str, findings: list[ReviewFinding]) -> None:
    if _PRIVATE_PATH_RE.search(value):
        findings.append(ReviewFinding("local_private_path", path, "Local private filesystem paths are not allowed."))
    if _PRIVATE_FACT_RE.search(value):
        findings.append(ReviewFinding("private_case_fact", path, "Private case facts are not allowed in committed review packets."))
    if _RAW_AUTH_RE.search(value):
        findings.append(ReviewFinding("raw_authenticated_value", path, "Raw authenticated values and credential material are not allowed."))
    if _LIVE_EXECUTION_RE.search(value):
        findings.append(ReviewFinding("live_execution_claim", path, "Review packets must not claim live LLM, DevHub, crawler, or processor execution."))
    if _GUARANTEE_RE.search(value):
        findings.append(ReviewFinding("outcome_guarantee", path, "Legal or permitting outcome guarantees are not allowed."))


def _first_present(mapping: Any, names: Iterable[str]) -> Any:
    if not isinstance(mapping, Mapping):
        return None
    for name in names:
        if name in mapping:
            return mapping[name]
    return None


def _has_text(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, Mapping):
        return any(_has_text(item) for item in value.values())
    if isinstance(value, list):
        return any(_has_text(item) for item in value)
    return False


def _as_string_list(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []
    if isinstance(value, Mapping):
        values: list[str] = []
        for key in ("owner", "name", "id", "bundle_id"):
            item = value.get(key)
            if isinstance(item, str) and item.strip():
                values.append(item.strip())
        return values
    if isinstance(value, list):
        values = []
        for item in value:
            values.extend(_as_string_list(item))
        return values
    return []


def _has_citation(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, Mapping):
        return any(_has_citation(value.get(key)) for key in ("source_evidence_id", "source_id", "citation", "url", "ref"))
    if isinstance(value, list):
        return any(_has_citation(item) for item in value)
    return False


def _has_offline_command(value: Any) -> bool:
    commands: list[str] = []
    if isinstance(value, str):
        commands = [value]
    elif isinstance(value, list):
        for item in value:
            if isinstance(item, str):
                commands.append(item)
            elif isinstance(item, list) and all(isinstance(part, str) and part.strip() for part in item):
                commands.append(" ".join(item))
    return any(command.strip() and not re.search(r"\b(?:curl|wget|devhub|playwright|browser|crawl|crawler|processor|llm)\b", command, re.IGNORECASE) for command in commands)


def _walk(value: Any, path: str = "$") -> Iterable[tuple[str, Any]]:
    yield path, value
    if isinstance(value, Mapping):
        for key, item in value.items():
            safe_key = str(key).replace("~", "~0").replace("/", "~1")
            yield from _walk(item, f"{path}.{safe_key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from _walk(item, f"{path}[{index}]")


def _path_leaf(path: str) -> str:
    leaf = path.rsplit(".", 1)[-1]
    if "[" in leaf:
        leaf = leaf.split("[", 1)[0]
    return leaf


__all__ = [
    "GuardrailRefreshRegressionReviewError",
    "ReviewFinding",
    "assert_valid_guardrail_refresh_regression_review_packet",
    "validate_guardrail_refresh_regression_review_packet",
]
