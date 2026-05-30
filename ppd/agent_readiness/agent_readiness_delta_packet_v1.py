"""Fixture-first agent readiness delta packet v1.

This module consumes fixture-shaped public source refresh patch plans,
DevHub read-only observation promotion plans, and guardrail regression replay
queues. It emits cited agent-facing deltas only; it does not change prompts,
agent state, source registries, surface maps, guardrails, DevHub state, or live
crawl state.
"""

from __future__ import annotations

import shlex
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence

PACKET_VERSION = "agent-readiness-delta-packet-v1"
CONSUMES = (
    "public_source_refresh_patch_plan_v1",
    "devhub_read_only_observation_promotion_plan_v1",
    "guardrail_regression_replay_queue_v1",
)

REQUIRED_ATTESTATIONS = {
    "fixture_first": True,
    "offline_only": True,
    "no_prompt_changes": True,
    "no_agent_state_changes": True,
    "no_live_crawl": True,
    "no_devhub_session": True,
    "no_private_artifact": True,
    "no_official_action": True,
    "no_active_mutation": True,
}

DEFAULT_VALIDATION_COMMANDS = (
    ("python3", "-m", "pytest", "ppd/tests/test_agent_readiness_delta_packet_v1.py"),
    ("python3", "ppd/daemon/ppd_daemon.py", "--self-test"),
)

MUTATION_KEYS = frozenset(
    {
        "active_agent_state_mutation",
        "active_guardrail_mutation",
        "active_prompt_mutation",
        "active_release_state_mutation",
        "active_source_mutation",
        "active_surface_map_mutation",
        "active_surface_registry_mutation",
        "agent_state_mutation",
        "apply_agent_state_changes",
        "apply_guardrail_changes",
        "apply_prompt_changes",
        "apply_release_state_changes",
        "apply_source_changes",
        "apply_surface_registry_changes",
        "change_agent_state",
        "change_guardrails",
        "change_prompts",
        "change_release_state",
        "change_sources",
        "change_surface_registry",
        "guardrail_mutation",
        "mutate_agent_state",
        "mutate_guardrails",
        "mutate_prompts",
        "mutate_release_state",
        "mutate_sources",
        "mutate_surface_registry",
        "prompt_changes",
        "prompt_mutation",
        "release_state_mutation",
        "source_mutation",
        "surface_registry_mutation",
        "update_agent_state",
        "update_guardrails",
        "update_prompts",
        "update_release_state",
        "update_sources",
        "update_surface_registry",
        "writes_agent_state",
        "writes_guardrails",
        "writes_prompts",
        "writes_release_state",
        "writes_sources",
        "writes_surface_registry",
    }
)

PRIVATE_OR_LIVE_KEYS = frozenset(
    {
        "account_data",
        "auth_artifact",
        "auth_state",
        "authenticated_artifact",
        "authenticated_capture",
        "authenticated_page_value",
        "browser_state",
        "cookie",
        "credentials",
        "devhub_session",
        "downloaded_document",
        "har",
        "live_crawl",
        "local_private_file_path",
        "password",
        "payment_detail",
        "private_artifact",
        "private_upload",
        "raw_authenticated_value",
        "raw_body",
        "raw_crawl_output",
        "screenshot",
        "session_state",
        "storage_state",
        "trace",
    }
)

FORBIDDEN_TEXT_RULES = (
    ("forbidden_prompt_mutation_text", ("change the agent prompt", "update the prompt", "mutate the prompt", "rewrite the prompt")),
    ("forbidden_agent_state_mutation_text", ("mutate agent state", "write agent state", "update agent state")),
    ("forbidden_release_state_mutation_text", ("mutate release state", "update release state", "promote the release", "mark released")),
    ("forbidden_source_mutation_text", ("mutate active source", "update active source", "write source registry", "change source registry")),
    ("forbidden_guardrail_mutation_text", ("mutate active guardrail", "update active guardrail", "write guardrail bundle", "change guardrail bundle")),
    ("forbidden_live_or_auth_text", ("start live crawl", "open devhub session", "use authenticated artifact", "private artifact")),
    ("forbidden_consequential_action_text", ("submit permit", "upload correction", "schedule inspection", "cancel inspection", "certify acknowledgement", "submit payment", "purchase permit", "make official change")),
    ("forbidden_outcome_guarantee_text", ("guarantee approval", "guaranteed approval", "permit will be approved", "permit will be issued", "application will be accepted", "inspection will pass", "legal determination", "permitting outcome guarantee")),
)

