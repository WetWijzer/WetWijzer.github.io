"""Fixture-first DevHub surface patch application preview v2.

Consumes an implementation patch staging plan v2 and a DevHub read-only surface
observation refresh candidate v2 into inactive surface-registry fixture preview
rows. This module is metadata-only: it does not open DevHub, authenticate, create
browser artifacts, or mutate the surface registry.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from ppd.devhub_surface_observation_refresh_candidate_v2 import validate_devhub_surface_observation_refresh_candidate_v2
from ppd.implementation_patch_staging_plan_v2 import (
    build_implementation_patch_staging_plan_v2_from_fixture,
    validate_implementation_patch_staging_plan_v2,
)

PREVIEW_TYPE = "ppd.devhub_surface_patch_application_preview.v2"
PREVIEW_VERSION = 2

ATTESTATIONS = {
    "no_live_devhub": True,
    "no_auth_state": True,
    "no_screenshot": True,
    "no_trace": True,
    "no_har": True,
    "no_surface_registry_mutation": True,
}

OFFLINE_VALIDATION_COMMANDS = [
    ["python3", "-m", "py_compile", "ppd/devhub_surface_patch_application_preview_v2.py"],
    ["python3", "-m", "pytest", "ppd/tests/test_devhub_surface_patch_application_preview_v2.py"],
    ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
]

_PROHIBITED_KEYS = {
    "access_token",
    "account_number",
    "auth",
    "auth_state",
    "authenticated_value",
    "authorization",
    "bearer_token",
    "browser_artifact",
    "browser_artifacts",
    "browser_context_state",
    "case_number",
    "cookie",
    "cookies",
    "credential",
    "credentials",
    "devhub_session_file",
    "har",
    "har_path",
    "local_storage",
    "login",
    "password",
    "permit_number",
    "playwright_state",
    "playwright_trace",
    "private_value",
    "secret",
    "screenshot",
    "screenshot_path",
    "session",
    "session_artifact",
    "session_state",
    "session_storage",
    "storage_state",
    "token",
    "trace",
    "trace_path",
}

_MUTATION_KEYS = {
    "active_agent_state_mutation",
    "active_guardrail_mutation",
    "active_monitoring_mutation",
    "active_prompt_mutation",
    "active_registry_mutation",
    "active_release_state_mutation",
    "active_surface_registry_mutation",
    "agent_state_mutation",
    "apply_surface_registry_changes",
    "guardrail_mutation",
    "monitoring_mutation",
    "mutate_surface_registry",
    "mutates_agent_state",
    "mutates_guardrails",
    "mutates_monitoring",
    "mutates_prompts",
    "mutates_release_state",
    "mutates_surface_registry",
    "prompt_mutation",
    "release_state_mutation",
    "surface_registry_mutation",
    "surface_registry_mutation_enabled",
    "surface_registry_write",
    "update_surface_registry",
}

_PRIVATE_TEXT = (
    "access token",
    "auth state",
    "authenticated value",
    "bearer token",
    "browser context state",
    "cookie value",
    "devhub session",
    "password",
    "private devhub value",
    "session artifact",
    "session storage",
    "storage state",
)

_BROWSER_ARTIFACT_TEXT = (
    ".har",
    "har file",
    "playwright trace",
    "screenshot file",
    "screenshot path",
    "storage-state.json",
    "trace.zip",
)

_LIVE_COMPLETION_TEXT = (
    "browser automation completed",
    "devhub completed",
    "devhub live run completed",
    "live devhub completion",
    "opened devhub",
    "playwright clicked",
    "ran playwright",
)

_OUTCOME_GUARANTEE_TEXT = (
    "approval is guaranteed",
    "guaranteed approval",
    "guaranteed permit",
    "legal outcome guaranteed",
    "permit approved",
    "permit will be approved",
    "permitting outcome guaranteed",
    "will be approved",
    "will receive a permit",
)

_CONSEQUENTIAL_ACTION_TEXT = (
    "cancel request enabled",
    "certification enabled",
    "certify acknowledgement",
    "consequential action enabled",
    "enable payment",
    "enable scheduling",
    "enable submission",
    "final submit",
    "official upload enabled",
    "purchase permit",
    "schedule inspection",
    "submit application",
    "submit payment",
    "submit permit",
    "submission completed",
    "upload correction",
)


@dataclass(frozen=True)
class DevHubSurfacePatchApplicationPreviewV2ValidationResult:
    ok: bool
    errors: tuple[str, ...]


def load_json(path: str | Path) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"expected JSON object at {path}")
    return data


def build_devhub_surface_patch_application_preview_v2_from_fixture(path: str | Path) -> dict[str, Any]:
    fixture_path = Path(path)
    fixture = load_json(fixture_path)
    base = fixture_path.parent
    plan = build_implementation_patch_staging_plan_v2_from_fixture(base / _required_text(fixture, "implementation_patch_staging_plan_v2_fixture"))
    candidate = load_json(base / _required_text(fixture, "devhub_read_only_surface_observation_refresh_candidate_v2_fixture"))
    return build_devhub_surface_patch_application_preview_v2(plan, candidate)


def build_devhub_surface_patch_application_preview_v2(
    implementation_patch_staging_plan_v2: Mapping[str, Any],
    devhub_read_only_surface_observation_refresh_candidate_v2: Mapping[str, Any],
) -> dict[str, Any]:
    plan_result = validate_implementation_patch_staging_plan_v2(implementation_patch_staging_plan_v2)
    if not plan_result.ok:
        raise ValueError("invalid implementation patch staging plan v2: " + "; ".join(plan_result.errors))

    candidate = dict(devhub_read_only_surface_observation_refresh_candidate_v2)
    candidate_result = validate_devhub_surface_observation_refresh_candidate_v2(candidate)
    if not candidate_result.ok:
        raise ValueError("invalid DevHub read-only surface observation refresh candidate v2: " + "; ".join(candidate_result.errors))

    observations = {_text(row.get("surface_id")): row for row in _dicts(candidate.get("observations"))}
    confidence = {_text(row.get("surface_id")): row for row in _dicts(candidate.get("selector_confidence_notes"))}
    handoff = {_text(row.get("surface_id")): row for row in _dicts(candidate.get("manual_handoff_dispositions"))}
    redaction = {_text(row.get("surface_id")): row for row in _dicts(candidate.get("redaction_dispositions"))}

    previews: list[dict[str, Any]] = []
    for staged in _dicts(implementation_patch_staging_plan_v2.get("inactive_surface_patch_candidates")):
        surface_id = _text(staged.get("target_id"))
        observation = observations.get(surface_id)
        if not observation:
            continue
        citations = _dicts(staged.get("citations")) + _dicts(observation.get("citations"))
        confidence_row = confidence.get(surface_id, {})
        handoff_row = handoff.get(surface_id, {})
        redaction_row = redaction.get(surface_id, {})
        citations += _dicts(confidence_row.get("citations"))
        citations += _dicts(handoff_row.get("citations"))
        citations += _dicts(redaction_row.get("citations"))
        before_confidence = "current_fixture_selector_confidence_retained"
        after_confidence = _text(confidence_row.get("confidence")) or _text(staged.get("selector_confidence")) or "review_required"
        previews.append(
            {
                "preview_id": f"devhub-surface-preview-{_slug(surface_id)}",
                "surface_patch_candidate_id": _text(staged.get("candidate_id")),
                "surface_id": surface_id,
                "affected_surface_ids": [surface_id],
                "inactive": True,
                "surface_registry_fixture_patch": True,
                "read_only": True,
                "reviewer_owner": _text(staged.get("reviewer_owner")) or "ppd-reviewer-unassigned",
                "before_synthetic_action_rows": [
                    {
                        "row_id": f"before-action-{_slug(surface_id)}",
                        "surface_id": surface_id,
                        "synthetic_action": "current fixture action row retained for offline review",
                        "row_state": "before_inactive_preview",
                        "citations": citations,
                    }
                ],
                "after_synthetic_action_rows": [
                    {
                        "row_id": f"after-action-{_slug(surface_id)}",
                        "surface_id": surface_id,
                        "synthetic_action": _text(observation.get("synthetic_action_candidate")) or "review read-only surface labels only",
                        "row_state": "after_inactive_fixture_preview",
                        "citations": citations,
                    }
                ],
                "selector_confidence_deltas": [
                    {
                        "surface_id": surface_id,
                        "before_confidence": before_confidence,
                        "after_confidence": after_confidence,
                        "delta_disposition": "review_required_before_any_active_registry_change",
                        "citations": _dicts(confidence_row.get("citations")) or citations,
                    }
                ],
                "manual_handoff_disposition": {
                    "required": bool(handoff_row.get("required", staged.get("manual_handoff_required", True))),
                    "reason": _text(handoff_row.get("reason")) or "User attendance remains required for account-scoped review.",
                    "citations": _dicts(handoff_row.get("citations")) or citations,
                },
                "redaction_disposition": {
                    "disposition": _text(redaction_row.get("disposition")) or _text(staged.get("redaction_disposition")) or "synthetic-only",
                    "reason": _text(redaction_row.get("reason")) or "Preview uses synthetic labels and omits account-specific values.",
                    "citations": _dicts(redaction_row.get("citations")) or citations,
                },
                "rollback_checkpoint": _text(staged.get("rollback_checkpoint")) or "Discard this inactive DevHub surface preview; no surface registry state is changed.",
                "citations": citations,
            }
        )

    packet = {
        "preview_type": PREVIEW_TYPE,
        "preview_version": PREVIEW_VERSION,
        "fixture_first": True,
        "mode": "inactive_surface_registry_fixture_patch_preview_only",
        "consumes": {
            "implementation_patch_staging_plan_v2": _text(implementation_patch_staging_plan_v2.get("plan_type")),
            "devhub_read_only_surface_observation_refresh_candidate_v2": _text(candidate.get("candidate_version")),
        },
        "affected_surface_ids": sorted({surface_id for preview in previews for surface_id in _strings(preview.get("affected_surface_ids"))}),
        "surface_registry_fixture_patch_previews": previews,
        "reviewer_owner_fields": _owner_rows(previews),
        "rollback_checkpoints": _rollback_rows(previews),
        "offline_validation_commands": list(OFFLINE_VALIDATION_COMMANDS),
        "attestations": dict(ATTESTATIONS),
    }
    require_devhub_surface_patch_application_preview_v2(packet)
    return packet


def validate_devhub_surface_patch_application_preview_v2(packet: Mapping[str, Any]) -> DevHubSurfacePatchApplicationPreviewV2ValidationResult:
    errors: list[str] = []
    if packet.get("preview_type") != PREVIEW_TYPE:
        errors.append(f"preview_type must be {PREVIEW_TYPE}")
    if packet.get("preview_version") != PREVIEW_VERSION:
        errors.append("preview_version must be 2")
    if packet.get("fixture_first") is not True:
        errors.append("fixture_first must be true")
    if packet.get("mode") != "inactive_surface_registry_fixture_patch_preview_only":
        errors.append("mode must be inactive_surface_registry_fixture_patch_preview_only")
    consumes = _mapping(packet.get("consumes"))
    if consumes.get("implementation_patch_staging_plan_v2") != "ppd.implementation_patch_staging_plan.v2":
        errors.append("consumes.implementation_patch_staging_plan_v2 must reference implementation patch staging plan v2")
    if consumes.get("devhub_read_only_surface_observation_refresh_candidate_v2") != "devhub_read_only_surface_observation_refresh_candidate_v2":
        errors.append("consumes.devhub_read_only_surface_observation_refresh_candidate_v2 must reference DevHub read-only surface observation refresh candidate v2")
    affected = _strings(packet.get("affected_surface_ids"))
    if not affected:
        errors.append("affected_surface_ids must be non-empty")
    _validate_previews(packet.get("surface_registry_fixture_patch_previews"), affected, errors)
    _validate_owner_rows(packet.get("reviewer_owner_fields"), errors)
    _validate_rollback_rows(packet.get("rollback_checkpoints"), errors)
    if packet.get("attestations") != ATTESTATIONS:
        errors.append("attestations must preserve no-live-DevHub/no-auth-state/no-screenshot/no-trace/no-HAR/no-surface-registry-mutation guardrails")
    commands = packet.get("offline_validation_commands")
    if not isinstance(commands, list) or not commands:
        errors.append("offline_validation_commands must be non-empty")
    elif not all(isinstance(command, list) and _strings(command) for command in commands):
        errors.append("offline_validation_commands must contain command lists")
    _reject_unsafe_content(packet, "$", errors)
    return DevHubSurfacePatchApplicationPreviewV2ValidationResult(not errors, tuple(errors))


def require_devhub_surface_patch_application_preview_v2(packet: Mapping[str, Any]) -> None:
    result = validate_devhub_surface_patch_application_preview_v2(packet)
    if not result.ok:
        raise ValueError("invalid DevHub surface patch application preview v2: " + "; ".join(result.errors))


def _owner_rows(previews: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for preview in previews:
        owner = _text(preview.get("reviewer_owner"))
        surface_id = _text(preview.get("surface_id"))
        key = (owner, surface_id)
        if owner and surface_id and key not in seen:
            seen.add(key)
            rows.append({"owner_field_id": f"owner-{_slug(owner)}-{_slug(surface_id)}", "reviewer_owner": owner, "surface_id": surface_id, "citations": _dicts(preview.get("citations"))})
    return rows


def _rollback_rows(previews: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    rows = [
        {
            "checkpoint_id": "discard-devhub-surface-patch-application-preview-v2",
            "summary": "Discard this inactive preview packet and rerun fixture validation; surface registry fixtures and active registries remain unchanged.",
            "affected_surface_ids": sorted({_text(preview.get("surface_id")) for preview in previews if _text(preview.get("surface_id"))}),
            "citations": [citation for preview in previews for citation in _dicts(preview.get("citations"))],
        }
    ]
    for preview in previews:
        rows.append(
            {
                "checkpoint_id": f"discard-{_slug(_text(preview.get('surface_id')))}-preview-row",
                "summary": _text(preview.get("rollback_checkpoint")) or "Discard this inactive DevHub surface preview row.",
                "affected_surface_ids": _strings(preview.get("affected_surface_ids")),
                "citations": _dicts(preview.get("citations")),
            }
        )
    return rows


def _validate_previews(value: Any, packet_affected: list[str], errors: list[str]) -> None:
    rows = _dicts(value)
    if not rows:
        errors.append("surface_registry_fixture_patch_previews must be non-empty")
        return
    for index, row in enumerate(rows):
        path = f"surface_registry_fixture_patch_previews[{index}]"
        for field in ("preview_id", "surface_patch_candidate_id", "surface_id", "reviewer_owner", "rollback_checkpoint"):
            if not _text(row.get(field)):
                errors.append(f"{path}.{field} must be present")
        if row.get("inactive") is not True:
            errors.append(f"{path}.inactive must be true")
        if row.get("surface_registry_fixture_patch") is not True:
            errors.append(f"{path}.surface_registry_fixture_patch must be true")
        if row.get("read_only") is not True:
            errors.append(f"{path}.read_only must be true")
        affected = _strings(row.get("affected_surface_ids"))
        if not affected:
            errors.append(f"{path}.affected_surface_ids must be non-empty")
        for surface_id in affected:
            if surface_id not in packet_affected:
                errors.append(f"{path}.affected_surface_ids must be included in packet affected_surface_ids")
        _validate_action_rows(path, "before_synthetic_action_rows", row.get("before_synthetic_action_rows"), errors)
        _validate_action_rows(path, "after_synthetic_action_rows", row.get("after_synthetic_action_rows"), errors)
        _validate_selector_deltas(path, row.get("selector_confidence_deltas"), errors)
        _validate_disposition(path, "manual_handoff_disposition", row.get("manual_handoff_disposition"), errors)
        _validate_disposition(path, "redaction_disposition", row.get("redaction_disposition"), errors)
        if not _dicts(row.get("citations")):
            errors.append(f"{path}.citations must be non-empty")


def _validate_action_rows(path: str, field: str, value: Any, errors: list[str]) -> None:
    rows = _dicts(value)
    if not rows:
        errors.append(f"{path}.{field} must be non-empty")
        return
    for index, row in enumerate(rows):
        row_path = f"{path}.{field}[{index}]"
        for required in ("row_id", "surface_id", "synthetic_action", "row_state"):
            if not _text(row.get(required)):
                errors.append(f"{row_path}.{required} must be present")
        if not _dicts(row.get("citations")):
            errors.append(f"{row_path}.citations must be non-empty")


def _validate_selector_deltas(path: str, value: Any, errors: list[str]) -> None:
    rows = _dicts(value)
    if not rows:
        errors.append(f"{path}.selector_confidence_deltas must be non-empty")
        return
    for index, row in enumerate(rows):
        row_path = f"{path}.selector_confidence_deltas[{index}]"
        for required in ("surface_id", "before_confidence", "after_confidence", "delta_disposition"):
            if not _text(row.get(required)):
                errors.append(f"{row_path}.{required} must be present")
        if not _dicts(row.get("citations")):
            errors.append(f"{row_path}.citations must be non-empty")


def _validate_disposition(path: str, field: str, value: Any, errors: list[str]) -> None:
    row = _mapping(value)
    if not row:
        errors.append(f"{path}.{field} must be present")
        return
    if field == "manual_handoff_disposition" and "required" not in row:
        errors.append(f"{path}.{field}.required must be present")
    if field == "redaction_disposition" and not _text(row.get("disposition")):
        errors.append(f"{path}.{field}.disposition must be present")
    if not _text(row.get("reason")):
        errors.append(f"{path}.{field}.reason must be present")
    if not _dicts(row.get("citations")):
        errors.append(f"{path}.{field}.citations must be non-empty")


def _validate_owner_rows(value: Any, errors: list[str]) -> None:
    rows = _dicts(value)
    if not rows:
        errors.append("reviewer_owner_fields must be non-empty")
        return
    for index, row in enumerate(rows):
        if not _text(row.get("owner_field_id")) or not _text(row.get("reviewer_owner")) or not _text(row.get("surface_id")):
            errors.append(f"reviewer_owner_fields[{index}] must include owner_field_id, reviewer_owner, and surface_id")
        if not _dicts(row.get("citations")):
            errors.append(f"reviewer_owner_fields[{index}].citations must be non-empty")


def _validate_rollback_rows(value: Any, errors: list[str]) -> None:
    rows = _dicts(value)
    if not rows:
        errors.append("rollback_checkpoints must be non-empty")
        return
    for index, row in enumerate(rows):
        if not _text(row.get("checkpoint_id")) or not _text(row.get("summary")):
            errors.append(f"rollback_checkpoints[{index}] must include checkpoint_id and summary")
        if not _strings(row.get("affected_surface_ids")):
            errors.append(f"rollback_checkpoints[{index}].affected_surface_ids must be non-empty")
        if not _dicts(row.get("citations")):
            errors.append(f"rollback_checkpoints[{index}].citations must be non-empty")


def _reject_unsafe_content(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            normalized = str(key).lower().replace("-", "_")
            if normalized in _PROHIBITED_KEYS and _present(child):
                errors.append(f"{child_path} is prohibited in DevHub surface patch application previews")
            if normalized in _MUTATION_KEYS and _is_active_flag(child):
                errors.append(f"{child_path} active mutation flags are not allowed")
            _reject_unsafe_content(child, child_path, errors)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_unsafe_content(child, f"{path}[{index}]", errors)
    elif isinstance(value, str):
        lowered = " ".join(value.lower().split())
        if any(term in lowered for term in _PRIVATE_TEXT):
            errors.append(f"{path} contains prohibited private, credential, session, or authenticated DevHub value language")
        if any(term in lowered for term in _BROWSER_ARTIFACT_TEXT):
            errors.append(f"{path} contains prohibited screenshot, trace, HAR, or browser artifact reference")
        if any(term in lowered for term in _LIVE_COMPLETION_TEXT):
            errors.append(f"{path} contains prohibited browser automation or live DevHub completion claim")
        if any(term in lowered for term in _OUTCOME_GUARANTEE_TEXT):
            errors.append(f"{path} contains prohibited legal or permitting outcome guarantee")
        if any(term in lowered for term in _CONSEQUENTIAL_ACTION_TEXT):
            errors.append(f"{path} contains prohibited consequential action enablement language")


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _dicts(value: Any) -> list[dict[str, Any]]:
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def _strings(value: Any) -> list[str]:
    return [item.strip() for item in value if isinstance(item, str) and item.strip()] if isinstance(value, list) else []


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _required_text(mapping: Mapping[str, Any], key: str) -> str:
    value = _text(mapping.get(key))
    if not value:
        raise ValueError(f"fixture must provide {key}")
    return value


def _is_active_flag(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"active", "enabled", "true", "yes"}
    if isinstance(value, (list, tuple, dict)):
        return bool(value)
    return False


def _present(value: Any) -> bool:
    if value is None or value is False:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, dict)):
        return bool(value)
    return True


def _slug(value: str) -> str:
    cleaned = "".join(char.lower() if char.isalnum() else "-" for char in value)
    return "-".join(part for part in cleaned.split("-") if part) or "item"
