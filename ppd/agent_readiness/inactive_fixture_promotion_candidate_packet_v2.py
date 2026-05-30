"""Inactive fixture promotion candidate packet v2 validation.

The packet is a fixture-first, metadata-only candidate. It must describe reviewable
inactive fixture promotion rows without applying them, storing private artifacts,
claiming live execution, or implying legal/permitting outcomes.
"""

from __future__ import annotations

import json
import re
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PACKET_TYPE = "ppd.inactive_fixture_promotion_candidate_packet.v2"
PACKET_VERSION = "v2"
VALIDATION_COMMANDS = [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]]

REQUIRED_TOP_LEVEL_SEQUENCES = (
    "promotion_candidate_rows",
    "fixture_family_ownership_assignments",
    "prerequisite_validation_replay_inventory",
    "reviewer_approval_placeholders",
    "rollback_plan_references",
    "validation_commands",
)

REQUIRED_CANDIDATE_ROW_FIELDS = (
    "candidate_id",
    "fixture_family",
    "candidate_fixture_path",
    "source_evidence_ids",
    "owner_assignment_ref",
    "prerequisite_validation_ref",
    "reviewer_approval_placeholder_ref",
    "no_go_reason",
    "rollback_plan_ref",
    "validation_commands",
)

REQUIRED_OWNERSHIP_FIELDS = (
    "assignment_id",
    "fixture_family",
    "reviewer_owner",
    "ownership_status",
)

REQUIRED_REPLAY_FIELDS = (
    "validation_ref",
    "command",
    "expected_result",
)

REQUIRED_REVIEWER_FIELDS = (
    "placeholder_id",
    "candidate_id",
    "approval_status",
    "reviewer",
    "reviewed_at",
    "notes",
)

REQUIRED_ROLLBACK_FIELDS = (
    "rollback_plan_ref",
    "candidate_id",
    "rollback_status",
    "plan_summary",
)

MUTATION_FLAGS = {
    "active_artifact_mutation",
    "active_prompt_mutation",
    "active_release_state_mutation",
    "active_fixture_mutation",
    "active_agent_state_mutation",
    "active_artifact_mutated",
    "active_prompt_mutated",
    "active_release_state_mutated",
    "active_fixture_mutated",
    "active_agent_state_mutated",
    "artifact_mutation",
    "prompt_mutation",
    "release_state_mutation",
    "fixture_mutation",
    "agent_state_mutation",
    "promotion_executed",
    "fixture_promoted",
}

PRIVATE_OR_RAW_KEY_RE = re.compile(
    r"(^|_)(access[_-]?token|auth|authenticated|browser|cookie|credential|devhub[_-]?session|download|har|local[_-]?private[_-]?path|password|payment|private|raw|screenshot|session|storage[_-]?state|token|trace|warc|pdf[_-]?(bytes|download|raw)?)(_|$)",
    re.IGNORECASE,
)

PRIVATE_OR_RAW_VALUE_RE = re.compile(
    r"(auth state|authenticated artifact|browser artifact|browser state|cookie jar|downloaded data|downloaded document|downloaded pdf|har file|playwright trace|private devhub session|raw body|raw crawl|raw html|raw pdf|session storage|storage state|warc payload|/(tmp|private|var/folders|home)/|\\users\\|\.har$|\.warc(\.gz)?$)",
    re.IGNORECASE,
)

LIVE_OR_PROMOTION_RE = re.compile(
    r"(live execution completed|live execution|live crawl completed|live crawl|promotion complete|promotion completed|promoted to active|fixture promoted|release state updated|applied to active)",
    re.IGNORECASE,
)

OUTCOME_GUARANTEE_RE = re.compile(
    r"(approval guaranteed|guaranteed approval|guarantee approval|permit guaranteed|permit will be approved|permit will issue|legally compliant|legal advice|legal outcome guaranteed|no legal risk|cannot be denied)",
    re.IGNORECASE,
)

CONSEQUENTIAL_ACTION_RE = re.compile(
    r"(agent will submit|automation will submit|certify acknowledgement|certify the application|click pay|click submit|enter payment|execute payment|make official changes|pay fees|purchase permit|purchase trade permit|schedule inspection|submit payment|submit permit|submit the application|upload correction|upload corrections|upload to devhub|withdraw permit|cancel permit)",
    re.IGNORECASE,
)

EVIDENCE_PREFIXES = (
    "source:",
    "citation:",
    "fixture-source:",
    "observation:",
    "official-source:",
)


@dataclass(frozen=True)
class InactiveFixturePromotionCandidatePacketV2ValidationResult:
    valid: bool
    problems: tuple[str, ...]


class InactiveFixturePromotionCandidatePacketV2Error(ValueError):
    def __init__(self, problems: Iterable[str]) -> None:
        self.problems = tuple(problems)
        super().__init__("invalid inactive fixture promotion candidate packet v2: " + "; ".join(self.problems))


