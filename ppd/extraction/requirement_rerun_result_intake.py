"""Validation for requirement extraction rerun result-intake packets."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Iterable


ID_FIELDS = (
    "requirement_ids",
    "process_ids",
    "guardrail_ids",
)

RAW_REFERENCE_RE = re.compile(
    r"\b(raw[_ -]?(body|html|text|payload|crawl)|download(ed|s)?|archive(d|s)?|browser[_ -]?trace|screenshot)\b",
    re.IGNORECASE,
)
PRIVATE_FACT_RE = re.compile(
    r"\b(private case fact|case-specific fact|applicant name|owner name|tenant name|address|phone|email|permit number|tax lot|parcel)\b",
    re.IGNORECASE,
)
LIVE_EXECUTION_RE = re.compile(
    r"\b(live extraction|live processor|ran extraction|executed processor|called processor|scraped live|fetched live|reran processor)\b",
    re.IGNORECASE,
)
OUTCOME_GUARANTEE_RE = re.compile(
    r"\b(guarantee[sd]?|will be approved|shall be approved|permit approval|permitting outcome|legal outcome|legal advice|compliance guaranteed)\b",
    re.IGNORECASE,
)
MUTATION_FIELD_RE = re.compile(
    r"(mutat|write|publish|release|activate|deploy|promote|update).*(requirement|process|guardrail|prompt|monitor|release[_ -]?state)|"
    r"(requirement|process|guardrail|prompt|monitor|release[_ -]?state).*(mutat|write|publish|release|activate|deploy|promote|update)",
    re.IGNORECASE,
)
ACTIVE_WORD_RE = re.compile(r"\b(true|active|enabled|yes|write|publish|release|activate|deploy|promote|update|mutate)\b", re.IGNORECASE)


class RequirementRerunResultIntakeValidationError(ValueError):
    """Raised when a requirement rerun result-intake packet is invalid."""

    def __init__(self, errors: Iterable[str]) -> None:
        self.errors = list(errors)
        super().__init__("; ".join(self.errors))


def _is_nonempty_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(isinstance(item, str) and item.strip() for item in value)


def _iter_nodes(value: Any, path: str = "$") -> Iterable[tuple[str, Any]]:
    yield path, value
    if isinstance(value, dict):
        for key, child in value.items():
            yield from _iter_nodes(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _iter_nodes(child, f"{path}[{index}]")


def _get_citations(item: dict[str, Any]) -> list[Any]:
    for key in ("citations", "citation_ids", "evidence_ids", "source_citations"):
        value = item.get(key)
        if isinstance(value, list):
            return value
    evidence = item.get("evidence")
    if isinstance(evidence, dict):
        for key in ("citations", "citation_ids", "source_citations"):
            value = evidence.get(key)
            if isinstance(value, list):
                return value
    return []


def _decision_items(packet: dict[str, Any]) -> list[dict[str, Any]]:
    candidates: list[Any] = []
    for key in ("result_decisions", "decisions", "results"):
        if key in packet:
            candidates.append(packet[key])
    result_intake = packet.get("result_intake")
    if isinstance(result_intake, dict):
        for key in ("result_decisions", "decisions", "results"):
            if key in result_intake:
                candidates.append(result_intake[key])

    items: list[dict[str, Any]] = []
    for candidate in candidates:
        if isinstance(candidate, list):
            items.extend(item for item in candidate if isinstance(item, dict))
        elif isinstance(candidate, dict):
            items.append(candidate)
    return items


def validate_requirement_rerun_result_intake_packet(packet: dict[str, Any]) -> list[str]:
    """Return validation errors for a requirement extraction rerun result-intake packet."""

    errors: list[str] = []
    if not isinstance(packet, dict):
        return ["packet must be a JSON object"]

    affected = packet.get("affected")
    if not isinstance(affected, dict):
        affected = packet.get("affected_ids")
    if not isinstance(affected, dict):
        errors.append("affected requirement, process, and guardrail IDs are required")
    else:
        for field in ID_FIELDS:
            if not _is_nonempty_list(affected.get(field)):
                errors.append(f"affected.{field} must contain at least one ID")

    reviewer_owners = packet.get("reviewer_owners")
    reviewers = packet.get("reviewers")
    has_reviewer_owner = _is_nonempty_list(reviewer_owners)
    if isinstance(reviewers, list):
        has_reviewer_owner = has_reviewer_owner or any(
            isinstance(reviewer, dict) and isinstance(reviewer.get("owner"), str) and reviewer["owner"].strip()
            for reviewer in reviewers
        )
    if not has_reviewer_owner:
        errors.append("at least one reviewer owner is required")

    offline_validation = packet.get("offline_validation")
    commands = None
    if isinstance(offline_validation, dict):
        commands = offline_validation.get("commands")
    if commands is None:
        commands = packet.get("offline_validation_commands")
    if not _is_nonempty_list(commands):
        errors.append("offline validation commands are required")

    decisions = _decision_items(packet)
    if not decisions:
        errors.append("at least one cited result decision is required")
    for index, decision in enumerate(decisions):
        citations = _get_citations(decision)
        if not citations or not all(isinstance(citation, str) and citation.strip() for citation in citations):
            errors.append(f"result decision {index} must include citations")

    for path, value in _iter_nodes(packet):
        path_leaf = path.rsplit(".", 1)[-1]
        text = value if isinstance(value, str) else ""
        if isinstance(value, str):
            if RAW_REFERENCE_RE.search(value):
                errors.append(f"raw body, download, archive, or trace reference is prohibited at {path}")
            if PRIVATE_FACT_RE.search(value):
                errors.append(f"private case fact is prohibited at {path}")
            if LIVE_EXECUTION_RE.search(value):
                errors.append(f"live extraction or processor execution claim is prohibited at {path}")
            if OUTCOME_GUARANTEE_RE.search(value):
                errors.append(f"legal or permitting outcome guarantee is prohibited at {path}")
        if RAW_REFERENCE_RE.search(path_leaf):
            errors.append(f"raw body, download, archive, or trace field is prohibited at {path}")
        if PRIVATE_FACT_RE.search(path_leaf):
            errors.append(f"private case fact field is prohibited at {path}")
        if LIVE_EXECUTION_RE.search(path_leaf):
            errors.append(f"live extraction or processor execution field is prohibited at {path}")
        if OUTCOME_GUARANTEE_RE.search(path_leaf):
            errors.append(f"legal or permitting outcome guarantee field is prohibited at {path}")
        if MUTATION_FIELD_RE.search(path_leaf):
            active = value is True or (isinstance(value, str) and ACTIVE_WORD_RE.search(value)) or (isinstance(value, list) and bool(value))
            if active:
                errors.append(f"active mutation flag is prohibited at {path}")
        if isinstance(value, str) and MUTATION_FIELD_RE.search(text) and ACTIVE_WORD_RE.search(text):
            errors.append(f"active mutation claim is prohibited at {path}")

    return list(dict.fromkeys(errors))


def assert_valid_requirement_rerun_result_intake_packet(packet: dict[str, Any]) -> None:
    errors = validate_requirement_rerun_result_intake_packet(packet)
    if errors:
        raise RequirementRerunResultIntakeValidationError(errors)


def load_packet(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        packet = json.load(handle)
    if not isinstance(packet, dict):
        raise RequirementRerunResultIntakeValidationError(["packet must be a JSON object"])
    return packet


def validate_packet_file(path: str | Path) -> list[str]:
    return validate_requirement_rerun_result_intake_packet(load_packet(path))


validate_packet = validate_requirement_rerun_result_intake_packet
assert_valid_packet = assert_valid_requirement_rerun_result_intake_packet
