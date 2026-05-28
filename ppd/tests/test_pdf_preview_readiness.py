from pathlib import Path

import pytest

from ppd.pdf.preview_readiness import (
    PreviewReadinessError,
    build_preview_readiness_summary,
    load_preview_readiness_packet,
    validate_preview_readiness_packet,
)


FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "pdf_preview_readiness"
    / "residential_mechanical_preview_packet.json"
)


def test_preview_readiness_fixture_combines_required_packet_sections() -> None:
    packet = load_preview_readiness_packet(FIXTURE_PATH)
    summary = build_preview_readiness_summary(packet)

    assert summary.workflow_id == "residential_mechanical_trade_permit_local_pdf_preview"
    assert summary.preview_only is True
    assert summary.required_field_count == 5
    assert summary.satisfied_field_count == 4
    assert summary.missing_prompt_count == 1
    assert summary.blocked_certification_field_count == 2
    assert summary.citation_count == 4
    assert summary.output_kind == "local_pdf_preview_packet"
    assert summary.ready_for_preview is False


def test_preview_readiness_fixture_keeps_certification_fields_blocked() -> None:
    packet = load_preview_readiness_packet(FIXTURE_PATH)

    blocked_names = {field["pdf_field_name"] for field in packet["blocked_certification_fields"]}
    assert blocked_names == {"applicant_signature", "certification_acknowledgement_checkbox"}
    assert all(field["may_autofill"] is False for field in packet["blocked_certification_fields"])
    assert packet["preview_output_metadata"]["official_submission_ready"] is False
    assert {"upload", "submit", "certify", "pay", "schedule", "cancel"}.issubset(
        set(packet["preview_output_metadata"]["disallowed_actions"])
    )


def test_preview_readiness_rejects_non_preview_packets() -> None:
    packet = load_preview_readiness_packet(FIXTURE_PATH)
    packet["preview_only"] = False

    with pytest.raises(PreviewReadinessError, match="preview_only=true"):
        validate_preview_readiness_packet(packet)


def test_preview_readiness_rejects_unknown_requirement_traces() -> None:
    packet = load_preview_readiness_packet(FIXTURE_PATH)
    packet["form_fields"][0]["requirement_trace_ids"] = ["missing_evidence"]

    with pytest.raises(PreviewReadinessError, match="unknown citations"):
        validate_preview_readiness_packet(packet)
