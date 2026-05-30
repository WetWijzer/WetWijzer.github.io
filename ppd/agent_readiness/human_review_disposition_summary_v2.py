from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from ppd.agent_readiness.human_review_handoff_packet_v2 import (
    build_human_review_handoff_packet_v2_from_fixture,
    validate_human_review_handoff_packet_v2,
)

PACKET_TYPE = "ppd.human_review_disposition_summary.v2"
PACKET_VERSION = 2

REQUIRED_ATTESTATIONS = {
    "fixture_first",
    "no_live",
    "no_auth",
    "no_official_action",
    "no_release_state_mutation",
}

ALLOWED_DECISIONS = {"accepted", "deferred", "rejected"}
OFFLINE_VALIDATION_COMMANDS = [
    ["python3", "-m", "py_compile", "ppd/agent_readiness/human_review_disposition_summary_v2.py"],
    ["python3", "-m", "pytest", "ppd/tests/test_human_review_disposition_summary_v2.py"],
    ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
]

_FORBIDDEN_KEYS = {
    "auth_state",
    "authenticated_fact",
    "authenticated_facts",
    "authenticated_value",
    "authenticated_values",
    "browser_artifact",
    "browser_artifacts",
    "browser_state",
    "cookies",
    "credential",
    "credentials",
    "crawl_artifact",
    "crawl_artifacts",
    "crawl_output",
    "devhub_session",
    "downloaded_document",
    "downloaded_documents",
    "har",
    "har_file",
    "password",
    "payment_details",
    "pdf_artifact",
    "pdf_artifacts",
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
    "raw_session_artifact",
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
    "active_agent_state",
    "active_agent_state_mutation",
    "active_guardrail",
    "active_guardrail_mutation",
    "active_monitoring",
    "active_monitoring_mutation",
    "active_prompt",
    "active_prompt_mutation",
    "active_release_state",
    "active_release_state_mutation",
    "active_source",
    "active_source_mutation",
    "active_source_registry",
    "active_source_registry_mutation",
    "active_surface_registry",
    "active_surface_registry_mutation",
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
    re.compile(r"\b(?:ran|executed|completed)\s+(?:a\s+)?(?:live crawl|live browser|live network|live devhub|live automation)\b", re.IGNORECASE),
    re.compile(r"\b(?:confirmed|observed|verified)\s+(?:in|from)\s+(?:the\s+)?(?:live devhub|authenticated devhub|private account)\b", re.IGNORECASE),
    re.compile(r"\b(?:permit|approval|issuance|inspection|application|upload|payment)\s+(?:will|is guaranteed to|is certain to)\s+(?:be\s+)?(?:approved|issued|pass|accepted|processed|completed)\b", re.IGNORECASE),
    re.compile(r"\bguarantee(?:d|s)?\s+(?:approval|issuance|acceptance|permit outcome|inspection passage|legal outcome|permitting outcome)\b", re.IGNORECASE),
    re.compile(r"\b(?:legal|permitting)\s+outcome\s+(?:is|will be|is guaranteed|is certain)\b", re.IGNORECASE),
    re.compile(r"\b(?:finally|final|officially)\s+(?:submit|submitted|submission|pay|paid|payment|upload|uploaded|schedule|scheduled|cancel|cancelled|canceled)\b", re.IGNORECASE),
    re.compile(r"\b(?:submitted|uploaded|paid|scheduled|cancelled|canceled)\s+(?:the\s+)?(?:application|permit|payment|inspection|record|upload)\b", re.IGNORECASE),
    re.compile(r"\b(?:click|press|select|perform|complete)\s+(?:the\s+)?(?:submit|certify|upload|pay|payment|schedule|cancel|withdraw)\b", re.IGNORECASE),
    re.compile(r"\b(?:make|enter|submit)\s+(?:the\s+)?payment\b", re.IGNORECASE),
    re.compile(r"\b(?:upload corrections|schedule inspection|certify acknowledgement|submit application|purchase permit|cancel permit|withdraw application)\b", re.IGNORECASE),
    re.compile(r"\b(?:raw crawl|raw pdf|raw html|browser artifact|session artifact|session state|storage state|trace file|har file|downloaded document|crawl artifact|pdf artifact)\b", re.IGNORECASE),
    re.compile(r"\b(?:private|authenticated)\s+(?:fact|facts|value|values|devhub value|case fact)\b", re.IGNORECASE),
)


