"""Fixture-first requirement extraction rerun work-order packet builder.

This module intentionally builds metadata-only synthetic work orders from
review packets. It does not crawl, invoke processors, extract requirements, or
mutate requirement/process/guardrail/prompt/monitoring/release artifacts.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

ATTESTATIONS: dict[str, bool] = {
    "no_live_extraction": True,
    "no_processor_invocation": True,
    "no_requirement_mutation": True,
    "no_process_mutation": True,
    "no_guardrail_mutation": True,
    "no_prompt_mutation": True,
    "no_monitoring_mutation": True,
    "no_release_state_mutation": True,
    "no_legal_or_permitting_outcome_guarantee": True,
}

EXPECTED_METADATA_ONLY_OUTPUTS: tuple[dict[str, Any], ...] = (
    {
        "output_id": "requirement_extraction_rerun_metadata_manifest",
        "metadata_only": True,
        "allowed_fields": [
            "work_item_id",
            "source_ids",
            "requirement_ids",
            "guardrail_ids",
            "rerun_reason",
            "reviewer_owner",
            "expected_validation_status",
        ],
        "prohibited_outputs": [
            "raw_source_body",
            "downloaded_document",
            "processor_artifact",
            "new_requirement_node",
            "mutated_requirement_node",
            "mutated_process_model",
            "mutated_guardrail_bundle",
            "mutated_prompt",
            "mutated_monitoring_plan",
            "mutated_release_state",
        ],
    },
)

_REASON_PRIORITY = {
    "traceability_gap": 10,
    "source_freshness_delta": 20,
    "impact_precheck": 30,
}

_FALSE_EXECUTION_CLAIM_KEYS = {
    "live_extraction",
    "live_extraction_claim",
    "live_network_used",
    "crawler_invoked",
    "processor_invoked",
    "processor_invocation",
    "extraction_executed",
    "requirement_extraction_executed",
}

_MUTATION_FLAG_KEYS = {
    "active_requirement_mutation",
    "active_requirement_mutation_flag",
    "active_process_mutation",
    "active_process_mutation_flag",
    "active_guardrail_mutation",
    "active_guardrail_mutation_flag",
    "active_prompt_mutation",
    "active_prompt_mutation_flag",
    "active_monitoring_mutation",
    "active_monitoring_mutation_flag",
    "active_release_state_mutation",
    "active_release_state_mutation_flag",
    "requirements_mutated",
    "processes_mutated",
    "guardrails_mutated",
    "prompts_mutated",
    "monitoring_mutated",
    "release_state_mutated",
}

_FORBIDDEN_REFERENCE_KEYS = {
    "archive_artifact_ref",
    "archive_path",
    "download_path",
    "download_ref",
    "downloaded_document_ref",
    "raw_archive_ref",
    "raw_body",
    "raw_body_ref",
    "raw_html",
    "raw_source_body",
    "raw_source_text",
    "source_body",
    "warc_path",
}

_PRIVATE_FACT_KEYS = {
    "case_fact",
    "case_facts",
    "known_facts",
    "private_case",
    "private_case_fact",
    "private_case_facts",
    "private_fact",
    "private_facts",
    "property_address",
    "user_fact",
    "user_facts",
}

_GUARANTEE_KEYS = {
    "approval_guarantee",
    "guaranteed_approval",
    "guaranteed_outcome",
    "legal_outcome_guarantee",
    "permit_approval_guarantee",
    "permitting_outcome_guarantee",
}

_FORBIDDEN_STRING_MARKERS = (
    "file://",
    "storage_state",
    "trace.zip",
    "playwright-trace",
    "raw body",
    "raw_body",
    "raw-html",
    "raw_html",
    "warc",
    "download_path",
    "downloaded document",
    "archive_artifact_ref",
    "raw_archive_ref",
    "private case fact",
    "known private fact",
    "guaranteed approval",
    "guarantee approval",
    "guarantee permit",
    "legal outcome guarantee",
    "permitting outcome guarantee",
    "live extraction executed",
    "processor executed",
    "processor invocation completed",
)


@dataclass(frozen=True)
class RequirementExtractionRerunWorkOrderValidationResult:
    valid: bool
    errors: tuple[str, ...]


class RequirementExtractionRerunWorkOrderPacketError(ValueError):
    pass


@dataclass(frozen=True)
class _Candidate:
    reason: str
    source_ids: tuple[str, ...]
    requirement_ids: tuple[str, ...]
    guardrail_ids: tuple[str, ...]
    reviewer_owner: str
    reviewer_backup: str
    notes: tuple[str, ...]

    @property
    def sort_key(self) -> tuple[int, str, str, str]:
        return (
            _REASON_PRIORITY[self.reason],
            self.requirement_ids[0] if self.requirement_ids else "",
            self.source_ids[0] if self.source_ids else "",
            self.guardrail_ids[0] if self.guardrail_ids else "",
        )


def load_packet(path: Path | str) -> dict[str, Any]:
    """Load a committed fixture packet from disk."""

    with Path(path).open("r", encoding="utf-8") as handle:
        packet = json.load(handle)
    if not isinstance(packet, dict):
        raise ValueError(f"packet must be a JSON object: {path}")
    return packet


def build_packet_from_fixture_paths(
    impact_precheck_path: Path | str,
    source_freshness_delta_path: Path | str,
    traceability_review_path: Path | str,
) -> dict[str, Any]:
    """Build the rerun work-order packet from three fixture packet paths."""

    return build_requirement_extraction_rerun_work_order_packet(
        impact_precheck=load_packet(impact_precheck_path),
        source_freshness_delta=load_packet(source_freshness_delta_path),
        traceability_review=load_packet(traceability_review_path),
    )


def build_requirement_extraction_rerun_work_order_packet(
    *,
    impact_precheck: Mapping[str, Any],
    source_freshness_delta: Mapping[str, Any],
    traceability_review: Mapping[str, Any],
) -> dict[str, Any]:
    """Create ordered synthetic rerun work items from review packets."""

    input_errors: list[str] = []
    _reject_forbidden_content(impact_precheck, "impact_precheck", input_errors)
    _reject_forbidden_content(source_freshness_delta, "source_freshness_delta", input_errors)
    _reject_forbidden_content(traceability_review, "traceability_review", input_errors)
    if input_errors:
        raise RequirementExtractionRerunWorkOrderPacketError("invalid work-order inputs: " + "; ".join(input_errors))

    candidates = [
        *_candidates_from_traceability_review(traceability_review),
        *_candidates_from_source_freshness_delta(source_freshness_delta),
        *_candidates_from_impact_precheck(impact_precheck),
    ]
    ordered_candidates = sorted(_dedupe_candidates(candidates), key=lambda item: item.sort_key)

    work_items = [
        _candidate_to_work_item(index=index, candidate=candidate)
        for index, candidate in enumerate(ordered_candidates, start=1)
    ]

    packet = {
        "packet_id": "requirement-extraction-rerun-work-order-fixture-packet",
        "packet_type": "requirement_extraction_rerun_work_order",
        "mode": "fixture_first_metadata_only",
        "consumed_packet_ids": [
            _packet_id(impact_precheck),
            _packet_id(source_freshness_delta),
            _packet_id(traceability_review),
        ],
        "source_packet_types": [
            "requirement_extraction_impact_precheck",
            "source_freshness_delta_review",
            "requirement_to_guardrail_traceability_review",
        ],
        "work_items": work_items,
        "expected_packet_outputs": list(EXPECTED_METADATA_ONLY_OUTPUTS),
        "attestations": dict(ATTESTATIONS),
    }
    require_valid_requirement_extraction_rerun_work_order_packet(packet)
    return packet


def validate_requirement_extraction_rerun_work_order_packet(
    packet: Mapping[str, Any],
) -> RequirementExtractionRerunWorkOrderValidationResult:
    """Validate that a rerun work-order packet is metadata-only and cited."""

    errors: list[str] = []
    _reject_forbidden_content(packet, "packet", errors)

    if packet.get("packet_type") != "requirement_extraction_rerun_work_order":
        errors.append("packet_type must be requirement_extraction_rerun_work_order")
    if packet.get("mode") != "fixture_first_metadata_only":
        errors.append("mode must be fixture_first_metadata_only")

    packet_outputs = _require_list(packet.get("expected_packet_outputs"), "expected_packet_outputs", errors)
    _validate_expected_outputs(packet_outputs, "expected_packet_outputs", errors)

    attestations = packet.get("attestations")
    if not isinstance(attestations, Mapping):
        errors.append("attestations must be an object")
    else:
        for key, expected in ATTESTATIONS.items():
            if attestations.get(key) is not expected:
                errors.append(f"attestations.{key} must be {str(expected).lower()}")

    work_items = _require_list(packet.get("work_items"), "work_items", errors)
    if not work_items:
        errors.append("work_items must contain at least one work item")
    _validate_work_items(work_items, errors)

    return RequirementExtractionRerunWorkOrderValidationResult(valid=not errors, errors=tuple(errors))


def require_valid_requirement_extraction_rerun_work_order_packet(packet: Mapping[str, Any]) -> None:
    result = validate_requirement_extraction_rerun_work_order_packet(packet)
    if not result.valid:
        raise RequirementExtractionRerunWorkOrderPacketError("; ".join(result.errors))


def _candidates_from_impact_precheck(packet: Mapping[str, Any]) -> list[_Candidate]:
    candidates: list[_Candidate] = []
    for item in _list(packet, "impacted_requirements"):
        requirement_ids = _tuple(item, "requirement_ids", fallback_key="requirement_id")
        source_ids = _tuple(item, "source_ids", fallback_key="source_id")
        guardrail_ids = _tuple(item, "guardrail_ids", fallback_key="guardrail_id")
        if not requirement_ids or not source_ids:
            continue
        candidates.append(
            _Candidate(
                reason="impact_precheck",
                source_ids=source_ids,
                requirement_ids=requirement_ids,
                guardrail_ids=guardrail_ids,
                reviewer_owner=str(item.get("reviewer_owner", "requirements-reviewer")),
                reviewer_backup=str(item.get("reviewer_backup", "guardrail-reviewer")),
                notes=_tuple(item, "notes", fallback_key="note"),
            )
        )
    return candidates


def _candidates_from_source_freshness_delta(packet: Mapping[str, Any]) -> list[_Candidate]:
    candidates: list[_Candidate] = []
    for item in _list(packet, "source_deltas"):
        source_ids = _tuple(item, "source_ids", fallback_key="source_id")
        requirement_ids = _tuple(item, "affected_requirement_ids", fallback_key="affected_requirement_id")
        guardrail_ids = _tuple(item, "affected_guardrail_ids", fallback_key="affected_guardrail_id")
        if not source_ids or not requirement_ids:
            continue
        candidates.append(
            _Candidate(
                reason="source_freshness_delta",
                source_ids=source_ids,
                requirement_ids=requirement_ids,
                guardrail_ids=guardrail_ids,
                reviewer_owner=str(item.get("reviewer_owner", "source-freshness-reviewer")),
                reviewer_backup=str(item.get("reviewer_backup", "requirements-reviewer")),
                notes=_tuple(item, "delta_summary", fallback_key="note"),
            )
        )
    return candidates


def _candidates_from_traceability_review(packet: Mapping[str, Any]) -> list[_Candidate]:
    candidates: list[_Candidate] = []
    for item in _list(packet, "traceability_findings"):
        requirement_ids = _tuple(item, "requirement_ids", fallback_key="requirement_id")
        source_ids = _tuple(item, "source_ids", fallback_key="source_id")
        guardrail_ids = _tuple(item, "guardrail_ids", fallback_key="guardrail_id")
        if not requirement_ids or not source_ids:
            continue
        candidates.append(
            _Candidate(
                reason="traceability_gap",
                source_ids=source_ids,
                requirement_ids=requirement_ids,
                guardrail_ids=guardrail_ids,
                reviewer_owner=str(item.get("reviewer_owner", "guardrail-traceability-reviewer")),
                reviewer_backup=str(item.get("reviewer_backup", "requirements-reviewer")),
                notes=_tuple(item, "finding_summary", fallback_key="note"),
            )
        )
    return candidates


def _candidate_to_work_item(*, index: int, candidate: _Candidate) -> dict[str, Any]:
    return {
        "work_item_id": f"synthetic-requirement-rerun-{index:03d}",
        "rerun_reason": candidate.reason,
        "source_ids": list(candidate.source_ids),
        "requirement_ids": list(candidate.requirement_ids),
        "guardrail_ids": list(candidate.guardrail_ids),
        "expected_outputs": list(EXPECTED_METADATA_ONLY_OUTPUTS),
        "reviewer_owner": {
            "primary": candidate.reviewer_owner,
            "backup": candidate.reviewer_backup,
        },
        "notes": list(candidate.notes),
        "attestations": dict(ATTESTATIONS),
    }


def _validate_work_items(work_items: Sequence[Any], errors: list[str]) -> None:
    seen_ids: set[str] = set()
    for index, item in enumerate(work_items):
        path = f"work_items[{index}]"
        if not isinstance(item, Mapping):
            errors.append(path + " must be an object")
            continue
        work_item_id = _text(item.get("work_item_id"))
        if not work_item_id:
            errors.append(path + ".work_item_id is required")
        if work_item_id in seen_ids:
            errors.append(path + ".work_item_id must be unique")
        seen_ids.add(work_item_id)

        if not _string_list(item.get("source_ids")):
            errors.append(path + ".source_ids must cite at least one public source id")
        if not _string_list(item.get("requirement_ids")):
            errors.append(path + ".requirement_ids must cite at least one requirement id")

        reviewer_owner = item.get("reviewer_owner")
        if not isinstance(reviewer_owner, Mapping):
            errors.append(path + ".reviewer_owner must be an object")
        else:
            if not _text(reviewer_owner.get("primary")):
                errors.append(path + ".reviewer_owner.primary is required")
            if not _text(reviewer_owner.get("backup")):
                errors.append(path + ".reviewer_owner.backup is required")

        expected_outputs = _require_list(item.get("expected_outputs"), path + ".expected_outputs", errors)
        _validate_expected_outputs(expected_outputs, path + ".expected_outputs", errors)

        attestations = item.get("attestations")
        if not isinstance(attestations, Mapping):
            errors.append(path + ".attestations must be an object")
        else:
            for key, expected in ATTESTATIONS.items():
                if attestations.get(key) is not expected:
                    errors.append(f"{path}.attestations.{key} must be {str(expected).lower()}")


def _validate_expected_outputs(outputs: Sequence[Any], path: str, errors: list[str]) -> None:
    if not outputs:
        errors.append(path + " must include the metadata-only output contract")
        return
    matching = [output for output in outputs if isinstance(output, Mapping) and output.get("output_id") == "requirement_extraction_rerun_metadata_manifest"]
    if not matching:
        errors.append(path + " must include requirement_extraction_rerun_metadata_manifest")
        return
    for output in matching:
        if output.get("metadata_only") is not True:
            errors.append(path + ".metadata_only must be true")
        allowed_fields = _string_list(output.get("allowed_fields"))
        prohibited_outputs = _string_list(output.get("prohibited_outputs"))
        for required in ("work_item_id", "source_ids", "requirement_ids", "reviewer_owner", "expected_validation_status"):
            if required not in allowed_fields:
                errors.append(path + f".allowed_fields must include {required}")
        for prohibited in ("raw_source_body", "downloaded_document", "processor_artifact", "mutated_requirement_node"):
            if prohibited not in prohibited_outputs:
                errors.append(path + f".prohibited_outputs must include {prohibited}")


def _reject_forbidden_content(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            child_path = path + "." + key_text
            _validate_key_value(key_text, child, child_path, errors)
            if isinstance(child, str):
                _validate_string_value(child, child_path, errors)
            _reject_forbidden_content(child, child_path, errors)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            _reject_forbidden_content(child, f"{path}[{index}]", errors)
    elif isinstance(value, str):
        _validate_string_value(value, path, errors)


def _validate_key_value(key: str, value: Any, path: str, errors: list[str]) -> None:
    normalized = key.lower()
    if normalized in _FORBIDDEN_REFERENCE_KEYS:
        errors.append(path + " is not allowed in metadata-only work-order packets")
    if normalized in _PRIVATE_FACT_KEYS:
        errors.append(path + " must not include private case facts")
    if normalized in _GUARANTEE_KEYS:
        errors.append(path + " must not guarantee legal or permitting outcomes")
    if normalized in _FALSE_EXECUTION_CLAIM_KEYS and value is not False:
        errors.append(path + " must be false when present")
    if normalized in _MUTATION_FLAG_KEYS and value is not False:
        errors.append(path + " must be false when present")
    if normalized.startswith("active_") and normalized.endswith("_mutation_flag") and value is not False:
        errors.append(path + " must be false when present")
    if normalized.startswith("active_") and normalized.endswith("_mutation") and value is not False:
        errors.append(path + " must be false when present")


def _validate_string_value(value: str, path: str, errors: list[str]) -> None:
    lowered = value.lower()
    if any(marker in lowered for marker in _FORBIDDEN_STRING_MARKERS):
        errors.append(path + " contains a forbidden raw, private, execution, or guarantee marker")


def _dedupe_candidates(candidates: Iterable[_Candidate]) -> list[_Candidate]:
    seen: set[tuple[str, tuple[str, ...], tuple[str, ...], tuple[str, ...]]] = set()
    deduped: list[_Candidate] = []
    for candidate in candidates:
        key = (
            candidate.reason,
            candidate.source_ids,
            candidate.requirement_ids,
            candidate.guardrail_ids,
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(candidate)
    return deduped


def _packet_id(packet: Mapping[str, Any]) -> str:
    value = packet.get("packet_id")
    if not isinstance(value, str) or not value:
        raise ValueError("input packet is missing packet_id")
    return value


def _list(packet: Mapping[str, Any], key: str) -> list[Mapping[str, Any]]:
    value = packet.get(key, [])
    if not isinstance(value, list):
        raise ValueError(f"{key} must be a list")
    result: list[Mapping[str, Any]] = []
    for entry in value:
        if not isinstance(entry, Mapping):
            raise ValueError(f"{key} entries must be objects")
        result.append(entry)
    return result


def _tuple(packet: Mapping[str, Any], key: str, *, fallback_key: str) -> tuple[str, ...]:
    value = packet.get(key)
    if value is None:
        value = packet.get(fallback_key)
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,) if value else ()
    if isinstance(value, list):
        return tuple(sorted(str(item) for item in value if str(item)))
    return (str(value),)


def _require_list(value: Any, path: str, errors: list[str]) -> list[Any]:
    if not isinstance(value, list):
        errors.append(path + " must be a list")
        return []
    return value


def _string_list(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value] if value else []
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return sorted({str(item) for item in value if isinstance(item, str) and item})
    return []


def _text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()
