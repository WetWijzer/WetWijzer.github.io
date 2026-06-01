from pathlib import Path

from ppd.agent_api_rehearsal_v4 import (
    OFFLINE_VALIDATION_COMMANDS,
    PROHIBITED_SIDE_EFFECTS,
    rehearse_agent_api_compatibility_v4,
)

FIXTURE_ROOT = Path(__file__).parent / "fixtures"
MONITORING_FIXTURES = FIXTURE_ROOT / "post_activation_monitoring_rehearsal_v4"
REQUEST_FIXTURES = FIXTURE_ROOT / "synthetic_agent_requests_v4"


def _responses_by_request_id():
    result = rehearse_agent_api_compatibility_v4(MONITORING_FIXTURES, REQUEST_FIXTURES)
    return {response["request_id"]: response for response in result["responses"]}


def test_rehearsal_consumes_only_expected_fixture_kinds():
    result = rehearse_agent_api_compatibility_v4(MONITORING_FIXTURES, REQUEST_FIXTURES)

    assert result["fixture_inputs"] == {
        "monitoring_fixture_kind": "post_activation_monitoring_rehearsal_v4",
        "request_fixture_kind": "synthetic_agent_request_v4",
        "monitoring_fixture_count": 1,
        "request_fixture_count": 1,
    }
    assert result["side_effects"] == PROHIBITED_SIDE_EFFECTS
    assert result["offline_validation_commands"] == OFFLINE_VALIDATION_COMMANDS


def test_reports_missing_stale_and_conflicting_evidence():
    responses = _responses_by_request_id()

    missing = responses["request-missing-facts"]
    assert missing["status"] == "blocked"
    assert missing["blocked_reasons"] == ["missing_facts"]
    assert missing["missing_facts"] == ["site_address", "permit_type"]

    stale = responses["request-stale-evidence"]
    assert stale["blocked_reasons"] == ["stale_evidence"]
    assert stale["stale_evidence"] == [
        {
            "fact_id": "contractor_license_status",
            "observed_at": "2026-01-15",
            "freshness_required_after": "2026-05-01",
        }
    ]

    conflict = responses["request-conflicting-evidence"]
    assert conflict["blocked_reasons"] == ["conflicting_evidence"]
    assert conflict["conflicting_evidence"] == [
        {
            "fact_id": "project_scope",
            "values": ["interior remodel", "detached ADU"],
            "resolution_required": "Ask user to confirm the active scope before drafting.",
        }
    ]


def test_reports_action_boundaries_without_side_effects():
    responses = _responses_by_request_id()

    draft = responses["request-reversible-draft"]
    assert draft["action_classification"] == "reversible_draft_only"
    assert draft["reversible_draft_only"] is True
    assert draft["manual_handoff_required"] is False
    assert draft["status"] == "ready_for_read_only_response"

    handoff = responses["request-manual-handoff"]
    assert handoff["action_classification"] == "manual_handoff_required"
    assert handoff["manual_handoff_required"] is True
    assert handoff["status"] == "blocked"
    assert handoff["refusal_explanation"].startswith("This official DevHub action requires")

    refused = responses["request-refusal"]
    assert refused["action_classification"] == "refused"
    assert refused["status"] == "blocked"
    assert "outside PP&D offline rehearsal boundaries" in refused["refusal_explanation"]

    for response in responses.values():
        assert response["side_effects"] == PROHIBITED_SIDE_EFFECTS
        assert all(value is False for value in response["side_effects"].values())
        assert response["guarantees"] == []


def test_source_citation_payloads_and_validation_commands_are_exact():
    responses = _responses_by_request_id()
    response = responses["request-citations"]

    assert response["source_citations"] == [
        {
            "source_id": "src-devhub-guide-submit-application",
            "canonical_url": "https://www.portland.gov/ppd/devhub-guide-submit-permit-application",
            "title": "DevHub permit application guide",
            "last_verified_at": "2026-05-08",
            "excerpt": "The public guide describes application request types, save-for-later behavior, uploads, and acknowledgement review.",
        },
        {
            "source_id": "src-submit-plans-online",
            "canonical_url": "https://www.portland.gov/ppd/get-permit/submit-plans-online",
            "title": "Submit Plans Online / Single PDF Process",
            "last_verified_at": "2026-05-08",
            "excerpt": "Plans are prepared as one PDF while applications, calculations, and supporting documents are separate PDFs.",
        },
    ]
    assert response["offline_validation_commands"] == [
        ["python3", "-m", "py_compile", "ppd/agent_api_rehearsal_v4.py"],
        ["python3", "-m", "pytest", "ppd/tests/test_agent_api_rehearsal_v4.py"],
        ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
    ]
