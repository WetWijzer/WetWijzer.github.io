from __future__ import annotations

import json
from pathlib import Path

from ppd.crawler.live_dry_run_acceptance_review_v2 import (
    packet_v2_is_accepted,
    validate_acceptance_review_packet_v2,
)


FIXTURES = Path(__file__).parent / "fixtures"


def test_acceptance_review_packet_v2_rejects_required_blockers() -> None:
    packet = json.loads((FIXTURES / "live_dry_run_acceptance_review_v2_rejected_packet.json").read_text())

    codes = {violation.code for violation in validate_acceptance_review_packet_v2(packet)}

    assert "uncited_observation_decision" in codes
    assert "missing_observation_rationale" in codes
    assert "missing_review_rationale" in codes
    assert "missing_packet_rationale" in codes
    assert "missing_reviewer_owner" in codes
    assert "unresolved_disposition" in codes
    assert "private_or_authenticated_fact" in codes
    assert "raw_artifact_reference" in codes
    assert "live_execution_claim" in codes
    assert "credential_or_challenge_automation" in codes
    assert "legal_or_permitting_guarantee" in codes
    assert "final_consequential_action" in codes
    assert "active_mutation_flag" in codes
    assert not packet_v2_is_accepted(packet)


def test_acceptance_review_packet_v2_accepts_cited_commit_safe_packet() -> None:
    packet = {
        "version": "live-dry-run-acceptance-review-packet-v2",
        "decision": "accepted",
        "rationale": "All observations are from public cited guidance and no live action was performed.",
        "reviewer_owners": ["ppd-review-owner"],
        "observation_decisions": [
            {
                "id": "obs-public-guide",
                "decision": "accepted",
                "rationale": "The observation is limited to public guidance text.",
                "source_evidence_ids": ["public-source-001"],
            }
        ],
        "review_decisions": [
            {
                "id": "review-safe",
                "decision": "accepted",
                "rationale": "The packet is a deterministic dry-run review artifact.",
            }
        ],
        "incident_dispositions": [
            {"id": "incident-none", "disposition": "resolved-no-incident"}
        ],
        "abort_dispositions": [
            {"id": "abort-none", "disposition": "resolved-no-abort"}
        ],
        "mutation_flags": [
            {"scope": "guardrail", "active": False},
            {"scope": "source_registry", "enabled": False},
        ],
        "notes": [
            "Dry-run review only; stores normalized public citations and commit-safe metadata."
        ],
    }

    assert validate_acceptance_review_packet_v2(packet) == []
    assert packet_v2_is_accepted(packet)
