"""Fixture-first manual-handoff decision packets for unsupported PP&D workflows.

The helpers here are intentionally side-effect free. They validate committed
fixtures that describe when an agent must stop before DevHub or official PP&D
workflow controls and hand the user back to a live, attended surface.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence


REQUIRED_TRIGGER_IDS = frozenset(
    {
        "mfa",
        "captcha",
        "account_creation",
        "password_recovery",
        "final_payment_execution",
        "unclear_consequence_control",
        "non_devhub_permit_path",
    }
)

SAFE_ALTERNATIVE_TYPES = frozenset({"read_only_review", "local_preview"})


@dataclass(frozen=True)
class ManualHandoffTrigger:
    """A source-backed reason to stop and hand a workflow to the user."""

    trigger_id: str
    cited_reason: str
    user_visible_handoff_text: str
    blocked_action_ids: tuple[str, ...]
    source_evidence_ids: tuple[str, ...]


@dataclass(frozen=True)
class SafeAlternative:
    """A safe next step that avoids official side effects."""

    action_id: str
    action_type: str
    label: str
    preserves_official_state: bool


@dataclass(frozen=True)
class ManualHandoffDecisionPacket:
    """A deterministic manual-handoff packet for agent-facing guardrails."""

    packet_id: str
    fixture_only: bool
    triggers: tuple[ManualHandoffTrigger, ...]
    next_safe_alternatives: tuple[SafeAlternative, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "packet_id": self.packet_id,
            "fixture_only": self.fixture_only,
            "triggers": [
                {
                    "trigger_id": trigger.trigger_id,
                    "cited_reason": trigger.cited_reason,
                    "user_visible_handoff_text": trigger.user_visible_handoff_text,
                    "blocked_action_ids": list(trigger.blocked_action_ids),
                    "source_evidence_ids": list(trigger.source_evidence_ids),
                }
                for trigger in self.triggers
            ],
            "next_safe_alternatives": [
                {
                    "action_id": alternative.action_id,
                    "action_type": alternative.action_type,
                    "label": alternative.label,
                    "preserves_official_state": alternative.preserves_official_state,
                }
                for alternative in self.next_safe_alternatives
            ],
        }


def load_manual_handoff_decision_packet(path: Path) -> ManualHandoffDecisionPacket:
    """Load and validate a manual-handoff decision packet fixture."""

    with path.open(encoding="utf-8") as fixture_file:
        data = json.load(fixture_file)
    return decision_packet_from_mapping(data)


def decision_packet_from_mapping(data: Mapping[str, Any]) -> ManualHandoffDecisionPacket:
    """Build a packet from a mapping while preserving cited handoff fields."""

    packet = ManualHandoffDecisionPacket(
        packet_id=_required_string(data, "packet_id"),
        fixture_only=_required_bool(data, "fixture_only"),
        triggers=tuple(_trigger_from_mapping(item) for item in _required_list(data, "triggers")),
        next_safe_alternatives=tuple(
            _safe_alternative_from_mapping(item) for item in _required_list(data, "next_safe_alternatives")
        ),
    )
    validate_manual_handoff_decision_packet(packet)
    return packet


def validate_manual_handoff_decision_packet(packet: ManualHandoffDecisionPacket) -> None:
    """Raise ValueError when a handoff packet is incomplete or unsafe."""

    if not packet.fixture_only:
        raise ValueError("manual handoff decision packets must be fixture_only")

    trigger_ids = {trigger.trigger_id for trigger in packet.triggers}
    missing = REQUIRED_TRIGGER_IDS.difference(trigger_ids)
    if missing:
        raise ValueError(f"manual handoff packet is missing required triggers: {sorted(missing)}")

    for trigger in packet.triggers:
        if not trigger.cited_reason:
            raise ValueError(f"trigger {trigger.trigger_id} must preserve a cited reason")
        if not trigger.user_visible_handoff_text:
            raise ValueError(f"trigger {trigger.trigger_id} must include user-visible handoff text")
        if not trigger.blocked_action_ids:
            raise ValueError(f"trigger {trigger.trigger_id} must include blocked action ids")
        if not trigger.source_evidence_ids:
            raise ValueError(f"trigger {trigger.trigger_id} must include source evidence ids")

    if not packet.next_safe_alternatives:
        raise ValueError("manual handoff packet must include next safe alternatives")
    for alternative in packet.next_safe_alternatives:
        if alternative.action_type not in SAFE_ALTERNATIVE_TYPES:
            raise ValueError(f"unsafe alternative action type: {alternative.action_type}")
        if not alternative.preserves_official_state:
            raise ValueError(f"alternative must preserve official state: {alternative.action_id}")


def blocked_action_ids_by_trigger(packet: ManualHandoffDecisionPacket) -> dict[str, tuple[str, ...]]:
    """Return blocked action ids keyed by trigger id for guardrail assertions."""

    return {trigger.trigger_id: trigger.blocked_action_ids for trigger in packet.triggers}


def user_visible_handoff_text_by_trigger(packet: ManualHandoffDecisionPacket) -> dict[str, str]:
    """Return user-facing handoff text keyed by trigger id."""

    return {trigger.trigger_id: trigger.user_visible_handoff_text for trigger in packet.triggers}


def _trigger_from_mapping(value: Any) -> ManualHandoffTrigger:
    if not isinstance(value, Mapping):
        raise ValueError("triggers must contain mappings")
    return ManualHandoffTrigger(
        trigger_id=_required_string(value, "trigger_id"),
        cited_reason=_required_string(value, "cited_reason"),
        user_visible_handoff_text=_required_string(value, "user_visible_handoff_text"),
        blocked_action_ids=_required_string_tuple(value, "blocked_action_ids"),
        source_evidence_ids=_required_string_tuple(value, "source_evidence_ids"),
    )


def _safe_alternative_from_mapping(value: Any) -> SafeAlternative:
    if not isinstance(value, Mapping):
        raise ValueError("next_safe_alternatives must contain mappings")
    return SafeAlternative(
        action_id=_required_string(value, "action_id"),
        action_type=_required_string(value, "action_type"),
        label=_required_string(value, "label"),
        preserves_official_state=_required_bool(value, "preserves_official_state"),
    )


def _required_list(data: Mapping[str, Any], key: str) -> list[Any]:
    value = data.get(key)
    if not isinstance(value, list) or not value:
        raise ValueError(f"{key} must be a non-empty list")
    return value


def _required_string(data: Mapping[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a non-empty string")
    return value.strip()


def _required_bool(data: Mapping[str, Any], key: str) -> bool:
    value = data.get(key)
    if not isinstance(value, bool):
        raise ValueError(f"{key} must be a boolean")
    return value


def _required_string_tuple(data: Mapping[str, Any], key: str) -> tuple[str, ...]:
    value = data.get(key)
    if isinstance(value, str):
        items: Sequence[Any] = (value,)
    elif isinstance(value, list):
        items = value
    else:
        raise ValueError(f"{key} must be a string or list of strings")
    normalized = tuple(item.strip() for item in items if isinstance(item, str) and item.strip())
    if not normalized:
        raise ValueError(f"{key} must contain at least one string")
    return normalized
