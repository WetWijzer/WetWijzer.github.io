"""Fixture-first PDF preview readiness packet validation.

This module intentionally stays local and deterministic. It validates committed
preview packets that describe whether a narrow PP&D form workflow is ready for a
local PDF preview, while blocking certification or submission-related fields.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class PreviewReadinessError(ValueError):
    """Raised when a preview readiness packet is malformed or unsafe."""


@dataclass(frozen=True)
class PreviewReadinessSummary:
    workflow_id: str
    status: str
    preview_only: bool
    required_field_count: int
    satisfied_field_count: int
    missing_prompt_count: int
    blocked_certification_field_count: int
    citation_count: int
    output_kind: str

    @property
    def ready_for_preview(self) -> bool:
        return (
            self.preview_only
            and self.missing_prompt_count == 0
            and self.blocked_certification_field_count == 0
            and self.satisfied_field_count == self.required_field_count
        )


def load_preview_readiness_packet(path: str | Path) -> dict[str, Any]:
    packet_path = Path(path)
    with packet_path.open("r", encoding="utf-8") as packet_file:
        packet = json.load(packet_file)
    validate_preview_readiness_packet(packet)
    return packet


def build_preview_readiness_summary(packet: dict[str, Any]) -> PreviewReadinessSummary:
    validate_preview_readiness_packet(packet)

    form_fields = packet["form_fields"]
    synthetic_facts = packet["synthetic_user_facts"]
    satisfied_fields = [
        field
        for field in form_fields
        if field.get("required", False)
        and field.get("fact_key") in synthetic_facts
        and synthetic_facts[field["fact_key"]] not in (None, "")
    ]

    return PreviewReadinessSummary(
        workflow_id=packet["workflow_id"],
        status=packet["readiness_status"],
        preview_only=packet["preview_only"],
        required_field_count=sum(1 for field in form_fields if field.get("required", False)),
        satisfied_field_count=len(satisfied_fields),
        missing_prompt_count=len(packet["missing_prompts"]),
        blocked_certification_field_count=len(packet["blocked_certification_fields"]),
        citation_count=len(packet["citation_evidence"]),
        output_kind=packet["preview_output_metadata"]["output_kind"],
    )


def validate_preview_readiness_packet(packet: dict[str, Any]) -> None:
    required_top_level = {
        "packet_id",
        "workflow_id",
        "readiness_status",
        "preview_only",
        "form_fields",
        "synthetic_user_facts",
        "missing_prompts",
        "citation_evidence",
        "blocked_certification_fields",
        "preview_output_metadata",
    }
    missing_keys = sorted(required_top_level.difference(packet))
    if missing_keys:
        raise PreviewReadinessError(f"Missing packet keys: {missing_keys}")

    if packet["preview_only"] is not True:
        raise PreviewReadinessError("Preview readiness packets must be preview_only=true")

    _require_list(packet, "form_fields")
    _require_mapping(packet, "synthetic_user_facts")
    _require_list(packet, "missing_prompts")
    _require_list(packet, "citation_evidence")
    _require_list(packet, "blocked_certification_fields")
    _require_mapping(packet, "preview_output_metadata")

    citations_by_id = _validate_citations(packet["citation_evidence"])
    form_fact_keys = _validate_form_fields(packet["form_fields"], citations_by_id)
    _validate_missing_prompts(packet["missing_prompts"], form_fact_keys, citations_by_id)
    _validate_blocked_certification_fields(packet["blocked_certification_fields"], citations_by_id)
    _validate_preview_output_metadata(packet["preview_output_metadata"])


def _validate_citations(citations: list[dict[str, Any]]) -> set[str]:
    citation_ids: set[str] = set()
    for citation in citations:
        _require_mapping_value(citation, "citation")
        citation_id = _require_string(citation, "citation_id")
        if citation_id in citation_ids:
            raise PreviewReadinessError(f"Duplicate citation_id: {citation_id}")
        citation_ids.add(citation_id)
        url = _require_string(citation, "url")
        if not url.startswith("https://www.portland.gov/") and not url.startswith("https://devhub.portlandoregon.gov"):
            raise PreviewReadinessError(f"Citation URL is outside PP&D allowlist: {url}")
        _require_string(citation, "source_title")
        _require_string(citation, "evidence_text")
    if not citation_ids:
        raise PreviewReadinessError("At least one citation is required")
    return citation_ids


def _validate_form_fields(form_fields: list[dict[str, Any]], citation_ids: set[str]) -> set[str]:
    fact_keys: set[str] = set()
    field_names: set[str] = set()
    for field in form_fields:
        _require_mapping_value(field, "form field")
        field_name = _require_string(field, "pdf_field_name")
        if field_name in field_names:
            raise PreviewReadinessError(f"Duplicate pdf_field_name: {field_name}")
        field_names.add(field_name)
        fact_key = _require_string(field, "fact_key")
        fact_keys.add(fact_key)
        if not isinstance(field.get("required"), bool):
            raise PreviewReadinessError(f"Field {field_name} must declare a boolean required value")
        trace_ids = field.get("requirement_trace_ids")
        if not isinstance(trace_ids, list) or not trace_ids:
            raise PreviewReadinessError(f"Field {field_name} must include requirement_trace_ids")
        unknown = sorted(set(trace_ids).difference(citation_ids))
        if unknown:
            raise PreviewReadinessError(f"Field {field_name} references unknown citations: {unknown}")
    if not field_names:
        raise PreviewReadinessError("At least one form field is required")
    return fact_keys


def _validate_missing_prompts(
    prompts: list[dict[str, Any]], form_fact_keys: set[str], citation_ids: set[str]
) -> None:
    for prompt in prompts:
        _require_mapping_value(prompt, "missing prompt")
        fact_key = _require_string(prompt, "fact_key")
        if fact_key not in form_fact_keys:
            raise PreviewReadinessError(f"Missing prompt references unknown fact_key: {fact_key}")
        _require_string(prompt, "prompt")
        trace_ids = prompt.get("requirement_trace_ids")
        if not isinstance(trace_ids, list) or not trace_ids:
            raise PreviewReadinessError(f"Missing prompt for {fact_key} must include requirement_trace_ids")
        unknown = sorted(set(trace_ids).difference(citation_ids))
        if unknown:
            raise PreviewReadinessError(f"Missing prompt for {fact_key} references unknown citations: {unknown}")


def _validate_blocked_certification_fields(
    blocked_fields: list[dict[str, Any]], citation_ids: set[str]
) -> None:
    for field in blocked_fields:
        _require_mapping_value(field, "blocked certification field")
        _require_string(field, "pdf_field_name")
        reason = _require_string(field, "blocked_reason")
        if "certification" not in reason and "signature" not in reason:
            raise PreviewReadinessError("Blocked certification fields must identify certification or signature risk")
        if field.get("may_autofill") is not False:
            raise PreviewReadinessError("Blocked certification fields must set may_autofill=false")
        trace_ids = field.get("requirement_trace_ids")
        if not isinstance(trace_ids, list) or not trace_ids:
            raise PreviewReadinessError("Blocked certification fields must include requirement_trace_ids")
        unknown = sorted(set(trace_ids).difference(citation_ids))
        if unknown:
            raise PreviewReadinessError(f"Blocked field references unknown citations: {unknown}")


def _validate_preview_output_metadata(metadata: dict[str, Any]) -> None:
    if metadata.get("output_kind") != "local_pdf_preview_packet":
        raise PreviewReadinessError("preview_output_metadata.output_kind must be local_pdf_preview_packet")
    if metadata.get("official_submission_ready") is not False:
        raise PreviewReadinessError("Preview packets must set official_submission_ready=false")
    forbidden_actions = {"upload", "submit", "certify", "pay", "schedule", "cancel"}
    actions = metadata.get("disallowed_actions")
    if not isinstance(actions, list) or not forbidden_actions.issubset(set(actions)):
        raise PreviewReadinessError("Preview metadata must block upload, submit, certify, pay, schedule, and cancel")
    if metadata.get("stores_private_values") is not False:
        raise PreviewReadinessError("Preview metadata must not store private values")


def _require_list(packet: dict[str, Any], key: str) -> None:
    if not isinstance(packet.get(key), list):
        raise PreviewReadinessError(f"{key} must be a list")


def _require_mapping(packet: dict[str, Any], key: str) -> None:
    if not isinstance(packet.get(key), dict):
        raise PreviewReadinessError(f"{key} must be an object")


def _require_mapping_value(value: Any, label: str) -> None:
    if not isinstance(value, dict):
        raise PreviewReadinessError(f"Expected {label} to be an object")


def _require_string(packet: dict[str, Any], key: str) -> str:
    value = packet.get(key)
    if not isinstance(value, str) or not value:
        raise PreviewReadinessError(f"{key} must be a non-empty string")
    return value
