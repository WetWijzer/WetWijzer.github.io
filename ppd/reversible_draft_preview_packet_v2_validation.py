"""Validation for reversible draft preview packet v2 fixtures.

The validator is intentionally fixture-first and side-effect free. It accepts an
already-loaded packet object and reports deterministic issues for missing review
rows, missing placeholder traces, unsafe claims, private artifact references,
and active mutation flags.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


REQUIRED_NONEMPTY_SECTIONS = (
    "source_matrix_consumption",
    "synthetic_preview_rows",
    "draft_only_field_value_placeholders",
    "user_fact_trace_placeholders",
    "source_evidence_trace_placeholders",
    "redaction_notes",
    "not_ready_reasons",
    "exact_confirmation_stop_gate_summaries",
    "offline_validation_commands",
)

REQUIRED_OFFLINE_VALIDATION_COMMANDS = (
    ("python3", "-m", "unittest", "ppd.tests.test_reversible_draft_preview_packet_v2"),
    ("python3", "-m", "unittest", "discover", "-s", "ppd/tests", "-p", "test_*.py"),
    ("python3", "ppd/daemon/ppd_daemon.py", "--self-test"),
)

FORBIDDEN_ARTIFACT_TERMS = (
    "private session",
    "session artifact",
    "session state artifact",
    "browser artifact",
    "browser trace",
    "har file",
    "storage-state",
    "auth state",
    "raw crawl",
    "raw devhub output",
    "downloaded artifact",
    "downloaded document",
    "private artifact",
    "local private path",
    "file://",
)

FORBIDDEN_CLAIM_TERMS = (
    "live devhub execution completed",
    "live devhub execution ran",
    "live devhub run completed",
    "ran live devhub",
    "opened live devhub",
    "clicked live devhub",
    "filled live devhub",
    "official draft saved",
    "saved official draft",
    "official submission completed",
    "submitted official application",
    "payment submitted",
    "permit will issue",
    "permit will be issued",
    "will be approved",
    "approval is guaranteed",
    "guaranteed approval",
    "guarantee issuance",
    "legally sufficient",
    "complies with all code",
    "meets all legal requirements",
)

ACTIVE_MUTATION_FLAG_NAMES = {
    "active_prompt_mutation",
    "active_guardrail_mutation",
    "active_devhub_surface_mutation",
    "active_surface_map_mutation",
    "active_source_mutation",
    "active_contract_mutation",
    "active_release_state_mutation",
}

POLICY_SECTIONS_THAT_MUST_BE_FALSE = (
    "artifact_policy",
    "claim_policy",
    "mutation_flags",
    "prohibition_attestations",
)


class ReversibleDraftPreviewPacketV2ValidationError(ValueError):
    """Raised when a reversible draft preview packet v2 is unsafe."""

    def __init__(self, issues: Sequence[str]) -> None:
        self.issues = tuple(issues)
        super().__init__("; ".join(self.issues))


def validate_reversible_draft_preview_packet_v2(packet: Mapping[str, Any]) -> list[str]:
    """Return deterministic validation issues for a preview packet v2."""

    issues: list[str] = []

    for section in REQUIRED_NONEMPTY_SECTIONS:
        if not packet.get(section):
            issues.append(f"missing or empty {section}")

    if packet.get("fixture_first") is not True:
        issues.append("packet must be fixture-first")
    if packet.get("live_devhub_access_allowed") is not False:
        issues.append("live DevHub access must be disabled")

    preview_rows = _mapping_list(packet.get("synthetic_preview_rows"))
    if not preview_rows:
        issues.append("missing preview rows")
    expected_order = list(range(1, len(preview_rows) + 1))
    if [row.get("order") for row in preview_rows] != expected_order:
        issues.append("preview rows must be ordered without gaps")

    draft_placeholders = _items_by_id(packet.get("draft_only_field_value_placeholders"), "placeholder_id")
    user_traces = _items_by_id(packet.get("user_fact_trace_placeholders"), "trace_id")
    evidence_traces = _items_by_id(packet.get("source_evidence_trace_placeholders"), "trace_id")
    redaction_notes = _items_by_id(packet.get("redaction_notes"), "redaction_note_id")
    not_ready_reasons = _items_by_id(packet.get("not_ready_reasons"), "reason_id")
    stop_gates = _items_by_id(packet.get("exact_confirmation_stop_gate_summaries"), "summary_id")

    _validate_preview_rows(issues, preview_rows, draft_placeholders, user_traces, evidence_traces, redaction_notes, not_ready_reasons, stop_gates)
    _validate_draft_placeholders(issues, draft_placeholders.values())
    _validate_user_fact_traces(issues, user_traces.values())
    _validate_source_evidence_traces(issues, evidence_traces.values())
    _validate_redaction_notes(issues, redaction_notes.values())
    _validate_not_ready_reasons(issues, not_ready_reasons.values())
    _validate_stop_gates(issues, stop_gates.values())
    _validate_offline_commands(issues, packet.get("offline_validation_commands"))
    _validate_false_policy_sections(issues, packet)
    _validate_active_mutation_flags(issues, packet)
    _validate_forbidden_text(issues, packet)

    return sorted(set(issues))


def assert_valid_reversible_draft_preview_packet_v2(packet: Mapping[str, Any]) -> None:
    """Raise when a preview packet v2 is not valid."""

    issues = validate_reversible_draft_preview_packet_v2(packet)
    if issues:
        raise ReversibleDraftPreviewPacketV2ValidationError(issues)


def _validate_preview_rows(
    issues: list[str],
    rows: Sequence[Mapping[str, Any]],
    draft_placeholders: Mapping[str, Mapping[str, Any]],
    user_traces: Mapping[str, Mapping[str, Any]],
    evidence_traces: Mapping[str, Mapping[str, Any]],
    redaction_notes: Mapping[str, Mapping[str, Any]],
    not_ready_reasons: Mapping[str, Mapping[str, Any]],
    stop_gates: Mapping[str, Mapping[str, Any]],
) -> None:
    for row in rows:
        row_id = str(row.get("preview_row_id") or "")
        draft_ids = _string_list(row.get("draft_only_field_value_placeholder_ids"))
        user_trace_ids = _string_list(row.get("user_fact_trace_placeholder_ids"))
        evidence_trace_ids = _string_list(row.get("source_evidence_trace_placeholder_ids"))
        reason_ids = _string_list(row.get("not_ready_reason_ids"))
        stop_gate_ids = _string_list(row.get("stop_gate_summary_ids"))

        if not draft_ids:
            issues.append(f"missing draft-only field/value placeholders for {row_id}")
        if not user_trace_ids:
            issues.append(f"missing user-fact traces for {row_id}")
        if not evidence_trace_ids:
            issues.append(f"missing source-evidence traces for {row_id}")
        if row.get("redaction_note_id") not in redaction_notes:
            issues.append(f"missing redaction note for {row_id}")
        if row.get("readiness_status") != "ready_for_local_preview_only" and not reason_ids:
            issues.append(f"missing not-ready reasons for {row_id}")
        if row.get("classification") in {"consequential", "financial"} and not stop_gate_ids:
            issues.append(f"missing exact-confirmation stop gate summary for {row_id}")

        for placeholder_id in draft_ids:
            if placeholder_id not in draft_placeholders:
                issues.append(f"unknown draft placeholder {placeholder_id}")
        for trace_id in user_trace_ids:
            if trace_id not in user_traces:
                issues.append(f"unknown user-fact trace {trace_id}")
        for trace_id in evidence_trace_ids:
            if trace_id not in evidence_traces:
                issues.append(f"unknown source-evidence trace {trace_id}")
        for reason_id in reason_ids:
            if reason_id not in not_ready_reasons:
                issues.append(f"unknown not-ready reason {reason_id}")
        for summary_id in stop_gate_ids:
            if summary_id not in stop_gates:
                issues.append(f"unknown stop gate summary {summary_id}")


def _validate_draft_placeholders(issues: list[str], placeholders: Sequence[Mapping[str, Any]]) -> None:
    for placeholder in placeholders:
        placeholder_id = str(placeholder.get("placeholder_id") or "")
        if not str(placeholder.get("field_placeholder", "")).startswith("placeholder:"):
            issues.append(f"draft field label must stay placeholder-only for {placeholder_id}")
        if not str(placeholder.get("value_placeholder", "")).startswith("placeholder:"):
            issues.append(f"draft field value must stay placeholder-only for {placeholder_id}")
        if placeholder.get("draft_only") is not True or placeholder.get("preview_only") is not True:
            issues.append(f"draft field/value placeholder must be draft-only and preview-only for {placeholder_id}")
        if placeholder.get("writes_devhub_state") is not False or placeholder.get("saves_official_draft") is not False:
            issues.append(f"draft field/value placeholder must not write DevHub state or save official drafts for {placeholder_id}")


def _validate_user_fact_traces(issues: list[str], traces: Sequence[Mapping[str, Any]]) -> None:
    for trace in traces:
        trace_id = str(trace.get("trace_id") or "")
        if not str(trace.get("placeholder", "")).startswith("placeholder:"):
            issues.append(f"user-fact trace must stay placeholder-only for {trace_id}")
        if trace.get("actual_user_value") is not None:
            issues.append(f"user-fact trace must not contain actual user value for {trace_id}")


def _validate_source_evidence_traces(issues: list[str], traces: Sequence[Mapping[str, Any]]) -> None:
    for trace in traces:
        trace_id = str(trace.get("trace_id") or "")
        if not str(trace.get("placeholder", "")).startswith("placeholder:"):
            issues.append(f"source-evidence trace must stay placeholder-only for {trace_id}")
        if trace.get("live_url_fetched") is not False:
            issues.append(f"source-evidence trace must not claim a live fetch for {trace_id}")


def _validate_redaction_notes(issues: list[str], notes: Sequence[Mapping[str, Any]]) -> None:
    for note in notes:
        note_id = str(note.get("redaction_note_id") or "")
        if note.get("redacted_private_values") is not True or note.get("contains_private_values") is not False:
            issues.append(f"redaction note must confirm private values are absent for {note_id}")


def _validate_not_ready_reasons(issues: list[str], reasons: Sequence[Mapping[str, Any]]) -> None:
    for reason in reasons:
        reason_id = str(reason.get("reason_id") or "")
        if not reason_id or not str(reason.get("reason", "")).strip():
            issues.append("not-ready reason entries must include reason_id and reason")


def _validate_stop_gates(issues: list[str], gates: Sequence[Mapping[str, Any]]) -> None:
    for gate in gates:
        gate_id = str(gate.get("summary_id") or "")
        if gate.get("exact_confirmation_required") is not True or gate.get("allowed_without_exact_confirmation") is not False:
            issues.append(f"exact-confirmation stop gate summary must fail closed for {gate_id}")
        if not str(gate.get("summary", "")).startswith("EXACT_CONFIRMATION_REQUIRED:"):
            issues.append(f"exact-confirmation stop gate summary must name the required text for {gate_id}")


def _validate_offline_commands(issues: list[str], commands_value: Any) -> None:
    commands = _command_tuples(commands_value)
    for required in REQUIRED_OFFLINE_VALIDATION_COMMANDS:
        if required not in commands:
            issues.append("missing validation command: " + " ".join(required))
    for command in commands:
        joined = " ".join(command).lower()
        joined_without_daemon = joined.replace("ppd/daemon/ppd_daemon.py", "")
        if "curl" in joined or "playwright" in joined or "devhub" in joined_without_daemon:
            issues.append("offline validation commands must not invoke live crawl, browser, or DevHub tooling")


def _validate_false_policy_sections(issues: list[str], packet: Mapping[str, Any]) -> None:
    for section in POLICY_SECTIONS_THAT_MUST_BE_FALSE:
        value = packet.get(section)
        if not isinstance(value, Mapping) or not value:
            issues.append(f"missing or empty {section}")
            continue
        for key, child in value.items():
            if child is not False:
                issues.append(f"{section}.{key} must be false")


def _validate_active_mutation_flags(issues: list[str], packet: Mapping[str, Any]) -> None:
    for path, key, value in _walk_key_values(packet):
        if key in ACTIVE_MUTATION_FLAG_NAMES and value is not False:
            issues.append(f"active mutation flag must be false at {path}")


def _validate_forbidden_text(issues: list[str], packet: Mapping[str, Any]) -> None:
    for path, text in _walk_strings(packet):
        lowered = text.lower()
        if any(term in lowered for term in FORBIDDEN_ARTIFACT_TERMS):
            issues.append(f"private/session/browser/raw/downloaded artifact reference at {path}")
        if any(term in lowered for term in FORBIDDEN_CLAIM_TERMS):
            issues.append(f"forbidden live, official completion, or guarantee claim at {path}")


def _items_by_id(value: Any, id_key: str) -> dict[str, Mapping[str, Any]]:
    items: dict[str, Mapping[str, Any]] = {}
    for item in _mapping_list(value):
        item_id = item.get(id_key)
        if isinstance(item_id, str) and item_id:
            items[item_id] = item
    return items


def _mapping_list(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str) and item]


def _command_tuples(value: Any) -> set[tuple[str, ...]]:
    commands: set[tuple[str, ...]] = set()
    if not isinstance(value, list):
        return commands
    for command in value:
        if isinstance(command, list) and command and all(isinstance(part, str) and part for part in command):
            commands.add(tuple(command))
        else:
            commands.add(("",))
    return commands


def _walk_strings(value: Any, path: str = "packet") -> list[tuple[str, str]]:
    if isinstance(value, str):
        return [(path, value)]
    if isinstance(value, Mapping):
        hits: list[tuple[str, str]] = []
        for key, child in value.items():
            hits.extend(_walk_strings(child, f"{path}.{key}"))
        return hits
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        hits = []
        for index, child in enumerate(value):
            hits.extend(_walk_strings(child, f"{path}[{index}]"))
        return hits
    return []


def _walk_key_values(value: Any, path: str = "packet") -> list[tuple[str, str, Any]]:
    if isinstance(value, Mapping):
        rows: list[tuple[str, str, Any]] = []
        for key, child in value.items():
            child_path = f"{path}.{key}"
            rows.append((child_path, str(key), child))
            rows.extend(_walk_key_values(child, child_path))
        return rows
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        rows = []
        for index, child in enumerate(value):
            rows.extend(_walk_key_values(child, f"{path}[{index}]"))
        return rows
    return []
