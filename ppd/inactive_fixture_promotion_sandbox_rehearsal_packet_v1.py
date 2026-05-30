"""Fixture-first inactive promotion sandbox rehearsal packet v1.

This packet consumes an inactive fixture promotion application plan and turns it
into synthetic sandbox apply rows. It is a review artifact only: it does not
write active fixtures, mutate release state, change prompts, access DevHub,
crawl live sources, or perform official actions.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence


ARTIFACT_ID = "inactive_fixture_promotion_sandbox_rehearsal_packet_v1"
SOURCE_PLAN_ARTIFACT_ID = "inactive_fixture_promotion_application_plan_v1"
SELF_TEST_COMMAND = ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]

_REQUIRED_TOP_LEVEL_FLAGS = (
    "active_fixture_mutation",
    "active_source_mutation",
    "active_document_mutation",
    "active_requirement_mutation",
    "active_process_mutation",
    "active_guardrail_mutation",
    "active_prompt_mutation",
    "active_release_state_mutation",
    "active_agent_state_mutation",
    "devhub_accessed",
    "live_source_crawl_performed",
    "official_action_performed",
    "main_worktree_changed",
)

_PRIVATE_ARTIFACT_TERMS = (
    "auth_state",
    "authenticated-browser",
    "browser_artifact",
    "browser_context",
    "cookie",
    "credential",
    "har",
    "mfa",
    "password",
    "playwright-report",
    "private-devhub-session",
    "private_value",
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


@dataclass(frozen=True)
class SandboxRehearsalValidationResult:
    """Result returned by the sandbox rehearsal validator."""

    valid: bool
    errors: tuple[str, ...]

    def require_valid(self) -> None:
        if not self.valid:
            raise ValueError("; ".join(self.errors))


def build_inactive_fixture_promotion_sandbox_rehearsal_packet_v1(
    application_patch_plan: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a deterministic sandbox rehearsal packet from an application plan."""

    plan = deepcopy(dict(application_patch_plan))
    family_rows = [row for row in _sequence(plan.get("affected_fixture_family_rows")) if isinstance(row, Mapping)]
    application_steps = [row for row in _sequence(plan.get("ordered_application_steps")) if isinstance(row, Mapping)]
    application_steps.sort(key=lambda row: row.get("order") if isinstance(row.get("order"), int) else 9999)

    packet: dict[str, Any] = {
        "artifact_id": ARTIFACT_ID,
        "artifact_type": "fixture_first_inactive_promotion_sandbox_rehearsal",
        "version": 1,
        "status": "review_ready",
        "dry_run": True,
        "sandbox_only": True,
        "fixture_first": True,
        "consumed_input_packet_refs": [
            {
                "role": "inactive_fixture_promotion_application_patch_plan_v1",
                "artifact_id": _text(plan.get("artifact_id"), SOURCE_PLAN_ARTIFACT_ID),
                "version": plan.get("version", 1),
                "status": _text(plan.get("status"), "review_ready"),
            }
        ],
        "synthetic_sandbox_apply_steps": _synthetic_apply_steps(application_steps, family_rows),
        "expected_changed_fixture_family_inventory": _fixture_family_inventory(family_rows),
        "pre_apply_validation_commands": [SELF_TEST_COMMAND],
        "post_apply_validation_commands": [SELF_TEST_COMMAND],
        "rollback_rehearsal_commands": [SELF_TEST_COMMAND],
        "no_main_worktree_change_notes": _no_main_worktree_change_notes(family_rows),
        "reviewer_signoff_placeholders": _reviewer_signoff_placeholders(family_rows),
        "attestations": {
            "no_active_fixtures_modified": True,
            "no_prompts_modified": True,
            "no_release_state_modified": True,
            "no_live_source_crawl": True,
            "no_devhub_access": True,
            "no_official_actions": True,
            "no_private_artifacts": True,
            "no_raw_downloaded_artifacts": True,
        },
    }
    for flag in _REQUIRED_TOP_LEVEL_FLAGS:
        packet[flag] = False

    validate_inactive_fixture_promotion_sandbox_rehearsal_packet_v1(packet).require_valid()
    return packet


