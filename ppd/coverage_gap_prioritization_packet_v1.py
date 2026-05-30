"""Fixture-first PP&D coverage gap prioritization packet builder v1.

This module consumes a requirement extraction coverage gap queue fixture and emits a
review packet of cited, ordered candidates grouped by PP&D review families. It is
side-effect free unless the optional CLI output path is used.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

PACKET_VERSION = "coverage_gap_prioritization_packet_v1"
SUPPORTED_QUEUE_VERSION = "requirement_extraction_coverage_gap_queue_v1"

GROUP_ORDER = [
    "forms",
    "pdfs",
    "fee_triggers",
    "deadlines",
    "file_rules",
    "permit_type_exceptions",
    "action_gates",
]

GROUP_LABELS = {
    "forms": "Forms",
    "pdfs": "PDFs",
    "fee_triggers": "Fee triggers",
    "deadlines": "Deadlines",
    "file_rules": "File rules",
    "permit_type_exceptions": "Permit-type exceptions",
    "action_gates": "Action gates",
}

DEFAULT_OWNER_BY_GROUP = {
    "forms": "forms-reviewer",
    "pdfs": "pdf-reviewer",
    "fee_triggers": "fees-reviewer",
    "deadlines": "deadlines-reviewer",
    "file_rules": "documents-reviewer",
    "permit_type_exceptions": "process-model-reviewer",
    "action_gates": "guardrail-reviewer",
}

DEFAULT_FIXTURE_FAMILY_BY_GROUP = {
    "forms": "ppd/tests/fixtures/forms_requirement_extraction/",
    "pdfs": "ppd/tests/fixtures/pdf_requirement_extraction/",
    "fee_triggers": "ppd/tests/fixtures/fee_trigger_requirement_extraction/",
    "deadlines": "ppd/tests/fixtures/deadline_requirement_extraction/",
    "file_rules": "ppd/tests/fixtures/file_rule_requirement_extraction/",
    "permit_type_exceptions": "ppd/tests/fixtures/permit_type_exception_requirement_extraction/",
    "action_gates": "ppd/tests/fixtures/action_gate_requirement_extraction/",
}

SEVERITY_RANK = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
}

DEPENDENCY_STAGE_RANK = {
    "source_record": 0,
    "document_record": 1,
    "requirement_node": 2,
    "process_model": 3,
    "guardrail_bundle": 4,
    "user_gap_analysis": 5,
    "devhub_action": 6,
}

DEFAULT_OFFLINE_VALIDATION_COMMANDS = [
    ["python3", "-m", "py_compile", "ppd/coverage_gap_prioritization_packet_v1.py"],
    ["python3", "-m", "pytest", "ppd/tests/test_coverage_gap_prioritization_packet_v1.py"],
    ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
]

_FORBIDDEN_ARTIFACT_KEYS = {
    "auth",
    "authenticated_artifact",
    "authenticated_artifacts",
    "auth_state",
    "authorization",
    "browser_artifact",
    "browser_artifacts",
    "browser_session",
    "browser_state",
    "browser_trace",
    "cookie",
    "cookies",
    "credential",
    "credentials",
    "devhub_session",
    "download_path",
    "downloaded_data",
    "downloaded_document",
    "downloaded_documents",
    "downloaded_pdf",
    "har",
    "har_path",
    "local_download",
    "mfa",
    "password",
    "pdf_bytes",
    "private_artifact",
    "private_artifacts",
    "private_file",
    "private_file_path",
    "raw_body",
    "raw_content",
    "raw_crawl",
    "raw_crawl_output",
    "raw_data",
    "raw_download",
    "raw_html",
    "raw_pdf",
    "response_body",
    "screenshot",
    "session",
    "session_file",
    "storage_state",
    "token",
    "trace",
    "trace_path",
    "warc_path",
}

_LIVE_OR_PROMOTION_KEYS = {
    "active_promotion",
    "extraction_executed",
    "live_crawl",
    "live_extraction",
    "live_extraction_claim",
    "live_network_access",
    "live_processor_claim",
    "live_run",
    "promoted",
    "promotion_claim",
    "promotion_executed",
    "release_promotion_claim",
}

_OUTCOME_GUARANTEE_KEYS = {
    "approval_guarantee",
    "compliance_guarantee",
    "guaranteed_outcome",
    "legal_advice",
    "legal_determination",
    "permit_approval_guarantee",
    "permitting_outcome_guarantee",
}

_CONSEQUENTIAL_ACTION_KEYS = {
    "cancel_request",
    "certify_acknowledgement",
    "consequential_action",
    "execute_payment",
    "official_upload",
    "pay_fee",
    "purchase_permit",
    "schedule_inspection",
    "submit_application",
    "submit_permit",
    "upload_correction",
}

_MUTATION_KEYS = {
    "active_agent_state_mutation",
    "active_document_mutation",
    "active_guardrail_mutation",
    "active_process_mutation",
    "active_release_state_mutation",
    "active_requirement_mutation",
    "active_source_mutation",
    "agent_state_mutation",
    "document_mutation",
    "guardrail_mutation",
    "mutates_agent_state",
    "mutates_document",
    "mutates_documents",
    "mutates_guardrail",
    "mutates_guardrails",
    "mutates_process",
    "mutates_processes",
    "mutates_release_state",
    "mutates_requirement",
    "mutates_requirements",
    "mutates_source",
    "mutates_sources",
    "process_mutation",
    "release_state_mutation",
    "requirement_mutation",
    "source_mutation",
    "updates_active_document_record",
    "updates_active_guardrail",
    "updates_active_process",
    "updates_active_requirement",
    "updates_active_source",
}

_FORBIDDEN_PHRASE_CODES = (
    (
        "forbidden_private_authenticated_session_or_browser_artifact",
        (
            "authenticated artifact",
            "auth state",
            "browser artifact",
            "browser session",
            "cookie",
            "private file",
            "stored session",
            "trace saved",
        ),
    ),
    (
        "forbidden_raw_crawl_pdf_or_downloaded_data",
        (
            "downloaded pdf",
            "downloaded the document",
            "raw crawl output",
            "raw data saved",
            "raw pdf",
            "raw response body",
        ),
    ),
    (
        "forbidden_live_extraction_or_promotion_claim",
        (
            "live extraction",
            "live crawl",
            "promoted to active",
            "promotion completed",
            "release promoted",
        ),
    ),
    (
        "forbidden_legal_or_permitting_outcome_guarantee",
        (
            "approval guaranteed",
            "compliance guaranteed",
            "guarantee approval",
            "legally sufficient",
            "permit will be approved",
            "will pass inspection",
        ),
    ),
    (
        "forbidden_consequential_action_language",
        (
            "cancel the permit",
            "certify acknowledgement",
            "pay the fee",
            "purchase the permit",
            "schedule inspection",
            "submit permit",
            "submit the application",
            "upload correction",
        ),
    ),
    (
        "active_ppd_state_mutation",
        (
            "changed release state",
            "mutated active source",
            "promoted requirement",
            "updated active document",
            "updated agent state",
        ),
    ),
)


@dataclass(frozen=True)
class CoverageGapPrioritizationViolation:
    code: str
    path: str
    message: str


class CoverageGapPrioritizationPacketError(ValueError):
    """Raised when a prioritization packet is unsafe or malformed."""

    def __init__(self, violations: List[CoverageGapPrioritizationViolation]) -> None:
        self.violations = violations
        codes = ", ".join(sorted({violation.code for violation in violations}))
        super().__init__(f"invalid coverage gap prioritization packet v1: {codes}")


def load_json(path: Path) -> Dict[str, Any]:
    """Load a JSON object from a fixture path."""
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object at {path}")
    return value


def build_packet_from_paths(queue_path: Path, policy_path: Optional[Path] = None) -> Dict[str, Any]:
    """Build a packet from queue and optional reviewer policy fixture paths."""
    queue = load_json(queue_path)
    policy = load_json(policy_path) if policy_path is not None else {}
    packet = build_packet(queue, policy)
    packet["input_fixture"] = str(queue_path)
    if policy_path is not None:
        packet["reviewer_policy_fixture"] = str(policy_path)
    assert_valid_coverage_gap_prioritization_packet_v1(packet)
    return packet


def build_packet(queue: Mapping[str, Any], reviewer_policy: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    """Build a deterministic review packet from a coverage gap queue object."""
    policy = reviewer_policy or {}
    queue_version = _require_string(queue, "queue_version")
    if queue_version != SUPPORTED_QUEUE_VERSION:
        raise ValueError(f"unsupported queue_version: {queue_version}")

    raw_gaps = queue.get("gaps")
    if not isinstance(raw_gaps, list):
        raise ValueError("coverage gap queue must contain a gaps list")

    candidates_by_group: Dict[str, List[Dict[str, Any]]] = {group: [] for group in GROUP_ORDER}
    for index, raw_gap in enumerate(raw_gaps):
        if not isinstance(raw_gap, Mapping):
            raise ValueError(f"gap at index {index} must be an object")
        candidate = _candidate_from_gap(raw_gap, policy)
        candidates_by_group[candidate["group"]].append(candidate)

    review_groups: List[Dict[str, Any]] = []
    total_candidates = 0
    for group in GROUP_ORDER:
        candidates = sorted(candidates_by_group[group], key=_candidate_sort_key)
        if not candidates:
            continue
        total_candidates += len(candidates)
        review_groups.append(
            {
                "group": group,
                "label": GROUP_LABELS[group],
                "candidate_count": len(candidates),
                "candidates": candidates,
            }
        )

    packet = {
        "packet_version": PACKET_VERSION,
        "source_queue_version": queue_version,
        "source_queue_id": _require_string(queue, "queue_id"),
        "fixture_first": True,
        "scope_note": "Prioritization packet only; does not change active requirements, process models, guardrail bundles, source records, or release state.",
        "rollback_note": "Remove this derived packet and its fixtures; no active PP&D artifacts are mutated by this builder.",
        "group_order": GROUP_ORDER,
        "review_groups": review_groups,
        "candidate_count": total_candidates,
        "offline_validation_commands": _offline_validation_commands(policy),
    }
    assert_valid_coverage_gap_prioritization_packet_v1(packet)
    return packet


def validate_coverage_gap_prioritization_packet_v1(packet: Mapping[str, Any]) -> List[CoverageGapPrioritizationViolation]:
    violations: List[CoverageGapPrioritizationViolation] = []
    if not isinstance(packet, Mapping):
        return [_violation("packet_not_mapping", "$", "packet must be a mapping")]

    if packet.get("packet_version") != PACKET_VERSION:
        violations.append(_violation("invalid_packet_version", "packet_version", "packet_version must identify coverage gap prioritization packet v1"))
    if packet.get("fixture_first") is not True:
        violations.append(_violation("missing_fixture_first_attestation", "fixture_first", "packet must be fixture-first"))
    if not _text(packet.get("rollback_note")):
        violations.append(_violation("missing_rollback_note", "rollback_note", "packet rollback note is required"))

    rows = _priority_rows(packet)
    if not rows:
        violations.append(_violation("missing_priority_rows", "review_groups", "packet must include priority rows"))
    for index, row_with_path in enumerate(rows):
        row, path = row_with_path
        violations.extend(_validate_priority_row(row, path or f"priority_rows[{index}]"))

    violations.extend(_validate_offline_commands(packet.get("offline_validation_commands"), "offline_validation_commands"))
    violations.extend(_validate_forbidden_content(packet, "$"))
    return violations


def assert_valid_coverage_gap_prioritization_packet_v1(packet: Mapping[str, Any]) -> None:
    violations = validate_coverage_gap_prioritization_packet_v1(packet)
    if violations:
        raise CoverageGapPrioritizationPacketError(violations)


def is_valid_coverage_gap_prioritization_packet_v1(packet: Mapping[str, Any]) -> bool:
    return not validate_coverage_gap_prioritization_packet_v1(packet)


def _candidate_from_gap(gap: Mapping[str, Any], policy: Mapping[str, Any]) -> Dict[str, Any]:
    group = _normalize_group(_require_string(gap, "category"))
    evidence = _evidence_list(gap.get("source_evidence"))
    severity = _normalize_severity(_require_string(gap, "severity"))
    dependency_order = _dependency_order(gap)
    reviewer_owner = str(gap.get("reviewer_owner") or _owner_for_group(group, policy))
    expected_family = str(
        gap.get("expected_follow_up_fixture_family")
        or _fixture_family_for_group(group, policy)
    )
    rollback_note = str(
        gap.get("rollback_note")
        or "Drop the follow-up fixture candidate before promotion; no active requirement state is changed."
    )

    return {
        "candidate_id": _require_string(gap, "gap_id"),
        "priority_row_id": _require_string(gap, "gap_id"),
        "category": group,
        "group": group,
        "severity": severity,
        "dependency_order": dependency_order,
        "reviewer_owner": reviewer_owner,
        "expected_follow_up_fixture_family": expected_family,
        "rollback_note": rollback_note,
        "requirement_id": _require_string(gap, "requirement_id"),
        "permit_type": str(gap.get("permit_type", "unspecified")),
        "process_stage": str(gap.get("process_stage", "unspecified")),
        "coverage_reason": _require_string(gap, "coverage_reason"),
        "missing_detail": _require_string(gap, "missing_detail"),
        "dependencies": _string_list(gap.get("dependencies")),
        "citations": evidence,
        "offline_validation_commands": _gap_validation_commands(gap),
    }


def _validate_priority_row(row: Mapping[str, Any], path: str) -> List[CoverageGapPrioritizationViolation]:
    violations: List[CoverageGapPrioritizationViolation] = []
    if not _text(row.get("candidate_id")) and not _text(row.get("priority_row_id")):
        violations.append(_violation("missing_priority_row_id", f"{path}.candidate_id", "priority row id is required"))
    category = _text(row.get("category"), _text(row.get("group")))
    if not category:
        violations.append(_violation("missing_category", f"{path}.category", "priority row category is required"))
    else:
        try:
            _normalize_group(category)
        except ValueError as exc:
            violations.append(_violation("invalid_category", f"{path}.category", str(exc)))

    severity = _text(row.get("severity"))
    if not severity:
        violations.append(_violation("missing_severity", f"{path}.severity", "priority row severity is required"))
    else:
        try:
            _normalize_severity(severity)
        except ValueError as exc:
            violations.append(_violation("invalid_severity", f"{path}.severity", str(exc)))

    if "dependency_order" not in row or not isinstance(row.get("dependency_order"), int):
        violations.append(_violation("missing_dependency_order", f"{path}.dependency_order", "priority row dependency order is required"))
    if not _text(row.get("reviewer_owner")):
        violations.append(_violation("missing_reviewer_owner", f"{path}.reviewer_owner", "priority row reviewer owner is required"))
    if not _text(row.get("rollback_note")):
        violations.append(_violation("missing_rollback_note", f"{path}.rollback_note", "priority row rollback note is required"))

    citations = row.get("citations") or row.get("source_evidence")
    if not isinstance(citations, list) or not citations:
        violations.append(_violation("uncited_priority_row", f"{path}.citations", "priority row must include at least one citation"))
    else:
        for citation_index, citation in enumerate(citations):
            citation_path = f"{path}.citations[{citation_index}]"
            if not isinstance(citation, Mapping):
                violations.append(_violation("uncited_priority_row", citation_path, "citation must be an object"))
                continue
            for field in ("source_id", "title", "url", "citation"):
                if not _text(citation.get(field)):
                    violations.append(_violation("uncited_priority_row", f"{citation_path}.{field}", "citation field is required"))

    violations.extend(_validate_offline_commands(row.get("offline_validation_commands"), f"{path}.offline_validation_commands"))
    return violations


def _priority_rows(packet: Mapping[str, Any]) -> List[Tuple[Mapping[str, Any], str]]:
    rows = packet.get("ordered_review_candidates")
    if isinstance(rows, list):
        return [(row, f"ordered_review_candidates[{index}]") for index, row in enumerate(rows) if isinstance(row, Mapping)]

    priority_groups = packet.get("priority_groups")
    if isinstance(priority_groups, list):
        flattened: List[Tuple[Mapping[str, Any], str]] = []
        for group_index, group in enumerate(priority_groups):
            if not isinstance(group, Mapping):
                continue
            group_rows = group.get("rows")
            if isinstance(group_rows, list):
                for row_index, row in enumerate(group_rows):
                    if isinstance(row, Mapping):
                        flattened.append((row, f"priority_groups[{group_index}].rows[{row_index}]"))
        return flattened

    review_groups = packet.get("review_groups")
    if isinstance(review_groups, list):
        flattened = []
        for group_index, group in enumerate(review_groups):
            if not isinstance(group, Mapping):
                continue
            candidates = group.get("candidates")
            if isinstance(candidates, list):
                for candidate_index, candidate in enumerate(candidates):
                    if isinstance(candidate, Mapping):
                        flattened.append((candidate, f"review_groups[{group_index}].candidates[{candidate_index}]"))
        return flattened
    return []


def _validate_offline_commands(value: Any, path: str) -> List[CoverageGapPrioritizationViolation]:
    if not isinstance(value, list) or not value:
        return [_violation("missing_offline_validation_commands", path, "offline validation commands are required")]
    violations: List[CoverageGapPrioritizationViolation] = []
    unsafe_parts = {"curl", "wget", "playwright", "npx", "tesseract", "ocrmypdf"}
    for index, command in enumerate(value):
        if not isinstance(command, list) or not command or not all(isinstance(part, str) and part for part in command):
            violations.append(_violation("invalid_offline_validation_command", f"{path}[{index}]", "validation command must be a non-empty list of strings"))
        elif any(part in unsafe_parts for part in command):
            violations.append(_violation("unsafe_validation_command", f"{path}[{index}]", "validation command must remain offline and fixture-only"))
    return violations


def _validate_forbidden_content(value: Any, path: str) -> List[CoverageGapPrioritizationViolation]:
    violations: List[CoverageGapPrioritizationViolation] = []
    if isinstance(value, Mapping):
        for key, nested in value.items():
            key_text = str(key)
            normalized_key = key_text.lower()
            next_path = f"{path}.{key_text}"
            if normalized_key in _FORBIDDEN_ARTIFACT_KEYS:
                if nested or normalized_key in {"raw_pdf", "raw_crawl_output", "downloaded_data", "auth_state", "session", "browser_artifact"}:
                    if normalized_key.startswith("raw") or "download" in normalized_key or "pdf" in normalized_key:
                        code = "forbidden_raw_crawl_pdf_or_downloaded_data"
                    else:
                        code = "forbidden_private_authenticated_session_or_browser_artifact"
                    violations.append(_violation(code, next_path, "private, authenticated, session, browser, raw crawl, raw PDF, or downloaded data artifact is forbidden"))
            if normalized_key in _LIVE_OR_PROMOTION_KEYS and bool(nested):
                violations.append(_violation("forbidden_live_extraction_or_promotion_claim", next_path, "live extraction and promotion claims are forbidden"))
            if normalized_key in _OUTCOME_GUARANTEE_KEYS and bool(nested):
                violations.append(_violation("forbidden_legal_or_permitting_outcome_guarantee", next_path, "legal or permitting outcome guarantees are forbidden"))
            if normalized_key in _CONSEQUENTIAL_ACTION_KEYS and bool(nested):
                violations.append(_violation("forbidden_consequential_action_language", next_path, "consequential official action language is forbidden"))
            if normalized_key in _MUTATION_KEYS and bool(nested):
                violations.append(_violation("active_ppd_state_mutation", next_path, "active source, document, requirement, process, guardrail, release-state, or agent-state mutation flags are forbidden"))
            violations.extend(_validate_forbidden_content(nested, next_path))
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            violations.extend(_validate_forbidden_content(nested, f"{path}[{index}]"))
    elif isinstance(value, str):
        lowered = value.lower()
        for code, phrases in _FORBIDDEN_PHRASE_CODES:
            if any(phrase in lowered for phrase in phrases):
                violations.append(_violation(code, path, "forbidden safety-sensitive language is present"))
    return violations


def _normalize_group(category: str) -> str:
    normalized = category.strip().lower().replace("-", "_").replace(" ", "_")
    aliases = {
        "pdf": "pdfs",
        "form": "forms",
        "fee_trigger": "fee_triggers",
        "deadline": "deadlines",
        "file_rule": "file_rules",
        "permit_exception": "permit_type_exceptions",
        "permit_type_exception": "permit_type_exceptions",
        "action_gate": "action_gates",
    }
    group = aliases.get(normalized, normalized)
    if group not in GROUP_ORDER:
        raise ValueError(f"unsupported coverage gap category: {category}")
    return group


def _normalize_severity(severity: str) -> str:
    normalized = severity.strip().lower()
    if normalized not in SEVERITY_RANK:
        raise ValueError(f"unsupported severity: {severity}")
    return normalized


def _dependency_order(gap: Mapping[str, Any]) -> int:
    explicit = gap.get("dependency_order")
    if isinstance(explicit, int):
        return explicit
    stage = str(gap.get("dependency_stage", "requirement_node")).strip().lower()
    if stage in DEPENDENCY_STAGE_RANK:
        return DEPENDENCY_STAGE_RANK[stage]
    return DEPENDENCY_STAGE_RANK["requirement_node"]


def _candidate_sort_key(candidate: Mapping[str, Any]) -> Tuple[int, int, str]:
    severity = str(candidate["severity"])
    dependency_order = int(candidate["dependency_order"])
    candidate_id = str(candidate["candidate_id"])
    return (SEVERITY_RANK[severity], dependency_order, candidate_id)


def _owner_for_group(group: str, policy: Mapping[str, Any]) -> str:
    owners = policy.get("reviewer_owner_by_group")
    if isinstance(owners, Mapping) and isinstance(owners.get(group), str):
        return str(owners[group])
    return DEFAULT_OWNER_BY_GROUP[group]


def _fixture_family_for_group(group: str, policy: Mapping[str, Any]) -> str:
    families = policy.get("expected_follow_up_fixture_family_by_group")
    if isinstance(families, Mapping) and isinstance(families.get(group), str):
        return str(families[group])
    return DEFAULT_FIXTURE_FAMILY_BY_GROUP[group]


def _offline_validation_commands(policy: Mapping[str, Any]) -> List[List[str]]:
    commands = policy.get("offline_validation_commands")
    if commands is None:
        return [list(command) for command in DEFAULT_OFFLINE_VALIDATION_COMMANDS]
    return _command_list(commands)


def _gap_validation_commands(gap: Mapping[str, Any]) -> List[List[str]]:
    commands = gap.get("offline_validation_commands")
    if commands is None:
        return [list(command) for command in DEFAULT_OFFLINE_VALIDATION_COMMANDS[:2]]
    return _command_list(commands)


def _command_list(value: Any) -> List[List[str]]:
    if not isinstance(value, list):
        raise ValueError("offline validation commands must be a list")
    commands: List[List[str]] = []
    for index, command in enumerate(value):
        if not isinstance(command, list) or not command:
            raise ValueError(f"offline validation command at index {index} must be a non-empty list")
        commands.append([str(part) for part in command])
    return commands


def _evidence_list(value: Any) -> List[Dict[str, str]]:
    if not isinstance(value, list) or not value:
        raise ValueError("source_evidence must be a non-empty list")
    citations: List[Dict[str, str]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValueError(f"source_evidence at index {index} must be an object")
        citations.append(
            {
                "source_id": _require_string(item, "source_id"),
                "title": _require_string(item, "title"),
                "url": _require_string(item, "url"),
                "citation": _require_string(item, "citation"),
            }
        )
    return citations


def _string_list(value: Any) -> List[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("expected a list of strings")
    return [str(item) for item in value]


def _require_string(mapping: Mapping[str, Any], key: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"missing required string: {key}")
    return value


def _text(value: Any, default: str = "") -> str:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return default


def _violation(code: str, path: str, message: str) -> CoverageGapPrioritizationViolation:
    return CoverageGapPrioritizationViolation(code=code, path=path, message=message)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Build PP&D coverage gap prioritization packet v1")
    parser.add_argument("--queue", required=True, type=Path)
    parser.add_argument("--policy", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    packet = build_packet_from_paths(args.queue, args.policy)
    rendered = json.dumps(packet, indent=2, sort_keys=True) + "\n"
    if args.output is None:
        print(rendered, end="")
    else:
        args.output.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
