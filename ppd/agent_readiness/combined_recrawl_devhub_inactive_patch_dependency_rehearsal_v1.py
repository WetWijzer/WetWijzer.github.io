"""Fixture-first rehearsal for combined inactive PP&D patch dependencies.

This module intentionally consumes committed fixtures only. It does not crawl,
open browsers, read session state, mutate active artifacts, or download files.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

EXPECTED_PUBLIC_PREVIEW_ID = "public_source_recrawl_inactive_patch_preview_v1"
EXPECTED_DEVHUB_PREVIEW_ID = "devhub_observed_surface_inactive_patch_preview_v1"
REHEARSAL_ID = "combined_recrawl_devhub_inactive_patch_dependency_rehearsal_v1"

EXACT_OFFLINE_VALIDATION_COMMANDS = [
    [
        "python3",
        "-m",
        "py_compile",
        "ppd/agent_readiness/combined_recrawl_devhub_inactive_patch_dependency_rehearsal_v1.py",
    ],
    [
        "python3",
        "-m",
        "pytest",
        "ppd/tests/test_combined_recrawl_devhub_inactive_patch_dependency_rehearsal_v1.py",
    ],
    ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
]

REQUIRED_REVIEWER_DECISIONS = [
    "placeholder:reviewer_decision=pending",
    "placeholder:activation_scope=pending",
    "placeholder:required_followup=pending",
]

FORBIDDEN_ARTIFACT_KEY_FRAGMENTS = (
    "auth_state",
    "browser_artifact",
    "browser_state",
    "cookie",
    "downloaded_artifact",
    "downloaded_document",
    "har",
    "private_artifact",
    "private_value",
    "raw_crawl",
    "raw_download",
    "screenshot",
    "session_artifact",
    "session_state",
    "trace",
)

FORBIDDEN_CLAIM_PHRASES = (
    "accessed live devhub",
    "authenticated devhub",
    "captured session",
    "created browser session",
    "downloaded private",
    "live crawl completed",
    "live devhub access",
    "network access completed",
    "opened browser",
    "raw crawl output",
    "stored browser",
    "stored session",
)

FORBIDDEN_ACTION_LANGUAGE = (
    "agent may cancel",
    "agent may certify",
    "agent may pay",
    "agent may schedule",
    "agent may submit",
    "agent may upload",
    "ready to cancel",
    "ready to certify",
    "ready to pay",
    "ready to schedule",
    "ready to submit",
    "ready to upload",
    "safe to cancel",
    "safe to certify",
    "safe to pay",
    "safe to schedule",
    "safe to submit",
    "safe to upload",
    "will cancel",
    "will certify",
    "will pay",
    "will schedule",
    "will submit",
    "will upload",
)

FORBIDDEN_GUARANTEE_LANGUAGE = (
    "approval guaranteed",
    "compliance guaranteed",
    "guaranteed approval",
    "guaranteed permit",
    "legal advice",
    "permit guaranteed",
    "will be approved",
)

ACTIVE_MUTATION_FLAG_KEYS = (
    "active_artifact_mutation",
    "applies_active_patch",
    "mutates_active_artifacts",
    "mutates_active_prompts",
    "mutates_prompt",
    "mutates_prompts",
    "prompt_mutation_active",
)


def _read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"fixture must contain a JSON object: {path}")
    return data


def _require_preview(data: dict[str, Any], expected_preview_id: str, label: str) -> None:
    preview_id = data.get("preview_id")
    if preview_id != expected_preview_id:
        raise ValueError(
            f"{label} fixture preview_id must be {expected_preview_id!r}; got {preview_id!r}"
        )
    mode = data.get("mode")
    if mode != "inactive_patch_preview":
        raise ValueError(f"{label} fixture mode must be 'inactive_patch_preview'; got {mode!r}")


def _as_records(data: dict[str, Any], key: str, label: str) -> list[dict[str, Any]]:
    records = data.get(key)
    if not isinstance(records, list) or not records:
        raise ValueError(f"{label} fixture must include a non-empty {key} list")
    typed_records: list[dict[str, Any]] = []
    for index, record in enumerate(records, start=1):
        if not isinstance(record, dict):
            raise ValueError(f"{label} {key}[{index}] must be an object")
        typed_records.append(record)
    return typed_records


def _require_non_empty_string(record: dict[str, Any], key: str, label: str) -> str:
    value = record.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must include a non-empty {key}")
    return value


def _string_list(record: dict[str, Any], key: str) -> list[str]:
    value = record.get(key, [])
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"{key} must be a list")
    result: list[str] = []
    for item in value:
        if not isinstance(item, str):
            raise ValueError(f"{key} entries must be strings")
        result.append(item)
    return result


def _require_string_list(record: dict[str, Any], key: str, label: str) -> list[str]:
    values = _string_list(record, key)
    if not values or any(not value.strip() for value in values):
        raise ValueError(f"{label} must include a non-empty {key} list")
    return values


def _ordered(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(records, key=lambda item: (int(item.get("order", 9999)), str(item.get("id", ""))))


def _validate_public_preview(public_preview: Any) -> list[dict[str, Any]]:
    if not isinstance(public_preview, dict):
        raise ValueError("public recrawl fixture input is required and must be an object")
    _reject_forbidden_payload(public_preview, "public recrawl fixture")
    _require_preview(public_preview, EXPECTED_PUBLIC_PREVIEW_ID, "public recrawl")
    records = _ordered(
        _as_records(public_preview, "inactive_public_source_patches", "public recrawl")
    )
    for record in records:
        _require_non_empty_string(record, "source_patch_id", "public recrawl patch")
        _require_non_empty_string(record, "source_id", "public recrawl patch")
        _require_non_empty_string(record, "canonical_url", "public recrawl patch")
        _require_string_list(record, "changed_requirement_ids", "public recrawl patch")
        _require_string_list(record, "evidence_ids", "public recrawl patch")
        _require_non_empty_string(record, "rollback_ref", "public recrawl patch")
    return records


def _validate_devhub_preview(devhub_preview: Any) -> list[dict[str, Any]]:
    if not isinstance(devhub_preview, dict):
        raise ValueError("DevHub preview fixture input is required and must be an object")
    _reject_forbidden_payload(devhub_preview, "DevHub preview fixture")
    _require_preview(devhub_preview, EXPECTED_DEVHUB_PREVIEW_ID, "DevHub surface")
    records = _ordered(
        _as_records(devhub_preview, "inactive_devhub_surface_patches", "DevHub surface")
    )
    for record in records:
        _require_non_empty_string(record, "surface_patch_id", "DevHub surface patch")
        _require_non_empty_string(record, "surface_id", "DevHub surface patch")
        _require_non_empty_string(record, "observed_surface_ref", "DevHub surface patch")
        _string_list(record, "related_source_ids")
        _require_string_list(record, "action_labels", "DevHub surface patch")
        _require_non_empty_string(record, "rollback_ref", "DevHub surface patch")
        if record.get("requires_attendance") is not True:
            raise ValueError("DevHub surface patch requires_attendance must be true")
    return records


def build_rehearsal(public_preview: Any, devhub_preview: Any) -> dict[str, Any]:
    """Build deterministic dependency rows from inactive public and DevHub previews."""

    public_records = _validate_public_preview(public_preview)
    surface_records = _validate_devhub_preview(devhub_preview)

    rows: list[dict[str, Any]] = []
    linked_surface_ids: set[str] = set()

    for public_record in public_records:
        source_id = str(public_record["source_id"])
        matching_surfaces = [
            surface
            for surface in surface_records
            if source_id in _string_list(surface, "related_source_ids")
        ]
        if not matching_surfaces:
            rows.append(_dependency_row(len(rows) + 1, public_record, None))
            continue
        for surface_record in matching_surfaces:
            linked_surface_ids.add(str(surface_record["surface_patch_id"]))
            rows.append(_dependency_row(len(rows) + 1, public_record, surface_record))

    for surface_record in surface_records:
        surface_patch_id = str(surface_record["surface_patch_id"])
        if surface_patch_id not in linked_surface_ids:
            rows.append(_dependency_row(len(rows) + 1, None, surface_record))

    rehearsal = {
        "rehearsal_id": REHEARSAL_ID,
        "mode": "fixture_first_offline_rehearsal",
        "consumes": [public_preview["preview_id"], devhub_preview["preview_id"]],
        "mutates_active_artifacts": False,
        "artifact_boundaries": [
            "no active public source mutation",
            "no active DevHub surface mutation",
            "no process model mutation",
            "no requirement mutation",
            "no guardrail mutation",
            "no prompt mutation",
            "no release-state mutation",
            "no browser/session/crawl/downloaded artifact creation",
        ],
        "dependency_rows": rows,
        "rollback_references": _rollback_references(rows),
        "exact_offline_validation_commands": EXACT_OFFLINE_VALIDATION_COMMANDS,
    }
    validate_rehearsal(rehearsal)
    return rehearsal


def _dependency_row(
    dependency_order: int,
    public_record: dict[str, Any] | None,
    surface_record: dict[str, Any] | None,
) -> dict[str, Any]:
    source_patch_id = str(public_record["source_patch_id"]) if public_record else "placeholder:no-public-source-patch"
    surface_patch_id = str(surface_record["surface_patch_id"]) if surface_record else "placeholder:no-devhub-surface-patch"

    if public_record and surface_record:
        linkage = [
            "placeholder:review source evidence against observed DevHub surface before activation",
            f"source_id:{public_record['source_id']} -> surface_id:{surface_record['surface_id']}",
        ]
    elif public_record:
        linkage = [
            "placeholder:no DevHub observed surface patch linked to this public source patch yet"
        ]
    else:
        linkage = [
            "placeholder:no public source recrawl patch linked to this DevHub surface patch yet"
        ]

    return {
        "dependency_order": dependency_order,
        "dependency_id": f"dependency-{dependency_order:03d}-{source_patch_id}-{surface_patch_id}",
        "public_source_patch": _public_summary(public_record),
        "devhub_surface_patch": _surface_summary(surface_record),
        "source_to_surface_linkage_placeholders": linkage,
        "conflict_hold_placeholders": [
            "placeholder:hold if public source evidence conflicts with observed DevHub labels",
            "placeholder:hold if inactive preview freshness is stale before reviewer activation",
        ],
        "reviewer_decision_placeholders": list(REQUIRED_REVIEWER_DECISIONS),
        "rollback_references": _row_rollback_references(public_record, surface_record),
    }


def _public_summary(record: dict[str, Any] | None) -> dict[str, Any]:
    if record is None:
        return {
            "source_patch_id": "placeholder:no-public-source-patch",
            "source_id": "placeholder:no-source-id",
            "canonical_url": "placeholder:no-canonical-url",
            "changed_requirement_ids": [],
            "evidence_ids": [],
            "inactive_reason": "no linked public source patch in fixture",
        }
    return {
        "source_patch_id": str(record["source_patch_id"]),
        "source_id": str(record["source_id"]),
        "canonical_url": str(record["canonical_url"]),
        "changed_requirement_ids": _string_list(record, "changed_requirement_ids"),
        "evidence_ids": _string_list(record, "evidence_ids"),
        "inactive_reason": str(record.get("inactive_reason", "inactive fixture preview only")),
    }


def _surface_summary(record: dict[str, Any] | None) -> dict[str, Any]:
    if record is None:
        return {
            "surface_patch_id": "placeholder:no-devhub-surface-patch",
            "surface_id": "placeholder:no-surface-id",
            "observed_surface_ref": "placeholder:no-observed-surface-ref",
            "related_source_ids": [],
            "action_labels": [],
            "requires_attendance": True,
            "inactive_reason": "no linked DevHub surface patch in fixture",
        }
    return {
        "surface_patch_id": str(record["surface_patch_id"]),
        "surface_id": str(record["surface_id"]),
        "observed_surface_ref": str(record["observed_surface_ref"]),
        "related_source_ids": _string_list(record, "related_source_ids"),
        "action_labels": _string_list(record, "action_labels"),
        "requires_attendance": bool(record.get("requires_attendance", True)),
        "inactive_reason": str(record.get("inactive_reason", "inactive fixture preview only")),
    }


def _row_rollback_references(
    public_record: dict[str, Any] | None,
    surface_record: dict[str, Any] | None,
) -> list[str]:
    refs: list[str] = []
    if public_record is not None:
        refs.append(str(public_record.get("rollback_ref", "rollback:public-source-preview-only")))
    if surface_record is not None:
        refs.append(str(surface_record.get("rollback_ref", "rollback:devhub-surface-preview-only")))
    if not refs:
        refs.append("rollback:placeholder-no-active-artifact")
    return refs


def _rollback_references(rows: list[dict[str, Any]]) -> list[str]:
    refs: list[str] = []
    for row in rows:
        for ref in row["rollback_references"]:
            if ref not in refs:
                refs.append(ref)
    return refs


def _require_placeholder_list(row: dict[str, Any], key: str) -> list[str]:
    values = _require_string_list(row, key, f"dependency row {row.get('dependency_id', '')}")
    if not any(value.startswith("placeholder:") for value in values):
        raise ValueError(f"dependency row {row.get('dependency_id', '')} missing {key} placeholder")
    return values


def validate_rehearsal(rehearsal: Any) -> None:
    """Reject rehearsal packets that are incomplete or imply unsafe side effects."""

    if not isinstance(rehearsal, dict):
        raise ValueError("rehearsal packet must be an object")
    _reject_forbidden_payload(rehearsal, "combined rehearsal")

    if rehearsal.get("rehearsal_id") != REHEARSAL_ID:
        raise ValueError(f"rehearsal_id must be {REHEARSAL_ID!r}")
    if rehearsal.get("mode") != "fixture_first_offline_rehearsal":
        raise ValueError("rehearsal mode must be fixture_first_offline_rehearsal")
    if rehearsal.get("mutates_active_artifacts") is not False:
        raise ValueError("combined rehearsal must explicitly set mutates_active_artifacts to false")

    consumes = rehearsal.get("consumes")
    if consumes != [EXPECTED_PUBLIC_PREVIEW_ID, EXPECTED_DEVHUB_PREVIEW_ID]:
        raise ValueError("combined rehearsal must consume the expected public and DevHub previews")

    rows = rehearsal.get("dependency_rows")
    if not isinstance(rows, list) or not rows:
        raise ValueError("combined rehearsal must include non-empty dependency_rows")

    for index, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            raise ValueError(f"dependency_rows[{index}] must be an object")
        if row.get("dependency_order") != index:
            raise ValueError(f"dependency row {index} has a non-deterministic dependency_order")
        _require_non_empty_string(row, "dependency_id", f"dependency row {index}")
        _require_placeholder_list(row, "source_to_surface_linkage_placeholders")
        _require_placeholder_list(row, "conflict_hold_placeholders")
        reviewer_decisions = _require_placeholder_list(row, "reviewer_decision_placeholders")
        if reviewer_decisions != REQUIRED_REVIEWER_DECISIONS:
            raise ValueError(f"dependency row {index} must carry pending reviewer decision placeholders")
        _require_string_list(row, "rollback_references", f"dependency row {index}")

        public_patch = row.get("public_source_patch")
        surface_patch = row.get("devhub_surface_patch")
        if not isinstance(public_patch, dict):
            raise ValueError(f"dependency row {index} missing public_source_patch")
        if not isinstance(surface_patch, dict):
            raise ValueError(f"dependency row {index} missing devhub_surface_patch")
        _require_non_empty_string(public_patch, "source_patch_id", f"dependency row {index} public patch")
        _require_non_empty_string(surface_patch, "surface_patch_id", f"dependency row {index} DevHub patch")
        if surface_patch.get("requires_attendance") is not True:
            raise ValueError(f"dependency row {index} DevHub patch must require attendance")

    rollback_references = rehearsal.get("rollback_references")
    if not isinstance(rollback_references, list) or not rollback_references:
        raise ValueError("combined rehearsal must include top-level rollback_references")
    if any(not isinstance(ref, str) or not ref.strip() for ref in rollback_references):
        raise ValueError("top-level rollback_references must be non-empty strings")

    if rehearsal.get("exact_offline_validation_commands") != EXACT_OFFLINE_VALIDATION_COMMANDS:
        raise ValueError("combined rehearsal exact_offline_validation_commands drifted")


def _reject_forbidden_payload(value: Any, context: str) -> None:
    _walk_forbidden(value, context, [])


def _walk_forbidden(value: Any, context: str, path: list[str]) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            if not isinstance(key, str):
                raise ValueError(f"{context} contains non-string key at {'.'.join(path) or ''}")
            lowered_key = key.lower()
            if any(fragment in lowered_key for fragment in FORBIDDEN_ARTIFACT_KEY_FRAGMENTS):
                raise ValueError(f"{context} contains forbidden artifact key {'.'.join(path + [key])}")
            if lowered_key in ACTIVE_MUTATION_FLAG_KEYS and nested is not False:
                raise ValueError(f"{context} contains active artifact or prompt mutation flag {'.'.join(path + [key])}")
            _walk_forbidden(nested, context, path + [key])
        return

    if isinstance(value, list):
        for index, nested in enumerate(value):
            _walk_forbidden(nested, context, path + [str(index)])
        return

    if isinstance(value, str):
        lowered_value = " ".join(value.lower().split())
        for phrase in FORBIDDEN_CLAIM_PHRASES:
            if phrase in lowered_value and not _is_negative_or_fixture_statement(lowered_value):
                raise ValueError(f"{context} contains live network or DevHub access claim at {'.'.join(path)}")
        for phrase in FORBIDDEN_ACTION_LANGUAGE:
            if phrase in lowered_value:
                raise ValueError(f"{context} contains consequential action language at {'.'.join(path)}")
        for phrase in FORBIDDEN_GUARANTEE_LANGUAGE:
            if phrase in lowered_value:
                raise ValueError(f"{context} contains legal or permitting guarantee language at {'.'.join(path)}")


def _is_negative_or_fixture_statement(value: str) -> bool:
    return (
        value.startswith("no ")
        or "; no " in value
        or " not " in value
        or "fixture" in value
        or "placeholder" in value
    )


def build_rehearsal_from_fixture_paths(public_path: Path, devhub_path: Path) -> dict[str, Any]:
    return build_rehearsal(_read_json(public_path), _read_json(devhub_path))


def main() -> int:
    parser = argparse.ArgumentParser(description=REHEARSAL_ID)
    parser.add_argument("--public-preview", required=True, type=Path)
    parser.add_argument("--devhub-preview", required=True, type=Path)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    rehearsal = build_rehearsal_from_fixture_paths(args.public_preview, args.devhub_preview)
    if args.pretty:
        print(json.dumps(rehearsal, indent=2, sort_keys=True))
    else:
        print(json.dumps(rehearsal, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
