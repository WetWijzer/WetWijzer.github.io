"""Validation for reversible PDF draft preview packet v2 safety boundaries.

The validator is intentionally data-shape oriented so preview packet checks can run
against deterministic fixtures before any live crawl, private file, generated PDF,
upload, submission, certification, or mutation workflow is attempted.
"""

from __future__ import annotations

from pathlib import PurePosixPath, PureWindowsPath
from typing import Any, Mapping, Sequence


FORBIDDEN_CLAIM_TERMS = (
    "uploaded",
    "upload complete",
    "submitted",
    "submission complete",
    "certified",
    "certification complete",
    "filed",
    "live devhub",
    "devhub session",
    "permit approved",
    "approval guaranteed",
    "guaranteed approval",
    "legal advice",
    "legally sufficient",
    "will be approved",
)

PRIVATE_PATH_MARKERS = (
    "/home/",
    "/users/",
    "/var/folders/",
    "/tmp/",
    "/private/",
    "c:\\users\\",
    "c:/users/",
    "appdata\\",
)

PDF_ARTIFACT_SUFFIXES = (
    ".pdf",
    ".xfa",
    ".fdf",
    ".xfdf",
)


class PacketValidationError(ValueError):
    """Raised when a packet is missing required safety evidence."""

    def __init__(self, errors: Sequence[str]) -> None:
        self.errors = tuple(errors)
        super().__init__("; ".join(self.errors))


def validate_reversible_pdf_draft_preview_packet_v2(packet: Mapping[str, Any]) -> None:
    """Validate reversible PDF draft preview packet v2 safety evidence.

    Raises:
        PacketValidationError: if the packet is incomplete or contains unsafe claims.
    """

    errors: list[str] = []

    _require_non_empty_list(packet, "synthetic_facts", errors)
    _require_non_empty_list(packet, "pdf_field_plan_rows", errors)
    _require_non_empty_list(packet, "unsupported_field_notes", errors)
    _require_non_empty_list(packet, "required_fact_gaps", errors)
    _require_non_empty_list(packet, "citation_references", errors)
    _require_non_empty_list(packet, "user_visible_review_checkpoints", errors)
    _require_non_empty_list(packet, "no_private_file_assurances", errors)
    _require_non_empty_list(packet, "validation_commands", errors)

    active_mutation_flags = packet.get("active_mutation_flags")
    if active_mutation_flags not in (None, [], {}, False):
        errors.append("active_mutation_flags must be absent or empty")

    raw_or_generated_pdf_artifacts = packet.get("raw_or_generated_pdf_artifacts")
    if raw_or_generated_pdf_artifacts not in (None, [], {}, False):
        errors.append("raw_or_generated_pdf_artifacts must be absent or empty")

    _reject_private_paths(packet, errors)
    _reject_pdf_artifact_paths(packet, errors)
    _reject_forbidden_claims(packet, errors)

    if errors:
        raise PacketValidationError(errors)


def packet_validation_errors(packet: Mapping[str, Any]) -> list[str]:
    """Return validation errors without raising."""

    try:
        validate_reversible_pdf_draft_preview_packet_v2(packet)
    except PacketValidationError as exc:
        return list(exc.errors)
    return []


def _require_non_empty_list(packet: Mapping[str, Any], key: str, errors: list[str]) -> None:
    value = packet.get(key)
    if not isinstance(value, list) or not value:
        errors.append(f"{key} must be a non-empty list")


def _reject_private_paths(value: Any, errors: list[str]) -> None:
    for text in _walk_text(value):
        normalized = text.lower().replace("\\\\", "\\")
        if any(marker in normalized for marker in PRIVATE_PATH_MARKERS):
            errors.append("packet must not contain private file paths")
            return
        if _looks_like_absolute_private_path(text):
            errors.append("packet must not contain private file paths")
            return


def _reject_pdf_artifact_paths(value: Any, errors: list[str]) -> None:
    for text in _walk_text(value):
        stripped = text.strip().lower()
        if any(stripped.endswith(suffix) for suffix in PDF_ARTIFACT_SUFFIXES):
            errors.append("packet must not contain raw or generated PDF artifacts")
            return


def _reject_forbidden_claims(value: Any, errors: list[str]) -> None:
    for text in _walk_text(value):
        lowered = " ".join(text.lower().split())
        if any(term in lowered for term in FORBIDDEN_CLAIM_TERMS):
            errors.append("packet must not contain upload, submission, certification, live DevHub, legal, permitting guarantee, or mutation claims")
            return


def _walk_text(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, Mapping):
        found: list[str] = []
        for key, item in value.items():
            found.extend(_walk_text(key))
            found.extend(_walk_text(item))
        return found
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        found = []
        for item in value:
            found.extend(_walk_text(item))
        return found
    return []


def _looks_like_absolute_private_path(text: str) -> bool:
    if not text or " " in text.strip():
        return False
    posix = PurePosixPath(text)
    if posix.is_absolute() and len(posix.parts) > 2:
        return True
    windows = PureWindowsPath(text)
    return windows.is_absolute() and len(windows.parts) > 2
