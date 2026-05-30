from __future__ import annotations

import json
from pathlib import Path

import pytest

from ppd.crawler.public_recrawl_metadata_intake_v2 import (
    PACKET_VERSION,
    MetadataIntakeV2ValidationError,
    validate_public_recrawl_metadata_intake_v2,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "public_recrawl_metadata_intake_v2"


def load_valid_packet() -> dict:
    return json.loads((FIXTURE_DIR / "valid_metadata_packet.json").read_text())


def assert_rejected(packet: dict) -> None:
    with pytest.raises(MetadataIntakeV2ValidationError):
        validate_public_recrawl_metadata_intake_v2(packet)


def test_accepts_metadata_only_public_recrawl_intake_v2_packet() -> None:
    packet = load_valid_packet()

    validated = validate_public_recrawl_metadata_intake_v2(packet)

    assert validated.packet_version == PACKET_VERSION
    assert validated.run_id == "fixture-run-20260529"
    assert len(validated.captured_urls) == 2
    assert validated.captured_urls[0].content_hash.startswith("sha256:")
    assert validated.captured_urls[1].skip_evidence_ids == ("policy:no-raw-download-artifacts",)


@pytest.mark.parametrize(
    "field,value",
    [
        ("decision_citation_ids", []),
        ("redirect_chain", []),
        ("content_type", ""),
        ("content_hash", ""),
    ],
)
def test_rejects_uncited_or_incomplete_captured_url_evidence(field: str, value: object) -> None:
    packet = load_valid_packet()
    packet["captured_urls"][0][field] = value

    assert_rejected(packet)


def test_rejects_captured_url_hash_without_sha256_prefix() -> None:
    packet = load_valid_packet()
    packet["captured_urls"][0]["content_hash"] = "md5:abc"

    assert_rejected(packet)


@pytest.mark.parametrize(
    "url",
    [
        "http://www.portland.gov/ppd/devhub-faqs",
        "https://example.com/ppd/devhub-faqs",
        "https://devhub.portlandoregon.gov/account/permits",
        "https://www.portland.gov/ppd/devhub-faqs?token=secret",
    ],
)
def test_rejects_non_allowlisted_or_authenticated_urls(url: str) -> None:
    packet = load_valid_packet()
    packet["captured_urls"][0]["url"] = url

    assert_rejected(packet)


def test_rejects_non_allowlisted_redirects() -> None:
    packet = load_valid_packet()
    packet["captured_urls"][0]["redirect_chain"] = ["https://example.com/redirected"]

    assert_rejected(packet)


@pytest.mark.parametrize(
    "field,value",
    [
        ("skipped_reason", ""),
        ("skip_evidence_ids", []),
    ],
)
def test_rejects_missing_skip_evidence(field: str, value: object) -> None:
    packet = load_valid_packet()
    packet["captured_urls"][1][field] = value

    assert_rejected(packet)


@pytest.mark.parametrize(
    "field,value",
    [
        ("raw_body", "raw"),
        ("download_path", "/tmp/fee.pdf"),
        ("archive_path", "crawl.warc"),
        ("browser_artifact", "trace.zip"),
        ("screenshot_path", "page.png"),
        ("har", "network.har"),
        ("cookies", {"session": "redacted"}),
    ],
)
def test_rejects_raw_body_download_archive_or_browser_artifacts(field: str, value: object) -> None:
    packet = load_valid_packet()
    packet["captured_urls"][0][field] = value

    assert_rejected(packet)


@pytest.mark.parametrize(
    "field",
    [
        "live_crawl_executed",
        "processor_executed",
        "crawl_execution",
        "processor_execution",
    ],
)
def test_rejects_live_crawl_or_processor_execution_claims(field: str) -> None:
    packet = load_valid_packet()
    packet[field] = True

    assert_rejected(packet)


@pytest.mark.parametrize(
    "field",
    [
        "legal_outcome_guarantee",
        "permitting_outcome_guarantee",
        "approval_guaranteed",
        "permit_guaranteed",
    ],
)
def test_rejects_legal_or_permitting_outcome_guarantees(field: str) -> None:
    packet = load_valid_packet()
    packet[field] = True

    assert_rejected(packet)


@pytest.mark.parametrize(
    "field",
    [
        "active_source_mutation",
        "active_schedule_mutation",
        "active_requirement_mutation",
        "active_process_mutation",
        "active_guardrail_mutation",
        "active_prompt_mutation",
        "active_monitoring_mutation",
        "active_release_state_mutation",
        "active_agent_state_mutation",
        "source_mutations",
        "update_crawl_schedule",
    ],
)
def test_rejects_active_state_mutation_flags(field: str) -> None:
    packet = load_valid_packet()
    packet[field] = True

    assert_rejected(packet)
