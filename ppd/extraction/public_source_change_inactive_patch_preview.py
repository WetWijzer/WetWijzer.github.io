"""Fixture-first public source change inactive patch preview v1.

This module consumes public source change reviewer disposition queues and builds a
metadata-only before/after preview for inactive public-source fixtures. It never
applies fixture changes, crawls sources, downloads documents, mutates active
artifacts, changes prompts, or updates release state.
"""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any, Mapping

PREVIEW_VERSION = "public_source_change_inactive_patch_preview_v1"
QUEUE_VERSION = "public_source_change_reviewer_disposition_queue_v1"
MODE = "fixture_first_inactive_preview_only"
VALIDATION_COMMANDS = [
    ["python3", "-m", "py_compile", "ppd/extraction/public_source_change_inactive_patch_preview.py"],
    ["python3", "-m", "pytest", "ppd/tests/test_public_source_change_inactive_patch_preview.py"],
    ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
]

_MUTATION_FLAGS = (
    "active_source_mutation",
    "active_document_mutation",
    "active_requirement_mutation",
    "active_process_mutation",
    "active_guardrail_mutation",
    "active_release_state_mutation",
    "active_prompt_mutation",
    "active_fixture_mutation",
    "active_agent_state_mutation",
)

_FORBIDDEN_KEYS = {
    "auth",
    "auth_state",
    "authenticated_artifact",
    "browser_artifact",
    "browser_context",
    "browser_session",
    "cookies",
    "credentials",
    "devhub_session",
    "downloaded_data",
    "downloaded_document",
    "downloaded_file",
    "har",
    "password",
    "pdf_bytes",
    "private_artifact",
    "raw_body",
    "raw_crawl",
    "raw_crawl_output",
    "raw_download",
    "raw_html",
    "raw_pdf",
    "response_body",
    "screenshot",
    "session_artifact",
    "session_storage",
    "storage_state",
    "trace",
}

_FORBIDDEN_PHRASES = (
    "applied promotion",
    "authenticated session",
    "certify acknowledgement",
    "downloaded data",
    "downloaded document",
    "downloaded pdf",
    "fixture changes applied",
    "guaranteed approval",
    "guaranteed permit",
    "legal advice",
    "legal outcome guaranteed",
    "live crawl",
    "permit will be approved",
    "raw crawl",
    "raw pdf",
    "refresh complete",
    "schedule inspection",
    "submit application",
    "submit payment",
    "upload correction",
)

_MUTATION_KEY_FRAGMENTS = (
    "active_",
    "apply_",
    "applies_",
    "mutation",
    "mutates_",
    "promotion_applied",
    "update_active",
)

_ALLOWED_TOP_LEVEL_FALSE_FLAGS = {
    "applies_fixture_changes",
    "active_public_source_artifact_mutation",
    "live_source_crawl",
    "downloaded_documents",
    "prompt_changes",
    "release_state_updates",
}


class PublicSourceChangeInactivePatchPreviewError(ValueError):
    """Raised when a public source inactive patch preview is unsafe."""


def load_reviewer_disposition_queue(path: str | Path) -> dict[str, Any]:
    """Load a reviewer disposition queue fixture from disk."""
    with Path(path).open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("reviewer disposition queue fixture must be a JSON object")
    return value


