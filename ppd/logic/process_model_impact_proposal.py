"""Fixture-first process model impact proposal builder.

This module is intentionally side-effect free. It reads requirement
formalization candidate packets and process model fixtures, then returns a
reviewable proposal describing how active process models might change. It does
not write active process models, requirements, guardrail bundles, prompts, or
agent state.
"""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

PROPOSAL_VERSION = "process_model_impact_proposal_v1"
DEFAULT_REVIEWER_OWNER = "ppd-process-model-reviewer"
DEFAULT_ROLLBACK_NOTE = (
    "Discard this proposal artifact. No active process models, requirements, "
    "guardrail bundles, prompts, or agent state are mutated by this builder."
)

IMPACT_CATEGORIES = (
    "required_user_facts",
    "required_documents",
    "file_rules",
    "fees",
    "deadlines",
    "unsupported_paths",
    "exceptions",
    "action_gates",
)

CATEGORY_ORDER = {category: index + 1 for index, category in enumerate(IMPACT_CATEGORIES)}

REQUIREMENT_TYPE_TO_CATEGORY = {
    "precondition": "required_user_facts",
    "license_requirement": "required_user_facts",
    "document_requirement": "required_documents",
    "fee_trigger": "fees",
    "deadline": "deadlines",
    "exception": "exceptions",
    "action_gate": "action_gates",
    "prohibition": "unsupported_paths",
}

OFFLINE_VALIDATION_COMMANDS = [
    ["python3", "-m", "py_compile", "ppd/logic/process_model_impact_proposal.py"],
    ["python3", "ppd/tests/test_process_model_impact_proposal.py"],
    ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
]


def load_json(path: str | Path) -> dict[str, Any]:
    """Load a JSON object from a fixture path."""
    loaded = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return loaded


def build_impact_proposal(
    candidate_packet: dict[str, Any],
    process_fixture_set: dict[str, Any],
    *,
    reviewer_owner: str = DEFAULT_REVIEWER_OWNER,
    rollback_note: str = DEFAULT_ROLLBACK_NOTE,
) -> dict[str, Any]:
    """Build a cited proposal from requirement candidates and process fixtures.

    The returned object is deterministic for stable fixtures. Inputs are deep
    copied before processing so callers can assert that fixtures were not
    mutated.
    """
    packet = deepcopy(candidate_packet)
    processes = deepcopy(process_fixture_set)
    _validate_packet(packet)
    _validate_process_fixture_set(processes)

    process_index = _index_processes(processes["process_models"])
    evidence_index = _index_evidence(packet.get("source_evidence", []))
    impacts = {category: [] for category in IMPACT_CATEGORIES}

    accepted_candidates = [
        candidate
        for candidate in packet["candidates"]
        if candidate.get("formalization_status") in {"candidate", "proposed"}
    ]

    for candidate in sorted(accepted_candidates, key=lambda item: item["requirement_id"]):
        category = _candidate_category(candidate)
        if category not in impacts:
            raise ValueError(
                f"Unsupported impact category {category!r} for {candidate['requirement_id']}"
            )
        affected_process_ids = _affected_process_ids(candidate, process_index)
        citations = _citations_for_candidate(candidate, evidence_index)
        impact = {
            "impact_id": f"impact-{candidate['requirement_id']}",
            "category": category,
            "affected_process_ids": affected_process_ids,
            "dependency_order": CATEGORY_ORDER[category],
            "source_requirement_ids": [candidate["requirement_id"]],
            "process_stage": candidate.get("process_stage"),
            "proposed_change": _proposed_change(candidate, category),
            "citations": citations,
            "reviewer_owner": candidate.get("reviewer_owner", reviewer_owner),
            "rollback_note": candidate.get("rollback_note", rollback_note),
        }
        impacts[category].append(impact)

    return {
        "proposal_version": PROPOSAL_VERSION,
        "proposal_id": f"{packet['packet_id']}__{processes['fixture_set_id']}__impact_proposal_v1",
        "source_packet_id": packet["packet_id"],
        "process_fixture_set_id": processes["fixture_set_id"],
        "mutation_policy": "proposal_only_no_active_model_mutation",
        "reviewer_owner": reviewer_owner,
        "rollback_note": rollback_note,
        "offline_validation_commands": deepcopy(OFFLINE_VALIDATION_COMMANDS),
        "impacts": impacts,
        "affected_process_ids": sorted(
            {
                process_id
                for category_impacts in impacts.values()
                for impact in category_impacts
                for process_id in impact["affected_process_ids"]
            }
        ),
        "dependency_order": list(IMPACT_CATEGORIES),
    }


