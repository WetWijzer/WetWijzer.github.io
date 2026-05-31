"""Fail-closed validation for stale-source re-extraction readiness packets v2.

The packet is a reviewer planning artifact only. It must carry enough
placeholder and disposition structure to prove that stale source rows are not
being promoted, refreshed, recompiled, or mutated from a fixture-first review.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any


PACKET_VERSION = "stale-source-reextraction-readiness-packet-v2"

REQUIRED_LIST_SECTIONS = (
    "candidate_rows",
    "source_evidence_refresh_placeholders",
    "stale_hold_carry_forward_notes",
    "requirement_review_placeholders",
    "guardrail_recompile_prerequisites",
    "reviewer_dispositions",
    "validation_commands",
)

REQUIRED_VALIDATION_COMMANDS = (
    ("python3", "-m", "unittest", "ppd.tests.test_stale_source_reextraction_readiness_packet_v2"),
    ("python3", "ppd/daemon/ppd_daemon.py", "--self-test"),
)

ACTIVE_MUTATION_KEYS = {
    "active_source_mutation",
    "source_mutation_enabled",
    "active_requirement_mutation",
    "requirement_mutation_enabled",
    "active_guardrail_mutation",
    "guardrail_mutation_enabled",
    "active_prompt_mutation",
    "prompt_mutation_enabled",
    "active_contract_mutation",
    "contract_mutation_enabled",
    "active_devhub_surface_mutation",
    "devhub_surface_mutation_enabled",
    "active_release_state_mutation",
    "release_state_mutation_enabled",
}

MUTATION_KEY_RE = re.compile(
    r"(^|_)(active_)?(source|requirement|guardrail|prompt|contract|devhub_surface|devhub[-_ ]surface|release_state|release[-_ ]state)_.*(mutation|mutate|write|update|promote|enable|apply)",
    re.IGNORECASE,
)
RAW_BODY_RE = re.compile(
    r"\b(raw[-_ ]?(downloaded[-_ ]?)?(body|crawl|html|pdf|document|download)|downloaded[-_ ]?(body|document|file|pdf)|crawl[-_ ]?output|warc)\b",
    re.IGNORECASE,
)
LIVE_CLAIM_RE = re.compile(
    r"\b(live[-_ ]?crawl|live[-_ ]?refresh|recrawl|live[-_ ]?devhub|devhub[-_ ]?(crawl|automation|execution|login|session))\b.{0,80}\b(complete|completed|succeeded|finished|executed|ran|opened|done|claimed)\b|\b(opened|ran|executed|completed)\b.{0,80}\b(live[-_ ]?devhub|live[-_ ]?crawl)\b",
    re.IGNORECASE,
)
GUARANTEE_RE = re.compile(
    r"\b(guarantee|guaranteed|approval guaranteed|will be approved|permit will issue|permit will be issued|legally sufficient|legal advice|complies with all code|meets all legal requirements|permitting outcome is assured)\b",
    re.IGNORECASE,
)
ACTIVE_MUTATION_TEXT_RE = re.compile(
    r"\b(active|apply|enable|mutate|promote|publish|replace|update|write)\b.{0,80}\b(source|requirement|guardrail|prompt|contract|devhub[-_ ]?surface|release[-_ ]?state)\b",
    re.IGNORECASE,
)


class StaleSourceReextractionReadinessPacketV2Error(ValueError):
    """Raised when a stale-source re-extraction readiness packet is unsafe."""

    def __init__(self, issues: Sequence[str]) -> None:
        self.issues = tuple(issues)
        super().__init__("; ".join(self.issues))


def validate_stale_source_reextraction_readiness_packet_v2(packet: Mapping[str, Any]) -> list[str]:
    """Return deterministic rejection reasons for an unsafe packet."""

    issues: list[str] = []

    if packet.get("version") != PACKET_VERSION:
        issues.append("version must be " + PACKET_VERSION)

    for section in REQUIRED_LIST_SECTIONS:
        value = packet.get(section)
        if not isinstance(value, list) or not value:
            issues.append(f"missing or empty {section}")

    rows = _mapping_list(packet.get("candidate_rows"))
    refresh_placeholders = _items_by_id(packet.get("source_evidence_refresh_placeholders"), "placeholder_id")
    carry_notes = _items_by_id(packet.get("stale_hold_carry_forward_notes"), "note_id")
    review_placeholders = _items_by_id(packet.get("requirement_review_placeholders"), "placeholder_id")
    prerequisites = _items_by_id(packet.get("guardrail_recompile_prerequisites"), "prerequisite_id")
    dispositions = _items_by_id(packet.get("reviewer_dispositions"), "disposition_id")

    _validate_candidate_rows(issues, rows, refresh_placeholders, carry_notes, review_placeholders, prerequisites, dispositions)
    _validate_refresh_placeholders(issues, refresh_placeholders.values())
    _validate_carry_notes(issues, carry_notes.values())
    _validate_requirement_review_placeholders(issues, review_placeholders.values())
    _validate_guardrail_prerequisites(issues, prerequisites.values())
    _validate_reviewer_dispositions(issues, dispositions.values())
    _validate_commands(issues, packet.get("validation_commands"))
    _reject_active_mutation_flags(issues, packet)
    _reject_forbidden_text(issues, packet)

    return sorted(set(issues))


def assert_valid_stale_source_reextraction_readiness_packet_v2(packet: Mapping[str, Any]) -> None:
    """Raise when a stale-source re-extraction readiness packet is unsafe."""

    issues = validate_stale_source_reextraction_readiness_packet_v2(packet)
    if issues:
        raise StaleSourceReextractionReadinessPacketV2Error(issues)


def _validate_candidate_rows(
    issues: list[str],
    rows: Sequence[Mapping[str, Any]],
    refresh_placeholders: Mapping[str, Mapping[str, Any]],
    carry_notes: Mapping[str, Mapping[str, Any]],
    review_placeholders: Mapping[str, Mapping[str, Any]],
    prerequisites: Mapping[str, Mapping[str, Any]],
    dispositions: Mapping[str, Mapping[str, Any]],
) -> None:
    seen: set[str] = set()
    orders: list[int] = []
    for row in rows:
        row_id = _text(row.get("candidate_id"))
        if not row_id:
            issues.append("candidate row missing candidate_id")
            row_id = ""
        elif row_id in seen:
            issues.append("duplicate candidate row " + row_id)
        else:
            seen.add(row_id)

        order = row.get("order")
        if not isinstance(order, int):
            issues.append(f"candidate row {row_id} order must be an integer")
        else:
            orders.append(order)

        if not _text(row.get("source_id")):
            issues.append(f"candidate row {row_id} missing source_id")
        if row.get("stale_status") not in {"stale", "expired", "superseded"}:
            issues.append(f"candidate row {row_id} stale_status must identify stale source state")

        _require_references(issues, row, row_id, "source_evidence_refresh_placeholder_ids", refresh_placeholders, "source-evidence refresh placeholder")
        _require_references(issues, row, row_id, "stale_hold_carry_forward_note_ids", carry_notes, "stale-hold carry-forward note")
        _require_references(issues, row, row_id, "requirement_review_placeholder_ids", review_placeholders, "requirement-review placeholder")
        _require_references(issues, row, row_id, "guardrail_recompile_prerequisite_ids", prerequisites, "guardrail-recompile prerequisite")
        _require_references(issues, row, row_id, "reviewer_disposition_ids", dispositions, "reviewer disposition")

    if orders and sorted(orders) != list(range(1, len(orders) + 1)):
        issues.append("candidate_rows order must be contiguous starting at 1")


def _validate_refresh_placeholders(issues: list[str], placeholders: Sequence[Mapping[str, Any]]) -> None:
    for placeholder in placeholders:
        placeholder_id = _text(placeholder.get("placeholder_id"))
        if not _text(placeholder.get("candidate_id")):
            issues.append(f"source-evidence refresh placeholder {placeholder_id} missing candidate_id")
        if not _text(placeholder.get("placeholder")).startswith("placeholder:"):
            issues.append(f"source-evidence refresh placeholder must stay placeholder-only for {placeholder_id}")
        if placeholder.get("live_fetch_allowed") is not False:
            issues.append(f"source-evidence refresh placeholder {placeholder_id} must disable live fetch")
        if placeholder.get("raw_body_persistence_allowed") is not False:
            issues.append(f"source-evidence refresh placeholder {placeholder_id} must disable raw body persistence")


def _validate_carry_notes(issues: list[str], notes: Sequence[Mapping[str, Any]]) -> None:
    for note in notes:
        note_id = _text(note.get("note_id"))
        if not _text(note.get("candidate_id")) or not _text(note.get("note")):
            issues.append(f"stale-hold carry-forward note {note_id} must include candidate_id and note")
        if note.get("hold_carries_forward") is not True:
            issues.append(f"stale-hold carry-forward note {note_id} must carry the hold forward")
        if note.get("release_blocked_until_review") is not True:
            issues.append(f"stale-hold carry-forward note {note_id} must block release until review")


def _validate_requirement_review_placeholders(issues: list[str], placeholders: Sequence[Mapping[str, Any]]) -> None:
    for placeholder in placeholders:
        placeholder_id = _text(placeholder.get("placeholder_id"))
        if not _text(placeholder.get("candidate_id")):
            issues.append(f"requirement-review placeholder {placeholder_id} missing candidate_id")
        if not _text(placeholder.get("placeholder")).startswith("placeholder:"):
            issues.append(f"requirement-review placeholder must stay placeholder-only for {placeholder_id}")
        if placeholder.get("human_review_required") is not True:
            issues.append(f"requirement-review placeholder {placeholder_id} must require human review")


def _validate_guardrail_prerequisites(issues: list[str], prerequisites: Sequence[Mapping[str, Any]]) -> None:
    for prerequisite in prerequisites:
        prerequisite_id = _text(prerequisite.get("prerequisite_id"))
        if not _text(prerequisite.get("candidate_id")) or not _text(prerequisite.get("prerequisite")):
            issues.append(f"guardrail-recompile prerequisite {prerequisite_id} must include candidate_id and prerequisite")
        if prerequisite.get("satisfied") is not False:
            issues.append(f"guardrail-recompile prerequisite {prerequisite_id} must remain unsatisfied")
        if prerequisite.get("recompile_blocked") is not True:
            issues.append(f"guardrail-recompile prerequisite {prerequisite_id} must block recompilation")


def _validate_reviewer_dispositions(issues: list[str], dispositions: Sequence[Mapping[str, Any]]) -> None:
    for disposition in dispositions:
        disposition_id = _text(disposition.get("disposition_id"))
        if not _text(disposition.get("candidate_id")):
            issues.append(f"reviewer disposition {disposition_id} missing candidate_id")
        if disposition.get("disposition") != "pending_reviewer_disposition":
            issues.append(f"reviewer disposition {disposition_id} must remain pending")
        if disposition.get("mutation_allowed") is not False:
            issues.append(f"reviewer disposition {disposition_id} must not allow mutation")


def _validate_commands(issues: list[str], value: Any) -> None:
    commands = _command_tuples(value)
    for required in REQUIRED_VALIDATION_COMMANDS:
        if required not in commands:
            issues.append("missing validation command: " + " ".join(required))
    for command in commands:
        joined = " ".join(command).lower()
        if any(term in joined for term in ("curl", "wget", "playwright", "browser", "devhub.portlandoregon.gov")):
            issues.append("validation commands must remain offline and fixture-first")


def _reject_active_mutation_flags(issues: list[str], packet: Mapping[str, Any]) -> None:
    for path, key, value in _walk_key_values(packet):
        if key in ACTIVE_MUTATION_KEYS or MUTATION_KEY_RE.search(key):
            if value is not False:
                issues.append(f"active mutation flag must be false at {path}")


def _reject_forbidden_text(issues: list[str], packet: Mapping[str, Any]) -> None:
    for path, text in _walk_strings(packet):
        if RAW_BODY_RE.search(text):
            issues.append(f"raw downloaded body artifact rejected at {path}")
        if LIVE_CLAIM_RE.search(text):
            issues.append(f"live crawl or DevHub claim rejected at {path}")
        if GUARANTEE_RE.search(text):
            issues.append(f"legal or permitting guarantee rejected at {path}")
        if ACTIVE_MUTATION_TEXT_RE.search(text):
            issues.append(f"active mutation language rejected at {path}")


def _require_references(
    issues: list[str],
    row: Mapping[str, Any],
    row_id: str,
    field: str,
    known: Mapping[str, Mapping[str, Any]],
    label: str,
) -> None:
    refs = _string_list(row.get(field))
    if not refs:
        issues.append(f"missing {label} references for {row_id}")
        return
    for ref in refs:
        if ref not in known:
            issues.append(f"unknown {label} {ref} for {row_id}")


def _items_by_id(value: Any, id_key: str) -> dict[str, Mapping[str, Any]]:
    items: dict[str, Mapping[str, Any]] = {}
    for item in _mapping_list(value):
        item_id = item.get(id_key)
        if isinstance(item_id, str) and item_id:
            items[item_id] = item
    return items


def _mapping_list(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str) and item]


def _command_tuples(value: Any) -> set[tuple[str, ...]]:
    commands: set[tuple[str, ...]] = set()
    if not isinstance(value, list):
        return commands
    for command in value:
        if isinstance(command, list) and command and all(isinstance(part, str) and part for part in command):
            commands.add(tuple(command))
        else:
            commands.add(("",))
    return commands


def _walk_strings(value: Any, path: str = "packet") -> list[tuple[str, str]]:
    if isinstance(value, str):
        return [(path, value)]
    if isinstance(value, Mapping):
        hits: list[tuple[str, str]] = []
        for key, child in value.items():
            hits.extend(_walk_strings(child, f"{path}.{key}"))
        return hits
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        hits = []
        for index, child in enumerate(value):
            hits.extend(_walk_strings(child, f"{path}[{index}]"))
        return hits
    return []


def _walk_key_values(value: Any, path: str = "packet") -> list[tuple[str, str, Any]]:
    if isinstance(value, Mapping):
        rows: list[tuple[str, str, Any]] = []
        for key, child in value.items():
            child_path = f"{path}.{key}"
            rows.append((child_path, str(key), child))
            rows.extend(_walk_key_values(child, child_path))
        return rows
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        rows = []
        for index, child in enumerate(value):
            rows.extend(_walk_key_values(child, f"{path}[{index}]"))
        return rows
    return []


def _text(value: Any) -> str:
    return value if isinstance(value, str) else ""
