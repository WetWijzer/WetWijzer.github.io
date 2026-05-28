"""Fixture-first PP&D process-model assembly packet.

This module assembles already-reviewed RequirementNode candidates into a narrow
synthetic ProcessModel shape. It is intentionally deterministic and fixture-only:
it does not crawl, log in to DevHub, upload files, submit applications, pay fees,
or infer facts from private user data.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable, Mapping


REVIEWED_STATUSES = frozenset({"reviewed", "approved", "accepted", "human_reviewed"})

STANDARD_STAGE_ORDER = (
    "pre-application research",
    "account setup or manual login",
    "property lookup",
    "permit type selection",
    "eligibility screening",
    "document preparation",
    "application data entry",
    "upload staging",
    "acknowledgement/certification review",
    "submission",
    "prescreen/intake",
    "fee payment",
    "plan review",
    "corrections/checksheets",
    "approval/issuance",
    "inspections",
    "closeout, cancellation, expiration, extension, or reactivation",
)

_STAGE_INDEX = {stage: index for index, stage in enumerate(STANDARD_STAGE_ORDER)}


class ProcessModelAssemblyError(ValueError):
    """Raised when a fixture cannot be assembled into a safe packet."""


def load_assembly_fixture(path: str | Path) -> dict[str, Any]:
    """Load a committed JSON assembly fixture."""

    fixture_path = Path(path)
    with fixture_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ProcessModelAssemblyError("assembly fixture must be a JSON object")
    return payload


def assemble_process_model_packet_from_fixture(path: str | Path) -> dict[str, Any]:
    """Load and assemble a fixture-first process-model packet."""

    return assemble_process_model_packet(load_assembly_fixture(path))


def assemble_process_model_packet(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Assemble reviewed RequirementNode candidates into a ProcessModel packet.

    The accepted fixture shape is intentionally small: metadata, source evidence,
    optional guardrail bundle linkage, and ``requirement_node_candidates``. Only
    candidates with reviewed/approved/accepted human review status are assembled.
    Every assembled item must cite committed ``source_evidence_ids``.
    """

    process_id = _required_text(payload, "process_id")
    permit_type = _required_text(payload, "permit_type")
    scope = _required_text(payload, "scope")
    guardrail_bundle_id = _required_text(payload, "guardrail_bundle_id")
    evidence_ids = _committed_evidence_ids(payload.get("source_evidence"))

    raw_candidates = payload.get("requirement_node_candidates")
    if not isinstance(raw_candidates, list) or not raw_candidates:
        raise ProcessModelAssemblyError("requirement_node_candidates must be a non-empty list")

    reviewed_nodes = [
        _normalize_node(candidate, evidence_ids)
        for candidate in raw_candidates
        if _is_reviewed(candidate)
    ]
    if not reviewed_nodes:
        raise ProcessModelAssemblyError("at least one reviewed requirement node is required")
    reviewed_nodes.sort(key=lambda node: node["requirement_id"])

    assembled_evidence_ids = _sorted_unique(
        evidence_id for node in reviewed_nodes for evidence_id in node["source_evidence_ids"]
    )

    process_model = {
        "process_id": process_id,
        "permit_type": permit_type,
        "scope": scope,
        "eligibility_rules": _summaries(reviewed_nodes, {"precondition", "license_requirement"}),
        "required_user_facts": _required_user_facts(reviewed_nodes),
        "required_documents": _required_documents(reviewed_nodes),
        "file_rules": _file_rules(reviewed_nodes),
        "fees": _summaries(reviewed_nodes, {"fee_trigger"}),
        "stages": _stages(reviewed_nodes),
        "deadlines": _summaries(reviewed_nodes, {"deadline"}),
        "exceptions": _summaries(reviewed_nodes, {"exception"}),
        "unsupported_paths": _unsupported_paths(reviewed_nodes),
        "devhub_surface_refs": _devhub_surface_refs(reviewed_nodes),
        "guardrail_bundle_id": guardrail_bundle_id,
        "source_evidence_ids": assembled_evidence_ids,
    }

    guardrail_bundle_linkage = {
        "guardrail_bundle_id": guardrail_bundle_id,
        "process_id": process_id,
        "reviewed_requirement_node_ids": [node["requirement_id"] for node in reviewed_nodes],
        "source_evidence_ids": assembled_evidence_ids,
        "linkage_status": "fixture_linked",
    }

    packet = {
        "packet_type": "fixture_first_process_model_assembly",
        "process_model": process_model,
        "reviewed_requirement_nodes": reviewed_nodes,
        "guardrail_bundle_linkage": guardrail_bundle_linkage,
    }
    _validate_packet(packet)
    return packet


