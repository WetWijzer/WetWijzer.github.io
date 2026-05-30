"""Fixture-first inactive release application dry-run plan v2.

This module converts an inactive release decision packet v2 into a deterministic
application plan. The plan is a committed-fixture, metadata-only rehearsal: it
lists what a later reviewed application proposal would do, but it does not
promote releases, change active artifacts, contact live sources, access DevHub,
store private artifacts, or perform consequential public-record actions.
"""

from __future__ import annotations

import re
from typing import Any, Iterable

from ppd.inactive_release_decision_packet_v2 import assert_valid_inactive_release_decision_packet

PLAN_VERSION = "inactive-release-application-dry-run-plan-v2"
VALIDATION_COMMANDS = [
    ["python3", "-m", "py_compile", "ppd/inactive_release_application_dry_run_plan_v2.py"],
    ["python3", "-m", "pytest", "ppd/tests/test_inactive_release_application_dry_run_plan_v2.py"],
    ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
]

_REQUIRED_TOP_LEVEL_SECTIONS = (
    "ordered_synthetic_application_steps",
    "expected_file_delta_placeholders",
    "post_application_replay_prerequisites",
    "rollback_rehearsal_checkpoints",
    "reviewer_stop_gates",
    "validation_commands",
)

_PRIVATE_FIELD_RE = re.compile(
    r"(auth[_-]?state|browser[_-]?(artifact|state)?|cookie|credential|download(ed)?|har|private|"
    r"raw[_-]?(artifact|body|capture|crawl|data|download|html|pdf)?|screenshot|session[_-]?(artifact|state|storage)?|"
    r"storage[_-]?state|token|trace)",
    re.IGNORECASE,
)
_PRIVATE_TEXT_RE = re.compile(
    r"(^file://)|(^/home/[^/]+/)|(^/Users/[^/]+/)|(^/tmp/)|"
    r"(auth[_ -]?state|browser[_ -]?(artifact|state)|cookie|credential|downloaded[_ -]?(artifact|document|file|pdf)|"
    r"har\b|password|private[_ -]?(artifact|file|path|value)|raw[_ -]?(artifact|body|capture|crawl|data|download|html|pdf)|"
    r"screenshot|session[_ -]?(artifact|state|storage)|storage[_ -]?state|token|trace[_ -]?(file|zip)?)",
    re.IGNORECASE,
)
_LIVE_TEXT_RE = re.compile(
    r"\b(live execution|live crawl|live browser|live devhub|live run|ran live|performed live|accessed devhub|logged in|used authenticated session)\b",
    re.IGNORECASE,
)
_OFFICIAL_ACTION_RE = re.compile(
    r"\b(official action performed|submitted|submission completed|paid the fee|paid fee|payment completed|scheduled inspection|"
    r"cancelled inspection|canceled inspection|certified application|uploaded corrections|uploaded plans)\b",
    re.IGNORECASE,
)
_GUARANTEE_RE = re.compile(
    r"\b(guaranteed approval|guaranteed issuance|permit will be approved|permit will be issued|approval is guaranteed|"
    r"issuance is guaranteed|legal advice|legal guarantee|permitting guarantee)\b",
    re.IGNORECASE,
)
_MUTATION_NAME_RE = re.compile(
    r"(^|_)(active_)?(artifact|source|surface|process|requirement|guardrail|prompt|contract|release_state|fixture|agent_state)"
    r"_(mutation|update|write|promotion)(_|$)|"
    r"(^|_)(mutates|updates|promotes)_(artifact|artifacts|sources|surfaces|processes|requirements|guardrails|prompts|contracts|"
    r"release_state|fixtures|agent_state)(_|$)",
    re.IGNORECASE,
)
_COMMAND_FORBIDDEN_RE = re.compile(r"\b(live|crawl|devhub|playwright|browser|network|auth|session)\b", re.IGNORECASE)


def build_inactive_release_application_dry_run_plan(decision_packet: dict[str, Any]) -> dict[str, Any]:
    """Build a deterministic dry-run application plan from decision packet v2."""

    assert_valid_inactive_release_decision_packet(decision_packet)
    _raise_for_unsafe_content(decision_packet)

    decision_rows = decision_packet.get("rows")
    if not isinstance(decision_rows, list) or not decision_rows:
        raise ValueError("decision packet must contain release decision rows")

    rows = sorted(decision_rows, key=lambda row: row.get("decision_order", 0))
    plan = {
        "plan_version": PLAN_VERSION,
        "source_packet_version": decision_packet.get("packet_version"),
        "mode": "fixture-first-inactive-release-application-dry-run-only",
        "dry_run": True,
        "fixture_first": True,
        "metadata_only": True,
        "active_promotion_applied": False,
        "live_source_accessed": False,
        "devhub_accessed": False,
        "private_artifact_stored": False,
        "official_action_performed": False,
        "ordered_synthetic_application_steps": _application_steps(rows),
        "expected_file_delta_placeholders": _file_delta_placeholders(rows),
        "post_application_replay_prerequisites": _replay_prerequisites(rows),
        "rollback_rehearsal_checkpoints": _rollback_checkpoints(rows),
        "reviewer_stop_gates": _reviewer_stop_gates(rows),
        "validation_commands": VALIDATION_COMMANDS,
    }
    assert_valid_inactive_release_application_dry_run_plan(plan)
    return plan


