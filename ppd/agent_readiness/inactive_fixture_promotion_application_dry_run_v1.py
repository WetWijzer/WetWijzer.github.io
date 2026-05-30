"""Inactive fixture promotion application dry-run v1.

This module turns an already-built inactive fixture promotion gate packet and
application preview into a deterministic, file-scoped application dry-run. The
packet is intentionally metadata-only: it describes what a later reviewed patch
would touch, but it does not write fixtures, active artifacts, release state,
prompts, agent state, crawl output, DevHub artifacts, or official-action
artifacts.
"""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from typing import Any, Iterable, Mapping, Sequence


PACKET_TYPE = "ppd.inactive_fixture_promotion_application_dry_run.v1"
VALIDATION_COMMANDS = [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]]

MUTATION_FLAGS = (
    "active_fixture_promotion",
    "active_fixture_mutation",
    "active_source_mutation",
    "active_document_mutation",
    "active_requirement_mutation",
    "active_process_mutation",
    "active_guardrail_mutation",
    "active_prompt_mutation",
    "active_agent_state_mutation",
    "active_release_state_mutation",
    "public_source_artifact_mutation",
    "release_state_mutation",
    "devhub_artifact_mutation",
    "official_action_performed",
)

DISALLOWED_PATH_PREFIXES = (
    "src/lib/logic/",
    "public/corpus/portland-or/current/",
    "ipfs_datasets_py/.daemon/",
    "ppd/prompts/",
    "ppd/daemon/agent-state/",
    "ppd/daemon/release-state/",
    "ppd/devhub/artifacts/",
    "ppd/crawler/live-output/",
    "ppd/official-actions/",
)

PRIVATE_OR_RAW_KEY_TOKENS = (
    "auth",
    "browser",
    "cookie",
    "credential",
    "devhub_session",
    "download",
    "har",
    "local_private_path",
    "password",
    "payment_detail",
    "private_value",
    "raw_body",
    "raw_crawl",
    "raw_html",
    "raw_pdf",
    "screenshot",
    "session",
    "storage_state",
    "trace",
    "warc_payload",
)

LIVE_OR_PROMOTION_CLAIM_TOKENS = (
    "fixture_promoted",
    "live_crawl_completed",
    "live_execution_completed",
    "promoted_to_active",
    "promotion_complete",
    "promotion_completed",
    "release_state_updated",
)

PROHIBITED_TEXT_PHRASES = (
    "approval is guaranteed",
    "guaranteed approval",
    "guarantees approval",
    "permit will be approved",
    "permit outcome is guaranteed",
    "promotion complete",
    "promotion completed",
    "live execution completed",
    "submit permit",
    "certify acknowledgement",
    "schedule inspection",
    "pay fees",
    "final payment",
    "upload correction",
    "purchase permit",
    "cancel permit",
    "withdraw permit",
)

REQUIRED_PATCH_FIELDS = (
    "manifest_id",
    "file_path",
    "source_preview_row_id",
    "gate_row_id",
    "operation",
    "patch_kind",
    "status",
    "source_evidence_ids",
    "deterministic_content_ref",
)

EVIDENCE_PREFIXES = (
    "source:",
    "observation:",
    "citation:",
    "official-source:",
    "fixture-source:",
    "fixture-preview:",
    "regression-rehearsal:",
    "observed:",
)


class InactiveFixturePromotionApplicationDryRunV1Error(ValueError):
    """Raised when an application dry-run packet is incomplete or unsafe."""

    def __init__(self, errors: Iterable[str]) -> None:
        self.errors = tuple(errors)
        super().__init__("invalid inactive fixture promotion application dry-run v1: " + "; ".join(self.errors))


