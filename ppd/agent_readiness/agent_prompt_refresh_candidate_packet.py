"""Fixture-first PP&D agent prompt refresh candidate packet builder.

This module consumes already-committed review packets and produces prompt-change
candidates only. It does not call live LLMs, open DevHub, mutate prompt stores,
compile guardrails, or write agent state.
"""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping, Sequence

PACKET_TYPE = "ppd.agent_prompt_refresh_candidate_packet.v1"
PACKET_STATUS = "candidate_prompt_changes_not_applied"

REQUIRED_SOURCE_PACKET_KEYS = (
    "guardrail_refresh_regression_review_packet",
    "agent_regression_refresh_packet",
    "agent_consumer_release_handoff_packet",
)

REQUIRED_ATTESTATIONS = (
    "fixture_first",
    "no_live_llm",
    "no_devhub",
    "no_prompt",
    "no_guardrail",
    "no_agent_state_mutation",
)

_PRIVATE_OR_LIVE_MARKERS = (
    "/home/",
    "/Users/",
    "C:/Users/",
    "file://",
    "auth_state",
    "session_state",
    "trace.zip",
    ".har",
    "live llm",
    "live devhub",
    "opened devhub",
    "called the llm",
)

_MUTATION_KEYS = {
    "active_agent_state_mutation",
    "active_guardrail_mutation",
    "active_prompt_mutation",
    "agent_state_mutation_enabled",
    "guardrail_mutation_enabled",
    "prompt_mutation_enabled",
}

_CONSEQUENTIAL_WORDS = (
    "cancel",
    "certify",
    "payment",
    "pay",
    "purchase",
    "schedule",
    "submit",
    "submission",
    "upload",
    "withdraw",
)


class AgentPromptRefreshCandidatePacketError(ValueError):
    """Raised when a prompt refresh candidate packet is malformed."""


def load_source_packets(path: str | Path) -> dict[str, Any]:
    """Load prompt-refresh source packets from a local fixture."""

    with Path(path).open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise AgentPromptRefreshCandidatePacketError("source fixture must be a JSON object")
    return data


def build_agent_prompt_refresh_candidate_packet(source_packets: Mapping[str, Any]) -> dict[str, Any]:
    """Build a deterministic prompt refresh candidate packet from offline inputs."""

    _reject_unsafe_content(source_packets)
    missing = [key for key in REQUIRED_SOURCE_PACKET_KEYS if key not in source_packets]
    if missing:
        raise AgentPromptRefreshCandidatePacketError("missing source packet(s): " + ", ".join(missing))

    guardrail_packet = _mapping(source_packets["guardrail_refresh_regression_review_packet"])
    regression_packet = _mapping(source_packets["agent_regression_refresh_packet"])
    handoff_packet = _mapping(source_packets["agent_consumer_release_handoff_packet"])

    prompt_changes = _prompt_change_candidates(guardrail_packet, regression_packet, handoff_packet)
    safe_scenarios = _safe_read_only_scenarios(regression_packet, handoff_packet)

    packet = {
        "packet_type": PACKET_TYPE,
        "packet_id": "agent-prompt-refresh-candidate-20260529-fixture-first",
        "packet_status": PACKET_STATUS,
        "source_packet_ids": {
            "guardrail_refresh_regression_review_packet": _packet_id(guardrail_packet, "guardrail-refresh-regression-review"),
            "agent_regression_refresh_packet": _packet_id(regression_packet, "agent-regression-refresh"),
            "agent_consumer_release_handoff_packet": _packet_id(handoff_packet, "agent-consumer-release-handoff"),
        },
        "prompt_change_candidates": prompt_changes,
        "supported_safe_read_only_scenarios": safe_scenarios,
        "blocked_consequential_action_language": _blocked_action_language(guardrail_packet, regression_packet, handoff_packet),
        "rollback_notes": _rollback_notes(guardrail_packet, prompt_changes),
        "reviewer_owner_fields": _reviewer_owner_fields(guardrail_packet, regression_packet, handoff_packet),
        "offline_validation_commands": _offline_validation_commands(guardrail_packet, regression_packet, handoff_packet),
        "attestations": {key: True for key in REQUIRED_ATTESTATIONS},
    }
    validate_agent_prompt_refresh_candidate_packet(packet)
    return deepcopy(packet)


