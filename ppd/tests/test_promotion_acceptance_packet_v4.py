from __future__ import annotations

from pathlib import Path

import pytest

from ppd.promotion_acceptance_packet_v4 import (
    OFFLINE_VALIDATION_COMMANDS,
    PACKET_VERSION,
    REQUIRED_ATTESTATIONS,
    PromotionAcceptancePacketV4Error,
    build_packet_from_manifest,
    validate_packet,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "promotion_acceptance_packet_v4"
MANIFEST = FIXTURE_DIR / "input_manifest.json"


def test_builds_fixture_first_promotion_acceptance_packet_v4() -> None:
    packet = build_packet_from_manifest(MANIFEST)

    assert packet["packet_version"] == PACKET_VERSION
    assert packet["mode"] == "fixture_first_promotion_acceptance_only"
    assert packet["manifest_id"] == "promotion-acceptance-packet-v4-inputs-20260530"
    assert packet["consumes"] == {
        "public_freshness_scheduler_rehearsal_v4": "ppd.public_freshness_scheduler_rehearsal.v4",
        "reversible_draft_preview_handoff_packet_v4": "draft-preview-agent-handoff-packet-v4",
        "guardrail_fixtures": "guardrail-bundle-fixtures-v1",
        "process_model_fixtures": "process-model-fixtures-v1",
    }
    assert packet["attestations"] == {key: True for key in REQUIRED_ATTESTATIONS}
    assert validate_packet(packet) == []


def test_acceptance_criteria_are_cited_and_reviewer_ready() -> None:
    packet = build_packet_from_manifest(MANIFEST)
    criteria = packet["reviewer_ready_acceptance_criteria"]

    assert [criterion["criterion_id"] for criterion in criteria] == [
        "freshness-scheduler-output-cited",
        "draft-preview-handoff-output-cited",
        "guardrail-process-boundary-aligned",
        "rollback-and-diff-review-ready",
    ]
    assert all(criterion["ready_for_review"] is True for criterion in criteria)
    assert all(criterion["reviewer_owner"] for criterion in criteria)
    assert all(criterion["citation_ids"] for criterion in criteria)
    assert any("watch-plan-v3:portland-zoning-code" in criterion["citation_ids"] for criterion in criteria)
    assert any("guardrail-bundle-fixtures-v1" in criterion["citation_ids"] for criterion in criteria)
    assert any("process-model-fixtures-v1" in criterion["citation_ids"] for criterion in criteria)


def test_dependency_order_rollback_checkpoints_fixture_diffs_and_commands_are_present() -> None:
    packet = build_packet_from_manifest(MANIFEST)

    assert [step["step_id"] for step in packet["dependency_order"]] == [
        "read-public-freshness-scheduler-rehearsal-v4",
        "read-reversible-draft-preview-handoff-v4",
        "cross-check-guardrail-and-process-fixtures",
        "review-acceptance-criteria-and-fixture-diffs",
    ]
    assert packet["dependency_order"][1]["depends_on"] == ["read-public-freshness-scheduler-rehearsal-v4"]
    assert all(step["offline_only"] is True for step in packet["dependency_order"])

    assert len(packet["rollback_checkpoints"]) == 2
    assert all(checkpoint["requires_reviewer_confirmation"] is True for checkpoint in packet["rollback_checkpoints"])
    assert all(checkpoint["active_state_mutation_allowed"] is False for checkpoint in packet["rollback_checkpoints"])

    assert len(packet["expected_fixture_diffs"]) == 3
    assert all(diff["fixture_path"].startswith("ppd/tests/fixtures/") for diff in packet["expected_fixture_diffs"])
    assert all(diff["live_artifact_expected"] is False for diff in packet["expected_fixture_diffs"])

    assert packet["offline_validation_commands"] == OFFLINE_VALIDATION_COMMANDS
    assert ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"] in packet["offline_validation_commands"]


def test_validation_rejects_missing_attestations_out_of_order_dependencies_and_live_artifacts() -> None:
    packet = build_packet_from_manifest(MANIFEST)

    broken_attestation = dict(packet)
    broken_attestation["attestations"] = dict(packet["attestations"])
    broken_attestation["attestations"]["no_devhub"] = False
    assert "attestations.no_devhub must be true" in validate_packet(broken_attestation)

    broken_order = dict(packet)
    steps = list(packet["dependency_order"])
    broken_order["dependency_order"] = [steps[1], steps[0], steps[2], steps[3]]
    assert any("dependency is missing or out of order" in error for error in validate_packet(broken_order))

    broken_diff = dict(packet)
    broken_diff["expected_fixture_diffs"] = [dict(packet["expected_fixture_diffs"][0], fixture_path="private/output.json")]
    assert "expected_fixture_diffs[0].fixture_path must stay under ppd/tests/fixtures" in validate_packet(broken_diff)

    private_packet = dict(packet)
    private_packet["private_artifact"] = "session data"
    assert any("private, authenticated, browser, session, raw crawl, or PDF artifacts" in error for error in validate_packet(private_packet))

    mutation_packet = dict(packet)
    mutation_packet["active_state_mutation"] = True
    assert any("active mutation flags" in error for error in validate_packet(mutation_packet))


def test_validation_rejects_uncited_criteria_missing_order_diffs_and_rollbacks() -> None:
    packet = build_packet_from_manifest(MANIFEST)

    uncited = dict(packet)
    criteria = [dict(item) for item in packet["reviewer_ready_acceptance_criteria"]]
    criteria[0]["citation_ids"] = []
    uncited["reviewer_ready_acceptance_criteria"] = criteria
    assert "reviewer_ready_acceptance_criteria[0].citation_ids must be non-empty" in validate_packet(uncited)

    missing_dependency = dict(packet)
    steps = [dict(item) for item in packet["dependency_order"]]
    steps[1]["depends_on"] = []
    missing_dependency["dependency_order"] = steps
    assert "dependency_order[1].depends_on must include a prior step" in validate_packet(missing_dependency)

    missing_diffs = dict(packet)
    missing_diffs["expected_fixture_diffs"] = []
    assert "expected_fixture_diffs must be non-empty" in validate_packet(missing_diffs)

    missing_rollbacks = dict(packet)
    missing_rollbacks["rollback_checkpoints"] = []
    assert "rollback_checkpoints must be non-empty" in validate_packet(missing_rollbacks)


def test_validation_rejects_private_authenticated_raw_browser_and_session_artifacts() -> None:
    packet = build_packet_from_manifest(MANIFEST)

    rejected_keys = [
        "authenticated_fact",
        "auth_token",
        "browser_storage",
        "downloaded_document",
        "raw_crawl_output",
        "raw_pdf",
        "screenshot",
        "session_state",
    ]
    for key in rejected_keys:
        mutated = dict(packet)
        mutated[key] = "unsafe"
        errors = validate_packet(mutated)
        assert any("private, authenticated, browser, session, raw crawl, or PDF artifacts" in error for error in errors), key


def test_validation_rejects_live_execution_promotion_claims_guarantees_and_consequential_language() -> None:
    packet = build_packet_from_manifest(MANIFEST)

    forbidden_texts = [
        "live execution completed",
        "promoted to production",
        "permit approval guaranteed",
        "submit permit now",
        "upload corrections to the official record",
        "schedule inspection from DevHub",
        "pay fees in the payment flow",
    ]
    for text in forbidden_texts:
        mutated = dict(packet)
        mutated["unsafe_reviewer_note"] = text
        errors = validate_packet(mutated)
        assert any("forbidden claim or consequential action language" in error for error in errors), text


def test_validation_rejects_active_registry_guardrail_prompt_release_and_agent_state_mutation_flags() -> None:
    packet = build_packet_from_manifest(MANIFEST)

    rejected_flags = [
        "active_source_registry_mutation",
        "active_surface_registry_mutation",
        "active_guardrail_mutation",
        "active_prompt_mutation",
        "active_release_state_mutation",
        "active_agent_state_mutation",
    ]
    for key in rejected_flags:
        mutated = dict(packet)
        mutated[key] = True
        assert any("active mutation flags" in error for error in validate_packet(mutated)), key


def test_builder_requires_all_consumed_packet_families() -> None:
    packet = build_packet_from_manifest(MANIFEST)
    bad_packet = dict(packet)
    bad_packet["packet_version"] = "wrong"

    with pytest.raises(PromotionAcceptancePacketV4Error, match="invalid promotion acceptance packet v4"):
        from ppd.promotion_acceptance_packet_v4 import require_packet

        require_packet(bad_packet)


def test_packet_contains_no_private_or_live_runtime_artifacts() -> None:
    packet = build_packet_from_manifest(MANIFEST)
    serialized = repr(packet).lower()

    assert "session_cookie" not in serialized
    assert "auth_state" not in serialized
    assert "raw_html" not in serialized
    assert "raw_pdf" not in serialized
    assert "downloaded_document" not in serialized
    assert "no_live_crawl" in serialized
    assert "no_devhub" in serialized
    assert "no_private_artifact" in serialized
    assert "no_official_action" in serialized
    assert "no_active_state_mutation" in serialized


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__]))
