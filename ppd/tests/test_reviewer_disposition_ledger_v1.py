from __future__ import annotations

import json
from pathlib import Path

from ppd.reviewer_disposition_ledger_v1 import REQUIRED_ATTESTATIONS, build_reviewer_disposition_ledger

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "reviewer_disposition_ledger_v1"


def test_build_reviewer_disposition_ledger_v1_matches_fixture() -> None:
    expected = json.loads((FIXTURE_DIR / "expected_reviewer_disposition_ledger_v1.json").read_text(encoding="utf-8"))
    assert build_reviewer_disposition_ledger(FIXTURE_DIR) == expected


def test_reviewer_disposition_records_include_required_attestations() -> None:
    ledger = build_reviewer_disposition_ledger(FIXTURE_DIR)
    assert len(ledger["records"]) == 3
    for record in ledger["records"]:
        assert record["attestations"] == REQUIRED_ATTESTATIONS
        assert record["disposition"] in {"approve", "defer", "block"}
        assert record["citations"]
        assert record["offline_validation_command"]
