from __future__ import annotations

from pathlib import Path

from ppd.logic.gap_analysis_refresh_packet_v2 import build_refresh_packet_from_files

FIXTURES = Path(__file__).parent / "fixtures" / "gap_analysis_refresh_packet_v2"


def _expectations(packet: dict, kind: str) -> dict[str, dict]:
    return {item["expectation_id"]: item for item in packet["expectation_updates"][kind]}


def test_gap_analysis_refresh_packet_v2_combines_cited_expectations() -> None:
    packet = build_refresh_packet_from_files(
        FIXTURES / "process_model_refresh_impact_v2.json",
        FIXTURES / "guardrail_bundle_refresh_candidate_v2.json",
        FIXTURES / "existing_user_gap_analysis_v2.json",
    )

    assert packet["packet_id"] == "gap-analysis-refresh-packet-v2"
    assert packet["packet_version"] == 2
    assert packet["case_id"] == "case_fixture_residential_addition_001"
    assert packet["process_id"] == "process_residential_addition_devhub_v2"
    assert packet["guardrail_bundle_id"] == "guardrail_residential_addition_devhub_v2_candidate"
    assert packet["input_fixture_ids"] == [
        "existing-user-gap-analysis-v2-fixture",
        "guardrail-bundle-refresh-candidate-v2-fixture",
        "process-model-refresh-impact-v2-fixture",
    ]

    missing_facts = _expectations(packet, "missing_fact")
    assert missing_facts["property_owner_authorization"]["citation_ids"] == ["src-devhub-application-guide-owner-auth"]
    assert missing_facts["contractor_license_status"]["reviewer_owner"] == {
        "reviewer_role": "ppd_guardrail_reviewer",
        "owner_role": "applicant",
    }

    stale_evidence = _expectations(packet, "stale_evidence")
    assert stale_evidence["site_plan_revision_date"]["citation_ids"] == ["src-single-pdf-file-prep"]

    conflicting_evidence = _expectations(packet, "conflicting_evidence")
    assert conflicting_evidence["project_scope_description"]["citation_ids"] == [
        "src-apply-permits-addition",
        "src-devhub-application-guide-scope",
    ]

    missing_documents = _expectations(packet, "missing_document")
    assert missing_documents["structural_calculations_pdf"]["citation_ids"] == ["src-submit-plans-separate-pdfs"]

    blocked_actions = _expectations(packet, "blocked_action")
    assert blocked_actions["submit_permit_request"]["citation_ids"] == ["src-devhub-certification-submit"]
    assert blocked_actions["upload_plan_set_to_devhub"]["reason"] == "Official upload is consequential and must wait for user attendance."

    next_safe_actions = _expectations(packet, "next_safe_action")
    assert next_safe_actions["draft_document_checklist"]["citation_ids"] == ["src-submit-plans-separate-pdfs"]
    assert next_safe_actions["prepare_reversible_field_map"]["citation_ids"] == ["src-devhub-application-guide-save-draft"]


def test_gap_analysis_refresh_packet_v2_contains_offline_attestations_and_validation() -> None:
    packet = build_refresh_packet_from_files(
        FIXTURES / "process_model_refresh_impact_v2.json",
        FIXTURES / "guardrail_bundle_refresh_candidate_v2.json",
        FIXTURES / "existing_user_gap_analysis_v2.json",
    )

    assert packet["attestations"] == {
        "no_live_devhub": True,
        "no_private_document": True,
        "no_gap_analysis_mutation": True,
        "no_process_mutation": True,
        "no_guardrail_mutation": True,
    }
    assert packet["reviewer_owner_fields"] == {
        "reviewer_role": "ppd_guardrail_reviewer",
        "owner_role": "applicant",
        "required_for_each_expectation": True,
    }
    assert packet["offline_validation_commands"] == [
        ["python3", "-m", "py_compile", "ppd/logic/gap_analysis_refresh_packet_v2.py"],
        ["python3", "-m", "pytest", "ppd/tests/test_gap_analysis_refresh_packet_v2.py"],
    ]

    for expectations in packet["expectation_updates"].values():
        for expectation in expectations:
            assert expectation["citation_ids"]
            assert expectation["reviewer_owner"]["reviewer_role"]
            assert expectation["reviewer_owner"]["owner_role"]
