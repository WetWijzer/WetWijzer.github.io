import json
from pathlib import Path


FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "devhub_attended_read_only"
    / "status_review_observation_packet.json"
)


REQUIRED_LINKS = {
    "session_handoff_checklist": "session-handoff-checklist",
    "accessible_structure_surface_map": "accessible-structure-surface-map",
    "allowed_read_only_scope": "allowed-read-only-scope",
    "redaction_policy": "redaction-policy",
    "post_observation_journal_expectations": "post-observation-journal-expectations",
}


PROHIBITED_ACTION_TERMS = {
    "Account creation",
    "Sign-in automation",
    "MFA or CAPTCHA automation",
    "Credential or cookie capture",
    "Opening or downloading private documents",
    "Uploading files",
    "Paying fees or entering payment details",
    "Scheduling, rescheduling, or cancelling inspections",
    "Certifying, acknowledging, submitting, withdrawing, cancelling, or otherwise changing an official record",
}


SENSITIVE_REDACTION_TERMS = {
    "Names",
    "Email addresses",
    "Phone numbers",
    "Site addresses",
    "Permit numbers",
    "Application numbers",
    "Payment information",
    "Browser session identifiers",
    "Local private file paths",
}


def load_packet():
    with FIXTURE_PATH.open(encoding="utf-8") as fixture_file:
        return json.load(fixture_file)


def test_status_review_observation_packet_links_required_sections():
    packet = load_packet()

    assert packet["packet_type"] == "devhub_attended_read_only_observation_packet"
    assert packet["fixture_first"] is True
    assert packet["synthetic_only"] is True
    assert packet["workflow"]["workflow_id"] == "synthetic-status-review"

    linked_surfaces = packet["linked_surfaces"]
    for link_name, section_id in REQUIRED_LINKS.items():
        assert linked_surfaces[link_name] == f"#{section_id}"
        assert packet[link_name]["section_id"] == section_id


def test_packet_limits_scope_to_attended_read_only_observation():
    packet = load_packet()
    scope = packet["allowed_read_only_scope"]
    surface_map = packet["accessible_structure_surface_map"]

    assert surface_map["requires_attendance"] is True
    assert surface_map["selector_confidence"] == "fixture_only_no_live_selectors"
    assert "No browser automation in this fixture packet" in scope["allowed_automation"]

    blocked_actions = set(scope["blocked_actions"])
    assert PROHIBITED_ACTION_TERMS.issubset(blocked_actions)

    observed_action_kinds = {
        action["kind"] for action in surface_map["read_only_actions_to_map"]
    }
    assert observed_action_kinds == {
        "read_only_observation",
        "attended_manual_navigation_observation",
    }


def test_packet_redaction_policy_blocks_private_devhub_artifacts():
    packet = load_packet()
    redaction_policy = packet["redaction_policy"]

    assert redaction_policy["classification"] == "commit_safe_redacted_metadata_only"
    assert SENSITIVE_REDACTION_TERMS.issubset(set(redaction_policy["must_redact"]))

    storage_rules = " ".join(redaction_policy["storage_rules"])
    assert "screenshots" in storage_rules
    assert "traces" in storage_rules
    assert "HAR files" in storage_rules
    assert "storage state" in storage_rules
    assert "raw authenticated HTML" in storage_rules


def test_packet_defines_commit_safe_post_observation_journal():
    packet = load_packet()
    journal = packet["post_observation_journal_expectations"]
    example = journal["example_commit_safe_journal"]

    assert journal["journal_event_type"] == "DevHub attended preflight"
    assert example["packet_id"] == packet["packet_id"]
    assert example["workflow_id"] == packet["workflow"]["workflow_id"]
    assert example["user_attendance_confirmed"] is True
    assert example["read_only_scope_confirmed"] is True
    assert example["redaction_policy_applied"] is True
    assert "Synthetic packet only" in example["completion_evidence"]

    required_fields = set(journal["required_fields"])
    assert set(example).issuperset(required_fields)
