"""Fixture-first user gap analysis for draft preview bridge v1.

The bridge intentionally works from committed fixtures only. It does not read
private files, open DevHub, or perform official actions. The output is shaped
for agent-facing draft preview consumers that need cited prompts and blockers
before any reversible draft handoff can be treated as ready for user review.
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping
import json

JsonObject = dict[str, Any]


PRIVATE_PATH_MARKERS = (
    "/home/",
    "/Users/",
    "C:\\Users\\",
    "private_file_path",
    "auth_state",
    "storage_state",
    "session_state",
    "trace.zip",
    ".har",
    "cookie",
    "credential",
    "password",
    "mfa",
)

RAW_ARTIFACT_KEYS = {
    "raw_document",
    "raw_document_text",
    "raw_html",
    "html_body",
    "browser_trace",
    "trace_path",
    "har_path",
    "screenshot",
    "screenshot_path",
    "session_file",
    "storage_state",
    "auth_state",
    "downloaded_document_path",
}

MUTATION_FLAG_KEYS = {
    "active_prompt_mutation",
    "active_guardrail_mutation",
    "active_source_mutation",
    "active_surface_registry_mutation",
    "active_release_state_mutation",
    "active_agent_state_mutation",
    "mutates_prompt",
    "mutates_guardrail",
    "mutates_sources",
    "mutates_surface_registry",
    "mutates_release_state",
    "mutates_agent_state",
}

GUARANTEE_PHRASES = (
    "will be approved",
    "guaranteed approval",
    "guarantees approval",
    "permit will issue",
    "permit is approved",
    "approval is guaranteed",
    "inspection will pass",
    "no review required",
)

FINAL_OFFICIAL_ACTION_PHRASES = (
    "submit the application",
    "submit permit request",
    "certify the acknowledgement",
    "certify acknowledgement",
    "upload to official record",
    "officially upload",
    "pay the fee",
    "submit payment",
    "schedule inspection",
    "cancel permit",
    "withdraw application",
    "request final approval",
)

CONSEQUENTIAL_CLASSIFICATIONS = {"consequential_official", "financial", "authenticated_write"}
REQUIRED_CITED_COLLECTIONS = (
    "cited_missing_fact_prompts",
    "stale_conflict_notices",
    "field_level_draft_blockers",
    "user_review_checkpoints",
    "next_safe_read_only_actions",
)


def load_fixture_packet(path: str | Path) -> JsonObject:
    """Load a deterministic bridge fixture packet from disk."""

    with Path(path).open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("fixture packet must be a JSON object")
    return data


def build_user_gap_analysis(
    *,
    user_gap_fixture: Mapping[str, Any],
    process_model_fixture: Mapping[str, Any],
    guardrail_fixture: Mapping[str, Any],
    handoff_packet_v4: Mapping[str, Any],
) -> JsonObject:
    """Build a deterministic draft-preview user gap analysis.

    Inputs are fixture dictionaries, not live crawl or authenticated state. The
    function keeps source citations attached to every user-facing prompt or
    notice so an agent can ask for missing facts without guessing.
    """

    case_id = _require_string(user_gap_fixture, "case_id")
    process_id = _require_string(process_model_fixture, "process_id")
    handoff_id = _require_string(handoff_packet_v4, "handoff_id")

    known_facts = _as_mapping(user_gap_fixture.get("known_facts", {}))
    stale_fact_ids = _fact_ids(user_gap_fixture.get("stale_evidence", []))
    conflict_fact_ids = _fact_ids(user_gap_fixture.get("conflicting_evidence", []))

    required_facts = _as_list(process_model_fixture.get("required_user_facts", []))
    missing_prompts = _missing_fact_prompts(required_facts, known_facts, stale_fact_ids, conflict_fact_ids)
    missing_fact_ids = {prompt["fact_id"] for prompt in missing_prompts}

    stale_notices = _evidence_notices(
        user_gap_fixture.get("stale_evidence", []),
        notice_type="stale_evidence",
    )
    conflict_notices = _evidence_notices(
        user_gap_fixture.get("conflicting_evidence", []),
        notice_type="conflicting_evidence",
    )

    field_blockers = _field_level_blockers(
        handoff_packet_v4.get("draft_fields", []),
        missing_fact_ids=missing_fact_ids,
        stale_fact_ids=stale_fact_ids,
        conflict_fact_ids=conflict_fact_ids,
        required_facts=required_facts,
    )

    checkpoints = _user_review_checkpoints(guardrail_fixture, handoff_packet_v4, field_blockers)
    next_safe_actions = _next_safe_read_only_actions(guardrail_fixture)
    attestations = _attestations(user_gap_fixture, process_model_fixture, guardrail_fixture, handoff_packet_v4, next_safe_actions)

    analysis = {
        "analysis_id": f"user-gap-analysis::{handoff_id}",
        "bridge_version": "draft_preview_bridge_v1",
        "case_id": case_id,
        "process_id": process_id,
        "handoff_id": handoff_id,
        "cited_missing_fact_prompts": missing_prompts,
        "stale_conflict_notices": stale_notices + conflict_notices,
        "field_level_draft_blockers": field_blockers,
        "user_review_checkpoints": checkpoints,
        "next_safe_read_only_actions": next_safe_actions,
        "attestations": attestations,
    }
    validate_user_gap_analysis_bridge_v1_output(analysis)
    return analysis


def build_user_gap_analysis_from_packet(packet: Mapping[str, Any]) -> JsonObject:
    """Build analysis from a single combined fixture packet."""

    validate_user_gap_analysis_bridge_v1_packet(packet)
    return build_user_gap_analysis(
        user_gap_fixture=_as_mapping(packet.get("user_gap_fixture", {})),
        process_model_fixture=_as_mapping(packet.get("process_model_fixture", {})),
        guardrail_fixture=_as_mapping(packet.get("guardrail_fixture", {})),
        handoff_packet_v4=_as_mapping(packet.get("handoff_packet_v4", {})),
    )


def validate_user_gap_analysis_bridge_v1_packet(packet: Mapping[str, Any]) -> None:
    """Reject unsafe or unsupported fixture input before bridge analysis.

    The validator is intentionally conservative: committed bridge fixtures may
    contain normalized public facts and citations, but not private/authenticated
    facts, raw browser artifacts, outcome guarantees, official-action language,
    or active mutation flags for prompts, guardrails, sources, surfaces,
    release state, or agent state.
    """

    packet_obj = _as_mapping(packet)
    violations: list[str] = []
    process_model = _as_mapping(packet_obj.get("process_model_fixture", {}))
    guardrail = _as_mapping(packet_obj.get("guardrail_fixture", {}))
    user_gap = _as_mapping(packet_obj.get("user_gap_fixture", {}))
    handoff = _as_mapping(packet_obj.get("handoff_packet_v4", {}))

    process_id = _optional_string(process_model, "process_id")
    supported_process_ids = set(_strings(packet_obj.get("supported_process_ids", []))) or ({process_id} if process_id else set())
    for location, value in (
        ("process_model_fixture.process_id", process_id),
        ("guardrail_fixture.process_id", _optional_string(guardrail, "process_id")),
        ("user_gap_fixture.process_id", _optional_string(user_gap, "process_id")),
        ("handoff_packet_v4.process_id", _optional_string(handoff, "process_id")),
    ):
        if value and value not in supported_process_ids:
            violations.append(f"unsupported process id at {location}: {value}")
    ids = {value for value in (
        process_id,
        _optional_string(guardrail, "process_id"),
        _optional_string(user_gap, "process_id"),
        _optional_string(handoff, "process_id"),
    ) if value}
    if len(ids) > 1:
        violations.append("process id mismatch across bridge fixtures")

    _collect_recursive_policy_violations(packet_obj, path="packet", violations=violations)
    _validate_fixture_citations(process_model, guardrail, user_gap, handoff, violations)
    _validate_handoff_draft_values(user_gap, handoff, violations)
    _validate_actions_are_read_only(guardrail, handoff, violations)

    if violations:
        raise ValueError("draft preview bridge v1 validation failed: " + "; ".join(violations))


def validate_user_gap_analysis_bridge_v1_output(analysis: Mapping[str, Any]) -> None:
    """Reject unsafe or uncited bridge output before agent consumption."""

    analysis_obj = _as_mapping(analysis)
    violations: list[str] = []
    if analysis_obj.get("bridge_version") != "draft_preview_bridge_v1":
        violations.append("unsupported bridge version")
    _collect_recursive_policy_violations(analysis_obj, path="analysis", violations=violations)
    for collection_name in REQUIRED_CITED_COLLECTIONS:
        for index, item in enumerate(_as_list(analysis_obj.get(collection_name, []))):
            item_obj = _as_mapping(item)
            citations = _strings(item_obj.get("citations", []))
            if not citations:
                violations.append(f"uncited {collection_name}[{index}]")
            if collection_name == "field_level_draft_blockers" and item_obj.get("blocked") is True:
                if not _strings(item_obj.get("reasons", [])):
                    violations.append(f"missing blocker explanation at {collection_name}[{index}]")
                if not _strings(item_obj.get("blocking_fact_ids", [])):
                    violations.append(f"missing blocker fact ids at {collection_name}[{index}]")
    attestations = _as_mapping(analysis_obj.get("attestations", {}))
    for key in ("no_private_file_attestation", "no_devhub_attestation", "no_official_action_attestation"):
        if attestations.get(key) is not True:
            violations.append(f"failed attestation: {key}")
    if violations:
        raise ValueError("draft preview bridge v1 output validation failed: " + "; ".join(violations))


def _missing_fact_prompts(
    required_facts: list[Any],
    known_facts: Mapping[str, Any],
    stale_fact_ids: set[str],
    conflict_fact_ids: set[str],
) -> list[JsonObject]:
    prompts: list[JsonObject] = []
    for item in required_facts:
        fact = _as_mapping(item)
        fact_id = _require_string(fact, "fact_id")
        known_value = known_facts.get(fact_id)
        reasons: list[str] = []
        if known_value in (None, ""):
            reasons.append("missing")
        if fact_id in stale_fact_ids:
            reasons.append("stale")
        if fact_id in conflict_fact_ids:
            reasons.append("conflicting")
        if not reasons:
            continue
        prompts.append(
            {
                "prompt_id": f"prompt::{fact_id}",
                "fact_id": fact_id,
                "prompt": _require_string(fact, "prompt"),
                "reason": "+".join(reasons),
                "citations": _strings(fact.get("citation_ids", [])),
                "blocks_draft_fields": _strings(fact.get("blocks_draft_fields", [])),
            }
        )
    return prompts


def _evidence_notices(entries: Any, *, notice_type: str) -> list[JsonObject]:
    notices: list[JsonObject] = []
    for entry in _as_list(entries):
        evidence = _as_mapping(entry)
        fact_id = _require_string(evidence, "fact_id")
        notices.append(
            {
                "notice_id": f"{notice_type}::{fact_id}",
                "notice_type": notice_type,
                "fact_id": fact_id,
                "message": _require_string(evidence, "message"),
                "citations": _strings(evidence.get("citation_ids", [])),
                "blocks_draft_fields": _strings(evidence.get("blocks_draft_fields", [])),
            }
        )
    return notices


def _field_level_blockers(
    draft_fields: Any,
    *,
    missing_fact_ids: set[str],
    stale_fact_ids: set[str],
    conflict_fact_ids: set[str],
    required_facts: list[Any],
) -> list[JsonObject]:
    fact_citations = {
        _require_string(_as_mapping(fact), "fact_id"): _strings(_as_mapping(fact).get("citation_ids", []))
        for fact in required_facts
    }
    blockers: list[JsonObject] = []
    for raw_field in _as_list(draft_fields):
        field = _as_mapping(raw_field)
        field_id = _require_string(field, "field_id")
        required_fact_ids = set(_strings(field.get("requires_fact_ids", [])))
        blocking_fact_ids = sorted(required_fact_ids & (missing_fact_ids | stale_fact_ids | conflict_fact_ids))
        if not blocking_fact_ids:
            continue
        reasons: list[str] = []
        for fact_id in blocking_fact_ids:
            if fact_id in missing_fact_ids:
                reasons.append(f"{fact_id}:missing")
            if fact_id in stale_fact_ids:
                reasons.append(f"{fact_id}:stale")
            if fact_id in conflict_fact_ids:
                reasons.append(f"{fact_id}:conflicting")
        citations = sorted({citation for fact_id in blocking_fact_ids for citation in fact_citations.get(fact_id, [])})
        blockers.append(
            {
                "field_id": field_id,
                "label": _require_string(field, "label"),
                "blocked": True,
                "blocking_fact_ids": blocking_fact_ids,
                "reasons": reasons,
                "citations": citations,
            }
        )
    return blockers


def _user_review_checkpoints(
    guardrail_fixture: Mapping[str, Any],
    handoff_packet_v4: Mapping[str, Any],
    field_blockers: list[JsonObject],
) -> list[JsonObject]:
    checkpoints: list[JsonObject] = []
    for item in _as_list(guardrail_fixture.get("user_review_checkpoints", [])):
        checkpoint = _as_mapping(item)
        checkpoints.append(
            {
                "checkpoint_id": _require_string(checkpoint, "checkpoint_id"),
                "label": _require_string(checkpoint, "label"),
                "required_before": _require_string(checkpoint, "required_before"),
                "citations": _strings(checkpoint.get("citation_ids", [])),
            }
        )
    for item in _as_list(handoff_packet_v4.get("user_review_checkpoints", [])):
        checkpoint = _as_mapping(item)
        checkpoints.append(
            {
                "checkpoint_id": _require_string(checkpoint, "checkpoint_id"),
                "label": _require_string(checkpoint, "label"),
                "required_before": _require_string(checkpoint, "required_before"),
                "citations": _strings(checkpoint.get("citation_ids", [])),
            }
        )
    if field_blockers:
        checkpoints.append(
            {
                "checkpoint_id": "checkpoint::resolve-field-blockers",
                "label": "User must resolve blocked draft fields before preview can be treated as review-ready.",
                "required_before": "draft_preview_review",
                "citations": sorted({citation for blocker in field_blockers for citation in blocker["citations"]}),
            }
        )
    return _dedupe_by_id(checkpoints, "checkpoint_id")


def _next_safe_read_only_actions(guardrail_fixture: Mapping[str, Any]) -> list[JsonObject]:
    actions: list[JsonObject] = []
    for raw_action in _as_list(guardrail_fixture.get("next_safe_read_only_actions", [])):
        action = _as_mapping(raw_action)
        if action.get("classification") != "read_only":
            continue
        if bool(action.get("requires_devhub_auth", False)):
            continue
        actions.append(
            {
                "action_id": _require_string(action, "action_id"),
                "label": _require_string(action, "label"),
                "classification": "read_only",
                "citations": _strings(action.get("citation_ids", [])),
            }
        )
    return actions


def _attestations(
    user_gap_fixture: Mapping[str, Any],
    process_model_fixture: Mapping[str, Any],
    guardrail_fixture: Mapping[str, Any],
    handoff_packet_v4: Mapping[str, Any],
    next_safe_actions: list[JsonObject],
) -> JsonObject:
    combined = {
        "user_gap_fixture": deepcopy(dict(user_gap_fixture)),
        "process_model_fixture": deepcopy(dict(process_model_fixture)),
        "guardrail_fixture": deepcopy(dict(guardrail_fixture)),
        "handoff_packet_v4": deepcopy(dict(handoff_packet_v4)),
    }
    no_private_files = not _contains_private_marker(combined)
    no_devhub = handoff_packet_v4.get("preview_mode") == "offline_fixture" and all(
        not action.get("requires_devhub_auth", False)
        for action in _as_list(guardrail_fixture.get("next_safe_read_only_actions", []))
        if _as_mapping(action).get("action_id") in {item["action_id"] for item in next_safe_actions}
    )
    no_official_action = not bool(handoff_packet_v4.get("official_action_performed", False)) and not any(
        _as_mapping(action).get("classification") in CONSEQUENTIAL_CLASSIFICATIONS
        for action in _as_list(handoff_packet_v4.get("handoff_actions", []))
    )
    return {
        "no_private_file_attestation": no_private_files,
        "no_devhub_attestation": no_devhub,
        "no_official_action_attestation": no_official_action,
        "attestation_basis": [
            "fixture inputs only",
            "offline draft preview handoff v4 packet",
            "safe actions filtered to unauthenticated read-only classifications",
        ],
    }


def _validate_fixture_citations(
    process_model: Mapping[str, Any],
    guardrail: Mapping[str, Any],
    user_gap: Mapping[str, Any],
    handoff: Mapping[str, Any],
    violations: list[str],
) -> None:
    for index, fact in enumerate(_as_list(process_model.get("required_user_facts", []))):
        fact_obj = _as_mapping(fact)
        if not _strings(fact_obj.get("citation_ids", [])):
            violations.append(f"uncited required fact at process_model_fixture.required_user_facts[{index}]")
    for collection in ("stale_evidence", "conflicting_evidence"):
        for index, evidence in enumerate(_as_list(user_gap.get(collection, []))):
            evidence_obj = _as_mapping(evidence)
            if not _strings(evidence_obj.get("citation_ids", [])):
                violations.append(f"uncited evidence at user_gap_fixture.{collection}[{index}]")
    for collection in ("user_review_checkpoints", "next_safe_read_only_actions"):
        for index, item in enumerate(_as_list(guardrail.get(collection, []))):
            item_obj = _as_mapping(item)
            if not _strings(item_obj.get("citation_ids", [])):
                violations.append(f"uncited guardrail item at guardrail_fixture.{collection}[{index}]")
    for index, item in enumerate(_as_list(handoff.get("user_review_checkpoints", []))):
        item_obj = _as_mapping(item)
        if not _strings(item_obj.get("citation_ids", [])):
            violations.append(f"uncited handoff checkpoint at handoff_packet_v4.user_review_checkpoints[{index}]")


def _validate_handoff_draft_values(user_gap: Mapping[str, Any], handoff: Mapping[str, Any], violations: list[str]) -> None:
    known_facts = _as_mapping(user_gap.get("known_facts", {}))
    for index, field in enumerate(_as_list(handoff.get("draft_fields", []))):
        field_obj = _as_mapping(field)
        field_path = f"handoff_packet_v4.draft_fields[{index}]"
        proposed = field_obj.get("proposed_value", field_obj.get("value"))
        if proposed in (None, ""):
            continue
        source_fact_ids = _strings(field_obj.get("value_source_fact_ids", field_obj.get("source_fact_ids", [])))
        if not source_fact_ids:
            violations.append(f"ungrounded draft value at {field_path}")
            continue
        for fact_id in source_fact_ids:
            if fact_id not in known_facts:
                violations.append(f"draft value at {field_path} references unknown fact {fact_id}")
                continue
            fact_value = _fact_value(known_facts[fact_id])
            if fact_value in (None, ""):
                violations.append(f"draft value at {field_path} references empty fact {fact_id}")
            if isinstance(fact_value, str) and isinstance(proposed, str) and proposed != fact_value:
                violations.append(f"draft value at {field_path} is not grounded in fact {fact_id}")
            if _contains_private_marker(fact_value):
                violations.append(f"draft value at {field_path} references private fact {fact_id}")


def _validate_actions_are_read_only(guardrail: Mapping[str, Any], handoff: Mapping[str, Any], violations: list[str]) -> None:
    for index, action in enumerate(_as_list(guardrail.get("next_safe_read_only_actions", []))):
        action_obj = _as_mapping(action)
        if action_obj.get("classification") != "read_only":
            violations.append(f"non-read-only next safe action at guardrail_fixture.next_safe_read_only_actions[{index}]")
        if action_obj.get("requires_devhub_auth") is True:
            violations.append(f"authenticated next safe action at guardrail_fixture.next_safe_read_only_actions[{index}]")
    if handoff.get("official_action_performed") is True:
        violations.append("handoff packet records official action performed")
    for index, action in enumerate(_as_list(handoff.get("handoff_actions", []))):
        action_obj = _as_mapping(action)
        if action_obj.get("classification") in CONSEQUENTIAL_CLASSIFICATIONS:
            violations.append(f"consequential handoff action at handoff_packet_v4.handoff_actions[{index}]")


def _collect_recursive_policy_violations(value: Any, *, path: str, violations: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            key_text = str(key)
            child_path = f"{path}.{key_text}"
            if key_text in RAW_ARTIFACT_KEYS and item not in (None, "", [], {}):
                violations.append(f"raw document/session/browser artifact at {child_path}")
            if key_text in MUTATION_FLAG_KEYS and item not in (None, False, "", [], {}):
                violations.append(f"active mutation flag at {child_path}")
            if key_text in {"source_type", "privacy_classification", "auth_scope"} and item in {
                "devhub_authenticated",
                "authenticated",
                "private",
                "account_scoped",
            }:
                violations.append(f"private or authenticated fact at {child_path}")
            _collect_recursive_policy_violations(item, path=child_path, violations=violations)
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            _collect_recursive_policy_violations(item, path=f"{path}[{index}]", violations=violations)
        return
    if isinstance(value, str):
        lowered = value.lower()
        if _contains_private_marker(value):
            violations.append(f"private/authenticated artifact marker at {path}")
        if any(phrase in lowered for phrase in GUARANTEE_PHRASES):
            violations.append(f"legal or permitting outcome guarantee at {path}")
        if any(phrase in lowered for phrase in FINAL_OFFICIAL_ACTION_PHRASES):
            violations.append(f"final official-action language at {path}")


def _fact_value(value: Any) -> Any:
    if isinstance(value, Mapping) and "value" in value:
        return value.get("value")
    return value


def _fact_ids(entries: Any) -> set[str]:
    return {_require_string(_as_mapping(entry), "fact_id") for entry in _as_list(entries)}


def _contains_private_marker(value: Any) -> bool:
    if isinstance(value, str):
        return any(marker.lower() in value.lower() for marker in PRIVATE_PATH_MARKERS)
    if isinstance(value, Mapping):
        return any(_contains_private_marker(key) or _contains_private_marker(item) for key, item in value.items())
    if isinstance(value, list):
        return any(_contains_private_marker(item) for item in value)
    return False


def _dedupe_by_id(items: list[JsonObject], key: str) -> list[JsonObject]:
    seen: set[str] = set()
    result: list[JsonObject] = []
    for item in items:
        item_id = _require_string(item, key)
        if item_id in seen:
            continue
        seen.add(item_id)
        result.append(item)
    return result


def _require_string(mapping: Mapping[str, Any], key: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"expected non-empty string for {key}")
    return value


def _optional_string(mapping: Mapping[str, Any], key: str) -> str | None:
    value = mapping.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"expected string for {key}")
    return value or None


def _strings(value: Any) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError("expected list of strings")
    return list(value)


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError("expected JSON object")
    return value


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("expected JSON array")
    return value