def validate_agent_prompt_refresh_candidate_packet(packet: Mapping[str, Any]) -> None:
    """Raise when a prompt refresh candidate packet is invalid."""

    problems: list[str] = []
    if not isinstance(packet, Mapping):
        raise AgentPromptRefreshCandidatePacketError("packet must be an object")

    try:
        _reject_unsafe_content(packet)
    except AgentPromptRefreshCandidatePacketError as exc:
        problems.append(str(exc))

    if packet.get("packet_type") != PACKET_TYPE:
        problems.append("packet_type must be " + PACKET_TYPE)
    if packet.get("packet_status") != PACKET_STATUS:
        problems.append("packet_status must keep prompt changes unapplied")

    source_packet_ids = packet.get("source_packet_ids")
    if not isinstance(source_packet_ids, Mapping):
        problems.append("source_packet_ids must be an object")
    else:
        for key in REQUIRED_SOURCE_PACKET_KEYS:
            if not _text(source_packet_ids.get(key)):
                problems.append(f"source_packet_ids.{key} is required")

    for index, change in enumerate(_mapping_sequence(packet.get("prompt_change_candidates"))):
        path = f"prompt_change_candidates[{index}]"
        if not _text(change.get("change_id")):
            problems.append(path + ".change_id is required")
        if change.get("status") != "candidate_only":
            problems.append(path + ".status must be candidate_only")
        if not _text(change.get("candidate_prompt_text")):
            problems.append(path + ".candidate_prompt_text is required")
        if not _string_list(change.get("source_evidence_ids")):
            problems.append(path + ".source_evidence_ids is required")
        if not _text(change.get("reviewer_owner")):
            problems.append(path + ".reviewer_owner is required")
    if not _mapping_sequence(packet.get("prompt_change_candidates")):
        problems.append("prompt_change_candidates must be a non-empty list")

    for index, scenario in enumerate(_mapping_sequence(packet.get("supported_safe_read_only_scenarios"))):
        path = f"supported_safe_read_only_scenarios[{index}]"
        if not _text(scenario.get("scenario_id")):
            problems.append(path + ".scenario_id is required")
        if scenario.get("automation_boundary") != "safe_read_only_or_reversible_draft_only":
            problems.append(path + ".automation_boundary must be safe_read_only_or_reversible_draft_only")
        if not _string_list(scenario.get("source_evidence_ids")):
            problems.append(path + ".source_evidence_ids is required")
    if not _mapping_sequence(packet.get("supported_safe_read_only_scenarios")):
        problems.append("supported_safe_read_only_scenarios must be a non-empty list")

    if not _mapping_sequence(packet.get("blocked_consequential_action_language")):
        problems.append("blocked_consequential_action_language must be a non-empty list")
    if not _mapping_sequence(packet.get("rollback_notes")):
        problems.append("rollback_notes must be a non-empty list")
    if not _mapping_sequence(packet.get("reviewer_owner_fields")):
        problems.append("reviewer_owner_fields must be a non-empty list")
    if not _command_sequence(packet.get("offline_validation_commands")):
        problems.append("offline_validation_commands must be a non-empty list of commands")

    attestations = packet.get("attestations")
    if not isinstance(attestations, Mapping):
        problems.append("attestations must be an object")
    else:
        for key in REQUIRED_ATTESTATIONS:
            if attestations.get(key) is not True:
                problems.append(f"attestations.{key} must be true")

    if problems:
        raise AgentPromptRefreshCandidatePacketError("; ".join(problems))


def _prompt_change_candidates(
    guardrail_packet: Mapping[str, Any],
    regression_packet: Mapping[str, Any],
    handoff_packet: Mapping[str, Any],
) -> list[dict[str, Any]]:
    changes: list[dict[str, Any]] = []
    guardrail_packet_id = _packet_id(guardrail_packet, "guardrail-refresh-regression-review")
    regression_packet_id = _packet_id(regression_packet, "agent-regression-refresh")
    handoff_packet_id = _packet_id(handoff_packet, "agent-consumer-release-handoff")

    for index, expectation in enumerate(_mapping_sequence(guardrail_packet.get("guardrail_predicate_expectations")), start=1):
        predicate_id = _text(expectation.get("predicate_id") or f"predicate-{index}")
        changes.append(
            {
                "change_id": f"prompt-guardrail-boundary-{index}",
                "status": "candidate_only",
                "candidate_prompt_text": "Before offering a PP&D next action, cite the guardrail predicate " + predicate_id + " and keep consequential official actions blocked unless a separate attended confirmation gate applies.",
                "change_reason": _text(expectation.get("expectation_basis")) or "Guardrail regression expectation carried into prompt refresh review.",
                "source_packet_id": guardrail_packet_id,
                "source_evidence_ids": _string_list(expectation.get("source_evidence_ids")) or [predicate_id],
                "reviewer_owner": _text(expectation.get("reviewer_owner")) or _first_owner(guardrail_packet),
            }
        )

    for index, scenario in enumerate(_mapping_sequence(regression_packet.get("offline_user_scenarios")), start=1):
        scenario_id = _text(scenario.get("scenario_id") or f"agent-regression-scenario-{index}")
        changes.append(
            {
                "change_id": f"prompt-missing-fact-{index}",
                "status": "candidate_only",
                "candidate_prompt_text": "For " + scenario_id + ", ask only for missing, stale, ambiguous, or conflicting facts before drafting; offer fixture-backed safe-read-only review or reversible draft preview only.",
                "change_reason": _text(scenario.get("refusal_explanation")) or "Agent regression scenario requires narrower missing-fact prompt behavior.",
                "source_packet_id": regression_packet_id,
                "source_evidence_ids": _citation_ids(scenario.get("cited_offline_evidence")) or [scenario_id],
                "reviewer_owner": _text(scenario.get("reviewer_owner")) or _first_owner(regression_packet),
            }
        )

    for index, example in enumerate(_mapping_sequence(handoff_packet.get("refusal_examples")), start=1):
        changes.append(
            {
                "change_id": f"prompt-release-handoff-refusal-{index}",
                "status": "candidate_only",
                "candidate_prompt_text": "Use release-handoff refusal language for DevHub submit, certify, upload, schedule, cancel, withdraw, purchase, and payment requests; route the user to attended review instead of automating the action.",
                "change_reason": _text(example.get("response") or example.get("message")) or "Release handoff requires refusal wording for consequential actions.",
                "source_packet_id": handoff_packet_id,
                "source_evidence_ids": _string_list(example.get("source_evidence_ids")) or ["release-handoff-refusal"],
                "reviewer_owner": _first_owner(handoff_packet),
            }
        )

    return changes


