"""Fixture-first PP&D post-release monitoring readiness packet assembly.

The compiler consumes committed packet metadata only. It does not crawl public
sources, open DevHub, prompt an agent, mutate guardrails, or write release
state.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from ppd.agent_readiness.post_release_monitoring_plan_validation import require_post_release_monitoring_plan
from ppd.agent_readiness.release_consumer_handoff_packet import require_release_consumer_handoff_packet

PACKET_TYPE = "ppd.post_release_monitoring_readiness_packet.v1"
REQUIRED_ATTESTATIONS = (
    "no-live-crawl",
    "no-DevHub",
    "no-prompt",
    "no-guardrail-mutation",
    "no-release-mutation",
)


@dataclass(frozen=True)
class PostReleaseMonitoringReadinessValidationResult:
    ready: bool
    problems: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {"ready": self.ready, "problems": list(self.problems)}


def build_post_release_monitoring_readiness_packet(packet: Mapping[str, Any]) -> dict[str, Any]:
    """Build a deterministic monitoring readiness packet from source packets."""

    monitoring_plan = _required_mapping(packet, "post_release_monitoring_plan")
    checklist = _required_mapping(packet, "offline_release_candidate_validation_checklist")
    handoff = _required_mapping(packet, "release_consumer_handoff_packet")

    require_post_release_monitoring_plan(monitoring_plan)
    require_release_consumer_handoff_packet(handoff)
    checklist_problems = _checklist_problems(checklist)
    if checklist_problems:
        raise ValueError("invalid_offline_release_candidate_validation_checklist: " + "; ".join(checklist_problems))

    reviewer_owner_fields = dict(_mapping(checklist.get("reviewer_owner_fields")))
    reviewer_owner_fields.update(_handoff_reviewer_owner_fields(handoff))

    compiled = {
        "packet_type": PACKET_TYPE,
        "packet_id": str(packet.get("packet_id") or "post-release-monitoring-readiness-fixture"),
        "source_packet_ids": _source_packet_ids(monitoring_plan, checklist, handoff),
        "fixture_first": True,
        "monitoring_checks": _compiled_monitoring_checks(monitoring_plan),
        "rollback_owner_contacts": _rollback_owner_contacts(checklist),
        "offline_validation_commands": _offline_validation_commands(packet),
        "reviewer_owner_fields": reviewer_owner_fields,
        "attestations": _compiled_attestations(checklist),
        "execution_boundaries": {
            "live_crawl": False,
            "devhub": False,
            "prompt": False,
            "guardrail_mutation": False,
            "release_mutation": False,
        },
    }
    require_post_release_monitoring_readiness_packet(compiled)
    return compiled


def validate_post_release_monitoring_readiness_packet(packet: Mapping[str, Any]) -> PostReleaseMonitoringReadinessValidationResult:
    problems: list[str] = []
    if packet.get("packet_type") != PACKET_TYPE:
        problems.append(f"packet_type must be {PACKET_TYPE}")
    if packet.get("fixture_first") is not True:
        problems.append("fixture_first must be true")

    for index, check in enumerate(_mapping_sequence(packet.get("monitoring_checks"))):
        path = f"monitoring_checks[{index}]"
        if not check.get("check_id"):
            problems.append(f"{path} lacks check_id")
        if not _text_list(check.get("source_evidence_ids")):
            problems.append(f"{path} lacks source_evidence_ids")
        if not check.get("reviewer_owner"):
            problems.append(f"{path} lacks reviewer_owner")
        if not check.get("escalation_note"):
            problems.append(f"{path} lacks escalation_note")
        if not isinstance(check.get("escalation_threshold"), Mapping) or not check.get("escalation_threshold"):
            problems.append(f"{path} lacks escalation_threshold")

    if not _mapping_sequence(packet.get("rollback_owner_contacts")):
        problems.append("rollback_owner_contacts must include at least one owner contact")
    for index, contact in enumerate(_mapping_sequence(packet.get("rollback_owner_contacts"))):
        if not contact.get("owner_id") or not contact.get("role"):
            problems.append(f"rollback_owner_contacts[{index}] lacks owner_id or role")

    commands = packet.get("offline_validation_commands")
    if not isinstance(commands, list) or not commands:
        problems.append("offline_validation_commands must be a non-empty list")
    else:
        for index, command in enumerate(commands):
            if not isinstance(command, list) or not command or not all(isinstance(part, str) and part for part in command):
                problems.append(f"offline_validation_commands[{index}] must be a non-empty string list")

    reviewer_owner_fields = _mapping(packet.get("reviewer_owner_fields"))
    for key in ("release_owner", "rollback_owner", "validation_reviewer"):
        if not reviewer_owner_fields.get(key):
            problems.append(f"reviewer_owner_fields lacks {key}")

    attestations = _mapping(packet.get("attestations"))
    for key in REQUIRED_ATTESTATIONS:
        if attestations.get(key) is not True:
            problems.append(f"required attestation must be true: {key}")

    boundaries = _mapping(packet.get("execution_boundaries"))
    for key in ("live_crawl", "devhub", "prompt", "guardrail_mutation", "release_mutation"):
        if boundaries.get(key) is not False:
            problems.append(f"execution boundary must be false: {key}")

    return PostReleaseMonitoringReadinessValidationResult(ready=not problems, problems=tuple(problems))


def require_post_release_monitoring_readiness_packet(packet: Mapping[str, Any]) -> None:
    result = validate_post_release_monitoring_readiness_packet(packet)
    if not result.ready:
        raise ValueError("invalid_post_release_monitoring_readiness_packet: " + "; ".join(result.problems))


def _compiled_monitoring_checks(monitoring_plan: Mapping[str, Any]) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for index, check in enumerate(_mapping_sequence(monitoring_plan.get("monitoring_checks"))):
        check_id = str(check.get("check_id") or f"monitoring-check-{index + 1}")
        checks.append(
            {
                "check_id": check_id,
                "description": str(check.get("description") or check_id),
                "source_evidence_ids": _evidence_ids(check),
                "reviewer_owner": str(check.get("reviewer_owner") or check.get("owner") or ""),
                "escalation_note": str(check.get("escalation_note") or check.get("escalation_path") or ""),
                "escalation_threshold": dict(_mapping(check.get("alert_threshold") or check.get("threshold"))),
                "source_packet_ref": str(monitoring_plan.get("packet_type") or "ppd.post_release_monitoring_plan.v1"),
            }
        )
    return checks


def _rollback_owner_contacts(checklist: Mapping[str, Any]) -> list[dict[str, str]]:
    owners = _mapping(checklist.get("reviewer_owner_fields"))
    contacts: list[dict[str, str]] = []
    for role in ("release_owner", "rollback_owner", "rollback_reviewer", "validation_reviewer"):
        owner_id = owners.get(role)
        if isinstance(owner_id, str) and owner_id:
            contacts.append({"role": role, "owner_id": owner_id, "contact_policy": "committed reviewer-owner id only"})
    return contacts


def _handoff_reviewer_owner_fields(handoff: Mapping[str, Any]) -> dict[str, str]:
    fields: dict[str, str] = {}
    for index, owner in enumerate(_mapping_sequence(handoff.get("reviewer_owners"))):
        owner_id = owner.get("owner_id") or owner.get("reviewer_owner_id") or owner.get("reviewer_id")
        if isinstance(owner_id, str) and owner_id:
            fields[f"release_consumer_reviewer_{index + 1}"] = owner_id
    return fields


def _compiled_attestations(checklist: Mapping[str, Any]) -> dict[str, bool]:
    raw = _mapping(checklist.get("attestations"))
    return {
        "no-live-crawl": raw.get("no_live_crawl") is True or raw.get("no-live-crawl") is True,
        "no-DevHub": raw.get("no_devhub") is True or raw.get("no-DevHub") is True,
        "no-prompt": raw.get("no_prompt") is True or raw.get("no-prompt") is True,
        "no-guardrail-mutation": raw.get("no_guardrail_mutation") is True or raw.get("no-guardrail-mutation") is True,
        "no-release-mutation": raw.get("no_release_mutation") is True or raw.get("no-release-mutation") is True,
    }


def _offline_validation_commands(packet: Mapping[str, Any]) -> list[list[str]]:
    raw = packet.get("offline_validation_commands")
    if isinstance(raw, list) and raw:
        commands: list[list[str]] = []
        for command in raw:
            if isinstance(command, list) and all(isinstance(part, str) and part for part in command):
                commands.append(list(command))
        if commands:
            return commands
    return [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]]


def _source_packet_ids(*packets: Mapping[str, Any]) -> list[str]:
    ids: list[str] = []
    for packet in packets:
        for key in ("packet_id", "checklist_id", "packet_type"):
            value = packet.get(key)
            if isinstance(value, str) and value:
                ids.append(value)
                break
    return ids


def _checklist_problems(checklist: Mapping[str, Any]) -> list[str]:
    problems: list[str] = []
    if checklist.get("final_decision") != "go":
        problems.append("offline release candidate checklist final_decision must be go")
    if not _mapping(checklist.get("reviewer_owner_fields")):
        problems.append("offline release candidate checklist lacks reviewer_owner_fields")
    if not _text_list(checklist.get("rollback_drill_refs")):
        problems.append("offline release candidate checklist lacks rollback_drill_refs")
    attestations = _compiled_attestations(checklist)
    for key in REQUIRED_ATTESTATIONS:
        if attestations.get(key) is not True:
            problems.append(f"offline release candidate checklist lacks true attestation: {key}")
    return problems


def _required_mapping(packet: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = packet.get(key)
    if not isinstance(value, Mapping):
        raise ValueError(f"packet field must be an object: {key}")
    return value


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _mapping_sequence(value: Any) -> list[Mapping[str, Any]]:
    if isinstance(value, Mapping):
        return [value]
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [item for item in value if isinstance(item, Mapping)]
    return []


def _text_list(value: Any) -> list[str]:
    if isinstance(value, str) and value:
        return [value]
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [item for item in value if isinstance(item, str) and item]
    return []


def _evidence_ids(record: Mapping[str, Any]) -> list[str]:
    for key in ("source_evidence_ids", "citation_ids", "evidence_ids"):
        refs = _text_list(record.get(key))
        if refs:
            return refs
    for key in ("source_evidence_id", "citation_id", "evidence_id"):
        ref = record.get(key)
        if isinstance(ref, str) and ref:
            return [ref]
    return []
