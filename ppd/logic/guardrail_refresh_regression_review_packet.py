"""Fixture-first guardrail refresh regression review packet builder.

This module consumes already-materialized PP&D review packets and emits a
review-only regression packet. It must not call live LLMs, open DevHub, mutate
prompts, compile guardrails, or update release state.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
from typing import Any

PACKET_TYPE = "ppd.guardrail_refresh_regression_review_packet.v1"

REQUIRED_SOURCE_PACKET_KEYS = (
    "process_and_guardrail_refresh_candidate_packet",
    "agent_regression_refresh_packet",
    "source_refresh_result_reconciliation_packet",
)

REQUIRED_ATTESTATIONS = (
    "fixture_first",
    "no_live_llm",
    "no_devhub",
    "no_prompt_mutation",
    "no_guardrail_mutation",
    "no_release_state_mutation",
)

_MUTATION_KEYS = {
    "active_guardrail_mutation",
    "active_prompt_mutation",
    "guardrail_mutation_enabled",
    "prompt_mutation_enabled",
    "release_state_mutation",
    "release_state_updated",
}

_LIVE_KEYS = {
    "call_llm",
    "calls_llm",
    "devhub_enabled",
    "execute_devhub",
    "launch_devhub",
    "live_devhub",
    "live_llm",
    "open_browser",
    "uses_devhub",
}

_PRIVATE_MARKERS = (
    "/home/",
    "/Users/",
    "C:/Users/",
    "file://",
    "auth_state",
    "session_state",
    "trace.zip",
    ".har",
)


class GuardrailRefreshRegressionReviewPacketError(ValueError):
    """Raised when a fixture-first review packet is malformed."""


def build_guardrail_refresh_regression_review_packet(source_packets: Mapping[str, Any]) -> dict[str, Any]:
    """Build a deterministic review packet from three offline source packets."""

    _reject_live_private_or_mutating_inputs(source_packets)
    missing = [key for key in REQUIRED_SOURCE_PACKET_KEYS if key not in source_packets]
    if missing:
        raise GuardrailRefreshRegressionReviewPacketError("missing source packet(s): " + ", ".join(missing))

    process_packet = _mapping(source_packets["process_and_guardrail_refresh_candidate_packet"])
    agent_packet = _mapping(source_packets["agent_regression_refresh_packet"])
    reconciliation_packet = _mapping(source_packets["source_refresh_result_reconciliation_packet"])

    predicate_expectations = _predicate_expectations(process_packet, agent_packet, reconciliation_packet)
    affected_bundle_ids = _affected_guardrail_bundle_ids(process_packet, reconciliation_packet)
    rollback_notes = _rollback_notes(process_packet, reconciliation_packet, affected_bundle_ids)

    packet = {
        "packet_type": PACKET_TYPE,
        "packet_id": "guardrail-refresh-regression-review-20260529-fixture-first",
        "packet_status": "review_required_no_state_mutation",
        "source_packet_ids": {
            "process_and_guardrail_refresh_candidate_packet": _packet_id(process_packet, "process-guardrail-refresh-candidate"),
            "agent_regression_refresh_packet": _packet_id(agent_packet, "agent-regression-refresh"),
            "source_refresh_result_reconciliation_packet": _packet_id(reconciliation_packet, "source-refresh-result-reconciliation"),
        },
        "guardrail_predicate_expectations": predicate_expectations,
        "affected_guardrail_bundle_ids": affected_bundle_ids,
        "rollback_notes": rollback_notes,
        "reviewer_owner_fields": _reviewer_owner_fields(process_packet, agent_packet, reconciliation_packet),
        "offline_validation_commands": _offline_validation_commands(process_packet, agent_packet, reconciliation_packet),
        "attestations": {key: True for key in REQUIRED_ATTESTATIONS},
    }

    validate_guardrail_refresh_regression_review_packet(packet)
    return deepcopy(packet)


def validate_guardrail_refresh_regression_review_packet(packet: Mapping[str, Any]) -> None:
    """Raise when a guardrail refresh regression review packet is invalid."""

    problems: list[str] = []
    if not isinstance(packet, Mapping):
        raise GuardrailRefreshRegressionReviewPacketError("packet must be an object")

    try:
        _reject_live_private_or_mutating_inputs(packet)
    except GuardrailRefreshRegressionReviewPacketError as exc:
        problems.append(str(exc))

    if packet.get("packet_type") != PACKET_TYPE:
        problems.append("packet_type must be " + PACKET_TYPE)
    if packet.get("packet_status") != "review_required_no_state_mutation":
        problems.append("packet_status must keep review blocked without state mutation")

    source_packet_ids = packet.get("source_packet_ids")
    if not isinstance(source_packet_ids, Mapping):
        problems.append("source_packet_ids must be an object")
    else:
        for key in REQUIRED_SOURCE_PACKET_KEYS:
            if not _text(source_packet_ids.get(key)):
                problems.append(f"source_packet_ids.{key} is required")

    expectations = _mapping_sequence(packet.get("guardrail_predicate_expectations"))
    if not expectations:
        problems.append("guardrail_predicate_expectations must be a non-empty list")
    for index, expectation in enumerate(expectations):
        path = f"guardrail_predicate_expectations[{index}]"
        if not _text(expectation.get("predicate_id")):
            problems.append(path + ".predicate_id is required")
        if expectation.get("expected_result") not in {"pass", "fail"}:
            problems.append(path + ".expected_result must be pass or fail")
        if not _string_list(expectation.get("source_evidence_ids")):
            problems.append(path + ".source_evidence_ids is required")
        if not _string_list(expectation.get("affected_guardrail_bundle_ids")):
            problems.append(path + ".affected_guardrail_bundle_ids is required")
        if not _text(expectation.get("reviewer_owner")):
            problems.append(path + ".reviewer_owner is required")

    if not _string_list(packet.get("affected_guardrail_bundle_ids")):
        problems.append("affected_guardrail_bundle_ids must be a non-empty list")
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
        raise GuardrailRefreshRegressionReviewPacketError("; ".join(problems))


def _predicate_expectations(
    process_packet: Mapping[str, Any],
    agent_packet: Mapping[str, Any],
    reconciliation_packet: Mapping[str, Any],
) -> list[dict[str, Any]]:
    expectations: list[dict[str, Any]] = []
    process_packet_id = _packet_id(process_packet, "process-guardrail-refresh-candidate")
    agent_packet_id = _packet_id(agent_packet, "agent-regression-refresh")
    reconciliation_packet_id = _packet_id(reconciliation_packet, "source-refresh-result-reconciliation")

    for index, delta in enumerate(_mapping_sequence(process_packet.get("candidate_guardrail_deltas")), start=1):
        predicate_id = _text(delta.get("predicate_id") or delta.get("guardrail_id") or delta.get("delta_id") or f"candidate-guardrail-delta-{index}")
        expected_result = "fail" if _text(delta.get("operation")).lower() in {"remove", "delete", "retire"} else "pass"
        expectations.append(
            {
                "expectation_id": f"candidate-guardrail-delta-{index}",
                "predicate_id": predicate_id,
                "expected_result": expected_result,
                "expectation_basis": _text(delta.get("summary")) or "Candidate guardrail delta remains fixture-review only.",
                "source_packet_id": process_packet_id,
                "source_evidence_ids": _string_list(delta.get("source_evidence_ids")),
                "affected_guardrail_bundle_ids": _bundle_ids_from_record(delta),
                "reviewer_owner": _first_owner(process_packet),
            }
        )

    for index, scenario in enumerate(_mapping_sequence(agent_packet.get("offline_user_scenarios")), start=1):
        scenario_id = _text(scenario.get("scenario_id") or f"agent-regression-scenario-{index}")
        evidence_ids = _citation_ids(scenario.get("cited_offline_evidence")) or [scenario_id]
        expectations.append(
            {
                "expectation_id": f"agent-regression-blocked-action-{index}",
                "predicate_id": "agent_regression_blocks_consequential_action." + scenario_id,
                "expected_result": "pass",
                "expectation_basis": _text(scenario.get("blocked_consequential_action_message")) or "Consequential actions remain blocked in offline regression review.",
                "source_packet_id": agent_packet_id,
                "source_evidence_ids": evidence_ids,
                "affected_guardrail_bundle_ids": _string_list(agent_packet.get("affected_guardrail_bundle_ids")) or _affected_guardrail_bundle_ids(process_packet, reconciliation_packet),
                "reviewer_owner": _text(scenario.get("reviewer_owner")) or _first_owner(agent_packet),
            }
        )

    for index, decision in enumerate(_mapping_sequence(reconciliation_packet.get("source_decisions")), start=1):
        source_id = _text(decision.get("source_id") or f"source-decision-{index}")
        decision_status = _text(decision.get("decision"))
        expectations.append(
            {
                "expectation_id": f"source-reconciliation-{index}",
                "predicate_id": "source_refresh_reconciliation." + source_id,
                "expected_result": "pass" if decision_status == "accepted" else "fail",
                "expectation_basis": "; ".join(_string_list(decision.get("decision_basis"))) or "Source refresh decision carried into regression review.",
                "source_packet_id": reconciliation_packet_id,
                "source_evidence_ids": _citation_ids(decision.get("citations")) or [source_id],
                "affected_guardrail_bundle_ids": _bundle_ids_from_record(decision),
                "reviewer_owner": _text(decision.get("reviewer_owner")) or _first_owner(reconciliation_packet),
            }
        )

    return sorted(expectations, key=lambda item: item["expectation_id"])


def _affected_guardrail_bundle_ids(process_packet: Mapping[str, Any], reconciliation_packet: Mapping[str, Any]) -> list[str]:
    bundle_ids: list[str] = []
    for delta in _mapping_sequence(process_packet.get("candidate_guardrail_deltas")):
        bundle_ids.extend(_bundle_ids_from_record(delta))
    for decision in _mapping_sequence(reconciliation_packet.get("source_decisions")):
        bundle_ids.extend(_bundle_ids_from_record(decision))
    bundle_ids.extend(_string_list(process_packet.get("affected_guardrail_bundle_ids")))
    bundle_ids.extend(_string_list(reconciliation_packet.get("affected_guardrail_bundle_ids")))
    return sorted(set(bundle_ids))


def _rollback_notes(
    process_packet: Mapping[str, Any],
    reconciliation_packet: Mapping[str, Any],
    affected_bundle_ids: Sequence[str],
) -> list[dict[str, Any]]:
    notes = list(_mapping_sequence(process_packet.get("rollback_notes")))
    notes.append(
        {
            "note_id": "rollback.keep-current-guardrail-bundles",
            "applies_to_guardrail_bundle_ids": list(affected_bundle_ids),
            "instruction": "Keep current guardrail bundles active until a separate human-reviewed promotion packet passes offline validation.",
            "source_packet_id": _packet_id(reconciliation_packet, "source-refresh-result-reconciliation"),
        }
    )
    notes.append(
        {
            "note_id": "rollback.discard-review-packet-on-failure",
            "applies_to_guardrail_bundle_ids": list(affected_bundle_ids),
            "instruction": "If any predicate expectation fails, discard this review packet and rebuild from committed fixtures only.",
            "source_packet_id": _packet_id(process_packet, "process-guardrail-refresh-candidate"),
        }
    )
    return notes


def _reviewer_owner_fields(
    process_packet: Mapping[str, Any],
    agent_packet: Mapping[str, Any],
    reconciliation_packet: Mapping[str, Any],
) -> list[dict[str, str]]:
    owners: dict[str, dict[str, str]] = {}

    for owner in _mapping_sequence(process_packet.get("reviewer_owner_fields")):
        owner_id = _text(owner.get("reviewer_owner_id") or owner.get("owner_id") or owner.get("reviewer_owner"))
        if owner_id:
            owners[owner_id] = {
                "reviewer_owner_id": owner_id,
                "role": _text(owner.get("role")) or "process_guardrail_refresh_reviewer",
                "source_packet_id": _packet_id(process_packet, "process-guardrail-refresh-candidate"),
            }

    agent_owners = agent_packet.get("reviewer_owner_fields")
    if isinstance(agent_owners, Mapping):
        for role, owner_id in agent_owners.items():
            text_owner = _text(owner_id)
            if text_owner:
                owners[text_owner] = {
                    "reviewer_owner_id": text_owner,
                    "role": _text(role),
                    "source_packet_id": _packet_id(agent_packet, "agent-regression-refresh"),
                }

    reconciliation_owner = _text(reconciliation_packet.get("reviewer_owner"))
    if reconciliation_owner:
        owners[reconciliation_owner] = {
            "reviewer_owner_id": reconciliation_owner,
            "role": "source_refresh_reconciliation_reviewer",
            "source_packet_id": _packet_id(reconciliation_packet, "source-refresh-result-reconciliation"),
        }

    return [owners[key] for key in sorted(owners)]


def _offline_validation_commands(*packets: Mapping[str, Any]) -> list[list[str]]:
    commands: list[list[str]] = [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]]
    for packet in packets:
        for key in ("offline_validation_commands", "expected_offline_validation_commands"):
            for command in _command_sequence(packet.get(key)):
                if command not in commands:
                    commands.append(command)
    return commands


def _bundle_ids_from_record(record: Mapping[str, Any]) -> list[str]:
    bundle_ids: list[str] = []
    for key in ("affected_guardrail_bundle_ids", "guardrail_bundle_ids", "guardrail_bundle_id", "active_guardrail_bundle_id"):
        bundle_ids.extend(_string_list(record.get(key)))
    if not bundle_ids:
        bundle_ids.extend(_string_list(record.get("affected_guardrail_ids")))
        bundle_ids.extend(_string_list(record.get("guardrail_ids")))
    return sorted(set(bundle_ids))


def _citation_ids(value: Any) -> list[str]:
    ids: list[str] = []
    for citation in _mapping_sequence(value):
        ids.extend(_string_list(citation.get("source_evidence_ids")))
        ids.extend(_string_list(citation.get("evidence_id")))
        ids.extend(_string_list(citation.get("href")))
        ids.extend(_string_list(citation.get("locator")))
        ids.extend(_string_list(citation.get("source_packet_id")))
    return sorted(set(ids))


def _reject_live_private_or_mutating_inputs(value: Any, key: str = "$") -> None:
    normalized_key = key.lower().replace("-", "_")
    if normalized_key in _MUTATION_KEYS and bool(value):
        raise GuardrailRefreshRegressionReviewPacketError(key + " must not enable mutation")
    if normalized_key in _LIVE_KEYS and bool(value):
        raise GuardrailRefreshRegressionReviewPacketError(key + " must not enable live execution")
    if isinstance(value, str) and any(marker in value for marker in _PRIVATE_MARKERS):
        raise GuardrailRefreshRegressionReviewPacketError(key + " must not reference private paths or browser artifacts")
    if isinstance(value, Mapping):
        for child_key, child_value in value.items():
            _reject_live_private_or_mutating_inputs(child_value, str(child_key))
    elif isinstance(value, list):
        for child in value:
            _reject_live_private_or_mutating_inputs(child, key)


def _first_owner(packet: Mapping[str, Any]) -> str:
    if _text(packet.get("reviewer_owner")):
        return _text(packet.get("reviewer_owner"))
    owner_fields = packet.get("reviewer_owner_fields")
    if isinstance(owner_fields, Mapping):
        for value in owner_fields.values():
            if _text(value):
                return _text(value)
    for owner in _mapping_sequence(owner_fields):
        owner_id = _text(owner.get("reviewer_owner_id") or owner.get("owner_id") or owner.get("reviewer_owner"))
        if owner_id:
            return owner_id
    return "PP&D guardrail refresh reviewer"


def _mapping(value: Any) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise GuardrailRefreshRegressionReviewPacketError("source packet entries must be objects")
    return value


def _mapping_sequence(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _command_sequence(value: Any) -> list[list[str]]:
    commands: list[list[str]] = []
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return commands
    for command in value:
        if isinstance(command, Sequence) and not isinstance(command, (str, bytes, bytearray)):
            parts = [_text(part) for part in command if _text(part)]
            if parts:
                commands.append(parts)
    return commands


def _string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value else []
    if isinstance(value, Mapping):
        return []
    if not isinstance(value, Sequence) or isinstance(value, (bytes, bytearray)):
        return [str(value)] if str(value) else []
    return [str(item).strip() for item in value if str(item).strip()]


def _packet_id(packet: Mapping[str, Any], fallback: str) -> str:
    return _text(packet.get("packet_id") or packet.get("id") or fallback)


def _text(value: Any) -> str:
    return str(value).strip() if value is not None else ""
