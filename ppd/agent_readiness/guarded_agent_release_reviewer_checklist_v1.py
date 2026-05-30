"""Fixture-first guarded agent release reviewer checklist v1.

The checklist consumes already-built offline packets and emits reviewer-facing
rows only. It does not promote fixtures, change prompts, mutate active
boundaries, crawl live sources, access DevHub, or create private artifacts.
"""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


PACKET_TYPE = "ppd.guarded_agent_release_reviewer_checklist.v1"
VALIDATION_COMMAND = ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]
REQUIRED_INPUTS = (
    "guarded_agent_release_readiness_packet_v1",
    "release_promotion_decision_packet_v1",
    "public_source_refresh_plan_v2",
    "devhub_observed_surface_update_plan_v2",
)
MUTATION_FLAGS = (
    "active_fixture_promotion",
    "active_prompt_mutation",
    "active_guardrail_mutation",
    "active_release_state_mutation",
    "active_source_mutation",
    "active_devhub_surface_mutation",
)
FORBIDDEN_TEXT = (
    "auth_state",
    "storage_state",
    "cookie",
    "credential",
    "password",
    "trace.zip",
    ".har",
    "raw crawl",
    "raw html",
    "raw pdf",
    "downloaded pdf",
    "downloaded document",
    "live crawl completed",
    "live devhub access",
    "promoted to production",
    "permit will be approved",
)


class GuardedAgentReleaseReviewerChecklistV1Error(ValueError):
    """Raised when checklist inputs or output are unsafe."""

    def __init__(self, errors: Iterable[str]) -> None:
        self.errors = tuple(errors)
        super().__init__("invalid guarded agent release reviewer checklist v1: " + "; ".join(self.errors))


