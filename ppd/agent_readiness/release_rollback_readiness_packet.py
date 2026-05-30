"""Fixture-first release rollback readiness packet support.

The packet produced here is an offline governance artifact. It consumes already
validated fixture packets and consolidates rollback prerequisites, owner
acknowledgements, blocked live-action boundaries, validation commands, and
non-mutation attestations before any release rollback could be considered.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any
from urllib.parse import parse_qsl, urlparse

from ppd.agent_readiness.offline_release_readiness_packet import validate_offline_release_readiness_packet
from ppd.agent_readiness.prompt_refresh_release_handoff_packet import validate_prompt_refresh_release_handoff_packet
from ppd.release.rollback_drill_outcome_review_packets import validate_release_rollback_drill_outcome_review_packet

PACKET_TYPE = "ppd.release_rollback_readiness_packet.v1"
PROMPT_HANDOFF_ROLE = "prompt_refresh_release_handoff_packet"
MONITORING_SMOKE_ROLE = "prompt_refresh_monitoring_smoke_transcript_packet"
ROLLBACK_OUTCOME_ROLE = "release_rollback_drill_outcome_review_packet"
OFFLINE_READINESS_ROLE = "offline_release_readiness_packet"

REQUIRED_SOURCE_ROLES = (
    PROMPT_HANDOFF_ROLE,
    MONITORING_SMOKE_ROLE,
    ROLLBACK_OUTCOME_ROLE,
    OFFLINE_READINESS_ROLE,
)

REQUIRED_ATTESTATIONS = (
    "no-live-release",
    "no-live-monitoring",
    "no-DevHub",
    "no-prompt",
    "no-guardrail",
    "no-release-state-mutation",
)

EXECUTION_BOUNDARIES = (
    "live_release",
    "live_monitoring",
    "devhub",
    "prompt_execution",
    "prompt_mutation",
    "guardrail_mutation",
    "release_state_mutation",
)

_MUTATION_TARGETS = (
    "prompt",
    "guardrail",
    "monitoring",
    "release_state",
    "releasestate",
    "source",
    "schedule",
    "agent_state",
    "agentstate",
)
_AUTH_QUERY_KEYS = {"token", "auth", "apikey", "api_key", "key", "session", "sid", "password", "signature"}
_FORBIDDEN_COMMAND_TOKENS = ("crawl", "crawler", "devhub", "monitor", "playwright", "scrape", "processor", "llm")
_PRIVATE_OR_RUNTIME_RE = re.compile(
    r"(auth[_-]?state|browser[_-]?state|cookie|credential|har|password|secret|session[_-]?state|token|trace\.zip|"
    r"/home/|/Users/|/tmp/|file://|raw[_-]?(?:body|crawl|download)|downloaded[_ -]?document|\.warc)",
    re.IGNORECASE,
)
_PRIVATE_FACT_RE = re.compile(
    r"\b(private|authenticated|account|user-owned|session|credential|secret|token)\s+(fact|facts|value|values|data|field|fields)\b",
    re.IGNORECASE,
)
_LIVE_EXECUTION_RE = re.compile(
    r"\b(live[_ -]?(release|monitoring|crawler|crawl|scrape)|devhub|llm|processor)\b.*\b(ran|run|executed|completed|enabled|called|invoked|published|released|rolled back|monitored)\b|"
    r"\b(ran|run|executed|completed|enabled|called|invoked|published|released|rolled back|monitored)\b.*\b(live[_ -]?(release|monitoring|crawler|crawl|scrape)|devhub|llm|processor)\b",
    re.IGNORECASE,
)
_LEGAL_GUARANTEE_RE = re.compile(
    r"\b(permit(?:ting)?\s+(?:approval|outcome)\s+(?:is\s+)?guaranteed|guarantees?\s+(?:permit|legal|approval|issuance)|"
    r"will\s+be\s+(?:approved|issued|legally\s+compliant)|legally\s+compliant|permit\s+approved)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ReleaseRollbackReadinessValidationResult:
    valid: bool
    problems: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {"valid": self.valid, "problems": list(self.problems)}


class ReleaseRollbackReadinessPacketError(ValueError):
    """Raised when a release rollback readiness packet is invalid."""


def build_release_rollback_readiness_packet(
    prompt_refresh_release_handoff_packet: Mapping[str, Any],
    prompt_refresh_monitoring_smoke_transcript_packet: Mapping[str, Any],
    release_rollback_drill_outcome_review_packet: Mapping[str, Any],
    offline_release_readiness_packet: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a side-effect-free release rollback readiness packet."""

    _require_valid_source_packets(
        prompt_refresh_release_handoff_packet,
        prompt_refresh_monitoring_smoke_transcript_packet,
        release_rollback_drill_outcome_review_packet,
        offline_release_readiness_packet,
    )
    consumed_packets = _consumed_packets(
        prompt_refresh_release_handoff_packet,
        prompt_refresh_monitoring_smoke_transcript_packet,
        release_rollback_drill_outcome_review_packet,
        offline_release_readiness_packet,
    )
    packet = {
        "packet_type": PACKET_TYPE,
        "packet_id": "fixture-first-release-rollback-readiness-packet",
        "fixture_first": True,
        "offline_only": True,
        "consumed_packets": consumed_packets,
        "rollback_prerequisites": _rollback_prerequisites(
            prompt_refresh_release_handoff_packet,
            prompt_refresh_monitoring_smoke_transcript_packet,
            release_rollback_drill_outcome_review_packet,
            offline_release_readiness_packet,
        ),
        "owner_acknowledgements": _owner_acknowledgements(
            prompt_refresh_release_handoff_packet,
            release_rollback_drill_outcome_review_packet,
            offline_release_readiness_packet,
        ),
        "blocked_live_action_boundaries": _blocked_live_action_boundaries(consumed_packets),
        "offline_validation_commands": _offline_validation_commands(
            prompt_refresh_release_handoff_packet,
            prompt_refresh_monitoring_smoke_transcript_packet,
            offline_release_readiness_packet,
        ),
        "attestations": {key: True for key in REQUIRED_ATTESTATIONS},
        "execution_boundaries": {key: False for key in EXECUTION_BOUNDARIES},
    }
    assert_valid_release_rollback_readiness_packet(packet)
    return packet


