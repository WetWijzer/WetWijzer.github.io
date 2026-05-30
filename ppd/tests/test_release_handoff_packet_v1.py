import json
from pathlib import Path

from ppd.release_handoff_packet_v1 import validate_human_release_handoff_packet_v1


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "release_handoff_packet_v1"


def _fixture(name: str):
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def _codes(packet):
    return {issue.code for issue in validate_human_release_handoff_packet_v1(packet).issues}


def test_accepts_minimal_safe_handoff_packet_v1():
    result = validate_human_release_handoff_packet_v1(_fixture("valid_packet.json"))

    assert result.valid is True
    assert result.issues == ()


def test_rejects_uncited_recommendations():
    packet = _fixture("valid_packet.json")
    packet["recommendations"] = [{"summary": "Keep release human reviewed."}]

    assert "uncited_recommendation" in _codes(packet)


def test_rejects_missing_inspectable_fixture_families():
    packet = _fixture("valid_packet.json")
    packet["inspectable_fixture_families"] = []

    assert "missing_inspectable_fixture_families" in _codes(packet)


def test_rejects_missing_unresolved_blocker_disclosure():
    packet = _fixture("valid_packet.json")
    packet.pop("unresolved_blockers_disclosed")

    assert "missing_unresolved_blocker_disclosure" in _codes(packet)


def test_rejects_missing_rollback_and_post_apply_checklists():
    packet = _fixture("valid_packet.json")
    packet["rollback_checklist"] = []
    packet["post_apply_validation_checklist"] = []

    codes = _codes(packet)
    assert "missing_rollback_checklist" in codes
    assert "missing_post_apply_validation_checklist" in codes


def test_rejects_private_or_authenticated_artifacts():
    packet = _fixture("valid_packet.json")
    packet["artifacts"] = [
        {
            "artifact_id": "devhub-session-trace",
            "privacy_classification": "authenticated",
            "auth_scope": "devhub_account",
        }
    ]

    assert "private_or_authenticated_artifact" in _codes(packet)


def test_rejects_live_execution_or_promotion_claims():
    packet = _fixture("valid_packet.json")
    packet["operator_notes"] = "Promotion completed after the live execution run."

    assert "live_execution_or_promotion_claim" in _codes(packet)


def test_rejects_legal_or_permitting_outcome_guarantees():
    packet = _fixture("valid_packet.json")
    packet["recommendations"][0]["summary"] = "This will be approved by permitting staff."

    assert "legal_or_permitting_outcome_guarantee" in _codes(packet)


def test_rejects_consequential_action_language():
    packet = _fixture("valid_packet.json")
    packet["recommendations"][0]["summary"] = "Submit the permit after applying the patch."

    assert "consequential_action_language" in _codes(packet)


def test_rejects_active_forbidden_mutation_flags():
    packet = _fixture("valid_packet.json")
    packet["mutation_flags"] = {
        "source-registry": True,
        "guardrail": True,
        "prompt": True,
        "release-state": True,
        "agent-state": True,
    }

    assert "active_forbidden_mutation_flag" in _codes(packet)


def test_allows_inactive_forbidden_mutation_flags():
    packet = _fixture("valid_packet.json")
    packet["mutation_flags"] = {
        "source-registry": False,
        "guardrail": False,
        "prompt": False,
        "release-state": False,
        "agent-state": False,
    }

    assert validate_human_release_handoff_packet_v1(packet).valid is True
