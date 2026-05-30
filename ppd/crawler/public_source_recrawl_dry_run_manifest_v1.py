"""Fixture-first public source recrawl dry-run manifest v1.

This module consumes the offline public source recrawl preflight review packet v1
and emits ordered synthetic request rows. It does not fetch URLs, open DevHub,
download documents, store response bodies, invoke processors, mutate active
source/process/guardrail artifacts, or update prompts.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from ppd.agent_readiness.public_source_recrawl_preflight_review_packet_v1 import (
    assert_valid_public_source_recrawl_preflight_review_packet_v1,
)

MANIFEST_VERSION = "public_source_recrawl_dry_run_manifest_v1"

ALLOWED_HOSTS = {
    "www.portland.gov",
    "devhub.portlandoregon.gov",
    "www.portlandoregon.gov",
    "www.portlandmaps.com",
}

PORTAL_DEFERRED_HOSTS = {
    "devhub.portlandoregon.gov",
}

SUPPORTED_METADATA_CONTENT_TYPES = {
    "text/html": {
        "adapter_id": "processor-suite-adapter:public-html-metadata-only:v1",
        "adapter_module": "ppd.crawler.processor_suite",
        "processor_name": "ipfs-datasets-public-html-archive-adapter",
        "processor_version": "placeholder-version",
    },
    "application/pdf": {
        "adapter_id": "processor-suite-adapter:public-pdf-metadata-only:v1",
        "adapter_module": "ppd.crawler.processor_suite",
        "processor_name": "ipfs-datasets-public-pdf-archive-adapter",
        "processor_version": "placeholder-version",
    },
}

SKIPPED_ADAPTER_REF = {
    "adapter_id": "processor-suite-adapter:metadata-only-skip:v1",
    "adapter_module": "ppd.crawler.processor_suite",
    "processor_name": "no-processor-dry-run-skip",
    "processor_version": "not-applicable",
}

EXPECTED_METADATA_ONLY_CAPTURE_FIELDS = [
    "source_id",
    "requested_url",
    "canonical_url",
    "redirect_chain_placeholder",
    "http_status_placeholder",
    "content_type_placeholder",
    "content_hash_placeholder",
    "etag_placeholder",
    "last_modified_placeholder",
    "capture_started_at_placeholder",
    "capture_finished_at_placeholder",
    "processor_adapter_ref",
    "normalized_document_id_placeholder",
    "skipped_reason",
    "no_raw_body_persisted",
]

OFFLINE_VALIDATION_COMMANDS = [
    ["python3", "-m", "py_compile", "ppd/crawler/public_source_recrawl_dry_run_manifest_v1.py"],
    ["python3", "-m", "pytest", "ppd/tests/test_public_source_recrawl_dry_run_manifest_v1.py"],
    ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
]

FORBIDDEN_TRUE_FLAGS = {
    "network_request_performed",
    "document_download_performed",
    "raw_response_body_stored",
    "devhub_access_performed",
    "processor_invoked",
    "active_source_mutation",
    "active_process_mutation",
    "active_guardrail_mutation",
    "active_prompt_mutation",
    "freshness_monitor_mutation",
}

FORBIDDEN_KEYS_WITH_DATA = {
    "raw_body",
    "raw_response_body",
    "response_body",
    "body_text",
    "html_body",
    "pdf_bytes",
    "archive_artifact_ref",
    "document_path",
    "download_path",
    "trace_path",
    "screenshot_path",
    "storage_state",
    "cookies",
    "token",
    "password",
}

FORBIDDEN_VALUE_FRAGMENTS = (
    "raw response body",
    "raw body persisted",
    "network request performed",
    "download performed",
    "processor invoked",
    "prompt updated",
    "active artifact mutated",
)


class ManifestValidationError(ValueError):
    """Raised when a dry-run manifest violates fixture-first boundaries."""


def load_json(path: Path) -> dict[str, Any]:
    """Load a JSON fixture object from disk."""

    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ManifestValidationError(f"fixture must contain a JSON object: {path}")
    return data


def build_public_source_recrawl_dry_run_manifest_v1(preflight_packet: Mapping[str, Any]) -> dict[str, Any]:
    """Build an ordered, metadata-only dry-run manifest from a preflight packet."""

    assert_valid_public_source_recrawl_preflight_review_packet_v1(preflight_packet)

    candidate_rows = preflight_packet["candidate_preflight_rows"]
    if not isinstance(candidate_rows, Sequence) or isinstance(candidate_rows, (str, bytes)):
        raise ManifestValidationError("candidate_preflight_rows must be a sequence")

    synthetic_request_rows = [
        build_synthetic_request_row(order=index + 1, preflight_row=row)
        for index, row in enumerate(candidate_rows)
    ]

    manifest = {
        "manifest_version": MANIFEST_VERSION,
        "manifest_id": f"{MANIFEST_VERSION}:from:{preflight_packet.get('packet_id', 'unidentified-preflight-packet')}",
        "input_packet_version": preflight_packet.get("packet_version"),
        "input_packet_id": preflight_packet.get("packet_id"),
        "fixture_first": True,
        "side_effect_boundary": {
            "network_requests_allowed": False,
            "document_downloads_allowed": False,
            "raw_response_body_storage_allowed": False,
            "devhub_access_allowed": False,
            "processor_invocation_allowed": False,
            "active_source_mutation_allowed": False,
            "active_process_mutation_allowed": False,
            "active_guardrail_mutation_allowed": False,
            "active_prompt_mutation_allowed": False,
        },
        "synthetic_request_rows": synthetic_request_rows,
        "expected_metadata_only_capture_fields": list(EXPECTED_METADATA_ONLY_CAPTURE_FIELDS),
        "freshness_monitor_update_placeholders": [
            build_freshness_placeholder(row) for row in synthetic_request_rows
        ],
        "reviewer_disposition_placeholders": [
            build_reviewer_placeholder(row) for row in synthetic_request_rows
        ],
        "offline_validation_commands": list(OFFLINE_VALIDATION_COMMANDS),
        "active_source_mutation": False,
        "active_process_mutation": False,
        "active_guardrail_mutation": False,
        "active_prompt_mutation": False,
        "freshness_monitor_mutation": False,
        "network_request_performed": False,
        "document_download_performed": False,
        "raw_response_body_stored": False,
        "devhub_access_performed": False,
        "processor_invoked": False,
    }
    validate_public_source_recrawl_dry_run_manifest_v1(manifest)
    return manifest


def build_public_source_recrawl_dry_run_manifest_v1_from_file(preflight_packet_path: Path) -> dict[str, Any]:
    """Build a dry-run manifest from a committed preflight packet fixture."""

    return build_public_source_recrawl_dry_run_manifest_v1(load_json(preflight_packet_path))


def build_synthetic_request_row(order: int, preflight_row: Any) -> dict[str, Any]:
    if not isinstance(preflight_row, Mapping):
        raise ManifestValidationError(f"candidate_preflight_rows[{order - 1}] must be an object")

    source_id = require_text(preflight_row, "source_id")
    canonical_url = require_text(preflight_row, "canonical_url")
    expected_content_type = infer_expected_content_type(preflight_row)
    skip_reason = resolve_skip_reason(canonical_url, expected_content_type)
    allow_reason = None if skip_reason else "official_anchor_policy_preflight_ready"
    adapter_ref = SKIPPED_ADAPTER_REF if skip_reason else SUPPORTED_METADATA_CONTENT_TYPES[expected_content_type]

    return {
        "request_order": order,
        "synthetic_request_id": f"synthetic-recrawl-request:v1:{order:03d}:{source_id}",
        "source_id": source_id,
        "requested_url": canonical_url,
        "canonical_url": canonical_url,
        "official_anchor_citation": require_text(preflight_row, "official_anchor_citation"),
        "allow_reason": allow_reason,
        "skipped_reason": skip_reason,
        "expected_content_type": expected_content_type,
        "expected_metadata_only_capture": {
            "redirect_chain_placeholder": [],
            "http_status_placeholder": None,
            "content_hash_placeholder": None,
            "etag_placeholder": None,
            "last_modified_placeholder": None,
            "capture_started_at_placeholder": None,
            "capture_finished_at_placeholder": None,
            "normalized_document_id_placeholder": None if skip_reason else f"normalized-document:placeholder:v1:{source_id}",
            "no_raw_body_persisted": True,
        },
        "processor_suite_adapter_ref": dict(adapter_ref),
        "preflight_review_refs": {
            "robots_decision_placeholder": require_text(preflight_row, "robots_decision_placeholder"),
            "policy_decision_placeholder": require_text(preflight_row, "policy_decision_placeholder"),
            "raw_body_persistence_exclusion_check": require_text(
                preflight_row,
                "raw_body_persistence_exclusion_check",
            ),
            "download_exclusion_check": require_text(preflight_row, "download_exclusion_check"),
            "processor_handoff_dry_run_prerequisites": list(
                require_text_sequence(preflight_row, "processor_handoff_dry_run_prerequisites")
            ),
        },
        "reviewer_hold_placeholder": "pending_reviewer_hold_or_release_decision",
        "reviewer_approve_placeholder": require_text(preflight_row, "reviewer_approval_placeholder"),
    }


def infer_expected_content_type(preflight_row: Mapping[str, Any]) -> str:
    explicit = preflight_row.get("expected_content_type")
    if isinstance(explicit, str) and explicit:
        return explicit

    canonical_url = require_text(preflight_row, "canonical_url")
    path = urlparse(canonical_url).path.lower()
    if path.endswith("/download"):
        return "application/pdf"
    return "text/html"


def resolve_skip_reason(canonical_url: str, expected_content_type: str) -> str | None:
    parsed = urlparse(canonical_url)
    if parsed.scheme != "https":
        return "unsupported_scheme"
    if parsed.hostname not in ALLOWED_HOSTS:
        return "outside_allowlist"
    if parsed.hostname in PORTAL_DEFERRED_HOSTS:
        return "portal_access_deferred_no_devhub_access"
    if expected_content_type not in SUPPORTED_METADATA_CONTENT_TYPES:
        return "unsupported_content_type"
    return None


def build_freshness_placeholder(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "source_id": row["source_id"],
        "synthetic_request_id": row["synthetic_request_id"],
        "current_freshness_status_placeholder": "pending_metadata_capture_review",
        "proposed_next_check_placeholder": None,
        "freshness_monitor_mutation_allowed": False,
        "reviewer_required_before_update": True,
    }


def build_reviewer_placeholder(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "source_id": row["source_id"],
        "synthetic_request_id": row["synthetic_request_id"],
        "hold_reason_placeholder": "pending_reviewer_disposition",
        "approve_reason_placeholder": "pending_reviewer_disposition",
        "reviewer_name_placeholder": None,
        "reviewed_at_placeholder": None,
        "approved_for_live_recrawl": False,
    }


def validate_public_source_recrawl_dry_run_manifest_v1(manifest: Mapping[str, Any]) -> None:
    errors: list[str] = []

    if manifest.get("manifest_version") != MANIFEST_VERSION:
        errors.append("manifest_version must be public_source_recrawl_dry_run_manifest_v1")
    if manifest.get("fixture_first") is not True:
        errors.append("fixture_first must be true")

    boundary = manifest.get("side_effect_boundary")
    if not isinstance(boundary, Mapping):
        errors.append("side_effect_boundary is required")
    else:
        for key, value in boundary.items():
            if key.endswith("_allowed") and value is not False:
                errors.append(f"side_effect_boundary.{key} must be false")

    rows = manifest.get("synthetic_request_rows")
    if not isinstance(rows, Sequence) or isinstance(rows, (str, bytes)) or not rows:
        errors.append("synthetic_request_rows must be a non-empty sequence")
    else:
        expected_order = list(range(1, len(rows) + 1))
        actual_order = [row.get("request_order") if isinstance(row, Mapping) else None for row in rows]
        if actual_order != expected_order:
            errors.append("synthetic_request_rows must preserve contiguous request_order values")
        for index, row in enumerate(rows):
            if isinstance(row, Mapping):
                errors.extend(validate_synthetic_request_row(row, index))
            else:
                errors.append(f"synthetic_request_rows[{index}] must be an object")

    freshness_rows = manifest.get("freshness_monitor_update_placeholders")
    if not isinstance(freshness_rows, Sequence) or isinstance(freshness_rows, (str, bytes)) or not freshness_rows:
        errors.append("freshness_monitor_update_placeholders must be non-empty")
    else:
        for index, row in enumerate(freshness_rows):
            if not isinstance(row, Mapping):
                errors.append(f"freshness_monitor_update_placeholders[{index}] must be an object")
            elif row.get("freshness_monitor_mutation_allowed") is not False:
                errors.append(f"freshness_monitor_update_placeholders[{index}] must not allow mutation")

    reviewer_rows = manifest.get("reviewer_disposition_placeholders")
    if not isinstance(reviewer_rows, Sequence) or isinstance(reviewer_rows, (str, bytes)) or not reviewer_rows:
        errors.append("reviewer_disposition_placeholders must be non-empty")
    else:
        for index, row in enumerate(reviewer_rows):
            if not isinstance(row, Mapping):
                errors.append(f"reviewer_disposition_placeholders[{index}] must be an object")
            elif row.get("approved_for_live_recrawl") is not False:
                errors.append(f"reviewer_disposition_placeholders[{index}] must not pre-approve live recrawl")

    commands = manifest.get("offline_validation_commands")
    if not is_command_list(commands):
        errors.append("offline_validation_commands must contain command arrays")
    elif commands != OFFLINE_VALIDATION_COMMANDS:
        errors.append("offline_validation_commands must match the exact v1 command list")

    errors.extend(find_forbidden_claims(manifest))
    if errors:
        raise ManifestValidationError("invalid public source recrawl dry-run manifest v1: " + "; ".join(errors))


def validate_synthetic_request_row(row: Mapping[str, Any], index: int) -> list[str]:
    errors: list[str] = []
    label = f"synthetic_request_rows[{index}]"

    for key in (
        "synthetic_request_id",
        "source_id",
        "requested_url",
        "canonical_url",
        "official_anchor_citation",
        "expected_content_type",
        "processor_suite_adapter_ref",
        "expected_metadata_only_capture",
        "preflight_review_refs",
        "reviewer_hold_placeholder",
        "reviewer_approve_placeholder",
    ):
        if key not in row:
            errors.append(f"{label} missing {key}")

    canonical_url = row.get("canonical_url")
    if isinstance(canonical_url, str):
        parsed = urlparse(canonical_url)
        if parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS:
            errors.append(f"{label}.canonical_url must be an allowlisted https URL")
    else:
        errors.append(f"{label}.canonical_url must be text")

    allow_reason = row.get("allow_reason")
    skipped_reason = row.get("skipped_reason")
    if bool(allow_reason) == bool(skipped_reason):
        errors.append(f"{label} must contain exactly one allow_reason or skipped_reason")

    capture = row.get("expected_metadata_only_capture")
    if not isinstance(capture, Mapping):
        errors.append(f"{label}.expected_metadata_only_capture must be an object")
    elif capture.get("no_raw_body_persisted") is not True:
        errors.append(f"{label}.expected_metadata_only_capture.no_raw_body_persisted must be true")

    adapter = row.get("processor_suite_adapter_ref")
    if not isinstance(adapter, Mapping):
        errors.append(f"{label}.processor_suite_adapter_ref must be an object")
    else:
        for key in ("adapter_id", "adapter_module", "processor_name", "processor_version"):
            if not isinstance(adapter.get(key), str) or not adapter.get(key):
                errors.append(f"{label}.processor_suite_adapter_ref.{key} is required")

    return errors


def find_forbidden_claims(value: Any, path: str = "manifest") -> list[str]:
    errors: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in FORBIDDEN_TRUE_FLAGS and child is not False:
                errors.append(f"{child_path} must be false")
            if key in FORBIDDEN_KEYS_WITH_DATA and child not in (None, "", [], {}):
                errors.append(f"{child_path} must not contain raw, private, or downloaded artifact data")
            errors.extend(find_forbidden_claims(child, child_path))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child in enumerate(value):
            errors.extend(find_forbidden_claims(child, f"{path}[{index}]"))
    elif isinstance(value, str):
        normalized = " ".join(value.lower().split())
        for fragment in FORBIDDEN_VALUE_FRAGMENTS:
            if fragment in normalized:
                errors.append(f"{path} contains forbidden dry-run claim text")
                break
    return errors


def require_text(row: Mapping[str, Any], key: str) -> str:
    value = row.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ManifestValidationError(f"required text field missing: {key}")
    return value


def require_text_sequence(row: Mapping[str, Any], key: str) -> tuple[str, ...]:
    value = row.get(key)
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)) or not value:
        raise ManifestValidationError(f"required text sequence missing: {key}")
    if any(not isinstance(item, str) or not item.strip() for item in value):
        raise ManifestValidationError(f"required text sequence has invalid entries: {key}")
    return tuple(value)


def is_command_list(value: Any) -> bool:
    return (
        isinstance(value, Sequence)
        and not isinstance(value, (str, bytes))
        and bool(value)
        and all(
            isinstance(command, Sequence)
            and not isinstance(command, (str, bytes))
            and bool(command)
            and all(isinstance(part, str) and bool(part) for part in command)
            for command in value
        )
    )


def main() -> None:
    fixture_dir = Path(__file__).parents[1] / "tests" / "fixtures" / "public_source_recrawl_dry_run_manifest_v1"
    manifest = build_public_source_recrawl_dry_run_manifest_v1_from_file(fixture_dir / "preflight_packet.json")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