def _validate_packet(packet: Mapping[str, Any]) -> None:
    model = packet["process_model"]
    required_lists = (
        "required_user_facts",
        "required_documents",
        "file_rules",
        "fees",
        "unsupported_paths",
        "exceptions",
        "stages",
        "deadlines",
    )
    missing = [key for key in required_lists if not model.get(key)]
    if missing:
        raise ProcessModelAssemblyError("assembled process model is missing: " + ", ".join(missing))
    if model["guardrail_bundle_id"] != packet["guardrail_bundle_linkage"]["guardrail_bundle_id"]:
        raise ProcessModelAssemblyError("guardrail bundle linkage must match process model")


def _is_reviewed(candidate: Any) -> bool:
    if not isinstance(candidate, Mapping):
        return False
    status = _text(candidate.get("human_review_status") or candidate.get("review_status") or candidate.get("status"))
    return status.lower() in REVIEWED_STATUSES


def _normalize_node(candidate: Any, committed_evidence_ids: set[str]) -> dict[str, Any]:
    if not isinstance(candidate, Mapping):
        raise ProcessModelAssemblyError("requirement node candidates must be objects")

    requirement_id = _required_text(candidate, "requirement_id")
    source_evidence_ids = candidate.get("source_evidence_ids")
    if not isinstance(source_evidence_ids, list) or not source_evidence_ids:
        raise ProcessModelAssemblyError(f"{requirement_id} must include source_evidence_ids")

    normalized_evidence = []
    for evidence_id in source_evidence_ids:
        evidence_text = _text(evidence_id)
        if not evidence_text:
            raise ProcessModelAssemblyError(f"{requirement_id} has an empty evidence id")
        if evidence_text not in committed_evidence_ids:
            raise ProcessModelAssemblyError(
                f"{requirement_id} references uncommitted evidence id {evidence_text}"
            )
        normalized_evidence.append(evidence_text)

    conditions = candidate.get("conditions") or {}
    if not isinstance(conditions, Mapping):
        raise ProcessModelAssemblyError(f"{requirement_id} conditions must be an object")

    return {
        "requirement_id": requirement_id,
        "source_evidence_ids": _sorted_unique(normalized_evidence),
        "requirement_type": _required_text(candidate, "requirement_type"),
        "subject": _text(candidate.get("subject")),
        "action": _required_text(candidate, "action"),
        "object": _required_text(candidate, "object"),
        "conditions": _stable_jsonable(dict(conditions)),
        "deadline_or_temporal_scope": _text(candidate.get("deadline_or_temporal_scope")),
        "permit_types": _text_list(candidate.get("permit_types")),
        "process_stage": _required_text(candidate, "process_stage"),
        "confidence": candidate.get("confidence", "fixture"),
        "human_review_status": _text(candidate.get("human_review_status") or candidate.get("status")),
        "formalization_status": _text(candidate.get("formalization_status")) or "assembly_candidate",
    }


def _committed_evidence_ids(source_evidence: Any) -> set[str]:
    if not isinstance(source_evidence, list) or not source_evidence:
        raise ProcessModelAssemblyError("source_evidence must be a non-empty list")
    evidence_ids: set[str] = set()
    for entry in source_evidence:
        if not isinstance(entry, Mapping):
            raise ProcessModelAssemblyError("source_evidence entries must be objects")
        evidence_ids.add(_required_text(entry, "evidence_id"))
    return evidence_ids


def _summaries(nodes: list[dict[str, Any]], requirement_types: set[str]) -> list[dict[str, Any]]:
    return sorted(
        [_summary(node) for node in nodes if node["requirement_type"] in requirement_types],
        key=lambda item: item["requirement_id"],
    )