@dataclass(frozen=True)
class HumanReviewDispositionSummaryV2ValidationResult:
    ok: bool
    errors: tuple[str, ...]


def load_json(path: str | Path) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"expected JSON object at {path}")
    return data


def build_human_review_disposition_summary_v2_from_fixture(path: str | Path) -> dict[str, Any]:
    fixture = load_json(path)
    handoff_fixture = _text(fixture.get("human_review_handoff_fixture"))
    if not handoff_fixture:
        raise ValueError("fixture must provide human_review_handoff_fixture")
    fixture_path = Path(path).parent / handoff_fixture
    handoff_packet = build_human_review_handoff_packet_v2_from_fixture(fixture_path)
    return build_human_review_disposition_summary_v2(handoff_packet)


def build_human_review_disposition_summary_v2(handoff_packet_v2: Mapping[str, Any]) -> dict[str, Any]:
    handoff_result = validate_human_review_handoff_packet_v2(handoff_packet_v2)
    if not handoff_result.ok:
        raise ValueError("invalid human review handoff packet v2: " + "; ".join(handoff_result.errors))

    decisions = _checklist_decisions(handoff_packet_v2)
    summary = {
        "packet_type": PACKET_TYPE,
        "packet_version": PACKET_VERSION,
        "mode": "fixture_first_offline_human_review_disposition_summary_v2",
        "consumes": {
            "human_review_handoff_packet_v2": _text(handoff_packet_v2.get("packet_type")),
        },
        "disposition_rationales": _disposition_rationales(decisions),
        "checklist_decisions": decisions,
        "reviewer_owner_fields": _reviewer_owner_fields(decisions),
        "dependency_ordering": _dependency_ordering(decisions),
        "implementation_follow_up_order": _implementation_follow_up_order(decisions),
        "rollback_notes": _rollback_notes(handoff_packet_v2, decisions),
        "validation_notes": _validation_notes(handoff_packet_v2, decisions),
        "offline_validation_commands": list(OFFLINE_VALIDATION_COMMANDS),
        "attestations": {key: True for key in sorted(REQUIRED_ATTESTATIONS)},
        "summary_status": "ready_for_ordered_implementation_follow_up",
    }
    require_human_review_disposition_summary_v2(summary)
    return summary


def validate_human_review_disposition_summary_v2(packet: Mapping[str, Any]) -> HumanReviewDispositionSummaryV2ValidationResult:
    errors: list[str] = []
    if packet.get("packet_type") != PACKET_TYPE:
        errors.append(f"packet_type must be {PACKET_TYPE}")
    if packet.get("packet_version") != PACKET_VERSION:
        errors.append("packet_version must be 2")
    if packet.get("mode") != "fixture_first_offline_human_review_disposition_summary_v2":
        errors.append("mode must be fixture_first_offline_human_review_disposition_summary_v2")

    consumes = _mapping(packet.get("consumes"))
    if consumes.get("human_review_handoff_packet_v2") != "ppd.human_review_handoff_packet.v2":
        errors.append("consumes.human_review_handoff_packet_v2 must reference human review handoff packet v2")

    decisions = _mapping_sequence(packet.get("checklist_decisions"))
    if not decisions:
        errors.append("checklist_decisions must be non-empty")
    seen_decisions = {_text(row.get("decision")) for row in decisions}
    missing_decisions = ALLOWED_DECISIONS - seen_decisions
    if missing_decisions:
        errors.append("checklist_decisions must include accepted, deferred, and rejected decisions")
    for index, row in enumerate(decisions):
        decision = _text(row.get("decision"))
        if not _text(row.get("decision_id")):
            errors.append(f"checklist_decisions[{index}].decision_id must be present")
        if decision not in ALLOWED_DECISIONS:
            errors.append(f"checklist_decisions[{index}].decision must be accepted, deferred, or rejected")
        if not _text(row.get("checklist_item_ref")):
            errors.append(f"checklist_decisions[{index}].checklist_item_ref must be present")
        if not _text(row.get("reviewer_owner")):
            errors.append(f"checklist_decisions[{index}].reviewer_owner must be present")
        if not _mapping_sequence(row.get("citations")):
            errors.append(f"checklist_decisions[{index}].citations must be non-empty")
        if not _text(row.get("rationale")):
            errors.append(f"checklist_decisions[{index}].rationale must be present")
        if not _text(row.get("implementation_follow_up")):
            errors.append(f"checklist_decisions[{index}].implementation_follow_up must be present")
        if not _string_list(row.get("dependency_after")):
            errors.append(f"checklist_decisions[{index}].dependency_after must be non-empty")
        if decision == "deferred" and not _text(row.get("next_task_ref")):
            errors.append(f"checklist_decisions[{index}].next_task_ref must be present for deferred dispositions")
        if not _text(row.get("rollback_note")):
            errors.append(f"checklist_decisions[{index}].rollback_note must be present")
        if not _text(row.get("validation_note")):
            errors.append(f"checklist_decisions[{index}].validation_note must be present")

    _validate_disposition_rationales(errors, packet.get("disposition_rationales"))
    _validate_owner_fields(errors, packet.get("reviewer_owner_fields"))
    _validate_dependency_ordering(errors, packet.get("dependency_ordering"), decisions)
    _validate_cited_note_rows(errors, packet.get("implementation_follow_up_order"), "implementation_follow_up_order", "follow_up_id")
    _validate_deferred_follow_up_rows(errors, packet.get("implementation_follow_up_order"))
    _validate_cited_note_rows(errors, packet.get("rollback_notes"), "rollback_notes", "rollback_note_id")
    _validate_cited_note_rows(errors, packet.get("validation_notes"), "validation_notes", "validation_note_id")

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
    if _text(packet.get("summary_status")) != "ready_for_ordered_implementation_follow_up":
        errors.append("summary_status must be ready_for_ordered_implementation_follow_up")

    _reject_unsafe_content(packet, "$", errors)
    return HumanReviewDispositionSummaryV2ValidationResult(not errors, tuple(errors))