def validate_inactive_fixture_promotion_sandbox_rehearsal_packet_v1(
    packet: Mapping[str, Any],
) -> SandboxRehearsalValidationResult:
    """Validate an inactive promotion sandbox rehearsal packet v1 mapping."""

    errors: list[str] = []

    if packet.get("artifact_id") != ARTIFACT_ID:
        errors.append("artifact_id must be inactive_fixture_promotion_sandbox_rehearsal_packet_v1")
    if packet.get("version") != 1:
        errors.append("version must be 1")
    if packet.get("dry_run") is not True:
        errors.append("dry_run must be true")
    if packet.get("sandbox_only") is not True:
        errors.append("sandbox_only must be true")
    if packet.get("fixture_first") is not True:
        errors.append("fixture_first must be true")

    _validate_consumed_refs(errors, packet.get("consumed_input_packet_refs"))
    _validate_apply_steps(errors, packet.get("synthetic_sandbox_apply_steps"))
    _validate_fixture_family_inventory(errors, packet.get("expected_changed_fixture_family_inventory"))
    _validate_command_list(errors, packet.get("pre_apply_validation_commands"), "pre_apply_validation_commands")
    _validate_command_list(errors, packet.get("post_apply_validation_commands"), "post_apply_validation_commands")
    _validate_command_list(errors, packet.get("rollback_rehearsal_commands"), "rollback_rehearsal_commands")
    _validate_no_main_worktree_notes(errors, packet.get("no_main_worktree_change_notes"))
    _validate_signoff_placeholders(errors, packet.get("reviewer_signoff_placeholders"))
    _validate_attestations(errors, packet.get("attestations"))

    for flag in _REQUIRED_TOP_LEVEL_FLAGS:
        if packet.get(flag) is not False:
            errors.append(f"{flag} must be false")

    _reject_terms(errors, packet, _PRIVATE_ARTIFACT_TERMS, "private/authenticated/session/browser artifact")
    _reject_terms(errors, packet, _RAW_ARTIFACT_TERMS, "raw crawl/PDF/downloaded data")
    _reject_terms(errors, packet, _LIVE_CLAIM_TERMS, "live execution or promotion-complete claim")
    _reject_terms(errors, packet, _GUARANTEE_TERMS, "legal or permitting outcome guarantee")
    _reject_terms(errors, packet, _CONSEQUENTIAL_ACTION_TERMS, "consequential action language")

    return SandboxRehearsalValidationResult(valid=not errors, errors=tuple(errors))


def assert_valid_inactive_fixture_promotion_sandbox_rehearsal_packet_v1(packet: Mapping[str, Any]) -> None:
    validate_inactive_fixture_promotion_sandbox_rehearsal_packet_v1(packet).require_valid()


