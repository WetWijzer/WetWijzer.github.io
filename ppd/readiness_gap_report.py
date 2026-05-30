"""Fixture-first PP&D readiness gap report v1.

The report intentionally consumes committed packet-shaped dictionaries and emits a
commit-safe readiness artifact. It performs no live crawl, DevHub access, private
artifact reads, official actions, or active state mutation.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

REQUIRED_PACKET_KEYS = (
    "readiness_ledger_v1",
    "source_to_requirement_traceability_packet_v1",
    "guardrail_to_agent_explanation_packet_v1",
    "reversible_draft_preview_handoff_packet_v4",
    "action_journal_replay_validator_v1",
    "attended_devhub_observation_dry_run_runbook_v1",
)

ATTESTATIONS = {
    "no_live_crawl": True,
    "no_devhub": True,
    "no_private_artifact": True,
    "no_official_action": True,
    "no_active_state_mutation": True,
}

DEFAULT_OFFLINE_VALIDATION_COMMANDS = [
    ["python3", "-m", "py_compile", "ppd/readiness_gap_report.py"],
    ["python3", "-m", "pytest", "ppd/tests/test_readiness_gap_report_v1.py"],
]

SUPPORTED_READINESS_TOPICS = {
    "source_citation_coverage",
    "guardrail_explanation",
    "reversible_draft_preview",
    "action_journal_replay",
    "attended_devhub_dry_run",
    "manual_review_blocker",
}

MUTATION_FLAG_KEYS = {
    "active_source_mutation",
    "source_registry_mutation",
    "surface_registry_mutation",
    "guardrail_mutation",
    "prompt_mutation",
    "release_state_mutation",
    "agent_state_mutation",
}

PRIVATE_ARTIFACT_KEYS = {
    "auth_state",
    "browser_state",
    "cookie_jar",
    "credentials",
    "devhub_session_file",
    "downloaded_document_path",
    "har_path",
    "local_private_file_path",
    "payment_details",
    "private_artifact_ref",
    "private_upload_path",
    "raw_crawl_output",
    "raw_pdf_bytes",
    "raw_pdf_path",
    "screenshot_path",
    "session_storage",
    "storage_state",
    "trace_path",
}

RAW_OR_PRIVATE_VALUE_RE = re.compile(
    r"(trace\.zip|\.har\b|storage_state|session\.json|raw[_ -]?(crawl|pdf)|"
    r"screenshot\.(png|jpg)|/home/[^\s]+|C:\\\\Users\\\\|cookie jar|auth state)",
    re.IGNORECASE,
)

LIVE_EXECUTION_RE = re.compile(
    r"\b(live crawl completed|logged in to devhub|executed live|ran live|clicked submit|"
    r"submitted the application|uploaded corrections|paid fees|scheduled inspection)\b",
    re.IGNORECASE,
)

OUTCOME_GUARANTEE_RE = re.compile(
    r"\b(guarantee[sd]?|assure[sd]?|will be approved|permit approval is certain|"
    r"approval guaranteed|legally sufficient|complies with all code)\b",
    re.IGNORECASE,
)

CONSEQUENTIAL_ACTION_RE = re.compile(
    r"\b(agent|automation|worker|system|report)\s+(may|can|will|should|is ready to)\s+"
    r"(submit|upload|certify|pay|schedule|cancel)\b|"
    r"\bnext safe action\s*:\s*(submit|upload|certify|pay|schedule|cancel)\b",
    re.IGNORECASE,
)

NEGATION_RE = re.compile(
    r"\b(no|not|never|does not|do not|without|rejects?|refuses?|blocks?|stops?|requires attendance|requires exact confirmation)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class GapInput:
    """Normalized remaining readiness item."""

    gap_id: str
    title: str
    status: str
    blocker: str
    dependencies: tuple[str, ...]
    reviewer_owner: str
    reviewer_role: str
    source_requirement_ids: tuple[str, ...]
    guardrail_ids: tuple[str, ...]
    draft_preview_ids: tuple[str, ...]
    journal_validator_ids: tuple[str, ...]
    devhub_runbook_step_ids: tuple[str, ...]
    offline_validation_commands: tuple[tuple[str, ...], ...]


def load_packet_file(path: Path) -> dict[str, Any]:
    """Load a fixture packet file without following any external references."""

    with path.open("r", encoding="utf-8") as packet_file:
        value = json.load(packet_file)
    if not isinstance(value, dict):
        raise ValueError("readiness gap report packet file must contain a JSON object")
    return value


def build_readiness_gap_report(packets: dict[str, Any]) -> dict[str, Any]:
    """Build a deterministic readiness gap report from fixture packets."""

    _validate_commit_safe_packet_content(packets)
    missing_packets = [key for key in REQUIRED_PACKET_KEYS if key not in packets]
    if missing_packets:
        raise ValueError(f"missing required packet(s): {', '.join(missing_packets)}")

    gaps = _remaining_gap_inputs(packets)
    _validate_declared_dependency_order(packets, gaps)
    ordered_gaps = _dependency_order(gaps)
    rows = [_gap_row(gap, packets) for gap in ordered_gaps]
    _validate_gap_rows_are_cited(rows)

    return {
        "artifact_type": "ppd_readiness_gap_report_v1",
        "schema_version": 1,
        "source_packets": list(REQUIRED_PACKET_KEYS),
        "attestations": dict(ATTESTATIONS),
        "offline_validation_commands": DEFAULT_OFFLINE_VALIDATION_COMMANDS,
        "remaining_gap_rows": rows,
        "dependency_order": [gap.gap_id for gap in ordered_gaps],
        "reviewer_owner_fields": [
            {
                "gap_id": gap.gap_id,
                "reviewer_owner": gap.reviewer_owner,
                "reviewer_role": gap.reviewer_role,
            }
            for gap in ordered_gaps
        ],
    }


def _remaining_gap_inputs(packets: dict[str, Any]) -> list[GapInput]:
    ledger = packets["readiness_ledger_v1"]
    readiness_items = ledger.get("readiness_items", [])
    if not isinstance(readiness_items, list):
        raise ValueError("readiness_ledger_v1.readiness_items must be a list")

    gaps: list[GapInput] = []
    for item in readiness_items:
        if not isinstance(item, dict):
            raise ValueError("readiness ledger item must be an object")
        topic = item.get("readiness_topic")
        if topic is not None and topic not in SUPPORTED_READINESS_TOPICS:
            raise ValueError(f"unsupported readiness topic: {topic}")
        status = _required_string(item, "status")
        if status == "ready":
            continue
        gaps.append(
            GapInput(
                gap_id=_required_string(item, "gap_id"),
                title=_required_string(item, "title"),
                status=status,
                blocker=_required_string(item, "blocker"),
                dependencies=tuple(_string_list(item.get("dependencies", []), "dependencies")),
                reviewer_owner=_required_string(item, "reviewer_owner"),
                reviewer_role=_required_string(item, "reviewer_role"),
                source_requirement_ids=tuple(_string_list(item.get("source_requirement_ids", []), "source_requirement_ids")),
                guardrail_ids=tuple(_string_list(item.get("guardrail_ids", []), "guardrail_ids")),
                draft_preview_ids=tuple(_string_list(item.get("draft_preview_ids", []), "draft_preview_ids")),
                journal_validator_ids=tuple(_string_list(item.get("journal_validator_ids", []), "journal_validator_ids")),
                devhub_runbook_step_ids=tuple(_string_list(item.get("devhub_runbook_step_ids", []), "devhub_runbook_step_ids")),
                offline_validation_commands=tuple(
                    tuple(command)
                    for command in _command_list(
                        item.get("offline_validation_commands", DEFAULT_OFFLINE_VALIDATION_COMMANDS)
                    )
                ),
            )
        )
    return gaps


def _dependency_order(gaps: list[GapInput]) -> list[GapInput]:
    by_id = {gap.gap_id: gap for gap in gaps}
    ordered: list[GapInput] = []
    temporary: set[str] = set()
    permanent: set[str] = set()

    for gap in gaps:
        for dependency_id in gap.dependencies:
            if dependency_id not in by_id:
                raise ValueError(f"gap {gap.gap_id} references missing dependency {dependency_id}")

    def visit(gap_id: str) -> None:
        if gap_id in permanent:
            return
        if gap_id in temporary:
            raise ValueError(f"cycle detected in readiness gap dependencies at {gap_id}")
        temporary.add(gap_id)
        for dependency_id in by_id[gap_id].dependencies:
            visit(dependency_id)
        temporary.remove(gap_id)
        permanent.add(gap_id)
        ordered.append(by_id[gap_id])

    for gap in sorted(gaps, key=lambda item: item.gap_id):
        visit(gap.gap_id)
    return ordered


def _gap_row(gap: GapInput, packets: dict[str, Any]) -> dict[str, Any]:
    return {
        "gap_id": gap.gap_id,
        "title": gap.title,
        "status": gap.status,
        "blocker": gap.blocker,
        "dependencies": list(gap.dependencies),
        "reviewer_owner": gap.reviewer_owner,
        "reviewer_role": gap.reviewer_role,
        "citations": _citations_for_gap(gap, packets),
        "offline_validation_commands": [list(command) for command in gap.offline_validation_commands],
        "attestations": dict(ATTESTATIONS),
    }


def _citations_for_gap(gap: GapInput, packets: dict[str, Any]) -> list[dict[str, str]]:
    citations: list[dict[str, str]] = []
    citations.extend(
        _lookup_citations(
            packets["source_to_requirement_traceability_packet_v1"].get("requirement_traces", []),
            "requirement_id",
            gap.source_requirement_ids,
            "source_requirement",
        )
    )
    citations.extend(
        _lookup_citations(
            packets["guardrail_to_agent_explanation_packet_v1"].get("guardrail_explanations", []),
            "guardrail_id",
            gap.guardrail_ids,
            "guardrail_explanation",
        )
    )
    citations.extend(
        _lookup_citations(
            packets["reversible_draft_preview_handoff_packet_v4"].get("draft_previews", []),
            "draft_preview_id",
            gap.draft_preview_ids,
            "draft_preview_handoff",
        )
    )
    citations.extend(
        _lookup_citations(
            packets["action_journal_replay_validator_v1"].get("validator_checks", []),
            "validator_check_id",
            gap.journal_validator_ids,
            "action_journal_replay_validator",
        )
    )
    citations.extend(
        _lookup_citations(
            packets["attended_devhub_observation_dry_run_runbook_v1"].get("runbook_steps", []),
            "runbook_step_id",
            gap.devhub_runbook_step_ids,
            "attended_devhub_dry_run_runbook",
        )
    )
    expected_count = (
        len(gap.source_requirement_ids)
        + len(gap.guardrail_ids)
        + len(gap.draft_preview_ids)
        + len(gap.journal_validator_ids)
        + len(gap.devhub_runbook_step_ids)
    )
    if len(citations) != expected_count:
        raise ValueError(f"gap {gap.gap_id} references unresolved citation ids")
    return citations


def _lookup_citations(rows: Any, id_key: str, wanted_ids: Iterable[str], packet_name: str) -> list[dict[str, str]]:
    if not isinstance(rows, list):
        raise ValueError(f"{packet_name} rows must be a list")
    wanted = set(wanted_ids)
    result: list[dict[str, str]] = []
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError(f"{packet_name} row must be an object")
        row_id = row.get(id_key)
        if row_id not in wanted:
            continue
        result.append(
            {
                "packet": packet_name,
                "id": str(row_id),
                "citation": _required_string(row, "citation"),
                "evidence_summary": _required_string(row, "evidence_summary"),
            }
        )
    return result


def _validate_gap_rows_are_cited(rows: list[dict[str, Any]]) -> None:
    for row in rows:
        if not row.get("citations"):
            raise ValueError(f"gap {row.get('gap_id', '')} has no citations")


def _validate_declared_dependency_order(packets: dict[str, Any], gaps: list[GapInput]) -> None:
    ledger = packets["readiness_ledger_v1"]
    declared = ledger.get("dependency_order")
    if declared is None:
        return
    if not isinstance(declared, list) or not all(isinstance(item, str) for item in declared):
        raise ValueError("readiness_ledger_v1.dependency_order must be a list of gap ids")
    remaining_ids = {gap.gap_id for gap in gaps}
    if set(declared) != remaining_ids:
        raise ValueError("readiness_ledger_v1.dependency_order must include every remaining gap exactly once")
    positions = {gap_id: index for index, gap_id in enumerate(declared)}
    for gap in gaps:
        for dependency_id in gap.dependencies:
            if dependency_id not in positions or positions[dependency_id] > positions[gap.gap_id]:
                raise ValueError(f"declared dependency_order places {gap.gap_id} before {dependency_id}")


def _validate_commit_safe_packet_content(value: Any) -> None:
    for path, item in _walk(value):
        key = path[-1] if path else ""
        if key in MUTATION_FLAG_KEYS and item is True:
            raise ValueError(f"active mutation flag is not allowed: {'.'.join(path)}")
        if key in PRIVATE_ARTIFACT_KEYS and _has_present_value(item):
            raise ValueError(f"private or raw artifact field is not allowed: {'.'.join(path)}")
        if isinstance(item, str):
            _validate_safe_text(path, item)


def _validate_safe_text(path: tuple[str, ...], text: str) -> None:
    if not text.strip():
        return
    if RAW_OR_PRIVATE_VALUE_RE.search(text) and not _is_negated_or_refusal(text):
        raise ValueError(f"private, authenticated, raw crawl, PDF, session, or browser data is not allowed: {'.'.join(path)}")
    if LIVE_EXECUTION_RE.search(text) and not _is_negated_or_refusal(text):
        raise ValueError(f"live execution claim is not allowed: {'.'.join(path)}")
    if OUTCOME_GUARANTEE_RE.search(text) and not _is_negated_or_refusal(text):
        raise ValueError(f"legal or permitting outcome guarantee is not allowed: {'.'.join(path)}")
    if CONSEQUENTIAL_ACTION_RE.search(text) and not _is_negated_or_refusal(text):
        raise ValueError(f"consequential action language is not allowed: {'.'.join(path)}")


def _is_negated_or_refusal(text: str) -> bool:
    return bool(NEGATION_RE.search(text))


def _walk(value: Any, path: tuple[str, ...] = ()) -> Iterable[tuple[tuple[str, ...], Any]]:
    yield path, value
    if isinstance(value, dict):
        for key, child in value.items():
            yield from _walk(child, path + (str(key),))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk(child, path + (str(index),))


def _has_present_value(value: Any) -> bool:
    if value is None or value is False:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict, tuple, set)):
        return bool(value)
    return True


def _required_string(row: dict[str, Any], key: str) -> str:
    value = row.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"required non-empty string field missing: {key}")
    return value


def _string_list(value: Any, field_name: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"{field_name} must be a list of strings")
    return value


def _command_list(value: Any) -> list[list[str]]:
    if not isinstance(value, list):
        raise ValueError("offline_validation_commands must be a list")
    commands: list[list[str]] = []
    for command in value:
        if not isinstance(command, list) or not all(isinstance(part, str) for part in command):
            raise ValueError("each offline validation command must be a list of strings")
        commands.append(command)
    return commands


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a PP&D readiness gap report v1 from fixture packets.")
    parser.add_argument("packet_file", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    report = build_readiness_gap_report(load_packet_file(args.packet_file))
    serialized = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(serialized, encoding="utf-8")
    else:
        print(serialized, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
