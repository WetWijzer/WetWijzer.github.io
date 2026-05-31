"""Fixture-first DevHub authenticated workflow boundary packet v2.

This module is intentionally offline-only. It defines validation helpers for a
synthetic packet that classifies account-scoped DevHub surfaces by action risk
without opening DevHub, creating browser state, or performing authenticated work.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PACKET_VERSION = "devhub-authenticated-workflow-boundary-packet-v2"

ACTION_CATEGORIES = {
    "read_only",
    "reversible_draft",
    "consequential_official",
    "financial",
    "unsupported_manual_handoff",
}

REQUIRED_PACKET_KEYS = {
    "packet_id",
    "version",
    "scope",
    "non_actions",
    "offline_validation_commands",
    "redaction_expectations",
    "abort_conditions",
    "reviewer_placeholders",
    "surfaces",
}

REQUIRED_SURFACE_KEYS = {
    "surface_id",
    "synthetic_account_scope",
    "surface_label",
    "action_category",
    "attendance_required",
    "exact_confirmation_required",
    "allowed_offline_assistance",
    "prohibited_automation",
    "redaction_expectations",
    "abort_conditions",
    "reviewer_placeholder",
}

SENSITIVE_TERMS = (
    "cookie",
    "password",
    "mfa",
    "captcha",
    "payment card",
    "card number",
    "bank account",
    "session storage",
    "auth state",
    "har",
    "trace",
    "screenshot",
)


def fixture_path() -> Path:
    """Return the committed packet fixture path."""
    return Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "devhub" / "authenticated_workflow_boundary_packet_v2.json"


def load_packet(path: Path | None = None) -> dict[str, Any]:
    """Load a boundary packet from a fixture path."""
    packet_file = path or fixture_path()
    return json.loads(packet_file.read_text(encoding="utf-8"))


def validate_packet(packet: dict[str, Any]) -> list[str]:
    """Return deterministic validation errors for a boundary packet."""
    errors: list[str] = []

    missing_packet_keys = sorted(REQUIRED_PACKET_KEYS - set(packet))
    if missing_packet_keys:
        errors.append("missing packet keys: " + ", ".join(missing_packet_keys))

    if packet.get("version") != PACKET_VERSION:
        errors.append("packet version must be " + PACKET_VERSION)

    surfaces = packet.get("surfaces")
    if not isinstance(surfaces, list) or not surfaces:
        errors.append("surfaces must be a non-empty list")
        return errors

    categories_seen: set[str] = set()
    surface_ids: set[str] = set()

    for index, surface in enumerate(surfaces):
        if not isinstance(surface, dict):
            errors.append(f"surface {index} must be an object")
            continue

        surface_id = surface.get("surface_id")
        if not isinstance(surface_id, str) or not surface_id:
            errors.append(f"surface {index} must have a surface_id")
            surface_id = f"surface[{index}]"
        elif surface_id in surface_ids:
            errors.append(f"duplicate surface_id: {surface_id}")
        else:
            surface_ids.add(surface_id)

        missing_surface_keys = sorted(REQUIRED_SURFACE_KEYS - set(surface))
        if missing_surface_keys:
            errors.append(f"{surface_id} missing keys: " + ", ".join(missing_surface_keys))

        category = surface.get("action_category")
        if category not in ACTION_CATEGORIES:
            errors.append(f"{surface_id} has unsupported action_category: {category}")
        else:
            categories_seen.add(category)

        attendance_required = surface.get("attendance_required")
        exact_required = surface.get("exact_confirmation_required")
        if category in {"consequential_official", "financial", "unsupported_manual_handoff"}:
            if attendance_required is not True:
                errors.append(f"{surface_id} must require attendance")
            if exact_required is not True:
                errors.append(f"{surface_id} must require exact confirmation")
        if category == "read_only" and exact_required is True:
            errors.append(f"{surface_id} read-only actions must not require exact confirmation")

        for list_key in ("allowed_offline_assistance", "prohibited_automation", "redaction_expectations", "abort_conditions"):
            value = surface.get(list_key)
            if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
                errors.append(f"{surface_id} {list_key} must be a non-empty list of strings")

    missing_categories = sorted(ACTION_CATEGORIES - categories_seen)
    if missing_categories:
        errors.append("missing action categories: " + ", ".join(missing_categories))

    commands = packet.get("offline_validation_commands")
    if not isinstance(commands, list) or not commands:
        errors.append("offline_validation_commands must be a non-empty list")
    else:
        for command in commands:
            if not isinstance(command, list) or not all(isinstance(part, str) and part for part in command):
                errors.append("each offline validation command must be a non-empty string array")

    redactions = packet.get("redaction_expectations")
    if not isinstance(redactions, list):
        errors.append("redaction_expectations must be a list")
    else:
        redaction_text = " ".join(redactions).lower()
        missing_terms = [term for term in SENSITIVE_TERMS if term not in redaction_text]
        if missing_terms:
            errors.append("redaction expectations missing terms: " + ", ".join(missing_terms))

    return errors


def assert_valid_packet(packet: dict[str, Any]) -> None:
    """Raise AssertionError when the packet is not valid."""
    errors = validate_packet(packet)
    if errors:
        raise AssertionError("; ".join(errors))


__all__ = [
    "ACTION_CATEGORIES",
    "PACKET_VERSION",
    "assert_valid_packet",
    "fixture_path",
    "load_packet",
    "validate_packet",
]
