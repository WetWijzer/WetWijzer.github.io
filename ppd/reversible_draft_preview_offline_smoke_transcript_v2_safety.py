from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

from ppd.reversible_draft_preview_offline_smoke_transcript_v2 import PACKET_TYPE, REQUIRED_OUTPUT_IDS


PRIVATE_CASE_FACT_KEYS = {
    "private_case_fact",
    "private_case_facts",
    "case_private_facts",
    "private_applicant_value",
    "private_applicant_values",
    "private_owner_value",
    "private_owner_values",
    "applicant_email",
    "applicant_phone",
    "owner_email",
    "owner_phone",
    "tax_id",
    "ssn",
}

PRIVATE_PATH_KEYS = {
    "local_private_path",
    "local_private_paths",
    "local_private_document_path",
    "local_private_document_paths",
    "private_document_path",
    "private_document_paths",
    "source_pdf_path",
    "pdf_file_path",
    "document_file_path",
}

RAW_VALUE_KEYS = {
    "raw_authenticated_value",
    "raw_authenticated_values",
    "authenticated_value",
    "authenticated_values",
    "raw_devhub_value",
    "raw_devhub_values",
    "raw_pdf_value",
    "raw_pdf_values",
    "pdf_value",
    "pdf_values",
    "pdf_base64",
    "pdf_bytes",
    "pdf_binary",
    "raw_pdf",
    "raw_pdf_body",
    "raw_pdf_payload",
    "form_values",
    "raw_form_values",
    "field_values",
    "filled_values",
}

LIVE_EXECUTION_KEYS = {
    "live_llm_execution",
    "live_devhub_execution",
    "live_browser_execution",
    "live_pdf_execution",
    "live_pdf_read",
    "live_pdf_write",
    "live_crawler_execution",
    "live_processor_execution",
    "llm_execution",
    "devhub_execution",
    "browser_execution",
    "pdf_execution",
    "crawler_execution",
    "processor_execution",
    "live_llm_used",
    "devhub_accessed",
}

MUTATION_FLAG_KEYS = {
    "active_prompt_mutation",
    "active_guardrail_mutation",
    "active_pdf_mutation",
    "active_gap_analysis_mutation",
    "active_monitoring_mutation",
    "active_release_state_mutation",
    "active_agent_state_mutation",
    "prompt_mutation_enabled",
    "guardrail_mutation_enabled",
    "pdf_mutation_enabled",
    "gap_analysis_mutation_enabled",
    "monitoring_mutation_enabled",
    "release_state_mutation_enabled",
    "agent_state_mutation_enabled",
}


class ReversibleDraftPreviewOfflineSmokeTranscriptV2SafetyError(ValueError):
    pass


