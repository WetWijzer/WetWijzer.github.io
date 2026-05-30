from pathlib import Path

from ppd.devhub.read_only_observation_rehearsal_v1 import (
    PROHIBITED_ATTESTATIONS,
    build_read_only_observation_rehearsal,
    rehearsal_to_json,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "devhub"
SURFACE_MAP = FIXTURE_DIR / "read_only_observation_surface_map_v1.json"
ACTION_CLASSIFICATIONS = FIXTURE_DIR / "read_only_observation_action_classification_v1.json"


def test_rehearsal_builds_cited_read_only_steps_from_fixtures() -> None:
    rehearsal = build_read_only_observation_rehearsal(SURFACE_MAP, ACTION_CLASSIFICATIONS)

    assert rehearsal["rehearsal_id"] == "devhub-read-only-observation-rehearsal-v1"
    assert rehearsal["source_policy"]["fixture_only"] is True
    assert rehearsal["source_policy"]["live_crawl"] is False
    assert rehearsal["source_policy"]["authenticated_automation"] is False
    assert len(rehearsal["steps"]) == 2

    first_step = rehearsal["steps"][0]
    assert first_step["surface_id"] == "devhub-public-landing"
    assert first_step["citations"] == [
        {
            "fixture": "read_only_observation_surface_map_v1.json",
            "pointer": "/surfaces/0",
        }
    ]
    assert first_step["allowed_observation_evidence"]
    assert any(
        evidence["action_label"] == "Sign In/Register"
        for evidence in first_step["blocked_action_evidence"]
    )


def test_rehearsal_declares_visible_evidence_redaction_and_attendance_gates() -> None:
    rehearsal = build_read_only_observation_rehearsal(SURFACE_MAP, ACTION_CLASSIFICATIONS)
    summary_step = rehearsal["steps"][1]

    visible_kinds = {
        expectation["kind"] for expectation in summary_step["visible_ui_evidence_expectations"]
    }
    assert "page_heading" in visible_kinds
    assert "accessible_landmarks" in visible_kinds
    assert "validation_messages" in visible_kinds
    assert "upload_controls" in visible_kinds
    assert "state_transitions" in visible_kinds
    assert "action_label" in visible_kinds

    redaction_text = "\n".join(
        requirement["requirement"] for requirement in summary_step["redaction_requirements"]
    )
    assert "Redact the value entirely" in redaction_text
    assert "Do not capture resulting page values" in redaction_text

    checkpoint_names = {
        checkpoint["checkpoint"]
        for checkpoint in summary_step["manual_attendance_checkpoints"]
    }
    assert "surface_requires_attendance" in checkpoint_names
    assert "surface_requires_exact_confirmation" in checkpoint_names
    assert "manual_gate_for_upload-corrections" in checkpoint_names
    assert "manual_gate_for_submit-application" in checkpoint_names
    assert "manual_gate_for_pay-fees" in checkpoint_names
    assert "manual_gate_for_schedule-inspection" in checkpoint_names


def test_rehearsal_attests_no_side_effect_workflows_and_offline_validation() -> None:
    rehearsal = build_read_only_observation_rehearsal(SURFACE_MAP, ACTION_CLASSIFICATIONS)

    assert rehearsal["attestations"] == PROHIBITED_ATTESTATIONS
    for key in (
        "no_login",
        "no_session_state",
        "no_click_through",
        "no_upload",
        "no_submit",
        "no_payment",
        "no_scheduling",
    ):
        assert key in rehearsal["attestations"]
        assert rehearsal["attestations"][key]

    commands = rehearsal["offline_validation_commands"]
    assert ["python3", "-m", "py_compile", "ppd/devhub/read_only_observation_rehearsal_v1.py"] in commands
    assert ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"] in commands

    serialized = rehearsal_to_json(rehearsal)
    assert "devhub-read-only-observation-rehearsal-v1" in serialized
    assert "no_session_state" in serialized
