"""Validation for process-to-gap-analysis refresh packet v2.

The packet is an evidence refresh artifact. It may describe proposed gap-analysis
updates, blocked actions, and next safe actions, but it must not carry private
case facts, raw authenticated values, execution claims, guarantees, enabled
consequential actions, or mutation instructions.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Iterable


CitationKeys = frozenset(
    {
        "citation",
        "citations",
        "citation_refs",
        "source_evidence_id",
        "source_evidence_ids",
        "source_refs",
        "source_references",
        "sources",
    }
)

ProcessKeys = frozenset(
    {
        "process_id",
        "process_ids",
        "process_ref",
        "process_refs",
        "process_reference",
        "process_references",
    }
)

SourceKeys = frozenset(
    {
        "source_id",
        "source_ids",
        "source_ref",
        "source_refs",
        "source_reference",
        "source_references",
        "source_evidence_id",
        "source_evidence_ids",
        "sources",
    }
)

RationaleKeys = frozenset({"rationale", "reason", "source_backed_reason", "why"})

PrivateFactKeys = frozenset(
    {
        "applicant",
        "applicant_name",
        "applicant_email",
        "applicant_phone",
        "case_fact",
        "case_facts",
        "known_fact",
        "known_facts",
        "owner",
        "owner_name",
        "private_fact",
        "private_facts",
        "project_address",
        "site_address",
        "tenant",
        "tenant_name",
    }
)

RawAuthenticatedKeys = frozenset(
    {
        "access_token",
        "auth_state",
        "authenticated_value",
        "authenticated_values",
        "cookie",
        "cookies",
        "csrf",
        "har",
        "password",
        "raw_auth",
        "raw_authenticated_value",
        "raw_authenticated_values",
        "raw_devhub_value",
        "raw_value",
        "raw_values",
        "refresh_token",
        "session",
        "session_id",
        "token",
        "trace",
    }
)

MutationFlagKeys = frozenset(
    {
        "agent_state_mutation",
        "agent_state_mutation_enabled",
        "apply_gap_analysis_update",
        "crawler_mutation_enabled",
        "gap_analysis_mutation",
        "gap_analysis_mutation_enabled",
        "guardrail_mutation",
        "guardrail_mutation_enabled",
        "monitoring_mutation",
        "monitoring_mutation_enabled",
        "mutate_agent_state",
        "mutate_gap_analysis",
        "mutate_guardrails",
        "mutate_monitoring",
        "mutate_process",
        "mutate_prompt",
        "mutate_release_state",
        "process_mutation",
        "process_mutation_enabled",
        "prompt_mutation",
        "prompt_mutation_enabled",
        "release_state_mutation",
        "release_state_mutation_enabled",
        "update_agent_state",
        "update_guardrails",
        "update_monitoring",
        "update_process_model",
        "update_prompts",
        "update_release_state",
    }
)

ExecutionClaimKeys = frozenset(
    {
        "browser_execution",
        "crawler_execution",
        "devhub_execution",
        "executed_browser",
        "executed_crawler",
        "executed_devhub",
        "executed_llm",
        "executed_processor",
        "live_browser_execution",
        "live_crawler_execution",
        "live_devhub_execution",
        "live_execution",
        "live_llm_execution",
        "live_processor_execution",
        "llm_execution",
        "processor_execution",
    }
)

ConsequentialVerbs = frozenset(
    {
        "cancel",
        "certify",
        "pay",
        "purchase",
        "schedule",
        "submit",
        "upload",
        "withdraw",
    }
)

_LOCAL_PATH_RE = re.compile(
    r"(?:file://|(?:^|[\s'\"])(?:/home/|/Users/|/private/|/var/folders/|[A-Za-z]:[\\/]))"
)
_EXECUTION_RE = re.compile(
    r"\b(?:clicked|opened|ran|called|executed|scraped|crawled|processed)\b.{0,80}\b(?:devhub|browser|playwright|llm|crawler|processor)\b|"
    r"\b(?:devhub|browser|playwright|llm|crawler|processor)\b.{0,80}\b(?:clicked|opened|ran|called|executed|scraped|crawled|processed)\b",
    re.IGNORECASE,
)
_GUARANTEE_RE = re.compile(
    r"\b(?:guarantee[ds]?|will be approved|approval is certain|permit will issue|legally compliant|lawful outcome|no legal risk)\b",
    re.IGNORECASE,
)
_PRIVATE_CLASS_RE = re.compile(r"\b(?:private|confidential|restricted|authenticated_private)\b", re.IGNORECASE)


@dataclass(frozen=True)
class PacketValidationResult:
    """Result returned by the packet validator."""

    ok: bool
    errors: tuple[str, ...]


class PacketValidationError(ValueError):
    """Raised when a refresh packet v2 is not safe to consume."""

    def __init__(self, errors: Iterable[str]) -> None:
        self.errors = tuple(errors)
        super().__init__("; ".join(self.errors))


def validate_process_to_gap_analysis_refresh_packet_v2(packet: dict[str, Any]) -> PacketValidationResult:
    """Return validation errors for a process-to-gap-analysis refresh packet v2."""

    errors: list[str] = []
    if not isinstance(packet, dict):
        return PacketValidationResult(False, ("packet must be an object",))

    version = packet.get("version", packet.get("packet_version"))
    if version not in (2, "2", "v2"):
        errors.append("packet version must be v2")

    packet_type = str(packet.get("packet_type", packet.get("type", ""))).strip()
    if packet_type and packet_type != "process_to_gap_analysis_refresh":
        errors.append("packet_type must be process_to_gap_analysis_refresh")

    if not _has_any_nonempty(packet, SourceKeys):
        errors.append("packet must include source references")
    if not _has_any_nonempty(packet, ProcessKeys):
        errors.append("packet must include process references")

    for path, update in _iter_named_dicts(packet, {"gap_analysis_updates", "updates", "proposed_updates"}):
        if not _has_any_nonempty(update, CitationKeys):
            errors.append(f"{path} must include citations")
        if not _has_any_nonempty(update, ProcessKeys):
            errors.append(f"{path} must include a process reference")
        if not _has_any_nonempty(update, SourceKeys):
            errors.append(f"{path} must include a source reference")

    for path, action in _iter_named_dicts(packet, {"blocked_actions", "blocked_action"}):
        if not _has_any_nonempty(action, RationaleKeys):
            errors.append(f"{path} must include blocked-action rationale")

    for path, action in _iter_named_dicts(packet, {"next_safe_actions", "next_safe_action"}):
        if not _has_any_nonempty(action, RationaleKeys):
            errors.append(f"{path} must include next-safe-action rationale")

    for path, key, value in _walk(packet):
        normalized_key = key.lower()
        if normalized_key in PrivateFactKeys:
            errors.append(f"{path} must not include private case facts")
        if normalized_key in RawAuthenticatedKeys:
            errors.append(f"{path} must not include raw authenticated values")
        if normalized_key in ExecutionClaimKeys and bool(value):
            errors.append(f"{path} must not claim live execution")
        if normalized_key in MutationFlagKeys and bool(value):
            errors.append(f"{path} must not enable active mutation")
        if normalized_key == "privacy_classification" and isinstance(value, str) and _PRIVATE_CLASS_RE.search(value):
            errors.append(f"{path} must not include private case facts")
        if isinstance(value, str):
            if _LOCAL_PATH_RE.search(value):
                errors.append(f"{path} must not include local private document paths")
            if _EXECUTION_RE.search(value):
                errors.append(f"{path} must not claim live execution")
            if _GUARANTEE_RE.search(value):
                errors.append(f"{path} must not guarantee legal or permitting outcomes")

    for path, action in _iter_action_dicts(packet):
        if _is_enabled_consequential_action(action):
            errors.append(f"{path} must not enable consequential actions")

    return PacketValidationResult(not errors, tuple(dict.fromkeys(errors)))


def assert_valid_process_to_gap_analysis_refresh_packet_v2(packet: dict[str, Any]) -> None:
    """Raise PacketValidationError when the refresh packet is unsafe."""

    result = validate_process_to_gap_analysis_refresh_packet_v2(packet)
    if not result.ok:
        raise PacketValidationError(result.errors)


def _has_any_nonempty(item: dict[str, Any], keys: frozenset[str]) -> bool:
    for key in keys:
        if key in item and _is_nonempty(item[key]):
            return True
    return False


def _is_nonempty(value: Any) -> bool:
    if value is None or value is False:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)
    return True


def _iter_named_dicts(value: Any, names: set[str], path: str = "packet") -> Iterable[tuple[str, dict[str, Any]]]:
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in names:
                if isinstance(child, dict):
                    yield child_path, child
                elif isinstance(child, list):
                    for index, item in enumerate(child):
                        if isinstance(item, dict):
                            yield f"{child_path}[{index}]", item
            yield from _iter_named_dicts(child, names, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _iter_named_dicts(child, names, f"{path}[{index}]")


def _iter_action_dicts(value: Any, path: str = "packet") -> Iterable[tuple[str, dict[str, Any]]]:
    if isinstance(value, dict):
        lower_keys = {key.lower() for key in value}
        if lower_keys & {"action", "action_type", "verb", "enabled", "consequential", "requires_exact_confirmation"}:
            yield path, value
        for key, child in value.items():
            yield from _iter_action_dicts(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _iter_action_dicts(child, f"{path}[{index}]")


def _is_enabled_consequential_action(action: dict[str, Any]) -> bool:
    if not bool(action.get("enabled", action.get("is_enabled", False))):
        return False
    action_text = " ".join(
        str(action.get(key, ""))
        for key in ("action", "action_type", "verb", "label", "description")
    ).lower()
    explicit_consequential = bool(action.get("consequential", False)) or str(action.get("risk", "")).lower() == "consequential"
    uses_consequential_verb = any(re.search(rf"\b{re.escape(verb)}\b", action_text) for verb in ConsequentialVerbs)
    return explicit_consequential or uses_consequential_verb


def _walk(value: Any, path: str = "packet") -> Iterable[tuple[str, str, Any]]:
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            yield child_path, str(key), child
            yield from _walk(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk(child, f"{path}[{index}]")
