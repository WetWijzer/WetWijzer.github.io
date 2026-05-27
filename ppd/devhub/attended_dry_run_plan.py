"""Fixture-first attended DevHub dry-run plan validation.

This validator is deterministic and side-effect free. It accepts only committed
synthetic fixtures for read-only and reversible draft DevHub planning.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence


class AttendedDryRunPlanError(ValueError):
    """Raised when a dry-run plan is unsafe or incomplete."""


@dataclass(frozen=True)
class AttendedDryRunPlanResult:
    plan_id: str
    surface_count: int
    action_count: int
    missing_fact_count: int
    missing_document_count: int
    preview_count: int
    refused_action_classes: tuple[str, ...]
    journal_event_types: tuple[str, ...]


PLAN_VERSION = "devhub-attended-dry-run-plan-v1"
RUN_MODE = "fixture_first_attended_devhub_dry_run"
MINIMUM_SELECTOR_CONFIDENCE = 0.85
ALLOWED_STATES = {"read_only", "reversible_draft"}
ALLOWED_DECISIONS = {"allow_read_only", "allow_reversible_draft"}
REFUSAL_DECISION = "refuse"
REQUIRED_PREVIEWS = {"surface_map", "user_case_gap", "reversible_draft"}
REQUIRED_JOURNAL_EVENTS = {
    "DevHub attended preflight",
    "user gap analysis",
    "reversible draft plan",
    "local PDF preview",
    "manual handoff",
}
REQUIRED_REFUSED_ACTION_CLASSES = {
    "account_creation_automation",
    "cancellation",
    "captcha_automation",
    "certification",
    "final_payment_execution",
    "inspection_scheduling",
    "login_automation",
    "mfa_automation",
    "official_upload",
    "payment_detail_entry",
    "submission",
}
FORBIDDEN_ACTION_CLASSES = REQUIRED_REFUSED_ACTION_CLASSES | {
    "account_creation",
    "captcha",
    "login",
    "mfa",
    "password_recovery",
    "payment_execution",
    "payment_submission",
}
FORBIDDEN_PRIVATE_FIELDS = {
    "auth_state",
    "captcha",
    "cookie",
    "credentials",
    "download_path",
    "har_path",
    "mfa",
    "password",
    "payment_details",
    "private_file_path",
    "raw_crawl_output",
    "screenshot_path",
    "session_file",
    "storage_state",
    "trace_path",
}


def load_plan(path: str | Path) -> Mapping[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise AttendedDryRunPlanError("plan fixture must be a JSON object")
    return data


def validate_plan_file(path: str | Path) -> AttendedDryRunPlanResult:
    return validate_plan(load_plan(path))


def validate_plan(plan: Mapping[str, Any]) -> AttendedDryRunPlanResult:
    _reject_private_fields(plan, "plan")
    _validate_header(plan)

    surfaces = _required_list(plan, "surface_map_readiness")
    actions = _required_list(plan, "action_decisions")
    gaps = _required_mapping(plan, "user_case_gap_analysis")
    previews = _required_list(plan, "preview_requirements")
    journal_events = _required_list(plan, "journal_event_expectations")

    _validate_surfaces(surfaces)
    _validate_actions(actions)
    missing_fact_count, missing_document_count, refused_action_classes = _validate_gaps(gaps)
    _validate_previews(previews)
    journal_event_types = _validate_journal_events(journal_events)

    return AttendedDryRunPlanResult(
        plan_id=_required_text(plan, "plan_id"),
        surface_count=len(surfaces),
        action_count=len(actions),
        missing_fact_count=missing_fact_count,
        missing_document_count=missing_document_count,
        preview_count=len(previews),
        refused_action_classes=tuple(sorted(refused_action_classes)),
        journal_event_types=tuple(sorted(journal_event_types)),
    )


def _validate_header(plan: Mapping[str, Any]) -> None:
    if plan.get("plan_version") != PLAN_VERSION:
        raise AttendedDryRunPlanError("plan_version must be devhub-attended-dry-run-plan-v1")
    if plan.get("run_mode") != RUN_MODE:
        raise AttendedDryRunPlanError("run_mode must be fixture_first_attended_devhub_dry_run")
    if plan.get("live_devhub_session") is not False:
        raise AttendedDryRunPlanError("live_devhub_session must be false")
    if plan.get("browser_launched") is not False:
        raise AttendedDryRunPlanError("browser_launched must be false")
    if plan.get("auth_state_saved") is not False:
        raise AttendedDryRunPlanError("auth_state_saved must be false")
    allowed = plan.get("allowed_state_classes")
    if not isinstance(allowed, list) or set(allowed) != ALLOWED_STATES:
        raise AttendedDryRunPlanError("allowed_state_classes must be exactly read_only and reversible_draft")


def _validate_surfaces(surfaces: Sequence[Any]) -> None:
    for index, surface in enumerate(surfaces):
        if not isinstance(surface, Mapping):
            raise AttendedDryRunPlanError(f"surface_map_readiness[{index}] must be an object")
        surface_id = _required_text(surface, "surface_id")
        if _required_text(surface, "state_class") not in ALLOWED_STATES:
            raise AttendedDryRunPlanError(f"surface {surface_id} has forbidden state_class")
        if surface.get("ready_for_dry_run") is not True:
            raise AttendedDryRunPlanError(f"surface {surface_id} must be ready_for_dry_run")
        if surface.get("requires_attendance") is not True:
            raise AttendedDryRunPlanError(f"surface {surface_id} must require attendance")
        if surface.get("requires_exact_confirmation") is not False:
            raise AttendedDryRunPlanError(f"surface {surface_id} must not require exact confirmation")
        if not _confidence_at_or_above(surface.get("selector_confidence"), MINIMUM_SELECTOR_CONFIDENCE):
            raise AttendedDryRunPlanError(f"surface {surface_id} selector confidence is too low")
        _required_list(surface, "readiness_evidence")


def _validate_actions(actions: Sequence[Any]) -> None:
    for index, action in enumerate(actions):
        if not isinstance(action, Mapping):
            raise AttendedDryRunPlanError(f"action_decisions[{index}] must be an object")
        action_id = _required_text(action, "action_id")
        action_class = _required_text(action, "action_class")
        if action_class in FORBIDDEN_ACTION_CLASSES or action_class not in ALLOWED_STATES:
            raise AttendedDryRunPlanError(f"action {action_id} must be read_only or reversible_draft only")
        if _required_text(action, "decision") not in ALLOWED_DECISIONS:
            raise AttendedDryRunPlanError(f"action {action_id} has forbidden decision")
        if action.get("may_execute_in_dry_run") is not True:
            raise AttendedDryRunPlanError(f"action {action_id} must be dry-run executable")
        if action.get("changes_official_state") is not False:
            raise AttendedDryRunPlanError(f"action {action_id} must not change official state")
        if action.get("requires_exact_confirmation") is not False:
            raise AttendedDryRunPlanError(f"action {action_id} must not require exact confirmation")


def _validate_gaps(gaps: Mapping[str, Any]) -> tuple[int, int, set[str]]:
    _required_text(gaps, "case_id")
    missing_facts = _required_list(gaps, "missing_facts")
    missing_documents = _required_list(gaps, "missing_documents")
    next_safe_actions = _required_list(gaps, "next_safe_actions")
    blocked_actions = _required_list(gaps, "blocked_actions")
    for action in next_safe_actions:
        if not isinstance(action, Mapping) or _required_text(action, "action_class") not in ALLOWED_STATES:
            raise AttendedDryRunPlanError("next_safe_actions must stay read-only or reversible draft")

    refused_action_classes: set[str] = set()
    for action in blocked_actions:
        if not isinstance(action, Mapping):
            raise AttendedDryRunPlanError("blocked_actions entries must be objects")
        action_id = _required_text(action, "action_id")
        action_class = _required_text(action, "action_class")
        if action_class not in REQUIRED_REFUSED_ACTION_CLASSES:
            raise AttendedDryRunPlanError("blocked_actions must name required refused action classes")
        refused_action_classes.add(action_class)
        if action.get("decision") != REFUSAL_DECISION:
            raise AttendedDryRunPlanError(f"blocked action {action_id} must be refused")
        if action.get("may_execute_in_dry_run") is not False:
            raise AttendedDryRunPlanError(f"blocked action {action_id} must not execute in dry run")
        if action.get("blocked_until") != "manual_handoff_and_exact_confirmation":
            raise AttendedDryRunPlanError("blocked_actions must require manual handoff and exact confirmation")
        if action.get("refusal_reason") != "consequential_devhub_action":
            raise AttendedDryRunPlanError(f"blocked action {action_id} must use the consequential DevHub refusal reason")

    missing_refusals = REQUIRED_REFUSED_ACTION_CLASSES - refused_action_classes
    if missing_refusals:
        raise AttendedDryRunPlanError("blocked_actions missing required refused action classes")
    return len(missing_facts), len(missing_documents), refused_action_classes


def _validate_previews(previews: Sequence[Any]) -> None:
    kinds = set()
    for index, preview in enumerate(previews):
        if not isinstance(preview, Mapping):
            raise AttendedDryRunPlanError(f"preview_requirements[{index}] must be an object")
        preview_id = _required_text(preview, "preview_id")
        kinds.add(_required_text(preview, "preview_kind"))
        if preview.get("required_before_devhub_interaction") is not True:
            raise AttendedDryRunPlanError(f"preview {preview_id} must be required before DevHub interaction")
        if preview.get("contains_private_values") is not False:
            raise AttendedDryRunPlanError(f"preview {preview_id} must not contain private values")
        if preview.get("may_touch_live_devhub") is not False:
            raise AttendedDryRunPlanError(f"preview {preview_id} must not touch live DevHub")
    if REQUIRED_PREVIEWS - kinds:
        raise AttendedDryRunPlanError("preview requirements missing required kind")


def _validate_journal_events(events: Sequence[Any]) -> set[str]:
    event_types = set()
    for index, event in enumerate(events):
        if not isinstance(event, Mapping):
            raise AttendedDryRunPlanError(f"journal_event_expectations[{index}] must be an object")
        event_type = _required_text(event, "event_type")
        event_types.add(event_type)
        if event_type not in REQUIRED_JOURNAL_EVENTS:
            raise AttendedDryRunPlanError(f"journal event {event_type!r} is not allowed")
        if event.get("commit_safe") is not True:
            raise AttendedDryRunPlanError(f"journal event {event_type!r} must be commit safe")
        if event.get("contains_private_values") is not False:
            raise AttendedDryRunPlanError(f"journal event {event_type!r} must not contain private values")
        if event.get("records_browser_artifact") is not False:
            raise AttendedDryRunPlanError(f"journal event {event_type!r} must not record browser artifacts")
    if REQUIRED_JOURNAL_EVENTS - event_types:
        raise AttendedDryRunPlanError("journal expectations missing required event type")
    return event_types


def _required_mapping(value: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    item = value.get(key)
    if not isinstance(item, Mapping):
        raise AttendedDryRunPlanError(f"{key} must be an object")
    return item


def _required_list(value: Mapping[str, Any], key: str) -> list[Any]:
    item = value.get(key)
    if not isinstance(item, list) or not item:
        raise AttendedDryRunPlanError(f"{key} must be a non-empty array")
    return item


def _required_text(value: Mapping[str, Any], key: str) -> str:
    item = value.get(key)
    if not isinstance(item, str) or not item.strip():
        raise AttendedDryRunPlanError(f"{key} must be a non-empty string")
    return item.strip()


def _confidence_at_or_above(value: Any, minimum: float) -> bool:
    if isinstance(value, bool):
        return False
    try:
        return float(value) >= minimum
    except (TypeError, ValueError):
        return False


def _reject_private_fields(value: Any, path: str) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if not isinstance(key, str):
                raise AttendedDryRunPlanError(f"{path} contains a non-string field name")
            if key.strip().lower().replace("-", "_") in FORBIDDEN_PRIVATE_FIELDS:
                raise AttendedDryRunPlanError(f"forbidden private field at {path}.{key}")
            _reject_private_fields(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_private_fields(child, f"{path}[{index}]")
