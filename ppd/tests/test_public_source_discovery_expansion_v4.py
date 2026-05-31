from pathlib import Path

from ppd.crawler.public_source_discovery_expansion_v4 import (
    ALLOWED_HOSTS,
    SKIP_REASON_CODES,
    build_expansion_packet,
    canonicalize_url,
    load_fixture,
    validate_expansion_packet,
)

FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "public_source_discovery_expansion_v4"
    / "synthetic_anchor_pages.json"
)


def test_fixture_first_expansion_packet_validates_offline() -> None:
    fixture = load_fixture(FIXTURE_PATH)
    packet = build_expansion_packet(fixture)

    assert validate_expansion_packet(packet) == []
    assert packet["metadata"]["fixture_only"] is True
    assert packet["metadata"]["no_network_access"] is True
    assert packet["metadata"]["no_live_crawl"] is True
    assert packet["metadata"]["no_raw_downloads"] is True
    assert packet["metadata"]["no_processor_execution"] is True
    assert packet["metadata"]["no_devhub_access"] is True
    assert packet["metadata"]["no_registry_mutation"] is True
    assert set(packet["metadata"]["allowed_hosts"]) == ALLOWED_HOSTS
    assert set(packet["metadata"]["skip_reason_codes"]) == SKIP_REASON_CODES


def test_discovered_rows_preserve_source_page_and_link_text_evidence() -> None:
    packet = build_expansion_packet(load_fixture(FIXTURE_PATH))
    source_evidence_ids = {
        row["source_page_evidence_id"] for row in packet["source_page_evidence"]
    }
    link_evidence_by_id = {
        row["link_text_evidence_id"]: row for row in packet["link_text_evidence"]
    }

    assert packet["discovered_link_rows"]
    for row in packet["discovered_link_rows"]:
        assert row["source_page_evidence_id"] in source_evidence_ids
        assert row["link_text_evidence_id"] in link_evidence_by_id
        assert link_evidence_by_id[row["link_text_evidence_id"]]["link_text"].strip()
        assert canonicalize_url(row["canonical_url"]) == row["canonical_url"]
        assert "raw_body" not in row
        assert "raw_html" not in row


def test_allowlist_decisions_cover_allowed_and_skipped_sources() -> None:
    packet = build_expansion_packet(load_fixture(FIXTURE_PATH))
    decisions = {row["canonical_url"]: row for row in packet["allowlist_decisions"]}

    assert decisions["https://www.portland.gov/ppd/how-use-online-permitting-tools"]["decision"] == "allow"
    assert decisions["https://www.portland.gov/ppd/get-permit/apply-permits"]["decision"] == "allow"
    assert decisions["https://devhub.portlandoregon.gov"]["decision"] == "allow"
    assert decisions["https://www.portlandmaps.com"]["decision"] == "allow"
    assert decisions["https://example.com/permit-reference"]["skip_reason_code"] == "outside_allowlist"
    assert decisions["mailto:devhub@example.invalid"]["skip_reason_code"] == "unsupported_scheme"
    assert decisions["https://www.portland.gov/ppd/documents/how-pay-fees/download"]["skip_reason_code"] == "raw_download_not_permitted"
    assert decisions["https://www.portland.gov/user/login"]["skip_reason_code"] == "private_authenticated"


def test_duplicate_normalization_rows_identify_canonical_duplicates() -> None:
    packet = build_expansion_packet(load_fixture(FIXTURE_PATH))
    duplicates = packet["duplicate_normalization_rows"]

    assert duplicates
    assert {
        row["canonical_url"] for row in duplicates
    } == {"https://www.portland.gov/ppd/get-permit/apply-permits"}
    assert all(row["normalization_basis"] == "canonical_url" for row in duplicates)


def test_skipped_url_reason_rows_are_complete_and_policy_grounded() -> None:
    packet = build_expansion_packet(load_fixture(FIXTURE_PATH))
    skipped_ids = {
        row["discovery_id"] for row in packet["discovered_link_rows"] if row["decision"] == "skip"
    }
    reason_ids = {row["discovery_id"] for row in packet["skipped_url_reason_rows"]}

    assert skipped_ids == reason_ids
    assert {row["skip_reason_code"] for row in packet["skipped_url_reason_rows"]} == {
        "outside_allowlist",
        "unsupported_scheme",
        "raw_download_not_permitted",
        "private_authenticated",
    }


def test_packet_includes_exact_offline_validation_commands() -> None:
    packet = build_expansion_packet(load_fixture(FIXTURE_PATH))

    assert packet["offline_validation_commands"] == [
        ["python3", "-m", "py_compile", "ppd/crawler/public_source_discovery_expansion_v4.py", "ppd/tests/test_public_source_discovery_expansion_v4.py"],
        ["python3", "-m", "pytest", "ppd/tests/test_public_source_discovery_expansion_v4.py"],
        ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
    ]
