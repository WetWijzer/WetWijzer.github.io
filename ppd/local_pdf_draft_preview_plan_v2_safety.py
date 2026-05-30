from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any


REQUIRED_ATTESTATIONS = {
    "no_private_document",
    "no_pdf_read",
    "no_pdf_write",
    "no_upload",
    "no_devhub",
    "no_guardrail_mutation",
}

PRIVATE_PATH_PATTERNS = (
    re.compile(r"/home/[^\s,;]+"),
    re.compile(r"/Users/[^\s,;]+"),
    re.compile(r"[A-Za-z]:\\\\[^\s,;]+"),
    re.compile(r"file://", re.IGNORECASE),
)

RAW_PDF_OR_FORM_VALUE_KEYS = {
    "pdf_base64",
    "pdf_bytes",
    "pdf_binary",
    "raw_pdf",
    "raw_pdf_body",
    "raw_pdf_payload",
    "acroform_payload",
    "form_values",
    "raw_form_values",
    "field_values",
    "filled_values",
    "actual_form_values",
}

LIVE_PDF_OR_EXECUTION_KEYS = {
    "live_pdf_read",
    "live_pdf_write",
    "live_pdf_reads",
    "live_pdf_writes",
    "pdf_read_enabled",
    "pdf_write_enabled",
    "read_pdf_binary",
    "write_pdf_binary",
    "devhub_execution",
    "browser_execution",
    "crawler_execution",
    "processor_execution",
    "llm_execution",
    "live_devhub_execution",
    "live_browser_execution",
    "live_crawler_execution",
    "live_processor_execution",
    "live_llm_execution",
}

MUTATION_FLAG_KEYS = {
    "active_pdf_mutation",
    "active_document_mutation",
    "active_process_mutation",
    "active_process_model_mutation",
    "active_gap_analysis_mutation",
    "active_guardrail_mutation",
    "active_prompt_mutation",
    "active_release_state_mutation",
    "active_agent_state_mutation",
    "pdf_mutation_enabled",
    "document_mutation_enabled",
    "process_mutation_enabled",
    "gap_analysis_mutation_enabled",
    "guardrail_mutation_enabled",
    "prompt_mutation_enabled",
    "release_state_mutation",
    "agent_state_mutation",
}

RAW_PDF_MARKERS = (
    re.compile(r"%PDF-\d\.\d"),
    re.compile(r"%%EOF", re.IGNORECASE),
    re.compile(r"/AcroForm\b"),
    re.compile(r"\b(?:pdf_base64|raw_pdf_body|form_values|field_values)\b", re.IGNORECASE),
)

EXECUTION_CLAIM_PATTERNS = (
    re.compile(r"\b(?:ran|executed|launched|opened|drove|crawled|processed|called)\b.{0,48}\b(?:DevHub|browser|crawler|processor|LLM|language model)\b", re.IGNORECASE),
    re.compile(r"\b(?:DevHub|browser|crawler|processor|LLM|language model)\b.{0,48}\b(?:ran|executed|launched|opened|drove|crawled|processed|called)\b", re.IGNORECASE),
)

GUARANTEE_PATTERNS = (
    re.compile(r"\bguarantee(?:d|s)?\b.{0,48}\b(?:approval|permit|issuance|legal|compliance|outcome)\b", re.IGNORECASE),
    re.compile(r"\b(?:will|shall)\s+(?:be\s+)?(?:approved|issued|accepted|legally compliant)\b", re.IGNORECASE),
)

FINAL_ACTION_PATTERNS = (
    re.compile(r"\b(?:final|complete|execute|perform|proceed with|ready for|authorized for)\s+(?:permit\s+)?(?:submission|payment|upload|scheduling|cancellation)\b", re.IGNORECASE),
    re.compile(r"\b(?:submit|pay|upload|schedule|cancel)\b.{0,32}\b(?:now|automatically|without review|without confirmation|as final)\b", re.IGNORECASE),
)


class LocalPdfDraftPreviewPlanV2SafetyError(ValueError):
    pass


