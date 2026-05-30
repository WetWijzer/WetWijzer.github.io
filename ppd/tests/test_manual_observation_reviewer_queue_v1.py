from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, Dict, Mapping

import pytest

from ppd.devhub.manual_observation_reviewer_queue import ReviewerQueueError, build_reviewer_queue

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "devhub"


def _valid_packet() -> Dict[str, Any]:
    with (FIXTURE_DIR / "manual_observation_evidence_intake_packet_v1.json").open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _release_gate_matrix() -> Dict[str, Any]:
    return {
        "matrix_version": "devhub_release_gate_decision_matrix_v1",
        "decisions": [
            _release_gate("devhub-home-read-only-synthetic"),
            _release_gate("devhub-permit-status-read-only-synthetic"),
        ],
    }


def _release_gate(surface_id: str) -> Dict[str, Any]:
    return {
        "surface_id": surface_id,
        "decision": "manual_review_required_read_only",
        "decision_reasons": ["Synthetic fixture requires read-only human review before promotion."],
        "required_stop_gates": ["Stop before any authenticated DevHub mutation or official account action."],
        "reviewer_owner": "ppd-devhub-reviewer",
        "rollback_notes": ["Discard the queue item if any private value, artifact, or active mutation flag appears."],
        "offline_validation_commands": [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]],
        "read_only_scope": True,
        "synthetic_fixture": True,
        "mutation_flags": {
            "active_devhub_mutation": False,
            "active_surface_registry_mutation": False,
            "active_guardrail_mutation": False,
            "active_prompt_mutation": False,
            "active_release_state_mutation": False,
            "active_agent_state_mutation": False,
        },
        "attestations": {
            "no_login_automation": True,
            "no_session_state": True,
            "no_screenshot": True,
            "no_trace": True,
            "no_har": True,
            "no_click_through": True,
            "no_upload": True,
            "no_submit": True,
            "no_payment": True,
            "no_scheduling": True,
            "no_write_capable_action_evidence": True,
        },
    }


def _rejection_cases() -> Dict[str, Any]:
    with (FIXTURE_DIR / "manual_observation_reviewer_queue_v1_rejection_cases.json").open(
        "r", encoding="utf-8"
    ) as handle:
        return json.load(handle)


def _merge_patch(target: Dict[str, Any], patch: Mapping[str, Any]) -> None:
    for key, value in patch.items():
        if isinstance(value, Mapping) and isinstance(target.get(key), dict):
            _merge_patch(target[key], value)
        elif key == "observations" and isinstance(value, list):
            for index, observation_patch in enumerate(value):
                _merge_patch(target[key][index], observation_patch)
        else:
            target[key] = copy.deepcopy(value)


def test_manual_observation_reviewer_queue_accepts_commit_safe_fixture() -> None:
    queue = build_reviewer_queue(_valid_packet(), _release_gate_matrix())

    assert [item["surface_id"] for item in queue] == [
        "devhub-home-read-only-synthetic",
        "devhub-permit-status-read-only-synthetic",
    ]
    for item in queue:
        assert item["read_only_scope"] is True
        assert item["synthetic_fixture"] is True
        assert item["redaction_checks"]
        assert item["attendance_requirements"]
        assert all(value is False for value in item["mutation_flags"].values())
        assert item["attestations"]["no_write_capable_action_evidence"] is True


@pytest.mark.parametrize("case", _rejection_cases()["cases"], ids=lambda case: case["case_id"])
def test_manual_observation_reviewer_queue_rejects_unsafe_evidence(case: Mapping[str, Any]) -> None:
    packet = _valid_packet()
    for field in case.get("remove_observation_fields", []):
        packet["observations"][0].pop(field, None)
    patch = case.get("patch")
    if patch:
        _merge_patch(packet, patch)

    with pytest.raises(ReviewerQueueError, match=case["expected_error_fragment"]):
        build_reviewer_queue(packet, _release_gate_matrix())