def build_public_source_change_inactive_patch_preview_v1(queue: Mapping[str, Any]) -> dict[str, Any]:
    """Build an inactive public-source fixture patch preview from a reviewer queue."""
    _require_queue(queue)
    rows = [_preview_row(row, index) for index, row in enumerate(_queue_rows(queue), start=1)]

    packet: dict[str, Any] = {
        "preview_version": PREVIEW_VERSION,
        "input_queue_version": _queue_version(queue),
        "mode": MODE,
        "fixture_scope": "inactive_public_source_fixtures_only",
        "applies_fixture_changes": False,
        "active_public_source_artifact_mutation": False,
        "live_source_crawl": False,
        "downloaded_documents": False,
        "prompt_changes": False,
        "release_state_updates": False,
        "file_scoped_previews": rows,
        "citation_preservation_checks": _citation_checks(rows),
        "unchanged_row_inventory": _unchanged_inventory(rows),
        "blocked_row_explanations": _blocked_rows(rows),
        "reviewer_signoff_placeholders": _signoff_placeholders(rows),
        "rollback_notes": _rollback_notes(queue, rows),
        "validation_replay_commands": deepcopy(VALIDATION_COMMANDS),
        "mutation_flags": {flag: False for flag in _MUTATION_FLAGS},
    }
    errors = validate_public_source_change_inactive_patch_preview_v1(packet)
    if errors:
        raise PublicSourceChangeInactivePatchPreviewError("; ".join(errors))
    return packet


def validate_public_source_change_inactive_patch_preview_v1(packet: Mapping[str, Any]) -> list[str]:
    """Return deterministic validation errors for an inactive patch preview."""
    errors: list[str] = []
    if packet.get("preview_version") != PREVIEW_VERSION:
        errors.append(f"preview_version must be {PREVIEW_VERSION}")
    if packet.get("mode") != MODE:
        errors.append(f"mode must be {MODE}")
    if packet.get("fixture_scope") != "inactive_public_source_fixtures_only":
        errors.append("fixture_scope must be inactive_public_source_fixtures_only")

    for flag in _ALLOWED_TOP_LEVEL_FALSE_FLAGS:
        if packet.get(flag) is not False:
            errors.append(f"{flag} must be false")

    rows_value = packet.get("file_scoped_previews")
    rows: list[Mapping[str, Any]] = []
    if not isinstance(rows_value, list) or not rows_value:
        errors.append("file_scoped_previews must contain at least one row")
    else:
        for index, row in enumerate(rows_value):
            if not isinstance(row, Mapping):
                errors.append(f"file_scoped_previews[{index}] must be an object")
                continue
            rows.append(row)
            _validate_preview_row(row, index, errors)

    for field in (
        "citation_preservation_checks",
        "unchanged_row_inventory",
        "blocked_row_explanations",
        "reviewer_signoff_placeholders",
        "rollback_notes",
        "validation_replay_commands",
    ):
        if not isinstance(packet.get(field), list):
            errors.append(f"{field} must be a list")

    _validate_citation_checks(packet.get("citation_preservation_checks"), rows, errors)
    _validate_unchanged_inventory(packet.get("unchanged_row_inventory"), rows, errors)
    _validate_blocked_explanations(packet.get("blocked_row_explanations"), rows, errors)
    _validate_signoff_placeholders(packet.get("reviewer_signoff_placeholders"), rows, errors)

    rollback_notes = packet.get("rollback_notes")
    if not isinstance(rollback_notes, list) or not any(str(note).strip() for note in rollback_notes):
        errors.append("rollback_notes must contain rollback notes")

    commands = packet.get("validation_replay_commands")
    if not isinstance(commands, list) or not commands or not all(_valid_command(command) for command in commands):
        errors.append("validation_replay_commands must contain command arrays")

    mutation_flags = packet.get("mutation_flags")
    if not isinstance(mutation_flags, Mapping):
        errors.append("mutation_flags must be an object")
    else:
        for flag in _MUTATION_FLAGS:
            if mutation_flags.get(flag) is not False:
                errors.append(f"mutation_flags.{flag} must be false")
        for flag, value in mutation_flags.items():
            if flag not in _MUTATION_FLAGS and _is_active_flag(value):
                errors.append(f"mutation_flags.{flag} is outside inactive public-source fixture preview scope")

    _scan_for_forbidden_content(packet, "$", errors)
    return sorted(set(errors))


def assert_valid_public_source_change_inactive_patch_preview_v1(packet: Mapping[str, Any]) -> None:
    """Raise ValueError if an inactive patch preview is invalid."""
    errors = validate_public_source_change_inactive_patch_preview_v1(packet)
    if errors:
        raise ValueError("public source change inactive patch preview rejected: " + "; ".join(errors))