def _summary(node: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "requirement_id": node["requirement_id"],
        "requirement_type": node["requirement_type"],
        "subject": node["subject"],
        "action": node["action"],
        "object": node["object"],
        "process_stage": node["process_stage"],
        "source_evidence_ids": node["source_evidence_ids"],
    }


def _required_user_facts(nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    facts = []
    for node in nodes:
        conditions = node["conditions"]
        fact_key = _text(conditions.get("required_user_fact") or conditions.get("fact_key"))
        if fact_key:
            facts.append(
                {
                    "fact_key": fact_key,
                    "label": _text(conditions.get("fact_label")) or node["object"],
                    "requirement_id": node["requirement_id"],
                    "process_stage": node["process_stage"],
                    "source_evidence_ids": node["source_evidence_ids"],
                }
            )
    return sorted(facts, key=lambda item: (item["fact_key"], item["requirement_id"]))


def _required_documents(nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    documents = []
    for node in nodes:
        if node["requirement_type"] != "document_requirement":
            continue
        conditions = node["conditions"]
        documents.append(
            {
                "document_key": _text(conditions.get("document_key")) or _slug(node["object"]),
                "label": _text(conditions.get("document_label")) or node["object"],
                "requirement_id": node["requirement_id"],
                "process_stage": node["process_stage"],
                "source_evidence_ids": node["source_evidence_ids"],
            }
        )
    return sorted(documents, key=lambda item: (item["document_key"], item["requirement_id"]))


def _file_rules(nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rules = []
    for node in nodes:
        rule = _text(node["conditions"].get("file_rule"))
        if rule:
            rules.append(
                {
                    "file_rule": rule,
                    "requirement_id": node["requirement_id"],
                    "process_stage": node["process_stage"],
                    "source_evidence_ids": node["source_evidence_ids"],
                }
            )
    return sorted(rules, key=lambda item: (item["file_rule"], item["requirement_id"]))


def _unsupported_paths(nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    paths = []
    for node in nodes:
        path = _text(node["conditions"].get("unsupported_path"))
        if path or node["requirement_type"] == "prohibition":
            paths.append(
                {
                    "path": path or node["object"],
                    "requirement_id": node["requirement_id"],
                    "source_evidence_ids": node["source_evidence_ids"],
                }
            )
    return sorted(paths, key=lambda item: (item["path"], item["requirement_id"]))


def _devhub_surface_refs(nodes: list[dict[str, Any]]) -> list[str]:
    refs = []
    for node in nodes:
        value = node["conditions"].get("devhub_surface_ref")
        if isinstance(value, list):
            refs.extend(_text_list(value))
        elif _text(value):
            refs.append(_text(value))
    return _sorted_unique(refs)


def _stages(nodes: list[dict[str, Any]]) -> list[str]:
    return sorted(
        {node["process_stage"] for node in nodes},
        key=lambda stage: (_STAGE_INDEX.get(stage, len(_STAGE_INDEX)), stage),
    )


def _required_text(payload: Mapping[str, Any], key: str) -> str:
    value = _text(payload.get(key))
    if not value:
        raise ProcessModelAssemblyError(f"missing required field: {key}")
    return value


def _text(value: Any) -> str:
    if value is None:
        return ""
    if not isinstance(value, str):
        value = str(value)
    return " ".join(value.strip().split())


def _text_list(value: Any) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        value = [value]
    return [_text(item) for item in value if _text(item)]


def _sorted_unique(values: Iterable[str]) -> list[str]:
    return sorted({value for value in values if value})


def _stable_jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _stable_jsonable(value[key]) for key in sorted(value)}
    if isinstance(value, list):
        return [_stable_jsonable(item) for item in value]
    return value


def _slug(value: str) -> str:
    parts = []
    previous_dash = False
    for char in value.lower():
        if char.isalnum():
            parts.append(char)
            previous_dash = False
        elif not previous_dash:
            parts.append("-")
            previous_dash = True
    return "".join(parts).strip("-") or "document"