def _safe_read_only_scenarios(regression_packet: Mapping[str, Any], handoff_packet: Mapping[str, Any]) -> list[dict[str, Any]]:
    scenarios: list[dict[str, Any]] = []
    for index, scenario in enumerate(_mapping_sequence(regression_packet.get("offline_user_scenarios")), start=1):
        scenario_id = _text(scenario.get("scenario_id") or f"safe-read-only-{index}")
        scenarios.append(
            {
                "scenario_id": scenario_id,
                "supported_action": "Review cited offline evidence, identify missing facts, and preview reversible draft language.",
                "automation_boundary": "safe_read_only_or_reversible_draft_only",
                "blocked_follow_up": _text(scenario.get("blocked_consequential_action_message")) or "Blocked: no official PP&D action may be submitted from this packet.",
                "source_evidence_ids": _citation_ids(scenario.get("cited_offline_evidence")) or [scenario_id],
            }
        )
    if not scenarios:
        scenarios.append(
            {
                "scenario_id": "release-handoff-read-only-review",
                "supported_action": "Review release handoff evidence and refusal examples without writing consumer or agent state.",
                "automation_boundary": "safe_read_only_or_reversible_draft_only",
                "blocked_follow_up": "Blocked: release handoff does not authorize live DevHub or consequential controls.",
                "source_evidence_ids": _handoff_evidence_ids(handoff_packet),
            }
        )
    return scenarios


