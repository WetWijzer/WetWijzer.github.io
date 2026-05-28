from __future__ import annotations

from pathlib import Path

import pytest

from ppd.process_model_assembly_packet import (
    ProcessModelAssemblyError,
    assemble_process_model_packet,
    assemble_process_model_packet_from_fixture,
    load_assembly_fixture,
)


FIXTURE = (
    Path(__file__).parent
    / "fixtures"
    / "process_model"
    / "fixture_first_assembly_packet.json"
)


def test_fixture_first_packet_assembles_reviewed_requirement_nodes() -> None:
    packet = assemble_process_model_packet_from_fixture(FIXTURE)

    model = packet["process_model"]
    linkage = packet["guardrail_bundle_linkage"]

    assert packet["packet_type"] == "fixture_first_process_model_assembly"
    assert model["process_id"] == "synthetic-residential-plan-review-intake"
    assert model["guardrail_bundle_id"] == "guardrail-synthetic-residential-plan-review-intake"
    assert linkage["guardrail_bundle_id"] == model["guardrail_bundle_id"]
    assert linkage["process_id"] == model["process_id"]
    assert "req-draft-unreviewed-note" not in linkage["reviewed_requirement_node_ids"]

    assert {fact["fact_key"] for fact in model["required_user_facts"]} == {
        "project_scope",
        "property_address",
    }
    assert {document["document_key"] for document in model["required_documents"]} == {
        "complete_drawing_plans"
    }
    assert model["file_rules"]
    assert model["fees"]
    assert model["unsupported_paths"]
    assert model["exceptions"]
    assert model["deadlines"]
    assert model["stages"] == [
        "property lookup",
        "permit type selection",
        "document preparation",
        "application data entry",
        "upload staging",
        "submission",
        "fee payment",
        "corrections/checksheets",
    ]
    assert model["devhub_surface_refs"] == [
        "devhub-fees",
        "devhub-property-search",
        "devhub-submit-application",
    ]


def test_packet_source_evidence_is_shared_by_model_and_guardrail_linkage() -> None:
    packet = assemble_process_model_packet_from_fixture(FIXTURE)

    model = packet["process_model"]
    linkage = packet["guardrail_bundle_linkage"]

    assert model["source_evidence_ids"] == linkage["source_evidence_ids"]
    assert set(model["source_evidence_ids"]) == {
        "src-devhub-guide-apply",
        "src-fee-payment-guide",
        "src-file-naming-standards",
        "src-single-pdf-process",
    }


def test_assembly_rejects_uncommitted_evidence_ids() -> None:
    payload = load_assembly_fixture(FIXTURE)
    payload["requirement_node_candidates"][0]["source_evidence_ids"] = ["src-not-committed"]

    with pytest.raises(ProcessModelAssemblyError, match="uncommitted evidence id"):
        assemble_process_model_packet(payload)


def test_assembly_requires_all_process_model_sections() -> None:
    payload = load_assembly_fixture(FIXTURE)
    payload["requirement_node_candidates"] = [
        node
        for node in payload["requirement_node_candidates"]
        if node["requirement_id"] != "req-fee-trigger-intake"
    ]

    with pytest.raises(ProcessModelAssemblyError, match="fees"):
        assemble_process_model_packet(payload)
