from __future__ import annotations

import json
from pathlib import Path

from ppd.devhub.attended_observation_queue import QueueSource, build_attended_observation_queue


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "devhub"


def _load_fixture(name: str) -> dict[str, object]:
    with (FIXTURE_DIR / name).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def test_attended_observation_queue_is_fixture_first_and_read_only() -> None:
    surface_map = _load_fixture("attended_observation_surface_map_v1.json")
    policy = _load_fixture("guarded_action_policy_v1.json")

    queue = build_attended_observation_queue(
        surface_map,
        policy,
        source=QueueSource(
            surface_map_fixture="attended_observation_surface_map_v1.json",
            action_policy_fixture="guarded_action_policy_v1.json",
        ),
    )

    assert queue["schema_version"] == "devhub.attended_observation_queue.v1"
    assert queue["mode"] == "fixture_first_read_only_observation"
    assert queue["artifact_policy"] == {
        "opens_devhub": False,
        "stores_session_or_auth_state": False,
        "stores_browser_artifacts": False,
        "stores_screenshots_traces_or_har": False,
        "stores_private_page_values": False,
        "changes_prompts": False,
        "performs_official_actions": False,
    }

    candidate_rows = queue["candidate_rows"]
    assert [row["action"]["action_id"] for row in candidate_rows] == [
        "review_account_home_status",
        "review_permit_request_list",
        "review_fee_notice",
    ]
    assert [row["order"] for row in candidate_rows] == [1, 2, 3]
    assert all(row["candidate_kind"] == "read_only_observation" for row in candidate_rows)
    assert all(row["action"]["classification"] == "safe_read_only" for row in candidate_rows)
    assert all(row["action"]["allowed_in_observation_queue"] is True for row in candidate_rows)
    assert all(row["attendance_preflight"]["manual_login_required"] is True for row in candidate_rows)
    assert all(row["attendance_preflight"]["no_session_or_auth_state_storage"] is True for row in candidate_rows)
    assert all(
        row["attendance_preflight"]["no_screenshots_traces_har_or_raw_private_values"] is True
        for row in candidate_rows
    )
    assert all(row["reviewer_approval_placeholder"]["status"] == "pending_reviewer_approval" for row in candidate_rows)


def test_attended_observation_queue_blocks_consequential_and_draft_actions() -> None:
    surface_map = _load_fixture("attended_observation_surface_map_v1.json")
    policy = _load_fixture("guarded_action_policy_v1.json")

    queue = build_attended_observation_queue(surface_map, policy)

    reminders = queue["blocked_consequential_action_reminders"]
    blocked_by_action = {item["action_id"]: item for item in reminders}

    assert set(blocked_by_action) == {
        "start_new_permit_application",
        "upload_correction_to_record",
        "submit_payment",
    }
    assert blocked_by_action["start_new_permit_application"]["classification"] == "reversible_draft"
    assert blocked_by_action["upload_correction_to_record"]["classification"] == "consequential_official"
    assert blocked_by_action["submit_payment"]["classification"] == "consequential_official"
    assert all(item["not_added_to_candidate_rows"] is True for item in reminders)
    assert all(item["requires_attendance"] is True for item in reminders)
    assert all(item["requires_exact_confirmation"] is True for item in reminders)
    assert "official" in blocked_by_action["submit_payment"]["blocked_reason"]


def test_attended_observation_queue_carries_redaction_references() -> None:
    surface_map = _load_fixture("attended_observation_surface_map_v1.json")
    policy = _load_fixture("guarded_action_policy_v1.json")

    queue = build_attended_observation_queue(surface_map, policy)

    rows_by_surface = {row["surface"]["surface_id"]: row for row in queue["candidate_rows"]}
    assert rows_by_surface["devhub-home"]["redaction_checklist_refs"] == [
        "devhub-account-identifiers",
        "devhub-private-notices",
    ]
    assert rows_by_surface["my-permits-and-requests"]["redaction_checklist_refs"] == [
        "devhub-case-identifiers",
        "devhub-applicant-contact-values",
        "devhub-private-attachment-names",
    ]
    assert rows_by_surface["fee-notice-review"]["redaction_checklist_refs"] == [
        "devhub-fee-amounts",
        "devhub-payment-details",
        "devhub-case-identifiers",
    ]
    assert queue["reviewer_approval_placeholder"] == {
        "required_before_live_use": True,
        "status": "pending_reviewer_approval",
        "reviewer": None,
        "approved_at": None,
        "notes": None,
    }
