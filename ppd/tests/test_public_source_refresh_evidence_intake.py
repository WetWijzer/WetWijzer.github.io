from __future__ import annotations

from pathlib import Path

from ppd.extraction.public_source_refresh_evidence_intake import (
    ATTESTATIONS,
    PACKET_VERSION,
    FixtureIntakeInputs,
    build_packet_from_fixture_paths,
    load_json,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "public_source_refresh_evidence_intake"


def test_fixture_first_public_source_refresh_evidence_intake_matches_expected_packet() -> None:
    packet = build_packet_from_fixture_paths(
        FixtureIntakeInputs(
            freshness_handoff_path=FIXTURE_DIR / "public_freshness_reviewer_handoff_v1.json",
            change_impact_rehearsal_path=FIXTURE_DIR / "public_source_change_impact_rehearsal_v1.json",
        )
    )

    expected = load_json(FIXTURE_DIR / "fixture_first_public_source_refresh_evidence_intake_v1.json")

    assert packet == expected


def test_intake_packet_is_metadata_only_and_offline_validation_ready() -> None:
    packet = build_packet_from_fixture_paths(
        FixtureIntakeInputs(
            freshness_handoff_path=FIXTURE_DIR / "public_freshness_reviewer_handoff_v1.json",
            change_impact_rehearsal_path=FIXTURE_DIR / "public_source_change_impact_rehearsal_v1.json",
        )
    )

    assert packet["packet_version"] == PACKET_VERSION
    assert packet["attestations"] == ATTESTATIONS
    assert packet["rows"]

    for row in packet["rows"]:
        assert row["attestations"] == ATTESTATIONS
        assert row["observed_public_page_title"]
        assert row["visible_updated_date"]
        assert row["affected_source_ids"] == sorted(set(row["affected_source_ids"]))
        assert row["affected_requirement_ids"] == sorted(set(row["affected_requirement_ids"]))
        assert row["defer_reason"]
        assert row["rollback_note"]
        assert ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"] in row["offline_validation_commands"]
        assert "raw_body" not in row
        assert "downloaded_document_path" not in row
        assert "processor_output_path" not in row

        for citation in row["citations"]:
            assert sorted(citation) == ["label", "observed_field", "url"]
            assert citation["url"].startswith("https://www.portland.gov/")
