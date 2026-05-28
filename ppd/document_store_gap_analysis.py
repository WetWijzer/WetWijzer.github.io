"""Fixture-first document-store gap analysis for PP&D user cases.

This module compares synthetic user facts and synthetic document metadata to a
single synthetic ProcessModel-like fixture. It never reads private user files and
rejects committed fixtures that expose local paths.
"""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path
from typing import Any

_DEFAULT_FIXTURE = (
    Path(__file__).parent
    / "tests"
    / "fixtures"
    / "document_store_gap_analysis"
    / "synthetic_single_pdf_case.json"
)
_LOCAL_PATH_PATTERNS = (
    re.compile(r"(?:^|[\"'\s])/(?:home|Users|tmp|var|private|mnt|Volumes)/"),
    re.compile(r"[A-Za-z]:\\\\"),
    re.compile(r"file://"),
)
_CONSEQUENTIAL_CLASSIFICATIONS = {"official_upload", "certification", "submission", "payment"}


class DocumentStoreGapAnalysisError(ValueError):
    """Raised when a synthetic gap-analysis fixture is invalid or unsafe."""


def load_document_store_gap_analysis_packet(
    *,
    fixture_path: Path | None = None,
) -> dict[str, Any]:
    """Load, validate, and analyze the committed synthetic gap-analysis fixture."""

    path = fixture_path or _DEFAULT_FIXTURE
    payload = json.loads(path.read_text(encoding="utf-8"))
    return analyze_document_store_gap(payload)


def analyze_document_store_gap(payload: dict[str, Any]) -> dict[str, Any]:
    """Compare synthetic case facts and document metadata to one process model."""

    _validate_payload(payload)
    process = payload["process_model"]
    case_facts = {fact["id"]: fact for fact in payload.get("case_facts", [])}
    documents = payload.get("document_store_metadata", [])
    as_of = _parse_date(payload["as_of"])

    known_facts: list[dict[str, Any]] = []
    missing_facts: list[dict[str, Any]] = []
    ambiguous_facts: list[dict[str, Any]] = []
    conflicting_facts: list[dict[str, Any]] = []

    for required_fact in process.get("required_user_facts", []):
        fact = case_facts.get(required_fact["id"])
        if fact is None or fact.get("status") == "missing":
            missing_facts.append(_fact_gap(required_fact, "missing"))
        elif fact.get("status") == "ambiguous":
            ambiguous_facts.append(_fact_gap(required_fact, "ambiguous", fact))
        elif fact.get("status") == "conflicting":
            conflicting_facts.append(_fact_gap(required_fact, "conflicting", fact))
        else:
            known_facts.append(
                {
                    "fact_id": required_fact["id"],
                    "label": required_fact["label"],
                    "status": fact.get("status", "known"),
                    "source_document_id": fact.get("source_document_id"),
                }
            )

    matched_documents: list[dict[str, Any]] = []
    missing_documents: list[dict[str, Any]] = []
    stale_evidence: list[dict[str, Any]] = []

    for required_document in process.get("required_documents", []):
        matches = [
            document
            for document in documents
            if required_document["id"] in document.get("satisfies_document_ids", [])
        ]
        if not matches:
            missing_documents.append(
                {
                    "document_id": required_document["id"],
                    "name": required_document["name"],
                    "reason": "no matching document metadata in synthetic store",
                }
            )
            continue

        for document in matches:
            matched_documents.append(
                {
                    "required_document_id": required_document["id"],
                    "document_id": document["document_id"],
                    "title": document["title"],
                    "document_type": document["document_type"],
                }
            )
            max_age_days = required_document.get("max_age_days")
            evidence_date = document.get("evidence_date")
            if isinstance(max_age_days, int) and evidence_date:
                age_days = (as_of - _parse_date(evidence_date)).days
                if age_days > max_age_days:
                    stale_evidence.append(
                        {
                            "document_id": document["document_id"],
                            "required_document_id": required_document["id"],
                            "evidence_date": evidence_date,
                            "age_days": age_days,
                            "max_age_days": max_age_days,
                            "reason": "evidence is older than the process model freshness limit",
                        }
                    )

    conflicting_evidence = _document_conflicts(documents) + conflicting_facts
    required_confirmations = _required_confirmations(process, ambiguous_facts, conflicting_evidence, stale_evidence)
    blockers = _blocker_ids(missing_facts, missing_documents, stale_evidence, conflicting_evidence, ambiguous_facts)
    blocked_actions = _blocked_actions(process, blockers)

    return {
        "case_id": payload["case_id"],
        "process_id": process["process_id"],
        "analysis_as_of": payload["as_of"],
        "known_facts": known_facts,
        "matched_documents": matched_documents,
        "missing_facts": missing_facts,
        "missing_documents": missing_documents,
        "stale_evidence": stale_evidence,
        "conflicting_evidence": conflicting_evidence,
        "ambiguous_facts": ambiguous_facts,
        "blocked_actions": blocked_actions,
        "required_confirmations": required_confirmations,
        "next_safe_prompts": _next_safe_prompts(missing_facts, missing_documents, ambiguous_facts, conflicting_evidence, stale_evidence),
        "privacy": {
            "fixture_only": True,
            "reads_private_files": False,
            "stores_private_paths": False,
        },
    }


