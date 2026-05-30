"""Validation for PP&D prompt consumer dry-run transcript packets.

The validator is intentionally deterministic and side-effect free. It inspects
committed packet dictionaries only; it never invokes LLMs, DevHub, browsers,
crawlers, processors, monitoring, or active prompt/release mutation paths.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import re
from typing import Any


PACKET_TYPE = "ppd.prompt_consumer_dry_run_transcript_packet.v1"

_CITATION_FIELDS = (
    "citation_ids",
    "citations",
    "source_evidence_ids",
    "source_refs",
    "citation_sources",
)
_EXPECTED_RESPONSE_FIELDS = (
    "expected_response",
    "expected_after",
    "expected",
    "expected_outcome",
    "response_expectation",
)
_REFUSAL_REFERENCE_FIELDS = (
    "refusal_reference_ids",
    "refusal_refs",
    "refused_action_predicate_refs",
    "refusal_source_evidence_ids",
)
_EXACT_CONFIRMATION_REFERENCE_FIELDS = (
    "exact_confirmation_reference_ids",
    "exact_confirmation_refs",
    "exact_confirmation_predicate_refs",
    "exact_confirmation_source_evidence_ids",
)

_PRIVATE_KEY_RE = re.compile(
    r"(private_case_fact|case_facts?|known_facts?|applicant|owner|tenant|contractor|email|phone|address|taxlot|permit_number|case_number|license|ssn|dob|payment|card|bank|routing)",
    re.IGNORECASE,
)
_RAW_AUTH_KEY_RE = re.compile(
    r"(cookie|session|token|authorization|auth[_-]?state|password|secret|credential|csrf|bearer|saml|oauth|mfa|raw_authenticated_values?)",
    re.IGNORECASE,
)
_RAW_AUTH_VALUE_RE = re.compile(
    r"(bearer\s+[a-z0-9._~-]+|cookie:|set-cookie:|sessionid=|access[_-]?token|refresh[_-]?token|password=|client_secret|auth_state\.json)",
    re.IGNORECASE,
)
_LOCAL_PRIVATE_PATH_RE = re.compile(
    r"(^|\s)(/home/[^\s'\"]+|/Users/[^\s'\"]+|/private/var/[^\s'\"]+|/tmp/[^\s'\"]+|[A-Za-z]:\\[^\s'\"]+|file://[^\s'\"]+|~/(?:[^\s'\"]+))"
)
_LIVE_EXECUTION_RE = re.compile(
    r"\b(live|actually|successfully|completed|executed|ran|called|invoked|opened|launched|queried|crawled|processed|logged in|authenticated)\b.{0,80}\b(llm|devhub|crawler|processor|playwright|browser|monitoring|devhub portal)\b|\b(llm|devhub|crawler|processor|playwright|browser|monitoring|devhub portal)\b.{0,80}\b(live|actually|successfully|completed|executed|ran|called|invoked|opened|launched|queried|crawled|processed|logged in|authenticated)\b",
    re.IGNORECASE,
)
_OUTCOME_GUARANTEE_RE = re.compile(
    r"\b(guarantee(?:d|s)?|will be approved|will receive (?:a )?permit|permit will issue|approval is assured|outcome is certain|legally sufficient|legally valid|compliant as a matter of law|no permitting risk|no legal risk|cannot be denied)\b",
    re.IGNORECASE,
)
_FINAL_ACTION_LANGUAGE_RE = re.compile(
    r"\b(i|we|the agent|consumer|assistant)\s+(?:will|can|did|have|has|successfully|now)\s+(?:submit|submitted|pay|paid|make payment|upload|uploaded|schedule|scheduled|cancel|cancelled|canceled)\b|\b(final submission|submit payment|submitted payment|final payment|official upload|uploaded to devhub|schedule inspection|cancel inspection|cancel permit|withdraw permit)\b",
    re.IGNORECASE,
)
_MUTATION_KEY_PARTS = (
    "prompt_mutation",
    "prompt-mutation",
    "guardrail_mutation",
    "guardrail-mutation",
    "surface_registry_mutation",
    "surface-registry-mutation",
    "monitoring_mutation",
    "monitoring-mutation",
    "release_state_mutation",
    "release-state-mutation",
    "agent_state_mutation",
    "agent-state-mutation",
)
_MUTATION_TRUE_WORDS = {"true", "enabled", "active", "allowed", "yes", "on"}
_EXPECTED_PUBLIC_PRIVATE_KEY_EXCEPTIONS = {
    "expected_response",
    "expected_after",
    "expected",
    "expected_outcome",
    "response_expectation",
}


@dataclass(frozen=True)
class PromptConsumerDryRunTranscriptFinding:
    code: str
    path: str
    message: str


@dataclass(frozen=True)
class PromptConsumerDryRunTranscriptValidationResult:
    findings: tuple[PromptConsumerDryRunTranscriptFinding, ...]

    @property
    def valid(self) -> bool:
        return not self.findings

    @property
    def errors(self) -> tuple[str, ...]:
        return tuple(finding.code for finding in self.findings)

    def codes(self) -> tuple[str, ...]:
        return self.errors

    def as_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "findings": [finding.__dict__ for finding in self.findings],
            "errors": list(self.errors),
        }


class PromptConsumerDryRunTranscriptValidationError(ValueError):
    def __init__(self, findings: Sequence[PromptConsumerDryRunTranscriptFinding]) -> None:
        self.findings = tuple(findings)
        detail = "; ".join(f"{finding.path}: {finding.code}" for finding in self.findings)
        super().__init__("invalid prompt consumer dry-run transcript packet: " + detail)


def validate_prompt_consumer_dry_run_transcript_packet(
    packet: Mapping[str, Any],
) -> PromptConsumerDryRunTranscriptValidationResult:
    """Return validation findings for a prompt consumer dry-run transcript packet."""

    findings: list[PromptConsumerDryRunTranscriptFinding] = []
    if not isinstance(packet, Mapping):
        return PromptConsumerDryRunTranscriptValidationResult(
            (PromptConsumerDryRunTranscriptFinding("packet_not_mapping", "$", "Packet must be a mapping."),)
        )

    if packet.get("packet_type") not in (PACKET_TYPE, None):
        _add(findings, "invalid_packet_type", "$.packet_type", "Unexpected prompt consumer dry-run transcript packet type.")

    _validate_dry_run_attestations(packet, findings)
    _validate_reference_sets(packet, findings)
    _validate_scenarios(packet, findings)
    _scan_payload(packet, "$", findings)
    return PromptConsumerDryRunTranscriptValidationResult(tuple(_dedupe_findings(findings)))


def assert_valid_prompt_consumer_dry_run_transcript_packet(packet: Mapping[str, Any]) -> None:
    result = validate_prompt_consumer_dry_run_transcript_packet(packet)
    if result.findings:
        raise PromptConsumerDryRunTranscriptValidationError(result.findings)


def require_prompt_consumer_dry_run_transcript_packet(packet: Mapping[str, Any]) -> None:
    assert_valid_prompt_consumer_dry_run_transcript_packet(packet)


def _validate_dry_run_attestations(packet: Mapping[str, Any], findings: list[PromptConsumerDryRunTranscriptFinding]) -> None:
    mode = str(packet.get("mode") or packet.get("run_mode") or "").lower()
    if "dry" not in mode and packet.get("fixture_only") is not True:
        _add(findings, "missing_dry_run_mode", "$.mode", "Packet must be fixture-only dry-run evidence.")
    for key in ("invokes_live_llm", "invokes_live_devhub", "invokes_browser", "invokes_crawler", "invokes_processor"):
        if packet.get(key) is True:
            _add(findings, "live_execution_claim", f"$.{key}", "Dry-run transcript must not invoke live execution paths.")


def _validate_reference_sets(packet: Mapping[str, Any], findings: list[PromptConsumerDryRunTranscriptFinding]) -> None:
    if not _has_any_field(packet, _REFUSAL_REFERENCE_FIELDS):
        _add(findings, "missing_refusal_references", "$", "Prompt consumer dry runs must cite refusal references.")
    if not _has_any_field(packet, _EXACT_CONFIRMATION_REFERENCE_FIELDS):
        _add(findings, "missing_exact_confirmation_references", "$", "Prompt consumer dry runs must cite exact-confirmation references.")


def _validate_scenarios(packet: Mapping[str, Any], findings: list[PromptConsumerDryRunTranscriptFinding]) -> None:
    scenarios = _scenario_rows(packet)
    if not scenarios:
        _add(findings, "missing_scenarios", "$.scenarios", "At least one prompt consumer scenario is required.")
        return
    for index, scenario in enumerate(scenarios):
        path = f"$.scenarios[{index}]"
        if not isinstance(scenario, Mapping):
            _add(findings, "invalid_scenario", path, "Scenario must be a mapping.")
            continue
        if not _nonempty_text(scenario.get("scenario_id") or scenario.get("id")):
            _add(findings, "missing_scenario_id", path, "Scenario requires a stable id.")
        expected = _expected_response(scenario)
        if not isinstance(expected, Mapping):
            _add(findings, "missing_expected_response", path, "Scenario requires an expected response mapping.")
            continue
        expected_path = f"{path}.expected_response"
        if not _has_text(expected):
            _add(findings, "missing_expected_response", expected_path, "Expected response requires user-visible text.")
        if not _has_citations(expected) and not _has_citations(scenario):
            _add(findings, "uncited_expected_response", expected_path, "Expected responses must cite source evidence.")
        if _looks_like_refusal_case(scenario, expected) and not _has_any_field(expected, _REFUSAL_REFERENCE_FIELDS) and not _has_any_field(scenario, _REFUSAL_REFERENCE_FIELDS):
            _add(findings, "missing_refusal_references", expected_path, "Refusal expected responses must cite refusal references.")
        if _looks_like_exact_confirmation_case(scenario, expected) and not _has_any_field(expected, _EXACT_CONFIRMATION_REFERENCE_FIELDS) and not _has_any_field(scenario, _EXACT_CONFIRMATION_REFERENCE_FIELDS):
            _add(findings, "missing_exact_confirmation_references", expected_path, "Exact-confirmation expected responses must cite exact-confirmation references.")


def _scenario_rows(packet: Mapping[str, Any]) -> list[Any]:
    for key in ("scenarios", "consumer_scenarios", "transcript_scenarios", "dry_run_scenarios"):
        value = packet.get(key)
        if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
            return list(value)
    return []


def _expected_response(scenario: Mapping[str, Any]) -> Any:
    for key in _EXPECTED_RESPONSE_FIELDS:
        if key in scenario:
            return scenario[key]
    return None


def _has_citations(value: Mapping[str, Any]) -> bool:
    return _has_any_field(value, _CITATION_FIELDS)


def _has_any_field(value: Mapping[str, Any], fields: Sequence[str]) -> bool:
    return any(_nonempty_sequence_or_text(value.get(field)) for field in fields)


def _has_text(value: Mapping[str, Any]) -> bool:
    for key in ("text", "answer", "message", "response", "outcome"):
        if _nonempty_text(value.get(key)):
            return True
    return False


def _looks_like_refusal_case(scenario: Mapping[str, Any], expected: Mapping[str, Any]) -> bool:
    text = _joined_text(scenario, expected)
    return "refusal" in text or "refuse" in text or "decline" in text or "blocked" in text


def _looks_like_exact_confirmation_case(scenario: Mapping[str, Any], expected: Mapping[str, Any]) -> bool:
    text = _joined_text(scenario, expected)
    return "exact confirmation" in text or "exact-confirmation" in text or "requires_confirmation" in text


def _joined_text(*values: Mapping[str, Any]) -> str:
    parts: list[str] = []
    for value in values:
        for item in value.values():
            if isinstance(item, str):
                parts.append(item.lower())
            elif isinstance(item, Sequence) and not isinstance(item, (str, bytes, bytearray)):
                parts.extend(str(child).lower() for child in item if isinstance(child, str))
    return " ".join(parts)


def _scan_payload(value: Any, path: str, findings: list[PromptConsumerDryRunTranscriptFinding]) -> None:
    if isinstance(value, Mapping):
        for raw_key, child in value.items():
            key = str(raw_key)
            child_path = f"{path}.{key}" if path != "$" else f"$.{key}"
            lowered = key.lower()
            if _is_active_mutation_flag(lowered, child):
                _add(findings, "active_mutation_flag", child_path, "Prompt, guardrail, surface-registry, monitoring, release-state, and agent-state mutation flags must be inactive.")
            if _RAW_AUTH_KEY_RE.search(key) and _has_value(child):
                _add(findings, "raw_authenticated_value", child_path, "Raw authenticated values are not allowed.")
            if _PRIVATE_KEY_RE.search(key) and _has_value(child) and lowered not in _EXPECTED_PUBLIC_PRIVATE_KEY_EXCEPTIONS:
                _add(findings, "private_case_fact", child_path, "Private case facts are not allowed.")
            _scan_payload(child, child_path, findings)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            _scan_payload(child, f"{path}[{index}]", findings)
    elif isinstance(value, str):
        if _RAW_AUTH_VALUE_RE.search(value):
            _add(findings, "raw_authenticated_value", path, "Raw authenticated values are not allowed.")
        if _LOCAL_PRIVATE_PATH_RE.search(value):
            _add(findings, "local_private_path", path, "Local private paths are not allowed.")
        if "private case fact" in value.lower():
            _add(findings, "private_case_fact", path, "Private case facts are not allowed.")
        if _LIVE_EXECUTION_RE.search(value):
            _add(findings, "live_execution_claim", path, "Live LLM, DevHub, browser, crawler, or processor execution claims are not allowed.")
        if _OUTCOME_GUARANTEE_RE.search(value):
            _add(findings, "outcome_guarantee", path, "Legal or permitting outcome guarantees are not allowed.")
        if _FINAL_ACTION_LANGUAGE_RE.search(value):
            _add(findings, "final_consequential_action_language", path, "Final submission, payment, upload, scheduling, and cancellation language is not allowed.")


def _is_active_mutation_flag(key: str, value: Any) -> bool:
    if not any(part in key for part in _MUTATION_KEY_PARTS):
        return False
    if value is True:
        return True
    if isinstance(value, str) and value.strip().lower() in _MUTATION_TRUE_WORDS:
        return True
    if isinstance(value, Mapping):
        return value.get("enabled") is True or value.get("active") is True
    return False


def _has_value(value: Any) -> bool:
    if value in (None, False, "", [], {}):
        return False
    if isinstance(value, Mapping):
        return any(_has_value(item) for item in value.values())
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return any(_has_value(item) for item in value)
    return True


def _nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _nonempty_sequence_or_text(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return any(str(item).strip() for item in value)
    return False


def _add(findings: list[PromptConsumerDryRunTranscriptFinding], code: str, path: str, message: str) -> None:
    findings.append(PromptConsumerDryRunTranscriptFinding(code, path, message))


def _dedupe_findings(findings: Sequence[PromptConsumerDryRunTranscriptFinding]) -> list[PromptConsumerDryRunTranscriptFinding]:
    seen: set[tuple[str, str]] = set()
    result: list[PromptConsumerDryRunTranscriptFinding] = []
    for finding in findings:
        key = (finding.code, finding.path)
        if key not in seen:
            seen.add(key)
            result.append(finding)
    return result


__all__ = [
    "PACKET_TYPE",
    "PromptConsumerDryRunTranscriptFinding",
    "PromptConsumerDryRunTranscriptValidationError",
    "PromptConsumerDryRunTranscriptValidationResult",
    "assert_valid_prompt_consumer_dry_run_transcript_packet",
    "require_prompt_consumer_dry_run_transcript_packet",
    "validate_prompt_consumer_dry_run_transcript_packet",
]
