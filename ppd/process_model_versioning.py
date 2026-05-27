"""Fixture-only PP&D process model version validation.

This module validates committed synthetic process-model version records. It does
not crawl public sources, read DevHub, authenticate, submit, upload, pay, or
perform any live source lookup.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

READINESS_STATUSES = frozenset(
    {
        "blocked_pending_human_review",
        "blocked_pending_source_refresh",
        "ready_for_fixture_validation",
        "ready_for_guardrail_compile",
    }
)

REQUIRED_TOP_LEVEL_FIELDS = (
    "version_id",
    "process_id",
    "workflow_id",
    "permit_type",
    "narrow_scope",
    "fixture_policy",
    "source_evidence_hashes",
    "current_source_hashes",
    "process_stages",
    "requirement_ids",
    "guardrail_bundle_ids",
    "linked_requirement_evidence",
    "required_documents",
    "devhub_paths",
    "actions",
    "readiness_status",
    "blocked_reasons",
)

EVIDENCE_ID_FIELDS = (
    "source_evidence_ids",
    "source_evidence_id",
    "evidence_ids",
    "citation_source_ids",
    "stage_source_evidence_ids",
)

CITATION_SPAN_FIELDS = (
    "citation_spans",
    "source_citation_spans",
    "stage_citation_spans",
)

AUTOMATABLE_LEVELS = frozenset({"automatable", "reversible_draft", "agent_allowed"})
MANUAL_ONLY_LEVELS = frozenset({"manual_only", "manual_handoff", "unsupported", "not_automatable"})
FINANCIAL_BOUNDARY_CLASSES = frozenset(
    {
        "financial_boundary",
        "fee_payment_boundary",
        "fee_or_payment_boundary",
        "payment_boundary",
        "manual_financial_handoff",
        "requires_exact_confirmation",
    }
)


def load_process_model_version_fixture(path: Path) -> dict[str, Any]:
    """Load a process-model version fixture from a repository-local JSON file."""

    return json.loads(path.read_text(encoding="utf-8"))


def validate_process_model_version(record: Mapping[str, Any]) -> list[str]:
    """Return validation errors for a synthetic process-model version record."""

    errors: list[str] = []
    for field in REQUIRED_TOP_LEVEL_FIELDS:
        if field not in record:
            errors.append(f"missing required field: {field}")

    if errors:
        return errors

    _validate_text_field(record, "version_id", errors)
    _validate_text_field(record, "process_id", errors)
    _validate_text_field(record, "workflow_id", errors)
    _validate_text_field(record, "permit_type", errors)
    _validate_text_field(record, "narrow_scope", errors)

    fixture_policy = record.get("fixture_policy")
    if not isinstance(fixture_policy, Mapping):
        errors.append("fixture_policy must be an object")
    else:
        if fixture_policy.get("fixture_only") is not True:
            errors.append("fixture_policy.fixture_only must be true")
        if fixture_policy.get("live_source_reads_allowed") is not False:
            errors.append("fixture_policy.live_source_reads_allowed must be false")
        if fixture_policy.get("authenticated_devhub_reads_allowed") is not False:
            errors.append("fixture_policy.authenticated_devhub_reads_allowed must be false")

    evidence_rows = record.get("source_evidence_hashes")
    evidence_ids: set[str] = set()
    if not isinstance(evidence_rows, list) or not evidence_rows:
        errors.append("source_evidence_hashes must be a non-empty list")
    else:
        for index, evidence in enumerate(evidence_rows):
            if not isinstance(evidence, Mapping):
                errors.append(f"source_evidence_hashes[{index}] must be an object")
                continue
            evidence_id = evidence.get("source_evidence_id")
            if not isinstance(evidence_id, str) or not evidence_id.strip():
                errors.append(f"source_evidence_hashes[{index}].source_evidence_id is required")
            else:
                evidence_ids.add(evidence_id)
            digest = evidence.get("content_sha256")
            if not _is_sha256_hex(digest):
                errors.append(f"source_evidence_hashes[{index}].content_sha256 must be a sha256 hex digest")
            if evidence.get("synthetic_excerpt") is not True:
                errors.append(f"source_evidence_hashes[{index}].synthetic_excerpt must be true")
            if evidence.get("live_read_performed") is not False:
                errors.append(f"source_evidence_hashes[{index}].live_read_performed must be false")
            if evidence.get("hash_status") == "stale" or evidence.get("is_current") is False:
                errors.append(f"source_evidence_hashes[{index}] must not be marked stale")

    _validate_current_source_hashes(record, evidence_rows, errors)

    requirement_ids = _validate_text_list(record, "requirement_ids", errors)
    guardrail_bundle_ids = _validate_text_list(record, "guardrail_bundle_ids", errors)
    blocked_reasons = _validate_optional_text_list(record, "blocked_reasons", errors)

    if len(requirement_ids) != len(set(requirement_ids)):
        errors.append("requirement_ids must be unique")
    if len(guardrail_bundle_ids) != len(set(guardrail_bundle_ids)):
        errors.append("guardrail_bundle_ids must be unique")

    readiness_status = record.get("readiness_status")
    if readiness_status not in READINESS_STATUSES:
        errors.append("readiness_status is not recognized")
    if isinstance(readiness_status, str) and readiness_status.startswith("blocked") and not blocked_reasons:
        errors.append("blocked readiness statuses require at least one blocked reason")

    links = record.get("linked_requirement_evidence")
    if not isinstance(links, Mapping) or not links:
        errors.append("linked_requirement_evidence must be a non-empty object")
    else:
        for requirement_id, linked_evidence_ids in links.items():
            if requirement_id not in requirement_ids:
                errors.append(f"linked_requirement_evidence references unknown requirement: {requirement_id}")
            if not isinstance(linked_evidence_ids, list) or not linked_evidence_ids:
                errors.append(f"linked_requirement_evidence[{requirement_id}] must be a non-empty list")
                continue
            for evidence_id in linked_evidence_ids:
                if evidence_id not in evidence_ids:
                    errors.append(
                        f"linked_requirement_evidence[{requirement_id}] references unknown evidence: {evidence_id}"
                    )

    _validate_process_stages(record, evidence_ids, errors)
    _validate_required_documents(record, requirement_ids, evidence_ids, errors)
    _validate_devhub_paths(record, errors)
    _validate_actions(record, errors)

    return errors


def _validate_current_source_hashes(
    record: Mapping[str, Any], evidence_rows: Any, errors: list[str]
) -> None:
    current_hashes = record.get("current_source_hashes")
    if not isinstance(current_hashes, Mapping) or not current_hashes:
        errors.append("current_source_hashes must be a non-empty object")
        return

    for evidence_id, digest in current_hashes.items():
        if not isinstance(evidence_id, str) or not evidence_id.strip():
            errors.append("current_source_hashes keys must be non-empty strings")
        if not _is_sha256_hex(digest):
            errors.append(f"current_source_hashes[{evidence_id}] must be a sha256 hex digest")

    if not isinstance(evidence_rows, list):
        return

    for index, evidence in enumerate(evidence_rows):
        if not isinstance(evidence, Mapping):
            continue
        evidence_id = evidence.get("source_evidence_id")
        digest = evidence.get("content_sha256")
        if not isinstance(evidence_id, str) or not evidence_id.strip():
            continue
        if evidence_id not in current_hashes:
            errors.append(f"source_evidence_hashes[{index}] lacks a current source hash")
            continue
        if current_hashes[evidence_id] != digest:
            errors.append(f"source_evidence_hashes[{index}] has stale content_sha256 for {evidence_id}")


def _validate_process_stages(record: Mapping[str, Any], evidence_ids: set[str], errors: list[str]) -> None:
    stages = record.get("process_stages")
    if not isinstance(stages, list) or not stages:
        errors.append("process_stages must be a non-empty list")
        return

    seen_stage_ids: set[str] = set()
    for index, stage in enumerate(stages):
        if not isinstance(stage, Mapping):
            errors.append(f"process_stages[{index}] must be an object")
            continue
        stage_id = stage.get("stage_id") or stage.get("id")
        if not isinstance(stage_id, str) or not stage_id.strip():
            errors.append(f"process_stages[{index}].stage_id is required")
        elif stage_id in seen_stage_ids:
            errors.append(f"process_stages[{index}].stage_id must be unique")
        else:
            seen_stage_ids.add(stage_id)
        citation_ids = _evidence_refs(stage)
        if not citation_ids and not _has_citation_spans(stage):
            errors.append(f"process_stages[{index}] must cite source evidence or citation spans")
        for evidence_id in citation_ids:
            if evidence_id not in evidence_ids:
                errors.append(f"process_stages[{index}] references unknown evidence: {evidence_id}")


def _validate_required_documents(
    record: Mapping[str, Any], requirement_ids: list[str], evidence_ids: set[str], errors: list[str]
) -> None:
    documents = record.get("required_documents")
    if not isinstance(documents, list):
        errors.append("required_documents must be a list")
        return

    for index, document in enumerate(documents):
        if not isinstance(document, Mapping):
            errors.append(f"required_documents[{index}] must be an object")
            continue
        document_id = document.get("document_id") or document.get("id") or document.get("key")
        if not isinstance(document_id, str) or not document_id.strip():
            errors.append(f"required_documents[{index}].document_id is required")
        linked_requirements = _string_list(document.get("requirement_ids") or document.get("linked_requirement_ids"))
        if not linked_requirements:
            errors.append(f"required_documents[{index}] must link to at least one requirement_id")
        for requirement_id in linked_requirements:
            if requirement_id not in requirement_ids:
                errors.append(f"required_documents[{index}] references unknown requirement: {requirement_id}")
        linked_evidence = _evidence_refs(document)
        if not linked_evidence:
            errors.append(f"required_documents[{index}] must link to source evidence")
        for evidence_id in linked_evidence:
            if evidence_id not in evidence_ids:
                errors.append(f"required_documents[{index}] references unknown evidence: {evidence_id}")


def _validate_devhub_paths(record: Mapping[str, Any], errors: list[str]) -> None:
    paths = record.get("devhub_paths")
    if not isinstance(paths, list):
        errors.append("devhub_paths must be a list")
        return

    for index, path in enumerate(paths):
        if not isinstance(path, Mapping):
            errors.append(f"devhub_paths[{index}] must be an object")
            continue
        path_id = path.get("path_id") or path.get("id") or path.get("route") or f"index {index}"
        unsupported = _is_unsupported_devhub_path(path)
        automatable = _is_marked_automatable(path)
        if unsupported and automatable:
            errors.append(f"devhub_paths[{index}] unsupported path {path_id!r} must not be marked automatable")


def _validate_actions(record: Mapping[str, Any], errors: list[str]) -> None:
    actions = record.get("actions")
    if not isinstance(actions, list):
        errors.append("actions must be a list")
        return

    for index, action in enumerate(actions):
        if not isinstance(action, Mapping):
            errors.append(f"actions[{index}] must be an object")
            continue
        if not _is_fee_or_payment_action(action):
            continue
        boundary = action.get("financial_boundary_classification") or action.get("financial_boundary")
        if boundary not in FINANCIAL_BOUNDARY_CLASSES:
            errors.append(
                f"actions[{index}] fee/payment action must include a supported financial-boundary classification"
            )


def _validate_text_field(record: Mapping[str, Any], field: str, errors: list[str]) -> None:
    value = record.get(field)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{field} must be a non-empty string")


def _validate_text_list(record: Mapping[str, Any], field: str, errors: list[str]) -> list[str]:
    value = record.get(field)
    if not isinstance(value, list) or not value:
        errors.append(f"{field} must be a non-empty list")
        return []

    return _validate_list_items(value, field, errors)


def _validate_optional_text_list(record: Mapping[str, Any], field: str, errors: list[str]) -> list[str]:
    value = record.get(field)
    if not isinstance(value, list):
        errors.append(f"{field} must be a list")
        return []

    return _validate_list_items(value, field, errors)


def _validate_list_items(value: list[Any], field: str, errors: list[str]) -> list[str]:
    result: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            errors.append(f"{field}[{index}] must be a non-empty string")
        else:
            result.append(item)
    return result


def _evidence_refs(record: Mapping[str, Any]) -> list[str]:
    refs: list[str] = []
    for field in EVIDENCE_ID_FIELDS:
        refs.extend(_string_list(record.get(field)))
    return refs


def _string_list(value: Any) -> list[str]:
    if isinstance(value, str) and value.strip():
        return [value]
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str) and item.strip()]


def _has_citation_spans(record: Mapping[str, Any]) -> bool:
    return any(bool(record.get(field)) for field in CITATION_SPAN_FIELDS)


def _is_unsupported_devhub_path(path: Mapping[str, Any]) -> bool:
    status = _lower(path.get("support_status") or path.get("supported_path_status"))
    route_type = _lower(path.get("route_type") or path.get("official_channel"))
    return (
        path.get("supported_in_devhub") is False
        or path.get("supported") is False
        or status in {"unsupported", "manual_only", "not_supported"}
        or route_type in {"manual", "manual_only", "offline", "non_devhub", "phone", "in_person"}
    )


def _is_marked_automatable(path: Mapping[str, Any]) -> bool:
    level = _lower(path.get("automation_level") or path.get("automation_status"))
    if path.get("automatable") is True or path.get("automation_supported") is True:
        return True
    if level in AUTOMATABLE_LEVELS:
        return True
    return level not in {"", *MANUAL_ONLY_LEVELS} and path.get("automatable") is not False


def _is_fee_or_payment_action(action: Mapping[str, Any]) -> bool:
    text = " ".join(
        _lower(action.get(field))
        for field in ("action_id", "id", "kind", "action_kind", "label", "name", "description")
    )
    boundary = _lower(action.get("boundary_type") or action.get("action_boundary"))
    return any(token in text for token in ("fee", "payment", "pay", "purchase")) or boundary in {
        "fee",
        "payment",
        "fee_payment",
        "financial",
    }


def _lower(value: Any) -> str:
    return str(value).strip().lower() if value is not None else ""


def _is_sha256_hex(value: Any) -> bool:
    if not isinstance(value, str) or len(value) != 64:
        return False
    try:
        int(value, 16)
    except ValueError:
        return False
    return True
