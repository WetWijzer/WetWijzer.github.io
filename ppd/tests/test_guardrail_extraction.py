from __future__ import annotations

import json
from pathlib import Path

from ppd.logic.guardrail_extraction import extract_guardrails


FIXTURE = Path(__file__).parent / "fixtures" / "logic" / "processor_requirement_batch.json"


def test_extract_guardrails_from_processor_requirement_batch() -> None:
    batch = json.loads(FIXTURE.read_text(encoding="utf-8"))

    result = extract_guardrails(batch)

    assert result["batch_id"] == "fixture-permit-batch"
    assert {item["requirement_id"] for item in result["obligations"]} == {
        "req-zoning-check",
        "req-submit-stop",
    }
    assert result["prerequisites"][0]["requirement_id"] == "req-zoning-check"
    assert {item["question"] for item in result["missing_fact_questions"]} == {
        "What is the value for zoning designation?",
        "What is the value for overlay status?",
        "What is the value for the unspecified requirement fact?",
    }
    assert [item["requirement_id"] for item in result["reversible_action_predicates"]] == ["req-draft-only"]
    assert [item["requirement_id"] for item in result["exact_confirmation_predicates"]] == ["req-submit-stop"]
    assert result["refused_official_action_stop_gates"] == [
        {
            "id": "req-submit-stop:stop_gate",
            "requirement_id": "req-submit-stop",
            "action": "submit",
            "reason": "Official PP&D actions require explicit human control and exact confirmation.",
            "source": "fixture://ppd/requirements",
        }
    ]
