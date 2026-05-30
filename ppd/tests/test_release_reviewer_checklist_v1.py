from __future__ import annotations

import json
from pathlib import Path

from ppd.release_review.checklist_v1 import validate_release_reviewer_go_no_go_checklist_v1


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "release_review"


def load_valid_checklist() -> dict:
    return json.loads((FIXTURE_DIR / "checklist_v1_valid.json").read_text(encoding="utf-8"))


def finding_codes(checklist: dict) -> set[str]:
    return {finding.code for finding in validate_release_reviewer_go_no_go_checklist_v1(checklist)}


def test_valid_release_reviewer_checklist_v1_has_no_findings() -> None:
    assert validate_release_reviewer_go_no_go_checklist_v1(load_valid_checklist()) == []


def test_rejects_missing_checklist_item_and_evidence_coverage() -> None:
    checklist = load_valid_checklist()
    checklist["checklist_items"].pop("private-artifact-review")
    checklist["evidence_citation_coverage"] = [
        row for row in checklist["evidence_citation_coverage"] if row["checklist_item_id"] != "private-artifact-review"
    ]

    codes = finding_codes(checklist)

    assert "missing-checklist-item" in codes
    assert "missing-evidence-coverage" in codes


def test_rejects_missing_release_readiness_confirmations_and_commands() -> None:
    checklist = load_valid_checklist()
    for field in (
        "rollback_owner_confirmed",
        "rollback_steps_confirmed",
        "rollback_stop_condition_confirmed",
        "validation_replay_owner_confirmed",
        "validation_replay_inputs_confirmed",
        "validation_replay_expected_results_confirmed",
        "unresolved_risks_acknowledged",
        "unresolved_risk_owner_placeholder",
        "unresolved_risk_followup_placeholder",
    ):
        checklist[field] = False
    checklist["validation_commands"] = []

    codes = finding_codes(checklist)

    assert "missing-rollback-confirmation" in codes
    assert "missing-validation-replay-confirmation" in codes
    assert "missing-unresolved-risk-placeholder" in codes
    assert "missing-validation-command" in codes


def test_rejects_private_browser_auth_and_raw_data_artifacts() -> None:
    checklist = load_valid_checklist()
    checklist["artifacts"] = [
        {"path": "ppd/.auth/storage-state.json"},
        {"path": "ppd/traces/devhub.trace.zip"},
        {"path": "ppd/screenshots/review.png"},
        {"path": "ppd/tests/fixtures/raw/public-page.html"},
        {"path": "ppd/downloads/source.pdf"},
    ]

    codes = finding_codes(checklist)

    assert "private-or-browser-artifact" in codes
    assert "raw-crawl-or-download-artifact" in codes


def test_rejects_live_release_claims_guarantees_and_consequential_language() -> None:
    checklist = load_valid_checklist()
    checklist["claims"] = [
        "The live crawl executed and the release is complete.",
        "This guarantees the permit will be approved.",
        "Submit the permit request and pay fee now.",
    ]

    codes = finding_codes(checklist)

    assert "live-execution-or-release-complete-claim" in codes
    assert "legal-or-permitting-guarantee" in codes
    assert "consequential-action-language" in codes


def test_rejects_active_mutation_flags() -> None:
    checklist = load_valid_checklist()
    checklist["artifact_mutation_enabled"] = True
    checklist["prompt_mutation_enabled"] = True
    checklist["release_state_mutation_enabled"] = True
    checklist["fixture_mutation_enabled"] = True
    checklist["agent_state_mutation_enabled"] = True

    codes = finding_codes(checklist)

    assert codes == {"active-mutation-flag"}
