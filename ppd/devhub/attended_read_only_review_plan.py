"""Fixture-first attended DevHub read-only review plan validation.

The validator is deterministic and local. It accepts only committed fixtures that
model redacted accessible structure for account-scoped DevHub review states after
a manual-login handoff. It does not launch a browser, store auth state, crawl
DevHub, download documents, or authorize consequential actions.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence


class AttendedReadOnlyReviewPlanError(ValueError):
    """Raised when an attended read-only review plan is unsafe or incomplete."""


@dataclass(frozen=True)
class AttendedReadOnlyReviewPlanResult:
    plan_id: str
    review_state_count: int
    allowed_action_count: int
    blocked_action_count: int
    review_states: tuple[str, ...]


PLAN_VERSION = "devhub-attended-read-only-review-plan-v1"
RUN_MODE = "fixture_first_attended_devhub_read_only_review"
SOURCE_METADATA_KIND = "redacted_accessible_structure"

REQUIRED_REVIEW_STATES = {
    "status_review",
    "fee_notice_review",
    "correction_request_review",
    "attachment_list_review",
    "inspection_result_review",
}

ALLOWED_READ_ONLY_ACTIONS = {
    "open_review_state",
    "read_accessible_structure",
    "summarize_redacted_metadata",
}

REQUIRED_REJECTED_ARTIFACTS = {
    "screenshots",
    "traces",
    "har_data",
    "cookies",
    "auth_state",
    "credentials",
    "private_values",
}

REQUIRED_BLOCKED_ACTIONS = {
    "account_creation",
    "cancellation",
    "captcha_automation",
    "certification",
    "document_download",
    "final_payment_execution",
    "inspection_scheduling",
    "login_automation",
    "mfa_automation",
    "official_upload",
    "payment_detail_entry",
    "raw_page_capture",
    "submission",
}

FORBIDDEN_PRIVATE_FIELDS = {
    "auth_state",
    "auth_state_path",
    "captcha",
    "cookie",
    "cookies",
    "credential",
    "credentials",
    "download_path",
    "har",
    "har_data",
    "har_path",
    "mfa_secret",
    "password",
    "payment_details",
    "private_file_path",
    "private_value",
    "private_values",
    "raw_crawl_output",
    "raw_document",
    "raw_html",
    "screenshot",
    "screenshot_path",
    "screenshots",
    "session_file",
    "storage_state",
    "trace",
    "trace_path",
    "traces",
}

FORBIDDEN_VALUE_MARKERS = (
    "password=",
    "set-cookie",
    "storage_state",
    "trace.zip",
    "har.zip",
    "card_number",
    "routing_number",
    "cvv",
)


def load_review_plan(path: str | Path) -> Mapping[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise AttendedReadOnlyReviewPlanError("read-only review plan fixture must be a JSON object")
    return data


def validate_review_plan_file(path: str | Path) -> AttendedReadOnlyReviewPlanResult:
    return validate_review_plan(load_review_plan(path))


def validate_review_plan(plan: Mapping[str, Any]) -> AttendedReadOnlyReviewPlanResult:
    _reject_private_fields(plan, "plan")
    _validate_header(plan)
    _validate_manual_login_handoff(_required_mapping(plan, "manual_login_handoff"))

    rejected_artifacts = _required_list(plan, "rejected_artifacts")
    review_states = _required_list(plan, "review_states")
    blocked_actions = _required_list(plan, "blocked_consequential_actions")
    _validate_rejected_artifacts(rejected_artifacts)
    state_names, allowed_action_count = _validate_review_states(review_states)
    _validate_blocked_actions(blocked_actions)

    return AttendedReadOnlyReviewPlanResult(
        plan_id=_required_text(plan, "plan_id"),
        review_state_count=len(review_states),
        allowed_action_count=allowed_action_count,
        blocked_action_count=len(blocked_actions),
        review_states=tuple(sorted(state_names)),
    )


def _validate_header(plan: Mapping[str, Any]) -> None:
    if plan.get("plan_version") != PLAN_VERSION:
        raise AttendedReadOnlyReviewPlanError("plan_version must be devhub-attended-read-only-review-plan-v1")
    if plan.get("run_mode") != RUN_MODE:
        raise AttendedReadOnlyReviewPlanError("run_mode must be fixture_first_attended_devhub_read_only_review")
    if plan.get("source_metadata_kind") != SOURCE_METADATA_KIND:
        raise AttendedReadOnlyReviewPlanError("source_metadata_kind must be redacted_accessible_structure")
    if plan.get("live_devhub_session") is not False:
        raise AttendedReadOnlyReviewPlanError("live_devhub_session must be false for committed fixtures")
    if plan.get("browser_launched") is not False:
        raise AttendedReadOnlyReviewPlanError("browser_launched must be false for fixture validation")
    if plan.get("private_values_persisted") is not False:
        raise AttendedReadOnlyReviewPlanError("private_values_persisted must be false")


def _validate_manual_login_handoff(handoff: Mapping[str, Any]) -> None:
    if handoff.get("required") is not True:
        raise AttendedReadOnlyReviewPlanError("manual login handoff is required")
    if handoff.get("requires_user_attendance") is not True:
        raise AttendedReadOnlyReviewPlanError("manual login handoff must require user attendance")
    if handoff.get("credentials_collected") is not False:
        raise AttendedReadOnlyReviewPlanError("credentials must not be collected")
    if handoff.get("auth_state_saved") is not False:
        raise AttendedReadOnlyReviewPlanError("auth state must not be saved")
    if handoff.get("worker_completes_mfa") is not False:
        raise AttendedReadOnlyReviewPlanError("worker must not complete MFA")
    if handoff.get("worker_solves_captcha") is not False:
        raise AttendedReadOnlyReviewPlanError("worker must not solve CAPTCHA")
    if _required_text(handoff, "continue_after") != "authenticated_home_visible":
        raise AttendedReadOnlyReviewPlanError("manual login handoff must continue only after authenticated home is visible")


def _validate_rejected_artifacts(artifacts: Sequence[Any]) -> None:
    seen: set[str] = set()
    for index, artifact in enumerate(artifacts):
        if not isinstance(artifact, Mapping):
            raise AttendedReadOnlyReviewPlanError(f"rejected_artifacts[{index}] must be an object")
        artifact_kind = _required_text(artifact, "artifact_kind")
        seen.add(artifact_kind)
        if artifact_kind not in REQUIRED_REJECTED_ARTIFACTS:
            raise AttendedReadOnlyReviewPlanError(f"artifact {artifact_kind} is not part of the read-only privacy boundary")
        if artifact.get("decision") != "reject":
            raise AttendedReadOnlyReviewPlanError(f"artifact {artifact_kind} must be rejected")
        if artifact.get("persisted") is not False:
            raise AttendedReadOnlyReviewPlanError(f"artifact {artifact_kind} must not be persisted")
        if artifact.get("may_capture") is not False:
            raise AttendedReadOnlyReviewPlanError(f"artifact {artifact_kind} must not be captured")
        _required_text(artifact, "reason")
    missing = REQUIRED_REJECTED_ARTIFACTS - seen
    if missing:
        raise AttendedReadOnlyReviewPlanError("read-only review plan missing required rejected private artifacts")


def _validate_review_states(states: Sequence[Any]) -> tuple[set[str], int]:
    seen: set[str] = set()
    allowed_action_count = 0
    for index, state in enumerate(states):
        if not isinstance(state, Mapping):
            raise AttendedReadOnlyReviewPlanError(f"review_states[{index}] must be an object")
        state_id = _required_text(state, "state_id")
        review_state = _required_text(state, "review_state")
        if review_state not in REQUIRED_REVIEW_STATES:
            raise AttendedReadOnlyReviewPlanError(f"review state {state_id} is not an allowed attended read-only state")
        if review_state in seen:
            raise AttendedReadOnlyReviewPlanError(f"review state {review_state} is duplicated")
        seen.add(review_state)

        if state.get("redacted_values_only") is not True:
            raise AttendedReadOnlyReviewPlanError(f"review state {state_id} must contain redacted values only")
        if state.get("metadata_only") is not True:
            raise AttendedReadOnlyReviewPlanError(f"review state {state_id} must be metadata only")
        if state.get("changes_official_state") is not False:
            raise AttendedReadOnlyReviewPlanError(f"review state {state_id} must not change official state")
        if state.get("requires_manual_login_handoff") is not True:
            raise AttendedReadOnlyReviewPlanError(f"review state {state_id} must require manual login handoff")

        structure = _required_mapping(state, "accessible_structure")
        _validate_accessible_structure(state_id, structure)

        actions = _required_list(state, "allowed_read_only_actions")
        for action in actions:
            if not isinstance(action, Mapping):
                raise AttendedReadOnlyReviewPlanError(f"allowed action for {state_id} must be an object")
            action_id = _required_text(action, "action_id")
            action_kind = _required_text(action, "action_kind")
            if action_kind not in ALLOWED_READ_ONLY_ACTIONS:
                raise AttendedReadOnlyReviewPlanError(f"action {action_id} is not read-only")
            if action.get("may_touch_live_devhub") is not False:
                raise AttendedReadOnlyReviewPlanError(f"action {action_id} must not touch live DevHub in fixture validation")
            if action.get("records_private_values") is not False:
                raise AttendedReadOnlyReviewPlanError(f"action {action_id} must not record private values")
            allowed_action_count += 1

    missing = REQUIRED_REVIEW_STATES - seen
    if missing:
        raise AttendedReadOnlyReviewPlanError("read-only review plan missing required review states")
    return seen, allowed_action_count


def _validate_accessible_structure(state_id: str, structure: Mapping[str, Any]) -> None:
    if structure.get("source") != SOURCE_METADATA_KIND:
        raise AttendedReadOnlyReviewPlanError(f"accessible structure for {state_id} must be redacted accessible metadata")
    if structure.get("contains_raw_values") is not False:
        raise AttendedReadOnlyReviewPlanError(f"accessible structure for {state_id} must not contain raw values")
    if structure.get("contains_documents") is not False:
        raise AttendedReadOnlyReviewPlanError(f"accessible structure for {state_id} must not contain documents")
    landmarks = _required_list(structure, "landmarks")
    controls = _required_list(structure, "controls")
    labels = _required_list(structure, "redacted_labels")
    if not all(isinstance(item, str) and item.strip() for item in landmarks):
        raise AttendedReadOnlyReviewPlanError(f"accessible landmarks for {state_id} must be non-empty strings")
    if not all(isinstance(item, str) and item.strip() for item in labels):
        raise AttendedReadOnlyReviewPlanError(f"redacted labels for {state_id} must be non-empty strings")
    for control in controls:
        if not isinstance(control, Mapping):
            raise AttendedReadOnlyReviewPlanError(f"accessible controls for {state_id} must be objects")
        _required_text(control, "role")
        _required_text(control, "name")
        if control.get("selector_strategy") not in {"role", "accessible_name", "landmark"}:
            raise AttendedReadOnlyReviewPlanError(f"control for {state_id} must use accessible selector metadata")


def _validate_blocked_actions(actions: Sequence[Any]) -> None:
    seen: set[str] = set()
    for index, action in enumerate(actions):
        if not isinstance(action, Mapping):
            raise AttendedReadOnlyReviewPlanError(f"blocked_consequential_actions[{index}] must be an object")
        action_kind = _required_text(action, "action_kind")
        seen.add(action_kind)
        if action_kind not in REQUIRED_BLOCKED_ACTIONS:
            raise AttendedReadOnlyReviewPlanError(f"blocked action {action_kind} is not part of the read-only review boundary")
        if action.get("decision") != "refuse":
            raise AttendedReadOnlyReviewPlanError(f"blocked action {action_kind} must be refused")
        if action.get("blocked_until") != "manual_handoff_and_action_specific_confirmation":
            raise AttendedReadOnlyReviewPlanError(f"blocked action {action_kind} must require manual handoff and action-specific confirmation")
        if action.get("may_execute") is not False:
            raise AttendedReadOnlyReviewPlanError(f"blocked action {action_kind} must not execute")
    missing = REQUIRED_BLOCKED_ACTIONS - seen
    if missing:
        raise AttendedReadOnlyReviewPlanError("read-only review plan missing required blocked consequential actions")


def _required_mapping(value: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    item = value.get(key)
    if not isinstance(item, Mapping):
        raise AttendedReadOnlyReviewPlanError(f"{key} must be an object")
    return item


def _required_list(value: Mapping[str, Any], key: str) -> list[Any]:
    item = value.get(key)
    if not isinstance(item, list) or not item:
        raise AttendedReadOnlyReviewPlanError(f"{key} must be a non-empty array")
    return item


def _required_text(value: Mapping[str, Any], key: str) -> str:
    item = value.get(key)
    if not isinstance(item, str) or not item.strip():
        raise AttendedReadOnlyReviewPlanError(f"{key} must be a non-empty string")
    return item.strip()


def _reject_private_fields(value: Any, path: str) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if not isinstance(key, str):
                raise AttendedReadOnlyReviewPlanError(f"{path} contains a non-string field name")
            normalized = key.strip().lower().replace("-", "_")
            if normalized in FORBIDDEN_PRIVATE_FIELDS:
                raise AttendedReadOnlyReviewPlanError(f"forbidden private field at {path}.{key}")
            _reject_private_fields(child, f"{path}.{key}")
        return
    if isinstance(value, list):
        for index, child in enumerate(value):
            _reject_private_fields(child, f"{path}[{index}]")
        return
    if isinstance(value, str):
        lowered = value.lower()
        if any(marker in lowered for marker in FORBIDDEN_VALUE_MARKERS):
            raise AttendedReadOnlyReviewPlanError(f"forbidden private value marker at {path}")
