from __future__ import annotations

from collections.abc import Mapping
from typing import Any


REQUIRED_ATTESTATIONS = {
    "no_private_documents",
    "no_pdf_write",
    "no_upload",
    "no_devhub",
    "no_agent_state_mutation",
}

PRIVATE_CASE_FACT_KEYS = {
    "private_case_fact",
    "private_case_facts",
    "case_private_facts",
    "private_applicant_value",
    "private_applicant_values",
    "private_owner_value",
    "private_owner_values",
    "applicant_phone",
    "applicant_email",
    "owner_phone",
    "owner_email",
    "tax_id",
    "ssn",
}

PRIVATE_DOCUMENT_PATH_KEYS = {
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
    "live_devhub_execution",
    "live_browser_execution",
    "live_pdf_execution",
    "live_pdf_read",
    "live_pdf_write",
    "live_llm_execution",
    "live_crawler_execution",
    "live_processor_execution",
    "devhub_execution",
    "browser_execution",
    "pdf_execution",
    "llm_execution",
    "crawler_execution",
    "processor_execution",
}

MUTATION_FLAG_KEYS = {
    "active_pdf_mutation",
    "active_gap_analysis_mutation",
    "active_guardrail_mutation",
    "active_prompt_mutation",
    "active_release_state_mutation",
    "active_agent_state_mutation",
    "pdf_mutation_enabled",
    "gap_analysis_mutation_enabled",
    "guardrail_mutation_enabled",
    "prompt_mutation_enabled",
    "release_state_mutation",
    "agent_state_mutation",
}


class LocalDraftPreviewReviewPacketV2SafetyError(ValueError):
    pass


