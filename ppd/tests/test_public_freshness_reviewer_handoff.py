from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

from ppd.public_freshness_scheduler_rehearsal_v4_validation import (
    validate_public_freshness_scheduler_rehearsal_v4_safety,
)
from ppd.source_freshness.public_freshness_reviewer_handoff import (
    build_public_freshness_reviewer_handoff_v1,
    validate_public_freshness_reviewer_handoff_v1,
)

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "public_freshness_reviewer_handoff" / "input.json"
GENERATED_AT = "2026-05-30T01:00:00Z"


def _fixture() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _build_packet() -> dict:
    scheduler_packet = _fixture()["scheduler_rehearsal_v4_packet"]
    validation_outcome = validate_public_freshness_scheduler_rehearsal_v4_safety(scheduler_packet)
    return build_public_freshness_reviewer_handoff_v1(
        scheduler_packet,
        validation_outcome,
        generated_at=GENERATED_AT,
    )


def test_builds_cited_public_freshness_reviewer_handoff_rows() -> None:
    packet = _build_packet()

    result = validate_public_freshness_reviewer_handoff_v1(packet)

    assert result.valid is True
    assert packet["packet_type"] == "ppd.public_freshness_reviewer_handoff.v1"
    assert packet["mode"] == "fixture_first_public_freshness_reviewer_handoff"
    assert packet["execution_policy"] == {
        "network_allowed": False,
        "network_invoked": False,
        "fetch_urls": False,
        "recrawl_invoked": False,
        "download_documents": False,
        "processor_invoked": False,
        "source_registry_mutation_allowed": False,
        "registry_mutated": False,
        "schedule_mutated": False,
    }
    assert packet["source_ids"] == [
        "ppd-devhub-faq",
        "ppd-fee-payment-guide",
        "ppd-submit-plans-online",
    ]


def test_rows_include_owner_affected_ids_reasons_checks_and_attestations() -> None:
    packet = _build_packet()
    rows = {row["primary_source_id"]: row for row in packet["reviewer_handoff_rows"]}

    devhub = rows["ppd-devhub-faq"]
    assert devhub["reviewer_owner"] == "ppd-devhub-guidance-reviewer"
    assert devhub["affected_requirement_ids"] == ["REQ-DEVHUB-UPLOAD-GATE-002"]
    assert devhub["affected_process_ids"] == ["PROC-DEVHUB-CORRECTIONS"]
    assert devhub["citation_ids"] == ["cite-devhub-faq-guidance-20260530"]
    assert devhub["validation_outcome"] == {"scheduler_validation_ok": True, "related_error_codes": []}
    assert all(devhub["attestations"][key] is True for key in ("no_recrawl", "no_download", "no_processor", "no_registry_mutation"))
    assert "Confirm REQ-DEVHUB-UPLOAD-GATE-002" in devhub["proposed_offline_checks"][1]

    fee = rows["ppd-fee-payment-guide"]
    assert fee["row_kind"] == "skip_or_defer"
    assert fee["reviewer_owner"] == "ppd-financial-action-reviewer"
    assert fee["stale_or_defer_reasons"][0]["reason_id"].startswith("source-row-reason-")


def test_validation_outcome_errors_become_review_reasons_without_private_url_leakage() -> None:
    scheduler_packet = deepcopy(_fixture()["scheduler_rehearsal_v4_packet"])
    scheduler_packet["cited_metadata_only_recrawl_schedule_candidates"][0]["canonical_url"] = "https://devhub.portlandoregon.gov/account/my-permits?token=secret"
    validation_outcome = validate_public_freshness_scheduler_rehearsal_v4_safety(scheduler_packet)

    packet = build_public_freshness_reviewer_handoff_v1(
        scheduler_packet,
        validation_outcome,
        generated_at=GENERATED_AT,
    )
    result = validate_public_freshness_reviewer_handoff_v1(packet)
    devhub = {row["primary_source_id"]: row for row in packet["reviewer_handoff_rows"]}["ppd-devhub-faq"]

    assert validation_outcome["ok"] is False
    assert result.valid is True
    assert devhub["canonical_url"] == ""
    assert devhub["validation_outcome"]["scheduler_validation_ok"] is False
    assert "authenticated_url" in devhub["validation_outcome"]["related_error_codes"]
    assert any(reason["reason_id"] == "scheduler-validation-authenticated-url" for reason in devhub["stale_or_defer_reasons"])


def test_validation_rejects_missing_attestation() -> None:
    packet = _build_packet()
    packet["reviewer_handoff_rows"][0]["attestations"]["no_processor"] = False

    result = validate_public_freshness_reviewer_handoff_v1(packet)

    assert result.valid is False
    assert "reviewer_handoff_rows[0].attestations.no_processor must be true" in result.errors
