"""Validation for prompt refresh monitoring readiness packets.

The validator is intentionally side-effect free. It checks committed packet-shaped
metadata and rejects claims that would imply live crawling, authenticated access,
legal outcomes, or active mutation of PP&D operating state.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence


@dataclass(frozen=True)
class ReadinessFinding:
    """A deterministic validation finding for a readiness packet."""

    code: str
    message: str
    path: str


_PRIVATE_FACT_MARKERS = (
    "authenticated fact",
    "authenticated-only",
    "private fact",
    "private account",
    "user account",
    "account-scoped",
    "session cookie",
    "cookie",
    "credential",
    "password",
    "mfa",
    "captcha",
    "devhub private",
    "permit record from login",
)

_RAW_CRAWL_MARKERS = (
    "raw crawl output",
    "raw html",
    "raw body",
    "raw response body",
    "warc payload",
    "browser trace",
    "har file",
    "screenshot artifact",
)

_LIVE_EXECUTION_MARKERS = (
    "live monitoring ran",
    "live monitor ran",
    "live crawler ran",
    "crawler executed",
    "processor executed",
    "devhub executed",
    "devhub automation ran",
    "llm executed",
    "llm refreshed",
    "live prompt refresh completed",
    "production monitor updated",
)

_LEGAL_GUARANTEE_MARKERS = (
    "guaranteed approval",
    "approval guaranteed",
    "permit will be approved",
    "inspection will pass",
    "legally compliant",
    "legal compliance guaranteed",
    "no permitting risk",
    "final permit outcome",
)

_MUTATION_FLAG_NAMES = (
    "active_source_mutation",
    "active_schedule_mutation",
    "active_prompt_mutation",
    "active_guardrail_mutation",
    "active_surface_registry_mutation",
    "active_monitoring_mutation",
    "active_release_state_mutation",
    "active_agent_state_mutation",
    "source_mutation_active",
    "schedule_mutation_active",
    "prompt_mutation_active",
    "guardrail_mutation_active",
    "surface_registry_mutation_active",
    "monitoring_mutation_active",
    "release_state_mutation_active",
    "agent_state_mutation_active",
)

_MUTATION_TEXT_MARKERS = (
    "active source mutation",
    "active schedule mutation",
    "active prompt mutation",
    "active guardrail mutation",
    "active surface-registry mutation",
    "active surface registry mutation",
    "active monitoring mutation",
    "active release-state mutation",
    "active release state mutation",
    "active agent-state mutation",
    "active agent state mutation",
)


_REQUIRED_LISTS = {
    "drift_signals": "missing_drift_signals",
    "escalation_owners": "missing_escalation_owners",
    "rollback_triggers": "missing_rollback_triggers",
    "offline_validation_commands": "missing_offline_validation_commands",
}


def validate_monitoring_readiness_packet(packet: Mapping[str, Any]) -> list[ReadinessFinding]:
    """Return validation findings for a prompt refresh monitoring readiness packet."""

    findings: list[ReadinessFinding] = []

    checks = packet.get("checks")
    if not _non_empty_sequence(checks):
        findings.append(
            ReadinessFinding(
                code="missing_checks",
                message="readiness packet must include at least one cited check",
                path="checks",
            )
        )
    else:
        for index, check in enumerate(checks):
            if not isinstance(check, Mapping):
                findings.append(
                    ReadinessFinding(
                        code="invalid_check",
                        message="readiness checks must be objects",
                        path=f"checks[{index}]",
                    )
                )
                continue
            if not _has_citation(check):
                findings.append(
                    ReadinessFinding(
                        code="uncited_check",
                        message="readiness checks must cite public source evidence",
                        path=f"checks[{index}]",
                    )
                )

    for key, code in _REQUIRED_LISTS.items():
        if not _non_empty_sequence(packet.get(key)):
            findings.append(
                ReadinessFinding(
                    code=code,
                    message=f"readiness packet must include non-empty {key}",
                    path=key,
                )
            )

    findings.extend(_reject_markers(packet, _PRIVATE_FACT_MARKERS, "private_or_authenticated_fact"))
    findings.extend(_reject_markers(packet, _RAW_CRAWL_MARKERS, "raw_crawl_output"))
    findings.extend(_reject_markers(packet, _LIVE_EXECUTION_MARKERS, "live_execution_claim"))
    findings.extend(_reject_markers(packet, _LEGAL_GUARANTEE_MARKERS, "legal_or_permitting_outcome_guarantee"))
    findings.extend(_reject_markers(packet, _MUTATION_TEXT_MARKERS, "active_mutation_flag"))
    findings.extend(_reject_mutation_flags(packet))

    return findings


def _has_citation(item: Mapping[str, Any]) -> bool:
    for key in ("citations", "source_evidence_ids", "source_ids", "evidence"):
        value = item.get(key)
        if _non_empty_sequence(value):
            return True
        if isinstance(value, str) and value.strip():
            return True
    return False


def _non_empty_sequence(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)) and len(value) > 0


def _reject_mutation_flags(value: Any, path: str = "$") -> list[ReadinessFinding]:
    findings: list[ReadinessFinding] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            normalized_key = str(key).replace("-", "_").lower()
            if normalized_key in _MUTATION_FLAG_NAMES and child is True:
                findings.append(
                    ReadinessFinding(
                        code="active_mutation_flag",
                        message="readiness packets must not assert active mutation of PP&D operating state",
                        path=child_path,
                    )
                )
            findings.extend(_reject_mutation_flags(child, child_path))
    elif _non_empty_sequence(value):
        for index, child in enumerate(value):
            findings.extend(_reject_mutation_flags(child, f"{path}[{index}]"))
    return findings


def _reject_markers(value: Any, markers: Iterable[str], code: str, path: str = "$") -> list[ReadinessFinding]:
    findings: list[ReadinessFinding] = []
    marker_tuple = tuple(markers)
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            lowered_key = str(key).replace("_", " ").replace("-", " ").lower()
            if any(marker in lowered_key for marker in marker_tuple):
                findings.append(_marker_finding(code, child_path))
            findings.extend(_reject_markers(child, marker_tuple, code, child_path))
    elif isinstance(value, str):
        lowered_value = value.lower()
        if any(marker in lowered_value for marker in marker_tuple):
            findings.append(_marker_finding(code, path))
    elif _non_empty_sequence(value):
        for index, child in enumerate(value):
            findings.extend(_reject_markers(child, marker_tuple, code, f"{path}[{index}]"))
    return findings


def _marker_finding(code: str, path: str) -> ReadinessFinding:
    messages = {
        "private_or_authenticated_fact": "readiness packets must not include private or authenticated facts",
        "raw_crawl_output": "readiness packets must not include raw crawl or browser output",
        "live_execution_claim": "readiness packets must not claim live monitoring, crawler, processor, DevHub, or LLM execution",
        "legal_or_permitting_outcome_guarantee": "readiness packets must not guarantee legal or permitting outcomes",
        "active_mutation_flag": "readiness packets must not assert active source, schedule, prompt, guardrail, surface-registry, monitoring, release-state, or agent-state mutation",
    }
    return ReadinessFinding(code=code, message=messages[code], path=path)
