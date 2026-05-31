"""Inactive guardrail bundle promotion candidate v2 validation.

This packet is fixture-first and review-only. It consumes approved guardrail
recompile reviewer packet v2 rows into ordered inactive bundle candidate records
without replacing active guardrails, changing prompts, opening DevHub, crawling
live sources, or activating release state.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
import json
import re
from pathlib import Path
from typing import Any

PACKET_TYPE = "ppd.inactive_guardrail_bundle_promotion_candidate.v2"
PACKET_VERSION = "v2"
INACTIVE_STATUS = "inactive_candidate_only"
VALIDATION_COMMANDS = [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]]
APPROVED_REVIEWER_DISPOSITIONS = {
    "approved_for_inactive_guardrail_bundle_candidate_v2",
    "approved_for_inactive_bundle_candidate_v2",
}
OFFLINE_VALIDATION_COMMANDS = [
    ["python3", "-m", "py_compile", "ppd/agent_readiness/inactive_guardrail_bundle_promotion_candidate_v2.py"],
    ["python3", "-m", "unittest", "ppd.tests.test_inactive_guardrail_bundle_promotion_candidate_v2"],
    ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
]

_REQUIRED_TOP_LEVEL_LISTS = (
    "approved_recompile_reviewer_rows",
    "inactive_bundle_candidate_records",
    "source_evidence_trace_placeholders",
    "predicate_snapshot_placeholders",
    "rollback_references",
    "reviewer_approval_placeholders",
    "release_gate_prerequisites",
    "offline_validation_commands",
    "validation_commands",
)

_REQUIRED_TRUE_FLAGS = (
    "fixture_first",
    "metadata_only",
    "candidate_only",
    "inactive_only",
    "reviewer_rows_consumed",
    "no_devhub_opened",
    "no_live_source_crawl",
    "no_prompt_changes",
    "no_active_guardrail_replacement",
    "no_release_activation",
)

_REQUIRED_FALSE_FLAGS = (
    "active_source_mutation",
    "active_requirement_mutation",
    "active_process_model_mutation",
    "active_process_mutation",
    "active_guardrail_replaced",
    "active_guardrail_mutation",
    "active_prompt_mutation",
    "active_contract_mutation",
    "active_devhub_surface_mutation",
    "active_surface_mutation",
    "active_release_state_mutation",
    "source_mutation",
    "requirement_mutation",
    "process_model_mutation",
    "process_mutation",
    "guardrail_mutation",
    "prompt_mutation",
    "contract_mutation",
    "devhub_surface_mutation",
    "surface_mutation",
    "devhub_opened",
    "live_source_crawl",
    "release_state_activated",
    "release_state_mutation",
    "promotion_executed",
)

_PRIVATE_OR_LIVE_KEY_RE = re.compile(
    r"(^|_)(auth|browser|cookie|credential|devhub[_-]?session|download|downloaded|har|password|payment|private|raw|screenshot|session|storage[_-]?state|token|trace[_-]?(file|artifact|archive)?|warc)(_|$)",
    re.IGNORECASE,
)
_PRIVATE_OR_LIVE_VALUE_RE = re.compile(
    r"(auth state|browser state|cookie jar|downloaded document|har file|opened devhub|devhub observed|private devhub|raw crawl|raw body|raw html|raw pdf|session state|storage state|trace.zip|warc payload|live crawl|live devhub|live source|/(tmp|private|var/folders|home)/|\\users\\|\.har$|\.warc(\.gz)?$)",
    re.IGNORECASE,
)
_OUTCOME_OR_ACTION_RE = re.compile(
    r"(approval guaranteed|guarantee approval|guaranteed approval|legal advice|legal guarantee|legally compliant|permit guaranteed|permit will be approved|permit will issue|agent will submit|automation will submit|click pay|click submit|enter payment|pay fees|schedule inspection|submit payment|submit permit|upload correction|withdraw permit|cancel permit)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class InactiveGuardrailBundlePromotionCandidateV2Result:
    valid: bool
    problems: tuple[str, ...]


class InactiveGuardrailBundlePromotionCandidateV2Error(ValueError):
    def __init__(self, problems: Iterable[str]) -> None:
        self.problems = tuple(problems)
        super().__init__("invalid inactive guardrail bundle promotion candidate v2: " + "; ".join(self.problems))


def load_inactive_guardrail_bundle_promotion_candidate_v2(path: str | Path) -> dict[str, Any]:
    loaded = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError("inactive guardrail bundle promotion candidate v2 fixture must be a JSON object")
    assert_valid_inactive_guardrail_bundle_promotion_candidate_v2(loaded)
    return loaded


def assert_valid_inactive_guardrail_bundle_promotion_candidate_v2(packet: Mapping[str, Any]) -> None:
    result = validate_inactive_guardrail_bundle_promotion_candidate_v2(packet)
    if not result.valid:
        raise InactiveGuardrailBundlePromotionCandidateV2Error(result.problems)


def validate_inactive_guardrail_bundle_promotion_candidate_v2(
    packet: Mapping[str, Any],
) -> InactiveGuardrailBundlePromotionCandidateV2Result:
    if not isinstance(packet, Mapping):
        return InactiveGuardrailBundlePromotionCandidateV2Result(False, ("packet must be an object",))

    problems: list[str] = []
    if packet.get("packet_type") != PACKET_TYPE:
        problems.append(f"packet_type must be {PACKET_TYPE}")
    if packet.get("packet_version") != PACKET_VERSION:
        problems.append("packet_version must be v2")

    for key in _REQUIRED_TRUE_FLAGS:
        if packet.get(key) is not True:
            problems.append(f"{key} must be true")
    for key in _REQUIRED_FALSE_FLAGS:
        if packet.get(key) is not False:
            problems.append(f"{key} must be false")
    for key in _REQUIRED_TOP_LEVEL_LISTS:
        if not _non_empty_sequence(packet.get(key)):
            problems.append(f"{key} must be a non-empty list")

    if packet.get("offline_validation_commands") != OFFLINE_VALIDATION_COMMANDS:
        problems.append("offline_validation_commands must exactly match the inactive candidate offline validation command bundle")
    if packet.get("validation_commands") != VALIDATION_COMMANDS:
        problems.append("validation_commands must contain the PP&D daemon self-test command")

    _validate_reviewer_rows(packet.get("approved_recompile_reviewer_rows"), problems)
    _validate_candidate_records(packet.get("inactive_bundle_candidate_records"), problems)
    _validate_source_trace_placeholders(packet.get("source_evidence_trace_placeholders"), problems)
    _validate_predicate_snapshots(packet.get("predicate_snapshot_placeholders"), problems)
    _validate_rollback_references(packet.get("rollback_references"), problems)
    _validate_reviewer_placeholders(packet.get("reviewer_approval_placeholders"), problems)
    _validate_release_gate_prerequisites(packet.get("release_gate_prerequisites"), problems)
    _validate_cross_references(packet, problems)
    _validate_forbidden_payload(packet, problems)
    return InactiveGuardrailBundlePromotionCandidateV2Result(not problems, tuple(problems))


def _validate_reviewer_rows(value: Any, problems: list[str]) -> None:
    rows = _mapping_sequence(value)
    if not rows:
        return
    seen: set[str] = set()
    for index, row in enumerate(rows):
        prefix = f"approved_recompile_reviewer_rows[{index}]"
        row_id = _text(row.get("row_id"))
        if not row_id:
            problems.append(f"{prefix}.row_id is required")
        elif row_id in seen:
            problems.append(f"{prefix}.row_id must be unique")
        seen.add(row_id)
        if _text(row.get("reviewer_disposition")) not in APPROVED_REVIEWER_DISPOSITIONS:
            problems.append(f"{prefix}.reviewer_disposition must approve inactive bundle candidacy")
        for key in (
            "requirement_delta_traces",
            "predicate_impact_review_note",
            "migration_risk_disposition",
            "stale_source_hold_carry_forward_decision",
            "blocked_action_reminder_check",
        ):
            if not _present(row.get(key)):
                problems.append(f"{prefix}.{key} is required from the recompile reviewer row")


def _validate_candidate_records(value: Any, problems: list[str]) -> None:
    rows = _mapping_sequence(value)
    if not rows:
        return
    expected_sequence = 1
    seen: set[str] = set()
    for index, row in enumerate(rows):
        prefix = f"inactive_bundle_candidate_records[{index}]"
        candidate_id = _text(row.get("candidate_id"))
        if not candidate_id:
            problems.append(f"{prefix}.candidate_id is required")
        elif candidate_id in seen:
            problems.append(f"{prefix}.candidate_id must be unique")
        seen.add(candidate_id)
        if row.get("sequence") != expected_sequence:
            problems.append(f"{prefix}.sequence must be {expected_sequence}")
        expected_sequence += 1
        if row.get("candidate_status") != INACTIVE_STATUS:
            problems.append(f"{prefix}.candidate_status must remain inactive_candidate_only")
        if row.get("activation_allowed") is not False:
            problems.append(f"{prefix}.activation_allowed must be false")
        if not _text(row.get("source_reviewer_row_ref")):
            problems.append(f"{prefix}.source_reviewer_row_ref is required")
        if not _text(row.get("inactive_guardrail_bundle_candidate_id")):
            problems.append(f"{prefix}.inactive_guardrail_bundle_candidate_id is required")
        if _text(row.get("active_guardrail_bundle_id")) and row.get("replaces_active_guardrail") is not False:
            problems.append(f"{prefix}.replaces_active_guardrail must be false when an active bundle is referenced")
        if not _string_list(row.get("source_evidence_trace_placeholder_refs")):
            problems.append(f"{prefix}.source_evidence_trace_placeholder_refs must be non-empty")
        if not _string_list(row.get("predicate_snapshot_placeholder_refs")):
            problems.append(f"{prefix}.predicate_snapshot_placeholder_refs must be non-empty")
        if not _text(row.get("rollback_ref")):
            problems.append(f"{prefix}.rollback_ref is required")
        if not _text(row.get("reviewer_approval_placeholder_ref")):
            problems.append(f"{prefix}.reviewer_approval_placeholder_ref is required")
        if not _text(row.get("release_gate_prerequisite_ref")):
            problems.append(f"{prefix}.release_gate_prerequisite_ref is required")


def _validate_source_trace_placeholders(value: Any, problems: list[str]) -> None:
    for index, row in enumerate(_mapping_sequence(value)):
        prefix = f"source_evidence_trace_placeholders[{index}]"
        if not _text(row.get("placeholder_id")):
            problems.append(f"{prefix}.placeholder_id is required")
        if not _text(row.get("candidate_id")):
            problems.append(f"{prefix}.candidate_id is required")
        if not _string_list(row.get("source_evidence_ids")):
            problems.append(f"{prefix}.source_evidence_ids must be non-empty")
        if row.get("trace_status") != "placeholder_pending_manual_evidence_review":
            problems.append(f"{prefix}.trace_status must remain placeholder_pending_manual_evidence_review")


def _validate_predicate_snapshots(value: Any, problems: list[str]) -> None:
    for index, row in enumerate(_mapping_sequence(value)):
        prefix = f"predicate_snapshot_placeholders[{index}]"
        if not _text(row.get("snapshot_id")):
            problems.append(f"{prefix}.snapshot_id is required")
        if not _text(row.get("candidate_id")):
            problems.append(f"{prefix}.candidate_id is required")
        if not _string_list(row.get("predicate_ids")):
            problems.append(f"{prefix}.predicate_ids must be non-empty")
        if row.get("snapshot_status") != "placeholder_pending_recompile_snapshot_review":
            problems.append(f"{prefix}.snapshot_status must remain placeholder_pending_recompile_snapshot_review")
        if row.get("activation_allowed") is not False:
            problems.append(f"{prefix}.activation_allowed must be false")


def _validate_rollback_references(value: Any, problems: list[str]) -> None:
    for index, row in enumerate(_mapping_sequence(value)):
        prefix = f"rollback_references[{index}]"
        if not _text(row.get("rollback_ref")):
            problems.append(f"{prefix}.rollback_ref is required")
        if not _text(row.get("candidate_id")):
            problems.append(f"{prefix}.candidate_id is required")
        if row.get("rollback_status") != "ready_no_active_changes":
            problems.append(f"{prefix}.rollback_status must be ready_no_active_changes")
        if _text(row.get("rollback_target")) != "discard_inactive_candidate_only":
            problems.append(f"{prefix}.rollback_target must be discard_inactive_candidate_only")


def _validate_reviewer_placeholders(value: Any, problems: list[str]) -> None:
    for index, row in enumerate(_mapping_sequence(value)):
        prefix = f"reviewer_approval_placeholders[{index}]"
        if not _text(row.get("placeholder_id")):
            problems.append(f"{prefix}.placeholder_id is required")
        if not _text(row.get("candidate_id")):
            problems.append(f"{prefix}.candidate_id is required")
        if row.get("approval_status") != "pending_manual_review":
            problems.append(f"{prefix}.approval_status must be pending_manual_review")
        if row.get("reviewer") not in {"", None}:
            problems.append(f"{prefix}.reviewer must be blank until manual review")
        if row.get("reviewed_at") not in {"", None}:
            problems.append(f"{prefix}.reviewed_at must be blank until manual review")


def _validate_release_gate_prerequisites(value: Any, problems: list[str]) -> None:
    for index, row in enumerate(_mapping_sequence(value)):
        prefix = f"release_gate_prerequisites[{index}]"
        if not _text(row.get("gate_ref")):
            problems.append(f"{prefix}.gate_ref is required")
        if not _text(row.get("candidate_id")):
            problems.append(f"{prefix}.candidate_id is required")
        if row.get("gate_status") != "blocked_pending_manual_release_review":
            problems.append(f"{prefix}.gate_status must be blocked_pending_manual_release_review")
        if row.get("activation_allowed") is not False:
            problems.append(f"{prefix}.activation_allowed must be false")
        if row.get("requires_offline_validation") is not True:
            problems.append(f"{prefix}.requires_offline_validation must be true")
        if row.get("requires_reviewer_approval") is not True:
            problems.append(f"{prefix}.requires_reviewer_approval must be true")
        if row.get("requires_rollback_review") is not True:
            problems.append(f"{prefix}.requires_rollback_review must be true")
        if row.get("requires_no_active_guardrail_replacement") is not True:
            problems.append(f"{prefix}.requires_no_active_guardrail_replacement must be true")


def _validate_cross_references(packet: Mapping[str, Any], problems: list[str]) -> None:
    candidate_ids = {_text(row.get("candidate_id")) for row in _mapping_sequence(packet.get("inactive_bundle_candidate_records"))}
    reviewer_rows = {_text(row.get("row_id")) for row in _mapping_sequence(packet.get("approved_recompile_reviewer_rows"))}
    traces = {_text(row.get("placeholder_id")) for row in _mapping_sequence(packet.get("source_evidence_trace_placeholders"))}
    snapshots = {_text(row.get("snapshot_id")) for row in _mapping_sequence(packet.get("predicate_snapshot_placeholders"))}
    rollbacks = {_text(row.get("rollback_ref")) for row in _mapping_sequence(packet.get("rollback_references"))}
    approvals = {_text(row.get("placeholder_id")) for row in _mapping_sequence(packet.get("reviewer_approval_placeholders"))}
    gates = {_text(row.get("gate_ref")) for row in _mapping_sequence(packet.get("release_gate_prerequisites"))}

    for index, row in enumerate(_mapping_sequence(packet.get("inactive_bundle_candidate_records"))):
        prefix = f"inactive_bundle_candidate_records[{index}]"
        if _text(row.get("source_reviewer_row_ref")) not in reviewer_rows:
            problems.append(f"{prefix}.source_reviewer_row_ref must reference approved_recompile_reviewer_rows")
        for trace_ref in _string_list(row.get("source_evidence_trace_placeholder_refs")):
            if trace_ref not in traces:
                problems.append(f"{prefix}.source_evidence_trace_placeholder_refs must reference source_evidence_trace_placeholders")
        for snapshot_ref in _string_list(row.get("predicate_snapshot_placeholder_refs")):
            if snapshot_ref not in snapshots:
                problems.append(f"{prefix}.predicate_snapshot_placeholder_refs must reference predicate_snapshot_placeholders")
        if _text(row.get("rollback_ref")) not in rollbacks:
            problems.append(f"{prefix}.rollback_ref must reference rollback_references")
        if _text(row.get("reviewer_approval_placeholder_ref")) not in approvals:
            problems.append(f"{prefix}.reviewer_approval_placeholder_ref must reference reviewer_approval_placeholders")
        if _text(row.get("release_gate_prerequisite_ref")) not in gates:
            problems.append(f"{prefix}.release_gate_prerequisite_ref must reference release_gate_prerequisites")

    _require_candidate_refs("source_evidence_trace_placeholders", "candidate_id", packet, candidate_ids, problems)
    _require_candidate_refs("predicate_snapshot_placeholders", "candidate_id", packet, candidate_ids, problems)
    _require_candidate_refs("rollback_references", "candidate_id", packet, candidate_ids, problems)
    _require_candidate_refs("reviewer_approval_placeholders", "candidate_id", packet, candidate_ids, problems)
    _require_candidate_refs("release_gate_prerequisites", "candidate_id", packet, candidate_ids, problems)


def _require_candidate_refs(section: str, field: str, packet: Mapping[str, Any], candidate_ids: set[str], problems: list[str]) -> None:
    for index, row in enumerate(_mapping_sequence(packet.get(section))):
        candidate_id = _text(row.get(field))
        if candidate_id and candidate_id not in candidate_ids:
            problems.append(f"{section}[{index}].{field} must reference inactive_bundle_candidate_records")


def _validate_forbidden_payload(packet: Mapping[str, Any], problems: list[str]) -> None:
    allowed_placeholder_keys = {
        "source_evidence_trace_placeholders",
        "source_evidence_trace_placeholder_refs",
        "trace_status",
    }
    for path, key, value in _walk(packet):
        normalized_key = key.lower().replace("-", "_")
        if normalized_key not in allowed_placeholder_keys and _PRIVATE_OR_LIVE_KEY_RE.search(normalized_key) and _truthy(value):
            problems.append(f"{path} must not include private, live, raw, session, browser, or downloaded artifacts")
        if isinstance(value, str):
            if _PRIVATE_OR_LIVE_VALUE_RE.search(value):
                problems.append(f"{path} must not reference private, live, raw, session, browser, or downloaded artifacts")
            if _OUTCOME_OR_ACTION_RE.search(value):
                problems.append(f"{path} must not guarantee outcomes or authorize consequential actions")


def _walk(value: Any, prefix: str = "packet", key: str = "packet") -> Iterable[tuple[str, str, Any]]:
    if isinstance(value, Mapping):
        for child_key, child_value in value.items():
            child_key_text = str(child_key)
            child_path = f"{prefix}.{child_key_text}"
            yield child_path, child_key_text, child_value
            yield from _walk(child_value, child_path, child_key_text)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child_value in enumerate(value):
            child_path = f"{prefix}[{index}]"
            yield child_path, key, child_value
            yield from _walk(child_value, child_path, key)


def _mapping_sequence(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


def _non_empty_sequence(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes)) and bool(value)


def _present(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return bool(value)
    return value is not None


def _truthy(value: Any) -> bool:
    if value is None or value is False or value == "":
        return False
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)) and not value:
        return False
    if isinstance(value, Mapping) and not value:
        return False
    return True


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""
