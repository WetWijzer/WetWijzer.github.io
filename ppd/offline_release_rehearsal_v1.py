"""Fixture-first supervised offline release rehearsal v1.

This module consumes committed fixture packets only. It does not crawl public
sources, open DevHub, read private artifacts, or perform official permitting
or promotion actions.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Mapping


PACKET_TYPE = "ppd.offline_release_rehearsal.v1"

REQUIRED_PACKET_IDS = (
    "release_gate_decision_matrix_v1",
    "public_source_refresh_reviewer_queue_v1",
    "devhub_manual_observation_reviewer_queue_v1",
    "guarded_agent_response_acceptance_packet_v1",
    "release_candidate_evidence_bundle_v1",
)

REQUIRED_ATTESTATIONS = (
    "no_live_crawl",
    "no_devhub",
    "no_private_artifact",
    "no_official_action",
    "no_active_promotion",
)

REQUIRED_STEP_IDS = (
    "confirm_release_gate_decision_matrix",
    "review_public_source_refresh_queue",
    "review_devhub_manual_observation_queue",
    "verify_guarded_agent_response_acceptance",
    "assemble_release_candidate_evidence",
    "record_manual_review_blockers",
    "validate_fixture_artifacts",
    "hold_promotion_pending_supervisor_signoff",
)

FORBIDDEN_KEYS = {
    "archive_artifact_ref",
    "auth_state",
    "browser_state",
    "cookie",
    "credentials",
    "download_path",
    "downloaded_document_path",
    "field_value",
    "har",
    "local_path",
    "password",
    "private_artifact",
    "private_path",
    "raw_body",
    "raw_crawl_output",
    "raw_html",
    "raw_pdf",
    "screenshot",
    "secret",
    "session_state",
    "storage_state",
    "token",
    "trace",
    "value",
    "warc_path",
}

FORBIDDEN_TRUE_KEYS = {
    "active_promotion",
    "active_release_state_mutation",
    "devhub_execution_performed",
    "devhub_run_performed",
    "live_actions_performed",
    "live_crawl_executed",
    "live_devhub_execution",
    "live_network_called",
    "official_action_performed",
    "promotion_executed",
    "submitted_to_devhub",
    "uses_authenticated_session",
}

FORBIDDEN_TEXT_RE = re.compile(
    r"(^file://)|(^/home/[^/]+/)|(^/Users/[^/]+/)|(^/root/)|(^/tmp/)|"
    r"(auth[_-]?state|browser[_-]?state|cookie|credential|har|password|private[_-]?artifact|"
    r"raw[_-]?(body|crawl|data|html|pdf)|session[_-]?(state|storage)|screenshot|secret|storage[_-]?state|token|trace\.zip|warc)",
    re.IGNORECASE,
)

CONSEQUENTIAL_ACTION_RE = re.compile(
    r"\b(click\s+submit|submit\s+(the\s+)?(permit|application|request)|upload\s+(correction|document|file|plans?)|"
    r"pay\s+(fee|fees|invoice)|enter\s+payment|schedule\s+(an\s+)?inspection|certify\s+(the\s+)?(application|acknowledgement)|"
    r"cancel\s+(permit|inspection|application)|withdraw\s+(permit|application|request)|purchase\s+(permit|trade\s+permit))\b",
    re.IGNORECASE,
)


class OfflineReleaseRehearsalError(ValueError):
    """Raised when an offline release rehearsal packet is invalid."""


def load_offline_release_rehearsal_fixture(path: str | Path) -> dict[str, Any]:
    fixture_path = Path(path)
    with fixture_path.open("r", encoding="utf-8") as handle:
        loaded = json.load(handle)
    if not isinstance(loaded, dict):
        raise OfflineReleaseRehearsalError("fixture must contain a JSON object")
    return loaded


def build_offline_release_rehearsal(packet: Mapping[str, Any]) -> dict[str, Any]:
    """Build a cited supervised offline release rehearsal from fixture packets."""

    problems = validate_offline_release_rehearsal_input(packet)
    if problems:
        raise OfflineReleaseRehearsalError("invalid offline release rehearsal input: " + "; ".join(problems))

    consumed_packets = list(_mapping_sequence(packet.get("consumed_packets")))
    packet_by_id = {str(item["packet_id"]): item for item in consumed_packets}
    blockers = _manual_review_blockers(packet_by_id)
    steps = _dry_run_steps(packet_by_id, blockers)
    artifacts = _expected_artifacts(packet_by_id)

    rehearsal = {
        "packet_type": PACKET_TYPE,
        "fixture_only": True,
        "supervised": True,
        "decision_basis": "committed_fixture_packets_only",
        "consumed_packet_ids": list(REQUIRED_PACKET_IDS),
        "cited_dry_run_release_steps": steps,
        "expected_fixture_only_artifacts": artifacts,
        "manual_review_blockers": blockers,
        "rollback_checkpoints": _rollback_checkpoints(packet_by_id),
        "validation_command_inventory": _validation_commands(packet),
        "attestations": {name: True for name in REQUIRED_ATTESTATIONS},
    }

    output_problems = validate_offline_release_rehearsal_output(rehearsal)
    if output_problems:
        raise OfflineReleaseRehearsalError("invalid offline release rehearsal output: " + "; ".join(output_problems))
    return rehearsal


def rehearsal_from_fixture(path: str | Path) -> dict[str, Any]:
    return build_offline_release_rehearsal(load_offline_release_rehearsal_fixture(path))


def validate_offline_release_rehearsal_input(packet: Mapping[str, Any]) -> list[str]:
    problems: list[str] = []
    problems.extend(_walk_safety_errors(packet, "$"))

    if packet.get("packet_type") != "ppd.offline_release_rehearsal_input.v1":
        problems.append("packet_type must be ppd.offline_release_rehearsal_input.v1")
    if packet.get("fixture_only") is not True:
        problems.append("fixture_only must be true")
    if packet.get("supervised") is not True:
        problems.append("supervised must be true")

    attestations = packet.get("attestations")
    if not isinstance(attestations, Mapping):
        problems.append("attestations must be an object")
    else:
        for name in REQUIRED_ATTESTATIONS:
            if attestations.get(name) is not True:
                problems.append(f"attestations.{name} must be true")

    consumed_packets = list(_mapping_sequence(packet.get("consumed_packets")))
    packet_ids = {str(item.get("packet_id") or "") for item in consumed_packets}
    for packet_id in REQUIRED_PACKET_IDS:
        if packet_id not in packet_ids:
            problems.append(f"consumed_packets missing {packet_id}")

    for index, item in enumerate(consumed_packets):
        path = f"consumed_packets[{index}]"
        _require_non_empty_string(item, "packet_id", path, problems)
        _require_non_empty_string(item, "schema_version", path, problems)
        _require_non_empty_string(item, "status", path, problems)
        _require_citations(item, path, problems)

    command_inventory = packet.get("validation_command_inventory")
    if not isinstance(command_inventory, list) or not command_inventory:
        problems.append("validation_command_inventory must be a non-empty list")
    else:
        for index, command in enumerate(command_inventory):
            if not _is_command(command):
                problems.append(f"validation_command_inventory[{index}] must be a list of strings")

    return problems


def validate_offline_release_rehearsal_output(rehearsal: Mapping[str, Any]) -> list[str]:
    problems: list[str] = []
    problems.extend(_walk_safety_errors(rehearsal, "$"))

    if rehearsal.get("packet_type") != PACKET_TYPE:
        problems.append(f"packet_type must be {PACKET_TYPE}")
    if rehearsal.get("fixture_only") is not True:
        problems.append("fixture_only must be true")
    if rehearsal.get("supervised") is not True:
        problems.append("supervised must be true")

    consumed_packet_ids = tuple(_string_sequence(rehearsal.get("consumed_packet_ids")))
    if consumed_packet_ids != REQUIRED_PACKET_IDS:
        problems.append("consumed_packet_ids must match the required packet order")

    attestations = rehearsal.get("attestations")
    if not isinstance(attestations, Mapping):
        problems.append("attestations must be an object")
    else:
        for name in REQUIRED_ATTESTATIONS:
            if attestations.get(name) is not True:
                problems.append(f"attestations.{name} must be true")

    steps = list(_mapping_sequence(rehearsal.get("cited_dry_run_release_steps")))
    step_ids = tuple(str(step.get("step_id") or "") for step in steps)
    if step_ids != REQUIRED_STEP_IDS:
        problems.append("cited_dry_run_release_steps must contain the required step order")
    for index, step in enumerate(steps):
        path = f"cited_dry_run_release_steps[{index}]"
        _require_non_empty_string(step, "instruction", path, problems)
        _require_citations(step, path, problems)
        refs = set(_string_sequence(step.get("consumed_packet_refs")))
        if not refs or not refs.issubset(set(REQUIRED_PACKET_IDS)):
            problems.append(f"{path}.consumed_packet_refs must reference consumed packets")

    artifacts = list(_mapping_sequence(rehearsal.get("expected_fixture_only_artifacts")))
    if not artifacts:
        problems.append("expected_fixture_only_artifacts must be non-empty")
    for index, artifact in enumerate(artifacts):
        path = f"expected_fixture_only_artifacts[{index}]"
        _require_non_empty_string(artifact, "artifact_id", path, problems)
        _require_non_empty_string(artifact, "expected_status", path, problems)
        _require_citations(artifact, path, problems)
        if artifact.get("fixture_only") is not True:
            problems.append(f"{path}.fixture_only must be true")

    blockers = list(_mapping_sequence(rehearsal.get("manual_review_blockers")))
    if not blockers:
        problems.append("manual_review_blockers must include at least one disposition")
    for index, blocker in enumerate(blockers):
        path = f"manual_review_blockers[{index}]"
        _require_non_empty_string(blocker, "blocker_id", path, problems)
        _require_non_empty_string(blocker, "disposition", path, problems)
        _require_citations(blocker, path, problems)
        if blocker.get("requires_manual_review") is not True:
            problems.append(f"{path}.requires_manual_review must be true")

    rollback_checkpoints = list(_mapping_sequence(rehearsal.get("rollback_checkpoints")))
    if not rollback_checkpoints:
        problems.append("rollback_checkpoints must be non-empty")
    for index, checkpoint in enumerate(rollback_checkpoints):
        path = f"rollback_checkpoints[{index}]"
        _require_non_empty_string(checkpoint, "checkpoint_id", path, problems)
        _require_non_empty_string(checkpoint, "restore_action", path, problems)
        _require_citations(checkpoint, path, problems)

    commands = rehearsal.get("validation_command_inventory")
    if not isinstance(commands, list) or not commands:
        problems.append("validation_command_inventory must be a non-empty list")
    else:
        for index, command in enumerate(commands):
            if not _is_command(command):
                problems.append(f"validation_command_inventory[{index}] must be a list of strings")

    return problems


def _dry_run_steps(packet_by_id: Mapping[str, Mapping[str, Any]], blockers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    blocker_count = len([blocker for blocker in blockers if blocker["disposition"] != "not_blocking"])
    return [
        _step("confirm_release_gate_decision_matrix", "Confirm the release gate matrix decision and carry forward every defer or block row as a supervised release blocker.", ["release_gate_decision_matrix_v1"], packet_by_id),
        _step("review_public_source_refresh_queue", "Review public source refresh queue items from fixture citations and keep source refresh work in reviewer-owned pending status.", ["public_source_refresh_reviewer_queue_v1"], packet_by_id),
        _step("review_devhub_manual_observation_queue", "Review DevHub manual observation queue items as offline notes only and require attended reviewer disposition before any browser work.", ["devhub_manual_observation_reviewer_queue_v1"], packet_by_id),
        _step("verify_guarded_agent_response_acceptance", "Verify accepted agent responses are cited, reversible, and free of consequential action instructions.", ["guarded_agent_response_acceptance_packet_v1"], packet_by_id),
        _step("assemble_release_candidate_evidence", "Assemble the release candidate evidence bundle into fixture-only artifact expectations and cite each included packet.", ["release_candidate_evidence_bundle_v1"], packet_by_id),
        _step("record_manual_review_blockers", f"Record {blocker_count} manual-review blocker disposition entries and keep release promotion unavailable until each is closed.", list(REQUIRED_PACKET_IDS), packet_by_id),
        _step("validate_fixture_artifacts", "Run only deterministic local validation commands against committed PP&D fixtures and Python modules.", list(REQUIRED_PACKET_IDS), packet_by_id),
        _step("hold_promotion_pending_supervisor_signoff", "Hold the rehearsal at supervised dry-run status with no active promotion or official release claim.", list(REQUIRED_PACKET_IDS), packet_by_id),
    ]


def _step(step_id: str, instruction: str, refs: list[str], packet_by_id: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    return {
        "step_id": step_id,
        "instruction": instruction,
        "consumed_packet_refs": refs,
        "citations": _citations_for_refs(refs, packet_by_id),
        "requires_supervisor_review": True,
    }


def _expected_artifacts(packet_by_id: Mapping[str, Mapping[str, Any]]) -> list[dict[str, Any]]:
    artifact_specs = (
        ("release_gate_decision_matrix_summary", "release_gate_decision_matrix_v1"),
        ("public_source_refresh_reviewer_queue_summary", "public_source_refresh_reviewer_queue_v1"),
        ("devhub_manual_observation_reviewer_queue_summary", "devhub_manual_observation_reviewer_queue_v1"),
        ("guarded_agent_response_acceptance_summary", "guarded_agent_response_acceptance_packet_v1"),
        ("release_candidate_evidence_bundle_summary", "release_candidate_evidence_bundle_v1"),
        ("offline_release_rehearsal_report", "release_candidate_evidence_bundle_v1"),
    )
    artifacts = []
    for artifact_id, packet_ref in artifact_specs:
        artifacts.append(
            {
                "artifact_id": artifact_id,
                "fixture_only": True,
                "expected_status": "derived_from_committed_fixture_metadata",
                "consumed_packet_refs": [packet_ref],
                "citations": _citations_for_refs([packet_ref], packet_by_id),
            }
        )
    return artifacts


def _manual_review_blockers(packet_by_id: Mapping[str, Mapping[str, Any]]) -> list[dict[str, Any]]:
    blockers: list[dict[str, Any]] = []
    for packet_id in REQUIRED_PACKET_IDS:
        packet = packet_by_id[packet_id]
        for index, blocker in enumerate(_mapping_sequence(packet.get("manual_review_blockers"))):
            blocker_id = str(blocker.get("blocker_id") or f"{packet_id}_blocker_{index + 1}")
            blockers.append(
                {
                    "blocker_id": blocker_id,
                    "source_packet_ref": packet_id,
                    "requires_manual_review": True,
                    "disposition": str(blocker.get("disposition") or "pending_manual_review"),
                    "owner": str(blocker.get("owner") or packet.get("owner") or "supervisor"),
                    "citations": _merge_citations(blocker.get("citations"), packet.get("citations")),
                }
            )
    if blockers:
        return blockers
    return [
        {
            "blocker_id": "supervisor_signoff_required",
            "source_packet_ref": "release_gate_decision_matrix_v1",
            "requires_manual_review": True,
            "disposition": "pending_manual_release_review",
            "owner": "supervisor",
            "citations": _citations_for_refs(["release_gate_decision_matrix_v1"], packet_by_id),
        }
    ]


def _rollback_checkpoints(packet_by_id: Mapping[str, Mapping[str, Any]]) -> list[dict[str, Any]]:
    refs = list(REQUIRED_PACKET_IDS)
    citations = _citations_for_refs(refs, packet_by_id)
    return [
        {
            "checkpoint_id": "restore_last_passing_fixture_bundle",
            "restore_action": "Restore the last passing committed fixture bundle and rerun deterministic validation.",
            "consumed_packet_refs": refs,
            "citations": citations,
        },
        {
            "checkpoint_id": "reopen_reviewer_queues",
            "restore_action": "Return public source refresh and DevHub manual observation reviewer queues to pending supervisor review.",
            "consumed_packet_refs": ["public_source_refresh_reviewer_queue_v1", "devhub_manual_observation_reviewer_queue_v1"],
            "citations": _citations_for_refs(["public_source_refresh_reviewer_queue_v1", "devhub_manual_observation_reviewer_queue_v1"], packet_by_id),
        },
        {
            "checkpoint_id": "retain_no_promotion_attestations",
            "restore_action": "Keep active promotion disabled and preserve all no-live, no-private, and no-official-action attestations.",
            "consumed_packet_refs": refs,
            "citations": citations,
        },
    ]


def _validation_commands(packet: Mapping[str, Any]) -> list[list[str]]:
    commands = packet.get("validation_command_inventory")
    if not isinstance(commands, list):
        return []
    return [list(command) for command in commands if _is_command(command)]


def _citations_for_refs(refs: list[str], packet_by_id: Mapping[str, Mapping[str, Any]]) -> list[str]:
    citations: list[str] = []
    for ref in refs:
        citations.extend(_string_sequence(packet_by_id[ref].get("citations")))
    return _dedupe(citations)


def _merge_citations(primary: Any, fallback: Any) -> list[str]:
    merged = _string_sequence(primary) + _string_sequence(fallback)
    return _dedupe(merged)


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def _walk_safety_errors(value: Any, path: str) -> list[str]:
    problems: list[str] = []
    if isinstance(value, Mapping):
        for key, nested in value.items():
            key_text = str(key)
            child_path = f"{path}.{key_text}"
            if key_text in FORBIDDEN_KEYS:
                problems.append(f"{child_path} is a forbidden private or raw artifact key")
            if key_text in FORBIDDEN_TRUE_KEYS and nested is True:
                problems.append(f"{child_path} must not be true in an offline release rehearsal")
            problems.extend(_walk_safety_errors(nested, child_path))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            problems.extend(_walk_safety_errors(item, f"{path}[{index}]"))
    elif isinstance(value, str):
        if FORBIDDEN_TEXT_RE.search(value):
            problems.append(f"{path} contains private or raw artifact text")
        if CONSEQUENTIAL_ACTION_RE.search(value):
            problems.append(f"{path} contains consequential official-action text")
    return problems


def _mapping_sequence(value: Any) -> tuple[Mapping[str, Any], ...]:
    if not isinstance(value, list):
        return ()
    return tuple(item for item in value if isinstance(item, Mapping))


def _string_sequence(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str) and item]


def _require_non_empty_string(item: Mapping[str, Any], key: str, path: str, problems: list[str]) -> None:
    if not isinstance(item.get(key), str) or not item.get(key):
        problems.append(f"{path}.{key} must be a non-empty string")


def _require_citations(item: Mapping[str, Any], path: str, problems: list[str]) -> None:
    if not _string_sequence(item.get("citations")):
        problems.append(f"{path}.citations must be a non-empty list of strings")


def _is_command(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(isinstance(part, str) and part for part in value)
