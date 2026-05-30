from __future__ import annotations

from copy import deepcopy

from ppd.agent_readiness.public_source_recrawl_preflight_review_packet_v1 import (
    validate_public_source_recrawl_preflight_review_packet_v1,
)


def _valid_packet() -> dict[str, object]:
    return {
        "packet_version": "public_source_recrawl_preflight_review_packet_v1",
        "freshness_monitor_update_placeholder": "offline placeholder for freshness monitor update review",
        "reviewer_hold_placeholder": "offline reviewer may hold this source before live work",
        "reviewer_approval_placeholder": "offline reviewer may approve metadata-only preflight",
        "candidate_preflight_rows": [
            {
                "source_id": "ppd-online-tools",
                "canonical_url": "https://www.portland.gov/ppd/how-use-online-permitting-tools",
                "official_anchor_citation": "https://www.portland.gov/ppd/how-use-online-permitting-tools",
                "allow_reason": "official public PP&D guide on allowlisted host",
                "robots_decision_placeholder": "robots decision must be checked before live execution",
                "policy_decision_placeholder": "policy decision must be checked before live execution",
                "raw_body_persistence_exclusion_check": "metadata-only capture; raw body persistence excluded",
                "download_exclusion_check": "no document download is part of this dry run",
                "metadata_only_capture": True,
                "metadata_only_capture_placeholder": "capture URL, status placeholder, hash placeholder, and citation metadata only",
                "no_raw_body_persisted": True,
                "live_network_invoked": False,
                "raw_download_invoked": False,
                "processor_suite_adapter_ref": "ppd.processor_suite.public_metadata_archive_adapter",
                "freshness_monitor_update_placeholder": "freshness monitor update is deferred until reviewer approval",
                "reviewer_hold_placeholder": "reviewer hold disposition placeholder",
                "reviewer_approval_placeholder": "reviewer approval disposition placeholder",
                "processor_handoff_dry_run_prerequisites": [
                    "allowlist decision recorded",
                    "robots decision recorded",
                    "metadata-only adapter selected",
                ],
                "validation_commands": [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]],
            }
        ],
        "synthetic_request_rows": [
            {
                "source_id": "ppd-online-tools",
                "synthetic_request_id": "synthetic-ppd-online-tools-get",
                "canonical_url": "https://www.portland.gov/ppd/how-use-online-permitting-tools",
                "method": "GET",
                "synthetic_only": True,
                "network_invoked": False,
                "body_included": False,
                "request_metadata_placeholder": "offline request metadata shape only",
            }
        ],
        "active_artifact_mutation": False,
        "active_prompt_mutation": False,
        "active_release_state_mutation": False,
        "active_guardrail_mutation": False,
        "validation_commands": [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]],
    }


def _errors(packet: dict[str, object]) -> tuple[str, ...]:
    return validate_public_source_recrawl_preflight_review_packet_v1(packet).errors


def test_valid_public_source_recrawl_preflight_packet_accepts_metadata_only_fixture() -> None:
    result = validate_public_source_recrawl_preflight_review_packet_v1(_valid_packet())

    assert result.valid is True
    assert result.errors == ()


def test_public_source_recrawl_preflight_packet_rejects_missing_required_rows_and_placeholders() -> None:
    packet = _valid_packet()
    packet.pop("synthetic_request_rows")
    packet.pop("validation_commands")
    row = packet["candidate_preflight_rows"][0]  # type: ignore[index]
    assert isinstance(row, dict)
    for key in (
        "allow_reason",
        "metadata_only_capture_placeholder",
        "processor_suite_adapter_ref",
        "freshness_monitor_update_placeholder",
        "reviewer_hold_placeholder",
        "reviewer_approval_placeholder",
    ):
        row.pop(key)

    errors = _errors(packet)

    assert "synthetic_request_rows must contain at least one synthetic request row" in errors
    assert "validation_commands must include at least one command array" in errors
    assert "candidate_preflight_rows[0] must include allow_reason or skip_reason" in errors
    assert "candidate_preflight_rows[0].metadata_only_capture_placeholder is required" in errors
    assert "candidate_preflight_rows[0].processor_suite_adapter_ref is required" in errors
    assert "candidate_preflight_rows[0].freshness_monitor_update_placeholder is required" in errors
    assert "candidate_preflight_rows[0].reviewer_hold_placeholder is required" in errors
    assert "candidate_preflight_rows[0].reviewer_approval_placeholder is required" in errors


def test_public_source_recrawl_preflight_packet_rejects_prohibited_artifacts_claims_and_mutations() -> None:
    packet = deepcopy(_valid_packet())
    packet["active_guardrail_mutation"] = True
    packet["notes"] = [
        "browser-state trace.zip was captured",
        "raw crawl response body retained",
        "live crawl completed successfully",
        "permit will be approved",
        "submit permit through DevHub",
    ]
    row = packet["candidate_preflight_rows"][0]  # type: ignore[index]
    assert isinstance(row, dict)
    row["session_cookie"] = "cookie=value"

    errors = _errors(packet)

    assert "active_guardrail_mutation must be false" in errors
    assert any("private/authenticated/session/browser artifacts" in error for error in errors)
    assert any("raw crawl/PDF/downloaded data references" in error for error in errors)
    assert any("live crawl execution" in error for error in errors)
    assert any("legal or permitting outcome guarantees" in error for error in errors)
    assert any("consequential DevHub action language" in error for error in errors)
