"""Build fixture-first draft preview agent handoff packet v2.

The packet is intentionally offline and deterministic. It consumes committed
fixtures that describe an offline smoke transcript, a local review packet, and a
prompt-refresh release handoff, then emits consumer-facing notes with citations
and explicit action boundaries.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

PACKET_VERSION = "draft-preview-agent-handoff-packet-v2"
REQUIRED_ATTESTATIONS = (
    "no_live_llm",
    "no_devhub",
    "no_private_document",
    "no_pdf_write",
    "no_prompt",
    "no_release_state_mutation",
)
REQUIRED_INPUT_KINDS = (
    "reversible_draft_preview_offline_smoke_transcript_v2",
    "local_draft_preview_review_packet_v2",
    "prompt_refresh_release_handoff_fixtures",
)


class HandoffPacketError(ValueError):
    """Raised when a fixture cannot support a v2 handoff packet."""


def load_json(path: Path) -> dict[str, Any]:
    """Load a JSON object from a fixture path."""
    with path.open("r", encoding="utf-8") as handle:
        loaded = json.load(handle)
    if not isinstance(loaded, dict):
        raise HandoffPacketError(f"{path} must contain a JSON object")
    return loaded


def fixture_digest(path: Path) -> str:
    """Return a stable digest for fixture provenance."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_inputs(
    smoke_transcript_path: Path,
    review_packet_path: Path,
    prompt_release_handoff_path: Path,
) -> dict[str, dict[str, Any]]:
    """Load and validate the three fixture inputs required by the packet."""
    inputs = {
        "smoke_transcript": load_json(smoke_transcript_path),
        "review_packet": load_json(review_packet_path),
        "prompt_release_handoff": load_json(prompt_release_handoff_path),
    }
    expected = {
        "smoke_transcript": REQUIRED_INPUT_KINDS[0],
        "review_packet": REQUIRED_INPUT_KINDS[1],
        "prompt_release_handoff": REQUIRED_INPUT_KINDS[2],
    }
    for name, expected_kind in expected.items():
        actual_kind = inputs[name].get("fixture_kind")
        if actual_kind != expected_kind:
            raise HandoffPacketError(
                f"{name} fixture_kind must be {expected_kind!r}, got {actual_kind!r}"
            )
    return inputs


def _as_list(value: Any, field_name: str) -> list[Any]:
    if not isinstance(value, list):
        raise HandoffPacketError(f"{field_name} must be a list")
    return value