def _blocked_action_language(
    guardrail_packet: Mapping[str, Any],
    regression_packet: Mapping[str, Any],
    handoff_packet: Mapping[str, Any],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, scenario in enumerate(_mapping_sequence(regression_packet.get("offline_user_scenarios")), start=1):
        message = _text(scenario.get("blocked_consequential_action_message"))
        if message:
            rows.append(
                {
                    "language_id": f"blocked-agent-regression-{index}",
                    "message": message,
                    "blocked_action_categories": list(_CONSEQUENTIAL_WORDS),
                    "source_evidence_ids": _citation_ids(scenario.get("cited_offline_evidence")) or [_text(scenario.get("scenario_id")) or f"scenario-{index}"],
                }
            )
    for index, example in enumerate(_mapping_sequence(handoff_packet.get("refusal_examples")), start=1):
        rows.append(
            {
                "language_id": f"blocked-release-handoff-{index}",
                "message": _text(example.get("response") or example.get("message") or example.get("refusal_text")),
                "blocked_action_categories": list(_CONSEQUENTIAL_WORDS),
                "source_evidence_ids": _string_list(example.get("source_evidence_ids")) or _handoff_evidence_ids(handoff_packet),
            }
        )
    if not rows:
        rows.append(
            {
                "language_id": "blocked-default-consequential-actions",
                "message": "Blocked: the prompt refresh candidate can support safe read-only review and reversible draft previews only; it cannot submit, certify, upload, schedule, cancel, withdraw, purchase, pay, or mutate agent state.",
                "blocked_action_categories": list(_CONSEQUENTIAL_WORDS),
                "source_evidence_ids": _string_list(guardrail_packet.get("affected_guardrail_bundle_ids")) or ["guardrail-refresh-review"],
            }
        )
    return rows


def _rollback_notes(guardrail_packet: Mapping[str, Any], prompt_changes: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    notes = list(_mapping_sequence(guardrail_packet.get("rollback_notes")))
    notes.append(
        {
            "note_id": "rollback.prompt-candidates-not-applied",
            "instruction": "Discard these prompt-change candidates if any cited guardrail, regression, or handoff source packet is superseded before reviewer approval.",
            "applies_to_change_ids": [_text(change.get("change_id")) for change in prompt_changes if _text(change.get("change_id"))],
            "source_evidence_ids": _string_list(guardrail_packet.get("affected_guardrail_bundle_ids")) or ["guardrail-refresh-review"],
        }
    )
    return notes


def _reviewer_owner_fields(*packets: Mapping[str, Any]) -> list[dict[str, str]]:
    owners: list[dict[str, str]] = []
    for index, packet in enumerate(packets, start=1):
        owner = _first_owner(packet)
        if owner:
            owners.append({"reviewer_owner_id": owner, "source_packet_id": _packet_id(packet, f"source-packet-{index}")})
    return owners or [{"reviewer_owner_id": "PP&D prompt refresh reviewer", "source_packet_id": "fixture-default"}]


def _offline_validation_commands(*packets: Mapping[str, Any]) -> list[list[str]]:
    commands = [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]]
    for packet in packets:
        for command in _command_sequence(packet.get("offline_validation_commands") or packet.get("expected_offline_validation_commands")):
            if command not in commands:
                commands.append(command)
    command = ["python3", "-m", "unittest", "ppd.tests.test_agent_prompt_refresh_candidate_packet"]
    if command not in commands:
        commands.append(command)
    return commands


def _reject_unsafe_content(value: Any, path: str = "$") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            lowered_key = key_text.lower()
            child_path = f"{path}.{key_text}"
            if lowered_key in _MUTATION_KEYS and child not in (False, None, "", "disabled", "not_enabled"):
                raise AgentPromptRefreshCandidatePacketError(child_path + " must not enable prompt, guardrail, or agent-state mutation")
            if "enabled" in lowered_key and any(word in lowered_key for word in _CONSEQUENTIAL_WORDS) and child not in (False, None, "", "disabled", "not_enabled"):
                raise AgentPromptRefreshCandidatePacketError(child_path + " must not enable consequential controls")
            _reject_unsafe_content(child, child_path)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child in enumerate(value):
            _reject_unsafe_content(child, f"{path}[{index}]")
    elif isinstance(value, str):
        lowered = value.lower()
        if any(marker in lowered for marker in _PRIVATE_OR_LIVE_MARKERS):
            raise AgentPromptRefreshCandidatePacketError(path + " must not include private paths, auth artifacts, live execution claims, or traces")


def _packet_id(packet: Mapping[str, Any], fallback: str) -> str:
    return _text(packet.get("packet_id") or packet.get("id") or fallback)


def _first_owner(packet: Mapping[str, Any]) -> str:
    direct = _text(packet.get("reviewer_owner") or packet.get("owner"))
    if direct:
        return direct
    owners = packet.get("reviewer_owner_fields") or packet.get("reviewer_owners") or packet.get("reviewers")
    for owner in _mapping_sequence(owners):
        text = _text(owner.get("reviewer_owner_id") or owner.get("owner_id") or owner.get("name"))
        if text:
            return text
    if isinstance(owners, Mapping):
        for value in owners.values():
            text = _text(value)
            if text:
                return text
    return "PP&D prompt refresh reviewer"


def _citation_ids(value: Any) -> list[str]:
    ids: list[str] = []
    for item in _mapping_sequence(value):
        text = _text(item.get("source_evidence_id") or item.get("evidence_id") or item.get("source_packet_id") or item.get("locator"))
        if text:
            ids.append(text)
    if not ids:
        ids = _string_list(value)
    return sorted(set(ids))


def _handoff_evidence_ids(packet: Mapping[str, Any]) -> list[str]:
    ids: list[str] = []
    for evidence in _mapping_sequence(packet.get("normalized_source_evidence")):
        evidence_id = _text(evidence.get("evidence_id"))
        if evidence_id:
            ids.append(evidence_id)
    return ids or ["release-handoff-evidence"]


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _mapping_sequence(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _command_sequence(value: Any) -> list[list[str]]:
    commands: list[list[str]] = []
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return commands
    for command in value:
        if isinstance(command, Sequence) and not isinstance(command, (str, bytes)) and all(isinstance(part, str) and part for part in command):
            commands.append(list(command))
    return commands


def _string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value.strip() else []
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return [str(item).strip() for item in value if str(item).strip()]
    return [str(value).strip()] if str(value).strip() else []


def _text(value: Any) -> str:
    return str(value).strip() if value is not None else ""


__all__ = [
    "AgentPromptRefreshCandidatePacketError",
    "PACKET_TYPE",
    "REQUIRED_ATTESTATIONS",
    "REQUIRED_SOURCE_PACKET_KEYS",
    "build_agent_prompt_refresh_candidate_packet",
    "load_source_packets",
    "validate_agent_prompt_refresh_candidate_packet",
]
