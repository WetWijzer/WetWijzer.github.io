from __future__ import annotations

import json
from pathlib import Path

from ppd.devhub.draft_preview_handoff_v4 import (
    assert_valid_reversible_draft_preview_handoff_packet_v4,
    validate_reversible_draft_preview_handoff_packet_v4,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "draft_preview_handoff_v4"


def _load_fixture(name: str):
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def test_valid_reversible_draft_preview_handoff_packet_v4_passes() -> None:
    packet = _load_fixture("valid_packet.json")

    result = validate_reversible_draft_preview_handoff_packet_v4(packet)

    assert result.ok, result.errors
    assert result.errors == ()
    assert_valid_reversible_draft_preview_handoff_packet_v4(packet)


def test_reversible_draft_preview_handoff_packet_v4_rejects_required_risks() -> None:
    invalid_packets = _load_fixture("invalid_packets.json")

    expected_fragments = {
        "uncited_proposal": "citation_ids must cite source evidence",
        "ungrounded_value": "not grounded in fixture_facts",
        "missing_review_checkpoint": "missing required kinds",
        "private_local_path": "private local paths",
        "raw_pdf": "raw PDFs",
        "upload_staging": "upload staging",
        "consequential_language": "certification, submission, payment, scheduling, cancellation",
        "outcome_guarantee": "outcome guarantees",
        "active_mutation_flags": "active mutation flags",
    }

    assert set(invalid_packets) == set(expected_fragments)
    for name, packet in invalid_packets.items():
        result = validate_reversible_draft_preview_handoff_packet_v4(packet)
        assert not result.ok, name
        joined_errors = "\n".join(result.errors)
        assert expected_fragments[name] in joined_errors


def test_reversible_draft_preview_handoff_packet_v4_rejects_unknown_citations() -> None:
    packet = _load_fixture("valid_packet.json")
    packet["draft_field_proposals"][0]["citation_ids"] = ["missing-citation"]

    result = validate_reversible_draft_preview_handoff_packet_v4(packet)

    assert not result.ok
    assert "unknown citations" in "\n".join(result.errors)