def require_human_review_disposition_summary_v2(packet: Mapping[str, Any]) -> None:
    result = validate_human_review_disposition_summary_v2(packet)
    if not result.ok:
        raise ValueError("invalid human review disposition summary v2: " + "; ".join(result.errors))


def _checklist_decisions(handoff: Mapping[str, Any]) -> list[dict[str, Any]]:
    decisions: list[dict[str, Any]] = []
    for item in _mapping_sequence(handoff.get("reviewer_checklist_items")):
        item_id = _text(item.get("checklist_item_id"))
        if "proposal-guardrail" in item_id:
            decision = "deferred"
            follow_up = "Keep guardrail proposal staged until a reviewer resolves dependent blocked-action rows."
            dependency_after = ["accepted-source-and-surface-decisions"]
            next_task_ref = "next-task-review-proposed-guardrail-disposition"
        else:
            decision = "accepted"
            follow_up = "Carry this cited review item into implementation planning as proposed-only follow-up."
            dependency_after = ["validate-human-review-handoff-packet-v2"]
            next_task_ref = ""
        decisions.append(_decision_from_row(item_id, item, decision, follow_up, dependency_after, "ppd-human-reviewer", next_task_ref))

    for deferral in _mapping_sequence(handoff.get("unresolved_deferrals")):
        deferral_id = _text(deferral.get("deferral_id"))
        if "blocked-action" in deferral_id:
            decision = "rejected"
            follow_up = "Do not implement this consequential action path; retain an attended review boundary."
            dependency_after = ["accepted-read-only-and-draft-decisions"]
            next_task_ref = ""
        else:
            decision = "deferred"
            follow_up = "Leave this item blocked until a future reviewer records a cited resolution."
            dependency_after = ["accepted-source-and-surface-decisions"]
            next_task_ref = f"next-task-resolve-{_slug(deferral_id)}"
        decisions.append(_decision_from_row(deferral_id, deferral, decision, follow_up, dependency_after, "ppd-disposition-reviewer", next_task_ref))
    return decisions


def _decision_from_row(raw_id: str, row: Mapping[str, Any], decision: str, follow_up: str, dependency_after: list[str], owner: str, next_task_ref: str) -> dict[str, Any]:
    disposition = {
        "decision_id": f"{decision}-{_slug(raw_id)}",
        "checklist_item_ref": raw_id,
        "decision": decision,
        "reviewer_owner": owner,
        "rationale": _rationale(decision),
        "implementation_follow_up": follow_up,
        "dependency_after": dependency_after,
        "rollback_note": "Rollback is discarding this disposition row; no registry, guardrail, prompt, release, or external system is changed.",
        "validation_note": "Validate with fixture-only packet tests and PP&D daemon self-test before follow-up.",
        "citations": _citation_list(row.get("citations")),
    }
    if next_task_ref:
        disposition["next_task_ref"] = next_task_ref
    return disposition