def validate_reversible_draft_preview_offline_smoke_transcript_v2_safety(packet: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []

    if packet.get("packet_type") != PACKET_TYPE:
        errors.append("packet_type must identify reversible draft preview offline smoke transcript v2")
    if packet.get("mode") != "fixture_first_offline_smoke_transcript":
        errors.append("mode must be fixture_first_offline_smoke_transcript")

    _validate_expected_outputs(packet.get("expected_agent_outputs"), errors)
    _validate_forbidden_content(packet, errors)
    return errors


def assert_reversible_draft_preview_offline_smoke_transcript_v2_safe(packet: Mapping[str, Any]) -> None:
    errors = validate_reversible_draft_preview_offline_smoke_transcript_v2_safety(packet)
    if errors:
        raise ReversibleDraftPreviewOfflineSmokeTranscriptV2SafetyError("; ".join(errors))


def _validate_expected_outputs(value: Any, errors: list[str]) -> None:
    outputs = value if isinstance(value, list) else []
    output_ids = [str(output.get("output_id")) for output in outputs if isinstance(output, Mapping)]
    if output_ids != list(REQUIRED_OUTPUT_IDS):
        errors.append("expected_agent_outputs must include all required output scenarios in order")

    seen_missing_information = False
    seen_refusal = False
    for index, output in enumerate(outputs):
        path = f"expected_agent_outputs[{index}]"
        if not isinstance(output, Mapping):
            errors.append(path + " must be an object")
            continue
        output_id = _text(output.get("output_id"))
        expected = _text(output.get("expected_agent_output"))
        if not expected:
            errors.append(path + ".expected_agent_output is required")
        if not _strings(output.get("citations")):
            errors.append(path + " must include citations")
        if not _strings(output.get("source_packet_roles")):
            errors.append(path + " must include source_packet_roles")
        lowered = expected.lower()
        if output_id == "missing_information_followups":
            seen_missing_information = "missing" in lowered and ("followup" in lowered or "ask" in lowered)
        if output_id == "refusal_of_consequential_actions":
            seen_refusal = "refus" in lowered and ("must not" in lowered or "do not" in lowered)

    if not seen_missing_information:
        errors.append("missing_information_followups scenario is required")
    if not seen_refusal:
        errors.append("refusal_of_consequential_actions scenario is required")


def _validate_forbidden_content(packet: Mapping[str, Any], errors: list[str]) -> None:
    for path, key, value in _walk(packet):
        normalized_key = _normalize_key(key)
        if normalized_key in PRIVATE_CASE_FACT_KEYS and _truthy_or_nonempty(value):
            errors.append(path + " contains private case facts")
        if normalized_key in PRIVATE_PATH_KEYS and _truthy_or_nonempty(value):
            errors.append(path + " contains a local private path")
        if normalized_key in RAW_VALUE_KEYS and _truthy_or_nonempty(value):
            errors.append(path + " contains raw authenticated or PDF values")
        if normalized_key in LIVE_EXECUTION_KEYS and _truthy_or_nonempty(value):
            errors.append(path + " claims live LLM, DevHub, browser, PDF, crawler, or processor execution")
        if normalized_key in MUTATION_FLAG_KEYS and _truthy_or_nonempty(value):
            errors.append(path + " declares an active prompt, guardrail, PDF, gap-analysis, monitoring, release-state, or agent-state mutation flag")
        if isinstance(value, str):
            lowered = value.lower()
            if _contains_private_path(lowered):
                errors.append(path + " contains a local private path")
            if _contains_raw_value_marker(lowered):
                errors.append(path + " contains raw authenticated or PDF values")
            if _contains_live_execution_claim(lowered):
                errors.append(path + " contains live execution claim")
            if _contains_outcome_guarantee(lowered):
                errors.append(path + " contains legal or permitting outcome guarantee")
            if _contains_final_action_language(lowered):
                errors.append(path + " contains final submission/payment/upload/scheduling/cancellation language")
            if _contains_active_mutation_language(lowered):
                errors.append(path + " declares an active prompt, guardrail, PDF, gap-analysis, monitoring, release-state, or agent-state mutation flag")


def _contains_private_path(value: str) -> bool:
    return "/home/" in value or "/users/" in value or "c:/users/" in value or "file://" in value


def _contains_raw_value_marker(value: str) -> bool:
    markers = (
        "%pdf-",
        "%%eof",
        "/acroform",
        "raw_authenticated",
        "raw devhub",
        "raw_devhub",
        "raw_pdf",
        "pdf_base64",
        "pdf bytes",
        "form_values",
        "field_values",
    )
    return any(marker in value for marker in markers)


def _contains_live_execution_claim(value: str) -> bool:
    if any(negative in value for negative in ("no live", "not live", "must not", "do not", "without live")):
        return False
    target = r"(llm|language model|devhub|browser|pdf|crawler|processor)"
    verb = r"(ran|executed|launched|opened|drove|read|wrote|crawled|processed|called|accessed|loaded)"
    return bool(re.search(target + r".{0,40}" + verb, value) or re.search(verb + r".{0,40}" + target, value))


def _contains_outcome_guarantee(value: str) -> bool:
    if "guarantee" in value and any(target in value for target in ("approval", "permit", "issuance", "legal", "compliance", "outcome")):
        return True
    phrases = (
        "will be approved",
        "shall be approved",
        "will be issued",
        "shall be issued",
        "will be accepted",
        "legally compliant",
        "permit approval is assured",
    )
    return any(phrase in value for phrase in phrases)


def _contains_final_action_language(value: str) -> bool:
    if "must not" in value or "do not" in value or "not a " in value:
        return False
    final_targets = ("submission", "payment", "upload", "scheduling", "cancellation")
    if any("final " + target in value for target in final_targets):
        return True
    guarded_prefixes = ("ready for", "authorized for", "cleared for", "approved for", "proceed with", "execute", "perform", "complete")
    if any(prefix in value for prefix in guarded_prefixes) and any(target in value for target in final_targets):
        return True
    action_verbs = ("submit", "pay", "upload", "schedule", "cancel")
    unsafe_suffixes = ("now", "automatically", "without review", "without confirmation", "as final")
    return any(verb in value for verb in action_verbs) and any(suffix in value for suffix in unsafe_suffixes)


def _contains_active_mutation_language(value: str) -> bool:
    if "active" not in value and "enabled" not in value:
        return False
    return "mutation" in value and any(target in value for target in ("prompt", "guardrail", "pdf", "gap-analysis", "gap analysis", "monitoring", "release-state", "release state", "agent-state", "agent state"))


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _strings(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


def _normalize_key(key: str) -> str:
    return "_".join("".join(character if character.isalnum() else " " for character in key.lower()).split())


def _truthy_or_nonempty(value: Any) -> bool:
    if value is False or value is None or value == "":
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
