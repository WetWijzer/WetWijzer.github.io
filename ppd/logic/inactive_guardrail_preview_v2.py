"""Fixture-first inactive guardrail migration preview packet v2.

This module intentionally produces preview-only artifacts from committed fixtures. It does
not promote guardrails, mutate active requirements, crawl sources, or touch DevHub state.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PACKET_VERSION = 2
PREVIEW_STATUS = "inactive_fixture_preview_only"

OFFLINE_VALIDATION_COMMANDS: list[list[str]] = [
    ["python3", "-m", "py_compile", "ppd/logic/inactive_guardrail_preview_v2.py"],
    ["python3", "-m", "pytest", "ppd/tests/test_inactive_guardrail_preview_v2.py"],
    ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
]


def load_fixture(path: Path) -> dict[str, Any]:
    """Load a committed inactive-delta fixture."""
    with path.open("r", encoding="utf-8") as fixture_file:
        data = json.load(fixture_file)
    if not isinstance(data, dict):
        raise ValueError("inactive guardrail preview fixture must be a JSON object")
    return data


def build_preview_packet(fixture: dict[str, Any]) -> dict[str, Any]:
    """Map synthetic inactive process-model deltas into preview-only guardrail artifacts."""
    _validate_fixture(fixture)
    deltas = fixture["synthetic_inactive_process_model_deltas"]

    deterministic_predicates = [_deterministic_predicate(delta) for delta in deltas]
    deontic_rules = [_deontic_rule(delta) for delta in deltas]
    temporal_rules = [_temporal_rule(delta) for delta in deltas if delta.get("temporal_scope")]
    reversible_action_predicates = [
        _reversible_action_predicate(delta)
        for delta in deltas
        if delta.get("action_class") == "reversible_draft"
    ]
    exact_confirmation_predicates = [
        _exact_confirmation_predicate(delta)
        for delta in deltas
        if delta.get("requires_exact_confirmation") is True
    ]
    refused_action_predicates = [
        _refused_action_predicate(delta)
        for delta in deltas
        if delta.get("action_class") == "consequential_official"
    ]
    stale_source_holds = [
        _stale_source_hold(delta)
        for delta in deltas
        if delta.get("source_freshness") == "stale"
    ]

    return {
        "migration_preview_packet_version": PACKET_VERSION,
        "preview_status": PREVIEW_STATUS,
        "fixture_id": fixture["fixture_id"],
        "source_mode": "committed_fixture_only",
        "promotion_allowed": False,
        "active_prompt_changes_allowed": False,
        "live_crawl_allowed": False,
        "devhub_access_allowed": False,
        "release_state_mutation_allowed": False,
        "process_id": fixture["process_id"],
        "permit_type": fixture["permit_type"],
        "synthetic_delta_ids": [delta["delta_id"] for delta in deltas],
        "proposed_deterministic_predicates": deterministic_predicates,
        "proposed_deontic_rules": deontic_rules,
        "proposed_temporal_rules": temporal_rules,
        "proposed_reversible_action_predicates": reversible_action_predicates,
        "proposed_exact_confirmation_predicates": exact_confirmation_predicates,
        "proposed_refused_action_predicates": refused_action_predicates,
        "proposed_stale_source_holds": stale_source_holds,
        "explanation_template_placeholders": _explanation_template_placeholders(deltas),
        "reviewer_disposition_placeholders": _reviewer_disposition_placeholders(deltas),
        "exact_offline_validation_commands": OFFLINE_VALIDATION_COMMANDS,
    }


def _validate_fixture(fixture: dict[str, Any]) -> None:
    required_top_level = {
        "fixture_id",
        "process_id",
        "permit_type",
        "synthetic_inactive_process_model_deltas",
    }
    missing = sorted(required_top_level.difference(fixture))
    if missing:
        raise ValueError(f"inactive guardrail preview fixture missing keys: {missing}")

    deltas = fixture["synthetic_inactive_process_model_deltas"]
    if not isinstance(deltas, list) or not deltas:
        raise ValueError("synthetic_inactive_process_model_deltas must be a non-empty list")

    required_delta_keys = {
        "delta_id",
        "inactive",
        "source_evidence_ids",
        "process_stage",
        "action",
        "object",
        "action_class",
        "source_freshness",
    }
    for delta in deltas:
        if not isinstance(delta, dict):
            raise ValueError("each inactive delta must be a JSON object")
        missing_delta_keys = sorted(required_delta_keys.difference(delta))
        if missing_delta_keys:
            raise ValueError(f"delta {delta.get('delta_id', '')} missing keys: {missing_delta_keys}")
        if delta["inactive"] is not True:
            raise ValueError(f"delta {delta['delta_id']} must remain inactive for preview")


def _predicate_id(delta: dict[str, Any], prefix: str) -> str:
    return f"{prefix}.{delta['delta_id']}"


def _deterministic_predicate(delta: dict[str, Any]) -> dict[str, Any]:
    return {
        "predicate_id": _predicate_id(delta, "deterministic"),
        "delta_id": delta["delta_id"],
        "status": "proposed_inactive",
        "if_all": [
            {"field": "process_stage", "equals": delta["process_stage"]},
            {"field": "action", "equals": delta["action"]},
            {"field": "object", "equals": delta["object"]},
        ],
        "then": {"classification": delta["action_class"]},
        "source_evidence_ids": delta["source_evidence_ids"],
    }


def _deontic_rule(delta: dict[str, Any]) -> dict[str, Any]:
    action_class = delta["action_class"]
    if action_class == "read_only":
        modality = "permitted"
    elif action_class == "reversible_draft":
        modality = "permitted_with_preview"
    elif action_class == "consequential_official":
        modality = "prohibited_without_attended_exact_confirmation"
    else:
        modality = "requires_human_review"

    return {
        "rule_id": _predicate_id(delta, "deontic"),
        "delta_id": delta["delta_id"],
        "status": "proposed_inactive",
        "modality": modality,
        "subject": "agent",
        "action": delta["action"],
        "object": delta["object"],
        "conditions": delta.get("conditions", []),
        "source_evidence_ids": delta["source_evidence_ids"],
    }


def _temporal_rule(delta: dict[str, Any]) -> dict[str, Any]:
    return {
        "rule_id": _predicate_id(delta, "temporal"),
        "delta_id": delta["delta_id"],
        "status": "proposed_inactive",
        "scope": delta["temporal_scope"],
        "hold_when_source_is_stale": delta.get("source_freshness") == "stale",
        "source_evidence_ids": delta["source_evidence_ids"],
    }


def _reversible_action_predicate(delta: dict[str, Any]) -> dict[str, Any]:
    return {
        "predicate_id": _predicate_id(delta, "reversible_action"),
        "delta_id": delta["delta_id"],
        "status": "proposed_inactive",
        "allowed_only_before_official_action": True,
        "requires_local_preview": True,
        "action": delta["action"],
        "object": delta["object"],
    }


def _exact_confirmation_predicate(delta: dict[str, Any]) -> dict[str, Any]:
    return {
        "predicate_id": _predicate_id(delta, "exact_confirmation"),
        "delta_id": delta["delta_id"],
        "status": "proposed_inactive",
        "required_confirmation_text_placeholder": "{{exact_user_confirmation_text}}",
        "must_match_action": delta["action"],
        "must_match_object": delta["object"],
        "must_be_attended": True,
    }


def _refused_action_predicate(delta: dict[str, Any]) -> dict[str, Any]:
    return {
        "predicate_id": _predicate_id(delta, "refused_action"),
        "delta_id": delta["delta_id"],
        "status": "proposed_inactive",
        "refuse_when_unattended": True,
        "refuse_when_confirmation_missing": True,
        "refuse_when_source_stale": delta.get("source_freshness") == "stale",
        "action": delta["action"],
        "object": delta["object"],
    }


def _stale_source_hold(delta: dict[str, Any]) -> dict[str, Any]:
    return {
        "hold_id": _predicate_id(delta, "stale_source_hold"),
        "delta_id": delta["delta_id"],
        "status": "proposed_inactive",
        "held_artifact_types": [
            "deterministic_predicate",
            "deontic_rule",
            "temporal_rule",
            "action_predicate",
        ],
        "release_condition_placeholder": "{{reviewer_confirms_source_freshness}}",
        "source_evidence_ids": delta["source_evidence_ids"],
    }


def _explanation_template_placeholders(deltas: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "template_id": _predicate_id(delta, "explanation_template"),
            "delta_id": delta["delta_id"],
            "status": "placeholder_only",
            "template": (
                "{{action_label}} is {{guardrail_classification}} for {{process_stage}} "
                "because {{source_summary}}. Next safe step: {{next_safe_action}}."
            ),
            "required_placeholders": [
                "action_label",
                "guardrail_classification",
                "process_stage",
                "source_summary",
                "next_safe_action",
            ],
        }
        for delta in deltas
    ]


def _reviewer_disposition_placeholders(deltas: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "disposition_id": _predicate_id(delta, "reviewer_disposition"),
            "delta_id": delta["delta_id"],
            "status": "awaiting_review",
            "allowed_dispositions": [
                "accept_preview_mapping",
                "revise_preview_mapping",
                "reject_preview_mapping",
                "hold_for_fresh_source_review",
            ],
            "reviewer_notes_placeholder": "{{reviewer_notes}}",
        }
        for delta in deltas
    ]
