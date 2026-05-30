"""Fixture-first inactive release application dry-run plan v1.

This module consumes a release reviewer go/no-go checklist v1 and emits a
metadata-only plan for a later human-reviewed inactive fixture application. It
never applies fixture changes, mutates prompts or release state, crawls live
sources, accesses DevHub, or performs official actions.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath
import re
from typing import Any, Mapping, Sequence

from ppd.release_review.checklist_v1 import validate_release_reviewer_go_no_go_checklist_v1


INACTIVE_RELEASE_APPLICATION_DRY_RUN_PLAN_V1_PACKET_TYPE = "ppd.release_review.inactive_application_dry_run_plan.v1"
SELF_TEST_COMMAND = ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]

_REQUIRED_SECTIONS = (
    "ordered_dry_run_application_steps",
    "fixture_family_change_inventory",
    "preflight_validation_gates",
    "rollback_checkpoints",
    "reviewer_approval_placeholders",
    "non_application_no_release_notes",
)

_REQUIRED_STEP_IDS = (
    "preflight-validate-reviewer-checklist",
    "inventory-fixture-families",
    "confirm-preflight-gates",
    "record-no-release-disposition",
)

_REQUIRED_GATE_IDS = (
    "gate-checklist-validation-clean",
    "gate-rollback-confirmations-present",
    "gate-validation-replay-commands-present",
    "gate-unresolved-risk-placeholders-present",
)

_REQUIRED_NOTE_IDS = (
    "no-active-fixture-application",
    "no-release-state-change",
    "no-live-or-devhub-work",
    "no-official-action",
)

_MUTATION_FLAGS = (
    "active_artifact_mutation_enabled",
    "active_fixture_mutation_enabled",
    "active_prompt_mutation_enabled",
    "active_release_state_mutation_enabled",
    "active_agent_state_mutation_enabled",
    "artifact_mutation_enabled",
    "fixture_mutation_enabled",
    "prompt_mutation_enabled",
    "release_state_mutation_enabled",
    "agent_state_mutation_enabled",
    "live_source_crawl_enabled",
    "devhub_access_enabled",
    "official_action_enabled",
)

_PRIVATE_OR_RAW_KEY_TOKENS = (
    "auth",
    "authenticated",
    "browser",
    "cookie",
    "credential",
    "download",
    "downloaded",
    "har",
    "password",
    "private",
    "raw_body",
    "raw_crawl",
    "raw_download",
    "raw_html",
    "raw_pdf",
    "screenshot",
    "session",
    "storage_state",
    "trace",
)

_PRIVATE_OR_RAW_PATTERNS = (
    re.compile(r"(^|/)(\.auth|auth-state|authenticated|storage-state|session|sessions|cookies|browser-state|playwright-report)(/|$)", re.IGNORECASE),
    re.compile(r"(^|/)(screenshots?|traces?|har|raw|crawl|crawls|downloads?|downloaded)(/|$)", re.IGNORECASE),
    re.compile(r"\.(auth|cookies?|har|trace|zip|png|jpe?g|webp|mp4|webm|warc|pdf|html?|mhtml|bin|dat)$", re.IGNORECASE),
)

_FORBIDDEN_TEXT_PATTERNS = (
    re.compile(r"\b(live crawl|live execution|executed live|applied to active|changes? (?:were |has been |have been )?applied|release[- ]complete|release complete|released successfully|release state updated)\b", re.IGNORECASE),
    re.compile(r"\b(guarantee[sd]?|guarantees|will be approved|permit will issue|legal outcome|permitting outcome|approval is certain|approval is assured)\b", re.IGNORECASE),
    re.compile(r"\b(submit(?: the)? permit|certify acknowledgement|upload corrections?|schedule inspection|cancel permit|withdraw permit|pay fee|pay fees|final payment|purchase permit|create account)\b", re.IGNORECASE),
)


@dataclass(frozen=True)
class InactiveReleaseApplicationDryRunPlanFinding:
    """A deterministic inactive application dry-run plan validation failure."""

    code: str
    message: str
    location: str


def build_inactive_release_application_dry_run_plan_v1(
    release_reviewer_go_no_go_checklist_v1: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a non-applying dry-run plan from a valid go/no-go checklist."""

    checklist_findings = validate_release_reviewer_go_no_go_checklist_v1(release_reviewer_go_no_go_checklist_v1)
    if checklist_findings:
        summary = "; ".join(f"{finding.code} at {finding.location}" for finding in checklist_findings)
        raise ValueError(f"release reviewer go/no-go checklist v1 is not valid: {summary}")

    validation_commands = [list(command) for command in _sequence(release_reviewer_go_no_go_checklist_v1.get("validation_commands"))]
    evidence_rows = [row for row in _sequence(release_reviewer_go_no_go_checklist_v1.get("evidence_citation_coverage")) if isinstance(row, Mapping)]
    inventory = _fixture_family_change_inventory(release_reviewer_go_no_go_checklist_v1, evidence_rows)

    plan: dict[str, Any] = {
        "packet_type": INACTIVE_RELEASE_APPLICATION_DRY_RUN_PLAN_V1_PACKET_TYPE,
        "packet_version": "v1",
        "fixture_first": True,
        "dry_run_only": True,
        "metadata_only": True,
        "consumed_input_ref": "release_reviewer_go_no_go_checklist_v1",
        "ordered_dry_run_application_steps": _ordered_steps(evidence_rows),
        "fixture_family_change_inventory": inventory,
        "preflight_validation_gates": _preflight_gates(release_reviewer_go_no_go_checklist_v1, validation_commands),
        "rollback_checkpoints": _rollback_checkpoints(inventory, validation_commands),
        "reviewer_approval_placeholders": _reviewer_approval_placeholders(evidence_rows),
        "non_application_no_release_notes": _non_application_notes(),
        "validation_commands": validation_commands,
    }
    for flag in _MUTATION_FLAGS:
        plan[flag] = False
    assert_valid_inactive_release_application_dry_run_plan_v1(plan)
    return plan


