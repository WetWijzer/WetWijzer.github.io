"""Fixture-first guarded agent readiness delta packet v2 builder.

This module is intentionally offline-only. It combines an inactive fixture
promotion candidate packet with existing guarded agent readiness packets and
emits ordered agent-facing delta scenarios for review and citation tracing.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

DELTA_PACKET_VERSION = "guarded-agent-readiness-delta-packet-v2"
REQUIRED_SCENARIO_KINDS = (
    "citation_traceability",
    "missing_information_prompt",
    "refusal_behavior",
    "blocked_consequential_action",
    "reversible_draft_boundary",
    "journal_event_safety",
    "rollback_readiness",
    "offline_validation_command",
)
FORBIDDEN_ACTIONS = (
    "devhub_access",
    "live_crawl",
    "official_submission",
    "captcha",
    "mfa",
    "payment",
    "upload",
    "certification",
    "cancellation",
)


@dataclass(frozen=True)
class DeltaSource:
    packet_id: str
    packet_version: str
    inactive: bool
    path_hint: str


def _read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object in {path}")
    return value


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _string_set(values: Iterable[Any]) -> set[str]:
    return {str(value) for value in values if str(value).strip()}


def _packet_id(packet: dict[str, Any], fallback: str) -> str:
    for key in ("packet_id", "id", "name"):
        value = packet.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return fallback


def _packet_version(packet: dict[str, Any]) -> str:
    value = packet.get("packet_version") or packet.get("version")
    if isinstance(value, str) and value.strip():
        return value
    return "unknown"


def _source(packet: dict[str, Any], fallback: str) -> DeltaSource:
    return DeltaSource(
        packet_id=_packet_id(packet, fallback),
        packet_version=_packet_version(packet),
        inactive=bool(packet.get("inactive", False)),
        path_hint=str(packet.get("path_hint") or fallback),
    )


def _scenario_from_candidate(candidate: dict[str, Any], index: int, source: DeltaSource) -> dict[str, Any]:
    kind = str(candidate.get("kind") or candidate.get("scenario_kind") or "unknown")
    title = str(candidate.get("title") or kind.replace("_", " ").title())
    citations = _as_list(candidate.get("citations"))
    prompts = _as_list(candidate.get("missing_information_prompts"))
    blocked_actions = _string_set(_as_list(candidate.get("blocked_actions")))
    blocked_actions.update(action for action in FORBIDDEN_ACTIONS if action in _string_set(_as_list(candidate.get("actions"))))
    validation_commands = _as_list(candidate.get("validation_commands"))
    return {
        "order": index,
        "kind": kind,
        "title": title,
        "source_packet_id": source.packet_id,
        "source_packet_version": source.packet_version,
        "citation_traceability": citations,
        "missing_information_prompts": prompts,
        "refusal_required": bool(candidate.get("refusal_required", kind == "refusal_behavior")),
        "blocked_actions": sorted(blocked_actions),
        "reversible_draft_only": bool(candidate.get("reversible_draft_only", kind == "reversible_draft_boundary")),
        "journal_event_safe": bool(candidate.get("journal_event_safe", kind == "journal_event_safety")),
        "rollback_ready": bool(candidate.get("rollback_ready", kind == "rollback_readiness")),
        "offline_validation_commands": validation_commands,
        "agent_facing_delta": str(candidate.get("agent_facing_delta") or candidate.get("delta") or title),
    }


def build_delta_packet(
    promotion_candidate_packet: dict[str, Any],
    readiness_packets: Iterable[dict[str, Any]],
) -> dict[str, Any]:
    """Build an ordered guarded readiness delta packet from offline fixtures."""
    candidate_source = _source(promotion_candidate_packet, "inactive_fixture_promotion_candidate_packet_v2")
    readiness_sources = [_source(packet, f"guarded_agent_readiness_packet_{index}") for index, packet in enumerate(readiness_packets, start=1)]

    candidate_scenarios = _as_list(promotion_candidate_packet.get("delta_candidates"))
    if not candidate_scenarios:
        candidate_scenarios = _as_list(promotion_candidate_packet.get("scenarios"))

    scenarios = []
    for index, candidate in enumerate(candidate_scenarios, start=1):
        if not isinstance(candidate, dict):
            raise ValueError("delta candidates must be JSON objects")
        scenarios.append(_scenario_from_candidate(candidate, index, candidate_source))

    present_kinds = {scenario["kind"] for scenario in scenarios}
    readiness_kinds = set[str]()
    for packet in readiness_packets:
        readiness_kinds.update(_string_set(_as_list(packet.get("readiness_kinds"))))
        readiness_kinds.update(_string_set(item.get("kind") for item in _as_list(packet.get("scenarios")) if isinstance(item, dict)))

    missing_required_kinds = [kind for kind in REQUIRED_SCENARIO_KINDS if kind not in present_kinds]
    return {
        "packet_version": DELTA_PACKET_VERSION,
        "mode": "fixture_first_offline_only",
        "consumes": {
            "inactive_fixture_promotion_candidate_packet_v2": candidate_source.__dict__,
            "guarded_agent_readiness_packets": [source.__dict__ for source in readiness_sources],
        },
        "ordered_agent_facing_delta_scenarios": scenarios,
        "coverage": {
            "required_scenario_kinds": list(REQUIRED_SCENARIO_KINDS),
            "present_scenario_kinds": sorted(present_kinds),
            "readiness_packet_kinds": sorted(readiness_kinds),
            "missing_required_scenario_kinds": missing_required_kinds,
        },
        "guards": {
            "active_artifact_mutation": "forbidden",
            "devhub_access": "forbidden",
            "live_source_crawl": "forbidden",
            "official_actions": "forbidden",
            "prompt_changes": "forbidden",
        },
    }


def build_delta_packet_from_files(candidate_path: Path, readiness_paths: Iterable[Path]) -> dict[str, Any]:
    candidate = _read_json(candidate_path)
    readiness = [_read_json(path) for path in readiness_paths]
    return build_delta_packet(candidate, readiness)