AGENT_FACING_DELTA_FIELDS = (
    "source_freshness_notes",
    "requirement_impact_links",
    "surface_map_observation_notes",
    "next_safe_action_expectations",
    "blocked_action_expectations",
)

REQUIRED_NON_EMPTY_SECTIONS = AGENT_FACING_DELTA_FIELDS + (
    "rollback_notes",
    "offline_validation_commands",
)


@dataclass(frozen=True)
class DeltaPacketIssue:
    code: str
    path: str
    message: str


class DeltaPacketError(ValueError):
    """Raised when a delta packet cannot be safely produced or accepted."""

    def __init__(self, issues: Iterable[DeltaPacketIssue]) -> None:
        self.issues = tuple(issues)
        detail = "; ".join(f"{issue.path}: {issue.code}" for issue in self.issues)
        super().__init__(detail)


def build_agent_readiness_delta_packet_v1(source_inputs: Mapping[str, Any]) -> dict[str, Any]:
    """Build cited agent-facing readiness deltas from fixture packet inputs."""

    public_plan = _required_mapping(source_inputs, "public_source_refresh_patch_plan_v1")
    devhub_plan = _required_mapping(source_inputs, "devhub_read_only_observation_promotion_plan_v1")
    replay_queue = _required_mapping(source_inputs, "guardrail_regression_replay_queue_v1")

    packet = {
        "packet_version": PACKET_VERSION,
        "fixture_first": True,
        "offline_only": True,
        "consumes": list(CONSUMES),
        "source_freshness_notes": _source_freshness_notes(public_plan),
        "requirement_impact_links": _requirement_impact_links(public_plan),
        "surface_map_observation_notes": _surface_observation_notes(devhub_plan),
        "next_safe_action_expectations": _next_safe_action_expectations(replay_queue),
        "blocked_action_expectations": _blocked_action_expectations(replay_queue),
        "rollback_notes": _rollback_notes(public_plan, devhub_plan, replay_queue),
        "offline_validation_commands": _offline_validation_commands(public_plan, devhub_plan, replay_queue),
        "attestations": dict(REQUIRED_ATTESTATIONS),
        "prompt_changes": [],
        "agent_state_changes": [],
    }
    require_valid_agent_readiness_delta_packet_v1(packet)
    return packet


def validate_agent_readiness_delta_packet_v1(packet: Mapping[str, Any]) -> list[DeltaPacketIssue]:
    """Return deterministic validation issues for an agent readiness delta packet."""

    issues: list[DeltaPacketIssue] = []
    if packet.get("packet_version") != PACKET_VERSION:
        issues.append(DeltaPacketIssue("invalid_version", "packet_version", f"packet_version must be {PACKET_VERSION}"))
    if packet.get("fixture_first") is not True:
        issues.append(DeltaPacketIssue("not_fixture_first", "fixture_first", "packet must be fixture-first"))
    if packet.get("offline_only") is not True:
        issues.append(DeltaPacketIssue("not_offline_only", "offline_only", "packet must be offline-only"))
    if packet.get("consumes") != list(CONSUMES):
        issues.append(DeltaPacketIssue("invalid_consumes", "consumes", "packet must name the three expected source packets"))

    attestations = packet.get("attestations")
    if not isinstance(attestations, Mapping):
        issues.append(DeltaPacketIssue("missing_attestations", "attestations", "attestations are required"))
    else:
        for key, expected in REQUIRED_ATTESTATIONS.items():
            if attestations.get(key) is not expected:
                issues.append(DeltaPacketIssue("missing_required_attestation", f"attestations.{key}", f"{key} must be {expected}"))

    for field in REQUIRED_NON_EMPTY_SECTIONS:
        values = packet.get(field)
        if not isinstance(values, list) or not values:
            issues.append(DeltaPacketIssue("missing_delta_section", field, f"{field} must be a non-empty list"))

    for field in AGENT_FACING_DELTA_FIELDS:
        for index, item in enumerate(_sequence(packet.get(field))):
            path = f"{field}[{index}]"
            if not isinstance(item, Mapping):
                issues.append(DeltaPacketIssue("delta_not_object", path, "delta entries must be objects"))
                continue
            if not _sequence(item.get("citations")):
                issues.append(DeltaPacketIssue("missing_citations", f"{path}.citations", "agent-facing deltas must be cited"))
            if not item.get("delta_id"):
                issues.append(DeltaPacketIssue("missing_delta_id", f"{path}.delta_id", "delta entries require delta_id"))

    _validate_affected_ids(packet, issues)
    _validate_expectations(packet, issues)

    if packet.get("prompt_changes") not in (None, []):
        issues.append(DeltaPacketIssue("prompt_changes_present", "prompt_changes", "packet must not carry prompt changes"))
    if packet.get("agent_state_changes") not in (None, []):
        issues.append(DeltaPacketIssue("agent_state_changes_present", "agent_state_changes", "packet must not carry agent state changes"))

    for command_index, command in enumerate(_sequence(packet.get("offline_validation_commands"))):
        if not _is_python_command(command):
            issues.append(DeltaPacketIssue("invalid_validation_command", f"offline_validation_commands[{command_index}]", "offline validation commands must be python command arrays"))

    _scan_for_forbidden_content(packet, "$", issues)
    return issues


