"""Fixture-first intake for requirement extraction rerun results.

This module intentionally consumes only caller-provided packet dictionaries. It does
not crawl, invoke processors, or mutate active artifacts.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any


DECISIONS = {"accepted", "deferred", "rejected"}
REQUIRED_ATTESTATIONS = {
    "no_live_extraction": True,
    "no_processor_execution": True,
    "no_active_artifact_mutation": True,
}


def _require_mapping(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be a mapping")
    return value


def _require_string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value


def _string_list(value: Any, name: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
        raise ValueError(f"{name} must be a list of non-empty strings")
    return list(value)


def _validate_validation_commands(commands: Any) -> list[list[str]]:
    if not isinstance(commands, list) or not commands:
        raise ValueError("validation_commands must be a non-empty list")
    normalized: list[list[str]] = []
    for index, command in enumerate(commands):
        if not isinstance(command, list) or not command:
            raise ValueError(f"validation_commands[{index}] must be a non-empty list")
        if not all(isinstance(part, str) and part for part in command):
            raise ValueError(f"validation_commands[{index}] must contain only non-empty strings")
        normalized.append(list(command))
    return normalized


def _result_decision(result: dict[str, Any], fixture_id: str) -> dict[str, Any]:
    decision = _require_string(result.get("decision"), "result.decision")
    if decision not in DECISIONS:
        raise ValueError(f"unsupported decision: {decision}")

    evidence = result.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        raise ValueError("result.evidence must be a non-empty list")

    citations: list[dict[str, str]] = []
    for item in evidence:
        item_map = _require_mapping(item, "evidence item")
        citations.append(
            {
                "fixture_id": fixture_id,
                "source_fixture": _require_string(item_map.get("source_fixture"), "evidence.source_fixture"),
                "selector": _require_string(item_map.get("selector"), "evidence.selector"),
                "quote": _require_string(item_map.get("quote"), "evidence.quote"),
            }
        )

    return {
        "decision": decision,
        "requirement_id": _require_string(result.get("requirement_id"), "result.requirement_id"),
        "process_id": _require_string(result.get("process_id"), "result.process_id"),
        "guardrail_ids": _string_list(result.get("guardrail_ids"), "result.guardrail_ids"),
        "reviewer_owner": _require_string(result.get("reviewer_owner"), "result.reviewer_owner"),
        "rationale": _require_string(result.get("rationale"), "result.rationale"),
        "citations": citations,
    }


def build_result_intake_packet(work_order: dict[str, Any], rerun_output: dict[str, Any]) -> dict[str, Any]:
    """Build a cited result-intake packet from fixture work-order and output data."""
    work_order = _require_mapping(work_order, "work_order")
    rerun_output = _require_mapping(rerun_output, "rerun_output")

    if work_order.get("packet_type") != "requirement_extraction_rerun_work_order":
        raise ValueError("work_order.packet_type must be requirement_extraction_rerun_work_order")
    if rerun_output.get("artifact_type") != "synthetic_requirement_extraction_rerun_output":
        raise ValueError("rerun_output.artifact_type must be synthetic_requirement_extraction_rerun_output")

    fixture_id = _require_string(rerun_output.get("fixture_id"), "rerun_output.fixture_id")
    results = rerun_output.get("results")
    if not isinstance(results, list) or not results:
        raise ValueError("rerun_output.results must be a non-empty list")

    decisions = [_result_decision(_require_mapping(result, "result"), fixture_id) for result in results]

    affected_requirement_ids = sorted({decision["requirement_id"] for decision in decisions})
    affected_process_ids = sorted({decision["process_id"] for decision in decisions})
    affected_guardrail_ids = sorted({guardrail for decision in decisions for guardrail in decision["guardrail_ids"]})

    validation_commands = _validate_validation_commands(work_order.get("validation_commands"))

    return {
        "packet_type": "requirement_extraction_rerun_result_intake",
        "packet_version": 1,
        "packet_id": f"result-intake-for-{_require_string(work_order.get('packet_id'), 'work_order.packet_id')}",
        "generated_at": datetime(2026, 5, 29, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z"),
        "source_work_order_packet_id": work_order["packet_id"],
        "source_rerun_fixture_id": fixture_id,
        "reviewer_owner": _require_string(work_order.get("reviewer_owner"), "work_order.reviewer_owner"),
        "affected_requirement_ids": affected_requirement_ids,
        "affected_process_ids": affected_process_ids,
        "affected_guardrail_ids": affected_guardrail_ids,
        "result_decisions": decisions,
        "offline_validation_commands": validation_commands,
        "attestations": deepcopy(REQUIRED_ATTESTATIONS),
    }
