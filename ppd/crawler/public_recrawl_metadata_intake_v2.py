"""Validation for public recrawl post-run metadata intake v2 packets.

The intake accepts only commit-safe metadata about public recrawl outcomes. It does
not accept raw crawl artifacts, authenticated material, execution claims, legal
outcome guarantees, or mutation flags for PP&D source/process state.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

PACKET_VERSION = "public-recrawl-post-run-metadata-intake-v2"

ALLOWED_HOSTS = frozenset(
    {
        "www.portland.gov",
        "devhub.portlandoregon.gov",
        "www.portlandoregon.gov",
        "www.portlandmaps.com",
    }
)

CAPTURE_DECISIONS = frozenset({"captured", "capture", "accepted"})
SKIP_DECISIONS = frozenset({"skipped", "skip", "rejected"})
SUPPORTED_DECISIONS = CAPTURE_DECISIONS | SKIP_DECISIONS

AUTHENTICATED_URL_MARKERS = (
    "/login",
    "/signin",
    "/sign-in",
    "/register",
    "/account",
    "/accounts",
    "/my-permits",
    "/mypermits",
    "/dashboard",
    "/payment",
    "/payments",
    "/checkout",
    "/upload",
    "/submit",
    "/schedule",
    "/inspection/schedule",
)

PROHIBITED_KEY_MARKERS = (
    "raw_body",
    "body_bytes",
    "body_text",
    "html_body",
    "response_body",
    "download_path",
    "downloaded_file",
    "archive_path",
    "warc_path",
    "browser_artifact",
    "screenshot",
    "trace",
    "har",
    "cookie",
    "cookies",
    "credential",
    "credentials",
    "local_path",
    "private_path",
)

PROHIBITED_EXECUTION_KEYS = (
    "live_crawl_executed",
    "live_crawl_started",
    "live_crawl_completed",
    "processor_executed",
    "processor_started",
    "processor_completed",
    "executed_processors",
    "crawl_execution",
    "processor_execution",
)

PROHIBITED_GUARANTEE_KEYS = (
    "legal_outcome_guarantee",
    "permitting_outcome_guarantee",
    "approval_guaranteed",
    "permit_guaranteed",
    "guaranteed_outcome",
    "guarantees_approval",
)

PROHIBITED_MUTATION_KEYS = (
    "mutate_sources",
    "source_mutations",
    "update_source_registry",
    "schedule_mutations",
    "update_crawl_schedule",
    "requirement_mutations",
    "process_mutations",
    "guardrail_mutations",
    "prompt_mutations",
    "monitoring_mutations",
    "release_state_mutations",
    "agent_state_mutations",
    "active_source_mutation",
    "active_schedule_mutation",
    "active_requirement_mutation",
    "active_process_mutation",
    "active_guardrail_mutation",
    "active_prompt_mutation",
    "active_monitoring_mutation",
    "active_release_state_mutation",
    "active_agent_state_mutation",
)


class MetadataIntakeV2ValidationError(ValueError):
    """Raised when a public recrawl metadata intake v2 packet is unsafe."""


@dataclass(frozen=True)
class ValidatedUrlDecision:
    """Commit-safe URL decision metadata accepted by intake v2."""

    url: str
    decision: str
    citation_ids: tuple[str, ...]
    redirect_chain: tuple[str, ...] = ()
    content_type: str | None = None
    content_hash: str | None = None
    http_status: int | None = None
    skipped_reason: str | None = None
    skip_evidence_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class ValidatedMetadataPacket:
    """Validated public recrawl metadata packet."""

    packet_version: str
    run_id: str
    captured_urls: tuple[ValidatedUrlDecision, ...]


def validate_public_recrawl_metadata_intake_v2(
    packet: Mapping[str, Any],
) -> ValidatedMetadataPacket:
    """Validate and normalize a public recrawl post-run metadata intake v2 packet.

    The validator is intentionally conservative. It accepts metadata-only packets
    and rejects any field that implies unsafe storage, authenticated crawling,
    processor execution, legal/permitting guarantees, or live mutation of PP&D
    state.
    """

    if not isinstance(packet, Mapping):
        raise MetadataIntakeV2ValidationError("packet must be a mapping")

    _reject_prohibited_keys(packet, path="packet")

    packet_version = _required_string(packet, "packet_version", "packet")
    if packet_version != PACKET_VERSION:
        raise MetadataIntakeV2ValidationError(
            f"packet.packet_version must be {PACKET_VERSION!r}"
        )

    run_id = _required_string(packet, "run_id", "packet")
    captured_urls_value = packet.get("captured_urls")
    if not isinstance(captured_urls_value, Sequence) or isinstance(
        captured_urls_value, (str, bytes, bytearray)
    ):
        raise MetadataIntakeV2ValidationError("packet.captured_urls must be a list")
    if not captured_urls_value:
        raise MetadataIntakeV2ValidationError("packet.captured_urls must not be empty")

    decisions = tuple(
        _validate_url_decision(item, index)
        for index, item in enumerate(captured_urls_value)
    )
    return ValidatedMetadataPacket(
        packet_version=packet_version,
        run_id=run_id,
        captured_urls=decisions,
    )


def _validate_url_decision(value: Any, index: int) -> ValidatedUrlDecision:
    path = f"packet.captured_urls[{index}]"
    if not isinstance(value, Mapping):
        raise MetadataIntakeV2ValidationError(f"{path} must be a mapping")

    _reject_prohibited_keys(value, path=path)

    url = _required_string(value, "url", path)
    _validate_public_allowlisted_url(url, f"{path}.url")

    decision = _required_string(value, "decision", path).lower()
    if decision not in SUPPORTED_DECISIONS:
        raise MetadataIntakeV2ValidationError(
            f"{path}.decision must be one of {sorted(SUPPORTED_DECISIONS)!r}"
        )

    citation_ids = _string_tuple(value.get("decision_citation_ids"), f"{path}.decision_citation_ids")
    if not citation_ids:
        raise MetadataIntakeV2ValidationError(
            f"{path}.decision_citation_ids must cite the captured URL decision"
        )

    if decision in CAPTURE_DECISIONS:
        redirect_chain = _string_tuple(value.get("redirect_chain"), f"{path}.redirect_chain")
        if not redirect_chain:
            raise MetadataIntakeV2ValidationError(
                f"{path}.redirect_chain is required for captured URLs"
            )
        for redirect_index, redirect_url in enumerate(redirect_chain):
            _validate_public_allowlisted_url(
                redirect_url,
                f"{path}.redirect_chain[{redirect_index}]",
            )

        content_type = _required_string(value, "content_type", path)
        content_hash = _required_string(value, "content_hash", path)
        if not content_hash.startswith("sha256:"):
            raise MetadataIntakeV2ValidationError(
                f"{path}.content_hash must be a sha256: digest"
            )
        http_status = _optional_int(value.get("http_status"), f"{path}.http_status")
        return ValidatedUrlDecision(
            url=url,
            decision=decision,
            citation_ids=citation_ids,
            redirect_chain=redirect_chain,
            content_type=content_type,
            content_hash=content_hash,
            http_status=http_status,
        )

    skipped_reason = _required_string(value, "skipped_reason", path)
    skip_evidence_ids = _string_tuple(value.get("skip_evidence_ids"), f"{path}.skip_evidence_ids")
    if not skip_evidence_ids:
        raise MetadataIntakeV2ValidationError(
            f"{path}.skip_evidence_ids must explain skipped URL decisions"
        )
    return ValidatedUrlDecision(
        url=url,
        decision=decision,
        citation_ids=citation_ids,
        skipped_reason=skipped_reason,
        skip_evidence_ids=skip_evidence_ids,
    )


def _validate_public_allowlisted_url(url: str, path: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme != "https":
        raise MetadataIntakeV2ValidationError(f"{path} must use https")
    hostname = (parsed.hostname or "").lower()
    if hostname not in ALLOWED_HOSTS:
        raise MetadataIntakeV2ValidationError(f"{path} host is not PP&D allowlisted")
    lowered_path = parsed.path.lower()
    lowered_query = parsed.query.lower()
    if any(marker in lowered_path for marker in AUTHENTICATED_URL_MARKERS):
        raise MetadataIntakeV2ValidationError(f"{path} appears authenticated or consequential")
    if any(token in lowered_query for token in ("token=", "session=", "auth=", "code=")):
        raise MetadataIntakeV2ValidationError(f"{path} query appears authenticated")


def _reject_prohibited_keys(value: Mapping[str, Any], path: str) -> None:
    for key, child in value.items():
        key_text = str(key).lower()
        if _contains_any(key_text, PROHIBITED_KEY_MARKERS):
            raise MetadataIntakeV2ValidationError(f"{path}.{key} is a prohibited artifact field")
        if key_text in PROHIBITED_EXECUTION_KEYS:
            raise MetadataIntakeV2ValidationError(f"{path}.{key} claims live crawl or processor execution")
        if key_text in PROHIBITED_GUARANTEE_KEYS:
            raise MetadataIntakeV2ValidationError(f"{path}.{key} claims a legal or permitting guarantee")
        if key_text in PROHIBITED_MUTATION_KEYS:
            raise MetadataIntakeV2ValidationError(f"{path}.{key} is an active mutation flag")
        if isinstance(child, Mapping):
            _reject_prohibited_keys(child, f"{path}.{key}")
        elif isinstance(child, Sequence) and not isinstance(child, (str, bytes, bytearray)):
            for index, item in enumerate(child):
                if isinstance(item, Mapping):
                    _reject_prohibited_keys(item, f"{path}.{key}[{index}]")


def _contains_any(text: str, markers: Sequence[str]) -> bool:
    return any(marker in text for marker in markers)


def _required_string(value: Mapping[str, Any], key: str, path: str) -> str:
    result = value.get(key)
    if not isinstance(result, str) or not result.strip():
        raise MetadataIntakeV2ValidationError(f"{path}.{key} must be a non-empty string")
    return result.strip()


def _string_tuple(value: Any, path: str) -> tuple[str, ...]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise MetadataIntakeV2ValidationError(f"{path} must be a list of strings")
    result = tuple(item.strip() for item in value if isinstance(item, str) and item.strip())
    if len(result) != len(value):
        raise MetadataIntakeV2ValidationError(f"{path} must contain only non-empty strings")
    return result


def _optional_int(value: Any, path: str) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise MetadataIntakeV2ValidationError(f"{path} must be an integer when present")
    return value
