"""Validation for stale evidence conflict resolution packet v2.

The packet is fixture-first and metadata-only. It documents how stale source
conflicts were reviewed without claiming a live crawl, DevHub action, official
action completion, or any active mutation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse


REQUIRED_CASE_LISTS = {
    "stale_source_cases": "missing_stale_source_cases",
    "changed_hash_cases": "missing_changed_hash_cases",
    "conflicting_requirement_cases": "missing_conflicting_requirement_cases",
    "missing_document_cases": "missing_missing_document_cases",
    "unsupported_path_cases": "missing_unsupported_path_cases",
    "user_gap_questions": "missing_user_gap_questions",
    "holds_and_refusals": "missing_holds_refusals",
    "next_safe_action_summaries": "missing_next_safe_action_summaries",
    "reviewer_dispositions": "missing_reviewer_dispositions",
}

ALLOWLISTED_PUBLIC_HOSTS = frozenset(
    {
        "www.portland.gov",
        "portland.gov",
        "efiles.portlandoregon.gov",
        "www.oregon.gov",
        "oregon.gov",
        "www.portlandmaps.com",
        "portlandmaps.com",
    }
)

PRIVATE_ARTIFACT_MARKERS = (
    "cookie",
    "cookies",
    "authorization",
    "bearer ",
    "access_token",
    "refresh_token",
    "sessionid",
    "session_id",
    "auth_state",
    "storage_state",
    "localstorage",
    "indexeddb",
    "trace.zip",
    ".har",
    "screenshot",
    "video.webm",
    "devhub_session",
    "browser_context",
    "playwright_trace",
)

RAW_OR_DOWNLOADED_MARKERS = (
    "raw_body",
    "body_html",
    "response_body",
    "downloaded_file",
    "download_path",
    "downloaded_document",
    "local_download",
    "archive_path",
    "warc",
    ".zip",
    ".tar",
    ".gz",
    "/tmp/",
    "/var/folders/",
)

LIVE_OR_DEVHUB_CLAIM_MARKERS = (
    "live crawl",
    "live-crawl",
    "ran crawl",
    "executed crawl",
    "ran scraper",
    "executed scraper",
    "ran processor",
    "executed processor",
    "devhub crawl",
    "devhub login",
    "signed in to devhub",
    "authenticated devhub",
    "browser automation ran",
    "playwright run",
    "selenium run",
)

OFFICIAL_ACTION_COMPLETION_MARKERS = (
    "submitted the application",
    "submission completed",
    "permit submitted",
    "paid the fee",
    "payment completed",
    "scheduled inspection",
    "inspection scheduled",
    "uploaded corrections",
    "corrections uploaded",
    "certified and submitted",
    "official action completed",
)

LEGAL_OR_PERMITTING_GUARANTEE_MARKERS = (
    "guarantee permit",
    "guarantees permit",
    "permit will be approved",
    "approval guaranteed",
    "legal determination",
    "legally sufficient",
    "compliance guaranteed",
    "entitled to approval",
)

ACTIVE_MUTATION_FLAG_NAMES = frozenset(
    {
        "active_mutation",
        "active_registry_mutation",
        "active_requirement_mutation",
        "active_guardrail_mutation",
        "active_document_mutation",
        "active_devhub_mutation",
        "mutates_registry",
        "mutates_requirements",
        "mutates_guardrails",
        "mutates_documents",
        "mutates_devhub",
        "mutation_enabled",
        "write_enabled",
    }
)


@dataclass(frozen=True)
class StaleEvidencePacketFinding:
    code: str
    path: str
    message: str


def validate_packet(packet: dict[str, Any]) -> list[StaleEvidencePacketFinding]:
    """Return all validation findings for a stale evidence packet v2."""

    findings: list[StaleEvidencePacketFinding] = []

    if packet.get("packet_version") != "stale_evidence_conflict_resolution_packet_v2":
        findings.append(
            StaleEvidencePacketFinding(
                "invalid_packet_version",
                "$.packet_version",
                "packet_version must be stale_evidence_conflict_resolution_packet_v2",
            )
        )

    for field_name, code in REQUIRED_CASE_LISTS.items():
        if not _has_nonempty_list(packet, field_name):
            findings.append(
                StaleEvidencePacketFinding(
                    code,
                    f"$.{field_name}",
                    f"{field_name} must contain at least one metadata-only review item",
                )
            )

    _validate_validation_commands(packet, findings)
    _validate_dispositions(packet, findings)

    for path, value in _walk(packet):
        lowered_path = path.lower()
        lowered_value = value.lower() if isinstance(value, str) else ""

        if isinstance(value, str) and _looks_like_url(value):
            findings.extend(_validate_url(path, value))

        if _contains_any(lowered_path, PRIVATE_ARTIFACT_MARKERS) or _contains_any(lowered_value, PRIVATE_ARTIFACT_MARKERS):
            findings.append(
                StaleEvidencePacketFinding(
                    "private_session_or_browser_artifact",
                    path,
                    "packets must not include private, session, browser, trace, screenshot, or auth artifacts",
                )
            )

        if _contains_any(lowered_path, RAW_OR_DOWNLOADED_MARKERS) or _contains_any(lowered_value, RAW_OR_DOWNLOADED_MARKERS):
            findings.append(
                StaleEvidencePacketFinding(
                    "raw_or_downloaded_artifact",
                    path,
                    "packets must not include raw bodies, archives, local downloads, or downloaded documents",
                )
            )

        if _contains_any(lowered_value, LIVE_OR_DEVHUB_CLAIM_MARKERS):
            findings.append(
                StaleEvidencePacketFinding(
                    "live_crawl_or_devhub_claim",
                    path,
                    "packets must not claim live crawl execution or DevHub authenticated activity",
                )
            )

        if _contains_any(lowered_value, OFFICIAL_ACTION_COMPLETION_MARKERS):
            findings.append(
                StaleEvidencePacketFinding(
                    "official_action_completion_claim",
                    path,
                    "packets must not claim submissions, payments, uploads, scheduling, certification, or other official actions completed",
                )
            )

        if _contains_any(lowered_value, LEGAL_OR_PERMITTING_GUARANTEE_MARKERS):
            findings.append(
                StaleEvidencePacketFinding(
                    "legal_or_permitting_guarantee",
                    path,
                    "packets must not guarantee legal sufficiency or permitting outcomes",
                )
            )

        if _field_name(path) in ACTIVE_MUTATION_FLAG_NAMES and bool(value):
            findings.append(
                StaleEvidencePacketFinding(
                    "active_mutation_flag",
                    path,
                    "packets must keep active mutation flags false or absent",
                )
            )

    return findings


def assert_valid_packet(packet: dict[str, Any]) -> None:
    findings = validate_packet(packet)
    if findings:
        details = "; ".join(f"{finding.code} at {finding.path}" for finding in findings)
        raise ValueError(f"invalid stale evidence conflict resolution packet v2: {details}")


def _validate_validation_commands(packet: dict[str, Any], findings: list[StaleEvidencePacketFinding]) -> None:
    commands = packet.get("validation_commands")
    if not isinstance(commands, list) or not commands:
        findings.append(
            StaleEvidencePacketFinding(
                "missing_validation_commands",
                "$.validation_commands",
                "packets must include deterministic offline validation commands",
            )
        )
        return

    for index, command in enumerate(commands):
        path = f"$.validation_commands[{index}]"
        if not isinstance(command, list) or len(command) == 0:
            findings.append(
                StaleEvidencePacketFinding(
                    "invalid_validation_command",
                    path,
                    "each validation command must be a nonempty argv list",
                )
            )
            continue
        if not all(isinstance(part, str) and part.strip() for part in command):
            findings.append(
                StaleEvidencePacketFinding(
                    "invalid_validation_command",
                    path,
                    "validation command argv entries must be nonempty strings",
                )
            )


def _validate_dispositions(packet: dict[str, Any], findings: list[StaleEvidencePacketFinding]) -> None:
    dispositions = packet.get("reviewer_dispositions")
    if not isinstance(dispositions, list):
        return

    for index, disposition in enumerate(dispositions):
        path = f"$.reviewer_dispositions[{index}]"
        if not isinstance(disposition, dict):
            findings.append(
                StaleEvidencePacketFinding(
                    "invalid_reviewer_disposition",
                    path,
                    "reviewer dispositions must be objects",
                )
            )
            continue
        if not _has_text(disposition, "reviewer"):
            findings.append(
                StaleEvidencePacketFinding(
                    "missing_reviewer_disposition_reviewer",
                    path,
                    "each reviewer disposition must name a reviewer",
                )
            )
        if not _has_text(disposition, "disposition"):
            findings.append(
                StaleEvidencePacketFinding(
                    "missing_reviewer_disposition_result",
                    path,
                    "each reviewer disposition must include a disposition result",
                )
            )
        if not _has_nonempty_list(disposition, "evidence_refs"):
            findings.append(
                StaleEvidencePacketFinding(
                    "uncited_reviewer_disposition",
                    path,
                    "each reviewer disposition must cite evidence_refs",
                )
            )


def _has_nonempty_list(packet: dict[str, Any], field_name: str) -> bool:
    return isinstance(packet.get(field_name), list) and bool(packet[field_name])


def _has_text(packet: dict[str, Any], field_name: str) -> bool:
    return isinstance(packet.get(field_name), str) and bool(packet[field_name].strip())


def _walk(value: Any, path: str = "$") -> list[tuple[str, Any]]:
    items: list[tuple[str, Any]] = [(path, value)]
    if isinstance(value, dict):
        for key, child in value.items():
            items.extend(_walk(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            items.extend(_walk(child, f"{path}[{index}]"))
    return items


def _field_name(path: str) -> str:
    tail = path.rsplit(".", 1)[-1]
    return tail.split("[", 1)[0]


def _looks_like_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _validate_url(path: str, value: str) -> list[StaleEvidencePacketFinding]:
    parsed = urlparse(value)
    host = parsed.netloc.lower().split(":", 1)[0]
    lowered = value.lower()
    findings: list[StaleEvidencePacketFinding] = []

    if host not in ALLOWLISTED_PUBLIC_HOSTS:
        findings.append(
            StaleEvidencePacketFinding(
                "unsupported_path_or_host",
                path,
                "packets may only cite allowlisted public Portland source URLs",
            )
        )

    if parsed.query or _contains_any(lowered, PRIVATE_ARTIFACT_MARKERS):
        findings.append(
            StaleEvidencePacketFinding(
                "private_session_or_browser_artifact",
                path,
                "packets must not include query-bearing or session-like URLs",
            )
        )

    return findings


def _contains_any(value: str, markers: tuple[str, ...]) -> bool:
    return any(marker in value for marker in markers)
