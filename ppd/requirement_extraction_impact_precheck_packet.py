"""Fixture-first requirement extraction impact precheck packets.

This module assembles offline metadata for reviewer-owned requirement extraction
rerun scoping. It consumes committed packet fixtures only and intentionally does
not run extraction, invoke processors, or mutate active requirement, process, or
guardrail artifacts.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence


PACKET_TYPE = "ppd_requirement_extraction_impact_precheck_packet"
PACKET_STATUS = "fixture_first_metadata_only_precheck_ready"

REQUIRED_ATTESTATIONS = (
    "fixture_first_inputs_only",
    "metadata_only_outputs",
    "no_live_extraction_performed",
    "no_processor_invoked",
    "no_active_artifact_mutation_performed",
    "no_requirement_mutation_performed",
    "no_process_mutation_performed",
    "no_guardrail_mutation_performed",
)

_RAW_KEYS = {
    "archive_path",
    "archive_ref",
    "body",
    "body_html",
    "download_path",
    "download_url",
    "raw_archive",
    "raw_body",
    "raw_content",
    "raw_html",
    "response_body",
    "warc_path",
}
_MUTATION_KEYS = {
    "active_artifact_mutation",
    "active_guardrail_mutation",
    "active_process_mutation",
    "active_requirement_mutation",
    "apply_to_live_guardrails",
    "apply_to_live_processes",
    "apply_to_live_requirements",
    "guardrail_mutation_enabled",
    "process_mutation_enabled",
    "requirement_mutation_enabled",
    "mutates_active_artifact",
    "mutates_active_guardrail",
    "mutates_active_process",
    "mutates_active_requirement",
    "writes_live_guardrail",
    "writes_live_process",
    "writes_live_requirement",
}
_RAW_MARKERS = (
    "raw_body",
    "raw html",
    "raw_html",
    "response_body",
    "download_path",
    "download url",
    "download_url",
    "archive_path",
    "warc",
)
_PRIVATE_MARKERS = (
    "access_token",
    "authorization",
    "bearer ",
    "cookie",
    "credential",
    "devhub_session",
    "password",
    "private_case_fact",
    "refresh_token",
    "sessionid",
    "storage_state",
    "trace.zip",
    ".har",
)
_LIVE_MARKERS = (
    "live extraction",
    "extracted live",
    "live extractor",
    "ran extraction",
    "executed extraction",
    "processor ran",
    "processor executed",
    "processor invoked",
    "ran processor",
    "live crawl",
    "crawler ran",
    "fetched url",
    "downloaded document",
)


def build_requirement_extraction_impact_precheck_packet(packet: Mapping[str, Any]) -> dict[str, Any]:
    """Build a metadata-only extraction impact precheck packet from fixtures."""

    _reject_unsafe_content(packet, "input_packet")
    source_delta_packet = _mapping(packet, "source_freshness_delta_review_packet")
    rehearsal_packet = _mapping(packet, "requirement_regeneration_rehearsal_tranche_packet")
    traceability_packet = _mapping(packet, "requirement_guardrail_traceability_review_packet")

    cases_by_requirement = _cases_by_requirement(rehearsal_packet)
    traceability_by_requirement = _traceability_by_requirement(traceability_packet)
    scopes: list[dict[str, Any]] = []

    for index, delta in enumerate(_source_deltas(source_delta_packet), start=1):
        source_id = _required_text(delta, "source_id")
        delta_id = _required_text(delta, "delta_id")
        requirement_ids = _ordered_unique(
            _text_list(delta.get("affected_requirement_ids"))
            + [
                requirement_id
                for requirement_id, case in cases_by_requirement.items()
                if case.get("source_id") == source_id
            ]
        )
        if not requirement_ids:
            raise ValueError("each source delta must resolve at least one affected requirement")

        process_ids = _ordered_unique(
            _text_list(delta.get("affected_process_ids"))
            + _linked_values(requirement_ids, cases_by_requirement, traceability_by_requirement, "affected_process_ids", "process_ids")
        )
        guardrail_ids = _ordered_unique(
            _text_list(delta.get("affected_guardrail_ids"))
            + _linked_values(requirement_ids, cases_by_requirement, traceability_by_requirement, "affected_guardrail_ids", "guardrail_ids")
        )
        evidence_ids = _ordered_unique(
            _text_list(delta.get("source_evidence_ids"))
            + _linked_values(requirement_ids, cases_by_requirement, traceability_by_requirement, "source_evidence_ids", "source_evidence_ids")
        )
        if not any(_looks_cited(evidence_id) for evidence_id in evidence_ids):
            raise ValueError("candidate extraction rerun scopes must include cited source evidence")

        scope_id = "candidate-extraction-rerun-scope-" + _slug(source_id) + "-" + str(index)
        case_refs = [
            {
                "case_id": _required_text(cases_by_requirement[requirement_id], "case_id"),
                "requirement_id": requirement_id,
                "rerun_step_ref": _required_text(cases_by_requirement[requirement_id], "rerun_step_ref"),
            }
            for requirement_id in requirement_ids
            if requirement_id in cases_by_requirement
        ]
        output_refs = [
            "metadata://requirement-extraction-impact-precheck/" + _slug(scope_id) + "/" + _slug(requirement_id)
            for requirement_id in requirement_ids
        ]
        scopes.append(
            {
                "scope_id": scope_id,
                "source_id": source_id,
                "delta_id": delta_id,
                "canonical_url": _required_text(delta, "canonical_url"),
                "candidate_rerun_reason": _text(delta.get("delta_summary")) or "source freshness delta may affect cited requirements",
                "source_evidence_ids": evidence_ids,
                "affected_requirement_ids": requirement_ids,
                "affected_process_ids": process_ids,
                "affected_guardrail_ids": guardrail_ids,
                "candidate_requirement_cases": case_refs,
                "expected_metadata_only_output_refs": output_refs,
                "reviewer_owner_fields": _reviewer_owner_fields(delta, requirement_ids, cases_by_requirement, traceability_by_requirement),
            }
        )

    precheck = {
        "packet_type": PACKET_TYPE,
        "packet_version": "1.0",
        "packet_id": _required_text(packet, "packet_id"),
        "precheck_status": PACKET_STATUS,
        "consumes_packet_ids": [
            _required_text(source_delta_packet, "packet_id"),
            _required_text(rehearsal_packet, "packet_id"),
            _required_text(traceability_packet, "packet_id"),
        ],
        "candidate_extraction_rerun_scopes": scopes,
        "affected_requirement_ids": _ordered_unique(value for scope in scopes for value in scope["affected_requirement_ids"]),
        "affected_process_ids": _ordered_unique(value for scope in scopes for value in scope["affected_process_ids"]),
        "affected_guardrail_ids": _ordered_unique(value for scope in scopes for value in scope["affected_guardrail_ids"]),
        "expected_metadata_only_outputs": _expected_outputs(scopes),
        "reviewer_owner_fields_required": True,
        "attestations": {key: True for key in REQUIRED_ATTESTATIONS},
    }
    validate_requirement_extraction_impact_precheck_packet(precheck)
    return precheck


def validate_requirement_extraction_impact_precheck_packet(packet: Mapping[str, Any]) -> None:
    """Raise ValueError when an impact precheck packet is incomplete or unsafe."""

    if packet.get("packet_type") != PACKET_TYPE:
        raise ValueError("unexpected packet_type")
    if packet.get("precheck_status") != PACKET_STATUS:
        raise ValueError("precheck_status must remain fixture-first metadata-only")
    _required_text(packet, "packet_id")
    if not _required_text_list(packet, "consumes_packet_ids"):
        raise ValueError("consumes_packet_ids must not be empty")

    attestations = _mapping(packet, "attestations")
    for key in REQUIRED_ATTESTATIONS:
        if attestations.get(key) is not True:
            raise ValueError("required attestation is missing or false: " + key)

    scopes = packet.get("candidate_extraction_rerun_scopes")
    if not isinstance(scopes, list) or not scopes:
        raise ValueError("candidate_extraction_rerun_scopes must be a non-empty list")

    seen_scope_ids: set[str] = set()
    expected_output_refs: set[str] = set()
    for index, scope in enumerate(scopes):
        if not isinstance(scope, Mapping):
            raise ValueError("candidate_extraction_rerun_scopes entries must be objects")
        prefix = "candidate_extraction_rerun_scopes[" + str(index) + "]"
        scope_id = _required_text(scope, "scope_id")
        if scope_id in seen_scope_ids:
            raise ValueError("duplicate scope_id: " + scope_id)
        seen_scope_ids.add(scope_id)
        _required_text(scope, "source_id")
        _required_text(scope, "delta_id")
        _required_text(scope, "canonical_url")
        _required_text(scope, "candidate_rerun_reason")
        evidence_ids = _required_text_list(scope, "source_evidence_ids")
        if not any(_looks_cited(evidence_id) for evidence_id in evidence_ids):
            raise ValueError(prefix + ".source_evidence_ids must include cited evidence")
        _required_text_list(scope, "affected_requirement_ids")
        _required_text_list(scope, "affected_process_ids")
        _required_text_list(scope, "affected_guardrail_ids")
        owners = _mapping(scope, "reviewer_owner_fields")
        for key in ("source_delta_owner", "requirement_owner", "process_owner", "guardrail_owner", "precheck_owner"):
            if not _text(owners.get(key)):
                raise ValueError(prefix + ".reviewer_owner_fields." + key + " is required")
        output_refs = _required_text_list(scope, "expected_metadata_only_output_refs")
        expected_output_refs.update(output_refs)

    if set(_required_text_list(packet, "affected_requirement_ids")) != _ordered_set(value for scope in scopes for value in scope["affected_requirement_ids"]):
        raise ValueError("top-level affected_requirement_ids must match scopes")
    if set(_required_text_list(packet, "affected_process_ids")) != _ordered_set(value for scope in scopes for value in scope["affected_process_ids"]):
        raise ValueError("top-level affected_process_ids must match scopes")
    if set(_required_text_list(packet, "affected_guardrail_ids")) != _ordered_set(value for scope in scopes for value in scope["affected_guardrail_ids"]):
        raise ValueError("top-level affected_guardrail_ids must match scopes")

    outputs = packet.get("expected_metadata_only_outputs")
    if not isinstance(outputs, list) or not outputs:
        raise ValueError("expected_metadata_only_outputs must be a non-empty list")
    seen_refs: set[str] = set()
    for output in outputs:
        if not isinstance(output, Mapping):
            raise ValueError("expected_metadata_only_outputs entries must be objects")
        output_ref = _required_text(output, "output_ref")
        seen_refs.add(output_ref)
        if output.get("metadata_only") is not True:
            raise ValueError("expected metadata output must be metadata_only")
        for key in ("no_requirement_record_written", "no_process_model_written", "no_guardrail_bundle_written", "no_active_artifact_written"):
            if output.get(key) is not True:
                raise ValueError("expected metadata output must attest " + key)
    if seen_refs != expected_output_refs:
        raise ValueError("expected_metadata_only_outputs must cover every scope output ref")

    _reject_unsafe_content(packet, "packet")


def _source_deltas(packet: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    rows = packet.get("reviewed_source_deltas") or packet.get("source_freshness_deltas") or packet.get("source_deltas")
    if not isinstance(rows, list) or not rows:
        raise ValueError("source freshness delta review packet must include reviewed source deltas")
    result: list[Mapping[str, Any]] = []
    for row in rows:
        if not isinstance(row, Mapping):
            raise ValueError("source delta entries must be objects")
        result.append(row)
    return result


def _cases_by_requirement(packet: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    rows = packet.get("ordered_synthetic_rerun_cases")
    if not isinstance(rows, list) or not rows:
        raise ValueError("requirement regeneration rehearsal packet must include ordered_synthetic_rerun_cases")
    indexed: dict[str, Mapping[str, Any]] = {}
    for row in rows:
        if not isinstance(row, Mapping):
            raise ValueError("rerun case entries must be objects")
        indexed[_required_text(row, "requirement_id")] = row
    return indexed


def _traceability_by_requirement(packet: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    rows = packet.get("requirement_to_process_to_guardrail_links")
    if not isinstance(rows, list) or not rows:
        raise ValueError("traceability packet must include requirement links")
    indexed: dict[str, Mapping[str, Any]] = {}
    for row in rows:
        if not isinstance(row, Mapping):
            raise ValueError("traceability link entries must be objects")
        indexed[_required_text(row, "requirement_id")] = row
    return indexed


def _linked_values(
    requirement_ids: Sequence[str],
    cases: Mapping[str, Mapping[str, Any]],
    traceability: Mapping[str, Mapping[str, Any]],
    case_key: str,
    trace_key: str,
) -> list[str]:
    values: list[str] = []
    for requirement_id in requirement_ids:
        case = cases.get(requirement_id, {})
        trace = traceability.get(requirement_id, {})
        values.extend(_text_list(case.get(case_key)))
        values.extend(_text_list(trace.get(trace_key)))
    return values


def _reviewer_owner_fields(
    delta: Mapping[str, Any],
    requirement_ids: Sequence[str],
    cases: Mapping[str, Mapping[str, Any]],
    traceability: Mapping[str, Mapping[str, Any]],
) -> dict[str, str]:
    delta_owners = delta.get("reviewer_owner_fields") if isinstance(delta.get("reviewer_owner_fields"), Mapping) else {}
    first_requirement = requirement_ids[0]
    first_case = cases.get(first_requirement, {})
    first_trace = traceability.get(first_requirement, {})
    trace_owners = first_trace.get("reviewer_owner_fields") if isinstance(first_trace.get("reviewer_owner_fields"), Mapping) else {}
    return {
        "source_delta_owner": _text(delta_owners.get("source_delta_owner")) or _text(delta.get("reviewer_owner")) or "ppd-source-freshness-reviewer",
        "requirement_owner": _text(delta_owners.get("requirement_owner")) or _text(first_case.get("reviewer_owner")) or "ppd-requirement-reviewer",
        "process_owner": _text(delta_owners.get("process_owner")) or _text(trace_owners.get("process_owner")) or "ppd-process-reviewer",
        "guardrail_owner": _text(delta_owners.get("guardrail_owner")) or _text(trace_owners.get("guardrail_owner")) or _text(trace_owners.get("traceability_owner")) or "ppd-guardrail-reviewer",
        "precheck_owner": _text(delta_owners.get("precheck_owner")) or "ppd-requirement-extraction-precheck-owner",
    }


def _expected_outputs(scopes: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    outputs: list[dict[str, Any]] = []
    for scope in scopes:
        for output_ref in _text_list(scope.get("expected_metadata_only_output_refs")):
            outputs.append(
                {
                    "scope_id": _required_text(scope, "scope_id"),
                    "output_ref": output_ref,
                    "output_kind": "candidate_requirement_extraction_rerun_scope_metadata",
                    "metadata_only": True,
                    "no_requirement_record_written": True,
                    "no_process_model_written": True,
                    "no_guardrail_bundle_written": True,
                    "no_active_artifact_written": True,
                }
            )
    return outputs


def _mapping(value: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    child = value.get(key)
    if not isinstance(child, Mapping):
        raise ValueError(key + " must be an object")
    return child


def _required_text(value: Mapping[str, Any], key: str) -> str:
    child = value.get(key)
    if not isinstance(child, str) or not child.strip():
        raise ValueError(key + " must be a non-empty string")
    return child.strip()


def _required_text_list(value: Mapping[str, Any], key: str) -> list[str]:
    result = _text_list(value.get(key))
    if not result:
        raise ValueError(key + " must be a non-empty list of strings")
    return result


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) and value.strip() else ""


def _text_list(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    result = [item.strip() for item in value if isinstance(item, str) and item.strip()]
    if len(result) != len(value):
        return []
    return result


def _ordered_unique(items: Any) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if isinstance(item, str) and item and item not in seen:
            seen.add(item)
            result.append(item)
    return result


def _ordered_set(items: Any) -> set[str]:
    return set(_ordered_unique(items))


def _looks_cited(value: str) -> bool:
    return ":" in value or value.startswith(("citation-", "evidence-", "source-", "trace-"))


def _reject_unsafe_content(value: Any, path: str) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            key_lower = key_text.lower()
            child_path = path + "." + key_text
            if key_lower in _RAW_KEYS:
                raise ValueError("raw body/download/archive reference is not allowed: " + child_path)
            if key_lower in _MUTATION_KEYS and child not in (False, None, "", "false", "metadata_only", "review_only"):
                raise ValueError("active artifact mutation flag is not allowed: " + child_path)
            if any(marker in key_lower for marker in _PRIVATE_MARKERS):
                raise ValueError("private or browser artifact field is not allowed: " + child_path)
            _reject_unsafe_content(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_unsafe_content(child, path + "[" + str(index) + "]")
    elif isinstance(value, str):
        lowered = value.lower()
        if any(marker in lowered for marker in _RAW_MARKERS):
            raise ValueError("raw body/download/archive reference is not allowed: " + path)
        if any(marker in lowered for marker in _PRIVATE_MARKERS):
            raise ValueError("private or browser artifact reference is not allowed: " + path)
        if any(marker in lowered for marker in _LIVE_MARKERS):
            raise ValueError("live extraction or processor execution claim is not allowed: " + path)


def _slug(value: str) -> str:
    chars: list[str] = []
    previous_dash = False
    for char in value.lower():
        if char.isalnum():
            chars.append(char)
            previous_dash = False
        elif not previous_dash:
            chars.append("-")
            previous_dash = True
    return "".join(chars).strip("-") or "item"
