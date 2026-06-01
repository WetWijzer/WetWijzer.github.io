"""Validation for fixture-first attended DevHub read-only observation packets."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence


class AuthorizationPacketError(ValueError):
    """Raised when a read-only observation authorization packet is unsafe or incomplete."""


@dataclass(frozen=True)
class ReadOnlyObservationAuthorizationPacket:
    """Commit-safe authorization packet for attended DevHub read-only observation."""

    packet: Mapping[str, Any]

    @property
    def packet_id(self) -> str:
        value = self.packet.get("packet_id")
        if not isinstance(value, str) or not value:
            raise AuthorizationPacketError("packet_id must be a non-empty string")
        return value

    def validate(self) -> None:
        _require_equal(
            self.packet,
            "schema_version",
            "attended-devhub-read-only-observation-authorization-packet/v1",
        )
        _require_equal(self.packet, "mode", "fixture_first_read_only_observation")
        _require_equal(self.packet, "live_devhub_opening_authorized", False)
        _require_equal(self.packet, "auth_state_storage_authorized", False)
        _require_equal(self.packet, "active_devhub_mutation_authorized", False)
        _require_non_empty_sequence(self.packet, "synthetic_user_attendance_prerequisites")
        _require_non_empty_sequence(self.packet, "allowed_read_only_surfaces")
        _require_non_empty_sequence(self.packet, "redaction_requirements")
        _require_non_empty_sequence(self.packet, "stop_conditions")
        _require_non_empty_sequence(self.packet, "manual_handoff_points")
        _require_non_empty_sequence(self.packet, "observation_evidence_placeholders")
        _require_exact_offline_validation_commands(self.packet)
        _require_forbidden_actions(self.packet)


def validate_read_only_observation_authorization_packet(
    packet: Mapping[str, Any],
) -> ReadOnlyObservationAuthorizationPacket:
    authorization = ReadOnlyObservationAuthorizationPacket(packet=packet)
    authorization.validate()
    return authorization


def _require_equal(packet: Mapping[str, Any], key: str, expected: object) -> None:
    actual = packet.get(key)
    if actual != expected:
        raise AuthorizationPacketError(f"{key} must be {expected!r}")


def _require_non_empty_sequence(packet: Mapping[str, Any], key: str) -> Sequence[Any]:
    value = packet.get(key)
    if not isinstance(value, list) or not value:
        raise AuthorizationPacketError(f"{key} must be a non-empty list")
    return value


def _require_exact_offline_validation_commands(packet: Mapping[str, Any]) -> None:
    commands = packet.get("offline_validation_commands")
    expected = [
        ["python3", "-m", "py_compile", "ppd/devhub/read_only_observation_authorization.py"],
        ["python3", "-m", "pytest", "ppd/tests/test_read_only_observation_authorization_packet.py"],
        ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
    ]
    if commands != expected:
        raise AuthorizationPacketError("offline_validation_commands must contain only the exact offline validation commands")


def _require_forbidden_actions(packet: Mapping[str, Any]) -> None:
    prohibited = packet.get("prohibited_actions")
    if not isinstance(prohibited, list):
        raise AuthorizationPacketError("prohibited_actions must be a list")
    required = {
        "open_devhub",
        "store_auth_state",
        "create_screenshots_traces_or_har",
        "read_private_values",
        "fill_forms",
        "upload_files",
        "submit_requests",
        "certify_acknowledgements",
        "enter_or_execute_payments",
        "schedule_or_cancel_inspections",
        "change_account_settings",
        "mutate_active_devhub_surface_prompt_guardrail_process_model_release_crawler_or_daemon_state",
    }
    missing = sorted(required.difference(prohibited))
    if missing:
        raise AuthorizationPacketError("prohibited_actions is missing: " + ", ".join(missing))