def validate_inactive_release_application_dry_run_plan(plan: dict[str, Any]) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []

    if plan.get("plan_version") != PLAN_VERSION:
        _issue(issues, "invalid_plan_version", "plan_version", f"plan_version must be {PLAN_VERSION}")
    if plan.get("mode") != "fixture-first-inactive-release-application-dry-run-only":
        _issue(issues, "invalid_mode", "mode", "mode must remain fixture-first-inactive-release-application-dry-run-only")
    for field in ("dry_run", "fixture_first", "metadata_only"):
        if plan.get(field) is not True:
            _issue(issues, "missing_fixture_first_attestation", field, f"{field} must be true")
    for field in (
        "active_promotion_applied",
        "live_source_accessed",
        "devhub_accessed",
        "private_artifact_stored",
        "official_action_performed",
    ):
        if plan.get(field) is not False:
            _issue(issues, "non_promotion_attestation_failed", field, f"{field} must be false")

    for section in _REQUIRED_TOP_LEVEL_SECTIONS:
        value = plan.get(section)
        if not isinstance(value, list) or not value:
            _issue(issues, f"missing_{section}", section, f"{section} must be a non-empty list")

    _validate_steps(plan.get("ordered_synthetic_application_steps"), issues)
    _validate_file_deltas(plan.get("expected_file_delta_placeholders"), issues)
    _validate_replay_prerequisites(plan.get("post_application_replay_prerequisites"), issues)
    _validate_rollback_checkpoints(plan.get("rollback_rehearsal_checkpoints"), issues)
    _validate_reviewer_stop_gates(plan.get("reviewer_stop_gates"), issues)
    _validate_commands(plan.get("validation_commands"), issues)
    _scan_for_unsafe_content(plan, "", issues)
    return issues


def assert_valid_inactive_release_application_dry_run_plan(plan: dict[str, Any]) -> None:
    issues = validate_inactive_release_application_dry_run_plan(plan)
    if issues:
        formatted = "; ".join(f"{issue['code']} at {issue['path']}" for issue in issues)
        raise ValueError(f"inactive release application dry-run plan v2 validation failed: {formatted}")


def _application_steps(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    steps: list[dict[str, Any]] = []
    for row in rows:
        release_id = _text(row.get("release_id"))
        order = len(steps) + 1
        steps.append(
            {
                "step_order": order,
                "step_id": f"stage-{release_id}-decision-packet",
                "release_id": release_id,
                "synthetic_action": "stage inactive release decision fixture for review",
                "input_ref": f"decision-row-{row.get('decision_order')}",
                "expected_state": "staged-placeholder-only",
                "requires_reviewer_stop_gate": True,
            }
        )
        steps.append(
            {
                "step_order": order + 1,
                "step_id": f"map-{release_id}-file-placeholders",
                "release_id": release_id,
                "synthetic_action": "map expected complete-file replacement placeholders",
                "input_ref": row.get("rollback_plan_reference"),
                "expected_state": "file-delta-placeholders-only",
                "requires_reviewer_stop_gate": True,
            }
        )
    for index, step in enumerate(steps, start=1):
        step["step_order"] = index
    return steps


def _file_delta_placeholders(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "delta_order": index,
            "delta_id": f"delta-{_text(row.get('release_id'))}",
            "release_id": _text(row.get("release_id")),
            "target_path_placeholder": f"ppd/tests/fixtures/inactive_release_application_dry_run_plan_v2/{_text(row.get('release_id'))}.json",
            "delta_kind": "complete-file-replacement-placeholder",
            "expected_status": "not-applied",
            "source_decision_order": row.get("decision_order"),
            "citations": [f"inactive-release-decision-row:{_text(row.get('release_id'))}"],
        }
        for index, row in enumerate(rows, start=1)
    ]


