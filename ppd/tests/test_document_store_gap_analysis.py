from __future__ import annotations

from pathlib import Path

import pytest

from ppd.document_store_gap_analysis import (
    DocumentStoreGapAnalysisError,
    load_document_store_gap_analysis_packet,
)

FIXTURE = Path(__file__).parent / "fixtures" / "document_store_gap_analysis" / "synthetic_single_pdf_case.json"


def test_document_store_gap_analysis_packet_identifies_core_gaps() -> None:
    packet = load_document_store_gap_analysis_packet(fixture_path=FIXTURE)

    assert packet["case_id"] == "synthetic_single_pdf_gap_case"
    assert packet["process_id"] == "process_single_pdf_residential_addition_synthetic"
    assert packet["privacy"] == {
        "fixture_only": True,
        "reads_private_files": False,
        "stores_private_paths": False,
    }

    assert {item["fact_id"] for item in packet["missing_facts"]} == {"owner_authorization"}
    assert {item["document_id"] for item in packet["missing_documents"]} == {"owner_signature_authorization"}
    assert {item["required_document_id"] for item in packet["stale_evidence"]} == {"structural_calculations"}
    assert {item["fact_id"] for item in packet["ambiguous_facts"]} == {"contractor_license"}
    assert any(item["fact_id"] == "project_valuation" for item in packet["conflicting_evidence"])

    blocked = {item["action_id"]: item for item in packet["blocked_actions"]}
    assert blocked["draft_application_values"]["blocked_by"] == ["project_valuation", "contractor_license"]
    assert set(blocked["stage_uploads"]["blocked_by"]) == {
        "structural_calculations",
        "owner_signature_authorization",
        "owner_authorization",
    }
    assert blocked["submit_application"]["requires_exact_confirmation"] is True

    confirmations = {item["confirmation_id"] for item in packet["required_confirmations"]}
    assert "stage_uploads" in confirmations
    assert "submit_application" in confirmations
    assert "resolve_conflicting_evidence" in confirmations
    assert "refresh_stale_evidence" in confirmations

    assert packet["next_safe_prompts"] == [
        "Can you confirm that the owner authorized this permit application?",
        "Provide or identify metadata for owner signature authorization.",
        "Is a licensed contractor attached to this application, or is this owner-performed work?",
        "Which synthetic fact value should control where the documents disagree?",
        "Can you confirm whether the stale evidence has been refreshed?",
    ]


def test_document_store_gap_analysis_rejects_private_paths(tmp_path: Path) -> None:
    unsafe_fixture = {
        "case_id": "unsafe",
        "as_of": "2026-05-28",
        "process_model": {
            "process_id": "process_unsafe",
            "required_user_facts": [],
            "required_documents": [],
            "action_gates": [],
        },
        "case_facts": [],
        "document_store_metadata": [
            {
                "document_id": "doc_unsafe",
                "title": "Unsafe",
                "document_type": "application_form",
                "local_path": "/home/example/private.pdf",
            }
        ],
    }

    path = tmp_path / "unsafe_private_path.json"
    path.write_text(__import__("json").dumps(unsafe_fixture), encoding="utf-8")

    with pytest.raises(DocumentStoreGapAnalysisError):
        load_document_store_gap_analysis_packet(fixture_path=path)
