from __future__ import annotations

import importlib.util
import json
from pathlib import Path

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "processor_suite" / "tranche2_public_document_flow.json"
MODULE_PATH = Path(__file__).parents[1] / "processor_suite" / "tranche2_integration_plan.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("tranche2_integration_plan", MODULE_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_tranche2_public_document_flow_fixture_is_valid() -> None:
    module = _load_module()
    plan = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    module.assert_valid_integration_plan(plan)


def test_agent_handoff_remains_blocked_until_requirement_review() -> None:
    plan = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    handoff = next(stage for stage in plan["stages"] if stage["name"] == "agent_handoff")

    assert handoff["outputs"]["allowed"] is False
    assert "human_review_required" in handoff["outputs"]["blocking_checks"]
