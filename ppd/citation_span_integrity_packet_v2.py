"""Fixture-first citation span integrity packet v2 for PP&D agent-facing outputs.

This module validates committed synthetic fixtures only. It does not crawl live
sources, download documents, read private DevHub data, or mutate active source,
document, requirement, process-model, guardrail, prompt, contract, DevHub, or
release state.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re
from typing import Any, Mapping, Sequence


PACKET_TYPE = "fixture_first_citation_span_integrity_packet_v2"
PACKET_MODE = "offline_fixture_validation_only"
PACKET_VERSION = "2"

REQUIRED_SAMPLE_TYPES = (
    "synthetic_normalized_html",
    "synthetic_normalized_pdf",
    "synthetic_normalized_form",
    "synthetic_process_model",
    "synthetic_requirement",
    "synthetic_guardrail",
)

REQUIRED_ATTESTATIONS = (
    "fixture_first_inputs_only",
    "synthetic_records_only",
    "no_live_crawl",
    "no_document_download",
    "no_private_data",
    "no_active_source_mutation",
    "no_active_document_mutation",
    "no_active_requirement_mutation",
    "no_active_process_model_mutation",
    "no_active_guardrail_mutation",
    "no_active_prompt_mutation",
    "no_contract_mutation",
    "no_devhub_surface_mutation",
    "no_release_state_mutation",
    "no_legal_or_permitting_guarantees",
)

REQUIRED_MUTATION_FLAGS = (
    "active_source_mutation",
    "active_document_mutation",
    "active_requirement_mutation",
    "active_process_model_mutation",
    "active_guardrail_mutation",
    "active_prompt_mutation",
    "active_contract_mutation",
    "active_devhub_surface_mutation",
    "active_release_state_mutation",
)

ALLOWED_FRESHNESS_STATUSES = {
    "fresh_fixture",
    "synthetic_current",
    "review_required_fixture",
    "stale_fixture_pending_review",
}

OFFLINE_VALIDATION_COMMANDS = (
    ("python3", "-m", "py_compile", "ppd/citation_span_integrity_packet_v2.py", "ppd/tests/test_citation_span_integrity_packet_v2.py"),
    ("python3", "-m", "pytest", "ppd/tests/test_citation_span_integrity_packet_v2.py"),
    ("python3", "ppd/daemon/ppd_daemon.py", "--self-test"),
)

_STABLE_EVIDENCE_ID_RE = re.compile(r"^synthetic-source-evidence:[a-z0-9][a-z0-9_.:-]*$")
_STABLE_SPAN_ID_RE = re.compile(r"^citation-span:[a-z0-9][a-z0-9_.:-]*$")
_STABLE_TRACE_ID_RE = re.compile(r"^(requirement-to-guardrail-trace|refusal-to-source-trace):[a-z0-9][a-z0-9_.:-]*$")
_PRIVATE_OR_LIVE_KEY_RE = re.compile(
    r"(auth[_-]?state|cookie|credential|password|secret|token|\.har\b|trace\.zip|screenshot|browser[_-]?state|session[_-]?storage|local[_-]?storage|raw[_-]?crawl|raw[_-]?download|downloaded[_-]?document|downloaded[_-]?artifact|private[_-]?artifact|devhub[_-]?session)",
    re.IGNORECASE,
)
_PRIVATE_OR_LIVE_VALUE_RE = re.compile(
    r"(auth[_-]?state|cookie|credential|password|secret|token|\.har\b|trace\.zip|screenshot|browser[_-]?state|session[_-]?storage|local[_-]?storage|raw[_-]?crawl|raw[_-]?download|downloaded[_-]?document|downloaded[_-]?artifact|private[_-]?artifact|/home/[^\s]+/(?:Desktop|Documents|Downloads)|C:\\\\Users\\\\|live[_ -]?crawl|live[_ -]?scrape|devhub[_ -]?session|authenticated[_ -]?devhub|observed[_ -]?devhub|devhub[_ -]?verified|current[_ -]?devhub[_ -]?surface)",
    re.IGNORECASE,
)
_GUARANTEE_RE = re.compile(
    r"(legal advice|legal determination|guarantee(?:d|s)?\b|permit(?:ting)? approval is certain|will be approved|will be issued|must be approved|official approval assured|approval assured|issuance assured)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class CitationSpanPacketFinding:
    """A deterministic validation finding for citation span integrity packets."""

    code: str
    path: str
    message: str


@dataclass(frozen=True)
class CitationSpanPacketValidationResult:
    """Validation result for a fixture-first citation span integrity packet."""

    valid: bool
    findings: tuple[CitationSpanPacketFinding, ...]

    def codes(self) -> tuple[str, ...]:
        return tuple(finding.code for finding in self.findings)


class CitationSpanPacketError(ValueError):
    """Raised when a citation span integrity packet fails validation."""

    def __init__(self, findings: Sequence[CitationSpanPacketFinding]) -> None:
        self.findings = tuple(findings)
        detail = "; ".join(f"{item.code} at {item.path}: {item.message}" for item in self.findings)
        super().__init__("invalid citation span integrity packet v2: " + detail)


def build_citation_span_integrity_packet_v2(fixture: Mapping[str, Any], *, generated_at: str) -> dict[str, Any]:
    """Build a deterministic review packet from a committed synthetic fixture."""

    if not isinstance(fixture, Mapping):
        raise TypeError("fixture must be a mapping")

    packet_body = {
        "packet_type": PACKET_TYPE,
        "packet_version": PACKET_VERSION,
        "packet_mode": PACKET_MODE,
        "generated_at": generated_at,
        "fixture_id": _string(fixture.get("fixture_id")) or "citation-span-integrity-fixture-v2",
        "sample_records": _list(fixture.get("sample_records")),
        "source_evidence": _list(fixture.get("source_evidence")),
        "citation_spans": _list(fixture.get("citation_spans")),
        "agent_facing_requirements": _list(fixture.get("agent_facing_requirements")),
        "agent_facing_refusals": _list(fixture.get("agent_facing_refusals")),
        "requirement_to_guardrail_traces": _list(fixture.get("requirement_to_guardrail_traces")),
        "refusal_to_source_traces": _list(fixture.get("refusal_to_source_traces")),
        "reviewer_disposition_placeholders": _list(fixture.get("reviewer_disposition_placeholders")),
        "freshness_statuses": sorted(ALLOWED_FRESHNESS_STATUSES),
        "offline_validation_commands": [list(command) for command in OFFLINE_VALIDATION_COMMANDS],
        "attestations": {key: True for key in REQUIRED_ATTESTATIONS},
        "active_mutation_flags": {key: False for key in REQUIRED_MUTATION_FLAGS},
    }
    packet_body["packet_id"] = "citation-span-integrity-v2-" + _stable_hash(packet_body)

    assert_valid_citation_span_integrity_packet_v2(packet_body)
    return packet_body


def validate_citation_span_integrity_packet_v2(packet: Mapping[str, Any]) -> CitationSpanPacketValidationResult:
    """Validate a fixture-first citation span integrity packet v2."""

    findings: list[CitationSpanPacketFinding] = []
    if not isinstance(packet, Mapping):
        return CitationSpanPacketValidationResult(False, (CitationSpanPacketFinding("packet_not_mapping", "$", "packet must be an object"),))

    if packet.get("packet_type") != PACKET_TYPE:
        findings.append(CitationSpanPacketFinding("wrong_packet_type", "packet_type", f"packet_type must be {PACKET_TYPE}"))
    if packet.get("packet_mode") != PACKET_MODE:
        findings.append(CitationSpanPacketFinding("wrong_packet_mode", "packet_mode", f"packet_mode must be {PACKET_MODE}"))
    if packet.get("packet_version") != PACKET_VERSION:
        findings.append(CitationSpanPacketFinding("wrong_packet_version", "packet_version", f"packet_version must be {PACKET_VERSION}"))

    _validate_no_private_live_or_guarantee_strings(packet, findings)
    _validate_attestations(packet, findings)
    _validate_mutation_flags(packet, findings)
    _validate_offline_commands(packet, findings)

    sample_types = _sample_types(packet.get("sample_records"), findings)
    for required_type in REQUIRED_SAMPLE_TYPES:
        if required_type not in sample_types:
            findings.append(CitationSpanPacketFinding("missing_sample_type", "sample_records", f"missing required sample type {required_type}"))

    evidence_index = _evidence_index(packet.get("source_evidence"), findings)
    span_index = _span_index(packet.get("citation_spans"), evidence_index, findings)
    reviewer_dispositions = _reviewer_dispositions(packet.get("reviewer_disposition_placeholders"), findings)
    requirement_trace_index = _requirement_trace_index(packet.get("requirement_to_guardrail_traces"), evidence_index, findings)
    refusal_trace_index = _refusal_trace_index(packet.get("refusal_to_source_traces"), evidence_index, findings)

    _validate_agent_facing_rows(
        packet.get("agent_facing_requirements"),
        "agent_facing_requirements",
        evidence_index,
        span_index,
        reviewer_dispositions,
        requirement_trace_index,
        findings,
    )
    _validate_agent_facing_rows(
        packet.get("agent_facing_refusals"),
        "agent_facing_refusals",
        evidence_index,
        span_index,
        reviewer_dispositions,
        refusal_trace_index,
        findings,
    )

    return CitationSpanPacketValidationResult(not findings, tuple(findings))


def assert_valid_citation_span_integrity_packet_v2(packet: Mapping[str, Any]) -> None:
    """Raise a stable error if a citation span integrity packet v2 is invalid."""

    result = validate_citation_span_integrity_packet_v2(packet)
    if not result.valid:
        raise CitationSpanPacketError(result.findings)


def _list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, list) else []


def _string(value: Any) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _stable_hash(value: Mapping[str, Any]) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16]


def _sample_types(raw_records: Any, findings: list[CitationSpanPacketFinding]) -> set[str]:
    records = _list(raw_records)
    if not records:
        findings.append(CitationSpanPacketFinding("missing_sample_records", "sample_records", "sample_records must be a non-empty list"))
        return set()

    sample_types: set[str] = set()
    for index, record in enumerate(records):
        path = f"sample_records[{index}]"
        if not isinstance(record, Mapping):
            findings.append(CitationSpanPacketFinding("invalid_sample_record", path, "sample record must be an object"))
            continue
        record_type = _string(record.get("record_type"))
        if not record_type:
            findings.append(CitationSpanPacketFinding("missing_sample_record_type", f"{path}.record_type", "record_type is required"))
            continue
        sample_types.add(record_type)
        if record.get("synthetic") is not True:
            findings.append(CitationSpanPacketFinding("sample_not_synthetic", f"{path}.synthetic", "sample record must be synthetic"))
        if record.get("active_state") is True:
            findings.append(CitationSpanPacketFinding("active_sample_record", f"{path}.active_state", "sample record must not represent active state"))
    return sample_types


def _evidence_index(raw_evidence: Any, findings: list[CitationSpanPacketFinding]) -> dict[str, Mapping[str, Any]]:
    evidence_items = _list(raw_evidence)
    if not evidence_items:
        findings.append(CitationSpanPacketFinding("missing_source_evidence", "source_evidence", "source_evidence must be a non-empty list"))
        return {}

    evidence_index: dict[str, Mapping[str, Any]] = {}
    for index, evidence in enumerate(evidence_items):
        path = f"source_evidence[{index}]"
        if not isinstance(evidence, Mapping):
            findings.append(CitationSpanPacketFinding("invalid_source_evidence", path, "source evidence must be an object"))
            continue
        evidence_id = _string(evidence.get("evidence_id"))
        if not evidence_id or not _STABLE_EVIDENCE_ID_RE.match(evidence_id):
            findings.append(CitationSpanPacketFinding("missing_source_evidence_id", f"{path}.evidence_id", "evidence_id must use the synthetic-source-evidence namespace"))
            continue
        if evidence_id in evidence_index:
            findings.append(CitationSpanPacketFinding("duplicate_source_evidence_id", f"{path}.evidence_id", "evidence_id must be unique"))
            continue
        if evidence.get("synthetic") is not True:
            findings.append(CitationSpanPacketFinding("source_evidence_not_synthetic", f"{path}.synthetic", "source evidence must be synthetic"))
        if evidence.get("privacy_classification") != "commit_safe_public_fixture":
            findings.append(CitationSpanPacketFinding("unsafe_evidence_privacy", f"{path}.privacy_classification", "source evidence must be commit_safe_public_fixture"))
        freshness = _string(evidence.get("freshness_status"))
        if freshness not in ALLOWED_FRESHNESS_STATUSES:
            findings.append(CitationSpanPacketFinding("missing_freshness_status", f"{path}.freshness_status", "source evidence freshness_status must be an allowed fixture status"))
        evidence_index[evidence_id] = evidence
    return evidence_index


def _span_index(
    raw_spans: Any,
    evidence_index: Mapping[str, Mapping[str, Any]],
    findings: list[CitationSpanPacketFinding],
) -> dict[str, Mapping[str, Any]]:
    spans = _list(raw_spans)
    if not spans:
        findings.append(CitationSpanPacketFinding("missing_citation_span_placeholders", "citation_spans", "citation_spans must be a non-empty list"))
        return {}

    span_index: dict[str, Mapping[str, Any]] = {}
    for index, span in enumerate(spans):
        path = f"citation_spans[{index}]"
        if not isinstance(span, Mapping):
            findings.append(CitationSpanPacketFinding("invalid_citation_span", path, "citation span must be an object"))
            continue
        span_id = _string(span.get("span_id"))
        evidence_id = _string(span.get("evidence_id"))
        if not span_id or not _STABLE_SPAN_ID_RE.match(span_id):
            findings.append(CitationSpanPacketFinding("missing_citation_span_placeholder", f"{path}.span_id", "span_id must use the citation-span namespace"))
            continue
        if span_id in span_index:
            findings.append(CitationSpanPacketFinding("duplicate_span_id", f"{path}.span_id", "span_id must be unique"))
            continue
        if not evidence_id or evidence_id not in evidence_index:
            findings.append(CitationSpanPacketFinding("unknown_span_evidence_id", f"{path}.evidence_id", "span evidence_id must reference source_evidence"))
        if span.get("placeholder") is not True:
            findings.append(CitationSpanPacketFinding("span_not_placeholder", f"{path}.placeholder", "citation span must be marked as a placeholder"))
        disposition = _string(span.get("reviewer_disposition_placeholder"))
        if not disposition:
            findings.append(CitationSpanPacketFinding("missing_span_reviewer_disposition", f"{path}.reviewer_disposition_placeholder", "citation span requires a reviewer disposition placeholder"))
        freshness = _string(span.get("freshness_status"))
        if freshness not in ALLOWED_FRESHNESS_STATUSES:
            findings.append(CitationSpanPacketFinding("missing_span_freshness_status", f"{path}.freshness_status", "citation span requires an allowed freshness_status"))
        span_index[span_id] = span
    return span_index


def _reviewer_dispositions(raw_dispositions: Any, findings: list[CitationSpanPacketFinding]) -> set[str]:
    rows = _list(raw_dispositions)
    if not rows:
        findings.append(CitationSpanPacketFinding("missing_reviewer_disposition_placeholders", "reviewer_disposition_placeholders", "reviewer disposition placeholders are required"))
        return set()
    dispositions: set[str] = set()
    for index, row in enumerate(rows):
        path = f"reviewer_disposition_placeholders[{index}]"
        if not isinstance(row, Mapping):
            findings.append(CitationSpanPacketFinding("invalid_reviewer_disposition", path, "reviewer disposition row must be an object"))
            continue
        disposition_id = _string(row.get("disposition_id"))
        if not disposition_id:
            findings.append(CitationSpanPacketFinding("missing_reviewer_disposition_id", f"{path}.disposition_id", "disposition_id is required"))
            continue
        dispositions.add(disposition_id)
        if not _string(row.get("status")):
            findings.append(CitationSpanPacketFinding("missing_reviewer_disposition_status", f"{path}.status", "reviewer disposition status is required"))
    return dispositions


def _requirement_trace_index(
    raw_traces: Any,
    evidence_index: Mapping[str, Mapping[str, Any]],
    findings: list[CitationSpanPacketFinding],
) -> dict[str, Mapping[str, Any]]:
    return _trace_index(
        raw_traces,
        "requirement_to_guardrail_traces",
        "missing_requirement_to_guardrail_traces",
        "requirement-to-guardrail-trace",
        "requirement_id",
        "guardrail_ids",
        evidence_index,
        findings,
    )


def _refusal_trace_index(
    raw_traces: Any,
    evidence_index: Mapping[str, Mapping[str, Any]],
    findings: list[CitationSpanPacketFinding],
) -> dict[str, Mapping[str, Any]]:
    return _trace_index(
        raw_traces,
        "refusal_to_source_traces",
        "missing_refusal_to_source_traces",
        "refusal-to-source-trace",
        "refusal_id",
        "refused_action_predicate_ids",
        evidence_index,
        findings,
    )


def _trace_index(
    raw_traces: Any,
    section: str,
    missing_code: str,
    trace_prefix: str,
    row_id_field: str,
    required_list_field: str,
    evidence_index: Mapping[str, Mapping[str, Any]],
    findings: list[CitationSpanPacketFinding],
) -> dict[str, Mapping[str, Any]]:
    traces = _list(raw_traces)
    if not traces:
        findings.append(CitationSpanPacketFinding(missing_code, section, f"{section} must be a non-empty list"))
        return {}

    trace_index: dict[str, Mapping[str, Any]] = {}
    for index, trace in enumerate(traces):
        path = f"{section}[{index}]"
        if not isinstance(trace, Mapping):
            findings.append(CitationSpanPacketFinding("invalid_trace", path, "trace row must be an object"))
            continue
        trace_id = _string(trace.get("trace_id"))
        if not trace_id or not _STABLE_TRACE_ID_RE.match(trace_id) or not trace_id.startswith(trace_prefix + ":"):
            findings.append(CitationSpanPacketFinding("missing_trace_id", f"{path}.trace_id", f"trace_id must use the {trace_prefix} namespace"))
            continue
        if trace_id in trace_index:
            findings.append(CitationSpanPacketFinding("duplicate_trace_id", f"{path}.trace_id", "trace_id must be unique"))
            continue
        if not _string(trace.get(row_id_field)):
            findings.append(CitationSpanPacketFinding("missing_trace_subject", f"{path}.{row_id_field}", f"{row_id_field} is required"))
        if not _non_empty_string_list(trace.get(required_list_field)):
            findings.append(CitationSpanPacketFinding("missing_trace_target", f"{path}.{required_list_field}", f"{required_list_field} must be a non-empty string list"))
        _validate_row_evidence(trace.get("source_evidence_ids"), f"{path}.source_evidence_ids", evidence_index, findings)
        freshness = _string(trace.get("freshness_status"))
        if freshness not in ALLOWED_FRESHNESS_STATUSES:
            findings.append(CitationSpanPacketFinding("missing_trace_freshness_status", f"{path}.freshness_status", "trace must carry an allowed freshness_status"))
        trace_index[trace_id] = trace
    return trace_index


def _validate_agent_facing_rows(
    raw_rows: Any,
    section: str,
    evidence_index: Mapping[str, Mapping[str, Any]],
    span_index: Mapping[str, Mapping[str, Any]],
    reviewer_dispositions: set[str],
    trace_index: Mapping[str, Mapping[str, Any]],
    findings: list[CitationSpanPacketFinding],
) -> None:
    rows = _list(raw_rows)
    if not rows:
        findings.append(CitationSpanPacketFinding("missing_agent_facing_rows", section, f"{section} must be a non-empty list"))
        return

    trace_field = "guardrail_trace_ids" if section == "agent_facing_requirements" else "source_trace_ids"
    missing_trace_code = "missing_requirement_to_guardrail_trace" if section == "agent_facing_requirements" else "missing_refusal_to_source_trace"

    for index, row in enumerate(rows):
        path = f"{section}[{index}]"
        if not isinstance(row, Mapping):
            findings.append(CitationSpanPacketFinding("invalid_agent_facing_row", path, "agent-facing row must be an object"))
            continue
        row_id = _string(row.get("requirement_id") or row.get("refusal_id") or row.get("id"))
        if not row_id:
            findings.append(CitationSpanPacketFinding("missing_agent_facing_id", path, "agent-facing row requires an id"))
        _validate_row_evidence(row.get("source_evidence_ids"), f"{path}.source_evidence_ids", evidence_index, findings)
        _validate_row_spans(row.get("citation_span_placeholders"), f"{path}.citation_span_placeholders", span_index, findings)
        _validate_row_traces(row.get(trace_field), f"{path}.{trace_field}", trace_index, missing_trace_code, findings)
        freshness = _string(row.get("freshness_status"))
        if freshness not in ALLOWED_FRESHNESS_STATUSES:
            findings.append(CitationSpanPacketFinding("missing_agent_facing_freshness_status", f"{path}.freshness_status", "agent-facing row must carry an allowed freshness_status"))
        disposition = _string(row.get("reviewer_disposition_placeholder"))
        if not disposition or disposition not in reviewer_dispositions:
            findings.append(CitationSpanPacketFinding("missing_agent_facing_reviewer_disposition", f"{path}.reviewer_disposition_placeholder", "agent-facing row must reference a reviewer disposition placeholder"))


def _validate_row_evidence(
    raw_ids: Any,
    path: str,
    evidence_index: Mapping[str, Mapping[str, Any]],
    findings: list[CitationSpanPacketFinding],
) -> None:
    ids = _non_empty_string_list(raw_ids)
    if not ids:
        findings.append(CitationSpanPacketFinding("missing_agent_facing_source_evidence", path, "at least one source_evidence_id is required"))
        return
    for evidence_id in ids:
        if evidence_id not in evidence_index:
            findings.append(CitationSpanPacketFinding("unknown_agent_facing_source_evidence", path, f"unknown source_evidence_id {evidence_id}"))


def _validate_row_spans(
    raw_ids: Any,
    path: str,
    span_index: Mapping[str, Mapping[str, Any]],
    findings: list[CitationSpanPacketFinding],
) -> None:
    ids = _non_empty_string_list(raw_ids)
    if not ids:
        findings.append(CitationSpanPacketFinding("missing_agent_facing_citation_span", path, "at least one citation span placeholder is required"))
        return
    for span_id in ids:
        if span_id not in span_index:
            findings.append(CitationSpanPacketFinding("unknown_agent_facing_citation_span", path, f"unknown citation span placeholder {span_id}"))


def _validate_row_traces(
    raw_ids: Any,
    path: str,
    trace_index: Mapping[str, Mapping[str, Any]],
    missing_code: str,
    findings: list[CitationSpanPacketFinding],
) -> None:
    ids = _non_empty_string_list(raw_ids)
    if not ids:
        findings.append(CitationSpanPacketFinding(missing_code, path, "at least one trace id is required"))
        return
    for trace_id in ids:
        if trace_id not in trace_index:
            findings.append(CitationSpanPacketFinding("unknown_agent_facing_trace", path, f"unknown trace id {trace_id}"))


def _non_empty_string_list(value: Any) -> list[str]:
    return [item.strip() for item in _list(value) if isinstance(item, str) and item.strip()]


def _validate_attestations(packet: Mapping[str, Any], findings: list[CitationSpanPacketFinding]) -> None:
    attestations = packet.get("attestations")
    if not isinstance(attestations, Mapping):
        findings.append(CitationSpanPacketFinding("missing_attestations", "attestations", "attestations must be an object"))
        return
    for key in REQUIRED_ATTESTATIONS:
        if attestations.get(key) is not True:
            findings.append(CitationSpanPacketFinding("missing_required_attestation", f"attestations.{key}", "required attestation must be true"))


def _validate_mutation_flags(packet: Mapping[str, Any], findings: list[CitationSpanPacketFinding]) -> None:
    flags = packet.get("active_mutation_flags")
    if not isinstance(flags, Mapping):
        findings.append(CitationSpanPacketFinding("missing_active_mutation_flags", "active_mutation_flags", "active_mutation_flags must be an object"))
        return
    for key in REQUIRED_MUTATION_FLAGS:
        if flags.get(key) is not False:
            findings.append(CitationSpanPacketFinding("active_mutation_flag_enabled", f"active_mutation_flags.{key}", "active mutation flag must be false"))


def _validate_offline_commands(packet: Mapping[str, Any], findings: list[CitationSpanPacketFinding]) -> None:
    commands = packet.get("offline_validation_commands")
    expected = [list(command) for command in OFFLINE_VALIDATION_COMMANDS]
    if commands != expected:
        findings.append(CitationSpanPacketFinding("unexpected_validation_commands", "offline_validation_commands", "offline validation commands must match the exact fixture-first command list"))


def _validate_no_private_live_or_guarantee_strings(value: Any, findings: list[CitationSpanPacketFinding], path: str = "$") -> None:
    if isinstance(value, str):
        if _PRIVATE_OR_LIVE_VALUE_RE.search(value):
            findings.append(CitationSpanPacketFinding("private_or_live_artifact_reference", path, "packet must not reference private, session, browser, raw, downloaded, live crawl, or DevHub claim artifacts"))
        if _GUARANTEE_RE.search(value):
            findings.append(CitationSpanPacketFinding("legal_or_permitting_guarantee", path, "packet must not include legal or permitting guarantees"))
    elif isinstance(value, Mapping):
        for key, item in value.items():
            key_text = str(key)
            if _PRIVATE_OR_LIVE_KEY_RE.search(key_text):
                findings.append(CitationSpanPacketFinding("private_or_live_artifact_reference", f"{path}.{key_text}", "packet key must not reference private, session, browser, raw, or downloaded artifacts"))
            _validate_no_private_live_or_guarantee_strings(item, findings, f"{path}.{key_text}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _validate_no_private_live_or_guarantee_strings(item, findings, f"{path}[{index}]")


__all__ = [
    "ALLOWED_FRESHNESS_STATUSES",
    "OFFLINE_VALIDATION_COMMANDS",
    "PACKET_MODE",
    "PACKET_TYPE",
    "PACKET_VERSION",
    "CitationSpanPacketError",
    "CitationSpanPacketFinding",
    "CitationSpanPacketValidationResult",
    "assert_valid_citation_span_integrity_packet_v2",
    "build_citation_span_integrity_packet_v2",
    "validate_citation_span_integrity_packet_v2",
]
