import copy
import json
from pathlib import Path

from ppd.contracts.devhub_post_action_review import review_from_dict

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "devhub" / "post_action_hardening_review_safe_draft.json"


def _fixture_data():
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def test_safe_draft_post_action_hardening_review_fixture_is_valid():
    review = review_from_dict(_fixture_data())

    assert review.validate() == []


def test_review_requires_completion_evidence_for_completed_safe_actions():
    data = _fixture_data()
    data["completionEvidence"] = [
        item for item in data["completionEvidence"] if item["actionId"] != "save_draft_before_submission"
    ]

    errors = review_from_dict(data).validate()

    assert any("completion evidence missing" in error for error in errors)


def test_review_requires_refused_evidence_for_consequential_controls():
    data = _fixture_data()
    data["refusedActionEvidence"] = [
        item for item in data["refusedActionEvidence"] if item["controlId"] != "submit_payment"
    ]

    errors = review_from_dict(data).validate()

    assert any("refused-action evidence missing" in error and "submit_payment" in error for error in errors)


def test_review_rejects_unredacted_journal_and_private_browser_artifacts():
    data = _fixture_data()
    data["journalEvents"][0]["redactionStatus"] = "raw"
    data["journalEvents"][0]["payload"]["trace"] = "devhub-trace.zip"
    data["browserArtifacts"] = {"storageState": "ppd/private/storage-state.json"}

    errors = review_from_dict(data).validate()

    assert any("must be redacted" in error for error in errors)
    assert any("forbidden private browser artifact key" in error for error in errors)
    assert any("browser_artifacts must be empty" in error for error in errors)


def test_review_rejects_consequential_action_as_attempted_action():
    data = _fixture_data()
    mutated = copy.deepcopy(data["attemptedActions"][0])
    mutated["actionId"] = "submit_permit_request"
    mutated["actionClass"] = "consequential_official"
    data["attemptedActions"].append(mutated)

    errors = review_from_dict(data).validate()

    assert any("must be safe read-only or reversible draft" in error for error in errors)
