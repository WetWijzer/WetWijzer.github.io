from __future__ import annotations

from copy import deepcopy

from ppd.validation.public_recrawl_evidence_v2 import validate_public_recrawl_dry_run_evidence_v2


def valid_envelope() -> dict:
    return {
        "schema_version": "public-recrawl-dry-run-evidence-v2",
        "url_allowlist": ["https://www.portland.gov"],
        "citations": [
            {
                "id": "c1",
                "url": "https://www.portland.gov/bds/permits",
                "title": "Permits",
            }
        ],
        "decisions": {
            "robots": {"decision": "checked", "reason": "Dry-run fixture records robots review."},
            "rate_limit": {"decision": "not_applicable", "reason": "No live request is made."},
            "skip": {"decision": "dry_run_only", "reason": "Validation only."},
        },
        "observations": [
            {
                "text": "The cited public page is included only as deterministic dry-run evidence.",
                "citation_ids": ["c1"],
            }
        ],
        "mutation_flags": {
            "active_source_mutation": False,
            "schedule_mutation": False,
            "requirement_mutation": False,
            "process_mutation": False,
            "guardrail_mutation": False,
            "prompt_mutation": False,
            "monitoring_mutation": False,
            "release_state_mutation": False,
            "agent_state_mutation": False,
        },
    }


def test_valid_public_recrawl_dry_run_evidence_v2_passes() -> None:
    result = validate_public_recrawl_dry_run_evidence_v2(valid_envelope())
    assert result.ok, result.errors


def test_rejects_uncited_observation() -> None:
    envelope = valid_envelope()
    envelope["observations"][0].pop("citation_ids")
    result = validate_public_recrawl_dry_run_evidence_v2(envelope)
    assert not result.ok
    assert any("citation_ids" in error for error in result.errors)


def test_rejects_non_allowlisted_and_authenticated_urls() -> None:
    envelope = valid_envelope()
    envelope["citations"] = [
        {"id": "c1", "url": "https://user:secret@example.com/private"},
        {"id": "c2", "url": "https://www.portland.gov/bds?token=secret"},
    ]
    envelope["observations"][0]["citation_ids"] = ["c1"]
    result = validate_public_recrawl_dry_run_evidence_v2(envelope)
    assert not result.ok
    assert any("not allowlisted" in error for error in result.errors)
    assert any("authentication material" in error for error in result.errors)


def test_rejects_missing_safety_decisions() -> None:
    envelope = valid_envelope()
    envelope["decisions"].pop("robots")
    envelope["decisions"]["rate_limit"] = {"decision": "checked"}
    result = validate_public_recrawl_dry_run_evidence_v2(envelope)
    assert not result.ok
    assert any("decisions.robots" in error for error in result.errors)
    assert any("decisions.rate_limit.reason" in error for error in result.errors)


def test_rejects_raw_body_download_and_archive_references() -> None:
    envelope = valid_envelope()
    envelope["raw_body"] = ""
    envelope["evidence_files"] = [{"download_path": "/tmp/file.pdf", "archive_url": "https://archive.example/item"}]
    result = validate_public_recrawl_dry_run_evidence_v2(envelope)
    assert not result.ok
    assert any("raw_body" in error for error in result.errors)
    assert any("download_path" in error for error in result.errors)
    assert any("archive_url" in error for error in result.errors)


def test_rejects_completion_and_outcome_claims() -> None:
    envelope = valid_envelope()
    envelope["observations"][0]["text"] = "The live crawler completed and permit approval is guaranteed."
    result = validate_public_recrawl_dry_run_evidence_v2(envelope)
    assert not result.ok
    assert any("prohibited completion" in error for error in result.errors)


def test_rejects_active_mutation_flags() -> None:
    for flag in (
        "active_source_mutation",
        "schedule_mutation",
        "requirement_mutation",
        "process_mutation",
        "guardrail_mutation",
        "prompt_mutation",
        "monitoring_mutation",
        "release_state_mutation",
        "agent_state_mutation",
    ):
        envelope = deepcopy(valid_envelope())
        envelope["mutation_flags"][flag] = True
        result = validate_public_recrawl_dry_run_evidence_v2(envelope)
        assert not result.ok
        assert any(flag in error for error in result.errors)
