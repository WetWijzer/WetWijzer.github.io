"""Fixture-first PP&D public source freshness review packet v2.

This module intentionally consumes committed JSON fixtures only. It does not crawl,
download, persist response bodies, automate DevHub, or mutate active PP&D sources,
requirements, guardrails, prompts, contracts, or release state.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


PACKET_VERSION = "public-source-freshness-review-packet-v2"

OFFICIAL_PPD_ANCHORS: tuple[tuple[str, str], ...] = (
    ("ppd_bureau_landing_page", "https://www.portland.gov/ppd"),
    ("online_permitting_tools_overview", "https://www.portland.gov/ppd/how-use-online-permitting-tools"),
    ("devhub_public_portal", "https://devhub.portlandoregon.gov"),
    ("devhub_faq", "https://www.portland.gov/ppd/devhub-faqs"),
    ("devhub_account_sign_in_guide", "https://www.portland.gov/ppd/devhub-sign-guide"),
    ("apply_for_permits", "https://www.portland.gov/ppd/get-permit/apply-permits"),
    ("devhub_permit_application_guide", "https://www.portland.gov/ppd/devhub-guide-submit-permit-application"),
    ("submit_plans_online_single_pdf_process", "https://www.portland.gov/ppd/get-permit/submit-plans-online"),
    ("permit_applications_and_forms_index", "https://www.portland.gov/ppd/brochures-forms-handouts/permits-and-inspections-applications"),
    ("file_naming_standards_pdf_preparation", "https://www.portland.gov/ppd/spp-file-naming-standards-preparing-pdfs"),
    ("fee_payment_guide", "https://www.portland.gov/ppd/documents/how-pay-fees/download"),
    ("portland_maps_public_references", "https://www.portlandmaps.com"),
)

_FORBIDDEN_RAW_BODY_KEYS = {
    "raw_body",
    "body",
    "response_body",
    "html",
    "raw_html",
    "text",
    "raw_text",
    "content",
    "raw_content",
    "bytes",
    "raw_bytes",
    "crawl_output",
    "raw_crawl_output",
    "downloaded_body",
    "downloaded_document_body",
    "raw_downloaded_body_artifact",
    "har",
    "screenshot",
    "trace",
}

_FALSE_SAFETY_FLAGS = (
    "live_crawl_performed",
    "documents_downloaded",
    "raw_bodies_persisted",
    "raw_downloaded_body_artifacts_present",
    "crawl_output_persisted",
    "devhub_automation_performed",
    "unauthenticated_devhub_automation_claimed",
    "authenticated_devhub_automation_claimed",
    "legal_or_permitting_guarantees_made",
    "legal_guarantee_claimed",
    "permitting_guarantee_claimed",
    "permit_approval_guaranteed",
    "active_sources_mutated",
    "active_requirements_mutated",
    "active_guardrails_mutated",
    "active_prompts_mutated",
    "active_contracts_mutated",
    "active_release_state_mutated",
    "active_source_mutation_flag",
    "active_requirement_mutation_flag",
    "active_guardrail_mutation_flag",
    "active_prompt_mutation_flag",
    "active_contract_mutation_flag",
    "active_release_state_mutation_flag",
)


@dataclass(frozen=True)
class SourceRecord:
    source_id: str
    canonical_url: str
    source_type: str
    owning_surface: str
    allowlist_policy: str
    robots_policy: str
    crawl_frequency: str
    processor_policy: str
    privacy_classification: str
    last_seen_at: str | None
    freshness_status: str


@dataclass(frozen=True)
class ManifestRecord:
    manifest_id: str
    source_id: str
    canonical_url: str
    requested_url: str
    http_status: int | None
    content_type: str
    content_hash: str | None
    capture_started_at: str | None
    capture_finished_at: str | None
    processor_name: str
    processor_version: str
    archive_artifact_ref: str | None
    normalized_document_id: str | None
    skipped_reason: str | None
    no_raw_body_persisted: bool


@dataclass(frozen=True)
class PublicSourceFreshnessReviewV2ValidationResult:
    ok: bool
    errors: tuple[str, ...]


def load_json_fixture(path: Path | str) -> Any:
    fixture_path = Path(path)
    with fixture_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _records_from_payload(payload: Any, keys: Sequence[str]) -> list[Mapping[str, Any]]:
    if isinstance(payload, list):
        return [_require_mapping(item) for item in payload]
    if isinstance(payload, dict):
        for key in keys:
            value = payload.get(key)
            if isinstance(value, list):
                return [_require_mapping(item) for item in value]
    raise ValueError(f"fixture must be a list or contain one of: {', '.join(keys)}")


def _require_mapping(value: Any) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise ValueError("fixture records must be JSON objects")
    _reject_raw_body_fields(value)
    return value


def _reject_raw_body_fields(value: Mapping[str, Any], path: str = "record") -> None:
    for key, nested in value.items():
        lowered = key.lower()
        if lowered in _FORBIDDEN_RAW_BODY_KEYS:
            raise ValueError(f"raw crawl/body field is not allowed in freshness fixtures: {path}.{key}")
        if isinstance(nested, dict):
            _reject_raw_body_fields(nested, f"{path}.{key}")
        elif isinstance(nested, list):
            for index, item in enumerate(nested):
                if isinstance(item, dict):
                    _reject_raw_body_fields(item, f"{path}.{key}[{index}]")


def _optional_string(record: Mapping[str, Any], key: str) -> str | None:
    value = record.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"{key} must be a string when present")
    return value


def _string(record: Mapping[str, Any], key: str, default: str = "") -> str:
    value = record.get(key, default)
    if value is None:
        return default
    if not isinstance(value, str):
        raise ValueError(f"{key} must be a string")
    return value


def _optional_int(record: Mapping[str, Any], key: str) -> int | None:
    value = record.get(key)
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{key} must be an integer when present")
    return value


def _bool(record: Mapping[str, Any], key: str, default: bool = False) -> bool:
    value = record.get(key, default)
    if not isinstance(value, bool):
        raise ValueError(f"{key} must be a boolean")
    return value


def parse_source_registry(payload: Any) -> list[SourceRecord]:
    records = _records_from_payload(payload, ("sources", "source_registry"))
    parsed: list[SourceRecord] = []
    for record in records:
        parsed.append(
            SourceRecord(
                source_id=_string(record, "source_id"),
                canonical_url=_string(record, "canonical_url"),
                source_type=_string(record, "source_type"),
                owning_surface=_string(record, "owning_surface"),
                allowlist_policy=_string(record, "allowlist_policy"),
                robots_policy=_string(record, "robots_policy"),
                crawl_frequency=_string(record, "crawl_frequency"),
                processor_policy=_string(record, "processor_policy"),
                privacy_classification=_string(record, "privacy_classification"),
                last_seen_at=_optional_string(record, "last_seen_at"),
                freshness_status=_string(record, "freshness_status", "fixture_only"),
            )
        )
    return parsed


def parse_archive_manifest(payload: Any) -> list[ManifestRecord]:
    records = _records_from_payload(payload, ("captures", "archive_manifest", "manifests"))
    parsed: list[ManifestRecord] = []
    for record in records:
        parsed.append(
            ManifestRecord(
                manifest_id=_string(record, "manifest_id"),
                source_id=_string(record, "source_id"),
                canonical_url=_string(record, "canonical_url"),
                requested_url=_string(record, "requested_url"),
                http_status=_optional_int(record, "http_status"),
                content_type=_string(record, "content_type"),
                content_hash=_optional_string(record, "content_hash"),
                capture_started_at=_optional_string(record, "capture_started_at"),
                capture_finished_at=_optional_string(record, "capture_finished_at"),
                processor_name=_string(record, "processor_name"),
                processor_version=_string(record, "processor_version"),
                archive_artifact_ref=_optional_string(record, "archive_artifact_ref"),
                normalized_document_id=_optional_string(record, "normalized_document_id"),
                skipped_reason=_optional_string(record, "skipped_reason"),
                no_raw_body_persisted=_bool(record, "no_raw_body_persisted"),
            )
        )
    return parsed


def build_public_source_freshness_review_packet_v2(
    source_registry_fixture: Path | str,
    archive_manifest_fixture: Path | str,
) -> dict[str, Any]:
    sources = parse_source_registry(load_json_fixture(source_registry_fixture))
    manifests = parse_archive_manifest(load_json_fixture(archive_manifest_fixture))
    latest_manifest_by_source = _latest_manifest_by_source(manifests)
    ordered_sources = sorted(sources, key=_source_order_key)

    rows = [
        _build_row(source, latest_manifest_by_source.get(source.source_id), index + 1)
        for index, source in enumerate(ordered_sources)
    ]

    packet = {
        "packet_version": PACKET_VERSION,
        "generation_mode": "fixture_first_offline_synthetic_review",
        "live_crawl_performed": False,
        "documents_downloaded": False,
        "raw_bodies_persisted": False,
        "raw_downloaded_body_artifacts_present": False,
        "crawl_output_persisted": False,
        "devhub_automation_performed": False,
        "unauthenticated_devhub_automation_claimed": False,
        "authenticated_devhub_automation_claimed": False,
        "legal_or_permitting_guarantees_made": False,
        "active_sources_mutated": False,
        "active_requirements_mutated": False,
        "active_guardrails_mutated": False,
        "active_prompts_mutated": False,
        "active_contracts_mutated": False,
        "active_release_state_mutated": False,
        "source_registry_fixture": str(source_registry_fixture),
        "archive_manifest_fixture": str(archive_manifest_fixture),
        "official_anchor_order": [
            {"anchor_id": anchor_id, "canonical_url": canonical_url}
            for anchor_id, canonical_url in OFFICIAL_PPD_ANCHORS
        ],
        "ordered_synthetic_freshness_rows": rows,
        "offline_validation_commands": offline_validation_commands(),
        "reviewer_notes": [
            "Rows are derived from committed fixtures only.",
            "Hash-change, requirement-impact, guardrail-impact, and disposition fields are placeholders for human review.",
            "No raw crawl output, downloaded document body, authenticated state, or active PP&D source mutation is represented in this packet.",
        ],
    }
    require_valid_public_source_freshness_review_packet_v2(packet)
    return packet


def validate_public_source_freshness_review_packet_v2(packet: Mapping[str, Any]) -> PublicSourceFreshnessReviewV2ValidationResult:
    errors: list[str] = []
    if not isinstance(packet, Mapping):
        return PublicSourceFreshnessReviewV2ValidationResult(False, ("packet must be a JSON object",))

    if packet.get("packet_version") != PACKET_VERSION:
        errors.append("packet_version must identify public source freshness review packet v2")

    _collect_forbidden_artifact_errors(packet, "packet", errors)
    for flag in _FALSE_SAFETY_FLAGS:
        if _truthy(packet.get(flag)):
            errors.append(f"{flag} must be absent or false")

    commands = packet.get("offline_validation_commands")
    if not _valid_commands(commands):
        errors.append("offline_validation_commands must include at least one exact validation command")

    rows = packet.get("ordered_synthetic_freshness_rows")
    if not isinstance(rows, list) or not rows:
        errors.append("ordered_synthetic_freshness_rows must include at least one freshness row")
        rows = []

    official_anchor_order = packet.get("official_anchor_order")
    if not isinstance(official_anchor_order, list) or not official_anchor_order:
        errors.append("official_anchor_order must include official anchor traces")

    for index, row in enumerate(rows):
        row_path = f"ordered_synthetic_freshness_rows[{index}]"
        if not isinstance(row, Mapping):
            errors.append(f"{row_path} must be a JSON object")
            continue
        _collect_forbidden_artifact_errors(row, row_path, errors)
        _validate_row(row, row_path, errors)

    return PublicSourceFreshnessReviewV2ValidationResult(not errors, tuple(errors))


def require_valid_public_source_freshness_review_packet_v2(packet: Mapping[str, Any]) -> None:
    result = validate_public_source_freshness_review_packet_v2(packet)
    if not result.ok:
        raise ValueError("invalid public source freshness review packet v2: " + "; ".join(result.errors))


def _validate_row(row: Mapping[str, Any], row_path: str, errors: list[str]) -> None:
    if not row.get("source_id"):
        errors.append(f"{row_path}.source_id is required")
    if not row.get("canonical_url"):
        errors.append(f"{row_path}.canonical_url is required")

    trace = row.get("official_anchor_trace")
    if not isinstance(trace, Mapping):
        errors.append(f"{row_path}.official_anchor_trace is required")
    else:
        if not trace.get("anchor_id"):
            errors.append(f"{row_path}.official_anchor_trace.anchor_id is required")
        if not trace.get("canonical_url"):
            errors.append(f"{row_path}.official_anchor_trace.canonical_url is required")
        if trace.get("matched_official_anchor") is not True:
            errors.append(f"{row_path}.official_anchor_trace.matched_official_anchor must be true")

    if row.get("is_official_ppd_anchor") is not True:
        errors.append(f"{row_path}.is_official_ppd_anchor must be true")
    if not row.get("official_anchor_id"):
        errors.append(f"{row_path}.official_anchor_id is required")
    if not row.get("last_seen_placeholder"):
        errors.append(f"{row_path}.last_seen_placeholder is required")

    hash_change = row.get("hash_change_placeholder")
    if not isinstance(hash_change, Mapping):
        errors.append(f"{row_path}.hash_change_placeholder is required")
    else:
        for key in ("status", "previous_content_hash", "current_content_hash", "changed_source_hash"):
            if not hash_change.get(key):
                errors.append(f"{row_path}.hash_change_placeholder.{key} is required")

    if not _non_empty_string_list(row.get("affected_requirement_placeholders")):
        errors.append(f"{row_path}.affected_requirement_placeholders must include placeholder IDs")
    if not _non_empty_string_list(row.get("affected_guardrail_bundle_placeholders")):
        errors.append(f"{row_path}.affected_guardrail_bundle_placeholders must include placeholder IDs")

    disposition = row.get("reviewer_disposition_placeholder")
    if not isinstance(disposition, Mapping):
        errors.append(f"{row_path}.reviewer_disposition_placeholder is required")
    else:
        for key in ("status", "reviewer", "reviewed_at", "notes"):
            if not disposition.get(key):
                errors.append(f"{row_path}.reviewer_disposition_placeholder.{key} is required")

    if not _valid_commands(row.get("offline_validation_commands")):
        errors.append(f"{row_path}.offline_validation_commands must include exact validation commands")


def _collect_forbidden_artifact_errors(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            lowered = str(key).lower()
            if lowered in _FORBIDDEN_RAW_BODY_KEYS:
                errors.append(f"{path}.{key} is a forbidden raw/downloaded/browser artifact field")
            if lowered in _FALSE_SAFETY_FLAGS and _truthy(nested):
                errors.append(f"{path}.{key} must be absent or false")
            _collect_forbidden_artifact_errors(nested, f"{path}.{key}", errors)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _collect_forbidden_artifact_errors(item, f"{path}[{index}]", errors)


def _truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip().lower() not in {"", "false", "no", "none", "null", "0"}
    return bool(value)


def _valid_commands(value: Any) -> bool:
    if not isinstance(value, list) or not value:
        return False
    for command in value:
        if not isinstance(command, list) or not command:
            return False
        if not all(isinstance(part, str) and part for part in command):
            return False
    return True


def _non_empty_string_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(isinstance(item, str) and item for item in value)


def _latest_manifest_by_source(manifests: Iterable[ManifestRecord]) -> dict[str, ManifestRecord]:
    latest: dict[str, ManifestRecord] = {}
    for manifest in manifests:
        existing = latest.get(manifest.source_id)
        if existing is None or _capture_sort_value(manifest) > _capture_sort_value(existing):
            latest[manifest.source_id] = manifest
    return latest


def _capture_sort_value(manifest: ManifestRecord) -> tuple[str, str]:
    return (manifest.capture_finished_at or "", manifest.manifest_id)


def _source_order_key(source: SourceRecord) -> tuple[int, str, str]:
    anchor_index_by_url = {url: index for index, (_anchor_id, url) in enumerate(OFFICIAL_PPD_ANCHORS)}
    anchor_index = anchor_index_by_url.get(source.canonical_url)
    if anchor_index is None:
        return (len(OFFICIAL_PPD_ANCHORS), source.canonical_url, source.source_id)
    return (anchor_index, source.canonical_url, source.source_id)


def _anchor_id_for_url(canonical_url: str) -> str | None:
    for anchor_id, anchor_url in OFFICIAL_PPD_ANCHORS:
        if canonical_url == anchor_url:
            return anchor_id
    return None


def _build_row(source: SourceRecord, manifest: ManifestRecord | None, ordinal: int) -> dict[str, Any]:
    if manifest is not None and not manifest.no_raw_body_persisted:
        raise ValueError(f"archive manifest {manifest.manifest_id} must declare no_raw_body_persisted=true")

    anchor_id = _anchor_id_for_url(source.canonical_url)
    latest_capture_finished_at = manifest.capture_finished_at if manifest else None
    current_content_hash = manifest.content_hash if manifest else None

    return {
        "row_order": ordinal,
        "source_id": source.source_id,
        "canonical_url": source.canonical_url,
        "official_anchor_id": anchor_id,
        "official_anchor_trace": {
            "anchor_id": anchor_id,
            "canonical_url": source.canonical_url,
            "source_id": source.source_id,
            "matched_official_anchor": anchor_id is not None,
        },
        "is_official_ppd_anchor": anchor_id is not None,
        "source_type": source.source_type,
        "owning_surface": source.owning_surface,
        "allowlist_policy": source.allowlist_policy,
        "robots_policy": source.robots_policy,
        "crawl_frequency": source.crawl_frequency,
        "processor_policy": source.processor_policy,
        "privacy_classification": source.privacy_classification,
        "registry_freshness_status": source.freshness_status,
        "registry_last_seen_at": source.last_seen_at,
        "last_seen_placeholder": source.last_seen_at or "PLACEHOLDER_LAST_SEEN_PENDING_OFFLINE_FIXTURE_CAPTURE",
        "latest_manifest_id": manifest.manifest_id if manifest else None,
        "latest_capture_finished_at": latest_capture_finished_at,
        "latest_http_status": manifest.http_status if manifest else None,
        "latest_content_type": manifest.content_type if manifest else None,
        "current_content_hash": current_content_hash,
        "hash_change_placeholder": {
            "status": "PLACEHOLDER_HASH_CHANGE_REVIEW_PENDING",
            "previous_content_hash": "PLACEHOLDER_PREVIOUS_CONTENT_HASH",
            "current_content_hash": current_content_hash or "PLACEHOLDER_CURRENT_CONTENT_HASH_PENDING_CAPTURE",
            "changed_source_hash": "PLACEHOLDER_CHANGED_SOURCE_HASH_BOOLEAN",
        },
        "affected_requirement_placeholders": [
            "PLACEHOLDER_AFFECTED_REQUIREMENT_IDS_PENDING_DIFF_REVIEW"
        ],
        "affected_guardrail_bundle_placeholders": [
            "PLACEHOLDER_AFFECTED_GUARDRAIL_BUNDLE_IDS_PENDING_DIFF_REVIEW"
        ],
        "reviewer_disposition_placeholder": {
            "status": "PLACEHOLDER_REVIEWER_DISPOSITION_PENDING",
            "reviewer": "PLACEHOLDER_REVIEWER",
            "reviewed_at": "PLACEHOLDER_REVIEWED_AT",
            "notes": "PLACEHOLDER_REVIEW_NOTES",
        },
        "offline_validation_commands": offline_validation_commands(),
    }


def offline_validation_commands() -> list[list[str]]:
    return [
        ["python3", "-m", "py_compile", "ppd/extraction/public_source_freshness_review_v2.py"],
        ["python3", "-m", "unittest", "ppd.tests.test_public_source_freshness_review_v2"],
        ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
    ]


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the PP&D public source freshness review packet v2 from fixtures.")
    parser.add_argument("source_registry_fixture", type=Path)
    parser.add_argument("archive_manifest_fixture", type=Path)
    args = parser.parse_args(argv)
    packet = build_public_source_freshness_review_packet_v2(
        args.source_registry_fixture,
        args.archive_manifest_fixture,
    )
    print(json.dumps(packet, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
