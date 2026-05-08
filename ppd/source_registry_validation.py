"""Validation helpers for PP&D source registry surface policy.

This module is intentionally small and deterministic. It validates declared source
surfaces before any crawler or authenticated automation decides whether a source
is eligible for collection.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


SUPPORTED_SURFACES = frozenset(
    {
        "public",
        "authenticated_read_only",
        "reversible_draft",
    }
)

BLOCKED_SURFACES = frozenset(
    {
        "consequential_official",
        "financial",
        "unsupported",
    }
)

ALL_SURFACES = SUPPORTED_SURFACES | BLOCKED_SURFACES


@dataclass(frozen=True)
class SourceValidationResult:
    """Result of validating one PP&D source registry entry."""

    source_id: str
    surface: str
    allowed: bool
    reason: str


def validate_source_entry(entry: Mapping[str, Any]) -> SourceValidationResult:
    """Validate a single source registry entry.

    Expected entry fields are intentionally minimal:
    - id: stable source identifier
    - surface: one of the known PP&D surface categories
    - authenticated: optional bool for authenticated surfaces
    - read_only: optional bool for authenticated surfaces
    - reversible: optional bool for draft workflows
    """

    source_id_value = entry.get("id", "")
    source_id = source_id_value if isinstance(source_id_value, str) else ""

    surface_value = entry.get("surface", "unsupported")
    surface = surface_value if isinstance(surface_value, str) else "unsupported"

    if surface not in ALL_SURFACES:
        return SourceValidationResult(
            source_id=source_id,
            surface=surface,
            allowed=False,
            reason="unknown surface category",
        )

    if surface in BLOCKED_SURFACES:
        return SourceValidationResult(
            source_id=source_id,
            surface=surface,
            allowed=False,
            reason=f"{surface} surfaces require manual handling outside automation",
        )

    if surface == "authenticated_read_only":
        if entry.get("authenticated") is not True:
            return SourceValidationResult(
                source_id=source_id,
                surface=surface,
                allowed=False,
                reason="authenticated_read_only sources must declare authenticated=true",
            )
        if entry.get("read_only") is not True:
            return SourceValidationResult(
                source_id=source_id,
                surface=surface,
                allowed=False,
                reason="authenticated_read_only sources must declare read_only=true",
            )

    if surface == "reversible_draft" and entry.get("reversible") is not True:
        return SourceValidationResult(
            source_id=source_id,
            surface=surface,
            allowed=False,
            reason="reversible_draft sources must declare reversible=true",
        )

    return SourceValidationResult(
        source_id=source_id,
        surface=surface,
        allowed=True,
        reason="surface is eligible for PP&D source automation",
    )


def validate_source_registry(entries: list[Mapping[str, Any]]) -> list[SourceValidationResult]:
    """Validate a list of source registry entries."""

    return [validate_source_entry(entry) for entry in entries]