def _require_queue(queue: Mapping[str, Any]) -> None:
    if _queue_version(queue) != QUEUE_VERSION:
        raise ValueError(f"queue version must be {QUEUE_VERSION}")
    if not _queue_rows(queue):
        raise ValueError("queue must include reviewer decision rows")


def _queue_version(queue: Mapping[str, Any]) -> str:
    return str(queue.get("version") or queue.get("queue_version") or "")


def _queue_rows(queue: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    rows = queue.get("reviewer_decision_rows") or queue.get("decision_rows")
    if not isinstance(rows, list):
        return []
    return [row for row in rows if isinstance(row, Mapping)]


def _preview_row(row: Mapping[str, Any], index: int) -> dict[str, Any]:
    source_id = str(row.get("source_id") or row.get("change_id") or f"source-{index}")
    disposition = _normalize_disposition(row.get("disposition") or row.get("bucket"))
    impact_references = deepcopy(row.get("impact_references") or row.get("cited_impact_references") or [])
    blocked_reason = str(row.get("blocked_promotion_reason") or "").strip()
    promotion_blocked = row.get("promotion_blocked") is True or disposition == "needs_review" or bool(blocked_reason)
    inactive_fixture_path = f"ppd/tests/fixtures/public_source_change_inactive_patch_preview/inactive/{source_id}.json"

    before = {
        "fixture_state": "inactive",
        "source_id": source_id,
        "canonical_url": str(row.get("canonical_url") or ""),
        "reviewer_disposition": "not_applied",
        "citation_refs": _citation_refs(impact_references),
    }
    after = deepcopy(before)
    after.update(
        {
            "reviewer_disposition": disposition,
            "preview_only": True,
            "promotion_blocked": promotion_blocked,
            "citation_refs": _citation_refs(impact_references),
        }
    )

    return {
        "row_id": f"inactive-preview:{source_id}",
        "source_id": source_id,
        "inactive_fixture_path": inactive_fixture_path,
        "file_scope": inactive_fixture_path,
        "disposition": disposition,
        "before": before,
        "after": after,
        "impact_references": impact_references,
        "citation_preserved": bool(_citation_refs(impact_references)),
        "unchanged": disposition == "unchanged",
        "promotion_blocked": promotion_blocked,
        "blocked_explanation": blocked_reason or ("Human review is required before any fixture promotion." if promotion_blocked else ""),
        "reviewer_signoff_placeholder": {
            "reviewer": "TBD",
            "signed_at": "TBD",
            "decision": "pending_manual_review",
        },
        "rollback_note": f"Discard preview row for {source_id}; no active public source fixture was modified.",
    }


def _normalize_disposition(value: Any) -> str:
    normalized = str(value or "needs_review").strip().lower().replace("-", "_")
    if normalized not in {"changed", "unchanged", "needs_review"}:
        return "needs_review"
    return normalized


def _citation_refs(references: Any) -> list[str]:
    refs: list[str] = []
    if not isinstance(references, list):
        return refs
    for reference in references:
        if isinstance(reference, str) and reference.strip():
            refs.append(reference.strip())
        elif isinstance(reference, Mapping):
            for key in ("citation", "source_evidence_id", "canonical_url", "url", "reference_id"):
                value = reference.get(key)
                if isinstance(value, str) and value.strip():
                    refs.append(value.strip())
                    break
    return refs


def _citation_checks(rows: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "row_id": str(row.get("row_id")),
            "source_id": str(row.get("source_id")),
            "status": "pass" if row.get("citation_preserved") is True else "blocked",
            "citation_refs": deepcopy(row.get("after", {}).get("citation_refs", [])) if isinstance(row.get("after"), Mapping) else [],
        }
        for row in rows
    ]


