"""Fixture-first DevHub read-only observation promotion plan v1.

This module consumes approved reviewer disposition ledger items and DevHub
manual observation reviewer queue items, then emits synthetic surface-map fixture
update proposals. It is offline-only and does not launch browsers, log in, click
through DevHub, upload files, submit forms, schedule inspections, process
payments, or persist private browser artifacts.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence

from ppd.agent_readiness.reviewer_disposition_ledger_v1 import (
    assert_valid_reviewer_disposition_ledger_v1,
)

PLAN_VERSION = "devhub_read_only_observation_promotion_plan_v1"
PLAN_MODE = "fixture_first_synthetic_surface_map_update_proposals"

REQUIRED_ATTESTATIONS: tuple[str, ...] = (
    "no-login-automation",
    "no-session-state",
    "no-screenshot",
    "no-trace",
    "no-HAR",
    "no-click-through",
    "no-upload",
    "no-submit",
    "no-payment",
    "no-scheduling",
)

ATTESTATION_ALIASES: Mapping[str, str] = {
    "no_login_automation": "no-login-automation",
    "no_session_state": "no-session-state",
    "no_screenshot": "no-screenshot",
    "no_trace": "no-trace",
    "no_har": "no-HAR",
    "no_click_through": "no-click-through",
    "no_upload": "no-upload",
    "no_submit": "no-submit",
    "no_payment": "no-payment",
    "no_scheduling": "no-scheduling",
}

FORBIDDEN_KEYS: tuple[str, ...] = (
    "auth_state",
    "browser_state",
    "cookie",
    "credential",
    "har",
    "password",
    "private_value",
    "raw_authenticated_value",
    "screenshot",
    "session_state",
    "storage_state",
    "trace",
)

FORBIDDEN_TEXT: tuple[str, ...] = (
    "auth_state.json",
    "storage_state.json",
    "trace.zip",
    ".har",
    ".png",
    ".jpg",
    ".jpeg",
    "click submit",
    "submit the application",
    "upload the plans",
    "pay the fee",
    "schedule the inspection",
    "automate login",
    "solve captcha",
    "complete mfa",
)

SAFE_PREFIXES: tuple[str, ...] = (
    "do not ",
    "no ",
    "stop before ",
    "must not ",
    "blocked before ",
    "refuse ",
)


@dataclass(frozen=True)
class PromotionPlanError(ValueError):
    """Raised when fixture inputs cannot produce a safe promotion plan."""

    message: str

    def __str__(self) -> str:
        return self.message


def build_read_only_observation_promotion_plan_v1(
    reviewer_disposition_ledger: Mapping[str, Any],
    manual_observation_reviewer_queue: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Build synthetic surface-map fixture update proposals from approved inputs."""

    assert_valid_reviewer_disposition_ledger_v1(reviewer_disposition_ledger)
    _scan_commit_safe(reviewer_disposition_ledger, "reviewer_disposition_ledger")
    _scan_commit_safe(manual_observation_reviewer_queue, "manual_observation_reviewer_queue")

    dispositions = _approved_dispositions_by_surface(reviewer_disposition_ledger)
    if not manual_observation_reviewer_queue:
        raise PromotionPlanError("manual observation reviewer queue must not be empty")

    proposals: list[dict[str, Any]] = []
    for index, queue_item in enumerate(manual_observation_reviewer_queue, start=1):
        if not isinstance(queue_item, Mapping):
            raise PromotionPlanError(f"manual_observation_reviewer_queue[{index - 1}] must be an object")
        surface_id = _required_text(queue_item, "surface_id")
        disposition = dispositions.get(surface_id)
        if disposition is None:
            raise PromotionPlanError(f"missing approved reviewer disposition for surface {surface_id}")
        proposal = _build_proposal(index, queue_item, disposition)
        _validate_proposal(proposal)
        proposals.append(proposal)

    plan = {
        "plan_version": PLAN_VERSION,
        "mode": PLAN_MODE,
        "fixture_first": True,
        "offline_only": True,
        "synthetic_only": True,
        "read_only_observation_only": True,
        "active_surface_map_mutation": False,
        "writes_surface_registry": False,
        "source_inputs": {
            "reviewer_disposition_ledger_version": _required_text(reviewer_disposition_ledger, "ledger_version"),
            "manual_observation_reviewer_queue_version": "devhub_manual_observation_reviewer_queue_v1",
        },
        "attestations": {name: True for name in REQUIRED_ATTESTATIONS},
        "surface_map_fixture_update_proposals": proposals,
        "offline_validation_commands": _deduped_commands(proposals),
    }
    validate_read_only_observation_promotion_plan_v1(plan)
    return plan


