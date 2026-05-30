from __future__ import annotations

from copy import deepcopy

from ppd.guardrail_patch_application_preview_v2_hardening import (
    validate_guardrail_patch_application_preview_v2_hardening,
)


def _citation() -> dict[str, str]:
    return {"citation_id": "src-devhub-submit-guide-certification-step"}


def _valid_preview() -> dict[str, object]:
    citation = _citation()
    return {
        "preview_type": "ppd.guardrail_patch_application_preview.v2",
        "guardrail_fixture_patch_previews": [
            {
                "preview_id": "guardrail-preview-submit",
                "citations": [citation],
                "before_predicate_rows": [{"row_id": "before", "citations": [citation]}],
                "after_predicate_rows": [{"row_id": "after", "citations": [citation]}],
                "blocked_consequential_action_checks": [{"check_id": "blocked-submit", "citations": [citation]}],
                "explanation_template_deltas": [{"template_delta_id": "template-submit", "citations": [citation]}],
                "rollback_checkpoint": "Discard the inactive preview; no active guardrail state changes.",
            }
        ],
        "rollback_checkpoints": [
            {
                "checkpoint_id": "discard-preview",
                "summary": "Discard inactive preview packet.",
                "citations": [citation],
            }
        ],
    }


def _error_text(packet: dict[str, object]) -> str:
    return "\n".join(validate_guardrail_patch_application_preview_v2_hardening(packet).errors)


def test_hardening_accepts_cited_inactive_preview_shape() -> None:
    result = validate_guardrail_patch_application_preview_v2_hardening(_valid_preview())

    assert result.ok is True
    assert result.errors == ()


def test_hardening_rejects_uncited_predicate_preview_rows() -> None:
    packet = _valid_preview()
    preview = packet["guardrail_fixture_patch_previews"][0]
    assert isinstance(preview, dict)
    preview["citations"] = [{}]
    preview["before_predicate_rows"] = [{"row_id": "before", "citations": [{}]}]
    preview["after_predicate_rows"] = [{"row_id": "after", "citations": [{}]}]

    text = _error_text(packet)

    assert "guardrail_fixture_patch_previews[0].citations[0] must include a citation" in text
    assert "before_predicate_rows[0].citations[0] must include a citation" in text
    assert "after_predicate_rows[0].citations[0] must include a citation" in text


def test_hardening_rejects_missing_required_preview_rows_and_rollback() -> None:
    packet = _valid_preview()
    preview = packet["guardrail_fixture_patch_previews"][0]
    assert isinstance(preview, dict)
    preview["before_predicate_rows"] = []
    preview["after_predicate_rows"] = []
    preview["blocked_consequential_action_checks"] = []
    preview["explanation_template_deltas"] = []
    preview["rollback_checkpoint"] = ""
    packet["rollback_checkpoints"] = []

    text = _error_text(packet)

    assert "before_predicate_rows must be non-empty" in text
    assert "after_predicate_rows must be non-empty" in text
    assert "blocked_consequential_action_checks must be non-empty" in text
    assert "explanation_template_deltas must be non-empty" in text
    assert "rollback_checkpoint must be present" in text
    assert "rollback_checkpoints must be non-empty" in text


def test_hardening_rejects_private_raw_live_outcome_and_final_action_content() -> None:
    packet = _valid_preview()
    preview = packet["guardrail_fixture_patch_previews"][0]
    assert isinstance(preview, dict)
    preview.update(
        {
            "private_fact": "authenticated fact from a private DevHub value and session token",
            "raw_pdf": "raw PDF stored at storage_state.json with screenshot trace.zip",
            "claim": "Called live LLM, opened DevHub, ran crawler, and ran processor.",
            "outcome": "Permit will be approved with guaranteed approval.",
            "official_action": "Final submit, submit payment, upload correction, schedule inspection, and cancel permit.",
        }
    )

    text = _error_text(packet)

    assert "private, credential, session, or authenticated fact language" in text
    assert "raw crawl, PDF, session, browser, private, or authenticated artifacts are not allowed" in text
    assert "raw crawl, PDF, session, or browser artifact language" in text
    assert "live LLM, DevHub, crawler, or processor execution claim" in text
    assert "legal or permitting outcome guarantee" in text
    assert "final submission, payment, upload, scheduling, or cancellation language" in text


def test_hardening_rejects_authenticated_urls_and_all_active_mutation_flag_families() -> None:
    packet = deepcopy(_valid_preview())
    packet["rollback_checkpoints"][0]["citations"] = [
        {"url": "https://user:pass@www.portland.gov/ppd/devhub-guide-submit-permit-application"}
    ]
    packet.update(
        {
            "active_guardrail_mutation": True,
            "active_prompt_mutation": True,
            "active_source_mutation": True,
            "active_surface_registry_mutation": True,
            "active_monitoring_mutation": True,
            "active_release_state_mutation": True,
            "active_agent_state_mutation": True,
        }
    )

    text = _error_text(packet)

    assert "authenticated URLs are not allowed" in text
    assert text.count("active guardrail, prompt, source, surface-registry, monitoring, release-state, or agent-state mutation flags are not allowed") == 7
