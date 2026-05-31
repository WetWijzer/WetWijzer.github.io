"""Fixture-first inactive release transition audit packet v1.

This module intentionally performs no artifact promotion and no release-state mutation. It
only compares synthetic decision rows against transition-readiness evidence and emits
no-op recommendations for reviewer inspection.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

PACKET_VERSION = "inactive-release-transition-audit-packet-v1"
ALLOWED_DECISIONS = {"release-ready", "release-held", "release-rejected"}
PROHIBITED_MUTATIONS = (
    "promote_artifacts",
    "change_release_state",
    "mutate_active_prompts",
    "mutate_guardrails",
    "mutate_process_models",
    "mutate_requirements",
    "mutate_contracts",
    "mutate_source_registries",
    "mutate_devhub_surfaces",
    "mutate_crawler_state",
    "mutate_daemon_state",
    "use_live_crawl",
    "use_devhub",
    "use_private_files",
    "create_uploads",
    "create_submissions",
    "create_certifications",
    "create_payments",
    "create_scheduling",
)

_PRIVATE_ARTIFACT_KEYS = {
    "auth_state",
    "browser_artifacts",
    "browser_state",
    "cookies",
    "credentials",
    "download_path",
    "downloaded_artifact",
    "downloaded_artifacts",
    "downloaded_file",
    "har_path",
    "local_private_path",
    "private_artifact",
    "private_artifacts",
    "private_file_path",
    "raw_artifact",
    "raw_artifacts",
    "raw_body",
    "raw_download",
    "raw_html",
    "screenshot_path",
    "session_artifact",
    "session_artifacts",
    "session_state",
    "trace_path",
}
_PRIVATE_ARTIFACT_CLASSES = {"private", "session", "browser", "raw", "downloaded", "download"}
_RELEASE_PROMOTION_CLAIM_KEYS = {
    "artifact_promotion_performed",
    "artifacts_promoted",
    "change_release_state",
    "promote_artifacts",
    "promoted",
    "promotion_completed",
    "promotion_performed",
    "release_promoted",
    "release_promotion_claim",
    "release_state_changed",
    "transition_executed",
}
_OFFICIAL_ACTION_CLAIM_KEYS = {
    "certification_completed",
    "completion_claims",
    "fee_payment_completed",
    "inspection_scheduled",
    "official_action_completed",
    "official_action_performed",
    "official_record_upload_completed",
    "permit_submitted",
    "payment_completed",
    "scheduled_inspection",
    "submission_completed",
    "uploaded_to_official_record",
}
_LIVE_OR_DEVHUB_CLAIM_KEYS = {
    "crawled_live",
    "devhub_claim",
    "devhub_claims",
    "devhub_session",
    "devhub_used",
    "live_crawl_claim",
    "live_crawl_claims",
    "live_crawl_used",
    "used_devhub",
    "used_live_crawl",
}
_GUARANTEE_CLAIM_KEYS = {
    "approval_guarantee",
    "guarantee",
    "guarantees",
    "legal_advice",
    "legal_guarantee",
    "permit_guarantee",
    "permitting_guarantee",
}
_ACTIVE_MUTATION_FLAG_KEYS = {
    "active_mutation",
    "active_mutation_flags",
    "active_state_mutated",
    "mutation_flags",
    "mutation_performed",
    "mutations_performed",
}
_PROHIBITED_BOOLEAN_KEYS = (
    _RELEASE_PROMOTION_CLAIM_KEYS
    | _OFFICIAL_ACTION_CLAIM_KEYS
    | _LIVE_OR_DEVHUB_CLAIM_KEYS
    | _ACTIVE_MUTATION_FLAG_KEYS
)
_PROHIBITED_NONEMPTY_KEYS = (
    _PRIVATE_ARTIFACT_KEYS
    | _GUARANTEE_CLAIM_KEYS
    | _RELEASE_PROMOTION_CLAIM_KEYS
    | _OFFICIAL_ACTION_CLAIM_KEYS
    | _LIVE_OR_DEVHUB_CLAIM_KEYS
    | _ACTIVE_MUTATION_FLAG_KEYS
)


@dataclass(frozen=True)
class AuditFinding:
    check_id: str
    status: str
    detail: str

    def to_dict(self) -> dict[str, str]:
        return {"check_id": self.check_id, "status": self.status, "detail": self.detail}


def sha256_text(value: str) -> str:
    """Return a deterministic sha256 hex digest for fixture evidence text."""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def load_fixture(path: Path | str) -> dict[str, Any]:
    fixture_path = Path(path)
    with fixture_path.open("r", encoding="utf-8") as fixture_file:
        data = json.load(fixture_file)
    if not isinstance(data, dict):
        raise ValueError("inactive release transition fixture must be a JSON object")
    return data


def build_audit_packet_from_fixture(path: Path | str) -> dict[str, Any]:
    return build_audit_packet(load_fixture(path))


def build_audit_packet(fixture: Mapping[str, Any]) -> dict[str, Any]:
    top_level_problems = _inactive_boundary_problems(fixture, "fixture", descend=False)
    if top_level_problems:
        raise ValueError("; ".join(top_level_problems))

    rows = fixture.get("decision_rows")
    if not isinstance(rows, list) or not rows:
        raise ValueError("fixture decision_rows must be a non-empty list")

    audited_rows = [_audit_decision_row(row) for row in rows]
    return {
        "packet_version": PACKET_VERSION,
        "audit_mode": "fixture_first_inactive",
        "side_effects": "none",
        "prohibited_mutations": list(PROHIBITED_MUTATIONS),
        "audited_decision_count": len(audited_rows),
        "audited_decisions": audited_rows,
        "all_recommendations_are_no_op": all(
            row["transition_recommendation"].startswith("no_op_") for row in audited_rows
        ),
        "synthetic_decisions_present": sorted({row["decision"] for row in audited_rows}),
    }


def _audit_decision_row(row: Mapping[str, Any]) -> dict[str, Any]:
    row_id = _required_str(row, "row_id")
    decision = _required_str(row, "decision")
    if decision not in ALLOWED_DECISIONS:
        raise ValueError(f"unsupported release decision for {row_id}: {decision}")

    findings: list[AuditFinding] = []
    findings.extend(_check_inactive_boundary(row, row_id))
    findings.extend(_check_prerequisites(row))
    findings.extend(_check_source_evidence(row))
    findings.extend(_check_reviewer_approvals(row))
    findings.extend(_check_rollback_blocker_checks(row))
    findings.extend(_check_validation_commands(row))

    failing_checks = [finding.check_id for finding in findings if finding.status != "pass"]
    ready_for_external_promotion = decision == "release-ready" and not failing_checks

    return {
        "row_id": row_id,
        "decision": decision,
        "ready_for_external_promotion": ready_for_external_promotion,
        "failing_checks": failing_checks,
        "checks": [finding.to_dict() for finding in findings],
        "transition_recommendation": _recommend_no_op(decision, failing_checks),
        "state_mutation_performed": False,
        "artifact_promotion_performed": False,
    }


def _check_inactive_boundary(row: Mapping[str, Any], row_id: str) -> list[AuditFinding]:
    problems = _inactive_boundary_problems(row, row_id, descend=True)
    if not problems:
        return [AuditFinding("inactive_boundary", "pass", "row contains no active, private, live, or guarantee claims")]
    return [AuditFinding("inactive_boundary", "fail", problem) for problem in problems]


def _inactive_boundary_problems(value: Any, path: str, *, descend: bool) -> list[str]:
    problems: list[str] = []
    if isinstance(value, Mapping):
        for key, nested in value.items():
            key_text = str(key)
            key_name = key_text.lower()
            nested_path = f"{path}.{key_text}"
            if key_name in _PRIVATE_ARTIFACT_KEYS and _is_present(nested):
                problems.append(f"{nested_path} contains a private/session/browser/raw/downloaded artifact")
            if key_name in _PROHIBITED_BOOLEAN_KEYS and nested is True:
                problems.append(f"{nested_path} claims prohibited inactive transition activity")
            if key_name in _PROHIBITED_NONEMPTY_KEYS and key_name not in _PROHIBITED_BOOLEAN_KEYS and _is_present(nested):
                problems.append(f"{nested_path} contains prohibited inactive transition content")
            if key_name in _GUARANTEE_CLAIM_KEYS and _is_present(nested):
                problems.append(f"{nested_path} contains a legal or permitting guarantee")
            if key_name in {"artifacts", "artifact_refs", "artifact_records"}:
                problems.extend(_artifact_reference_problems(nested, nested_path))
            if descend:
                problems.extend(_inactive_boundary_problems(nested, nested_path, descend=True))
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            if descend:
                problems.extend(_inactive_boundary_problems(nested, f"{path}[{index}]", descend=True))
    return problems


def _artifact_reference_problems(value: Any, path: str) -> list[str]:
    problems: list[str] = []
    items = value if isinstance(value, list) else [value]
    for index, item in enumerate(items):
        item_path = f"{path}[{index}]"
        if isinstance(item, Mapping):
            artifact_class = str(
                item.get("artifact_class") or item.get("artifact_type") or item.get("type") or ""
            ).lower()
            if artifact_class in _PRIVATE_ARTIFACT_CLASSES:
                problems.append(f"{item_path} references prohibited {artifact_class} artifact content")
            ref = item.get("artifact_ref") or item.get("path") or item.get("uri")
            if isinstance(ref, str) and _private_artifact_ref(ref):
                problems.append(f"{item_path} references prohibited private artifact ref")
        elif isinstance(item, str) and _private_artifact_ref(item):
            problems.append(f"{item_path} references prohibited private artifact ref")
    return problems


def _private_artifact_ref(value: str) -> bool:
    normalized = value.lower()
    return normalized.startswith(("private://", "session://", "browser://", "raw://", "downloaded://"))


def _is_present(value: Any) -> bool:
    if value is None or value is False:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)
    return True


def _check_prerequisites(row: Mapping[str, Any]) -> list[AuditFinding]:
    prerequisites = row.get("promotion_prerequisites")
    if not isinstance(prerequisites, dict) or not prerequisites:
        return [AuditFinding("promotion_prerequisites", "fail", "no promotion prerequisites were supplied")]

    findings: list[AuditFinding] = []
    for name in sorted(prerequisites):
        satisfied = prerequisites[name]
        status = "pass" if satisfied is True else "fail"
        detail = "satisfied" if satisfied is True else "not satisfied"
        findings.append(AuditFinding(f"promotion_prerequisite:{name}", status, detail))
    return findings


def _check_source_evidence(row: Mapping[str, Any]) -> list[AuditFinding]:
    evidence_items = row.get("source_evidence")
    if not isinstance(evidence_items, list) or not evidence_items:
        return [AuditFinding("source_evidence", "fail", "no source evidence hashes were supplied")]

    findings: list[AuditFinding] = []
    for index, item in enumerate(evidence_items):
        if not isinstance(item, dict):
            findings.append(AuditFinding(f"source_evidence:{index}", "fail", "evidence item is not an object"))
            continue
        evidence_id = str(item.get("evidence_id", index))
        text = item.get("evidence_text")
        expected_hash = item.get("expected_sha256")
        if not isinstance(text, str) or not isinstance(expected_hash, str):
            findings.append(AuditFinding(f"source_evidence:{evidence_id}", "fail", "missing text or expected hash"))
            continue
        if not _is_sha256_hex(expected_hash):
            findings.append(AuditFinding(f"source_evidence:{evidence_id}", "fail", "expected hash is not a sha256 hex digest"))
            continue
        actual_hash = sha256_text(text)
        if actual_hash == expected_hash:
            findings.append(AuditFinding(f"source_evidence:{evidence_id}", "pass", "sha256 hash matches fixture evidence"))
        else:
            findings.append(AuditFinding(f"source_evidence:{evidence_id}", "fail", "sha256 hash mismatch"))
    return findings


def _check_reviewer_approvals(row: Mapping[str, Any]) -> list[AuditFinding]:
    approvals = row.get("reviewer_approvals")
    if not isinstance(approvals, list) or not approvals:
        return [AuditFinding("reviewer_approvals", "fail", "no reviewer approvals were supplied")]

    findings: list[AuditFinding] = []
    for index, approval in enumerate(approvals):
        if not isinstance(approval, dict):
            findings.append(AuditFinding(f"reviewer_approval:{index}", "fail", "approval item is not an object"))
            continue
        reviewer_id = str(approval.get("reviewer_id", index))
        role = approval.get("role")
        approved = approval.get("approved") is True
        if not isinstance(role, str) or not role:
            findings.append(AuditFinding(f"reviewer_approval:{reviewer_id}", "fail", "reviewer approval row is missing a role"))
            continue
        status = "pass" if approved else "fail"
        detail = "approved" if approved else "approval missing or denied"
        findings.append(AuditFinding(f"reviewer_approval:{reviewer_id}", status, detail))
    return findings


def _check_rollback_blocker_checks(row: Mapping[str, Any]) -> list[AuditFinding]:
    checks = row.get("rollback_blocker_checks")
    if not isinstance(checks, list) or not checks:
        return [AuditFinding("rollback_blocker_checks", "fail", "no rollback blocker checks were supplied")]

    findings: list[AuditFinding] = []
    for index, check in enumerate(checks):
        if not isinstance(check, dict):
            findings.append(AuditFinding(f"rollback_blocker_check:{index}", "fail", "rollback blocker check is not an object"))
            continue
        check_id = str(check.get("check_id", index))
        blocker_present = check.get("blocker_present") is True
        cleared = check.get("cleared") is True
        if not isinstance(check.get("check_id"), str) or not check.get("check_id"):
            findings.append(AuditFinding(f"rollback_blocker_check:{index}", "fail", "rollback blocker check is missing check_id"))
        elif blocker_present and not cleared:
            findings.append(AuditFinding(f"rollback_blocker_check:{check_id}", "fail", "uncleared rollback blocker"))
        else:
            findings.append(AuditFinding(f"rollback_blocker_check:{check_id}", "pass", "rollback blocker check cleared"))
    return findings


def _check_validation_commands(row: Mapping[str, Any]) -> list[AuditFinding]:
    commands = row.get("validation_commands")
    if not isinstance(commands, list) or not commands:
        return [AuditFinding("validation_commands", "fail", "no validation command records were supplied")]

    findings: list[AuditFinding] = []
    for index, command in enumerate(commands):
        if not isinstance(command, dict):
            findings.append(AuditFinding(f"validation_command:{index}", "fail", "validation command item is not an object"))
            continue
        command_id = str(command.get("command_id", index))
        argv = command.get("argv")
        exit_code = command.get("exit_code")
        output_hash = command.get("output_sha256")
        recorded_at = command.get("recorded_at")
        has_argv = isinstance(argv, list) and all(isinstance(part, str) for part in argv) and bool(argv)
        has_hash = isinstance(output_hash, str) and _is_sha256_hex(output_hash)
        has_time = isinstance(recorded_at, str) and bool(recorded_at)
        if has_argv and has_hash and has_time and exit_code == 0:
            findings.append(AuditFinding(f"validation_command:{command_id}", "pass", "recorded command passed with output hash"))
        else:
            findings.append(AuditFinding(f"validation_command:{command_id}", "fail", "command record missing required passing evidence"))
    return findings


def _is_sha256_hex(value: str) -> bool:
    return len(value) == 64 and all(character in "0123456789abcdef" for character in value.lower())


def _recommend_no_op(decision: str, failing_checks: Sequence[str]) -> str:
    if decision == "release-ready" and not failing_checks:
        return "no_op_release_ready_requires_external_promotion_review"
    if decision == "release-ready":
        return "no_op_release_ready_blocked_until_audit_findings_clear"
    if decision == "release-held":
        return "no_op_keep_release_held_until_findings_clear"
    return "no_op_keep_release_rejected_without_transition"


def _required_str(row: Mapping[str, Any], key: str) -> str:
    value = row.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"decision row missing required string field: {key}")
    return value


__all__ = [
    "PACKET_VERSION",
    "PROHIBITED_MUTATIONS",
    "build_audit_packet",
    "build_audit_packet_from_fixture",
    "load_fixture",
    "sha256_text",
]
