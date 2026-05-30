"""Validation for public source recrawl preflight review packet v1.

The packet is an offline reviewer artifact. It must prove that every recrawl
candidate has synthetic request rows, policy reasons, metadata-only capture
placeholders, processor-suite adapter references, freshness/reviewer
placeholders, and validation commands before any public crawl or processor
handoff can run.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

PACKET_VERSION = "public_source_recrawl_preflight_review_packet_v1"

OFFICIAL_ANCHOR_PREFIXES = (
    "https://www.portland.gov/ppd",
    "https://devhub.portlandoregon.gov",
    "https://www.portlandoregon.gov",
    "https://www.portlandmaps.com",
)

SENSITIVE_KEY_FRAGMENTS = (
    "auth_state",
    "authenticated",
    "browser",
    "cookie",
    "credential",
    "har",
    "local_storage",
    "password",
    "private",
    "session",
    "screenshot",
    "storage_state",
    "token",
    "trace",
)

SENSITIVE_VALUE_FRAGMENTS = (
    ".har",
    "auth_state",
    "authenticated artifact",
    "browser-state",
    "cookie",
    "credential",
    "localstorage",
    "private devhub",
    "session",
    "screenshot",
    "storage_state",
    "trace.zip",
)

RAW_ARTIFACT_FRAGMENTS = (
    ".warc",
    "downloaded_data",
    "downloaded document",
    "downloaded pdf",
    "raw body",
    "raw crawl",
    "raw download",
    "raw html",
    "raw pdf",
    "response body",
)

LIVE_CRAWL_CLAIM_FRAGMENTS = (
    "crawl executed",
    "downloaded live",
    "fetched live",
    "live crawl completed",
    "live crawl execution",
    "live network executed",
    "network request performed",
    "recrawl completed",
    "scraped live",
)

LEGAL_OR_OUTCOME_GUARANTEE_FRAGMENTS = (
    "approval guaranteed",
    "guarantee approval",
    "guaranteed permit",
    "legal advice",
    "legal determination",
    "permit will be approved",
    "will pass inspection",
)

CONSEQUENTIAL_DEVHUB_ACTION_FRAGMENTS = (
    "certify acknowledgement",
    "final submit",
    "pay fee",
    "purchase permit",
    "schedule inspection",
    "submit application",
    "submit permit",
    "upload correction",
)

MUTATION_FLAG_NAMES = (
    "active_artifact_mutation",
    "active_prompt_mutation",
    "active_release_state_mutation",
    "active_guardrail_mutation",
    "artifact_mutation_active",
    "prompt_mutation_active",
    "release_state_mutation_active",
    "guardrail_mutation_active",
    "mutates_active_artifacts",
    "mutates_active_prompts",
    "mutates_active_release_state",
    "mutates_active_guardrails",
)

URL_OR_CITATION_KEY_FRAGMENTS = (
    "anchor",
    "citation",
    "canonical_url",
    "source_url",
    "url",
)

REQUIRED_PACKET_PLACEHOLDERS = (
    "freshness_monitor_update_placeholder",
    "reviewer_hold_placeholder",
    "reviewer_approval_placeholder",
)

REQUIRED_ROW_TEXT_FIELDS = (
    "source_id",
    "canonical_url",
    "official_anchor_citation",
    "robots_decision_placeholder",
    "policy_decision_placeholder",
    "raw_body_persistence_exclusion_check",
    "download_exclusion_check",
    "metadata_only_capture_placeholder",
    "processor_suite_adapter_ref",
    "freshness_monitor_update_placeholder",
    "reviewer_hold_placeholder",
    "reviewer_approval_placeholder",
)

REQUIRED_SYNTHETIC_REQUEST_TEXT_FIELDS = (
    "source_id",
    "synthetic_request_id",
    "canonical_url",
    "method",
    "request_metadata_placeholder",
)


@dataclass(frozen=True)
class PacketValidationResult:
    """Result returned by the public recrawl preflight packet validator."""

    valid: bool
    errors: tuple[str, ...]


def validate_public_source_recrawl_preflight_review_packet_v1(
    packet: Mapping[str, Any],
) -> PacketValidationResult:
    """Validate a public source recrawl preflight review packet v1."""

    errors: list[str] = []

    if packet.get("packet_version") != PACKET_VERSION:
        errors.append("packet_version must be public_source_recrawl_preflight_review_packet_v1")

    for field in REQUIRED_PACKET_PLACEHOLDERS:
        if not _has_text(packet.get(field)):
            errors.append(f"{field} is required")

    rows = packet.get("candidate_preflight_rows")
    if not isinstance(rows, Sequence) or isinstance(rows, (str, bytes)) or not rows:
        errors.append("candidate_preflight_rows must contain at least one row")
        rows = ()

    synthetic_rows = packet.get("synthetic_request_rows")
    if not isinstance(synthetic_rows, Sequence) or isinstance(synthetic_rows, (str, bytes)) or not synthetic_rows:
        errors.append("synthetic_request_rows must contain at least one synthetic request row")
        synthetic_rows = ()

    candidate_source_ids: set[str] = set()
    for index, row in enumerate(rows):
        row_path = f"candidate_preflight_rows[{index}]"
        if not isinstance(row, Mapping):
            errors.append(f"{row_path} must be an object")
            continue
        source_id = _validate_candidate_row(row, row_path, errors)
        if source_id:
            candidate_source_ids.add(source_id)

    synthetic_source_ids: set[str] = set()
    for index, row in enumerate(synthetic_rows):
        row_path = f"synthetic_request_rows[{index}]"
        if not isinstance(row, Mapping):
            errors.append(f"{row_path} must be an object")
            continue
        source_id = _validate_synthetic_request_row(row, row_path, errors)
        if source_id:
            synthetic_source_ids.add(source_id)

    for source_id in sorted(candidate_source_ids - synthetic_source_ids):
        errors.append(f"synthetic_request_rows missing source_id {source_id}")

    packet_commands = packet.get("validation_commands")
    if not _is_non_empty_command_list(packet_commands):
        errors.append("validation_commands must include at least one command array")

    _validate_no_active_mutation_flags(packet, errors)
    _validate_no_prohibited_content(packet, errors)

    return PacketValidationResult(valid=not errors, errors=tuple(dict.fromkeys(errors)))


def assert_valid_public_source_recrawl_preflight_review_packet_v1(
    packet: Mapping[str, Any],
) -> None:
    """Raise ValueError when the packet fails v1 validation."""

    result = validate_public_source_recrawl_preflight_review_packet_v1(packet)
    if not result.valid:
        raise ValueError("; ".join(result.errors))


def _validate_candidate_row(row: Mapping[str, Any], row_path: str, errors: list[str]) -> str:
    for field in REQUIRED_ROW_TEXT_FIELDS:
        if not _has_text(row.get(field)):
            errors.append(f"{row_path}.{field} is required")

    allow_reason = row.get("allow_reason")
    skip_reason = row.get("skip_reason")
    if not _has_text(allow_reason) and not _has_text(skip_reason):
        errors.append(f"{row_path} must include allow_reason or skip_reason")

    canonical_url = row.get("canonical_url")
    if _has_text(canonical_url) and not _is_official_anchor(str(canonical_url)):
        errors.append(f"{row_path}.canonical_url must be an official public PP&D anchor")

    citation = row.get("official_anchor_citation")
    if _has_text(citation) and not _is_official_anchor(str(citation)):
        errors.append(f"{row_path}.official_anchor_citation must cite an official public anchor")

    if row.get("metadata_only_capture") is not True:
        errors.append(f"{row_path}.metadata_only_capture must be true")
    if row.get("no_raw_body_persisted") is not True:
        errors.append(f"{row_path}.no_raw_body_persisted must be true")
    if row.get("live_network_invoked") is not False:
        errors.append(f"{row_path}.live_network_invoked must be false")
    if row.get("raw_download_invoked") is not False:
        errors.append(f"{row_path}.raw_download_invoked must be false")

    prerequisites = row.get("processor_handoff_dry_run_prerequisites")
    if not _is_non_empty_text_list(prerequisites):
        errors.append(f"{row_path}.processor_handoff_dry_run_prerequisites must be non-empty")

    row_commands = row.get("validation_commands")
    if row_commands is not None and not _is_non_empty_command_list(row_commands):
        errors.append(f"{row_path}.validation_commands must be command arrays when present")

    source_id = row.get("source_id")
    return source_id.strip() if isinstance(source_id, str) else ""


def _validate_synthetic_request_row(row: Mapping[str, Any], row_path: str, errors: list[str]) -> str:
    for field in REQUIRED_SYNTHETIC_REQUEST_TEXT_FIELDS:
        if not _has_text(row.get(field)):
            errors.append(f"{row_path}.{field} is required")

    method = row.get("method")
    if _has_text(method) and str(method).upper() != "GET":
        errors.append(f"{row_path}.method must be GET")

    canonical_url = row.get("canonical_url")
    if _has_text(canonical_url) and not _is_official_anchor(str(canonical_url)):
        errors.append(f"{row_path}.canonical_url must be an official public PP&D anchor")

    if row.get("synthetic_only") is not True:
        errors.append(f"{row_path}.synthetic_only must be true")
    if row.get("network_invoked") is not False:
        errors.append(f"{row_path}.network_invoked must be false")
    if row.get("body_included") is not False:
        errors.append(f"{row_path}.body_included must be false")

    source_id = row.get("source_id")
    return source_id.strip() if isinstance(source_id, str) else ""


def _validate_no_active_mutation_flags(packet: Mapping[str, Any], errors: list[str]) -> None:
    for path, value in _walk(packet):
        key = path[-1] if path else ""
        if not isinstance(key, str):
            continue
        normalized_key = key.lower()
        is_named_flag = normalized_key in MUTATION_FLAG_NAMES
        is_active_mutation_flag = normalized_key.endswith("_mutation_active")
        is_mutates_active_flag = normalized_key.startswith("mutates_active_")
        if (is_named_flag or is_active_mutation_flag or is_mutates_active_flag) and value is not False:
            errors.append(f"{_format_path(path)} must be false")


def _validate_no_prohibited_content(packet: Mapping[str, Any], errors: list[str]) -> None:
    for path, value in _walk(packet):
        key = path[-1] if path else ""
        normalized_key = str(key).lower()
        if any(fragment in normalized_key for fragment in SENSITIVE_KEY_FRAGMENTS):
            if value not in (False, None, "", [], {}):
                errors.append(f"{_format_path(path)} must not contain private/authenticated/session/browser artifact fields")

        if not isinstance(value, str):
            continue

        normalized_value = value.lower()
        formatted_path = _format_path(path)
        is_url_or_citation = any(fragment in normalized_key for fragment in URL_OR_CITATION_KEY_FRAGMENTS)

        if any(fragment in normalized_value for fragment in SENSITIVE_VALUE_FRAGMENTS):
            errors.append(f"{formatted_path} must not reference private/authenticated/session/browser artifacts")
        if any(fragment in normalized_value for fragment in RAW_ARTIFACT_FRAGMENTS):
            errors.append(f"{formatted_path} must not contain raw crawl/PDF/downloaded data references")
        if any(fragment in normalized_value for fragment in LIVE_CRAWL_CLAIM_FRAGMENTS):
            errors.append(f"{formatted_path} must not claim live crawl execution")
        if any(fragment in normalized_value for fragment in LEGAL_OR_OUTCOME_GUARANTEE_FRAGMENTS):
            errors.append(f"{formatted_path} must not contain legal or permitting outcome guarantees")
        if not is_url_or_citation and any(
            fragment in normalized_value for fragment in CONSEQUENTIAL_DEVHUB_ACTION_FRAGMENTS
        ):
            errors.append(f"{formatted_path} must not contain consequential DevHub action language")


def _walk(value: Any, path: tuple[Any, ...] = ()) -> Iterable[tuple[tuple[Any, ...], Any]]:
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = path + (key,)
            yield child_path, child
            yield from _walk(child, child_path)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child in enumerate(value):
            child_path = path + (index,)
            yield child_path, child
            yield from _walk(child, child_path)


def _format_path(path: tuple[Any, ...]) -> str:
    parts: list[str] = []
    for part in path:
        if isinstance(part, int):
            parts.append(f"[{part}]")
        elif not parts:
            parts.append(str(part))
        else:
            parts.append(f".{part}")
    return "".join(parts) if parts else "packet"


def _has_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_non_empty_text_list(value: Any) -> bool:
    return (
        isinstance(value, Sequence)
        and not isinstance(value, (str, bytes))
        and bool(value)
        and all(_has_text(item) for item in value)
    )


def _is_non_empty_command_list(value: Any) -> bool:
    return (
        isinstance(value, Sequence)
        and not isinstance(value, (str, bytes))
        and bool(value)
        and all(_is_non_empty_text_list(command) for command in value)
    )


def _is_official_anchor(value: str) -> bool:
    return value.startswith(OFFICIAL_ANCHOR_PREFIXES)
