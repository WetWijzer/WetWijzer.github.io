from __future__ import annotations

import json
from pathlib import Path

from ppd.draft_executor_review_packet_v2 import build_draft_executor_review_packet_v2

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "draft_executor_review_packet_v2"


def _load_fixture(name: str) -> dict:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def test_draft_executor_review_packet_v2_builds_ordered_reviewer_rows() -> None:
    packet = build_draft_executor_review_packet_v2(_load_fixture("draft_executor_dry_run_contract_v2.json"))

    assert packet["packet_type"] == "reversible_draft_executor_review_packet_v2"
    assert packet["packet_version"] == 2
    assert packet["mode"] == "fixture_first_offline_review_only"
    assert [row["review_order"] for row in packet["reviewer_rows"]] == [1, 2, 3, 4, 5, 6, 7]
    assert [row["review_area"] for row in packet["reviewer_rows"]] == [
        "dry_run_request_acceptance",
        "preview_only_response_review",
        "user_fact_trace_review",
        "source_evidence_trace_review",
        "selector_confidence_hold_reasons",
        "exact_confirmation_stop_gate_review",
        "refused_consequential_action_review",
    ]


def test_draft_executor_review_packet_v2_reviews_request_and_preview_only_response_fields() -> None:
    packet = build_draft_executor_review_packet_v2(_load_fixture("draft_executor_dry_run_contract_v2.json"))
    request_row = packet["reviewer_rows"][0]
    response_row = packet["reviewer_rows"][1]

    assert request_row["dry_run_request_acceptance"]["accepted_request_kind"] == "synthetic_executor_preview_request"
    assert request_row["dry_run_request_acceptance"]["all_requests_preview_only"] is True
    assert request_row["dry_run_request_acceptance"]["accepted_source_action_ids"] == ["act-001", "act-002", "act-003"]

    response_reviews = response_row["preview_only_response_review"]
    assert [item["source_row_id"] for item in response_reviews] == ["dryrun-v2-001", "dryrun-v2-002", "dryrun-v2-003"]
    assert all(item["executed_playwright_actions"] == [] for item in response_reviews)
    assert all(item["saved_official_drafts"] == [] for item in response_reviews)
    assert all(item["uploaded_files"] == [] for item in response_reviews)
    assert all(item["forbidden_flags_clear"] is True for item in response_reviews)


def test_draft_executor_review_packet_v2_reviews_traces_holds_stop_gates_and_refusals() -> None:
    packet = build_draft_executor_review_packet_v2(_load_fixture("draft_executor_dry_run_contract_v2.json"))

    user_fact_reviews = packet["reviewer_rows"][2]["user_fact_trace_review"]
    source_evidence_reviews = packet["reviewer_rows"][3]["source_evidence_trace_review"]
    selector_holds = packet["reviewer_rows"][4]["selector_confidence_hold_reasons"]
    stop_gates = packet["reviewer_rows"][5]["exact_confirmation_stop_gate_review"]
    refusals = packet["reviewer_rows"][6]["refused_consequential_action_review"]

    assert all(item["trace_count"] == 1 for item in user_fact_reviews)
    assert all(item["trace_count"] == 1 for item in source_evidence_reviews)
    assert all(item["hold_required"] is True for item in selector_holds)
    assert all(item["hold_reason"] == "offline fixture contract does not evaluate live DOM selectors" for item in selector_holds)
    assert all(item["requires_exact_confirmation"] is True for item in stop_gates)
    assert stop_gates[0]["confirmation_phrase"] == "I confirm this is a preview-only dry run and no official PP&D action will be taken."
    assert refusals == [
        {
            "source_row_id": "dryrun-v2-002",
            "reason": "consequential action is outside reversible preview-only dry-run scope",
            "example": "submit",
        },
        {
            "source_row_id": "dryrun-v2-003",
            "reason": "consequential action is outside reversible preview-only dry-run scope",
            "example": "upload_file",
        },
    ]


def test_draft_executor_review_packet_v2_exposes_exact_offline_validation_commands() -> None:
    packet = build_draft_executor_review_packet_v2(_load_fixture("draft_executor_dry_run_contract_v2.json"))

    assert packet["offline_validation_commands"] == [
        ["python3", "-m", "py_compile", "ppd/draft_executor_review_packet_v2.py"],
        ["python3", "-m", "pytest", "ppd/tests/test_draft_executor_review_packet_v2.py"],
        ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
    ]
    assert packet["side_effects"] == {
        "playwright_actions_executed": False,
        "devhub_opened": False,
        "live_forms_filled": False,
        "official_drafts_saved": False,
        "files_uploaded": False,
        "submitted": False,
        "certified": False,
        "paid": False,
        "scheduled": False,
        "cancelled": False,
        "accounts_changed": False,
        "release_state_activated": False,
    }
