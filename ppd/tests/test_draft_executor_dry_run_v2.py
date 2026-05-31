from __future__ import annotations

import json
from pathlib import Path

from ppd.draft_executor_dry_run_v2 import build_draft_executor_dry_run_v2

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "draft_executor_dry_run_v2"


def _load_fixture(name: str) -> dict:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def test_draft_executor_dry_run_v2_builds_ordered_preview_rows() -> None:
    contract = build_draft_executor_dry_run_v2(
        _load_fixture("preflight_decision_table_v2.json"),
        _load_fixture("human_review_handoff_packet_v2.json"),
    )

    assert contract["contract_version"] == "draft_executor_dry_run_v2"
    assert contract["mode"] == "fixture_first_offline_preview_only"
    assert contract["source_contracts"] == [
        "guarded_action_preflight_decision_table_v2",
        "post_preview_human_review_handoff_packet_v2",
    ]
    assert [row["synthetic_row_id"] for row in contract["rows"]] == [
        "dryrun-v2-001",
        "dryrun-v2-002",
        "dryrun-v2-003",
    ]


def test_draft_executor_dry_run_v2_requires_traces_and_selector_placeholders() -> None:
    contract = build_draft_executor_dry_run_v2(
        _load_fixture("preflight_decision_table_v2.json"),
        _load_fixture("human_review_handoff_packet_v2.json"),
    )
    first = contract["rows"][0]

    assert first["preview_only"] is True
    assert first["field_mapping"]["preview_value"] == "1120 SW 5th Ave, Portland, OR"
    assert first["user_fact_trace"] == [
        {"trace_kind": "user_fact", "key": "project_address", "value_present": True}
    ]
    assert first["source_evidence_trace"] == [
        {"trace_kind": "source_evidence", "key": "project_address", "value_present": True}
    ]
    assert first["selector_confidence"] == {
        "placeholder": True,
        "value": None,
        "reason": "offline fixture contract does not evaluate live DOM selectors",
    }


def test_draft_executor_dry_run_v2_stop_gates_and_refuses_consequential_actions() -> None:
    contract = build_draft_executor_dry_run_v2(
        _load_fixture("preflight_decision_table_v2.json"),
        _load_fixture("human_review_handoff_packet_v2.json"),
    )
    rows = contract["rows"]

    for row in rows:
        assert row["stop_gate"]["requires_exact_confirmation"] is True
        assert row["response"]["executed_playwright_actions"] == []
        assert row["response"]["saved_official_drafts"] == []
        assert row["response"]["uploaded_files"] == []
        assert row["response"]["submitted"] is False
        assert row["response"]["paid"] is False
        assert row["response"]["scheduled"] is False
        assert row["response"]["cancelled"] is False
        assert row["response"]["account_changed"] is False
        assert row["response"]["release_state_activated"] is False

    assert rows[1]["refusal"] == {
        "refused": True,
        "reason": "consequential action is outside reversible preview-only dry-run scope",
        "example": "submit",
    }
    assert rows[2]["refusal"]["example"] == "upload_file"
    assert "activate_release_state" in contract["refused_consequential_action_examples"]


def test_draft_executor_dry_run_v2_exposes_exact_offline_validation_commands() -> None:
    contract = build_draft_executor_dry_run_v2(
        _load_fixture("preflight_decision_table_v2.json"),
        _load_fixture("human_review_handoff_packet_v2.json"),
    )

    assert contract["offline_validation_commands"] == [
        ["python3", "-m", "py_compile", "ppd/draft_executor_dry_run_v2.py"],
        ["python3", "-m", "pytest", "ppd/tests/test_draft_executor_dry_run_v2.py"],
        ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
    ]
