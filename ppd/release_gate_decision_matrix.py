"""Fixture-first PP&D release gate decision matrix v1.

This module intentionally works from committed evidence dictionaries or JSON
fixtures. It does not crawl public sources, open DevHub, read private artifacts,
or perform official permitting actions.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence

REQUIRED_INPUT_SECTIONS = (
    "release_candidate_evidence_bundle_v1",
    "readiness_gap_report_v1",
    "public_source_refresh_evidence_intake_packet_v1",
    "devhub_observation_evidence_intake_packet_v1",
    "action_journal_replay_findings_v1",
)

REQUIRED_ATTESTATIONS = (
    "no_live_crawl",
    "no_devhub",
    "no_private_artifact",
    "no_official_action",
    "no_active_promotion",
)

DEPENDENCY_ORDER = (
    "public_source_refresh_evidence_intake_packet_v1",
    "devhub_observation_evidence_intake_packet_v1",
    "action_journal_replay_findings_v1",
    "readiness_gap_report_v1",
    "release_candidate_evidence_bundle_v1",
    "reviewer_signoff",
)

OFFLINE_VALIDATION_COMMANDS = (
    ("python3", "-m", "py_compile", "ppd/release_gate_decision_matrix.py"),
    ("python3", "-m", "pytest", "ppd/tests/test_release_gate_decision_matrix.py"),
    ("python3", "ppd/daemon/ppd_daemon.py", "--self-test"),
)

ROLLBACK_CHECKPOINTS = (
    "restore_last_passing_fixture_bundle",
    "revert_generated_release_gate_matrix",
    "retain_no_live_crawl_and_no_devhub_attestations",
    "keep_active_promotion_disabled_until_new_matrix_passes",
)

REVIEWER_SIGNOFF_FIELDS = (
    "reviewer_name",
    "reviewer_role",
    "reviewed_at",
    "decision_acknowledged",
    "notes",
)

_MUTATION_FLAG_KEYS = {
    "active_source_mutation",
    "source_mutation",
    "source_mutation_active",
    "active_surface_registry_mutation",
    "surface_registry_mutation",
    "surface_registry_mutation_active",
    "active_guardrail_mutation",
    "guardrail_mutation",
    "guardrail_mutation_active",
    "active_prompt_mutation",
    "prompt_mutation",
    "prompt_mutation_active",
    "active_release_state_mutation",
    "release_state_mutation",
    "release_state_mutation_active",
    "active_agent_state_mutation",
    "agent_state_mutation",
    "agent_state_mutation_active",
}

_PRIVATE_OR_RAW_KEY_RE = re.compile(
    r"(auth|authenticated|browser|cookie|credential|devhub_session|download|har|password|private|raw|session|screenshot|secret|storage_state|token|trace)",
    re.IGNORECASE,
)
_PRIVATE_OR_RAW_VALUE_RE = re.compile(
    r"(^file://)|(^/home/[^/]+/)|(^/Users/[^/]+/)|(^/root/)|(^/tmp/)|"
    r"(auth[_-]?state|browser[_-]?state|cookie|credential|har|password|private[_-]?artifact|raw[_-]?(body|crawl|data|html|pdf)|"
    r"session[_-]?(state|storage)|screenshot|secret|storage[_-]?state|token|trace\.zip|warc)",
    re.IGNORECASE,
)
_LIVE_OR_PROMOTION_CLAIM_RE = re.compile(
    r"\b(live\s+(crawl|execution|processor|promotion|release|run)|promoted\s+(to\s+)?(active|production|release)|"
    r"promotion\s+(complete|executed|performed)|deployed\s+to\s+production|published\s+live)\b",
    re.IGNORECASE,
)
_OUTCOME_GUARANTEE_RE = re.compile(
    r"\b(guarantee[sd]?\s+(approval|issuance|permit|legal|compliance|outcome)|"
    r"(permit|application|inspection|appeal)\s+(will|shall)\s+be\s+(approved|issued|accepted|granted|upheld)|"
    r"legally\s+guaranteed|guaranteed\s+code\s+compliance)\b",
    re.IGNORECASE,
)
_CONSEQUENTIAL_ACTION_RE = re.compile(
    r"\b(click\s+submit|submit\s+(the\s+)?(permit|application|request)|upload\s+(correction|document|file|plans?)|"
    r"pay\s+(fee|fees|invoice)|enter\s+payment|schedule\s+(an\s+)?inspection|certify\s+(the\s+)?(application|acknowledgement)|"
    r"cancel\s+(permit|inspection|application)|withdraw\s+(permit|application|request)|purchase\s+(permit|trade\s+permit))\b",
    re.IGNORECASE,
)

DecisionMatrix = Dict[str, Any]
EvidenceBundle = Mapping[str, Any]


class ReleaseGateDecisionMatrixError(ValueError):
    """Raised when a release gate fixture is structurally invalid."""


def load_evidence_bundle(path: Path | str) -> Dict[str, Any]:
    """Load a release gate evidence fixture from JSON."""

    fixture_path = Path(path)
    with fixture_path.open("r", encoding="utf-8") as handle:
        loaded = json.load(handle)
    if not isinstance(loaded, dict):
        raise ReleaseGateDecisionMatrixError("release gate fixture must contain a JSON object")
    return loaded


def build_release_gate_decision_matrix(evidence: EvidenceBundle) -> DecisionMatrix:
    """Build the v1 decision matrix from fixture evidence."""

    _raise_if_forbidden_payload(evidence)
    _require_sections(evidence)
    attestations = _attestations(evidence)
    candidates = _release_candidates(evidence)
    rows = [_decision_row(candidate, evidence, attestations) for candidate in candidates]
    overall_decision = _overall_decision(row["decision"] for row in rows)

    matrix = {
        "schema_version": "ppd.release_gate_decision_matrix.v1",
        "decision_basis": "fixture_first_offline_evidence_only",
        "overall_decision": overall_decision,
        "attestations": attestations,
        "dependency_order": list(DEPENDENCY_ORDER),
        "rollback_checkpoints": list(ROLLBACK_CHECKPOINTS),
        "offline_validation_commands": [list(command) for command in OFFLINE_VALIDATION_COMMANDS],
        "reviewer_signoff_fields": _blank_reviewer_signoff(),
        "rows": rows,
    }
    errors = validate_release_gate_decision_matrix(matrix)
    if errors:
        raise ReleaseGateDecisionMatrixError("invalid release gate decision matrix: " + "; ".join(errors))
    return matrix


def matrix_from_fixture(path: Path | str) -> DecisionMatrix:
    """Load fixture evidence and build the decision matrix."""

    return build_release_gate_decision_matrix(load_evidence_bundle(path))


def validate_release_gate_decision_matrix(matrix: Mapping[str, Any]) -> List[str]:
    """Return deterministic validation errors for a release gate decision matrix."""

    errors: List[str] = []
    try:
        _raise_if_forbidden_payload(matrix)
    except ReleaseGateDecisionMatrixError as exc:
        errors.append(str(exc))

    if matrix.get("schema_version") != "ppd.release_gate_decision_matrix.v1":
        errors.append("schema_version must be ppd.release_gate_decision_matrix.v1")

    attestations = matrix.get("attestations")
    if not isinstance(attestations, Mapping):
        errors.append("attestations must be an object")
    else:
        for name in REQUIRED_ATTESTATIONS:
            if attestations.get(name) is not True:
                errors.append(f"attestations.{name} must be true")

    if tuple(_as_string_list(matrix.get("dependency_order"))) != DEPENDENCY_ORDER:
        errors.append("dependency_order must include the required release gate order")

    checkpoints = _as_string_list(matrix.get("rollback_checkpoints"))
    if tuple(checkpoints) != ROLLBACK_CHECKPOINTS:
        errors.append("rollback_checkpoints must include the required rollback checkpoints")

    signoff = matrix.get("reviewer_signoff_fields")
    _validate_reviewer_signoff(signoff, "reviewer_signoff_fields", errors)

    rows = matrix.get("rows")
    if not isinstance(rows, list) or not rows:
        errors.append("rows must be a non-empty list")
        return errors

    for index, row in enumerate(rows):
        path = f"rows[{index}]"
        if not isinstance(row, Mapping):
            errors.append(f"{path} must be an object")
            continue
        decision = str(row.get("decision", ""))
        if decision not in {"pass", "defer", "block"}:
            errors.append(f"{path}.decision must be pass, defer, or block")
        if not _as_string_list(row.get("citations")):
            errors.append(f"{path}.citations must be non-empty")
        if not _as_string_list(row.get("reasons")):
            errors.append(f"{path}.reasons must be non-empty")
        _validate_reviewer_signoff(row.get("reviewer_signoff"), f"{path}.reviewer_signoff", errors)
        if tuple(_as_string_list(row.get("dependency_order"))) != DEPENDENCY_ORDER:
            errors.append(f"{path}.dependency_order must include the required release gate order")
        if tuple(_as_string_list(row.get("rollback_checkpoints"))) != ROLLBACK_CHECKPOINTS:
            errors.append(f"{path}.rollback_checkpoints must include the required rollback checkpoints")
        if not isinstance(row.get("unresolved_blocker_handling"), Mapping):
            errors.append(f"{path}.unresolved_blocker_handling must be present")
        else:
            handling = row["unresolved_blocker_handling"]
            required_status = "manual_reconciliation_required_before_release_claim" if decision in {"defer", "block"} else "no_unresolved_blockers_detected"
            if handling.get("status") != required_status:
                errors.append(f"{path}.unresolved_blocker_handling.status must be {required_status}")
            if not _as_string_list(handling.get("citations")):
                errors.append(f"{path}.unresolved_blocker_handling.citations must be non-empty")

    return errors


def _require_sections(evidence: EvidenceBundle) -> None:
    missing = [section for section in REQUIRED_INPUT_SECTIONS if section not in evidence]
    if missing:
        joined = ", ".join(missing)
        raise ReleaseGateDecisionMatrixError(f"missing required evidence sections: {joined}")


def _attestations(evidence: EvidenceBundle) -> Dict[str, bool]:
    raw = evidence.get("attestations_v1", {})
    if not isinstance(raw, Mapping):
        raise ReleaseGateDecisionMatrixError("attestations_v1 must be an object when provided")
    return {name: bool(raw.get(name, False)) for name in REQUIRED_ATTESTATIONS}


def _release_candidates(evidence: EvidenceBundle) -> List[Mapping[str, Any]]:
    section = evidence["release_candidate_evidence_bundle_v1"]
    if not isinstance(section, Mapping):
        raise ReleaseGateDecisionMatrixError("release_candidate_evidence_bundle_v1 must be an object")
    candidates = section.get("candidates", [])
    if not isinstance(candidates, list) or not candidates:
        raise ReleaseGateDecisionMatrixError("release_candidate_evidence_bundle_v1.candidates must be a non-empty list")
    normalized: List[Mapping[str, Any]] = []
    for candidate in candidates:
        if not isinstance(candidate, Mapping):
            raise ReleaseGateDecisionMatrixError("each release candidate must be an object")
        if not candidate.get("candidate_id"):
            raise ReleaseGateDecisionMatrixError("each release candidate requires candidate_id")
        if not _as_string_list(candidate.get("evidence_ids")):
            raise ReleaseGateDecisionMatrixError("each release candidate requires evidence_ids")
        normalized.append(candidate)
    return normalized


def _decision_row(
    candidate: Mapping[str, Any],
    evidence: EvidenceBundle,
    attestations: Mapping[str, bool],
) -> Dict[str, Any]:
    candidate_id = str(candidate["candidate_id"])
    blocking_reasons: List[str] = []
    deferring_reasons: List[str] = []

    failed_attestations = [name for name, passed in attestations.items() if not passed]
    if failed_attestations:
        blocking_reasons.append("required safety attestations failed: " + ", ".join(failed_attestations))

    if _candidate_has_flag(candidate, "private_artifact_refs"):
        blocking_reasons.append("release candidate references private artifacts")
    if _candidate_has_flag(candidate, "official_action_requested"):
        blocking_reasons.append("release candidate requests official action")
    if _candidate_has_flag(candidate, "active_promotion_requested"):
        blocking_reasons.append("release candidate requests active promotion")

    readiness_gaps = _matching_items(
        evidence["readiness_gap_report_v1"], "gaps", candidate_id, "candidate_id"
    )
    unresolved_gaps = [gap for gap in readiness_gaps if str(gap.get("status", "")).lower() != "closed"]
    if unresolved_gaps:
        deferring_reasons.append("unresolved readiness gaps remain")

    source_items = _matching_items(
        evidence["public_source_refresh_evidence_intake_packet_v1"],
        "refresh_evidence",
        candidate_id,
        "candidate_id",
    )
    stale_sources = [item for item in source_items if str(item.get("freshness_status", "")).lower() != "current"]
    if stale_sources:
        deferring_reasons.append("public source refresh evidence is not current")

    devhub_items = _matching_items(
        evidence["devhub_observation_evidence_intake_packet_v1"],
        "observations",
        candidate_id,
        "candidate_id",
    )
    unreviewed_devhub = [item for item in devhub_items if str(item.get("review_status", "")).lower() != "accepted"]
    if unreviewed_devhub:
        deferring_reasons.append("DevHub observation evidence has not been accepted")

    journal_items = _matching_items(
        evidence["action_journal_replay_findings_v1"],
        "findings",
        candidate_id,
        "candidate_id",
    )
    unsafe_journal_findings = [
        item for item in journal_items if str(item.get("severity", "")).lower() in {"critical", "blocker"}
    ]
    if unsafe_journal_findings:
        blocking_reasons.append("action journal replay contains blocker findings")

    if blocking_reasons:
        decision = "block"
        reasons = blocking_reasons + deferring_reasons
    elif deferring_reasons:
        decision = "defer"
        reasons = deferring_reasons
    else:
        decision = "pass"
        reasons = ["all required fixture evidence is current, accepted, closed, and replay-clean"]

    citations = _citations(candidate, readiness_gaps, source_items, devhub_items, journal_items)
    return {
        "candidate_id": candidate_id,
        "title": str(candidate.get("title", candidate_id)),
        "decision": decision,
        "reasons": reasons,
        "citations": citations,
        "reviewer_signoff": _blank_reviewer_signoff(),
        "dependency_order": list(DEPENDENCY_ORDER),
        "rollback_checkpoints": list(ROLLBACK_CHECKPOINTS),
        "offline_validation_commands": [list(command) for command in OFFLINE_VALIDATION_COMMANDS],
        "attestations": dict(attestations),
        "unresolved_blocker_handling": _unresolved_blocker_handling(decision, citations),
    }


def _unresolved_blocker_handling(decision: str, citations: Sequence[str]) -> Dict[str, Any]:
    if decision in {"defer", "block"}:
        return {
            "status": "manual_reconciliation_required_before_release_claim",
            "summary": "Release claims remain blocked until unresolved blockers are closed in cited fixture evidence.",
            "citations": list(citations),
        }
    return {
        "status": "no_unresolved_blockers_detected",
        "summary": "No unresolved blocker was detected in the cited fixture evidence for this row.",
        "citations": list(citations),
    }


def _candidate_has_flag(candidate: Mapping[str, Any], name: str) -> bool:
    value = candidate.get(name, False)
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return len(value) > 0
    return bool(value)


def _matching_items(section: Any, list_name: str, candidate_id: str, id_name: str) -> List[Mapping[str, Any]]:
    if not isinstance(section, Mapping):
        raise ReleaseGateDecisionMatrixError(f"{list_name} section must be an object")
    items = section.get(list_name, [])
    if not isinstance(items, list):
        raise ReleaseGateDecisionMatrixError(f"{list_name} must be a list")
    matched: List[Mapping[str, Any]] = []
    for item in items:
        if not isinstance(item, Mapping):
            raise ReleaseGateDecisionMatrixError(f"{list_name} entries must be objects")
        if str(item.get(id_name, "")) == candidate_id:
            matched.append(item)
    return matched


def _citations(candidate: Mapping[str, Any], *item_groups: Iterable[Mapping[str, Any]]) -> List[str]:
    ordered: List[str] = []
    for evidence_id in _as_string_list(candidate.get("evidence_ids", [])):
        if evidence_id not in ordered:
            ordered.append(evidence_id)
    for group in item_groups:
        for item in group:
            for evidence_id in _as_string_list(item.get("evidence_ids", item.get("evidence_id", []))):
                if evidence_id not in ordered:
                    ordered.append(evidence_id)
    return ordered


def _as_string_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        return [str(item) for item in value if item is not None]
    return [str(value)]


def _blank_reviewer_signoff() -> Dict[str, Optional[Any]]:
    return {
        "reviewer_name": None,
        "reviewer_role": None,
        "reviewed_at": None,
        "decision_acknowledged": False,
        "notes": None,
    }


def _validate_reviewer_signoff(value: Any, path: str, errors: List[str]) -> None:
    if not isinstance(value, Mapping):
        errors.append(f"{path} must be an object")
        return
    missing = [field for field in REVIEWER_SIGNOFF_FIELDS if field not in value]
    if missing:
        errors.append(f"{path} missing required fields: {', '.join(missing)}")
    if value.get("decision_acknowledged") is not False:
        errors.append(f"{path}.decision_acknowledged must default to false")


def _overall_decision(decisions: Iterable[str]) -> str:
    materialized = list(decisions)
    if "block" in materialized:
        return "block"
    if "defer" in materialized:
        return "defer"
    return "pass"


def _raise_if_forbidden_payload(value: Any, path: str = "$") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            normalized_key = key_text.strip().lower().replace("-", "_")
            child_path = f"{path}.{key_text}"
            if _active_mutation_key(normalized_key, child):
                raise ReleaseGateDecisionMatrixError(f"active mutation flag is not allowed at {child_path}")
            if _PRIVATE_OR_RAW_KEY_RE.search(normalized_key) and child not in (None, "", [], {}):
                raise ReleaseGateDecisionMatrixError(f"private, authenticated, raw, session, or browser artifact is not allowed at {child_path}")
            _raise_if_forbidden_payload(child, child_path)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            _raise_if_forbidden_payload(child, f"{path}[{index}]")
    elif isinstance(value, str):
        if _PRIVATE_OR_RAW_VALUE_RE.search(value):
            raise ReleaseGateDecisionMatrixError(f"private, authenticated, raw, session, or browser artifact is not allowed at {path}")
        if _LIVE_OR_PROMOTION_CLAIM_RE.search(value):
            raise ReleaseGateDecisionMatrixError(f"live execution or promotion claim is not allowed at {path}")
        if _OUTCOME_GUARANTEE_RE.search(value):
            raise ReleaseGateDecisionMatrixError(f"legal or permitting outcome guarantee is not allowed at {path}")
        if _CONSEQUENTIAL_ACTION_RE.search(value):
            raise ReleaseGateDecisionMatrixError(f"consequential action language is not allowed at {path}")


def _active_mutation_key(normalized_key: str, value: Any) -> bool:
    if normalized_key in _MUTATION_FLAG_KEYS and _truthy(value):
        return True
    if normalized_key == "mutation_flags" and isinstance(value, Mapping):
        for flag, flag_value in value.items():
            flag_key = str(flag).strip().lower().replace("-", "_")
            if flag_key in _MUTATION_FLAG_KEYS and _truthy(flag_value):
                return True
    return False


def _truthy(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"active", "enabled", "true", "yes", "1", "mutate", "mutation"}
    return False


__all__ = [
    "DEPENDENCY_ORDER",
    "OFFLINE_VALIDATION_COMMANDS",
    "REQUIRED_ATTESTATIONS",
    "ROLLBACK_CHECKPOINTS",
    "ReleaseGateDecisionMatrixError",
    "build_release_gate_decision_matrix",
    "load_evidence_bundle",
    "matrix_from_fixture",
    "validate_release_gate_decision_matrix",
]
