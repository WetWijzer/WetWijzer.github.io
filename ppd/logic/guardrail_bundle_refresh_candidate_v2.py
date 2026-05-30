"""Fixture-first guardrail bundle refresh candidate v2 builder.

This module intentionally operates on committed JSON fixtures only. It does not
crawl public sources, call live LLMs, touch DevHub, compile production
GuardrailBundle state, mutate prompt state, or update release ledgers.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REQUIRED_ATTESTATIONS = (
    "no_live_llm",
    "no_devhub",
    "no_guardrail_state_mutation",
    "no_prompt_state_mutation",
    "no_release_state_mutation",
)

REQUIRED_OFFLINE_COMMANDS = (
    ("python3", "-m", "pytest", "ppd/tests/test_guardrail_bundle_refresh_candidate_v2.py"),
    ("python3", "ppd/daemon/ppd_daemon.py", "--self-test"),
)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value


def _require_list(value: Any, field: str) -> list[Any]:
    if not isinstance(value, list):
        raise ValueError(f"{field} must be a list")
    return value


def _attestations() -> dict[str, bool]:
    return {name: True for name in REQUIRED_ATTESTATIONS}


def _offline_validation_commands() -> list[list[str]]:
    return [list(command) for command in REQUIRED_OFFLINE_COMMANDS]


def _normalize_checkpoint_expectations(guardrail_fixture: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    reversible = []
    exact = []

    for predicate in _require_list(guardrail_fixture.get("reversible_action_predicates", []), "reversible_action_predicates"):
        if not isinstance(predicate, dict):
            raise ValueError("reversible_action_predicates entries must be objects")
        reversible.append(
            {
                "predicate_id": _require_string(predicate.get("predicate_id"), "reversible predicate_id"),
                "action_type": _require_string(predicate.get("action_type"), "reversible action_type"),
                "expected_checkpoint": "reversible_action_checkpoint",
                "must_remain_draft_only": True,
                "citation_ids": list(_require_list(predicate.get("citation_ids", []), "reversible citation_ids")),
            }
        )

    for predicate in _require_list(guardrail_fixture.get("exact_confirmation_predicates", []), "exact_confirmation_predicates"):
        if not isinstance(predicate, dict):
            raise ValueError("exact_confirmation_predicates entries must be objects")
        exact.append(
            {
                "predicate_id": _require_string(predicate.get("predicate_id"), "exact predicate_id"),
                "action_type": _require_string(predicate.get("action_type"), "exact action_type"),
                "expected_checkpoint": "exact_confirmation_checkpoint",
                "requires_user_visible_action_label": True,
                "citation_ids": list(_require_list(predicate.get("citation_ids", []), "exact citation_ids")),
            }
        )

    return {
        "reversible_action_checkpoint_expectations": reversible,
        "exact_confirmation_checkpoint_expectations": exact,
    }


def build_guardrail_bundle_refresh_candidate_v2(
    process_model_refresh_impact: dict[str, Any],
    requirement_regeneration_work_order: dict[str, Any],
    guardrail_compiler_fixture: dict[str, Any],
) -> dict[str, Any]:
    """Build a deterministic guardrail refresh candidate packet from fixtures."""

    process_ids = sorted(
        {
            _require_string(process_id, "affected_process_ids entry")
            for process_id in _require_list(
                process_model_refresh_impact.get("affected_process_ids", []),
                "affected_process_ids",
            )
        }
    )
    requirement_ids = sorted(
        {
            _require_string(requirement_id, "requirement_ids_to_regenerate entry")
            for requirement_id in _require_list(
                requirement_regeneration_work_order.get("requirement_ids_to_regenerate", []),
                "requirement_ids_to_regenerate",
            )
        }
    )

    source_evidence_ids = sorted(
        {
            _require_string(evidence_id, "source_evidence_ids entry")
            for evidence_id in _require_list(
                requirement_regeneration_work_order.get("source_evidence_ids", []),
                "source_evidence_ids",
            )
            + _require_list(guardrail_compiler_fixture.get("source_evidence_ids", []), "compiler source_evidence_ids")
        }
    )

    predicate_update_candidates = []
    for predicate in _require_list(guardrail_compiler_fixture.get("deterministic_predicates", []), "deterministic_predicates"):
        if not isinstance(predicate, dict):
            raise ValueError("deterministic_predicates entries must be objects")
        predicate_update_candidates.append(
            {
                "candidate_id": f"candidate:{_require_string(predicate.get('predicate_id'), 'predicate_id')}",
                "predicate_id": _require_string(predicate.get("predicate_id"), "predicate_id"),
                "predicate_kind": _require_string(predicate.get("predicate_kind"), "predicate_kind"),
                "operation": "refresh_from_fixture",
                "affected_process_ids": process_ids,
                "affected_requirement_ids": requirement_ids,
                "citation_ids": list(_require_list(predicate.get("citation_ids", []), "predicate citation_ids")),
                "reviewer_owner": _require_string(
                    requirement_regeneration_work_order.get("reviewer_owner"),
                    "reviewer_owner",
                ),
                "implementation_owner": _require_string(
                    requirement_regeneration_work_order.get("implementation_owner"),
                    "implementation_owner",
                ),
                "requires_human_review": True,
            }
        )

    checkpoint_expectations = _normalize_checkpoint_expectations(guardrail_compiler_fixture)

    return {
        "packet_type": "guardrail_bundle_refresh_candidate_v2",
        "packet_id": _require_string(
            requirement_regeneration_work_order.get("work_order_id"),
            "work_order_id",
        ).replace("requirement-regeneration-work-order", "guardrail-bundle-refresh-candidate"),
        "consumes": {
            "process_model_refresh_impact_id": _require_string(
                process_model_refresh_impact.get("impact_id"),
                "impact_id",
            ),
            "requirement_regeneration_work_order_id": _require_string(
                requirement_regeneration_work_order.get("work_order_id"),
                "work_order_id",
            ),
            "guardrail_compiler_fixture_id": _require_string(
                guardrail_compiler_fixture.get("fixture_id"),
                "fixture_id",
            ),
        },
        "affected_process_ids": process_ids,
        "affected_requirement_ids": requirement_ids,
        "source_evidence_ids": source_evidence_ids,
        "predicate_update_candidates": predicate_update_candidates,
        "reversible_action_checkpoint_expectations": checkpoint_expectations[
            "reversible_action_checkpoint_expectations"
        ],
        "exact_confirmation_checkpoint_expectations": checkpoint_expectations[
            "exact_confirmation_checkpoint_expectations"
        ],
        "reviewer_owner": _require_string(requirement_regeneration_work_order.get("reviewer_owner"), "reviewer_owner"),
        "implementation_owner": _require_string(
            requirement_regeneration_work_order.get("implementation_owner"),
            "implementation_owner",
        ),
        "offline_validation_commands": _offline_validation_commands(),
        "attestations": _attestations(),
        "validation_status": "fixture_candidate_pending_review",
    }


def build_from_fixture_paths(
    process_model_refresh_impact_path: Path,
    requirement_regeneration_work_order_path: Path,
    guardrail_compiler_fixture_path: Path,
) -> dict[str, Any]:
    return build_guardrail_bundle_refresh_candidate_v2(
        load_json(process_model_refresh_impact_path),
        load_json(requirement_regeneration_work_order_path),
        load_json(guardrail_compiler_fixture_path),
    )