def _require_mapping(value: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise HandoffPacketError(f"{field_name} must be an object")
    return value


def _unique_strings(values: Iterable[Any]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if not isinstance(value, str):
            raise HandoffPacketError("expected string value")
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def _citations_by_id(review_packet: dict[str, Any]) -> dict[str, dict[str, str]]:
    citations: dict[str, dict[str, str]] = {}
    for citation in _as_list(review_packet.get("citations"), "review_packet.citations"):
        citation_obj = _require_mapping(citation, "review_packet.citations[]")
        citation_id = citation_obj.get("citation_id")
        title = citation_obj.get("title")
        source = citation_obj.get("source")
        if not all(isinstance(item, str) and item for item in (citation_id, title, source)):
            raise HandoffPacketError("each citation needs citation_id, title, and source")
        citations[citation_id] = {
            "citation_id": citation_id,
            "title": title,
            "source": source,
            "quote_or_fact": str(citation_obj.get("quote_or_fact", "")),
        }
    return citations


def _resolve_citations(citation_ids: Iterable[Any], citation_map: dict[str, dict[str, str]]) -> list[dict[str, str]]:
    resolved: list[dict[str, str]] = []
    for citation_id in citation_ids:
        if not isinstance(citation_id, str):
            raise HandoffPacketError("citation ids must be strings")
        if citation_id not in citation_map:
            raise HandoffPacketError(f"unknown citation id: {citation_id}")
        resolved.append(citation_map[citation_id])
    return resolved


def _consumer_notes(review_packet: dict[str, Any], citation_map: dict[str, dict[str, str]]) -> list[dict[str, Any]]:
    notes: list[dict[str, Any]] = []
    for note in _as_list(review_packet.get("consumer_facing_notes"), "review_packet.consumer_facing_notes"):
        note_obj = _require_mapping(note, "review_packet.consumer_facing_notes[]")
        note_id = note_obj.get("note_id")
        body = note_obj.get("body")
        if not isinstance(note_id, str) or not isinstance(body, str):
            raise HandoffPacketError("each consumer note needs string note_id and body")
        citation_ids = _as_list(note_obj.get("citation_ids"), "consumer_facing_notes[].citation_ids")
        notes.append(
            {
                "note_id": note_id,
                "body": body,
                "citations": _resolve_citations(citation_ids, citation_map),
            }
        )
    if not notes:
        raise HandoffPacketError("at least one consumer-facing note is required")
    return notes


def _supported_scenarios(smoke_transcript: dict[str, Any], citation_map: dict[str, dict[str, str]]) -> list[dict[str, Any]]:
    scenarios: list[dict[str, Any]] = []
    for scenario in _as_list(smoke_transcript.get("safe_draft_preview_scenarios"), "smoke_transcript.safe_draft_preview_scenarios"):
        scenario_obj = _require_mapping(scenario, "safe_draft_preview_scenarios[]")
        scenario_id = scenario_obj.get("scenario_id")
        title = scenario_obj.get("title")
        allowed_operations = _unique_strings(_as_list(scenario_obj.get("allowed_operations"), "safe_draft_preview_scenarios[].allowed_operations"))
        citation_ids = _as_list(scenario_obj.get("citation_ids"), "safe_draft_preview_scenarios[].citation_ids")
        if not isinstance(scenario_id, str) or not isinstance(title, str):
            raise HandoffPacketError("each safe scenario needs string scenario_id and title")
        scenarios.append(
            {
                "scenario_id": scenario_id,
                "title": title,
                "allowed_operations": allowed_operations,
                "citations": _resolve_citations(citation_ids, citation_map),
            }
        )
    if not scenarios:
        raise HandoffPacketError("at least one supported safe draft-preview scenario is required")
    return scenarios


def _blocked_language(smoke_transcript: dict[str, Any], citation_map: dict[str, dict[str, str]]) -> list[dict[str, Any]]:
    blocked: list[dict[str, Any]] = []
    for item in _as_list(smoke_transcript.get("blocked_consequential_actions"), "smoke_transcript.blocked_consequential_actions"):
        item_obj = _require_mapping(item, "blocked_consequential_actions[]")
        action = item_obj.get("action")
        language = item_obj.get("consumer_language")
        citation_ids = _as_list(item_obj.get("citation_ids"), "blocked_consequential_actions[].citation_ids")
        if not isinstance(action, str) or not isinstance(language, str):
            raise HandoffPacketError("each blocked action needs string action and consumer_language")
        blocked.append(
            {
                "action": action,
                "consumer_language": language,
                "citations": _resolve_citations(citation_ids, citation_map),
            }
        )
    if not blocked:
        raise HandoffPacketError("at least one blocked consequential-action language entry is required")
    return blocked


def _exact_confirmation_reminders(prompt_release_handoff: dict[str, Any]) -> list[dict[str, str]]:
    reminders: list[dict[str, str]] = []
    for reminder in _as_list(prompt_release_handoff.get("exact_confirmation_reminders"), "prompt_release_handoff.exact_confirmation_reminders"):
        reminder_obj = _require_mapping(reminder, "exact_confirmation_reminders[]")
        trigger = reminder_obj.get("trigger")
        reminder_text = reminder_obj.get("reminder")
        if not isinstance(trigger, str) or not isinstance(reminder_text, str):
            raise HandoffPacketError("each exact confirmation reminder needs trigger and reminder")
        reminders.append({"trigger": trigger, "reminder": reminder_text})
    if not reminders:
        raise HandoffPacketError("at least one exact-confirmation reminder is required")
    return reminders


def _rollback_owner_fields(review_packet: dict[str, Any]) -> dict[str, str]:
    rollback = _require_mapping(review_packet.get("rollback_owner"), "review_packet.rollback_owner")
    required = ("owner", "contact_route", "rollback_scope")
    fields: dict[str, str] = {}
    for key in required:
        value = rollback.get(key)
        if not isinstance(value, str) or not value:
            raise HandoffPacketError(f"rollback_owner.{key} is required")
        fields[key] = value
    return fields


def _offline_validation_commands(prompt_release_handoff: dict[str, Any]) -> list[list[str]]:
    commands: list[list[str]] = []
    for command in _as_list(prompt_release_handoff.get("offline_validation_commands"), "prompt_release_handoff.offline_validation_commands"):
        command_list = _as_list(command, "offline_validation_commands[]")
        if not command_list or not all(isinstance(part, str) and part for part in command_list):
            raise HandoffPacketError("offline validation commands must be non-empty string arrays")
        commands.append(command_list)
    if not commands:
        raise HandoffPacketError("at least one offline validation command is required")
    return commands


def _attestations(*fixtures: dict[str, Any]) -> dict[str, bool]:
    merged: dict[str, bool] = {}
    for fixture in fixtures:
        fixture_attestations = _require_mapping(fixture.get("attestations"), "fixture.attestations")
        for key, value in fixture_attestations.items():
            if isinstance(key, str) and isinstance(value, bool):
                merged[key] = value
    missing = [key for key in REQUIRED_ATTESTATIONS if merged.get(key) is not True]
    if missing:
        raise HandoffPacketError("missing required true attestations: " + ", ".join(missing))
    return {key: True for key in REQUIRED_ATTESTATIONS}


def build_packet(
    smoke_transcript: dict[str, Any],
    review_packet: dict[str, Any],
    prompt_release_handoff: dict[str, Any],
    *,
    provenance: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    """Build a validated handoff packet from already-loaded fixture objects."""
    citation_map = _citations_by_id(review_packet)
    packet = {
        "packet_version": PACKET_VERSION,
        "source_fixture_ids": [
            str(smoke_transcript.get("fixture_id", "")),
            str(review_packet.get("fixture_id", "")),
            str(prompt_release_handoff.get("fixture_id", "")),
        ],
        "fixture_provenance": provenance or [],
        "consumer_facing_handoff_notes": _consumer_notes(review_packet, citation_map),
        "supported_safe_draft_preview_scenarios": _supported_scenarios(smoke_transcript, citation_map),
        "blocked_consequential_action_language": _blocked_language(smoke_transcript, citation_map),
        "required_exact_confirmation_reminders": _exact_confirmation_reminders(prompt_release_handoff),
        "rollback_owner_fields": _rollback_owner_fields(review_packet),
        "offline_validation_commands": _offline_validation_commands(prompt_release_handoff),
        "attestations": _attestations(smoke_transcript, review_packet, prompt_release_handoff),
    }
    validate_packet(packet)
    return packet


def build_packet_from_paths(
    smoke_transcript_path: Path,
    review_packet_path: Path,
    prompt_release_handoff_path: Path,
) -> dict[str, Any]:
    """Load fixture files and build the handoff packet with digest provenance."""
    paths = [smoke_transcript_path, review_packet_path, prompt_release_handoff_path]
    inputs = load_inputs(smoke_transcript_path, review_packet_path, prompt_release_handoff_path)
    provenance = [
        {
            "path_name": path.name,
            "sha256": fixture_digest(path),
        }
        for path in paths
    ]
    return build_packet(
        inputs["smoke_transcript"],
        inputs["review_packet"],
        inputs["prompt_release_handoff"],
        provenance=provenance,
    )


def validate_packet(packet: dict[str, Any]) -> None:
    """Validate the public shape of a generated packet."""
    if packet.get("packet_version") != PACKET_VERSION:
        raise HandoffPacketError("unexpected packet_version")
    for field in (
        "consumer_facing_handoff_notes",
        "supported_safe_draft_preview_scenarios",
        "blocked_consequential_action_language",
        "required_exact_confirmation_reminders",
        "offline_validation_commands",
    ):
        value = packet.get(field)
        if not isinstance(value, list) or not value:
            raise HandoffPacketError(f"{field} must be a non-empty list")
    rollback = packet.get("rollback_owner_fields")
    if not isinstance(rollback, dict) or not rollback.get("owner"):
        raise HandoffPacketError("rollback_owner_fields.owner is required")
    attestations = packet.get("attestations")
    if not isinstance(attestations, dict):
        raise HandoffPacketError("attestations must be an object")
    missing = [key for key in REQUIRED_ATTESTATIONS if attestations.get(key) is not True]
    if missing:
        raise HandoffPacketError("packet attestations missing: " + ", ".join(missing))


def main(argv: list[str] | None = None) -> int:
    """CLI helper for local fixture validation."""
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("smoke_transcript", type=Path)
    parser.add_argument("review_packet", type=Path)
    parser.add_argument("prompt_release_handoff", type=Path)
    args = parser.parse_args(argv)

    packet = build_packet_from_paths(
        args.smoke_transcript,
        args.review_packet,
        args.prompt_release_handoff,
    )
    print(json.dumps(packet, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
