from pathlib import Path

from ppd.crawler.public_frontier_expansion import expand_public_frontier_from_fixture


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "public_frontier_expansion" / "frontier_expansion_packet_v1.json"


def test_public_frontier_expansion_is_metadata_only_and_deterministic() -> None:
    rows = expand_public_frontier_from_fixture(FIXTURE_PATH)

    assert len(rows) == 5
    assert rows == expand_public_frontier_from_fixture(FIXTURE_PATH)
    assert all("raw_body" not in row for row in rows)
    assert all("archive_artifact_ref" not in row for row in rows)
    assert all(row["reviewer_owner"] == "ppd-public-crawl-reviewer" for row in rows)
    assert all(row["rollback_note"].startswith("Discard metadata-only candidates") for row in rows)
    assert all(row["offline_validation_commands"] for row in rows)


def test_public_frontier_expansion_allows_official_html_and_pdf_candidates() -> None:
    rows = expand_public_frontier_from_fixture(FIXTURE_PATH)
    by_url = {row["canonical_url"]: row for row in rows}

    html = by_url["https://www.portland.gov/ppd/get-permit/apply-permits"]
    assert html["source_page"] == "https://www.portland.gov/ppd/how-use-online-permitting-tools"
    assert html["link_text"] == "Apply for permits"
    assert html["content_type_expectation"] == "text/html"
    assert html["allow_skip_decision"] == "allow"
    assert html["skip_reason"] == ""
    assert html["processor_handoff_expectation"] == "candidate_for_html_processor:public_html_metadata_then_normalized_text"

    pdf = by_url["https://www.portland.gov/ppd/documents/how-pay-fees/download"]
    assert pdf["content_type_expectation"] == "application/pdf"
    assert pdf["allow_skip_decision"] == "allow"
    assert pdf["processor_handoff_expectation"] == "candidate_for_pdf_processor:public_pdf_metadata_then_text_extraction"


def test_public_frontier_expansion_records_skips_without_active_frontier_mutation() -> None:
    rows = expand_public_frontier_from_fixture(FIXTURE_PATH)
    by_url = {row["canonical_url"]: row for row in rows}

    devhub_login = by_url["https://devhub.portlandoregon.gov/login"]
    assert devhub_login["allow_skip_decision"] == "skip"
    assert devhub_login["skip_reason"] == "private_or_authenticated"
    assert devhub_login["processor_handoff_expectation"] == "no_handoff:private_or_authenticated"

    outside = by_url["https://example.com/permit-advice"]
    assert outside["allow_skip_decision"] == "skip"
    assert outside["skip_reason"] == "outside_allowlist"
    assert outside["processor_handoff_expectation"] == "no_handoff:outside_allowlist"

    mailto = by_url["mailto:ppd@example.invalid"]
    assert mailto["allow_skip_decision"] == "skip"
    assert mailto["skip_reason"] == "unsupported_scheme"
    assert mailto["processor_handoff_expectation"] == "no_handoff:unsupported_scheme"

    active_frontier_path = Path(__file__).parents[1] / "crawler" / "active_frontier.json"
    assert not active_frontier_path.exists()
