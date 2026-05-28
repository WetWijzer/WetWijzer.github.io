from __future__ import annotations

from datetime import date

from ppd.validation.agent_preflight import validate_agent_preflight_decision_matrix


def test_accepts_matrix_with_required_safety_gates() -> None:
    matrix = {
        "recommendations": [
            {
                "text": "Use the public permit checklist.",
                "citations": [{"url": "https://www.portland.gov/example/checklist"}],
            }
        ],
        "process_evidence": [{"observed_on": "2026-05-20", "source": "public page"}],
        "human_review": {"required": True, "reviewer": "operator"},
        "artifacts": [{"path": "ppd/tests/fixtures/preflight/public-checklist.json", "visibility": "public"}],
        "actions": [
            {"name": "prepare draft", "consequential": False},
            {"name": "submit application", "consequential": True, "confirmation": "exact"},
            {
                "name": "pay permit fee",
                "financial": True,
                "classification": "manual_handoff",
                "confirmation": "exact",
            },
        ],
    }

    result = validate_agent_preflight_decision_matrix(matrix, today=date(2026, 5, 27))

    assert result.accepted is True
    assert result.issues == ()


def test_rejects_uncited_stale_missing_review_private_and_action_risks() -> None:
    matrix = {
        "recommendations": [{"text": "Submit this option."}],
        "process_evidence": [{"observed_on": "2026-04-01", "source": "old page"}],
        "human_review": {"required": False},
        "artifacts": [{"path": "ipfs_datasets_py/.daemon/session-trace.json", "visibility": "private"}],
        "actions": [
            {"name": "submit application", "consequential": True, "confirmation": "click"},
            {"name": "pay fee", "financial": True, "classification": "automated"},
        ],
    }

    result = validate_agent_preflight_decision_matrix(matrix, today=date(2026, 5, 27))

    assert result.accepted is False
    assert {issue.code for issue in result.issues} == {
        "uncited_recommendation",
        "stale_process_evidence",
        "missing_human_review_gate",
        "private_artifact",
        "missing_exact_confirmation",
        "financial_action_without_manual_handoff",
    }
