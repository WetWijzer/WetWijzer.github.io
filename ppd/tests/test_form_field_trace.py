from __future__ import annotations

from pathlib import Path

from ppd.form_field_trace import build_trace_index
from ppd.form_field_trace import load_trace_packet
from ppd.form_field_trace import missing_prompt_ids
from ppd.form_field_trace import preview_draft_values
from ppd.form_field_trace import validate_trace_packet


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "form_field_trace" / "devhub_to_pdf_owner_occupied_simple.json"


def test_form_field_trace_fixture_is_valid() -> None:
    packet = load_trace_packet(FIXTURE_PATH)

    assert validate_trace_packet(packet) == []


def test_form_field_trace_links_devhub_pdf_requirements_and_evidence() -> None:
    packet = load_trace_packet(FIXTURE_PATH)
    traces = build_trace_index(packet)

    applicant = traces["trace-applicant-name"]
    assert applicant["requirement_id"] == "req-applicant-legal-name"
    assert applicant["source_evidence_id"] == "src-ppd-forms-index-residential-application"
    assert applicant["devhub_field_id"] == "devhub-applicant-name"
    assert applicant["pdf_field_id"] == "pdf-applicant-name"
    assert applicant["user_fact_id"] == "fact-applicant-name"
    assert applicant["value_mode"] == "preview_only"


def test_preview_values_exclude_missing_prompt_fields() -> None:
    packet = load_trace_packet(FIXTURE_PATH)

    assert preview_draft_values(packet) == {
        "pdf-applicant-name": "Morgan Lee",
        "pdf-site-address": "1234 SE Example St, Portland, OR 97202",
        "pdf-work-description": "Interior kitchen remodel with no exterior work proposed.",
    }
    assert missing_prompt_ids(packet) == ["prompt-owner-occupied"]


def test_fixture_does_not_contain_private_devhub_capture() -> None:
    packet = load_trace_packet(FIXTURE_PATH)

    assert packet["safety"]["fixture_only"] is True
    assert packet["safety"]["preview_only"] is True
    assert packet["safety"]["contains_private_devhub_data"] is False
    assert "submission" in packet["safety"]["blocked_actions"]
