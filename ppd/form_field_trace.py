from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REQUIRED_PACKET_KEYS = {
    "packet_id",
    "workflow_id",
    "workflow_name",
    "scope",
    "safety",
    "source_evidence",
    "requirements",
    "user_facts",
    "missing_prompts",
    "devhub_fields",
    "pdf_fields",
    "field_traces",
}

_ALLOWED_TRACE_STATUSES = {"ready_for_preview", "blocked_missing_fact"}
_ALLOWED_FIELD_SOURCES = {"user_fact", "missing_prompt", "constant"}
_ALLOWED_VALUE_MODES = {"preview_only", "not_drafted"}


class FormFieldTraceError(ValueError):
    """Raised when a form-field requirement trace packet is invalid."""


def load_trace_packet(path: str | Path) -> dict[str, Any]:
    packet_path = Path(path)
    with packet_path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise FormFieldTraceError("trace packet root must be an object")
    return value


def assert_valid_trace_packet(packet: dict[str, Any]) -> None:
    errors = validate_trace_packet(packet)
    if errors:
        raise FormFieldTraceError("invalid form-field trace packet: " + "; ".join(errors))


def validate_trace_packet(packet: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(packet, dict):
        return ["packet must be an object"]

    missing_keys = sorted(REQUIRED_PACKET_KEYS.difference(packet.keys()))
    for key in missing_keys:
        errors.append(f"missing required packet key: {key}")

    if errors:
        return errors

    _validate_safety(packet.get("safety"), errors)

    evidence_by_id = _index_objects(packet.get("source_evidence"), "evidence_id", "source_evidence", errors)
    requirements_by_id = _index_objects(packet.get("requirements"), "requirement_id", "requirements", errors)
    user_facts_by_id = _index_objects(packet.get("user_facts"), "fact_id", "user_facts", errors)
    prompts_by_id = _index_objects(packet.get("missing_prompts"), "prompt_id", "missing_prompts", errors)
    devhub_fields_by_id = _index_objects(packet.get("devhub_fields"), "field_id", "devhub_fields", errors)
    pdf_fields_by_id = _index_objects(packet.get("pdf_fields"), "field_id", "pdf_fields", errors)

    for requirement in requirements_by_id.values():
        evidence_ids = requirement.get("source_evidence_ids")
        if not isinstance(evidence_ids, list) or not evidence_ids:
            errors.append(f"requirement {requirement.get('requirement_id')} must cite source evidence")
            continue
        for evidence_id in evidence_ids:
            if evidence_id not in evidence_by_id:
                errors.append(f"requirement {requirement.get('requirement_id')} cites unknown evidence {evidence_id}")

    for prompt in prompts_by_id.values():
        if prompt.get("fact_id") not in user_facts_by_id:
            errors.append(f"missing prompt {prompt.get('prompt_id')} references unknown fact {prompt.get('fact_id')}")

    field_traces = packet.get("field_traces")
    if not isinstance(field_traces, list) or not field_traces:
        errors.append("field_traces must be a non-empty list")
        return errors

    for index, trace in enumerate(field_traces):
        _validate_field_trace(
            trace,
            index,
            requirements_by_id,
            evidence_by_id,
            user_facts_by_id,
            prompts_by_id,
            devhub_fields_by_id,
            pdf_fields_by_id,
            errors,
        )

    return errors


def build_trace_index(packet: dict[str, Any]) -> dict[str, dict[str, Any]]:
    assert_valid_trace_packet(packet)
    return {trace["trace_id"]: trace for trace in packet["field_traces"]}


def preview_draft_values(packet: dict[str, Any]) -> dict[str, Any]:
    assert_valid_trace_packet(packet)
    values: dict[str, Any] = {}
    for trace in packet["field_traces"]:
        if trace.get("value_mode") == "preview_only" and trace.get("trace_status") == "ready_for_preview":
            values[trace["pdf_field_id"]] = trace.get("preview_draft_value")
    return values


def missing_prompt_ids(packet: dict[str, Any]) -> list[str]:
    assert_valid_trace_packet(packet)
    prompt_ids: list[str] = []
    for trace in packet["field_traces"]:
        if trace.get("missing_prompt_id"):
            prompt_ids.append(trace["missing_prompt_id"])
    return sorted(set(prompt_ids))


def _index_objects(value: Any, id_key: str, label: str, errors: list[str]) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    if not isinstance(value, list) or not value:
        errors.append(f"{label} must be a non-empty list")
        return indexed

    for offset, item in enumerate(value):
        if not isinstance(item, dict):
            errors.append(f"{label}[{offset}] must be an object")
            continue
        item_id = item.get(id_key)
        if not isinstance(item_id, str) or not item_id:
            errors.append(f"{label}[{offset}] must include non-empty {id_key}")
            continue
        if item_id in indexed:
            errors.append(f"duplicate {label} id: {item_id}")
            continue
        indexed[item_id] = item
    return indexed


def _validate_safety(value: Any, errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append("safety must be an object")
        return
    if value.get("fixture_only") is not True:
        errors.append("safety.fixture_only must be true")
    if value.get("preview_only") is not True:
        errors.append("safety.preview_only must be true")
    if value.get("contains_private_devhub_data") is not False:
        errors.append("safety.contains_private_devhub_data must be false")
    blocked_actions = value.get("blocked_actions")
    if not isinstance(blocked_actions, list) or "submission" not in blocked_actions:
        errors.append("safety.blocked_actions must include submission")


def _validate_field_trace(
    trace: Any,
    index: int,
    requirements_by_id: dict[str, dict[str, Any]],
    evidence_by_id: dict[str, dict[str, Any]],
    user_facts_by_id: dict[str, dict[str, Any]],
    prompts_by_id: dict[str, dict[str, Any]],
    devhub_fields_by_id: dict[str, dict[str, Any]],
    pdf_fields_by_id: dict[str, dict[str, Any]],
    errors: list[str],
) -> None:
    if not isinstance(trace, dict):
        errors.append(f"field_traces[{index}] must be an object")
        return

    trace_id = trace.get("trace_id")
    if not isinstance(trace_id, str) or not trace_id:
        errors.append(f"field_traces[{index}] must include trace_id")
        trace_id = f"field_traces[{index}]"

    _require_known(trace, "requirement_id", requirements_by_id, trace_id, errors)
    _require_known(trace, "source_evidence_id", evidence_by_id, trace_id, errors)
    _require_known(trace, "devhub_field_id", devhub_fields_by_id, trace_id, errors)
    _require_known(trace, "pdf_field_id", pdf_fields_by_id, trace_id, errors)

    field_source = trace.get("field_source")
    if field_source not in _ALLOWED_FIELD_SOURCES:
        errors.append(f"trace {trace_id} has unsupported field_source {field_source}")

    value_mode = trace.get("value_mode")
    if value_mode not in _ALLOWED_VALUE_MODES:
        errors.append(f"trace {trace_id} has unsupported value_mode {value_mode}")

    trace_status = trace.get("trace_status")
    if trace_status not in _ALLOWED_TRACE_STATUSES:
        errors.append(f"trace {trace_id} has unsupported trace_status {trace_status}")

    fact_id = trace.get("user_fact_id")
    prompt_id = trace.get("missing_prompt_id")
    preview_value_present = "preview_draft_value" in trace

    if field_source == "user_fact":
        if fact_id not in user_facts_by_id:
            errors.append(f"trace {trace_id} references unknown user_fact_id {fact_id}")
        if prompt_id is not None:
            errors.append(f"trace {trace_id} cannot include missing_prompt_id when sourced from user_fact")
        if value_mode != "preview_only" or not preview_value_present:
            errors.append(f"trace {trace_id} must include a preview-only draft value")

    if field_source == "missing_prompt":
        if prompt_id not in prompts_by_id:
            errors.append(f"trace {trace_id} references unknown missing_prompt_id {prompt_id}")
        if fact_id not in user_facts_by_id:
            errors.append(f"trace {trace_id} must still identify the missing user_fact_id")
        if value_mode != "not_drafted":
            errors.append(f"trace {trace_id} must not draft a value for a missing prompt")
        if preview_value_present and trace.get("preview_draft_value") not in (None, ""):
            errors.append(f"trace {trace_id} must not carry a draft value while blocked")

    if field_source == "constant":
        if value_mode != "preview_only" or not preview_value_present:
            errors.append(f"trace {trace_id} constant fields must include a preview-only value")


def _require_known(
    trace: dict[str, Any],
    key: str,
    known: dict[str, dict[str, Any]],
    trace_id: str,
    errors: list[str],
) -> None:
    value = trace.get(key)
    if value not in known:
        errors.append(f"trace {trace_id} references unknown {key} {value}")
