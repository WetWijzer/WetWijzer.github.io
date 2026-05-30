"""Validation for PP&D agent consumer post-release smoke transcript packets.

The validator is deterministic and side-effect free. It only inspects committed
packet mappings and never invokes LLMs, DevHub, crawlers, processors, monitoring,
or any active mutation pathway.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import re
from typing import Any


PACKET_TYPE = "ppd.agent_consumer_post_release_smoke_transcript_packet.v1"

_CITATION_FIELDS = ("citations", "citation_ids", "source_evidence_ids", "source_refs")
_TEXT_FIELDS = ("text", "answer", "message", "observed_text", "response")

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
_LOCAL_PATH_RE = re.compile(
    r"(^|\s)(/home/[^\s'\"]+|/Users/[^\s'\"]+|/private/var/[^\s'\"]+|/tmp/[^\s'\"]+|[A-Za-z]:\\[^\s'\"]+|file://[^\s'\"]+|~/(?:[^\s'\"]+))"
)
_LIVE_EXECUTION_RE = re.compile(
    r"\b(live|actually|successfully|completed|executed|ran|called|invoked|opened|launched|queried|crawled|processed|logged in|authenticated)\b.{0,80}\b(llm|devhub|crawler|processor|playwright|browser|monitoring|devhub portal)\b|\b(llm|devhub|crawler|processor|playwright|browser|monitoring|devhub portal)\b.{0,80}\b(live|actually|successfully|completed|executed|ran|called|invoked|opened|launched|queried|crawled|processed|logged in|authenticated)\b",
    re.IGNORECASE,
)
_GUARANTEE_RE = re.compile(
    r"\b(guarantee(?:d|s)?|will be approved|will receive (?:a )?permit|permit will issue|approval is assured|outcome is certain|legally sufficient|legally valid|compliant as a matter of law|no permitting risk|no legal risk|cannot be denied)\b",
    re.IGNORECASE,
)

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
    "scheduling",
    "cancel",
    "withdraw",
    "official",
    "consequential",
    "financial",
}
_MUTATION_KEY_PARTS = (
    "prompt_mutation",
    "guardrail_mutation",
    "surface_registry_mutation",
    "surface-registry-mutation",
    "monitoring_mutation",
    "agent_state_mutation",
    "agent-state-mutation",
)
_MUTATION_TRUE_WORDS = {"true", "enabled", "active", "allowed", "yes"}


@dataclass(frozen=True)
class PostReleaseSmokeTranscriptFinding:
    code: str
    path: str
    message: str


@dataclass(frozen=True)
class PostReleaseSmokeTranscriptValidationResult:
    findings: tuple[PostReleaseSmokeTranscriptFinding, ...]

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


class PostReleaseSmokeTranscriptValidationError(ValueError):
    def __init__(self, findings: Sequence[PostReleaseSmokeTranscriptFinding]) -> None:
        self.findings = tuple(findings)
        detail = "; ".join(f"{finding.path}: {finding.code}" for finding in self.findings)
        super().__init__("invalid agent consumer post-release smoke transcript packet: " + detail)


def validate_agent_consumer_post_release_smoke_transcript_packet(
    packet: Mapping[str, Any],
) -> PostReleaseSmokeTranscriptValidationResult:
    """Return validation findings for a post-release smoke transcript packet."""

    findings: list[PostReleaseSmokeTranscriptFinding] = []
    if not isinstance(packet, Mapping):
        return PostReleaseSmokeTranscriptValidationResult(
            (PostReleaseSmokeTranscriptFinding("packet_not_mapping", "$", "Packet must be a mapping."),)
        )

    if packet.get("packet_type") not in (PACKET_TYPE, None):
        _add(findings, "invalid_packet_type", "$.packet_type", "Unexpected post-release smoke transcript packet type.")

    _validate_reviewer_owners(packet.get("reviewer_owners"), findings)
    _validate_consumer_scenarios(_scenario_rows(packet), findings)
    _validate_reversible_boundaries(packet, findings)
    _validate_blocked_action_messages(packet, findings)
    _validate_controls(packet.get("consequential_controls") or packet.get("controls"), findings)
    _scan_payload(packet, "$", findings)
    return PostReleaseSmokeTranscriptValidationResult(tuple(_dedupe_findings(findings)))


def assert_valid_agent_consumer_post_release_smoke_transcript_packet(packet: Mapping[str, Any]) -> None:
    result = validate_agent_consumer_post_release_smoke_transcript_packet(packet)
    if result.findings:
        raise PostReleaseSmokeTranscriptValidationError(result.findings)


def require_agent_consumer_post_release_smoke_transcript_packet(packet: Mapping[str, Any]) -> None:
    assert_valid_agent_consumer_post_release_smoke_transcript_packet(packet)


def build_agent_consumer_post_release_smoke_transcript_packet(inputs: Mapping[str, Any]) -> dict[str, Any]:
    """Build a minimal deterministic packet from fixture inputs and validate it."""

    packet = {
        "packet_type": PACKET_TYPE,
        "packet_id": str(inputs.get("packet_id") or "fixture-agent-consumer-post-release-smoke-transcript"),
        "fixture_only": True,
        "offline_only": True,
        "consumer_scenarios": list(_scenario_rows(inputs)),
        "reversible_draft_preview_boundaries": list(inputs.get("reversible_draft_preview_boundaries") or []),
        "blocked_action_messages": list(inputs.get("blocked_action_messages") or []),
        "reviewer_owners": list(inputs.get("reviewer_owners") or []),
        "consequential_controls": list(inputs.get("consequential_controls") or []),
        "mutation_flags": dict(inputs.get("mutation_flags") or {}),
    }
    assert_valid_agent_consumer_post_release_smoke_transcript_packet(packet)
    return packet


def _validate_consumer_scenarios(scenarios: Sequence[Mapping[str, Any]], findings: list[PostReleaseSmokeTranscriptFinding]) -> None:
    if not scenarios:
        _add(findings, "missing_consumer_scenarios", "$.consumer_scenarios", "Consumer scenarios are required.")
        return
    for index, scenario in enumerate(scenarios):
        path = f"$.consumer_scenarios[{index}]"
        if not _has_citations(scenario):
            _add(findings, "uncited_consumer_scenario", path, "Consumer scenario must cite source evidence.")
        if not _nonempty_text(scenario.get("scenario_id") or scenario.get("id")):
            _add(findings, "missing_consumer_scenario_id", path, "Consumer scenario requires a stable id.")
        if not _nonempty_text(scenario.get("reviewer_owner")):
            _add(findings, "missing_reviewer_owner", f"{path}.reviewer_owner", "Consumer scenario requires a reviewer owner.")
        response = scenario.get("observed_safe_read_only_response") or scenario.get("observed_read_only_response")
        if not isinstance(response, Mapping) or not _has_text(response) or not _has_citations(response):
            _add(
                findings,
                "missing_observed_safe_read_only_response",
                f"{path}.observed_safe_read_only_response",
                "Scenario requires an observed cited safe-read-only response.",
            )


def _validate_reviewer_owners(value: Any, findings: list[PostReleaseSmokeTranscriptFinding]) -> None:
    owners = _mapping_sequence(value)
    if not owners:
        _add(findings, "missing_reviewer_owners", "$.reviewer_owners", "At least one reviewer owner is required.")
        return
    for index, owner in enumerate(owners):
        path = f"$.reviewer_owners[{index}]"
        if not _nonempty_text(owner.get("owner") or owner.get("owner_id") or owner.get("reviewer_owner")):
            _add(findings, "missing_reviewer_owner", path, "Reviewer owner id is required.")
        if not _nonempty_text(owner.get("review_scope") or owner.get("role") or owner.get("review_area")):
            _add(findings, "missing_reviewer_owner", path, "Reviewer owner scope or role is required.")


def _validate_reversible_boundaries(packet: Mapping[str, Any], findings: list[PostReleaseSmokeTranscriptFinding]) -> None:
    boundaries = _mapping_sequence(
        packet.get("reversible_draft_preview_boundaries")
        or packet.get("draft_preview_boundaries")
        or packet.get("reversible_draft_boundaries")
    )
    if not boundaries:
        _add(
            findings,
            "missing_reversible_draft_preview_boundary",
            "$.reversible_draft_preview_boundaries",
            "Reversible draft-preview boundaries are required.",
        )
        return
    for index, boundary in enumerate(boundaries):
        path = f"$.reversible_draft_preview_boundaries[{index}]"
        for field in ("allowed_preview_only_actions", "blocked_boundary_actions", "stop_before"):
            if not _nonempty_sequence_or_text(boundary.get(field)):
                _add(findings, "missing_reversible_draft_preview_boundary", f"{path}.{field}", f"{field} is required.")
        if not _has_citations(boundary):
            _add(findings, "uncited_reversible_draft_preview_boundary", path, "Draft-preview boundary must cite evidence.")


def _validate_blocked_action_messages(packet: Mapping[str, Any], findings: list[PostReleaseSmokeTranscriptFinding]) -> None:
    messages = _mapping_sequence(packet.get("blocked_action_messages") or packet.get("blocked_actions"))
    if not messages:
        _add(findings, "missing_blocked_action_message", "$.blocked_action_messages", "Blocked-action messages are required.")
        return
    for index, message in enumerate(messages):
        path = f"$.blocked_action_messages[{index}]"
        if not _has_text(message):
            _add(findings, "missing_blocked_action_message", path, "Blocked action requires a user-visible message.")
        if not _has_citations(message):
            _add(findings, "uncited_blocked_action_message", path, "Blocked action message must cite source evidence.")


def _validate_controls(value: Any, findings: list[PostReleaseSmokeTranscriptFinding]) -> None:
    if value is None:
        return
    controls = value.values() if isinstance(value, Mapping) else value
    if not isinstance(controls, Sequence) or isinstance(controls, (str, bytes, bytearray)):
        _add(findings, "invalid_consequential_controls", "$.consequential_controls", "Controls must be a list or mapping.")
        return
    for index, control in enumerate(controls):
        if not isinstance(control, Mapping):
            continue
        label = " ".join(str(control.get(key, "")) for key in ("id", "name", "label", "action", "kind", "category", "scope")).lower()
        enabled = control.get("enabled") is True or str(control.get("state") or "").lower() in {"enabled", "active", "available", "allowed"}
        if enabled and any(word in label for word in _CONSEQUENTIAL_WORDS):
            _add(findings, "enabled_consequential_control", f"$.consequential_controls[{index}]", "Consequential controls must be disabled.")


def _scan_payload(value: Any, path: str, findings: list[PostReleaseSmokeTranscriptFinding]) -> None:
    if isinstance(value, Mapping):
        for raw_key, child in value.items():
            key = str(raw_key)
            child_path = f"{path}.{key}" if path != "$" else f"$.{key}"
            lowered = key.lower()
            if _is_active_mutation_flag(lowered, child):
                _add(findings, "active_mutation_flag", child_path, "Prompt, guardrail, surface-registry, monitoring, and agent-state mutation flags must be inactive.")
            if _RAW_AUTH_KEY_RE.search(key) and _has_value(child):
                _add(findings, "raw_authenticated_value", child_path, "Raw authenticated values are not allowed.")
            if _PRIVATE_KEY_RE.search(key) and _has_value(child) and not _is_expected_public_field(lowered):
                _add(findings, "private_case_fact", child_path, "Private case facts are not allowed.")
            _scan_payload(child, child_path, findings)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            _scan_payload(child, f"{path}[{index}]", findings)
    elif isinstance(value, str):
        if _RAW_AUTH_VALUE_RE.search(value):
            _add(findings, "raw_authenticated_value", path, "Raw authenticated values are not allowed.")
        if _LOCAL_PATH_RE.search(value):
            _add(findings, "local_private_path", path, "Local private paths are not allowed.")
        if "private case fact" in value.lower():
            _add(findings, "private_case_fact", path, "Private case facts are not allowed.")
        if _LIVE_EXECUTION_RE.search(value):
            _add(findings, "live_execution_claim", path, "Live LLM, DevHub, crawler, processor, or monitoring execution claims are not allowed.")
        if _GUARANTEE_RE.search(value):
            _add(findings, "outcome_guarantee", path, "Legal or permitting outcome guarantees are not allowed.")


def _scenario_rows(packet: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    for key in ("consumer_scenarios", "post_release_consumer_scenarios", "smoke_scenarios", "scenarios"):
        rows = _mapping_sequence(packet.get(key))
        if rows:
            return rows
    return []


def _has_citations(value: Mapping[str, Any]) -> bool:
    return any(_nonempty_sequence_or_text(value.get(field)) for field in _CITATION_FIELDS)


def _has_text(value: Mapping[str, Any]) -> bool:
    return any(_nonempty_text(value.get(field)) for field in _TEXT_FIELDS)


def _mapping_sequence(value: Any) -> list[Mapping[str, Any]]:
    if isinstance(value, Mapping):
        return [value]
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [item for item in value if isinstance(item, Mapping)]
    return []


def _nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _nonempty_sequence_or_text(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return any(str(item).strip() for item in value)
    return False


def _has_value(value: Any) -> bool:
    if value in (None, False, "", [], {}):
        return False
    if isinstance(value, Mapping):
        return any(_has_value(item) for item in value.values())
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return any(_has_value(item) for item in value)
    return True


def _is_expected_public_field(key: str) -> bool:
    return key in {"observed_safe_read_only_response", "observed_read_only_response", "expected_read_only_answer"}


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


def _add(findings: list[PostReleaseSmokeTranscriptFinding], code: str, path: str, message: str) -> None:
    findings.append(PostReleaseSmokeTranscriptFinding(code, path, message))


def _dedupe_findings(findings: Sequence[PostReleaseSmokeTranscriptFinding]) -> list[PostReleaseSmokeTranscriptFinding]:
    seen: set[tuple[str, str]] = set()
    result: list[PostReleaseSmokeTranscriptFinding] = []
    for finding in findings:
        key = (finding.code, finding.path)
        if key not in seen:
            seen.add(key)
            result.append(finding)
    return result


__all__ = [
    "PACKET_TYPE",
    "PostReleaseSmokeTranscriptFinding",
    "PostReleaseSmokeTranscriptValidationError",
    "PostReleaseSmokeTranscriptValidationResult",
    "assert_valid_agent_consumer_post_release_smoke_transcript_packet",
    "build_agent_consumer_post_release_smoke_transcript_packet",
    "require_agent_consumer_post_release_smoke_transcript_packet",
    "validate_agent_consumer_post_release_smoke_transcript_packet",
]