def build_impact_proposal_from_files(
    candidate_packet_path: str | Path,
    process_fixture_set_path: str | Path,
) -> dict[str, Any]:
    """Load fixtures and build a process model impact proposal."""
    return build_impact_proposal(
        load_json(candidate_packet_path),
        load_json(process_fixture_set_path),
    )


def _validate_packet(packet: dict[str, Any]) -> None:
    if not packet.get("packet_id"):
        raise ValueError("candidate packet requires packet_id")
    candidates = packet.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        raise ValueError("candidate packet requires non-empty candidates list")
    for candidate in candidates:
        if not isinstance(candidate, dict):
            raise ValueError("candidate entries must be objects")
        for field in ("requirement_id", "requirement_type", "summary"):
            if not candidate.get(field):
                raise ValueError(f"candidate missing {field}")


def _validate_process_fixture_set(process_fixture_set: dict[str, Any]) -> None:
    if not process_fixture_set.get("fixture_set_id"):
        raise ValueError("process fixture set requires fixture_set_id")
    process_models = process_fixture_set.get("process_models")
    if not isinstance(process_models, list) or not process_models:
        raise ValueError("process fixture set requires non-empty process_models list")
    for process in process_models:
        if not isinstance(process, dict):
            raise ValueError("process model entries must be objects")
        for field in ("process_id", "permit_type"):
            if not process.get(field):
                raise ValueError(f"process model missing {field}")


def _index_processes(process_models: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {process["process_id"]: process for process in process_models}


def _index_evidence(evidence_items: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        evidence["evidence_id"]: evidence
        for evidence in evidence_items
        if isinstance(evidence, dict) and evidence.get("evidence_id")
    }


def _candidate_category(candidate: dict[str, Any]) -> str:
    explicit_category = candidate.get("impact_category")
    if explicit_category:
        return explicit_category
    requirement_type = candidate.get("requirement_type")
    if requirement_type in REQUIREMENT_TYPE_TO_CATEGORY:
        return REQUIREMENT_TYPE_TO_CATEGORY[requirement_type]
    if requirement_type == "obligation" and candidate.get("object_kind") == "file_rule":
        return "file_rules"
    raise ValueError(
        f"Candidate {candidate.get('requirement_id')} has no supported impact category"
    )


def _affected_process_ids(
    candidate: dict[str, Any], process_index: dict[str, dict[str, Any]]
) -> list[str]:
    explicit_process_ids = candidate.get("affected_process_ids")
    if explicit_process_ids:
        unknown = sorted(set(explicit_process_ids) - set(process_index))
        if unknown:
            raise ValueError(
                f"Candidate {candidate['requirement_id']} references unknown processes: {unknown}"
            )
        return sorted(explicit_process_ids)

    permit_types = set(candidate.get("permit_types", []))
    if not permit_types or "all" in permit_types:
        return sorted(process_index)

    matched = sorted(
        process_id
        for process_id, process in process_index.items()
        if process.get("permit_type") in permit_types
    )
    if not matched:
        raise ValueError(
            f"Candidate {candidate['requirement_id']} did not match process fixtures"
        )
    return matched


def _citations_for_candidate(
    candidate: dict[str, Any], evidence_index: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    citation_ids = candidate.get("source_evidence_ids", [])
    citations = []
    for evidence_id in citation_ids:
        evidence = evidence_index.get(evidence_id)
        if evidence is None:
            raise ValueError(
                f"Candidate {candidate['requirement_id']} references unknown evidence {evidence_id}"
            )
        citations.append(
            {
                "evidence_id": evidence_id,
                "source_id": evidence.get("source_id"),
                "canonical_url": evidence.get("canonical_url"),
                "title": evidence.get("title"),
                "span": evidence.get("span"),
                "retrieved_at": evidence.get("retrieved_at"),
            }
        )
    if not citations:
        raise ValueError(f"Candidate {candidate['requirement_id']} has no citations")
    return citations


def _proposed_change(candidate: dict[str, Any], category: str) -> dict[str, Any]:
    change = {
        "operation": "propose_add_or_update",
        "target_field": category,
        "summary": candidate["summary"],
    }
    for optional_field in (
        "subject",
        "action",
        "object",
        "conditions",
        "deadline_or_temporal_scope",
        "process_stage",
        "confidence",
        "human_review_status",
    ):
        if optional_field in candidate:
            change[optional_field] = deepcopy(candidate[optional_field])
    return change


if __name__ == "__main__":
    fixture_dir = Path(__file__).parents[1] / "tests" / "fixtures" / "process_model_impact_proposal_v1"
    proposal = build_impact_proposal_from_files(
        fixture_dir / "requirement_formalization_candidate_packet_v1.json",
        fixture_dir / "process_model_fixtures_v1.json",
    )
    print(json.dumps(proposal, indent=2, sort_keys=True))