def validate_local_pdf_draft_preview_plan_v2(packet: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []

    if packet.get("packet_type") != "local_pdf_draft_preview_plan_v2":
        errors.append("packet_type must be local_pdf_draft_preview_plan_v2")
    if packet.get("fixture_first") is not True:
        errors.append("fixture_first must be true")
    if packet.get("preview_only") is not True:
        errors.append("preview_only must be true")

    evidence_ids = _evidence_ids(packet.get("source_evidence"))
    owner_fields = _owner_fields(packet.get("reviewer_owner_fields"))
    field_names = _field_names(packet.get("field_mapping_decisions"))

    _validate_field_mapping_decisions(packet.get("field_mapping_decisions"), evidence_ids, owner_fields, errors)
    _validate_blockers(packet, evidence_ids, owner_fields, field_names, errors)
    _validate_preview_safety(packet, errors)
    _validate_attestations(packet.get("attestations"), errors)
    _validate_forbidden_content(packet, errors)

    return errors


def assert_local_pdf_draft_preview_plan_v2_safe(packet: Mapping[str, Any]) -> None:
    errors = validate_local_pdf_draft_preview_plan_v2(packet)
    if errors:
        raise LocalPdfDraftPreviewPlanV2SafetyError("; ".join(errors))


def _validate_field_mapping_decisions(value: Any, evidence_ids: set[str], owner_fields: set[str], errors: list[str]) -> None:
    decisions = _sequence(value)
    if not decisions:
        errors.append("field_mapping_decisions must not be empty")
        return

    for index, decision in enumerate(decisions):
        if not isinstance(decision, Mapping):
            errors.append(f"field_mapping_decisions[{index}] must be an object")
            continue
        path = f"field_mapping_decisions[{index}]"
        if not _text(decision.get("pdf_field_name")):
            errors.append(path + ".pdf_field_name is required")
        decision_label = _text(decision.get("decision"))
        if not decision_label:
            errors.append(path + ".decision is required")
        citations = set(_strings(decision.get("source_evidence_ids")))
        if not citations:
            errors.append(path + " must cite source_evidence_ids")
        elif not citations.issubset(evidence_ids):
            errors.append(path + " cites unknown source evidence")
        owner = _text(decision.get("reviewer_owner_field"))
        if owner not in owner_fields:
            errors.append(path + ".reviewer_owner_field must reference reviewer_owner_fields")
        if decision_label.startswith("withhold") and not _text(decision.get("withheld_reason")):
            errors.append(path + " withholds a field without withheld_reason")


def _validate_blockers(packet: Mapping[str, Any], evidence_ids: set[str], owner_fields: set[str], field_names: set[str], errors: list[str]) -> None:
    fact_blockers = _sequence(packet.get("missing_fact_blockers"))
    document_blockers = _sequence(packet.get("missing_document_blockers"))
    blocked_fields: set[str] = set()

    if not fact_blockers:
        errors.append("missing_fact_blockers must not be empty")
    for index, blocker in enumerate(fact_blockers):
        if not isinstance(blocker, Mapping):
            errors.append(f"missing_fact_blockers[{index}] must be an object")
            continue
        path = f"missing_fact_blockers[{index}]"
        if not _text(blocker.get("blocker_id")):
            errors.append(path + ".blocker_id is required")
        if not _text(blocker.get("reason")):
            errors.append(path + ".reason is required")
        fields = set(_strings(blocker.get("blocks_field_names")))
        if not fields:
            errors.append(path + ".blocks_field_names must not be empty")
        elif not fields.issubset(field_names):
            errors.append(path + ".blocks_field_names must reference field_mapping_decisions")
        blocked_fields.update(fields)
        _require_known_citations(blocker, path, evidence_ids, errors)
        _require_known_owner(blocker, path, owner_fields, errors)

    if not document_blockers:
        errors.append("missing_document_blockers must not be empty")
    for index, blocker in enumerate(document_blockers):
        if not isinstance(blocker, Mapping):
            errors.append(f"missing_document_blockers[{index}] must be an object")
            continue
        path = f"missing_document_blockers[{index}]"
        for key in ("blocker_id", "document_label", "reason"):
            if not _text(blocker.get(key)):
                errors.append(path + f".{key} is required")
        if not _strings(blocker.get("source_fixture_finding_ids")):
            errors.append(path + ".source_fixture_finding_ids must not be empty")
        if not _strings(blocker.get("blocks_actions")):
            errors.append(path + ".blocks_actions must not be empty")
        _require_known_citations(blocker, path, evidence_ids, errors)
        _require_known_owner(blocker, path, owner_fields, errors)

    for decision in _sequence(packet.get("field_mapping_decisions")):
        if not isinstance(decision, Mapping):
            continue
        if _text(decision.get("decision")).startswith("withhold_until_missing_fact"):
            field_name = _text(decision.get("pdf_field_name"))
            if field_name and field_name not in blocked_fields:
                errors.append("withheld missing-fact field lacks a matching missing_fact_blocker")


def _validate_preview_safety(packet: Mapping[str, Any], errors: list[str]) -> None:
    expectations = packet.get("preview_only_artifact_expectations")
    if not isinstance(expectations, Mapping):
        errors.append("preview_only_artifact_expectations must be an object")
        return

    expected_false = {
        "may_read_pdf_binary",
        "may_write_pdf_binary",
        "may_create_private_document_copy",
        "may_upload_to_devhub",
        "may_mutate_guardrail_bundle",
    }
    for key in expected_false:
        if expectations.get(key) is not False:
            errors.append(f"preview_only_artifact_expectations.{key} must be false")


def _validate_attestations(value: Any, errors: list[str]) -> None:
    if not isinstance(value, Mapping):
        errors.append("attestations must be an object")
        return
    for key in sorted(REQUIRED_ATTESTATIONS):
        if value.get(key) is not True:
            errors.append(f"attestations.{key} must be true")


def _validate_forbidden_content(packet: Mapping[str, Any], errors: list[str]) -> None:
    for path, key, value in _walk(packet):
        normalized_key = _normalize_key(key)
        if normalized_key in RAW_PDF_OR_FORM_VALUE_KEYS:
            errors.append(path + " references raw PDF body or form values")
        if normalized_key in LIVE_PDF_OR_EXECUTION_KEYS and _truthy_or_nonempty(value):
            errors.append(path + " claims live PDF, DevHub, browser, crawler, processor, or LLM execution")
        if normalized_key in MUTATION_FLAG_KEYS and _truthy_or_nonempty(value):
            errors.append(path + " declares an active PDF, document, process, gap-analysis, guardrail, prompt, release-state, or agent-state mutation flag")
        if isinstance(value, str):
            if any(pattern.search(value) for pattern in PRIVATE_PATH_PATTERNS):
                errors.append(path + " contains a local private path")
            if any(pattern.search(value) for pattern in RAW_PDF_MARKERS):
                errors.append(path + " contains raw PDF body or form-value reference")
            if any(pattern.search(value) for pattern in EXECUTION_CLAIM_PATTERNS):
                errors.append(path + " contains live execution claim")
            if any(pattern.search(value) for pattern in GUARANTEE_PATTERNS):
                errors.append(path + " contains legal or permitting outcome guarantee")
            if any(pattern.search(value) for pattern in FINAL_ACTION_PATTERNS):
                errors.append(path + " contains final submission/payment/upload/scheduling/cancellation language")


def _require_known_citations(record: Mapping[str, Any], path: str, evidence_ids: set[str], errors: list[str]) -> None:
    citations = set(_strings(record.get("source_evidence_ids")))
    if not citations:
        errors.append(path + " must cite source_evidence_ids")
    elif not citations.issubset(evidence_ids):
        errors.append(path + " cites unknown source evidence")


def _require_known_owner(record: Mapping[str, Any], path: str, owner_fields: set[str], errors: list[str]) -> None:
    owner = _text(record.get("reviewer_owner_field"))
    if owner not in owner_fields:
        errors.append(path + ".reviewer_owner_field must reference reviewer_owner_fields")


def _evidence_ids(value: Any) -> set[str]:
    return {_text(item.get("evidence_id")) for item in _sequence(value) if isinstance(item, Mapping) and _text(item.get("evidence_id"))}


def _owner_fields(value: Any) -> set[str]:
    return {_text(item.get("field")) for item in _sequence(value) if isinstance(item, Mapping) and _text(item.get("field"))}


def _field_names(value: Any) -> set[str]:
    return {_text(item.get("pdf_field_name")) for item in _sequence(value) if isinstance(item, Mapping) and _text(item.get("pdf_field_name"))}


def _sequence(value: Any) -> Sequence[Any]:
    return value if isinstance(value, list) else []


def _strings(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [_text(item) for item in value if _text(item)]


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _normalize_key(key: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", key.lower()).strip("_")


def _truthy_or_nonempty(value: Any) -> bool:
    if value is False or value is None:
        return False
    if value == "":
        return False
    if isinstance(value, (list, dict, tuple, set)) and not value:
        return False
    return True


def _walk(value: Any, path: str = "$", key: str = ""):
    yield path, key, value
    if isinstance(value, Mapping):
        for child_key, child_value in value.items():
            child_key_text = str(child_key)
            yield from _walk(child_value, path + "." + child_key_text, child_key_text)
    elif isinstance(value, list):
        for index, child_value in enumerate(value):
            yield from _walk(child_value, f"{path}[{index}]", key)
