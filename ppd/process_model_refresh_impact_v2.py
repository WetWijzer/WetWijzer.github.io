"""Fixture-first process-model refresh impact v2 packets.

This module consumes committed fixture packets only. It does not launch DevHub,
fetch sources, invoke processors, mutate active process models, mutate active
surface registries, mutate active guardrail bundles, update prompts, alter
monitoring, alter agent state, or alter release state.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence


PACKET_TYPE = "ppd.process_model_refresh_impact_v2"
DEFAULT_VALIDATION_COMMANDS = [
    ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
    ["python3", "-m", "pytest", "ppd/tests/test_process_model_refresh_impact_v2.py"],
]
REQUIRED_ATTESTATIONS = {
    "fixture_first": True,
    "no_live_devhub": True,
    "no_live_browser": True,
    "no_live_crawler": True,
    "no_processor_invocation": True,
    "no_llm_execution": True,
    "no_process_mutation": True,
    "no_guardrail_mutation": True,
    "no_prompt_mutation": True,
    "no_surface_registry_mutation": True,
    "no_monitoring_mutation": True,
    "no_release_state_mutation": True,
    "no_agent_state_mutation": True,
    "no_official_action": True,
}
FORBIDDEN_TEXT = (
    "live devhub",
    "devhub launched",
    "devhub invoked",
    "browser launched",
    "browser invoked",
    "playwright launched",
    "crawler launched",
    "crawler invoked",
    "processor launched",
    "processor invoked",
    "llm executed",
    "llm invoked",
    "model executed",
    "authenticated session",
    "authenticated fact",
    "private fact",
    "private devhub",
    "raw crawl",
    "raw body",
    "raw pdf",
    "downloaded document",
    "file://",
    ".warc",
    ".har",
    "trace.zip",
    "credential",
    "cookie",
    "password",
    "payment detail",
    "process mutated",
    "guardrail mutated",
    "prompt updated",
    "surface registry mutated",
    "monitoring mutated",
    "release state updated",
    "agent state updated",
    "permit will be approved",
    "approval is guaranteed",
    "guaranteed approval",
    "guaranteed permit",
    "legal outcome guaranteed",
    "permitting outcome guaranteed",
    "submission enabled",
    "certification enabled",
    "official upload enabled",
    "payment enabled",
    "inspection scheduling enabled",
    "consequential action enabled",
)
FORBIDDEN_TRUE_KEYS = (
    "live_devhub_allowed",
    "devhub_invocation_allowed",
    "live_browser_allowed",
    "browser_execution_allowed",
    "crawler_invocation_allowed",
    "processor_invocation_allowed",
    "llm_execution_allowed",
    "official_action_allowed",
    "consequential_action_enabled",
    "submission_enabled",
    "certification_enabled",
    "official_upload_enabled",
    "payment_enabled",
    "inspection_scheduling_enabled",
    "process_mutation_allowed",
    "guardrail_mutation_allowed",
    "prompt_mutation_allowed",
    "surface_registry_mutation_allowed",
    "monitoring_mutation_allowed",
    "release_state_mutation_allowed",
    "agent_state_mutation_allowed",
    "active_process_mutated",
    "active_guardrail_mutated",
    "active_prompt_mutated",
    "active_surface_registry_mutated",
    "active_monitoring_mutated",
    "release_state_mutated",
    "active_agent_state_mutated",
)
FORBIDDEN_FACT_KEYS = (
    "private_fact",
    "private_facts",
    "authenticated_fact",
    "authenticated_facts",
    "account_fact",
    "account_facts",
    "devhub_private_fact",
    "devhub_authenticated_fact",
)
UNSUPPORTED_PATH_KEYWORDS = (
    "upload",
    "submit",
    "submission",
    "certify",
    "certification",
    "payment",
    "schedule",
    "inspection",
    "cancel",
    "withdraw",
    "official",
    "correction",
    "checksheets",
)


@dataclass(frozen=True)
class ProcessModelRefreshImpactV2Issue:
    code: str
    path: str
    message: str


class ProcessModelRefreshImpactV2Error(ValueError):
    def __init__(self, issues: Sequence[ProcessModelRefreshImpactV2Issue]) -> None:
        self.issues = tuple(issues)
        detail = "; ".join(f"{issue.code} at {issue.path}: {issue.message}" for issue in self.issues)
        super().__init__(detail)


def build_process_model_refresh_impact_v2(packet_input: Mapping[str, Any]) -> dict[str, Any]:
    input_issues = _safety_issues(packet_input)
    if input_issues:
        raise ProcessModelRefreshImpactV2Error(input_issues)

    work_order = _mapping(packet_input.get("requirement_regeneration_work_order_v2"))
    impact_review = _mapping(packet_input.get("process_model_impact_review_fixture"))
    guardrail_candidate = _mapping(packet_input.get("guardrail_bundle_update_candidate_fixture"))
    if not work_order or not impact_review or not guardrail_candidate:
        raise ProcessModelRefreshImpactV2Error([
            ProcessModelRefreshImpactV2Issue(
                "missing_prerequisite_packets",
                "$",
                "work-order v2, process impact review, and guardrail candidate fixtures are required",
            )
        ])

    decisions = _process_stage_impact_decisions(work_order, impact_review, guardrail_candidate)
    packet = {
        "packet_type": PACKET_TYPE,
        "packet_id": str(packet_input.get("packet_id") or "fixture-process-model-refresh-impact-v2"),
        "fixture_only": True,
        "source_packet_ids": {
            "requirement_regeneration_work_order_v2": _packet_id(work_order, "requirement-regeneration-work-order-v2-fixture"),
            "process_model_impact_review_fixture": _packet_id(impact_review, "process-model-impact-review-fixture"),
            "guardrail_bundle_update_candidate_fixture": _packet_id(guardrail_candidate, "guardrail-bundle-update-candidate-fixture"),
        },
        "process_stage_impact_decisions": decisions,
        "unsupported_path_notes": _unsupported_path_notes(impact_review, decisions),
        "downstream_guardrail_bundle_refs": _downstream_guardrail_bundle_refs(guardrail_candidate, decisions),
        "reviewer_owner_fields": _reviewer_owner_fields(decisions, impact_review, guardrail_candidate),
        "offline_validation_commands": [list(command) for command in DEFAULT_VALIDATION_COMMANDS],
        "attestations": dict(REQUIRED_ATTESTATIONS),
    }
    issues = validate_process_model_refresh_impact_v2(packet)
    if issues:
        raise ProcessModelRefreshImpactV2Error(issues)
    return packet


def validate_process_model_refresh_impact_v2(packet: Mapping[str, Any]) -> list[ProcessModelRefreshImpactV2Issue]:
    issues: list[ProcessModelRefreshImpactV2Issue] = []
    if not isinstance(packet, Mapping):
        return [ProcessModelRefreshImpactV2Issue("invalid_packet", "$", "packet must be an object")]
    issues.extend(_safety_issues(packet))

    if packet.get("packet_type") != PACKET_TYPE:
        issues.append(ProcessModelRefreshImpactV2Issue("invalid_packet_type", "$.packet_type", "unexpected packet type"))
    if packet.get("fixture_only") is not True:
        issues.append(ProcessModelRefreshImpactV2Issue("not_fixture_only", "$.fixture_only", "packet must be fixture-only"))

    source_packet_ids = _mapping(packet.get("source_packet_ids"))
    for key in (
        "requirement_regeneration_work_order_v2",
        "process_model_impact_review_fixture",
        "guardrail_bundle_update_candidate_fixture",
    ):
        if not _text(source_packet_ids.get(key)):
            issues.append(ProcessModelRefreshImpactV2Issue("missing_source_packet_ref", f"$.source_packet_ids.{key}", "source packet reference is required"))

    decisions = list(_mapping_sequence(packet.get("process_stage_impact_decisions")))
    if not decisions:
        issues.append(ProcessModelRefreshImpactV2Issue("missing_process_stage_impact_decisions", "$.process_stage_impact_decisions", "process-stage impact decisions are required"))
    for index, decision in enumerate(decisions):
        path = f"$.process_stage_impact_decisions[{index}]"
        if not _text(decision.get("requirement_id")):
            issues.append(ProcessModelRefreshImpactV2Issue("missing_requirement_id", path + ".requirement_id", "requirement ID is required"))
        if not _text(decision.get("process_stage")):
            issues.append(ProcessModelRefreshImpactV2Issue("missing_process_stage", path + ".process_stage", "process stage is required"))
        if not _strings(decision.get("source_evidence_ids")):
            issues.append(ProcessModelRefreshImpactV2Issue("uncited_process_stage_impact_decision", path + ".source_evidence_ids", "impact decision must cite fixture evidence"))
        if not _strings(decision.get("downstream_guardrail_bundle_ids")):
            issues.append(ProcessModelRefreshImpactV2Issue("missing_decision_downstream_guardrail_refs", path + ".downstream_guardrail_bundle_ids", "each impact decision must name downstream guardrail bundle references"))
        if not _text(decision.get("reviewer_owner")):
            issues.append(ProcessModelRefreshImpactV2Issue("missing_reviewer_owner", path + ".reviewer_owner", "reviewer owner is required"))
        _require_false(issues, decision, path, (
            "live_devhub_allowed",
            "official_action_allowed",
            "process_mutation_allowed",
            "guardrail_mutation_allowed",
            "prompt_mutation_allowed",
            "surface_registry_mutation_allowed",
            "monitoring_mutation_allowed",
            "release_state_mutation_allowed",
            "agent_state_mutation_allowed",
            "consequential_action_enabled",
        ))

    notes = list(_mapping_sequence(packet.get("unsupported_path_notes")))
    if not notes:
        issues.append(ProcessModelRefreshImpactV2Issue("missing_unsupported_path_notes", "$.unsupported_path_notes", "unsupported-path notes are required"))
    for index, note in enumerate(notes):
        path = f"$.unsupported_path_notes[{index}]"
        if not _text(note.get("path_id")):
            issues.append(ProcessModelRefreshImpactV2Issue("missing_unsupported_path_id", path + ".path_id", "unsupported path ID is required"))
        if not _strings(note.get("source_evidence_ids")):
            issues.append(ProcessModelRefreshImpactV2Issue("uncited_unsupported_path_note", path + ".source_evidence_ids", "unsupported path note must cite evidence"))
        _require_false(issues, note, path, ("live_devhub_allowed", "official_action_allowed", "process_mutation_allowed", "consequential_action_enabled"))

    refs = list(_mapping_sequence(packet.get("downstream_guardrail_bundle_refs")))
    ref_bundle_ids = {bundle_id for ref in refs for bundle_id in [_text(ref.get("guardrail_bundle_id"))] if bundle_id}
    if not refs:
        issues.append(ProcessModelRefreshImpactV2Issue("missing_downstream_guardrail_bundle_refs", "$.downstream_guardrail_bundle_refs", "downstream guardrail references are required"))
    for index, ref in enumerate(refs):
        path = f"$.downstream_guardrail_bundle_refs[{index}]"
        if not _text(ref.get("guardrail_bundle_id")):
            issues.append(ProcessModelRefreshImpactV2Issue("missing_guardrail_bundle_id", path + ".guardrail_bundle_id", "guardrail bundle ID is required"))
        if not _strings(ref.get("source_evidence_ids")):
            issues.append(ProcessModelRefreshImpactV2Issue("uncited_guardrail_bundle_ref", path + ".source_evidence_ids", "guardrail reference must cite evidence"))
        _require_false(issues, ref, path, ("activation_allowed", "guardrail_mutation_allowed", "release_state_mutation_allowed", "consequential_action_enabled"))
    for index, decision in enumerate(decisions):
        for bundle_id in _strings(decision.get("downstream_guardrail_bundle_ids")):
            if bundle_id not in ref_bundle_ids:
                issues.append(ProcessModelRefreshImpactV2Issue("missing_downstream_guardrail_reference_for_decision", f"$.process_stage_impact_decisions[{index}].downstream_guardrail_bundle_ids", "decision references must resolve to downstream guardrail bundle refs"))

    _validate_required_unsupported_path_dispositions(issues, decisions, notes)

    owners = list(_mapping_sequence(packet.get("reviewer_owner_fields")))
    if not owners:
        issues.append(ProcessModelRefreshImpactV2Issue("missing_reviewer_owner_fields", "$.reviewer_owner_fields", "reviewer-owner fields are required"))
    for index, owner in enumerate(owners):
        path = f"$.reviewer_owner_fields[{index}]"
        if not _text(owner.get("reviewer_owner")):
            issues.append(ProcessModelRefreshImpactV2Issue("missing_reviewer_owner", path + ".reviewer_owner", "reviewer owner is required"))
        if not _strings(owner.get("owned_decision_ids")):
            issues.append(ProcessModelRefreshImpactV2Issue("missing_owned_decision_ids", path + ".owned_decision_ids", "owned decisions are required"))
        if owner.get("owner_must_confirm_citations_before_refresh") is not True:
            issues.append(ProcessModelRefreshImpactV2Issue("missing_owner_confirmation_gate", path + ".owner_must_confirm_citations_before_refresh", "owner must confirm citations before refresh"))
        if owner.get("owner_must_confirm_no_active_mutation") is not True:
            issues.append(ProcessModelRefreshImpactV2Issue("missing_owner_no_mutation_gate", path + ".owner_must_confirm_no_active_mutation", "owner must confirm no active mutation before refresh"))

    commands = packet.get("offline_validation_commands")
    if not isinstance(commands, list) or not commands:
        issues.append(ProcessModelRefreshImpactV2Issue("missing_offline_validation_commands", "$.offline_validation_commands", "offline validation commands are required"))
    else:
        for index, command in enumerate(commands):
            if not _strings(command):
                issues.append(ProcessModelRefreshImpactV2Issue("invalid_validation_command", f"$.offline_validation_commands[{index}]", "validation command must be a list of strings"))

    attestations = _mapping(packet.get("attestations"))
    for key, expected in REQUIRED_ATTESTATIONS.items():
        if attestations.get(key) is not expected:
            issues.append(ProcessModelRefreshImpactV2Issue("missing_attestation", f"$.attestations.{key}", "required no-live/no-mutation attestation is missing"))
    return issues


def assert_valid_process_model_refresh_impact_v2(packet: Mapping[str, Any]) -> None:
    issues = validate_process_model_refresh_impact_v2(packet)
    if issues:
        raise ProcessModelRefreshImpactV2Error(issues)


def _process_stage_impact_decisions(work_order: Mapping[str, Any], impact_review: Mapping[str, Any], guardrail_candidate: Mapping[str, Any]) -> list[dict[str, Any]]:
    claims = list(_mapping_sequence(impact_review.get("process_stage_impact_claims")))
    affected_process_ids = _strings(impact_review.get("affected_process_ids")) or _strings(guardrail_candidate.get("affected_process_ids")) or ["unknown-process"]
    guardrail_ids = _guardrail_ids(guardrail_candidate)
    rows: list[dict[str, Any]] = []
    for index, decision in enumerate(_mapping_sequence(work_order.get("queued_requirement_decisions"))):
        requirement_id = _text(decision.get("requirement_id"))
        claim = _claim_for_requirement(claims, requirement_id)
        process_stage = _text(claim.get("process_stage")) or _stage_from_requirement(requirement_id)
        source_evidence_ids = _ordered_unique(
            _strings(decision.get("source_evidence_ids"))
            + _strings(claim.get("source_evidence_ids"))
            + _strings(guardrail_candidate.get("source_evidence_ids"))
        )
        work_order_decision = _text(decision.get("decision")) or "review"
        rows.append({
            "decision_id": f"process-refresh-impact-v2.{index + 1}.{_slug(requirement_id)}",
            "requirement_id": requirement_id,
            "work_order_decision": work_order_decision,
            "process_id": (_strings(decision.get("affected_process_ids")) or affected_process_ids)[0],
            "process_stage": process_stage,
            "impact_decision": _impact_decision(work_order_decision),
            "rationale": _text(claim.get("impact")) or "Carry fixture-backed requirement regeneration decision into process-stage impact review.",
            "source_evidence_ids": source_evidence_ids,
            "downstream_guardrail_bundle_ids": guardrail_ids,
            "reviewer_owner": _text(decision.get("reviewer_owner")) or _first_string(impact_review.get("reviewer_owners"), "ppd-process-reviewer"),
            "live_devhub_allowed": False,
            "official_action_allowed": False,
            "consequential_action_enabled": False,
            "process_mutation_allowed": False,
            "guardrail_mutation_allowed": False,
            "prompt_mutation_allowed": False,
            "surface_registry_mutation_allowed": False,
            "monitoring_mutation_allowed": False,
            "release_state_mutation_allowed": False,
            "agent_state_mutation_allowed": False,
        })
    return rows


def _unsupported_path_notes(impact_review: Mapping[str, Any], decisions: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    default_evidence = _ordered_unique([evidence for decision in decisions for evidence in _strings(decision.get("source_evidence_ids"))])
    notes: list[dict[str, Any]] = []
    for index, item in enumerate(_mapping_sequence(impact_review.get("unsupported_paths"))):
        notes.append({
            "path_id": _text(item.get("path_id")) or f"unsupported-path.{index + 1}",
            "process_stage": _text(item.get("process_stage")) or "unsupported path",
            "note": _text(item.get("note")) or _text(item.get("reason")) or "Unsupported path remains blocked pending reviewer confirmation.",
            "source_evidence_ids": _strings(item.get("source_evidence_ids")) or default_evidence,
            "reviewer_owner": _text(item.get("reviewer_owner")) or "ppd-process-reviewer",
            "live_devhub_allowed": False,
            "official_action_allowed": False,
            "consequential_action_enabled": False,
            "process_mutation_allowed": False,
        })
    for index, item in enumerate(_mapping_sequence(impact_review.get("blocked_action_carryovers"))):
        notes.append({
            "path_id": _text(item.get("action_id")) or f"blocked-action-carryover.{index + 1}",
            "process_stage": _text(item.get("process_stage")) or "consequential official action",
            "note": _text(item.get("reason")) or "Consequential action remains unsupported for unattended automation.",
            "source_evidence_ids": _strings(item.get("source_evidence_ids")) or default_evidence,
            "reviewer_owner": _text(item.get("reviewer_owner")) or "ppd-process-reviewer",
            "live_devhub_allowed": False,
            "official_action_allowed": False,
            "consequential_action_enabled": False,
            "process_mutation_allowed": False,
        })
    if not notes:
        notes.append({
            "path_id": "unsupported-path.default-official-actions",
            "process_stage": "submission",
            "note": "Submission, certification, official upload, payment, scheduling, cancellation, and release activation remain unsupported in this offline impact packet.",
            "source_evidence_ids": default_evidence,
            "reviewer_owner": "ppd-process-reviewer",
            "live_devhub_allowed": False,
            "official_action_allowed": False,
            "consequential_action_enabled": False,
            "process_mutation_allowed": False,
        })
    return notes


def _downstream_guardrail_bundle_refs(guardrail_candidate: Mapping[str, Any], decisions: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    bundle_id = _text(guardrail_candidate.get("active_guardrail_bundle_id")) or _text(guardrail_candidate.get("guardrail_bundle_id")) or "candidate-guardrail-bundle"
    default_evidence = _ordered_unique([evidence for decision in decisions for evidence in _strings(decision.get("source_evidence_ids"))])
    refs: list[dict[str, Any]] = []
    predicates = list(_mapping_sequence(guardrail_candidate.get("cited_predicate_additions"))) + list(_mapping_sequence(guardrail_candidate.get("cited_predicate_removals")))
    if not predicates:
        predicates = [{"predicate_id": bundle_id, "source_evidence_ids": default_evidence}]
    for index, predicate in enumerate(predicates):
        refs.append({
            "ref_id": f"downstream-guardrail-ref.{index + 1}.{_slug(_text(predicate.get('predicate_id')) or bundle_id)}",
            "guardrail_bundle_id": bundle_id,
            "predicate_id": _text(predicate.get("predicate_id")) or bundle_id,
            "operation": _text(predicate.get("operation")) or "review_candidate_predicate",
            "source_evidence_ids": _strings(predicate.get("source_evidence_ids")) or _citation_ids(predicate.get("citations")) or default_evidence,
            "activation_allowed": False,
            "guardrail_mutation_allowed": False,
            "release_state_mutation_allowed": False,
            "consequential_action_enabled": False,
        })
    return refs


def _reviewer_owner_fields(decisions: Sequence[Mapping[str, Any]], impact_review: Mapping[str, Any], guardrail_candidate: Mapping[str, Any]) -> list[dict[str, Any]]:
    owner_to_decisions: dict[str, list[str]] = {}
    for decision in decisions:
        owner_to_decisions.setdefault(_text(decision.get("reviewer_owner")) or "ppd-process-reviewer", []).append(_text(decision.get("decision_id")))
    for owner in _strings(impact_review.get("reviewer_owners")) + _strings(guardrail_candidate.get("reviewer_owners")):
        owner_to_decisions.setdefault(owner, [])
    rows = []
    for owner in sorted(owner_to_decisions):
        rows.append({
            "reviewer_owner": owner,
            "owned_decision_ids": sorted(item for item in owner_to_decisions[owner] if item) or ["review-downstream-guardrail-references"],
            "owner_must_confirm_citations_before_refresh": True,
            "owner_must_confirm_no_active_mutation": True,
        })
    return rows


def _validate_required_unsupported_path_dispositions(issues: list[ProcessModelRefreshImpactV2Issue], decisions: Sequence[Mapping[str, Any]], notes: Sequence[Mapping[str, Any]]) -> None:
    note_haystacks = [_row_haystack(note, ("path_id", "process_stage", "note")) for note in notes]
    for index, decision in enumerate(decisions):
        if not _requires_unsupported_path_disposition(decision):
            continue
        decision_terms = _decision_disposition_terms(decision)
        has_matching_note = any(any(term in haystack for term in decision_terms) for haystack in note_haystacks)
        if not has_matching_note:
            issues.append(ProcessModelRefreshImpactV2Issue(
                "missing_required_unsupported_path_disposition",
                f"$.process_stage_impact_decisions[{index}]",
                "official or consequential process-stage impacts require a cited unsupported-path disposition",
            ))


def _requires_unsupported_path_disposition(decision: Mapping[str, Any]) -> bool:
    haystack = _row_haystack(decision, ("requirement_id", "process_stage", "impact_decision", "rationale"))
    return any(keyword in haystack for keyword in UNSUPPORTED_PATH_KEYWORDS)


def _decision_disposition_terms(decision: Mapping[str, Any]) -> list[str]:
    haystack = _row_haystack(decision, ("requirement_id", "process_stage", "rationale"))
    return [keyword for keyword in UNSUPPORTED_PATH_KEYWORDS if keyword in haystack] or [_text(decision.get("process_stage")).lower()]


def _claim_for_requirement(claims: Sequence[Mapping[str, Any]], requirement_id: str) -> Mapping[str, Any]:
    for claim in claims:
        if requirement_id and requirement_id in _strings(claim.get("affected_requirement_ids")):
            return claim
    return claims[0] if claims else {}


def _stage_from_requirement(requirement_id: str) -> str:
    if "upload" in requirement_id or "correction" in requirement_id:
        return "corrections/checksheets"
    if "pdf" in requirement_id or "document" in requirement_id or "plan" in requirement_id:
        return "document preparation"
    if "trade" in requirement_id or "license" in requirement_id:
        return "eligibility screening"
    return "process impact review"


def _impact_decision(work_order_decision: str) -> str:
    if work_order_decision == "unchanged":
        return "retain_process_stage_without_active_mutation"
    if work_order_decision == "regenerate":
        return "queue_process_stage_refresh_review"
    return "queue_process_stage_human_review"


def _guardrail_ids(packet: Mapping[str, Any]) -> list[str]:
    return _ordered_unique(_strings(packet.get("affected_guardrail_ids")) + [_text(packet.get("active_guardrail_bundle_id")) or _text(packet.get("guardrail_bundle_id"))])


def _require_false(issues: list[ProcessModelRefreshImpactV2Issue], row: Mapping[str, Any], path: str, keys: Sequence[str]) -> None:
    for key in keys:
        if row.get(key) is not False:
            issues.append(ProcessModelRefreshImpactV2Issue("forbidden_live_or_mutating_claim", path + "." + key, "live execution, consequential action enablement, official action, and active mutations must be blocked"))


def _safety_issues(value: Any, path: str = "$") -> list[ProcessModelRefreshImpactV2Issue]:
    issues: list[ProcessModelRefreshImpactV2Issue] = []
    if isinstance(value, Mapping):
        for key, item in value.items():
            child_path = f"{path}.{key}"
            key_text = str(key).lower()
            if item is True and key_text in FORBIDDEN_TRUE_KEYS:
                issues.append(ProcessModelRefreshImpactV2Issue("forbidden_live_or_mutating_claim", child_path, "unsafe live, consequential-action, or mutation flag is true"))
            if item and key_text in FORBIDDEN_FACT_KEYS:
                issues.append(ProcessModelRefreshImpactV2Issue("forbidden_private_or_authenticated_fact", child_path, "private or authenticated facts are not allowed in fixture impact packets"))
            issues.extend(_safety_issues(item, child_path))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            issues.extend(_safety_issues(item, f"{path}[{index}]"))
    elif isinstance(value, str):
        lowered = value.lower()
        for phrase in FORBIDDEN_TEXT:
            if phrase in lowered:
                issues.append(ProcessModelRefreshImpactV2Issue("forbidden_private_raw_or_live_reference", path, "packet must not include private, raw, live-execution, mutation, consequential-action, or outcome-guarantee references"))
                break
    return issues


def _packet_id(packet: Mapping[str, Any], fallback: str) -> str:
    return _text(packet.get("packet_id")) or _text(packet.get("candidate_id")) or _text(packet.get("rehearsal_id")) or fallback


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _mapping_sequence(value: Any) -> Sequence[Mapping[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _strings(value: Any) -> list[str]:
    if isinstance(value, str) and value:
        return [value]
    if isinstance(value, list):
        return [item for item in value if isinstance(item, str) and item]
    return []


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _first_string(value: Any, fallback: str) -> str:
    strings = _strings(value)
    return strings[0] if strings else fallback


def _citation_ids(value: Any) -> list[str]:
    ids: list[str] = []
    for citation in _mapping_sequence(value):
        for key in ("citation_id", "source_evidence_id", "source_id", "fixture_id"):
            text = _text(citation.get(key))
            if text:
                ids.append(text)
                break
    return _ordered_unique(ids)


def _row_haystack(row: Mapping[str, Any], keys: Sequence[str]) -> str:
    return " ".join(_text(row.get(key)).lower() for key in keys)


def _ordered_unique(values: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            ordered.append(value)
    return ordered


def _slug(value: str) -> str:
    chars = [char.lower() if char.isalnum() else "-" for char in value]
    return "-".join(part for part in "".join(chars).split("-") if part) or "item"
