"""Fixture-first offline acceptance rehearsal summary v1.

This module combines offline fixture packets into a cited acceptance rehearsal
summary. It is deliberately side-effect free: it does not crawl, open DevHub,
read private artifacts, perform official actions, or promote active state.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence


PACKET_VERSION = "offline-acceptance-rehearsal-summary-v1"

CONSUMES = (
    "combined_promotion_dependency_packet_v1",
    "guardrail_regression_replay_queue_v1",
    "agent_readiness_delta_packet_v1",
    "action_journal_replay_findings_v1",
)

REQUIRED_ATTESTATIONS = {
    "fixture_first": True,
    "offline_only": True,
    "no_live_crawl": True,
    "no_devhub_session": True,
    "no_private_artifact": True,
    "no_official_action": True,
    "no_active_promotion": True,
}

DEFAULT_VALIDATION_COMMANDS = (
    ("python3", "-m", "pytest", "ppd/tests/test_offline_acceptance_rehearsal_summary_v1.py"),
    ("python3", "ppd/daemon/ppd_daemon.py", "--self-test"),
)

FORBIDDEN_KEYS = frozenset(
    {
        "access_token",
        "auth",
        "auth_artifact",
        "auth_state",
        "authenticated_artifact",
        "browser_artifact",
        "browser_profile",
        "browser_state",
        "cookie",
        "cookies",
        "credentials",
        "devhub_session",
        "download",
        "downloaded_artifact",
        "downloaded_artifacts",
        "downloaded_document",
        "downloaded_documents",
        "har",
        "har_file",
        "local_private_path",
        "password",
        "payment_detail",
        "payment_details",
        "private_artifact",
        "private_artifacts",
        "raw_artifact",
        "raw_body",
        "raw_capture",
        "raw_crawl_output",
        "raw_download",
        "raw_downloaded_artifact",
        "raw_pdf",
        "screenshot",
        "screenshots",
        "secret",
        "session",
        "session_artifact",
        "session_state",
        "storage_state",
        "token",
        "trace",
        "trace_file",
    }
)

FORBIDDEN_TRUE_KEYS = frozenset(
    {
        "active_agent_state_mutated",
        "active_guardrail_mutated",
        "active_guardrail_state_mutated",
        "active_promotion",
        "active_release_promotion",
        "active_release_state_mutated",
        "active_source_mutated",
        "active_source_registry_mutated",
        "active_state_mutated",
        "active_surface_registry_mutated",
        "agent_state_mutated",
        "browser_execution_performed",
        "devhub_execution_performed",
        "guardrail_mutated",
        "guardrail_state_mutated",
        "live_crawl_executed",
        "live_execution_performed",
        "live_network_called",
        "official_action_performed",
        "prompt_mutated",
        "prompt_state_mutated",
        "promotion_executed",
        "release_state_mutated",
        "source_mutated",
        "source_registry_mutated",
        "surface_registry_mutated",
        "uses_devhub_session",
    }
)

FORBIDDEN_TEXT = (
    "auth state",
    "browser state",
    "cookie",
    "credentials",
    "devhub session",
    "downloaded artifact",
    "downloaded document",
    "har file",
    "live crawl executed",
    "live execution performed",
    "official action performed",
    "private artifact",
    "promoted to active",
    "raw crawl output",
    "raw downloaded",
    "screenshot",
    "storage state",
    "trace file",
)

FORBIDDEN_GUARANTEE_TEXT = (
    "approval is guaranteed",
    "guarantee approval",
    "guarantees approval",
    "guaranteed approval",
    "legally compliant",
    "permit approved",
    "permit is approved",
    "permit will be approved",
    "will satisfy code",
    "will satisfy permitting",
    "will secure approval",
)

FORBIDDEN_CONSEQUENTIAL_ACTION_TEXT = (
    "certify acknowledgement",
    "cancel inspection",
    "cancel permit",
    "enter payment details",
    "execute payment",
    "final payment",
    "official upload",
    "pay fees",
    "purchase permit",
    "schedule inspection",
    "submit application",
    "submit permit",
    "submit payment",
    "upload correction",
    "withdraw permit",
)

FORBIDDEN_MUTATION_TEXT = (
    "active agent state mutated",
    "active guardrail mutated",
    "active prompt mutated",
    "active release state mutated",
    "active source registry mutated",
    "active source mutated",
    "active surface registry mutated",
    "mutated active agent state",
    "mutated active guardrail",
    "mutated active prompt",
    "mutated active release state",
    "mutated active source registry",
    "mutated active source",
    "mutated active surface registry",
)


@dataclass(frozen=True)
class OfflineAcceptanceSummaryIssue:
    code: str
    path: str
    message: str


class OfflineAcceptanceSummaryError(ValueError):
    """Raised when a fixture-first acceptance summary cannot be accepted."""

    def __init__(self, issues: Iterable[OfflineAcceptanceSummaryIssue]) -> None:
        self.issues = tuple(issues)
        details = "; ".join(f"{issue.path}: {issue.code}" for issue in self.issues)
        super().__init__(details)


def build_offline_acceptance_rehearsal_summary_v1(source_inputs: Mapping[str, Any]) -> dict[str, Any]:
    """Build an offline acceptance rehearsal summary from fixture packets."""

    combined_packet = _required_mapping(source_inputs, "combined_promotion_dependency_packet_v1")
    replay_queue = _required_mapping(source_inputs, "guardrail_regression_replay_queue_v1")
    delta_packet = _required_mapping(source_inputs, "agent_readiness_delta_packet_v1")
    journal_findings = _required_mapping(source_inputs, "action_journal_replay_findings_v1")

    unresolved_deferrals = _unresolved_deferrals(combined_packet, replay_queue, delta_packet, journal_findings)
    summary = {
        "packet_version": PACKET_VERSION,
        "fixture_first": True,
        "offline_only": True,
        "consumes": list(CONSUMES),
        "acceptance_rows": _acceptance_rows(combined_packet, replay_queue, delta_packet, journal_findings),
        "manual_review_blockers": _manual_review_blockers(combined_packet, replay_queue, delta_packet, journal_findings),
        "unresolved_deferrals": unresolved_deferrals,
        "deferral_handling": _deferral_handling(unresolved_deferrals),
        "rollback_checkpoints": _rollback_checkpoints(combined_packet, replay_queue, delta_packet, journal_findings),
        "validation_command_inventory": _validation_commands(combined_packet, replay_queue, delta_packet, journal_findings),
        "attestations": dict(REQUIRED_ATTESTATIONS),
    }
    require_valid_offline_acceptance_rehearsal_summary_v1(summary)
    return summary


def validate_offline_acceptance_rehearsal_summary_v1(packet: Mapping[str, Any]) -> list[OfflineAcceptanceSummaryIssue]:
    """Return deterministic validation issues for an offline acceptance summary."""

    issues: list[OfflineAcceptanceSummaryIssue] = []
    if packet.get("packet_version") != PACKET_VERSION:
        issues.append(_issue("invalid_version", "packet_version", f"packet_version must be {PACKET_VERSION}"))
    if packet.get("fixture_first") is not True:
        issues.append(_issue("not_fixture_first", "fixture_first", "summary must be fixture-first"))
    if packet.get("offline_only") is not True:
        issues.append(_issue("not_offline_only", "offline_only", "summary must be offline-only"))
    if packet.get("consumes") != list(CONSUMES):
        issues.append(_issue("invalid_consumes", "consumes", "summary must name all four consumed fixture packets"))

    attestations = packet.get("attestations")
    if not isinstance(attestations, Mapping):
        issues.append(_issue("missing_attestations", "attestations", "attestations must be an object"))
    else:
        for key, expected in REQUIRED_ATTESTATIONS.items():
            if attestations.get(key) is not expected:
                issues.append(_issue("missing_attestation", f"attestations.{key}", f"{key} must be {expected}"))

    for section in ("acceptance_rows", "manual_review_blockers", "rollback_checkpoints", "validation_command_inventory"):
        value = packet.get(section)
        if not isinstance(value, list) or not value:
            issues.append(_issue("missing_required_section", section, f"{section} must be a non-empty list"))

    deferral_handling = packet.get("deferral_handling")
    if not isinstance(deferral_handling, Mapping):
        issues.append(_issue("missing_deferral_handling", "deferral_handling", "deferral handling must be an object"))
    else:
        if deferral_handling.get("status") not in {"unresolved_deferrals_present", "no_unresolved_deferrals"}:
            issues.append(_issue("invalid_deferral_status", "deferral_handling.status", "deferral handling status is invalid"))
        if not _non_empty_string_sequence(deferral_handling.get("citations")):
            issues.append(_issue("missing_citations", "deferral_handling.citations", "deferral handling must be cited"))
        if deferral_handling.get("status") == "unresolved_deferrals_present" and not _sequence(packet.get("unresolved_deferrals")):
            issues.append(_issue("missing_deferrals", "unresolved_deferrals", "deferral handling says deferrals are present but none are listed"))

    for section in ("acceptance_rows", "manual_review_blockers", "unresolved_deferrals", "rollback_checkpoints"):
        for index, item in enumerate(_sequence(packet.get(section))):
            path = f"{section}[{index}]"
            if not isinstance(item, Mapping):
                issues.append(_issue("section_entry_not_object", path, "section entries must be objects"))
                continue
            if not _non_empty_string(item.get("id")):
                issues.append(_issue("missing_id", f"{path}.id", "entry id is required"))
            if not _non_empty_string(item.get("summary")):
                issues.append(_issue("missing_summary", f"{path}.summary", "entry summary is required"))
            if not _non_empty_string_sequence(item.get("citations")):
                issues.append(_issue("missing_citations", f"{path}.citations", "entry citations must be non-empty strings"))

    for index, command in enumerate(_sequence(packet.get("validation_command_inventory"))):
        if not _non_empty_string_sequence(command):
            issues.append(_issue("invalid_command", f"validation_command_inventory[{index}]", "commands must be argv lists of strings"))

    issues.extend(_walk_forbidden(packet, "$"))
    return issues


def require_valid_offline_acceptance_rehearsal_summary_v1(packet: Mapping[str, Any]) -> None:
    issues = validate_offline_acceptance_rehearsal_summary_v1(packet)
    if issues:
        raise OfflineAcceptanceSummaryError(issues)


def _acceptance_rows(*packets: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    rows.extend(_rows_from_named_items(packets[0], ("dependency_rows", "promotion_dependencies", "dependencies"), "dependency"))
    rows.extend(_rows_from_named_items(packets[1], ("replay_queue", "replay_rows", "replays"), "guardrail_replay"))
    rows.extend(_rows_from_named_items(packets[2], ("next_safe_action_expectations", "blocked_action_expectations"), "agent_readiness_delta"))
    rows.extend(_rows_from_named_items(packets[3], ("replay_findings", "journal_findings", "findings"), "action_journal_replay"))
    if rows:
        return rows
    return [
        {
            "id": "acceptance.fixture-packets-present",
            "source_packet": "offline_acceptance_summary_builder",
            "summary": "All four required fixture packet inputs were present for offline acceptance rehearsal.",
            "disposition": "accepted_for_offline_review",
            "citations": list(CONSUMES),
        }
    ]


def _manual_review_blockers(*packets: Mapping[str, Any]) -> list[dict[str, Any]]:
    blockers = []
    for packet in packets:
        blockers.extend(_rows_from_named_items(packet, ("manual_review_blockers", "blockers", "review_blockers"), "manual_review"))
    if blockers:
        return blockers
    return [
        {
            "id": "manual-review.confirm-attestations",
            "source_packet": "offline_acceptance_summary_builder",
            "summary": "Human reviewer must confirm fixture-only attestations before any later live or active promotion planning.",
            "disposition": "manual_review_required",
            "citations": list(CONSUMES),
        }
    ]


def _unresolved_deferrals(*packets: Mapping[str, Any]) -> list[dict[str, Any]]:
    deferrals = []
    for packet in packets:
        deferrals.extend(_rows_from_named_items(packet, ("unresolved_deferrals", "deferrals", "deferred_items"), "deferral"))
    return deferrals


def _deferral_handling(deferrals: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    if deferrals:
        citations = []
        for deferral in deferrals:
            citations.extend(_citations(deferral))
        return {
            "status": "unresolved_deferrals_present",
            "summary": "Unresolved deferrals remain manual-review items and are not treated as accepted release evidence.",
            "citations": _dedupe_strings(citations) or list(CONSUMES),
        }
    return {
        "status": "no_unresolved_deferrals",
        "summary": "No unresolved deferrals were present in the consumed offline fixture packets.",
        "citations": list(CONSUMES),
    }


def _rollback_checkpoints(*packets: Mapping[str, Any]) -> list[dict[str, Any]]:
    checkpoints = []
    for packet in packets:
        checkpoints.extend(_rows_from_named_items(packet, ("rollback_checkpoints", "rollback_notes"), "rollback"))
    if checkpoints:
        return checkpoints
    return [
        {
            "id": "rollback.keep-active-state-unchanged",
            "source_packet": "offline_acceptance_summary_builder",
            "summary": "Rollback checkpoint is to leave active source, guardrail, prompt, agent, and release state unchanged.",
            "disposition": "available",
            "citations": list(CONSUMES),
        }
    ]


def _validation_commands(*packets: Mapping[str, Any]) -> list[list[str]]:
    commands: list[list[str]] = [list(command) for command in DEFAULT_VALIDATION_COMMANDS]
    for packet in packets:
        for key in ("validation_command_inventory", "offline_validation_commands", "validation_commands"):
            for command in _sequence(packet.get(key)):
                if _non_empty_string_sequence(command):
                    normalized = [str(part) for part in command]
                    if normalized not in commands:
                        commands.append(normalized)
    return commands


def _rows_from_named_items(packet: Mapping[str, Any], names: Sequence[str], source_packet: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for name in names:
        for index, item in enumerate(_sequence(packet.get(name))):
            if isinstance(item, Mapping):
                citations = _citations(item) or _citations(packet) or [source_packet]
                row_id = item.get("id") or item.get("row_id") or item.get("checkpoint_id") or item.get("blocker_id") or item.get("finding_id")
                summary = item.get("summary") or item.get("description") or item.get("reason") or item.get("rollback_note") or item.get("rule")
                disposition = item.get("disposition") or item.get("status") or item.get("expected_outcome") or "review"
            else:
                row_id = None
                summary = item if isinstance(item, str) else None
                disposition = "review"
                citations = _citations(packet) or [source_packet]
            rows.append(
                {
                    "id": str(row_id or f"{source_packet}.{name}.{index}"),
                    "source_packet": source_packet,
                    "summary": str(summary or f"Offline acceptance input from {name}."),
                    "disposition": str(disposition),
                    "citations": citations,
                }
            )
    return rows


def _required_mapping(source_inputs: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = source_inputs.get(key)
    if not isinstance(value, Mapping):
        raise OfflineAcceptanceSummaryError((_issue("missing_input", key, f"{key} must be an object"),))
    issues = _walk_forbidden(value, key)
    if issues:
        raise OfflineAcceptanceSummaryError(issues)
    return value


def _citations(value: Mapping[str, Any]) -> list[str]:
    citations = value.get("citations") or value.get("fixture_refs") or value.get("source_fixture_refs")
    if isinstance(citations, Mapping):
        return [str(item) for item in citations.values() if _non_empty_string(item)]
    if isinstance(citations, list):
        return [str(item) for item in citations if _non_empty_string(item)]
    return []


def _walk_forbidden(value: Any, path: str) -> list[OfflineAcceptanceSummaryIssue]:
    issues: list[OfflineAcceptanceSummaryIssue] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            normalized = str(key).strip().lower().replace("-", "_").replace(" ", "_")
            if normalized in FORBIDDEN_KEYS:
                issues.append(_issue("forbidden_artifact_key", child_path, "private, raw, authenticated, browser, downloaded, or payment artifact keys are forbidden"))
            if normalized in FORBIDDEN_TRUE_KEYS and child is True:
                issues.append(_issue("forbidden_true_flag", child_path, "live, official action, promotion, or active-state mutation flags must not be true"))
            issues.extend(_walk_forbidden(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            issues.extend(_walk_forbidden(child, f"{path}[{index}]"))
    elif isinstance(value, str):
        lowered = value.lower()
        for forbidden in FORBIDDEN_TEXT:
            if forbidden in lowered:
                issues.append(_issue("forbidden_text", path, f"forbidden text: {forbidden}"))
        for forbidden in FORBIDDEN_GUARANTEE_TEXT:
            if forbidden in lowered:
                issues.append(_issue("forbidden_outcome_guarantee", path, f"forbidden legal or permitting outcome guarantee: {forbidden}"))
        for forbidden in FORBIDDEN_CONSEQUENTIAL_ACTION_TEXT:
            if forbidden in lowered:
                issues.append(_issue("forbidden_consequential_action_language", path, f"forbidden consequential action language: {forbidden}"))
        for forbidden in FORBIDDEN_MUTATION_TEXT:
            if forbidden in lowered:
                issues.append(_issue("forbidden_active_state_mutation", path, f"forbidden active-state mutation language: {forbidden}"))
    return issues


def _dedupe_strings(values: Iterable[str]) -> list[str]:
    deduped: list[str] = []
    for value in values:
        if _non_empty_string(value) and value not in deduped:
            deduped.append(value)
    return deduped


def _sequence(value: Any) -> tuple[Any, ...]:
    if isinstance(value, list):
        return tuple(value)
    return ()


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _non_empty_string_sequence(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(_non_empty_string(item) for item in value)


def _issue(code: str, path: str, message: str) -> OfflineAcceptanceSummaryIssue:
    return OfflineAcceptanceSummaryIssue(code, path, message)


__all__ = [
    "CONSUMES",
    "DEFAULT_VALIDATION_COMMANDS",
    "PACKET_VERSION",
    "REQUIRED_ATTESTATIONS",
    "OfflineAcceptanceSummaryError",
    "OfflineAcceptanceSummaryIssue",
    "build_offline_acceptance_rehearsal_summary_v1",
    "require_valid_offline_acceptance_rehearsal_summary_v1",
    "validate_offline_acceptance_rehearsal_summary_v1",
]