def validate_release_rollback_readiness_packet(packet: Mapping[str, Any]) -> ReleaseRollbackReadinessValidationResult:
    problems: list[str] = []
    if not isinstance(packet, Mapping):
        return ReleaseRollbackReadinessValidationResult(False, ("packet must be a mapping",))
    if packet.get("packet_type") != PACKET_TYPE:
        problems.append(f"packet_type must be {PACKET_TYPE}")
    if packet.get("fixture_first") is not True:
        problems.append("fixture_first must be true")
    if packet.get("offline_only") is not True:
        problems.append("offline_only must be true")

    consumed_roles = {str(item.get("packet_role")) for item in _mapping_sequence(packet.get("consumed_packets"))}
    for role in REQUIRED_SOURCE_ROLES:
        if role not in consumed_roles:
            problems.append(f"consumed_packets must include {role}")

    problems.extend(_cited_item_problems(packet.get("rollback_prerequisites"), "rollback_prerequisites", "prerequisite_id"))
    problems.extend(_acknowledgement_problems(packet.get("owner_acknowledgements")))
    problems.extend(_boundary_problems(packet.get("blocked_live_action_boundaries")))
    problems.extend(_command_problems(packet.get("offline_validation_commands")))
    problems.extend(_attestation_problems(packet.get("attestations")))
    problems.extend(_execution_boundary_problems(packet.get("execution_boundaries")))
    problems.extend(_recursive_safety_problems(packet))
    return ReleaseRollbackReadinessValidationResult(not problems, tuple(dict.fromkeys(problems)))


def assert_valid_release_rollback_readiness_packet(packet: Mapping[str, Any]) -> None:
    result = validate_release_rollback_readiness_packet(packet)
    if not result.valid:
        raise ReleaseRollbackReadinessPacketError("invalid_release_rollback_readiness_packet: " + "; ".join(result.problems))


