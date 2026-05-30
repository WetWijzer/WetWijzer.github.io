"""Validation for inactive fixture promotion application dry-run v1 packets."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence


ARTIFACT_ID = "inactive_fixture_promotion_application_dry_run_v1"
SELF_TEST_COMMAND = ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]

_PRIVATE_ARTIFACT_TERMS = (
    "auth_state",
    "authenticated-browser",
    "browser_context",
    "cookie",
    "credential",
    "devhub_session",
    "har",
    "mfa",
    "password",
    "playwright-report",
    "private-devhub-session",
    "session_storage",
    "screenshot",
    "storage_state",
    "trace",
    "video.webm",
)

_RAW_ARTIFACT_TERMS = (
    "downloaded-data",
    "downloaded_document",
    "downloaded_pdf",
    "pdf_bytes",
    "raw_body",
    "raw-crawl-output",
    "raw_download",
    "raw_html",
    "raw_pdf",
    "response-body",
    "warc_payload",
)

_LIVE_CLAIM_TERMS = (
    "executed live",
    "fixture promoted",
    "live crawl completed",
    "live execution completed",
    "promotion complete",
    "promotion completed",
    "promotion executed",
    "promoted to active",
    "release state updated",
)

_GUARANTEE_TERMS = (
    "approval is guaranteed",
    "guarantee approval",
    "guaranteed approval",
    "legal advice",
    "legally sufficient",
    "permit approved",
    "permit will be approved",
    "will pass inspection",
)

_CONSEQUENTIAL_ACTION_TERMS = (
    "cancel permit",
    "certify acknowledgement",
    "certify application",
    "create account",
    "enter payment details",
    "make official changes",
    "pay fees",
    "purchase trade permit",
    "schedule inspection",
    "submit application",
    "submit payment",
    "submit permit",
    "upload corrections",
    "upload to devhub",
    "withdraw permit",
)

_MUTATION_FLAG_TERMS = (
    "active_source_mutation",
    "active_document_mutation",
    "active_requirement_mutation",
    "active_process_mutation",
    "active_guardrail_mutation",
    "active_prompt_mutation",
    "active_release_state_mutation",
    "active_fixture_mutation",
    "active_fixture_promotion",
    "active_agent_state_mutation",
    "source_mutation_enabled",
    "document_mutation_enabled",
    "requirement_mutation_enabled",
    "process_mutation_enabled",
    "guardrail_mutation_enabled",
    "prompt_mutation_enabled",
    "release_state_mutation_enabled",
    "fixture_mutation_enabled",
    "agent_state_mutation_enabled",
)

_BLOCKED_COMMAND_TERMS = (
    "live_public_crawl",
    "authenticated_devhub_browser_session",
    "captcha_automation",
    "mfa_automation",
    "account_creation",
    "payment_entry_or_submission",
    "permit_submission",
    "official_upload",
    "inspection_scheduling",
    "permit_or_request_cancellation",
)

_NEGATED_OR_BLOCKED_CONTEXT = (
    "do not ",
    "does not ",
    "must not ",
    "no ",
    "not ",
    "without ",
    "blocked ",
    "blocks ",
    "remain blocked",
    "remains blocked",
)

_CHANGED_TYPES = frozenset({"add_inactive_fixture", "update_inactive_fixture", "remove_inactive_fixture"})
_ALLOWED_TYPES = _CHANGED_TYPES | {"unchanged"}


@dataclass(frozen=True)
class DryRunValidationResult:
    valid: bool
    errors: tuple[str, ...]

    def require_valid(self) -> None:
        if not self.valid:
            raise ValueError("; ".join(self.errors))


def validate_inactive_fixture_promotion_application_dry_run_v1(packet: Mapping[str, Any]) -> DryRunValidationResult:
    errors: list[str] = []

    if packet.get("artifact_id") != ARTIFACT_ID:
        errors.append("artifact_id must be inactive_fixture_promotion_application_dry_run_v1")
    if packet.get("version") != 1:
        errors.append("version must be 1")
    if packet.get("dry_run") is not True:
        errors.append("dry_run must be true")
    if _text(packet.get("mutation_scope")) != "inactive_fixture_promotion_only":
        errors.append("mutation_scope must be inactive_fixture_promotion_only")

    _validate_patch_manifest_rows(errors, packet.get("patch_manifest_rows"))
    _validate_unchanged_file_inventory(errors, packet.get("unchanged_file_inventory"))
    _validate_validation_commands(errors, packet.get("validation_commands"))
    _validate_rollback_notes(errors, packet.get("rollback_notes"))

    _reject_terms(errors, packet, _PRIVATE_ARTIFACT_TERMS, "private/authenticated/session/browser artifact")
    _reject_terms(errors, packet, _RAW_ARTIFACT_TERMS, "raw crawl/PDF/downloaded data")
    _reject_terms(errors, packet, _LIVE_CLAIM_TERMS, "live execution claim")
    _reject_terms(errors, packet, _GUARANTEE_TERMS, "legal or permitting outcome guarantee")
    _reject_terms(errors, packet, _CONSEQUENTIAL_ACTION_TERMS, "consequential action language")
    _reject_terms(errors, packet, _MUTATION_FLAG_TERMS, "mutation flag outside inactive fixture promotion scope", reject_negated=True)

    return DryRunValidationResult(valid=not errors, errors=tuple(errors))


def assert_valid_inactive_fixture_promotion_application_dry_run_v1(packet: Mapping[str, Any]) -> None:
    validate_inactive_fixture_promotion_application_dry_run_v1(packet).require_valid()


def _validate_patch_manifest_rows(errors: list[str], value: Any) -> None:
    rows = _sequence(value)
    if not rows:
        errors.append("patch_manifest_rows must include patch-manifest rows")
        return
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            errors.append(f"patch_manifest_rows[{index}] must be an object")
            continue
        change_type = _text(row.get("change_type"))
        if change_type not in _ALLOWED_TYPES:
            errors.append(f"patch_manifest_rows[{index}].change_type must be inactive fixture change or unchanged")
        if not _text(row.get("patch_row_id")):
            errors.append(f"patch_manifest_rows[{index}].patch_row_id is required")
        target = _text(row.get("target_path"))
        if not target:
            errors.append(f"patch_manifest_rows[{index}].target_path is required")
        elif not target.startswith("ppd/tests/fixtures/"):
            errors.append(f"patch_manifest_rows[{index}].target_path must stay under ppd/tests/fixtures/")
        if row.get("inactive_fixture_promotion_scope") is not True:
            errors.append(f"patch_manifest_rows[{index}].inactive_fixture_promotion_scope must be true")
        if change_type in _CHANGED_TYPES:
            evidence = row.get("changed_row_evidence")
            if not isinstance(evidence, Mapping):
                errors.append(f"patch_manifest_rows[{index}].changed_row_evidence is required")
            elif not _string_list(evidence.get("citations")):
                errors.append(f"patch_manifest_rows[{index}].changed_row_evidence.citations is required")
            if not _string_list(row.get("citations")):
                errors.append(f"patch_manifest_rows[{index}].citations is required for changed rows")


def _validate_unchanged_file_inventory(errors: list[str], value: Any) -> None:
    rows = _sequence(value)
    if not rows:
        errors.append("unchanged_file_inventory must include unchanged-file inventory")
        return
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            errors.append(f"unchanged_file_inventory[{index}] must be an object")
            continue
        if not _text(row.get("file_path")):
            errors.append(f"unchanged_file_inventory[{index}].file_path is required")
        if not _text(row.get("content_hash")):
            errors.append(f"unchanged_file_inventory[{index}].content_hash is required")
        if row.get("asserted_unchanged") is not True:
            errors.append(f"unchanged_file_inventory[{index}].asserted_unchanged must be true")
        if not _string_list(row.get("citations")):
            errors.append(f"unchanged_file_inventory[{index}].citations is required")


def _validate_validation_commands(errors: list[str], value: Any) -> None:
    commands = _sequence(value)
    if not commands:
        errors.append("validation_commands must include offline validation commands")
        return
    if not any(list(_string_list_values(command)) == SELF_TEST_COMMAND for command in commands):
        errors.append("validation_commands must include the PP&D daemon self-test command")
    for index, command in enumerate(commands):
        parts = _string_list_values(command)
        if not parts:
            errors.append(f"validation_commands[{index}] must be a list of command strings")
            continue
        command_text = " ".join(parts).lower()
        for term in _BLOCKED_COMMAND_TERMS:
            if term in command_text or term.replace("_", " ") in command_text:
                errors.append(f"validation_commands[{index}] must not include blocked live or consequential behavior: {term}")
                break


def _validate_rollback_notes(errors: list[str], value: Any) -> None:
    notes = _sequence(value)
    if not notes:
        errors.append("rollback_notes must include rollback notes")
        return
    for index, note in enumerate(notes):
        if not isinstance(note, Mapping):
            errors.append(f"rollback_notes[{index}] must be an object")
            continue
        if not _text(note.get("note_id")):
            errors.append(f"rollback_notes[{index}].note_id is required")
        if not _text(note.get("rollback_action")):
            errors.append(f"rollback_notes[{index}].rollback_action is required")
        if note.get("local_discard_only") is not True:
            errors.append(f"rollback_notes[{index}].local_discard_only must be true")
        if not _string_list(note.get("citations")):
            errors.append(f"rollback_notes[{index}].citations is required")


def _reject_terms(errors: list[str], value: Any, terms: Iterable[str], label: str, *, reject_negated: bool = False) -> None:
    lowered_terms = tuple(term.lower() for term in terms)
    for path, text in _walk_strings(value):
        lowered = " ".join(text.lower().replace("_", " ").replace("-", " ").split())
        compact = text.lower().replace("-", "_")
        if not reject_negated and any(prefix in lowered for prefix in _NEGATED_OR_BLOCKED_CONTEXT):
            continue
        for term in lowered_terms:
            normalized = " ".join(term.replace("_", " ").replace("-", " ").split())
            if normalized in lowered or term in compact:
                errors.append(f"reject {label} at {path}: {term}")
                break


def _walk_strings(value: Any, path: str = "$." ) -> Iterable[tuple[str, str]]:
    if isinstance(value, str):
        yield path.rstrip("."), value
    elif isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            yield from _walk_strings(key_text, f"{path}{key_text}#key.")
            yield from _walk_strings(child, f"{path}{key_text}.")
    elif isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray, str)):
        for index, child in enumerate(value):
            yield from _walk_strings(child, f"{path}[{index}].")


def _sequence(value: Any) -> tuple[Any, ...]:
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray, str)):
        return tuple(value)
    return ()


def _text(value: Any) -> str:
    if isinstance(value, str):
        return value.strip()
    return ""


def _string_list(value: Any) -> bool:
    return bool(_string_list_values(value))


def _string_list_values(value: Any) -> tuple[str, ...]:
    if not isinstance(value, Sequence) or isinstance(value, (bytes, bytearray, str)):
        return ()
    return tuple(item.strip() for item in value if isinstance(item, str) and item.strip())