def validate_inactive_release_application_dry_run_plan_v1(plan: Mapping[str, Any]) -> list[InactiveReleaseApplicationDryRunPlanFinding]:
    findings: list[InactiveReleaseApplicationDryRunPlanFinding] = []

    if plan.get("packet_type") != INACTIVE_RELEASE_APPLICATION_DRY_RUN_PLAN_V1_PACKET_TYPE:
        findings.append(_finding("invalid-packet-type", "Packet type must identify inactive release application dry-run plan v1.", "packet_type"))
    for field in ("fixture_first", "dry_run_only", "metadata_only"):
        if plan.get(field) is not True:
            findings.append(_finding("missing-dry-run-attestation", "Fixture-first dry-run attestations must be true.", field))
    for field in _MUTATION_FLAGS:
        if plan.get(field) is not False:
            findings.append(_finding("mutation-or-live-flag-enabled", "Active artifact, prompt, release-state, fixture, agent-state, live, DevHub, and official action flags must be false.", field))
    for section in _REQUIRED_SECTIONS:
        if not _sequence(plan.get(section)):
            findings.append(_finding("missing-required-section", "Dry-run plan section must be a non-empty list.", section))

    _validate_ordered_steps(plan.get("ordered_dry_run_application_steps"), findings)
    _validate_inventory(plan.get("fixture_family_change_inventory"), findings)
    _validate_preflight_gates(plan.get("preflight_validation_gates"), findings)
    _validate_rollback_checkpoints(plan.get("rollback_checkpoints"), findings)
    _validate_reviewer_placeholders(plan.get("reviewer_approval_placeholders"), findings)
    _validate_notes(plan.get("non_application_no_release_notes"), findings)
    _validate_validation_commands(plan.get("validation_commands"), findings)
    _scan_for_forbidden_content(plan, findings)

    return findings


