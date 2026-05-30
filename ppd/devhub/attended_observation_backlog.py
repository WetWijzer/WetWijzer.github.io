"""Fixture-first DevHub attended read-only observation backlog packets.

This module intentionally models only committed, synthetic observations. It does
not open browsers, persist session state, write traces, save screenshots, create
HAR files, store auth state, or capture private values.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

PACKET_VERSION = "devhub-attended-readonly-observation-backlog-v1"
READ_ONLY_ACTIONS = frozenset(
    {
        "observe_accessible_structure",
        "observe_status_text",
        "observe_fee_notice_presence",
        "observe_correction_request_presence",
        "observe_attachment_list_structure",
        "observe_inspection_result_presence",
    }
)
CONSEQUENTIAL_ACTION_KEYWORDS = (
    "submit",
    "certify",
    "upload",
    "purchase",
    "pay",
    "payment",
    "schedule",
    "cancel",
    "withdraw",
    "extension",
    "reactivation",
    "account_security",
)
FORBIDDEN_ARTIFACT_TYPES = frozenset(
    {
        "session_state",
        "trace",
        "screenshot",
        "har",
        "auth_file",
        "private_value",
        "official_action_artifact",
        "raw_authenticated_output",
    }
)


@dataclass(frozen=True)
class ObservationWorkItem:
    """A committed, redacted, manually attended DevHub observation task."""

    order: int
    work_item_id: str
    surface_id: str
    objective: str
    safe_read_only_evidence_needs: tuple[str, ...]
    redaction_requirements: tuple[str, ...]
    manual_attendance_checkpoints: tuple[str, ...]
    blocked_consequential_actions: tuple[str, ...]
    offline_validation_commands: tuple[tuple[str, ...], ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "order": self.order,
            "work_item_id": self.work_item_id,
            "surface_id": self.surface_id,
            "objective": self.objective,
            "safe_read_only_evidence_needs": list(self.safe_read_only_evidence_needs),
            "redaction_requirements": list(self.redaction_requirements),
            "manual_attendance_checkpoints": list(self.manual_attendance_checkpoints),
            "blocked_consequential_actions": list(self.blocked_consequential_actions),
            "offline_validation_commands": [list(command) for command in self.offline_validation_commands],
        }


def build_observation_backlog_packet(fixture: Mapping[str, Any]) -> dict[str, Any]:
    """Compile a synthetic fixture into an ordered observation backlog packet.

    The fixture is expected to describe synthetic DevHub surfaces and policy
    constraints only. The returned packet contains no browser/session artifacts
    and rejects any fixture that asks for prohibited capture types.
    """

    _validate_fixture_header(fixture)
    defaults = fixture.get("defaults", {})
    redaction_defaults = _string_tuple(defaults.get("redaction_requirements", ()))
    attendance_defaults = _string_tuple(defaults.get("manual_attendance_checkpoints", ()))
    validation_defaults = _command_tuple(defaults.get("offline_validation_commands", ()))

    work_items: list[ObservationWorkItem] = []
    for index, surface in enumerate(fixture.get("synthetic_surfaces", ()), start=1):
        if not isinstance(surface, Mapping):
            raise ValueError("synthetic_surfaces entries must be objects")
        work_items.append(
            _surface_to_work_item(
                surface=surface,
                order=index,
                redaction_defaults=redaction_defaults,
                attendance_defaults=attendance_defaults,
                validation_defaults=validation_defaults,
            )
        )

    return {
        "packet_version": PACKET_VERSION,
        "packet_id": _required_string(fixture, "packet_id"),
        "source_fixture_id": _required_string(fixture, "fixture_id"),
        "mode": "fixture_first_attended_read_only_observation",
        "artifact_policy": {
            "creates_session_state": False,
            "creates_traces": False,
            "creates_screenshots": False,
            "creates_har_files": False,
            "creates_auth_files": False,
            "captures_private_values": False,
            "creates_official_action_artifacts": False,
        },
        "work_items": [item.to_dict() for item in sorted(work_items, key=lambda item: item.order)],
    }


def validate_observation_backlog_packet(packet: Mapping[str, Any]) -> list[str]:
    """Return deterministic validation errors for a compiled packet."""

    errors: list[str] = []
    if packet.get("packet_version") != PACKET_VERSION:
        errors.append("packet_version must be devhub-attended-readonly-observation-backlog-v1")
    if packet.get("mode") != "fixture_first_attended_read_only_observation":
        errors.append("mode must be fixture_first_attended_read_only_observation")

    artifact_policy = packet.get("artifact_policy", {})
    if not isinstance(artifact_policy, Mapping):
        errors.append("artifact_policy must be an object")
    else:
        for key, value in artifact_policy.items():
            if value is not False:
                errors.append(f"artifact_policy.{key} must be false")

    work_items = packet.get("work_items", [])
    if not isinstance(work_items, list) or not work_items:
        errors.append("work_items must be a non-empty list")
        return errors

    expected_order = list(range(1, len(work_items) + 1))
    observed_order: list[int] = []
    seen_ids: set[str] = set()
    for item in work_items:
        if not isinstance(item, Mapping):
            errors.append("each work item must be an object")
            continue
        order = item.get("order")
        if isinstance(order, int):
            observed_order.append(order)
        else:
            errors.append("work item order must be an integer")
        work_item_id = item.get("work_item_id")
        if not isinstance(work_item_id, str) or not work_item_id:
            errors.append("work item must include work_item_id")
        elif work_item_id in seen_ids:
            errors.append(f"duplicate work_item_id: {work_item_id}")
        else:
            seen_ids.add(work_item_id)
        _require_non_empty_list(item, "safe_read_only_evidence_needs", errors)
        _require_non_empty_list(item, "redaction_requirements", errors)
        _require_non_empty_list(item, "manual_attendance_checkpoints", errors)
        _require_non_empty_list(item, "blocked_consequential_actions", errors)
        _require_non_empty_command_list(item, "offline_validation_commands", errors)

    if sorted(observed_order) != expected_order:
        errors.append("work item order must be contiguous starting at 1")
    return errors


def _surface_to_work_item(
    *,
    surface: Mapping[str, Any],
    order: int,
    redaction_defaults: tuple[str, ...],
    attendance_defaults: tuple[str, ...],
    validation_defaults: tuple[tuple[str, ...], ...],
) -> ObservationWorkItem:
    surface_id = _required_string(surface, "surface_id")
    allowed_observations = _string_tuple(surface.get("allowed_observations", ()))
    unsupported_actions = _string_tuple(surface.get("blocked_consequential_actions", ()))
    requested_artifacts = frozenset(_string_tuple(surface.get("requested_artifacts", ())))
    forbidden_requested = sorted(requested_artifacts.intersection(FORBIDDEN_ARTIFACT_TYPES))
    if forbidden_requested:
        raise ValueError(f"surface {surface_id} requests forbidden artifacts: {', '.join(forbidden_requested)}")

    for action in allowed_observations:
        if action not in READ_ONLY_ACTIONS:
            raise ValueError(f"surface {surface_id} has non-read-only observation: {action}")
    for action in unsupported_actions:
        lowered = action.lower()
        if not any(keyword in lowered for keyword in CONSEQUENTIAL_ACTION_KEYWORDS):
            raise ValueError(f"blocked action lacks consequential classification keyword: {action}")

    evidence_needs = tuple(
        dict.fromkeys(
            _string_tuple(surface.get("safe_read_only_evidence_needs", ()))
            + tuple(f"confirm synthetic {action.replace('_', ' ')}" for action in allowed_observations)
        )
    )
    redaction_requirements = tuple(
        dict.fromkeys(redaction_defaults + _string_tuple(surface.get("redaction_requirements", ())))
    )
    manual_attendance_checkpoints = tuple(
        dict.fromkeys(attendance_defaults + _string_tuple(surface.get("manual_attendance_checkpoints", ())))
    )

    if not evidence_needs:
        raise ValueError(f"surface {surface_id} must define safe read-only evidence needs")
    if not redaction_requirements:
        raise ValueError(f"surface {surface_id} must define redaction requirements")
    if not manual_attendance_checkpoints:
        raise ValueError(f"surface {surface_id} must define manual attendance checkpoints")
    if not unsupported_actions:
        raise ValueError(f"surface {surface_id} must define blocked consequential actions")

    return ObservationWorkItem(
        order=order,
        work_item_id=f"devhub-readonly-observe-{order:03d}-{surface_id}",
        surface_id=surface_id,
        objective=_required_string(surface, "objective"),
        safe_read_only_evidence_needs=evidence_needs,
        redaction_requirements=redaction_requirements,
        manual_attendance_checkpoints=manual_attendance_checkpoints,
        blocked_consequential_actions=unsupported_actions,
        offline_validation_commands=validation_defaults,
    )


def _validate_fixture_header(fixture: Mapping[str, Any]) -> None:
    if fixture.get("packet_version") != PACKET_VERSION:
        raise ValueError("fixture packet_version is not supported")
    if fixture.get("fixture_kind") != "synthetic_devhub_surface_observations":
        raise ValueError("fixture_kind must be synthetic_devhub_surface_observations")
    if not isinstance(fixture.get("synthetic_surfaces"), list) or not fixture["synthetic_surfaces"]:
        raise ValueError("synthetic_surfaces must be a non-empty list")


def _required_string(mapping: Mapping[str, Any], key: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"{key} must be a non-empty string")
    return value


def _string_tuple(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, Iterable) or isinstance(value, (str, bytes)):
        raise ValueError("expected a list of strings")
    result: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item:
            raise ValueError("expected a list of non-empty strings")
        result.append(item)
    return tuple(result)


def _command_tuple(value: Any) -> tuple[tuple[str, ...], ...]:
    if value is None:
        return ()
    if not isinstance(value, Iterable) or isinstance(value, (str, bytes)):
        raise ValueError("expected a list of command arrays")
    commands: list[tuple[str, ...]] = []
    for command in value:
        commands.append(_string_tuple(command))
    return tuple(commands)


def _require_non_empty_list(mapping: Mapping[str, Any], key: str, errors: list[str]) -> None:
    value = mapping.get(key)
    if not isinstance(value, list) or not value or not all(isinstance(item, str) and item for item in value):
        errors.append(f"{key} must be a non-empty list of strings")


def _require_non_empty_command_list(mapping: Mapping[str, Any], key: str, errors: list[str]) -> None:
    value = mapping.get(key)
    if not isinstance(value, list) or not value:
        errors.append(f"{key} must be a non-empty list of commands")
        return
    for command in value:
        if not isinstance(command, list) or not command or not all(isinstance(part, str) and part for part in command):
            errors.append(f"{key} must contain non-empty string command arrays")
