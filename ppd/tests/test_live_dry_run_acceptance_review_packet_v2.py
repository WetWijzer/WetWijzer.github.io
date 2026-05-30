from __future__ import annotations

import copy
import json
from pathlib import Path

from ppd.acceptance.live_dry_run_acceptance_review_packet_v2 import (
    REQUIRED_ATTESTATIONS,
    build_live_dry_run_acceptance_review_packet_v2,
    require_valid_live_dry_run_acceptance_review_packet_v2,
    validate_live_dry_run_acceptance_review_packet_v2,
)
from ppd.live_dry_run_post_run_triage_packet_v2 import build_live_dry_run_post_run_triage_packet_v2


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "live_dry_run_acceptance_review_packet_v2" / "source_packets.json"


def _source_packets() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _packet() -> dict:
    sources = _source_packets()
    triage = build_live_dry_run_post_run_triage_packet_v2(sources)
    return build_live_dry_run_acceptance_review_packet_v2(
        triage,
        sources["public_recrawl_dry_run_evidence_envelope_v2"],
        sources["attended_devhub_read_only_evidence_envelope_v2"],
    )


def test_builds_fixture_first_acceptance_review_packet_v2() -> None:
    packet = _packet()

    assert packet["packet_type"] == "live-dry-run-acceptance-review-packet-v2"
    assert packet["version"] == "v2"
    assert packet["mode"] == "fixture_first_live_dry_run_acceptance_review_only"
    assert packet["fixture_first"] is True
    assert set(packet["observation_rows"]) == {"accepted", "deferred", "rejected"}
    assert all(packet["observation_rows"][decision] for decision in ("accepted", "deferred", "rejected"))
    require_valid_live_dry_run_acceptance_review_packet_v2(packet)


def test_observation_rows_are_cited_and_have_owner_and_follow_up_fields() -> None:
    packet = _packet()

    for rows in packet["observation_rows"].values():
        for row in rows:
            assert row["citations"]
            assert row["source_packet_refs"]
            assert row["reviewer_owner"].startswith("TBD_PP_D_")
            assert row["follow_up_task_ref"].startswith("follow-up-")
            assert row["rationale"]

    assert packet["reviewer_owner_fields"]["primary_reviewer_owner"] == "TBD_PP_D_ACCEPTANCE_REVIEW_OWNER"
    assert packet["follow_up_task_references"]


def test_includes_offline_validation_commands_and_required_attestations() -> None:
    packet = _packet()

    assert ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"] in packet["offline_validation_commands"]
    assert packet["attestations"] == {key: True for key in REQUIRED_ATTESTATIONS}
    assert packet["side_effects"] == {
        "live_repeat_performed": False,
        "auth_state_created_or_read": False,
        "browser_artifact_created_or_read": False,
        "official_action_performed": False,
        "release_state_mutated": False,
    }


def test_validator_rejects_uncited_observation_row() -> None:
    packet = _packet()
    packet["observation_rows"]["accepted"][0]["citations"] = []

    result = validate_live_dry_run_acceptance_review_packet_v2(packet)

    assert not result.valid
    assert "observation_rows.accepted[0].citations must be non-empty" in result.errors


def test_validator_rejects_missing_reviewer_owner_fields_and_follow_up_tasks() -> None:
    packet = _packet()
    packet["reviewer_owner_fields"].pop("release_state_owner")
    packet["follow_up_task_references"] = []

    result = validate_live_dry_run_acceptance_review_packet_v2(packet)

    assert not result.valid
    assert "reviewer_owner_fields.release_state_owner is required" in result.errors
    assert "follow_up_task_references must be non-empty" in result.errors


def test_validator_rejects_missing_attestation_and_side_effect_claim() -> None:
    packet = _packet()
    packet["attestations"]["no_auth_state"] = False
    packet["side_effects"]["browser_artifact_created_or_read"] = True

    result = validate_live_dry_run_acceptance_review_packet_v2(packet)

    assert not result.valid
    assert "attestations.no_auth_state must be true" in result.errors
    assert "side_effects.browser_artifact_created_or_read must be false" in result.errors


def test_validator_rejects_private_auth_state_browser_artifacts_live_repeat_and_official_actions() -> None:
    packet = _packet()
    packet["observation_rows"]["accepted"][0]["observation_summary"] = (
        "Opened live DevHub with Playwright, captured screenshot and auth_state.json, "
        "then submitted payment for permit number: 24-123456-000-00-CO."
    )

    result = validate_live_dry_run_acceptance_review_packet_v2(packet)

    assert not result.valid
    assert any("private, credential, session, or authenticated values" in error for error in result.errors)
    assert any("browser artifact" in error for error in result.errors)
    assert any("live repeat" in error for error in result.errors)
    assert any("official action" in error for error in result.errors)


def test_builder_rejects_invalid_source_envelope_attestation() -> None:
    sources = _source_packets()
    triage = build_live_dry_run_post_run_triage_packet_v2(sources)
    public_envelope = copy.deepcopy(sources["public_recrawl_dry_run_evidence_envelope_v2"])
    public_envelope["attestations"]["no_download"] = False

    try:
        build_live_dry_run_acceptance_review_packet_v2(
            triage,
            public_envelope,
            sources["attended_devhub_read_only_evidence_envelope_v2"],
        )
    except ValueError as exc:
        assert "no_download" in str(exc)
    else:
        raise AssertionError("expected invalid public envelope failure")