def _validate_payload(payload: dict[str, Any]) -> None:
    required_top_level = ("case_id", "as_of", "process_model", "case_facts", "document_store_metadata")
    for key in required_top_level:
        if key not in payload:
            raise DocumentStoreGapAnalysisError(f"fixture missing {key}")

    process = payload["process_model"]
    if not isinstance(process, dict) or not process.get("process_id"):
        raise DocumentStoreGapAnalysisError("fixture must include one process_model with process_id")
    if not isinstance(process.get("required_user_facts"), list):
        raise DocumentStoreGapAnalysisError("process_model.required_user_facts must be a list")
    if not isinstance(process.get("required_documents"), list):
        raise DocumentStoreGapAnalysisError("process_model.required_documents must be a list")

    serialized = json.dumps(payload, sort_keys=True)
    for pattern in _LOCAL_PATH_PATTERNS:
        if pattern.search(serialized):
            raise DocumentStoreGapAnalysisError("fixture must not contain local private file paths")

    for document in payload.get("document_store_metadata", []):
        forbidden = {"local_path", "file_path", "absolute_path", "source_path"}
        exposed = sorted(forbidden.intersection(document))
        if exposed:
            raise DocumentStoreGapAnalysisError(f"document {document.get('document_id')} exposes path fields: {exposed}")


def _parse_date(value: str) -> date:
    return date.fromisoformat(value)


def _fact_gap(required_fact: dict[str, Any], status: str, fact: dict[str, Any] | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {
        "fact_id": required_fact["id"],
        "label": required_fact["label"],
        "status": status,
        "prompt": required_fact.get("prompt", f"Confirm {required_fact['label']}"),
    }
    if fact:
        result["source_document_id"] = fact.get("source_document_id")
        result["notes"] = tuple(fact.get("notes", ()))
    return result


def _document_conflicts(documents: list[dict[str, Any]]) -> list[dict[str, Any]]:
    conflicts: list[dict[str, Any]] = []
    for document in documents:
        for conflict in document.get("conflicts", []):
            conflicts.append(
                {
                    "document_id": document["document_id"],
                    "fact_id": conflict["fact_id"],
                    "document_value": conflict["document_value"],
                    "conflicts_with": conflict["conflicts_with"],
                    "reason": conflict.get("reason", "document metadata conflicts with case fact"),
                }
            )
    return conflicts


def _required_confirmations(
    process: dict[str, Any],
    ambiguous_facts: list[dict[str, Any]],
    conflicting_evidence: list[dict[str, Any]],
    stale_evidence: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    confirmations: list[dict[str, Any]] = []
    for gate in process.get("action_gates", []):
        if gate.get("classification") in _CONSEQUENTIAL_CLASSIFICATIONS:
            confirmations.append(
                {
                    "confirmation_id": gate["id"],
                    "action_id": gate["id"],
                    "text": gate.get("required_confirmation", "Exact user confirmation required."),
                }
            )
    for fact in ambiguous_facts:
        confirmations.append(
            {
                "confirmation_id": f"confirm_{fact['fact_id']}",
                "fact_id": fact["fact_id"],
                "text": fact["prompt"],
            }
        )
    if conflicting_evidence:
        confirmations.append(
            {
                "confirmation_id": "resolve_conflicting_evidence",
                "text": "Resolve conflicting synthetic facts before drafting or staging uploads.",
            }
        )
    if stale_evidence:
        confirmations.append(
            {
                "confirmation_id": "refresh_stale_evidence",
                "text": "Confirm refreshed evidence before relying on stale synthetic document metadata.",
            }
        )
    return confirmations


def _blocker_ids(
    missing_facts: list[dict[str, Any]],
    missing_documents: list[dict[str, Any]],
    stale_evidence: list[dict[str, Any]],
    conflicting_evidence: list[dict[str, Any]],
    ambiguous_facts: list[dict[str, Any]],
) -> set[str]:
    blockers = {item["fact_id"] for item in missing_facts}
    blockers.update(item["document_id"] for item in missing_documents)
    blockers.update(item["required_document_id"] for item in stale_evidence)
    blockers.update(item["fact_id"] for item in conflicting_evidence if item.get("fact_id"))
    blockers.update(item["fact_id"] for item in ambiguous_facts)
    return blockers


def _blocked_actions(process: dict[str, Any], blockers: set[str]) -> list[dict[str, Any]]:
    blocked: list[dict[str, Any]] = []
    for action in process.get("action_gates", []):
        action_blockers = [item for item in action.get("blocks_until", []) if item in blockers]
        if action_blockers or action.get("classification") in _CONSEQUENTIAL_CLASSIFICATIONS:
            blocked.append(
                {
                    "action_id": action["id"],
                    "name": action["name"],
                    "classification": action.get("classification"),
                    "blocked_by": action_blockers,
                    "requires_exact_confirmation": bool(action.get("required_confirmation")),
                }
            )
    return blocked


def _next_safe_prompts(
    missing_facts: list[dict[str, Any]],
    missing_documents: list[dict[str, Any]],
    ambiguous_facts: list[dict[str, Any]],
    conflicting_evidence: list[dict[str, Any]],
    stale_evidence: list[dict[str, Any]],
) -> list[str]:
    prompts: list[str] = []
    prompts.extend(item["prompt"] for item in missing_facts)
    prompts.extend(f"Provide or identify metadata for {item['name']}." for item in missing_documents)
    prompts.extend(item["prompt"] for item in ambiguous_facts)
    if conflicting_evidence:
        prompts.append("Which synthetic fact value should control where the documents disagree?")
    if stale_evidence:
        prompts.append("Can you confirm whether the stale evidence has been refreshed?")
    return prompts


__all__ = [
    "DocumentStoreGapAnalysisError",
    "analyze_document_store_gap",
    "load_document_store_gap_analysis_packet",
]
