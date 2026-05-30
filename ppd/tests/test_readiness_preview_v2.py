from __future__ import annotations

import json
from pathlib import Path

from ppd.readiness_preview_v2 import validate_reversible_draft_preview_readiness_packet_v2

_FIXTURES = Path(__file__).parent / "fixtures" / "readiness_preview_v2"


def _load_fixture(name: str) -> dict:
    return json.loads((_FIXTURES / name).read_text(encoding="utf-8"))


def test_valid_reversible_draft_preview_readiness_packet_v2_passes() -> None:
    packet = _load_fixture("valid_packet.json")

    assert validate_reversible_draft_preview_readiness_packet_v2(packet) == []


def test_invalid_reversible_draft_preview_readiness_packet_v2_rejects_guarded_content() -> None:
    packet = _load_fixture("invalid_packet.json")

    errors = validate_reversible_draft_preview_readiness_packet_v2(packet)

    assert errors
    joined = "\n".join(errors)
    assert "readiness_decisions[0] must include citations" in joined
    assert "required_fact_checks must be a non-empty list" in joined
    assert "missing_document_checks must be a non-empty list" in joined
    assert "reversible_action_predicates[0] must affirm reversibility" in joined
    assert "exact_confirmation_checkpoints[0] must affirm exact confirmation" in joined
    assert "private case facts are not allowed" in joined
    assert "local private document paths are not allowed" in joined
    assert "raw authenticated values are not allowed" in joined
    assert "live DevHub/browser/LLM/crawler/processor execution claims are not allowed" in joined
    assert "legal or permitting outcome guarantees are not allowed" in joined
    assert "final submission/payment/upload/scheduling/cancellation language is not allowed" in joined
    assert "active_pdf_mutation must not be active" in joined
