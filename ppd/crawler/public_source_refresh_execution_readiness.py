"""Validation for public source refresh execution readiness packets.

The validator is side-effect free. It checks reviewer-facing readiness packets
before any public source refresh can leave fixture-only review, and rejects
packets that imply live crawling, downloads, processor execution, raw artifact
use, authenticated access, legal outcome guarantees, or active state mutation.
"""

from __future__ import annotations

import re
import shlex
from typing import Any, Mapping, Sequence
from urllib.parse import urlparse


ALLOWED_HOSTS = {
    "www.portland.gov",
    "portland.gov",
    "devhub.portlandoregon.gov",
    "www.portlandoregon.gov",
    "portlandoregon.gov",
    "www.portlandmaps.com",
    "portlandmaps.com",
}

AUTHENTICATED_PATH_MARKERS = (
    "/account",
    "/accounts",
    "/auth",
    "/checkout",
    "/dashboard",
    "/login",
    "/my-permits",
    "/mypermits",
    "/oauth",
    "/payment",
    "/payments",
    "/profile",
    "/register",
    "/schedule",
    "/sign-in",
    "/signin",
    "/submit",
    "/upload",
)

AUTHENTICATED_QUERY_MARKERS = (
    "api_key=",
    "auth=",
    "code=",
    "password=",
    "receipt=",
    "session=",
    "token=",
)

COMMAND_KEYS = {
    "command",
    "command_string",
    "execution_command",
    "operator_command",
    "proposed_command",
    "refresh_command",
    "shell_command",
}

LIVE_COMMAND_TOKENS = {
    "aria2c",
    "curl",
    "fetch",
    "ftp",
    "playwright",
    "requests.get",
    "scrapy",
    "wget",
}

LIVE_COMMAND_TEXT_MARKERS = (
    "download_file",
    "execute processor",
    "fetch(",
    "invoke processor",
    "live_public_scrape",
    "process live",
    "processor_suite",
    "requests.get",
    "save_as",
)

DOWNLOAD_COMMAND_TOKENS = {
    "--output",
    "--remote-name",
    "-O",
    "download",
}

RAW_REFERENCE_KEYS = {
    "archive_artifact_ref",
    "archive_ref",
    "artifact_ref",
    "artifact_uri",
    "download_path",
    "download_ref",
    "downloaded_file_ref",
    "har_ref",
    "raw_artifact_ref",
    "raw_body",
    "raw_body_path",
    "raw_body_ref",
    "screenshot_ref",
    "trace_ref",
    "warc_ref",
}

RAW_REFERENCE_MARKERS = (
    "archive-artifacts/",
    "downloaded-documents/",
    "har://",
    "raw-artifacts/",
    "raw_body",
    "raw-body",
    "trace.zip",
    "warc://",
    ".har",
    ".warc",
)

LEGAL_OR_PERMITTING_GUARANTEE_MARKERS = (
    "approved permit outcome",
    "guaranteed permit approval",
    "guarantees approval",
    "guarantees issuance",
    "legal approval guaranteed",
    "permit approval is guaranteed",
    "permit is guaranteed",
    "permit will be approved",
    "will be legally accepted",
    "will pass plan review",
)

MUTATION_FLAG_KEYS = {
    "active_guardrail_mutation",
    "active_registry_mutation",
    "active_release_state_mutation",
    "active_requirement_mutation",
    "active_schedule_mutation",
    "active_source_mutation",
    "apply_guardrail_update",
    "apply_registry_update",
    "apply_release_state_update",
    "apply_requirement_update",
    "apply_schedule_update",
    "apply_source_update",
    "guardrail_mutation_allowed",
    "guardrail_update_enabled",
    "registry_mutation_allowed",
    "registry_update_enabled",
    "release_state_mutation_allowed",
    "release_state_update_enabled",
    "requirement_mutation_allowed",
    "requirement_update_enabled",
    "schedule_mutation_allowed",
    "schedule_update_enabled",
    "source_mutation_allowed",
    "source_update_enabled",
}

MUTATION_KEY_TOKENS = (
    "guardrail",
    "registry",
    "releasestate",
    "requirement",
    "schedule",
    "source",
)

ACTIVE_MUTATION_VALUES = {
    "1",
    "active",
    "apply",
    "enabled",
    "execute",
    "live",
    "mutate",
    "mutating",
    "true",
    "update",
    "yes",
}

ALLOWLIST_EVIDENCE_KEYS = (
    "allowlist_evidence_refs",
    "allowlist_evidence",
    "policy_evidence_refs",
    "policy_evidence",
    "source_policy_evidence_refs",
)

