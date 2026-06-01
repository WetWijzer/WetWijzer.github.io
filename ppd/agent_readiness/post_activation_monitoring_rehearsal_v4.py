"""Validation for fixture-first post-activation monitoring rehearsal v4.

The v4 rehearsal is a committed, offline validation artifact. It must prove that
post-activation monitoring would be ready without claiming live monitoring,
activating schedules, mutating guardrails, opening DevHub, storing private
artifacts, completing official actions, or guaranteeing legal/permitting
outcomes.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PACKET_TYPE = "ppd.post_activation_monitoring_rehearsal.v4"
PACKET_VERSION = "v4"
EXACT_VALIDATION_COMMANDS = [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]]

REQUIRED_BOUNDARIES = {
    "fixture_first": True,
    "offline_rehearsal_only": True,
    "synthetic_inputs_only": True,
    "live_monitoring_enabled": False,
    "active_mutation_enabled": False,
    "active_guardrail_mutation_enabled": False,
    "devhub_opened": False,
    "private_artifact_storage_enabled": False,
    "official_action_enabled": False,
    "legal_or_permitting_guarantee_enabled": False,
}

REQUIRED_REFERENCED_SECTIONS = {
    "guardrail_lookup_health_rows": "guardrail lookup health rows",
    "stale_source_stop_gate_checks": "stale-source stop-gate checks",
    "exact_confirmation_gate_checks": "exact-confirmation gate checks",
    "refused_consequential_or_financial_action_checks": "refused consequential or financial action checks",
    "rollback_trigger_thresholds": "rollback trigger thresholds",
    "reviewer_escalation_routing": "reviewer escalation routing",
}

REQUIRED_ROW_TEXT_FIELDS = {
    "activation_checklist_references": ("activation_checklist_reference_id", "checklist_item", "source_packet_id"),
    "guardrail_lookup_health_rows": ("health_row_id", "source_activation_checklist_reference", "lookup_name", "expected_status"),
    "stale_source_stop_gate_checks": ("stop_gate_check_id", "source_activation_checklist_reference", "stale_condition", "expected_result"),
    "exact_confirmation_gate_checks": ("gate_check_id", "source_activation_checklist_reference", "action_class", "expected_result"),
    "refused_consequential_or_financial_action_checks": ("refusal_check_id", "source_activation_checklist_reference", "action_class", "expected_result"),
    "rollback_trigger_thresholds": ("threshold_id", "source_activation_checklist_reference", "threshold", "expected_result"),
    "reviewer_escalation_routing": ("route_id", "source_activation_checklist_reference", "reviewer_role", "expected_route"),
}

EXPECTED_SECTION_VALUES = {
    "guardrail_lookup_health_rows": {"expected_status": "offline_lookup_present"},
    "stale_source_stop_gate_checks": {"expected_result": "agent_blocks_until_source_refresh_or_reviewer_disposition"},
    "exact_confirmation_gate_checks": {"expected_result": "exact_confirmation_required_before_consequential_step"},
    "refused_consequential_or_financial_action_checks": {"expected_result": "refused_without_user_attendance_and_exact_confirmation"},
    "rollback_trigger_thresholds": {"expected_result": "rollback_reviewer_hold"},
    "reviewer_escalation_routing": {"expected_route": "human_reviewer_queue"},
}

FORBIDDEN_TRUE_FLAG_KEYS = {
    "active_guardrail_mutation",
    "active_guardrail_mutation_enabled",
    "active_mutation",
    "active_mutation_enabled",
    "active_prompt_mutation",
    "approval_guaranteed",
    "automated_submission_enabled",
    "browser_automation_enabled",
    "devhub_opened",
    "final_action_completed",
    "guardrail_activation_enabled",
    "legal_advice_provided",
    "legal_or_permitting_guarantee_enabled",
    "live_monitoring_enabled",
    "mutation_enabled",
    "official_action_completed",
    "official_action_enabled",
    "permit_guaranteed",
    "private_artifact_storage_enabled",
    "release_state_update_enabled",
    "schedule_active",
    "schedule_enabled",
}

FORBIDDEN_KEY_MARKERS = (
    "auth_state",
    "browser_state",
    "cookie",
    "credential",
    "downloaded_artifact",
    "downloaded_document",
    "downloaded_file",
    "har",
    "private_artifact",
    "raw_artifact",
    "raw_body",
    "raw_crawl",
    "raw_download",
    "raw_html",
    "raw_pdf",
    "screenshot",
    "session_state",
    "storage_state",
    "trace",
)

FORBIDDEN_TEXT_RE = re.compile(
    r"\b("
    r"active mutation|approval is guaranteed|certification completed|devhub opened|downloaded document|"
    r"downloaded file|final payment executed|guardrails activated|legal advice|live monitoring|"
    r"live monitor ran|monitoring is live|official action completed|payment completed|"
    r"permit approval guaranteed|permit is guaranteed|private artifact|raw crawl|raw download|"
    r"release activated|schedule inspection completed|session state|storage state|submitted permit|"
    r"trace file|uploaded plans"
    r")\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class PostActivationMonitoringRehearsalV4ValidationResult:
    """Machine-readable v4 rehearsal validation result."""

    ready: bool
    problems: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {"ready": self.ready, "problems": list(self.problems)}


class PostActivationMonitoringRehearsalV4Error(ValueError):
    """Raised when a v4 rehearsal packet is incomplete or unsafe."""

    def __init__(self, problems: Sequence[str]) -> None:
        self.problems = tuple(problems)
        super().__init__("invalid post-activation monitoring rehearsal v4: " + "; ".join(self.problems))


def load_post_activation_monitoring_rehearsal_v4(path: str | Path) -> dict[str, Any]:
    packet = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(packet, dict):
        raise PostActivationMonitoringRehearsalV4Error(["packet must be an object"])
    require_post_activation_monitoring_rehearsal_v4(packet)
    return packet


def validate_post_activation_monitoring_rehearsal_v4(
    packet: Mapping[str, Any],
) -> PostActivationMonitoringRehearsalV4ValidationResult:
    """Return fail-closed validation for a fixture-only v4 rehearsal packet."""

    problems: list[str] = []
    if packet.get("packet_type") != PACKET_TYPE:
        problems.append(f"packet_type must be {PACKET_TYPE}")
    if packet.get("packet_version") != PACKET_VERSION:
        problems.append("packet_version must be v4")
    if packet.get("boundaries") != REQUIRED_BOUNDARIES:
        problems.append("boundaries must exactly declare fixture-only offline rehearsal with no live monitoring, mutation, private artifact storage, official action, or guarantees")
    if packet.get("validation_commands") != EXACT_VALIDATION_COMMANDS:
        problems.append("validation_commands must contain only the daemon self-test command")

    checklist_refs = _activation_checklist_reference_ids(packet.get("activation_checklist_references"), problems)
    if not checklist_refs:
        problems.append("activation_checklist_references must be a non-empty list")

    for section, label in REQUIRED_REFERENCED_SECTIONS.items():
        _validate_referenced_section(section, label, packet.get(section), checklist_refs, problems)

    _scan_for_forbidden_payload(packet, "$", problems)
    return PostActivationMonitoringRehearsalV4ValidationResult(ready=not problems, problems=tuple(sorted(set(problems))))


def require_post_activation_monitoring_rehearsal_v4(packet: Mapping[str, Any]) -> None:
    """Raise when the v4 rehearsal packet is incomplete or unsafe."""

    result = validate_post_activation_monitoring_rehearsal_v4(packet)
    if not result.ready:
        raise PostActivationMonitoringRehearsalV4Error(result.problems)


def _activation_checklist_reference_ids(value: Any, problems: list[str]) -> set[str]:
    rows = _required_mapping_rows("activation_checklist_references", value, problems)
    refs: set[str] = set()
    for index, row in enumerate(rows):
        prefix = f"activation_checklist_references[{index}]"
        _require_text_fields(row, prefix, REQUIRED_ROW_TEXT_FIELDS["activation_checklist_references"], problems)
        ref_id = row.get("activation_checklist_reference_id")
        if isinstance(ref_id, str) and ref_id.strip():
            refs.add(ref_id)
    if len(refs) != len(rows):
        problems.append("activation_checklist_references must have unique non-empty activation_checklist_reference_id values")
    return refs


def _validate_referenced_section(
    section: str,
    label: str,
    value: Any,
    checklist_refs: set[str],
    problems: list[str],
) -> None:
    rows = _required_mapping_rows(section, value, problems)
    observed_refs: set[str] = set()
    for index, row in enumerate(rows):
        prefix = f"{section}[{index}]"
        _require_text_fields(row, prefix, REQUIRED_ROW_TEXT_FIELDS[section], problems)
        source_ref = row.get("source_activation_checklist_reference")
        if isinstance(source_ref, str) and source_ref.strip():
            observed_refs.add(source_ref)
            if checklist_refs and source_ref not in checklist_refs:
                problems.append(f"{prefix}.source_activation_checklist_reference references unknown activation checklist reference {source_ref}")
        for field, expected in EXPECTED_SECTION_VALUES.get(section, {}).items():
            if row.get(field) != expected:
                problems.append(f"{prefix}.{field} must be {expected}")
    for missing_ref in sorted(checklist_refs - observed_refs):
        problems.append(f"{label} missing activation checklist reference {missing_ref}")


def _required_mapping_rows(section: str, value: Any, problems: list[str]) -> list[Mapping[str, Any]]:
    if not isinstance(value, list) or not value:
        problems.append(f"{section} must be a non-empty list")
        return []
    rows: list[Mapping[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            problems.append(f"{section}[{index}] must be an object")
            continue
        rows.append(item)
    return rows


def _require_text_fields(row: Mapping[str, Any], prefix: str, fields: Sequence[str], problems: list[str]) -> None:
    for field in fields:
        value = row.get(field)
        if not isinstance(value, str) or not value.strip():
            problems.append(f"{prefix}.{field} must be non-empty")


def _scan_for_forbidden_payload(value: Any, path: str, problems: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            normalized_key = key_text.lower().replace("-", "_")
            child_path = f"{path}.{key_text}"
            if normalized_key in FORBIDDEN_TRUE_FLAG_KEYS and child is True:
                problems.append(f"forbidden live/mutation/official/guarantee true flag at {child_path}")
            if "mutation" in normalized_key and child is True:
                problems.append(f"active mutation flag is not allowed at {child_path}")
            if any(marker in normalized_key for marker in FORBIDDEN_KEY_MARKERS) and child not in (None, False, "", [], {}):
                problems.append(f"forbidden private/session/auth/raw artifact field at {child_path}")
            _scan_for_forbidden_payload(child, child_path, problems)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            _scan_for_forbidden_payload(child, f"{path}[{index}]", problems)
    elif isinstance(value, str) and FORBIDDEN_TEXT_RE.search(value):
        problems.append(f"forbidden live/mutation/official/guarantee/private claim at {path}")
