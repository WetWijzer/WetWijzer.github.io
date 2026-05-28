from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from ppd.public_change_monitor_notification import (
    PROHIBITED_PUBLIC_BODY_KEYS,
    build_public_change_monitor_notification,
    validate_public_change_monitor_notification_packet,
)

FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "public_change_monitor_notification"
    / "changed_public_guidance_packet.json"
)


def load_fixture() -> dict[str, object]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def test_notification_packet_summarizes_changed_hashes_and_requirement_deltas() -> None:
    packet = build_public_change_monitor_notification(load_fixture())

    assert packet["packet_kind"] == "public_change_monitor_notification"
    assert packet["source_change_basis"] == "fixture_only_public_metadata"
    assert packet["raw_public_page_bodies_included"] is False
    assert len(packet["source_hash_changes"]) == 2

    summary = packet["requirement_change_summary"]
    assert summary["added_requirement_ids"] == ["req-plan-review-upload-label-current"]
    assert summary["removed_requirement_ids"] == ["req-prior-filename-exception"]
    assert summary["changed_requirement_ids"] == ["req-devhub-correction-upload-action-gate"]

    for source_change in packet["source_hash_changes"]:
        assert source_change["previous_source_hash"].startswith("sha256:")
        assert source_change["current_source_hash"].startswith("sha256:")
        assert source_change["previous_source_hash"] != source_change["current_source_hash"]
        assert source_change["canonical_url"].startswith("https://www.portland.gov/ppd/")
        assert source_change["source_freshness_status"] == "fresh"


def test_notification_packet_includes_affected_versions_blocks_and_review_prompts() -> None:
    packet = build_public_change_monitor_notification(load_fixture())

    assert packet["affected_versions"]["process_versions"] == [
        "process-single-pdf-plan-review:v2026-05-27",
        "process-document-preparation:v2026-05-27",
        "process-corrections-upload:v2026-05-27",
    ]
    assert "guardrail-devhub-consequential-actions:v2026-05-27" in packet["affected_versions"][
        "guardrail_bundle_versions"
    ]
    assert all(reason.startswith("blocked_") for reason in packet["blocked_readiness_reasons"])
    assert len(packet["next_human_review_prompts"]) == 4
    assert any("DevHub correction-upload action gate" in prompt for prompt in packet["next_human_review_prompts"])


def test_notification_packet_rejects_raw_public_page_body_fields() -> None:
    fixture = load_fixture()
    fixture["source_hash_changes"][0]["raw_body"] = "synthetic public page body that must not be committed"

    with pytest.raises(ValueError, match="raw public page body field is not allowed"):
        build_public_change_monitor_notification(fixture)

    clean_packet = build_public_change_monitor_notification(load_fixture())
    validate_public_change_monitor_notification_packet(clean_packet)
    packet_text = json.dumps(clean_packet, sort_keys=True)
    for prohibited_key in PROHIBITED_PUBLIC_BODY_KEYS:
        assert f'"{prohibited_key}"' not in packet_text


def test_notification_packet_rejects_missing_affected_ids() -> None:
    fixture = load_fixture()
    fixture["requirement_changes"][0]["affected_process_ids"] = []

    with pytest.raises(ValueError, match="affected_process_ids must be a non-empty list"):
        build_public_change_monitor_notification(fixture)

    fixture = load_fixture()
    fixture["affected_versions"]["guardrail_bundle_versions"] = ["guardrail-upload-staging:v2026-05-27"]

    with pytest.raises(ValueError, match="affected_versions missing guardrail bundle ids"):
        build_public_change_monitor_notification(fixture)


def test_notification_packet_rejects_unsupported_change_categories() -> None:
    fixture = load_fixture()
    fixture["requirement_changes"][0]["change_category"] = "agent_auto_apply"

    with pytest.raises(ValueError, match="unsupported requirement change category"):
        build_public_change_monitor_notification(fixture)


def test_notification_packet_rejects_stale_source_freshness() -> None:
    fixture = load_fixture()
    fixture["source_hash_changes"][0]["source_freshness_status"] = "stale"

    with pytest.raises(ValueError, match="stale source freshness rejected"):
        build_public_change_monitor_notification(fixture)


def test_notification_packet_rejects_downloaded_document_paths() -> None:
    fixture = load_fixture()
    fixture["source_hash_changes"][0]["downloaded_document_path"] = "/tmp/Downloads/permit-guide.pdf"

    with pytest.raises(ValueError, match="downloaded document path"):
        build_public_change_monitor_notification(fixture)

    fixture = load_fixture()
    fixture["recommendations"][0]["summary"] = "Review /Users/example/Downloads/private-plan.pdf"

    with pytest.raises(ValueError, match="downloaded document path"):
        build_public_change_monitor_notification(fixture)


def test_notification_packet_rejects_private_or_authenticated_urls() -> None:
    fixture = load_fixture()
    fixture["source_hash_changes"][0]["canonical_url"] = "https://devhub.portlandoregon.gov/permits/12345"

    with pytest.raises(ValueError, match="private or authenticated URL"):
        build_public_change_monitor_notification(fixture)

    fixture = load_fixture()
    fixture["recommendations"][0]["summary"] = "Open https://www.portland.gov/login?token=secret"

    with pytest.raises(ValueError, match="private or authenticated URL"):
        build_public_change_monitor_notification(fixture)


def test_notification_packet_rejects_recommendations_that_bypass_human_review() -> None:
    fixture = load_fixture()
    fixture["recommendations"][0]["human_review_required"] = False

    with pytest.raises(ValueError, match="recommendations must require human review"):
        build_public_change_monitor_notification(fixture)

    fixture = load_fixture()
    fixture["recommendations"][0]["action_status"] = "agent_may_apply"

    with pytest.raises(ValueError, match="recommendations must be blocked_until_human_review"):
        build_public_change_monitor_notification(fixture)


def test_built_packet_is_detached_from_fixture_mutations() -> None:
    fixture = load_fixture()
    packet = build_public_change_monitor_notification(fixture)
    mutated = copy.deepcopy(packet)
    mutated["recommendations"][0]["human_review_required"] = False

    with pytest.raises(ValueError, match="recommendations must require human review"):
        validate_public_change_monitor_notification_packet(mutated)
