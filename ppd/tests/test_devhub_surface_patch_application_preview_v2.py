from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from ppd.devhub_surface_patch_application_preview_v2 import (
    ATTESTATIONS,
    build_devhub_surface_patch_application_preview_v2_from_fixture,
    require_devhub_surface_patch_application_preview_v2,
    validate_devhub_surface_patch_application_preview_v2,
)

FIXTURE = Path(__file__).parent / "fixtures" / "devhub_surface_patch_application_preview_v2" / "source_packets.json"


def valid_preview() -> dict[str, object]:
    return build_devhub_surface_patch_application_preview_v2_from_fixture(FIXTURE)


def error_text(packet: dict[str, object]) -> str:
    return "\n".join(validate_devhub_surface_patch_application_preview_v2(packet).errors)


def test_builds_inactive_cited_surface_registry_fixture_patch_previews() -> None:
    packet = valid_preview()

    assert packet["preview_type"] == "ppd.devhub_surface_patch_application_preview.v2"
    assert packet["fixture_first"] is True
    assert packet["attestations"] == ATTESTATIONS
    assert packet["affected_surface_ids"] == ["devhub-home-read-only"]
    assert packet["reviewer_owner_fields"]
    assert packet["rollback_checkpoints"]

    previews = packet["surface_registry_fixture_patch_previews"]
    assert isinstance(previews, list)
    assert previews
    first = previews[0]
    assert isinstance(first, dict)
    assert first["inactive"] is True
    assert first["surface_registry_fixture_patch"] is True
    assert first["read_only"] is True
    assert first["before_synthetic_action_rows"]
    assert first["after_synthetic_action_rows"]
    assert first["selector_confidence_deltas"]
    assert first["manual_handoff_disposition"]["required"] is True
    assert first["redaction_disposition"]["disposition"] == "synthetic-only"
    assert first["citations"]
    require_devhub_surface_patch_application_preview_v2(packet)


def test_preview_records_selector_confidence_delta_owner_rollback_and_offline_commands() -> None:
    packet = valid_preview()
    preview = packet["surface_registry_fixture_patch_previews"][0]
    delta = preview["selector_confidence_deltas"][0]

    assert delta["before_confidence"] == "current_fixture_selector_confidence_retained"
    assert delta["after_confidence"] == "medium"
    assert preview["reviewer_owner"] == "ppd-devhub-surface-reviewer"
    assert packet["rollback_checkpoints"][0]["affected_surface_ids"] == ["devhub-home-read-only"]
    assert ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"] in packet["offline_validation_commands"]


def test_validation_rejects_uncited_surface_and_action_preview_rows() -> None:
    broken = deepcopy(valid_preview())
    preview = broken["surface_registry_fixture_patch_previews"][0]
    preview["citations"] = []
    preview["before_synthetic_action_rows"][0]["citations"] = []
    preview["after_synthetic_action_rows"][0]["citations"] = []
    preview["selector_confidence_deltas"][0]["citations"] = []

    text = error_text(broken)

    assert "surface_registry_fixture_patch_previews[0].citations must be non-empty" in text
    assert "before_synthetic_action_rows[0].citations must be non-empty" in text
    assert "after_synthetic_action_rows[0].citations must be non-empty" in text
    assert "selector_confidence_deltas[0].citations must be non-empty" in text


def test_validation_rejects_missing_action_rows_selector_deltas_and_dispositions() -> None:
    broken = deepcopy(valid_preview())
    preview = broken["surface_registry_fixture_patch_previews"][0]
    preview["before_synthetic_action_rows"] = []
    preview["after_synthetic_action_rows"] = []
    preview["selector_confidence_deltas"] = []
    preview["manual_handoff_disposition"] = {}
    preview["redaction_disposition"] = {}

    text = error_text(broken)

    assert "before_synthetic_action_rows must be non-empty" in text
    assert "after_synthetic_action_rows must be non-empty" in text
    assert "selector_confidence_deltas must be non-empty" in text
    assert "manual_handoff_disposition must be present" in text
    assert "redaction_disposition must be present" in text


def test_validation_rejects_missing_selector_confidence_delta_fields() -> None:
    broken = deepcopy(valid_preview())
    delta = broken["surface_registry_fixture_patch_previews"][0]["selector_confidence_deltas"][0]
    delta["before_confidence"] = ""
    delta["after_confidence"] = ""
    delta["delta_disposition"] = ""

    text = error_text(broken)

    assert "selector_confidence_deltas[0].before_confidence must be present" in text
    assert "selector_confidence_deltas[0].after_confidence must be present" in text
    assert "selector_confidence_deltas[0].delta_disposition must be present" in text


def test_validation_rejects_active_registry_guardrail_prompt_monitoring_release_and_agent_mutation_flags() -> None:
    broken = deepcopy(valid_preview())
    broken["surface_registry_mutation_enabled"] = True
    broken["active_guardrail_mutation"] = "enabled"
    broken["active_prompt_mutation"] = True
    broken["active_monitoring_mutation"] = True
    broken["active_release_state_mutation"] = True
    broken["active_agent_state_mutation"] = True

    text = error_text(broken)

    assert text.count("active mutation flags are not allowed") >= 6


def test_validation_rejects_private_credentials_session_and_browser_artifacts() -> None:
    broken = deepcopy(valid_preview())
    preview = broken["surface_registry_fixture_patch_previews"][0]
    preview["auth_state"] = "storage-state.json"
    preview["credentials"] = {"username": "private-user"}
    preview["session_artifact"] = "devhub session artifact"
    preview["private_value"] = "private DevHub value"
    preview["screenshot_path"] = "devhub.png"
    preview["trace_path"] = "trace.zip"
    preview["har_path"] = "devhub.har"

    text = error_text(broken)

    assert "auth_state is prohibited" in text
    assert "credentials is prohibited" in text
    assert "session_artifact is prohibited" in text
    assert "private_value is prohibited" in text
    assert "screenshot_path is prohibited" in text
    assert "trace_path is prohibited" in text
    assert "har_path is prohibited" in text
    assert "screenshot, trace, HAR, or browser artifact reference" in text


def test_validation_rejects_browser_completion_live_devhub_claims_outcome_guarantees_and_consequential_actions() -> None:
    broken = deepcopy(valid_preview())
    preview = broken["surface_registry_fixture_patch_previews"][0]
    preview["automation_note"] = "Browser automation completed and DevHub live run completed."
    preview["outcome_note"] = "Permit will be approved with guaranteed approval."
    preview["action_note"] = "Enable submission, submit application, upload correction, schedule inspection, and submit payment."

    text = error_text(broken)

    assert "browser automation or live DevHub completion claim" in text
    assert "legal or permitting outcome guarantee" in text
    assert "consequential action enablement language" in text
