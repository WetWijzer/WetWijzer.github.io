"""Tranche 2 processor-suite integration planning helpers.

This module is intentionally small and deterministic. It validates that PP&D
public documents move through the planned processor artifacts before any agent
handoff is allowed.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

REQUIRED_STAGE_ORDER = (
    "archive_manifest",
    "normalized_document_records",
    "pdf_metadata",
    "requirement_batches",
    "agent_handoff",
)

REQUIRED_OUTPUTS = {
    "archive_manifest": ("manifest_id", "source_url", "content_hash", "retrieved_at"),
    "normalized_document_records": ("document_id", "manifest_id", "title", "public_url"),
    "pdf_metadata": ("document_id", "page_count", "pdf_hash", "metadata_extracted_at"),
    "requirement_batches": ("batch_id", "document_id", "requirements", "review_status"),
    "agent_handoff": ("batch_id", "allowed", "blocking_checks"),
}


@dataclass(frozen=True)
class StageCheck:
    """Validation result for one integration-plan stage."""

    name: str
    ok: bool
    errors: tuple[str, ...]


def validate_integration_plan(plan: dict[str, Any]) -> list[StageCheck]:
    """Validate the tranche 2 processor-suite integration plan shape."""

    stages = plan.get("stages")
    if not isinstance(stages, list):
        return [StageCheck("stages", False, ("plan.stages must be a list",))]

    checks: list[StageCheck] = []
    seen_outputs: set[str] = set()
    stage_names = [stage.get("name") for stage in stages if isinstance(stage, dict)]

    if tuple(stage_names) != REQUIRED_STAGE_ORDER:
        checks.append(
            StageCheck(
                "stage_order",
                False,
                ("stages must be ordered from archive manifest through gated agent handoff",),
            )
        )

    for expected_name in REQUIRED_STAGE_ORDER:
        stage = _find_stage(stages, expected_name)
        if stage is None:
            checks.append(StageCheck(expected_name, False, ("stage is missing",)))
            continue

        errors: list[str] = []
        outputs = stage.get("outputs")
        if not isinstance(outputs, dict):
            errors.append("outputs must be an object")
            outputs = {}

        for required_output in REQUIRED_OUTPUTS[expected_name]:
            if required_output not in outputs:
                errors.append(f"missing output: {required_output}")

        inputs = stage.get("requires", [])
        if not isinstance(inputs, list):
            errors.append("requires must be a list")
            inputs = []

        for required_input in inputs:
            if required_input not in seen_outputs:
                errors.append(f"requires unavailable prior output: {required_input}")

        if expected_name == "agent_handoff" and outputs.get("allowed") is not False:
            errors.append("agent handoff must remain blocked in the planning fixture")

        seen_outputs.update(str(key) for key in outputs)
        checks.append(StageCheck(expected_name, not errors, tuple(errors)))

    return checks


def assert_valid_integration_plan(plan: dict[str, Any]) -> None:
    """Raise AssertionError with compact diagnostics when the plan is invalid."""

    failed = [check for check in validate_integration_plan(plan) if not check.ok]
    if failed:
        details = "; ".join(f"{check.name}: {', '.join(check.errors)}" for check in failed)
        raise AssertionError(details)


def _find_stage(stages: list[Any], name: str) -> dict[str, Any] | None:
    for stage in stages:
        if isinstance(stage, dict) and stage.get("name") == name:
            return stage
    return None