def assert_valid_inactive_release_application_dry_run_plan_v1(plan: Mapping[str, Any]) -> None:
    findings = validate_inactive_release_application_dry_run_plan_v1(plan)
    if findings:
        summary = "; ".join(f"{finding.code} at {finding.location}" for finding in findings)
        raise ValueError(f"inactive release application dry-run plan v1 validation failed: {summary}")


def _ordered_steps(evidence_rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    steps = [
        {
            "order": 1,
            "step_id": "preflight-validate-reviewer-checklist",
            "action": "Replay deterministic checklist validation from committed fixture inputs.",
            "status": "pending_manual_review",
            "source_refs": ["release_reviewer_go_no_go_checklist_v1"],
        },
        {
            "order": 2,
            "step_id": "inventory-fixture-families",
            "action": "Build fixture-family inventory for review without changing active fixtures.",
            "status": "pending_manual_review",
            "source_refs": ["evidence_citation_coverage"],
        },
        {
            "order": 3,
            "step_id": "confirm-preflight-gates",
            "action": "Confirm validation, rollback, and unresolved-risk gates before any later reviewed proposal.",
            "status": "pending_manual_review",
            "source_refs": ["validation_commands", "rollback_confirmations", "unresolved_risk_placeholders"],
        },
    ]
    for index, row in enumerate(evidence_rows, start=4):
        item_id = str(row.get("checklist_item_id") or f"checklist-item-{index}")
        steps.append(
            {
                "order": index,
                "step_id": f"review-{_slug(item_id)}",
                "action": "Review cited checklist evidence as dry-run material only.",
                "status": "pending_reviewer_approval",
                "source_refs": [str(row.get("citation") or item_id)],
            }
        )
    steps.append(
        {
            "order": len(steps) + 1,
            "step_id": "record-no-release-disposition",
            "action": "Record that this artifact is informational and leaves release state unchanged.",
            "status": "pending_manual_review",
            "source_refs": ["non_application_no_release_notes"],
        }
    )
    return steps


def _fixture_family_change_inventory(checklist: Mapping[str, Any], evidence_rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    families: dict[str, set[str]] = {}
    for row in evidence_rows:
        citation = str(row.get("citation") or "").strip()
        family = _fixture_family_from_path(citation)
        if family:
            families.setdefault(family, set()).add(citation)
    for artifact in _sequence(checklist.get("artifacts")):
        path = _artifact_path(artifact)
        family = _fixture_family_from_path(path)
        if family:
            families.setdefault(family, set()).add(path)
    if not families:
        return [
            {
                "family_id": "release-review-control-no-fixture-family-change",
                "planned_change": "none",
                "active_fixture_change": False,
                "candidate_refs": ["release_reviewer_go_no_go_checklist_v1"],
                "review_status": "pending_manual_review",
            }
        ]
    return [
        {
            "family_id": family,
            "planned_change": "none",
            "active_fixture_change": False,
            "candidate_refs": sorted(refs),
            "review_status": "pending_manual_review",
        }
        for family, refs in sorted(families.items())
    ]


def _preflight_gates(checklist: Mapping[str, Any], validation_commands: Sequence[Sequence[str]]) -> list[dict[str, Any]]:
    return [
        {
            "gate_id": "gate-checklist-validation-clean",
            "status": "ready_for_replay",
            "required": True,
            "evidence_ref": "validate_release_reviewer_go_no_go_checklist_v1",
        },
        {
            "gate_id": "gate-rollback-confirmations-present",
            "status": "confirmed_from_checklist" if all(checklist.get(field) is True for field in ("rollback_owner_confirmed", "rollback_steps_confirmed", "rollback_stop_condition_confirmed")) else "blocked",
            "required": True,
            "evidence_ref": "rollback_readiness_confirmations",
        },
        {
            "gate_id": "gate-validation-replay-commands-present",
            "status": "ready_for_replay" if validation_commands else "blocked",
            "required": True,
            "evidence_ref": "validation_commands",
        },
        {
            "gate_id": "gate-unresolved-risk-placeholders-present",
            "status": "confirmed_from_checklist" if all(checklist.get(field) is True for field in ("unresolved_risks_acknowledged", "unresolved_risk_owner_placeholder", "unresolved_risk_followup_placeholder")) else "blocked",
            "required": True,
            "evidence_ref": "unresolved_risk_placeholders",
        },
    ]


def _rollback_checkpoints(inventory: Sequence[Mapping[str, Any]], validation_commands: Sequence[Sequence[str]]) -> list[dict[str, Any]]:
    checkpoints = [
        {
            "checkpoint_id": "rollback-discard-dry-run-plan",
            "status": "ready_no_changes_applied",
            "checkpoint": "Discard this dry-run plan; no active fixture or release-state restore is needed.",
            "verification_commands": [list(command) for command in validation_commands] or [SELF_TEST_COMMAND],
        }
    ]
    for index, row in enumerate(inventory, start=1):
        checkpoints.append(
            {
                "checkpoint_id": f"rollback-fixture-family-{index}",
                "status": "ready_no_changes_applied",
                "checkpoint": f"Keep fixture family {row.get('family_id')} unchanged in this dry-run.",
                "verification_commands": [list(command) for command in validation_commands] or [SELF_TEST_COMMAND],
            }
        )
    return checkpoints


def _reviewer_approval_placeholders(evidence_rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    placeholders = [
        {
            "approval_id": "release-supervisor-dry-run-review",
            "role": "release supervisor",
            "disposition_placeholder": "pending_name_timestamp_and_go_no_go",
            "required_before": "any_separate_future_release_application",
            "source_refs": ["release_reviewer_go_no_go_checklist_v1"],
        }
    ]
    for index, row in enumerate(evidence_rows, start=1):
        placeholders.append(
            {
                "approval_id": f"checklist-evidence-approval-{index}",
                "role": "release reviewer",
                "disposition_placeholder": "pending_name_timestamp_and_go_no_go",
                "required_before": "any_separate_future_release_application",
                "source_refs": [str(row.get("citation") or row.get("checklist_item_id") or "checklist-evidence")],
            }
        )
    return placeholders


def _non_application_notes() -> list[dict[str, str]]:
    return [
        {
            "note_id": "no-active-fixture-application",
            "note": "This plan is metadata only and leaves active fixture files unchanged.",
        },
        {
            "note_id": "no-release-state-change",
            "note": "This plan does not update release state and is not a release decision.",
        },
        {
            "note_id": "no-live-or-devhub-work",
            "note": "This plan uses committed fixture evidence only and performs no live source or DevHub work.",
        },
        {
            "note_id": "no-official-action",
            "note": "This plan performs no official PP&D action and creates no private artifacts.",
        },
    ]


def _validate_ordered_steps(value: Any, findings: list[InactiveReleaseApplicationDryRunPlanFinding]) -> None:
    rows = _sequence(value)
    seen_step_ids: set[str] = set()
    expected = 1
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            findings.append(_finding("invalid-step", "Application steps must be objects.", f"ordered_dry_run_application_steps[{index}]"))
            continue
        step_id = str(row.get("step_id") or "")
        if step_id:
            seen_step_ids.add(step_id)
        if row.get("order") != expected:
            findings.append(_finding("invalid-step-order", "Application steps must be ordered consecutively from 1.", f"ordered_dry_run_application_steps[{index}].order"))
        expected += 1
        for field in ("step_id", "action", "status", "source_refs"):
            if field == "source_refs":
                if not _sequence(row.get(field)):
                    findings.append(_finding("missing-step-field", "Application step source references are required.", f"ordered_dry_run_application_steps[{index}].{field}"))
            elif not _non_empty_text(row.get(field)):
                findings.append(_finding("missing-step-field", "Application step field is required.", f"ordered_dry_run_application_steps[{index}].{field}"))
    for required_step_id in _REQUIRED_STEP_IDS:
        if required_step_id not in seen_step_ids:
            findings.append(_finding("missing-dry-run-application-step", "Required dry-run application step is missing.", f"ordered_dry_run_application_steps.{required_step_id}"))


def _validate_inventory(value: Any, findings: list[InactiveReleaseApplicationDryRunPlanFinding]) -> None:
    for index, row in enumerate(_sequence(value)):
        if not isinstance(row, Mapping):
            findings.append(_finding("invalid-inventory-row", "Fixture-family inventory rows must be objects.", f"fixture_family_change_inventory[{index}]"))
            continue
        if not _non_empty_text(row.get("family_id")):
            findings.append(_finding("missing-inventory-field", "Fixture-family inventory requires family_id.", f"fixture_family_change_inventory[{index}].family_id"))
        if row.get("planned_change") != "none":
            findings.append(_finding("fixture-change-not-dry-run", "Fixture-family inventory must declare no applied change.", f"fixture_family_change_inventory[{index}].planned_change"))
        if row.get("active_fixture_change") is not False:
            findings.append(_finding("active-fixture-change-enabled", "Active fixture changes must be false.", f"fixture_family_change_inventory[{index}].active_fixture_change"))
        if not _sequence(row.get("candidate_refs")):
            findings.append(_finding("missing-inventory-refs", "Fixture-family inventory requires candidate refs.", f"fixture_family_change_inventory[{index}].candidate_refs"))


def _validate_preflight_gates(value: Any, findings: list[InactiveReleaseApplicationDryRunPlanFinding]) -> None:
    seen_gate_ids: set[str] = set()
    for index, row in enumerate(_sequence(value)):
        if not isinstance(row, Mapping):
            findings.append(_finding("invalid-preflight-gate", "Preflight gates must be objects.", f"preflight_validation_gates[{index}]"))
            continue
        gate_id = str(row.get("gate_id") or "")
        if gate_id:
            seen_gate_ids.add(gate_id)
        if not _non_empty_text(row.get("gate_id")) or not _non_empty_text(row.get("status")):
            findings.append(_finding("missing-preflight-gate-field", "Preflight gate id and status are required.", f"preflight_validation_gates[{index}]"))
        if row.get("required") is not True:
            findings.append(_finding("preflight-gate-not-required", "Preflight gates must be required.", f"preflight_validation_gates[{index}].required"))
    for required_gate_id in _REQUIRED_GATE_IDS:
        if required_gate_id not in seen_gate_ids:
            findings.append(_finding("missing-preflight-validation-gate", "Required preflight validation gate is missing.", f"preflight_validation_gates.{required_gate_id}"))


def _validate_rollback_checkpoints(value: Any, findings: list[InactiveReleaseApplicationDryRunPlanFinding]) -> None:
    for index, row in enumerate(_sequence(value)):
        if not isinstance(row, Mapping):
            findings.append(_finding("invalid-rollback-checkpoint", "Rollback checkpoints must be objects.", f"rollback_checkpoints[{index}]"))
            continue
        for field in ("checkpoint_id", "status", "checkpoint", "verification_commands"):
            if field == "verification_commands":
                if not _sequence(row.get(field)):
                    findings.append(_finding("missing-rollback-field", "Rollback checkpoint verification commands are required.", f"rollback_checkpoints[{index}].{field}"))
            elif not _non_empty_text(row.get(field)):
                findings.append(_finding("missing-rollback-field", "Rollback checkpoint field is required.", f"rollback_checkpoints[{index}].{field}"))


def _validate_reviewer_placeholders(value: Any, findings: list[InactiveReleaseApplicationDryRunPlanFinding]) -> None:
    for index, row in enumerate(_sequence(value)):
        if not isinstance(row, Mapping):
            findings.append(_finding("invalid-reviewer-placeholder", "Reviewer approval placeholders must be objects.", f"reviewer_approval_placeholders[{index}]"))
            continue
        for field in ("approval_id", "role", "disposition_placeholder", "required_before", "source_refs"):
            if field == "source_refs":
                if not _sequence(row.get(field)):
                    findings.append(_finding("missing-reviewer-placeholder-field", "Reviewer placeholder source refs are required.", f"reviewer_approval_placeholders[{index}].{field}"))
            elif not _non_empty_text(row.get(field)):
                findings.append(_finding("missing-reviewer-placeholder-field", "Reviewer placeholder field is required.", f"reviewer_approval_placeholders[{index}].{field}"))


def _validate_notes(value: Any, findings: list[InactiveReleaseApplicationDryRunPlanFinding]) -> None:
    seen_note_ids: set[str] = set()
    for index, row in enumerate(_sequence(value)):
        if not isinstance(row, Mapping):
            findings.append(_finding("invalid-note", "Non-application notes must be objects.", f"non_application_no_release_notes[{index}]"))
            continue
        note_id = str(row.get("note_id") or "")
        if note_id:
            seen_note_ids.add(note_id)
        if not _non_empty_text(row.get("note_id")) or not _non_empty_text(row.get("note")):
            findings.append(_finding("missing-note-field", "Non-application note id and text are required.", f"non_application_no_release_notes[{index}]"))
    for required_note_id in _REQUIRED_NOTE_IDS:
        if required_note_id not in seen_note_ids:
            findings.append(_finding("missing-non-application-no-release-note", "Required non-application/no-release note is missing.", f"non_application_no_release_notes.{required_note_id}"))


def _validate_validation_commands(value: Any, findings: list[InactiveReleaseApplicationDryRunPlanFinding]) -> None:
    commands = _sequence(value)
    if not commands:
        findings.append(_finding("missing-validation-command", "Validation commands are required.", "validation_commands"))
        return
    for index, command in enumerate(commands):
        if not isinstance(command, list) or not command or not all(isinstance(part, str) and part.strip() for part in command):
            findings.append(_finding("invalid-validation-command", "Validation command must be a non-empty argv string list.", f"validation_commands[{index}]"))


def _scan_for_forbidden_content(value: Any, findings: list[InactiveReleaseApplicationDryRunPlanFinding], location: str = "plan") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            normalized_key = key_text.lower().replace("-", "_")
            child_location = f"{location}.{key_text}"
            if _truthy(child) and any(token in normalized_key for token in _PRIVATE_OR_RAW_KEY_TOKENS):
                findings.append(_finding("private-or-raw-artifact-reference", "Plan must not include private, authenticated, session, browser, screenshot, trace, HAR, auth, raw crawl, PDF, or downloaded data artifacts.", child_location))
            _scan_for_forbidden_content(child, findings, child_location)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            _scan_for_forbidden_content(child, findings, f"{location}[{index}]")
    elif isinstance(value, str):
        normalized_path = PurePosixPath(value.replace("\\", "/")).as_posix()
        if any(pattern.search(normalized_path) for pattern in _PRIVATE_OR_RAW_PATTERNS):
            findings.append(_finding("private-or-raw-artifact-reference", "Plan must not reference private, browser, raw crawl, PDF, or downloaded artifacts.", location))
        if any(pattern.search(value) for pattern in _FORBIDDEN_TEXT_PATTERNS):
            findings.append(_finding("forbidden-release-or-official-action-language", "Plan must not claim live execution, applied/release-complete status, guarantee legal or permitting outcomes, or direct consequential official actions.", location))


def _fixture_family_from_path(path: str) -> str:
    normalized = PurePosixPath(str(path).replace("\\", "/")).as_posix()
    marker = "ppd/tests/fixtures/"
    if marker not in normalized:
        return ""
    remainder = normalized.split(marker, 1)[1]
    first = remainder.split("/", 1)[0].split("#", 1)[0]
    return _slug(first) if first else ""


def _artifact_path(value: Any) -> str:
    if isinstance(value, Mapping):
        raw_path = value.get("path") or value.get("artifact_path") or ""
    else:
        raw_path = value
    return PurePosixPath(str(raw_path).replace("\\", "/")).as_posix() if raw_path else ""


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


def _finding(code: str, message: str, location: str) -> InactiveReleaseApplicationDryRunPlanFinding:
    return InactiveReleaseApplicationDryRunPlanFinding(code=code, message=message, location=location)
