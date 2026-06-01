"""Inactive candidate rollback rehearsal packet v1 validation.

This packet is a committed fixture-only rehearsal contract. It validates that an
inactive candidate rollback rehearsal has the minimum references and review gates
needed to reason about rollback ordering without activating a release, crawling
live sources, touching DevHub, or carrying private/runtime artifacts.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

PACKET_TYPE = "ppd.inactive_candidate_rollback_rehearsal_packet.v1"
PACKET_VERSION = "v1"

REQUIRED_TOP_LEVEL_SEQUENCES = (
    "inactive_candidate_refs",
    "smoke_replay_refs",
    "rollback_triggers",
    "rollback_order",
    "evidence_preservation_checks",
    "reviewer_dispositions",
    "validation_commands",
)

ALLOWED_REVIEWER_DISPOSITIONS = {
    "pending_manual_review",
    "hold_for_stale_source",
    "hold_for_missing_evidence",
    "rejected_for_rehearsal_gap",
    "accepted_for_rehearsal_only",
}

FORBIDDEN_FIELD_RE = re.compile(
    r"(^|_)(auth|authenticated|browser|cookie|credential|download|downloaded|har|password|payment|private|raw|screenshot|session|storage_state|token|trace|warc)(_|$)",
    re.IGNORECASE,
)

FORBIDDEN_TEXT_RE = re.compile(
    r"(^file://)|(^/home/[^/]+/)|(^/Users/[^/]+/)|(^/tmp/)|"
    r"\b(auth state|browser state|cookie|credential|downloaded document|downloaded pdf|har file|password|private artifact|private file|private path|raw artifact|raw body|raw crawl|raw data|raw download|raw html|raw pdf|screenshot|session artifact|session state|storage state|token|trace\.zip|warc payload)\b|"
    r"\b(live crawl|live source crawl|crawl completed|devhub accessed|devhub session|live devhub|opened devhub|opened browser|browser automation completed)\b|"
    r"\b(activated release|activation completed|promoted release|promoted to active|promotion completed|release activation|release activated|release complete|release completed|release state updated|rollback activated|rollback applied|rollback completed)\b|"
    r"\b(certification completed|certified acknowledgement|official action completed|official action performed|paid fee|payment completed|scheduled inspection|submitted application|submitted permit|submitted payment|upload completed|uploaded corrections)\b",
    re.IGNORECASE,
)

ACTIVE_MUTATION_FIELD_RE = re.compile(
    r"(^|_)(active_)?(artifact|candidate|document|fixture|guardrail|process|prompt|release_state|source|surface)_(mutation|mutated|update|updated|write|written|promotion|promoted)(_|$)|"
    r"(^|_)(activates|applies|mutates|promotes|updates|writes)_(artifact|candidate|document|fixture|guardrail|process|prompt|release|release_state|source|surface|rollback)(_|$)",
    re.IGNORECASE,
)

COMMAND_FORBIDDEN_RE = re.compile(r"\b(live|crawl|devhub|playwright|browser|network|auth|session|download)\b", re.IGNORECASE)


@dataclass(frozen=True)
class InactiveCandidateRollbackRehearsalPacketV1Result:
    valid: bool
    problems: tuple[str, ...]


class InactiveCandidateRollbackRehearsalPacketV1Error(ValueError):
    def __init__(self, problems: Iterable[str]) -> None:
        self.problems = tuple(problems)
        super().__init__("invalid inactive candidate rollback rehearsal packet v1: " + "; ".join(self.problems))


def assert_valid_inactive_candidate_rollback_rehearsal_packet_v1(packet: Mapping[str, Any]) -> None:
    result = validate_inactive_candidate_rollback_rehearsal_packet_v1(packet)
    if not result.valid:
        raise InactiveCandidateRollbackRehearsalPacketV1Error(result.problems)


def validate_inactive_candidate_rollback_rehearsal_packet_v1(packet: Mapping[str, Any]) -> InactiveCandidateRollbackRehearsalPacketV1Result:
    problems: list[str] = []
    if not isinstance(packet, Mapping):
        return InactiveCandidateRollbackRehearsalPacketV1Result(False, ("packet must be an object",))

    if packet.get("packet_type") != PACKET_TYPE:
        problems.append(f"packet_type must be {PACKET_TYPE}")
    if packet.get("packet_version") != PACKET_VERSION:
        problems.append("packet_version must be v1")
    if packet.get("fixture_only") is not True:
        problems.append("fixture_only must be true")
    if packet.get("rollback_rehearsal_only") is not True:
        problems.append("rollback_rehearsal_only must be true")
    if packet.get("candidate_only") is not True:
        problems.append("candidate_only must be true")

    for field in REQUIRED_TOP_LEVEL_SEQUENCES:
        if not _non_empty_sequence(packet.get(field)):
            problems.append(f"{field} must be a non-empty list")

    if not _non_empty_sequence(packet.get("monitoring_outcome_refs")) and not _non_empty_sequence(packet.get("stale_source_hold_refs")):
        problems.append("monitoring_outcome_refs or stale_source_hold_refs must be a non-empty list")

    _validate_inactive_candidate_refs(packet, problems)
    _validate_smoke_replay_refs(packet, problems)
    _validate_monitoring_or_stale_refs(packet, problems)
    _validate_rollback_triggers(packet, problems)
    _validate_rollback_order(packet, problems)
    _validate_evidence_preservation_checks(packet, problems)
    _validate_reviewer_dispositions(packet, problems)
    _validate_validation_commands(packet.get("validation_commands"), "validation_commands", problems)
    _validate_cross_references(packet, problems)
    _validate_no_forbidden_payload(packet, problems)

    return InactiveCandidateRollbackRehearsalPacketV1Result(not problems, tuple(problems))


def _validate_inactive_candidate_refs(packet: Mapping[str, Any], problems: list[str]) -> None:
    for index, row in enumerate(_mapping_sequence(packet.get("inactive_candidate_refs"))):
        prefix = f"inactive_candidate_refs[{index}]"
        if not _text(row.get("candidate_ref")):
            problems.append(f"{prefix}.candidate_ref is required")
        if row.get("candidate_state") != "inactive_reference_only":
            problems.append(f"{prefix}.candidate_state must be inactive_reference_only")
        if row.get("active_candidate_mutation") is not False:
            problems.append(f"{prefix}.active_candidate_mutation must be false")
        if not _string_sequence(row.get("evidence_refs")):
            problems.append(f"{prefix}.evidence_refs must be a non-empty list")


def _validate_smoke_replay_refs(packet: Mapping[str, Any], problems: list[str]) -> None:
    for index, row in enumerate(_mapping_sequence(packet.get("smoke_replay_refs"))):
        prefix = f"smoke_replay_refs[{index}]"
        if not _text(row.get("smoke_replay_ref")):
            problems.append(f"{prefix}.smoke_replay_ref is required")
        if row.get("replay_mode") != "offline_fixture_only":
            problems.append(f"{prefix}.replay_mode must be offline_fixture_only")
        if row.get("passed") is not True:
            problems.append(f"{prefix}.passed must be true")
        if not _string_sequence(row.get("candidate_refs")):
            problems.append(f"{prefix}.candidate_refs must be a non-empty list")


def _validate_monitoring_or_stale_refs(packet: Mapping[str, Any], problems: list[str]) -> None:
    for index, row in enumerate(_mapping_sequence(packet.get("monitoring_outcome_refs"))):
        prefix = f"monitoring_outcome_refs[{index}]"
        if not _text(row.get("monitoring_outcome_ref")):
            problems.append(f"{prefix}.monitoring_outcome_ref is required")
        if row.get("outcome") not in {"clear_for_rehearsal", "hold_for_stale_source"}:
            problems.append(f"{prefix}.outcome must be clear_for_rehearsal or hold_for_stale_source")
        if not _string_sequence(row.get("source_refs")):
            problems.append(f"{prefix}.source_refs must be a non-empty list")

    for index, row in enumerate(_mapping_sequence(packet.get("stale_source_hold_refs"))):
        prefix = f"stale_source_hold_refs[{index}]"
        if not _text(row.get("stale_source_hold_ref")):
            problems.append(f"{prefix}.stale_source_hold_ref is required")
        if row.get("hold_state") != "manual_review_required":
            problems.append(f"{prefix}.hold_state must be manual_review_required")
        if not _string_sequence(row.get("source_refs")):
            problems.append(f"{prefix}.source_refs must be a non-empty list")


def _validate_rollback_triggers(packet: Mapping[str, Any], problems: list[str]) -> None:
    for index, row in enumerate(_mapping_sequence(packet.get("rollback_triggers"))):
        prefix = f"rollback_triggers[{index}]"
        if not _text(row.get("trigger_ref")):
            problems.append(f"{prefix}.trigger_ref is required")
        if row.get("trigger_state") != "rehearsal_only":
            problems.append(f"{prefix}.trigger_state must be rehearsal_only")
        if not _string_sequence(row.get("candidate_refs")):
            problems.append(f"{prefix}.candidate_refs must be a non-empty list")
        if not _text(row.get("reason")):
            problems.append(f"{prefix}.reason is required")


def _validate_rollback_order(packet: Mapping[str, Any], problems: list[str]) -> None:
    rows = _mapping_sequence(packet.get("rollback_order"))
    for index, row in enumerate(rows):
        prefix = f"rollback_order[{index}]"
        if row.get("sequence") != index + 1:
            problems.append(f"{prefix}.sequence must be {index + 1}")
        if not _text(row.get("trigger_ref")):
            problems.append(f"{prefix}.trigger_ref is required")
        if not _string_sequence(row.get("candidate_refs")):
            problems.append(f"{prefix}.candidate_refs must be a non-empty list")
        if row.get("rollback_state") != "rehearsal_only_no_active_rollback":
            problems.append(f"{prefix}.rollback_state must be rehearsal_only_no_active_rollback")
        if not _string_sequence(row.get("validation_command_refs")):
            problems.append(f"{prefix}.validation_command_refs must be a non-empty list")


def _validate_evidence_preservation_checks(packet: Mapping[str, Any], problems: list[str]) -> None:
    for index, row in enumerate(_mapping_sequence(packet.get("evidence_preservation_checks"))):
        prefix = f"evidence_preservation_checks[{index}]"
        if not _text(row.get("check_ref")):
            problems.append(f"{prefix}.check_ref is required")
        if not _text(row.get("evidence_ref")):
            problems.append(f"{prefix}.evidence_ref is required")
        if row.get("preserved") is not True:
            problems.append(f"{prefix}.preserved must be true")
        if row.get("private_artifacts_absent") is not True:
            problems.append(f"{prefix}.private_artifacts_absent must be true")
        if row.get("raw_artifacts_absent") is not True:
            problems.append(f"{prefix}.raw_artifacts_absent must be true")


def _validate_reviewer_dispositions(packet: Mapping[str, Any], problems: list[str]) -> None:
    for index, row in enumerate(_mapping_sequence(packet.get("reviewer_dispositions"))):
        prefix = f"reviewer_dispositions[{index}]"
        if not _text(row.get("reviewer_ref")):
            problems.append(f"{prefix}.reviewer_ref is required")
        if row.get("disposition") not in ALLOWED_REVIEWER_DISPOSITIONS:
            problems.append(f"{prefix}.disposition must be an allowed reviewer disposition")
        if not _string_sequence(row.get("candidate_refs")):
            problems.append(f"{prefix}.candidate_refs must be a non-empty list")
        if not _text(row.get("notes")):
            problems.append(f"{prefix}.notes is required")


def _validate_validation_commands(value: Any, path: str, problems: list[str]) -> None:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        problems.append(f"{path} must be a list of argv lists")
        return
    if not value:
        problems.append(f"{path} must be a non-empty list")
        return
    for index, command in enumerate(value):
        command_path = f"{path}[{index}]"
        if not _string_sequence(command):
            problems.append(f"{command_path} must be an argv string list")
            continue
        if COMMAND_FORBIDDEN_RE.search(" ".join(command)):
            problems.append(f"{command_path} must not invoke live crawl, DevHub, browser, network, auth, session, or download paths")


def _validate_cross_references(packet: Mapping[str, Any], problems: list[str]) -> None:
    candidate_refs = _ids_from_rows(packet.get("inactive_candidate_refs"), "candidate_ref")
    smoke_refs = _ids_from_rows(packet.get("smoke_replay_refs"), "smoke_replay_ref")
    trigger_refs = _ids_from_rows(packet.get("rollback_triggers"), "trigger_ref")
    command_refs = _command_refs(packet.get("validation_commands"))

    for key in ("smoke_replay_refs", "rollback_triggers", "rollback_order", "reviewer_dispositions"):
        for index, row in enumerate(_mapping_sequence(packet.get(key))):
            refs = set(_string_sequence(row.get("candidate_refs")))
            if refs and not refs.issubset(candidate_refs):
                problems.append(f"{key}[{index}].candidate_refs must reference inactive_candidate_refs")

    for index, row in enumerate(_mapping_sequence(packet.get("rollback_order"))):
        trigger_ref = _text(row.get("trigger_ref"))
        if trigger_ref and trigger_ref not in trigger_refs:
            problems.append(f"rollback_order[{index}].trigger_ref must reference rollback_triggers")
        refs = set(_string_sequence(row.get("validation_command_refs")))
        if refs and not refs.issubset(command_refs):
            problems.append(f"rollback_order[{index}].validation_command_refs must reference validation_commands")

    for index, row in enumerate(_mapping_sequence(packet.get("evidence_preservation_checks"))):
        evidence_ref = _text(row.get("evidence_ref"))
        if evidence_ref and evidence_ref not in candidate_refs and evidence_ref not in smoke_refs:
            problems.append(f"evidence_preservation_checks[{index}].evidence_ref must reference inactive candidate or smoke replay evidence")


def _validate_no_forbidden_payload(packet: Mapping[str, Any], problems: list[str]) -> None:
    for path, key, value in _walk(packet):
        normalized_key = key.lower().replace("-", "_")
        if ACTIVE_MUTATION_FIELD_RE.search(normalized_key) and _active_value(value):
            problems.append(f"{path} must not contain active mutation flags")
        if FORBIDDEN_FIELD_RE.search(normalized_key) and _present_value(value):
            problems.append(f"{path} must not include private, session, browser, raw, downloaded, payment, or trace artifacts")
        if isinstance(value, str) and FORBIDDEN_TEXT_RE.search(value):
            problems.append(f"{path} must not claim private artifacts, live crawl or DevHub access, release activation, promotion, rollback completion, or official-action completion")


def _ids_from_rows(value: Any, field: str) -> set[str]:
    return {_text(row.get(field)) for row in _mapping_sequence(value) if _text(row.get(field))}


def _command_refs(value: Any) -> set[str]:
    refs: set[str] = set()
    for index, command in enumerate(value if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)) else []):
        if isinstance(command, Mapping):
            command_ref = _text(command.get("command_ref"))
            if command_ref:
                refs.add(command_ref)
        elif _string_sequence(command):
            refs.add(f"validation-command-{index + 1}")
    return refs


def _walk(value: Any, prefix: str = "packet", key: str = "packet") -> Iterable[tuple[str, str, Any]]:
    if isinstance(value, Mapping):
        for child_key, child_value in value.items():
            child_key_text = str(child_key)
            child_path = f"{prefix}.{child_key_text}"
            yield child_path, child_key_text, child_value
            yield from _walk(child_value, child_path, child_key_text)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child_value in enumerate(value):
            child_path = f"{prefix}[{index}]"
            yield child_path, key, child_value
            yield from _walk(child_value, child_path, key)


def _mapping_sequence(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _non_empty_sequence(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)) and bool(value)


def _string_sequence(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _present_value(value: Any) -> bool:
    if value is None or value is False:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, Mapping):
        return bool(value)
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return bool(value)
    return True


def _active_value(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"1", "active", "enabled", "true", "yes"}
    if isinstance(value, Mapping):
        return bool(value)
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return bool(value)
    return False
