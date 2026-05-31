"""Validation for inactive guardrail migration preview packet v2.

The packet is preview-only. Validation is intentionally structural and fail-closed so a
candidate cannot imply live crawl, DevHub access, official action completion, legal
certainty, private artifact capture, or active PP&D state mutation.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

PACKET_TYPE = "ppd.inactive_guardrail_migration_preview_packet.v2"
PREVIEW_MODE = "inactive_guardrail_migration_preview_validation_only"

REQUIRED_ROW_SECTIONS = (
    "predicate_rows",
    "deontic_rule_rows",
    "temporal_rule_rows",
    "reversible_action_predicates",
    "exact_confirmation_predicates",
    "refused_action_predicates",
    "stale_source_holds",
)

REQUIRED_TOP_LEVEL_SECTIONS = REQUIRED_ROW_SECTIONS + (
    "source_evidence_traces",
    "reviewer_dispositions",
    "validation_commands",
)

MUTATION_FLAG_KEYS = {
    "active_guardrail_mutation_allowed",
    "active_prompt_mutation_allowed",
    "active_requirement_mutation_allowed",
    "active_process_model_mutation_allowed",
    "active_contract_mutation_allowed",
    "active_source_mutation_allowed",
    "active_devhub_surface_mutation_allowed",
    "active_release_state_mutation_allowed",
    "guardrail_promotion_allowed",
    "prompt_update_allowed",
    "requirement_update_allowed",
    "process_model_update_allowed",
    "contract_update_allowed",
    "source_registry_update_allowed",
    "devhub_surface_update_allowed",
    "release_state_update_allowed",
    "live_crawl_allowed",
    "devhub_access_allowed",
    "official_action_allowed",
}

FORBIDDEN_KEY_FRAGMENTS = (
    "private",
    "session",
    "browser",
    "raw_crawl",
    "raw_download",
    "downloaded",
    "screenshot",
    "credential",
    "cookie",
    "access_token",
    "api_token",
    "payment_method",
)

FORBIDDEN_VALUE_PHRASES = (
    "official action completed",
    "official-action completion",
    "submitted application",
    "application submitted",
    "uploaded document",
    "document uploaded",
    "certification completed",
    "certified filing",
    "payment completed",
    "paid fee",
    "inspection scheduled",
    "live crawl completed",
    "live crawler executed",
    "opened devhub",
    "devhub session",
    "devhub claim",
    "legal guarantee",
    "permitting guarantee",
    "permit guaranteed",
    "approval guaranteed",
    "will be approved",
)


def load_inactive_guardrail_migration_preview_packet_v2(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as packet_file:
        packet = json.load(packet_file)
    if not isinstance(packet, dict):
        raise ValueError("inactive guardrail migration preview packet v2 must be a JSON object")
    assert_valid_inactive_guardrail_migration_preview_packet_v2(packet)
    return packet


def assert_valid_inactive_guardrail_migration_preview_packet_v2(packet: Mapping[str, Any]) -> None:
    problems = validate_inactive_guardrail_migration_preview_packet_v2(packet)
    if problems:
        raise ValueError("invalid inactive guardrail migration preview packet v2: " + "; ".join(problems))


def validate_inactive_guardrail_migration_preview_packet_v2(packet: Mapping[str, Any]) -> list[str]:
    problems: list[str] = []
    if not isinstance(packet, Mapping):
        return ["packet must be an object"]

    if packet.get("packet_type") != PACKET_TYPE:
        problems.append(f"packet_type must be {PACKET_TYPE}")
    if packet.get("mode") != PREVIEW_MODE:
        problems.append(f"mode must be {PREVIEW_MODE}")
    if packet.get("inactive_preview_only") is not True:
        problems.append("inactive_preview_only must be true")

    for section in REQUIRED_TOP_LEVEL_SECTIONS:
        rows = packet.get(section)
        if not isinstance(rows, list) or not rows:
            problems.append(f"{section} must be a non-empty list")

    trace_ids = _trace_ids(packet.get("source_evidence_traces"))
    if isinstance(packet.get("source_evidence_traces"), list):
        for index, trace in enumerate(packet["source_evidence_traces"]):
            if not isinstance(trace, Mapping):
                problems.append(f"source_evidence_traces[{index}] must be an object")
                continue
            if not _text(trace.get("trace_id")):
                problems.append(f"source_evidence_traces[{index}].trace_id is required")
            if trace.get("source_mode") != "synthetic_committed_fixture_only":
                problems.append(f"source_evidence_traces[{index}].source_mode must be synthetic_committed_fixture_only")
            if trace.get("live_crawl") is not False:
                problems.append(f"source_evidence_traces[{index}].live_crawl must be false")

    for section in REQUIRED_ROW_SECTIONS:
        rows = packet.get(section)
        if isinstance(rows, list):
            for index, row in enumerate(rows):
                _validate_row(section, index, row, trace_ids, problems)

    dispositions = packet.get("reviewer_dispositions")
    if isinstance(dispositions, list):
        for index, row in enumerate(dispositions):
            if not isinstance(row, Mapping):
                problems.append(f"reviewer_dispositions[{index}] must be an object")
                continue
            if not _text(row.get("disposition_id")):
                problems.append(f"reviewer_dispositions[{index}].disposition_id is required")
            if row.get("status") != "pending_reviewer_disposition":
                problems.append(f"reviewer_dispositions[{index}].status must be pending_reviewer_disposition")
            allowed = row.get("allowed_dispositions")
            if not isinstance(allowed, list) or not allowed:
                problems.append(f"reviewer_dispositions[{index}].allowed_dispositions must be a non-empty list")

    commands = packet.get("validation_commands")
    if isinstance(commands, list):
        for index, command in enumerate(commands):
            if not isinstance(command, list) or not command or not all(_text(part) for part in command):
                problems.append(f"validation_commands[{index}] must be a non-empty argv string list")
        command_text = " ".join(" ".join(command) for command in commands if isinstance(command, list))
        if "unittest" not in command_text or "ppd/tests" not in command_text:
            problems.append("validation_commands must include exact offline unittest coverage")

    problems.extend(_find_forbidden_content(packet))
    return problems


def _validate_row(section: str, index: int, row: Any, trace_ids: set[str], problems: list[str]) -> None:
    prefix = f"{section}[{index}]"
    if not isinstance(row, Mapping):
        problems.append(f"{prefix} must be an object")
        return
    if not _text(row.get("id")):
        problems.append(f"{prefix}.id is required")
    if row.get("status") != "proposed_inactive":
        problems.append(f"{prefix}.status must be proposed_inactive")
    cited = row.get("source_evidence_trace_ids")
    if not isinstance(cited, list) or not cited or not all(_text(item) for item in cited):
        problems.append(f"{prefix}.source_evidence_trace_ids must be a non-empty string list")
        return
    missing = sorted(set(cited).difference(trace_ids))
    if missing:
        problems.append(f"{prefix}.source_evidence_trace_ids references missing traces: {missing}")


def _trace_ids(traces: Any) -> set[str]:
    if not isinstance(traces, list):
        return set()
    return {trace["trace_id"] for trace in traces if isinstance(trace, Mapping) and _text(trace.get("trace_id"))}


def _find_forbidden_content(value: Any, path: str = "packet") -> list[str]:
    problems: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            lowered_key = key_text.lower()
            child_path = f"{path}.{key_text}"
            if lowered_key in MUTATION_FLAG_KEYS and child is not False:
                problems.append(f"{child_path} must be false")
            if "active_" in lowered_key and ("mutation" in lowered_key or "update" in lowered_key) and child is not False:
                problems.append(f"{child_path} is an active mutation flag and must be false")
            if any(fragment in lowered_key for fragment in FORBIDDEN_KEY_FRAGMENTS):
                problems.append(f"{child_path} must not contain private/session/browser/raw/downloaded artifacts")
            problems.extend(_find_forbidden_content(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            problems.extend(_find_forbidden_content(child, f"{path}[{index}]"))
    elif isinstance(value, str):
        lowered_value = value.lower()
        if any(phrase in lowered_value for phrase in FORBIDDEN_VALUE_PHRASES):
            problems.append(f"{path} contains forbidden official/live/legal claim")
        if "/downloads/" in lowered_value or lowered_value.endswith(".har") or "browser-trace" in lowered_value:
            problems.append(f"{path} must not reference downloaded or browser artifacts")
    return problems


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())