ROBOTS_EVIDENCE_KEYS = (
    "robots_evidence_refs",
    "robots_evidence",
    "robots_policy_evidence_refs",
    "robots_policy_evidence",
)


class PublicSourceRefreshExecutionReadinessError(ValueError):
    """Raised when an execution readiness packet is incomplete or unsafe."""


def validate_public_source_refresh_execution_readiness_packet(packet: Mapping[str, Any]) -> list[str]:
    """Return deterministic issue codes for a refresh execution readiness packet."""

    issues: list[str] = []
    if packet.get("packet_type") != "ppd_public_source_refresh_execution_readiness":
        issues.append("invalid_packet_type")
    if packet.get("mode") != "metadata_only_execution_readiness_review":
        issues.append("invalid_mode")

    _validate_consumed_packet_refs(packet, issues)
    _validate_launch_gates(packet, issues)
    _validate_go_no_go_decisions(packet, issues)
    _validate_required_list(packet, issues, "operator_prerequisites", "missing_operator_prerequisites")
    _validate_required_list(packet, issues, "abort_triggers", "missing_abort_triggers")
    _validate_required_list(packet, issues, "expected_metadata_only_outputs", "missing_expected_metadata_only_outputs")
    _validate_expected_result_records(packet, issues)
    _validate_source_policy_evidence(packet, issues)
    _validate_reviewer_owners(packet, issues)
    _append_recursive_safety_issues(packet, issues)
    return sorted(set(issues))


def require_public_source_refresh_execution_readiness_packet(packet: Mapping[str, Any]) -> None:
    """Raise if the packet is not safe for execution readiness review."""

    issues = validate_public_source_refresh_execution_readiness_packet(packet)
    if issues:
        raise PublicSourceRefreshExecutionReadinessError(",".join(issues))


def _validate_consumed_packet_refs(packet: Mapping[str, Any], issues: list[str]) -> None:
    refs = [_text(ref) for ref in _items(packet.get("consumed_packet_refs"))]
    if not any(refs):
        issues.append("missing_consumed_packet_refs")
    if any(not ref for ref in refs):
        issues.append("blank_consumed_packet_ref")


def _validate_launch_gates(packet: Mapping[str, Any], issues: list[str]) -> None:
    gates = [gate for gate in _items(packet.get("launch_gates") or packet.get("preflight_gates")) if isinstance(gate, Mapping)]
    if not gates:
        issues.append("missing_launch_gates")
        return
    for gate in gates:
        if not _text(gate.get("gate_id")) and not _text(gate.get("id")):
            issues.append("missing_launch_gate_id")
        citations = _items(gate.get("citation_refs") or gate.get("evidence_refs") or gate.get("source_evidence_ids"))
        if not any(_text(citation) for citation in citations):
            issues.append("uncited_launch_gate")


def _validate_go_no_go_decisions(packet: Mapping[str, Any], issues: list[str]) -> None:
    decisions = [item for item in _items(packet.get("go_no_go_decisions")) if isinstance(item, Mapping)]
    if not decisions:
        issues.append("missing_go_no_go_decisions")
        return
    for decision in decisions:
        if not _text(decision.get("decision")):
            issues.append("missing_go_no_go_decision")
        citations = _items(decision.get("citation_refs") or decision.get("evidence_refs"))
        if not any(_text(citation) for citation in citations):
            issues.append("uncited_go_no_go_decision")


def _validate_required_list(packet: Mapping[str, Any], issues: list[str], key: str, issue: str) -> None:
    values = [_text(item) for item in _items(packet.get(key))]
    if not any(values):
        issues.append(issue)


def _validate_expected_result_records(packet: Mapping[str, Any], issues: list[str]) -> None:
    records = [record for record in _items(packet.get("expected_metadata_only_result_records")) if isinstance(record, Mapping)]
    if not records:
        issues.append("missing_expected_metadata_only_result_records")
        return
    for record in records:
        if not _text(record.get("record_id")) and not _text(record.get("result_id")):
            issues.append("missing_expected_metadata_only_result_record_id")
        if record.get("metadata_only") is not True:
            issues.append("missing_expected_metadata_only_result_records")


def _validate_source_policy_evidence(packet: Mapping[str, Any], issues: list[str]) -> None:
    sources = [source for source in _items(packet.get("source_scope") or packet.get("sources") or packet.get("launch_sources")) if isinstance(source, Mapping)]
    if not sources:
        if not _has_any_evidence(packet, ALLOWLIST_EVIDENCE_KEYS):
            issues.append("missing_allowlist_evidence")
        if not _has_any_evidence(packet, ROBOTS_EVIDENCE_KEYS):
            issues.append("missing_robots_evidence")
        return
    for source in sources:
        if not _has_any_evidence(source, ALLOWLIST_EVIDENCE_KEYS):
            issues.append("missing_allowlist_evidence")
        if not _has_any_evidence(source, ROBOTS_EVIDENCE_KEYS):
            issues.append("missing_robots_evidence")


