"""Build and validate inactive release decision packet v2 from approved offline reviewer dispositions."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Iterable

PACKET_VERSION = "inactive-release-decision-packet-v2"
VALIDATION_COMMANDS = [
    ["python3", "-m", "py_compile", "ppd/inactive_release_decision_packet_v2.py"],
    ["python3", "-m", "pytest", "ppd/tests/test_inactive_release_decision_packet_v2.py"],
    ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
]

_MUTATION_FLAG_NAMES = {
    "active_artifact_mutation",
    "active_release_state_mutation",
    "active_fixture_mutation",
    "active_prompt_mutation",
    "active_guardrail_mutation",
    "active_agent_state_mutation",
    "mutates_artifacts",
    "mutates_release_state",
    "mutates_fixtures",
    "mutates_prompts",
    "promotes_fixtures",
    "release_state_update_enabled",
}

_MUTATION_NAME_RE = re.compile(
    r"(^|_)(active_)?(artifact|release_state|fixture|prompt|guardrail|agent_state)_(mutation|update|write|promotion)(_|$)|"
    r"(^|_)(mutates|updates|promotes)_(artifact|artifacts|release_state|fixtures|prompts|guardrails|agent_state)(_|$)",
    re.IGNORECASE,
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
_LIVE_CLAIM_RE = re.compile(
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
_COMMAND_FORBIDDEN_RE = re.compile(r"\b(live|crawl|devhub|playwright|browser|network|auth|session)\b", re.IGNORECASE)


def _require_text(row: dict[str, Any], field: str) -> str:
    value = row.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"disposition row missing required text field: {field}")
    return value.strip()


def _require_approved(row: dict[str, Any]) -> None:
    disposition = _require_text(row, "reviewer_disposition")
    if disposition != "approved-offline":
        release_id = row.get("release_id", "")
        raise ValueError(f"release {release_id} is not approved for inactive decision: {disposition}")


def _sort_key(row: dict[str, Any]) -> tuple[int, str]:
    order = row.get("review_order")
    if not isinstance(order, int):
        raise ValueError("disposition row missing integer review_order")
    return order, _require_text(row, "release_id")


def build_inactive_release_decision_packet(disposition_packet: dict[str, Any]) -> dict[str, Any]:
    rows = disposition_packet.get("rows")
    if not isinstance(rows, list) or not rows:
        raise ValueError("disposition packet must contain a non-empty rows list")

    _raise_for_unsafe_content(disposition_packet)

    decision_rows: list[dict[str, Any]] = []
    for row in sorted(rows, key=_sort_key):
        if not isinstance(row, dict):
            raise ValueError("each disposition row must be an object")
        _require_approved(row)
        release_id = _require_text(row, "release_id")
        decision_rows.append(
            {
                "decision_order": len(decision_rows) + 1,
                "release_id": release_id,
                "source_disposition_packet_version": disposition_packet.get("packet_version", "approved-offline-release-reviewer-disposition-packet-v2"),
                "source_review_order": row["review_order"],
                "inactive_release_decision": "hold-inactive-pending-human-approval",
                "decision_basis": _require_text(row, "reviewer_rationale"),
                "promotion_scope_placeholder": {
                    "status": "placeholder-only",
                    "scope": "no promotion scope authorized by this fixture",
                    "requires_human_scope_selection": True,
                },
                "human_approval_placeholder": {
                    "status": "not-approved",
                    "required_before_promotion": True,
                    "approval_record": None,
                },
                "rollback_plan_reference": _require_text(row, "rollback_plan_reference"),
                "no_live_access_attestation": {
                    "attested": True,
                    "basis": _require_text(row, "no_live_access_basis"),
                },
            }
        )

    packet = {
        "packet_version": PACKET_VERSION,
        "source_packet_version": disposition_packet.get("packet_version", "approved-offline-release-reviewer-disposition-packet-v2"),
        "mode": "fixture-first-offline-only",
        "rows": decision_rows,
        "validation_commands": VALIDATION_COMMANDS,
    }
    assert_valid_inactive_release_decision_packet(packet)
    return packet


def validate_inactive_release_decision_packet(packet: dict[str, Any]) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []

    if packet.get("packet_version") != PACKET_VERSION:
        _issue(issues, "invalid_packet_version", "packet_version", f"packet_version must be {PACKET_VERSION}")
    if packet.get("mode") != "fixture-first-offline-only":
        _issue(issues, "invalid_mode", "mode", "mode must remain fixture-first-offline-only")

    rows = packet.get("rows")
    if not isinstance(rows, list) or not rows:
        _issue(issues, "missing_release_decision_rows", "rows", "inactive release decision packet requires non-empty release decision rows")
    else:
        for index, row in enumerate(rows):
            if not isinstance(row, dict):
                _issue(issues, "invalid_release_decision_row", f"rows[{index}]", "release decision row must be an object")
                continue
            _validate_decision_row(row, index, issues)

    commands = packet.get("validation_commands")
    if not isinstance(commands, list) or not commands:
        _issue(issues, "missing_validation_commands", "validation_commands", "validation_commands must be a non-empty argv list collection")
    else:
        for index, command in enumerate(commands):
            _validate_command(command, f"validation_commands[{index}]", issues)

    _scan_for_unsafe_content(packet, "", issues)
    return issues


def assert_valid_inactive_release_decision_packet(packet: dict[str, Any]) -> None:
    issues = validate_inactive_release_decision_packet(packet)
    if issues:
        formatted = "; ".join(f"{issue['code']} at {issue['path']}" for issue in issues)
        raise ValueError(f"inactive release decision packet v2 validation failed: {formatted}")


def _validate_decision_row(row: dict[str, Any], index: int, issues: list[dict[str, str]]) -> None:
    path = f"rows[{index}]"
    if not _text(row.get("release_id")):
        _issue(issues, "missing_release_id", f"{path}.release_id", "release decision row requires release_id")
    if row.get("inactive_release_decision") != "hold-inactive-pending-human-approval":
        _issue(issues, "invalid_inactive_release_decision", f"{path}.inactive_release_decision", "inactive release decision must hold pending human approval")
    if not _text(row.get("decision_basis")):
        _issue(issues, "missing_decision_basis", f"{path}.decision_basis", "release decision row requires decision_basis")

    scope = row.get("promotion_scope_placeholder")
    if not isinstance(scope, dict):
        _issue(issues, "missing_promotion_scope_placeholder", f"{path}.promotion_scope_placeholder", "promotion scope placeholder is required")
    else:
        if scope.get("status") != "placeholder-only" or scope.get("requires_human_scope_selection") is not True or not _text(scope.get("scope")):
            _issue(issues, "invalid_promotion_scope_placeholder", f"{path}.promotion_scope_placeholder", "promotion scope must remain placeholder-only and require human scope selection")

    approval = row.get("human_approval_placeholder")
    if not isinstance(approval, dict):
        _issue(issues, "missing_human_approval_placeholder", f"{path}.human_approval_placeholder", "human approval placeholder is required")
    else:
        if approval.get("status") != "not-approved" or approval.get("required_before_promotion") is not True or approval.get("approval_record") is not None:
            _issue(issues, "invalid_human_approval_placeholder", f"{path}.human_approval_placeholder", "human approval must remain an unapproved placeholder")

    if not _text(row.get("rollback_plan_reference")):
        _issue(issues, "missing_rollback_plan_reference", f"{path}.rollback_plan_reference", "rollback plan reference is required")

    attestation = row.get("no_live_access_attestation")
    if not isinstance(attestation, dict):
        _issue(issues, "missing_no_live_access_attestation", f"{path}.no_live_access_attestation", "no-live-access attestation is required")
    else:
        if attestation.get("attested") is not True or not _text(attestation.get("basis")):
            _issue(issues, "invalid_no_live_access_attestation", f"{path}.no_live_access_attestation", "no-live-access attestation must be true and include a basis")


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
        raise ValueError(f"unsafe inactive release decision content: {formatted}")


def _scan_for_unsafe_content(value: Any, path: str, issues: list[dict[str, str]]) -> None:
    for child_path, child in _walk(value, path):
        name = _path_name(child_path).lower().replace("-", "_")
        if name and (name in _MUTATION_FLAG_NAMES or _MUTATION_NAME_RE.search(name)) and _active_flag(child):
            _issue(issues, "active_mutation_flag", child_path, "active artifact or release-state mutation flags are not allowed")
        if name and not name.startswith("no_") and _PRIVATE_FIELD_RE.search(name) and _present_value(child):
            _issue(issues, "private_or_raw_artifact_field", child_path, "private, session, browser, raw, or downloaded artifacts are not allowed")
        if isinstance(child, str):
            if _PRIVATE_TEXT_RE.search(child):
                _issue(issues, "private_or_raw_artifact_text", child_path, "private, session, browser, raw, or downloaded artifact text is not allowed")
            if _LIVE_CLAIM_RE.search(child):
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


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _issue(issues: list[dict[str, str]], code: str, path: str, message: str) -> None:
    issues.append({"code": code, "path": path, "message": message})


def load_packet(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("packet root must be an object")
    return data


def write_packet(packet: dict[str, Any], path: Path) -> None:
    path.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
