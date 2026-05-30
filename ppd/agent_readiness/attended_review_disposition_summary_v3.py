"""Fixture-first attended review disposition summary v3.

This module consumes committed attended review readiness checklist v3
fixtures only. It does not open DevHub, authenticate, crawl live sources,
mutate release state, or perform official actions.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from ppd.devhub.review_readiness_checklist_v3 import validate_checklist_v3

PACKET_TYPE = "ppd.attended_review_disposition_summary.v3"
PACKET_VERSION = 3

ALLOWED_DECISIONS = {"accepted", "deferred", "rejected"}
REQUIRED_ATTESTATIONS = ("no_live", "no_auth", "no_release", "no_official_action")
OFFLINE_VALIDATION_COMMANDS = [
    ["python3", "-m", "py_compile", "ppd/agent_readiness/attended_review_disposition_summary_v3.py"],
    ["python3", "-m", "unittest", "ppd.tests.test_attended_review_disposition_summary_v3"],
    ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
]


@dataclass(frozen=True)
class DispositionSummaryV3ValidationResult:
    ok: bool
    errors: tuple[str, ...]


def load_json(path: str | Path) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"expected JSON object at {path}")
    return data


def build_attended_review_disposition_summary_v3_from_manifest(path: str | Path) -> dict[str, Any]:
    manifest_path = Path(path)
    manifest = load_json(manifest_path)
    valid_path = manifest_path.parent / _text(manifest.get("readiness_checklist_fixture"))
    rejection_path = manifest_path.parent / _text(manifest.get("rejection_checklist_fixture"))
    return build_attended_review_disposition_summary_v3(
        readiness_checklist=load_json(valid_path),
        rejection_checklist=load_json(rejection_path),
        source_manifest_id=_text(manifest.get("manifest_id")),
        readiness_fixture_ref=_text(manifest.get("readiness_checklist_fixture")),
        rejection_fixture_ref=_text(manifest.get("rejection_checklist_fixture")),
    )


def build_attended_review_disposition_summary_v3(
    readiness_checklist: Mapping[str, Any],
    rejection_checklist: Mapping[str, Any],
    source_manifest_id: str = "inline-fixtures",
    readiness_fixture_ref: str = "readiness_checklist",
    rejection_fixture_ref: str = "rejection_checklist",
) -> dict[str, Any]:
    readiness_result = validate_checklist_v3(readiness_checklist)
    if not readiness_result.ok:
        raise ValueError("readiness checklist fixture must validate before disposition summary v3 is built")

    rejection_result = validate_checklist_v3(rejection_checklist)
    if rejection_result.ok:
        raise ValueError("rejection checklist fixture must be rejected before disposition summary v3 is built")

    decisions = _readiness_decisions(readiness_checklist, readiness_fixture_ref)
    decisions.extend(_rejection_decisions(rejection_result.errors, rejection_fixture_ref))

    summary = {
        "packet_type": PACKET_TYPE,
        "packet_version": PACKET_VERSION,
        "mode": "fixture_first_attended_review_disposition_summary_v3",
        "source_manifest_id": source_manifest_id,
        "consumes": {
            "attended_review_readiness_checklist_v3": readiness_fixture_ref,
            "attended_review_readiness_rejection_fixture_v3": rejection_fixture_ref,
        },
        "checklist_decisions": decisions,
        "reviewer_owner_fields": _reviewer_owner_fields(decisions),
        "unresolved_deferral_follow_ups": _unresolved_deferral_follow_ups(decisions),
        "rollback_verification_notes": _rollback_verification_notes(decisions),
        "offline_validation_commands": list(OFFLINE_VALIDATION_COMMANDS),
        "attestations": {key: True for key in REQUIRED_ATTESTATIONS},
        "summary_status": "ready_for_attended_review_follow_up",
    }
    require_attended_review_disposition_summary_v3(summary)
    return summary


def validate_attended_review_disposition_summary_v3(packet: Mapping[str, Any]) -> DispositionSummaryV3ValidationResult:
    errors: list[str] = []
    if packet.get("packet_type") != PACKET_TYPE:
        errors.append(f"packet_type must be {PACKET_TYPE}")
    if packet.get("packet_version") != PACKET_VERSION:
        errors.append("packet_version must be 3")
    if packet.get("mode") != "fixture_first_attended_review_disposition_summary_v3":
        errors.append("mode must be fixture_first_attended_review_disposition_summary_v3")

    consumes = _mapping(packet.get("consumes"))
    if not _text(consumes.get("attended_review_readiness_checklist_v3")):
        errors.append("consumes.attended_review_readiness_checklist_v3 must be present")
    if not _text(consumes.get("attended_review_readiness_rejection_fixture_v3")):
        errors.append("consumes.attended_review_readiness_rejection_fixture_v3 must be present")

    decisions = _mapping_sequence(packet.get("checklist_decisions"))
    if not decisions:
        errors.append("checklist_decisions must be non-empty")
    seen_decisions = {_text(row.get("decision")) for row in decisions}
    for decision in sorted(ALLOWED_DECISIONS):
        if decision not in seen_decisions:
            errors.append(f"checklist_decisions must include {decision}")

    for index, decision in enumerate(decisions):
        prefix = f"checklist_decisions[{index}]"
        decision_value = _text(decision.get("decision"))
        if decision_value not in ALLOWED_DECISIONS:
            errors.append(f"{prefix}.decision must be accepted, deferred, or rejected")
        for key in ("decision_id", "checklist_item_ref", "reviewer_owner", "rationale", "rollback_verification_note"):
            if not _text(decision.get(key)):
                errors.append(f"{prefix}.{key} must be present")
        if not _mapping_sequence(decision.get("citations")):
            errors.append(f"{prefix}.citations must be non-empty")
        if decision_value == "deferred" and not _text(decision.get("follow_up_task_ref")):
            errors.append(f"{prefix}.follow_up_task_ref must be present for unresolved deferrals")
        if decision_value == "rejected" and not _text(decision.get("rejection_reason")):
            errors.append(f"{prefix}.rejection_reason must be present for rejected rows")

    _validate_owner_fields(errors, packet.get("reviewer_owner_fields"))
    _validate_follow_ups(errors, packet.get("unresolved_deferral_follow_ups"), decisions)
    _validate_rollback_notes(errors, packet.get("rollback_verification_notes"))

    commands = _sequence(packet.get("offline_validation_commands"))
    if not commands:
        errors.append("offline_validation_commands must be non-empty")
    for index, command in enumerate(commands):
        if not _string_list(command):
            errors.append(f"offline_validation_commands[{index}] must be a command list")

    attestations = _mapping(packet.get("attestations"))
    for key in REQUIRED_ATTESTATIONS:
        if attestations.get(key) is not True:
            errors.append(f"attestations.{key} must be true")
    if _text(packet.get("summary_status")) != "ready_for_attended_review_follow_up":
        errors.append("summary_status must be ready_for_attended_review_follow_up")

    return DispositionSummaryV3ValidationResult(ok=not errors, errors=tuple(errors))


def require_attended_review_disposition_summary_v3(packet: Mapping[str, Any]) -> None:
    result = validate_attended_review_disposition_summary_v3(packet)
    if not result.ok:
        raise ValueError("invalid attended review disposition summary v3: " + "; ".join(result.errors))


def _readiness_decisions(checklist: Mapping[str, Any], fixture_ref: str) -> list[dict[str, Any]]:
    decisions: list[dict[str, Any]] = []
    for row in _mapping_sequence(checklist.get("rows")):
        row_id = _text(row.get("id") or row.get("checklist_id"))
        disposition = _text(row.get("unresolved_deferral_disposition"))
        decision = "deferred" if disposition not in ("none", "not_applicable") else "accepted"
        decision_row = {
            "decision_id": f"{decision}-{_slug(row_id)}",
            "checklist_item_ref": row_id,
            "decision": decision,
            "reviewer_owner": _text(row.get("reviewer_owner")),
            "rationale": _rationale(decision),
            "citations": _citations(row, fixture_ref),
            "rollback_verification_note": "Fixture-only disposition can be rolled back by discarding this generated summary; no portal, source registry, guardrail, prompt, or release state is changed.",
        }
        if decision == "deferred":
            decision_row["follow_up_task_ref"] = f"task-resolve-{_slug(row_id)}-attended-review-deferral"
        decisions.append(decision_row)
    return decisions


def _rejection_decisions(errors: Sequence[Any], fixture_ref: str) -> list[dict[str, Any]]:
    decisions: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for error in errors:
        code = _text(getattr(error, "code", ""))
        path = _text(getattr(error, "path", ""))
        if not code or not path:
            continue
        key = (path, code)
        if key in seen:
            continue
        seen.add(key)
        ref = f"{path}:{code}"
        decisions.append(
            {
                "decision_id": f"rejected-{_slug(path)}-{_slug(code)}",
                "checklist_item_ref": ref,
                "decision": "rejected",
                "reviewer_owner": "ppd-attended-review-rejection-owner",
                "rationale": _rationale("rejected"),
                "rejection_reason": code,
                "citations": [{"fixture": fixture_ref, "rejection_path": path, "rejection_code": code}],
                "rollback_verification_note": "Rejected fixture content is used only as a deterministic negative control; rollback is deleting this summary with no external state change.",
            }
        )
    return decisions


def _reviewer_owner_fields(decisions: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for decision in decisions:
        owner = _text(decision.get("reviewer_owner"))
        scope = _text(decision.get("decision"))
        key = (owner, scope)
        if owner and key not in seen:
            seen.add(key)
            rows.append(
                {
                    "owner_field_id": f"owner-{_slug(owner)}-{scope}",
                    "reviewer_owner": owner,
                    "decision_scope": scope,
                    "citations": _mapping_sequence(decision.get("citations")),
                }
            )
    return rows


def _unresolved_deferral_follow_ups(decisions: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for decision in decisions:
        if _text(decision.get("decision")) != "deferred":
            continue
        rows.append(
            {
                "follow_up_task_ref": _text(decision.get("follow_up_task_ref")),
                "decision_ref": _text(decision.get("decision_id")),
                "reviewer_owner": _text(decision.get("reviewer_owner")),
                "summary": "Resolve the attended review deferral with cited reviewer disposition before implementation follow-up.",
                "citations": _mapping_sequence(decision.get("citations")),
            }
        )
    return rows


def _rollback_verification_notes(decisions: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "rollback_note_id": "discard-disposition-summary-v3",
            "summary": "Rollback is deleting the generated fixture-first disposition summary v3; consumed fixtures and active PP&D state remain unchanged.",
            "citations": _all_citations(decisions),
        },
        {
            "rollback_note_id": "preserve-official-action-boundary",
            "summary": "Disposition follow-up remains review-only and cannot represent upload, payment, scheduling, cancellation, certification, submission, release, live crawl, or authenticated automation as complete.",
            "citations": _all_citations(decisions),
        },
    ]


def _validate_owner_fields(errors: list[str], value: Any) -> None:
    rows = _mapping_sequence(value)
    if not rows:
        errors.append("reviewer_owner_fields must be non-empty")
        return
    for index, row in enumerate(rows):
        for key in ("owner_field_id", "reviewer_owner", "decision_scope"):
            if not _text(row.get(key)):
                errors.append(f"reviewer_owner_fields[{index}].{key} must be present")
        if not _mapping_sequence(row.get("citations")):
            errors.append(f"reviewer_owner_fields[{index}].citations must be non-empty")


def _validate_follow_ups(errors: list[str], value: Any, decisions: Sequence[Mapping[str, Any]]) -> None:
    rows = _mapping_sequence(value)
    deferred_count = sum(1 for decision in decisions if _text(decision.get("decision")) == "deferred")
    if deferred_count and len(rows) != deferred_count:
        errors.append("unresolved_deferral_follow_ups must include one row per deferred decision")
    for index, row in enumerate(rows):
        for key in ("follow_up_task_ref", "decision_ref", "reviewer_owner", "summary"):
            if not _text(row.get(key)):
                errors.append(f"unresolved_deferral_follow_ups[{index}].{key} must be present")
        if not _mapping_sequence(row.get("citations")):
            errors.append(f"unresolved_deferral_follow_ups[{index}].citations must be non-empty")


def _validate_rollback_notes(errors: list[str], value: Any) -> None:
    rows = _mapping_sequence(value)
    if not rows:
        errors.append("rollback_verification_notes must be non-empty")
        return
    for index, row in enumerate(rows):
        for key in ("rollback_note_id", "summary"):
            if not _text(row.get(key)):
                errors.append(f"rollback_verification_notes[{index}].{key} must be present")
        if not _mapping_sequence(row.get("citations")):
            errors.append(f"rollback_verification_notes[{index}].citations must be non-empty")


def _rationale(decision: str) -> str:
    if decision == "accepted":
        return "Accepted because the cited checklist row validates and has no unresolved deferral disposition."
    if decision == "deferred":
        return "Deferred because the cited checklist row validates but still requires reviewer-owned follow-up."
    return "Rejected because the rejection fixture produced a deterministic checklist validation failure."


def _citations(row: Mapping[str, Any], fixture_ref: str) -> list[dict[str, Any]]:
    values: list[str] = []
    for key in ("citation_ids", "source_evidence_ids", "source_citations", "evidence_ids"):
        value = row.get(key)
        if isinstance(value, str) and value:
            values.append(value)
        elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
            values.extend(str(item) for item in value if str(item))
    return [{"fixture": fixture_ref, "citation_id": value} for value in values]


def _all_citations(decisions: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    citations: list[dict[str, Any]] = []
    for decision in decisions:
        citations.extend(_mapping_sequence(decision.get("citations")))
    return citations or [{"fixture": "attended_review_disposition_summary_v3"}]


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _mapping_sequence(value: Any) -> list[Mapping[str, Any]]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return [item for item in value if isinstance(item, Mapping)]
    return []


def _sequence(value: Any) -> Sequence[Any]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return value
    return []


def _string_list(value: Any) -> list[str]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return [item for item in value if isinstance(item, str) and item]
    return []


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _slug(value: str) -> str:
    cleaned = []
    for char in value.lower():
        if char.isalnum():
            cleaned.append(char)
        else:
            cleaned.append("-")
    slug = "".join(cleaned).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug or "item"


__all__ = [
    "DispositionSummaryV3ValidationResult",
    "build_attended_review_disposition_summary_v3",
    "build_attended_review_disposition_summary_v3_from_manifest",
    "load_json",
    "require_attended_review_disposition_summary_v3",
    "validate_attended_review_disposition_summary_v3",
]
