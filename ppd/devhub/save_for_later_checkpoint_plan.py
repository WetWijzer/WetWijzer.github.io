"""Fixture-first validation for attended DevHub save-for-later checkpoints.

The validator is side-effect free. It is intended for committed synthetic
fixtures that describe a planned attended DevHub save-for-later checkpoint
without launching a browser, storing auth state, or touching DevHub.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence


PLAN_VERSION = "devhub-save-for-later-checkpoint-plan-v1"
RUN_MODE = "fixture_first_attended_devhub_save_for_later_checkpoint"
REQUIRED_CHECKPOINT_KINDS = {"reversible_field_entry", "save_for_later_control"}
REQUIRED_EXCLUDED_ACTIONS = {
    "upload",
    "submission",
    "certification",
    "inspection_scheduling",
    "cancellation",
    "payment_detail_entry",
    "final_payment_execution",
}
ALLOWED_SELECTOR_STRATEGIES = {"accessible_role", "label_text", "test_fixture_accessible_tree"}
ALLOWED_JOURNAL_EVENT_TYPES = {
    "DevHub attended preflight",
    "reversible draft plan",
    "DevHub attempted action",
    "exact-confirmation checkpoint",
    "manual handoff",
    "refused action",
}
FORBIDDEN_KEYS = {
    "auth_state",
    "captcha",
    "cookie",
    "cookies",
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
    "upload_path",
}
PRIVATE_ARTIFACT_POLICY_KEYS = {
    "stores_auth_state",
    "stores_cookies",
    "stores_screenshots",
    "stores_traces",
    "stores_har",
    "stores_downloads",
    "stores_private_uploads",
    "captures_payment_detail_entry",
}


class SaveForLaterCheckpointPlanError(ValueError):
    """Raised when a save-for-later checkpoint fixture is unsafe."""


@dataclass(frozen=True)
class SaveForLaterCheckpointPlanResult:
    plan_id: str
    checkpoint_count: int
    source_evidence_count: int
    excluded_action_count: int
    journal_expectation_count: int


def load_plan(path: str | Path) -> Mapping[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise SaveForLaterCheckpointPlanError("checkpoint plan fixture must be a JSON object")
    return payload


def validate_plan_file(path: str | Path) -> SaveForLaterCheckpointPlanResult:
    return validate_plan(load_plan(path))


def validate_plan(plan: Mapping[str, Any]) -> SaveForLaterCheckpointPlanResult:
    _reject_forbidden_keys(plan, "plan")
    _validate_header(plan)
    _validate_browser_artifact_policy(_required_mapping(plan, "browser_artifact_policy"))
    evidence_ids = _validate_source_evidence(_required_list(plan, "source_evidence"))
    _validate_manual_attendance(_required_mapping(plan, "manual_attendance"))
    checkpoint_kinds = _validate_checkpoints(_required_list(plan, "checkpoints"), evidence_ids)
    if REQUIRED_CHECKPOINT_KINDS - checkpoint_kinds:
        raise SaveForLaterCheckpointPlanError("checkpoint plan must include field entry and save-for-later control checkpoints")
    excluded_count = _validate_excluded_actions(_required_list(plan, "excluded_actions"))
    journal_count = _validate_action_journal_expectations(
        _required_list(plan, "action_journal_expectations"), evidence_ids
    )
    return SaveForLaterCheckpointPlanResult(
        plan_id=_required_text(plan, "plan_id"),
        checkpoint_count=len(checkpoint_kinds),
        source_evidence_count=len(evidence_ids),
        excluded_action_count=excluded_count,
        journal_expectation_count=journal_count,
    )


def _validate_header(plan: Mapping[str, Any]) -> None:
    if plan.get("plan_version") != PLAN_VERSION:
        raise SaveForLaterCheckpointPlanError("plan_version is not supported")
    if plan.get("run_mode") != RUN_MODE:
        raise SaveForLaterCheckpointPlanError("run_mode must be fixture-first attended save-for-later")
    if plan.get("live_devhub_session") is not False:
        raise SaveForLaterCheckpointPlanError("committed fixtures must not require a live DevHub session")
    if plan.get("browser_launched") is not False:
        raise SaveForLaterCheckpointPlanError("checkpoint fixture validation must not launch a browser")
    if plan.get("auth_state_saved") is not False:
        raise SaveForLaterCheckpointPlanError("checkpoint fixtures must not save auth state")


def _validate_browser_artifact_policy(policy: Mapping[str, Any]) -> None:
    for key in PRIVATE_ARTIFACT_POLICY_KEYS:
        if policy.get(key) is not False:
            raise SaveForLaterCheckpointPlanError(f"browser_artifact_policy.{key} must be false")
    if policy.get("committed_artifacts") != "none":
        raise SaveForLaterCheckpointPlanError("browser_artifact_policy.committed_artifacts must be none")


def _validate_source_evidence(items: Sequence[Any]) -> set[str]:
    evidence_ids: set[str] = set()
    for index, item in enumerate(items):
        if not isinstance(item, Mapping):
            raise SaveForLaterCheckpointPlanError(f"source_evidence[{index}] must be an object")
        evidence_id = _required_text(item, "evidence_id")
        if evidence_id in evidence_ids:
            raise SaveForLaterCheckpointPlanError(f"duplicate source evidence id {evidence_id}")
        evidence_ids.add(evidence_id)
        _required_text(item, "source_url")
        _required_text(item, "source_type")
        _required_text(item, "supports_checkpoint")
    return evidence_ids


def _validate_manual_attendance(attendance: Mapping[str, Any]) -> None:
    required_true = ("requires_user_present", "requires_attended_browser", "user_operates_login")
    for key in required_true:
        if attendance.get(key) is not True:
            raise SaveForLaterCheckpointPlanError(f"manual_attendance.{key} must be true")
    required_false = ("automation_performs_login", "automation_handles_mfa", "automation_handles_captcha")
    for key in required_false:
        if attendance.get(key) is not False:
            raise SaveForLaterCheckpointPlanError(f"manual_attendance.{key} must be false")
    _validate_manual_login_handoff(_required_mapping(attendance, "manual_login_handoff"))


def _validate_manual_login_handoff(handoff: Mapping[str, Any]) -> None:
    required_true = ("handoff_required", "user_completes_login", "credentials_not_collected", "mfa_captcha_user_only")
    for key in required_true:
        if handoff.get(key) is not True:
            raise SaveForLaterCheckpointPlanError(f"manual_login_handoff.{key} must be true")
    if handoff.get("automation_resumes_after_user_attendance") is not True:
        raise SaveForLaterCheckpointPlanError("manual_login_handoff.automation_resumes_after_user_attendance must be true")
    if handoff.get("automation_creates_account") is not False:
        raise SaveForLaterCheckpointPlanError("manual_login_handoff.automation_creates_account must be false")
    _required_text(handoff, "handoff_instruction")


def _validate_checkpoints(items: Sequence[Any], evidence_ids: set[str]) -> set[str]:
    kinds: set[str] = set()
    checkpoint_ids: set[str] = set()
    for index, item in enumerate(items):
        if not isinstance(item, Mapping):
            raise SaveForLaterCheckpointPlanError(f"checkpoints[{index}] must be an object")
        checkpoint_id = _required_text(item, "checkpoint_id")
        if checkpoint_id in checkpoint_ids:
            raise SaveForLaterCheckpointPlanError(f"duplicate checkpoint id {checkpoint_id}")
        checkpoint_ids.add(checkpoint_id)
        kind = _required_text(item, "checkpoint_kind")
        if kind not in REQUIRED_CHECKPOINT_KINDS:
            raise SaveForLaterCheckpointPlanError(f"unsupported checkpoint kind {kind}")
        kinds.add(kind)
        if item.get("requires_manual_attendance") is not True:
            raise SaveForLaterCheckpointPlanError(f"checkpoint {checkpoint_id} must require manual attendance")
        if item.get("changes_official_state") is not False:
            raise SaveForLaterCheckpointPlanError(f"checkpoint {checkpoint_id} must not change official state")
        if item.get("requires_official_confirmation") is not False:
            raise SaveForLaterCheckpointPlanError(f"checkpoint {checkpoint_id} must not be an official confirmation")
        _validate_evidence_refs(item, evidence_ids, f"checkpoint {checkpoint_id}")
        _validate_selector_metadata(_required_mapping(item, "selector_metadata"), checkpoint_id)
        _validate_preview_metadata(_required_mapping(item, "preview_metadata"), evidence_ids, checkpoint_id)
        if kind == "reversible_field_entry":
            if item.get("allowed_action") != "enter_redacted_field_value":
                raise SaveForLaterCheckpointPlanError("field-entry checkpoint must only allow redacted field entry")
            if item.get("uses_save_for_later_control") is not False:
                raise SaveForLaterCheckpointPlanError("field-entry checkpoint must not use the save-for-later control")
        if kind == "save_for_later_control":
            if item.get("allowed_action") != "activate_save_for_later_control":
                raise SaveForLaterCheckpointPlanError("save-for-later checkpoint must only activate save-for-later")
            if item.get("enters_field_values") is not False:
                raise SaveForLaterCheckpointPlanError("save-for-later checkpoint must not enter field values")
    return kinds


def _validate_selector_metadata(metadata: Mapping[str, Any], checkpoint_id: str) -> None:
    _required_text(metadata, "selector_id")
    _required_text(metadata, "role")
    _required_text(metadata, "accessible_name")
    strategy = _required_text(metadata, "selector_strategy")
    if strategy not in ALLOWED_SELECTOR_STRATEGIES:
        raise SaveForLaterCheckpointPlanError(f"selector metadata for {checkpoint_id} uses unsupported selector strategy")
    if metadata.get("selector_confidence") != "high":
        raise SaveForLaterCheckpointPlanError(f"selector metadata for {checkpoint_id} must be high confidence")
    if metadata.get("matched_element_count") != 1:
        raise SaveForLaterCheckpointPlanError(f"selector metadata for {checkpoint_id} must match exactly one element")
    if metadata.get("ambiguous_matches") != 0:
        raise SaveForLaterCheckpointPlanError(f"selector metadata for {checkpoint_id} must reject ambiguous selectors")
    if metadata.get("selector_unique") is not True:
        raise SaveForLaterCheckpointPlanError(f"selector metadata for {checkpoint_id} must be unique")
    forbidden_true = ("uses_positional_selector", "uses_private_dom", "uses_text_only_selector")
    for key in forbidden_true:
        if metadata.get(key) is not False:
            raise SaveForLaterCheckpointPlanError(f"selector metadata for {checkpoint_id} has unsafe {key}")


def _validate_preview_metadata(metadata: Mapping[str, Any], evidence_ids: set[str], checkpoint_id: str) -> None:
    _required_text(metadata, "preview_id")
    if metadata.get("redacted") is not True:
        raise SaveForLaterCheckpointPlanError(f"preview metadata for {checkpoint_id} must be redacted")
    if metadata.get("contains_private_values") is not False:
        raise SaveForLaterCheckpointPlanError(f"preview metadata for {checkpoint_id} must not contain private values")
    if metadata.get("may_touch_live_devhub") is not False:
        raise SaveForLaterCheckpointPlanError(f"preview metadata for {checkpoint_id} must not touch live DevHub")
    _validate_evidence_refs(metadata, evidence_ids, f"preview metadata for {checkpoint_id}")


def _validate_excluded_actions(items: Sequence[Any]) -> int:
    seen: set[str] = set()
    for index, item in enumerate(items):
        if not isinstance(item, Mapping):
            raise SaveForLaterCheckpointPlanError(f"excluded_actions[{index}] must be an object")
        action_class = _required_text(item, "action_class")
        seen.add(action_class)
        if item.get("decision") != "exclude":
            raise SaveForLaterCheckpointPlanError(f"excluded action {action_class} must use exclude decision")
        if item.get("may_execute") is not False:
            raise SaveForLaterCheckpointPlanError(f"excluded action {action_class} must not execute")
        if item.get("requires_separate_exact_confirmation") is not True:
            raise SaveForLaterCheckpointPlanError(f"excluded action {action_class} must require separate exact confirmation")
    missing = REQUIRED_EXCLUDED_ACTIONS - seen
    if missing:
        raise SaveForLaterCheckpointPlanError("excluded_actions missing required consequential action classes")
    return len(items)


def _validate_action_journal_expectations(items: Sequence[Any], evidence_ids: set[str]) -> int:
    for index, item in enumerate(items):
        if not isinstance(item, Mapping):
            raise SaveForLaterCheckpointPlanError(f"action_journal_expectations[{index}] must be an object")
        event_type = _required_text(item, "event_type")
        if event_type not in ALLOWED_JOURNAL_EVENT_TYPES:
            raise SaveForLaterCheckpointPlanError(f"journal event type {event_type} is not allowed")
        if item.get("redacted") is not True:
            raise SaveForLaterCheckpointPlanError("journal expectations must be redacted")
        if item.get("contains_private_values") is not False:
            raise SaveForLaterCheckpointPlanError("journal expectations must not contain private values")
        _required_text(item, "expected_message")
        _validate_evidence_refs(item, evidence_ids, f"journal expectation {index}")
    return len(items)


def _validate_evidence_refs(item: Mapping[str, Any], evidence_ids: set[str], context: str) -> None:
    refs = _required_list(item, "source_evidence_ids")
    for ref in refs:
        if ref not in evidence_ids:
            raise SaveForLaterCheckpointPlanError(f"{context} references unknown source evidence id")


def _required_mapping(value: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    item = value.get(key)
    if not isinstance(item, Mapping):
        raise SaveForLaterCheckpointPlanError(f"{key} must be an object")
    return item


def _required_list(value: Mapping[str, Any], key: str) -> list[Any]:
    item = value.get(key)
    if not isinstance(item, list) or not item:
        raise SaveForLaterCheckpointPlanError(f"{key} must be a non-empty array")
    return item


def _required_text(value: Mapping[str, Any], key: str) -> str:
    item = value.get(key)
    if not isinstance(item, str) or not item.strip():
        raise SaveForLaterCheckpointPlanError(f"{key} must be a non-empty string")
    return item


def _reject_forbidden_keys(value: Any, path: str) -> None:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            key_text = str(key)
            if key_text in FORBIDDEN_KEYS:
                raise SaveForLaterCheckpointPlanError(f"forbidden private field at {path}.{key_text}")
            _reject_forbidden_keys(nested, f"{path}.{key_text}")
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            _reject_forbidden_keys(nested, f"{path}[{index}]")
