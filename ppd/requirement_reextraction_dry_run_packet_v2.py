"""Fixture-first requirement re-extraction dry-run packet v2.

This module consumes stale-source re-extraction readiness packets and produces
synthetic requirement delta rows only. It does not crawl, fetch documents, write
registries, alter process models, or recompile guardrails.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from ppd.stale_source_reextraction_readiness_packet_v2 import (
    PACKET_VERSION as READINESS_PACKET_VERSION,
    assert_valid_stale_source_reextraction_readiness_packet_v2,
)


PACKET_VERSION = "requirement-reextraction-dry-run-packet-v2"
DELTA_STATUSES = ("unchanged", "added", "removed", "changed")
REQUIRED_VALIDATION_COMMANDS = (
    ("python3", "-m", "unittest", "ppd.tests.test_requirement_reextraction_dry_run_packet_v2"),
    ("python3", "ppd/daemon/ppd_daemon.py", "--self-test"),
)
PLACEHOLDER_FIELDS = (
    "requirement_placeholder_id",
    "citation_span_placeholder_id",
    "confidence_placeholder_id",
    "human_review_placeholder_id",
    "affected_process_model_placeholder_id",
    "affected_guardrail_placeholder_id",
)


class RequirementReextractionDryRunPacketV2Error(ValueError):
    """Raised when a requirement re-extraction dry-run packet is unsafe."""

    def __init__(self, issues: Sequence[str]) -> None:
        self.issues = tuple(issues)
        super().__init__("; ".join(self.issues))


def build_requirement_reextraction_dry_run_packet_v2(readiness_packet: Mapping[str, Any]) -> dict[str, Any]:
    """Build an ordered, placeholder-only dry-run packet from readiness input."""

    assert_valid_stale_source_reextraction_readiness_packet_v2(readiness_packet)
    candidate_rows = sorted(_mapping_list(readiness_packet.get("candidate_rows")), key=lambda row: int(row.get("order", 0)))

    requirement_placeholders: list[dict[str, Any]] = []
    citation_span_placeholders: list[dict[str, Any]] = []
    confidence_placeholders: list[dict[str, Any]] = []
    human_review_placeholders: list[dict[str, Any]] = []
    affected_process_model_placeholders: list[dict[str, Any]] = []
    affected_guardrail_placeholders: list[dict[str, Any]] = []
    delta_rows: list[dict[str, Any]] = []

    order = 1
    for candidate in candidate_rows:
        candidate_id = _required_text(candidate.get("candidate_id"), "candidate_id")
        source_id = _required_text(candidate.get("source_id"), "source_id")
        base = _token(candidate_id)
        for status in DELTA_STATUSES:
            row_id = f"delta-{base}-{status}"
            requirement_id = f"req-placeholder-{base}-{status}"
            citation_id = f"citation-placeholder-{base}-{status}"
            confidence_id = f"confidence-placeholder-{base}-{status}"
            review_id = f"human-review-placeholder-{base}-{status}"
            process_id = f"process-placeholder-{base}-{status}"
            guardrail_id = f"guardrail-placeholder-{base}-{status}"

            requirement_placeholders.append({"placeholder_id": requirement_id, "candidate_id": candidate_id, "delta_status": status, "placeholder": f"placeholder: synthetic {status} requirement text pending refreshed evidence and reviewer approval", "active_registry_mutation_allowed": False})
            citation_span_placeholders.append({"placeholder_id": citation_id, "candidate_id": candidate_id, "source_id": source_id, "delta_status": status, "placeholder": "placeholder: citation span pending approved refreshed source evidence", "live_fetch_allowed": False, "stored_page_body_allowed": False})
            confidence_placeholders.append({"placeholder_id": confidence_id, "candidate_id": candidate_id, "delta_status": status, "placeholder": "placeholder: confidence score pending reviewer disposition", "confidence_value": None, "confidence_status": "pending_human_review"})
            human_review_placeholders.append({"placeholder_id": review_id, "candidate_id": candidate_id, "delta_status": status, "placeholder": "placeholder: human review disposition pending", "human_review_required": True, "review_status": "pending", "mutation_allowed": False})
            affected_process_model_placeholders.append({"placeholder_id": process_id, "candidate_id": candidate_id, "delta_status": status, "placeholder": "placeholder: affected process model pending reviewer mapping", "process_model_mutation_allowed": False})
            affected_guardrail_placeholders.append({"placeholder_id": guardrail_id, "candidate_id": candidate_id, "delta_status": status, "placeholder": "placeholder: affected guardrail bundle pending approved requirement delta", "guardrail_recompile_allowed": False})
            delta_rows.append({"order": order, "delta_row_id": row_id, "candidate_id": candidate_id, "source_id": source_id, "delta_status": status, "requirement_placeholder_id": requirement_id, "citation_span_placeholder_id": citation_id, "confidence_placeholder_id": confidence_id, "human_review_placeholder_id": review_id, "affected_process_model_placeholder_id": process_id, "affected_guardrail_placeholder_id": guardrail_id})
            order += 1

    packet = {
        "version": PACKET_VERSION,
        "packet_id": "fixture-requirement-reextraction-dry-run-v2",
        "mode": "fixture_first_no_network",
        "generated_from_readiness_packet_id": _required_text(readiness_packet.get("packet_id"), "packet_id"),
        "source_readiness_packet_version": READINESS_PACKET_VERSION,
        "synthetic_requirement_delta_rows": delta_rows,
        "requirement_placeholders": requirement_placeholders,
        "citation_span_placeholders": citation_span_placeholders,
        "confidence_placeholders": confidence_placeholders,
        "human_review_placeholders": human_review_placeholders,
        "affected_process_model_placeholders": affected_process_model_placeholders,
        "affected_guardrail_placeholders": affected_guardrail_placeholders,
        "attestations": {
            "fixture_first": True,
            "no_live_crawling": True,
            "no_pdf_downloads": True,
            "no_stored_page_bodies": True,
            "no_active_requirement_registry_mutation": True,
            "no_process_model_changes": True,
            "no_guardrail_recompile": True,
        },
        "validation_commands": [list(command) for command in REQUIRED_VALIDATION_COMMANDS],
    }
    assert_valid_requirement_reextraction_dry_run_packet_v2(packet)
    return packet


def validate_requirement_reextraction_dry_run_packet_v2(packet: Mapping[str, Any]) -> list[str]:
    """Return deterministic rejection reasons for an unsafe dry-run packet."""

    issues: list[str] = []
    if packet.get("version") != PACKET_VERSION:
        issues.append("version must be " + PACKET_VERSION)
    if packet.get("source_readiness_packet_version") != READINESS_PACKET_VERSION:
        issues.append("source_readiness_packet_version must be " + READINESS_PACKET_VERSION)

    rows = _mapping_list(packet.get("synthetic_requirement_delta_rows"))
    if not rows:
        issues.append("synthetic_requirement_delta_rows must be non-empty")
    _validate_delta_rows(issues, rows, packet)
    _validate_requirement_placeholders(issues, _mapping_list(packet.get("requirement_placeholders")))
    _validate_citation_span_placeholders(issues, _mapping_list(packet.get("citation_span_placeholders")))
    _validate_confidence_placeholders(issues, _mapping_list(packet.get("confidence_placeholders")))
    _validate_human_review_placeholders(issues, _mapping_list(packet.get("human_review_placeholders")))
    _validate_process_placeholders(issues, _mapping_list(packet.get("affected_process_model_placeholders")))
    _validate_guardrail_placeholders(issues, _mapping_list(packet.get("affected_guardrail_placeholders")))
    _validate_attestations(issues, packet.get("attestations"))
    _validate_commands(issues, packet.get("validation_commands"))
    return sorted(set(issues))


def assert_valid_requirement_reextraction_dry_run_packet_v2(packet: Mapping[str, Any]) -> None:
    """Raise when a requirement re-extraction dry-run packet is unsafe."""

    issues = validate_requirement_reextraction_dry_run_packet_v2(packet)
    if issues:
        raise RequirementReextractionDryRunPacketV2Error(issues)


def _validate_delta_rows(issues: list[str], rows: Sequence[Mapping[str, Any]], packet: Mapping[str, Any]) -> None:
    orders = [row.get("order") for row in rows]
    if any(not isinstance(order, int) for order in orders):
        issues.append("synthetic_requirement_delta_rows order values must be integers")
    elif sorted(orders) != list(range(1, len(rows) + 1)):
        issues.append("synthetic_requirement_delta_rows order must be contiguous starting at 1")

    statuses = {row.get("delta_status") for row in rows}
    for status in DELTA_STATUSES:
        if status not in statuses:
            issues.append("missing synthetic requirement delta status: " + status)

    indexes = {
        "requirement_placeholder_id": _ids(packet.get("requirement_placeholders")),
        "citation_span_placeholder_id": _ids(packet.get("citation_span_placeholders")),
        "confidence_placeholder_id": _ids(packet.get("confidence_placeholders")),
        "human_review_placeholder_id": _ids(packet.get("human_review_placeholders")),
        "affected_process_model_placeholder_id": _ids(packet.get("affected_process_model_placeholders")),
        "affected_guardrail_placeholder_id": _ids(packet.get("affected_guardrail_placeholders")),
    }
    seen: set[str] = set()
    for row in rows:
        row_id = _text(row.get("delta_row_id"))
        if not row_id:
            issues.append("synthetic requirement delta row missing delta_row_id")
        elif row_id in seen:
            issues.append("duplicate synthetic requirement delta row " + row_id)
        else:
            seen.add(row_id)
        if row.get("delta_status") not in DELTA_STATUSES:
            issues.append(f"synthetic requirement delta row {row_id} has invalid delta_status")
        if not _text(row.get("candidate_id")) or not _text(row.get("source_id")):
            issues.append(f"synthetic requirement delta row {row_id} must include candidate_id and source_id")
        for field in PLACEHOLDER_FIELDS:
            ref = _text(row.get(field))
            if not ref:
                issues.append(f"synthetic requirement delta row {row_id} missing {field}")
            elif ref not in indexes[field]:
                issues.append(f"synthetic requirement delta row {row_id} references unknown {field}: {ref}")


def _validate_requirement_placeholders(issues: list[str], placeholders: Sequence[Mapping[str, Any]]) -> None:
    if not placeholders:
        issues.append("requirement_placeholders must be non-empty")
    for placeholder in placeholders:
        placeholder_id = _text(placeholder.get("placeholder_id"))
        if placeholder.get("delta_status") not in DELTA_STATUSES:
            issues.append(f"requirement placeholder {placeholder_id} has invalid delta_status")
        if not _text(placeholder.get("placeholder")).startswith("placeholder:"):
            issues.append(f"requirement placeholder {placeholder_id} must stay placeholder-only")
        if placeholder.get("active_registry_mutation_allowed") is not False:
            issues.append(f"requirement placeholder {placeholder_id} must not allow active registry mutation")


def _validate_citation_span_placeholders(issues: list[str], placeholders: Sequence[Mapping[str, Any]]) -> None:
    if not placeholders:
        issues.append("citation_span_placeholders must be non-empty")
    for placeholder in placeholders:
        placeholder_id = _text(placeholder.get("placeholder_id"))
        if not _text(placeholder.get("placeholder")).startswith("placeholder:"):
            issues.append(f"citation-span placeholder {placeholder_id} must stay placeholder-only")
        if placeholder.get("live_fetch_allowed") is not False:
            issues.append(f"citation-span placeholder {placeholder_id} must disable live fetch")
        if placeholder.get("stored_page_body_allowed") is not False:
            issues.append(f"citation-span placeholder {placeholder_id} must disable stored page bodies")


def _validate_confidence_placeholders(issues: list[str], placeholders: Sequence[Mapping[str, Any]]) -> None:
    if not placeholders:
        issues.append("confidence_placeholders must be non-empty")
    for placeholder in placeholders:
        placeholder_id = _text(placeholder.get("placeholder_id"))
        if not _text(placeholder.get("placeholder")).startswith("placeholder:"):
            issues.append(f"confidence placeholder {placeholder_id} must stay placeholder-only")
        if placeholder.get("confidence_value") is not None:
            issues.append(f"confidence placeholder {placeholder_id} must not assign confidence before review")
        if placeholder.get("confidence_status") != "pending_human_review":
            issues.append(f"confidence placeholder {placeholder_id} must remain pending_human_review")


def _validate_human_review_placeholders(issues: list[str], placeholders: Sequence[Mapping[str, Any]]) -> None:
    if not placeholders:
        issues.append("human_review_placeholders must be non-empty")
    for placeholder in placeholders:
        placeholder_id = _text(placeholder.get("placeholder_id"))
        if placeholder.get("human_review_required") is not True:
            issues.append(f"human-review placeholder {placeholder_id} must require human review")
        if placeholder.get("review_status") != "pending":
            issues.append(f"human-review placeholder {placeholder_id} must remain pending")
        if placeholder.get("mutation_allowed") is not False:
            issues.append(f"human-review placeholder {placeholder_id} must not allow mutation")


def _validate_process_placeholders(issues: list[str], placeholders: Sequence[Mapping[str, Any]]) -> None:
    if not placeholders:
        issues.append("affected_process_model_placeholders must be non-empty")
    for placeholder in placeholders:
        placeholder_id = _text(placeholder.get("placeholder_id"))
        if not _text(placeholder.get("placeholder")).startswith("placeholder:"):
            issues.append(f"affected process-model placeholder {placeholder_id} must stay placeholder-only")
        if placeholder.get("process_model_mutation_allowed") is not False:
            issues.append(f"affected process-model placeholder {placeholder_id} must not allow process model mutation")


def _validate_guardrail_placeholders(issues: list[str], placeholders: Sequence[Mapping[str, Any]]) -> None:
    if not placeholders:
        issues.append("affected_guardrail_placeholders must be non-empty")
    for placeholder in placeholders:
        placeholder_id = _text(placeholder.get("placeholder_id"))
        if not _text(placeholder.get("placeholder")).startswith("placeholder:"):
            issues.append(f"affected guardrail placeholder {placeholder_id} must stay placeholder-only")
        if placeholder.get("guardrail_recompile_allowed") is not False:
            issues.append(f"affected guardrail placeholder {placeholder_id} must not allow guardrail recompilation")


def _validate_attestations(issues: list[str], value: Any) -> None:
    if not isinstance(value, Mapping):
        issues.append("attestations must be a mapping")
        return
    for key in ("fixture_first", "no_live_crawling", "no_pdf_downloads", "no_stored_page_bodies", "no_active_requirement_registry_mutation", "no_process_model_changes", "no_guardrail_recompile"):
        if value.get(key) is not True:
            issues.append(f"attestation must be true: {key}")


def _validate_commands(issues: list[str], value: Any) -> None:
    commands = _command_tuples(value)
    for required in REQUIRED_VALIDATION_COMMANDS:
        if required not in commands:
            issues.append("missing validation command: " + " ".join(required))
    for command in commands:
        joined = " ".join(command).lower()
        if any(term in joined for term in ("curl", "wget", "playwright", "browser", "devhub.portlandoregon.gov")):
            issues.append("validation commands must remain offline and fixture-first")


def _mapping_list(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _ids(value: Any) -> set[str]:
    return {_text(item.get("placeholder_id")) for item in _mapping_list(value) if _text(item.get("placeholder_id"))}


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


def _required_text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(name + " must be a non-empty string")
    return value


def _text(value: Any) -> str:
    return value if isinstance(value, str) else ""


def _token(value: str) -> str:
    token = "".join(char.lower() if char.isalnum() else "-" for char in value).strip("-")
    while "--" in token:
        token = token.replace("--", "-")
    return token or "placeholder"