def _synthetic_apply_steps(
    application_steps: Sequence[Mapping[str, Any]],
    family_rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    family_ids = [_text(row.get("family_id")) for row in family_rows if _text(row.get("family_id"))]
    steps: list[dict[str, Any]] = []
    for index, step in enumerate(application_steps, start=1):
        source_step_id = _text(step.get("step_id"), f"source-step-{index:03d}")
        steps.append(
            {
                "order": index,
                "step_id": f"sandbox_apply_{source_step_id}",
                "source_step_id": source_step_id,
                "synthetic_apply_action": "Stage synthetic complete-file replacement metadata for inactive fixture family review.",
                "target_fixture_families": family_ids,
                "pre_apply_validation_commands": [SELF_TEST_COMMAND],
                "post_apply_validation_commands": [SELF_TEST_COMMAND],
                "rollback_rehearsal_commands": [SELF_TEST_COMMAND],
                "reviewer_owner": _text(step.get("reviewer_owner"), "promotion-supervisor-reviewer"),
                "citations": _string_list(step.get("citations")) or [f"inactive-sandbox-rehearsal:v1:{source_step_id}"],
            }
        )
    return steps


def _fixture_family_inventory(family_rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    inventory: list[dict[str, Any]] = []
    for row in family_rows:
        family_id = _text(row.get("family_id"))
        if not family_id:
            continue
        inventory.append(
            {
                "family_id": family_id,
                "target_fixture_area": _text(row.get("target_fixture_area")),
                "expected_change_type": "synthetic_sandbox_complete_replacement",
                "active_fixture_mutation": False,
                "reviewer_owner": _text(row.get("reviewer_owner"), "fixture-reviewer"),
                "review_focus": _text(row.get("review_focus"), "inactive fixture family review"),
                "citations": [f"inactive-sandbox-rehearsal:v1:family:{family_id}"],
            }
        )
    return inventory


def _no_main_worktree_change_notes(family_rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    notes = [
        {
            "note_id": "no-main-worktree-change-sandbox-only",
            "scope": "main_worktree",
            "asserted_unchanged": True,
            "note": "The rehearsal describes synthetic sandbox rows only and leaves the main worktree unchanged.",
            "citations": ["inactive-sandbox-rehearsal:v1:no-main-worktree-change"],
        }
    ]
    for row in family_rows:
        family_id = _text(row.get("family_id"))
        target = _text(row.get("target_fixture_area"))
        if family_id and target:
            notes.append(
                {
                    "note_id": f"no-main-worktree-change-{family_id}",
                    "scope": target,
                    "asserted_unchanged": True,
                    "note": "Fixture family is inventoried as an expected sandbox change family, not applied to active fixtures by this packet.",
                    "citations": [f"inactive-sandbox-rehearsal:v1:family:{family_id}"],
                }
            )
    return notes


def _reviewer_signoff_placeholders(family_rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    placeholders: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in family_rows:
        reviewer = _text(row.get("reviewer_owner"), "fixture-reviewer")
        family_id = _text(row.get("family_id"), "fixture-family")
        signoff_id = f"signoff-{family_id}"
        seen.add(signoff_id)
        placeholders.append(
            {
                "signoff_id": signoff_id,
                "family_id": family_id,
                "reviewer_owner": reviewer,
                "status": "pending_manual_review",
                "reviewer_name": "",
                "signed_at": "",
                "disposition": "",
                "citations": [f"inactive-sandbox-rehearsal:v1:signoff:{family_id}"],
            }
        )
    if "signoff-promotion-supervisor" not in seen:
        placeholders.append(
            {
                "signoff_id": "signoff-promotion-supervisor",
                "family_id": "sandbox_rehearsal_packet",
                "reviewer_owner": "promotion-supervisor-reviewer",
                "status": "pending_manual_review",
                "reviewer_name": "",
                "signed_at": "",
                "disposition": "",
                "citations": ["inactive-sandbox-rehearsal:v1:signoff:supervisor"],
            }
        )
    return placeholders


def _validate_consumed_refs(errors: list[str], value: Any) -> None:
    rows = _sequence(value)
    if not rows:
        errors.append("consumed_input_packet_refs must include the application patch plan reference")
        return
    if not any(isinstance(row, Mapping) and row.get("artifact_id") == SOURCE_PLAN_ARTIFACT_ID for row in rows):
        errors.append("consumed_input_packet_refs must reference inactive_fixture_promotion_application_plan_v1")


def _validate_apply_steps(errors: list[str], value: Any) -> None:
    rows = _sequence(value)
    if not rows:
        errors.append("synthetic_sandbox_apply_steps must include apply steps")
        return
    orders: list[int] = []
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            errors.append(f"synthetic_sandbox_apply_steps[{index}] must be an object")
            continue
        order = row.get("order")
        if not isinstance(order, int):
            errors.append(f"synthetic_sandbox_apply_steps[{index}].order is required")
        else:
            orders.append(order)
        for key in ("step_id", "source_step_id", "synthetic_apply_action", "reviewer_owner"):
            if not _text(row.get(key)):
                errors.append(f"synthetic_sandbox_apply_steps[{index}].{key} is required")
        if not _string_list(row.get("target_fixture_families")):
            errors.append(f"synthetic_sandbox_apply_steps[{index}].target_fixture_families is required")
        if not _string_list(row.get("citations")):
            errors.append(f"synthetic_sandbox_apply_steps[{index}].citations is required")
        _validate_command_list(errors, row.get("pre_apply_validation_commands"), f"synthetic_sandbox_apply_steps[{index}].pre_apply_validation_commands")
        _validate_command_list(errors, row.get("post_apply_validation_commands"), f"synthetic_sandbox_apply_steps[{index}].post_apply_validation_commands")
        _validate_command_list(errors, row.get("rollback_rehearsal_commands"), f"synthetic_sandbox_apply_steps[{index}].rollback_rehearsal_commands")
    if orders != sorted(orders):
        errors.append("synthetic_sandbox_apply_steps must be sorted by order")


def _validate_fixture_family_inventory(errors: list[str], value: Any) -> None:
    rows = _sequence(value)
    if not rows:
        errors.append("expected_changed_fixture_family_inventory must include fixture-family rows")
        return
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            errors.append(f"expected_changed_fixture_family_inventory[{index}] must be an object")
            continue
        for key in ("family_id", "target_fixture_area", "expected_change_type", "reviewer_owner", "review_focus"):
            if not _text(row.get(key)):
                errors.append(f"expected_changed_fixture_family_inventory[{index}].{key} is required")
        target = _text(row.get("target_fixture_area"))
        if target and not target.startswith("ppd/tests/fixtures/"):
            errors.append(f"expected_changed_fixture_family_inventory[{index}].target_fixture_area must stay under ppd/tests/fixtures/")
        if row.get("expected_change_type") != "synthetic_sandbox_complete_replacement":
            errors.append(f"expected_changed_fixture_family_inventory[{index}].expected_change_type must be synthetic_sandbox_complete_replacement")
        if row.get("active_fixture_mutation") is not False:
            errors.append(f"expected_changed_fixture_family_inventory[{index}].active_fixture_mutation must be false")
        if not _string_list(row.get("citations")):
            errors.append(f"expected_changed_fixture_family_inventory[{index}].citations is required")


def _validate_command_list(errors: list[str], value: Any, label: str) -> None:
    commands = _sequence(value)
    if not commands:
        errors.append(f"{label} must include validation commands")
        return
    if not any(list(_string_list_values(command)) == SELF_TEST_COMMAND for command in commands):
        errors.append(f"{label} must include the PP&D daemon self-test command")
    for index, command in enumerate(commands):
        parts = _string_list_values(command)
        if not parts:
            errors.append(f"{label}[{index}] must be a list of command strings")
            continue
        command_text = " ".join(parts).lower()
        for term in _BLOCKED_COMMAND_TERMS:
            if term in command_text or term.replace("_", " ") in command_text:
                errors.append(f"{label}[{index}] must not include blocked live or consequential behavior: {term}")
                break


def _validate_no_main_worktree_notes(errors: list[str], value: Any) -> None:
    rows = _sequence(value)
    if not rows:
        errors.append("no_main_worktree_change_notes must include notes")
        return
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            errors.append(f"no_main_worktree_change_notes[{index}] must be an object")
            continue
        if not _text(row.get("note_id")):
            errors.append(f"no_main_worktree_change_notes[{index}].note_id is required")
        if row.get("asserted_unchanged") is not True:
            errors.append(f"no_main_worktree_change_notes[{index}].asserted_unchanged must be true")
        if not _string_list(row.get("citations")):
            errors.append(f"no_main_worktree_change_notes[{index}].citations is required")


def _validate_signoff_placeholders(errors: list[str], value: Any) -> None:
    rows = _sequence(value)
    if not rows:
        errors.append("reviewer_signoff_placeholders must include placeholders")
        return
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            errors.append(f"reviewer_signoff_placeholders[{index}] must be an object")
            continue
        for key in ("signoff_id", "family_id", "reviewer_owner", "status"):
            if not _text(row.get(key)):
                errors.append(f"reviewer_signoff_placeholders[{index}].{key} is required")
        if row.get("status") != "pending_manual_review":
            errors.append(f"reviewer_signoff_placeholders[{index}].status must be pending_manual_review")
        for blank_key in ("reviewer_name", "signed_at", "disposition"):
            if row.get(blank_key) not in ("", None):
                errors.append(f"reviewer_signoff_placeholders[{index}].{blank_key} must stay blank")
        if not _string_list(row.get("citations")):
            errors.append(f"reviewer_signoff_placeholders[{index}].citations is required")


def _validate_attestations(errors: list[str], value: Any) -> None:
    if not isinstance(value, Mapping):
        errors.append("attestations must be an object")
        return
    for key in (
        "no_active_fixtures_modified",
        "no_prompts_modified",
        "no_release_state_modified",
        "no_live_source_crawl",
        "no_devhub_access",
        "no_official_actions",
        "no_private_artifacts",
        "no_raw_downloaded_artifacts",
    ):
        if value.get(key) is not True:
            errors.append(f"attestations.{key} must be true")


def _reject_terms(errors: list[str], value: Any, terms: Sequence[str], label: str) -> None:
    for path, candidate in _walk_text(value):
        lowered = " ".join(candidate.lower().split())
        for term in terms:
            normalized_term = " ".join(term.lower().split())
            if normalized_term in lowered and not _has_negated_context(lowered):
                errors.append(f"{path} must not include {label}: {term}")
                break


def _walk_text(value: Any, path: str = "packet") -> Iterable[tuple[str, str]]:
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            yield child_path, str(key)
            yield from _walk_text(child, child_path)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child in enumerate(value):
            yield from _walk_text(child, f"{path}[{index}]")
    elif isinstance(value, str):
        yield path, value


def _has_negated_context(text: str) -> bool:
    return any(prefix in text for prefix in _NEGATED_OR_BLOCKED_CONTEXT)


def _sequence(value: Any) -> Sequence[Any]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return value
    return ()


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


def _string_list_values(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [item for item in value if isinstance(item, str)]


def _text(value: Any, fallback: str = "") -> str:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return fallback
