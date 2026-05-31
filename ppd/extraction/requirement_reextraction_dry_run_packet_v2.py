"""Validation for requirement re-extraction dry-run packet v2.

The packet is a fixture-first review artifact. It may describe intended
re-extraction deltas and placeholders for reviewer impact analysis, but it must
not contain raw/source artifacts, browser/session data, live crawl claims,
permitting guarantees, or active mutation flags.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence
from urllib.parse import urlparse


PACKET_TYPE = "requirement_reextraction_dry_run_packet_v2"
SCHEMA_VERSION = 2

_REQUIRED_DELTA_PLACEHOLDERS = ("unchanged", "added", "removed", "changed")
_REQUIRED_TOP_LEVEL_COLLECTIONS = {
    "requirement_delta_rows": "missing_requirement_delta_rows",
    "citation_span_placeholders": "missing_citation_span_placeholders",
    "confidence_placeholders": "missing_confidence_placeholders",
    "human_review_placeholders": "missing_human_review_placeholders",
    "affected_process_model_placeholders": "missing_affected_process_model_placeholders",
    "affected_guardrail_placeholders": "missing_affected_guardrail_placeholders",
    "validation_commands": "missing_validation_commands",
}

_PRIVATE_URL_MARKERS = (
    "/account",
    "/admin",
    "/auth",
    "/callback",
    "/checkout",
    "/dashboard",
    "/login",
    "/logout",
    "/my-permits",
    "/oauth",
    "/payment",
    "/profile",
    "/session",
    "/signin",
    "/sign-in",
    "/submit",
    "/upload",
)
_ALLOWED_PUBLIC_HOSTS = {
    "www.portland.gov",
    "portland.gov",
    "devhub.portlandoregon.gov",
    "www.portlandoregon.gov",
    "www.portlandmaps.com",
    "portlandmaps.com",
}
_PRIVATE_OR_RAW_KEY_PARTS = (
    "auth_state",
    "browser",
    "cookie",
    "credential",
    "download",
    "har",
    "local_path",
    "password",
    "private",
    "raw",
    "screenshot",
    "session",
    "storage_state",
    "token",
    "trace",
    "warc",
)
_LIVE_CLAIM_KEY_PARTS = (
    "devhub_claim",
    "devhub_live",
    "live_browser",
    "live_crawl",
    "live_fetch",
    "live_network",
    "live_scrape",
)
_LIVE_CLAIM_TRUE_KEYS = {
    "browser_launched",
    "crawler_invoked",
    "devhub_accessed",
    "devhub_launched",
    "devhub_session_used",
    "fetch_attempted",
    "live_crawl_performed",
    "live_devhub_used",
    "live_network_used",
    "network_actions_performed",
    "processor_invoked",
    "urls_fetched",
}
_MUTATION_TRUE_KEYS = {
    "active_contract_mutation",
    "active_contract_mutation_flag",
    "active_guardrail_mutation",
    "active_guardrail_mutation_flag",
    "active_process_model_mutation",
    "active_process_model_mutation_flag",
    "active_prompt_mutation",
    "active_prompt_mutation_flag",
    "active_release_state_mutation",
    "active_release_state_mutation_flag",
    "active_requirement_mutation",
    "active_requirement_mutation_flag",
    "active_source_mutation",
    "active_source_mutation_flag",
    "apply_to_active",
    "commit_contracts",
    "commit_guardrails",
    "commit_process_models",
    "commit_prompts",
    "commit_requirements",
    "commit_release_state",
    "commit_sources",
    "mutates_active_contracts",
    "mutates_active_guardrails",
    "mutates_active_process_models",
    "mutates_active_prompts",
    "mutates_active_release_state",
    "mutates_active_requirements",
    "mutates_active_sources",
    "promote_to_active",
    "release_state_mutated",
    "write_active_contracts",
    "write_active_guardrails",
    "write_active_process_models",
    "write_active_prompts",
    "write_active_release_state",
    "write_active_requirements",
    "write_active_sources",
}
_GUARANTEE_PHRASES = (
    "guarantee permit approval",
    "guaranteed permit approval",
    "guarantees permit approval",
    "guarantee approval",
    "guaranteed approval",
    "guarantees approval",
    "permit will be approved",
    "approval is guaranteed",
    "issuance is guaranteed",
    "legally sufficient",
    "legal advice",
    "legal conclusion",
    "permitting guarantee",
)


@dataclass(frozen=True)
class RequirementReextractionDryRunPacketV2Finding:
    code: str
    path: str
    message: str


class RequirementReextractionDryRunPacketV2Error(ValueError):
    """Raised when a v2 dry-run packet fails validation."""

    def __init__(self, findings: Sequence[RequirementReextractionDryRunPacketV2Finding]) -> None:
        self.findings = tuple(findings)
        details = "; ".join(f"{item.code} at {item.path}: {item.message}" for item in self.findings)
        super().__init__(details)


def validate_requirement_reextraction_dry_run_packet_v2(
    packet: Mapping[str, Any],
) -> list[RequirementReextractionDryRunPacketV2Finding]:
    """Return deterministic validation findings for a dry-run packet."""

    findings: list[RequirementReextractionDryRunPacketV2Finding] = []
    if not isinstance(packet, Mapping):
        return [
            RequirementReextractionDryRunPacketV2Finding(
                "invalid_packet",
                "$",
                "packet must be an object",
            )
        ]

    if packet.get("packet_type") != PACKET_TYPE:
        findings.append(
            RequirementReextractionDryRunPacketV2Finding(
                "invalid_packet_type",
                "$.packet_type",
                f"packet_type must be {PACKET_TYPE}",
            )
        )
    if packet.get("schema_version") != SCHEMA_VERSION:
        findings.append(
            RequirementReextractionDryRunPacketV2Finding(
                "invalid_schema_version",
                "$.schema_version",
                "schema_version must be 2",
            )
        )
    if packet.get("mode") != "fixture_first_offline_dry_run":
        findings.append(
            RequirementReextractionDryRunPacketV2Finding(
                "not_fixture_first_offline_dry_run",
                "$.mode",
                "mode must be fixture_first_offline_dry_run",
            )
        )

    for key, code in _REQUIRED_TOP_LEVEL_COLLECTIONS.items():
        if not _non_empty_collection(packet.get(key)):
            findings.append(RequirementReextractionDryRunPacketV2Finding(code, f"$.{key}", f"{key} is required"))

    _validate_delta_placeholders(packet, findings)
    _validate_requirement_delta_rows(packet, findings)
    _validate_validation_commands(packet, findings)
    _scan_for_forbidden_content(packet, "$", findings)
    return _dedupe(findings)


def assert_valid_requirement_reextraction_dry_run_packet_v2(packet: Mapping[str, Any]) -> None:
    findings = validate_requirement_reextraction_dry_run_packet_v2(packet)
    if findings:
        raise RequirementReextractionDryRunPacketV2Error(findings)


def _validate_delta_placeholders(
    packet: Mapping[str, Any], findings: list[RequirementReextractionDryRunPacketV2Finding]
) -> None:
    placeholders = packet.get("delta_placeholders")
    if not isinstance(placeholders, Mapping):
        findings.append(
            RequirementReextractionDryRunPacketV2Finding(
                "missing_delta_placeholders",
                "$.delta_placeholders",
                "delta_placeholders must include unchanged, added, removed, and changed placeholders",
            )
        )
        return
    for name in _REQUIRED_DELTA_PLACEHOLDERS:
        if not _truthy(placeholders.get(name)):
            findings.append(
                RequirementReextractionDryRunPacketV2Finding(
                    f"missing_{name}_placeholder",
                    f"$.delta_placeholders.{name}",
                    f"{name} placeholder is required",
                )
            )


def _validate_requirement_delta_rows(
    packet: Mapping[str, Any], findings: list[RequirementReextractionDryRunPacketV2Finding]
) -> None:
    rows = packet.get("requirement_delta_rows")
    if not isinstance(rows, list):
        return
    allowed_kinds = set(_REQUIRED_DELTA_PLACEHOLDERS)
    observed_kinds: set[str] = set()
    for index, row in enumerate(rows):
        path = f"$.requirement_delta_rows[{index}]"
        if not isinstance(row, Mapping):
            findings.append(RequirementReextractionDryRunPacketV2Finding("invalid_requirement_delta_row", path, "row must be an object"))
            continue
        delta_kind = _text(row.get("delta_kind") or row.get("change_type"))
        if delta_kind not in allowed_kinds:
            findings.append(
                RequirementReextractionDryRunPacketV2Finding(
                    "invalid_requirement_delta_kind",
                    path + ".delta_kind",
                    "delta_kind must be unchanged, added, removed, or changed",
                )
            )
        else:
            observed_kinds.add(delta_kind)
        if not _text(row.get("requirement_id")):
            findings.append(
                RequirementReextractionDryRunPacketV2Finding(
                    "missing_requirement_id",
                    path + ".requirement_id",
                    "each delta row must carry a requirement id or placeholder id",
                )
            )
        if not _truthy(row.get("citation_span_placeholder")) and not _truthy(row.get("citation_span_placeholders")):
            findings.append(
                RequirementReextractionDryRunPacketV2Finding(
                    "missing_citation_span_placeholder",
                    path + ".citation_span_placeholder",
                    "each delta row must carry a citation-span placeholder",
                )
            )
        if not _truthy(row.get("confidence_placeholder")):
            findings.append(
                RequirementReextractionDryRunPacketV2Finding(
                    "missing_confidence_placeholder",
                    path + ".confidence_placeholder",
                    "each delta row must carry a confidence placeholder",
                )
            )
        if not _truthy(row.get("human_review_placeholder")):
            findings.append(
                RequirementReextractionDryRunPacketV2Finding(
                    "missing_human_review_placeholder",
                    path + ".human_review_placeholder",
                    "each delta row must carry a human-review placeholder",
                )
            )
        if not _truthy(row.get("affected_process_model_placeholder")):
            findings.append(
                RequirementReextractionDryRunPacketV2Finding(
                    "missing_affected_process_model_placeholder",
                    path + ".affected_process_model_placeholder",
                    "each delta row must carry an affected process-model placeholder",
                )
            )
        if not _truthy(row.get("affected_guardrail_placeholder")):
            findings.append(
                RequirementReextractionDryRunPacketV2Finding(
                    "missing_affected_guardrail_placeholder",
                    path + ".affected_guardrail_placeholder",
                    "each delta row must carry an affected guardrail placeholder",
                )
            )
    for required_kind in sorted(allowed_kinds - observed_kinds):
        findings.append(
            RequirementReextractionDryRunPacketV2Finding(
                f"missing_{required_kind}_delta_row",
                "$.requirement_delta_rows",
                f"at least one {required_kind} delta row is required",
            )
        )


def _validate_validation_commands(
    packet: Mapping[str, Any], findings: list[RequirementReextractionDryRunPacketV2Finding]
) -> None:
    commands = packet.get("validation_commands")
    if not isinstance(commands, list):
        return
    for index, command in enumerate(commands):
        path = f"$.validation_commands[{index}]"
        if not isinstance(command, list) or not command or not all(isinstance(part, str) and part for part in command):
            findings.append(
                RequirementReextractionDryRunPacketV2Finding(
                    "invalid_validation_command",
                    path,
                    "validation commands must be non-empty argv arrays of strings",
                )
            )


def _scan_for_forbidden_content(
    value: Any, path: str, findings: list[RequirementReextractionDryRunPacketV2Finding]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            normalized_key = key_text.lower()
            child_path = f"{path}.{key_text}" if path != "$" else f"$.{key_text}"
            if any(part in normalized_key for part in _PRIVATE_OR_RAW_KEY_PARTS) and _truthy(child):
                findings.append(
                    RequirementReextractionDryRunPacketV2Finding(
                        "forbidden_private_session_browser_raw_or_downloaded_artifact",
                        child_path,
                        "private/session/browser/raw/downloaded artifacts are not allowed in dry-run packets",
                    )
                )
            if (normalized_key in _LIVE_CLAIM_TRUE_KEYS or any(part in normalized_key for part in _LIVE_CLAIM_KEY_PARTS)) and _truthy(child):
                findings.append(
                    RequirementReextractionDryRunPacketV2Finding(
                        "forbidden_live_crawl_or_devhub_claim",
                        child_path,
                        "live crawl, browser, processor, network, or DevHub claims are not allowed",
                    )
                )
            if normalized_key in _MUTATION_TRUE_KEYS and _truthy(child):
                findings.append(
                    RequirementReextractionDryRunPacketV2Finding(
                        "forbidden_active_mutation_flag",
                        child_path,
                        "active source, requirement, process-model, guardrail, prompt, contract, or release-state mutation flags are not allowed",
                    )
                )
            if isinstance(child, str):
                _scan_string(child, child_path, findings)
            _scan_for_forbidden_content(child, child_path, findings)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            child_path = f"{path}[{index}]"
            if isinstance(child, str):
                _scan_string(child, child_path, findings)
            _scan_for_forbidden_content(child, child_path, findings)


def _scan_string(value: str, path: str, findings: list[RequirementReextractionDryRunPacketV2Finding]) -> None:
    lowered = value.lower()
    if any(phrase in lowered for phrase in _GUARANTEE_PHRASES):
        findings.append(
            RequirementReextractionDryRunPacketV2Finding(
                "forbidden_legal_or_permitting_guarantee",
                path,
                "dry-run packets must not make legal conclusions or permitting guarantees",
            )
        )
    if _is_private_or_authenticated_url(value):
        findings.append(
            RequirementReextractionDryRunPacketV2Finding(
                "forbidden_private_or_authenticated_url",
                path,
                "private, authenticated, payment, upload, submit, or non-allowlisted URLs are not allowed",
            )
        )


def _is_private_or_authenticated_url(value: str) -> bool:
    if not value.startswith(("http://", "https://")):
        return False
    parsed = urlparse(value)
    host = parsed.netloc.lower()
    private_text = f"{parsed.path.lower()}?{parsed.query.lower()}"
    if parsed.username or parsed.password:
        return True
    if host and host not in _ALLOWED_PUBLIC_HOSTS:
        return True
    return any(marker in private_text for marker in _PRIVATE_URL_MARKERS)


def _non_empty_collection(value: Any) -> bool:
    if isinstance(value, Mapping):
        return bool(value)
    if isinstance(value, list):
        return bool(value)
    return False


def _truthy(value: Any) -> bool:
    return value not in (None, False, "", [], {})


def _text(value: Any) -> str:
    if isinstance(value, str):
        return value.strip().lower()
    return ""


def _dedupe(
    findings: Sequence[RequirementReextractionDryRunPacketV2Finding],
) -> list[RequirementReextractionDryRunPacketV2Finding]:
    seen: set[tuple[str, str]] = set()
    deduped: list[RequirementReextractionDryRunPacketV2Finding] = []
    for finding in findings:
        key = (finding.code, finding.path)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(finding)
    return deduped
