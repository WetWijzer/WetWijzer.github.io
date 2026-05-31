"""Validation for agent missing-information rehearsal packet v2.

The validator is intentionally conservative: rehearsal packets must contain the
rows and acknowledgements needed for a safe dry run, and must not claim live
DevHub access, official outcomes, legal guarantees, mutation, or private/raw
artifacts.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Any


REQUIRED_ROW_FIELDS = {
    "workflow_cases": ("case_id", "workflow", "expected_missing_information"),
    "missing_fact_rows": ("fact_id", "prompt", "reason"),
    "missing_document_rows": ("document_id", "document_type", "reason"),
    "stale_or_conflicting_evidence_rows": ("evidence_id", "issue", "resolution_prompt"),
    "blocked_actions": ("action", "reason"),
    "next_safe_action_rows": ("action", "precondition", "owner"),
    "citation_references": ("citation_id", "source", "locator"),
    "reviewer_dispositions": ("reviewer", "disposition", "reason"),
    "validation_commands": ("command", "expected_result"),
}

REQUIRED_CONFIRMATIONS = (
    "dry_run_only",
    "no_private_session_artifacts",
    "no_official_action_completion_claims",
    "no_legal_or_permitting_guarantees",
    "no_live_crawl_or_devhub_claims",
    "no_active_mutation_flags",
)

PRIVATE_ARTIFACT_TOKENS = (
    "auth_state",
    "browser_state",
    "cookies",
    "devhub_session",
    "downloaded",
    "private_session",
    "raw_crawl",
    "session_storage",
    "trace.zip",
    "traces/",
)

PROHIBITED_TEXT_TOKENS = (
    "approved by pp&d",
    "certified complete",
    "devhub live crawl",
    "final permit approval",
    "guaranteed approval",
    "guaranteed permit",
    "legal advice",
    "legally guaranteed",
    "live devhub session",
    "official action completed",
    "officially submitted",
    "permit guaranteed",
)

MUTATION_KEYS = (
    "active_mutation",
    "active_mutation_flags",
    "cancel",
    "certify",
    "create_account",
    "mutation_enabled",
    "pay",
    "submit",
    "upload",
    "write_enabled",
)


@dataclass(frozen=True)
class PacketValidationResult:
    valid: bool
    errors: tuple[str, ...]


def validate_missing_information_packet_v2(packet: Mapping[str, Any]) -> PacketValidationResult:
    """Return validation errors for a rehearsal packet v2 mapping."""

    errors: list[str] = []

    if packet.get("packet_version") != "agent-missing-information-rehearsal-v2":
        errors.append("packet_version must be agent-missing-information-rehearsal-v2")

    for section, required_fields in REQUIRED_ROW_FIELDS.items():
        rows = packet.get(section)
        if not isinstance(rows, Sequence) or isinstance(rows, (str, bytes)) or not rows:
            errors.append(f"{section} must contain at least one row")
            continue
        for index, row in enumerate(rows):
            if not isinstance(row, Mapping):
                errors.append(f"{section}[{index}] must be an object")
                continue
            for field in required_fields:
                value = row.get(field)
                if value in (None, "", []):
                    errors.append(f"{section}[{index}].{field} is required")

    confirmations = packet.get("required_confirmations")
    if not isinstance(confirmations, Mapping):
        errors.append("required_confirmations must be an object")
    else:
        for confirmation in REQUIRED_CONFIRMATIONS:
            if confirmations.get(confirmation) is not True:
                errors.append(f"required_confirmations.{confirmation} must be true")

    artifact_paths = packet.get("artifact_paths", [])
    if artifact_paths is None:
        artifact_paths = []
    if not isinstance(artifact_paths, Sequence) or isinstance(artifact_paths, (str, bytes)):
        errors.append("artifact_paths must be a list when present")
    else:
        for index, path_value in enumerate(artifact_paths):
            if not isinstance(path_value, str):
                errors.append(f"artifact_paths[{index}] must be a string")
                continue
            normalized = str(PurePosixPath(path_value.lower()))
            if any(token in normalized for token in PRIVATE_ARTIFACT_TOKENS):
                errors.append(f"artifact_paths[{index}] references private/session/browser/raw/downloaded artifact")

    _collect_prohibited_claim_errors(packet, errors)
    _collect_mutation_errors(packet, errors)

    return PacketValidationResult(valid=not errors, errors=tuple(errors))


def _collect_prohibited_claim_errors(value: Any, errors: list[str], path: str = "$") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            _collect_prohibited_claim_errors(child, errors, f"{path}.{key}")
        return
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child in enumerate(value):
            _collect_prohibited_claim_errors(child, errors, f"{path}[{index}]")
        return
    if isinstance(value, str):
        lowered = value.lower()
        for token in PROHIBITED_TEXT_TOKENS:
            if token in lowered:
                errors.append(f"{path} contains prohibited claim: {token}")


def _collect_mutation_errors(value: Any, errors: list[str], path: str = "$") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key).lower()
            child_path = f"{path}.{key}"
            if key_text in MUTATION_KEYS and child not in (False, None, "", [], {}):
                errors.append(f"{child_path} enables or requests an active mutation")
            _collect_mutation_errors(child, errors, child_path)
        return
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child in enumerate(value):
            _collect_mutation_errors(child, errors, f"{path}[{index}]")
