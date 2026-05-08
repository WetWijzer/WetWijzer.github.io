from __future__ import annotations

import json
from pathlib import Path

from ppd.contracts.guardrail_bundle import compile_guardrail_bundle


def test_compile_reviewed_nodes_into_guardrail_bundle() -> None:
    fixture_path = Path(__file__).parent / "fixtures" / "guardrails" / "reviewed_requirement_nodes.json"
    nodes = json.loads(fixture_path.read_text(encoding="utf-8"))

    bundle = compile_guardrail_bundle(nodes)

    assert bundle["version"] == 1
    assert [item["node_id"] for item in bundle["obligations"]] == [
        "ppd-intake-account",
        "ppd-property-address",
    ]
    assert bundle["prerequisites"] == [
        {
            "id": "prerequisite:ppd-property-address:ppd-intake-account",
            "node_id": "ppd-property-address",
            "requires_node_id": "ppd-intake-account",
            "predicate": "requires_prior_satisfied_requirement",
        }
    ]
    assert bundle["temporal_ordering"] == [
        {
            "id": "after:ppd-intake-account:ppd-property-address",
            "before_node_id": "ppd-intake-account",
            "after_node_id": "ppd-property-address",
            "predicate": "must_occur_after",
        }
    ]
    assert [item["fact"] for item in bundle["missing_fact_prompts"]] == [
        "devhub_account_status",
        "property_address",
    ]
    assert bundle["exact_confirmation_gates"][0]["node_id"] == "ppd-intake-account"
    assert [item["official_action"] for item in bundle["refused_official_action_predicates"]] == [
        "create_account",
        "submit_application",
    ]


def test_unreviewed_nodes_are_ignored() -> None:
    bundle = compile_guardrail_bundle(
        [
            {"id": "draft", "status": "draft", "text": "Do not compile."},
            {"id": "accepted", "status": "accepted", "text": "Compile this."},
        ]
    )

    assert [item["node_id"] for item in bundle["obligations"]] == ["accepted"]
