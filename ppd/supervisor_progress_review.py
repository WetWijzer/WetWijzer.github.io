"""Fixture-first supervisor progress review packets for PP&D.

This module is intentionally side-effect free. It evaluates committed fixture
metadata that maps completed PP&D data products to the original architecture
milestones and reports the next missing fixture, validation, or guardrail layer.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

MAX_PLAN_NEXT_TASK_ADDITIONS = 3

REQUIRED_PACKET_KEYS = {
    "packet_id",
    "reviewed_at",
    "architecture_milestones",
    "completed_data_products",
    "next_missing_layers",
    "completed_task_history",
    "domain_completion_claims",
    "plan_next_tasks",
    "recent_failures",
    "syntax_preflight_recovery",
}

REQUIRED_MILESTONE_KEYS = {
    "milestone_id",
    "name",
    "plan_section",
    "expected_data_products",
}

REQUIRED_PRODUCT_KEYS = {
    "product_id",
    "product_type",
    "fixture_path",
    "validated_by",
    "milestone_ids",
}

REQUIRED_LAYER_KEYS = {
    "layer_id",
    "layer_type",
    "milestone_id",
    "reason",
    "recommended_fixture_path",
}

REQUIRED_TASK_HISTORY_KEYS = {
    "task_id",
    "status",
    "completed_at",
    "summary",
    "evidence_refs",
}

REQUIRED_DOMAIN_CLAIM_KEYS = {
    "domain_id",
    "status",
    "promoted_source_change_ids",
}

REQUIRED_PLAN_NEXT_TASK_KEYS = {
    "order",
    "task_id",
    "title",
    "reason",
}

ALLOWED_LAYER_TYPES = {"fixture", "validation", "guardrail"}
ALLOWED_DOMAIN_STATUSES = {"not_started", "partial", "blocked", "complete"}


@dataclass(frozen=True)
class ReviewFinding:
    """A deterministic packet validation finding."""

    code: str
    message: str


@dataclass(frozen=True)
class MilestoneProgress:
    """Progress for one architecture milestone."""

    milestone_id: str
    name: str
    expected_count: int
    completed_count: int
    missing_product_types: tuple[str, ...]

    @property
    def status(self) -> str:
        if self.expected_count == 0:
            return "not_applicable"
        if self.completed_count >= self.expected_count:
            return "complete"
        if self.completed_count > 0:
            return "partial"
        return "missing"


def load_review_packet(path: Path) -> dict[str, Any]:
    """Load a supervisor progress review packet from JSON."""

    with path.open("r", encoding="utf-8") as packet_file:
        packet = json.load(packet_file)
    if not isinstance(packet, dict):
        raise ValueError("review packet must be a JSON object")
    return packet


def _is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _validate_completed_task_history(packet: dict[str, Any], findings: list[ReviewFinding]) -> None:
    history = packet.get("completed_task_history", [])
    if not isinstance(history, list):
        findings.append(ReviewFinding("invalid_completed_task_history", "completed_task_history must be a list"))
        return
    if not history:
        findings.append(ReviewFinding("missing_completed_task_history", "packet must preserve completed task history"))
        return

    seen_task_ids: set[str] = set()
    for index, entry in enumerate(history):
        if not isinstance(entry, dict):
            findings.append(ReviewFinding("invalid_task_history_entry", f"completed task history entry {index} must be an object"))
            continue
        for key in sorted(REQUIRED_TASK_HISTORY_KEYS.difference(entry)):
            findings.append(ReviewFinding("missing_task_history_key", f"completed task history entry {index} is missing {key}"))
        task_id = entry.get("task_id")
        if not _is_non_empty_string(task_id):
            findings.append(ReviewFinding("invalid_task_history_id", f"completed task history entry {index} needs a task_id"))
        elif task_id in seen_task_ids:
            findings.append(ReviewFinding("duplicate_task_history_id", f"completed task history repeats {task_id}"))
        else:
            seen_task_ids.add(task_id)
        if entry.get("status") != "completed":
            findings.append(ReviewFinding("invalid_task_history_status", f"completed task history entry {task_id or index} must keep status completed"))
        evidence_refs = entry.get("evidence_refs", [])
        if not isinstance(evidence_refs, list) or not all(_is_non_empty_string(item) for item in evidence_refs):
            findings.append(ReviewFinding("invalid_task_history_evidence", f"completed task history entry {task_id or index} needs evidence_refs"))


def _validate_domain_completion_claims(packet: dict[str, Any], findings: list[ReviewFinding]) -> None:
    claims = packet.get("domain_completion_claims", [])
    if not isinstance(claims, list):
        findings.append(ReviewFinding("invalid_domain_completion_claims", "domain_completion_claims must be a list"))
        return
    for index, claim in enumerate(claims):
        if not isinstance(claim, dict):
            findings.append(ReviewFinding("invalid_domain_completion_claim", f"domain completion claim {index} must be an object"))
            continue
        for key in sorted(REQUIRED_DOMAIN_CLAIM_KEYS.difference(claim)):
            findings.append(ReviewFinding("missing_domain_completion_key", f"domain completion claim {index} is missing {key}"))
        domain_id = claim.get("domain_id", index)
        status = claim.get("status")
        if status not in ALLOWED_DOMAIN_STATUSES:
            findings.append(ReviewFinding("invalid_domain_completion_status", f"domain completion claim {domain_id} has invalid status {status}"))
        promoted = claim.get("promoted_source_change_ids", [])
        if not isinstance(promoted, list) or not all(_is_non_empty_string(item) for item in promoted):
            findings.append(ReviewFinding("invalid_promoted_source_changes", f"domain completion claim {domain_id} needs promoted_source_change_ids as strings"))
            promoted = []
        if status == "complete" and not promoted:
            findings.append(ReviewFinding("complete_domain_without_promoted_source_changes", f"domain completion claim {domain_id} cannot be complete without promoted source changes"))


def _validate_plan_next_tasks(packet: dict[str, Any], findings: list[ReviewFinding]) -> None:
    plan = packet.get("plan_next_tasks", {})
    if not isinstance(plan, dict):
        findings.append(ReviewFinding("invalid_plan_next_tasks", "plan_next_tasks must be an object"))
        return
    additions = plan.get("backlog_additions", [])
    if not isinstance(additions, list):
        findings.append(ReviewFinding("invalid_backlog_additions", "plan_next_tasks.backlog_additions must be a list"))
        return
    if len(additions) > MAX_PLAN_NEXT_TASK_ADDITIONS:
        findings.append(ReviewFinding("too_many_backlog_additions", "plan_next_tasks backlog additions must stay narrow"))

    expected_order = 1
    for index, addition in enumerate(additions):
        if not isinstance(addition, dict):
            findings.append(ReviewFinding("invalid_backlog_addition", f"backlog addition {index} must be an object"))
            continue
        for key in sorted(REQUIRED_PLAN_NEXT_TASK_KEYS.difference(addition)):
            findings.append(ReviewFinding("missing_backlog_addition_key", f"backlog addition {index} is missing {key}"))
        order = addition.get("order")
        if order != expected_order:
            findings.append(ReviewFinding("unordered_backlog_addition", f"backlog addition {index} must have order {expected_order}"))
        expected_order += 1
        title = addition.get("title")
        reason = addition.get("reason")
        if not _is_non_empty_string(title) or not _is_non_empty_string(reason):
            findings.append(ReviewFinding("invalid_backlog_addition_text", f"backlog addition {index} needs title and reason"))
        if _is_non_empty_string(title) and " and " in title.lower():
            findings.append(ReviewFinding("broad_backlog_addition", f"backlog addition {index} title should describe one narrow task"))


def _validate_syntax_preflight_recovery(packet: dict[str, Any], findings: list[ReviewFinding]) -> None:
    failures = packet.get("recent_failures", [])
    if not isinstance(failures, list):
        findings.append(ReviewFinding("invalid_recent_failures", "recent_failures must be a list"))
        return
    has_syntax_preflight_failure = any(isinstance(item, dict) and item.get("kind") == "syntax_preflight" for item in failures)
    if not has_syntax_preflight_failure:
        return

    recovery = packet.get("syntax_preflight_recovery", {})
    if not isinstance(recovery, dict):
        findings.append(ReviewFinding("invalid_syntax_preflight_recovery", "syntax_preflight_recovery must be an object after syntax_preflight failures"))
        return
    guidance = recovery.get("parser_clean_validation_guidance", [])
    if not isinstance(guidance, list) or not all(_is_non_empty_string(item) for item in guidance):
        findings.append(ReviewFinding("missing_parser_clean_guidance", "syntax_preflight_recovery needs parser-clean validation guidance"))
        return
    joined = "\n".join(guidance).lower()
    if "py_compile" not in joined or "typescript-style" not in joined or "malformed python" not in joined:
        findings.append(ReviewFinding("incomplete_parser_clean_guidance", "parser-clean guidance must mention py_compile, malformed Python, and TypeScript-style fragments"))


def validate_review_packet(packet: dict[str, Any]) -> list[ReviewFinding]:
    """Return deterministic validation findings for a review packet."""

    findings: list[ReviewFinding] = []
    missing_packet_keys = sorted(REQUIRED_PACKET_KEYS.difference(packet))
    for key in missing_packet_keys:
        findings.append(ReviewFinding("missing_packet_key", f"packet is missing {key}"))

    milestones = packet.get("architecture_milestones", [])
    products = packet.get("completed_data_products", [])
    layers = packet.get("next_missing_layers", [])

    if not isinstance(milestones, list):
        findings.append(ReviewFinding("invalid_milestones", "architecture_milestones must be a list"))
        milestones = []
    if not isinstance(products, list):
        findings.append(ReviewFinding("invalid_products", "completed_data_products must be a list"))
        products = []
    if not isinstance(layers, list):
        findings.append(ReviewFinding("invalid_layers", "next_missing_layers must be a list"))
        layers = []

    milestone_ids: set[str] = set()
    for index, milestone in enumerate(milestones):
        if not isinstance(milestone, dict):
            findings.append(ReviewFinding("invalid_milestone", f"milestone {index} must be an object"))
            continue
        for key in sorted(REQUIRED_MILESTONE_KEYS.difference(milestone)):
            findings.append(ReviewFinding("missing_milestone_key", f"milestone {index} is missing {key}"))
        milestone_id = milestone.get("milestone_id")
        if isinstance(milestone_id, str) and milestone_id:
            milestone_ids.add(milestone_id)
        expected = milestone.get("expected_data_products", [])
        if not isinstance(expected, list) or not all(isinstance(item, str) and item for item in expected):
            findings.append(ReviewFinding("invalid_expected_products", f"milestone {milestone_id or index} expected_data_products must be non-empty strings"))

    product_ids: set[str] = set()
    for index, product in enumerate(products):
        if not isinstance(product, dict):
            findings.append(ReviewFinding("invalid_product", f"product {index} must be an object"))
            continue
        for key in sorted(REQUIRED_PRODUCT_KEYS.difference(product)):
            findings.append(ReviewFinding("missing_product_key", f"product {index} is missing {key}"))
        product_id = product.get("product_id")
        if isinstance(product_id, str) and product_id:
            product_ids.add(product_id)
        linked_ids = product.get("milestone_ids", [])
        if not isinstance(linked_ids, list) or not linked_ids:
            findings.append(ReviewFinding("invalid_product_milestones", f"product {product_id or index} needs milestone_ids"))
            linked_ids = []
        for linked_id in linked_ids:
            if linked_id not in milestone_ids:
                findings.append(ReviewFinding("unknown_product_milestone", f"product {product_id or index} references unknown milestone {linked_id}"))
        fixture_path = product.get("fixture_path")
        if not isinstance(fixture_path, str) or not fixture_path.startswith("ppd/tests/fixtures/"):
            findings.append(ReviewFinding("invalid_fixture_path", f"product {product_id or index} fixture_path must stay under ppd/tests/fixtures/"))

    for index, layer in enumerate(layers):
        if not isinstance(layer, dict):
            findings.append(ReviewFinding("invalid_layer", f"next missing layer {index} must be an object"))
            continue
        for key in sorted(REQUIRED_LAYER_KEYS.difference(layer)):
            findings.append(ReviewFinding("missing_layer_key", f"next missing layer {index} is missing {key}"))
        layer_id = layer.get("layer_id", index)
        layer_type = layer.get("layer_type")
        if layer_type not in ALLOWED_LAYER_TYPES:
            findings.append(ReviewFinding("invalid_layer_type", f"layer {layer_id} has invalid layer_type {layer_type}"))
        milestone_id = layer.get("milestone_id")
        if milestone_id not in milestone_ids:
            findings.append(ReviewFinding("unknown_layer_milestone", f"layer {layer_id} references unknown milestone {milestone_id}"))
        fixture_path = layer.get("recommended_fixture_path")
        if not isinstance(fixture_path, str) or not fixture_path.startswith("ppd/tests/fixtures/"):
            findings.append(ReviewFinding("invalid_recommended_fixture_path", f"layer {layer_id} recommended_fixture_path must stay under ppd/tests/fixtures/"))

    if not product_ids:
        findings.append(ReviewFinding("no_completed_products", "packet must identify at least one completed data product"))
    if not layers:
        findings.append(ReviewFinding("no_next_missing_layers", "packet must identify the next missing layer"))

    _validate_completed_task_history(packet, findings)
    _validate_domain_completion_claims(packet, findings)
    _validate_plan_next_tasks(packet, findings)
    _validate_syntax_preflight_recovery(packet, findings)

    return findings


def summarize_milestone_progress(packet: dict[str, Any]) -> list[MilestoneProgress]:
    """Summarize completed product coverage for each architecture milestone."""

    milestones = packet.get("architecture_milestones", [])
    products = packet.get("completed_data_products", [])
    if not isinstance(milestones, list) or not isinstance(products, list):
        return []

    completed_by_milestone: dict[str, set[str]] = {}
    for product in products:
        if not isinstance(product, dict):
            continue
        product_type = product.get("product_type")
        milestone_ids = product.get("milestone_ids", [])
        if not isinstance(product_type, str) or not isinstance(milestone_ids, list):
            continue
        for milestone_id in milestone_ids:
            if isinstance(milestone_id, str):
                completed_by_milestone.setdefault(milestone_id, set()).add(product_type)

    progress: list[MilestoneProgress] = []
    for milestone in milestones:
        if not isinstance(milestone, dict):
            continue
        milestone_id = milestone.get("milestone_id")
        name = milestone.get("name")
        expected = milestone.get("expected_data_products", [])
        if not isinstance(milestone_id, str) or not isinstance(name, str) or not isinstance(expected, list):
            continue
        expected_types = tuple(item for item in expected if isinstance(item, str))
        completed_types = completed_by_milestone.get(milestone_id, set())
        missing = tuple(item for item in expected_types if item not in completed_types)
        progress.append(MilestoneProgress(milestone_id=milestone_id, name=name, expected_count=len(expected_types), completed_count=len(expected_types) - len(missing), missing_product_types=missing))
    return progress


def next_missing_layers(packet: dict[str, Any]) -> list[dict[str, str]]:
    """Return the ordered next missing fixture, validation, or guardrail layers."""

    layers = packet.get("next_missing_layers", [])
    if not isinstance(layers, list):
        return []

    normalized: list[dict[str, str]] = []
    for layer in layers:
        if not isinstance(layer, dict):
            continue
        layer_id = layer.get("layer_id")
        layer_type = layer.get("layer_type")
        milestone_id = layer.get("milestone_id")
        reason = layer.get("reason")
        fixture_path = layer.get("recommended_fixture_path")
        if all(isinstance(value, str) and value for value in (layer_id, layer_type, milestone_id, reason, fixture_path)):
            normalized.append({"layer_id": layer_id, "layer_type": layer_type, "milestone_id": milestone_id, "reason": reason, "recommended_fixture_path": fixture_path})
    return normalized


def build_review_report(packet: dict[str, Any]) -> dict[str, Any]:
    """Build a compact, deterministic supervisor review report."""

    findings = validate_review_packet(packet)
    progress = summarize_milestone_progress(packet)
    return {
        "packet_id": packet.get("packet_id"),
        "valid": not findings,
        "findings": [finding.__dict__ for finding in findings],
        "milestone_progress": [
            {
                "milestone_id": item.milestone_id,
                "name": item.name,
                "status": item.status,
                "expected_count": item.expected_count,
                "completed_count": item.completed_count,
                "missing_product_types": list(item.missing_product_types),
            }
            for item in progress
        ],
        "next_missing_layers": next_missing_layers(packet),
    }