def build_inactive_fixture_promotion_application_dry_run_v1(
    *,
    inactive_fixture_promotion_gate_packet_v1: Mapping[str, Any],
    inactive_fixture_promotion_application_preview_v1: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a metadata-only dry-run application packet from offline inputs."""

    input_errors: list[str] = []
    _validate_no_private_raw_live_or_unsafe_payload(
        inactive_fixture_promotion_gate_packet_v1,
        input_errors,
        root="inactive_fixture_promotion_gate_packet_v1",
    )
    _validate_no_private_raw_live_or_unsafe_payload(
        inactive_fixture_promotion_application_preview_v1,
        input_errors,
        root="inactive_fixture_promotion_application_preview_v1",
    )
    if input_errors:
        raise InactiveFixturePromotionApplicationDryRunV1Error(input_errors)

    gate_packet = deepcopy(dict(inactive_fixture_promotion_gate_packet_v1))
    application_preview = deepcopy(dict(inactive_fixture_promotion_application_preview_v1))
    patch_manifest = _patch_manifest(application_preview, gate_packet)
    checklist = _ordered_application_checklist(patch_manifest, gate_packet)

    packet: dict[str, Any] = {
        "packet_type": PACKET_TYPE,
        "packet_version": "v1",
        "mode": "offline_inactive_fixture_application_dry_run_only",
        "fixture_first": True,
        "metadata_only": True,
        "dry_run_only": True,
        "consumed_input_packet_refs": {
            "inactive_fixture_promotion_gate_packet_v1": _packet_ref(
                gate_packet,
                "ppd.inactive_fixture_promotion_gate_packet.v1",
            ),
            "inactive_fixture_promotion_application_preview_v1": _packet_ref(
                application_preview,
                "ppd.inactive_fixture_promotion_application_preview.v1",
            ),
        },
        "attestations": {
            "no_active_fixtures_written": True,
            "no_public_source_artifacts_written": True,
            "no_release_state_written": True,
            "no_prompt_or_agent_state_written": True,
            "no_live_crawl_output_written": True,
            "no_devhub_artifacts_written": True,
            "no_official_action_artifacts_written": True,
        },
        "file_scoped_patch_manifest": patch_manifest,
        "ordered_application_checklist": checklist,
        "unchanged_file_inventory": _unchanged_file_inventory(patch_manifest),
        "expected_validation_commands": VALIDATION_COMMANDS,
        "rollback_notes": _rollback_notes(patch_manifest),
    }
    for flag in MUTATION_FLAGS:
        packet[flag] = False

    errors = validate_inactive_fixture_promotion_application_dry_run_v1(packet)
    if errors:
        raise InactiveFixturePromotionApplicationDryRunV1Error(errors)
    return packet


def validate_inactive_fixture_promotion_application_dry_run_v1(packet: Mapping[str, Any]) -> list[str]:
    """Return deterministic validation errors for an application dry-run packet."""

    errors: list[str] = []
    if packet.get("packet_type") != PACKET_TYPE:
        errors.append("packet_type must be ppd.inactive_fixture_promotion_application_dry_run.v1")
    if packet.get("fixture_first") is not True:
        errors.append("fixture_first must be true")
    if packet.get("metadata_only") is not True:
        errors.append("metadata_only must be true")
    if packet.get("dry_run_only") is not True:
        errors.append("dry_run_only must be true")
    if packet.get("expected_validation_commands") != VALIDATION_COMMANDS:
        errors.append("expected_validation_commands must contain the PP&D daemon self-test command")
    for flag in MUTATION_FLAGS:
        if packet.get(flag) is not False:
            errors.append(f"{flag} must be false")
    _validate_attestations(packet.get("attestations"), errors)
    _validate_patch_manifest(packet.get("file_scoped_patch_manifest"), errors)
    _validate_checklist(packet.get("ordered_application_checklist"), errors)
    _validate_unchanged_inventory(packet.get("unchanged_file_inventory"), errors)
    _validate_rollback_notes(packet.get("rollback_notes"), errors)
    _validate_no_private_raw_live_or_unsafe_payload(packet, errors, root="packet")
    return errors


def _patch_manifest(application_preview: Mapping[str, Any], gate_packet: Mapping[str, Any]) -> list[dict[str, Any]]:
    gate_go_rows = [
        row
        for row in _sequence(gate_packet.get("go_no_go_rows"))
        if isinstance(row, Mapping) and _text(row.get("decision")) == "go"
    ]
    gate_row_id = _text(gate_go_rows[0].get("row_id"), "application-preview-coverage") if gate_go_rows else "application-preview-coverage"
    gate_evidence = _evidence_ids(gate_packet)
    rows = [row for row in _sequence(application_preview.get("preview_rows")) if isinstance(row, Mapping)]
    rows.sort(key=lambda row: _text(row.get("row_id"), _text(row.get("candidate_fixture"), "row")))

    manifest: list[dict[str, Any]] = []
    for index, row in enumerate(rows, start=1):
        row_id = _text(row.get("row_id"), f"preview-row-{index}")
        candidate_fixture = _text(row.get("candidate_fixture"), row_id)
        file_path = f"ppd/tests/fixtures/inactive_fixture_promotion_application_dry_run_v1/{_slug(candidate_fixture)}.json"
        evidence = _dedupe([*_evidence_ids(row), *gate_evidence])
        if not evidence:
            evidence = [f"observation:{row_id}:dry-run-missing-evidence"]
        content_ref_payload = "|".join([file_path, row_id, candidate_fixture, *evidence])
        manifest.append(
            {
                "manifest_id": f"dry-run-file-{index:03d}",
                "file_path": file_path,
                "source_preview_row_id": row_id,
                "gate_row_id": gate_row_id,
                "operation": "inactive_fixture_candidate_complete_replacement",
                "patch_kind": "complete_file_replacement",
                "status": "not_applied",
                "source_evidence_ids": evidence,
                "deterministic_content_ref": sha256(content_ref_payload.encode("utf-8")).hexdigest(),
            }
        )
    return manifest


def _ordered_application_checklist(
    patch_manifest: Sequence[Mapping[str, Any]], gate_packet: Mapping[str, Any]
) -> list[dict[str, Any]]:
    gate_rows = [row for row in _sequence(gate_packet.get("go_no_go_rows")) if isinstance(row, Mapping)]
    gate_decisions = [_text(row.get("decision"), "no_go") for row in gate_rows]
    has_no_go = any(decision != "go" for decision in gate_decisions)
    checklist: list[dict[str, Any]] = [
        {
            "order": 1,
            "check_id": "confirm-gate-packet-reviewed",
            "status": "blocked_pending_manual_review" if has_no_go else "ready_for_manual_review",
            "description": "Confirm the gate packet rows have separate reviewer disposition before any later fixture change.",
            "source_refs": ["inactive_fixture_promotion_gate_packet_v1"],
        },
        {
            "order": 2,
            "check_id": "confirm-application-preview-rows",
            "status": "ready_for_manual_review" if patch_manifest else "blocked_missing_preview_rows",
            "description": "Confirm each application preview row has an evidence-backed file-scoped dry-run entry.",
            "source_refs": ["inactive_fixture_promotion_application_preview_v1"],
        },
    ]
    for index, item in enumerate(patch_manifest, start=3):
        checklist.append(
            {
                "order": index,
                "check_id": f"review-{_text(item.get('manifest_id'), 'dry-run-file')}",
                "status": "not_started",
                "description": "Review this file-scoped candidate without applying it to active fixtures.",
                "source_refs": [_text(item.get("manifest_id"), "dry-run-file")],
            }
        )
    checklist.append(
        {
            "order": len(checklist) + 1,
            "check_id": "run-expected-validation",
            "status": "not_started",
            "description": "Replay the expected validation command after a separate future reviewed proposal.",
            "source_refs": ["expected_validation_commands"],
        }
    )
    return checklist


def _unchanged_file_inventory(patch_manifest: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    inventory: list[dict[str, Any]] = []
    for item in patch_manifest:
        inventory.append(
            {
                "file_path": _text(item.get("file_path"), ""),
                "unchanged_in_this_dry_run": True,
                "reason": "dry-run manifest only; no complete file replacement has been applied",
            }
        )
    for path in (
        "public/corpus/portland-or/current/",
        "src/lib/logic/",
        "ppd/daemon/release-state/",
        "ppd/daemon/agent-state/",
        "ppd/devhub/artifacts/",
        "ppd/crawler/live-output/",
        "ppd/official-actions/",
    ):
        inventory.append(
            {
                "file_path": path,
                "unchanged_in_this_dry_run": True,
                "reason": "protected path remains outside the inactive fixture dry-run scope",
            }
        )
    return inventory


def _rollback_notes(patch_manifest: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "rollback_id": "rollback-dry-run-metadata-only",
            "status": "ready_no_active_changes",
            "note": "Discarding this packet restores the prior state because the dry-run applies no file replacements.",
            "affected_manifest_ids": [_text(item.get("manifest_id"), "dry-run-file") for item in patch_manifest],
        },
        {
            "rollback_id": "rollback-future-reviewed-application",
            "status": "requires_separate_future_patch_review",
            "note": "A later reviewed proposal must include its own inverse file list before fixture changes are applied.",
            "affected_manifest_ids": [_text(item.get("manifest_id"), "dry-run-file") for item in patch_manifest],
        },
    ]


def _validate_attestations(attestations: Any, errors: list[str]) -> None:
    if not isinstance(attestations, Mapping):
        errors.append("attestations must be an object")
        return
    for key in (
        "no_active_fixtures_written",
        "no_public_source_artifacts_written",
        "no_release_state_written",
        "no_prompt_or_agent_state_written",
        "no_live_crawl_output_written",
        "no_devhub_artifacts_written",
        "no_official_action_artifacts_written",
    ):
        if attestations.get(key) is not True:
            errors.append(f"attestations.{key} must be true")


def _validate_patch_manifest(manifest: Any, errors: list[str]) -> None:
    if not isinstance(manifest, Sequence) or isinstance(manifest, (str, bytes)) or not manifest:
        errors.append("file_scoped_patch_manifest must be a non-empty list")
        return
    seen_paths: set[str] = set()
    for index, item in enumerate(manifest):
        if not isinstance(item, Mapping):
            errors.append(f"file_scoped_patch_manifest[{index}] must be an object")
            continue
        for field in REQUIRED_PATCH_FIELDS:
            if field not in item:
                errors.append(f"file_scoped_patch_manifest[{index}].{field} is required")
        file_path = _text(item.get("file_path"))
        if not file_path.startswith("ppd/tests/fixtures/inactive_fixture_promotion_application_dry_run_v1/"):
            errors.append(f"file_scoped_patch_manifest[{index}].file_path must target inactive PP&D test fixtures")
        if any(file_path.startswith(prefix) for prefix in DISALLOWED_PATH_PREFIXES):
            errors.append(f"file_scoped_patch_manifest[{index}].file_path targets a protected path")
        if file_path in seen_paths:
            errors.append(f"file_scoped_patch_manifest[{index}].file_path must be unique")
        seen_paths.add(file_path)
        if item.get("operation") != "inactive_fixture_candidate_complete_replacement":
            errors.append(f"file_scoped_patch_manifest[{index}].operation must be inactive_fixture_candidate_complete_replacement")
        if item.get("patch_kind") != "complete_file_replacement":
            errors.append(f"file_scoped_patch_manifest[{index}].patch_kind must be complete_file_replacement")
        if item.get("status") != "not_applied":
            errors.append(f"file_scoped_patch_manifest[{index}].status must be not_applied")
        evidence_ids = _string_items(item.get("source_evidence_ids"))
        if not evidence_ids or any(not _is_cited_evidence(evidence_id) for evidence_id in evidence_ids):
            errors.append(f"file_scoped_patch_manifest[{index}].source_evidence_ids must cite source or observation evidence")


def _validate_checklist(checklist: Any, errors: list[str]) -> None:
    if not isinstance(checklist, Sequence) or isinstance(checklist, (str, bytes)) or not checklist:
        errors.append("ordered_application_checklist must be a non-empty list")
        return
    expected_order = 1
    for index, item in enumerate(checklist):
        if not isinstance(item, Mapping):
            errors.append(f"ordered_application_checklist[{index}] must be an object")
            continue
        if item.get("order") != expected_order:
            errors.append(f"ordered_application_checklist[{index}].order must be {expected_order}")
        expected_order += 1
        if not _text(item.get("check_id")):
            errors.append(f"ordered_application_checklist[{index}].check_id is required")
        if not _text(item.get("status")):
            errors.append(f"ordered_application_checklist[{index}].status is required")
        if not _string_items(item.get("source_refs")):
            errors.append(f"ordered_application_checklist[{index}].source_refs must be non-empty")


def _validate_unchanged_inventory(inventory: Any, errors: list[str]) -> None:
    if not isinstance(inventory, Sequence) or isinstance(inventory, (str, bytes)) or not inventory:
        errors.append("unchanged_file_inventory must be a non-empty list")
        return
    for index, item in enumerate(inventory):
        if not isinstance(item, Mapping):
            errors.append(f"unchanged_file_inventory[{index}] must be an object")
            continue
        if not _text(item.get("file_path")):
            errors.append(f"unchanged_file_inventory[{index}].file_path is required")
        if item.get("unchanged_in_this_dry_run") is not True:
            errors.append(f"unchanged_file_inventory[{index}].unchanged_in_this_dry_run must be true")
        if not _text(item.get("reason")):
            errors.append(f"unchanged_file_inventory[{index}].reason is required")


def _validate_rollback_notes(notes: Any, errors: list[str]) -> None:
    if not isinstance(notes, Sequence) or isinstance(notes, (str, bytes)) or not notes:
        errors.append("rollback_notes must be a non-empty list")
        return
    for index, item in enumerate(notes):
        if not isinstance(item, Mapping):
            errors.append(f"rollback_notes[{index}] must be an object")
            continue
        if not _text(item.get("rollback_id")):
            errors.append(f"rollback_notes[{index}].rollback_id is required")
        if not _text(item.get("status")):
            errors.append(f"rollback_notes[{index}].status is required")
        if not _text(item.get("note")):
            errors.append(f"rollback_notes[{index}].note is required")


def _validate_no_private_raw_live_or_unsafe_payload(value: Mapping[str, Any], errors: list[str], *, root: str) -> None:
    for path, key, child_value in _walk(value, path=root):
        key_name = key.lower()
        if any(token in key_name for token in PRIVATE_OR_RAW_KEY_TOKENS) and _truthy(child_value):
            errors.append(f"{path} must not include private, authenticated, session, browser, raw, PDF, crawl, or downloaded artifacts")
        if any(token in key_name for token in LIVE_OR_PROMOTION_CLAIM_TOKENS) and _truthy(child_value):
            errors.append(f"{path} must not claim live execution, promotion completion, or release-state update")
        if isinstance(child_value, str):
            lowered = child_value.lower()
            if any(phrase in lowered for phrase in PROHIBITED_TEXT_PHRASES):
                errors.append(f"{path} must not include live execution, promotion-complete, outcome guarantee, or consequential action language")


def _walk(value: Any, path: str = "packet", key: str = "") -> Iterable[tuple[str, str, Any]]:
    if isinstance(value, Mapping):
        for child_key, child_value in value.items():
            child_key_text = str(child_key)
            child_path = f"{path}.{child_key_text}"
            yield child_path, child_key_text, child_value
            yield from _walk(child_value, child_path, child_key_text)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child_value in enumerate(value):
            child_path = f"{path}[{index}]"
            yield child_path, key, child_value
            yield from _walk(child_value, child_path, key)


def _evidence_ids(packet: Mapping[str, Any]) -> list[str]:
    found: list[str] = []
    for key in ("source_evidence_ids", "evidence_ids", "citations", "offline_citations", "observation_evidence_ids"):
        found.extend(_string_items(packet.get(key)))
    for row_key in ("rows", "preview_rows", "regression_rows", "go_no_go_rows", "checks"):
        for row in _sequence(packet.get(row_key)):
            if isinstance(row, Mapping):
                found.extend(_evidence_ids(row))
    return _dedupe(found)


def _packet_ref(packet: Mapping[str, Any], fallback: str) -> str:
    for key in ("packet_type", "preview_version", "schema_version", "packet_version"):
        value = packet.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return fallback


def _sequence(value: Any) -> Sequence[Any]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return value
    return ()


def _string_items(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


def _dedupe(values: Sequence[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def _is_cited_evidence(value: str) -> bool:
    text = value.strip().lower()
    return bool(text) and not text.endswith(":missing-evidence") and text.startswith(EVIDENCE_PREFIXES)


def _truthy(value: Any) -> bool:
    if value is None or value is False or value == "":
        return False
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)) and not value:
        return False
    if isinstance(value, Mapping) and not value:
        return False
    return True


def _text(value: Any, fallback: str = "") -> str:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return fallback


def _slug(value: str) -> str:
    lowered = value.strip().lower()
    result: list[str] = []
    previous_dash = False
    for character in lowered:
        if character.isalnum():
            result.append(character)
            previous_dash = False
        elif not previous_dash:
            result.append("-")
            previous_dash = True
    slug = "".join(result).strip("-")
    return slug or "candidate-fixture"
