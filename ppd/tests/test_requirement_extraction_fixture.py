from __future__ import annotations

from pathlib import Path

from ppd.requirement_extraction import extract_requirement_nodes


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "requirement_extraction" / "synthetic_guidance.txt"


def test_synthetic_guidance_maps_to_requirement_nodes_with_evidence_ids() -> None:
    nodes = extract_requirement_nodes(FIXTURE_PATH.read_text(encoding="utf-8"))

    assert [(node["type"], node["source_evidence_id"]) for node in nodes] == [
        ("obligation", "E1"),
        ("prohibition", "E2"),
        ("permission", "E3"),
        ("precondition", "E4"),
        ("deadline", "E5"),
        ("fee_trigger", "E6"),
        ("license_requirement", "E7"),
        ("document_requirement", "E8"),
        ("action_gate", "E9"),
    ]

    assert {node["id"] for node in nodes} == {
        "e1_obligation",
        "e2_prohibition",
        "e3_permission",
        "e4_precondition",
        "e5_deadline",
        "e6_fee_trigger",
        "e7_license_requirement",
        "e8_document_requirement",
        "e9_action_gate",
    }
    assert all(node["text"] for node in nodes)
