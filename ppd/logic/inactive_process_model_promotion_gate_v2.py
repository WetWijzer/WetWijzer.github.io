"""Fixture-first promotion gate for inactive PP&D process-model deltas.

This module is intentionally side-effect free. It evaluates committed synthetic
fixture rows only and returns recommendations; it does not promote, mutate, crawl,
submit, upload, pay, schedule, or touch active process-model state.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import re
from typing import Any, Iterable, Literal

Recommendation = Literal["promote", "hold", "reject"]

_ALLOWED_RECOMMENDATIONS = {"promote", "hold", "reject"}
_REQUIRED_GATES = {
    "permit_family_recommendation",
    "citation_integrity",
    "stale_evidence_hold",
    "document_matrix",
    "fee_deadline_matrix",
    "unsupported_path_notes",
    "reviewer_disposition",
    "offline_validation_commands",
}
_FORBIDDEN_COMMAND_TOKENS = {
    "crawl",
    "devhub",
    "playwright",
    "upload",
    "submit",
    "certify",
    "payment",
    "schedule",
    "curl",
    "wget",
}
_PRIVATE_ARTIFACT_RE = re.compile(
    r"\b(auth[_-]?state|browser[_-]?state|cookie|credential|downloaded[_-]?document|har|private[_-]?file|raw[_-]?(?:body|crawl|download)|session[_-]?(?:state|file)|screenshot|trace\.zip|playwright-report)\b",
    re.IGNORECASE,
)
_LIVE_OR_DEVHUB_RE = re.compile(
    r"\b(live crawl(?:ed|ing)?|recrawled live|opened devhub|devhub session|authenticated devhub|playwright browser|browser automation)\b",
    re.IGNORECASE,
)
_GUARANTEE_RE = re.compile(
    r"\b(guarantee[sd]? (?:approval|issuance|permit|compliance|legal|permitting)|permit will (?:issue|be approved)|approval is (?:certain|assured|guaranteed)|legal outcome|permitting outcome)\b",
    re.IGNORECASE,
)
_OFFICIAL_COMPLETION_RE = re.compile(
    r"\b(submitted|uploaded|certified|paid|scheduled|cancelled|withdrew|purchased)\b.*\b(?:permit|application|inspection|fee|official record|devhub)\b",
    re.IGNORECASE,
)
_ACTIVE_MUTATION_KEYS = {
    "active_mutation",
    "active_mutation_enabled",
    "mutates_active_process_model",
    "mutates_active_process_models",
    "mutates_active_requirements",
    "mutates_active_guardrails",
    "mutates_active_prompts",
    "mutates_active_contracts",
    "mutates_source_registry",
    "mutates_devhub_surface",
    "mutates_release_state",
    "promote_active",
    "apply_to_active_state",
}
_ACTIVE_MUTATION_TEXT_RE = re.compile(
    r"\b(mutates? active|promote(?:s|d)? to active|appl(?:y|ied|ies) to active|active process-model mutation|release state mutation)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class GateResult:
    """A single gate outcome for one inactive process-model delta row."""

    gate: str
    passed: bool
    severity: Literal["info", "hold", "reject"]
    note: str


@dataclass(frozen=True)
class DeltaRecommendation:
    """Recommendation emitted by the v2 gate.

    The recommendation is advisory only. Consumers must not treat it as a state
    transition for an active process model.
    """

    delta_id: str
    process_id: str
    recommendation: Recommendation
    gate_results: tuple[GateResult, ...]
    offline_validation_commands: tuple[tuple[str, ...], ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "delta_id": self.delta_id,
            "process_id": self.process_id,
            "recommendation": self.recommendation,
            "gate_results": [result.__dict__ for result in self.gate_results],
            "offline_validation_commands": [list(command) for command in self.offline_validation_commands],
        }


def load_packet(path: str | Path) -> dict[str, Any]:
    """Load a promotion-gate packet from a committed JSON fixture."""

    packet_path = Path(path)
    with packet_path.open("r", encoding="utf-8") as handle:
        packet = json.load(handle)
    if not isinstance(packet, dict):
        raise ValueError("promotion gate packet must be a JSON object")
    return packet


def validate_packet(packet: dict[str, Any]) -> None:
    """Raise ValueError when a packet is incomplete or unsafe for v2 evaluation."""

    _validate_packet_scope(packet)
    _reject_forbidden_content(packet)
    assert_packet_has_all_v2_gates(packet)
    if not _commands({}, packet):
        raise ValueError("packet missing offline validation commands")
    command_gate = _offline_validation_commands({}, packet)
    if not command_gate.passed:
        raise ValueError(command_gate.note)
    rows = packet.get("synthetic_inactive_delta_rows")
    if not isinstance(rows, list) or not rows:
        raise ValueError("packet must include non-empty synthetic_inactive_delta_rows")
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("delta row must be an object")
        _validate_required_row_checks(row)


def evaluate_packet(packet: dict[str, Any]) -> list[DeltaRecommendation]:
    """Evaluate all synthetic inactive deltas in a v2 promotion-gate packet."""

    validate_packet(packet)
    rows = packet["synthetic_inactive_delta_rows"]
    return [_evaluate_row(row, packet) for row in rows]


def recommendations_as_dicts(packet: dict[str, Any]) -> list[dict[str, Any]]:
    """Convenience API for daemon checks and fixture tests."""

    return [recommendation.to_dict() for recommendation in evaluate_packet(packet)]


def _validate_packet_scope(packet: dict[str, Any]) -> None:
    if packet.get("packet_version") != "inactive-process-model-promotion-gate-v2":
        raise ValueError("unsupported packet_version")
    if packet.get("source_mode") != "fixture_first_synthetic_only":
        raise ValueError("packet must be fixture_first_synthetic_only")
    if packet.get("process_model_state") != "inactive":
        raise ValueError("packet must target inactive process models only")
    forbidden_surfaces = packet.get("forbidden_surfaces", [])
    if not isinstance(forbidden_surfaces, list):
        raise ValueError("forbidden_surfaces must be a list")
    required_forbidden = {
        "active_process_models",
        "requirements",
        "guardrails",
        "prompts",
        "contracts",
        "source_registries",
        "devhub_surfaces",
        "release_state",
        "live_crawl",
        "private_files",
        "uploads",
        "submissions",
        "certifications",
        "payments",
        "scheduling",
    }
    missing = required_forbidden - set(forbidden_surfaces)
    if missing:
        raise ValueError("packet must explicitly exclude forbidden surfaces: " + ", ".join(sorted(missing)))


def _validate_required_row_checks(row: dict[str, Any]) -> None:
    _required_string(row, "delta_id")
    _required_string(row, "process_id")
    if row.get("state") != "inactive":
        raise ValueError("delta row is not inactive")
    if row.get("source_kind") != "synthetic_fixture":
        raise ValueError("delta row is not synthetic fixture data")
    gates = (
        _permit_family_recommendation(row),
        _citation_integrity(row),
        _citation_integrity_check(row),
        _stale_evidence_hold(row),
        _stale_evidence_hold_check(row),
        _document_matrix(row),
        _fee_deadline_matrix(row),
        _unsupported_path_notes(row),
        _reviewer_disposition(row),
        _offline_validation_commands(row, {}),
    )
    reject_or_missing = [gate for gate in gates if gate.severity == "reject" or "missing" in gate.note]
    if reject_or_missing:
        first = reject_or_missing[0]
        raise ValueError(f"row {row.get('delta_id', '')} failed required {first.gate}: {first.note}")


def _evaluate_row(row: dict[str, Any], packet: dict[str, Any]) -> DeltaRecommendation:
    delta_id = _required_string(row, "delta_id")
    process_id = _required_string(row, "process_id")
    gate_results = (
        _permit_family_recommendation(row),
        _citation_integrity(row),
        _stale_evidence_hold(row),
        _document_matrix(row),
        _fee_deadline_matrix(row),
        _unsupported_path_notes(row),
        _reviewer_disposition(row),
        _offline_validation_commands(row, packet),
    )
    severities = {result.severity for result in gate_results if not result.passed}
    if "reject" in severities:
        recommendation: Recommendation = "reject"
    elif "hold" in severities:
        recommendation = "hold"
    else:
        recommendation = "promote"
    return DeltaRecommendation(
        delta_id=delta_id,
        process_id=process_id,
        recommendation=recommendation,
        gate_results=gate_results,
        offline_validation_commands=_commands(row, packet),
    )


def _permit_family_recommendation(row: dict[str, Any]) -> GateResult:
    recommendation = row.get("permit_family_recommendation")
    if not isinstance(recommendation, dict):
        return GateResult("permit_family_recommendation", False, "reject", "missing permit-family recommendation")
    if recommendation.get("recommendation") not in _ALLOWED_RECOMMENDATIONS:
        return GateResult("permit_family_recommendation", False, "reject", "permit-family recommendation must be promote, hold, or reject")
    required_strings = ("permit_family", "rationale")
    if any(not isinstance(recommendation.get(key), str) or not recommendation.get(key) for key in required_strings):
        return GateResult("permit_family_recommendation", False, "reject", "permit-family recommendation needs permit_family and rationale")
    citation_ids = recommendation.get("citation_ids")
    if not isinstance(citation_ids, list) or not citation_ids or not all(isinstance(item, str) and item for item in citation_ids):
        return GateResult("permit_family_recommendation", False, "reject", "permit-family recommendation needs citation_ids")
    return GateResult("permit_family_recommendation", True, "info", "permit-family recommendation is cited")


def _citation_integrity(row: dict[str, Any]) -> GateResult:
    citations = row.get("citations", [])
    if not isinstance(citations, list) or not citations:
        return GateResult("citation_integrity", False, "reject", "missing citations")
    bad = [citation for citation in citations if not _valid_citation(citation)]
    if bad:
        return GateResult("citation_integrity", False, "reject", "one or more citations lack source_id, locator, quote_hash, or public/synthetic scope")
    return GateResult("citation_integrity", True, "info", "all citations are scoped and addressable")


def _citation_integrity_check(row: dict[str, Any]) -> GateResult:
    check = row.get("citation_integrity_check")
    if not isinstance(check, dict):
        return GateResult("citation_integrity", False, "reject", "missing citation check")
    if check.get("status") != "passed" or not check.get("checked_at"):
        return GateResult("citation_integrity", False, "reject", "citation check must be passed and timestamped")
    return GateResult("citation_integrity", True, "info", "citation check is present")


def _stale_evidence_hold(row: dict[str, Any]) -> GateResult:
    stale = row.get("stale_evidence", [])
    if stale is None:
        stale = []
    if not isinstance(stale, list):
        return GateResult("stale_evidence_hold", False, "reject", "stale_evidence must be a list")
    unresolved = [item for item in stale if isinstance(item, dict) and item.get("status") != "resolved"]
    if unresolved:
        return GateResult("stale_evidence_hold", False, "hold", "unresolved stale evidence requires reviewer hold")
    return GateResult("stale_evidence_hold", True, "info", "no unresolved stale evidence")


def _stale_evidence_hold_check(row: dict[str, Any]) -> GateResult:
    check = row.get("stale_evidence_hold_check")
    if not isinstance(check, dict):
        return GateResult("stale_evidence_hold", False, "reject", "missing stale-evidence hold check")
    if check.get("status") not in {"clear", "hold_required"} or not check.get("checked_at"):
        return GateResult("stale_evidence_hold", False, "reject", "stale-evidence hold check must be clear or hold_required and timestamped")
    return GateResult("stale_evidence_hold", True, "info", "stale-evidence hold check is present")


def _document_matrix(row: dict[str, Any]) -> GateResult:
    matrix = row.get("document_matrix")
    if not isinstance(matrix, dict):
        return GateResult("document_matrix", False, "reject", "missing document matrix")
    required = matrix.get("required", [])
    mapped = matrix.get("mapped", [])
    if not isinstance(required, list) or not isinstance(mapped, list):
        return GateResult("document_matrix", False, "reject", "document matrix required and mapped entries must be lists")
    if not required:
        return GateResult("document_matrix", False, "reject", "missing document checks")
    missing = sorted(set(required) - set(mapped))
    if missing:
        return GateResult("document_matrix", False, "hold", "missing mapped documents: " + ", ".join(missing))
    return GateResult("document_matrix", True, "info", "required documents are mapped")


def _fee_deadline_matrix(row: dict[str, Any]) -> GateResult:
    matrix = row.get("fee_deadline_matrix")
    if not isinstance(matrix, dict):
        return GateResult("fee_deadline_matrix", False, "reject", "missing fee/deadline matrix")
    fees = matrix.get("fees", [])
    deadlines = matrix.get("deadlines", [])
    if not isinstance(fees, list) or not isinstance(deadlines, list):
        return GateResult("fee_deadline_matrix", False, "reject", "fees and deadlines must be lists")
    if not fees and not deadlines:
        return GateResult("fee_deadline_matrix", False, "reject", "missing fee/deadline checks")
    incomplete_fees = [fee for fee in fees if not isinstance(fee, dict) or not fee.get("trigger") or not fee.get("citation_id")]
    incomplete_deadlines = [deadline for deadline in deadlines if not isinstance(deadline, dict) or not deadline.get("event") or not deadline.get("citation_id")]
    if incomplete_fees or incomplete_deadlines:
        return GateResult("fee_deadline_matrix", False, "hold", "fee or deadline rows need trigger/event and citation_id")
    return GateResult("fee_deadline_matrix", True, "info", "fee and deadline rows are cited")


def _unsupported_path_notes(row: dict[str, Any]) -> GateResult:
    notes = row.get("unsupported_path_notes")
    if not isinstance(notes, list):
        return GateResult("unsupported_path_notes", False, "reject", "missing unsupported-path checks")
    if not notes:
        return GateResult("unsupported_path_notes", False, "reject", "missing unsupported-path checks")
    bad = [note for note in notes if not isinstance(note, dict) or not note.get("path") or not note.get("reason") or not note.get("citation_id")]
    if bad:
        return GateResult("unsupported_path_notes", False, "hold", "unsupported paths need path, reason, and citation_id")
    return GateResult("unsupported_path_notes", True, "info", "unsupported paths are documented")


def _reviewer_disposition(row: dict[str, Any]) -> GateResult:
    disposition = row.get("reviewer_disposition")
    if not isinstance(disposition, dict):
        return GateResult("reviewer_disposition", False, "reject", "missing reviewer disposition")
    if not disposition.get("reviewer") or not disposition.get("reviewed_at"):
        return GateResult("reviewer_disposition", False, "reject", "reviewer disposition needs reviewer and reviewed_at")
    status = disposition.get("status")
    if status == "approved_for_inactive_promotion_packet":
        return GateResult("reviewer_disposition", True, "info", "reviewer disposition allows recommendation")
    if status == "rejected":
        return GateResult("reviewer_disposition", False, "reject", "reviewer rejected delta")
    return GateResult("reviewer_disposition", False, "hold", "reviewer disposition is not approved")


def _offline_validation_commands(row: dict[str, Any], packet: dict[str, Any]) -> GateResult:
    commands = _commands(row, packet)
    if not commands:
        return GateResult("offline_validation_commands", False, "reject", "missing offline validation commands")
    for command in commands:
        if not command or command[0] not in {"python3", "pytest"}:
            return GateResult("offline_validation_commands", False, "reject", "commands must be exact offline python3 or pytest invocations")
        lowered = " ".join(command).lower()
        if any(token in lowered for token in _FORBIDDEN_COMMAND_TOKENS):
            return GateResult("offline_validation_commands", False, "reject", "command references forbidden live or consequential workflow surface")
    return GateResult("offline_validation_commands", True, "info", "offline validation commands are exact and local")


def _commands(row: dict[str, Any], packet: dict[str, Any]) -> tuple[tuple[str, ...], ...]:
    row_commands = row.get("offline_validation_commands") if row else None
    commands = row_commands if row_commands is not None else packet.get("offline_validation_commands", [])
    if not isinstance(commands, list):
        return ()
    normalized: list[tuple[str, ...]] = []
    for command in commands:
        if isinstance(command, list) and all(isinstance(part, str) and part for part in command):
            normalized.append(tuple(command))
    return tuple(normalized)


def _valid_citation(citation: Any) -> bool:
    if not isinstance(citation, dict):
        return False
    if citation.get("scope") not in {"public", "synthetic_fixture"}:
        return False
    return all(isinstance(citation.get(key), str) and citation.get(key) for key in ("citation_id", "source_id", "locator", "quote_hash"))


def _required_string(row: dict[str, Any], key: str) -> str:
    value = row.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"delta row missing required string field: {key}")
    return value


def _reject_forbidden_content(value: Any, path: str = "$", parent_key: str = "") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            lowered_key = key.lower()
            if lowered_key in _ACTIVE_MUTATION_KEYS and child:
                raise ValueError(f"active mutation flag is not allowed at {child_path}")
            if lowered_key.endswith("active_mutation_flags") and child:
                raise ValueError(f"active mutation flags are not allowed at {child_path}")
            _reject_forbidden_content(child, child_path, lowered_key)
        return
    if isinstance(value, list):
        for index, child in enumerate(value):
            _reject_forbidden_content(child, f"{path}[{index}]", parent_key)
        return
    if isinstance(value, str):
        if _PRIVATE_ARTIFACT_RE.search(value):
            raise ValueError(f"private/session/browser/raw/downloaded artifact is not allowed at {path}")
        if _LIVE_OR_DEVHUB_RE.search(value):
            raise ValueError(f"live crawl or DevHub claim is not allowed at {path}")
        if _GUARANTEE_RE.search(value):
            raise ValueError(f"legal or permitting guarantee is not allowed at {path}")
        if _OFFICIAL_COMPLETION_RE.search(value):
            raise ValueError(f"official-action completion claim is not allowed at {path}")
        if _ACTIVE_MUTATION_TEXT_RE.search(value):
            raise ValueError(f"active mutation language is not allowed at {path}")


def assert_packet_has_all_v2_gates(packet: dict[str, Any]) -> None:
    """Small validation helper for fixture tests."""

    declared = packet.get("gate_names")
    if not isinstance(declared, list):
        raise ValueError("packet must declare gate_names")
    missing = _REQUIRED_GATES - set(declared)
    if missing:
        raise ValueError("packet missing required gates: " + ", ".join(sorted(missing)))


def assert_recommendations_only(recommendations: Iterable[DeltaRecommendation]) -> None:
    """Ensure the evaluator only emits advisory recommendation states."""

    for recommendation in recommendations:
        if recommendation.recommendation not in _ALLOWED_RECOMMENDATIONS:
            raise ValueError("unexpected recommendation: " + recommendation.recommendation)
