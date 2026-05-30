from __future__ import annotations

from ppd.validation.inactive_fixture_promotion_application_preview_v1 import (
    validate_inactive_fixture_promotion_application_preview_v1,
)


def valid_preview() -> dict[str, object]:
    return {
        "schema_version": "inactive_fixture_promotion_application_preview_v1",
        "active": False,
        "release_state": "inactive_preview",
        "before_fixture_preview": {"rows": 1, "digest": "before-fixture-preview"},
        "after_fixture_preview": {"rows": 1, "digest": "after-fixture-preview"},
        "source_citations": ["Portland source citation placeholder retained"],
        "observation_evidence": ["Observed fixture delta in deterministic preview"],
        "citation_preservation_checks": {"all_existing_citations_preserved": True},
        "blocked_row_explanations": ["No row is promoted without an explanation"],
        "validation_replay_inventory": ["validator:self-test fixture replay"],
        "reviewer_signoff_placeholders": ["reviewer:name/date placeholder"],
        "rollback_notes": "Discard preview fixture and keep current inactive corpus unchanged.",
        "active_artifact_mutation": False,
        "release_state_mutation": False,
        "fixture_mutation": False,
        "agent_state_mutation": False,
    }


def assert_rejected(payload: dict[str, object], expected: str) -> None:
    result = validate_inactive_fixture_promotion_application_preview_v1(payload)
    assert not result.ok
    assert any(expected in error for error in result.errors)


def test_valid_preview_is_accepted() -> None:
    result = validate_inactive_fixture_promotion_application_preview_v1(valid_preview())
    assert result.ok
    assert result.errors == ()


def test_rejects_missing_required_preview_evidence_and_review_fields() -> None:
    payload = valid_preview()
    for key in (
        "before_fixture_preview",
        "after_fixture_preview",
        "source_citations",
        "observation_evidence",
        "citation_preservation_checks",
        "blocked_row_explanations",
        "validation_replay_inventory",
        "reviewer_signoff_placeholders",
        "rollback_notes",
    ):
        payload.pop(key)

    result = validate_inactive_fixture_promotion_application_preview_v1(payload)
    assert not result.ok
    joined = "\n".join(result.errors)
    assert "before_fixture_preview" in joined
    assert "after_fixture_preview" in joined
    assert "source_citations" in joined
    assert "observation_evidence" in joined
    assert "citation_preservation_checks" in joined
    assert "blocked_row_explanations" in joined
    assert "validation_replay_inventory" in joined
    assert "reviewer_signoff_placeholders" in joined
    assert "rollback_notes" in joined


def test_rejects_private_raw_live_legal_and_consequential_language() -> None:
    blocked_phrases = (
        "authenticated session",
        "browser trace",
        "raw crawl",
        "downloaded pdf",
        "live execution",
        "promotion applied",
        "guarantee approval",
        "must submit",
    )
    for phrase in blocked_phrases:
        payload = valid_preview()
        payload["observation_evidence"] = [f"contains {phrase}"]
        assert_rejected(payload, phrase)


def test_rejects_active_release_fixture_and_agent_mutation_flags() -> None:
    for flag in (
        "active_artifact_mutation",
        "release_state_mutation",
        "fixture_mutation",
        "agent_state_mutation",
        "mutates_active_artifacts",
        "mutates_release_state",
        "mutates_fixtures",
        "mutates_agent_state",
    ):
        payload = valid_preview()
        payload[flag] = True
        assert_rejected(payload, flag)

    active_payload = valid_preview()
    active_payload["active"] = True
    assert_rejected(active_payload, "active must not be true")

    released_payload = valid_preview()
    released_payload["release_state"] = "released"
    assert_rejected(released_payload, "release_state")
