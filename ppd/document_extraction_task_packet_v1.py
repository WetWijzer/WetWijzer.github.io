"""Fixture-first document extraction task packet v1 for Portland PP&D.

The builder consumes a coverage gap prioritization packet fixture and committed
DocumentRecord fixtures, then emits offline-only extraction work items for one
narrow document family. It does not read private files, download documents,
execute OCR, persist raw PDFs, claim live processor work, promise legal or
permitting outcomes, propose consequential actions, or mutate active PP&D state.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

PACKET_TYPE = "fixture_first_document_extraction_task_packet_v1"
DOCUMENT_FAMILY = "single_pdf_process_guidance"

TARGET_TYPES = (
    "sections",
    "tables",
    "checklist_items",
    "fillable_field_labels",
    "signature_certification_blocks",
    "citation_spans",
)

EXTRACTION_TARGET_FIELDS = (
    "target_type",
    "fixture_input_ref",
    "expected_fixture_output_ref",
)

REQUIRED_WORK_ITEM_FIELDS = (
    "work_item_id",
    "document_family",
    "target_type",
    "title",
    "priority_row_id",
    "affected_document_id",
    "affected_source_id",
    "citation",
    "fixture_input_ref",
    "expected_fixture_output_ref",
    "human_review_status",
    "reviewer_owner",
    "rollback_note",
    "offline_validation_commands",
)

HUMAN_REVIEW_STATUSES = {"needs_review", "in_review", "approved", "rejected"}

_FORBIDDEN_ARTIFACT_KEYS = {
    "auth",
    "authenticated_artifact",
    "authenticated_artifacts",
    "auth_state",
    "authorization",
    "body",
    "cookie",
    "cookies",
    "credential",
    "credentials",
    "devhub_session",
    "download_path",
    "downloaded_document",
    "downloaded_documents",
    "downloaded_pdf",
    "har",
    "har_path",
    "mfa",
    "ocr_output",
    "ocr_text",
    "password",
    "pdf_bytes",
    "private_artifact",
    "private_artifacts",
    "private_file",
    "private_file_path",
    "raw_body",
    "raw_content",
    "raw_crawl_output",
    "raw_download",
    "raw_html",
    "raw_pdf",
    "response_body",
    "screenshot",
    "session",
    "session_file",
    "storage_state",
    "token",
    "trace",
    "warc_path",
}

_LIVE_PROCESSOR_KEYS = {
    "extraction_executed",
    "live_extraction",
    "live_extraction_claim",
    "live_processor_claim",
    "live_processor_run",
    "processor_artifact",
    "processor_claim",
    "processor_output",
    "processor_run_id",
}

_OUTCOME_GUARANTEE_KEYS = {
    "approval_guarantee",
    "compliance_guarantee",
    "guaranteed_outcome",
    "legal_advice",
    "legal_determination",
    "permit_approval_guarantee",
    "permitting_outcome_guarantee",
}

_CONSEQUENTIAL_ACTION_KEYS = {
    "cancel_request",
    "certify_acknowledgement",
    "consequential_action",
    "execute_payment",
    "official_upload",
    "pay_fee",
    "purchase_permit",
    "schedule_inspection",
    "submit_application",
    "submit_permit",
    "upload_correction",
}

_MUTATION_KEYS = {
    "active_agent_state_mutation",
    "active_document_mutation",
    "active_guardrail_mutation",
    "active_process_mutation",
    "active_release_state_mutation",
    "active_requirement_mutation",
    "active_source_mutation",
    "agent_state_mutation",
    "document_mutation",
    "guardrail_mutation",
    "mutates_agent_state",
    "mutates_documents",
    "mutates_guardrails",
    "mutates_processes",
    "mutates_release_state",
    "mutates_requirements",
    "mutates_sources",
    "process_mutation",
    "promotes_document_record",
    "release_state_mutation",
    "requirement_mutation",
    "source_mutation",
    "updates_active_document_record",
    "updates_documents",
}

_FORBIDDEN_PHRASE_CODES = (
    ("forbidden_private_authenticated_or_raw_artifact", ("authenticated artifact", "auth state", "cookie", "downloaded pdf", "downloaded the document", "private file", "raw pdf saved", "stored session", "trace saved")),
    ("forbidden_live_extraction_or_processor_claim", ("live extraction", "processor executed", "processor ran", "ran the processor", "ocr executed", "ocr ran")),
    ("forbidden_legal_or_permitting_outcome_guarantee", ("approval guaranteed", "compliance guaranteed", "guarantee approval", "legally sufficient", "permit will be approved", "will pass inspection")),
    ("forbidden_consequential_action_language", ("cancel the permit", "certify acknowledgement", "pay the fee", "purchase the permit", "schedule inspection", "submit permit", "submit the application", "upload correction")),
    ("active_ppd_state_mutation", ("updated active document", "mutated active source", "promoted requirement", "changed release state", "updated agent state")),
)


@dataclass(frozen=True)
class DocumentExtractionTaskViolation:
    code: str
    path: str
    message: str


class DocumentExtractionTaskPacketError(ValueError):
    """Raised when a document extraction task packet is unsafe or malformed."""

    def __init__(self, violations: list[DocumentExtractionTaskViolation]) -> None:
        self.violations = violations
        codes = ", ".join(sorted({violation.code for violation in violations}))
        super().__init__(f"invalid document extraction task packet v1: {codes}")


def load_json(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"expected object fixture at {path}")
    return data


def build_document_extraction_task_packet_v1(
    prioritization_packet: Mapping[str, Any],
    document_records: Mapping[str, Any],
    *,
    document_family: str = DOCUMENT_FAMILY,
) -> dict[str, Any]:
    documents = [
        document
        for document in _objects(document_records.get("documents"))
        if _text(document.get("extraction_family")) == document_family
    ]
    if not documents:
        raise ValueError(f"no document records found for family {document_family}")

    priority_rows = [
        row
        for row in _priority_rows(prioritization_packet)
        if _text(row.get("expected_follow_up_fixture_family")) == document_family
    ]
    if not priority_rows:
        raise ValueError(f"no prioritization rows found for family {document_family}")

    work_items: list[dict[str, Any]] = []
    for document in sorted(documents, key=lambda item: _text(item.get("document_id"))):
        for target_type in TARGET_TYPES:
            priority_row = _select_priority_row(priority_rows, target_type)
            source_id = _first_text(document.get("source_id"), priority_row.get("affected_source_ids", [""]))
            work_items.append(
                {
                    "work_item_id": f"doc-extract-v1:{document_family}:{_slug(target_type)}:{_text(document.get('document_id'))}",
                    "document_family": document_family,
                    "target_type": target_type,
                    "title": f"Extract {target_type.replace('_', ' ')} from {_text(document.get('title'))}",
                    "priority_row_id": _text(priority_row.get("priority_row_id")),
                    "affected_document_id": _text(document.get("document_id")),
                    "affected_source_id": source_id,
                    "citation": _citation(document, priority_row, target_type, source_id),
                    "fixture_input_ref": f"document_records:{_text(document.get('document_id'))}",
                    "expected_fixture_output_ref": f"ppd/tests/fixtures/document_extraction_task_packet_v1/{document_family}_{target_type}.json",
                    "source_gap_category": _text(priority_row.get("category")),
                    "severity": _text(priority_row.get("severity")),
                    "dependency_order": priority_row.get("dependency_order"),
                    "human_review_status": "needs_review",
                    "reviewer_owner": _text(priority_row.get("reviewer_owner"), "ppd-document-extraction-reviewer"),
                    "rollback_note": "Fixture-only extraction task; remove this generated packet and expected fixture output if the cited document fixture changes.",
                    "offline_validation_commands": _offline_validation_commands(),
                }
            )

    packet = {
        "packet_type": PACKET_TYPE,
        "packet_id": f"document-extraction-task-packet-v1:{document_family}",
        "document_family": document_family,
        "source_packets": {
            "coverage_gap_prioritization_packet_id": prioritization_packet.get("packet_id"),
            "document_records_fixture_id": document_records.get("fixture_id"),
        },
        "safety_attestations": {
            "fixture_first_only": True,
            "no_private_files_read": True,
            "no_authenticated_artifacts": True,
            "no_document_downloads": True,
            "no_ocr_execution": True,
            "no_raw_pdf_persistence": True,
            "no_live_extraction_or_processor_execution": True,
            "no_legal_or_permitting_outcome_guarantees": True,
            "no_consequential_actions": True,
            "no_active_state_mutation": True,
        },
        "target_types": list(TARGET_TYPES),
        "work_items": work_items,
        "offline_validation_commands": _offline_validation_commands(),
    }
    assert_valid_document_extraction_task_packet_v1(packet)
    return packet


def build_document_extraction_task_packet_from_paths(paths: Mapping[str, str | Path]) -> dict[str, Any]:
    return build_document_extraction_task_packet_v1(
        prioritization_packet=load_json(paths["coverage_gap_prioritization_packet"]),
        document_records=load_json(paths["document_records"]),
    )


def validate_document_extraction_task_packet_v1(packet: Mapping[str, Any]) -> list[DocumentExtractionTaskViolation]:
    violations: list[DocumentExtractionTaskViolation] = []
    if packet.get("packet_type") != PACKET_TYPE:
        violations.append(_violation("invalid_packet_type", "packet_type", "unexpected document extraction task packet type"))

    if _text(packet.get("document_family")) != DOCUMENT_FAMILY:
        violations.append(_violation("invalid_document_family", "document_family", "packet must target the narrow single PDF process guidance family"))

    attestations = packet.get("safety_attestations")
    if not isinstance(attestations, Mapping):
        violations.append(_violation("missing_safety_attestations", "safety_attestations", "safety attestations are required"))
    else:
        for key in (
            "fixture_first_only",
            "no_private_files_read",
            "no_authenticated_artifacts",
            "no_document_downloads",
            "no_ocr_execution",
            "no_raw_pdf_persistence",
            "no_live_extraction_or_processor_execution",
            "no_legal_or_permitting_outcome_guarantees",
            "no_consequential_actions",
            "no_active_state_mutation",
        ):
            if attestations.get(key) is not True:
                violations.append(_violation("missing_safety_attestation", f"safety_attestations.{key}", "required safety attestation must be true"))

    if tuple(packet.get("target_types", ())) != TARGET_TYPES:
        violations.append(_violation("missing_target_coverage", "target_types", "packet must cover all required extraction target types in order"))

    work_items = packet.get("work_items")
    if not isinstance(work_items, list) or not work_items:
        violations.append(_violation("missing_work_items", "work_items", "work items must be a non-empty list"))
    else:
        seen_targets: set[str] = set()
        for index, item in enumerate(work_items):
            path = f"work_items[{index}]"
            if not isinstance(item, Mapping):
                violations.append(_violation("invalid_work_item", path, "work item must be an object"))
                continue
            seen_targets.add(_text(item.get("target_type")))
            violations.extend(_validate_work_item(item, path))
        missing_targets = set(TARGET_TYPES) - seen_targets
        if missing_targets:
            violations.append(_violation("missing_target_coverage", "work_items", "work items missing required target types: " + ", ".join(sorted(missing_targets))))

    violations.extend(_validate_offline_commands(packet.get("offline_validation_commands"), "offline_validation_commands"))
    violations.extend(_validate_forbidden_content(packet, "$"))
    return violations


def assert_valid_document_extraction_task_packet_v1(packet: Mapping[str, Any]) -> None:
    violations = validate_document_extraction_task_packet_v1(packet)
    if violations:
        raise DocumentExtractionTaskPacketError(violations)


def is_valid_document_extraction_task_packet_v1(packet: Mapping[str, Any]) -> bool:
    return not validate_document_extraction_task_packet_v1(packet)


def _validate_work_item(item: Mapping[str, Any], path: str) -> list[DocumentExtractionTaskViolation]:
    violations: list[DocumentExtractionTaskViolation] = []
    for field in REQUIRED_WORK_ITEM_FIELDS:
        if field not in item:
            violations.append(_violation("missing_required_field", f"{path}.{field}", "required work item field is missing"))

    for field in EXTRACTION_TARGET_FIELDS:
        if not _text(item.get(field)):
            violations.append(_violation("missing_extraction_target_field", f"{path}.{field}", "extraction target field is required"))

    if _text(item.get("document_family")) != DOCUMENT_FAMILY:
        violations.append(_violation("invalid_document_family", f"{path}.document_family", "work item must stay within the selected document family"))
    if _text(item.get("target_type")) not in TARGET_TYPES:
        violations.append(_violation("invalid_target_type", f"{path}.target_type", "target type is not allowed"))
    if not _text(item.get("priority_row_id")):
        violations.append(_violation("missing_priority_row_id", f"{path}.priority_row_id", "priority row id is required"))
    if not _text(item.get("affected_document_id")):
        violations.append(_violation("missing_document_id", f"{path}.affected_document_id", "affected document id is required"))
    if not _text(item.get("affected_source_id")):
        violations.append(_violation("missing_source_id", f"{path}.affected_source_id", "affected source id is required"))

    citation = item.get("citation")
    if not isinstance(citation, Mapping):
        violations.append(_violation("uncited_work_item", f"{path}.citation", "work item must include source id, document id, public URL, and anchor citation"))
    else:
        for field in ("source_id", "document_id", "url", "anchor"):
            if not _text(citation.get(field)):
                violations.append(_violation("uncited_work_item", f"{path}.citation.{field}", "citation field is required"))
        if _text(citation.get("source_id")) and citation.get("source_id") != item.get("affected_source_id"):
            violations.append(_violation("citation_source_mismatch", f"{path}.citation.source_id", "citation source must match affected source"))
        if _text(citation.get("document_id")) and citation.get("document_id") != item.get("affected_document_id"):
            violations.append(_violation("citation_document_mismatch", f"{path}.citation.document_id", "citation document must match affected document"))

    if _text(item.get("human_review_status")) not in HUMAN_REVIEW_STATUSES:
        violations.append(_violation("missing_human_review_status", f"{path}.human_review_status", "human review status is required"))
    if not _text(item.get("reviewer_owner")):
        violations.append(_violation("missing_reviewer_owner", f"{path}.reviewer_owner", "reviewer owner is required"))
    if not _text(item.get("rollback_note")):
        violations.append(_violation("missing_rollback_note", f"{path}.rollback_note", "rollback note is required"))
    violations.extend(_validate_offline_commands(item.get("offline_validation_commands"), f"{path}.offline_validation_commands"))
    return violations


def _validate_offline_commands(value: Any, path: str) -> list[DocumentExtractionTaskViolation]:
    if not isinstance(value, list) or not value:
        return [_violation("missing_offline_validation_commands", path, "offline validation commands are required")]
    violations: list[DocumentExtractionTaskViolation] = []
    for index, command in enumerate(value):
        if not isinstance(command, list) or not command or not all(isinstance(part, str) and part for part in command):
            violations.append(_violation("invalid_offline_validation_command", f"{path}[{index}]", "validation command must be a non-empty list of strings"))
        elif any(part in {"curl", "wget", "playwright", "ocrmypdf", "tesseract"} for part in command):
            violations.append(_violation("unsafe_validation_command", f"{path}[{index}]", "validation command must remain offline and fixture-only"))
    return violations


def _validate_forbidden_content(value: Any, path: str) -> list[DocumentExtractionTaskViolation]:
    violations: list[DocumentExtractionTaskViolation] = []
    if isinstance(value, Mapping):
        for key, nested in value.items():
            key_text = str(key)
            normalized_key = key_text.lower()
            next_path = f"{path}.{key_text}"
            if normalized_key in _FORBIDDEN_ARTIFACT_KEYS:
                violations.append(_violation("forbidden_private_authenticated_or_raw_artifact", next_path, "private, authenticated, raw, downloaded, session, OCR, or raw PDF artifact is forbidden"))
            if normalized_key in _LIVE_PROCESSOR_KEYS and bool(nested):
                violations.append(_violation("forbidden_live_extraction_or_processor_claim", next_path, "live extraction and processor execution claims are forbidden"))
            if normalized_key in _OUTCOME_GUARANTEE_KEYS and bool(nested):
                violations.append(_violation("forbidden_legal_or_permitting_outcome_guarantee", next_path, "legal or permitting outcome guarantees are forbidden"))
            if normalized_key in _CONSEQUENTIAL_ACTION_KEYS and bool(nested):
                violations.append(_violation("forbidden_consequential_action_language", next_path, "consequential official action language is forbidden"))
            if normalized_key in _MUTATION_KEYS and bool(nested):
                violations.append(_violation("active_ppd_state_mutation", next_path, "active source, document, requirement, process, guardrail, release-state, or agent-state mutation flags are forbidden"))
            violations.extend(_validate_forbidden_content(nested, next_path))
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            violations.extend(_validate_forbidden_content(nested, f"{path}[{index}]"))
    elif isinstance(value, str):
        lowered = value.lower()
        for code, phrases in _FORBIDDEN_PHRASE_CODES:
            if any(phrase in lowered for phrase in phrases):
                violations.append(_violation(code, path, "forbidden safety-sensitive language is present"))
    return violations


def _priority_rows(packet: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    rows = packet.get("ordered_review_candidates")
    if isinstance(rows, list):
        return [row for row in rows if isinstance(row, Mapping)]
    groups = packet.get("priority_groups")
    if isinstance(groups, list):
        flattened: list[Mapping[str, Any]] = []
        for group in groups:
            if isinstance(group, Mapping):
                flattened.extend(row for row in group.get("rows", []) if isinstance(row, Mapping))
        return flattened
    return []


def _select_priority_row(rows: list[Mapping[str, Any]], target_type: str) -> Mapping[str, Any]:
    for row in rows:
        if target_type in _strings(row.get("target_extraction_types")):
            return row
    return rows[0]


def _citation(document: Mapping[str, Any], priority_row: Mapping[str, Any], target_type: str, source_id: str) -> dict[str, str]:
    spans = [span for span in _objects(document.get("citation_spans")) if _text(span.get("target_type")) == target_type]
    if spans:
        span = spans[0]
        citation = priority_row.get("citation") if isinstance(priority_row.get("citation"), Mapping) else {}
        return {
            "source_id": source_id,
            "document_id": _text(document.get("document_id")),
            "citation_span_id": _text(span.get("citation_span_id")),
            "url": _first_text(span.get("url"), document.get("canonical_url"), citation.get("url")),
            "anchor": _first_text(span.get("anchor"), citation.get("anchor"), target_type),
        }
    citation = priority_row.get("citation") if isinstance(priority_row.get("citation"), Mapping) else {}
    return {
        "source_id": source_id,
        "document_id": _text(document.get("document_id")),
        "citation_span_id": f"fixture-span:{target_type}",
        "url": _first_text(document.get("canonical_url"), citation.get("url")),
        "anchor": _first_text(citation.get("anchor"), target_type),
    }


def _offline_validation_commands() -> list[list[str]]:
    return [
        ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
        ["python3", "-m", "pytest", "ppd/tests/test_document_extraction_task_packet_v1.py"],
    ]


def _objects(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _strings(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [_text(item) for item in value if _text(item)]


def _text(value: Any, default: str = "") -> str:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return default


def _first_text(*values: Any) -> str:
    for value in values:
        if isinstance(value, list) and value:
            value = value[0]
        text = _text(value)
        if text:
            return text
    return ""


def _slug(value: str) -> str:
    return "".join(character if character.isalnum() else "-" for character in value.lower()).strip("-")


def _violation(code: str, path: str, message: str) -> DocumentExtractionTaskViolation:
    return DocumentExtractionTaskViolation(code=code, path=path, message=message)