def _require_valid_source_packets(
    prompt_handoff: Mapping[str, Any],
    smoke_transcript: Mapping[str, Any],
    outcome_review: Mapping[str, Any],
    offline_readiness: Mapping[str, Any],
) -> None:
    prompt_result = validate_prompt_refresh_release_handoff_packet(prompt_handoff)
    if not prompt_result.valid:
        raise ReleaseRollbackReadinessPacketError("invalid prompt refresh release handoff packet: " + "; ".join(prompt_result.problems))
    smoke_problems = _monitoring_smoke_transcript_problems(smoke_transcript)
    if smoke_problems:
        raise ReleaseRollbackReadinessPacketError("invalid prompt refresh monitoring smoke transcript packet: " + "; ".join(smoke_problems))
    outcome_result = validate_release_rollback_drill_outcome_review_packet(outcome_review)
    if not outcome_result.ok:
        raise ReleaseRollbackReadinessPacketError("invalid release rollback drill outcome review packet: " + "; ".join(outcome_result.errors))
    offline_result = validate_offline_release_readiness_packet(offline_readiness)
    if not offline_result.valid:
        raise ReleaseRollbackReadinessPacketError("invalid offline release readiness packet: " + "; ".join(offline_result.problems))


def _monitoring_smoke_transcript_problems(packet: Mapping[str, Any]) -> list[str]:
    problems: list[str] = []
    if packet.get("packet_type") != "fixture_first_prompt_refresh_monitoring_smoke_transcript_packet":
        problems.append("monitoring smoke transcript packet_type is invalid")
    if packet.get("mode") != "offline_fixture_only":
        problems.append("monitoring smoke transcript mode must be offline_fixture_only")
    if not _mapping_sequence(packet.get("consumes")):
        problems.append("monitoring smoke transcript must cite consumed packets")
    if not _mapping_sequence(packet.get("citation_catalog")):
        problems.append("monitoring smoke transcript must include citation_catalog")
    if not _mapping_sequence(packet.get("rollback_trigger_checks")):
        problems.append("monitoring smoke transcript must include rollback_trigger_checks")
    return problems


