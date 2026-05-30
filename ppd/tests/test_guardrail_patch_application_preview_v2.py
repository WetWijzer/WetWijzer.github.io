from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from ppd.guardrail_patch_application_preview_v2 import (
    ATTESTATIONS,
    build_guardrail_patch_application_preview_v2_from_fixture,
    require_guardrail_patch_application_preview_v2,
    validate_guardrail_patch_application_preview_v2,
)

FIXTURE = Path(__file__).parent / "fixtures" / "guardrail_patch_application_preview_v2" / "source_packets.json"


def valid_preview() -> dict[str, object]:
    return build_guardrail_patch_application_preview_v2_from_fixture(FIXTURE)


def error_text(packet: dict[str, object]) -> str:
    return "\n".join(validate_guardrail_patch_application_preview_v2(packet).errors)


def test_builds_inactive_cited_guardrail_fixture_patch_previews() -> None:
    packet = valid_preview()

    assert packet["preview_type"] == "ppd.guardrail_patch_application_preview.v2"
    assert packet["fixture_first"] is True
    assert packet["attestations"] == ATTESTATIONS
    assert packet["affected_guardrail_bundle_ids"] == ["bundle-building-permit-draft-v1"]
    assert packet["reviewer_owner_fields"]
    assert packet["rollback_checkpoints"]

    previews = packet["guardrail_fixture_patch_previews"]
    assert isinstance(previews, list)
    assert previews
    first = previews[0]
    assert isinstance(first, dict)
    assert first["inactive"] is True
    assert first["guardrail_fixture_patch"] is True
    assert first["before_predicate_rows"]
    assert first["after_predicate_rows"]
    assert first["blocked_consequential_action_checks"]
    assert first["explanation_template_deltas"]
    assert first["citations"]
    require_guardrail_patch_application_preview_v2(packet)


def test_preview_records_predicate_delta_blocked_actions_owner_rollback_and_offline_commands() -> None:
    packet = valid_preview()
    preview = packet["guardrail_fixture_patch_previews"][0]
    before_row = preview["before_predicate_rows"][0]
    after_row = preview["after_predicate_rows"][0]
    template_delta = preview["explanation_template_deltas"][0]

    assert before_row["predicate_state"] == "current_fixture_predicate_retained"
    assert after_row["predicate_state"] == "after_inactive_fixture_preview"
    assert template_delta["delta_disposition"] == "review_required_before_any_active_guardrail_or_prompt_change"
    assert preview["reviewer_owner"] == "ppd-guardrail-reviewer"
    assert packet["rollback_checkpoints"][0]["affected_guardrail_bundle_ids"] == ["bundle-building-permit-draft-v1"]
    assert ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"] in packet["offline_validation_commands"]


def test_validation_rejects_uncited_preview_predicate_block_and_template_rows() -> None:
    broken = deepcopy(valid_preview())
    preview = broken["guardrail_fixture_patch_previews"][0]
    preview["citations"] = []
    preview["before_predicate_rows"][0]["citations"] = []
    preview["after_predicate_rows"][0]["citations"] = []
    preview["blocked_consequential_action_checks"][0]["citations"] = []
    preview["explanation_template_deltas"][0]["citations"] = []

    text = error_text(broken)

    assert "guardrail_fixture_patch_previews[0].citations must be non-empty" in text
    assert "before_predicate_rows[0].citations must be non-empty" in text
    assert "after_predicate_rows[0].citations must be non-empty" in text
    assert "blocked_consequential_action_checks[0].citations must be non-empty" in text
    assert "explanation_template_deltas[0].citations must be non-empty" in text


def test_validation_rejects_missing_predicate_rows_blocked_checks_and_template_deltas() -> None:
    broken = deepcopy(valid_preview())
    preview = broken["guardrail_fixture_patch_previews"][0]
    preview["before_predicate_rows"] = []
    preview["after_predicate_rows"] = []
    preview["blocked_consequential_action_checks"] = []
    preview["explanation_template_deltas"] = []

    text = error_text(broken)

    assert "before_predicate_rows must be non-empty" in text
    assert "after_predicate_rows must be non-empty" in text
    assert "blocked_consequential_action_checks must be non-empty" in text
    assert "explanation_template_deltas must be non-empty" in text


def test_validation_rejects_missing_blocked_check_and_template_delta_fields() -> None:
    broken = deepcopy(valid_preview())
    preview = broken["guardrail_fixture_patch_previews"][0]
    blocked = preview["blocked_consequential_action_checks"][0]
    blocked["blocked"] = False
    blocked["reason"] = ""
    delta = preview["explanation_template_deltas"][0]
    delta["before_template"] = ""
    delta["after_template"] = ""
    delta["delta_disposition"] = ""

    text = error_text(broken)

    assert "blocked_consequential_action_checks[0].blocked must be true" in text
    assert "blocked_consequential_action_checks[0].reason must be present" in text
    assert "explanation_template_deltas[0].before_template must be present" in text
    assert "explanation_template_deltas[0].after_template must be present" in text
    assert "explanation_template_deltas[0].delta_disposition must be present" in text


def test_validation_rejects_active_guardrail_prompt_release_monitoring_and_agent_mutation_flags() -> None:
    broken = deepcopy(valid_preview())
    broken["active_guardrail_mutation"] = "enabled"
    broken["active_prompt_mutation"] = True
    broken["active_monitoring_mutation"] = True
    broken["active_release_state_mutation"] = True
    broken["active_agent_state_mutation"] = True

    text = error_text(broken)

    assert text.count("active mutation flags are not allowed") >= 5


def test_validation_rejects_private_artifacts_live_claims_outcome_guarantees_and_official_action_language() -> None:
    broken = deepcopy(valid_preview())
    preview = broken["guardrail_fixture_patch_previews"][0]
    preview["llm_response"] = "called live LLM"
    preview["auth_state"] = "storage_state.json"
    preview["private_value"] = "private DevHub value from a session token"
    preview["automation_note"] = "Live crawler completed, processor completed, and DevHub live run completed."
    preview["outcome_note"] = "Permit will be approved with guaranteed approval."
    preview["action_note"] = "Enable submission, submit application, upload correction, schedule inspection, and submit payment."

    text = error_text(broken)

    assert "llm_response is prohibited" in text
    assert "auth_state is prohibited" in text
    assert "private_value is prohibited" in text
    assert "private, credential, session, or authenticated value language" in text
    assert "live LLM, DevHub, crawler, or processor execution claim" in text
    assert "legal or permitting outcome guarantee" in text
    assert "consequential official-action language" in text
