"""Inactive promotion sandbox rehearsal packet v1 validation.

This packet is an offline, metadata-only rehearsal record for reviewing an
inactive promotion candidate in a synthetic sandbox. It must prove that the
rehearsal described apply steps, fixture-family inventory, pre/post validation,
rollback rehearsal, no-main-worktree-change notes, and reviewer placeholders
without storing private artifacts or claiming that anything was applied live.
"""

from __future__ import annotations

import json
import re
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PACKET_TYPE = "ppd.inactive_promotion_sandbox_rehearsal_packet.v1"
PACKET_VERSION = "v1"
VALIDATION_COMMANDS = [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]]

REQUIRED_TOP_LEVEL_SEQUENCES = (
    "synthetic_sandbox_apply_steps",
    "expected_changed_fixture_family_inventory",
    "pre_apply_validation_commands",
    "post_apply_validation_commands",
    "rollback_rehearsal_commands",
    "no_main_worktree_change_notes",
    "reviewer_signoff_placeholders",
)

REQUIRED_APPLY_STEP_FIELDS = (
    "step_id",
    "fixture_family",
    "synthetic_action",
    "expected_result",
)

REQUIRED_INVENTORY_FIELDS = (
    "fixture_family",
    "expected_changed_paths",
    "change_reason",
)

REQUIRED_COMMAND_FIELDS = (
    "command_id",
    "command",
    "expected_result",
)

REQUIRED_NOTE_FIELDS = (
    "note_id",
    "statement",
)

REQUIRED_SIGNOFF_FIELDS = (
    "placeholder_id",
    "reviewer_role",
    "status",
    "disposition",
)

ACTIVE_MUTATION_FLAGS = {
    "active_artifact_mutation",
    "active_artifact_mutated",
    "active_prompt_mutation",
    "active_prompt_mutated",
    "active_release_state_mutation",
    "active_release_state_mutated",
    "active_fixture_mutation",
    "active_fixture_mutated",
    "active_agent_state_mutation",
    "active_agent_state_mutated",
    "artifact_mutation",
    "prompt_mutation",
    "release_state_mutation",
    "fixture_mutation",
    "agent_state_mutation",
}

PRIVATE_OR_RAW_KEY_RE = re.compile(
    r"(^|_)(access[_-]?token|auth|authenticated|browser|cookie|credential|devhub[_-]?session|download|har|local[_-]?private[_-]?path|password|payment|private|raw|screenshot|session|storage[_-]?state|token|trace|warc|pdf[_-]?(bytes|download|raw)?)(_|$)",
    re.IGNORECASE,
)

PRIVATE_OR_RAW_VALUE_RE = re.compile(
    r"(auth state|authenticated artifact|browser artifact|browser state|cookie jar|downloaded data|downloaded document|downloaded pdf|har file|playwright trace|private devhub session|raw body|raw crawl|raw html|raw pdf|session storage|storage state|warc payload|/(tmp|private|var/folders|home)/|\\users\\|\.har$|\.warc(\.gz)?$)",
    re.IGNORECASE,
)

LIVE_OR_APPLIED_RE = re.compile(
    r"(applied to active|applied to main worktree|fixture promoted|live crawl|live execution|main worktree applied|promotion complete|promotion completed|release complete|release completed|release state updated)",
    re.IGNORECASE,
)

OUTCOME_GUARANTEE_RE = re.compile(
    r"(approval guaranteed|cannot be denied|guarantee approval|guaranteed approval|legal advice|legal outcome guaranteed|legally compliant|no legal risk|permit guaranteed|permit will be approved|permit will issue)",
    re.IGNORECASE,
)

CONSEQUENTIAL_ACTION_RE = re.compile(
    r"(agent will submit|automation will submit|cancel permit|certify acknowledgement|certify the application|click pay|click submit|enter payment|execute payment|make official changes|pay fees|purchase permit|purchase trade permit|schedule inspection|submit payment|submit permit|submit the application|upload correction|upload corrections|upload to devhub|withdraw permit)",
    re.IGNORECASE,
)

