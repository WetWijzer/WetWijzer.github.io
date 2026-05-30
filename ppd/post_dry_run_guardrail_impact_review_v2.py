"""Fixture-first post-dry-run guardrail impact review v2.

This module consumes committed refresh-candidate and regression-matrix fixtures only.
It does not call an LLM, open DevHub, crawl sources, run processors, mutate active
guardrails, mutate prompts, or change release state.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from ppd.agent_readiness.guardrail_refresh_regression_matrix_v2 import (
    validate_guardrail_refresh_regression_matrix_v2_packet,
)
from ppd.devhub_surface_observation_refresh_candidate_v2 import (
    validate_devhub_surface_observation_refresh_candidate_v2,
)
from ppd.source_observation_refresh_candidate_v2 import validate_source_observation_refresh_candidate_v2

PACKET_TYPE = "ppd.post_dry_run_guardrail_impact_review.v2"

ATTESTATIONS = {
    "no_live_llm": True,
    "no_live_devhub": True,
    "no_crawler": True,
    "no_processor": True,
    "no_guardrail_mutation": True,
    "no_prompt_mutation": True,
    "no_release_state_mutation": True,
}

OFFLINE_VALIDATION_COMMANDS = [
    ["python3", "-m", "py_compile", "ppd/post_dry_run_guardrail_impact_review_v2.py"],
    ["python3", "-m", "unittest", "ppd.tests.test_post_dry_run_guardrail_impact_review_v2"],
    ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
]

_CONSEQUENTIAL_ACTIONS = (
    "permit_request_submission",
    "acknowledgement_certification",
    "correction_upload",
    "fee_payment_execution",
    "inspection_scheduling",
    "permit_cancellation_or_withdrawal",
)


@dataclass(frozen=True)
class GuardrailImpactReviewValidationResult:
    ok: bool
    errors: tuple[str, ...]


def load_json(path: str | Path) -> dict[str, Any]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"expected JSON object at {path}")
    return raw


def build_post_dry_run_guardrail_impact_review_v2_from_files(
    public_source_observation_refresh_candidate_v2_path: str | Path,
    devhub_read_only_surface_observation_refresh_candidate_v2_path: str | Path,
    guardrail_refresh_regression_matrix_v2_path: str | Path,
) -> dict[str, Any]:
    source_path = Path(public_source_observation_refresh_candidate_v2_path)
    devhub_path = Path(devhub_read_only_surface_observation_refresh_candidate_v2_path)
    matrix_path = Path(guardrail_refresh_regression_matrix_v2_path)

    source_packet = load_json(source_path)
    devhub_packet = load_json(devhub_path)
    matrix_packet = load_json(matrix_path)

    source_result = validate_source_observation_refresh_candidate_v2(source_packet)
    if not source_result.ok:
        raise ValueError("invalid public source observation refresh candidate v2: " + "; ".join(source_result.errors))
    devhub_result = validate_devhub_surface_observation_refresh_candidate_v2(devhub_packet)
    if not devhub_result.ok:
        raise ValueError("invalid DevHub surface observation refresh candidate v2: " + "; ".join(devhub_result.errors))
    matrix_result = validate_guardrail_refresh_regression_matrix_v2_packet(matrix_packet)
    if not matrix_result.valid:
        raise ValueError("invalid guardrail refresh regression matrix v2: " + "; ".join(matrix_result.problems))

    source_ref = source_path.as_posix()
    devhub_ref = devhub_path.as_posix()
    matrix_ref = matrix_path.as_posix()

    impacted: list[dict[str, Any]] = []
    unimpacted: list[dict[str, Any]] = []

    for candidate in _dicts(source_packet.get("candidates")):
        source_id = _text(candidate.get("source_id"))
        if not source_id:
            continue
        impacted.append(
            {
                "decision_id": f"impact-source-{source_id}",
                "decision": "impacted",
                "guardrail_bundle_id": "bundle.public-source-freshness-gates",
                "predicate_id": "predicate.public_source_observation_requires_reviewer_review",
                "affected_source_ids": _strings(candidate.get("affected_source_ids")) or [source_id],
                "affected_surface_ids": [],
                "rationale": "Metadata-only public source observation candidate can affect freshness predicates but does not change active guardrails.",
                "citations": [
                    {"fixture": source_ref, "field": f"candidates[{source_id}]", "supports": "source-observation"}
                ]
                + _citations(candidate),
            }
        )

    surfaces = [_text(item.get("surface_id")) for item in _dicts(devhub_packet.get("observations"))]
    surfaces = [surface for surface in surfaces if surface]
    if surfaces:
        impacted.append(
            {
                "decision_id": "impact-devhub-read-only-surfaces",
                "decision": "impacted",
                "guardrail_bundle_id": "bundle.devhub-read-only-action-gates",
                "predicate_id": "predicate.devhub_read_only_surface_requires_attended_review_before_promotion",
                "affected_source_ids": [],
                "affected_surface_ids": sorted(set(surfaces)),
                "rationale": "Read-only surface observations can update review predicates while preserving consequential-action blocks.",
                "citations": [{"fixture": devhub_ref, "field": "observations", "supports": "devhub-read-only-surface"}],
            }
        )

    for scenario in _dicts(matrix_packet.get("scenario_expectations")):
        scenario_id = _text(scenario.get("scenario_id"))
        disposition = _text(scenario.get("expected_disposition")).lower()
        decision = {
            "decision_id": f"matrix-{scenario_id}",
            "decision": "impacted" if disposition in {"fail", "expected_fail"} else "unimpacted",
            "guardrail_bundle_id": "bundle.agent-safe-action-regression-gates",
            "predicate_id": f"predicate.{scenario_id}",
            "affected_source_ids": _strings(source_packet.get("affected_source_ids")),
            "affected_surface_ids": sorted(set(surfaces)),
            "rationale": _text(scenario.get("expectation")),
            "citations": [
                {
                    "fixture": matrix_ref,
                    "field": f"scenario_expectations[{scenario_id}]",
                    "supports": "guardrail-regression-expectation",
                }
            ],
        }
        if decision["decision"] == "impacted":
            impacted.append(decision)
        else:
            unimpacted.append(decision)

    reviewer_owner_fields = _reviewer_owner_fields(source_packet, devhub_packet, matrix_packet)
    rollback_notes = _rollback_notes(matrix_packet, matrix_ref)
    blocked_checks = _blocked_consequential_action_checks(matrix_ref, devhub_ref)

    packet = {
        "packet_type": PACKET_TYPE,
        "fixture_first": True,
        "source_fixtures": {
            "public_source_observation_refresh_candidate_v2": source_ref,
            "devhub_read_only_surface_observation_refresh_candidate_v2": devhub_ref,
            "guardrail_refresh_regression_matrix_v2": matrix_ref,
        },
        "impacted_guardrail_predicate_decisions": impacted,
        "unimpacted_guardrail_predicate_decisions": unimpacted,
        "blocked_consequential_action_checks": blocked_checks,
        "rollback_notes": rollback_notes,
        "reviewer_owner_fields": reviewer_owner_fields,
        "offline_validation_commands": OFFLINE_VALIDATION_COMMANDS,
        "attestations": dict(ATTESTATIONS),
    }
    require_post_dry_run_guardrail_impact_review_v2(packet)
    return packet


def validate_post_dry_run_guardrail_impact_review_v2(packet: dict[str, Any]) -> GuardrailImpactReviewValidationResult:
    errors: list[str] = []
    if packet.get("packet_type") != PACKET_TYPE:
        errors.append(f"packet_type must be {PACKET_TYPE}")
    if packet.get("fixture_first") is not True:
        errors.append("fixture_first must be true")
    if packet.get("attestations") != ATTESTATIONS:
        errors.append("attestations must preserve no-live/no-mutation guardrails")
    _validate_decisions(packet.get("impacted_guardrail_predicate_decisions"), "impacted_guardrail_predicate_decisions", True, errors)
    _validate_decisions(packet.get("unimpacted_guardrail_predicate_decisions"), "unimpacted_guardrail_predicate_decisions", False, errors)
    _validate_blocked_checks(packet.get("blocked_consequential_action_checks"), errors)
    _validate_rollback_notes(packet.get("rollback_notes"), errors)
    _validate_reviewer_owners(packet.get("reviewer_owner_fields"), errors)
    if not isinstance(packet.get("offline_validation_commands"), list) or not packet.get("offline_validation_commands"):
        errors.append("offline_validation_commands must be present")
    return GuardrailImpactReviewValidationResult(ok=not errors, errors=tuple(errors))


def require_post_dry_run_guardrail_impact_review_v2(packet: dict[str, Any]) -> None:
    result = validate_post_dry_run_guardrail_impact_review_v2(packet)
    if not result.ok:
        raise ValueError("invalid post-dry-run guardrail impact review v2: " + "; ".join(result.errors))


def _validate_decisions(value: Any, name: str, require_non_empty: bool, errors: list[str]) -> None:
    if not isinstance(value, list) or (require_non_empty and not value):
        errors.append(f"{name} must be a non-empty list")
        return
    for index, item in enumerate(value):
        path = f"{name}[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{path} must be an object")
            continue
        expected_decision = "impacted" if name.startswith("impacted") else "unimpacted"
        if item.get("decision") != expected_decision:
            errors.append(f"{path}.decision must be {expected_decision}")
        for field in ("decision_id", "guardrail_bundle_id", "predicate_id", "rationale"):
            if not _text(item.get(field)):
                errors.append(f"{path}.{field} must be present")
        if not _has_citations(item.get("citations")):
            errors.append(f"{path}.citations must cite source, surface, or matrix evidence")


def _validate_blocked_checks(value: Any, errors: list[str]) -> None:
    if not isinstance(value, list) or not value:
        errors.append("blocked_consequential_action_checks must be a non-empty list")
        return
    for index, item in enumerate(value):
        path = f"blocked_consequential_action_checks[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{path} must be an object")
            continue
        if _text(item.get("action_type")) not in _CONSEQUENTIAL_ACTIONS:
            errors.append(f"{path}.action_type must identify a blocked consequential action")
        if item.get("blocked") is not True:
            errors.append(f"{path}.blocked must be true")
        if not _text(item.get("guardrail_predicate_id")):
            errors.append(f"{path}.guardrail_predicate_id must be present")
        if not _has_citations(item.get("citations")):
            errors.append(f"{path}.citations must be present")


def _validate_rollback_notes(value: Any, errors: list[str]) -> None:
    if not isinstance(value, list) or not value:
        errors.append("rollback_notes must be a non-empty list")
        return
    for index, item in enumerate(value):
        if not isinstance(item, dict) or not _text(item.get("note")) or not _has_citations(item.get("citations")):
            errors.append(f"rollback_notes[{index}] must include note and citations")


def _validate_reviewer_owners(value: Any, errors: list[str]) -> None:
    if not isinstance(value, list) or not value:
        errors.append("reviewer_owner_fields must be a non-empty list")
        return
    for index, item in enumerate(value):
        if not isinstance(item, dict) or not _text(item.get("reviewer_owner")) or not _text(item.get("scope")):
            errors.append(f"reviewer_owner_fields[{index}] must include scope and reviewer_owner")


def _blocked_consequential_action_checks(matrix_ref: str, devhub_ref: str) -> list[dict[str, Any]]:
    return [
        {
            "action_type": action,
            "blocked": True,
            "guardrail_predicate_id": "predicate.consequential_checkpoint_block",
            "review_note": "Fixture review preserves the attended exact-confirmation gate before any official action.",
            "citations": [
                {"fixture": matrix_ref, "field": "scenario_expectations[consequential_checkpoint_block]"},
                {"fixture": devhub_ref, "field": "observations"},
            ],
        }
        for action in _CONSEQUENTIAL_ACTIONS
    ]


def _rollback_notes(matrix_packet: dict[str, Any], matrix_ref: str) -> list[dict[str, Any]]:
    notes = []
    root_note = _text(matrix_packet.get("rollback_notes"))
    if root_note:
        notes.append({"scope": "packet", "note": root_note, "citations": [{"fixture": matrix_ref, "field": "rollback_notes"}]})
    for scenario in _dicts(matrix_packet.get("scenario_expectations")):
        scenario_id = _text(scenario.get("scenario_id"))
        note = _text(scenario.get("rollback_notes") or scenario.get("rollback_note"))
        if note:
            notes.append(
                {
                    "scope": f"scenario:{scenario_id}",
                    "note": note,
                    "citations": [{"fixture": matrix_ref, "field": f"scenario_expectations[{scenario_id}].rollback_notes"}],
                }
            )
    return notes


def _reviewer_owner_fields(source_packet: dict[str, Any], devhub_packet: dict[str, Any], matrix_packet: dict[str, Any]) -> list[dict[str, str]]:
    fields: list[dict[str, str]] = []
    for candidate in _dicts(source_packet.get("candidates")):
        owner = _text(candidate.get("reviewer_owner"))
        source_id = _text(candidate.get("source_id"))
        if owner:
            fields.append({"scope": f"source:{source_id}", "reviewer_owner": owner})
    for item in _dicts(devhub_packet.get("reviewer_owner_fields")):
        owner = _text(item.get("reviewer_owner"))
        surface_id = _text(item.get("surface_id"))
        if owner:
            fields.append({"scope": f"surface:{surface_id}", "reviewer_owner": owner})
    for owner in _strings(matrix_packet.get("reviewer_owners")):
        fields.append({"scope": "guardrail-regression-matrix", "reviewer_owner": owner})
    seen: set[tuple[str, str]] = set()
    unique = []
    for field in fields:
        key = (field["scope"], field["reviewer_owner"])
        if key not in seen:
            seen.add(key)
            unique.append(field)
    return unique


def _citations(item: dict[str, Any]) -> list[dict[str, Any]]:
    citations = item.get("citations")
    return [citation for citation in citations if isinstance(citation, dict)] if isinstance(citations, list) else []


def _dicts(value: Any) -> list[dict[str, Any]]:
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def _strings(value: Any) -> list[str]:
    return [item.strip() for item in value if isinstance(item, str) and item.strip()] if isinstance(value, list) else []


def _has_citations(value: Any) -> bool:
    return isinstance(value, list) and any(isinstance(item, dict) and item for item in value)


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""
