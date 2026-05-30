"""Validation for draft preview post-release monitoring readiness packet v2.

The packet is intentionally fixture-first and side-effect free. It validates
committed metadata only; it does not run monitors, open DevHub, invoke browsers
or LLMs, crawl sources, process PDFs, or mutate prompt, guardrail, surface,
monitoring, release, or agent state.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import json
import re
from pathlib import Path
from typing import Any

PACKET_TYPE = "draft_preview_post_release_monitoring_readiness_packet_v2"
PACKET_VERSION = 2

REQUIRED_TRUE_ATTESTATIONS = (
    "fixture_first",
    "no_live_monitoring",
    "no_devhub",
    "no_browser",
    "no_live_llm",
    "no_crawler",
    "no_processor",
    "no_private_or_authenticated_facts",
    "no_raw_crawl_pdf_session_artifacts",
    "no_legal_or_permitting_outcome_guarantees",
    "no_active_prompt_mutation",
    "no_active_guardrail_mutation",
    "no_active_pdf_mutation",
    "no_active_surface_registry_mutation",
    "no_active_monitoring_mutation",
    "no_release_state_mutation",
    "no_active_agent_state_mutation",
)

REQUIRED_FALSE_ATTESTATIONS = (
    "active_prompt_mutation",
    "active_guardrail_mutation",
    "active_pdf_mutation",
    "active_surface_registry_mutation",
    "active_monitoring_mutation",
    "release_state_mutation",
    "active_agent_state_mutation",
    "live_monitoring_executed",
    "devhub_executed",
    "browser_executed",
    "llm_executed",
    "crawler_executed",
    "processor_executed",
)

_ALLOWED_DEFAULT_COMMANDS = (
    ("python3", "-m", "py_compile", "ppd/agent_readiness/draft_preview_post_release_monitoring_readiness_packet_v2.py"),
    ("python3", "-m", "pytest", "ppd/tests/test_draft_preview_post_release_monitoring_readiness_packet_v2.py"),
    ("python3", "ppd/daemon/ppd_daemon.py", "--self-test"),
)

_CITATION_KEYS = {"source_evidence_id", "source_evidence_ids", "citation_id", "citation_ids", "citations"}
_PRIVATE_FACT_KEYS = {
    "account_number",
    "address",
    "auth_state",
    "authenticated_fact",
    "authenticated_facts",
    "authenticated_value",
    "authenticated_values",
    "case_facts",
    "cookie",
    "cookies",
    "credential",
    "credentials",
    "devhub_case_fact",
    "devhub_page_value",
    "email",
    "known_facts",
    "password",
    "payment_details",
    "phone",
    "private_fact",
    "private_facts",
    "private_value",
    "private_values",
    "raw_value",
    "session_cookie",
    "session_state",
    "storage_state",
    "token",
    "user_case_facts",
    "user_input",
}
_PRIVATE_CLASSIFICATIONS = {
    "authenticated",
    "case_private",
    "confidential",
    "devhub_authenticated",
    "devhub_authenticated_private",
    "private",
    "restricted",
    "session_private",
    "user_private",
}
_MUTATION_DOMAINS = (
    "prompt",
    "guardrail",
    "pdf",
    "surface_registry",
    "surface-registry",
    "monitoring",
    "release_state",
    "release-state",
    "agent_state",
    "agent-state",
)
_RAW_ARTIFACT_KEY_RE = re.compile(
    r"(^|_)(raw[_-]?(crawl|body|pdf|html|text|artifact)?|crawl[_-]?output|pdf[_-]?(path|artifact|download|bytes|session)?|download[_-]?(ref|url|path)?|session[_-]?(artifact|path|trace|state|file)?|auth[_-]?state|browser[_-]?state|har|trace|screenshot|warc[_-]?(ref|path)?|local[_-]?path)(_|$)",
    re.IGNORECASE,
)
_RAW_ARTIFACT_VALUE_RE = re.compile(
    r"(^(file|crawl|archive|warc|session)://|/(tmp|var/folders|private|home)/|\\users\\|\.warc(\.gz)?$|\.har$|trace\.zip$|/raw/|/downloads?/|/archives?/|/sessions?/|raw crawl|raw pdf|downloaded document|session artifact|browser trace|auth state|pdf bytes)",
    re.IGNORECASE,
)
_LIVE_EXECUTION_RE = re.compile(
    r"\b(live monitor(?:ing)?|monitor(?:ing)? (?:ran|executed|activated)|devhub (?:ran|executed|opened|accessed|clicked)|opened devhub|browser (?:ran|executed|opened|clicked)|live llm|llm (?:ran|executed|called)|crawler (?:ran|executed|captured|downloaded)|live crawl|processor (?:ran|executed|processed|downloaded)|live processor)\b",
    re.IGNORECASE,
)
_OUTCOME_GUARANTEE_RE = re.compile(
    r"\b(guarantee[sd]?|will be approved|approval is assured|permit will issue|permit must issue|ensures issuance|ensures approval|legally valid|legal outcome|legal compliance guaranteed|no legal risk|cannot be denied|permitting outcome guaranteed)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class DraftPreviewPostReleaseMonitoringReadinessV2ValidationResult:
    valid: bool
    problems: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {"valid": self.valid, "problems": list(self.problems)}


def load_draft_preview_post_release_monitoring_readiness_v2_fixture(path: str | Path) -> dict[str, Any]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("fixture must be a JSON object")
    assert_valid_draft_preview_post_release_monitoring_readiness_v2_packet(raw)
    return raw


def validate_draft_preview_post_release_monitoring_readiness_v2_packet(
    packet: Mapping[str, Any],
) -> DraftPreviewPostReleaseMonitoringReadinessV2ValidationResult:
    problems: list[str] = []
    if not isinstance(packet, Mapping):
        return DraftPreviewPostReleaseMonitoringReadinessV2ValidationResult(False, ("packet must be an object",))

    if packet.get("packet_type") != PACKET_TYPE:
        problems.append(f"packet_type must be {PACKET_TYPE}")
    if packet.get("packet_version") != PACKET_VERSION:
        problems.append("packet_version must be 2")
    if packet.get("mode") != "fixture_first_draft_preview_post_release_monitoring_readiness":
        problems.append("mode must be fixture_first_draft_preview_post_release_monitoring_readiness")

    evidence_ids = _packet_evidence_ids(packet)
    if not evidence_ids:
        problems.append("source_evidence_ids must be non-empty")

    _validate_monitoring_checks(problems, packet, evidence_ids)
    _validate_rollback_triggers(problems, packet, evidence_ids)
    _validate_allowed_validation_commands(problems, packet)
    _validate_attestations(problems, packet)
    _validate_recursive_policy_rejections(problems, packet)
    return DraftPreviewPostReleaseMonitoringReadinessV2ValidationResult(not problems, tuple(problems))


def assert_valid_draft_preview_post_release_monitoring_readiness_v2_packet(packet: Mapping[str, Any]) -> None:
    result = validate_draft_preview_post_release_monitoring_readiness_v2_packet(packet)
    if not result.valid:
        raise ValueError("invalid draft preview post-release monitoring readiness v2 packet: " + "; ".join(result.problems))


def default_allowed_validation_commands() -> list[list[str]]:
    return [list(command) for command in _ALLOWED_DEFAULT_COMMANDS]


def _validate_monitoring_checks(problems: list[str], packet: Mapping[str, Any], evidence_ids: set[str]) -> None:
    checks = packet.get("monitoring_checks")
    if not isinstance(checks, list) or not checks:
        problems.append("monitoring_checks must be a non-empty list")
        return
    for index, check in enumerate(_mapping_sequence(checks)):
        prefix = f"monitoring_checks[{index}]"
        if not _text(check.get("check_id")):
            problems.append(f"{prefix} lacks check_id")
        refs = _collect_evidence_refs(check)
        if not refs:
            problems.append(f"{prefix} lacks source evidence citations")
        for ref in sorted(refs):
            if ref not in evidence_ids:
                problems.append(f"{prefix} cites unknown source evidence {ref}")
        if not _string_list(check.get("drift_signals")):
            problems.append(f"{prefix} lacks drift_signals")
        if not _text(check.get("escalation_owner")) and not _string_list(check.get("escalation_owners")):
            problems.append(f"{prefix} lacks escalation owner")
        if not _text(check.get("escalation_path")) and not _text(check.get("escalation_note")):
            problems.append(f"{prefix} lacks escalation path or note")
        if not _text(check.get("rollback_trigger_ref")) and not _string_list(check.get("rollback_trigger_refs")):
            problems.append(f"{prefix} lacks rollback trigger reference")


def _validate_rollback_triggers(problems: list[str], packet: Mapping[str, Any], evidence_ids: set[str]) -> None:
    triggers = packet.get("rollback_triggers")
    if not isinstance(triggers, list) or not triggers:
        problems.append("rollback_triggers must be a non-empty list")
        return
    for index, trigger in enumerate(_mapping_sequence(triggers)):
        prefix = f"rollback_triggers[{index}]"
        if not _text(trigger.get("trigger_id")):
            problems.append(f"{prefix} lacks trigger_id")
        if not _text(trigger.get("condition")):
            problems.append(f"{prefix} lacks condition")
        if not _text(trigger.get("rollback_owner")):
            problems.append(f"{prefix} lacks rollback_owner")
        refs = _collect_evidence_refs(trigger)
        if not refs:
            problems.append(f"{prefix} lacks source evidence citations")
        for ref in sorted(refs):
            if ref not in evidence_ids:
                problems.append(f"{prefix} cites unknown source evidence {ref}")


def _validate_allowed_validation_commands(problems: list[str], packet: Mapping[str, Any]) -> None:
    allowed = _command_sequence(packet.get("allowed_validation_commands"))
    if not allowed:
        problems.append("allowed_validation_commands must be a non-empty list of commands")
        return
    offline = _command_sequence(packet.get("offline_validation_commands"))
    if not offline:
        problems.append("offline_validation_commands must be a non-empty list of commands")
        return
    allowed_tuples = {tuple(command) for command in allowed}
    for index, command in enumerate(offline):
        if tuple(command) not in allowed_tuples:
            problems.append(f"offline_validation_commands[{index}] is not listed in allowed_validation_commands")


def _validate_attestations(problems: list[str], packet: Mapping[str, Any]) -> None:
    attestations = packet.get("attestations") if isinstance(packet.get("attestations"), Mapping) else {}
    for key in REQUIRED_TRUE_ATTESTATIONS:
        if attestations.get(key) is not True:
            problems.append(f"attestations.{key} must be true")
    for key in REQUIRED_FALSE_ATTESTATIONS:
        if attestations.get(key) is not False:
            problems.append(f"attestations.{key} must be false")


def _validate_recursive_policy_rejections(problems: list[str], packet: Mapping[str, Any]) -> None:
    for path, value in _walk(packet):
        key = path.rsplit(".", 1)[-1]
        normalized_key = key.lower().replace("-", "_")
        if normalized_key in _PRIVATE_FACT_KEYS and _truthy_or_text(value):
            problems.append(f"{path} must not include private or authenticated facts")
        if _RAW_ARTIFACT_KEY_RE.search(normalized_key) and _truthy_or_text(value):
            problems.append(f"{path} must not reference raw crawl, PDF, session, browser, WARC, download, or local artifacts")
        if isinstance(value, Mapping):
            classification = _text(value.get("privacy_classification") or value.get("privacy") or value.get("auth_scope")).lower()
            if classification in _PRIVATE_CLASSIFICATIONS:
                problems.append(f"{path} must not include private or authenticated facts")
            mutation_flags = value.get("mutation_flags")
            if isinstance(mutation_flags, Mapping):
                for flag, flag_value in mutation_flags.items():
                    if _is_active_mutation_flag(str(flag).lower().replace("-", "_"), flag_value):
                        problems.append(f"{path}.mutation_flags.{flag} must be false")
        if isinstance(value, str):
            stripped = value.strip()
            if _RAW_ARTIFACT_VALUE_RE.search(stripped):
                problems.append(f"{path} must not reference raw crawl, PDF, session, browser, WARC, download, or local artifacts")
            if _LIVE_EXECUTION_RE.search(stripped):
                problems.append(f"{path} must not claim live monitoring, DevHub, browser, LLM, crawler, or processor execution")
            if _OUTCOME_GUARANTEE_RE.search(stripped):
                problems.append(f"{path} must not guarantee legal or permitting outcomes")
        if _is_active_mutation_flag(normalized_key, value):
            problems.append(f"{path} must not set active prompt, guardrail, PDF, surface-registry, monitoring, release-state, or agent-state mutation flags")


def _packet_evidence_ids(packet: Mapping[str, Any]) -> set[str]:
    ids = set(_string_list(packet.get("source_evidence_ids")))
    for key in ("source_evidence", "citations", "sources"):
        raw = packet.get(key)
        if not isinstance(raw, list):
            continue
        for item in raw:
            if not isinstance(item, Mapping):
                continue
            for id_key in ("source_evidence_id", "evidence_id", "citation_id", "source_id"):
                value = item.get(id_key)
                if isinstance(value, str) and value.strip():
                    ids.add(value.strip())
    return ids


def _collect_evidence_refs(value: Any) -> set[str]:
    refs: set[str] = set()
    if isinstance(value, Mapping):
        for key in _CITATION_KEYS:
            raw = value.get(key)
            if isinstance(raw, str) and raw.strip():
                refs.add(raw.strip())
            elif isinstance(raw, Sequence) and not isinstance(raw, (str, bytes, bytearray)):
                for item in raw:
                    if isinstance(item, str) and item.strip():
                        refs.add(item.strip())
                    elif isinstance(item, Mapping):
                        refs.update(_collect_evidence_refs(item))
        for child in value.values():
            refs.update(_collect_evidence_refs(child))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for child in value:
            refs.update(_collect_evidence_refs(child))
    return refs


def _is_active_mutation_flag(normalized_key: str, value: Any) -> bool:
    if value is not True:
        return False
    if normalized_key.startswith("no_active_") or normalized_key.startswith("no_"):
        return False
    has_domain = any(domain.replace("-", "_") in normalized_key for domain in _MUTATION_DOMAINS)
    has_mutation = any(term in normalized_key for term in ("mutation", "mutated", "write", "update", "enabled", "active"))
    if has_domain and has_mutation:
        return True
    return normalized_key in {
        "prompt_updated",
        "guardrail_updated",
        "pdf_written",
        "surface_registry_updated",
        "monitoring_state_updated",
        "release_state_updated",
        "agent_state_updated",
    }


def _command_sequence(value: Any) -> list[list[str]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return []
    commands: list[list[str]] = []
    for command in value:
        if not isinstance(command, Sequence) or isinstance(command, (str, bytes, bytearray)):
            continue
        parts = [_text(part) for part in command if _text(part)]
        if parts:
            commands.append(parts)
    return commands


def _mapping_sequence(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _string_list(value: Any) -> list[str]:
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _walk(value: Any, prefix: str = "") -> list[tuple[str, Any]]:
    items: list[tuple[str, Any]] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            items.append((path, child))
            items.extend(_walk(child, path))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            path = f"{prefix}[{index}]" if prefix else f"[{index}]"
            items.append((path, child))
            items.extend(_walk(child, path))
    return items


def _truthy_or_text(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    return bool(value)


def _text(value: Any) -> str:
    return str(value).strip() if value is not None else ""
