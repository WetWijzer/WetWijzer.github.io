"""Fixture-first guardrail impact replay plan v2.

Consumes inactive promotion candidate packet v2 fixtures and emits ordered,
synthetic guardrail replay cases only. This module does not compile guardrails,
change prompts, mutate active process models or requirements, access DevHub, or
perform official actions.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ppd.agent_readiness.inactive_promotion_candidate_packet_v2 import (
    PACKET_TYPE as INACTIVE_PACKET_TYPE,
    PACKET_VERSION as INACTIVE_PACKET_VERSION,
    assert_valid_inactive_promotion_candidate_packet_v2,
)

PLAN_TYPE = "ppd.guardrail_impact_replay_plan.v2"
PLAN_VERSION = "v2"
EXPECTED_OUTCOMES = {"allow", "block", "escalate"}
EXPECTED_GUARDRAIL_DECISIONS = {
    "allow": "ALLOW",
    "block": "BLOCK",
    "escalate": "ESCALATE",
}
EXACT_OFFLINE_VALIDATION_COMMANDS = [
    ["python3", "-m", "py_compile", "ppd/agent_readiness/guardrail_impact_replay_plan_v2.py"],
    ["python3", "-m", "pytest", "ppd/tests/test_guardrail_impact_replay_plan_v2.py"],
    ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
]

_REQUIRED_ATTESTATIONS = {
    "fixture_first": True,
    "consumes_inactive_promotion_candidate_packet_v2": True,
    "compiled_guardrails_changed": False,
    "prompts_changed": False,
    "active_guardrails_changed": False,
    "active_process_models_changed": False,
    "active_requirements_changed": False,
    "agent_release_artifacts_changed": False,
    "live_crawl_performed": False,
    "devhub_accessed": False,
    "official_action_performed": False,
}

_MUTATION_KEYS = {
    "active_guardrail_mutation",
    "active_process_mutation",
    "active_prompt_mutation",
    "active_release_state_mutation",
    "active_requirement_mutation",
    "agent_release_artifact_mutation",
    "compiled_guardrail_mutation",
    "guardrail_mutated",
    "process_mutated",
    "prompt_mutated",
    "release_state_mutated",
    "requirement_mutated",
}

_PRIVATE_RAW_OR_LIVE_KEY_TOKENS = (
    "auth",
    "browser",
    "captcha",
    "cookie",
    "credential",
    "download",
    "downloaded",
    "har",
    "local_path",
    "mfa",
    "password",
    "payment",
    "private",
    "raw",
    "screenshot",
    "secret",
    "session",
    "storage_state",
    "token",
    "trace",
    "warc",
)

_PRIVATE_RAW_OR_LIVE_VALUE_TOKENS = (
    "auth state",
    "browser state",
    "cookie",
    "credential",
    "downloaded document",
    "har file",
    "live crawl completed",
    "live devhub access",
    "opened browser",
    "password",
    "payment detail",
    "private devhub",
    "private value",
    "raw body",
    "raw crawl",
    "raw html",
    "raw pdf",
    "screenshot",
    "session state",
    "session storage",
    "storage state",
    "trace.zip",
    "warc payload",
)

_OFFICIAL_ACTION_TOKENS = (
    "agent may certify",
    "agent may pay",
    "agent may schedule",
    "agent may submit",
    "agent may upload",
    "certify acknowledgement",
    "click submit",
    "official action completed",
    "pay fees",
    "purchase permit",
    "schedule inspection",
    "submit payment",
    "submit permit",
    "upload corrections",
)

_GUARANTEE_TOKENS = (
    "approval guaranteed",
    "guaranteed approval",
    "legal advice",
    "legal guarantee",
    "legally compliant",
    "permit guaranteed",
    "permit will be approved",
    "permit will issue",
)


@dataclass(frozen=True)
class GuardrailImpactReplayPlanV2ValidationResult:
    valid: bool
    problems: tuple[str, ...]


class GuardrailImpactReplayPlanV2Error(ValueError):
    def __init__(self, problems: Iterable[str]) -> None:
        self.problems = tuple(problems)
        super().__init__("invalid guardrail impact replay plan v2: " + "; ".join(self.problems))


def load_json_object(path: str | Path) -> dict[str, Any]:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object at {path}")
    return value


def build_guardrail_impact_replay_plan_v2_from_file(path: str | Path) -> dict[str, Any]:
    return build_guardrail_impact_replay_plan_v2(load_json_object(path))


def build_guardrail_impact_replay_plan_v2(packet: Mapping[str, Any]) -> dict[str, Any]:
    assert_valid_inactive_promotion_candidate_packet_v2(packet)

    prerequisites = _mapping_sequence(packet.get("guardrail_replay_prerequisites"))
    source_deltas = _index_by_dependency(packet.get("inactive_source_registry_candidate_deltas"))
    surface_deltas = _index_by_dependency(packet.get("inactive_devhub_surface_candidate_deltas"))

    replay_cases: list[dict[str, Any]] = []
    for order, prerequisite in enumerate(prerequisites, start=1):
        dependency_id = _text(prerequisite.get("dependency_row_id"))
        source_delta = source_deltas.get(dependency_id, {})
        surface_delta = surface_deltas.get(dependency_id, {})
        evidence_ids = _string_sequence(prerequisite.get("required_source_evidence_ids"))
        requirement_ids = _string_sequence(prerequisite.get("required_requirement_ids"))
        surface_ids = _string_sequence(prerequisite.get("required_surface_ids"))
        process_refs = _process_refs(source_delta, surface_delta, requirement_ids)

        replay_cases.extend(
            [
                _replay_case(
                    dependency_order=order,
                    dependency_id=dependency_id,
                    suffix="allow-reversible-review",
                    expected_outcome="allow",
                    guardrail_decision="ALLOW",
                    replay_intent="Review inactive fixture evidence and prepare only reversible draft guidance.",
                    requirement_ids=requirement_ids,
                    process_refs=process_refs,
                    surface_ids=surface_ids,
                    evidence_ids=evidence_ids,
                ),
                _replay_case(
                    dependency_order=order,
                    dependency_id=dependency_id,
                    suffix="block-official-final-action",
                    expected_outcome="block",
                    guardrail_decision="BLOCK",
                    replay_intent="Refuse any final consequential action derived from the inactive candidate evidence.",
                    requirement_ids=requirement_ids,
                    process_refs=process_refs,
                    surface_ids=surface_ids,
                    evidence_ids=evidence_ids,
                ),
                _replay_case(
                    dependency_order=order,
                    dependency_id=dependency_id,
                    suffix="escalate-gap-comparison",
                    expected_outcome="escalate",
                    guardrail_decision="ESCALATE",
                    replay_intent="Hold for reviewer comparison when fixture gap analysis is missing, stale, or conflicting.",
                    requirement_ids=requirement_ids,
                    process_refs=process_refs,
                    surface_ids=surface_ids,
                    evidence_ids=evidence_ids,
                ),
            ]
        )

    plan = {
        "plan_type": PLAN_TYPE,
        "plan_version": PLAN_VERSION,
        "plan_id": f"guardrail-impact-replay-plan-v2-for-{_text(packet.get('source_rehearsal_id'), 'inactive-promotion-candidate-packet-v2')}",
        "fixture_only": True,
        "replay_mode": "ordered_synthetic_guardrail_impact_cases",
        "source_packet": {
            "packet_type": _text(packet.get("packet_type")),
            "packet_version": _text(packet.get("packet_version")),
            "source_rehearsal_id": _text(packet.get("source_rehearsal_id")),
        },
        "consumed_approved_dependency_row_ids": _string_sequence(packet.get("consumed_approved_dependency_row_ids")),
        "case_order": [case["case_id"] for case in replay_cases],
        "ordered_replay_cases": replay_cases,
        "reviewer_hold_placeholders": [_reviewer_hold(case) for case in replay_cases],
        "attestations": dict(_REQUIRED_ATTESTATIONS),
        "exact_offline_validation_commands": EXACT_OFFLINE_VALIDATION_COMMANDS,
    }
    assert_valid_guardrail_impact_replay_plan_v2(plan)
    return plan


def validate_guardrail_impact_replay_plan_v2(plan: Mapping[str, Any]) -> GuardrailImpactReplayPlanV2ValidationResult:
    problems: list[str] = []
    if not isinstance(plan, Mapping):
        return GuardrailImpactReplayPlanV2ValidationResult(False, ("plan must be an object",))

    if plan.get("plan_type") != PLAN_TYPE:
        problems.append(f"plan_type must be {PLAN_TYPE}")
    if plan.get("plan_version") != PLAN_VERSION:
        problems.append("plan_version must be v2")
    if plan.get("fixture_only") is not True:
        problems.append("fixture_only must be true")
    if plan.get("replay_mode") != "ordered_synthetic_guardrail_impact_cases":
        problems.append("replay_mode must be ordered_synthetic_guardrail_impact_cases")

    source_packet = _mapping(plan.get("source_packet"))
    if source_packet.get("packet_type") != INACTIVE_PACKET_TYPE:
        problems.append(f"source_packet.packet_type must be {INACTIVE_PACKET_TYPE}")
    if source_packet.get("packet_version") != INACTIVE_PACKET_VERSION:
        problems.append(f"source_packet.packet_version must be {INACTIVE_PACKET_VERSION}")

    consumed = set(_string_sequence(plan.get("consumed_approved_dependency_row_ids")))
    if not consumed:
        problems.append("consumed_approved_dependency_row_ids must be non-empty")

    cases = _mapping_sequence(plan.get("ordered_replay_cases"))
    if not cases:
        problems.append("ordered_replay_cases must be non-empty")
    case_order = _string_sequence(plan.get("case_order"))
    actual_order = [_text(case.get("case_id")) for case in cases]
    if case_order != actual_order:
        problems.append("case_order must exactly match ordered_replay_cases")

    _validate_cases(cases, consumed, problems)
    _validate_reviewer_holds(plan, cases, problems)
    _validate_attestations(plan, problems)
    if plan.get("exact_offline_validation_commands") != EXACT_OFFLINE_VALIDATION_COMMANDS:
        problems.append("exact_offline_validation_commands must match guardrail impact replay plan v2 validation commands")
    _validate_no_forbidden_payload(plan, problems)

    return GuardrailImpactReplayPlanV2ValidationResult(not problems, tuple(problems))


def assert_valid_guardrail_impact_replay_plan_v2(plan: Mapping[str, Any]) -> None:
    result = validate_guardrail_impact_replay_plan_v2(plan)
    if not result.valid:
        raise GuardrailImpactReplayPlanV2Error(result.problems)


def _replay_case(
    *,
    dependency_order: int,
    dependency_id: str,
    suffix: str,
    expected_outcome: str,
    guardrail_decision: str,
    replay_intent: str,
    requirement_ids: Sequence[str],
    process_refs: Sequence[str],
    surface_ids: Sequence[str],
    evidence_ids: Sequence[str],
) -> dict[str, Any]:
    case_id = f"guardrail-impact-{dependency_order:03d}-{suffix}"
    return {
        "case_id": case_id,
        "dependency_row_id": dependency_id,
        "source_packet_ref": f"inactive-promotion-candidate-packet-v2:{dependency_id}",
        "synthetic_case": True,
        "replay_intent": replay_intent,
        "impacted_requirement_refs": list(requirement_ids),
        "impacted_process_refs": list(process_refs),
        "impacted_surface_refs": list(surface_ids),
        "expected_outcome": expected_outcome,
        "expected_guardrail_decision": guardrail_decision,
        "citation_placeholders": [
            {
                "citation_id": f"citation-placeholder:{case_id}:{index:03d}",
                "source_evidence_id": evidence_id,
                "citation_status": "pending_replay_resolution",
            }
            for index, evidence_id in enumerate(evidence_ids, start=1)
        ],
        "gap_analysis_comparison_placeholders": {
            "baseline_gap_analysis_ref": "",
            "candidate_gap_analysis_ref": "",
            "comparison_status": "pending_offline_fixture_replay",
            "expected_comparison_result": "no_active_gap_analysis_mutation",
        },
        "reviewer_hold_ref": f"reviewer-hold:{case_id}",
        "compiled_guardrail_mutation": False,
        "active_guardrail_mutation": False,
        "active_process_mutation": False,
        "active_requirement_mutation": False,
        "active_prompt_mutation": False,
        "active_release_state_mutation": False,
        "prompt_mutation": False,
        "agent_release_artifact_mutation": False,
    }


def _reviewer_hold(case: Mapping[str, Any]) -> dict[str, Any]:
    case_id = _text(case.get("case_id"))
    return {
        "hold_id": f"reviewer-hold:{case_id}",
        "case_id": case_id,
        "hold_reason": "pending_manual_guardrail_impact_review",
        "reviewer": "",
        "reviewed_at": "",
        "decision": "pending_manual_review",
        "notes": "",
    }


def _validate_cases(cases: Sequence[Mapping[str, Any]], consumed: set[str], problems: list[str]) -> None:
    outcomes_by_dependency: dict[str, set[str]] = {dependency_id: set() for dependency_id in consumed}
    for index, case in enumerate(cases):
        prefix = f"ordered_replay_cases[{index}]"
        case_id = _text(case.get("case_id"))
        if not case_id:
            problems.append(f"{prefix}.case_id is required")
        dependency_id = _text(case.get("dependency_row_id"))
        if dependency_id not in consumed:
            problems.append(f"{prefix}.dependency_row_id must reference a consumed dependency row")
        if case.get("synthetic_case") is not True:
            problems.append(f"{prefix}.synthetic_case must be true")
        if not _text(case.get("source_packet_ref")):
            problems.append(f"{prefix}.source_packet_ref is required")
        if not _text(case.get("replay_intent")):
            problems.append(f"{prefix}.replay_intent is required")

        outcome = _text(case.get("expected_outcome"))
        if outcome not in EXPECTED_OUTCOMES:
            problems.append(f"{prefix}.expected_outcome must be allow, block, or escalate")
        else:
            outcomes_by_dependency.setdefault(dependency_id, set()).add(outcome)
            expected_decision = EXPECTED_GUARDRAIL_DECISIONS[outcome]
            if case.get("expected_guardrail_decision") != expected_decision:
                problems.append(f"{prefix}.expected_guardrail_decision must be {expected_decision}")

        if not _string_sequence(case.get("impacted_requirement_refs")):
            problems.append(f"{prefix}.impacted_requirement_refs must be non-empty")
        if not _string_sequence(case.get("impacted_process_refs")):
            problems.append(f"{prefix}.impacted_process_refs must be non-empty")
        if not _string_sequence(case.get("impacted_surface_refs")):
            problems.append(f"{prefix}.impacted_surface_refs must be non-empty")
        _validate_citation_placeholders(case, prefix, problems)
        _validate_gap_analysis_placeholders(case, prefix, problems)
        if not _text(case.get("reviewer_hold_ref")):
            problems.append(f"{prefix}.reviewer_hold_ref is required")

    for dependency_id, outcomes in sorted(outcomes_by_dependency.items()):
        if outcomes != EXPECTED_OUTCOMES:
            problems.append(f"dependency {dependency_id} must have allow, block, and escalate replay cases")


def _validate_citation_placeholders(case: Mapping[str, Any], prefix: str, problems: list[str]) -> None:
    citations = _mapping_sequence(case.get("citation_placeholders"))
    if not citations:
        problems.append(f"{prefix}.citation_placeholders must be non-empty")
        return
    for citation_index, citation in enumerate(citations):
        citation_prefix = f"{prefix}.citation_placeholders[{citation_index}]"
        if not _text(citation.get("citation_id")):
            problems.append(f"{citation_prefix}.citation_id is required")
        if not _text(citation.get("source_evidence_id")):
            problems.append(f"{citation_prefix}.source_evidence_id is required")
        if citation.get("citation_status") != "pending_replay_resolution":
            problems.append(f"{citation_prefix}.citation_status must be pending_replay_resolution")


def _validate_gap_analysis_placeholders(case: Mapping[str, Any], prefix: str, problems: list[str]) -> None:
    raw_gap = case.get("gap_analysis_comparison_placeholders")
    gap = _mapping(raw_gap)
    if not gap:
        problems.append(f"{prefix}.gap_analysis_comparison_placeholders must be present")
        return
    for field in ("baseline_gap_analysis_ref", "candidate_gap_analysis_ref", "comparison_status", "expected_comparison_result"):
        if field not in gap:
            problems.append(f"{prefix}.gap_analysis_comparison_placeholders.{field} is required")
    if gap.get("comparison_status") != "pending_offline_fixture_replay":
        problems.append(f"{prefix}.gap_analysis_comparison_placeholders.comparison_status must be pending_offline_fixture_replay")
    if gap.get("expected_comparison_result") != "no_active_gap_analysis_mutation":
        problems.append(f"{prefix}.gap_analysis_comparison_placeholders.expected_comparison_result must be no_active_gap_analysis_mutation")


def _validate_reviewer_holds(plan: Mapping[str, Any], cases: Sequence[Mapping[str, Any]], problems: list[str]) -> None:
    holds = _mapping_sequence(plan.get("reviewer_hold_placeholders"))
    expected_hold_ids = {_text(case.get("reviewer_hold_ref")) for case in cases if _text(case.get("reviewer_hold_ref"))}
    actual_hold_ids = {_text(hold.get("hold_id")) for hold in holds}
    if actual_hold_ids != expected_hold_ids:
        problems.append("reviewer_hold_placeholders must match every replay case reviewer_hold_ref")
    cases_by_id = {_text(case.get("case_id")): case for case in cases if _text(case.get("case_id"))}
    for index, hold in enumerate(holds):
        prefix = f"reviewer_hold_placeholders[{index}]"
        for field in ("hold_id", "case_id", "hold_reason", "reviewer", "reviewed_at", "decision", "notes"):
            if field not in hold:
                problems.append(f"{prefix}.{field} is required")
        case_id = _text(hold.get("case_id"))
        expected_hold_id = _text(cases_by_id.get(case_id, {}).get("reviewer_hold_ref"))
        if not expected_hold_id:
            problems.append(f"{prefix}.case_id must reference an ordered replay case")
        elif hold.get("hold_id") != expected_hold_id:
            problems.append(f"{prefix}.hold_id must match the replay case reviewer_hold_ref")
        if hold.get("hold_reason") != "pending_manual_guardrail_impact_review":
            problems.append(f"{prefix}.hold_reason must be pending_manual_guardrail_impact_review")
        if hold.get("decision") != "pending_manual_review":
            problems.append(f"{prefix}.decision must be pending_manual_review")
        if hold.get("reviewer") != "" or hold.get("reviewed_at") != "" or hold.get("notes") != "":
            problems.append(f"{prefix} must remain an unsigned reviewer hold placeholder")


def _validate_attestations(plan: Mapping[str, Any], problems: list[str]) -> None:
    attestations = _mapping(plan.get("attestations"))
    for key, expected in sorted(_REQUIRED_ATTESTATIONS.items()):
        if attestations.get(key) is not expected:
            problems.append(f"attestations.{key} must be {expected}")


def _validate_no_forbidden_payload(plan: Mapping[str, Any], problems: list[str]) -> None:
    for path, key, value in _walk(plan):
        normalized_key = key.lower().replace("-", "_")
        if normalized_key in _MUTATION_KEYS and value is not False:
            problems.append(f"{path} must be false")
        if any(token in normalized_key for token in _PRIVATE_RAW_OR_LIVE_KEY_TOKENS) and _truthy(value):
            problems.append(f"{path} must not include private, raw, authenticated, browser, session, or payment artifacts")
        if isinstance(value, str):
            text = value.lower()
            if any(token in text for token in _PRIVATE_RAW_OR_LIVE_VALUE_TOKENS):
                problems.append(f"{path} must not reference private, raw, authenticated, browser, session, or payment artifacts")
            if any(token in text for token in _OFFICIAL_ACTION_TOKENS):
                problems.append(f"{path} must not include consequential official-action execution language")
            if any(token in text for token in _GUARANTEE_TOKENS):
                problems.append(f"{path} must not include legal or permitting guarantees")


def _index_by_dependency(value: Any) -> dict[str, Mapping[str, Any]]:
    return {_text(row.get("dependency_row_id")): row for row in _mapping_sequence(value) if _text(row.get("dependency_row_id"))}


def _process_refs(source_delta: Mapping[str, Any], surface_delta: Mapping[str, Any], requirement_ids: Sequence[str]) -> list[str]:
    refs: list[str] = []
    source_id = _text(source_delta.get("source_id"))
    surface_id = _text(surface_delta.get("surface_id"))
    joined = " ".join([source_id, surface_id, " ".join(requirement_ids)]).lower()
    if "single-pdf" in joined or "document-staging" in joined or "submit-plans" in joined:
        refs.append("process:submit-plans-online-single-pdf")
    if "devhub" in joined or "application" in joined:
        refs.append("process:devhub-permit-application")
    if not refs:
        refs.append("process:ppd-fixture-first-review")
    return sorted(set(refs))


def _walk(value: Any, prefix: str = "plan", key: str = "plan") -> Iterable[tuple[str, str, Any]]:
    if isinstance(value, Mapping):
        for child_key, child_value in value.items():
            child_key_text = str(child_key)
            child_path = f"{prefix}.{child_key_text}"
            yield child_path, child_key_text, child_value
            yield from _walk(child_value, child_path, child_key_text)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child_value in enumerate(value):
            child_path = f"{prefix}[{index}]"
            yield child_path, key, child_value
            yield from _walk(child_value, child_path, key)


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _mapping_sequence(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _string_sequence(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [item for item in value if isinstance(item, str) and item]


def _truthy(value: Any) -> bool:
    if value is None or value is False or value == "":
        return False
    if isinstance(value, Mapping) and not value:
        return False
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)) and not value:
        return False
    return True


def _text(value: Any, fallback: str = "") -> str:
    return value.strip() if isinstance(value, str) and value.strip() else fallback