def require_valid_agent_readiness_delta_packet_v1(packet: Mapping[str, Any]) -> None:
    issues = validate_agent_readiness_delta_packet_v1(packet)
    if issues:
        raise DeltaPacketError(issues)


def _validate_affected_ids(packet: Mapping[str, Any], issues: list[DeltaPacketIssue]) -> None:
    for index, item in enumerate(_mapping_items(packet.get("source_freshness_notes"))):
        if not _text(item.get("source_id")):
            issues.append(DeltaPacketIssue("missing_affected_source_id", f"source_freshness_notes[{index}].source_id", "source freshness deltas require an affected source_id"))
        if not _text_list(item.get("affected_source_ids")):
            issues.append(DeltaPacketIssue("missing_affected_source_id", f"source_freshness_notes[{index}].affected_source_ids", "source freshness deltas require affected_source_ids"))
    for index, item in enumerate(_mapping_items(packet.get("requirement_impact_links"))):
        if not _text(item.get("source_id")):
            issues.append(DeltaPacketIssue("missing_affected_source_id", f"requirement_impact_links[{index}].source_id", "requirement deltas require an affected source_id"))
        if not _text(item.get("requirement_id")):
            issues.append(DeltaPacketIssue("missing_affected_requirement_id", f"requirement_impact_links[{index}].requirement_id", "requirement deltas require an affected requirement_id"))
        if not _text_list(item.get("affected_requirement_ids")):
            issues.append(DeltaPacketIssue("missing_affected_requirement_id", f"requirement_impact_links[{index}].affected_requirement_ids", "requirement deltas require affected_requirement_ids"))
    for index, item in enumerate(_mapping_items(packet.get("surface_map_observation_notes"))):
        if not _text(item.get("surface_id")):
            issues.append(DeltaPacketIssue("missing_affected_surface_id", f"surface_map_observation_notes[{index}].surface_id", "surface deltas require an affected surface_id"))
        if not _text_list(item.get("affected_surface_ids")):
            issues.append(DeltaPacketIssue("missing_affected_surface_id", f"surface_map_observation_notes[{index}].affected_surface_ids", "surface deltas require affected_surface_ids"))


def _validate_expectations(packet: Mapping[str, Any], issues: list[DeltaPacketIssue]) -> None:
    for field in ("next_safe_action_expectations", "blocked_action_expectations"):
        for index, item in enumerate(_mapping_items(packet.get(field))):
            path = f"{field}[{index}]"
            if not _text(item.get("expectation")):
                issues.append(DeltaPacketIssue("missing_action_expectation", f"{path}.expectation", "action expectation deltas require expectation text"))
            fixture_refs = _mapping(item.get("fixture_refs"))
            if not any(_text(fixture_refs.get(key)) for key in ("requirement", "requirement_id")):
                issues.append(DeltaPacketIssue("missing_affected_requirement_id", f"{path}.fixture_refs", "action expectations require an affected requirement fixture ref"))
            if field == "blocked_action_expectations" and not _mapping(item.get("blocked_action_check")):
                issues.append(DeltaPacketIssue("missing_blocked_action_check", f"{path}.blocked_action_check", "blocked-action expectations require blocked_action_check"))


def _source_freshness_notes(plan: Mapping[str, Any]) -> list[dict[str, Any]]:
    notes: list[dict[str, Any]] = []
    for index, row in enumerate(_patch_rows(plan), start=1):
        metadata = _mapping(row.get("source_freshness_metadata"))
        review = _mapping(row.get("visible_page_review_notes"))
        source_id = _text(metadata.get("source_id") or _first(row.get("affected_source_ids")))
        notes.append(
            {
                "delta_id": f"source-freshness-delta-v1-{index:03d}",
                "source_id": source_id,
                "affected_source_ids": _text_list(row.get("affected_source_ids")) or ([source_id] if source_id else []),
                "freshness_status": _text(metadata.get("freshness_status")),
                "visible_title": _text(review.get("title")),
                "visible_date_note": _text(review.get("date_review_note") or review.get("visible_date_text")),
                "agent_note": "Treat this as a cited source freshness note until a later reviewed packet supersedes it.",
                "citations": _citations(row),
            }
        )
    return notes


