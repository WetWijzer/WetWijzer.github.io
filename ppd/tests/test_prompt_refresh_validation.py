from __future__ import annotations

import json
from pathlib import Path

from ppd.daemon.prompt_refresh_validation import validate_prompt_refresh_candidate_packet


_FIXTURE_DIR = Path(__file__).parent / "fixtures" / "prompt_refresh_candidate_packets"


def _load_fixture(name: str) -> dict:
    return json.loads((_FIXTURE_DIR / name).read_text(encoding="utf-8"))


def test_prompt_refresh_validator_accepts_offline_cited_packet() -> None:
    report = validate_prompt_refresh_candidate_packet(_load_fixture("valid_packet.json"))

    assert report.ok, report.errors


def test_prompt_refresh_validator_rejects_unsafe_packet() -> None:
    report = validate_prompt_refresh_candidate_packet(_load_fixture("unsafe_packet.json"))

    assert not report.ok
    joined = "\n".join(report.errors)
    assert "missing citations" in joined
    assert "missing supported scenario references" in joined
    assert "missing blocked scenario references" in joined
    assert "missing rollback notes" in joined
    assert "missing reviewer owners" in joined
    assert "missing offline validation commands" in joined
    assert "private case fact" in joined
    assert "raw authenticated value" in joined
    assert "local private path" in joined
    assert "execution claim" in joined
    assert "outcome guarantee" in joined
    assert "consequential control" in joined
    assert "active mutation flag" in joined