def _replay_prerequisites(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    prerequisites = [
        {
            "prerequisite_order": 1,
            "prerequisite_id": "replay-source-decision-validation",
            "required_status": "pending-offline-replay",
            "command": ["python3", "-m", "pytest", "ppd/tests/test_inactive_release_decision_packet_v2.py"],
            "blocks_application": True,
        },
        {
            "prerequisite_order": 2,
            "prerequisite_id": "replay-plan-validation",
            "required_status": "pending-offline-replay",
            "command": ["python3", "-m", "pytest", "ppd/tests/test_inactive_release_application_dry_run_plan_v2.py"],
            "blocks_application": True,
        },
        {
            "prerequisite_order": 3,
            "prerequisite_id": "replay-daemon-self-test",
            "required_status": "pending-offline-replay",
            "command": ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
            "blocks_application": True,
        },
    ]
    if rows:
        prerequisites.append(
            {
                "prerequisite_order": 4,
                "prerequisite_id": "replay-row-count-reconciliation",
                "required_status": "pending-offline-review",
                "expected_release_row_count": len(rows),
                "blocks_application": True,
            }
        )
    return prerequisites


def _rollback_checkpoints(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "checkpoint_order": index,
            "checkpoint_id": f"rollback-{_text(row.get('release_id'))}",
            "release_id": _text(row.get("release_id")),
            "rollback_reference": row.get("rollback_plan_reference"),
            "rehearsal_status": "checkpoint-only-not-executed",
            "required_before_any_future_application": True,
        }
        for index, row in enumerate(rows, start=1)
    ]