def _requirement_impact_links(plan: Mapping[str, Any]) -> list[dict[str, Any]]:
    links: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for row in _patch_rows(plan):
        row_citations = _citations(row)
        source_id = _text(_mapping(row.get("source_freshness_metadata")).get("source_id") or _first(row.get("affected_source_ids")))
        impact_rows = _sequence(row.get("requirement_impact_links"))
        if not impact_rows:
            impact_rows = [{"source_id": source_id, "requirement_id": requirement_id, "impact": "source_refresh_review_required"} for requirement_id in _text_list(row.get("affected_requirement_ids"))]
        for impact in impact_rows:
            impact_map = _mapping(impact)
            requirement_id = _text(impact_map.get("requirement_id"))
            link_source_id = _text(impact_map.get("source_id") or source_id)
            key = (link_source_id, requirement_id)
            if not requirement_id or key in seen:
                continue
            seen.add(key)
            links.append(
                {
                    "delta_id": f"requirement-impact-delta-v1-{len(links) + 1:03d}",
                    "source_id": link_source_id,
                    "requirement_id": requirement_id,
                    "affected_requirement_ids": [requirement_id],
                    "impact": _text(impact_map.get("impact") or "source_refresh_review_required"),
                    "agent_note": "Link answers about this requirement to the cited refreshed-source review note.",
                    "citations": row_citations,
                }
            )
    return links


def _surface_observation_notes(plan: Mapping[str, Any]) -> list[dict[str, Any]]:
    notes: list[dict[str, Any]] = []
    for index, proposal in enumerate(_sequence(plan.get("surface_map_fixture_update_proposals")), start=1):
        proposal_map = _mapping(proposal)
        surface_id = _text(proposal_map.get("surface_id"))
        notes.append(
            {
                "delta_id": f"surface-map-observation-delta-v1-{index:03d}",
                "surface_id": surface_id,
                "affected_surface_ids": [surface_id] if surface_id else [],
                "page_heading": _text(proposal_map.get("page_heading")),
                "accessible_landmarks": _text_list(proposal_map.get("accessible_landmarks")),
                "validation_messages": _text_list(proposal_map.get("validation_messages")),
                "redaction_expectations": _text_list(proposal_map.get("redaction_expectations")),
                "stop_before_action_gates": _text_list(proposal_map.get("stop_before_action_gates")),
                "agent_note": "Use this only as a read-only surface observation note; stop before consequential DevHub controls.",
                "citations": _citations(proposal_map),
            }
        )
    return notes


def _next_safe_action_expectations(queue: Mapping[str, Any]) -> list[dict[str, Any]]:
    expectations: list[dict[str, Any]] = []
    for case in _sequence(queue.get("replay_cases")):
        case_map = _mapping(case)
        if case_map.get("expected_outcome") != "pass":
            continue
        expectations.append(
            {
                "delta_id": f"next-safe-action-delta-v1-{len(expectations) + 1:03d}",
                "replay_case_id": _text(case_map.get("id")),
                "expectation": "Agent may explain the cited read-only or reversible next step when stale/conflicting evidence checks are clear.",
                "fixture_refs": dict(_mapping(case_map.get("fixture_refs"))),
                "citations": _citations(case_map),
            }
        )
    return expectations


def _blocked_action_expectations(queue: Mapping[str, Any]) -> list[dict[str, Any]]:
    expectations: list[dict[str, Any]] = []
    for case in _sequence(queue.get("replay_cases")):
        case_map = _mapping(case)
        if case_map.get("expected_outcome") != "block":
            continue
        expectations.append(
            {
                "delta_id": f"blocked-action-delta-v1-{len(expectations) + 1:03d}",
                "replay_case_id": _text(case_map.get("id")),
                "expectation": "Agent must block or hand off when replay evidence is stale, conflicting, missing exact confirmation, or action classification is unsafe.",
                "blocked_action_check": dict(_mapping(case_map.get("blocked_action_check"))),
                "fixture_refs": dict(_mapping(case_map.get("fixture_refs"))),
                "citations": _citations(case_map),
            }
        )
    return expectations