def validate_read_only_observation_promotion_plan_v1(plan: Mapping[str, Any]) -> tuple[str, ...]:
    """Return deterministic validation errors for a promotion plan packet."""

    errors: list[str] = []
    _require(errors, plan.get("plan_version") == PLAN_VERSION, f"plan_version must be {PLAN_VERSION}")
    _require(errors, plan.get("mode") == PLAN_MODE, f"mode must be {PLAN_MODE}")
    for flag in ("fixture_first", "offline_only", "synthetic_only", "read_only_observation_only"):
        _require(errors, plan.get(flag) is True, f"{flag} must be true")
    for flag in ("active_surface_map_mutation", "writes_surface_registry"):
        _require(errors, plan.get(flag) is False, f"{flag} must be false")

    attestations = _mapping(plan.get("attestations"))
    for name in REQUIRED_ATTESTATIONS:
        _require(errors, attestations.get(name) is True, f"attestations.{name} must be true")

    proposals = _sequence(plan.get("surface_map_fixture_update_proposals"))
    _require(errors, bool(proposals), "surface_map_fixture_update_proposals must not be empty")
    for index, proposal in enumerate(proposals):
        proposal_map = _mapping(proposal)
        path = f"surface_map_fixture_update_proposals[{index}]"
        _require(errors, _text(proposal_map.get("proposal_effect")) == "synthetic_fixture_update_only", f"{path}.proposal_effect must be synthetic_fixture_update_only")
        _require(errors, proposal_map.get("active_surface_map_mutation") is False, f"{path}.active_surface_map_mutation must be false")
        for field in (
            "surface_id",
            "page_heading",
            "reviewer_owner",
            "rollback_note",
            "approved_disposition_id",
        ):
            _require(errors, bool(_text(proposal_map.get(field))), f"{path}.{field} is required")
        for field in (
            "accessible_landmarks",
            "validation_messages",
            "redaction_expectations",
            "stop_before_action_gates",
            "offline_validation_commands",
            "citations",
        ):
            _require(errors, bool(_sequence(proposal_map.get(field))), f"{path}.{field} must not be empty")
        proposal_attestations = _mapping(proposal_map.get("attestations"))
        for name in REQUIRED_ATTESTATIONS:
            _require(errors, proposal_attestations.get(name) is True, f"{path}.attestations.{name} must be true")

    _scan_for_forbidden_content(errors, plan)
    return tuple(dict.fromkeys(errors))


def assert_valid_read_only_observation_promotion_plan_v1(plan: Mapping[str, Any]) -> None:
    errors = validate_read_only_observation_promotion_plan_v1(plan)
    if errors:
        raise AssertionError("; ".join(errors))


