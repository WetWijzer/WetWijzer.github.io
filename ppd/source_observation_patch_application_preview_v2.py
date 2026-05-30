"""Fixture-first source observation patch application preview v2.

Builds inactive source-registry fixture patch previews from an implementation
patch staging plan v2 and a public source observation refresh candidate v2. This
module is metadata-only and does not crawl, download, run processors, persist raw
bodies, or mutate the source registry.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from ppd.implementation_patch_staging_plan_v2 import (
    build_implementation_patch_staging_plan_v2_from_fixture,
    validate_implementation_patch_staging_plan_v2,
)
from ppd.source_observation_refresh_candidate_v2 import validate_source_observation_refresh_candidate_v2

PREVIEW_TYPE = "ppd.source_observation_patch_application_preview.v2"
PREVIEW_VERSION = 2

ATTESTATIONS = {
    "no_live_crawl": True,
    "no_download": True,
    "no_processor": True,
    "no_raw_body": True,
    "no_source_registry_mutation": True,
}

OFFLINE_VALIDATION_COMMANDS = [
    ["python3", "-m", "py_compile", "ppd/source_observation_patch_application_preview_v2.py"],
    ["python3", "-m", "pytest", "ppd/tests/test_source_observation_patch_application_preview_v2.py"],
    ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
]

_PROHIBITED_KEYS = {
    "archive",
    "archive_path",
    "auth_state",
    "body",
    "browser_artifact",
    "crawl_output",
    "download",
    "download_path",
    "downloaded_document",
    "har",
    "raw_body",
    "raw_crawl",
    "raw_download",
    "raw_html",
    "raw_pdf",
    "response_body",
    "screenshot",
    "session_state",
    "storage_state",
    "trace",
}

_MUTATION_KEYS = {
    "active_source_registry_mutation",
    "active_source_mutation",
    "mutates_source_registry",
    "registry_mutation_enabled",
    "source_registry_mutation",
    "source_registry_mutation_enabled",
    "source_mutation_enabled",
}

_PROHIBITED_TEXT = (
    "live crawl completed",
    "live crawler completed",
    "downloaded document",
    "processor completed",
    "ran processor",
    "raw body",
    "raw crawl",
    "raw html",
    "registry updated",
    "source registry updated",
    "permit will be approved",
    "guaranteed approval",
)


@dataclass(frozen=True)
class SourceObservationPatchApplicationPreviewV2ValidationResult:
    ok: bool
    errors: tuple[str, ...]


def load_json(path: str | Path) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"expected JSON object at {path}")
    return data


def build_source_observation_patch_application_preview_v2_from_fixture(path: str | Path) -> dict[str, Any]:
    fixture_path = Path(path)
    fixture = load_json(fixture_path)
    base = fixture_path.parent
    plan = build_implementation_patch_staging_plan_v2_from_fixture(base / _required_text(fixture, "implementation_patch_staging_plan_v2_fixture"))
    source_candidate = load_json(base / _required_text(fixture, "public_source_observation_refresh_candidate_v2_fixture"))
    return build_source_observation_patch_application_preview_v2(plan, source_candidate)


def build_source_observation_patch_application_preview_v2(
    implementation_patch_staging_plan_v2: Mapping[str, Any],
    public_source_observation_refresh_candidate_v2: Mapping[str, Any],
) -> dict[str, Any]:
    plan_result = validate_implementation_patch_staging_plan_v2(implementation_patch_staging_plan_v2)
    if not plan_result.ok:
        raise ValueError("invalid implementation patch staging plan v2: " + "; ".join(plan_result.errors))
    source_packet = dict(public_source_observation_refresh_candidate_v2)
    source_result = validate_source_observation_refresh_candidate_v2(source_packet)
    if not source_result.ok:
        raise ValueError("invalid public source observation refresh candidate v2: " + "; ".join(source_result.errors))

    observations = {_text(item.get("source_id")): item for item in _dicts(source_packet.get("candidates"))}
    previews: list[dict[str, Any]] = []
    for candidate in _dicts(implementation_patch_staging_plan_v2.get("inactive_source_patch_candidates")):
        source_id = _text(candidate.get("target_id"))
        observation = observations.get(source_id)
        if not observation:
            continue
        metadata = _mapping(observation.get("candidate_metadata"))
        citations = _dicts(candidate.get("citations")) + _dicts(observation.get("citations"))
        previews.append(
            {
                "preview_id": f"source-observation-preview-{_slug(source_id)}",
                "source_patch_candidate_id": _text(candidate.get("candidate_id")),
                "source_id": source_id,
                "affected_source_ids": _strings(observation.get("affected_source_ids")) or [source_id],
                "inactive": True,
                "source_registry_fixture_patch": True,
                "reviewer_owner": _text(candidate.get("reviewer_owner")) or _text(observation.get("reviewer_owner")) or "ppd-reviewer-unassigned",
                "before_metadata_rows": _before_rows(source_id, metadata, citations),
                "after_metadata_rows": _after_rows(source_id, metadata, citations),
                "rollback_checkpoint": _text(candidate.get("rollback_checkpoint")) or "Discard this inactive preview; no source registry state is changed.",
                "citations": citations,
            }
        )

    packet = {
        "preview_type": PREVIEW_TYPE,
        "preview_version": PREVIEW_VERSION,
        "fixture_first": True,
        "mode": "inactive_source_registry_fixture_patch_preview_only",
        "consumes": {
            "implementation_patch_staging_plan_v2": _text(implementation_patch_staging_plan_v2.get("plan_type")),
            "public_source_observation_refresh_candidate_v2": _text(source_packet.get("schema_version")),
        },
        "affected_source_ids": sorted({source_id for preview in previews for source_id in _strings(preview.get("affected_source_ids"))}),
        "source_registry_fixture_patch_previews": previews,
        "reviewer_owner_fields": _owner_rows(previews),
        "rollback_checkpoints": _rollback_rows(previews),
        "offline_validation_commands": list(OFFLINE_VALIDATION_COMMANDS),
        "attestations": dict(ATTESTATIONS),
    }
    require_source_observation_patch_application_preview_v2(packet)
    return packet


def validate_source_observation_patch_application_preview_v2(packet: Mapping[str, Any]) -> SourceObservationPatchApplicationPreviewV2ValidationResult:
    errors: list[str] = []
    if packet.get("preview_type") != PREVIEW_TYPE:
        errors.append(f"preview_type must be {PREVIEW_TYPE}")
    if packet.get("preview_version") != PREVIEW_VERSION:
        errors.append("preview_version must be 2")
    if packet.get("fixture_first") is not True:
        errors.append("fixture_first must be true")
    if packet.get("mode") != "inactive_source_registry_fixture_patch_preview_only":
        errors.append("mode must be inactive_source_registry_fixture_patch_preview_only")
    consumes = _mapping(packet.get("consumes"))
    if consumes.get("implementation_patch_staging_plan_v2") != "ppd.implementation_patch_staging_plan.v2":
        errors.append("consumes.implementation_patch_staging_plan_v2 must reference implementation patch staging plan v2")
    if consumes.get("public_source_observation_refresh_candidate_v2") != "public_source_observation_refresh_candidate_v2":
        errors.append("consumes.public_source_observation_refresh_candidate_v2 must reference public source observation refresh candidate v2")
    affected = _strings(packet.get("affected_source_ids"))
    if not affected:
        errors.append("affected_source_ids must be non-empty")
    _validate_previews(packet.get("source_registry_fixture_patch_previews"), affected, errors)
    _validate_owner_rows(packet.get("reviewer_owner_fields"), errors)
    _validate_rollback_rows(packet.get("rollback_checkpoints"), errors)
    if packet.get("attestations") != ATTESTATIONS:
        errors.append("attestations must preserve no-live/no-download/no-processor/no-raw-body/no-source-registry-mutation guardrails")
    commands = packet.get("offline_validation_commands")
    if not isinstance(commands, list) or not commands:
        errors.append("offline_validation_commands must be non-empty")
    elif not all(_strings(command) for command in commands if isinstance(command, list)):
        errors.append("offline_validation_commands must contain command lists")
    _reject_unsafe_content(packet, "$", errors)
    return SourceObservationPatchApplicationPreviewV2ValidationResult(not errors, tuple(errors))


def require_source_observation_patch_application_preview_v2(packet: Mapping[str, Any]) -> None:
    result = validate_source_observation_patch_application_preview_v2(packet)
    if not result.ok:
        raise ValueError("invalid source observation patch application preview v2: " + "; ".join(result.errors))


def _before_rows(source_id: str, metadata: Mapping[str, Any], citations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    keys = sorted(metadata) or ["metadata_refresh_status"]
    return [
        {
            "row_id": f"before-{_slug(source_id)}-{_slug(key)}",
            "source_id": source_id,
            "metadata_key": key,
            "metadata_value": "current_fixture_value_retained",
            "row_state": "before_inactive_preview",
            "citations": citations,
        }
        for key in keys
    ]


def _after_rows(source_id: str, metadata: Mapping[str, Any], citations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for key in sorted(metadata) or ["metadata_refresh_status"]:
        value = metadata.get(key, "review_required")
        rows.append(
            {
                "row_id": f"after-{_slug(source_id)}-{_slug(key)}",
                "source_id": source_id,
                "metadata_key": key,
                "metadata_value": str(value),
                "row_state": "after_inactive_fixture_preview",
                "citations": citations,
            }
        )
    return rows


def _owner_rows(previews: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    seen: set[tuple[str, str]] = set()
    for preview in previews:
        owner = _text(preview.get("reviewer_owner"))
        source_id = _text(preview.get("source_id"))
        key = (owner, source_id)
        if owner and source_id and key not in seen:
            seen.add(key)
            rows.append({"owner_field_id": f"owner-{_slug(owner)}-{_slug(source_id)}", "reviewer_owner": owner, "source_id": source_id, "citations": _dicts(preview.get("citations"))})
    return rows


def _rollback_rows(previews: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    rows = [
        {
            "checkpoint_id": "discard-source-observation-patch-application-preview-v2",
            "summary": "Discard this inactive preview packet and rerun fixture validation; source registry fixtures and active registries remain unchanged.",
            "affected_source_ids": sorted({_text(preview.get("source_id")) for preview in previews if _text(preview.get("source_id"))}),
            "citations": [citation for preview in previews for citation in _dicts(preview.get("citations"))],
        }
    ]
    for preview in previews:
        rows.append(
            {
                "checkpoint_id": f"discard-{_slug(_text(preview.get('source_id')))}-preview-row",
                "summary": _text(preview.get("rollback_checkpoint")) or "Discard this inactive source preview row.",
                "affected_source_ids": _strings(preview.get("affected_source_ids")),
                "citations": _dicts(preview.get("citations")),
            }
        )
    return rows


def _validate_previews(value: Any, packet_affected: list[str], errors: list[str]) -> None:
    rows = _dicts(value)
    if not rows:
        errors.append("source_registry_fixture_patch_previews must be non-empty")
        return
    for index, row in enumerate(rows):
        path = f"source_registry_fixture_patch_previews[{index}]"
        for field in ("preview_id", "source_patch_candidate_id", "source_id", "reviewer_owner", "rollback_checkpoint"):
            if not _text(row.get(field)):
                errors.append(f"{path}.{field} must be present")
        if row.get("inactive") is not True:
            errors.append(f"{path}.inactive must be true")
        if row.get("source_registry_fixture_patch") is not True:
            errors.append(f"{path}.source_registry_fixture_patch must be true")
        affected = _strings(row.get("affected_source_ids"))
        if not affected:
            errors.append(f"{path}.affected_source_ids must be non-empty")
        for source_id in affected:
            if source_id not in packet_affected:
                errors.append(f"{path}.affected_source_ids must be included in packet affected_source_ids")
        if not _dicts(row.get("before_metadata_rows")):
            errors.append(f"{path}.before_metadata_rows must be non-empty")
        if not _dicts(row.get("after_metadata_rows")):
            errors.append(f"{path}.after_metadata_rows must be non-empty")
        if not _dicts(row.get("citations")):
            errors.append(f"{path}.citations must be non-empty")


def _validate_owner_rows(value: Any, errors: list[str]) -> None:
    rows = _dicts(value)
    if not rows:
        errors.append("reviewer_owner_fields must be non-empty")
        return
    for index, row in enumerate(rows):
        if not _text(row.get("owner_field_id")) or not _text(row.get("reviewer_owner")) or not _text(row.get("source_id")):
            errors.append(f"reviewer_owner_fields[{index}] must include owner_field_id, reviewer_owner, and source_id")
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
        if not _strings(row.get("affected_source_ids")):
            errors.append(f"rollback_checkpoints[{index}].affected_source_ids must be non-empty")
        if not _dicts(row.get("citations")):
            errors.append(f"rollback_checkpoints[{index}].citations must be non-empty")


def _reject_unsafe_content(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            normalized = str(key).lower().replace("-", "_")
            if normalized in _PROHIBITED_KEYS and child not in (None, "", [], {}):
                errors.append(f"{child_path} is prohibited in source observation patch application previews")
            if normalized in _MUTATION_KEYS and _is_active_flag(child):
                errors.append(f"{child_path} must not enable source registry mutation")
            _reject_unsafe_content(child, child_path, errors)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_unsafe_content(child, f"{path}[{index}]", errors)
    elif isinstance(value, str):
        lowered = value.lower()
        if any(term in lowered for term in _PROHIBITED_TEXT):
            errors.append(f"{path} contains prohibited live, processor, raw-body, mutation, or outcome language")


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


def _slug(value: str) -> str:
    cleaned = "".join(char.lower() if char.isalnum() else "-" for char in value)
    return "-".join(part for part in cleaned.split("-") if part) or "item"
