"""Fixture-first DevHub attended observation renewal queue builder.

This module is intentionally side-effect free. It consumes committed fixtures that
summarize known DevHub surfaces and guarded action policy, then emits read-only
observation candidates for attended review. It does not open DevHub, persist
browser/session artifacts, or perform official actions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


READ_ONLY_CLASSIFICATION = "safe_read_only"
CONSEQUENTIAL_CLASSIFICATION = "consequential_official"
REVERSIBLE_DRAFT_CLASSIFICATION = "reversible_draft"
UNKNOWN_CLASSIFICATION = "unknown_guarded_action"


@dataclass(frozen=True)
class QueueSource:
    """Names the source fixtures used to build a queue."""

    surface_map_fixture: str
    action_policy_fixture: str


def build_attended_observation_queue(
    surface_map: Mapping[str, Any],
    action_policy: Mapping[str, Any],
    *,
    source: QueueSource | None = None,
) -> dict[str, Any]:
    """Build an ordered, read-only attended observation queue from fixtures.

    Args:
        surface_map: DevHub surface-map fixture data.
        action_policy: Guarded action policy fixture data.
        source: Optional fixture names to carry into traceable output metadata.

    Returns:
        A deterministic dictionary suitable for tests, review, and later daemon
        validation. The output intentionally contains placeholders and policy
        references instead of private DevHub page values.
    """

    source = source or QueueSource(
        surface_map_fixture=str(surface_map.get("fixture_id", "surface-map-fixture")),
        action_policy_fixture=str(action_policy.get("fixture_id", "action-policy-fixture")),
    )
    policy_index = _policy_index(action_policy)
    rows: list[dict[str, Any]] = []
    blocked_reminders: list[dict[str, Any]] = []

    surfaces = sorted(
        _as_list(surface_map.get("surfaces")),
        key=lambda item: (
            str(item.get("observation_order", item.get("surface_id", ""))),
            str(item.get("surface_id", "")),
        ),
    )

    for surface in surfaces:
        surface_id = _required_string(surface, "surface_id")
        redaction_refs = _redaction_refs(surface, action_policy)
        actions = sorted(
            _as_list(surface.get("actions")),
            key=lambda item: (
                str(item.get("observation_order", item.get("action_id", ""))),
                str(item.get("action_id", "")),
            ),
        )
        for action in actions:
            classification = _classify_action(action, policy_index)
            action_id = _required_string(action, "action_id")
            if classification == READ_ONLY_CLASSIFICATION:
                rows.append(
                    _candidate_row(
                        order=len(rows) + 1,
                        surface=surface,
                        action=action,
                        classification=classification,
                        redaction_refs=redaction_refs,
                        source=source,
                    )
                )
            else:
                blocked_reminders.append(
                    _blocked_reminder(
                        surface=surface,
                        action=action,
                        classification=classification,
                        redaction_refs=redaction_refs,
                        source=source,
                    )
                )

    return {
        "schema_version": "devhub.attended_observation_queue.v1",
        "queue_id": str(surface_map.get("queue_id", "devhub-attended-observation-renewal-v1")),
        "mode": "fixture_first_read_only_observation",
        "source_fixture_refs": {
            "surface_map": source.surface_map_fixture,
            "guarded_action_policy": source.action_policy_fixture,
        },
        "artifact_policy": {
            "opens_devhub": False,
            "stores_session_or_auth_state": False,
            "stores_browser_artifacts": False,
            "stores_screenshots_traces_or_har": False,
            "stores_private_page_values": False,
            "changes_prompts": False,
            "performs_official_actions": False,
        },
        "attendance_preflight_template": _attendance_preflight_template(action_policy),
        "candidate_rows": rows,
        "blocked_consequential_action_reminders": blocked_reminders,
        "reviewer_approval_placeholder": {
            "required_before_live_use": True,
            "status": "pending_reviewer_approval",
            "reviewer": None,
            "approved_at": None,
            "notes": None,
        },
    }


def _candidate_row(
    *,
    order: int,
    surface: Mapping[str, Any],
    action: Mapping[str, Any],
    classification: str,
    redaction_refs: list[str],
    source: QueueSource,
) -> dict[str, Any]:
    surface_id = _required_string(surface, "surface_id")
    action_id = _required_string(action, "action_id")
    return {
        "queue_row_id": f"observe-{order:03d}-{surface_id}-{action_id}",
        "order": order,
        "candidate_kind": "read_only_observation",
        "surface": {
            "surface_id": surface_id,
            "auth_scope": str(surface.get("auth_scope", "authenticated_attended")),
            "url_pattern": str(surface.get("url_pattern", "redacted-fixture-url-pattern")),
            "page_heading": str(surface.get("page_heading", "")),
            "accessible_landmarks": [str(item) for item in _as_list(surface.get("accessible_landmarks"))],
            "requires_attendance": bool(surface.get("requires_attendance", True)),
            "requires_exact_confirmation": bool(surface.get("requires_exact_confirmation", False)),
        },
        "action": {
            "action_id": action_id,
            "label": str(action.get("label", action_id)),
            "classification": classification,
            "allowed_in_observation_queue": True,
            "allowed_effect": "observe_visible_structure_only",
            "official_action_block": None,
        },
        "attendance_preflight": {
            "status": "placeholder_pending_attended_run",
            "manual_login_required": True,
            "browser_must_be_user_visible": True,
            "operator_must_be_present": True,
            "no_credential_collection": True,
            "no_session_or_auth_state_storage": True,
            "no_screenshots_traces_har_or_raw_private_values": True,
        },
        "redaction_checklist_refs": redaction_refs,
        "reviewer_approval_placeholder": {
            "required_before_live_use": True,
            "status": "pending_reviewer_approval",
            "reviewer": None,
            "approved_at": None,
        },
        "source_fixture_refs": {
            "surface_map": source.surface_map_fixture,
            "guarded_action_policy": source.action_policy_fixture,
        },
    }


def _blocked_reminder(
    *,
    surface: Mapping[str, Any],
    action: Mapping[str, Any],
    classification: str,
    redaction_refs: list[str],
    source: QueueSource,
) -> dict[str, Any]:
    return {
        "surface_id": _required_string(surface, "surface_id"),
        "action_id": _required_string(action, "action_id"),
        "label": str(action.get("label", action.get("action_id", ""))),
        "classification": classification,
        "not_added_to_candidate_rows": True,
        "blocked_reason": _blocked_reason(classification),
        "requires_attendance": True,
        "requires_exact_confirmation": True,
        "redaction_checklist_refs": redaction_refs,
        "source_fixture_refs": {
            "surface_map": source.surface_map_fixture,
            "guarded_action_policy": source.action_policy_fixture,
        },
    }


def _policy_index(action_policy: Mapping[str, Any]) -> dict[str, str]:
    index: dict[str, str] = {}
    groups = {
        READ_ONLY_CLASSIFICATION: action_policy.get("safe_read_only_actions", []),
        REVERSIBLE_DRAFT_CLASSIFICATION: action_policy.get("reversible_draft_actions", []),
        CONSEQUENTIAL_CLASSIFICATION: action_policy.get("consequential_official_actions", []),
    }
    for classification, actions in groups.items():
        for action in _as_list(actions):
            if isinstance(action, str):
                index[action] = classification
            elif isinstance(action, Mapping):
                action_id = action.get("action_id")
                if action_id:
                    index[str(action_id)] = classification
    return index


def _classify_action(action: Mapping[str, Any], policy_index: Mapping[str, str]) -> str:
    explicit = action.get("classification")
    if explicit:
        return str(explicit)
    action_id = _required_string(action, "action_id")
    return policy_index.get(action_id, UNKNOWN_CLASSIFICATION)


def _redaction_refs(surface: Mapping[str, Any], action_policy: Mapping[str, Any]) -> list[str]:
    refs = [str(item) for item in _as_list(surface.get("redaction_checklist_refs"))]
    if refs:
        return refs
    defaults = action_policy.get("default_redaction_checklist_refs", [])
    return [str(item) for item in _as_list(defaults)]


def _attendance_preflight_template(action_policy: Mapping[str, Any]) -> dict[str, Any]:
    template = action_policy.get("attendance_preflight_template", {})
    if not isinstance(template, Mapping):
        template = {}
    return {
        "manual_login_required": bool(template.get("manual_login_required", True)),
        "browser_must_be_user_visible": bool(template.get("browser_must_be_user_visible", True)),
        "operator_must_be_present": bool(template.get("operator_must_be_present", True)),
        "no_credential_collection": bool(template.get("no_credential_collection", True)),
        "no_session_or_auth_state_storage": bool(template.get("no_session_or_auth_state_storage", True)),
        "no_screenshots_traces_har_or_raw_private_values": bool(
            template.get("no_screenshots_traces_har_or_raw_private_values", True)
        ),
    }


def _blocked_reason(classification: str) -> str:
    if classification == CONSEQUENTIAL_CLASSIFICATION:
        return "Consequential official DevHub action requires attended, informed, exact confirmation and is outside the read-only observation queue."
    if classification == REVERSIBLE_DRAFT_CLASSIFICATION:
        return "Reversible draft action is not read-only and is excluded from observation renewal candidates."
    return "Action is not classified as safe read-only by the guarded action policy fixture."


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _required_string(mapping: Mapping[str, Any], key: str) -> str:
    value = mapping.get(key)
    if not value:
        raise ValueError(f"Missing required fixture field: {key}")
    return str(value)