NEGATED_ACTION_RE = re.compile(
    r"\b(block|blocked|blocks|do not|does not|must not|no|not|refuse|refused|remain blocked|remains blocked)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class InactivePromotionSandboxRehearsalPacketV1ValidationResult:
    valid: bool
    problems: tuple[str, ...]


class InactivePromotionSandboxRehearsalPacketV1Error(ValueError):
    """Raised when an inactive promotion sandbox rehearsal packet is unsafe."""

    def __init__(self, problems: Iterable[str]) -> None:
        self.problems = tuple(problems)
        super().__init__("invalid inactive promotion sandbox rehearsal packet v1: " + "; ".join(self.problems))


def load_inactive_promotion_sandbox_rehearsal_packet_v1(path: str | Path) -> dict[str, Any]:
    loaded = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError("inactive promotion sandbox rehearsal packet v1 fixture must be a JSON object")
    assert_valid_inactive_promotion_sandbox_rehearsal_packet_v1(loaded)
    return loaded


def assert_valid_inactive_promotion_sandbox_rehearsal_packet_v1(packet: Mapping[str, Any]) -> None:
    result = validate_inactive_promotion_sandbox_rehearsal_packet_v1(packet)
    if not result.valid:
        raise InactivePromotionSandboxRehearsalPacketV1Error(result.problems)


def validate_inactive_promotion_sandbox_rehearsal_packet_v1(
    packet: Mapping[str, Any],
) -> InactivePromotionSandboxRehearsalPacketV1ValidationResult:
    problems: list[str] = []
    if not isinstance(packet, Mapping):
        return InactivePromotionSandboxRehearsalPacketV1ValidationResult(False, ("packet must be an object",))

    if packet.get("packet_type") != PACKET_TYPE:
        problems.append(f"packet_type must be {PACKET_TYPE}")
    if packet.get("packet_version") != PACKET_VERSION:
        problems.append("packet_version must be v1")
    if packet.get("fixture_first") is not True:
        problems.append("fixture_first must be true")
    if packet.get("metadata_only") is not True:
        problems.append("metadata_only must be true")
    if packet.get("sandbox_rehearsal_only") is not True:
        problems.append("sandbox_rehearsal_only must be true")
    if packet.get("validation_commands") != VALIDATION_COMMANDS:
        problems.append("validation_commands must contain the PP&D daemon self-test command")

    for key in REQUIRED_TOP_LEVEL_SEQUENCES:
        if not _non_empty_sequence(packet.get(key)):
            problems.append(f"{key} must be a non-empty list")

    _validate_apply_steps(packet.get("synthetic_sandbox_apply_steps"), problems)
    _validate_inventory(packet.get("expected_changed_fixture_family_inventory"), problems)
    _validate_command_rows(packet.get("pre_apply_validation_commands"), "pre_apply_validation_commands", problems)
    _validate_command_rows(packet.get("post_apply_validation_commands"), "post_apply_validation_commands", problems)
    _validate_command_rows(packet.get("rollback_rehearsal_commands"), "rollback_rehearsal_commands", problems)
    _validate_no_main_worktree_notes(packet.get("no_main_worktree_change_notes"), problems)
    _validate_signoff_placeholders(packet.get("reviewer_signoff_placeholders"), problems)
    _validate_no_forbidden_payload(packet, problems)
    return InactivePromotionSandboxRehearsalPacketV1ValidationResult(not problems, tuple(problems))


def _validate_apply_steps(value: Any, problems: list[str]) -> None:
    rows = _mapping_sequence(value)
    if not rows:
        return
    for index, row in enumerate(rows):
        prefix = f"synthetic_sandbox_apply_steps[{index}]"
        _require_text_fields(row, REQUIRED_APPLY_STEP_FIELDS, prefix, problems)
        if "synthetic" not in _text(row.get("synthetic_action")).lower() and "sandbox" not in _text(row.get("synthetic_action")).lower():
            problems.append(f"{prefix}.synthetic_action must describe a synthetic sandbox apply step")


def _validate_inventory(value: Any, problems: list[str]) -> None:
    rows = _mapping_sequence(value)
    if not rows:
        return
    for index, row in enumerate(rows):
        prefix = f"expected_changed_fixture_family_inventory[{index}]"
        _require_text_fields(row, ("fixture_family", "change_reason"), prefix, problems)
        paths = _string_sequence(row.get("expected_changed_paths"))
        if not paths:
            problems.append(f"{prefix}.expected_changed_paths must be a non-empty list")
        for path in paths:
            if not path.startswith("ppd/tests/fixtures/"):
                problems.append(f"{prefix}.expected_changed_paths must stay under ppd/tests/fixtures")


def _validate_command_rows(value: Any, key: str, problems: list[str]) -> None:
    rows = _mapping_sequence(value)
    if not rows:
        return
    for index, row in enumerate(rows):
        prefix = f"{key}[{index}]"
        for field in REQUIRED_COMMAND_FIELDS:
            if field == "command":
                if not _string_sequence(row.get(field)):
                    problems.append(f"{prefix}.command must be a command list")
            elif not _text(row.get(field)):
                problems.append(f"{prefix}.{field} is required")


def _validate_no_main_worktree_notes(value: Any, problems: list[str]) -> None:
    rows = _mapping_sequence(value)
    if not rows:
        return
    for index, row in enumerate(rows):
        prefix = f"no_main_worktree_change_notes[{index}]"
        _require_text_fields(row, REQUIRED_NOTE_FIELDS, prefix, problems)
        statement = _text(row.get("statement")).lower()
        if "main worktree" not in statement or not any(term in statement for term in ("unchanged", "no change", "not changed")):
            problems.append(f"{prefix}.statement must note no main worktree changes")


def _validate_signoff_placeholders(value: Any, problems: list[str]) -> None:
    rows = _mapping_sequence(value)
    if not rows:
        return
    for index, row in enumerate(rows):
        prefix = f"reviewer_signoff_placeholders[{index}]"
        for field in REQUIRED_SIGNOFF_FIELDS:
            if field not in row:
                problems.append(f"{prefix}.{field} is required")
        if row.get("status") != "pending_manual_review":
            problems.append(f"{prefix}.status must be pending_manual_review")
        if _text(row.get("disposition")) not in {"", "pending"}:
            problems.append(f"{prefix}.disposition must remain pending")


def _validate_no_forbidden_payload(packet: Mapping[str, Any], problems: list[str]) -> None:
    for path, key, value in _walk(packet):
        normalized_key = key.lower().replace("-", "_")
        if normalized_key in ACTIVE_MUTATION_FLAGS and value is not False:
            problems.append(f"{path} must be false")
        if value is True and normalized_key.startswith("active_") and any(
            token in normalized_key for token in ("artifact", "prompt", "release_state", "fixture", "agent_state")
        ):
            problems.append(f"{path} must not set active mutation flags")
        if PRIVATE_OR_RAW_KEY_RE.search(normalized_key) and _truthy(value) and not normalized_key.startswith("no_"):
            problems.append(f"{path} must not include private, authenticated, session, browser, screenshot, trace, HAR, auth, raw crawl, PDF, or downloaded artifacts")
        if isinstance(value, str):
            if PRIVATE_OR_RAW_VALUE_RE.search(value):
                problems.append(f"{path} must not reference private, authenticated, session, browser, screenshot, trace, HAR, auth, raw crawl, PDF, or downloaded artifacts")
            if LIVE_OR_APPLIED_RE.search(value):
                problems.append(f"{path} must not claim live execution, main-worktree application, release completion, or promotion completion")
            if OUTCOME_GUARANTEE_RE.search(value):
                problems.append(f"{path} must not guarantee legal or permitting outcomes")
            if CONSEQUENTIAL_ACTION_RE.search(value) and not NEGATED_ACTION_RE.search(value):
                problems.append(f"{path} must not include consequential action language")


def _require_text_fields(row: Mapping[str, Any], fields: Sequence[str], prefix: str, problems: list[str]) -> None:
    for field in fields:
        if not _text(row.get(field)):
            problems.append(f"{prefix}.{field} is required")


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
