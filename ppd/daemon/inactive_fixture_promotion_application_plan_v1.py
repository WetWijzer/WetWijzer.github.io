"""Validation for inactive fixture promotion application plan v1 artifacts.

Application plans are offline, fixture-first review artifacts. They may describe
how inactive fixture rows would be staged, reviewed, validated, and rolled back,
but they must not carry private browser/session material, raw crawl/downloaded
payloads, live execution claims, legal/permitting guarantees, consequential
actions, or active mutation flags.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence


ARTIFACT_ID = "inactive_fixture_promotion_application_plan_v1"
SELF_TEST_COMMAND = ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]

_REQUIRED_FIXTURE_FAMILIES = frozenset(
    {
        "public_source_refresh",
        "devhub_observed_surface",
        "inactive_promotion_diff_ledger",
        "combined_rehearsal",
    }
)

_PRIVATE_ARTIFACT_TERMS = (
    "auth_state",
    "authenticated-browser",
    "browser_artifact",
    "browser_context",
    "cookie",
    "credential",
    "devhub_session",
    "har",
    "local_private_path",
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

_NEGATED_OR_BLOCKED_CONTEXT = (
    "do not ",
    "does not ",
    "must not ",
    "no ",
    "not ",
    "without ",
    "exclude ",
    "excluded ",
    "blocked ",
    "blocks ",
    "block ",
    "remain blocked",
    "remains blocked",
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


@dataclass(frozen=True)
class ApplicationPlanValidationResult:
    """Result returned by the inactive fixture promotion application plan validator."""

    valid: bool
    errors: tuple[str, ...]

    def require_valid(self) -> None:
        if not self.valid:
            raise ValueError("; ".join(self.errors))


def validate_inactive_fixture_promotion_application_plan_v1(
    plan: Mapping[str, Any],
) -> ApplicationPlanValidationResult:
    """Validate an inactive fixture promotion application plan v1 mapping."""

    errors: list[str] = []

    if plan.get("artifact_id") != ARTIFACT_ID:
        errors.append("artifact_id must be inactive_fixture_promotion_application_plan_v1")
    if plan.get("version") != 1:
        errors.append("version must be 1")

    family_rows = _sequence(plan.get("affected_fixture_family_rows"))
    family_ids: set[str] = set()
    if not family_rows:
        errors.append("affected_fixture_family_rows must include fixture-family rows")
    for index, row in enumerate(family_rows):
        if not isinstance(row, Mapping):
            errors.append(f"affected_fixture_family_rows[{index}] must be an object")
            continue
        family_id = _string(row.get("family_id"))
        if not family_id:
            errors.append(f"affected_fixture_family_rows[{index}].family_id is required")
        else:
            family_ids.add(family_id)
        if not _string(row.get("reviewer_owner")):
            errors.append(f"affected_fixture_family_rows[{index}].reviewer_owner is required")
        if not _string(row.get("review_focus")):
            errors.append(f"affected_fixture_family_rows[{index}].review_focus is required")
        target = _string(row.get("target_fixture_area"))
        if not target:
            errors.append(f"affected_fixture_family_rows[{index}].target_fixture_area is required")
        elif not target.startswith("ppd/tests/fixtures/"):
            errors.append(f"affected_fixture_family_rows[{index}].target_fixture_area must stay under ppd/tests/fixtures/")
    for family_id in sorted(_REQUIRED_FIXTURE_FAMILIES - family_ids):
        errors.append(f"affected_fixture_family_rows missing row for {family_id}")

    gates = _sequence(plan.get("dependency_gates"))
    gate_ids: set[str] = set()
    if not gates:
        errors.append("dependency_gates must include offline dependency gates")
    for index, gate in enumerate(gates):
        if not isinstance(gate, Mapping):
            errors.append(f"dependency_gates[{index}] must be an object")
            continue
        gate_id = _string(gate.get("gate_id"))
        if not gate_id:
            errors.append(f"dependency_gates[{index}].gate_id is required")
        else:
            gate_ids.add(gate_id)
        if gate.get("must_pass") is not True:
            errors.append(f"dependency_gates[{index}].must_pass must be true")
        if not _string(gate.get("offline_check")):
            errors.append(f"dependency_gates[{index}].offline_check is required")

    checkpoints = _sequence(plan.get("rollback_checkpoints"))
    checkpoint_ids: set[str] = set()
    if not checkpoints:
        errors.append("rollback_checkpoints must include rollback checkpoints")
    for index, checkpoint in enumerate(checkpoints):
        if not isinstance(checkpoint, Mapping):
            errors.append(f"rollback_checkpoints[{index}] must be an object")
            continue
        checkpoint_id = _string(checkpoint.get("checkpoint_id"))
        if not checkpoint_id:
            errors.append(f"rollback_checkpoints[{index}].checkpoint_id is required")
        else:
            checkpoint_ids.add(checkpoint_id)
        if not _string(checkpoint.get("restore_scope")):
            errors.append(f"rollback_checkpoints[{index}].restore_scope is required")

    steps = _sequence(plan.get("ordered_application_steps"))
    if not steps:
        errors.append("ordered_application_steps must include application steps")
    step_orders: list[int] = []
    for index, step in enumerate(steps):
        if not isinstance(step, Mapping):
            errors.append(f"ordered_application_steps[{index}] must be an object")
            continue
        order = step.get("order")
        if isinstance(order, int):
            step_orders.append(order)
        else:
            errors.append(f"ordered_application_steps[{index}].order is required")
        if not _string(step.get("step_id")):
            errors.append(f"ordered_application_steps[{index}].step_id is required")
        if not _string(step.get("action")):
            errors.append(f"ordered_application_steps[{index}].action is required")
        if not _string_list(step.get("citations")):
            errors.append(f"ordered_application_steps[{index}].citations is required")
        reviewer_owner = _string(step.get("reviewer_owner"))
        if not reviewer_owner:
            errors.append(f"ordered_application_steps[{index}].reviewer_owner is required")
        rollback_checkpoint = _string(step.get("rollback_checkpoint"))
        if not rollback_checkpoint:
            errors.append(f"ordered_application_steps[{index}].rollback_checkpoint is required")
        elif checkpoint_ids and rollback_checkpoint not in checkpoint_ids:
            errors.append(f"ordered_application_steps[{index}].rollback_checkpoint must reference rollback_checkpoints")
        step_gate_ids = _string_list_values(step.get("dependency_gates"))
        if not step_gate_ids:
            errors.append(f"ordered_application_steps[{index}].dependency_gates is required")
        for gate_id in step_gate_ids:
            if gate_ids and gate_id not in gate_ids:
                errors.append(f"ordered_application_steps[{index}].dependency_gates references unknown gate {gate_id}")
    if step_orders and step_orders != sorted(step_orders):
        errors.append("ordered_application_steps must be sorted by order")

    validation_commands = _sequence(plan.get("exact_offline_validation_commands"))
    if not validation_commands:
        errors.append("exact_offline_validation_commands must include offline validation commands")
    elif not any(_command_equals(command, SELF_TEST_COMMAND) for command in validation_commands):
        errors.append("exact_offline_validation_commands must include the PP&D daemon self-test command")
    for index, command in enumerate(validation_commands):
        command_parts = _command_parts(command)
        if not command_parts:
            errors.append(f"exact_offline_validation_commands[{index}] must be a list of command strings")
            continue
        command_text = " ".join(command_parts).lower()
        for term in _BLOCKED_COMMAND_TERMS:
            if term.replace("_", " ") in command_text or term in command_text:
                errors.append(f"exact_offline_validation_commands[{index}] must not include blocked live or consequential behavior: {term}")
                break

    _reject_terms(errors, plan, _PRIVATE_ARTIFACT_TERMS, "private/authenticated/session/browser artifact")
    _reject_terms(errors, plan, _RAW_ARTIFACT_TERMS, "raw crawl/PDF/downloaded data")
    _reject_terms(errors, plan, _LIVE_CLAIM_TERMS, "live execution or promotion-complete claim")
    _reject_terms(errors, plan, _GUARANTEE_TERMS, "legal or permitting outcome guarantee")
    _reject_terms(errors, plan, _CONSEQUENTIAL_ACTION_TERMS, "consequential action language")
    _reject_terms(errors, plan, _MUTATION_FLAG_TERMS, "active mutation flag", reject_negated=True)

    return ApplicationPlanValidationResult(valid=not errors, errors=tuple(errors))


def _reject_terms(
    errors: list[str],
    value: Any,
    terms: Iterable[str],
    label: str,
    *,
    reject_negated: bool = False,
) -> None:
    lowered_terms = tuple(term.lower() for term in terms)
    for path, text in _walk_strings(value):
        lowered = " ".join(text.lower().replace("_", " ").replace("-", " ").split())
        compact = text.lower().replace("-", "_")
        if not reject_negated and _has_safe_context(lowered):
            continue
        for term in lowered_terms:
            normalized_term = " ".join(term.replace("_", " ").replace("-", " ").split())
            if normalized_term in lowered or term in compact:
                errors.append(f"reject {label} at {path}: {term}")
                break


def _has_safe_context(text: str) -> bool:
    return any(prefix in text for prefix in _NEGATED_OR_BLOCKED_CONTEXT)


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


def _string(value: Any) -> str:
    if isinstance(value, str):
        return value.strip()
    return ""


def _string_list(value: Any) -> bool:
    return bool(_string_list_values(value))


def _string_list_values(value: Any) -> tuple[str, ...]:
    if not isinstance(value, Sequence) or isinstance(value, (bytes, bytearray, str)):
        return ()
    return tuple(item.strip() for item in value if isinstance(item, str) and item.strip())


def _command_parts(value: Any) -> tuple[str, ...]:
    return _string_list_values(value)


def _command_equals(value: Any, expected: Sequence[str]) -> bool:
    return list(_command_parts(value)) == list(expected)
