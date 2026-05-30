"""Inactive release activation checklist v2 validation.

This module is intentionally fixture-only. It validates checklist packets used to
prepare a human-reviewed inactive release activation path without activating a
release, promoting artifacts, mutating release state, accessing DevHub, or
claiming live execution.
"""

from __future__ import annotations

import re
from typing import Any, Iterable, Mapping, Sequence

PACKET_VERSION = "inactive-release-activation-checklist-v2"

REQUIRED_ROW_FIELDS = (
    "activation_prerequisites",
    "human_approval_placeholders",
    "rollback_confirmations",
    "validation_transcript_placeholders",
    "no_live_access_attestations",
)

_MUTATION_FIELD_NAMES = {
    "active_promotion",
    "active_promotion_enabled",
    "active_release_state_mutation",
    "apply_release",
    "promote_release",
    "promotion_enabled",
    "release_activation_enabled",
    "release_state_mutation",
    "release_state_update_enabled",
}
_MUTATION_FIELD_RE = re.compile(
    r"(^|_)(active_)?(promotion|release_state|release)_(activation|mutation|promotion|update|write|enabled)(_|$)|"
    r"(^|_)(activate|apply|promote|mutate|update)_(release|release_state|promotion)(_|$)",
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
_LIVE_EXECUTION_RE = re.compile(
    r"\b(live execution|live crawl|live browser|live devhub|live run|ran live|performed live|accessed devhub|"
    r"logged in|authenticated session|used live source|used live sources)\b",
    re.IGNORECASE,
)
_OFFICIAL_ACTION_RE = re.compile(
    r"\b(official action performed|submitted|submission completed|paid the fee|paid fee|payment completed|scheduled inspection|"
    r"cancelled inspection|canceled inspection|certified application|uploaded corrections|uploaded plans|activated release|"
    r"release activated|promoted release)\b",
    re.IGNORECASE,
)
_GUARANTEE_RE = re.compile(
    r"\b(guaranteed approval|guaranteed issuance|permit will be approved|permit will be issued|approval is guaranteed|"
    r"issuance is guaranteed|legal advice|legal guarantee|permitting guarantee|permit outcome is guaranteed)\b",
    re.IGNORECASE,
)
_COMMAND_FORBIDDEN_RE = re.compile(r"\b(live|crawl|devhub|playwright|browser|network|auth|session|activate|promote|release-state)\b", re.IGNORECASE)


def validate_inactive_release_activation_checklist_v2(packet: Mapping[str, Any]) -> list[dict[str, str]]:
    """Return validation issues for an inactive release activation checklist v2 packet."""

    issues: list[dict[str, str]] = []

    if packet.get("packet_version") != PACKET_VERSION:
        _issue(issues, "invalid_packet_version", "packet_version", f"packet_version must be {PACKET_VERSION}")
    if packet.get("mode") != "inactive-fixture-only":
        _issue(issues, "invalid_mode", "mode", "mode must remain inactive-fixture-only")

    for field in REQUIRED_ROW_FIELDS:
        value = packet.get(field)
        if not isinstance(value, list) or not value:
            _issue(issues, f"missing_{field}", field, f"{field} must be a non-empty list")

    _validate_activation_prerequisites(packet.get("activation_prerequisites"), issues)
    _validate_human_approval_placeholders(packet.get("human_approval_placeholders"), issues)
    _validate_rollback_confirmations(packet.get("rollback_confirmations"), issues)
    _validate_validation_transcript_placeholders(packet.get("validation_transcript_placeholders"), issues)
    _validate_no_live_access_attestations(packet.get("no_live_access_attestations"), issues)
    _validate_validation_commands(packet.get("validation_commands"), issues)
    _scan_for_unsafe_content(packet, "", issues)
    return issues


def assert_valid_inactive_release_activation_checklist_v2(packet: Mapping[str, Any]) -> None:
    issues = validate_inactive_release_activation_checklist_v2(packet)
    if issues:
        formatted = "; ".join(f"{issue['code']} at {issue['path']}" for issue in issues)
        raise ValueError(f"inactive release activation checklist v2 validation failed: {formatted}")


def _validate_activation_prerequisites(value: Any, issues: list[dict[str, str]]) -> None:
    for index, row in enumerate(_mapping_rows(value)):
        path = f"activation_prerequisites[{index}]"
        if not _text(row.get("prerequisite_id")) or not _text(row.get("description")):
            _issue(issues, "invalid_activation_prerequisite", path, "activation prerequisite requires prerequisite_id and description")
        if row.get("status") not in {"pending", "placeholder-only", "not-satisfied"}:
            _issue(issues, "invalid_activation_prerequisite_status", f"{path}.status", "activation prerequisite must remain pending or placeholder-only")
        if row.get("required_before") != "any_release_activation":
            _issue(issues, "invalid_activation_prerequisite_gate", f"{path}.required_before", "activation prerequisite must gate release activation")


def _validate_human_approval_placeholders(value: Any, issues: list[dict[str, str]]) -> None:
    for index, row in enumerate(_mapping_rows(value)):
        path = f"human_approval_placeholders[{index}]"
        if row.get("status") != "not-approved" or row.get("required_before_activation") is not True:
            _issue(issues, "invalid_human_approval_placeholder", path, "human approval placeholder must remain not-approved and required before activation")
        if row.get("approval_record") is not None:
            _issue(issues, "invalid_human_approval_record", f"{path}.approval_record", "approval record must remain empty in inactive checklist")


def _validate_rollback_confirmations(value: Any, issues: list[dict[str, str]]) -> None:
    for index, row in enumerate(_mapping_rows(value)):
        path = f"rollback_confirmations[{index}]"
        if not _text(row.get("rollback_plan_reference")):
            _issue(issues, "missing_rollback_confirmation", f"{path}.rollback_plan_reference", "rollback confirmation requires a rollback plan reference")
        if row.get("confirmation_status") != "pending-human-confirmation":
            _issue(issues, "invalid_rollback_confirmation", f"{path}.confirmation_status", "rollback confirmation must remain pending human confirmation")


def _validate_validation_transcript_placeholders(value: Any, issues: list[dict[str, str]]) -> None:
    for index, row in enumerate(_mapping_rows(value)):
        path = f"validation_transcript_placeholders[{index}]"
        if row.get("status") != "placeholder-only" or row.get("transcript") is not None:
            _issue(issues, "invalid_validation_transcript_placeholder", path, "validation transcript must remain a placeholder with no transcript content")
        if not _text(row.get("expected_command_group")):
            _issue(issues, "missing_validation_transcript_placeholder", f"{path}.expected_command_group", "validation transcript placeholder requires expected_command_group")


def _validate_no_live_access_attestations(value: Any, issues: list[dict[str, str]]) -> None:
    for index, row in enumerate(_mapping_rows(value)):
        path = f"no_live_access_attestations[{index}]"
        if row.get("attested") is not True or not _text(row.get("basis")):
            _issue(issues, "invalid_no_live_access_attestation", path, "no-live-access attestation must be true and include a basis")


def _validate_validation_commands(value: Any, issues: list[dict[str, str]]) -> None:
    if not isinstance(value, list) or not value:
        _issue(issues, "missing_validation_commands", "validation_commands", "validation commands must be a non-empty argv list collection")
        return
    for index, command in enumerate(value):
        path = f"validation_commands[{index}]"
        if not isinstance(command, list) or not command or not all(isinstance(part, str) and part.strip() for part in command):
            _issue(issues, "invalid_validation_command", path, "validation command must be a non-empty argv string list")
            continue
        if _COMMAND_FORBIDDEN_RE.search(" ".join(command)):
            _issue(issues, "unsafe_validation_command", path, "validation command must not invoke live, crawl, DevHub, browser, network, auth, session, activation, or promotion workflows")


def _scan_for_unsafe_content(value: Any, path: str, issues: list[dict[str, str]]) -> None:
    for child_path, child in _walk(value, path):
        name = _path_name(child_path).lower().replace("-", "_")
        if name and (name in _MUTATION_FIELD_NAMES or _MUTATION_FIELD_RE.search(name)) and _active_flag(child):
            _issue(issues, "active_mutation_flag", child_path, "active promotion or release-state mutation flags are not allowed")
        if name and not name.startswith("no_") and _PRIVATE_FIELD_RE.search(name) and _present_value(child):
            _issue(issues, "private_or_raw_artifact_field", child_path, "private, session, browser, raw, or downloaded artifacts are not allowed")
        if isinstance(child, str):
            if _PRIVATE_TEXT_RE.search(child):
                _issue(issues, "private_or_raw_artifact_text", child_path, "private, session, browser, raw, or downloaded artifact text is not allowed")
            if _LIVE_EXECUTION_RE.search(child):
                _issue(issues, "live_execution_claim", child_path, "live execution claims are not allowed")
            if _OFFICIAL_ACTION_RE.search(child):
                _issue(issues, "consequential_official_action_language", child_path, "consequential official action language is not allowed")
            if _GUARANTEE_RE.search(child):
                _issue(issues, "legal_or_permitting_guarantee", child_path, "legal or permitting guarantees are not allowed")


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


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _issue(issues: list[dict[str, str]], code: str, path: str, message: str) -> None:
    issues.append({"code": code, "path": path, "message": message})
