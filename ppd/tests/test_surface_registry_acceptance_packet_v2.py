import json
from pathlib import Path

from ppd.validation.surface_registry_acceptance_packet_v2 import validate_surface_registry_acceptance_packet_v2

FIXTURES = Path(__file__).parent / "fixtures" / "surface_registry_acceptance_packet_v2"


def load_fixture(name: str):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def test_valid_acceptance_packet_v2_passes():
    assert validate_surface_registry_acceptance_packet_v2(load_fixture("valid.json")) == []


def test_invalid_acceptance_packet_v2_rejects_required_hazards():
    errors = set(validate_surface_registry_acceptance_packet_v2(load_fixture("invalid_all_hazards.json")))
    expected = {
        "uncited_acceptance_decision",
        "missing_accepted_rationale",
        "missing_deferred_rationale",
        "missing_rejected_rationale",
        "missing_selector_confidence_disposition",
        "missing_manual_handoff_disposition",
        "missing_redaction_gates",
        "missing_rollback_notes",
        "private_or_authenticated_value",
        "session_auth_or_browser_artifact_reference",
        "live_devhub_or_browser_execution_claim",
        "legal_or_permitting_outcome_guarantee",
        "consequential_action_enablement",
        "active_mutation_flag",
    }
    assert expected <= errors