def _validate_reviewer_owners(packet: Mapping[str, Any], issues: list[str]) -> None:
    owners = packet.get("reviewer_owners") or packet.get("reviewer_owner_fields")
    if not isinstance(owners, Mapping):
        issues.append("missing_reviewer_owners")
        return
    if not _text(owners.get("primary_reviewer")) and not _text(owners.get("reviewer")):
        issues.append("missing_reviewer_owners")
    if not _text(owners.get("execution_owner")) and not _text(owners.get("owner")):
        issues.append("missing_reviewer_owners")


def _append_recursive_safety_issues(value: Any, issues: list[str], parent_key: str = "") -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            key_text = str(key).lower()
            if key_text in RAW_REFERENCE_KEYS and _present(item):
                issues.append("raw_artifact_reference")
            if _is_mutation_key(key_text) and _is_active_mutation_value(item):
                issues.append("active_state_mutation_flag")
            if _is_command_key(key_text) and isinstance(item, str) and _command_fetches_downloads_or_processes_live_sources(item):
                issues.append("command_string_fetches_downloads_or_processes_live_sources")
            _append_recursive_safety_issues(item, issues, key_text)
        return
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for item in value:
            _append_recursive_safety_issues(item, issues, parent_key)
        return
    if isinstance(value, str):
        lowered = value.lower()
        if _is_command_key(parent_key) and _command_fetches_downloads_or_processes_live_sources(value):
            issues.append("command_string_fetches_downloads_or_processes_live_sources")
        if any(marker in lowered for marker in RAW_REFERENCE_MARKERS):
            issues.append("raw_artifact_reference")
        if any(marker in lowered for marker in LEGAL_OR_PERMITTING_GUARANTEE_MARKERS) or _looks_like_outcome_guarantee(lowered):
            issues.append("legal_or_permitting_outcome_guarantee")
        parsed = urlparse(value)
        if parsed.scheme in {"http", "https"}:
            host = parsed.hostname or ""
            path = parsed.path.lower()
            query = parsed.query.lower()
            if host.lower() not in ALLOWED_HOSTS:
                issues.append("non_allowlisted_url")
            if parsed.username or parsed.password or any(marker in path for marker in AUTHENTICATED_PATH_MARKERS) or any(marker in query for marker in AUTHENTICATED_QUERY_MARKERS):
                issues.append("authenticated_url")


def _command_fetches_downloads_or_processes_live_sources(command: str) -> bool:
    lowered = command.lower()
    try:
        tokens = [token.lower() for token in shlex.split(command)]
    except ValueError:
        tokens = lowered.split()
    if any(token in LIVE_COMMAND_TOKENS for token in tokens):
        return True
    if any(token in DOWNLOAD_COMMAND_TOKENS for token in tokens):
        return True
    if "http://" in lowered or "https://" in lowered:
        return True
    return any(marker in lowered for marker in LIVE_COMMAND_TEXT_MARKERS)


def _items(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return bool(value)
    if isinstance(value, Mapping):
        return bool(value)
    return True


def _has_any_evidence(record: Mapping[str, Any], keys: Sequence[str]) -> bool:
    for key in keys:
        value = record.get(key)
        if any(_text(item) for item in _items(value)) or (isinstance(value, Mapping) and bool(value)):
            return True
    return False


def _is_active_mutation_value(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in ACTIVE_MUTATION_VALUES
    return False


def _is_command_key(key: str) -> bool:
    return key in COMMAND_KEYS or key.endswith("command") or "command_" in key


def _is_mutation_key(key: str) -> bool:
    normalized = re.sub(r"[^a-z0-9]", "", key.lower())
    if key in MUTATION_FLAG_KEYS or normalized in {re.sub(r"[^a-z0-9]", "", item) for item in MUTATION_FLAG_KEYS}:
        return True
    if not any(domain in normalized for domain in MUTATION_KEY_TOKENS):
        return False
    return any(marker in normalized for marker in ("active", "allowed", "enabled", "mutation", "update", "write"))


def _looks_like_outcome_guarantee(text: str) -> bool:
    return "guarantee" in text and any(marker in text for marker in ("approval", "approved", "permit", "legal", "accepted", "issuance"))
