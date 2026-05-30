from pathlib import Path

from ppd.public_source_refresh_patch_preview_v3 import (
    BLOCK_CITATION_LOSS,
    build_preview_from_fixture_paths,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "public_source_refresh_patch_preview_v3"


def test_preview_rows_are_deterministic_and_fixture_first():
    preview = build_preview_from_fixture_paths(
        FIXTURE_DIR / "public_source_refresh_plan_v2.json",
        FIXTURE_DIR / "source_to_requirement_traceability_packet_v1.json",
        FIXTURE_DIR / "inactive_public_source_fixtures.json",
    )

    assert preview["preview_version"] == "public_source_refresh_inactive_patch_preview_v3"
    assert preview["mode"] == "fixture_first_no_live_crawl_no_active_mutation"
    assert preview["determinism"]["network_policy"] == "disabled"
    assert [row["source_id"] for row in preview["preview_rows"]] == [
        "ppd-devhub-faq-public",
        "ppd-submit-plans-online-public",
    ]


def test_preview_preserves_traceability_and_owner_metadata():
    preview = build_preview_from_fixture_paths(
        FIXTURE_DIR / "public_source_refresh_plan_v2.json",
        FIXTURE_DIR / "source_to_requirement_traceability_packet_v1.json",
        FIXTURE_DIR / "inactive_public_source_fixtures.json",
    )
    faq_row = preview["preview_rows"][0]

    assert faq_row["reviewer_owner"] == "ppd-public-source-reviewer"
    assert faq_row["affected_references"] == {
        "requirements": ["REQ-DEVHUB-ACCOUNT-001", "REQ-DEVHUB-CORRECTIONS-001"],
        "processes": ["PROC-DEVHUB-ACCOUNT-SETUP", "PROC-DEVHUB-CORRECTIONS"],
        "guardrails": ["GRD-AUTH-ATTENDANCE-001", "GRD-CORRECTION-UPLOAD-GATE-001"],
    }
    assert faq_row["citation_preservation_check"]["passed"] is True
    assert faq_row["proposed_patch"]["mutates_active_artifacts"] is False
    assert faq_row["proposed_patch"]["raw_content_committed"] is False
    assert faq_row["proposed_patch"]["live_crawl_required"] is False


def test_blocked_row_explains_citation_loss():
    preview = build_preview_from_fixture_paths(
        FIXTURE_DIR / "public_source_refresh_plan_v2.json",
        FIXTURE_DIR / "source_to_requirement_traceability_packet_v1.json",
        FIXTURE_DIR / "inactive_public_source_fixtures.json",
    )
    blocked = {row["source_id"]: row for row in preview["blocked_rows"]}

    assert "ppd-submit-plans-online-public" in blocked
    assert BLOCK_CITATION_LOSS in blocked["ppd-submit-plans-online-public"]["blocked_reasons"]
    assert "required traceability citations" in blocked["ppd-submit-plans-online-public"]["explanation"]


def test_validation_inventory_mentions_requirements_processes_and_guardrails():
    preview = build_preview_from_fixture_paths(
        FIXTURE_DIR / "public_source_refresh_plan_v2.json",
        FIXTURE_DIR / "source_to_requirement_traceability_packet_v1.json",
        FIXTURE_DIR / "inactive_public_source_fixtures.json",
    )
    validation_ids = {item["validation_id"] for item in preview["validation_inventory"]}

    assert "ppd-devhub-faq-public:requirement:REQ-DEVHUB-ACCOUNT-001" in validation_ids
    assert "ppd-devhub-faq-public:process:PROC-DEVHUB-CORRECTIONS" in validation_ids
    assert "ppd-devhub-faq-public:guardrail:GRD-AUTH-ATTENDANCE-001" in validation_ids
    assert "ppd-submit-plans-online-public:citation-preservation" in validation_ids
