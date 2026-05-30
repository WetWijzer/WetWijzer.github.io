"""Validation for inactive DevHub surface fixture migration packet v2."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Iterable

PACKET_TYPE = "devhub_surface_fixture_migration_packet"
PACKET_VERSION = 2

_ROW_KEYS = {"surfaces", "surface_rows", "actions", "action_rows", "fixture_rows"}
_CITATION_KEYS = {"citation", "citations", "source", "sources", "source_ref", "source_refs", "evidence", "evidence_refs"}
_DISPOSITION_VALUES = {"manual_handoff", "manual-handoff", "redacted", "redaction"}

_SENSITIVE_KEY_RE = re.compile(
    r"(password|passwd|secret|api[_-]?key|access[_-]?token|refresh[_-]?token|bearer|oauth|credential|cookie|csrf|session[_-]?id|localstorage|sessionstorage)",
    re.IGNORECASE,
)
_PRIVATE_AUTH_KEY_RE = re.compile(r"(private|authenticated|auth[_-]?required|requires[_-]?auth)", re.IGNORECASE)
_ARTIFACT_RE = re.compile(r"(screenshot|playwright-report|trace\.zip|\.har\b|\.png\b|\.jpe?g\b|\.webm\b)", re.IGNORECASE)
_AUTOMATION_RE = re.compile(r"(playwright|selenium|puppeteer|browser automation|live devhub|completed in devhub|clicked submit|submitted live)", re.IGNORECASE)
_OUTCOME_RE = re.compile(r"(guaranteed approval|approval guaranteed|permit guaranteed|guaranteed permit|permit issued|legally binding|will be approved|outcome guarantee)", re.IGNORECASE)
_CONSEQUENTIAL_RE = re.compile(r"(submit application|file permit|pay fee|make payment|schedule inspection|enable consequential|consequential action)", re.IGNORECASE)
_MUTATION_KEY_RE = re.compile(r"(surface[_-]?registry|guardrail|prompt|monitoring|release[_-]?state|agent[_-]?state).*?(mutation|mutate|write|active|enable)", re.IGNORECASE)


def load_packet(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        packet = json.load(handle)
    if not isinstance(packet, dict):
        raise ValueError("packet must be a JSON object")
    return packet


def validate_file(path: str | Path) -> list[str]:
    return validate_packet(load_packet(path))


def validate_devhub_surface_fixture_packet_v2(packet: dict[str, Any]) -> list[str]:
    return validate_packet(packet)


def validate_packet(packet: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if packet.get("packet_type") != PACKET_TYPE:
        errors.append("packet_type must identify a DevHub surface fixture migration packet")
    if packet.get("packet_version") != PACKET_VERSION:
        errors.append("packet_version must be 2")
    if packet.get("status") != "inactive":
        errors.append("packet status must be inactive")

    rows = list(_iter_fixture_rows(packet))
    if not rows:
        errors.append("packet must include surface/action fixture rows")
    for path, row in rows:
        _validate_row(path, row, errors)

    _scan_tree(packet, "$", errors)
    return sorted(set(errors))


def is_valid(packet: dict[str, Any]) -> bool:
    return not validate_packet(packet)


def _iter_fixture_rows(value: Any, path: str = "$") -> Iterable[tuple[str, dict[str, Any]]]:
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in _ROW_KEYS and isinstance(child, list):
                for index, item in enumerate(child):
                    if isinstance(item, dict):
                        yield f"{child_path}[{index}]", item
            yield from _iter_fixture_rows(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _iter_fixture_rows(child, f"{path}[{index}]")


def _validate_row(path: str, row: dict[str, Any], errors: list[str]) -> None:
    if not _has_citation(row):
        errors.append(f"{path} is missing a citation or evidence reference")
    if not _has_selector_confidence_checks(row):
        errors.append(f"{path} is missing selector-confidence before/after checks")
    if not _has_manual_handoff_or_redaction(row):
        errors.append(f"{path} is missing manual-handoff or redaction disposition")


def _has_citation(row: dict[str, Any]) -> bool:
    for key in _CITATION_KEYS:
        if _present(row.get(key)):
            return True
    return False


def _has_selector_confidence_checks(row: dict[str, Any]) -> bool:
    confidence = row.get("selector_confidence") or row.get("selector-confidence")
    if isinstance(confidence, dict):
        before = confidence.get("before_check") or confidence.get("before")
        after = confidence.get("after_check") or confidence.get("after")
        if _present(before) and _present(after):
            return True
    return _present(row.get("selector_confidence_before")) and _present(row.get("selector_confidence_after"))


def _has_manual_handoff_or_redaction(row: dict[str, Any]) -> bool:
    values = [row.get("disposition"), row.get("manual_handoff"), row.get("redaction_disposition")]
    return any(isinstance(value, str) and value.lower() in _DISPOSITION_VALUES for value in values)


def _present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict, tuple, set)):
        return bool(value)
    return True


def _scan_tree(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            key_text = str(key)
            if _SENSITIVE_KEY_RE.search(key_text):
                errors.append(f"{child_path} contains credential, session, or auth artifact metadata")
            if _PRIVATE_AUTH_KEY_RE.search(key_text) and child not in (False, None, "", [], {}):
                errors.append(f"{child_path} contains private or authenticated DevHub value metadata")
            if _MUTATION_KEY_RE.search(key_text) and child is True:
                errors.append(f"{child_path} enables active registry, guardrail, prompt, monitoring, release-state, or agent-state mutation")
            if key_text in {"consequential_actions_enabled", "enable_consequential_actions", "live_completion_claim"} and child is True:
                errors.append(f"{child_path} enables prohibited live or consequential behavior")
            _scan_tree(child, child_path, errors)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _scan_tree(child, f"{path}[{index}]", errors)
    elif isinstance(value, str):
        _scan_string(value, path, errors)


def _scan_string(text: str, path: str, errors: list[str]) -> None:
    checks = [
        (_SENSITIVE_KEY_RE, "contains credential, session, or auth artifact"),
        (_ARTIFACT_RE, "references screenshots, traces, HAR files, or captured browser media"),
        (_AUTOMATION_RE, "claims browser automation or live DevHub completion"),
        (_OUTCOME_RE, "claims legal or permitting outcome guarantee"),
        (_CONSEQUENTIAL_RE, "enables consequential permitting action"),
    ]
    for pattern, message in checks:
        if pattern.search(text):
            errors.append(f"{path} {message}")
