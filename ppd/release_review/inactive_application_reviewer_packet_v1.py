"""Fixture-first inactive release application reviewer packet v1.

This module consumes an inactive release application dry-run plan v1 and emits
reviewer-facing comparison rows. It is intentionally metadata-only: it does not
apply fixture changes, mutate prompts or release state, crawl live sources,
access DevHub, or perform official PP&D actions.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path, PurePosixPath
import re
from typing import Any, Mapping, Sequence

from ppd.release_review.inactive_application_dry_run_plan_v1 import (
    assert_valid_inactive_release_application_dry_run_plan_v1,
)


INACTIVE_RELEASE_APPLICATION_REVIEWER_PACKET_V1_PACKET_TYPE = "ppd.release_review.inactive_application_reviewer_packet.v1"

_REQUIRED_SECTIONS = (
    "reviewer_comparison_rows",
    "prerequisite_gate_acknowledgements",
    "fixture_family_risk_notes",
    "rollback_checkpoint_confirmations",
    "unresolved_hold_carry_forward_fields",
    "exact_offline_validation_commands",
)

_MUTATION_FLAGS = (
    "active_fixture_mutation_enabled",
    "active_prompt_mutation_enabled",
    "active_release_state_mutation_enabled",
    "live_source_crawl_enabled",
    "devhub_access_enabled",
    "official_action_enabled",
)

_FORBIDDEN_COMMAND_PARTS = (
    "curl",
    "wget",
    "playwright",
    "devhub",
    "submit",
    "payment",
    "schedule",
    "upload",
    "crawl-live",
    "--live",
)

_PRIVATE_OR_LIVE_PATTERNS = (
    re.compile(r"(^|/)(\.auth|auth-state|authenticated|storage-state|session|sessions|cookies|browser-state|playwright-report)(/|$)", re.IGNORECASE),
    re.compile(r"(^|/)(screenshots?|traces?|har|raw|crawl|crawls|downloads?|downloaded)(/|$)", re.IGNORECASE),
    re.compile(r"\.(auth|cookies?|har|trace|zip|png|jpe?g|webp|mp4|webm|warc|pdf|html?|mhtml|bin|dat)$", re.IGNORECASE),
)

_FORBIDDEN_TEXT_PATTERNS = (
    re.compile(r"\b(live crawl|live execution|applied to active|release[- ]complete|release state updated)\b", re.IGNORECASE),
    re.compile(r"\b(submit(?: the)? permit|certify acknowledgement|upload corrections?|schedule inspection|cancel permit|withdraw permit|pay fee|pay fees|final payment|purchase permit|create account)\b", re.IGNORECASE),
)


@dataclass(frozen=True)
class InactiveReleaseApplicationReviewerPacketFinding:
    """A deterministic reviewer packet validation failure."""

    code: str
    message: str
    location: str


def build_inactive_release_application_reviewer_packet_v1_from_file(path: Path) -> dict[str, Any]:
    """Load a dry-run plan fixture and build the reviewer packet."""

    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object at {path}")
    return build_inactive_release_application_reviewer_packet_v1(value)


def build_inactive_release_application_reviewer_packet_v1(dry_run_plan_v1: Mapping[str, Any]) -> dict[str, Any]:
    """Build a metadata-only reviewer packet from a valid dry-run plan v1."""

    assert_valid_inactive_release_application_dry_run_plan_v1(dry_run_plan_v1)
    inventory = [row for row in _sequence(dry_run_plan_v1.get("fixture_family_change_inventory")) if isinstance(row, Mapping)]
    validation_commands = [list(command) for command in _sequence(dry_run_plan_v1.get("validation_commands"))]

    comparison_rows = sorted(
        [_comparison_row(row, index) for index, row in enumerate(inventory, start=1)],
        key=lambda row: (row["family_id"], row["row_id"]),
    )
    packet: dict[str, Any] = {
        "packet_type": INACTIVE_RELEASE_APPLICATION_REVIEWER_PACKET_V1_PACKET_TYPE,
        "packet_version": "v1",
        "fixture_first": True,
        "metadata_only": True,
        "dry_run_plan_consumed": True,
        "source_dry_run_plan_type": str(dry_run_plan_v1.get("packet_type", "")),
        "source_dry_run_plan_version": str(dry_run_plan_v1.get("packet_version", "")),
        "reviewer_comparison_rows": comparison_rows,
        "prerequisite_gate_acknowledgements": _gate_acknowledgements(dry_run_plan_v1),
        "fixture_family_risk_notes": _risk_notes(comparison_rows),
        "rollback_checkpoint_confirmations": _rollback_confirmations(dry_run_plan_v1, validation_commands),
        "unresolved_hold_carry_forward_fields": _carry_forward_fields(dry_run_plan_v1),
        "exact_offline_validation_commands": validation_commands,
    }
    for flag in _MUTATION_FLAGS:
        packet[flag] = False
    assert_valid_inactive_release_application_reviewer_packet_v1(packet)
    return packet


def validate_inactive_release_application_reviewer_packet_v1(packet: Mapping[str, Any]) -> list[InactiveReleaseApplicationReviewerPacketFinding]:
    findings: list[InactiveReleaseApplicationReviewerPacketFinding] = []

    if packet.get("packet_type") != INACTIVE_RELEASE_APPLICATION_REVIEWER_PACKET_V1_PACKET_TYPE:
        findings.append(_finding("invalid-packet-type", "Packet type must identify inactive release application reviewer packet v1.", "packet_type"))
    for field in ("fixture_first", "metadata_only", "dry_run_plan_consumed"):
        if packet.get(field) is not True:
            findings.append(_finding("missing-fixture-first-attestation", "Reviewer packet must be fixture-first, metadata-only, and dry-run-plan consumed.", field))
    for flag in _MUTATION_FLAGS:
        if packet.get(flag) is not False:
            findings.append(_finding("mutation-live-devhub-or-official-flag-enabled", "Reviewer packet must not enable active fixture, prompt, release-state, live, DevHub, or official action behavior.", flag))
    for section in _REQUIRED_SECTIONS:
        if not _sequence(packet.get(section)):
            findings.append(_finding("missing-required-reviewer-section", "Reviewer packet section must be a non-empty list.", section))

    _validate_comparison_rows(packet.get("reviewer_comparison_rows"), findings)
    _validate_gate_acknowledgements(packet.get("prerequisite_gate_acknowledgements"), findings)
    _validate_risk_notes(packet.get("fixture_family_risk_notes"), findings)
    _validate_rollback_confirmations(packet.get("rollback_checkpoint_confirmations"), findings)
    _validate_carry_forward_fields(packet.get("unresolved_hold_carry_forward_fields"), findings)
    _validate_validation_commands(packet.get("exact_offline_validation_commands"), findings)
    _scan_for_forbidden_content(packet, findings)

    return findings


def assert_valid_inactive_release_application_reviewer_packet_v1(packet: Mapping[str, Any]) -> None:
    findings = validate_inactive_release_application_reviewer_packet_v1(packet)
    if findings:
        summary = "; ".join(f"{finding.code} at {finding.location}" for finding in findings)
        raise ValueError(f"inactive release application reviewer packet v1 validation failed: {summary}")


def _comparison_row(row: Mapping[str, Any], index: int) -> dict[str, Any]:
    family_id = str(row.get("family_id") or f"fixture-family-{index}")
    candidate_refs = sorted(str(ref) for ref in _sequence(row.get("candidate_refs")) if str(ref))
    status = "blocked_for_reviewer" if row.get("active_fixture_change") is not False else "ready_for_reviewer_comparison"
    return {
        "row_id": f"reviewer-comparison:{_slug(family_id)}",
        "family_id": family_id,
        "deterministic_sort_key": f"{_slug(family_id)}:{index:04d}",
        "candidate_refs": candidate_refs,
        "reviewer_decision": "pending",
        "comparison_status": status,
        "fixture_scope": "inactive_fixture_family_only",
        "before": {
            "source_plan_change": str(row.get("planned_change") or ""),
            "active_fixture_change": row.get("active_fixture_change"),
            "candidate_refs": candidate_refs,
        },
        "after": {
            "source_plan_change": "none",
            "active_fixture_change": False,
            "would_apply_fixture_change": False,
            "would_mutate_release_state": False,
            "candidate_refs": candidate_refs,
        },
        "unresolved_hold_carry_forward_field": f"hold:{_slug(family_id)}:reviewer-disposition",
    }


def _gate_acknowledgements(plan: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for gate in _sequence(plan.get("preflight_validation_gates")):
        if not isinstance(gate, Mapping):
            continue
        gate_id = str(gate.get("gate_id") or "")
        rows.append(
            {
                "gate_id": gate_id,
                "source_status": str(gate.get("status") or ""),
                "required": gate.get("required") is True,
                "acknowledgement_status": "pending_reviewer_acknowledgement",
                "acknowledged": False,
                "evidence_ref": str(gate.get("evidence_ref") or ""),
            }
        )
    return sorted(rows, key=lambda row: row["gate_id"])


def _risk_notes(comparison_rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "risk_note_id": f"risk-note:{_slug(str(row.get('family_id') or 'unknown'))}",
            "family_id": str(row.get("family_id") or ""),
            "risk_level": "review_required",
            "note": "Inactive fixture family remains unchanged until a separate reviewed proposal is approved.",
            "carry_forward_fields": [str(row.get("unresolved_hold_carry_forward_field") or "")],
        }
        for row in comparison_rows
    ]


def _rollback_confirmations(plan: Mapping[str, Any], validation_commands: Sequence[Sequence[str]]) -> list[dict[str, Any]]:
    rows = []
    for checkpoint in _sequence(plan.get("rollback_checkpoints")):
        if not isinstance(checkpoint, Mapping):
            continue
        checkpoint_id = str(checkpoint.get("checkpoint_id") or "")
        commands = [list(command) for command in _sequence(checkpoint.get("verification_commands"))] or [list(command) for command in validation_commands]
        rows.append(
            {
                "checkpoint_id": checkpoint_id,
                "source_status": str(checkpoint.get("status") or ""),
                "confirmation_status": "pending_reviewer_confirmation",
                "confirmed": False,
                "changes_to_restore": False,
                "verification_commands": commands,
            }
        )
    return sorted(rows, key=lambda row: row["checkpoint_id"])


def _carry_forward_fields(plan: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for placeholder in _sequence(plan.get("reviewer_approval_placeholders")):
        if not isinstance(placeholder, Mapping):
            continue
        approval_id = str(placeholder.get("approval_id") or "")
        rows.append(
            {
                "hold_field_id": f"hold:{_slug(approval_id)}",
                "source_approval_id": approval_id,
                "carry_forward_status": "unresolved_pending_reviewer_disposition",
                "required_before": str(placeholder.get("required_before") or ""),
                "owner_role": str(placeholder.get("role") or ""),
            }
        )
    return sorted(rows, key=lambda row: row["hold_field_id"])


def _validate_comparison_rows(value: Any, findings: list[InactiveReleaseApplicationReviewerPacketFinding]) -> None:
    rows = _sequence(value)
    sort_keys = [(str(row.get("family_id") or ""), str(row.get("row_id") or "")) for row in rows if isinstance(row, Mapping)]
    if sort_keys != sorted(sort_keys):
        findings.append(_finding("comparison-rows-not-deterministic", "Reviewer comparison rows must be sorted by family_id and row_id.", "reviewer_comparison_rows"))
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            findings.append(_finding("invalid-comparison-row", "Reviewer comparison rows must be objects.", f"reviewer_comparison_rows[{index}]"))
            continue
        for field in ("row_id", "family_id", "deterministic_sort_key", "candidate_refs", "before", "after", "unresolved_hold_carry_forward_field"):
            if field in ("candidate_refs",):
                if not _sequence(row.get(field)):
                    findings.append(_finding("missing-comparison-row-field", "Reviewer comparison row candidate refs are required.", f"reviewer_comparison_rows[{index}].{field}"))
            elif field in ("before", "after"):
                if not isinstance(row.get(field), Mapping):
                    findings.append(_finding("missing-comparison-row-field", "Reviewer comparison row before/after objects are required.", f"reviewer_comparison_rows[{index}].{field}"))
            elif not _non_empty_text(row.get(field)):
                findings.append(_finding("missing-comparison-row-field", "Reviewer comparison row field is required.", f"reviewer_comparison_rows[{index}].{field}"))
        after = row.get("after") if isinstance(row.get("after"), Mapping) else {}
        if after.get("would_apply_fixture_change") is not False or after.get("would_mutate_release_state") is not False:
            findings.append(_finding("comparison-row-would-apply-change", "Reviewer comparison rows must not apply fixture or release-state changes.", f"reviewer_comparison_rows[{index}].after"))


def _validate_gate_acknowledgements(value: Any, findings: list[InactiveReleaseApplicationReviewerPacketFinding]) -> None:
    for index, row in enumerate(_sequence(value)):
        if not isinstance(row, Mapping):
            findings.append(_finding("invalid-gate-acknowledgement", "Gate acknowledgements must be objects.", f"prerequisite_gate_acknowledgements[{index}]"))
            continue
        if row.get("required") is not True or row.get("acknowledged") is not False:
            findings.append(_finding("invalid-gate-acknowledgement-state", "Gate acknowledgements must be required and pending acknowledgement.", f"prerequisite_gate_acknowledgements[{index}]"))
        for field in ("gate_id", "source_status", "acknowledgement_status", "evidence_ref"):
            if not _non_empty_text(row.get(field)):
                findings.append(_finding("missing-gate-acknowledgement-field", "Gate acknowledgement field is required.", f"prerequisite_gate_acknowledgements[{index}].{field}"))


def _validate_risk_notes(value: Any, findings: list[InactiveReleaseApplicationReviewerPacketFinding]) -> None:
    for index, row in enumerate(_sequence(value)):
        if not isinstance(row, Mapping):
            findings.append(_finding("invalid-risk-note", "Fixture-family risk notes must be objects.", f"fixture_family_risk_notes[{index}]"))
            continue
        for field in ("risk_note_id", "family_id", "risk_level", "note", "carry_forward_fields"):
            if field == "carry_forward_fields":
                if not _sequence(row.get(field)):
                    findings.append(_finding("missing-risk-note-field", "Risk notes require carry-forward fields.", f"fixture_family_risk_notes[{index}].{field}"))
            elif not _non_empty_text(row.get(field)):
                findings.append(_finding("missing-risk-note-field", "Risk note field is required.", f"fixture_family_risk_notes[{index}].{field}"))


def _validate_rollback_confirmations(value: Any, findings: list[InactiveReleaseApplicationReviewerPacketFinding]) -> None:
    for index, row in enumerate(_sequence(value)):
        if not isinstance(row, Mapping):
            findings.append(_finding("invalid-rollback-confirmation", "Rollback confirmations must be objects.", f"rollback_checkpoint_confirmations[{index}]"))
            continue
        if row.get("confirmed") is not False or row.get("changes_to_restore") is not False:
            findings.append(_finding("invalid-rollback-confirmation-state", "Rollback confirmations must remain pending with no changes to restore.", f"rollback_checkpoint_confirmations[{index}]"))
        for field in ("checkpoint_id", "source_status", "confirmation_status", "verification_commands"):
            if field == "verification_commands":
                if not _sequence(row.get(field)):
                    findings.append(_finding("missing-rollback-confirmation-field", "Rollback confirmations require verification commands.", f"rollback_checkpoint_confirmations[{index}].{field}"))
            elif not _non_empty_text(row.get(field)):
                findings.append(_finding("missing-rollback-confirmation-field", "Rollback confirmation field is required.", f"rollback_checkpoint_confirmations[{index}].{field}"))


def _validate_carry_forward_fields(value: Any, findings: list[InactiveReleaseApplicationReviewerPacketFinding]) -> None:
    for index, row in enumerate(_sequence(value)):
        if not isinstance(row, Mapping):
            findings.append(_finding("invalid-carry-forward-field", "Carry-forward fields must be objects.", f"unresolved_hold_carry_forward_fields[{index}]"))
            continue
        for field in ("hold_field_id", "source_approval_id", "carry_forward_status", "required_before", "owner_role"):
            if not _non_empty_text(row.get(field)):
                findings.append(_finding("missing-carry-forward-field", "Carry-forward field data is required.", f"unresolved_hold_carry_forward_fields[{index}].{field}"))


def _validate_validation_commands(value: Any, findings: list[InactiveReleaseApplicationReviewerPacketFinding]) -> None:
    commands = _sequence(value)
    if not commands:
        findings.append(_finding("missing-exact-offline-validation-command", "Exact offline validation commands are required.", "exact_offline_validation_commands"))
        return
    for index, command in enumerate(commands):
        if not isinstance(command, list) or not command or not all(isinstance(part, str) and part.strip() for part in command):
            findings.append(_finding("invalid-exact-offline-validation-command", "Offline validation command must be a non-empty argv string list.", f"exact_offline_validation_commands[{index}]"))
            continue
        normalized = " ".join(command).lower()
        if command[0] != "python3" or any(part in normalized for part in _FORBIDDEN_COMMAND_PARTS):
            findings.append(_finding("live-or-consequential-validation-command", "Offline validation commands must be deterministic python3 commands and must not invoke live, DevHub, crawl, upload, submit, payment, or scheduling behavior.", f"exact_offline_validation_commands[{index}]"))


def _scan_for_forbidden_content(value: Any, findings: list[InactiveReleaseApplicationReviewerPacketFinding], location: str = "packet") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            child_location = f"{location}.{key_text}"
            if _truthy(child) and any(token in key_text.lower().replace("-", "_") for token in ("auth", "browser", "cookie", "download", "har", "password", "private", "raw", "screenshot", "session", "trace")):
                findings.append(_finding("private-raw-or-live-artifact-reference", "Reviewer packet must not include private, raw, browser, session, screenshot, trace, HAR, or downloaded artifacts.", child_location))
            _scan_for_forbidden_content(child, findings, child_location)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            _scan_for_forbidden_content(child, findings, f"{location}[{index}]")
    elif isinstance(value, str):
        normalized_path = PurePosixPath(value.replace("\\", "/")).as_posix()
        if any(pattern.search(normalized_path) for pattern in _PRIVATE_OR_LIVE_PATTERNS):
            findings.append(_finding("private-raw-or-live-artifact-reference", "Reviewer packet must not reference private, raw, browser, session, crawl, PDF, HTML, or downloaded artifacts.", location))
        if any(pattern.search(value) for pattern in _FORBIDDEN_TEXT_PATTERNS):
            findings.append(_finding("forbidden-release-or-official-action-language", "Reviewer packet must not claim live execution, applied/release-complete status, or direct consequential official actions.", location))


def _sequence(value: Any) -> Sequence[Any]:
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return value
    return ()


def _truthy(value: Any) -> bool:
    if value is None or value is False or value == "":
        return False
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)) and not value:
        return False
    if isinstance(value, Mapping) and not value:
        return False
    return True


def _non_empty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "unknown"


def _finding(code: str, message: str, location: str) -> InactiveReleaseApplicationReviewerPacketFinding:
    return InactiveReleaseApplicationReviewerPacketFinding(code=code, message=message, location=location)
