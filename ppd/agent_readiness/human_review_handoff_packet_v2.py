from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from ppd.agent_readiness.agent_readiness_replay_packet_v2 import validate_agent_readiness_replay_packet_v2
from ppd.refresh_implementation_proposal_v2 import validate_refresh_implementation_proposal_v2

PACKET_TYPE = "ppd.human_review_handoff_packet.v2"
PACKET_VERSION = 2

REQUIRED_ATTESTATIONS = {
    "fixture_first",
    "no_live",
    "no_auth",
    "no_release",
    "no_official_action",
    "no_private_artifacts",
    "no_prompt_mutation",
    "no_guardrail_mutation",
    "no_source_mutation",
    "no_surface_registry_mutation",
}

ALLOWED_DEFERRAL_DISPOSITIONS = {
    "carry_forward_pending_attended_review",
    "blocking_until_reviewer_disposition",
    "resolved_by_cited_reviewer_disposition",
}

OFFLINE_VALIDATION_COMMANDS = [
    ["python3", "-m", "py_compile", "ppd/agent_readiness/human_review_handoff_packet_v2.py"],
    ["python3", "-m", "pytest", "ppd/tests/test_human_review_handoff_packet_v2.py"],
    ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
]

_FORBIDDEN_KEYS = {
    "authenticated_fact",
    "authenticated_facts",
    "authenticated_value",
    "authenticated_values",
    "auth_state",
    "browser_artifact",
    "browser_artifacts",
    "browser_state",
    "cookies",
    "credential",
    "credentials",
    "downloaded_document",
    "downloaded_documents",
    "har",
    "har_file",
    "password",
    "payment_details",
    "private_fact",
    "private_facts",
    "private_file",
    "private_path",
    "raw_authenticated_fact",
    "raw_authenticated_value",
    "raw_browser_artifact",
    "raw_crawl_output",
    "raw_download",
    "raw_html",
    "raw_pdf",
    "screenshot",
    "session_artifact",
    "session_artifacts",
    "session_state",
    "storage_state",
    "token",
    "trace",
    "trace_file",
    "upload_payload",
}

_MUTATION_FLAG_KEYS = {
    "active_agent_state_mutation",
    "active_agent_state_mutation_flag",
    "active_guardrail_mutation",
    "active_guardrail_mutation_flag",
    "active_monitoring_mutation",
    "active_monitoring_mutation_flag",
    "active_prompt_mutation",
    "active_prompt_mutation_flag",
    "active_release_state_mutation",
    "active_release_state_mutation_flag",
    "active_source_mutation",
    "active_source_mutation_flag",
    "active_source_registry_mutation",
    "active_source_registry_mutation_flag",
    "active_surface_registry_mutation",
    "active_surface_registry_mutation_flag",
    "agent_state_mutation_enabled",
    "guardrail_mutation_enabled",
    "monitoring_mutation_enabled",
    "prompt_mutation_enabled",
    "release_state_mutation_enabled",
    "source_mutation_enabled",
    "source_registry_mutation_enabled",
    "surface_registry_mutation_enabled",
}

_FORBIDDEN_TEXT_PATTERNS = (
    re.compile(r"\b(?:opened|logged into|launched)\s+devhub\b", re.IGNORECASE),
    re.compile(r"\b(?:live crawl|live browser|live network|live llm)\s+(?:ran|completed|executed)\b", re.IGNORECASE),
    re.compile(r"\b(?:executed|completed|ran)\s+(?:a\s+)?(?:live crawl|live browser|live network|live llm)\b", re.IGNORECASE),
    re.compile(r"\b(?:permit|approval|issuance|inspection|application|upload|payment)\s+(?:will|is guaranteed to|is certain to)\s+(?:be\s+)?(?:approved|issued|pass|accepted|processed|completed)\b", re.IGNORECASE),
    re.compile(r"\bguarantee(?:d|s)?\s+(?:approval|issuance|acceptance|permit outcome|inspection passage|legal outcome|permitting outcome)\b", re.IGNORECASE),
    re.compile(r"\b(?:finally|final|officially)\s+(?:submit|submitted|submission|pay|paid|payment|upload|uploaded|schedule|scheduled|cancel|cancelled|canceled)\b", re.IGNORECASE),
    re.compile(r"\b(?:submitted|uploaded|paid|scheduled|cancelled|canceled)\s+(?:the\s+)?(?:application|permit|payment|inspection|record|upload)\b", re.IGNORECASE),
    re.compile(r"\b(?:raw crawl|raw pdf|raw html|browser artifact|session artifact|session state|storage state|trace file|har file|downloaded document)\b", re.IGNORECASE),
    re.compile(r"\b(?:private|authenticated)\s+(?:fact|facts|value|values|devhub value|case fact)\b", re.IGNORECASE),
)


