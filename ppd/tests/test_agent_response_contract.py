from __future__ import annotations

import json
from pathlib import Path

from ppd.agent_response_contract import RECOMMENDATION_ORDER, build_agent_recommendations


FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "agent_response_contract"
    / "synthetic_ready_to_draft_packet.json"
)


def _load_fixture() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def test_fixture_builds_all_recommendation_types_in_stable_order() -> None:
    fixture = _load_fixture()

    response = build_agent_recommendations(
        fixture["ready_to_draft_packet"], fixture["refreshed_guardrail_status"]
    )

    assert response["case_id"] == "synthetic-sfr-adu-001"
    assert response["recommendation_order"] == list(RECOMMENDATION_ORDER)
    assert [item["kind"] for item in response["recommendations"]] == list(
        RECOMMENDATION_ORDER
    )


def test_each_recommendation_is_cited_to_fixture_evidence() -> None:
    fixture = _load_fixture()

    response = build_agent_recommendations(
        fixture["ready_to_draft_packet"], fixture["refreshed_guardrail_status"]
    )

    for recommendation in response["recommendations"]:
        assert recommendation["citations"], recommendation["kind"]
        for citation in recommendation["citations"]:
            assert citation["evidence_id"].startswith("ppd-")
            assert citation["url"].startswith("https://www.portland.gov/ppd")
            assert citation["accessed_at"] == "2026-05-08"


def test_reversible_and_local_recommendations_do_not_require_attendance() -> None:
    fixture = _load_fixture()

    response = build_agent_recommendations(
        fixture["ready_to_draft_packet"], fixture["refreshed_guardrail_status"]
    )
    by_kind = {item["kind"]: item for item in response["recommendations"]}

    assert by_kind["local_preview"]["status"] == "available"
    assert by_kind["local_preview"]["reversible"] is True
    assert by_kind["local_preview"]["requires_user_attendance"] is False
    assert by_kind["reversible_draft"]["status"] == "available"
    assert by_kind["reversible_draft"]["reversible"] is True
    assert by_kind["reversible_draft"]["requires_user_attendance"] is False
    assert "submit" not in by_kind["local_preview"]["next_action"].lower()


def test_manual_handoff_and_refused_actions_gate_official_devhub_work() -> None:
    fixture = _load_fixture()

    response = build_agent_recommendations(
        fixture["ready_to_draft_packet"], fixture["refreshed_guardrail_status"]
    )
    by_kind = {item["kind"]: item for item in response["recommendations"]}

    assert by_kind["manual_handoff"]["status"] == "handoff_required"
    assert by_kind["manual_handoff"]["requires_user_attendance"] is True
    assert "devhub_login" in by_kind["manual_handoff"]["blocked_actions"]
    assert by_kind["refused_action"]["status"] == "refused"
    assert by_kind["refused_action"]["requires_user_attendance"] is True
    assert "submit_permit_request" in by_kind["refused_action"]["blocked_actions"]
    assert "submit_payment" in by_kind["refused_action"]["blocked_actions"]
