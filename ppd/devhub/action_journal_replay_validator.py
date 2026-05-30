"""Deterministic replay validator for PP&D action journal acceptance packet v1."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Any, Mapping, Sequence

from ppd.action_journal_acceptance_packet_v1 import (
    REQUIRED_ATTESTATIONS,
    validate_action_journal_acceptance_packet_v1,
)

ACCEPTANCE_PACKET_FIXTURE = (
    Path(__file__).resolve().parents[1]
    / "tests"
    / "fixtures"
    / "action_journal_acceptance_packet_v1.json"
)

EXPECTED_OFFLINE_VALIDATION_COMMANDS = (("python3", "ppd/daemon/ppd_daemon.py", "--self-test"),)

EXPECTED_EVENT_REPLAY_ORDER = (
    "public_crawl_preflight",
    "requirement_extraction",
    "user_gap_analysis",
    "reversible_draft_preview",
    "devhub_read_only_observation",
    "refusal",
)

_RESTRICTED_REPLAY_VALUE_PATTERNS = {
    "browser artifact": re.compile(r"\.(?:har|trace|png|jpe?g|webp|zip)\b|\b(?:screenshot|screenshots|trace file|har data|browser trace)\b", re.IGNORECASE),
    "private local path": re.compile(r"(?:file://|/(?:home|Users|private|tmp|var/folders)/[^\s]+|[A-Za-z]:\\[^\s]+)"),
    "raw crawl or PDF body": re.compile(r"\b(?:raw crawl body|raw crawl output|raw pdf body|raw PDF body|full html body|full pdf text|pdf body)\b", re.IGNORECASE),
    "unredacted evidence": re.compile(r"\b(?:unredacted|actual user value|private field value|unredacted field value|applicant ssn)\b", re.IGNORECASE),
    "outcome guarantee": re.compile(r"\b(?:guarantee[sd]?|will be approved|approval is assured|permit approval is assured|legal outcome is assured|issuance is guaranteed)\b", re.IGNORECASE),
}

_RESTRICTED_REPLAY_KEY_TERMS = frozenset(
    {
        "absolute_path",
        "downloaded_document",
        "har",
        "har_data",
        "local_path",
        "local_private_path",
        "pdf_body",
        "private_path",
        "raw_body",
        "raw_crawl_body",
        "raw_crawl_output",
        "raw_pdf_body",
        "screenshot",
        "screenshots",
        "trace",
        "traces",
    }
)

_MUTATION_FLAG_KEY_TERMS = frozenset(
    {
        "active_source_mutation",
        "source_mutation",
        "active_surface_registry_mutation",
        "surface_registry_mutation",
        "active_guardrail_mutation",
        "guardrail_mutation",
        "active_prompt_mutation",
        "prompt_mutation",
        "active_release_state_mutation",
        "release_state_mutation",
        "active_agent_state_mutation",
        "agent_state_mutation",
    }
)

_MUTATION_REPLAY_VALUE_PATTERN = re.compile(
    r"\b(?:mutate|write|promote|activate|update)\b.{0,80}\b(?:source|source registry|surface registry|guardrail|prompt|release state|agent state)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ActionJournalReplayFindingV1:
    """Single deterministic replay finding for the committed action journal fixture."""

    code: str
    ok: bool
    summary: str
    details: Mapping[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "ok": self.ok,
            "summary": self.summary,
            "details": _jsonable(self.details),
        }


@dataclass(frozen=True)
class ActionJournalReplayReportV1:
    """Replay report emitted from the fixture-first action journal validator."""

    ok: bool
    fixture_path: str
    packet_version: str
    event_count: int
    findings: tuple[ActionJournalReplayFindingV1, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "fixture_path": self.fixture_path,
            "packet_version": self.packet_version,
            "event_count": self.event_count,
            "findings": [finding.to_dict() for finding in self.findings],
        }


def load_committed_action_journal_acceptance_packet_v1(
    fixture_path: Path | str = ACCEPTANCE_PACKET_FIXTURE,
) -> dict[str, Any]:
    """Load the committed action journal acceptance packet v1 fixture."""

    path = Path(fixture_path)
    with path.open(encoding="utf-8") as fixture_file:
        loaded = json.load(fixture_file)
    if not isinstance(loaded, dict):
        raise ValueError("action journal acceptance packet fixture must contain a JSON object")
    return loaded


def replay_committed_action_journal_acceptance_packet_v1(
    fixture_path: Path | str = ACCEPTANCE_PACKET_FIXTURE,
) -> ActionJournalReplayReportV1:
    """Read the committed fixture and emit deterministic replay findings."""

    path = Path(fixture_path)
    packet = load_committed_action_journal_acceptance_packet_v1(path)
    return replay_action_journal_acceptance_packet_v1(packet, fixture_path=path)


def replay_action_journal_acceptance_packet_v1(
    packet: Mapping[str, Any],
    *,
    fixture_path: Path | str = ACCEPTANCE_PACKET_FIXTURE,
) -> ActionJournalReplayReportV1:
    """Replay the acceptance packet fixture checks without live network or browser state."""

    findings = (
        _replay_acceptance_packet_contract(packet),
        _replay_event_ordering(packet),
        _replay_citation_coverage(packet),
        _replay_redacted_evidence_summaries(packet),
        _replay_reviewer_owner_assignments(packet),
        _replay_offline_validation_commands(packet),
        _replay_safety_attestations(packet),
    )
    return ActionJournalReplayReportV1(
        ok=all(finding.ok for finding in findings),
        fixture_path=Path(fixture_path).as_posix(),
        packet_version=str(packet.get("packet_version", "")),
        event_count=len(_journal_events(packet)),
        findings=findings,
    )


def assert_action_journal_replay_report_v1(report: ActionJournalReplayReportV1) -> None:
    """Raise AssertionError when replay findings are not all passing."""

    if report.ok:
        return
    failed = [finding for finding in report.findings if not finding.ok]
    lines = [f"{finding.code}: {finding.summary}" for finding in failed]
    raise AssertionError("action journal replay validation failed:\n" + "\n".join(lines))


def _replay_acceptance_packet_contract(packet: Mapping[str, Any]) -> ActionJournalReplayFindingV1:
    result = validate_action_journal_acceptance_packet_v1(packet)
    return ActionJournalReplayFindingV1(
        code="acceptance_packet_contract",
        ok=result.ok,
        summary="Acceptance packet contract validation passed."
        if result.ok
        else "Acceptance packet contract validation failed.",
        details={
            "event_count": result.event_count,
            "event_types": result.event_types,
            "problems": result.problems,
        },
    )


def _replay_event_ordering(packet: Mapping[str, Any]) -> ActionJournalReplayFindingV1:
    events = _journal_events(packet)
    actual_order = tuple(str(event.get("event_type", "")) for event in events)
    event_ids = tuple(str(event.get("event_id", "")) for event in events)
    duplicate_ids = _duplicates(event_ids)
    missing_prerequisites = tuple(event_type for event_type in EXPECTED_EVENT_REPLAY_ORDER if event_type not in actual_order)
    ok = actual_order == EXPECTED_EVENT_REPLAY_ORDER and not duplicate_ids and not missing_prerequisites
    return ActionJournalReplayFindingV1(
        code="event_ordering",
        ok=ok,
        summary="Journal events replay in the expected deterministic v1 order."
        if ok
        else "Journal events do not replay in the expected deterministic v1 order.",
        details={
            "expected_order": EXPECTED_EVENT_REPLAY_ORDER,
            "actual_order": actual_order,
            "event_ids": event_ids,
            "duplicate_event_ids": duplicate_ids,
            "missing_prerequisite_event_types": missing_prerequisites,
        },
    )


def _replay_citation_coverage(packet: Mapping[str, Any]) -> ActionJournalReplayFindingV1:
    events = _journal_events(packet)
    uncited_event_ids: list[str] = []
    non_https_citation_refs: list[str] = []
    citation_counts: dict[str, int] = {}
    for event in events:
        event_id = str(event.get("event_id", ""))
        citations = event.get("citations")
        if not isinstance(citations, list) or not citations:
            uncited_event_ids.append(event_id)
            citation_counts[event_id] = 0
            continue
        citation_counts[event_id] = len(citations)
        for index, citation in enumerate(citations):
            if not isinstance(citation, Mapping) or not str(citation.get("url", "")).startswith("https://"):
                non_https_citation_refs.append(f"{event_id}.citations[{index}]")
    ok = not uncited_event_ids and not non_https_citation_refs and set(citation_counts) == set(_event_ids(events))
    return ActionJournalReplayFindingV1(
        code="citation_coverage",
        ok=ok,
        summary="Every replayed event has cited HTTPS source coverage."
        if ok
        else "One or more replayed events lack cited HTTPS source coverage.",
        details={
            "citation_counts_by_event_id": citation_counts,
            "uncited_event_ids": tuple(uncited_event_ids),
            "non_https_citation_refs": tuple(non_https_citation_refs),
        },
    )


def _replay_redacted_evidence_summaries(packet: Mapping[str, Any]) -> ActionJournalReplayFindingV1:
    missing_summary_event_ids: list[str] = []
    raw_evidence_event_ids: list[str] = []
    missing_redaction_event_ids: list[str] = []
    restricted_summary_refs: list[str] = []
    redaction_counts: dict[str, int] = {}
    for event in _journal_events(packet):
        event_id = str(event.get("event_id", ""))
        summary = event.get("redacted_evidence_summary")
        if not isinstance(summary, Mapping):
            missing_summary_event_ids.append(event_id)
            redaction_counts[event_id] = 0
            continue
        summary_text = str(summary.get("summary", ""))
        if not summary_text.strip():
            missing_summary_event_ids.append(event_id)
        restricted_summary_refs.extend(
            f"{event_id}{path[1:]}" for path in _restricted_replay_material_paths(summary)
        )
        if summary.get("raw_evidence_included") is not False:
            raw_evidence_event_ids.append(event_id)
        redactions = summary.get("redactions_applied")
        if not isinstance(redactions, list) or not redactions or not all(isinstance(item, str) and item.strip() for item in redactions):
            missing_redaction_event_ids.append(event_id)
            redaction_counts[event_id] = 0
        else:
            redaction_counts[event_id] = len(redactions)
    ok = (
        not missing_summary_event_ids
        and not raw_evidence_event_ids
        and not missing_redaction_event_ids
        and not restricted_summary_refs
    )
    return ActionJournalReplayFindingV1(
        code="redacted_evidence_summaries",
        ok=ok,
        summary="Every replayed event has a redacted evidence summary and excludes raw evidence."
        if ok
        else "One or more replayed events have incomplete redacted evidence summaries.",
        details={
            "redaction_counts_by_event_id": redaction_counts,
            "missing_summary_event_ids": tuple(missing_summary_event_ids),
            "raw_evidence_event_ids": tuple(raw_evidence_event_ids),
            "missing_redaction_event_ids": tuple(missing_redaction_event_ids),
            "restricted_summary_refs": tuple(restricted_summary_refs),
        },
    )


def _replay_reviewer_owner_assignments(packet: Mapping[str, Any]) -> ActionJournalReplayFindingV1:
    reviewer_owner_fields = packet.get("reviewer_owner_fields")
    packet_fields_ok = isinstance(reviewer_owner_fields, Mapping) and all(
        str(reviewer_owner_fields.get(field, "")).strip()
        for field in ("packet_owner", "technical_reviewer", "policy_reviewer")
    )
    unassigned_event_ids: list[str] = []
    assignments: dict[str, dict[str, str]] = {}
    for event in _journal_events(packet):
        event_id = str(event.get("event_id", ""))
        owner = str(event.get("owner", "")).strip()
        reviewer = str(event.get("reviewer", "")).strip()
        assignments[event_id] = {"owner": owner, "reviewer": reviewer}
        if not owner or not reviewer:
            unassigned_event_ids.append(event_id)
    ok = packet_fields_ok and not unassigned_event_ids
    details: dict[str, Any] = {
        "packet_owner": "",
        "technical_reviewer": "",
        "policy_reviewer": "",
        "assignments_by_event_id": assignments,
        "unassigned_event_ids": tuple(unassigned_event_ids),
    }
    if isinstance(reviewer_owner_fields, Mapping):
        details.update(
            {
                "packet_owner": str(reviewer_owner_fields.get("packet_owner", "")),
                "technical_reviewer": str(reviewer_owner_fields.get("technical_reviewer", "")),
                "policy_reviewer": str(reviewer_owner_fields.get("policy_reviewer", "")),
            }
        )
    return ActionJournalReplayFindingV1(
        code="reviewer_owner_assignments",
        ok=ok,
        summary="Packet and event reviewer-owner assignments are complete."
        if ok
        else "Packet or event reviewer-owner assignments are incomplete.",
        details=details,
    )


def _replay_offline_validation_commands(packet: Mapping[str, Any]) -> ActionJournalReplayFindingV1:
    commands = _tuple_commands(packet.get("offline_validation_commands"))
    ok = commands == EXPECTED_OFFLINE_VALIDATION_COMMANDS
    return ActionJournalReplayFindingV1(
        code="offline_validation_commands",
        ok=ok,
        summary="Offline validation commands are deterministic and limited to the PP&D daemon self-test."
        if ok
        else "Offline validation commands differ from the deterministic PP&D daemon self-test command.",
        details={
            "expected_commands": EXPECTED_OFFLINE_VALIDATION_COMMANDS,
            "actual_commands": commands,
        },
    )


def _replay_safety_attestations(packet: Mapping[str, Any]) -> ActionJournalReplayFindingV1:
    attestations = packet.get("attestations")
    missing_or_false: list[str] = []
    if not isinstance(attestations, Mapping):
        missing_or_false = sorted(REQUIRED_ATTESTATIONS)
        attestation_values: dict[str, bool] = {}
    else:
        attestation_values = {name: attestations.get(name) is True for name in sorted(REQUIRED_ATTESTATIONS)}
        missing_or_false = [name for name, is_true in attestation_values.items() if not is_true]
    restricted_material_paths = _restricted_replay_material_paths(packet)
    active_mutation_flag_paths = _active_mutation_flag_paths(packet)
    uncited_replay_finding_paths = _uncited_replay_finding_paths(packet)
    ok = (
        not missing_or_false
        and not restricted_material_paths
        and not active_mutation_flag_paths
        and not uncited_replay_finding_paths
    )
    return ActionJournalReplayFindingV1(
        code="safety_attestations",
        ok=ok,
        summary="Required replay safety attestations are present and no restricted replay material or active mutation flags are included."
        if ok
        else "One or more replay safety attestations or restricted-material checks failed.",
        details={
            "required_attestations": tuple(sorted(REQUIRED_ATTESTATIONS)),
            "attestation_values": attestation_values,
            "missing_or_false_attestations": tuple(missing_or_false),
            "restricted_material_paths": restricted_material_paths,
            "active_mutation_flag_paths": active_mutation_flag_paths,
            "uncited_replay_finding_paths": uncited_replay_finding_paths,
            "attestation_groups": {
                "no_credential": "no_credentials",
                "no_cookie": "no_cookies",
                "no_private_value": "no_private_values",
                "no_browser_artifact": ("no_screenshots", "no_traces", "no_har"),
                "no_payment": "no_payment",
                "no_official_action": "no_official_action",
                "no_private_local_path": "no_private_local_paths",
                "no_raw_body": "no_raw_crawl_or_pdf_bodies",
                "no_outcome_guarantee": "no_legal_or_permitting_outcome_guarantees",
                "no_active_mutation": (
                    "no_active_source_mutation",
                    "no_active_surface_registry_mutation",
                    "no_active_guardrail_mutation",
                    "no_active_prompt_mutation",
                    "no_active_release_state_mutation",
                    "no_active_agent_state_mutation",
                ),
            },
        },
    )


def _restricted_replay_material_paths(value: Any, path: str = "$") -> tuple[str, ...]:
    paths: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            child_path = f"{path}.{key_text}"
            normalized = _normalize_replay_key(key_text)
            if not normalized.startswith("no_") and normalized in _RESTRICTED_REPLAY_KEY_TERMS:
                paths.append(child_path)
            paths.extend(_restricted_replay_material_paths(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            paths.extend(_restricted_replay_material_paths(child, f"{path}[{index}]"))
    elif isinstance(value, str):
        for reason, pattern in _RESTRICTED_REPLAY_VALUE_PATTERNS.items():
            if pattern.search(value):
                paths.append(f"{path} ({reason})")
        if _MUTATION_REPLAY_VALUE_PATTERN.search(value):
            paths.append(f"{path} (active mutation language)")
    return tuple(paths)


def _active_mutation_flag_paths(value: Any, path: str = "$") -> tuple[str, ...]:
    paths: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            child_path = f"{path}.{key_text}"
            normalized = _normalize_replay_key(key_text)
            if normalized.startswith("no_"):
                continue
            if normalized in _MUTATION_FLAG_KEY_TERMS and child not in (False, None):
                paths.append(child_path)
            elif normalized == "active_mutation_flags" and child not in ([], (), {}, False, None):
                paths.append(child_path)
            paths.extend(_active_mutation_flag_paths(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            paths.extend(_active_mutation_flag_paths(child, f"{path}[{index}]"))
    return tuple(paths)


def _uncited_replay_finding_paths(packet: Mapping[str, Any]) -> tuple[str, ...]:
    findings = packet.get("replay_findings")
    if findings is None:
        return ()
    if not isinstance(findings, list):
        return ("$.replay_findings",)
    uncited: list[str] = []
    for index, finding in enumerate(findings):
        path = f"$.replay_findings[{index}]"
        if not isinstance(finding, Mapping):
            uncited.append(path)
            continue
        citations = finding.get("citations")
        if not isinstance(citations, list) or not citations:
            uncited.append(path)
            continue
        for citation_index, citation in enumerate(citations):
            if not isinstance(citation, Mapping) or not str(citation.get("url", "")).startswith("https://"):
                uncited.append(f"{path}.citations[{citation_index}]")
    return tuple(uncited)


def _journal_events(packet: Mapping[str, Any]) -> tuple[Mapping[str, Any], ...]:
    events = packet.get("journal_events")
    if not isinstance(events, list):
        return ()
    return tuple(event for event in events if isinstance(event, Mapping))


def _event_ids(events: Sequence[Mapping[str, Any]]) -> tuple[str, ...]:
    return tuple(str(event.get("event_id", "")) for event in events)


def _duplicates(values: Sequence[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    duplicates: list[str] = []
    for value in values:
        if value in seen and value not in duplicates:
            duplicates.append(value)
        seen.add(value)
    return tuple(duplicates)


def _tuple_commands(value: Any) -> tuple[tuple[str, ...], ...]:
    if not isinstance(value, list):
        return ()
    commands: list[tuple[str, ...]] = []
    for command in value:
        if isinstance(command, list):
            commands.append(tuple(str(part) for part in command))
        else:
            commands.append((str(command),))
    return tuple(commands)


def _normalize_replay_key(value: str) -> str:
    return value.strip().lower().replace("-", "_").replace(" ", "_")


def _jsonable(value: Any) -> Any:
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(child) for key, child in value.items()}
    return value


__all__ = [
    "ACCEPTANCE_PACKET_FIXTURE",
    "EXPECTED_EVENT_REPLAY_ORDER",
    "EXPECTED_OFFLINE_VALIDATION_COMMANDS",
    "ActionJournalReplayFindingV1",
    "ActionJournalReplayReportV1",
    "assert_action_journal_replay_report_v1",
    "load_committed_action_journal_acceptance_packet_v1",
    "replay_action_journal_acceptance_packet_v1",
    "replay_committed_action_journal_acceptance_packet_v1",
]
