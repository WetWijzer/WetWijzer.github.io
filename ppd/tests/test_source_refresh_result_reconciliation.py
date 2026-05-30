import json
from pathlib import Path

from ppd.source_refresh_result_reconciliation import reconcile_source_refresh_results


def test_reconciles_fixture_packets_into_cited_source_decisions():
    fixture_path = Path(__file__).parent / "fixtures" / "source_refresh_result_reconciliation" / "packet_bundle.json"
    bundle = json.loads(fixture_path.read_text(encoding="utf-8"))

    packet = reconcile_source_refresh_results(
        bundle["source_freshness_delta_review_packet"],
        bundle["public_source_refresh_metadata_intake_packet"],
        bundle["requirement_extraction_rerun_result_intake_packet"],
        reviewer_owner="ppd-reviewer:source-refresh",
    )

    assert packet == bundle["expected_reconciliation_packet"]
    assert packet["attestations"] == {
        "no_live_crawl": True,
        "no_processor_execution": True,
        "no_registry_mutation": True,
        "no_requirement_mutation": True,
        "no_guardrail_mutation": True,
    }


def test_reviewer_owner_is_required():
    fixture_path = Path(__file__).parent / "fixtures" / "source_refresh_result_reconciliation" / "packet_bundle.json"
    bundle = json.loads(fixture_path.read_text(encoding="utf-8"))

    try:
        reconcile_source_refresh_results(
            bundle["source_freshness_delta_review_packet"],
            bundle["public_source_refresh_metadata_intake_packet"],
            bundle["requirement_extraction_rerun_result_intake_packet"],
            reviewer_owner="",
        )
    except ValueError as exc:
        assert "reviewer_owner" in str(exc)
    else:
        raise AssertionError("expected reviewer_owner validation failure")
