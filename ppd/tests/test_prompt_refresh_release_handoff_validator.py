from __future__ import annotations

import json
from pathlib import Path

from ppd.prompt_refresh_release_handoff_validator import validate_handoff_packet


FIXTURES = Path(__file__).parent / "fixtures" / "prompt_refresh_release_handoff"


def _load_fixture(name: str) -> dict[str, object]:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def test_accepts_safe_fixture_labelled_handoff_packet() -> None:
    packet = _load_fixture("valid_packet.json")

    assert validate_handoff_packet(packet) == []


def test_rejects_required_release_handoff_safety_failures() -> None:
    packet = _load_fixture("invalid_packet.json")

    errors = validate_handoff_packet(packet)
    joined = "\n".join(errors)

    assert "prompt_versions[0] must include at least one citation" in joined
    assert "compatibility_notes must be a non-empty list" in joined
    assert "migration_checklist must be a non-empty list" in joined
    assert "rollback_owner must be a non-empty string" in joined
    assert "offline_validation_commands must be a non-empty list" in joined
    assert "private or authenticated fact" in joined
    assert "raw prompt injection text without fixture_label" in joined
    assert "claims live LLM, DevHub, crawler, or processor execution" in joined
    assert "legal or permitting outcome guarantee" in joined
    assert "consequential_controls.submit_application must not be enabled" in joined
    assert "active_prompt_mutation must not be active" in joined
    assert "mutate_guardrails must not be active" in joined
