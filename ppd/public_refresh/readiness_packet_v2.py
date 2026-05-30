"""Fixture-first public refresh readiness packet v2.

This module intentionally performs no network access and writes no crawl output. It
turns an inactive release activation checklist into a deterministic readiness
packet that can be reviewed before any public-source refresh is attempted.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
from dataclasses import dataclass
import re
from typing import Any

PACKET_VERSION = "public-refresh-readiness-packet-v2"
EXPECTED_CHECKLIST_VERSION = "inactive-release-activation-checklist-v2"

OFFLINE_VALIDATION_COMMANDS: list[list[str]] = [
    ["python3", "-m", "py_compile", "ppd/public_refresh/readiness_packet_v2.py"],
    ["python3", "-m", "pytest", "ppd/tests/test_public_refresh_readiness_packet_v2.py"],
    ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
]

_REQUIRED_TOP_LEVEL_LISTS = (
    "ordered_public_source_refresh_prerequisites",
    "allowlist_and_robots_review_placeholders",
    "source_freshness_comparison_placeholders",
    "raw_body_non_persistence_attestations",
    "affected_guardrail_review_placeholders",
    "exact_offline_validation_commands",
)
_REQUIRED_COMPARISON_FIELDS = {
    "content_hash",
    "last_seen_at",
    "freshness_status",
    "affected_requirement_ids",
    "affected_guardrail_bundle_ids",
}
_REQUIRED_ATTESTATION_IDS = {"no_raw_public_body_commits", "metadata_only_fixture_scope"}
_MUTATION_DOMAINS = ("source", "process", "requirement", "guardrail", "release_state", "release-state")
_MUTATION_TERMS = ("mutation", "mutated", "write", "update", "active", "enabled", "applied", "changed", "changes")
_ACTIVE_TEXT_VALUES = {"true", "active", "enabled", "applied", "mutated", "changed", "allowed", "yes"}
_FORBIDDEN_PRIVATE_KEYS = {
    "auth_state",
    "authenticated_fact",
    "authenticated_facts",
    "browser_context",
    "browser_state",
    "cookie",
    "cookies",
    "credential",
    "credentials",
    "downloaded_document_path",
    "downloaded_path",
    "har_path",
    "local_path",
    "password",
    "private_fact",
    "private_facts",
    "private_url",
    "raw_body",
    "raw_content",
    "raw_html",
    "session_cookie",
    "session_state",
    "screenshot_path",
    "storage_state",
    "token",
    "trace_path",
}
_FORBIDDEN_KEY_RE = re.compile(
    r"(^|_)(auth[_-]?state|browser[_-]?(artifact|context|state|trace)|downloaded?[_-]?(artifact|document|path|file)|har|private[_-]?(artifact|fact|path|url|value)|raw[_-]?(body|content|crawl|download|html|text)|session[_-]?(artifact|cookie|path|state)|screenshot|storage[_-]?state|trace|warc)(_|$)",
    re.IGNORECASE,
)
_FORBIDDEN_VALUE_RE = re.compile(
    r"(^(file|session|warc|crawl|archive)://|/(tmp|var/folders|private|home)/|\\users\\|\.har$|\.warc(\.gz)?$|trace\.zip$|/raw/|/downloads?/|/sessions?/|raw crawl output|raw response body|downloaded document|private session|browser trace|auth state)",
    re.IGNORECASE,
)
_LIVE_CRAWL_RE = re.compile(
    r"\b(live crawl|live recrawl|crawler (?:ran|executed|captured|downloaded)|network (?:access|crawl) (?:ran|executed|performed)|downloaded live|captured live)\b",
    re.IGNORECASE,
)
_CONSEQUENTIAL_ACTION_RE = re.compile(
    r"\b(submit(?:ted)? (?:a )?permit|submit(?:ted)? application|pay(?:ing|ment)? fees?|schedule(?:d)? inspection|upload(?:ed)? corrections?|certify acknowledgement|purchase(?:d)? permit|cancel(?:led)? permit|withdraw(?:n)? permit|official action completed)\b",
    re.IGNORECASE,
)
_OUTCOME_GUARANTEE_RE = re.compile(
    r"\b(guarantee[sd]?|will be approved|approval is assured|permit will issue|permit must issue|ensures issuance|ensures approval|legally valid|legal outcome|legal compliance guaranteed|no legal risk|cannot be denied|permitting outcome guaranteed)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class PublicRefreshReadinessPacketV2ValidationResult:
    valid: bool
    errors: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return self.valid

    def as_dict(self) -> dict[str, Any]:
        return {"valid": self.valid, "errors": list(self.errors)}


def build_public_refresh_readiness_packet_v2(checklist: dict[str, Any]) -> dict[str, Any]:
    """Build a deterministic offline readiness packet from a checklist fixture."""

    checklist_id = _required_str(checklist, "checklist_id")
    if checklist_id != EXPECTED_CHECKLIST_VERSION:
        raise ValueError(f"expected checklist_id {EXPECTED_CHECKLIST_VERSION!r}, got {checklist_id!r}")

    status = _required_str(checklist, "status")
    if status != "inactive":
        raise ValueError("public refresh readiness packet v2 only consumes inactive checklists")

    activation_items = _required_list(checklist, "activation_items")
    source_groups = _required_list(checklist, "source_groups")
    guardrail_bundles = _required_list(checklist, "affected_guardrail_bundles")

    prerequisites = [_prerequisite_from_item(index, item) for index, item in enumerate(activation_items, start=1)]

    packet = {
        "packet_version": PACKET_VERSION,
        "packet_id": "fixture-first-public-refresh-readiness-v2",
        "source_checklist_id": checklist_id,
        "source_checklist_status": status,
        "release": _required_str(checklist, "release"),
        "generated_from_fixture_at": _required_str(checklist, "generated_at"),
        "network_access": "not_requested",
        "devhub_scope": "not_touched",
        "active_source_registry_changes": "not_allowed",
        "ordered_public_source_refresh_prerequisites": prerequisites,
        "allowlist_and_robots_review_placeholders": [
            {
                "order": index,
                "source_group_id": _required_str(group, "source_group_id"),
                "canonical_hosts": _required_list(group, "canonical_hosts"),
                "allowlist_review_status": "placeholder_pending_human_review",
                "robots_review_status": "placeholder_pending_human_review",
                "review_notes": "Confirm host allowlist and robots directives before any live refresh.",
            }
            for index, group in enumerate(source_groups, start=1)
        ],
        "source_freshness_comparison_placeholders": [
            {
                "order": index,
                "source_group_id": _required_str(group, "source_group_id"),
                "current_manifest_ref": group.get("current_manifest_ref", "placeholder_current_manifest_ref"),
                "candidate_manifest_ref": "placeholder_candidate_manifest_ref",
                "comparison_status": "placeholder_not_run",
                "expected_comparison_fields": [
                    "content_hash",
                    "last_seen_at",
                    "freshness_status",
                    "affected_requirement_ids",
                    "affected_guardrail_bundle_ids",
                ],
            }
            for index, group in enumerate(source_groups, start=1)
        ],
        "raw_body_non_persistence_attestations": [
            {
                "order": 1,
                "attestation_id": "no_raw_public_body_commits",
                "status": "required_before_refresh",
                "statement": "Raw public response bodies, WARC files, screenshots, traces, HAR files, and downloaded documents are not committed by this readiness packet.",
            },
            {
                "order": 2,
                "attestation_id": "metadata_only_fixture_scope",
                "status": "satisfied_by_fixture",
                "statement": "Committed fixtures contain checklist metadata and expected readiness records only.",
            },
        ],
        "affected_guardrail_review_placeholders": [
            {
                "order": index,
                "guardrail_bundle_id": _required_str(bundle, "guardrail_bundle_id"),
                "review_status": "placeholder_pending_refresh_diff",
                "review_reason": _required_str(bundle, "review_reason"),
                "required_before_activation": True,
            }
            for index, bundle in enumerate(guardrail_bundles, start=1)
        ],
        "exact_offline_validation_commands": deepcopy(OFFLINE_VALIDATION_COMMANDS),
    }
    require_public_refresh_readiness_packet_v2(packet)
    return packet


def validate_public_refresh_readiness_packet_v2(packet: Mapping[str, Any]) -> PublicRefreshReadinessPacketV2ValidationResult:
    errors: list[str] = []
    if not isinstance(packet, Mapping):
        return PublicRefreshReadinessPacketV2ValidationResult(False, ("packet must be an object",))

    if packet.get("packet_version") != PACKET_VERSION:
        errors.append(f"packet_version must be {PACKET_VERSION}")
    if packet.get("network_access") != "not_requested":
        errors.append("network_access must be not_requested")
    if packet.get("devhub_scope") != "not_touched":
        errors.append("devhub_scope must be not_touched")
    if packet.get("active_source_registry_changes") != "not_allowed":
        errors.append("active_source_registry_changes must be not_allowed")

    for field in _REQUIRED_TOP_LEVEL_LISTS:
        if not _non_empty_list(packet.get(field)):
            errors.append(f"{field} must be a non-empty list")

    _validate_prerequisites(errors, packet.get("ordered_public_source_refresh_prerequisites"))
    _validate_allowlist_and_robots(errors, packet.get("allowlist_and_robots_review_placeholders"))
    _validate_source_freshness_placeholders(errors, packet.get("source_freshness_comparison_placeholders"))
    _validate_raw_body_attestations(errors, packet.get("raw_body_non_persistence_attestations"))
    _validate_guardrail_placeholders(errors, packet.get("affected_guardrail_review_placeholders"))
    _validate_validation_commands(errors, packet.get("exact_offline_validation_commands"))
    _validate_recursive_safety(errors, packet)
    return PublicRefreshReadinessPacketV2ValidationResult(not errors, tuple(errors))


def require_public_refresh_readiness_packet_v2(packet: Mapping[str, Any]) -> None:
    result = validate_public_refresh_readiness_packet_v2(packet)
    if not result.valid:
        raise ValueError("invalid public refresh readiness packet v2: " + "; ".join(result.errors))


def _validate_prerequisites(errors: list[str], value: Any) -> None:
    for index, item in enumerate(_mapping_sequence(value)):
        prefix = f"ordered_public_source_refresh_prerequisites[{index}]"
        for field in ("checklist_item_id", "title", "source_scope", "readiness_gate", "status"):
            if not _text(item.get(field)):
                errors.append(f"{prefix}.{field} must be present")
        if item.get("offline_only") is not True:
            errors.append(f"{prefix}.offline_only must be true")
        if item.get("blocks_live_refresh_until_resolved") is not True:
            errors.append(f"{prefix}.blocks_live_refresh_until_resolved must be true")


def _validate_allowlist_and_robots(errors: list[str], value: Any) -> None:
    for index, item in enumerate(_mapping_sequence(value)):
        prefix = f"allowlist_and_robots_review_placeholders[{index}]"
        if not _text(item.get("source_group_id")):
            errors.append(f"{prefix}.source_group_id must be present")
        if not _string_list(item.get("canonical_hosts")):
            errors.append(f"{prefix}.canonical_hosts must be non-empty")
        if not _text(item.get("allowlist_review_status")):
            errors.append(f"{prefix}.allowlist_review_status must be present")
        if not _text(item.get("robots_review_status")):
            errors.append(f"{prefix}.robots_review_status must be present")


def _validate_source_freshness_placeholders(errors: list[str], value: Any) -> None:
    for index, item in enumerate(_mapping_sequence(value)):
        prefix = f"source_freshness_comparison_placeholders[{index}]"
        for field in ("source_group_id", "current_manifest_ref", "candidate_manifest_ref", "comparison_status"):
            if not _text(item.get(field)):
                errors.append(f"{prefix}.{field} must be present")
        missing_fields = sorted(_REQUIRED_COMPARISON_FIELDS.difference(_string_list(item.get("expected_comparison_fields"))))
        if missing_fields:
            errors.append(f"{prefix}.expected_comparison_fields missing: {', '.join(missing_fields)}")


def _validate_raw_body_attestations(errors: list[str], value: Any) -> None:
    attestations = _mapping_sequence(value)
    present_ids = {_text(item.get("attestation_id")) for item in attestations}
    for attestation_id in sorted(_REQUIRED_ATTESTATION_IDS.difference(present_ids)):
        errors.append(f"missing raw-body non-persistence attestation: {attestation_id}")
    for index, item in enumerate(attestations):
        prefix = f"raw_body_non_persistence_attestations[{index}]"
        if not _text(item.get("status")):
            errors.append(f"{prefix}.status must be present")
        if not _text(item.get("statement")):
            errors.append(f"{prefix}.statement must be present")


def _validate_guardrail_placeholders(errors: list[str], value: Any) -> None:
    for index, item in enumerate(_mapping_sequence(value)):
        prefix = f"affected_guardrail_review_placeholders[{index}]"
        if not _text(item.get("guardrail_bundle_id")):
            errors.append(f"{prefix}.guardrail_bundle_id must be present")
        if not _text(item.get("review_status")):
            errors.append(f"{prefix}.review_status must be present")
        if item.get("required_before_activation") is not True:
            errors.append(f"{prefix}.required_before_activation must be true")


def _validate_validation_commands(errors: list[str], value: Any) -> None:
    commands = _command_sequence(value)
    if not commands:
        return
    if commands != OFFLINE_VALIDATION_COMMANDS:
        errors.append("exact_offline_validation_commands must match the allowed offline validation command list")


def _validate_recursive_safety(errors: list[str], packet: Mapping[str, Any]) -> None:
    for path, value in _walk(packet):
        key = path.rsplit(".", 1)[-1]
        normalized_key = key.lower().replace("-", "_")
        if normalized_key in _FORBIDDEN_PRIVATE_KEYS and _truthy_or_text(value):
            errors.append(f"{path} must not include private, session, browser, raw, or downloaded artifacts")
        if normalized_key != "raw_body_non_persistence_attestations" and _FORBIDDEN_KEY_RE.search(normalized_key) and _truthy_or_text(value):
            errors.append(f"{path} must not include private, session, browser, raw, or downloaded artifacts")
        if _is_live_crawl_flag(normalized_key, value):
            errors.append(f"{path} must not claim live crawl or network execution")
        if _is_active_mutation_flag(normalized_key, value):
            errors.append(f"{path} must not set active source, process, requirement, guardrail, or release-state mutation flags")
        if isinstance(value, str):
            if not _is_allowed_non_persistence_statement(path) and _FORBIDDEN_VALUE_RE.search(value.strip()):
                errors.append(f"{path} must not reference private, session, browser, raw, or downloaded artifacts")
            if _LIVE_CRAWL_RE.search(value):
                errors.append(f"{path} must not claim live crawl or network execution")
            if _CONSEQUENTIAL_ACTION_RE.search(value):
                errors.append(f"{path} must not use consequential official action language")
            if _OUTCOME_GUARANTEE_RE.search(value):
                errors.append(f"{path} must not guarantee legal or permitting outcomes")


def _prerequisite_from_item(order: int, item: dict[str, Any]) -> dict[str, Any]:
    return {
        "order": order,
        "checklist_item_id": _required_str(item, "item_id"),
        "title": _required_str(item, "title"),
        "source_scope": _required_str(item, "source_scope"),
        "readiness_gate": item.get("readiness_gate", "manual_review_required"),
        "status": "pending_public_refresh_review",
        "offline_only": True,
        "blocks_live_refresh_until_resolved": True,
    }


def _required_str(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"{key} must be a non-empty string")
    return value


def _required_list(data: dict[str, Any], key: str) -> list[Any]:
    value = data.get(key)
    if not isinstance(value, list) or not value:
        raise ValueError(f"{key} must be a non-empty list")
    return value


def _non_empty_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value)


def _mapping_sequence(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _command_sequence(value: Any) -> list[list[str]]:
    if not isinstance(value, list):
        return []
    commands: list[list[str]] = []
    for command in value:
        if not isinstance(command, list) or not command:
            return []
        parts = []
        for part in command:
            if not isinstance(part, str) or not part:
                return []
            parts.append(part)
        commands.append(parts)
    return commands


def _string_list(value: Any) -> set[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return set()
    return {item.strip() for item in value if isinstance(item, str) and item.strip()}


def _walk(value: Any, path: str = "packet") -> list[tuple[str, Any]]:
    rows = [(path, value)]
    if isinstance(value, Mapping):
        for key, child in value.items():
            rows.extend(_walk(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            rows.extend(_walk(child, f"{path}[{index}]"))
    return rows


def _is_allowed_non_persistence_statement(path: str) -> bool:
    return ".raw_body_non_persistence_attestations[" in path and path.endswith(".statement")


def _is_live_crawl_flag(normalized_key: str, value: Any) -> bool:
    if normalized_key in {"live_crawl", "live_crawl_performed", "live_crawl_executed", "network_execution"} and value is True:
        return True
    if normalized_key == "network_access" and _text(value).lower() not in {"", "not_requested", "false", "none"}:
        return True
    return False


def _is_active_mutation_flag(normalized_key: str, value: Any) -> bool:
    if normalized_key.startswith("no_active_") or normalized_key.startswith("no_"):
        return False
    if normalized_key == "active_source_registry_changes" and _text(value).lower() != "not_allowed":
        return True
    has_domain = any(domain.replace("-", "_") in normalized_key for domain in _MUTATION_DOMAINS)
    has_mutation_term = any(term in normalized_key for term in _MUTATION_TERMS)
    if not has_domain or not has_mutation_term:
        return False
    if value is True:
        return True
    if isinstance(value, str) and value.strip().lower() in _ACTIVE_TEXT_VALUES:
        return True
    return False


def _truthy_or_text(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return bool(value.strip())
    return value is not None


def _text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()
