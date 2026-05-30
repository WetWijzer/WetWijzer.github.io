from __future__ import annotations

import importlib.util
import json
from pathlib import Path

MODULE_PATH = Path(__file__).parents[1] / "review" / "guarded_agent_replay_acceptance_packet_v2.py"
FIXTURE_DIR = Path(__file__).parent / "fixtures" / "guarded_agent_replay_acceptance_packet_v2"
MATRIX_PATH = FIXTURE_DIR / "post_release_guarded_agent_replay_matrix_v2.json"
EXPECTED_PATH = FIXTURE_DIR / "expected_acceptance_packet_v2.json"


def _load_module():
    spec = importlib.util.spec_from_file_location("guarded_agent_replay_acceptance_packet_v2", MODULE_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_build_acceptance_packet_matches_fixture():
    module = _load_module()
    matrix = _load_json(MATRIX_PATH)
    expected = _load_json(EXPECTED_PATH)

    assert module.build_acceptance_packet(matrix) == expected


def test_rows_are_ordered_for_reviewer_acceptance():
    module = _load_module()
    packet = module.build_acceptance_packet(_load_json(MATRIX_PATH))

    assert [row["scenario_id"] for row in packet["reviewer_acceptance_rows"]] == [
        "missing-parcel-fact",
        "blocked-certified-submission",
    ]
    assert [row["reviewer_order"] for row in packet["reviewer_acceptance_rows"]] == [1, 2]


def test_packet_is_fixture_first_and_offline_only():
    module = _load_module()
    packet = module.build_acceptance_packet(_load_json(MATRIX_PATH))

    scope = packet["acceptance_scope"]
    assert scope["fixture_first"] is True
    assert scope["offline_only"] is True
    assert scope["changes_active_prompts"] is False
    assert scope["changes_production_contracts"] is False
    assert scope["changes_guardrails"] is False
    assert scope["changes_release_state"] is False
    assert scope["changes_public_sources"] is False
    assert scope["creates_private_artifacts"] is False
    assert packet["exact_offline_validation_commands"] == module.OFFLINE_VALIDATION_COMMANDS
