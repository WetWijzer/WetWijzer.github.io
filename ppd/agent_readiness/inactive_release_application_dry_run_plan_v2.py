"""Inactive release application dry-run plan v2 validation.

This module validates fixture-only dry-run plans for applying an inactive
release packet. The plan is intentionally metadata-only: it may describe a
future reviewed application sequence, but it must not include private artifacts,
raw crawl/download output, live execution claims, legal guarantees,
consequential PP&D action language, or active promotion/release-state mutation
flags.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from hashlib import sha256
from typing import Any, Iterable, Mapping, Sequence

PACKET_TYPE = "ppd.inactive_release_application_dry_run_plan.v2"

DEFAULT_VALIDATION_COMMANDS: tuple[tuple[str, ...], ...] = (
    ("python3", "ppd/daemon/ppd_daemon.py", "--self-test"),
)

_REQUIRED_SECTIONS = (
    "synthetic_application_steps",
    "expected_file_delta_placeholders",
    "post_application_replay_prerequisites",
    "rollback_rehearsal_checkpoints",
    "reviewer_stop_gates",
    "validation_commands",
)

_REQUIRED_FALSE_FLAGS = (
    "active_promotion_enabled",
    "active_release_application",
    "active_release_state_mutation",
    "apply_release",
    "fixture_promotion_enabled",
    "mutation_enabled",
    "promotes_fixtures",
    "release_state_mutation",
    "release_state_update_enabled",
    "updates_release_state",
)

_SAFE_STEP_ACTIONS = {
    "assemble_synthetic_patch_preview",
    "compare_expected_file_delta_placeholder",
    "verify_replay_prerequisite",
    "verify_rollback_checkpoint",
    "verify_reviewer_stop_gate",
    "verify_validation_command",
}

_FORBIDDEN_FIELD_NAME_RE = re.compile(
    r"(auth[_-]?state|browser[_-]?(artifact|state)?|cookie|credential|download(ed)?|har|private|"
    r"raw[_-]?(artifact|body|capture|crawl|data|download|html|pdf)?|screenshot|"
    r"session[_-]?(artifact|state|storage)?|storage[_-]?state|token|trace)",
    re.IGNORECASE,
)

_FORBIDDEN_TEXT_RE = re.compile(
    r"(^file://)|(^/home/[^/]+/)|(^/Users/[^/]+/)|(^/tmp/)|"
    r"(auth[_ -]?state|browser[_ -]?state|cookie|credential|har\b|password|private[_ -]?(artifact|file|path|value)|"
    r"raw[_ -]?(artifact|body|capture|crawl|data|download|html|pdf)|downloaded[_ -]?(data|document|pdf)|"
    r"screenshot|session[_ -]?(artifact|state|storage)?|storage[_ -]?state|token|trace[_ -]?(file|zip)?)|"
    r"\b(live\s+(crawl|browser|devhub|execution|processor|promotion|run)|crawl\s+live|access\s+devhub|"
    r"promoted\s+(fixtures|release|to)|promotion\s+(complete|completed)|release\s+(complete|completed|state\s+updated)|"
    r"official\s+action\s+performed|permit\s+will\s+be\s+(approved|issued)|approval\s+is\s+guaranteed|"
    r"guaranteed\s+(approval|issuance|permit\s+outcome)|legal\s+advice|legally\s+guaranteed|"
    r"payment|pay\s+(the\s+)?fee|submit(ted|s|ting)?\b|submission|schedule\s+(the\s+)?inspection|"
    r"cancel\s+(the\s+)?inspection|certif(y|ication)|upload(s|ed|ing)?\b)\b",
    re.IGNORECASE,
)

_COMMAND_FORBIDDEN_RE = re.compile(
    r"\b(live|crawl|devhub|playwright|browser|network|auth|session|download|raw)\b",
    re.IGNORECASE,
)

_ACTIVE_MUTATION_NAME_RE = re.compile(
    r"(^|_)(active_)?(promotion|release_state|fixture|artifact)_(mutation|mutating|update|change|promotion|write|enabled)(_|$)|"
    r"(^|_)(mutates|updates|changes|promotes|applies)_(release_state|fixtures|release|artifacts)(_|$)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class InactiveReleaseApplicationDryRunPlanIssue:
    code: str
    path: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "path": self.path, "message": self.message}


@dataclass(frozen=True)
class InactiveReleaseApplicationDryRunPlanValidationResult:
    ok: bool
    issues: tuple[InactiveReleaseApplicationDryRunPlanIssue, ...]

    def as_dict(self) -> dict[str, Any]:
        return {"ok": self.ok, "issues": [issue.as_dict() for issue in self.issues]}


def build_inactive_release_application_dry_run_plan_v2(
    *,
    plan_id: str = "inactive-release-application-dry-run-plan-v2",
    synthetic_step_ids: Sequence[str] = ("assemble", "file-deltas", "replay", "rollback", "reviewer-stop", "validation"),
    expected_file_paths: Sequence[str] = ("ppd/tests/fixtures/inactive_release_application_dry_run_plan_v2/expected-release-packet.json",),
    validation_commands: Sequence[Sequence[str]] = DEFAULT_VALIDATION_COMMANDS,
) -> dict[str, Any]:
    """Build a minimal valid metadata-only inactive dry-run plan."""

    steps = [
        {
            "step_id": f"synthetic-step-{index + 1}-{_slug(step_id)}",
            "synthetic": True,
            "action_type": action_type,
            "status": "planned_not_applied",
            "description": "Synthetic offline checkpoint for inactive release application review.",
            "source_evidence_ids": ["fixture:inactive-release-application-dry-run-plan-v2"],
        }
        for index, (step_id, action_type) in enumerate(zip(synthetic_step_ids, sorted(_SAFE_STEP_ACTIONS)))
    ]
    placeholders = [
        {
            "placeholder_id": f"expected-file-delta-{index + 1}",
            "file_path": file_path,
            "delta_kind": "complete_file_replacement_placeholder",
            "status": "placeholder_not_applied",
            "expected_content_ref": sha256(file_path.encode("utf-8")).hexdigest(),
            "source_evidence_ids": ["fixture:inactive-release-application-dry-run-plan-v2"],
        }
        for index, file_path in enumerate(expected_file_paths)
    ]
    packet: dict[str, Any] = {
        "packet_type": PACKET_TYPE,
        "packet_version": "v2",
        "plan_id": plan_id,
        "fixture_only": True,
        "metadata_only": True,
        "dry_run_only": True,
        "inactive_release_application_dry_run": True,
        "synthetic_application_steps": steps,
        "expected_file_delta_placeholders": placeholders,
        "post_application_replay_prerequisites": [
            {
                "prerequisite_id": "replay-daemon-self-test-after-separate-review",
                "status": "pending",
                "required_before": "post_application_acceptance_review",
                "replay_command": list(DEFAULT_VALIDATION_COMMANDS[0]),
                "source_evidence_ids": ["fixture:inactive-release-application-dry-run-plan-v2"],
            }
        ],
        "rollback_rehearsal_checkpoints": [
            {
                "checkpoint_id": "rollback-rehearsal-inverse-file-list-placeholder",
                "status": "pending_rehearsal",
                "required_before": "any_separate_release_application",
                "expected_inverse_delta_placeholder_ids": [row["placeholder_id"] for row in placeholders],
                "source_evidence_ids": ["fixture:inactive-release-application-dry-run-plan-v2"],
            }
        ],
        "reviewer_stop_gates": [
            {
                "gate_id": "manual-reviewer-stop-before-application",
                "status": "stop_required",
                "required_before": "any_separate_release_application",
                "reviewer_placeholder": "pending_manual_reviewer",
                "source_evidence_ids": ["fixture:inactive-release-application-dry-run-plan-v2"],
            }
        ],
        "validation_commands": [list(command) for command in validation_commands],
        "non_mutation_attestations": {key: False for key in _REQUIRED_FALSE_FLAGS},
    }
    assert_valid_inactive_release_application_dry_run_plan_v2(packet)
    return packet


def validate_inactive_release_application_dry_run_plan_v2(
    packet: Mapping[str, Any],
) -> InactiveReleaseApplicationDryRunPlanValidationResult:
    """Return fail-closed validation for inactive release application dry-run plan v2."""

    issues: list[InactiveReleaseApplicationDryRunPlanIssue] = []
    if packet.get("packet_type") != PACKET_TYPE:
        issues.append(_issue("invalid_packet_type", "packet_type", f"packet_type must be {PACKET_TYPE}"))
    for key in ("fixture_only", "metadata_only", "dry_run_only", "inactive_release_application_dry_run"):
        if packet.get(key) is not True:
            issues.append(_issue("required_true_flag", key, f"{key} must be true"))
    for section in _REQUIRED_SECTIONS:
        if not _non_empty_sequence(packet.get(section)):
            issues.append(_issue("missing_required_section", section, f"{section} must be a non-empty list"))

    _validate_synthetic_application_steps(packet.get("synthetic_application_steps"), issues)
    _validate_expected_file_delta_placeholders(packet.get("expected_file_delta_placeholders"), issues)
    _validate_post_application_replay_prerequisites(packet.get("post_application_replay_prerequisites"), issues)
    _validate_rollback_rehearsal_checkpoints(packet.get("rollback_rehearsal_checkpoints"), issues)
    _validate_reviewer_stop_gates(packet.get("reviewer_stop_gates"), issues)
    _validate_validation_commands(packet.get("validation_commands"), issues)
    _validate_non_mutation_attestations(packet.get("non_mutation_attestations"), issues)
    _scan_for_unsafe_content(packet, "packet", issues)

    return InactiveReleaseApplicationDryRunPlanValidationResult(not issues, tuple(issues))


def assert_valid_inactive_release_application_dry_run_plan_v2(packet: Mapping[str, Any]) -> None:
    result = validate_inactive_release_application_dry_run_plan_v2(packet)
    if not result.ok:
        formatted = "; ".join(f"{issue.code} at {issue.path}" for issue in result.issues)
        raise ValueError(f"inactive release application dry-run plan v2 validation failed: {formatted}")


def _validate_synthetic_application_steps(value: Any, issues: list[InactiveReleaseApplicationDryRunPlanIssue]) -> None:
    seen_actions: set[str] = set()
    for index, row in enumerate(_mapping_rows(value)):
        path = f"synthetic_application_steps[{index}]"
        if row.get("synthetic") is not True:
            issues.append(_issue("synthetic_step_required", f"{path}.synthetic", "synthetic application steps must be marked synthetic"))
        if not _text(row.get("step_id")):
            issues.append(_issue("missing_synthetic_step_id", f"{path}.step_id", "step_id is required"))
        action_type = _text(row.get("action_type"))
        if action_type not in _SAFE_STEP_ACTIONS:
            issues.append(_issue("invalid_synthetic_step_action", f"{path}.action_type", "action_type must be a safe synthetic checkpoint"))
        else:
            seen_actions.add(action_type)
        if row.get("status") != "planned_not_applied":
            issues.append(_issue("invalid_synthetic_step_status", f"{path}.status", "status must be planned_not_applied"))
        _validate_citations(row, path, issues)
    for action_type in sorted(_SAFE_STEP_ACTIONS - seen_actions):
        issues.append(_issue("missing_synthetic_step_action", "synthetic_application_steps", f"missing synthetic application action {action_type}"))


def _validate_expected_file_delta_placeholders(value: Any, issues: list[InactiveReleaseApplicationDryRunPlanIssue]) -> None:
    seen_paths: set[str] = set()
    for index, row in enumerate(_mapping_rows(value)):
        path = f"expected_file_delta_placeholders[{index}]"
        file_path = _text(row.get("file_path"))
        if not _text(row.get("placeholder_id")):
            issues.append(_issue("missing_file_delta_placeholder_id", f"{path}.placeholder_id", "placeholder_id is required"))
        if not file_path.startswith("ppd/tests/fixtures/inactive_release_application_dry_run_plan_v2/"):
            issues.append(_issue("invalid_file_delta_placeholder_path", f"{path}.file_path", "file delta placeholders must target committed PP&D test fixtures"))
        if file_path in seen_paths:
            issues.append(_issue("duplicate_file_delta_placeholder_path", f"{path}.file_path", "file delta placeholder paths must be unique"))
        seen_paths.add(file_path)
        if row.get("delta_kind") != "complete_file_replacement_placeholder":
            issues.append(_issue("invalid_file_delta_kind", f"{path}.delta_kind", "delta_kind must be complete_file_replacement_placeholder"))
        if row.get("status") != "placeholder_not_applied":
            issues.append(_issue("invalid_file_delta_status", f"{path}.status", "status must be placeholder_not_applied"))
        if not _text(row.get("expected_content_ref")):
            issues.append(_issue("missing_expected_content_ref", f"{path}.expected_content_ref", "expected_content_ref is required"))
        _validate_citations(row, path, issues)


def _validate_post_application_replay_prerequisites(value: Any, issues: list[InactiveReleaseApplicationDryRunPlanIssue]) -> None:
    for index, row in enumerate(_mapping_rows(value)):
        path = f"post_application_replay_prerequisites[{index}]"
        if not _text(row.get("prerequisite_id")):
            issues.append(_issue("missing_replay_prerequisite_id", f"{path}.prerequisite_id", "prerequisite_id is required"))
        if row.get("status") != "pending":
            issues.append(_issue("invalid_replay_prerequisite_status", f"{path}.status", "status must be pending"))
        if row.get("required_before") != "post_application_acceptance_review":
            issues.append(_issue("invalid_replay_prerequisite_gate", f"{path}.required_before", "replay prerequisite must gate post-application acceptance review"))
        _validate_single_command(row.get("replay_command"), f"{path}.replay_command", issues)
        _validate_citations(row, path, issues)


def _validate_rollback_rehearsal_checkpoints(value: Any, issues: list[InactiveReleaseApplicationDryRunPlanIssue]) -> None:
    for index, row in enumerate(_mapping_rows(value)):
        path = f"rollback_rehearsal_checkpoints[{index}]"
        if not _text(row.get("checkpoint_id")):
            issues.append(_issue("missing_rollback_checkpoint_id", f"{path}.checkpoint_id", "checkpoint_id is required"))
        if row.get("status") != "pending_rehearsal":
            issues.append(_issue("invalid_rollback_checkpoint_status", f"{path}.status", "status must be pending_rehearsal"))
        if row.get("required_before") != "any_separate_release_application":
            issues.append(_issue("invalid_rollback_checkpoint_gate", f"{path}.required_before", "rollback rehearsal must gate any separate release application"))
        if not _string_items(row.get("expected_inverse_delta_placeholder_ids")):
            issues.append(_issue("missing_inverse_delta_placeholders", f"{path}.expected_inverse_delta_placeholder_ids", "inverse delta placeholders are required"))
        _validate_citations(row, path, issues)


def _validate_reviewer_stop_gates(value: Any, issues: list[InactiveReleaseApplicationDryRunPlanIssue]) -> None:
    for index, row in enumerate(_mapping_rows(value)):
        path = f"reviewer_stop_gates[{index}]"
        if not _text(row.get("gate_id")):
            issues.append(_issue("missing_reviewer_stop_gate_id", f"{path}.gate_id", "gate_id is required"))
        if row.get("status") != "stop_required":
            issues.append(_issue("invalid_reviewer_stop_gate_status", f"{path}.status", "status must be stop_required"))
        if row.get("required_before") != "any_separate_release_application":
            issues.append(_issue("invalid_reviewer_stop_gate", f"{path}.required_before", "reviewer stop gate must gate any separate release application"))
        if not _text(row.get("reviewer_placeholder")):
            issues.append(_issue("missing_reviewer_placeholder", f"{path}.reviewer_placeholder", "reviewer_placeholder is required"))
        _validate_citations(row, path, issues)


def _validate_validation_commands(value: Any, issues: list[InactiveReleaseApplicationDryRunPlanIssue]) -> None:
    if not _non_empty_sequence(value):
        return
    for index, command in enumerate(value):
        _validate_single_command(command, f"validation_commands[{index}]", issues)


def _validate_single_command(value: Any, path: str, issues: list[InactiveReleaseApplicationDryRunPlanIssue]) -> None:
    if not _string_sequence(value):
        issues.append(_issue("invalid_validation_command", path, "validation command must be an argv string list"))
        return
    command_text = " ".join(value)
    if _COMMAND_FORBIDDEN_RE.search(command_text):
        issues.append(_issue("unsafe_validation_command", path, "validation command must not invoke live, crawler, DevHub, browser, network, auth, session, download, or raw paths"))


def _validate_non_mutation_attestations(value: Any, issues: list[InactiveReleaseApplicationDryRunPlanIssue]) -> None:
    if not isinstance(value, Mapping):
        issues.append(_issue("missing_non_mutation_attestations", "non_mutation_attestations", "non-mutation attestations are required"))
        return
    for key in _REQUIRED_FALSE_FLAGS:
        if value.get(key) is not False:
            issues.append(_issue("active_mutation_flag", f"non_mutation_attestations.{key}", f"{key} must be false"))


def _validate_citations(row: Mapping[str, Any], path: str, issues: list[InactiveReleaseApplicationDryRunPlanIssue]) -> None:
    evidence = _string_items(row.get("source_evidence_ids")) or _string_items(row.get("citations"))
    if not evidence:
        issues.append(_issue("missing_fixture_citation", f"{path}.source_evidence_ids", "fixture citation evidence is required"))
        return
    for item in evidence:
        if not item.startswith(("fixture:", "source:", "observation:", "citation:")):
            issues.append(_issue("invalid_fixture_citation", f"{path}.source_evidence_ids", "citations must be fixture, source, observation, or citation refs"))


def _scan_for_unsafe_content(value: Any, path: str, issues: list[InactiveReleaseApplicationDryRunPlanIssue]) -> None:
    for child_path, child in _walk(value, path):
        name = _path_name(child_path).lower().replace("-", "_")
        if name in _REQUIRED_FALSE_FLAGS and child is not False:
            issues.append(_issue("active_mutation_flag", child_path, "active promotion and release-state mutation flags must be false"))
        if _ACTIVE_MUTATION_NAME_RE.search(name) and _active_flag(child):
            issues.append(_issue("active_mutation_flag", child_path, "active promotion and release-state mutation flags are not allowed"))
        if name and not name.startswith("no_") and _FORBIDDEN_FIELD_NAME_RE.search(name) and _present_value(child):
            issues.append(_issue("private_or_raw_artifact_field", child_path, "plan fields must not carry private, session, browser, raw, or downloaded artifacts"))
        if isinstance(child, str) and _FORBIDDEN_TEXT_RE.search(child):
            issues.append(_issue("unsafe_plan_text", child_path, "plan text must not reference private artifacts, live execution, legal/permitting guarantees, consequential official actions, or active release mutation"))


def _walk(value: Any, path: str) -> Iterable[tuple[str, Any]]:
    yield path, value
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            yield from _walk(child, child_path)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            yield from _walk(child, f"{path}[{index}]")


def _mapping_rows(value: Any) -> tuple[Mapping[str, Any], ...]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return tuple(item for item in value if isinstance(item, Mapping))
    return ()


def _non_empty_sequence(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)) and bool(value)


def _string_sequence(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)) and bool(value) and all(isinstance(item, str) and item.strip() for item in value)


def _string_items(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


def _path_name(path: str) -> str:
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


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _slug(value: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return text or "step"


def _issue(code: str, path: str, message: str) -> InactiveReleaseApplicationDryRunPlanIssue:
    return InactiveReleaseApplicationDryRunPlanIssue(code=code, path=path, message=message)