def _rollback_notes(public_plan: Mapping[str, Any], devhub_plan: Mapping[str, Any], replay_queue: Mapping[str, Any]) -> list[dict[str, Any]]:
    notes: list[dict[str, Any]] = []
    for row in _patch_rows(public_plan):
        for checkpoint in _sequence(row.get("rollback_checkpoints") or [row.get("rollback_checkpoint")]):
            checkpoint_map = _mapping(checkpoint)
            if checkpoint_map:
                notes.append({"rollback_id": _text(checkpoint_map.get("checkpoint_id")), "note": "Restore the prior public source refresh fixture metadata.", "citations": _citations(row)})
    for proposal in _sequence(devhub_plan.get("surface_map_fixture_update_proposals")):
        proposal_map = _mapping(proposal)
        notes.append({"rollback_id": f"rollback:{_text(proposal_map.get('surface_id'))}", "note": _text(proposal_map.get("rollback_note")), "citations": _citations(proposal_map)})
    for index, note in enumerate(_text_list(replay_queue.get("rollback_notes")), start=1):
        notes.append({"rollback_id": f"guardrail-replay-rollback-v1-{index:03d}", "note": note, "citations": [{"packet": "guardrail_regression_replay_queue_v1", "section": "rollback_notes"}]})
    return notes


def _offline_validation_commands(*packets: Mapping[str, Any]) -> list[list[str]]:
    commands: list[list[str]] = []
    seen: set[tuple[str, ...]] = set()
    for packet in packets:
        for command in _sequence(packet.get("offline_validation_commands")):
            normalized = _normalize_command(command)
            if normalized and tuple(normalized) not in seen:
                seen.add(tuple(normalized))
                commands.append(normalized)
    for command_tuple in DEFAULT_VALIDATION_COMMANDS:
        command = list(command_tuple)
        if tuple(command) not in seen:
            seen.add(tuple(command))
            commands.append(command)
    return commands


def _patch_rows(plan: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    return [_mapping(row) for row in _sequence(plan.get("proposed_patch_rows") or plan.get("patch_rows"))]


def _citations(value: Mapping[str, Any]) -> list[Any]:
    citations = value.get("citations") or value.get("source_citations") or value.get("source_evidence") or []
    return list(_sequence(citations))


def _required_mapping(source_inputs: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = source_inputs.get(key)
    if not isinstance(value, Mapping):
        raise DeltaPacketError([DeltaPacketIssue("missing_source_packet", key, f"{key} is required")])
    return value


def _scan_for_forbidden_content(value: Any, path: str, issues: list[DeltaPacketIssue]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            key_lower = key_text.lower().replace("-", "_")
            child_path = f"{path}.{key_text}"
            if key_lower in MUTATION_KEYS and child:
                issues.append(DeltaPacketIssue("active_mutation_flag", child_path, "prompt, release-state, source, guardrail, surface, or agent-state mutation flags must be absent or false"))
            if key_lower in PRIVATE_OR_LIVE_KEYS and child:
                issues.append(DeltaPacketIssue("private_or_live_artifact", child_path, "private artifacts and live crawl/session fields must be absent"))
            _scan_for_forbidden_content(child, child_path, issues)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            _scan_for_forbidden_content(child, f"{path}[{index}]", issues)
    elif isinstance(value, str):
        normalized = " ".join(value.lower().split())
        for code, phrases in FORBIDDEN_TEXT_RULES:
            if any(phrase in normalized for phrase in phrases):
                issues.append(DeltaPacketIssue(code, path, "delta packet text must not include unsafe mutation, private/authenticated artifact, legal/permitting guarantee, or consequential action language"))


def _normalize_command(command: Any) -> list[str]:
    if isinstance(command, str):
        parts = shlex.split(command)
    elif isinstance(command, Sequence) and not isinstance(command, (bytes, bytearray, str)):
        parts = [str(part) for part in command]
    else:
        return []
    if not parts or not parts[0].startswith("python"):
        return []
    return parts


def _is_python_command(command: Any) -> bool:
    normalized = _normalize_command(command)
    return bool(normalized and normalized[0].startswith("python"))


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _mapping_items(value: Any) -> list[Mapping[str, Any]]:
    return [item for item in _sequence(value) if isinstance(item, Mapping)]


def _sequence(value: Any) -> list[Any]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return list(value)
    return []


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _text_list(value: Any) -> list[str]:
    return [_text(item) for item in _sequence(value) if _text(item)]


def _first(value: Any) -> Any:
    items = _sequence(value)
    return items[0] if items else ""
