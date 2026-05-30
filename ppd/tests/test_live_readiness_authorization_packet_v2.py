from __future__ import annotations

import json
from pathlib import Path

from ppd.devhub.live_readiness_authorization_packet_v2 import (
    validate_live_readiness_authorization_packet_v2,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "live_readiness_authorization_packet_v2"


def _load_packet(name: str) -> dict:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def test_live_readiness_authorization_packet_v2_accepts_commit_safe_packet() -> None:
    result = validate_live_readiness_authorization_packet_v2(_load_packet("valid_packet.json"))

    assert result.ok
    assert result.issues == ()


def test_live_readiness_authorization_packet_v2_rejects_blocked_readiness_content() -> None:
    result = validate_live_readiness_authorization_packet_v2(_load_packet("invalid_packet.json"))

    assert not result.ok
    assert set(result.error_codes()) >= {
        "prerequisite_uncited",
        "reviewer_signoff_incomplete",
        "operator_signoff_missing",
        "fixture_gaps_unresolved",
        "private_or_authenticated_fact",
        "session_or_auth_artifact",
        "browser_artifact_reference",
        "live_execution_claim",
        "blocked_credential_or_challenge_automation",
        "legal_or_permitting_outcome_guarantee",
        "official_action_enablement",
        "active_mutation_flag",
    }
