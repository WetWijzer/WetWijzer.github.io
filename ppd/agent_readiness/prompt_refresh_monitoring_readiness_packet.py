"""Fixture-first PP&D prompt refresh monitoring readiness packets.

This module consumes committed dry-run and monitoring fixture packets only. It
never opens DevHub, prompts an agent, runs a crawler, starts live monitoring, or
mutates prompt, guardrail, or release state.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import re
from typing import Any

from ppd.agent_readiness.post_release_monitoring_plan_validation import require_post_release_monitoring_plan
from ppd.agent_readiness.prompt_consumer_dry_run_transcript_packet import require_prompt_consumer_dry_run_transcript_packet
from ppd.evidence_freshness_watchlist_packet import assert_valid_evidence_freshness_watchlist_packet


PACKET_TYPE = "ppd.prompt_refresh_monitoring_readiness_packet.v1"
REQUIRED_ATTESTATIONS = (
    "no-live-monitoring",
    "no-crawler",
    "no-DevHub",
    "no-prompt",
    "no-guardrail-mutation",
    "no-release-state-mutation",
)

_LIVE_COMMAND_TOKENS = {"crawl", "crawler", "devhub", "llm", "monitor", "monitoring", "playwright", "prompt", "scrape"}
_PLACEHOLDER_OWNER_VALUES = {"", "owner", "reviewer", "tbd", "todo", "unknown", "none"}
_LOCAL_OR_RAW_RE = re.compile(
    r"(auth[_-]?state|cookie|credential|password|secret|token|\.har\b|trace\.zip|raw[_-]?(?:body|crawl|download)|warc://|/home/|/Users/|/tmp/|file://|C:\\\\Users\\\\)",
    re.IGNORECASE,
)
_LIVE_CLAIM_RE = re.compile(
    r"\b(live monitor|monitor ran|monitor executed|crawler ran|crawl executed|devhub opened|prompt executed|llm ran|guardrail mutated|release state mutated)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class PromptRefreshMonitoringReadinessFinding:
    code: str
    path: str
    message: str


@dataclass(frozen=True)
class PromptRefreshMonitoringReadinessValidationResult:
    findings: tuple[PromptRefreshMonitoringReadinessFinding, ...]

    @property
    def valid(self) -> bool:
        return not self.findings

    @property
    def ready(self) -> bool:
        return self.valid

    @property
    def errors(self) -> tuple[str, ...]:
        return tuple(finding.code for finding in self.findings)

    def codes(self) -> tuple[str, ...]:
        return self.errors

    def as_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "ready": self.ready,
            "findings": [finding.__dict__ for finding in self.findings],
            "errors": list(self.errors),
        }


class PromptRefreshMonitoringReadinessPacketError(ValueError):
    def __init__(self, findings: Sequence[PromptRefreshMonitoringReadinessFinding]) -> None:
        self.findings = tuple(findings)
        detail = "; ".join(f"{finding.code} at {finding.path}: {finding.message}" for finding in self.findings)
        super().__init__("invalid prompt refresh monitoring readiness packet: " + detail)


def build_prompt_refresh_monitoring_readiness_packet(inputs: Mapping[str, Any]) -> dict[str, Any]:
    """Build a deterministic offline readiness packet from three source packets."""

    prompt_transcript = _required_mapping(inputs, "prompt_consumer_dry_run_transcript_packet")
    monitoring_plan = _required_mapping(inputs, "post_release_monitoring_plan_packet")
    watchlist = _required_mapping(inputs, "source_freshness_watchlist_packet")

    require_prompt_consumer_dry_run_transcript_packet(prompt_transcript)
    require_post_release_monitoring_plan(monitoring_plan)
    assert_valid_evidence_freshness_watchlist_packet(watchlist)

    commands = _allowed_validation_commands(inputs.get("allowed_validation_commands"))
    packet = {
        "packet_type": PACKET_TYPE,
        "packet_id": str(inputs.get("packet_id") or "prompt-refresh-monitoring-readiness-fixture"),
        "fixture_first": True,
        "offline_only": True,
        "consumed_packets": {
            "prompt_consumer_dry_run_transcript_packet": _consumed_packet(prompt_transcript),
            "post_release_monitoring_plan_packet": _consumed_packet(monitoring_plan),
            "source_freshness_watchlist_packet": _consumed_packet(watchlist),
        },
        "offline_monitoring_checks": _offline_monitoring_checks(monitoring_plan, watchlist),
        "drift_signals": _drift_signals(prompt_transcript, watchlist),
        "escalation_owner_fields": _escalation_owner_fields(prompt_transcript, monitoring_plan, watchlist),
        "rollback_triggers": _rollback_triggers(prompt_transcript, monitoring_plan, watchlist),
        "allowed_validation_commands": commands,
        "attestations": {key: True for key in REQUIRED_ATTESTATIONS},
        "execution_boundaries": {
            "live_monitoring": False,
            "crawler": False,
            "devhub": False,
            "prompt": False,
            "guardrail_mutation": False,
            "release_state_mutation": False,
        },
    }
    assert_valid_prompt_refresh_monitoring_readiness_packet(packet)
    return packet


def validate_prompt_refresh_monitoring_readiness_packet(
    packet: Mapping[str, Any],
) -> PromptRefreshMonitoringReadinessValidationResult:
    findings: list[PromptRefreshMonitoringReadinessFinding] = []
    if not isinstance(packet, Mapping):
        return PromptRefreshMonitoringReadinessValidationResult(
            (PromptRefreshMonitoringReadinessFinding("packet_not_mapping", "$", "Packet must be a mapping."),)
        )

    if packet.get("packet_type") != PACKET_TYPE:
        _add(findings, "invalid_packet_type", "$.packet_type", "Unexpected packet type.")
    if packet.get("fixture_first") is not True:
        _add(findings, "not_fixture_first", "$.fixture_first", "Packet must declare fixture_first=true.")
    if packet.get("offline_only") is not True:
        _add(findings, "not_offline_only", "$.offline_only", "Packet must declare offline_only=true.")

    _validate_consumed_packets(packet.get("consumed_packets"), findings)
    _validate_offline_monitoring_checks(packet.get("offline_monitoring_checks"), findings)
    _validate_drift_signals(packet.get("drift_signals"), findings)
    _validate_owner_fields(packet.get("escalation_owner_fields"), findings)
    _validate_rollback_triggers(packet.get("rollback_triggers"), findings)
    _validate_allowed_validation_commands(packet.get("allowed_validation_commands"), findings)
    _validate_attestations(packet.get("attestations"), findings)
    _validate_execution_boundaries(packet.get("execution_boundaries"), findings)
    _scan_for_unsafe_content(packet, "$", findings)
    return PromptRefreshMonitoringReadinessValidationResult(tuple(_dedupe(findings)))


def assert_valid_prompt_refresh_monitoring_readiness_packet(packet: Mapping[str, Any]) -> None:
    result = validate_prompt_refresh_monitoring_readiness_packet(packet)
    if result.findings:
        raise PromptRefreshMonitoringReadinessPacketError(result.findings)


def require_prompt_refresh_monitoring_readiness_packet(packet: Mapping[str, Any]) -> None:
    assert_valid_prompt_refresh_monitoring_readiness_packet(packet)


def _offline_monitoring_checks(monitoring_plan: Mapping[str, Any], watchlist: Mapping[str, Any]) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    watchlist_sources = _mapping_sequence(watchlist.get("watchlist_sources"))
    for index, check in enumerate(_mapping_sequence(monitoring_plan.get("monitoring_checks")), start=1):
        source_ids = _strings(check.get("source_evidence_ids") or check.get("citation_ids"))
        related_watchlist_ids = [str(row.get("source_id")) for row in watchlist_sources if set(source_ids) & set(_strings(row.get("source_evidence_ids")))]
        check_id = _text(check.get("check_id")) or f"offline-monitoring-check-{index:02d}"
        checks.append(
            {
                "check_id": check_id,
                "description": _text(check.get("description")) or check_id,
                "source_evidence_ids": source_ids,
                "related_watchlist_source_ids": related_watchlist_ids,
                "reviewer_owner": _text(check.get("reviewer_owner") or check.get("owner")),
                "escalation_note": _text(check.get("escalation_note") or check.get("escalation_path")),
                "escalation_threshold": dict(_mapping(check.get("alert_threshold") or check.get("threshold"))),
                "monitoring_mode": "offline_fixture_comparison_only",
            }
        )
    return checks


def _drift_signals(prompt_transcript: Mapping[str, Any], watchlist: Mapping[str, Any]) -> list[dict[str, Any]]:
    signals: list[dict[str, Any]] = []
    prompt_scenarios = _scenario_ids(prompt_transcript)
    for index, source in enumerate(_mapping_sequence(watchlist.get("watchlist_sources")), start=1):
        source_id = _text(source.get("source_id")) or f"watchlist-source-{index:02d}"
        signals.append(
            {
                "signal_id": "prompt-refresh-drift-" + _slug(source_id),
                "source_id": source_id,
                "source_evidence_ids": _strings(source.get("source_evidence_ids")),
                "affected_requirement_ids": _strings(source.get("affected_requirement_ids")),
                "affected_guardrail_ids": _strings(source.get("affected_guardrail_ids")),
                "prompt_consumer_scenario_ids": prompt_scenarios,
                "drift_condition": "source freshness watchlist entry intersects prompt consumer dry-run refusal or exact-confirmation expectations",
                "required_response": "pause prompt refresh promotion for offline reviewer triage",
            }
        )
    return signals


def _escalation_owner_fields(prompt_transcript: Mapping[str, Any], monitoring_plan: Mapping[str, Any], watchlist: Mapping[str, Any]) -> dict[str, str]:
    watchlist_owners = _mapping(watchlist.get("reviewer_owner_fields"))
    monitoring_owner = ""
    for check in _mapping_sequence(monitoring_plan.get("monitoring_checks")):
        monitoring_owner = _text(check.get("reviewer_owner") or check.get("owner"))
        if monitoring_owner:
            break
    return {
        "prompt_refresh_owner": _text(prompt_transcript.get("reviewer_owner")) or "ppd-agent-prompt-reviewer",
        "monitoring_owner": monitoring_owner or "ppd-release-operator",
        "source_freshness_owner": _text(watchlist_owners.get("watchlist_owner")) or "ppd-evidence-freshness-watchlist-owner",
        "guardrail_owner": _text(watchlist_owners.get("traceability_owner")) or "ppd-guardrail-reviewer",
        "rollback_owner": _text(watchlist_owners.get("primary_reviewer")) or "ppd-release-rollback-reviewer",
    }


def _rollback_triggers(prompt_transcript: Mapping[str, Any], monitoring_plan: Mapping[str, Any], watchlist: Mapping[str, Any]) -> list[dict[str, Any]]:
    triggers: list[dict[str, Any]] = []
    for check in _mapping_sequence(monitoring_plan.get("monitoring_checks")):
        triggers.append(
            {
                "trigger_id": "monitoring-threshold-" + _slug(_text(check.get("check_id")) or "check"),
                "source_evidence_ids": _strings(check.get("source_evidence_ids") or check.get("citation_ids")),
                "condition": "offline monitoring threshold is exceeded or citation no longer matches normalized fixture metadata",
                "rollback_action": "hold prompt refresh packet and reopen offline release review",
                "owner_field": "monitoring_owner",
            }
        )
    for signal in _drift_signals(prompt_transcript, watchlist):
        triggers.append(
            {
                "trigger_id": "watchlist-drift-" + _slug(signal["source_id"]),
                "source_evidence_ids": signal["source_evidence_ids"],
                "condition": "source freshness watchlist drift signal affects a prompt consumer dry-run expectation",
                "rollback_action": "revert prompt refresh candidate to previous fixture-backed prompt contract",
                "owner_field": "source_freshness_owner",
            }
        )
    return triggers


def _allowed_validation_commands(value: Any) -> list[list[str]]:
    commands: list[list[str]] = []
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for command in value:
            if isinstance(command, Sequence) and not isinstance(command, (str, bytes, bytearray)):
                tokens = [part for part in command if isinstance(part, str) and part]
                if tokens:
                    commands.append(tokens)
    if commands:
        return commands
    return [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]]


def _validate_consumed_packets(value: Any, findings: list[PromptRefreshMonitoringReadinessFinding]) -> None:
    required = (
        "prompt_consumer_dry_run_transcript_packet",
        "post_release_monitoring_plan_packet",
        "source_freshness_watchlist_packet",
    )
    consumed = _mapping(value)
    if not consumed:
        _add(findings, "missing_consumed_packets", "$.consumed_packets", "Consumed packet references are required.")
        return
    for name in required:
        packet_ref = _mapping(consumed.get(name))
        path = f"$.consumed_packets.{name}"
        if not packet_ref:
            _add(findings, "missing_consumed_packet", path, "Required source packet was not consumed.")
        elif not _text(packet_ref.get("packet_id")):
            _add(findings, "missing_consumed_packet_id", path + ".packet_id", "Consumed packet requires packet_id.")
        elif not _strings(packet_ref.get("source_evidence_ids")):
            _add(findings, "uncited_consumed_packet", path + ".source_evidence_ids", "Consumed packet requires cited evidence.")


def _validate_offline_monitoring_checks(value: Any, findings: list[PromptRefreshMonitoringReadinessFinding]) -> None:
    checks = _mapping_sequence(value)
    if not checks:
        _add(findings, "missing_offline_monitoring_checks", "$.offline_monitoring_checks", "Offline monitoring checks are required.")
        return
    for index, check in enumerate(checks):
        path = f"$.offline_monitoring_checks[{index}]"
        for key in ("check_id", "reviewer_owner", "escalation_note"):
            if not _text(check.get(key)):
                _add(findings, "incomplete_offline_monitoring_check", f"{path}.{key}", f"{key} is required.")
        if not _strings(check.get("source_evidence_ids")):
            _add(findings, "uncited_offline_monitoring_check", path + ".source_evidence_ids", "Monitoring check must cite source evidence.")
        if not _mapping(check.get("escalation_threshold")):
            _add(findings, "missing_escalation_threshold", path + ".escalation_threshold", "Escalation threshold is required.")
        if check.get("monitoring_mode") != "offline_fixture_comparison_only":
            _add(findings, "invalid_monitoring_mode", path + ".monitoring_mode", "Monitoring mode must remain offline fixture comparison only.")


def _validate_drift_signals(value: Any, findings: list[PromptRefreshMonitoringReadinessFinding]) -> None:
    signals = _mapping_sequence(value)
    if not signals:
        _add(findings, "missing_drift_signals", "$.drift_signals", "At least one drift signal is required.")
        return
    for index, signal in enumerate(signals):
        path = f"$.drift_signals[{index}]"
        if not _text(signal.get("signal_id")):
            _add(findings, "missing_drift_signal_id", path + ".signal_id", "Drift signal requires signal_id.")
        if not _strings(signal.get("source_evidence_ids")):
            _add(findings, "uncited_drift_signal", path + ".source_evidence_ids", "Drift signal must cite source evidence.")
        if not _strings(signal.get("affected_requirement_ids")):
            _add(findings, "missing_drift_requirement_links", path + ".affected_requirement_ids", "Drift signal must link affected requirements.")
        if not _strings(signal.get("affected_guardrail_ids")):
            _add(findings, "missing_drift_guardrail_links", path + ".affected_guardrail_ids", "Drift signal must link affected guardrails.")


def _validate_owner_fields(value: Any, findings: list[PromptRefreshMonitoringReadinessFinding]) -> None:
    owners = _mapping(value)
    for key in ("prompt_refresh_owner", "monitoring_owner", "source_freshness_owner", "guardrail_owner", "rollback_owner"):
        owner = _text(owners.get(key))
        if owner.lower() in _PLACEHOLDER_OWNER_VALUES:
            _add(findings, "missing_escalation_owner", f"$.escalation_owner_fields.{key}", "Concrete escalation owner is required.")


def _validate_rollback_triggers(value: Any, findings: list[PromptRefreshMonitoringReadinessFinding]) -> None:
    triggers = _mapping_sequence(value)
    if not triggers:
        _add(findings, "missing_rollback_triggers", "$.rollback_triggers", "Rollback triggers are required.")
        return
    for index, trigger in enumerate(triggers):
        path = f"$.rollback_triggers[{index}]"
        if not _text(trigger.get("trigger_id")) or not _text(trigger.get("condition")) or not _text(trigger.get("rollback_action")):
            _add(findings, "incomplete_rollback_trigger", path, "Rollback trigger requires id, condition, and action.")
        if not _strings(trigger.get("source_evidence_ids")):
            _add(findings, "uncited_rollback_trigger", path + ".source_evidence_ids", "Rollback trigger must cite source evidence.")


def _validate_allowed_validation_commands(value: Any, findings: list[PromptRefreshMonitoringReadinessFinding]) -> None:
    commands = value if isinstance(value, list) else []
    if not commands:
        _add(findings, "missing_allowed_validation_commands", "$.allowed_validation_commands", "Allowed validation commands are required.")
        return
    for index, command in enumerate(commands):
        path = f"$.allowed_validation_commands[{index}]"
        if not isinstance(command, list) or not command or not all(isinstance(part, str) and part for part in command):
            _add(findings, "invalid_validation_command", path, "Validation command must be a non-empty string list.")
            continue
        lowered = {part.lower() for part in command}
        if lowered & _LIVE_COMMAND_TOKENS:
            _add(findings, "live_validation_command", path, "Validation command must not invoke live monitoring, crawler, DevHub, prompt, or Playwright paths.")


def _validate_attestations(value: Any, findings: list[PromptRefreshMonitoringReadinessFinding]) -> None:
    attestations = _mapping(value)
    for key in REQUIRED_ATTESTATIONS:
        if attestations.get(key) is not True:
            _add(findings, "missing_required_attestation", f"$.attestations.{key}", "Required no-live/no-mutation attestation must be true.")


def _validate_execution_boundaries(value: Any, findings: list[PromptRefreshMonitoringReadinessFinding]) -> None:
    boundaries = _mapping(value)
    for key in ("live_monitoring", "crawler", "devhub", "prompt", "guardrail_mutation", "release_state_mutation"):
        if boundaries.get(key) is not False:
            _add(findings, "enabled_execution_boundary", f"$.execution_boundaries.{key}", "Execution boundary must be false.")


def _scan_for_unsafe_content(value: Any, path: str, findings: list[PromptRefreshMonitoringReadinessFinding]) -> None:
    if isinstance(value, Mapping):
        for raw_key, child in value.items():
            key = str(raw_key)
            child_path = f"{path}.{key}" if path != "$" else f"$.{key}"
            lowered = key.lower()
            if any(flag in lowered for flag in ("mutation_enabled", "mutate_", "live_monitoring_enabled", "crawler_enabled")) and child is True:
                _add(findings, "active_mutation_or_execution_flag", child_path, "Active mutation or execution flags must not be true.")
            _scan_for_unsafe_content(child, child_path, findings)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _scan_for_unsafe_content(child, f"{path}[{index}]", findings)
    elif isinstance(value, str):
        if _LOCAL_OR_RAW_RE.search(value):
            _add(findings, "raw_private_or_auth_reference", path, "Raw, private, credential, browser, or local artifact references are not allowed.")
        if _LIVE_CLAIM_RE.search(value):
            _add(findings, "live_execution_claim", path, "Live monitoring, crawler, DevHub, prompt, guardrail, or release mutation claims are not allowed.")


def _required_mapping(packet: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = packet.get(key)
    if not isinstance(value, Mapping):
        raise ValueError(f"packet field must be an object: {key}")
    return value


def _consumed_packet(packet: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "packet_id": _text(packet.get("packet_id")) or _text(packet.get("packet_type")) or "fixture-packet",
        "packet_type": _text(packet.get("packet_type")) or "fixture-packet",
        "source_evidence_ids": _packet_evidence_ids(packet),
    }


def _packet_evidence_ids(packet: Mapping[str, Any]) -> list[str]:
    return _ordered_unique(_extract_strings_by_key(packet, {"source_evidence_ids", "citation_ids", "citations", "evidence_ids", "source_ids"}))


def _scenario_ids(packet: Mapping[str, Any]) -> list[str]:
    ids: list[str] = []
    for scenario in _mapping_sequence(packet.get("scenarios") or packet.get("consumer_scenarios") or packet.get("dry_run_scenarios")):
        ids.append(_text(scenario.get("scenario_id") or scenario.get("id")))
    return [item for item in ids if item]


def _extract_strings_by_key(value: Any, keys: set[str]) -> list[str]:
    found: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            if str(key) in keys:
                found.extend(_strings(child))
            found.extend(_extract_strings_by_key(child, keys))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for child in value:
            found.extend(_extract_strings_by_key(child, keys))
    return found


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _mapping_sequence(value: Any) -> list[Mapping[str, Any]]:
    if isinstance(value, Mapping):
        return [value]
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [item for item in value if isinstance(item, Mapping)]
    return []


def _strings(value: Any) -> list[str]:
    if isinstance(value, str):
        text = value.strip()
        return [text] if text else []
    if isinstance(value, Mapping):
        result: list[str] = []
        for key in ("source_id", "evidence_id", "id", "ref", "requirement_id", "guardrail_id"):
            result.extend(_strings(value.get(key)))
        return result
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        result: list[str] = []
        for item in value:
            result.extend(_strings(item))
        return result
    return []


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _ordered_unique(values: Sequence[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        text = value.strip()
        if text and text not in result:
            result.append(text)
    return result


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "item"


def _add(findings: list[PromptRefreshMonitoringReadinessFinding], code: str, path: str, message: str) -> None:
    findings.append(PromptRefreshMonitoringReadinessFinding(code, path, message))


def _dedupe(findings: Sequence[PromptRefreshMonitoringReadinessFinding]) -> tuple[PromptRefreshMonitoringReadinessFinding, ...]:
    seen: set[tuple[str, str]] = set()
    result: list[PromptRefreshMonitoringReadinessFinding] = []
    for finding in findings:
        key = (finding.code, finding.path)
        if key not in seen:
            result.append(finding)
            seen.add(key)
    return tuple(result)
