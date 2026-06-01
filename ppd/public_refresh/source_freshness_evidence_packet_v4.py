"""Fixture-first public source freshness evidence packet v4.

This module consumes committed SourceRegistry-style rows and ArchiveManifest
placeholder rows only. It performs no crawling, downloading, raw body storage, or
DevHub access. The packet classifies PP&D public sources as stale, changed,
skipped, or unchanged for reviewer evidence and offline validation.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

PACKET_TYPE = "ppd.public_source_freshness_evidence_packet.v4"
PACKET_VERSION = "v4"
EXECUTION_MODE = "fixture_first_committed_registry_and_manifest_placeholders_only"

EXACT_OFFLINE_VALIDATION_COMMANDS: list[list[str]] = [
    ["python3", "-m", "py_compile", "ppd/public_refresh/source_freshness_evidence_packet_v4.py"],
    ["python3", "-m", "py_compile", "ppd/tests/test_source_freshness_evidence_packet_v4.py"],
    ["python3", "-m", "pytest", "ppd/tests/test_source_freshness_evidence_packet_v4.py"],
    ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
]

FALSE_BOUNDARY_FLAGS: tuple[str, ...] = (
    "live_sites_crawled",
    "documents_downloaded",
    "raw_bodies_stored",
    "devhub_opened",
    "authenticated_surfaces_opened",
    "source_registry_mutated",
    "archive_manifest_mutated",
    "official_actions_performed",
)

ALLOWED_STATUSES = frozenset({"stale", "changed", "skipped", "unchanged"})
REVIEW_HOLD_STATUSES = frozenset({"stale", "changed", "skipped"})

PRIVATE_OR_RUNTIME_KEY_MARKERS = (
    "auth_state",
    "auth_token",
    "browser_state",
    "cookie",
    "credential",
    "download_path",
    "downloaded_document",
    "har",
    "local_private_path",
    "password",
    "raw_body",
    "raw_crawl_output",
    "raw_download",
    "screenshot",
    "session_state",
    "storage_state",
    "trace",
    "warc_path",
)

FORBIDDEN_TEXT_MARKERS = (
    "authenticated devhub",
    "auth token",
    "browser session",
    "devhub opened",
    "document downloaded",
    "downloaded document",
    "legal guarantee",
    "live crawl completed",
    "live site crawled",
    "official action completed",
    "permit approval guaranteed",
    "permit will be approved",
    "permitting guarantee",
    "raw body stored",
    "raw crawl output",
    "session artifact",
    "source registry updated",
)


def load_source_freshness_evidence_fixture_v4(path: str | Path) -> dict[str, Any]:
    loaded = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError("source freshness evidence fixture must be a JSON object")
    return loaded


def build_source_freshness_evidence_packet_v4_from_file(path: str | Path) -> dict[str, Any]:
    return build_source_freshness_evidence_packet_v4(load_source_freshness_evidence_fixture_v4(path))


def build_source_freshness_evidence_packet_v4(fixture: Mapping[str, Any]) -> dict[str, Any]:
    _reject_private_runtime_or_forbidden_claims(fixture)
    _validate_fixture_boundaries(fixture)
    registry_rows = _validated_rows(fixture.get("committed_source_registry_rows"), "committed_source_registry_rows")
    manifest_rows = _validated_rows(fixture.get("committed_archive_manifest_placeholders"), "committed_archive_manifest_placeholders")
    manifests_by_source = {_required_text(row, "source_id"): row for row in manifest_rows}

    evidence_rows = []
    for source in registry_rows:
        source_id = _required_text(source, "source_id")
        manifest = manifests_by_source.get(source_id)
        if manifest is None:
            raise ValueError(f"missing archive manifest placeholder for source_id: {source_id}")
        evidence_rows.append(_evidence_row(source, manifest))

    packet = {
        "packet_type": PACKET_TYPE,
        "packet_version": PACKET_VERSION,
        "packet_id": "public-source-freshness-evidence-packet-v4",
        "execution_mode": EXECUTION_MODE,
        "fixture_first": True,
        "input_contract": "committed_source_registry_rows_and_archive_manifest_placeholders_only",
        "boundary_flags": {flag: False for flag in FALSE_BOUNDARY_FLAGS},
        "source_registry_row_refs": [_required_text(row, "row_id") for row in registry_rows],
        "archive_manifest_placeholder_refs": [_required_text(row, "manifest_id") for row in manifest_rows],
        "freshness_evidence_rows": evidence_rows,
        "reviewer_holds": [_reviewer_hold(row) for row in evidence_rows if row["freshness_status"] in REVIEW_HOLD_STATUSES],
        "rollback_notes": [_rollback_note(row) for row in evidence_rows],
        "prohibited_actions": [
            "live_crawling",
            "document_download",
            "raw_body_storage",
            "devhub_access",
            "source_registry_mutation",
            "archive_manifest_mutation",
            "official_action",
        ],
        "exact_offline_validation_commands": [list(command) for command in EXACT_OFFLINE_VALIDATION_COMMANDS],
    }
    assert_valid_source_freshness_evidence_packet_v4(packet)
    return packet


def assert_valid_source_freshness_evidence_packet_v4(packet: Mapping[str, Any]) -> None:
    problems = validate_source_freshness_evidence_packet_v4(packet)
    if problems:
        raise ValueError("invalid public source freshness evidence packet v4: " + "; ".join(problems))


def validate_source_freshness_evidence_packet_v4(packet: Mapping[str, Any]) -> list[str]:
    problems: list[str] = []
    if not isinstance(packet, Mapping):
        return ["packet must be an object"]
    if packet.get("packet_type") != PACKET_TYPE:
        problems.append(f"packet_type must be {PACKET_TYPE}")
    if packet.get("packet_version") != PACKET_VERSION:
        problems.append("packet_version must be v4")
    if packet.get("execution_mode") != EXECUTION_MODE:
        problems.append(f"execution_mode must be {EXECUTION_MODE}")
    if packet.get("fixture_first") is not True:
        problems.append("fixture_first must be true")
    if packet.get("boundary_flags") != {flag: False for flag in FALSE_BOUNDARY_FLAGS}:
        problems.append("boundary_flags must preserve offline no-access no-mutation boundaries")
    if packet.get("exact_offline_validation_commands") != EXACT_OFFLINE_VALIDATION_COMMANDS:
        problems.append("exact_offline_validation_commands must match the allowed offline validation command list")

    rows = _mapping_sequence(packet.get("freshness_evidence_rows"))
    if not rows:
        problems.append("freshness_evidence_rows must be a non-empty list")
    seen_statuses: set[str] = set()
    row_ids: set[str] = set()
    source_registry_refs: set[str] = set()
    archive_manifest_refs: set[str] = set()
    hold_required_ids: set[str] = set()
    rollback_required_ids: set[str] = set()
    for index, row in enumerate(rows):
        prefix = f"freshness_evidence_rows[{index}]"
        row_id = _required_text_or_problem(row, "evidence_id", prefix, problems)
        if row_id:
            row_ids.add(row_id)
            rollback_required_ids.add(row_id)
        status = _required_text_or_problem(row, "freshness_status", prefix, problems)
        if status:
            seen_statuses.add(status)
            if status not in ALLOWED_STATUSES:
                problems.append(f"{prefix}.freshness_status must be stale, changed, skipped, or unchanged")
            if status in REVIEW_HOLD_STATUSES and row_id:
                hold_required_ids.add(row_id)
        for field in (
            "source_id",
            "source_registry_row_id",
            "archive_manifest_placeholder_id",
            "canonical_url",
            "freshness_status_reason",
            "reviewer_hold",
            "rollback_note",
        ):
            _required_text_or_problem(row, field, prefix, problems)
        registry_ref = _text(row.get("source_registry_row_id"))
        if registry_ref:
            source_registry_refs.add(registry_ref)
        manifest_ref = _text(row.get("archive_manifest_placeholder_id"))
        if manifest_ref:
            archive_manifest_refs.add(manifest_ref)
        if not _non_empty_text_sequence(row.get("affected_requirement_ids")):
            problems.append(f"{prefix}.affected_requirement_ids must be a non-empty list")
        if not _valid_citation_placeholders(row.get("citation_placeholders")):
            problems.append(f"{prefix}.citation_placeholders must include citation-placeholder entries")

    missing_statuses = ALLOWED_STATUSES - seen_statuses
    if missing_statuses:
        problems.append("freshness_evidence_rows missing statuses: " + ", ".join(sorted(missing_statuses)))
    _validate_top_level_ref_list(packet.get("source_registry_row_refs"), source_registry_refs, "source_registry_row_refs", problems)
    _validate_top_level_ref_list(packet.get("archive_manifest_placeholder_refs"), archive_manifest_refs, "archive_manifest_placeholder_refs", problems)
    _validate_refs(packet.get("reviewer_holds"), row_ids, "reviewer_holds", problems, required_ids=hold_required_ids)
    _validate_refs(packet.get("rollback_notes"), row_ids, "rollback_notes", problems, required_ids=rollback_required_ids)
    _reject_private_runtime_or_forbidden_claims(packet, problems)
    return problems


def _validate_fixture_boundaries(fixture: Mapping[str, Any]) -> None:
    if fixture.get("fixture_first") is not True:
        raise ValueError("fixture_first must be true")
    for flag in FALSE_BOUNDARY_FLAGS:
        if fixture.get(flag) is not False:
            raise ValueError(f"{flag} must be false")


def _validated_rows(value: Any, field_name: str) -> list[Mapping[str, Any]]:
    rows = _mapping_sequence(value)
    if not rows:
        raise ValueError(f"{field_name} must be a non-empty list")
    seen: set[str] = set()
    for index, row in enumerate(rows):
        prefix = f"{field_name}[{index}]"
        if row.get("committed_placeholder") is not True:
            raise ValueError(f"{prefix}.committed_placeholder must be true")
        row_id = _required_text(row, "row_id" if field_name == "committed_source_registry_rows" else "manifest_id")
        if row_id in seen:
            raise ValueError(f"{prefix} id must be unique")
        seen.add(row_id)
    return rows


def _evidence_row(source: Mapping[str, Any], manifest: Mapping[str, Any]) -> dict[str, Any]:
    source_id = _required_text(source, "source_id")
    status = _freshness_status(source, manifest)
    reason = _freshness_reason(status, source, manifest)
    return {
        "evidence_id": f"freshness-evidence-v4-{source_id}",
        "source_id": source_id,
        "source_registry_row_id": _required_text(source, "row_id"),
        "archive_manifest_placeholder_id": _required_text(manifest, "manifest_id"),
        "canonical_url": _required_text(source, "canonical_url"),
        "freshness_status": status,
        "freshness_status_reason": reason,
        "citation_placeholders": _citation_placeholders(source, manifest),
        "affected_requirement_ids": _text_sequence(source.get("affected_requirement_ids")),
        "reviewer_hold": _hold_text(status),
        "rollback_note": "Discard this packet and keep committed registry and archive placeholders unchanged if reviewer rejects the evidence.",
    }


def _freshness_status(source: Mapping[str, Any], manifest: Mapping[str, Any]) -> str:
    skipped_reason = str(manifest.get("skipped_reason", "")).strip()
    if skipped_reason:
        return "skipped"
    registry_status = str(source.get("freshness_status", "")).strip().lower()
    if registry_status == "stale":
        return "stale"
    previous_hash = str(manifest.get("previous_content_hash", "")).strip()
    current_hash = str(manifest.get("content_hash", "")).strip()
    if previous_hash and current_hash and previous_hash != current_hash:
        return "changed"
    return "unchanged"


def _freshness_reason(status: str, source: Mapping[str, Any], manifest: Mapping[str, Any]) -> str:
    if status == "skipped":
        return "archive manifest placeholder includes skipped_reason: " + _required_text(manifest, "skipped_reason")
    if status == "stale":
        return "source registry placeholder marks freshness_status as stale"
    if status == "changed":
        return "archive manifest placeholder content_hash differs from previous_content_hash"
    return "archive manifest placeholder hash is unchanged and no skip or stale marker is present"


def _citation_placeholders(source: Mapping[str, Any], manifest: Mapping[str, Any]) -> list[str]:
    citations = _text_sequence(source.get("citation_placeholders")) + _text_sequence(manifest.get("citation_placeholders"))
    if not citations:
        raise ValueError(f"source {source.get('source_id')} must include citation placeholders")
    return citations


def _hold_text(status: str) -> str:
    if status == "unchanged":
        return "no reviewer hold required before carrying unchanged fixture evidence forward"
    return "reviewer must resolve freshness evidence before requirement or guardrail promotion"


def _reviewer_hold(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "hold_id": "hold-" + _required_text(row, "evidence_id"),
        "evidence_id": _required_text(row, "evidence_id"),
        "source_id": _required_text(row, "source_id"),
        "hold_reason": _required_text(row, "reviewer_hold"),
        "affected_requirement_ids": _text_sequence(row.get("affected_requirement_ids")),
    }


def _rollback_note(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "rollback_id": "rollback-" + _required_text(row, "evidence_id"),
        "evidence_id": _required_text(row, "evidence_id"),
        "source_id": _required_text(row, "source_id"),
        "note": _required_text(row, "rollback_note"),
    }


def _validate_top_level_ref_list(value: Any, expected_refs: set[str], field_name: str, problems: list[str]) -> None:
    refs = set(_text_sequence(value))
    if not refs:
        problems.append(f"{field_name} must be a non-empty list")
        return
    missing = expected_refs - refs
    extra = refs - expected_refs
    if missing:
        problems.append(f"{field_name} missing references: " + ", ".join(sorted(missing)))
    if extra:
        problems.append(f"{field_name} contains unknown references: " + ", ".join(sorted(extra)))


def _validate_refs(
    value: Any,
    valid_ids: set[str],
    field_name: str,
    problems: list[str],
    *,
    required_ids: set[str] | None = None,
) -> None:
    rows = _mapping_sequence(value)
    if not rows:
        problems.append(f"{field_name} must be a non-empty list")
        return
    seen_ids: set[str] = set()
    for index, row in enumerate(rows):
        evidence_id = row.get("evidence_id")
        if not isinstance(evidence_id, str) or not evidence_id.strip():
            problems.append(f"{field_name}[{index}].evidence_id must be present")
        elif evidence_id not in valid_ids:
            problems.append(f"{field_name}[{index}].evidence_id references unknown evidence row")
        else:
            seen_ids.add(evidence_id)
    if required_ids:
        missing = required_ids - seen_ids
        if missing:
            problems.append(f"{field_name} missing required evidence references: " + ", ".join(sorted(missing)))


def _reject_private_runtime_or_forbidden_claims(value: Any, problems: list[str] | None = None) -> None:
    local: list[str] = []
    for path, item in _walk(value):
        key = path.rsplit(".", 1)[-1].lower()
        if any(marker in key for marker in PRIVATE_OR_RUNTIME_KEY_MARKERS):
            local.append(f"{path} contains private, raw, downloaded, browser, session, or DevHub artifacts")
        if isinstance(item, bool) and item is True and (key.startswith("active_") or "mutation" in key or "mutated" in key):
            local.append(f"{path} contains active mutation flags")
        if isinstance(item, str):
            lowered = item.lower()
            for marker in FORBIDDEN_TEXT_MARKERS:
                if marker in lowered:
                    local.append(f"{path} contains forbidden claim: {marker}")
    if problems is None:
        if local:
            raise ValueError("; ".join(local))
    else:
        problems.extend(local)


def _walk(value: Any, prefix: str = "packet") -> list[tuple[str, Any]]:
    walked: list[tuple[str, Any]] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_prefix = f"{prefix}.{key}"
            walked.append((child_prefix, child))
            walked.extend(_walk(child, child_prefix))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            child_prefix = f"{prefix}[{index}]"
            walked.append((child_prefix, child))
            walked.extend(_walk(child, child_prefix))
    return walked


def _mapping_sequence(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _text_sequence(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _text(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return value.strip()


def _non_empty_text_sequence(value: Any) -> bool:
    return bool(_text_sequence(value))


def _valid_citation_placeholders(value: Any) -> bool:
    citations = _text_sequence(value)
    return bool(citations) and all(item.startswith("citation-placeholder:") for item in citations)


def _required_text(row: Mapping[str, Any], field_name: str) -> str:
    value = row.get(field_name)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be present")
    return value.strip()


def _required_text_or_problem(row: Mapping[str, Any], field_name: str, prefix: str, problems: list[str]) -> str:
    value = row.get(field_name)
    if not isinstance(value, str) or not value.strip():
        problems.append(f"{prefix}.{field_name} must be present")
        return ""
    return value.strip()


__all__ = [
    "PACKET_TYPE",
    "PACKET_VERSION",
    "EXACT_OFFLINE_VALIDATION_COMMANDS",
    "load_source_freshness_evidence_fixture_v4",
    "build_source_freshness_evidence_packet_v4_from_file",
    "build_source_freshness_evidence_packet_v4",
    "validate_source_freshness_evidence_packet_v4",
    "assert_valid_source_freshness_evidence_packet_v4",
]
