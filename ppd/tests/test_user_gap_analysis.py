from __future__ import annotations

import json
from pathlib import Path

from ppd.rules.user_gap_analysis import find_user_gaps


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "user_gap_analysis" / "basic_gap_case.json"


def test_find_user_gaps_uses_only_local_facts_and_evidence_ids() -> None:
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    gaps = find_user_gaps(
        local_user_facts=fixture["local_user_facts"],
        required_facts=fixture["required_facts"],
    )

    assert gaps == fixture["expected_gaps"]


def test_find_user_gaps_rejects_required_fact_without_source_evidence() -> None:
    try:
        find_user_gaps(
            local_user_facts={},
            required_facts=[{"fact_id": "project_address", "label": "Project address"}],
        )
    except ValueError as exc:
        assert "source_evidence_ids" in str(exc)
    else:
        raise AssertionError("expected missing source evidence ids to fail")
