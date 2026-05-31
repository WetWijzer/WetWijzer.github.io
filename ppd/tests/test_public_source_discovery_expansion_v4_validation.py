from __future__ import annotations

import json
from pathlib import Path

from ppd.validation.public_source_discovery_expansion_v4 import (
    validate_public_source_discovery_expansion_packet_v4,
)

FIXTURES = Path(__file__).parent / "fixtures" / "public_source_discovery_expansion_v4"


def _fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def test_valid_packet_has_no_errors() -> None:
    assert validate_public_source_discovery_expansion_packet_v4(_fixture("valid_packet.json")) == []


def test_invalid_packet_rejects_required_guardrail_failures() -> None:
    errors = validate_public_source_discovery_expansion_packet_v4(_fixture("invalid_packet.json"))
    joined = "\n".join(errors)

    assert "canonical_url is required" in joined
    assert "source_page evidence is required" in joined
    assert "link_text evidence is required" in joined
    assert "allowlist_decision is required" in joined
    assert "duplicate_normalization must include at least one row" in joined
    assert "skipped_urls[0].reason is required" in joined
    assert "validation_commands must include at least one command" in joined
    assert "outside the public allowlist" in joined
    assert "raw or downloaded artifacts are not allowed" in joined
    assert "private session/browser artifacts are not allowed" in joined
    assert "live crawl or DevHub automation claims are not allowed" in joined
    assert "legal or permitting guarantees are not allowed" in joined
    assert "active mutation flags are not allowed" in joined