def _approved_dispositions_by_surface(ledger: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    dispositions = ledger.get("dispositions")
    if not isinstance(dispositions, Sequence) or isinstance(dispositions, (str, bytes, bytearray)):
        raise PromotionPlanError("dispositions must be a list")

    approved: dict[str, Mapping[str, Any]] = {}
    for index, disposition in enumerate(dispositions):
        if not isinstance(disposition, Mapping):
            raise PromotionPlanError(f"dispositions[{index}] must be an object")
        status = _text(disposition.get("disposition_status") or disposition.get("decision") or disposition.get("status"))
        if status != "approved":
            continue
        surface_id = _required_text(disposition, "surface_id")
        if surface_id in approved:
            raise PromotionPlanError(f"duplicate approved disposition for surface {surface_id}")
        approved[surface_id] = disposition
    if not approved:
        raise PromotionPlanError("at least one approved reviewer disposition is required")
    return approved


def _build_proposal(index: int, queue_item: Mapping[str, Any], disposition: Mapping[str, Any]) -> dict[str, Any]:
    surface_id = _required_text(queue_item, "surface_id")
    queue_attestations = _normalized_attestations(_mapping(queue_item.get("attestations")))
    disposition_attestations = _normalized_attestations(_mapping(disposition.get("attestations")))
    attestations = {name: queue_attestations.get(name) is True and disposition_attestations.get(name) is True for name in REQUIRED_ATTESTATIONS}

    return {
        "proposal_id": f"devhub-read-only-observation-surface-map-proposal-v1-{index:03d}",
        "surface_id": surface_id,
        "proposal_effect": "synthetic_fixture_update_only",
        "active_surface_map_mutation": False,
        "approved_disposition_id": _required_text(disposition, "disposition_id"),
        "page_heading": _required_text(queue_item, "page_heading"),
        "accessible_landmarks": _required_text_list(queue_item, "accessible_landmarks"),
        "validation_messages": _required_text_list(queue_item, "validation_message_expectations"),
        "redaction_expectations": _required_text_list(queue_item, "redaction_checks"),
        "stop_before_action_gates": _required_text_list(queue_item, "stop_before_action_gates"),
        "reviewer_owner": _required_text(disposition, "reviewer_owner"),
        "rollback_note": _rollback_note(queue_item, disposition),
        "offline_validation_commands": _required_command_list(queue_item, "offline_validation_commands"),
        "citations": _combined_citations(queue_item, disposition),
        "attestations": attestations,
    }


def _validate_proposal(proposal: Mapping[str, Any]) -> None:
    failed = [name for name, value in _mapping(proposal.get("attestations")).items() if value is not True]
    if failed:
        raise PromotionPlanError(f"proposal {proposal.get('proposal_id')} failed attestations: {', '.join(failed)}")
    if not _sequence(proposal.get("citations")):
        raise PromotionPlanError(f"proposal {proposal.get('proposal_id')} requires citations")


def _rollback_note(queue_item: Mapping[str, Any], disposition: Mapping[str, Any]) -> str:
    disposition_note = _text(disposition.get("rollback_note"))
    if disposition_note:
        return disposition_note
    notes = _required_text_list(queue_item, "rollback_notes")
    return notes[0]


def _combined_citations(queue_item: Mapping[str, Any], disposition: Mapping[str, Any]) -> list[Any]:
    citations: list[Any] = []
    citations.extend(_sequence(queue_item.get("citations")))
    citations.extend(_sequence(disposition.get("citations")))
    if not citations:
        raise PromotionPlanError("citations are required")
    return citations


def _deduped_commands(proposals: Sequence[Mapping[str, Any]]) -> list[list[str]]:
    seen: set[tuple[str, ...]] = set()
    commands: list[list[str]] = []
    for proposal in proposals:
        for command in _required_command_list(proposal, "offline_validation_commands"):
            key = tuple(command)
            if key not in seen:
                seen.add(key)
                commands.append(command)
    return commands


def _normalized_attestations(attestations: Mapping[str, Any]) -> dict[str, bool]:
    normalized: dict[str, bool] = {}
    for key, value in attestations.items():
        if not isinstance(key, str) or not isinstance(value, bool):
            raise PromotionPlanError("attestation keys must be strings and values must be booleans")
        normalized[ATTESTATION_ALIASES.get(key, key)] = value
    return normalized


def _scan_commit_safe(value: Any, path: str) -> None:
    errors: list[str] = []
    _scan_for_forbidden_content(errors, value, path)
    if errors:
        raise PromotionPlanError("; ".join(errors))


def _scan_for_forbidden_content(errors: list[str], value: Any, path: str = "packet") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = _text(key)
            key_lower = key_text.lower().replace("-", "_")
            child_path = f"{path}.{key_text}"
            if any(forbidden in key_lower for forbidden in FORBIDDEN_KEYS):
                errors.append(f"{child_path} must not contain private DevHub session or browser artifact data")
            _scan_for_forbidden_content(errors, child, child_path)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            _scan_for_forbidden_content(errors, child, f"{path}[{index}]")
    elif isinstance(value, str):
        normalized = " ".join(value.lower().split())
        if any(normalized.startswith(prefix) for prefix in SAFE_PREFIXES):
            return
        if any(marker in normalized for marker in FORBIDDEN_TEXT):
            errors.append(f"{path} must not contain private artifacts or consequential automation language")


def _required_text(mapping: Mapping[str, Any], key: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        raise PromotionPlanError(f"{key} must be a non-empty string")
    return value


def _required_text_list(mapping: Mapping[str, Any], key: str) -> list[str]:
    value = mapping.get(key)
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)) or not value:
        raise PromotionPlanError(f"{key} must be a non-empty string list")
    result: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise PromotionPlanError(f"{key} must contain only non-empty strings")
        result.append(item)
    return result


def _required_command_list(mapping: Mapping[str, Any], key: str) -> list[list[str]]:
    value = mapping.get(key)
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)) or not value:
        raise PromotionPlanError(f"{key} must be a non-empty command list")
    commands: list[list[str]] = []
    for command in value:
        if not isinstance(command, Sequence) or isinstance(command, (str, bytes, bytearray)) or not command:
            raise PromotionPlanError(f"{key} entries must be non-empty string arrays")
        command_parts = []
        for part in command:
            if not isinstance(part, str) or not part.strip():
                raise PromotionPlanError(f"{key} command parts must be non-empty strings")
            command_parts.append(part)
        commands.append(command_parts)
    return commands


def _mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    return {}


def _sequence(value: Any) -> list[Any]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return list(value)
    return []


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _require(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)