def _unchanged_inventory(rows: list[Mapping[str, Any]]) -> list[dict[str, str]]:
    return [
        {
            "row_id": str(row.get("row_id")),
            "source_id": str(row.get("source_id")),
            "reason": "Reviewer disposition is unchanged; preview records no fixture content change.",
        }
        for row in rows
        if row.get("unchanged") is True
    ]


def _blocked_rows(rows: list[Mapping[str, Any]]) -> list[dict[str, str]]:
    blocked = []
    for row in rows:
        if row.get("promotion_blocked") is True:
            blocked.append(
                {
                    "row_id": str(row.get("row_id")),
                    "source_id": str(row.get("source_id")),
                    "explanation": str(row.get("blocked_explanation") or "Manual review blocks fixture promotion."),
                }
            )
    return blocked


def _signoff_placeholders(rows: list[Mapping[str, Any]]) -> list[dict[str, str]]:
    return [
        {
            "row_id": str(row.get("row_id")),
            "source_id": str(row.get("source_id")),
            "reviewer": "TBD",
            "signed_at": "TBD",
            "decision": "pending_manual_review",
        }
        for row in rows
    ]


def _rollback_notes(queue: Mapping[str, Any], rows: list[Mapping[str, Any]]) -> list[str]:
    notes = ["Discard this inactive preview packet; no fixture changes were applied."]
    queue_notes = queue.get("rollback_checkpoints")
    if isinstance(queue_notes, list):
        notes.extend(str(note) for note in queue_notes if str(note).strip())
    notes.extend(str(row.get("rollback_note")) for row in rows if str(row.get("rollback_note") or "").strip())
    return notes


def _validate_preview_row(row: Mapping[str, Any], index: int, errors: list[str]) -> None:
    row_path = f"file_scoped_previews[{index}]"
    if not str(row.get("source_id") or "").strip():
        errors.append(f"{row_path}.source_id is required")
    if not str(row.get("row_id") or "").strip():
        errors.append(f"{row_path}.row_id is required")
    path = str(row.get("inactive_fixture_path") or "")
    if not path.startswith("ppd/tests/fixtures/") or "/inactive/" not in path:
        errors.append(f"{row_path}.inactive_fixture_path must point to an inactive PP&D fixture")
    before = row.get("before")
    after = row.get("after")
    if not isinstance(before, Mapping) or not isinstance(after, Mapping):
        errors.append(f"{row_path} must include before and after objects")
        return
    if before.get("fixture_state") != "inactive":
        errors.append(f"{row_path}.before.fixture_state must be inactive")
    if after.get("fixture_state") != "inactive":
        errors.append(f"{row_path}.after.fixture_state must be inactive")
    if after.get("preview_only") is not True:
        errors.append(f"{row_path}.after.preview_only must be true")
    if row.get("disposition") == "changed" and not _citation_refs(row.get("impact_references")):
        errors.append(f"{row_path} changed rows must preserve citations")
    if row.get("citation_preserved") is not True:
        errors.append(f"{row_path} must preserve citations")
    if row.get("promotion_blocked") is True and not str(row.get("blocked_explanation") or "").strip():
        errors.append(f"{row_path}.blocked_explanation is required when blocked")


def _validate_citation_checks(value: Any, rows: list[Mapping[str, Any]], errors: list[str]) -> None:
    if not isinstance(value, list):
        return
    checks = [check for check in value if isinstance(check, Mapping)]
    if not checks and rows:
        errors.append("citation_preservation_checks must include one check per preview row")
        return
    checks_by_row = {str(check.get("row_id")): check for check in checks}
    for row in rows:
        row_id = str(row.get("row_id") or "")
        check = checks_by_row.get(row_id)
        if not check:
            errors.append(f"citation_preservation_checks missing row {row_id}")
            continue
        if check.get("status") != "pass":
            errors.append(f"citation_preservation_checks row {row_id} must pass")
        if not _citation_refs(check.get("citation_refs")):
            errors.append(f"citation_preservation_checks row {row_id} must include citation refs")


