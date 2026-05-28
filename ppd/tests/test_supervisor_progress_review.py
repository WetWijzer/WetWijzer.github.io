from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from ppd.supervisor_progress_review import (
    build_review_report,
    load_review_packet,
    next_missing_layers,
    summarize_milestone_progress,
    validate_review_packet,
)

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "supervisor_progress_review" / "review_packet.json"


def finding_codes(packet: dict[str, object]) -> set[str]:
    return {finding.code for finding in validate_review_packet(packet)}


def test_review_packet_fixture_is_valid() -> None:
    packet = load_review_packet(FIXTURE_PATH)

    findings = validate_review_packet(packet)

    assert findings == []


def test_review_packet_maps_completed_products_to_milestones() -> None:
    packet = load_review_packet(FIXTURE_PATH)

    progress = {item.milestone_id: item for item in summarize_milestone_progress(packet)}

    assert progress["source-registry"].status == "partial"
    assert progress["source-registry"].missing_product_types == ("source_registry_validator",)
    assert progress["archive-manifest"].status == "partial"
    assert progress["document-record"].status == "partial"
    assert progress["requirement-node"].status == "partial"
    assert progress["process-model"].status == "partial"
    assert progress["guardrail-bundle"].status == "partial"
    assert progress["guardrail-bundle"].missing_product_types == ("guardrail_bundle_validator",)


def test_review_packet_identifies_next_missing_layers_in_order() -> None:
    packet = load_review_packet(FIXTURE_PATH)

    layers = next_missing_layers(packet)

    assert [layer["layer_type"] for layer in layers] == ["validation", "guardrail", "fixture"]
    assert layers[0]["recommended_fixture_path"].startswith("ppd/tests/fixtures/")
    assert layers[1]["milestone_id"] == "guardrail-bundle"
    assert "exact confirmation" in layers[1]["reason"]


def test_review_report_is_compact_and_deterministic() -> None:
    packet = load_review_packet(FIXTURE_PATH)

    report = build_review_report(packet)

    assert report["packet_id"] == "supervisor-20260527-132-progress-review-guardrails"
    assert report["valid"] is True
    assert report["findings"] == []
    assert len(report["milestone_progress"]) == 6
    assert len(report["next_missing_layers"]) == 3


def test_review_packet_requires_preserved_completed_task_history() -> None:
    packet = load_review_packet(FIXTURE_PATH)
    packet["completed_task_history"] = []

    assert "missing_completed_task_history" in finding_codes(packet)


def test_review_packet_rejects_complete_domain_without_promoted_source_changes() -> None:
    packet = load_review_packet(FIXTURE_PATH)
    packet["domain_completion_claims"][0]["status"] = "complete"
    packet["domain_completion_claims"][0]["promoted_source_change_ids"] = []

    assert "complete_domain_without_promoted_source_changes" in finding_codes(packet)


def test_review_packet_keeps_plan_next_tasks_narrow_and_ordered() -> None:
    packet = load_review_packet(FIXTURE_PATH)
    mutated = deepcopy(packet)
    mutated["plan_next_tasks"]["backlog_additions"] = [
        {"order": 2, "task_id": "task-wide", "title": "Add parser repair and crawl promotion", "reason": "too broad"},
        {"order": 3, "task_id": "task-extra-a", "title": "Add fixture A", "reason": "extra"},
        {"order": 4, "task_id": "task-extra-b", "title": "Add fixture B", "reason": "extra"},
        {"order": 5, "task_id": "task-extra-c", "title": "Add fixture C", "reason": "extra"},
    ]

    codes = finding_codes(mutated)

    assert "too_many_backlog_additions" in codes
    assert "unordered_backlog_addition" in codes
    assert "broad_backlog_addition" in codes


def test_review_packet_requires_parser_clean_guidance_after_syntax_preflight_failure() -> None:
    packet = load_review_packet(FIXTURE_PATH)
    packet["syntax_preflight_recovery"]["parser_clean_validation_guidance"] = ["Run validation later."]

    assert "incomplete_parser_clean_guidance" in finding_codes(packet)
