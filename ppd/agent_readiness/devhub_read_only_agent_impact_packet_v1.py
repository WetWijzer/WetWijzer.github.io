"""Validation for DevHub read-only agent impact packet v1.

The packet is a commit-safe, offline impact artifact for read-only DevHub agent
rehearsals. It must include the rows an agent consumer needs to understand
surface deltas, missing-information impact, blocked predicates, next safe
actions, reversible draft limits, exact-confirmation warnings, source/citation
placeholders, reviewer holds, and validation commands. It must reject private
browser/session artifacts, live DevHub or crawl claims, official-action claims,
consequential-action claims, legal/permitting guarantees, and active mutation
flags.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

PACKET_TYPE = "ppd.devhub_read_only_agent_impact_packet.v1"
PACKET_VERSION = "v1"

EXACT_VALIDATION_COMMANDS = [
    ["python3", "-m", "py_compile", "ppd/agent_readiness/devhub_read_only_agent_impact_packet_v1.py"],
    ["python3", "-m", "pytest", "ppd/tests/test_devhub_read_only_agent_impact_packet_v1.py"],
    ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
]

_REQUIRED_SEQUENCE_FIELDS = (
    "surface_delta_refs",
    "affected_missing_information_rows",
    "blocked_action_predicate_rows",
    "next_safe_action_rows",
    "reversible_draft_eligibility_notes",
    "exact_confirmation_warnings",
    "citation_source_placeholders",
    "reviewer_holds",
    "validation_commands",
)

_REQUIRED_FALSE_ATTESTATIONS = (
    "active_contract_mutation",
    "active_guardrail_mutation",
    "active_process_mutation",
    "active_prompt_mutation",
    "active_release_state_mutation",
    "active_requirement_mutation",
    "active_source_mutation",
    "active_surface_map_mutation",
    "consequential_action_performed",
    "devhub_accessed",
    "legal_or_permitting_guarantee_made",
    "live_crawl_performed",
    "live_devhub_claim_made",
    "official_action_completed",
)

_MUTATION_KEYS = frozenset(
    {
        "active_contract_mutation",
        "active_guardrail_mutation",
        "active_process_mutation",
        "active_prompt_mutation",
        "active_release_state_mutation",
        "active_requirement_mutation",
        "active_source_mutation",
        "active_surface_map_mutation",
        "contract_mutation",
        "contract_mutation_enabled",
        "guardrail_mutation",
        "guardrail_mutation_enabled",
        "mutates_contract",
        "mutates_contracts",
        "mutates_guardrail",
        "mutates_guardrails",
        "mutates_process",
        "mutates_processes",
        "mutates_prompt",
        "mutates_prompts",
        "mutates_release_state",
        "mutates_requirement",
        "mutates_requirements",
        "mutates_source",
        "mutates_sources",
        "mutates_surface_map",
        "mutates_surface_maps",
        "process_mutation",
        "process_mutation_enabled",
        "prompt_mutation",
        "prompt_mutation_enabled",
        "release_state_mutation",
        "release_state_mutation_enabled",
        "requirement_mutation",
        "requirement_mutation_enabled",
        "source_mutation",
        "source_mutation_enabled",
        "surface_map_mutation",
        "surface_map_mutation_enabled",
    }
)

_PRIVATE_KEY_TOKENS = (
    "auth",
    "browser",
    "captcha",
    "cookie",
    "credential",
    "download",
    "downloaded",
    "har",
    "local_path",
    "mfa",
    "password",
    "payment",
    "private",
    "raw",
    "screenshot",
    "secret",
    "session",
    "storage_state",
    "token",
    "trace",
)

_PRIVATE_VALUE_TOKENS = (
    "auth state",
    "browser artifact",
    "browser context",
    "browser state",
    "cookie",
    "credential",
    "devhub session",
    "downloaded document",
    "downloaded pdf",
    "har file",
    "local private path",
    "network trace",
    "password",
    "payment detail",
    "private artifact",
    "private value",
    "raw authenticated html",
    "raw body",
    "raw crawl",
    "raw download",
    "raw html",
    "raw pdf",
    "screenshot",
    "session artifact",
    "session state",
    "session storage",
    "storage state",
    "trace file",
    "trace.zip",
)

_LIVE_CLAIM_TOKENS = (
    "completed authenticated run",
    "devhub was updated",
    "executed in devhub",
    "live crawl completed",
    "live devhub confirmed",
    "live devhub observation",
    "logged into devhub and ran",
    "ran against live devhub",
)

_OFFICIAL_OR_CONSEQUENTIAL_TOKENS = (
    "agent may certify",
    "agent may pay",
    "agent may schedule",
    "agent may submit",
    "agent may upload",
    "cancel inspection",
    "cancel permit",
    "certification submitted",
    "certify acknowledgement",
    "click submit",
    "official action completed",
    "official upload",
    "paid fee",
    "pay fee",
    "pay fees",
    "purchase permit",
    "schedule inspection",
    "submit application",
    "submit payment",
    "submit permit",
    "submitted application",
    "submitted permit",
    "upload correction",
    "upload corrections",
    "withdraw application",
)

_GUARANTEE_TOKENS = (
    "approval guaranteed",
    "guarantee approval",
    "guaranteed approval",
    "guaranteed issuance",
    "guaranteed permit",
    "legal advice",
    "legal guarantee",
    "legally compliant",
    "permit approved",
    "permit guaranteed",
    "permit issued",
    "permit will be approved",
    "permit will be issued",
    "permit will issue",
    "will be approved",
    "will be issued",
    "will satisfy the city",
)


@dataclass(frozen=True)
class DevHubReadOnlyAgentImpactPacketV1ValidationResult:
    valid: bool
    problems: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {"valid": self.valid, "problems": list(self.problems)}


class DevHubReadOnlyAgentImpactPacketV1Error(ValueError):
    def __init__(self, problems: Iterable[str]) -> None:
        self.problems = tuple(problems)
        super().__init__("invalid devhub read-only agent impact packet v1: " + "; ".join(self.problems))


def validate_devhub_read_only_agent_impact_packet_v1(
    packet: Mapping[str, Any],
) -> DevHubReadOnlyAgentImpactPacketV1ValidationResult:
    problems: list[str] = []
    if not isinstance(packet, Mapping):
        return DevHubReadOnlyAgentImpactPacketV1ValidationResult(False, ("packet must be an object",))

    if packet.get("packet_type") != PACKET_TYPE:
        problems.append(f"packet_type must be {PACKET_TYPE}")
    if packet.get("packet_version") != PACKET_VERSION:
        problems.append(f"packet_version must be {PACKET_VERSION}")
    if packet.get("fixture_only") is not True:
        problems.append("fixture_only must be true")
    if packet.get("read_only") is not True:
        problems.append("read_only must be true")

    for field in _REQUIRED_SEQUENCE_FIELDS:
        if not _mapping_sequence(packet.get(field)) and field != "validation_commands":
            problems.append(f"{field} must be a non-empty list")
    if packet.get("validation_commands") != EXACT_VALIDATION_COMMANDS:
        problems.append("validation_commands must match exact DevHub read-only agent impact packet v1 validation commands")

    surface_refs = _validate_surface_delta_refs(packet.get("surface_delta_refs"), problems)
    missing_row_ids = _validate_rows(
        packet.get("affected_missing_information_rows"),
        "affected_missing_information_rows",
        "missing_information_row_id",
        surface_refs,
        problems,
    )
    blocked_row_ids = _validate_rows(
        packet.get("blocked_action_predicate_rows"),
        "blocked_action_predicate_rows",
        "predicate_id",
        surface_refs,
        problems,
    )
    next_action_ids = _validate_rows(
        packet.get("next_safe_action_rows"),
        "next_safe_action_rows",
        "next_safe_action_id",
        surface_refs,
        problems,
    )
    note_ids = _validate_rows(
        packet.get("reversible_draft_eligibility_notes"),
        "reversible_draft_eligibility_notes",
        "note_id",
        surface_refs,
        problems,
    )
    warning_ids = _validate_rows(
        packet.get("exact_confirmation_warnings"),
        "exact_confirmation_warnings",
        "warning_id",
        surface_refs,
        problems,
    )
    citation_ids = _validate_citation_source_placeholders(packet.get("citation_source_placeholders"), surface_refs, problems)
    _validate_reviewer_holds(
        packet.get("reviewer_holds"),
        missing_row_ids | blocked_row_ids | next_action_ids | note_ids | warning_ids | citation_ids,
        problems,
    )
    _validate_attestations(packet.get("attestations"), problems)
    _validate_no_forbidden_payload(packet, problems)

    return DevHubReadOnlyAgentImpactPacketV1ValidationResult(not problems, tuple(problems))


def assert_valid_devhub_read_only_agent_impact_packet_v1(packet: Mapping[str, Any]) -> None:
    result = validate_devhub_read_only_agent_impact_packet_v1(packet)
    if not result.valid:
        raise DevHubReadOnlyAgentImpactPacketV1Error(result.problems)


def _validate_surface_delta_refs(value: Any, problems: list[str]) -> set[str]:
    rows = _mapping_sequence(value)
    refs: set[str] = set()
    for index, row in enumerate(rows):
        prefix = f"surface_delta_refs[{index}]"
        ref = _text(row.get("surface_delta_ref"))
        if not ref:
            problems.append(f"{prefix}.surface_delta_ref is required")
        else:
            refs.add(ref)
        if not _text(row.get("surface_id")):
            problems.append(f"{prefix}.surface_id is required")
        if row.get("read_only") is not True:
            problems.append(f"{prefix}.read_only must be true")
        if row.get("active_surface_map_mutation") is not False:
            problems.append(f"{prefix}.active_surface_map_mutation must be false")
    return refs


def _validate_rows(value: Any, field: str, id_field: str, surface_refs: set[str], problems: list[str]) -> set[str]:
    rows = _mapping_sequence(value)
    ids: set[str] = set()
    for index, row in enumerate(rows):
        prefix = f"{field}[{index}]"
        row_id = _text(row.get(id_field))
        if not row_id:
            problems.append(f"{prefix}.{id_field} is required")
        else:
            ids.add(row_id)
        _require_surface_delta_ref(row, prefix, surface_refs, problems)
        if not _text(row.get("description")) and not _text(row.get("note")) and not _text(row.get("action_label")):
            problems.append(f"{prefix} must include description, note, or action_label")
        if not _text(row.get("reviewer_hold_ref")):
            problems.append(f"{prefix}.reviewer_hold_ref is required")
    return ids


def _validate_citation_source_placeholders(value: Any, surface_refs: set[str], problems: list[str]) -> set[str]:
    rows = _mapping_sequence(value)
    ids: set[str] = set()
    for index, row in enumerate(rows):
        prefix = f"citation_source_placeholders[{index}]"
        placeholder_id = _text(row.get("placeholder_id"))
        if not placeholder_id:
            problems.append(f"{prefix}.placeholder_id is required")
        else:
            ids.add(placeholder_id)
        _require_surface_delta_ref(row, prefix, surface_refs, problems)
        if not _text(row.get("source_id")):
            problems.append(f"{prefix}.source_id is required")
        if row.get("citation_status") != "pending_source_resolution":
            problems.append(f"{prefix}.citation_status must be pending_source_resolution")
        if not _text(row.get("reviewer_hold_ref")):
            problems.append(f"{prefix}.reviewer_hold_ref is required")
    return ids


def _validate_reviewer_holds(value: Any, referenced_row_ids: set[str], problems: list[str]) -> None:
    rows = _mapping_sequence(value)
    hold_ids: set[str] = set()
    covered_row_ids: set[str] = set()
    for index, row in enumerate(rows):
        prefix = f"reviewer_holds[{index}]"
        hold_id = _text(row.get("hold_id"))
        if not hold_id:
            problems.append(f"{prefix}.hold_id is required")
        else:
            hold_ids.add(hold_id)
        row_id = _text(row.get("row_id"))
        if not row_id:
            problems.append(f"{prefix}.row_id is required")
        else:
            covered_row_ids.add(row_id)
        if row.get("decision") != "pending_manual_review":
            problems.append(f"{prefix}.decision must be pending_manual_review")
        if row.get("reviewer") not in ("", None) or row.get("reviewed_at") not in ("", None):
            problems.append(f"{prefix} must remain an unsigned reviewer hold")
    if referenced_row_ids and not referenced_row_ids.issubset(covered_row_ids):
        missing = sorted(referenced_row_ids - covered_row_ids)
        problems.append("reviewer_holds must cover every impacted row: " + ", ".join(missing))
    if len(hold_ids) != len(rows):
        problems.append("reviewer_holds.hold_id values must be unique")


def _validate_attestations(value: Any, problems: list[str]) -> None:
    attestations = value if isinstance(value, Mapping) else {}
    if not attestations:
        problems.append("attestations must be present")
    for key in _REQUIRED_FALSE_ATTESTATIONS:
        if attestations.get(key) is not False:
            problems.append(f"attestations.{key} must be false")


def _require_surface_delta_ref(row: Mapping[str, Any], prefix: str, surface_refs: set[str], problems: list[str]) -> None:
    ref = _text(row.get("surface_delta_ref"))
    if not ref:
        problems.append(f"{prefix}.surface_delta_ref is required")
    elif surface_refs and ref not in surface_refs:
        problems.append(f"{prefix}.surface_delta_ref must reference surface_delta_refs")


def _validate_no_forbidden_payload(packet: Mapping[str, Any], problems: list[str]) -> None:
    for path, key, value in _walk(packet):
        normalized_key = key.lower().replace("-", "_")
        if normalized_key in _MUTATION_KEYS and value is not False:
            problems.append(f"{path} must be false")
        if any(token in normalized_key for token in _PRIVATE_KEY_TOKENS) and _truthy(value):
            problems.append(f"{path} must not include credentials, sessions, browser artifacts, screenshots, traces, HAR files, private artifacts, or raw crawl output")
        if isinstance(value, str):
            text = value.lower()
            if any(token in text for token in _PRIVATE_VALUE_TOKENS):
                problems.append(f"{path} must not reference credentials, sessions, browser artifacts, screenshots, traces, HAR files, private artifacts, or raw crawl output")
            if any(token in text for token in _LIVE_CLAIM_TOKENS):
                problems.append(f"{path} must not include live DevHub or crawl claims")
            if any(token in text for token in _OFFICIAL_OR_CONSEQUENTIAL_TOKENS):
                problems.append(f"{path} must not include official-action completion or consequential-action claims")
            if any(token in text for token in _GUARANTEE_TOKENS):
                problems.append(f"{path} must not include legal or permitting guarantees")


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


def _truthy(value: Any) -> bool:
    if value is None or value is False or value == "":
        return False
    if isinstance(value, Mapping) and not value:
        return False
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)) and not value:
        return False
    return True


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) and value.strip() else ""