def _validate_unchanged_inventory(value: Any, rows: list[Mapping[str, Any]], errors: list[str]) -> None:
    if not isinstance(value, list):
        return
    inventory_by_row = {str(item.get("row_id")): item for item in value if isinstance(item, Mapping)}
    for row in rows:
        if row.get("unchanged") is True:
            row_id = str(row.get("row_id") or "")
            item = inventory_by_row.get(row_id)
            if not item:
                errors.append(f"unchanged_row_inventory missing unchanged row {row_id}")
            elif not str(item.get("reason") or "").strip():
                errors.append(f"unchanged_row_inventory row {row_id} must include a reason")


def _validate_blocked_explanations(value: Any, rows: list[Mapping[str, Any]], errors: list[str]) -> None:
    if not isinstance(value, list):
        return
    explanations_by_row = {str(item.get("row_id")): item for item in value if isinstance(item, Mapping)}
    for row in rows:
        if row.get("promotion_blocked") is True:
            row_id = str(row.get("row_id") or "")
            item = explanations_by_row.get(row_id)
            if not item:
                errors.append(f"blocked_row_explanations missing blocked row {row_id}")
            elif not str(item.get("explanation") or "").strip():
                errors.append(f"blocked_row_explanations row {row_id} must include an explanation")


def _validate_signoff_placeholders(value: Any, rows: list[Mapping[str, Any]], errors: list[str]) -> None:
    if not isinstance(value, list):
        return
    signoffs_by_row = {str(item.get("row_id")): item for item in value if isinstance(item, Mapping)}
    for row in rows:
        row_id = str(row.get("row_id") or "")
        item = signoffs_by_row.get(row_id)
        if not item:
            errors.append(f"reviewer_signoff_placeholders missing row {row_id}")
            continue
        if item.get("decision") != "pending_manual_review":
            errors.append(f"reviewer_signoff_placeholders row {row_id} must remain pending_manual_review")
        if not str(item.get("reviewer") or "").strip() or not str(item.get("signed_at") or "").strip():
            errors.append(f"reviewer_signoff_placeholders row {row_id} must include reviewer and signed_at placeholders")


def _valid_command(command: Any) -> bool:
    return isinstance(command, list) and bool(command) and all(isinstance(part, str) and part.strip() for part in command)


def _scan_for_forbidden_content(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            normalized_key = key_text.lower().replace("-", "_")
            child_path = f"{path}.{key_text}"
            if normalized_key in _FORBIDDEN_KEYS:
                errors.append(f"{child_path} must not include private, raw, downloaded, session, or browser artifacts")
            if _is_forbidden_mutation_key(normalized_key, child_path) and _is_active_flag(child):
                errors.append(f"{child_path} must not enable mutation outside inactive public-source fixture preview scope")
            _scan_for_forbidden_content(child, child_path, errors)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _scan_for_forbidden_content(child, f"{path}[{index}]", errors)
    elif isinstance(value, str):
        lowered = value.lower()
        for phrase in _FORBIDDEN_PHRASES:
            if phrase in lowered:
                errors.append(f"{path} must not include forbidden claim or artifact phrase: {phrase}")


def _is_forbidden_mutation_key(normalized_key: str, path: str) -> bool:
    if path.startswith("$.mutation_flags."):
        return False
    if normalized_key in _ALLOWED_TOP_LEVEL_FALSE_FLAGS and path.count(".") == 1:
        return False
    return any(fragment in normalized_key for fragment in _MUTATION_KEY_FRAGMENTS)


def _is_active_flag(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"active", "applied", "enabled", "true", "yes"}
    if isinstance(value, (list, tuple, dict)):
        return bool(value)
    return False


__all__ = [
    "PREVIEW_VERSION",
    "PublicSourceChangeInactivePatchPreviewError",
    "assert_valid_public_source_change_inactive_patch_preview_v1",
    "build_public_source_change_inactive_patch_preview_v1",
    "load_reviewer_disposition_queue",
    "validate_public_source_change_inactive_patch_preview_v1",
]
