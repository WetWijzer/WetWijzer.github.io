"""Fixture-first guarded agent readiness delta packet v2.

Consumes guardrail impact replay plan v2 fixtures and emits agent-facing schema
placeholder deltas only. This module does not change active prompts, production
agent contracts, source artifacts, DevHub surfaces, guardrails, release state,
or any official workflow state.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from ppd.agent_readiness.guardrail_impact_replay_plan_v2 import (
    PLAN_TYPE as GUARDRAIL_IMPACT_REPLAY_PLAN_TYPE,
    PLAN_VERSION as GUARDRAIL_IMPACT_REPLAY_PLAN_VERSION,
    assert_valid_guardrail_impact_replay_plan_v2,
)

PACKET_TYPE = "ppd.agent_readiness_delta_packet.v2"
PACKET_VERSION = "v2"
CONSUMED_PLAN_TYPE = GUARDRAIL_IMPACT_REPLAY_PLAN_TYPE
CONSUMED_PLAN_VERSION = GUARDRAIL_IMPACT_REPLAY_PLAN_VERSION

EXACT_OFFLINE_VALIDATION_COMMANDS = [
    ["python3", "-m", "py_compile", "ppd/agent_readiness/agent_readiness_delta_packet_v2.py"],
    ["python3", "-m", "pytest", "ppd/tests/test_agent_readiness_delta_packet_v2.py"],
    ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
]

_REQUIRED_ATTESTATIONS = {
    "fixture_first": True,
    "offline_only": True,
    "consumes_guardrail_impact_replay_plan_v2": True,
    "active_prompts_changed": False,
    "production_agent_contracts_changed": False,
    "public_source_artifacts_changed": False,
    "devhub_surfaces_changed": False,
    "release_state_changed": False,
    "live_crawl_performed": False,
    "devhub_accessed": False,
    "official_action_performed": False,
}

_AGENT_SCHEMA_DELTA_FIELDS = (
    "agent_schema_delta_placeholders",
    "missing_information_prompt_expectations",
    "blocked_action_explanation_expectations",
    "reversible_draft_preview_expectations",
    "citation_coverage_placeholders",
    "reviewer_acceptance_placeholders",
)

_MUTATION_KEYS = {
    "active_prompt_mutation",
    "active_release_state_mutation",
    "active_source_artifact_mutation",
    "active_surface_mutation",
    "agent_contract_mutation",
    "devhub_surface_mutation",
    "production_contract_mutation",
    "prompt_mutation",
    "release_state_mutation",
    "source_artifact_mutation",
}

_PRIVATE_OR_LIVE_KEY_TOKENS = (
    "auth",
    "browser",
    "cookie",
    "credential",
    "download",
    "har",
    "local_path",
    "mfa",
    "password",
    "payment",
    "screenshot",
    "secret",
    "session",
    "storage_state",
    "token",
    "trace",
)

_FORBIDDEN_TEXT_TOKENS = (
    "approval guaranteed",
    "bypass captcha",
    "credential",
    "legal advice",
    "live devhub",
    "open browser",
    "password",
    "payment detail",
    "permit guaranteed",
    "raw crawl",
    "screenshot",
    "session state",
)


@dataclass(frozen=True)
class AgentReadinessDeltaPacketV2ValidationResult:
    valid: bool
    problems: tuple[str, ...]


class AgentReadinessDeltaPacketV2Error(ValueError):
    def __init__(self, problems: Iterable[str]) -> None:
        self.problems = tuple(problems)
        super().__init__("invalid agent readiness delta packet v2: " + "; ".join(self.problems))


def build_agent_readiness_delta_packet_v2(plan: Mapping[str, Any]) -> dict[str, Any]:
    """Build guarded agent-facing delta placeholders from replay plan v2."""

    assert_valid_guardrail_impact_replay_plan_v2(plan)
    cases = _mapping_sequence(plan.get("ordered_replay_cases"))

    packet = {
        "packet_type": PACKET_TYPE,
        "packet_version": PACKET_VERSION,
        "packet_id": f"agent-readiness-delta-packet-v2-for-{_text(plan.get('plan_id'), 'guardrail-impact-replay-plan-v2')}",
        "fixture_first": True,
        "offline_only": True,
        "consumes": [
            {
                "plan_type": _text(plan.get("plan_type")),
                "plan_version": _text(plan.get("plan_version")),
                "plan_id": _text(plan.get("plan_id")),
            }
        ],
        "agent_schema_delta_placeholders": [_schema_delta_placeholder(case) for case in cases],
        "missing_information_prompt_expectations": [
            _missing_information_prompt_expectation(case)
            for case in cases
            if case.get("expected_outcome") == "escalate"
        ],
        "blocked_action_explanation_expectations": [
            _blocked_action_explanation_expectation(case)
            for case in cases
            if case.get("expected_outcome") == "block"
        ],
        "reversible_draft_preview_expectations": [
            _reversible_draft_preview_expectation(case)
            for case in cases
            if case.get("expected_outcome") == "allow"
        ],
        "citation_coverage_placeholders": _citation_coverage_placeholders(cases),
        "reviewer_acceptance_placeholders": [_reviewer_acceptance_placeholder(case) for case in cases],
        "attestations": dict(_REQUIRED_ATTESTATIONS),
        "prompt_changes": [],
        "production_agent_contract_changes": [],
        "public_source_artifact_changes": [],
        "devhub_surface_changes": [],
        "release_state_changes": [],
        "exact_offline_validation_commands": [list(command) for command in EXACT_OFFLINE_VALIDATION_COMMANDS],
    }
    assert_valid_agent_readiness_delta_packet_v2(packet)
    return packet


def validate_agent_readiness_delta_packet_v2(packet: Mapping[str, Any]) -> AgentReadinessDeltaPacketV2ValidationResult:
    problems: list[str] = []
    if not isinstance(packet, Mapping):
        return AgentReadinessDeltaPacketV2ValidationResult(False, ("packet must be an object",))

    if packet.get("packet_type") != PACKET_TYPE:
        problems.append(f"packet_type must be {PACKET_TYPE}")
    if packet.get("packet_version") != PACKET_VERSION:
        problems.append("packet_version must be v2")
    if packet.get("fixture_first") is not True:
        problems.append("fixture_first must be true")
    if packet.get("offline_only") is not True:
        problems.append("offline_only must be true")

    consumed = _mapping_sequence(packet.get("consumes"))
    if len(consumed) != 1:
        problems.append("consumes must contain exactly one guardrail impact replay plan reference")
    else:
        plan_ref = consumed[0]
        if plan_ref.get("plan_type") != CONSUMED_PLAN_TYPE:
            problems.append(f"consumes[0].plan_type must be {CONSUMED_PLAN_TYPE}")
        if plan_ref.get("plan_version") != CONSUMED_PLAN_VERSION:
            problems.append(f"consumes[0].plan_version must be {CONSUMED_PLAN_VERSION}")
        if not _text(plan_ref.get("plan_id")):
            problems.append("consumes[0].plan_id is required")

    for field in _AGENT_SCHEMA_DELTA_FIELDS:
        values = _mapping_sequence(packet.get(field))
        if not values:
            problems.append(f"{field} must be a non-empty list")
        for index, item in enumerate(values):
            _validate_placeholder_common(field, index, item, problems)

    _validate_schema_delta_placeholders(packet, problems)
    _validate_missing_information_expectations(packet, problems)
    _validate_blocked_action_expectations(packet, problems)
    _validate_reversible_preview_expectations(packet, problems)
    _validate_citation_coverage(packet, problems)
    _validate_reviewer_acceptance(packet, problems)
    _validate_attestations(packet, problems)

    if packet.get("prompt_changes") not in (None, []):
        problems.append("prompt_changes must remain empty")
    if packet.get("production_agent_contract_changes") not in (None, []):
        problems.append("production_agent_contract_changes must remain empty")
    if packet.get("public_source_artifact_changes") not in (None, []):
        problems.append("public_source_artifact_changes must remain empty")
    if packet.get("devhub_surface_changes") not in (None, []):
        problems.append("devhub_surface_changes must remain empty")
    if packet.get("release_state_changes") not in (None, []):
        problems.append("release_state_changes must remain empty")
    if packet.get("exact_offline_validation_commands") != EXACT_OFFLINE_VALIDATION_COMMANDS:
        problems.append("exact_offline_validation_commands must match agent readiness delta packet v2 commands")

    _validate_no_forbidden_payload(packet, problems)
    return AgentReadinessDeltaPacketV2ValidationResult(not problems, tuple(problems))


def assert_valid_agent_readiness_delta_packet_v2(packet: Mapping[str, Any]) -> None:
    result = validate_agent_readiness_delta_packet_v2(packet)
    if not result.valid:
        raise AgentReadinessDeltaPacketV2Error(result.problems)


def _schema_delta_placeholder(case: Mapping[str, Any]) -> dict[str, Any]:
    case_id = _text(case.get("case_id"))
    return {
        "delta_id": f"agent-schema-delta-placeholder:{case_id}",
        "replay_case_id": case_id,
        "dependency_row_id": _text(case.get("dependency_row_id")),
        "expected_guardrail_decision": _text(case.get("expected_guardrail_decision")),
        "agent_schema_fields": list(_AGENT_SCHEMA_DELTA_FIELDS[1:]),
        "placeholder_status": "pending_reviewer_acceptance",
        "citations": _citation_refs(case),
    }


def _missing_information_prompt_expectation(case: Mapping[str, Any]) -> dict[str, Any]:
    case_id = _text(case.get("case_id"))
    return {
        "expectation_id": f"missing-information-prompt-expectation:{case_id}",
        "replay_case_id": case_id,
        "dependency_row_id": _text(case.get("dependency_row_id")),
        "requirement_refs": _string_sequence(case.get("impacted_requirement_refs")),
        "prompt_expectation": "Ask only for missing, stale, ambiguous, or conflicting case facts before continuing.",
        "must_include": [
            "missing fact label",
            "why the fact is needed",
            "cited requirement placeholder",
            "no permitting outcome guarantee",
        ],
        "placeholder_status": "pending_reviewer_acceptance",
        "citations": _citation_refs(case),
    }


def _blocked_action_explanation_expectation(case: Mapping[str, Any]) -> dict[str, Any]:
    case_id = _text(case.get("case_id"))
    return {
        "expectation_id": f"blocked-action-explanation-expectation:{case_id}",
        "replay_case_id": case_id,
        "dependency_row_id": _text(case.get("dependency_row_id")),
        "blocked_decision": _text(case.get("expected_guardrail_decision")),
        "explanation_expectation": "Explain the safety gate, required user attendance, exact confirmation need, and the reversible alternative.",
        "must_include": [
            "blocked action category",
            "source-backed reason placeholder",
            "required user confirmation placeholder",
            "next reversible alternative",
        ],
        "placeholder_status": "pending_reviewer_acceptance",
        "citations": _citation_refs(case),
    }


def _reversible_draft_preview_expectation(case: Mapping[str, Any]) -> dict[str, Any]:
    case_id = _text(case.get("case_id"))
    return {
        "expectation_id": f"reversible-draft-preview-expectation:{case_id}",
        "replay_case_id": case_id,
        "dependency_row_id": _text(case.get("dependency_row_id")),
        "preview_expectation": "Show a metadata-only draft preview that can be reviewed, changed, or discarded before any user-attended step.",
        "must_include": [
            "draft field label placeholder",
            "source evidence placeholder",
            "reversible status",
            "reviewer acceptance placeholder",
        ],
        "placeholder_status": "pending_reviewer_acceptance",
        "citations": _citation_refs(case),
    }


def _citation_coverage_placeholders(cases: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    placeholders: list[dict[str, Any]] = []
    for case in cases:
        case_id = _text(case.get("case_id"))
        for citation in _mapping_sequence(case.get("citation_placeholders")):
            placeholders.append(
                {
                    "coverage_id": f"citation-coverage-placeholder:{case_id}:{_text(citation.get('source_evidence_id'))}",
                    "replay_case_id": case_id,
                    "source_evidence_id": _text(citation.get("source_evidence_id")),
                    "citation_id": _text(citation.get("citation_id")),
                    "coverage_status": "pending_reviewer_acceptance",
                    "agent_output_sections": [
                        "missing_information_prompt_expectations",
                        "blocked_action_explanation_expectations",
                        "reversible_draft_preview_expectations",
                    ],
                    "citations": [_citation_ref(citation)],
                }
            )
    return placeholders


def _reviewer_acceptance_placeholder(case: Mapping[str, Any]) -> dict[str, Any]:
    case_id = _text(case.get("case_id"))
    return {
        "acceptance_id": f"reviewer-acceptance-placeholder:{case_id}",
        "replay_case_id": case_id,
        "reviewer": "",
        "reviewed_at": "",
        "decision": "pending_manual_review",
        "acceptance_criteria": [
            "agent-facing schema placeholders are complete",
            "missing-information expectation is source-linked when applicable",
            "blocked-action explanation expectation is present when applicable",
            "reversible-draft preview expectation is present when applicable",
            "citation coverage placeholder is present",
        ],
        "notes": "",
        "citations": _citation_refs(case),
    }


def _validate_placeholder_common(field: str, index: int, item: Mapping[str, Any], problems: list[str]) -> None:
    prefix = f"{field}[{index}]"
    identifier_keys = ("delta_id", "expectation_id", "coverage_id", "acceptance_id")
    if not any(_text(item.get(key)) for key in identifier_keys):
        problems.append(f"{prefix} must include a placeholder identifier")
    if not _text(item.get("replay_case_id")):
        problems.append(f"{prefix}.replay_case_id is required")
    if not _mapping_sequence(item.get("citations")):
        problems.append(f"{prefix}.citations must be non-empty")


def _validate_schema_delta_placeholders(packet: Mapping[str, Any], problems: list[str]) -> None:
    for index, item in enumerate(_mapping_sequence(packet.get("agent_schema_delta_placeholders"))):
        prefix = f"agent_schema_delta_placeholders[{index}]"
        fields = _string_sequence(item.get("agent_schema_fields"))
        for required_field in _AGENT_SCHEMA_DELTA_FIELDS[1:]:
            if required_field not in fields:
                problems.append(f"{prefix}.agent_schema_fields must include {required_field}")
        if item.get("placeholder_status") != "pending_reviewer_acceptance":
            problems.append(f"{prefix}.placeholder_status must be pending_reviewer_acceptance")


def _validate_missing_information_expectations(packet: Mapping[str, Any], problems: list[str]) -> None:
    for index, item in enumerate(_mapping_sequence(packet.get("missing_information_prompt_expectations"))):
        prefix = f"missing_information_prompt_expectations[{index}]"
        if not _text(item.get("prompt_expectation")):
            problems.append(f"{prefix}.prompt_expectation is required")
        if not _string_sequence(item.get("requirement_refs")):
            problems.append(f"{prefix}.requirement_refs must be non-empty")
        if item.get("placeholder_status") != "pending_reviewer_acceptance":
            problems.append(f"{prefix}.placeholder_status must be pending_reviewer_acceptance")


def _validate_blocked_action_expectations(packet: Mapping[str, Any], problems: list[str]) -> None:
    for index, item in enumerate(_mapping_sequence(packet.get("blocked_action_explanation_expectations"))):
        prefix = f"blocked_action_explanation_expectations[{index}]"
        if item.get("blocked_decision") != "BLOCK":
            problems.append(f"{prefix}.blocked_decision must be BLOCK")
        if not _text(item.get("explanation_expectation")):
            problems.append(f"{prefix}.explanation_expectation is required")
        if item.get("placeholder_status") != "pending_reviewer_acceptance":
            problems.append(f"{prefix}.placeholder_status must be pending_reviewer_acceptance")


def _validate_reversible_preview_expectations(packet: Mapping[str, Any], problems: list[str]) -> None:
    for index, item in enumerate(_mapping_sequence(packet.get("reversible_draft_preview_expectations"))):
        prefix = f"reversible_draft_preview_expectations[{index}]"
        if not _text(item.get("preview_expectation")):
            problems.append(f"{prefix}.preview_expectation is required")
        if item.get("placeholder_status") != "pending_reviewer_acceptance":
            problems.append(f"{prefix}.placeholder_status must be pending_reviewer_acceptance")


def _validate_citation_coverage(packet: Mapping[str, Any], problems: list[str]) -> None:
    for index, item in enumerate(_mapping_sequence(packet.get("citation_coverage_placeholders"))):
        prefix = f"citation_coverage_placeholders[{index}]"
        if not _text(item.get("source_evidence_id")):
            problems.append(f"{prefix}.source_evidence_id is required")
        if not _text(item.get("citation_id")):
            problems.append(f"{prefix}.citation_id is required")
        if item.get("coverage_status") != "pending_reviewer_acceptance":
            problems.append(f"{prefix}.coverage_status must be pending_reviewer_acceptance")


def _validate_reviewer_acceptance(packet: Mapping[str, Any], problems: list[str]) -> None:
    for index, item in enumerate(_mapping_sequence(packet.get("reviewer_acceptance_placeholders"))):
        prefix = f"reviewer_acceptance_placeholders[{index}]"
        if item.get("reviewer") != "" or item.get("reviewed_at") != "" or item.get("notes") != "":
            problems.append(f"{prefix} must remain unsigned")
        if item.get("decision") != "pending_manual_review":
            problems.append(f"{prefix}.decision must be pending_manual_review")
        if not _string_sequence(item.get("acceptance_criteria")):
            problems.append(f"{prefix}.acceptance_criteria must be non-empty")


def _validate_attestations(packet: Mapping[str, Any], problems: list[str]) -> None:
    attestations = _mapping(packet.get("attestations"))
    for key, expected in sorted(_REQUIRED_ATTESTATIONS.items()):
        if attestations.get(key) is not expected:
            problems.append(f"attestations.{key} must be {expected}")


def _validate_no_forbidden_payload(packet: Mapping[str, Any], problems: list[str]) -> None:
    for path, key, value in _walk(packet):
        normalized_key = key.lower().replace("-", "_")
        if normalized_key in _MUTATION_KEYS and value is not False:
            problems.append(f"{path} must be false")
        if any(token in normalized_key for token in _PRIVATE_OR_LIVE_KEY_TOKENS) and _truthy(value):
            problems.append(f"{path} must not include live, account, browser, credential, file, or payment artifacts")
        if isinstance(value, str):
            normalized_value = " ".join(value.lower().split())
            if any(token in normalized_value for token in _FORBIDDEN_TEXT_TOKENS):
                problems.append(f"{path} must not include unsafe live, account, file, payment, or guarantee language")


def _citation_refs(case: Mapping[str, Any]) -> list[dict[str, str]]:
    return [_citation_ref(citation) for citation in _mapping_sequence(case.get("citation_placeholders"))]


def _citation_ref(citation: Mapping[str, Any]) -> dict[str, str]:
    return {
        "citation_id": _text(citation.get("citation_id")),
        "source_evidence_id": _text(citation.get("source_evidence_id")),
        "citation_status": _text(citation.get("citation_status"), "pending_replay_resolution"),
    }


def _walk(value: Any, prefix: str = "packet", key: str = "packet") -> Iterable[tuple[str, str, Any]]:
    if isinstance(value, Mapping):
        for child_key, child_value in value.items():
            child_key_text = str(child_key)
            child_path = f"{prefix}.{child_key_text}"
            yield child_path, child_key_text, child_value
            yield from _walk(child_value, child_path, child_key_text)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child_value in enumerate(value):
            child_path = f"{prefix}[{index}]"
            yield child_path, key, child_value
            yield from _walk(child_value, child_path, key)


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _mapping_sequence(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _string_sequence(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


def _text(value: Any, default: str = "") -> str:
    if isinstance(value, str):
        stripped = value.strip()
        return stripped if stripped else default
    return default


def _truthy(value: Any) -> bool:
    if value in (None, False, "", [], {}, ()):  # deterministic empty payload check
        return False
    return True
