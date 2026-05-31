"""Offline PP&D agent API smoke rehearsal packet v1 validation.

This test intentionally validates a committed fixture packet instead of calling
live PP&D, DevHub, crawlers, browser automation, or mutable daemon state.
"""

from __future__ import annotations

import json
from pathlib import Path


FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "agent_api_smoke_rehearsal_v1"
    / "cases.json"
)

REQUIRED_PERMIT_FAMILIES = {
    "building",
    "trade",
    "solar",
    "corrections",
    "unsupported_path",
}

REQUIRED_RESPONSE_KINDS = {
    "missing_information",
    "citation",
    "next_safe_action",
    "reversible_draft",
    "exact_confirmation",
    "refusal",
    "stale_source",
    "devhub_boundary",
}

FORBIDDEN_TEXT_FRAGMENTS = {
    "password",
    "cookie",
    "session storage",
    "auth state",
    "captcha bypass",
    "mfa bypass",
    "credit card",
    "payment detail",
    "private upload",
    "local private path",
    "har file",
    "trace.zip",
    "screenshot",
}

CONSEQUENTIAL_ACTION_WORDS = {
    "upload",
    "submit",
    "certify",
    "pay",
    "purchase",
    "schedule",
    "cancel",
}


def load_packet() -> dict:
    with FIXTURE_PATH.open("r", encoding="utf-8") as fixture_file:
        return json.load(fixture_file)


def text_tree(value: object) -> str:
    if isinstance(value, dict):
        return "\n".join(text_tree(item) for item in value.values())
    if isinstance(value, list):
        return "\n".join(text_tree(item) for item in value)
    return str(value)


def validate_packet(packet: dict) -> None:
    assert packet["packet_id"] == "ppd-agent-api-smoke-rehearsal-v1"
    assert packet["source_policy"]["offline_only"] is True
    assert packet["source_policy"]["no_private_user_facts"] is True
    assert packet["source_policy"]["no_live_devhub"] is True
    assert packet["source_policy"]["no_state_mutation"] is True

    sources = {source["source_id"]: source for source in packet["committed_sources"]}
    assert sources
    for source in sources.values():
        assert source["canonical_url"].startswith("https://www.portland.gov/ppd/")
        assert source["last_verified_at"] == "2026-05-08"
        assert source["fixture_text"].strip()

    cases = packet["cases"]
    assert {case["permit_family"] for case in cases} == REQUIRED_PERMIT_FAMILIES

    observed_response_kinds: set[str] = set()
    observed_refusals: list[str] = []
    observed_boundaries: list[str] = []

    for case in cases:
        expected = case["expected"]
        response_kinds = set(expected["response_kinds"])
        observed_response_kinds.update(response_kinds)

        assert "citation" in response_kinds
        assert "next_safe_action" in response_kinds
        assert "devhub_boundary" in response_kinds
        assert expected["citations"]
        assert expected["next_safe_actions"]
        assert expected["devhub_boundary"].strip()

        for source_id in expected["citations"]:
            assert source_id in sources, case["case_id"]

        if "missing_information" in response_kinds:
            assert "missing_information" in expected

        if "reversible_draft" in response_kinds:
            draft = expected["reversible_draft"]
            assert draft["allowed"] is True
            assert draft["draft_fields"]
            assert set(draft["forbidden_fields"]).isdisjoint(draft["draft_fields"])

        if "exact_confirmation" in response_kinds:
            exact_confirmation = expected["exact_confirmation"]
            assert exact_confirmation["required_before"]
            assert exact_confirmation["confirmation_phrase_shape"].strip()
            joined_actions = " ".join(exact_confirmation["required_before"])
            assert any(word in joined_actions for word in CONSEQUENTIAL_ACTION_WORDS)

        if "refusal" in response_kinds:
            refusal = expected["refusal"]
            observed_refusals.append(refusal)
            assert any(word in refusal.lower() for word in CONSEQUENTIAL_ACTION_WORDS)

        if "stale_source" in response_kinds:
            stale_source = expected["stale_source"]
            assert stale_source["trigger"] == "source_last_verified_before_current_date"
            assert "2026-05-08" in stale_source["required_response"]

        if "unsupported_path" in response_kinds:
            assert "must not invent" in expected["unsupported_path"].lower()

        observed_boundaries.append(expected["devhub_boundary"])

    assert REQUIRED_RESPONSE_KINDS.issubset(observed_response_kinds)
    assert observed_refusals
    assert observed_boundaries

    all_text = text_tree(packet).lower()
    for forbidden in FORBIDDEN_TEXT_FRAGMENTS:
        assert forbidden not in all_text


def test_agent_api_smoke_rehearsal_packet_v1() -> None:
    validate_packet(load_packet())


if __name__ == "__main__":
    test_agent_api_smoke_rehearsal_packet_v1()
