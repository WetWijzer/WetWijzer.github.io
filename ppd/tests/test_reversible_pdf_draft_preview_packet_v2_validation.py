from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from ppd.reversible_pdf_draft_preview_packet_v2_validation import (
    PacketValidationError,
    packet_validation_errors,
    validate_reversible_pdf_draft_preview_packet_v2,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "reversible_pdf_draft_preview_packet_v2"


def load_valid_packet() -> dict:
    return json.loads((FIXTURE_DIR / "valid_packet.json").read_text(encoding="utf-8"))


def test_valid_packet_fixture_passes() -> None:
    validate_reversible_pdf_draft_preview_packet_v2(load_valid_packet())


@pytest.mark.parametrize(
    "missing_key",
    [
        "synthetic_facts",
        "pdf_field_plan_rows",
        "unsupported_field_notes",
        "required_fact_gaps",
        "citation_references",
        "user_visible_review_checkpoints",
        "no_private_file_assurances",
        "validation_commands",
    ],
)
def test_rejects_missing_required_packet_evidence(missing_key: str) -> None:
    packet = load_valid_packet()
    packet.pop(missing_key)

    errors = packet_validation_errors(packet)

    assert f"{missing_key} must be a non-empty list" in errors


@pytest.mark.parametrize(
    "field,value,expected",
    [
        ("notes", "/home/example/private/devhub-state.json", "packet must not contain private file paths"),
        ("notes", "C:/Users/example/auth/state.json", "packet must not contain private file paths"),
        ("notes", "draft-preview.pdf", "packet must not contain raw or generated PDF artifacts"),
        ("notes", "The packet was uploaded to DevHub.", "packet must not contain upload, submission, certification, live DevHub, legal, permitting guarantee, or mutation claims"),
        ("notes", "Submission complete.", "packet must not contain upload, submission, certification, live DevHub, legal, permitting guarantee, or mutation claims"),
        ("notes", "Certification complete.", "packet must not contain upload, submission, certification, live DevHub, legal, permitting guarantee, or mutation claims"),
        ("notes", "Live DevHub session verified.", "packet must not contain upload, submission, certification, live DevHub, legal, permitting guarantee, or mutation claims"),
        ("notes", "Permit approved and legally sufficient.", "packet must not contain upload, submission, certification, live DevHub, legal, permitting guarantee, or mutation claims"),
        ("active_mutation_flags", ["write_enabled"], "active_mutation_flags must be absent or empty"),
        ("raw_or_generated_pdf_artifacts", ["packet.pdf"], "raw_or_generated_pdf_artifacts must be absent or empty"),
    ],
)
def test_rejects_unsafe_packet_content(field: str, value: object, expected: str) -> None:
    packet = load_valid_packet()
    packet[field] = value

    errors = packet_validation_errors(packet)

    assert expected in errors


def test_raises_packet_validation_error_with_all_errors() -> None:
    packet = copy.deepcopy(load_valid_packet())
    packet["synthetic_facts"] = []
    packet["notes"] = "draft-preview.pdf"

    with pytest.raises(PacketValidationError) as exc_info:
        validate_reversible_pdf_draft_preview_packet_v2(packet)

    assert "synthetic_facts must be a non-empty list" in exc_info.value.errors
    assert "packet must not contain raw or generated PDF artifacts" in exc_info.value.errors
