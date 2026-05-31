"""Inactive activation rehearsal v2 for approved release decision packets.

This module is fixture-first and no-op only. It consumes an approved inactive
release decision packet v2 and produces a rehearsal plan that documents the
checkpoints an operator would review before any separate activation decision.
It does not activate a release, mutate active state, update prompts, alter
registries, change guardrails, access DevHub, or perform official PP&D work.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence

PACKET_TYPE = "ppd.inactive_activation_rehearsal.v2"
SOURCE_DECISION_PACKET_TYPE = "ppd.inactive_release_decision_packet.v2"

DEFAULT_OFFLINE_VALIDATION_COMMANDS: tuple[tuple[str, ...], ...] = (
    ("python3", "ppd/daemon/ppd_daemon.py", "--self-test"),
    ("python3", "-m", "pytest", "ppd/tests/test_inactive_activation_rehearsal_v2.py"),
)

_REQUIRED_SECTIONS = (
    "preflight_checkpoints",
    "target_inactive_bundle_ids",
    "expected_active_state_diffs",
    "rollback_rehearsal_references",
    "post_activation_smoke_check_placeholders",
    "offline_validation_commands",
)

_REQUIRED_PREFLIGHT_CHECKPOINT_IDS = frozenset(
    {
        "approved-decision-packet-present",
        "offline-validation-command-inventory-present",
        "active-state-diff-is-no-change",
    }
)

_REQUIRED_ACTIVE_STATE_COMPONENTS = frozenset(
    {
        "active_release_state",
        "agent_prompt_registry",
        "guardrail_bundle_registry",
        "source_registry",
        "process_model_registry",
        "contract_registry",
        "devhub_surface_registry",
    }
)

_REQUIRED_ROLLBACK_REFERENCE_IDS = frozenset({"rollback-rehearsal-from-decision-packet"})

_REQUIRED_SMOKE_PLACEHOLDER_IDS = frozenset(
    {
        "post-activation-daemon-self-test",
        "post-activation-rehearsal-unit-test",
    }
)

_REQUIRED_FALSE_ATTESTATIONS = (
    "changes_active_release_state",
    "changes_prompts",
    "changes_guardrails",
    "changes_source_registries",
    "changes_process_models",
    "changes_contracts",
    "changes_devhub_surfaces",
    "uses_live_sources",
    "accesses_devhub",
    "performs_official_actions",
)

_MUTATION_FIELD_RE = re.compile(
    r"(^|_)(active_)?(mutation|mutate|mutates|mutated|write|writes|update|updates|change|changes|promotion|promote|activation|activate)(_|$)|"
    r"(^|_)(active_)?(release_state|prompt|guardrail|source_registry|process_model|contract|devhub_surface)_(mutation|update|write|change|promotion|activation)(_|$)|"
    r"(^|_)(mutates|updates|changes|promotes|activates)_(active_release_state|release_state|prompts|guardrails|source_registries|process_models|contracts|devhub_surfaces)(_|$)",
    re.IGNORECASE,
)
_PRIVATE_FIELD_RE = re.compile(
    r"(auth[_-]?state|browser[_-]?(artifact|state)?|cookie|credential|download(ed)?|har|private|"
    r"raw[_-]?(artifact|body|capture|crawl|data|download|html|pdf)?|screenshot|session[_-]?(artifact|state|storage)?|"
    r"storage[_-]?state|token|trace)",
    re.IGNORECASE,
)
_UNSAFE_TEXT_RE = re.compile(
    r"(^file://)|(^/home/[^/]+/)|(^/Users/[^/]+/)|(^/tmp/)|"
    r"(auth[_ -]?state|browser[_ -]?(artifact|state)|cookie|credential|har\b|password|private[_ -]?(artifact|file|path|value)|"
    r"raw[_ -]?(artifact|body|capture|crawl|data|download|html|pdf)|downloaded[_ -]?(artifact|data|document|file|pdf)|"
    r"screenshot|session[_ -]?(artifact|state|storage)?|storage[_ -]?state|token|trace[_ -]?(file|zip)?)|"
    r"\b(live\s+(crawl|browser|devhub|execution|processor|promotion|run)|crawl(ed|ing)?\s+live|opened\s+devhub|access(ed|ing)?\s+devhub|"
    r"devhub\s+(login|session|was\s+opened|automation|browser)|browser\s+(session|trace)|"
    r"official\s+action\s+(complete|completed|performed|submitted|finished)|"
    r"(permit|application|inspection|payment)\s+(submitted|scheduled|cancelled|canceled|certified|paid|uploaded|complete|approved|issued)|"
    r"payment\s+(complete|completed|submitted|processed)|pay\s+(the\s+)?fee|submit(ted|s|ting)?\b|submission\s+(complete|completed)|"
    r"schedule(d|s|ing)?\s+(the\s+)?inspection|cancel(led|s|ing)?\s+(the\s+)?inspection|certif(y|ied|ication)|upload(s|ed|ing)?\b|"
    r"\b(guarantee[sd]?|will\s+be\s+(approved|issued|accepted)|permit\s+approval\s+is\s+assured|legal\s+advice|legally\s+valid|compliance\s+guarantee))",
    re.IGNORECASE,
)
_COMMAND_FORBIDDEN_RE = re.compile(r"\b(live|crawl|devhub|playwright|browser|network|auth|session|promote)\b", re.IGNORECASE)


@dataclass(frozen=True)
class InactiveActivationRehearsalIssue:
    code: str
    path: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "path": self.path, "message": self.message}


@dataclass(frozen=True)
class InactiveActivationRehearsalValidationResult:
    ok: bool
    issues: tuple[InactiveActivationRehearsalIssue, ...]

    def as_dict(self) -> dict[str, Any]:
        return {"ok": self.ok, "issues": [issue.as_dict() for issue in self.issues]}


def build_inactive_activation_rehearsal_v2(
    release_decision_packet: Mapping[str, Any],
    *,
    rehearsal_id: str = "inactive-activation-rehearsal-v2",
    target_inactive_bundle_ids: Sequence[str] | None = None,
    validation_commands: Sequence[Sequence[str]] = DEFAULT_OFFLINE_VALIDATION_COMMANDS,
) -> dict[str, Any]:
    """Build a no-op activation rehearsal from an approved decision packet."""

    _assert_approved_release_decision_packet(release_decision_packet)
    bundle_ids = list(target_inactive_bundle_ids or _target_bundle_ids(release_decision_packet))
    source_packet_id = str(release_decision_packet.get("packet_id") or "inactive-release-decision-packet-v2")

    packet: dict[str, Any] = {
        "packet_type": PACKET_TYPE,
        "packet_version": "v2",
        "rehearsal_id": rehearsal_id,
        "fixture_only": True,
        "no_op_activation_plan": True,
        "inactive_activation_rehearsal": True,
        "source_release_decision_packet": {
            "packet_type": SOURCE_DECISION_PACKET_TYPE,
            "packet_id": source_packet_id,
            "approved": True,
        },
        "preflight_checkpoints": [
            {
                "checkpoint_id": "approved-decision-packet-present",
                "status": "planned_check_only",
                "expected_input": source_packet_id,
                "required_before": "any_separate_activation_decision",
            },
            {
                "checkpoint_id": "offline-validation-command-inventory-present",
                "status": "planned_check_only",
                "expected_input": "offline_validation_commands",
                "required_before": "any_separate_activation_decision",
            },
            {
                "checkpoint_id": "active-state-diff-is-no-change",
                "status": "planned_check_only",
                "expected_input": "expected_active_state_diffs",
                "required_before": "any_separate_activation_decision",
            },
        ],
        "target_inactive_bundle_ids": bundle_ids,
        "expected_active_state_diffs": [
            {
                "target_inactive_bundle_id": bundle_id,
                "active_state_component": component,
                "expected_diff": "no_change",
                "status": "placeholder_only",
            }
            for bundle_id in bundle_ids
            for component in sorted(_REQUIRED_ACTIVE_STATE_COMPONENTS)
        ],
        "rollback_rehearsal_references": [
            {
                "reference_id": "rollback-rehearsal-from-decision-packet",
                "source_packet_id": source_packet_id,
                "status": "reference_only",
                "required_before": "any_separate_activation_decision",
            }
        ],
        "post_activation_smoke_check_placeholders": [
            {
                "placeholder_id": "post-activation-daemon-self-test",
                "status": "placeholder_only",
                "command_ref": "offline-validation-command-1",
                "result": None,
            },
            {
                "placeholder_id": "post-activation-rehearsal-unit-test",
                "status": "placeholder_only",
                "command_ref": "offline-validation-command-2",
                "result": None,
            },
        ],
        "offline_validation_commands": [list(command) for command in validation_commands],
        "no_op_attestations": {key: False for key in _REQUIRED_FALSE_ATTESTATIONS},
    }
    assert_valid_inactive_activation_rehearsal_v2(packet)
    return packet


def validate_inactive_activation_rehearsal_v2(packet: Mapping[str, Any]) -> InactiveActivationRehearsalValidationResult:
    issues: list[InactiveActivationRehearsalIssue] = []

    if packet.get("packet_type") != PACKET_TYPE:
        issues.append(_issue("invalid_packet_type", "packet_type", f"packet_type must be {PACKET_TYPE}"))
    for key in ("fixture_only", "no_op_activation_plan", "inactive_activation_rehearsal"):
        if packet.get(key) is not True:
            issues.append(_issue("required_true_flag", key, f"{key} must be true"))

    source = packet.get("source_release_decision_packet")
    if not isinstance(source, Mapping) or source.get("packet_type") != SOURCE_DECISION_PACKET_TYPE or source.get("approved") is not True:
        issues.append(_issue("invalid_source_decision_packet", "source_release_decision_packet", "source decision packet must be approved inactive release decision v2 metadata"))

    for section in _REQUIRED_SECTIONS:
        if not _non_empty_sequence(packet.get(section)):
            issues.append(_issue("missing_required_section", section, f"{section} must be a non-empty list"))

    _validate_preflight_checkpoints(packet.get("preflight_checkpoints"), issues)
    _validate_target_bundle_ids(packet.get("target_inactive_bundle_ids"), issues)
    _validate_expected_active_state_diffs(packet.get("expected_active_state_diffs"), packet.get("target_inactive_bundle_ids"), issues)
    _validate_rollback_references(packet.get("rollback_rehearsal_references"), issues)
    _validate_smoke_placeholders(packet.get("post_activation_smoke_check_placeholders"), issues)
    _validate_commands(packet.get("offline_validation_commands"), issues)
    _validate_attestations(packet.get("no_op_attestations"), issues)
    _scan_for_unsafe_content(packet, "", issues)

    return InactiveActivationRehearsalValidationResult(not issues, tuple(issues))


def assert_valid_inactive_activation_rehearsal_v2(packet: Mapping[str, Any]) -> None:
    result = validate_inactive_activation_rehearsal_v2(packet)
    if not result.ok:
        formatted = "; ".join(f"{issue.code} at {issue.path}" for issue in result.issues)
        raise ValueError(f"inactive activation rehearsal v2 validation failed: {formatted}")


def _assert_approved_release_decision_packet(packet: Mapping[str, Any]) -> None:
    if packet.get("packet_type") != SOURCE_DECISION_PACKET_TYPE:
        raise ValueError(f"release decision packet must have packet_type {SOURCE_DECISION_PACKET_TYPE}")
    if packet.get("fixture_only") is not True or packet.get("inactive_release_decision") is not True:
        raise ValueError("release decision packet must be fixture-only inactive release decision metadata")
    rows = _mapping_rows(packet.get("decision_rows"))
    if not rows:
        raise ValueError("release decision packet must include decision rows")
    if any(str(row.get("decision") or "") != "approve" for row in rows):
        raise ValueError("release decision packet must contain only approved decision rows")
    blocked = packet.get("blocked_release_reasons")
    if isinstance(blocked, Sequence) and not isinstance(blocked, (str, bytes, bytearray)) and blocked:
        raise ValueError("approved release decision packet must not carry blocked release reasons")


def _target_bundle_ids(packet: Mapping[str, Any]) -> tuple[str, ...]:
    direct = packet.get("target_inactive_bundle_ids")
    if _non_empty_sequence(direct) and all(isinstance(item, str) and item.strip() for item in direct):
        return tuple(str(item) for item in direct)
    rows = _mapping_rows(packet.get("decision_rows"))
    ids = tuple(
        str(row.get("target_inactive_bundle_id"))
        for row in rows
        if isinstance(row.get("target_inactive_bundle_id"), str) and str(row.get("target_inactive_bundle_id")).strip()
    )
    if ids:
        return ids
    return ("inactive-fixture-release-bundle-v2",)


def _validate_preflight_checkpoints(value: Any, issues: list[InactiveActivationRehearsalIssue]) -> None:
    rows = _mapping_rows(value)
    seen: set[str] = set()
    for index, row in enumerate(rows):
        path = f"preflight_checkpoints[{index}]"
        checkpoint_id = row.get("checkpoint_id")
        if not _text(checkpoint_id) or not _text(row.get("expected_input")):
            issues.append(_issue("invalid_preflight_checkpoint", path, "preflight checkpoint requires checkpoint_id and expected_input"))
        elif str(checkpoint_id) not in _REQUIRED_PREFLIGHT_CHECKPOINT_IDS:
            issues.append(_issue("unknown_preflight_checkpoint", f"{path}.checkpoint_id", "preflight checkpoint id is not part of inactive activation rehearsal v2"))
        else:
            seen.add(str(checkpoint_id))
        if row.get("status") != "planned_check_only":
            issues.append(_issue("invalid_preflight_status", f"{path}.status", "preflight checkpoint must remain planned_check_only"))
        if row.get("required_before") != "any_separate_activation_decision":
            issues.append(_issue("invalid_preflight_gate", f"{path}.required_before", "preflight checkpoint must gate any separate activation decision"))
    for missing in sorted(_REQUIRED_PREFLIGHT_CHECKPOINT_IDS.difference(seen)):
        issues.append(_issue("missing_preflight_checkpoint", "preflight_checkpoints", f"missing preflight checkpoint {missing}"))


def _validate_target_bundle_ids(value: Any, issues: list[InactiveActivationRehearsalIssue]) -> None:
    if not _non_empty_sequence(value):
        return
    seen: set[str] = set()
    for index, bundle_id in enumerate(value):
        path = f"target_inactive_bundle_ids[{index}]"
        if not isinstance(bundle_id, str) or not bundle_id.strip():
            issues.append(_issue("invalid_target_inactive_bundle_id", path, "target bundle id must be a non-empty inactive bundle id"))
            continue
        normalized = bundle_id.strip().lower()
        if not normalized.startswith("inactive-"):
            issues.append(_issue("invalid_target_inactive_bundle_id", path, "target bundle id must explicitly start with inactive-"))
        if normalized in seen:
            issues.append(_issue("duplicate_target_inactive_bundle_id", path, "target inactive bundle ids must be unique"))
        seen.add(normalized)


def _validate_expected_active_state_diffs(value: Any, bundle_ids: Any, issues: list[InactiveActivationRehearsalIssue]) -> None:
    expected_bundle_ids = {item for item in bundle_ids if isinstance(item, str)} if _non_empty_sequence(bundle_ids) else set()
    coverage: dict[str, set[str]] = {bundle_id: set() for bundle_id in expected_bundle_ids}
    for index, row in enumerate(_mapping_rows(value)):
        path = f"expected_active_state_diffs[{index}]"
        bundle_id = row.get("target_inactive_bundle_id")
        component = row.get("active_state_component")
        if not _text(bundle_id):
            issues.append(_issue("missing_diff_target", f"{path}.target_inactive_bundle_id", "expected active-state diff requires target inactive bundle id"))
        elif expected_bundle_ids and str(bundle_id) not in expected_bundle_ids:
            issues.append(_issue("unknown_diff_target", f"{path}.target_inactive_bundle_id", "expected active-state diff must reference a target inactive bundle id"))
        if not _text(component):
            issues.append(_issue("missing_active_state_component", f"{path}.active_state_component", "expected active-state diff requires component name"))
        elif str(component) not in _REQUIRED_ACTIVE_STATE_COMPONENTS:
            issues.append(_issue("unknown_active_state_component", f"{path}.active_state_component", "expected active-state diff component is not part of the rehearsal contract"))
        elif _text(bundle_id) and str(bundle_id) in coverage:
            coverage[str(bundle_id)].add(str(component))
        if row.get("expected_diff") != "no_change" or row.get("status") != "placeholder_only":
            issues.append(_issue("invalid_expected_active_state_diff", path, "expected active-state diff must be no_change and placeholder_only"))
    for bundle_id, components in sorted(coverage.items()):
        for missing_component in sorted(_REQUIRED_ACTIVE_STATE_COMPONENTS.difference(components)):
            issues.append(_issue("missing_active_state_diff_coverage", "expected_active_state_diffs", f"missing no-change diff coverage for {bundle_id} {missing_component}"))


def _validate_rollback_references(value: Any, issues: list[InactiveActivationRehearsalIssue]) -> None:
    seen: set[str] = set()
    for index, row in enumerate(_mapping_rows(value)):
        path = f"rollback_rehearsal_references[{index}]"
        reference_id = row.get("reference_id")
        if not _text(reference_id) or not _text(row.get("source_packet_id")):
            issues.append(_issue("invalid_rollback_reference", path, "rollback rehearsal reference requires reference_id and source_packet_id"))
        elif str(reference_id) in _REQUIRED_ROLLBACK_REFERENCE_IDS:
            seen.add(str(reference_id))
        if row.get("status") != "reference_only":
            issues.append(_issue("invalid_rollback_status", f"{path}.status", "rollback reference must remain reference_only"))
        if row.get("required_before") != "any_separate_activation_decision":
            issues.append(_issue("invalid_rollback_gate", f"{path}.required_before", "rollback rehearsal reference must gate any separate activation decision"))
    for missing in sorted(_REQUIRED_ROLLBACK_REFERENCE_IDS.difference(seen)):
        issues.append(_issue("missing_rollback_reference", "rollback_rehearsal_references", f"missing rollback rehearsal reference {missing}"))


def _validate_smoke_placeholders(value: Any, issues: list[InactiveActivationRehearsalIssue]) -> None:
    seen: set[str] = set()
    for index, row in enumerate(_mapping_rows(value)):
        path = f"post_activation_smoke_check_placeholders[{index}]"
        placeholder_id = row.get("placeholder_id")
        if not _text(placeholder_id) or not _text(row.get("command_ref")):
            issues.append(_issue("invalid_smoke_placeholder", path, "smoke-check placeholder requires placeholder_id and command_ref"))
        elif str(placeholder_id) in _REQUIRED_SMOKE_PLACEHOLDER_IDS:
            seen.add(str(placeholder_id))
        if row.get("status") != "placeholder_only" or row.get("result") is not None:
            issues.append(_issue("invalid_smoke_placeholder_status", path, "smoke-check result must remain an empty placeholder"))
    for missing in sorted(_REQUIRED_SMOKE_PLACEHOLDER_IDS.difference(seen)):
        issues.append(_issue("missing_smoke_placeholder", "post_activation_smoke_check_placeholders", f"missing post-activation smoke-check placeholder {missing}"))


def _validate_commands(value: Any, issues: list[InactiveActivationRehearsalIssue]) -> None:
    if not _non_empty_sequence(value):
        return
    normalized_commands: set[tuple[str, ...]] = set()
    for index, command in enumerate(value):
        path = f"offline_validation_commands[{index}]"
        if not isinstance(command, list) or not command or not all(isinstance(part, str) and part.strip() for part in command):
            issues.append(_issue("invalid_validation_command", path, "validation command must be a non-empty argv string list"))
            continue
        normalized = tuple(command)
        normalized_commands.add(normalized)
        if _COMMAND_FORBIDDEN_RE.search(" ".join(command)):
            issues.append(_issue("unsafe_validation_command", path, "validation command must remain offline and must not invoke live, crawl, DevHub, browser, network, auth, session, or promotion workflows"))
    for required in DEFAULT_OFFLINE_VALIDATION_COMMANDS:
        if required not in normalized_commands:
            issues.append(_issue("missing_validation_command", "offline_validation_commands", "offline validation commands must include daemon self-test and inactive activation rehearsal unit test"))


def _validate_attestations(value: Any, issues: list[InactiveActivationRehearsalIssue]) -> None:
    if not isinstance(value, Mapping):
        issues.append(_issue("missing_no_op_attestations", "no_op_attestations", "no-op attestations must be present"))
        return
    for key in _REQUIRED_FALSE_ATTESTATIONS:
        if value.get(key) is not False:
            issues.append(_issue("invalid_no_op_attestation", f"no_op_attestations.{key}", f"{key} must be false"))


def _scan_for_unsafe_content(value: Any, path: str, issues: list[InactiveActivationRehearsalIssue]) -> None:
    for child_path, child in _walk(value, path):
        name = _path_name(child_path).lower().replace("-", "_")
        if name and _MUTATION_FIELD_RE.search(name) and _active_flag(child):
            issues.append(_issue("active_mutation_flag", child_path, "active mutation flags are not allowed"))
        if name and not name.startswith("no_") and _PRIVATE_FIELD_RE.search(name) and _present_value(child):
            issues.append(_issue("private_or_raw_artifact_field", child_path, "private, session, browser, raw, or downloaded artifacts are not allowed"))
        if isinstance(child, str) and _UNSAFE_TEXT_RE.search(child):
            issues.append(_issue("unsafe_text", child_path, "private artifacts, live crawl or DevHub claims, official-action completion claims, legal or permitting guarantees, and raw/downloaded artifacts are not allowed"))


def _mapping_rows(value: Any) -> tuple[Mapping[str, Any], ...]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return tuple(item for item in value if isinstance(item, Mapping))
    return ()


def _walk(value: Any, path: str) -> Iterable[tuple[str, Any]]:
    yield path, value
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = str(key) if not path else f"{path}.{key}"
            yield from _walk(child, child_path)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            yield from _walk(child, f"{path}[{index}]")


def _path_name(path: str) -> str:
    if not path:
        return ""
    return path.rsplit(".", 1)[-1].split("[", 1)[0]


def _active_flag(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"1", "active", "enabled", "true", "yes"}
    if isinstance(value, Mapping):
        return bool(value)
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return bool(value)
    return False


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


def _non_empty_sequence(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)) and bool(value)


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _issue(code: str, path: str, message: str) -> InactiveActivationRehearsalIssue:
    return InactiveActivationRehearsalIssue(code, path, message)