def load_inactive_fixture_promotion_candidate_packet_v2(path: str | Path) -> dict[str, Any]:
    loaded = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError("inactive fixture promotion candidate packet v2 fixture must be a JSON object")
    assert_valid_inactive_fixture_promotion_candidate_packet_v2(loaded)
    return loaded


def assert_valid_inactive_fixture_promotion_candidate_packet_v2(packet: Mapping[str, Any]) -> None:
    result = validate_inactive_fixture_promotion_candidate_packet_v2(packet)
    if not result.valid:
        raise InactiveFixturePromotionCandidatePacketV2Error(result.problems)


def validate_inactive_fixture_promotion_candidate_packet_v2(
    packet: Mapping[str, Any],
) -> InactiveFixturePromotionCandidatePacketV2ValidationResult:
    problems: list[str] = []
    if not isinstance(packet, Mapping):
        return InactiveFixturePromotionCandidatePacketV2ValidationResult(False, ("packet must be an object",))

    if packet.get("packet_type") != PACKET_TYPE:
        problems.append(f"packet_type must be {PACKET_TYPE}")
    if packet.get("packet_version") != PACKET_VERSION:
        problems.append("packet_version must be v2")
    if packet.get("fixture_first") is not True:
        problems.append("fixture_first must be true")
    if packet.get("metadata_only") is not True:
        problems.append("metadata_only must be true")
    if packet.get("candidate_only") is not True:
        problems.append("candidate_only must be true")

    for key in REQUIRED_TOP_LEVEL_SEQUENCES:
        if not _non_empty_sequence(packet.get(key)):
            problems.append(f"{key} must be a non-empty list")

    if packet.get("validation_commands") != VALIDATION_COMMANDS:
        problems.append("validation_commands must contain the PP&D daemon self-test command")

    _validate_candidate_rows(packet.get("promotion_candidate_rows"), problems)
    _validate_ownership_assignments(packet.get("fixture_family_ownership_assignments"), problems)
    _validate_replay_inventory(packet.get("prerequisite_validation_replay_inventory"), problems)
    _validate_reviewer_placeholders(packet.get("reviewer_approval_placeholders"), problems)
    _validate_rollback_references(packet.get("rollback_plan_references"), problems)
    _validate_cross_references(packet, problems)
    _validate_no_forbidden_payload(packet, problems)
    return InactiveFixturePromotionCandidatePacketV2ValidationResult(not problems, tuple(problems))


def _validate_candidate_rows(value: Any, problems: list[str]) -> None:
    rows = _mapping_sequence(value)
    if not rows:
        return
    seen_ids: set[str] = set()
    for index, row in enumerate(rows):
        prefix = f"promotion_candidate_rows[{index}]"
        for field in REQUIRED_CANDIDATE_ROW_FIELDS:
            if field not in row:
                problems.append(f"{prefix}.{field} is required")
        candidate_id = _text(row.get("candidate_id"))
        if candidate_id in seen_ids:
            problems.append(f"{prefix}.candidate_id must be unique")
        if candidate_id:
            seen_ids.add(candidate_id)
        fixture_path = _text(row.get("candidate_fixture_path"))
        if fixture_path and not fixture_path.startswith("ppd/tests/fixtures/"):
            problems.append(f"{prefix}.candidate_fixture_path must stay under ppd/tests/fixtures")
        if not _cited_evidence_list(row.get("source_evidence_ids")):
            problems.append(f"{prefix}.source_evidence_ids must cite fixture/source evidence")
        if not _text(row.get("no_go_reason")):
            problems.append(f"{prefix}.no_go_reason is required")
        if row.get("validation_commands") != VALIDATION_COMMANDS:
            problems.append(f"{prefix}.validation_commands must contain the PP&D daemon self-test command")
        if row.get("candidate_status") not in {None, "inactive_candidate_only", "blocked_pending_review", "no_go"}:
            problems.append(f"{prefix}.candidate_status must remain inactive or blocked")


def _validate_ownership_assignments(value: Any, problems: list[str]) -> None:
    rows = _mapping_sequence(value)
    if not rows:
        return
    for index, row in enumerate(rows):
        prefix = f"fixture_family_ownership_assignments[{index}]"
        for field in REQUIRED_OWNERSHIP_FIELDS:
            if not _text(row.get(field)):
                problems.append(f"{prefix}.{field} is required")
        if _text(row.get("ownership_status")) not in {"assigned_pending_manual_review", "assigned"}:
            problems.append(f"{prefix}.ownership_status must assign a fixture-family reviewer")


def _validate_replay_inventory(value: Any, problems: list[str]) -> None:
    rows = _mapping_sequence(value)
    if not rows:
        return
    for index, row in enumerate(rows):
        prefix = f"prerequisite_validation_replay_inventory[{index}]"
        for field in REQUIRED_REPLAY_FIELDS:
            if field == "command":
                if not _string_sequence(row.get(field)):
                    problems.append(f"{prefix}.command must be a command list")
            elif not _text(row.get(field)):
                problems.append(f"{prefix}.{field} is required")
        if row.get("command") != VALIDATION_COMMANDS[0]:
            problems.append(f"{prefix}.command must replay the PP&D daemon self-test")


