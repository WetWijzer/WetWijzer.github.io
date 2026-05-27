"""Validate fixture-first attended DevHub reversible draft plans.

This module is intentionally deterministic and side-effect free. It validates
committed synthetic fixtures that describe address/property search, permit-type
selection, form field entry, and save-for-later planning without launching a
browser, storing auth state, or touching DevHub.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence


class ReversibleDraftPlanError(ValueError):
    """Raised when a reversible draft plan fixture is unsafe or incomplete."""


@dataclass(frozen=True)
class ReversibleDraftPlanResult:
    plan_id: str
    step_count: int
    case_fact_count: int
    surface_fixture_count: int
    source_evidence_count: int
    blocked_action_count: int
    step_kinds: tuple[str, ...]


PLAN_VERSION = "devhub-attended-reversible-draft-plan-v1"
RUN_MODE = "fixture_first_attended_devhub_reversible_draft"
REQUIRED_STEP_KINDS = {
    "address_property_search",
    "permit_type_selection",
    "form_field_entry",
    "save_for_later",
}
REQUIRED_LOGIN_PREREQUISITES = {
    "user_owned_devhub_account",
    "user_present_at_browser",
    "manual_login_completed_before_draft",
    "no_credentials_persisted",
}
ALLOWED_ACTION_CLASSES = {"read_only", "reversible_draft"}
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
REQUIRED_BLOCKED_CLASSES = {
    "account_creation_automation",
    "captcha_automation",
    "certification",
    "final_payment_execution",
    "login_automation",
    "mfa_automation",
    "official_upload",
    "payment_detail_entry",
    "submission",
}


def load_plan(path: str | Path) -> Mapping[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ReversibleDraftPlanError("reversible draft plan fixture must be a JSON object")
    return payload


def validate_plan_file(path: str | Path) -> ReversibleDraftPlanResult:
    return validate_plan(load_plan(path))


def validate_plan(plan: Mapping[str, Any]) -> ReversibleDraftPlanResult:
    _reject_private_fields(plan, "plan")
    _validate_header(plan)

    evidence_ids = _validate_source_evidence(_required_list(plan, "source_evidence"))
    _validate_manual_login_handoff(_required_mapping(plan, "manual_login_handoff"))
    case_fact_ids = _validate_case_facts(_required_list(plan, "synthetic_case_facts"), evidence_ids)
    surface_ids = _validate_surface_fixtures(_required_list(plan, "accessible_structure_fixtures"), evidence_ids)
    step_kinds = _validate_steps(_required_list(plan, "workflow_steps"), evidence_ids, case_fact_ids, surface_ids)
    blocked_count = _validate_blocked_actions(_required_list(plan, "blocked_actions"))

    missing_steps = REQUIRED_STEP_KINDS - step_kinds
    if missing_steps:
        raise ReversibleDraftPlanError("workflow_steps missing required reversible draft coverage")

    return ReversibleDraftPlanResult(
        plan_id=_required_text(plan, "plan_id"),
        step_count=len(step_kinds),
        case_fact_count=len(case_fact_ids),
        surface_fixture_count=len(surface_ids),
        source_evidence_count=len(evidence_ids),
        blocked_action_count=blocked_count,
        step_kinds=tuple(sorted(step_kinds)),
    )


def _validate_header(plan: Mapping[str, Any]) -> None:
    if plan.get("plan_version") != PLAN_VERSION:
        raise ReversibleDraftPlanError("plan_version must be devhub-attended-reversible-draft-plan-v1")
    if plan.get("run_mode") != RUN_MODE:
        raise ReversibleDraftPlanError("run_mode must be fixture_first_attended_devhub_reversible_draft")
    if plan.get("live_devhub_session") is not False:
        raise ReversibleDraftPlanError("live_devhub_session must be false for committed fixtures")
    if plan.get("browser_launched") is not False:
        raise ReversibleDraftPlanError("browser_launched must be false for fixture validation")
    if plan.get("auth_state_saved") is not False:
        raise ReversibleDraftPlanError("auth_state_saved must be false for committed fixtures")


def _validate_source_evidence(items: Sequence[Any]) -> set[str]:
    evidence_ids: set[str] = set()
    for index, item in enumerate(items):
        if not isinstance(item, Mapping):
            raise ReversibleDraftPlanError(f"source_evidence[{index}] must be an object")
        evidence_id = _required_text(item, "evidence_id")
        if evidence_id in evidence_ids:
            raise ReversibleDraftPlanError(f"duplicate source evidence id {evidence_id}")
        evidence_ids.add(evidence_id)
        _required_text(item, "source_url")
        _required_text(item, "source_type")
        _required_text(item, "summary")
    return evidence_ids


def _validate_manual_login_handoff(handoff: Mapping[str, Any]) -> None:
    if handoff.get("requires_user_present") is not True:
        raise ReversibleDraftPlanError("manual_login_handoff must require the user to be present")
    if handoff.get("user_completes_login") is not True:
        raise ReversibleDraftPlanError("manual_login_handoff must leave login to the user")
    if handoff.get("automation_performs_login") is not False:
        raise ReversibleDraftPlanError("automation must not perform DevHub login")
    if handoff.get("stores_credentials") is not False:
        raise ReversibleDraftPlanError("manual_login_handoff must not store credentials")
    prerequisites = _required_list(handoff, "prerequisites")
    missing = REQUIRED_LOGIN_PREREQUISITES - {str(item) for item in prerequisites}
    if missing:
        raise ReversibleDraftPlanError("manual_login_handoff missing required prerequisites")


def _validate_case_facts(items: Sequence[Any], evidence_ids: set[str]) -> set[str]:
    fact_ids: set[str] = set()
    for index, item in enumerate(items):
        if not isinstance(item, Mapping):
            raise ReversibleDraftPlanError(f"synthetic_case_facts[{index}] must be an object")
        fact_id = _required_text(item, "fact_id")
        if fact_id in fact_ids:
            raise ReversibleDraftPlanError(f"duplicate synthetic case fact id {fact_id}")
        fact_ids.add(fact_id)
        if item.get("value_class") != "synthetic":
            raise ReversibleDraftPlanError(f"case fact {fact_id} must be synthetic")
        token = _required_text(item, "value_token")
        if not token.startswith("synthetic_"):
            raise ReversibleDraftPlanError(f"case fact {fact_id} must use a synthetic value token")
        _validate_evidence_refs(item, evidence_ids, f"case fact {fact_id}")
    return fact_ids


def _validate_surface_fixtures(items: Sequence[Any], evidence_ids: set[str]) -> set[str]:
    surface_ids: set[str] = set()
    for index, item in enumerate(items):
        if not isinstance(item, Mapping):
            raise ReversibleDraftPlanError(f"accessible_structure_fixtures[{index}] must be an object")
        fixture_id = _required_text(item, "fixture_id")
        if fixture_id in surface_ids:
            raise ReversibleDraftPlanError(f"duplicate accessible structure fixture id {fixture_id}")
        surface_ids.add(fixture_id)
        if item.get("redaction") != "accessible_structure_only":
            raise ReversibleDraftPlanError(f"surface fixture {fixture_id} must be redacted accessible structure only")
        if item.get("contains_private_values") is not False:
            raise ReversibleDraftPlanError(f"surface fixture {fixture_id} must not contain private values")
        _required_list(item, "landmarks")
        _required_list(item, "controls")
        _validate_evidence_refs(item, evidence_ids, f"surface fixture {fixture_id}")
    return surface_ids


def _validate_steps(
    items: Sequence[Any],
    evidence_ids: set[str],
    fact_ids: set[str],
    surface_ids: set[str],
) -> set[str]:
    step_kinds: set[str] = set()
    for index, item in enumerate(items):
        if not isinstance(item, Mapping):
            raise ReversibleDraftPlanError(f"workflow_steps[{index}] must be an object")
        step_id = _required_text(item, "step_id")
        step_kind = _required_text(item, "step_kind")
        step_kinds.add(step_kind)
        if step_kind not in REQUIRED_STEP_KINDS:
            raise ReversibleDraftPlanError(f"workflow step {step_id} has unsupported step_kind")
        if _required_text(item, "action_class") not in ALLOWED_ACTION_CLASSES:
            raise ReversibleDraftPlanError(f"workflow step {step_id} must be read-only or reversible draft")
        if item.get("reversible") is not True:
            raise ReversibleDraftPlanError(f"workflow step {step_id} must be reversible")
        if item.get("changes_official_state") is not False:
            raise ReversibleDraftPlanError(f"workflow step {step_id} must not change official state")
        if item.get("requires_manual_login_handoff") is not True:
            raise ReversibleDraftPlanError(f"workflow step {step_id} must require manual-login handoff")
        if _required_text(item, "surface_fixture_id") not in surface_ids:
            raise ReversibleDraftPlanError(f"workflow step {step_id} references unknown surface fixture")
        _validate_evidence_refs(item, evidence_ids, f"workflow step {step_id}")
        _validate_preview_metadata(_required_mapping(item, "preview_metadata"), evidence_ids, step_id)
        for fact_id in item.get("uses_case_fact_ids", []):
            if fact_id not in fact_ids:
                raise ReversibleDraftPlanError(f"workflow step {step_id} references unknown case fact")
        if step_kind == "form_field_entry":
            _validate_form_fields(_required_list(item, "field_entries"), fact_ids, step_id)
        if step_kind == "save_for_later" and item.get("action_kind") != "save_for_later_draft":
            raise ReversibleDraftPlanError("save_for_later step must use save_for_later_draft action_kind")
    return step_kinds


def _validate_preview_metadata(metadata: Mapping[str, Any], evidence_ids: set[str], step_id: str) -> None:
    _required_text(metadata, "preview_id")
    _required_text(metadata, "preview_kind")
    if metadata.get("contains_private_values") is not False:
        raise ReversibleDraftPlanError(f"preview metadata for {step_id} must not contain private values")
    if metadata.get("may_touch_live_devhub") is not False:
        raise ReversibleDraftPlanError(f"preview metadata for {step_id} must not touch live DevHub")
    _validate_evidence_refs(metadata, evidence_ids, f"preview metadata for {step_id}")


def _validate_form_fields(items: Sequence[Any], fact_ids: set[str], step_id: str) -> None:
    for index, item in enumerate(items):
        if not isinstance(item, Mapping):
            raise ReversibleDraftPlanError(f"field_entries[{index}] for {step_id} must be an object")
        _required_text(item, "field_id")
        fact_id = _required_text(item, "case_fact_id")
        if fact_id not in fact_ids:
            raise ReversibleDraftPlanError(f"field entry for {step_id} references unknown case fact")
        if item.get("field_value_redacted") is not True:
            raise ReversibleDraftPlanError(f"field entry for {step_id} must redact the field value")


def _validate_blocked_actions(items: Sequence[Any]) -> int:
    blocked_classes: set[str] = set()
    for index, item in enumerate(items):
        if not isinstance(item, Mapping):
            raise ReversibleDraftPlanError(f"blocked_actions[{index}] must be an object")
        action_class = _required_text(item, "action_class")
        blocked_classes.add(action_class)
        if item.get("decision") != "refuse":
            raise ReversibleDraftPlanError(f"blocked action {action_class} must be refused")
        if item.get("may_execute") is not False:
            raise ReversibleDraftPlanError(f"blocked action {action_class} must not execute")
        if item.get("requires_exact_confirmation") is not True:
            raise ReversibleDraftPlanError(f"blocked action {action_class} must require exact confirmation")
    if REQUIRED_BLOCKED_CLASSES - blocked_classes:
        raise ReversibleDraftPlanError("blocked_actions missing required consequential action classes")
    return len(items)


def _validate_evidence_refs(item: Mapping[str, Any], evidence_ids: set[str], context: str) -> None:
    refs = _required_list(item, "source_evidence_ids")
    for ref in refs:
        if ref not in evidence_ids:
            raise ReversibleDraftPlanError(f"{context} references unknown source evidence id")


def _required_mapping(value: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    item = value.get(key)
    if not isinstance(item, Mapping):
        raise ReversibleDraftPlanError(f"{key} must be an object")
    return item


def _required_list(value: Mapping[str, Any], key: str) -> list[Any]:
    item = value.get(key)
    if not isinstance(item, list) or not item:
        raise ReversibleDraftPlanError(f"{key} must be a non-empty array")
    return item


def _required_text(value: Mapping[str, Any], key: str) -> str:
    item = value.get(key)
    if not isinstance(item, str) or not item.strip():
        raise ReversibleDraftPlanError(f"{key} must be a non-empty string")
    return item


def _reject_private_fields(value: Any, path: str) -> None:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            key_text = str(key)
            if key_text in FORBIDDEN_PRIVATE_FIELDS:
                raise ReversibleDraftPlanError(f"forbidden private field at {path}.{key_text}")
            _reject_private_fields(nested, f"{path}.{key_text}")
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            _reject_private_fields(nested, f"{path}[{index}]")
