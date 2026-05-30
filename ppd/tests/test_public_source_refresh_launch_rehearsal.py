from __future__ import annotations

import json
from pathlib import Path

from ppd.validation.public_source_refresh_launch_rehearsal import (
    assert_valid_public_source_refresh_launch_rehearsal_packet,
    validate_public_source_refresh_launch_rehearsal_packet,
)

_FIXTURE_DIR = Path(__file__).parent / "fixtures" / "public_source_refresh_launch_rehearsal"


def _load(name: str) -> dict:
    return json.loads((_FIXTURE_DIR / name).read_text(encoding="utf-8"))


def test_accepts_metadata_only_cited_rehearsal_packet() -> None:
    packet = _load("valid_packet.json")

    assert validate_public_source_refresh_launch_rehearsal_packet(packet) == []
    assert_valid_public_source_refresh_launch_rehearsal_packet(packet)


def test_rejects_unsafe_or_incomplete_rehearsal_packet() -> None:
    packet = _load("invalid_packet.json")

    errors = validate_public_source_refresh_launch_rehearsal_packet(packet)

    expected_fragments = [
        "missing consumed-packet references",
        "missing preflight gate outcome",
        "missing abort-trigger checks",
        "missing reviewer owner",
        "result placeholder 0 is not metadata-only",
        "rehearsal step 0 has no citations",
        "URL host is not allowlisted",
        "authenticated URL query parameter is not allowed",
        "fetches/downloads/processes live sources",
        "raw artifact reference is not allowed",
        "legal or permitting outcome guarantee is not allowed",
        "active mutation flag is not allowed",
    ]
    for fragment in expected_fragments:
        assert any(fragment in error for error in errors), fragment
