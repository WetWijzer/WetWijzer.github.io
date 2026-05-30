"""Validation for PP&D agent consumer release handoff packets.

The validator is intentionally deterministic and side-effect free. It accepts a
plain mapping so release producers can validate serialized JSON before exposing
capabilities to agent consumers.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Iterable, Mapping, Sequence


@dataclass(frozen=True)
class HandoffValidationFinding:
    code: str
    path: str
    message: str


class HandoffValidationError(ValueError):
    def __init__(self, findings: Sequence[HandoffValidationFinding]) -> None:
        self.findings = tuple(findings)
        super().__init__("agent consumer release handoff packet failed validation")


_PRIVATE_KEY_RE = re.compile(
    r"(cookie|credential|password|secret|session|token|auth[_-]?state|har|trace|screenshot|payment|card|ssn|dob)",
    re.IGNORECASE,
)
_PRIVATE_VALUE_RE = re.compile(
    r"(bearer\s+[a-z0-9._~-]+|cookie:|set-cookie:|sessionid=|access[_-]?token|refresh[_-]?token|password=|client_secret)",
    re.IGNORECASE,
)
_PRIVATE_FACT_RE = re.compile(
    r"(owner\s+date\s+of\s+birth|date\s+of\s+birth|ssn|social\s+security|credit\s+card|bank\s+account|private\s+case\s+fact|tenant\s+name|applicant\s+phone|applicant\s+email)",
    re.IGNORECASE,
)
_LOCAL_PATH_RE = re.compile(
    r"(^|\s)(/home/[^\s]+|/Users/[^\s]+|/private/var/[^\s]+|[A-Za-z]:\\[^\s]+|file://[^\s]+|~/(?:[^\s]+))"
)
_LIVE_EXECUTION_RE = re.compile(
    r"\b(live|actually|successfully|completed|executed|ran|called|invoked)\b.{0,60}\b(llm|devhub|crawler|processor|playwright|browser|automation)\b|\b(llm|devhub|crawler|processor|playwright|browser|automation)\b.{0,60}\b(live|actually|successfully|completed|executed|ran|called|invoked)\b",
    re.IGNORECASE,
)
_GUARANTEE_RE = re.compile(
    r"\b(guarantee|guaranteed|will\s+be\s+approved|will\s+receive\s+(?:a\s+)?permit|approval\s+is\s+assured|permit\s+outcome\s+is\s+certain|legally\s+valid|compliant\s+as\s+a\s+matter\s+of\s+law)\b",
    re.IGNORECASE,
)

_MUTATION_FLAG_KEYS = {
    "active_prompt_mutation",
    "prompt_mutation_enabled",
    "active_guardrail_mutation",
    "guardrail_mutation_enabled",
    "active_surface_registry_mutation",
    "surface_registry_mutation_enabled",
    "active_agent_state_mutation",
    "agent_state_mutation_enabled",
}

_CONSEQUENTIAL_WORDS = {
    "submit",
    "submission",
    "certify",
    "certification",
    "upload",
    "payment",
    "pay",
    "purchase",
    "schedule",
    "cancel",
    "withdraw",
    "official_record",
    "consequential",
    "financial",
}


def validate_agent_consumer_release_handoff_packet(packet: Mapping[str, Any]) -> list[HandoffValidationFinding]:
    """Return validation findings for an agent consumer release handoff packet."""

    findings: list[HandoffValidationFinding] = []
    if not isinstance(packet, Mapping):
        return [
            HandoffValidationFinding(
                "packet_not_mapping",
                "$",
                "Release handoff packet must be a JSON object mapping.",
            )
        ]

    _validate_capability_claims(packet.get("capability_claims"), findings)
    _validate_scenarios(packet.get("supported_scenarios"), "supported_scenarios", findings)
    _validate_scenarios(packet.get("blocked_scenarios"), "blocked_scenarios", findings)
    _validate_reversible_draft_boundaries(packet.get("reversible_draft_boundaries"), findings)
    _validate_reviewer_owners(packet.get("reviewer_owners"), findings)
    _validate_controls(packet.get("controls"), findings)
    _validate_mutation_flags(packet, findings)
    _scan_payload(packet, "$", findings)
    return findings


def assert_valid_agent_consumer_release_handoff_packet(packet: Mapping[str, Any]) -> None:
    findings = validate_agent_consumer_release_handoff_packet(packet)
    if findings:
        raise HandoffValidationError(findings)


def _validate_capability_claims(value: Any, findings: list[HandoffValidationFinding]) -> None:
    if not isinstance(value, list) or not value:
        findings.append(HandoffValidationFinding("missing_capability_claims", "$.capability_claims", "At least one cited capability claim is required."))
        return
    for index, claim in enumerate(value):
        path = f"$.capability_claims[{index}]"
        if not isinstance(claim, Mapping):
            findings.append(HandoffValidationFinding("invalid_capability_claim", path, "Capability claim must be an object."))
            continue
        if not _has_citations(claim):
            findings.append(HandoffValidationFinding("uncited_capability_claim", path, "Capability claims must include source citation identifiers."))


def _validate_scenarios(value: Any, field: str, findings: list[HandoffValidationFinding]) -> None:
    path = f"$.{field}"
    if not isinstance(value, list) or not value:
        findings.append(HandoffValidationFinding(f"missing_{field}", path, f"{field} must include at least one cited scenario."))
        return
    for index, scenario in enumerate(value):
        item_path = f"{path}[{index}]"
        if not isinstance(scenario, Mapping):
            findings.append(HandoffValidationFinding("invalid_scenario", item_path, "Scenario must be an object."))
            continue
        if not scenario.get("id"):
            findings.append(HandoffValidationFinding("missing_scenario_id", item_path, "Scenario must include a stable id."))
        if not _has_citations(scenario):
            findings.append(HandoffValidationFinding("uncited_scenario", item_path, "Scenario must include source citation identifiers."))


def _validate_reversible_draft_boundaries(value: Any, findings: list[HandoffValidationFinding]) -> None:
    path = "$.reversible_draft_boundaries"
    if not isinstance(value, Mapping):
        findings.append(HandoffValidationFinding("missing_reversible_draft_boundaries", path, "Reversible draft boundaries are required."))
        return
    for field in ("allowed_scope", "prohibited_scope", "stop_before"):
        if not _non_empty_sequence_or_string(value.get(field)):
            findings.append(HandoffValidationFinding("incomplete_reversible_draft_boundaries", f"{path}.{field}", f"{field} must be populated."))


def _validate_reviewer_owners(value: Any, findings: list[HandoffValidationFinding]) -> None:
    path = "$.reviewer_owners"
    if not isinstance(value, list) or not value:
        findings.append(HandoffValidationFinding("missing_reviewer_owners", path, "Release packet must identify reviewer owners."))
        return
    for index, owner in enumerate(value):
        item_path = f"{path}[{index}]"
        if not isinstance(owner, Mapping):
            findings.append(HandoffValidationFinding("invalid_reviewer_owner", item_path, "Reviewer owner must be an object."))
            continue
        if not owner.get("owner") or not owner.get("review_area"):
            findings.append(HandoffValidationFinding("incomplete_reviewer_owner", item_path, "Reviewer owner must include owner and review_area."))


def _validate_controls(value: Any, findings: list[HandoffValidationFinding]) -> None:
    if value is None:
        return
    controls: Iterable[Any]
    if isinstance(value, Mapping):
        controls = value.values()
    elif isinstance(value, list):
        controls = value
    else:
        findings.append(HandoffValidationFinding("invalid_controls", "$.controls", "Controls must be an object or list."))
        return
    for index, control in enumerate(controls):
        if not isinstance(control, Mapping):
            continue
        enabled = control.get("enabled") is True or str(control.get("state", "")).lower() == "enabled"
        label = " ".join(str(control.get(key, "")) for key in ("id", "name", "kind", "action_type", "category", "scope")).lower()
        if enabled and any(word in label for word in _CONSEQUENTIAL_WORDS):
            findings.append(HandoffValidationFinding("enabled_consequential_control", f"$.controls[{index}]", "Consequential or financial controls must not be enabled in release handoff packets."))


def _validate_mutation_flags(packet: Mapping[str, Any], findings: list[HandoffValidationFinding]) -> None:
    for key in _MUTATION_FLAG_KEYS:
        if packet.get(key) is True:
            findings.append(HandoffValidationFinding("active_mutation_flag", f"$.{key}", "Prompt, guardrail, surface-registry, and agent-state mutation flags must be inactive."))
    flags = packet.get("mutation_flags")
    if isinstance(flags, Mapping):
        for key, value in flags.items():
            normalized_key = str(key).lower()
            if value is True and any(part in normalized_key for part in ("prompt", "guardrail", "surface", "registry", "agent_state", "agent-state")):
                findings.append(HandoffValidationFinding("active_mutation_flag", f"$.mutation_flags.{key}", "Mutation flags must be inactive."))


def _scan_payload(value: Any, path: str, findings: list[HandoffValidationFinding]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            child_path = f"{path}.{key_text}"
            if _PRIVATE_KEY_RE.search(key_text):
                findings.append(HandoffValidationFinding("private_or_authenticated_key", child_path, "Release packet must not contain private, payment, session, credential, trace, or raw authenticated fields."))
            _scan_payload(child, child_path, findings)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _scan_payload(child, f"{path}[{index}]", findings)
    elif isinstance(value, str):
        if _PRIVATE_VALUE_RE.search(value):
            findings.append(HandoffValidationFinding("raw_authenticated_value", path, "Release packet must not include raw authenticated values."))
        if _PRIVATE_FACT_RE.search(value):
            findings.append(HandoffValidationFinding("private_case_fact", path, "Release packet must not include private case facts."))
        if _LOCAL_PATH_RE.search(value):
            findings.append(HandoffValidationFinding("local_private_path", path, "Release packet must not include local private paths."))
        if _LIVE_EXECUTION_RE.search(value):
            findings.append(HandoffValidationFinding("live_execution_claim", path, "Release packet must not claim live LLM, DevHub, crawler, browser, or processor execution."))
        if _GUARANTEE_RE.search(value):
            findings.append(HandoffValidationFinding("outcome_guarantee", path, "Release packet must not guarantee legal or permitting outcomes."))


def _has_citations(value: Mapping[str, Any]) -> bool:
    for key in ("citation_ids", "source_evidence_ids", "references", "citations"):
        citations = value.get(key)
        if isinstance(citations, str) and citations.strip():
            return True
        if isinstance(citations, Sequence) and not isinstance(citations, (str, bytes)) and any(str(item).strip() for item in citations):
            return True
    return False


def _non_empty_sequence_or_string(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return any(str(item).strip() for item in value)
    return False