def validate_local_draft_preview_review_packet_v2(packet: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []

    if packet.get("packet_version") != "local-draft-preview-review-packet-v2":
        errors.append("packet_version must be local-draft-preview-review-packet-v2")
    if packet.get("mode") != "fixture-first-offline":
        errors.append("mode must be fixture-first-offline")

    _validate_preview_rows(packet.get("reviewer_visible_preview_rows"), errors)
    _validate_blockers(packet.get("unresolved_blocker_summaries"), errors)
    _validate_gap_checkpoints(packet.get("gap_analysis_checkpoints"), errors)
    _validate_attestations(packet.get("attestations"), errors)
    _validate_forbidden_content(packet, errors)

    return errors


def assert_local_draft_preview_review_packet_v2_safe(packet: Mapping[str, Any]) -> None:
    errors = validate_local_draft_preview_review_packet_v2(packet)
    if errors:
        raise LocalDraftPreviewReviewPacketV2SafetyError("; ".join(errors))


def _validate_preview_rows(value: Any, errors: list[str]) -> None:
    rows = value if isinstance(value, list) else []
    if not rows:
        errors.append("reviewer_visible_preview_rows must not be empty")
        return
    for index, row in enumerate(rows):
        path = f"reviewer_visible_preview_rows[{index}]"
        if not isinstance(row, Mapping):
            errors.append(path + " must be an object")
            continue
        for key in ("row_id", "reviewer_visible_value", "reviewer_owner", "rollback_note"):
            if not _text(row.get(key)):
                errors.append(path + f".{key} is required")
        if not _text(row.get("citation")):
            errors.append(path + " must include citation")
        if not _text(row.get("value_explanation")):
            errors.append(path + " must include source-backed value_explanation")
        if not _text(row.get("confirmation_checkpoint")):
            errors.append(path + " must include exact confirmation_checkpoint")


def _validate_blockers(value: Any, errors: list[str]) -> None:
    blockers = value if isinstance(value, list) else []
    for index, blocker in enumerate(blockers):
        path = f"unresolved_blocker_summaries[{index}]"
        if not isinstance(blocker, Mapping):
            errors.append(path + " must be an object")
            continue
        for key in ("blocker_id", "summary", "owner", "citation"):
            if not _text(blocker.get(key)):
                errors.append(path + f".{key} is required")


def _validate_gap_checkpoints(value: Any, errors: list[str]) -> None:
    checkpoints = value if isinstance(value, list) else []
    if not checkpoints:
        errors.append("gap_analysis_checkpoints must not be empty")
        return
    for index, checkpoint in enumerate(checkpoints):
        path = f"gap_analysis_checkpoints[{index}]"
        if not isinstance(checkpoint, Mapping):
            errors.append(path + " must be an object")
            continue
        for key in ("gap_id", "summary", "exact_confirmation", "owner"):
            if not _text(checkpoint.get(key)):
                errors.append(path + f".{key} is required")


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
        if normalized_key in PRIVATE_CASE_FACT_KEYS and _truthy_or_nonempty(value):
            errors.append(path + " contains private case facts")
        if normalized_key in PRIVATE_DOCUMENT_PATH_KEYS and _truthy_or_nonempty(value):
            errors.append(path + " contains a local private document path")
        if normalized_key in RAW_VALUE_KEYS and _truthy_or_nonempty(value):
            errors.append(path + " contains raw authenticated or PDF values")
        if normalized_key in LIVE_EXECUTION_KEYS and _truthy_or_nonempty(value):
            errors.append(path + " claims live DevHub, browser, PDF, LLM, crawler, or processor execution")
        if normalized_key in MUTATION_FLAG_KEYS and _truthy_or_nonempty(value):
            errors.append(path + " declares an active PDF, gap-analysis, guardrail, prompt, release-state, or agent-state mutation flag")
        if isinstance(value, str):
            lower = value.lower()
            if _contains_private_path(lower):
                errors.append(path + " contains a local private path")
            if _contains_raw_value_marker(lower):
                errors.append(path + " contains raw authenticated or PDF values")
            if _contains_live_execution_claim(lower):
                errors.append(path + " contains live execution claim")
            if _contains_outcome_guarantee(lower):
                errors.append(path + " contains legal or permitting outcome guarantee")
            if _contains_final_action_language(lower):
                errors.append(path + " contains final submission/payment/upload/scheduling/cancellation language")


def _contains_private_path(value: str) -> bool:
    return "/home/" in value or "/users/" in value or "file://" in value


def _contains_raw_value_marker(value: str) -> bool:
    markers = ("%pdf-", "%%eof", "/acroform", "raw_authenticated", "raw_devhub", "pdf_base64", "raw_pdf", "form_values", "field_values")
    return any(marker in value for marker in markers)


def _contains_live_execution_claim(value: str) -> bool:
    targets = ("devhub", "browser", "pdf", "llm", "language model", "crawler", "processor")
    verbs = ("ran", "executed", "launched", "opened", "drove", "read", "wrote", "crawled", "processed", "called")
    return any(target in value for target in targets) and any(verb in value for verb in verbs)


def _contains_outcome_guarantee(value: str) -> bool:
    guaranteed_targets = ("approval", "permit", "issuance", "legal", "compliance", "outcome")
    if "guarantee" in value and any(target in value for target in guaranteed_targets):
        return True
    return any(phrase in value for phrase in ("will be approved", "shall be approved", "will be issued", "shall be issued", "will be accepted", "legally compliant"))


def _contains_final_action_language(value: str) -> bool:
    final_targets = ("submission", "payment", "upload", "scheduling", "cancellation")
    if any(("final " + target) in value for target in final_targets):
        return True
    guarded_prefixes = ("ready for", "authorized for", "cleared for", "approved for", "proceed with", "execute", "perform", "complete")
    if any(prefix in value for prefix in guarded_prefixes) and any(target in value for target in final_targets):
        return True
    action_verbs = ("submit", "pay", "upload", "schedule", "cancel")
    unsafe_suffixes = ("now", "automatically", "without review", "without confirmation", "as final")
    return any(verb in value for verb in action_verbs) and any(suffix in value for suffix in unsafe_suffixes)


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _normalize_key(key: str) -> str:
    return "_".join("".join(character if character.isalnum() else " " for character in key.lower()).split())


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