def load_guarded_agent_release_reviewer_checklist_fixture(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise GuardedAgentReleaseReviewerChecklistV1Error(["fixture bundle must be a JSON object"])
    missing = [key for key in REQUIRED_INPUTS if key not in payload]
    if missing:
        raise GuardedAgentReleaseReviewerChecklistV1Error([f"missing fixture input: {key}" for key in missing])
    return build_guarded_agent_release_reviewer_checklist_v1(
        guarded_agent_release_readiness_packet_v1=_mapping(payload, "guarded_agent_release_readiness_packet_v1"),
        release_promotion_decision_packet_v1=_mapping(payload, "release_promotion_decision_packet_v1"),
        public_source_refresh_plan_v2=_mapping(payload, "public_source_refresh_plan_v2"),
        devhub_observed_surface_update_plan_v2=_mapping(payload, "devhub_observed_surface_update_plan_v2"),
    )


def build_guarded_agent_release_reviewer_checklist_v1(
    *,
    guarded_agent_release_readiness_packet_v1: Mapping[str, Any],
    release_promotion_decision_packet_v1: Mapping[str, Any],
    public_source_refresh_plan_v2: Mapping[str, Any],
    devhub_observed_surface_update_plan_v2: Mapping[str, Any],
) -> dict[str, Any]:
    readiness = deepcopy(dict(guarded_agent_release_readiness_packet_v1))
    release = deepcopy(dict(release_promotion_decision_packet_v1))
    refresh = deepcopy(dict(public_source_refresh_plan_v2))
    devhub = deepcopy(dict(devhub_observed_surface_update_plan_v2))

    checklist = {
        "packet_type": PACKET_TYPE,
        "packet_version": "v1",
        "fixture_first": True,
        "metadata_only": True,
        "review_mode": "manual_signoff_only",
        "consumed_input_packet_refs": {
            "guarded_agent_release_readiness_packet_v1": _text(readiness.get("packet_type")),
            "release_promotion_decision_packet_v1": _text(release.get("packet_id") or release.get("packet_version")),
            "public_source_refresh_plan_v2": _text(refresh.get("packet_id") or refresh.get("plan_version") or refresh.get("schema_version")),
            "devhub_observed_surface_update_plan_v2": _text(devhub.get("packet_id") or devhub.get("plan_version")),
        },
        "attestations": {
            "no_fixture_promotion": True,
            "no_prompt_changes": True,
            "no_active_guardrail_changes": True,
            "no_live_source_crawl": True,
            "no_devhub_access": True,
            "no_private_artifacts": True,
        },
        "reviewer_checklist_rows": _reviewer_rows(readiness, release, refresh, devhub),
        "manual_signoff_placeholders": _manual_signoffs(release, refresh, devhub),
        "unresolved_blocker_references": _blockers(readiness, release),
        "validation_replay_commands": [VALIDATION_COMMAND],
        "rollback_checkpoints": _rollback_checkpoints(readiness, release, refresh, devhub),
        "human_handoff_notes": _handoff_notes(readiness, release, refresh, devhub),
        "active_fixture_promotion": False,
        "active_prompt_mutation": False,
        "active_guardrail_mutation": False,
        "active_release_state_mutation": False,
        "active_source_mutation": False,
        "active_devhub_surface_mutation": False,
    }
    errors = validate_guarded_agent_release_reviewer_checklist_v1(checklist)
    if errors:
        raise GuardedAgentReleaseReviewerChecklistV1Error(errors)
    return checklist


def validate_guarded_agent_release_reviewer_checklist_v1(packet: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if packet.get("packet_type") != PACKET_TYPE:
        errors.append("packet_type must be ppd.guarded_agent_release_reviewer_checklist.v1")
    if packet.get("fixture_first") is not True:
        errors.append("fixture_first must be true")
    if packet.get("metadata_only") is not True:
        errors.append("metadata_only must be true")
    for flag in MUTATION_FLAGS:
        if packet.get(flag) is not False:
            errors.append(f"{flag} must be false")
    _validate_rows(packet, "reviewer_checklist_rows", errors)
    _validate_rows(packet, "manual_signoff_placeholders", errors)
    _validate_rows(packet, "unresolved_blocker_references", errors)
    _validate_rows(packet, "rollback_checkpoints", errors)
    _validate_rows(packet, "human_handoff_notes", errors)
    if packet.get("validation_replay_commands") != [VALIDATION_COMMAND]:
        errors.append("validation_replay_commands must contain only the PP&D daemon self-test command")
    for path, value in _walk(packet):
        if isinstance(value, str):
            lowered = value.lower()
            for token in FORBIDDEN_TEXT:
                if token in lowered:
                    errors.append(f"forbidden unsafe text at {path}: {token}")
    return errors


def _reviewer_rows(readiness: Mapping[str, Any], release: Mapping[str, Any], refresh: Mapping[str, Any], devhub: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, row in enumerate(_sequence(readiness.get("agent_facing_readiness_rows")), start=1):
        if isinstance(row, Mapping):
            rows.append(_check_row(f"readiness-{index}", "Guarded agent readiness", "Confirm the agent-facing row is cited and still fixture-only.", row))
    for index, row in enumerate(_sequence(release.get("decision_rows")), start=1):
        if isinstance(row, Mapping):
            rows.append(_check_row(f"release-decision-{index}", "Release promotion decision", "Confirm the decision remains deferred or reviewer-owned until manual signoff.", row))
    for index, row in enumerate(_sequence(refresh.get("source_refresh_candidates") or refresh.get("refresh_candidates") or refresh.get("traceability_rows")), start=1):
        if isinstance(row, Mapping):
            rows.append(_check_row(f"public-refresh-{index}", "Public source refresh plan", "Confirm source refresh work is cited, offline, and not a live crawl instruction.", row))
    for index, row in enumerate(_sequence(devhub.get("surface_update_candidates")), start=1):
        if isinstance(row, Mapping):
            rows.append(_check_row(f"devhub-surface-{index}", "DevHub observed surface plan", "Confirm observed surface rows are redacted, read-only, and manual-review gated.", row))
    return rows


def _check_row(row_id: str, source_packet: str, checklist_item: str, source_row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "row_id": row_id,
        "source_packet": source_packet,
        "checklist_item": checklist_item,
        "reviewer_disposition_placeholder": "pending_manual_review",
        "citations": _citations(source_row) or [f"{source_packet}:{row_id}"],
    }


def _manual_signoffs(release: Mapping[str, Any], refresh: Mapping[str, Any], devhub: Mapping[str, Any]) -> list[dict[str, Any]]:
    signoffs: list[dict[str, Any]] = []
    for index, row in enumerate(_sequence(release.get("manual_signoff_placeholders")), start=1):
        if isinstance(row, Mapping):
            signoffs.append({"signoff_id": f"release-signoff-{index}", "role": _text(row.get("role"), "release supervisor"), "placeholder": "pending name, timestamp, and disposition", "citations": _citations(row) or ["release:manual-signoff"]})
    signoffs.append({"signoff_id": "public-source-reviewer-signoff", "role": "public source reviewer", "placeholder": "pending name, timestamp, and disposition", "citations": _first_citations(refresh, "public-source:refresh-plan")})
    signoffs.append({"signoff_id": "devhub-surface-reviewer-signoff", "role": "DevHub surface reviewer", "placeholder": "pending name, timestamp, and disposition", "citations": _first_citations(devhub, "devhub:observed-surface-plan")})
    return signoffs


def _blockers(readiness: Mapping[str, Any], release: Mapping[str, Any]) -> list[dict[str, Any]]:
    blockers: list[dict[str, Any]] = []
    for index, row in enumerate(_sequence(readiness.get("release_blockers")), start=1):
        if isinstance(row, Mapping):
            blockers.append({"blocker_ref": _text(row.get("blocker_id"), f"readiness-blocker-{index}"), "source_packet": "guarded_agent_release_readiness_packet_v1", "status": "unresolved_pending_manual_signoff", "citations": _citations(row) or ["readiness:release-blocker"]})
    for index, row in enumerate(_sequence(release.get("release_blockers")), start=1):
        if isinstance(row, Mapping):
            blockers.append({"blocker_ref": _text(row.get("blocker_id") or row.get("id"), f"release-blocker-{index}"), "source_packet": "release_promotion_decision_packet_v1", "status": "unresolved_pending_manual_signoff", "citations": _citations(row) or ["release:blocker"]})
    if blockers:
        return blockers
    return [{"blocker_ref": "manual-release-review-required", "source_packet": "reviewer_checklist", "status": "unresolved_pending_manual_signoff", "citations": ["reviewer-checklist:manual-review-required"]}]


def _rollback_checkpoints(readiness: Mapping[str, Any], release: Mapping[str, Any], refresh: Mapping[str, Any], devhub: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for source_name, packet in (("guarded readiness", readiness), ("release decision", release)):
        for index, row in enumerate(_sequence(packet.get("rollback_checkpoints")), start=1):
            if isinstance(row, Mapping):
                rows.append({"checkpoint_id": _text(row.get("checkpoint_id"), f"{source_name}-{index}"), "checkpoint": "Discard this checklist output and keep active PP&D state unchanged.", "verification_command": VALIDATION_COMMAND, "citations": _citations(row) or [f"{source_name}:rollback"]})
    rows.append({"checkpoint_id": "public-source-refresh-plan-rollback", "checkpoint": "Leave public source refresh candidates as fixture review material only.", "verification_command": VALIDATION_COMMAND, "citations": _first_citations(refresh, "public-source:rollback")})
    rows.append({"checkpoint_id": "devhub-observed-surface-plan-rollback", "checkpoint": "Leave DevHub observed surface candidates out of active surface registries.", "verification_command": VALIDATION_COMMAND, "citations": _first_citations(devhub, "devhub:rollback")})
    return rows


def _handoff_notes(readiness: Mapping[str, Any], release: Mapping[str, Any], refresh: Mapping[str, Any], devhub: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [
        {"note_id": "handoff-readiness", "handoff_to": "agent readiness reviewer", "note": "Review guarded agent expectations and unresolved blockers before any consumer release decision.", "citations": _first_citations(readiness, "readiness:handoff")},
        {"note_id": "handoff-release", "handoff_to": "release supervisor", "note": "Record manual signoff separately before any later release-state operation.", "citations": _first_citations(release, "release:handoff")},
        {"note_id": "handoff-public-source", "handoff_to": "public source reviewer", "note": "Use the refresh plan only as an offline checklist input; do not crawl from this artifact.", "citations": _first_citations(refresh, "public-source:handoff")},
        {"note_id": "handoff-devhub", "handoff_to": "DevHub surface reviewer", "note": "Use observed surface rows only for manual read-only review; keep attended work separate.", "citations": _first_citations(devhub, "devhub:handoff")},
    ]


def _validate_rows(packet: Mapping[str, Any], key: str, errors: list[str]) -> None:
    rows = packet.get(key)
    if not isinstance(rows, Sequence) or isinstance(rows, (str, bytes)) or not rows:
        errors.append(f"{key} must be a non-empty list")
        return
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            errors.append(f"{key}[{index}] must be an object")
            continue
        if not _string_list(row.get("citations")):
            errors.append(f"{key}[{index}].citations must be non-empty")


def _mapping(source: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = source.get(key)
    if not isinstance(value, Mapping):
        raise GuardedAgentReleaseReviewerChecklistV1Error([f"{key} must be an object"])
    return value


def _sequence(value: Any) -> Sequence[Any]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return value
    return ()


def _citations(row: Mapping[str, Any]) -> list[str]:
    value = row.get("citations") or row.get("source_evidence_ids") or row.get("evidence_citations")
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


def _first_citations(packet: Mapping[str, Any], fallback: str) -> list[str]:
    direct = _citations(packet)
    if direct:
        return direct
    for _path, value in _walk(packet):
        if isinstance(value, Mapping):
            citations = _citations(value)
            if citations:
                return citations
    return [fallback]


def _string_list(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes)) and bool(value) and all(isinstance(item, str) and bool(item.strip()) for item in value)


def _text(value: Any, fallback: str = "") -> str:
    return value.strip() if isinstance(value, str) and value.strip() else fallback


def _walk(value: Any, path: str = "$") -> Iterable[tuple[str, Any]]:
    if isinstance(value, Mapping):
        for key, child in value.items():
            yield from _walk(child, f"{path}.{key}")
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child in enumerate(value):
            yield from _walk(child, f"{path}[{index}]")
    else:
        yield path, value
