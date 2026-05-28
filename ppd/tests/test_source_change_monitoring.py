from pathlib import Path

from ppd.source_change_monitoring import build_report_from_files

FIXTURES = Path(__file__).parent / "fixtures" / "source_change_monitoring"


def test_source_change_report_flags_hash_cadence_fee_deadline_and_affected_ids():
    report = build_report_from_files(
        FIXTURES / "reviewed_sources.json",
        FIXTURES / "extraction_candidates.json",
        as_of="2026-05-28",
    )

    assert report["report_kind"] == "ppd_source_change_monitoring"
    assert report["summary"] == {
        "sources_checked": 2,
        "sources_requiring_review": 2,
        "affected_requirement_node_ids": [
            "RequirementNode:PPD:fees:building-permit",
            "RequirementNode:PPD:intake:residential",
        ],
        "affected_guardrail_bundle_ids": [
            "GuardrailBundle:PPD:deadline-review",
            "GuardrailBundle:PPD:fee-review",
        ],
    }

    fee_source = report["sources"][0]
    assert fee_source["source_id"] == "building-permit-fees"
    assert fee_source["hash_changed"] is True
    assert fee_source["recrawl"]["overdue"] is True
    assert fee_source["changed_file_rules"] == ["fee_schedule_pdf_changed", "table_heading_changed"]
    assert fee_source["changed_fee_language_candidates"] == ["candidate-fees-20260528"]
    assert fee_source["affected_requirement_node_ids"] == ["RequirementNode:PPD:fees:building-permit"]
    assert fee_source["affected_guardrail_bundle_ids"] == ["GuardrailBundle:PPD:fee-review"]
    assert any("fee language" in prompt for prompt in fee_source["human_review_prompts"])

    intake_source = report["sources"][1]
    assert intake_source["source_id"] == "residential-permit-intake"
    assert intake_source["hash_changed"] is False
    assert intake_source["recrawl"]["overdue"] is False
    assert intake_source["changed_deadline_language_candidates"] == ["candidate-intake-20260528"]
    assert intake_source["affected_requirement_node_ids"] == ["RequirementNode:PPD:intake:residential"]
    assert intake_source["affected_guardrail_bundle_ids"] == ["GuardrailBundle:PPD:deadline-review"]
    assert any("deadline language" in prompt for prompt in intake_source["human_review_prompts"])