def _reviewer_stop_gates(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    gates = [
        {
            "gate_order": 1,
            "gate_id": "stop-before-active-promotion",
            "status": "stop-required",
            "required_reviewer_action": "manual approval record must be supplied in a separate authorized path",
            "blocks_application": True,
        }
    ]
    for row in rows:
        gates.append(
            {
                "gate_order": len(gates) + 1,
                "gate_id": f"stop-{_text(row.get('release_id'))}-human-approval",
                "release_id": _text(row.get("release_id")),
                "status": "stop-required",
                "required_reviewer_action": "review the source decision basis and placeholder file delta before any later patch",
                "blocks_application": True,
            }
        )
    return gates


def _validate_steps(value: Any, issues: list[dict[str, str]]) -> None:
    rows = _list(value)
    expected_order = 1
    for index, row in enumerate(rows):
        path = f"ordered_synthetic_application_steps[{index}]"
        if not isinstance(row, dict):
            _issue(issues, "invalid_application_step", path, "application step must be an object")
            continue
        if row.get("step_order") != expected_order:
            _issue(issues, "invalid_application_step_order", f"{path}.step_order", f"step_order must be {expected_order}")
        expected_order += 1
        for field in ("step_id", "release_id", "synthetic_action", "expected_state"):
            if not _text(row.get(field)):
                _issue(issues, "missing_application_step_field", f"{path}.{field}", f"{field} is required")
        if row.get("requires_reviewer_stop_gate") is not True:
            _issue(issues, "application_step_missing_stop_gate", f"{path}.requires_reviewer_stop_gate", "each step must require a reviewer stop gate")


def _validate_file_deltas(value: Any, issues: list[dict[str, str]]) -> None:
    for index, row in enumerate(_list(value)):
        path = f"expected_file_delta_placeholders[{index}]"
        if not isinstance(row, dict):
            _issue(issues, "invalid_file_delta_placeholder", path, "file-delta placeholder must be an object")
            continue
        target = _text(row.get("target_path_placeholder"))
        if not target.startswith("ppd/tests/fixtures/inactive_release_application_dry_run_plan_v2/"):
            _issue(issues, "invalid_file_delta_target", f"{path}.target_path_placeholder", "placeholder target must stay under committed PP&D test fixtures")
        if row.get("delta_kind") != "complete-file-replacement-placeholder" or row.get("expected_status") != "not-applied":
            _issue(issues, "invalid_file_delta_status", path, "file delta must remain a not-applied complete-file replacement placeholder")
        if not _string_list(row.get("citations")):
            _issue(issues, "missing_file_delta_citations", f"{path}.citations", "file-delta placeholder requires citations")


def _validate_replay_prerequisites(value: Any, issues: list[dict[str, str]]) -> None:
    for index, row in enumerate(_list(value)):
        path = f"post_application_replay_prerequisites[{index}]"
        if not isinstance(row, dict):
            _issue(issues, "invalid_replay_prerequisite", path, "replay prerequisite must be an object")
            continue
        if not _text(row.get("prerequisite_id")) or row.get("blocks_application") is not True:
            _issue(issues, "invalid_replay_prerequisite", path, "replay prerequisite must have an id and block application")
        if "command" in row:
            _validate_command(row.get("command"), f"{path}.command", issues)


def _validate_rollback_checkpoints(value: Any, issues: list[dict[str, str]]) -> None:
    for index, row in enumerate(_list(value)):
        path = f"rollback_rehearsal_checkpoints[{index}]"
        if not isinstance(row, dict):
            _issue(issues, "invalid_rollback_checkpoint", path, "rollback checkpoint must be an object")
            continue
        if not _text(row.get("checkpoint_id")) or not _text(row.get("rollback_reference")):
            _issue(issues, "missing_rollback_checkpoint_reference", path, "rollback checkpoint requires id and reference")
        if row.get("rehearsal_status") != "checkpoint-only-not-executed":
            _issue(issues, "invalid_rollback_checkpoint_status", f"{path}.rehearsal_status", "rollback checkpoint must not be executed by this dry run")


def _validate_reviewer_stop_gates(value: Any, issues: list[dict[str, str]]) -> None:
    for index, row in enumerate(_list(value)):
        path = f"reviewer_stop_gates[{index}]"
        if not isinstance(row, dict):
            _issue(issues, "invalid_reviewer_stop_gate", path, "reviewer stop gate must be an object")
            continue
        if not _text(row.get("gate_id")) or row.get("status") != "stop-required" or row.get("blocks_application") is not True:
            _issue(issues, "invalid_reviewer_stop_gate", path, "reviewer gate must stop application")
        if not _text(row.get("required_reviewer_action")):
            _issue(issues, "missing_reviewer_stop_gate_action", f"{path}.required_reviewer_action", "reviewer stop gate requires action text")


def _validate_commands(value: Any, issues: list[dict[str, str]]) -> None:
    commands = _list(value)
    if VALIDATION_COMMANDS not in (commands,):
        if commands != VALIDATION_COMMANDS:
            _issue(issues, "invalid_exact_validation_commands", "validation_commands", "validation_commands must match the exact offline command list")
    for index, command in enumerate(commands):
        _validate_command(command, f"validation_commands[{index}]", issues)


def _validate_command(command: Any, path: str, issues: list[dict[str, str]]) -> None:
    if not isinstance(command, list) or not command or not all(isinstance(part, str) and part.strip() for part in command):
        _issue(issues, "invalid_validation_command", path, "validation command must be a non-empty argv string list")
        return
    if _COMMAND_FORBIDDEN_RE.search(" ".join(command)):
        _issue(issues, "unsafe_validation_command", path, "validation command must not invoke live, crawl, DevHub, browser, network, auth, or session workflows")


def _raise_for_unsafe_content(value: Any) -> None:
    issues: list[dict[str, str]] = []
    _scan_for_unsafe_content(value, "", issues)
    if issues:
        formatted = "; ".join(f"{issue['code']} at {issue['path']}" for issue in issues)
        raise ValueError(f"unsafe inactive release application dry-run content: {formatted}")


def _scan_for_unsafe_content(value: Any, path: str, issues: list[dict[str, str]]) -> None:
    for child_path, child in _walk(value, path):
        name = _path_name(child_path).lower().replace("-", "_")
        if name and _MUTATION_NAME_RE.search(name) and _active_flag(child):
            _issue(issues, "active_mutation_flag", child_path, "active mutation flags are not allowed")
        if name and not name.startswith("no_") and _PRIVATE_FIELD_RE.search(name) and _present_value(child):
            _issue(issues, "private_or_raw_artifact_field", child_path, "private, session, browser, raw, or downloaded artifacts are not allowed")
        if isinstance(child, str):
            if _PRIVATE_TEXT_RE.search(child):
                _issue(issues, "private_or_raw_artifact_text", child_path, "private, session, browser, raw, or downloaded artifact text is not allowed")
            if _LIVE_TEXT_RE.search(child):
                _issue(issues, "live_execution_claim", child_path, "live execution claims are not allowed")
            if _OFFICIAL_ACTION_RE.search(child):
                _issue(issues, "consequential_official_action_language", child_path, "consequential official action language is not allowed")
            if _GUARANTEE_RE.search(child):
                _issue(issues, "legal_or_permitting_guarantee", child_path, "legal or permitting guarantees are not allowed")


def _walk(value: Any, path: str) -> Iterable[tuple[str, Any]]:
    yield path, value
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = str(key) if not path else f"{path}.{key}"
            yield from _walk(child, child_path)
    elif isinstance(value, list):
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
    if isinstance(value, dict):
        return bool(value)
    if isinstance(value, list):
        return bool(value)
    return False


def _present_value(value: Any) -> bool:
    if value is None or value is False:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, dict):
        return bool(value)
    if isinstance(value, list):
        return bool(value)
    return True


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _issue(issues: list[dict[str, str]], code: str, path: str, message: str) -> None:
    issues.append({"code": code, "path": path, "message": message})