def _rationale(decision: str) -> str:
    if decision == "accepted":
        return "Accepted for implementation planning because the consumed handoff row is cited and proposed-only."
    if decision == "deferred":
        return "Deferred because the consumed handoff row still depends on a future cited reviewer disposition."
    return "Rejected for implementation follow-up because the consumed handoff row represents a consequential official-action boundary."


def _disposition_rationales(decisions: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    citations_by_decision: dict[str, list[dict[str, Any]]] = {decision: [] for decision in sorted(ALLOWED_DECISIONS)}
    for row in decisions:
        decision = _text(row.get("decision"))
        if decision in citations_by_decision:
            citations_by_decision[decision].extend(_citation_list(row.get("citations")))
    return [
        {
            "decision": decision,
            "rationale": _rationale(decision),
            "citations": citations_by_decision[decision] or [{"packet_field": "derived_from_human_review_handoff_packet_v2"}],
        }
        for decision in sorted(ALLOWED_DECISIONS)
    ]


def _reviewer_owner_fields(decisions: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for decision in decisions:
        owner = _text(decision.get("reviewer_owner"))
        decision_value = _text(decision.get("decision"))
        key = (owner, decision_value)
        if owner and key not in seen:
            seen.add(key)
            rows.append({
                "owner_field_id": f"owner-{_slug(owner)}-{decision_value}",
                "reviewer_owner": owner,
                "decision_scope": decision_value,
                "citations": _citation_list(decision.get("citations")),
            })
    return rows


def _dependency_ordering(decisions: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    order = [
        ("validate-human-review-handoff-packet-v2", []),
        ("accepted-source-and-surface-decisions", ["validate-human-review-handoff-packet-v2"]),
        ("accepted-read-only-and-draft-decisions", ["accepted-source-and-surface-decisions"]),
        ("deferred-review-resolution", ["accepted-read-only-and-draft-decisions"]),
        ("rejected-official-action-boundary", ["deferred-review-resolution"]),
        ("rollback-and-validation-readiness", ["rejected-official-action-boundary"]),
    ]
    citations = _derived_citations(decisions)
    return [
        {
            "dependency_id": dependency_id,
            "after": after,
            "citations": citations,
        }
        for dependency_id, after in order
    ]


def _implementation_follow_up_order(decisions: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, decision in enumerate(decisions, start=1):
        row = {
            "follow_up_id": f"follow-up-{index:02d}-{_slug(_text(decision.get('decision_id')))}",
            "decision_ref": _text(decision.get("decision_id")),
            "decision": _text(decision.get("decision")),
            "summary": _text(decision.get("implementation_follow_up")),
            "dependency_after": _string_list(decision.get("dependency_after")),
            "citations": _citation_list(decision.get("citations")),
        }
        next_task_ref = _text(decision.get("next_task_ref"))
        if next_task_ref:
            row["next_task_ref"] = next_task_ref
        rows.append(row)
    return rows


def _rollback_notes(handoff: Mapping[str, Any], decisions: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    handoff_rows = _mapping_sequence(handoff.get("rollback_verification"))
    return [
        {
            "rollback_note_id": "discard-disposition-summary-v2",
            "summary": "Rollback is deleting the fixture-first disposition summary; the consumed handoff packet and active PP&D state remain unchanged.",
            "citations": _derived_citations(decisions),
        },
        {
            "rollback_note_id": "preserve-handoff-rollback-verification",
            "summary": "Follow-up must preserve the consumed handoff packet rollback verification before any implementation proposal is staged.",
            "citations": _derived_citations(handoff_rows),
        },
    ]


def _validation_notes(handoff: Mapping[str, Any], decisions: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    commands = _sequence(handoff.get("offline_validation_commands"))
    return [
        {
            "validation_note_id": "replay-handoff-validation-first",
            "summary": "Run the consumed handoff packet validation before accepting disposition summary follow-up.",
            "citations": [{"packet_field": "human_review_handoff_packet_v2.offline_validation_commands", "command_count": len(commands)}],
        },
        {
            "validation_note_id": "validate-disposition-decisions",
            "summary": "Disposition decisions must stay cited and include accepted, deferred, and rejected outcomes before implementation follow-up.",
            "citations": _derived_citations(decisions),
        },
    ]


def _validate_disposition_rationales(errors: list[str], value: Any) -> None:
    rows = _mapping_sequence(value)
    if not rows:
        errors.append("disposition_rationales must be non-empty")
        return
    by_decision = {_text(row.get("decision")): row for row in rows}
    for decision in sorted(ALLOWED_DECISIONS):
        row = by_decision.get(decision)
        if row is None:
            errors.append(f"disposition_rationales must include {decision} rationale")
            continue
        if not _text(row.get("rationale")):
            errors.append(f"disposition_rationales[{decision}].rationale must be present")
        if not _mapping_sequence(row.get("citations")):
            errors.append(f"disposition_rationales[{decision}].citations must be non-empty")


def _validate_owner_fields(errors: list[str], value: Any) -> None:
    rows = _mapping_sequence(value)
    if not rows:
        errors.append("reviewer_owner_fields must be non-empty")
        return
    for index, row in enumerate(rows):
        if not _text(row.get("owner_field_id")):
            errors.append(f"reviewer_owner_fields[{index}].owner_field_id must be present")
        if not _text(row.get("reviewer_owner")):
            errors.append(f"reviewer_owner_fields[{index}].reviewer_owner must be present")
        if not _text(row.get("decision_scope")):
            errors.append(f"reviewer_owner_fields[{index}].decision_scope must be present")
        if not _mapping_sequence(row.get("citations")):
            errors.append(f"reviewer_owner_fields[{index}].citations must be non-empty")


def _validate_dependency_ordering(errors: list[str], value: Any, decisions: Sequence[Mapping[str, Any]]) -> None:
    rows = _mapping_sequence(value)
    if not rows:
        errors.append("dependency_ordering must be non-empty")
        return
    dependency_ids = {_text(row.get("dependency_id")) for row in rows}
    for index, row in enumerate(rows):
        if not _text(row.get("dependency_id")):
            errors.append(f"dependency_ordering[{index}].dependency_id must be present")
        if not _mapping_sequence(row.get("citations")):
            errors.append(f"dependency_ordering[{index}].citations must be non-empty")
    for decision_index, decision in enumerate(decisions):
        missing = [dependency for dependency in _string_list(decision.get("dependency_after")) if dependency not in dependency_ids]
        if missing:
            errors.append(f"checklist_decisions[{decision_index}].dependency_after references unknown dependency")


def _validate_cited_note_rows(errors: list[str], value: Any, field: str, id_key: str) -> None:
    rows = _mapping_sequence(value)
    if not rows:
        errors.append(f"{field} must be non-empty")
        return
    for index, row in enumerate(rows):
        if not _text(row.get(id_key)):
            errors.append(f"{field}[{index}].{id_key} must be present")
        if not _text(row.get("summary")):
            errors.append(f"{field}[{index}].summary must be present")
        if not _mapping_sequence(row.get("citations")):
            errors.append(f"{field}[{index}].citations must be non-empty")


def _validate_deferred_follow_up_rows(errors: list[str], value: Any) -> None:
    for index, row in enumerate(_mapping_sequence(value)):
        if _text(row.get("decision")) == "deferred" and not _text(row.get("next_task_ref")):
            errors.append(f"implementation_follow_up_order[{index}].next_task_ref must be present for deferred dispositions")


def _citation_list(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        rows = [dict(item) for item in value if isinstance(item, Mapping) and item]
        if rows:
            return rows
    return [{"packet_field": "derived_from_human_review_handoff_packet_v2"}]


def _derived_citations(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    citations: list[dict[str, Any]] = []
    for row in rows:
        citations.extend(_citation_list(row.get("citations")))
    if citations:
        return citations
    return [{"packet_field": "derived_from_human_review_handoff_packet_v2"}]


def _reject_unsafe_content(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            normalized = key_text.lower().replace("-", "_")
            child_path = f"{path}.{key_text}"
            if normalized in _FORBIDDEN_KEYS and child not in (None, "", [], {}):
                errors.append(f"{child_path} is not allowed in a human review disposition summary v2")
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
