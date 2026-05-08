import json
from pathlib import Path

import pytest

from ppd.guardrails.compiler import GuardrailBundleCompiler, GuardrailCompileError


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "guardrails" / "minimal_bundle.json"


def load_fixture():
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def test_compiler_covers_formal_guardrail_categories():
    compiled = GuardrailBundleCompiler().compile(load_fixture())

    assert compiled.category_counts() == {
        "deterministic_predicates": 1,
        "deontic_rules": 1,
        "temporal_rules": 1,
        "exact_confirmation_predicates": 1,
        "refused_action_predicates": 1,
        "explanation_support_maps": 5,
    }
    assert compiled.deterministic_predicates[0]["id"] == "predicate.has_permit_record"
    assert compiled.deontic_rules[0]["modality"] == "prohibited"
    assert compiled.temporal_rules[0]["relation"] == "after"
    assert compiled.exact_confirmation_predicates[0]["expected_text"]
    assert compiled.refused_action_predicates[0]["action"] == "payment"
    assert compiled.explanation_support_maps["predicate.refuses_payment"] == (
        "source.fixture.refusal",
    )


def test_compiler_rejects_unknown_explanation_support_rule_id():
    bundle = load_fixture()
    bundle["explanation_support_maps"]["missing.rule"] = ["source.fixture.missing"]

    with pytest.raises(GuardrailCompileError, match="unknown rule ids"):
        GuardrailBundleCompiler().compile(bundle)


def test_compiler_rejects_duplicate_rule_ids_within_category():
    bundle = load_fixture()
    bundle["deterministic_predicates"].append(
        {
            "id": "predicate.has_permit_record",
            "source": "fixture",
            "predicate": "duplicate",
        }
    )

    with pytest.raises(GuardrailCompileError, match="duplicate guardrail id"):
        GuardrailBundleCompiler().compile(bundle)