@dataclass(frozen=True)
class HumanReviewHandoffPacketV2ValidationResult:
    ok: bool
    errors: tuple[str, ...]


def load_json(path: str | Path) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"expected JSON object at {path}")
    return data


def build_human_review_handoff_packet_v2_from_fixture(path: str | Path) -> dict[str, Any]:
    fixture = load_json(path)
    source_packets = _mapping(fixture.get("source_packets"))
    return build_human_review_handoff_packet_v2(
        _mapping(source_packets.get("refresh_implementation_proposal_v2")),
        _mapping(source_packets.get("agent_readiness_replay_packet_v2")),
    )


def build_human_review_handoff_packet_v2(
    refresh_implementation_proposal_v2: Mapping[str, Any],
    agent_readiness_replay_packet_v2: Mapping[str, Any],
) -> dict[str, Any]:
    proposal_result = validate_refresh_implementation_proposal_v2(dict(refresh_implementation_proposal_v2))
    if not proposal_result.ok:
        raise ValueError("invalid refresh implementation proposal v2: " + "; ".join(proposal_result.errors))

    replay_result = validate_agent_readiness_replay_packet_v2(agent_readiness_replay_packet_v2)
    if not replay_result.valid:
        raise ValueError("invalid agent readiness replay packet v2: " + "; ".join(replay_result.problems))

    checklist = _reviewer_checklist_items(refresh_implementation_proposal_v2, agent_readiness_replay_packet_v2)
    deferrals = _unresolved_deferrals(refresh_implementation_proposal_v2, agent_readiness_replay_packet_v2)
    acceptance = _acceptance_criteria(checklist, deferrals)

    packet = {
        "packet_type": PACKET_TYPE,
        "packet_version": PACKET_VERSION,
        "mode": "fixture_first_offline_future_attended_review",
        "consumes": {
            "refresh_implementation_proposal_v2": _text(refresh_implementation_proposal_v2.get("proposal_version")),
            "agent_readiness_replay_packet_v2": _text(agent_readiness_replay_packet_v2.get("packet_type")),
        },
        "reviewer_checklist_items": checklist,
        "unresolved_deferrals": deferrals,
        "acceptance_criteria": acceptance,
        "rollback_verification": _rollback_verification(refresh_implementation_proposal_v2, agent_readiness_replay_packet_v2),
        "offline_validation_commands": list(OFFLINE_VALIDATION_COMMANDS),
        "attestations": {key: True for key in sorted(REQUIRED_ATTESTATIONS)},
        "review_status": "ready_for_future_attended_human_review",
    }
    require_human_review_handoff_packet_v2(packet)
    return packet


def validate_human_review_handoff_packet_v2(packet: Mapping[str, Any]) -> HumanReviewHandoffPacketV2ValidationResult:
    errors: list[str] = []
    if packet.get("packet_type") != PACKET_TYPE:
        errors.append(f"packet_type must be {PACKET_TYPE}")
    if packet.get("packet_version") != PACKET_VERSION:
        errors.append("packet_version must be 2")
    if packet.get("mode") != "fixture_first_offline_future_attended_review":
        errors.append("mode must be fixture_first_offline_future_attended_review")

    consumes = _mapping(packet.get("consumes"))
    if consumes.get("refresh_implementation_proposal_v2") != "refresh_implementation_proposal_v2":
        errors.append("consumes.refresh_implementation_proposal_v2 must reference refresh implementation proposal v2")
    if consumes.get("agent_readiness_replay_packet_v2") != "ppd.agent_readiness_replay_packet.v2":
        errors.append("consumes.agent_readiness_replay_packet_v2 must reference agent readiness replay packet v2")

    _validate_cited_rows(errors, packet.get("reviewer_checklist_items"), "reviewer_checklist_items")
    _validate_cited_rows(errors, packet.get("unresolved_deferrals"), "unresolved_deferrals")
    _validate_cited_rows(errors, packet.get("acceptance_criteria"), "acceptance_criteria")
    _validate_cited_rows(errors, packet.get("rollback_verification"), "rollback_verification")
    _validate_deferral_dispositions(errors, packet.get("unresolved_deferrals"))

    commands = _sequence(packet.get("offline_validation_commands"))
    if not commands:
        errors.append("offline_validation_commands must be non-empty")
    for index, command in enumerate(commands):
        if not _string_list(command):
            errors.append(f"offline_validation_commands[{index}] must be a command list")

    attestations = _mapping(packet.get("attestations"))
    for key in sorted(REQUIRED_ATTESTATIONS):
        if attestations.get(key) is not True:
            errors.append(f"attestations.{key} must be true")

    if _text(packet.get("review_status")) != "ready_for_future_attended_human_review":
        errors.append("review_status must be ready_for_future_attended_human_review")

    _reject_unsafe_content(packet, "$", errors)
    return HumanReviewHandoffPacketV2ValidationResult(not errors, tuple(errors))