def _consumed_packets(prompt_handoff: Mapping[str, Any], smoke_transcript: Mapping[str, Any], outcome_review: Mapping[str, Any], offline_readiness: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [
        _consumed_packet(PROMPT_HANDOFF_ROLE, prompt_handoff, _collect_citations(prompt_handoff)),
        _consumed_packet(MONITORING_SMOKE_ROLE, smoke_transcript, _collect_citations(smoke_transcript)),
        _consumed_packet(ROLLBACK_OUTCOME_ROLE, outcome_review, _collect_citations(outcome_review)),
        _consumed_packet(OFFLINE_READINESS_ROLE, offline_readiness, _collect_citations(offline_readiness)),
    ]


def _consumed_packet(role: str, packet: Mapping[str, Any], citations: Sequence[str]) -> dict[str, Any]:
    return {
        "packet_role": role,
        "packet_id": str(packet.get("packet_id") or role),
        "required": True,
        "source_evidence_ids": list(citations) or [f"{role}.fixture"],
    }


def _rollback_prerequisites(prompt_handoff: Mapping[str, Any], smoke_transcript: Mapping[str, Any], outcome_review: Mapping[str, Any], offline_readiness: Mapping[str, Any]) -> list[dict[str, Any]]:
    prerequisites: list[dict[str, Any]] = []
    manifest = _mapping(prompt_handoff.get("candidate_prompt_version_manifest"))
    prerequisites.append({
        "prerequisite_id": "prompt-release-handoff-candidate-only",
        "source_packet_role": PROMPT_HANDOFF_ROLE,
        "required_state": "candidate prompt version is handoff-ready but not promoted",
        "source_evidence_ids": _strings(manifest.get("source_evidence_ids")) or _collect_citations(prompt_handoff),
    })
    for check in _mapping_sequence(smoke_transcript.get("rollback_trigger_checks")):
        prerequisites.append({
            "prerequisite_id": "monitoring-smoke-" + _slug(str(check.get("check_id") or "rollback-check")),
            "source_packet_role": MONITORING_SMOKE_ROLE,
            "required_state": str(check.get("required_action") or check.get("reason") or "rollback smoke check reviewed"),
            "source_evidence_ids": _strings(check.get("citation_ids")) or _collect_citations(smoke_transcript),
        })
    for threshold in _mapping_sequence(outcome_review.get("decision_thresholds")):
        prerequisites.append({
            "prerequisite_id": "outcome-threshold-" + _slug(str(threshold.get("threshold_id") or "decision-threshold")),
            "source_packet_role": ROLLBACK_OUTCOME_ROLE,
            "required_state": str(threshold.get("decision") or "rollback decision threshold reviewed"),
            "source_evidence_ids": _strings(threshold.get("source_evidence_ids")) or _strings(threshold.get("citation")) or _collect_citations(outcome_review),
        })
    for checkpoint in _mapping_sequence(offline_readiness.get("rollback_checkpoints")):
        prerequisites.append({
            "prerequisite_id": "offline-checkpoint-" + _slug(str(checkpoint.get("checkpoint_id") or checkpoint.get("candidate_id") or "rollback-checkpoint")),
            "source_packet_role": OFFLINE_READINESS_ROLE,
            "required_state": str(checkpoint.get("checkpoint") or "offline rollback checkpoint reviewed"),
            "source_evidence_ids": _strings(checkpoint.get("source_evidence_ids")) or _collect_citations(offline_readiness),
        })
    return prerequisites


def _owner_acknowledgements(prompt_handoff: Mapping[str, Any], outcome_review: Mapping[str, Any], offline_readiness: Mapping[str, Any]) -> list[dict[str, Any]]:
    acknowledgements: list[dict[str, Any]] = []
    rollback_owner = _mapping(prompt_handoff.get("rollback_owner"))
    acknowledgements.append({
        "acknowledgement_id": "prompt-handoff-rollback-owner",
        "owner": str(rollback_owner.get("owner_id") or "release-rollback-owner"),
        "role": str(rollback_owner.get("role") or "prompt_refresh_release_rollback_owner"),
        "acknowledgement_status": "required_before_live_release_or_rollback",
        "source_evidence_ids": _strings(rollback_owner.get("source_evidence_ids")) or _collect_citations(prompt_handoff),
    })
    owners = _mapping(outcome_review.get("reviewer_owner_fields"))
    for key in ("review_owner", "rollback_decision_reviewer", "follow_up_owner"):
        if owners.get(key):
            acknowledgements.append({
                "acknowledgement_id": "outcome-review-" + key.replace("_", "-"),
                "owner": str(owners[key]),
                "role": key,
                "acknowledgement_status": "required_before_live_release_or_rollback",
                "source_evidence_ids": _collect_citations(outcome_review),
            })
    for signoff in _mapping_sequence(offline_readiness.get("required_operator_signoffs")):
        acknowledgements.append({
            "acknowledgement_id": "offline-signoff-" + _slug(str(signoff.get("signoff_id") or signoff.get("role") or "operator")),
            "owner": str(signoff.get("role") or "offline_release_operator"),
            "role": str(signoff.get("role") or "offline_release_operator"),
            "acknowledgement_status": "required_before_live_release_or_rollback",
            "source_evidence_ids": _strings(signoff.get("source_evidence_ids")) or _collect_citations(offline_readiness),
        })
    return acknowledgements


def _blocked_live_action_boundaries(consumed_packets: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    citations = sorted({citation for packet in consumed_packets for citation in _strings(packet.get("source_evidence_ids"))})
    labels = {
        "no-live-release": "release publication and rollback execution remain blocked",
        "no-live-monitoring": "monitoring remains offline fixture review only",
        "no-DevHub": "DevHub browsing and authenticated automation remain blocked",
        "no-prompt": "prompt execution and prompt mutation remain blocked",
        "no-guardrail": "guardrail mutation and promotion remain blocked",
        "no-release-state-mutation": "release ledger and active release state writes remain blocked",
    }
    return [
        {
            "boundary_id": key,
            "blocked": True,
            "enabled": False,
            "required_human_action": labels[key],
            "source_evidence_ids": citations or ["release-rollback-readiness-fixture"],
        }
        for key in REQUIRED_ATTESTATIONS
    ]


def _offline_validation_commands(prompt_handoff: Mapping[str, Any], smoke_transcript: Mapping[str, Any], offline_readiness: Mapping[str, Any]) -> list[list[str]]:
    commands: list[list[str]] = []
    commands.extend(_commands(prompt_handoff.get("offline_validation_commands")))
    commands.extend(_commands(smoke_transcript.get("allowed_validation_commands")))
    commands.extend(_commands(offline_readiness.get("offline_validation_commands")))
    if not commands:
        commands.append(["python3", "ppd/daemon/ppd_daemon.py", "--self-test"])
    return _dedupe_commands(commands)


def _cited_item_problems(value: Any, field: str, id_key: str) -> list[str]:
    items = _mapping_sequence(value)
    if not items:
        return [f"{field} must be a non-empty list"]
    problems: list[str] = []
    for index, item in enumerate(items):
        if not str(item.get(id_key) or "").strip():
            problems.append(f"{field}[{index}] must include {id_key}")
        if not _strings(item.get("source_evidence_ids")):
            problems.append(f"{field}[{index}] must include source_evidence_ids")
    return problems


def _acknowledgement_problems(value: Any) -> list[str]:
    problems = _cited_item_problems(value, "owner_acknowledgements", "acknowledgement_id")
    for index, item in enumerate(_mapping_sequence(value)):
        if not str(item.get("owner") or "").strip():
            problems.append(f"owner_acknowledgements[{index}].owner is required")
        if not str(item.get("role") or "").strip():
            problems.append(f"owner_acknowledgements[{index}].role is required")
        if item.get("acknowledgement_status") != "required_before_live_release_or_rollback":
            problems.append(f"owner_acknowledgements[{index}].acknowledgement_status must be required_before_live_release_or_rollback")
    return problems


def _boundary_problems(value: Any) -> list[str]:
    items = _mapping_sequence(value)
    if not items:
        return ["blocked_live_action_boundaries must be a non-empty list"]
    problems: list[str] = []
    seen = {str(item.get("boundary_id")) for item in items}
    for required in REQUIRED_ATTESTATIONS:
        if required not in seen:
            problems.append(f"blocked_live_action_boundaries must include {required}")
    for index, item in enumerate(items):
        if item.get("blocked") is not True:
            problems.append(f"blocked_live_action_boundaries[{index}].blocked must be true")
        if item.get("enabled") is not False:
            problems.append(f"blocked_live_action_boundaries[{index}].enabled must be false")
        if not _strings(item.get("source_evidence_ids")):
            problems.append(f"blocked_live_action_boundaries[{index}] must include source_evidence_ids")
    return problems


def _command_problems(value: Any) -> list[str]:
    commands = _commands(value)
    if not commands:
        return ["offline_validation_commands must be a non-empty list of command arrays"]
    problems: list[str] = []
    for index, command in enumerate(commands):
        joined = " ".join(command).lower()
        if any(token in joined for token in _FORBIDDEN_COMMAND_TOKENS):
            problems.append(f"offline_validation_commands[{index}] contains a live-action command token")
    return problems


def _attestation_problems(value: Any) -> list[str]:
    if not isinstance(value, Mapping):
        return ["attestations must be an object"]
    return [f"attestations.{key} must be true" for key in REQUIRED_ATTESTATIONS if value.get(key) is not True]


def _execution_boundary_problems(value: Any) -> list[str]:
    if not isinstance(value, Mapping):
        return ["execution_boundaries must be an object"]
    return [f"execution_boundaries.{key} must be false" for key in EXECUTION_BOUNDARIES if value.get(key) is not False]


def _recursive_safety_problems(value: Any, path: str = "$") -> list[str]:
    problems: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if _is_active_mutation_flag(str(key), child):
                problems.append(f"active mutation flag is not allowed at {child_path}")
            problems.extend(_recursive_safety_problems(child, child_path))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            problems.extend(_recursive_safety_problems(child, f"{path}[{index}]"))
    elif isinstance(value, str):
        url_error = _url_like_error(value)
        if url_error:
            problems.append(f"private or authenticated URL/fact is not allowed at {path}: {url_error}")
        if _PRIVATE_OR_RUNTIME_RE.search(value) or _PRIVATE_FACT_RE.search(value):
            problems.append(f"private, authenticated, runtime, raw, or downloaded artifact reference is not allowed at {path}")
        if _LIVE_EXECUTION_RE.search(value):
            problems.append(f"live release, monitoring, DevHub, LLM, crawler, or processor execution claim is not allowed at {path}")
        if _LEGAL_GUARANTEE_RE.search(value):
            problems.append(f"legal or permitting outcome guarantee is not allowed at {path}")
    return problems


def _is_active_mutation_flag(key: str, value: Any) -> bool:
    normalized = re.sub(r"[^a-z0-9]+", "_", key.lower()).strip("_")
    if normalized.startswith("no_"):
        return False
    compact = normalized.replace("_", "")
    has_target = any(target in normalized or target in compact for target in _MUTATION_TARGETS)
    has_mutation = "mutation" in normalized or "mutate" in normalized or "mutated" in normalized
    has_active = normalized.startswith("active_") or normalized.endswith("_enabled") or normalized.endswith("_allowed") or normalized.endswith("_active")
    return bool(has_target and has_mutation and has_active and _active_value(value))


def _active_value(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"true", "yes", "enabled", "allowed", "active", "mutated"}
    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)
    return False


def _url_like_error(value: str) -> str | None:
    if not re.match(r"^[a-z][a-z0-9+.-]*://", value, re.IGNORECASE):
        return None
    parsed = urlparse(value)
    if parsed.username or parsed.password:
        return "authenticated URL credentials"
    for key, _ignored in parse_qsl(parsed.query, keep_blank_values=True):
        if key.lower() in _AUTH_QUERY_KEYS:
            return "authenticated URL query parameters"
    return None


def _collect_citations(value: Any) -> list[str]:
    citations: list[str] = []
    if isinstance(value, Mapping):
        for key in ("source_evidence_ids", "citation_ids", "evidence_ids"):
            citations.extend(_strings(value.get(key)))
        for key in ("source_evidence_id", "citation", "citation_id", "evidence_id"):
            citations.extend(_strings(value.get(key)))
        for child in value.values():
            citations.extend(_collect_citations(child))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for child in value:
            citations.extend(_collect_citations(child))
    return _dedupe(citations)


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _mapping_sequence(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [str(item).strip() for item in value if str(item).strip()]
    return []


def _commands(value: Any) -> list[list[str]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return []
    commands: list[list[str]] = []
    for command in value:
        if isinstance(command, Sequence) and not isinstance(command, (str, bytes, bytearray)):
            parts = [str(part).strip() for part in command if str(part).strip()]
            if parts:
                commands.append(parts)
    return commands


def _dedupe(values: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def _dedupe_commands(commands: Sequence[Sequence[str]]) -> list[list[str]]:
    seen: set[tuple[str, ...]] = set()
    result: list[list[str]] = []
    for command in commands:
        key = tuple(command)
        if key not in seen:
            seen.add(key)
            result.append(list(command))
    return result


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "item"


__all__ = [
    "PACKET_TYPE",
    "REQUIRED_ATTESTATIONS",
    "ReleaseRollbackReadinessPacketError",
    "ReleaseRollbackReadinessValidationResult",
    "assert_valid_release_rollback_readiness_packet",
    "build_release_rollback_readiness_packet",
    "validate_release_rollback_readiness_packet",
]
