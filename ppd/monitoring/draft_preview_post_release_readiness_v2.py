"""Fixture-first draft preview post-release monitoring readiness packet v2.

This module composes committed packet fixtures into an offline monitoring
readiness packet. It performs no live monitoring, DevHub access, LLM calls, PDF
writes, prompt changes, or release-state mutation.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from ppd.monitoring.readiness import assert_post_release_monitoring_readiness_packet

PACKET_TYPE = "ppd.draft_preview_post_release_monitoring_readiness_packet.v2"
PACKET_VERSION = 2

REQUIRED_ATTESTATIONS = (
    "no_live_monitoring",
    "no_devhub",
    "no_llm",
    "no_pdf_write",
    "no_prompt",
    "no_release_state_mutation",
)

ALLOWED_VALIDATION_COMMANDS = (
    ("python3", "-m", "py_compile", "ppd/monitoring/draft_preview_post_release_readiness_v2.py"),
    ("python3", "-m", "pytest", "ppd/tests/test_draft_preview_post_release_monitoring_readiness_packet_v2.py"),
    ("python3", "ppd/daemon/ppd_daemon.py", "--self-test"),
)


class DraftPreviewPostReleaseMonitoringReadinessError(ValueError):
    """Raised when source fixtures cannot support packet v2."""


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise DraftPreviewPostReleaseMonitoringReadinessError(f"{path} must contain a JSON object")
    return value


def build_from_fixture_paths(
    draft_preview_agent_handoff_acceptance_packet_path: Path,
    prompt_refresh_monitoring_readiness_packet_path: Path,
    reversible_draft_preview_offline_smoke_transcript_v2_path: Path,
) -> dict[str, Any]:
    return build_packet(
        load_json(draft_preview_agent_handoff_acceptance_packet_path),
        load_json(prompt_refresh_monitoring_readiness_packet_path),
        load_json(reversible_draft_preview_offline_smoke_transcript_v2_path),
    )


def build_packet(
    draft_preview_agent_handoff_acceptance_packet_v2: Mapping[str, Any],
    prompt_refresh_monitoring_readiness_packet: Mapping[str, Any],
    reversible_draft_preview_offline_smoke_transcript_v2: Mapping[str, Any],
) -> dict[str, Any]:
    _validate_source_packets(
        draft_preview_agent_handoff_acceptance_packet_v2,
        prompt_refresh_monitoring_readiness_packet,
        reversible_draft_preview_offline_smoke_transcript_v2,
    )

    packet = {
        "packet_type": PACKET_TYPE,
        "packet_version": PACKET_VERSION,
        "mode": "fixture_first_offline_post_release_monitoring_readiness",
        "consumes": {
            "draft_preview_agent_handoff_acceptance_packet_v2": _packet_id(
                draft_preview_agent_handoff_acceptance_packet_v2,
                "draft-preview-agent-handoff-acceptance-packet-v2-fixture",
            ),
            "prompt_refresh_monitoring_readiness_packet": _packet_id(
                prompt_refresh_monitoring_readiness_packet,
                "prompt-refresh-monitoring-readiness-fixture",
            ),
            "reversible_draft_preview_offline_smoke_transcript_v2": _packet_id(
                reversible_draft_preview_offline_smoke_transcript_v2,
                "reversible-draft-preview-offline-smoke-transcript-v2-fixture",
            ),
        },
        "monitoring_checks": _monitoring_checks(
            draft_preview_agent_handoff_acceptance_packet_v2,
            prompt_refresh_monitoring_readiness_packet,
            reversible_draft_preview_offline_smoke_transcript_v2,
        ),
        "draft_preview_drift_signals": _draft_preview_drift_signals(
            draft_preview_agent_handoff_acceptance_packet_v2,
            prompt_refresh_monitoring_readiness_packet,
            reversible_draft_preview_offline_smoke_transcript_v2,
        ),
        "escalation_thresholds": {
            "uncited_monitor_check_count": 0,
            "missing_safe_scenario_count": 0,
            "accepted_handoff_note_missing_from_monitoring": 0,
            "prompt_refresh_drift_signal_requires_review": True,
        },
        "escalation_owners": _escalation_owners(prompt_refresh_monitoring_readiness_packet),
        "rollback": {
            "owner": "PP&D draft preview fixture maintainer",
            "owners": _rollback_owners(draft_preview_agent_handoff_acceptance_packet_v2),
            "trigger_ids": [
                "acceptance-packet-citation-loss",
                "draft-preview-boundary-drift",
                "prompt-refresh-monitoring-readiness-failure",
                "offline-smoke-transcript-scenario-loss",
            ],
            "validation": "Rerun only allowed offline validation commands after replacing the committed fixture packet.",
        },
        "rollback_triggers": _rollback_triggers(prompt_refresh_monitoring_readiness_packet),
        "allowed_validation_commands": [list(command) for command in ALLOWED_VALIDATION_COMMANDS],
        "offline_validation_commands": [list(command) for command in ALLOWED_VALIDATION_COMMANDS],
        "attestations": {key: True for key in REQUIRED_ATTESTATIONS},
        "validation_status": "ready_for_fixture_first_offline_monitor_review",
    }
    validate_packet(packet)
    return packet


def validate_packet(packet: Mapping[str, Any]) -> None:
    if packet.get("packet_type") != PACKET_TYPE:
        raise DraftPreviewPostReleaseMonitoringReadinessError("unexpected packet_type")
    if packet.get("packet_version") != PACKET_VERSION:
        raise DraftPreviewPostReleaseMonitoringReadinessError("packet_version must be 2")

    for key in ("monitoring_checks", "draft_preview_drift_signals", "escalation_owners", "rollback_triggers"):
        if not _non_empty_sequence(packet.get(key)):
            raise DraftPreviewPostReleaseMonitoringReadinessError(f"{key} must not be empty")

    for index, check in enumerate(_sequence(packet.get("monitoring_checks"))):
        if not isinstance(check, Mapping):
            raise DraftPreviewPostReleaseMonitoringReadinessError(f"monitoring_checks[{index}] must be a mapping")
        if not _non_empty_sequence(check.get("source_evidence_ids")):
            raise DraftPreviewPostReleaseMonitoringReadinessError(f"monitoring_checks[{index}].source_evidence_ids required")
        if not check.get("escalation_threshold"):
            raise DraftPreviewPostReleaseMonitoringReadinessError(f"monitoring_checks[{index}].escalation_threshold required")

    command_set = {tuple(command) for command in _sequence(packet.get("allowed_validation_commands")) if isinstance(command, Sequence)}
    for command in ALLOWED_VALIDATION_COMMANDS:
        if command not in command_set:
            raise DraftPreviewPostReleaseMonitoringReadinessError("allowed_validation_commands missing required command")

    attestations = packet.get("attestations")
    if not isinstance(attestations, Mapping):
        raise DraftPreviewPostReleaseMonitoringReadinessError("attestations must be a mapping")
    for key in REQUIRED_ATTESTATIONS:
        if attestations.get(key) is not True:
            raise DraftPreviewPostReleaseMonitoringReadinessError(f"attestations.{key} must be true")

    assert_post_release_monitoring_readiness_packet(packet)


def _validate_source_packets(*packets: Mapping[str, Any]) -> None:
    acceptance, prompt_readiness, smoke = packets
    if acceptance.get("packet_type") != "draft_preview_agent_handoff_acceptance_packet_v2":
        raise DraftPreviewPostReleaseMonitoringReadinessError("acceptance packet type mismatch")
    if not _non_empty_sequence(prompt_readiness.get("checks")):
        raise DraftPreviewPostReleaseMonitoringReadinessError("prompt refresh monitoring readiness checks required")
    if smoke.get("fixture_kind") != "reversible_draft_preview_offline_smoke_transcript_v2":
        raise DraftPreviewPostReleaseMonitoringReadinessError("offline smoke transcript fixture kind mismatch")


def _monitoring_checks(
    acceptance: Mapping[str, Any],
    prompt_readiness: Mapping[str, Any],
    smoke: Mapping[str, Any],
) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    accepted = _sequence(_mapping(acceptance.get("consumer_handoff_decisions")).get("accepted"))
    for row in accepted:
        if not isinstance(row, Mapping):
            continue
        decision_id = _text(row.get("decision_id"))
        citations = _citation_ids(row.get("citations"))
        checks.append(
            {
                "check_id": "acceptance:" + decision_id,
                "description": "Confirm the accepted draft preview handoff decision remains cited and limited to reversible preview guidance.",
                "source_evidence_ids": citations,
                "source_packet_roles": ["draft_preview_agent_handoff_acceptance_packet_v2"],
                "escalation_threshold": "escalate if citations are removed or the decision text claims an official action",
                "reviewer_owner": "draft_preview_release_owner",
            }
        )

    for row in _sequence(prompt_readiness.get("checks")):
        if not isinstance(row, Mapping):
            continue
        check_id = _text(row.get("check_id"))
        checks.append(
            {
                "check_id": "prompt-refresh:" + check_id,
                "description": _text(row.get("description")) or "Confirm prompt refresh monitoring readiness remains fixture-backed.",
                "source_evidence_ids": _string_list(row.get("source_evidence_ids")) or _string_list(row.get("citations")),
                "source_packet_roles": ["prompt_refresh_monitoring_readiness_packet"],
                "escalation_threshold": "escalate if prompt refresh readiness loses a cited offline check",
                "reviewer_owner": "prompt_refresh_owner",
            }
        )

    for scenario in _sequence(smoke.get("safe_draft_preview_scenarios")):
        if not isinstance(scenario, Mapping):
            continue
        scenario_id = _text(scenario.get("scenario_id"))
        checks.append(
            {
                "check_id": "smoke-scenario:" + scenario_id,
                "description": "Confirm the offline smoke transcript still covers the safe draft preview scenario.",
                "source_evidence_ids": _string_list(scenario.get("citation_ids")),
                "source_packet_roles": ["reversible_draft_preview_offline_smoke_transcript_v2"],
                "escalation_threshold": "escalate if the scenario is removed or gains consequential operations",
                "reviewer_owner": "agent_safety_owner",
            }
        )
    return checks


def _draft_preview_drift_signals(
    acceptance: Mapping[str, Any],
    prompt_readiness: Mapping[str, Any],
    smoke: Mapping[str, Any],
) -> list[dict[str, Any]]:
    signals = [
        {
            "signal_id": "accepted-handoff-note-citation-drift",
            "description": "An accepted draft preview handoff note loses citation coverage or changes its reversible preview boundary.",
            "source_evidence_ids": _all_acceptance_citation_ids(acceptance),
            "owner": "draft_preview_release_owner",
        },
        {
            "signal_id": "offline-smoke-safe-scenario-drift",
            "description": "A reversible draft preview offline smoke scenario is removed or no longer cites source evidence.",
            "source_evidence_ids": _all_smoke_citation_ids(smoke),
            "owner": "agent_safety_owner",
        },
    ]
    for row in _sequence(prompt_readiness.get("drift_signals")):
        if not isinstance(row, Mapping):
            continue
        signals.append(
            {
                "signal_id": "prompt-refresh:" + _text(row.get("signal_id")),
                "description": _text(row.get("description")) or "Prompt refresh monitoring drift signal requires offline review.",
                "source_evidence_ids": _string_list(row.get("source_evidence_ids")) or ["prompt-refresh-monitoring-readiness-fixture"],
                "owner": "prompt_refresh_owner",
            }
        )
    return signals


def _escalation_owners(prompt_readiness: Mapping[str, Any]) -> list[dict[str, str]]:
    owners = [
        {"owner_id": "draft_preview_release_owner", "scope": "accepted draft preview handoff packet citation and boundary drift"},
        {"owner_id": "prompt_refresh_owner", "scope": "prompt refresh monitoring readiness drift signals"},
        {"owner_id": "agent_safety_owner", "scope": "offline smoke transcript safety scenario drift"},
    ]
    for owner in _string_list(prompt_readiness.get("escalation_owners")):
        owners.append({"owner_id": owner, "scope": "source prompt refresh readiness fixture escalation"})
    return owners


def _rollback_owners(acceptance: Mapping[str, Any]) -> list[str]:
    rollback = acceptance.get("rollback_owner_fields")
    if isinstance(rollback, Mapping):
        owner = _text(rollback.get("owner"))
        if owner:
            return [owner, "prompt_refresh_owner", "agent_safety_owner"]
    return ["draft_preview_release_owner", "prompt_refresh_owner", "agent_safety_owner"]


def _rollback_triggers(prompt_readiness: Mapping[str, Any]) -> list[dict[str, Any]]:
    triggers = [
        {
            "trigger_id": "acceptance-packet-citation-loss",
            "description": "Rollback the fixture packet if any accepted handoff decision loses citations.",
            "owner": "draft_preview_release_owner",
            "source_evidence_ids": ["draft-preview-agent-handoff-acceptance-packet-v2-fixture"],
        },
        {
            "trigger_id": "offline-smoke-scenario-loss",
            "description": "Rollback the fixture packet if offline smoke coverage no longer includes safe draft preview scenarios.",
            "owner": "agent_safety_owner",
            "source_evidence_ids": ["reversible-draft-preview-offline-smoke-transcript-v2-fixture"],
        },
    ]
    for trigger in _sequence(prompt_readiness.get("rollback_triggers")):
        trigger_text = _text(trigger)
        if trigger_text:
            triggers.append(
                {
                    "trigger_id": "prompt-refresh:" + trigger_text,
                    "description": "Rollback the fixture packet if prompt refresh monitoring readiness reports this trigger.",
                    "owner": "prompt_refresh_owner",
                    "source_evidence_ids": ["prompt-refresh-monitoring-readiness-fixture"],
                }
            )
    return triggers


def _all_acceptance_citation_ids(acceptance: Mapping[str, Any]) -> list[str]:
    ids: list[str] = []
    decisions = _mapping(acceptance.get("consumer_handoff_decisions"))
    for bucket in ("accepted", "deferred", "rejected"):
        for row in _sequence(decisions.get(bucket)):
            if isinstance(row, Mapping):
                ids.extend(_citation_ids(row.get("citations")))
    return sorted(set(ids)) or ["draft-preview-agent-handoff-acceptance-packet-v2-fixture"]


def _all_smoke_citation_ids(smoke: Mapping[str, Any]) -> list[str]:
    ids: list[str] = []
    for key in ("safe_draft_preview_scenarios", "blocked_consequential_actions"):
        for row in _sequence(smoke.get(key)):
            if isinstance(row, Mapping):
                ids.extend(_string_list(row.get("citation_ids")))
    return sorted(set(ids)) or ["reversible-draft-preview-offline-smoke-transcript-v2-fixture"]


def _citation_ids(value: Any) -> list[str]:
    ids: list[str] = []
    for row in _sequence(value):
        if isinstance(row, Mapping):
            citation_id = _text(row.get("citation_id")) or _text(row.get("source"))
            if citation_id:
                ids.append(citation_id)
        elif isinstance(row, str) and row.strip():
            ids.append(row.strip())
    return sorted(set(ids))


def _packet_id(packet: Mapping[str, Any], fallback: str) -> str:
    return _text(packet.get("packet_id")) or _text(packet.get("fixture_id")) or fallback


def _mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    return {}


def _sequence(value: Any) -> Sequence[Any]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return value
    return ()


def _non_empty_sequence(value: Any) -> bool:
    return bool(_sequence(value))


def _string_list(value: Any) -> list[str]:
    return [_text(item) for item in _sequence(value) if _text(item)]


def _text(value: Any) -> str:
    if isinstance(value, str):
        return value.strip()
    return ""
