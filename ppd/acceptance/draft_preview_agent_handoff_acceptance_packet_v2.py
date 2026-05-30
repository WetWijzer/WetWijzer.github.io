"""Fixture-first draft preview agent handoff acceptance packet v2.

This module consumes committed PP&D fixtures only. It does not call live LLMs,
open DevHub, read private documents, write PDFs, inspect prompts, or mutate
release state. The output is a deterministic consumer handoff acceptance packet
with cited accepted, deferred, and rejected decisions.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

PACKET_TYPE = "draft_preview_agent_handoff_acceptance_packet_v2"
PACKET_VERSION = 2
HANDOFF_PACKET_VERSION = "draft-preview-agent-handoff-packet-v2"
SMOKE_FIXTURE_KIND = "reversible_draft_preview_offline_smoke_transcript_v2"
PROMPT_FIXTURE_KIND = "prompt_refresh_release_handoff_fixtures"

REQUIRED_ATTESTATIONS = (
    "no_live_llm",
    "no_devhub",
    "no_private_document",
    "no_pdf_write",
    "no_prompt",
    "no_release_state_mutation",
)

DEFAULT_OFFLINE_VALIDATION_COMMANDS = (
    ("python3", "-m", "py_compile", "ppd/acceptance/draft_preview_agent_handoff_acceptance_packet_v2.py"),
    ("python3", "-m", "pytest", "ppd/tests/test_draft_preview_agent_handoff_acceptance_packet_v2.py"),
    ("python3", "ppd/daemon/ppd_daemon.py", "--self-test"),
)

_DECISIONS = ("accepted", "deferred", "rejected")
_PRIVATE_MARKERS = (
    "/home/",
    "/Users/",
    "C:/Users/",
    "file://",
    "auth_state",
    "browser_state",
    "cookie",
    "session_state",
    "trace.zip",
    ".har",
    "AUTHENTICATED_VALUE:",
    "PRIVATE_FACT:",
    "RAW_PDF_BYTES:",
)
_SENSITIVE_FACT_KEYS = (
    "authenticated_fact",
    "authenticated_value",
    "private_fact",
    "private_value",
    "raw_pdf",
    "pdf_bytes",
    "browser_artifact",
    "devhub_page_value",
)
_ACTIVE_MUTATION_DOMAINS = (
    "prompt",
    "guardrail",
    "pdf",
    "gap_analysis",
    "monitoring",
    "release_state",
    "agent_state",
)
_EXECUTION_CLAIM_DOMAINS = (
    "live_llm",
    "llm",
    "devhub",
    "browser",
    "pdf",
    "crawler",
    "processor",
)
_EXECUTION_KEY_TERMS = (
    "executed",
    "accessed",
    "opened",
    "ran",
    "crawled",
    "processed",
    "captured",
    "downloaded",
    "called",
)
_OUTCOME_GUARANTEE_PATTERNS = (
    re.compile(r"\bpermit\s+(?:will|shall|is\s+guaranteed\s+to)\s+(?:be\s+)?(?:approved|issued|accepted)\b", re.IGNORECASE),
    re.compile(r"\bapproval\s+(?:is\s+)?guaranteed\b", re.IGNORECASE),
    re.compile(r"\bguarantee(?:d|s)?\s+(?:permit|approval|issuance|code\s+compliance)\b", re.IGNORECASE),
    re.compile(r"\blegally\s+(?:sufficient|compliant|approved|guaranteed)\b", re.IGNORECASE),
    re.compile(r"\bno\s+(?:code\s+)?(?:violation|enforcement\s+risk|permitting\s+risk)\b", re.IGNORECASE),
)
_FINAL_ACTION_PATTERNS = (
    re.compile(r"\b(?:i|we|the\s+agent)\s+(?:submitted|uploaded|scheduled|cancelled|canceled|paid)\b", re.IGNORECASE),
    re.compile(r"\b(?:application|permit|payment|upload|inspection|cancellation)\s+(?:submitted|uploaded|scheduled|cancelled|canceled|paid|completed)\b", re.IGNORECASE),
    re.compile(r"\b(?:click|press|select)\s+(?:submit|pay|upload|schedule|cancel)\b", re.IGNORECASE),
    re.compile(r"\b(?:submit|upload|pay|schedule|cancel)\s+(?:now|the\s+official|the\s+final|in\s+devhub)\b", re.IGNORECASE),
    re.compile(r"\bfinal\s+(?:submission|payment|upload|scheduling|cancellation)\s+(?:completed|performed|executed|allowed|enabled)\b", re.IGNORECASE),
)
_LIVE_EXECUTION_PATTERNS = (
    re.compile(r"\b(?:ran|called|used)\s+(?:a\s+)?live\s+llm\b", re.IGNORECASE),
    re.compile(r"\b(?:opened|accessed|logged\s+into)\s+devhub\b", re.IGNORECASE),
    re.compile(r"\bbrowser\s+automation\s+(?:ran|executed|clicked|submitted)\b", re.IGNORECASE),
    re.compile(r"\b(?:downloaded|processed|parsed)\s+(?:a\s+)?(?:live\s+)?pdf\b", re.IGNORECASE),
    re.compile(r"\b(?:crawler|processor)\s+(?:ran|executed|captured|processed|downloaded)\b", re.IGNORECASE),
)


class AcceptancePacketError(ValueError):
    """Raised when a fixture cannot support acceptance packet v2."""


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise AcceptancePacketError(f"{path} must contain a JSON object")
    return data


def build_from_fixture_paths(
    draft_preview_agent_handoff_packet_path: Path,
    reversible_draft_preview_offline_smoke_transcript_path: Path,
    prompt_refresh_release_handoff_fixtures_path: Path,
) -> dict[str, Any]:
    return build_acceptance_packet(
        load_json(draft_preview_agent_handoff_packet_path),
        load_json(reversible_draft_preview_offline_smoke_transcript_path),
        load_json(prompt_refresh_release_handoff_fixtures_path),
    )


def build_acceptance_packet(
    draft_preview_agent_handoff_packet_v2: Mapping[str, Any],
    reversible_draft_preview_offline_smoke_transcript_v2: Mapping[str, Any],
    prompt_refresh_release_handoff_fixtures: Mapping[str, Any],
) -> dict[str, Any]:
    _validate_inputs(
        draft_preview_agent_handoff_packet_v2,
        reversible_draft_preview_offline_smoke_transcript_v2,
        prompt_refresh_release_handoff_fixtures,
    )

    accepted = _accepted_decisions(draft_preview_agent_handoff_packet_v2)
    deferred = _deferred_decisions(prompt_refresh_release_handoff_fixtures)
    rejected = _rejected_decisions(draft_preview_agent_handoff_packet_v2)

    packet = {
        "packet_type": PACKET_TYPE,
        "packet_version": PACKET_VERSION,
        "mode": "fixture_first_offline_acceptance",
        "consumes": {
            "draft_preview_agent_handoff_packet_v2": _handoff_id(draft_preview_agent_handoff_packet_v2),
            "reversible_draft_preview_offline_smoke_transcript_v2": _fixture_id(reversible_draft_preview_offline_smoke_transcript_v2),
            "prompt_refresh_release_handoff_fixtures": _fixture_id(prompt_refresh_release_handoff_fixtures),
        },
        "consumer_handoff_decisions": {
            "accepted": accepted,
            "deferred": deferred,
            "rejected": rejected,
        },
        "migration_checklist_items": _migration_checklist_items(accepted, deferred, rejected),
        "rollback_owner_fields": _rollback_owner_fields(draft_preview_agent_handoff_packet_v2),
        "offline_validation_commands": _offline_validation_commands(
            draft_preview_agent_handoff_packet_v2,
            prompt_refresh_release_handoff_fixtures,
        ),
        "attestations": {key: True for key in REQUIRED_ATTESTATIONS},
        "validation_status": "fixture_acceptance_packet_ready_for_consumer_migration_review",
    }
    validate_acceptance_packet(packet)
    return packet


def validate_acceptance_packet(packet: Mapping[str, Any]) -> None:
    if packet.get("packet_type") != PACKET_TYPE:
        raise AcceptancePacketError("unexpected packet_type")
    if packet.get("packet_version") != PACKET_VERSION:
        raise AcceptancePacketError("packet_version must be 2")

    decisions = _mapping(packet.get("consumer_handoff_decisions"), "consumer_handoff_decisions")
    for decision in _DECISIONS:
        rows = _mapping_sequence(decisions.get(decision), f"consumer_handoff_decisions.{decision}")
        if not rows:
            raise AcceptancePacketError(f"consumer_handoff_decisions.{decision} must not be empty")
        for index, row in enumerate(rows):
            prefix = f"consumer_handoff_decisions.{decision}[{index}]"
            if row.get("decision") != decision:
                raise AcceptancePacketError(prefix + ".decision mismatch")
            if not _text(row.get("decision_id")):
                raise AcceptancePacketError(prefix + ".decision_id required")
            if not _text(row.get("consumer_handoff_decision")):
                raise AcceptancePacketError(prefix + ".consumer_handoff_decision required")
            if not _text(row.get("rationale")):
                raise AcceptancePacketError(prefix + ".rationale required")
            if not _mapping_sequence(row.get("citations"), prefix + ".citations"):
                raise AcceptancePacketError(prefix + ".citations required")

    checklist = _mapping_sequence(packet.get("migration_checklist_items"), "migration_checklist_items")
    if not checklist:
        raise AcceptancePacketError("migration_checklist_items must not be empty")
    for index, item in enumerate(checklist):
        prefix = f"migration_checklist_items[{index}]"
        for key in ("checklist_item_id", "status", "summary"):
            if not _text(item.get(key)):
                raise AcceptancePacketError(f"{prefix}.{key} required")
        if not _string_list(item.get("decision_refs")):
            raise AcceptancePacketError(f"{prefix}.decision_refs required")

    rollback = _mapping(packet.get("rollback_owner_fields"), "rollback_owner_fields")
    for key in ("owner", "contact_route", "rollback_scope", "rollback_trigger", "rollback_validation"):
        if not _text(rollback.get(key)):
            raise AcceptancePacketError(f"rollback_owner_fields.{key} required")

    if not _command_sequence(packet.get("offline_validation_commands")):
        raise AcceptancePacketError("offline_validation_commands required")

    attestations = _mapping(packet.get("attestations"), "attestations")
    for key in REQUIRED_ATTESTATIONS:
        if attestations.get(key) is not True:
            raise AcceptancePacketError(f"attestations.{key} must be true")

    _reject_unsafe_values(packet)


def _validate_inputs(*packets: Mapping[str, Any]) -> None:
    handoff, smoke, prompt = packets
    if handoff.get("packet_version") != HANDOFF_PACKET_VERSION:
        raise AcceptancePacketError("draft preview handoff packet must be v2")
    if smoke.get("fixture_kind") != SMOKE_FIXTURE_KIND:
        raise AcceptancePacketError("smoke transcript fixture_kind mismatch")
    if prompt.get("fixture_kind") != PROMPT_FIXTURE_KIND:
        raise AcceptancePacketError("prompt release handoff fixture_kind mismatch")
    for packet in packets:
        _require_attestations(packet)
        _reject_unsafe_values(packet)


def _accepted_decisions(handoff: Mapping[str, Any]) -> list[dict[str, Any]]:
    decisions: list[dict[str, Any]] = []
    for note in _mapping_sequence(handoff.get("consumer_facing_handoff_notes"), "consumer_facing_handoff_notes"):
        note_id = _text(note.get("note_id"))
        decisions.append(
            {
                "decision_id": "accept-note-" + note_id,
                "decision": "accepted",
                "consumer_handoff_decision": "Accept consumer handoff note for migration into draft preview agent wording.",
                "rationale": "The note is fixture-backed, cited, and limited to reversible draft preview handoff guidance.",
                "handoff_ref": note_id,
                "body": _text(note.get("body")),
                "citations": _citation_sequence(note.get("citations")),
                "source_packet_roles": ["draft_preview_agent_handoff_packet_v2"],
            }
        )
    for scenario in _mapping_sequence(handoff.get("supported_safe_draft_preview_scenarios"), "supported_safe_draft_preview_scenarios"):
        scenario_id = _text(scenario.get("scenario_id"))
        decisions.append(
            {
                "decision_id": "accept-scenario-" + scenario_id,
                "decision": "accepted",
                "consumer_handoff_decision": "Accept reversible local draft preview scenario as supported consumer behavior.",
                "rationale": "The scenario is constrained to local fixture review and does not claim DevHub execution or official outcomes.",
                "handoff_ref": scenario_id,
                "body": _text(scenario.get("title")),
                "allowed_operations": _string_list(scenario.get("allowed_operations")),
                "citations": _citation_sequence(scenario.get("citations")),
                "source_packet_roles": [
                    "draft_preview_agent_handoff_packet_v2",
                    "reversible_draft_preview_offline_smoke_transcript_v2",
                ],
            }
        )
    return decisions


def _deferred_decisions(prompt: Mapping[str, Any]) -> list[dict[str, Any]]:
    decisions: list[dict[str, Any]] = []
    fixture_id = _fixture_id(prompt)
    for reminder in _mapping_sequence(prompt.get("exact_confirmation_reminders"), "exact_confirmation_reminders"):
        trigger = _text(reminder.get("trigger"))
        reminder_text = _text(reminder.get("reminder"))
        decisions.append(
            {
                "decision_id": "defer-confirmation-" + trigger,
                "decision": "deferred",
                "consumer_handoff_decision": "Defer live or consequential action migration until attended exact-confirmation handling is reviewed.",
                "rationale": "The reminder concerns consequential action confirmation and must remain non-executable in this offline acceptance packet.",
                "handoff_ref": trigger,
                "body": reminder_text,
                "citations": [
                    {
                        "citation_id": fixture_id + ":" + trigger,
                        "title": "Prompt refresh release handoff fixture exact-confirmation reminder",
                        "source": "ppd/tests/fixtures/draft_preview_agent_handoff_packet_v2/prompt_refresh_release_handoff_fixtures.json",
                        "quote_or_fact": reminder_text,
                    }
                ],
                "source_packet_roles": ["prompt_refresh_release_handoff_fixtures"],
            }
        )
    return decisions


def _rejected_decisions(handoff: Mapping[str, Any]) -> list[dict[str, Any]]:
    decisions: list[dict[str, Any]] = []
    for blocked in _mapping_sequence(handoff.get("blocked_consequential_action_language"), "blocked_consequential_action_language"):
        action = _text(blocked.get("action"))
        decisions.append(
            {
                "decision_id": "reject-live-action-" + action,
                "decision": "rejected",
                "consumer_handoff_decision": "Reject migration that would let the consumer perform consequential PP&D actions from this offline packet.",
                "rationale": "The cited source language involves official or account-scoped PP&D actions that require attended user handling outside this packet.",
                "handoff_ref": action,
                "body": _text(blocked.get("consumer_language")),
                "citations": _citation_sequence(blocked.get("citations")),
                "source_packet_roles": [
                    "draft_preview_agent_handoff_packet_v2",
                    "reversible_draft_preview_offline_smoke_transcript_v2",
                ],
            }
        )
    return decisions


def _migration_checklist_items(
    accepted: Sequence[Mapping[str, Any]],
    deferred: Sequence[Mapping[str, Any]],
    rejected: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    return [
        {
            "checklist_item_id": "migrate-accepted-draft-preview-consumer-notes",
            "status": "ready_for_fixture_consumer_migration",
            "summary": "Carry accepted draft preview notes and safe scenario labels into consumer handoff documentation.",
            "decision_refs": [_text(item.get("decision_id")) for item in accepted],
        },
        {
            "checklist_item_id": "defer-exact-confirmation-live-action-reminders",
            "status": "deferred_until_attended_confirmation_review",
            "summary": "Keep exact-confirmation wording as a reminder only until attended DevHub action handling is separately reviewed.",
            "decision_refs": [_text(item.get("decision_id")) for item in deferred],
        },
        {
            "checklist_item_id": "reject-consequential-action-execution-migration",
            "status": "blocked_from_consumer_migration",
            "summary": "Do not migrate submit, upload, payment, inspection scheduling, cancellation, certification, or release-state mutation as executable behavior.",
            "decision_refs": [_text(item.get("decision_id")) for item in rejected],
        },
    ]


def _rollback_owner_fields(handoff: Mapping[str, Any]) -> dict[str, str]:
    rollback = _mapping(handoff.get("rollback_owner_fields"), "rollback_owner_fields")
    return {
        "owner": _required_text(rollback.get("owner"), "rollback_owner_fields.owner"),
        "contact_route": _required_text(rollback.get("contact_route"), "rollback_owner_fields.contact_route"),
        "rollback_scope": _required_text(rollback.get("rollback_scope"), "rollback_owner_fields.rollback_scope"),
        "rollback_trigger": _text(rollback.get("rollback_trigger")) or "Any uncited, unrationalized, private, live-execution, outcome-guarantee, final-action, or mutation claim discovered in the packet.",
        "rollback_validation": _text(rollback.get("rollback_validation")) or "Remove the unsafe acceptance packet, rerun offline validation, and keep DevHub, PDF, prompt, guardrail, monitoring, release, and agent state unchanged.",
    }


def _offline_validation_commands(*packets: Mapping[str, Any]) -> list[list[str]]:
    commands = [list(command) for command in DEFAULT_OFFLINE_VALIDATION_COMMANDS]
    for packet in packets:
        for command in _command_sequence(packet.get("offline_validation_commands")):
            if command not in commands:
                commands.append(command)
    return commands


def _require_attestations(packet: Mapping[str, Any]) -> None:
    attestations = _mapping(packet.get("attestations"), "attestations")
    missing = [key for key in REQUIRED_ATTESTATIONS if attestations.get(key) is not True]
    if missing:
        raise AcceptancePacketError("missing required attestations: " + ", ".join(missing))


def _handoff_id(handoff: Mapping[str, Any]) -> str:
    ids = _string_list(handoff.get("source_fixture_ids"))
    return HANDOFF_PACKET_VERSION + ":" + "+".join(ids)


def _fixture_id(packet: Mapping[str, Any]) -> str:
    return _required_text(packet.get("fixture_id"), "fixture_id")


def _citation_sequence(value: Any) -> list[dict[str, str]]:
    citations = _mapping_sequence(value, "citations")
    result: list[dict[str, str]] = []
    for citation in citations:
        result.append(
            {
                "citation_id": _required_text(citation.get("citation_id"), "citation_id"),
                "title": _required_text(citation.get("title"), "title"),
                "source": _required_text(citation.get("source"), "source"),
                "quote_or_fact": _text(citation.get("quote_or_fact")),
            }
        )
    if not result:
        raise AcceptancePacketError("citations required")
    return result


def _reject_unsafe_values(value: Any, key: str = "$") -> None:
    normalized_key = key.lower().replace("-", "_")
    if not normalized_key.startswith("no_"):
        if any(marker in normalized_key for marker in _SENSITIVE_FACT_KEYS) and _truthy_or_text(value):
            raise AcceptancePacketError(key + " must not include private/authenticated facts, raw PDF bytes, or authenticated values")
        if _is_active_mutation_flag(normalized_key, value):
            raise AcceptancePacketError(key + " must not enable prompt, guardrail, PDF, gap-analysis, monitoring, release-state, or agent-state mutation")
        if _is_execution_claim_flag(normalized_key, value):
            raise AcceptancePacketError(key + " must not claim live LLM, DevHub, browser, PDF, crawler, or processor execution")
    if isinstance(value, str):
        if any(marker in value for marker in _PRIVATE_MARKERS):
            raise AcceptancePacketError(key + " must not reference private paths, authenticated values, raw PDF bytes, or browser artifacts")
        _reject_unsafe_text_patterns(value, key)
    if isinstance(value, Mapping):
        for child_key, child_value in value.items():
            _reject_unsafe_values(child_value, str(child_key))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for child in value:
            _reject_unsafe_values(child, key)


def _is_active_mutation_flag(normalized_key: str, value: Any) -> bool:
    if value is not True:
        return False
    has_domain = any(domain in normalized_key for domain in _ACTIVE_MUTATION_DOMAINS)
    has_mutation = any(term in normalized_key for term in ("mutation", "mutated", "write", "update", "enabled", "active"))
    return has_domain and has_mutation


def _is_execution_claim_flag(normalized_key: str, value: Any) -> bool:
    if value is not True:
        return False
    has_domain = any(domain in normalized_key for domain in _EXECUTION_CLAIM_DOMAINS)
    has_execution = any(term in normalized_key for term in _EXECUTION_KEY_TERMS)
    return has_domain and has_execution


def _reject_unsafe_text_patterns(value: str, key: str) -> None:
    for pattern in _LIVE_EXECUTION_PATTERNS:
        if pattern.search(value):
            raise AcceptancePacketError(key + " must not claim live LLM, DevHub, browser, PDF, crawler, or processor execution")
    for pattern in _OUTCOME_GUARANTEE_PATTERNS:
        if pattern.search(value):
            raise AcceptancePacketError(key + " must not guarantee legal or permitting outcomes")
    for pattern in _FINAL_ACTION_PATTERNS:
        if pattern.search(value):
            raise AcceptancePacketError(key + " must not include final submission, payment, upload, scheduling, or cancellation language")


def _truthy_or_text(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    return bool(value)


def _mapping(value: Any, field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise AcceptancePacketError(field + " must be an object")
    return value


def _mapping_sequence(value: Any, field: str) -> list[Mapping[str, Any]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise AcceptancePacketError(field + " must be a list")
    result = [item for item in value if isinstance(item, Mapping)]
    if len(result) != len(value):
        raise AcceptancePacketError(field + " must contain only objects")
    return result


def _command_sequence(value: Any) -> list[list[str]]:
    commands: list[list[str]] = []
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return commands
    for command in value:
        if isinstance(command, Sequence) and not isinstance(command, (str, bytes, bytearray)):
            parts = [_text(part) for part in command if _text(part)]
            if parts:
                commands.append(parts)
    return commands


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _required_text(value: Any, field: str) -> str:
    text = _text(value)
    if not text:
        raise AcceptancePacketError(field + " required")
    return text


def _text(value: Any) -> str:
    return str(value).strip() if value is not None else ""
