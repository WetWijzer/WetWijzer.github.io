from pathlib import Path

from ppd.extraction.requirement_extraction_rerun_work_order import (
    ATTESTATIONS,
    build_packet_from_fixture_paths,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "requirement_extraction_rerun_work_order"


def test_requirement_extraction_rerun_work_order_is_fixture_first_and_ordered():
    packet = build_packet_from_fixture_paths(
        FIXTURE_DIR / "impact_precheck_packet.json",
        FIXTURE_DIR / "source_freshness_delta_packet.json",
        FIXTURE_DIR / "traceability_review_packet.json",
    )

    assert packet["packet_type"] == "requirement_extraction_rerun_work_order"
    assert packet["mode"] == "fixture_first_metadata_only"
    assert packet["consumed_packet_ids"] == [
        "fixture-impact-precheck-20260529",
        "fixture-source-freshness-delta-20260529",
        "fixture-traceability-review-20260529",
    ]
    assert packet["attestations"] == ATTESTATIONS

    work_items = packet["work_items"]
    assert [item["work_item_id"] for item in work_items] == [
        "synthetic-requirement-rerun-001",
        "synthetic-requirement-rerun-002",
        "synthetic-requirement-rerun-003",
        "synthetic-requirement-rerun-004",
        "synthetic-requirement-rerun-005",
        "synthetic-requirement-rerun-006",
    ]
    assert [item["rerun_reason"] for item in work_items] == [
        "traceability_gap",
        "traceability_gap",
        "source_freshness_delta",
        "source_freshness_delta",
        "impact_precheck",
        "impact_precheck",
    ]


def test_work_items_carry_citations_reviewer_owners_and_metadata_only_outputs():
    packet = build_packet_from_fixture_paths(
        FIXTURE_DIR / "impact_precheck_packet.json",
        FIXTURE_DIR / "source_freshness_delta_packet.json",
        FIXTURE_DIR / "traceability_review_packet.json",
    )

    for item in packet["work_items"]:
        assert item["source_ids"]
        assert item["requirement_ids"]
        assert item["guardrail_ids"]
        assert item["reviewer_owner"]["primary"]
        assert item["reviewer_owner"]["backup"]
        assert item["attestations"] == ATTESTATIONS
        assert item["expected_outputs"]
        for expected_output in item["expected_outputs"]:
            assert expected_output["metadata_only"] is True
            assert "raw_source_body" in expected_output["prohibited_outputs"]
            assert "processor_artifact" in expected_output["prohibited_outputs"]
            assert "new_requirement_node" in expected_output["prohibited_outputs"]
            assert "mutated_requirement_node" in expected_output["prohibited_outputs"]
            assert "mutated_process_model" in expected_output["prohibited_outputs"]
            assert "mutated_guardrail_bundle" in expected_output["prohibited_outputs"]


def test_packet_expected_outputs_are_metadata_only():
    packet = build_packet_from_fixture_paths(
        FIXTURE_DIR / "impact_precheck_packet.json",
        FIXTURE_DIR / "source_freshness_delta_packet.json",
        FIXTURE_DIR / "traceability_review_packet.json",
    )

    assert packet["expected_packet_outputs"]
    assert all(output["metadata_only"] is True for output in packet["expected_packet_outputs"])
    assert all("raw_source_body" in output["prohibited_outputs"] for output in packet["expected_packet_outputs"])