def _validate_reviewer_placeholders(value: Any, problems: list[str]) -> None:
    rows = _mapping_sequence(value)
    if not rows:
        return
    for index, row in enumerate(rows):
        prefix = f"reviewer_approval_placeholders[{index}]"
        for field in REQUIRED_REVIEWER_FIELDS:
            if field not in row:
                problems.append(f"{prefix}.{field} is required")
        if row.get("approval_status") != "pending_manual_review":
            problems.append(f"{prefix}.approval_status must be pending_manual_review")


def _validate_rollback_references(value: Any, problems: list[str]) -> None:
    rows = _mapping_sequence(value)
    if not rows:
        return
    for index, row in enumerate(rows):
        prefix = f"rollback_plan_references[{index}]"
        for field in REQUIRED_ROLLBACK_FIELDS:
            if not _text(row.get(field)):
                problems.append(f"{prefix}.{field} is required")
        if _text(row.get("rollback_status")) != "ready_no_active_changes":
            problems.append(f"{prefix}.rollback_status must be ready_no_active_changes")


def _validate_cross_references(packet: Mapping[str, Any], problems: list[str]) -> None:
    candidates = _mapping_sequence(packet.get("promotion_candidate_rows"))
    assignments = {_text(row.get("assignment_id")) for row in _mapping_sequence(packet.get("fixture_family_ownership_assignments"))}
    replays = {_text(row.get("validation_ref")) for row in _mapping_sequence(packet.get("prerequisite_validation_replay_inventory"))}
    reviewers = {_text(row.get("placeholder_id")) for row in _mapping_sequence(packet.get("reviewer_approval_placeholders"))}
    rollbacks = {_text(row.get("rollback_plan_ref")) for row in _mapping_sequence(packet.get("rollback_plan_references"))}
    for index, row in enumerate(candidates):
        prefix = f"promotion_candidate_rows[{index}]"
        if _text(row.get("owner_assignment_ref")) not in assignments:
            problems.append(f"{prefix}.owner_assignment_ref must reference fixture_family_ownership_assignments")
        if _text(row.get("prerequisite_validation_ref")) not in replays:
            problems.append(f"{prefix}.prerequisite_validation_ref must reference prerequisite_validation_replay_inventory")
        if _text(row.get("reviewer_approval_placeholder_ref")) not in reviewers:
            problems.append(f"{prefix}.reviewer_approval_placeholder_ref must reference reviewer_approval_placeholders")
        if _text(row.get("rollback_plan_ref")) not in rollbacks:
            problems.append(f"{prefix}.rollback_plan_ref must reference rollback_plan_references")


def _validate_no_forbidden_payload(packet: Mapping[str, Any], problems: list[str]) -> None:
    for path, key, value in _walk(packet):
        normalized_key = key.lower().replace("-", "_")
        if normalized_key in MUTATION_FLAGS and value is not False:
            problems.append(f"{path} must be false")
        if value is True and normalized_key.startswith("active_") and any(token in normalized_key for token in ("artifact", "prompt", "release_state", "fixture", "agent_state")):
            problems.append(f"{path} must not set active mutation flags")
        if PRIVATE_OR_RAW_KEY_RE.search(normalized_key) and _truthy(value):
            problems.append(f"{path} must not include private, authenticated, session, browser, raw crawl, PDF, or downloaded artifacts")
        if isinstance(value, str):
            if PRIVATE_OR_RAW_VALUE_RE.search(value):
                problems.append(f"{path} must not reference private, authenticated, session, browser, raw crawl, PDF, or downloaded artifacts")
            if LIVE_OR_PROMOTION_RE.search(value):
                problems.append(f"{path} must not claim live execution or promotion completion")
            if OUTCOME_GUARANTEE_RE.search(value):
                problems.append(f"{path} must not guarantee legal or permitting outcomes")
            if CONSEQUENTIAL_ACTION_RE.search(value):
                problems.append(f"{path} must not include consequential action language")


def _walk(value: Any, prefix: str = "packet", key: str = "packet") -> Iterable[tuple[str, str, Any]]:
    if isinstance(value, Mapping):
        for child_key, child_value in value.items():
            child_key_text = str(child_key)
            child_path = f"{prefix}.{child_key_text}"
            yield child_path, child_key_text, child_value
            yield from _walk(child_value, child_path, child_key_text)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child_value in enumerate(value):
            child_path = f"{prefix}[{index}]"
            yield child_path, key, child_value
            yield from _walk(child_value, child_path, key)


def _mapping_sequence(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _non_empty_sequence(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes)) and bool(value)


def _string_sequence(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [item for item in value if isinstance(item, str) and item]


def _cited_evidence_list(value: Any) -> list[str]:
    return [item for item in _string_sequence(value) if item.lower().startswith(EVIDENCE_PREFIXES)]


def _truthy(value: Any) -> bool:
    if value is None or value is False or value == "":
        return False
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)) and not value:
        return False
    if isinstance(value, Mapping) and not value:
        return False
    return True


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""
