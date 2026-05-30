from __future__ import annotations

import json
from pathlib import Path

from ppd.public_source_change_impact_rehearsal import (
    REQUIRED_ATTESTATIONS,
    build_change_impact_rows,
    validate_change_impact_rows,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "public_source_change_impact"


def _load_fixture(name: str) -> dict:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def test_build_change_impact_rows_from_committed_fixtures() -> None:
    traceability_packet = _load_fixture("source_to_requirement_traceability_packet_v1.json")
    freshness_handoff = _load_fixture("public_freshness_reviewer_handoff_v1.json")

    rows = build_change_impact_rows(traceability_packet, freshness_handoff)

    assert len(rows) == 2
    validate_change_impact_rows(rows)
    assert rows[0]["affected_source_ids"] == ["PPD-SRC-PORTLAND-ZONING-001"]
    assert "33.110.220" in rows[0]["document_sections"]
    assert "PPD-REQ-ZONING-SETBACKS" in rows[0]["requirement_ids"]
    assert "requirement-mapping" in rows[0]["process_stages"]
    assert "PPD-GUARDRAIL-PUBLIC-SOURCE-V1" in rows[0]["guardrail_bundle_ids"]
    assert rows[0]["reviewer_owner"] == "planning-policy-reviewer"
    assert rows[0]["reviewer_backup_owner"] == "ppd-guardrails-reviewer"
    assert rows[0]["rollback_notes"].startswith("Remove generated rehearsal row")
    assert rows[0]["attestations"] == REQUIRED_ATTESTATIONS


def test_rows_include_citations_and_offline_validation_commands_only() -> None:
    rows = build_change_impact_rows(
        _load_fixture("source_to_requirement_traceability_packet_v1.json"),
        _load_fixture("public_freshness_reviewer_handoff_v1.json"),
    )

    for row in rows:
        assert row["citations"]
        assert all(citation.startswith("fixture://") for citation in row["citations"])
        assert row["offline_validation_commands"] == [
            ["python3", "-m", "py_compile", "ppd/public_source_change_impact_rehearsal.py"],
            ["python3", "-m", "pytest", "ppd/tests/test_public_source_change_impact_rehearsal.py"],
        ]
        assert row["attestations"]["no_live_crawl"] is True
        assert row["attestations"]["no_download"] is True
        assert row["attestations"]["no_raw_body"] is True
        assert row["attestations"]["no_active_registry_mutation"] is True