def require_human_review_handoff_packet_v2(packet: Mapping[str, Any]) -> None:
    result = validate_human_review_handoff_packet_v2(packet)
    if not result.ok:
        raise ValueError("invalid human review handoff packet v2: " + "; ".join(result.errors))


def _reviewer_checklist_items(proposal: Mapping[str, Any], replay: Mapping[str, Any]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for row in _mapping_sequence(proposal.get("proposed_source_patch_rows")):
        items.append(_checklist_item("proposal-source", row.get("patch_id"), "Confirm proposed source registry row remains citation-backed and proposed-only.", row.get("citations"), ["refresh_implementation_proposal_v2"]))
    for row in _mapping_sequence(proposal.get("proposed_surface_patch_rows")):
        items.append(_checklist_item("proposal-surface", row.get("patch_id"), "Confirm read-only surface row has reviewer owner, redaction disposition, and selector confidence.", row.get("citations"), ["refresh_implementation_proposal_v2"]))
    for row in _mapping_sequence(proposal.get("proposed_guardrail_patch_rows")):
        items.append(_checklist_item("proposal-guardrail", row.get("patch_id"), "Confirm guardrail row is still proposed-only and does not enable consequential capability.", row.get("citations"), ["refresh_implementation_proposal_v2"]))

    for prompt in _mapping_sequence(replay.get("expected_missing_fact_prompts")):
        items.append(_checklist_item("replay-missing-fact", prompt.get("prompt_id"), "Review missing-fact prompt wording before any attended case use.", _evidence_citations(prompt), ["agent_readiness_replay_packet_v2"]))
    for action in _mapping_sequence(replay.get("next_safe_actions")):
        items.append(_checklist_item("replay-safe-action", action.get("action_id"), "Confirm next safe action remains read-only, local preview, reversible draft, or manual handoff.", _evidence_citations(action), ["agent_readiness_replay_packet_v2"]))
    return items


def _unresolved_deferrals(proposal: Mapping[str, Any], replay: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for notice in _mapping_sequence(replay.get("stale_evidence_notices")):
        rows.append(_deferral("stale-evidence", notice.get("notice_id"), "Stale evidence remains unresolved until a reviewer accepts or replaces the cited evidence.", _evidence_citations(notice)))
    for notice in _mapping_sequence(replay.get("conflicting_evidence_notices")):
        rows.append(_deferral("conflicting-evidence", notice.get("conflict_id"), "Conflicting evidence remains unresolved until a reviewer records the accepted interpretation.", _evidence_citations(notice)))
    for block in _mapping_sequence(replay.get("blocked_action_explanations")):
        rows.append(_deferral("blocked-action", block.get("action_id"), "Consequential action remains deferred to an attended review checkpoint.", _evidence_citations(block)))
    for row in _mapping_sequence(proposal.get("proposed_guardrail_patch_rows")):
        if row.get("patch_kind") == "blocked_consequential_action_review_row":
            rows.append(_deferral("proposal-blocked-action", row.get("patch_id"), "Blocked-action proposal row must be reviewed before any migration decision.", row.get("citations")))
    return rows


def _acceptance_criteria(checklist: Sequence[Mapping[str, Any]], deferrals: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    checklist_refs = [_text(item.get("checklist_item_id")) for item in checklist if _text(item.get("checklist_item_id"))]
    deferral_refs = [_text(item.get("deferral_id")) for item in deferrals if _text(item.get("deferral_id"))]
    return [
        {
            "criterion_id": "all-reviewer-checklist-items-cited",
            "status": "pending_human_review",
            "summary": "Every reviewer checklist item must retain citations to fixture evidence from the consumed packets.",
            "checklist_refs": checklist_refs,
            "deferral_refs": [],
            "citations": _derived_citations(checklist),
        },
        {
            "criterion_id": "all-deferrals-resolved-or-carried-forward",
            "status": "pending_human_review",
            "summary": "Each unresolved deferral must be resolved by reviewer disposition or carried forward as blocking work.",
            "checklist_refs": [],
            "deferral_refs": deferral_refs,
            "citations": _derived_citations(deferrals),
        },
        {
            "criterion_id": "offline-validation-passes-before-review",
            "status": "pending_validation",
            "summary": "Offline validation commands must pass before the packet is used for an attended review.",
            "checklist_refs": checklist_refs[:3],
            "deferral_refs": deferral_refs[:3],
            "citations": [{"packet_field": "offline_validation_commands"}],
        },
    ]


def _rollback_verification(proposal: Mapping[str, Any], replay: Mapping[str, Any]) -> list[dict[str, Any]]:
    rollback_rows = _mapping_sequence(proposal.get("rollback_notes"))
    reviewer_rows = _mapping_sequence(replay.get("reviewer_owner_fields"))
    return [
        {
            "rollback_check_id": "discard-proposed-refresh-rows",
            "status": "pending_human_review",
            "summary": "Rollback is verified by discarding proposed refresh rows and leaving current registries unchanged.",
            "citations": _derived_citations(rollback_rows),
        },
        {
            "rollback_check_id": "preserve-offline-replay-only-state",
            "status": "pending_human_review",
            "summary": "Rollback is verified by confirming replay output remains fixture-only and does not mutate agent state.",
            "citations": _derived_citations(reviewer_rows),
        },
    ]


def _checklist_item(kind: str, raw_id: Any, summary: str, citations: Any, roles: list[str]) -> dict[str, Any]:
    item_id = _slug(_text(raw_id) or kind)
    return {
        "checklist_item_id": f"{kind}-{item_id}",
        "status": "pending_human_review",
        "summary": summary,
        "source_packet_roles": roles,
        "citations": _citation_list(citations),
    }


def _deferral(kind: str, raw_id: Any, summary: str, citations: Any) -> dict[str, Any]:
    item_id = _slug(_text(raw_id) or kind)
    return {
        "deferral_id": f"{kind}-{item_id}",
        "status": "unresolved",
        "summary": summary,
        "requires_attended_review": True,
        "disposition": "carry_forward_pending_attended_review",
        "citations": _citation_list(citations),
    }


def _evidence_citations(row: Mapping[str, Any]) -> list[dict[str, str]]:
    return [{"source_evidence_id": evidence_id} for evidence_id in _string_list(row.get("source_evidence_ids"))]


def _derived_citations(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    citations: list[dict[str, Any]] = []
    for row in rows:
        citations.extend(_citation_list(row.get("citations")))
    if not citations:
        citations.append({"packet_field": "derived_from_consumed_fixture_packets"})
    return citations


def _citation_list(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        rows = [dict(item) for item in value if isinstance(item, Mapping) and item]
        if rows:
            return rows
    return [{"packet_field": "derived_from_consumed_fixture_packets"}]


def _validate_cited_rows(errors: list[str], value: Any, field: str) -> None:
    rows = _mapping_sequence(value)
    if not rows:
        errors.append(f"{field} must be non-empty")
        return
    id_keys = {
        "reviewer_checklist_items": "checklist_item_id",
        "unresolved_deferrals": "deferral_id",
        "acceptance_criteria": "criterion_id",
        "rollback_verification": "rollback_check_id",
    }
    id_key = id_keys[field]
    for index, row in enumerate(rows):
        if not _text(row.get(id_key)):
            errors.append(f"{field}[{index}].{id_key} must be present")
        if not _text(row.get("status")):
            errors.append(f"{field}[{index}].status must be present")
        if not _text(row.get("summary")):
            errors.append(f"{field}[{index}].summary must be present")
        if not _mapping_sequence(row.get("citations")):
            errors.append(f"{field}[{index}].citations must be non-empty")


def _validate_deferral_dispositions(errors: list[str], value: Any) -> None:
    for index, row in enumerate(_mapping_sequence(value)):
        disposition = _text(row.get("disposition"))
        if disposition not in ALLOWED_DEFERRAL_DISPOSITIONS:
            errors.append(f"unresolved_deferrals[{index}].disposition must record a reviewer deferral disposition")


def _reject_unsafe_content(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            normalized = key_text.lower().replace("-", "_")
            child_path = f"{path}.{key_text}"
            if normalized in _FORBIDDEN_KEYS and child not in (None, "", [], {}):
                errors.append(f"{child_path} is not allowed in a human review handoff packet")
            if normalized in _MUTATION_FLAG_KEYS and _is_active_flag(child):
                errors.append(f"{child_path} declares an active source, surface-registry, guardrail, prompt, monitoring, release-state, or agent-state mutation flag")
            _reject_unsafe_content(child, child_path, errors)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child in enumerate(value):
            _reject_unsafe_content(child, f"{path}[{index}]", errors)
    elif isinstance(value, str):
        for pattern in _FORBIDDEN_TEXT_PATTERNS:
            if pattern.search(value):
                errors.append(f"{path} contains unsafe live, private, outcome, artifact, mutation, or official-action language")
                break


def _is_active_flag(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"true", "enabled", "active", "yes"}
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return bool(value)
    if isinstance(value, Mapping):
        return bool(value)
    return False


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _sequence(value: Any) -> Sequence[Any]:
    return value if isinstance(value, Sequence) and not isinstance(value, (str, bytes)) else ()


def _mapping_sequence(value: Any) -> tuple[Mapping[str, Any], ...]:
    return tuple(item for item in _sequence(value) if isinstance(item, Mapping))


def _string_list(value: Any) -> list[str]:
    return [item for item in _sequence(value) if isinstance(item, str) and item]


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "item"
