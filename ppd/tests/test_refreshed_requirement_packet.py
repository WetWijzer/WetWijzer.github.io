import json
import re
from pathlib import Path


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "refreshed_requirement_packet" / "changed_synthetic_records_packet.json"
EXPECTED_CATEGORIES = {
    "fee",
    "deadline",
    "upload_rule",
    "required_document",
    "devhub_action_gate",
}
EXPECTED_TYPES = {
    "fee_trigger",
    "deadline",
    "precondition",
    "document_requirement",
    "action_gate",
}
EXPECTED_REVIEW_STATUSES = {"fixture_reviewed", "needs_human_review"}
HEX_64 = re.compile(r"^[0-9a-f]{64}$")


def _load_packet():
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _source_text(record, source_field):
    if source_field == "normalized_text":
        return record["normalized_text"]
    if source_field == "pdf_pages[0].text":
        return record["pdf_pages"][0]["text"]
    raise AssertionError(f"unexpected source field: {source_field}")


def test_packet_contains_changed_html_and_pdf_records_with_hash_deltas():
    packet = _load_packet()
    assert packet["source_change_basis"] == "fixture_only_synthetic_changed_records"
    assert {record["document_type"] for record in packet["records"]} == {"public_html", "public_pdf"}

    for record in packet["records"]:
        assert record["canonical_url"].startswith("https://www.portland.gov/ppd/")
        assert HEX_64.match(record["previous_source_hash"])
        assert HEX_64.match(record["refreshed_source_hash"])
        assert record["previous_source_hash"] != record["refreshed_source_hash"]
        delta = record["source_hash_delta"]
        assert delta["changed"] is True
        assert delta["algorithm"] == "sha256"
        assert "requirements" in delta["changed_fields"]


def test_requirements_cover_selected_categories_types_confidence_and_review_status():
    packet = _load_packet()
    requirements = [requirement for record in packet["records"] for requirement in record["requirements"]]

    assert {requirement["requirement_category"] for requirement in requirements} == EXPECTED_CATEGORIES
    assert {requirement["requirement_type"] for requirement in requirements} == EXPECTED_TYPES

    for requirement in requirements:
        assert isinstance(requirement["confidence"], (int, float))
        assert 0.0 <= requirement["confidence"] <= 1.0
        assert requirement["human_review_status"] in EXPECTED_REVIEW_STATUSES
        assert requirement["citation_spans"]


def test_citation_spans_match_changed_record_text_exactly():
    packet = _load_packet()

    for record in packet["records"]:
        for requirement in record["requirements"]:
            for span in requirement["citation_spans"]:
                source_text = _source_text(record, span["source_field"])
                start = span["start"]
                end = span["end"]
                assert isinstance(start, int)
                assert isinstance(end, int)
                assert 0 <= start < end <= len(source_text)
                assert source_text[start:end] == span["exact_text"]
                if record["document_type"] == "public_pdf":
                    assert span["page_number"] == 1
