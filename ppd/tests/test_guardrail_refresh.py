from ppd.validation.guardrail_refresh import (
    affected_guardrail_bundles,
    is_high_risk_requirement_delta,
    validate_guardrail_refresh,
)


def test_high_risk_delta_detection_covers_named_categories():
    assert is_high_risk_requirement_delta({"type": "fees"})
    assert is_high_risk_requirement_delta({"categories": ["upload_rules"]})
    assert is_high_risk_requirement_delta({"delta_type": "devhub_action_gates"})
    assert not is_high_risk_requirement_delta({"type": "copy_edit"})


def test_affected_guardrail_bundles_accepts_supported_field_names():
    assert affected_guardrail_bundles({"affected_guardrail_bundles": ["bundle-a"]}) == ("bundle-a",)
    assert affected_guardrail_bundles({"guardrail_bundles": "bundle-b"}) == ("bundle-b",)
    assert affected_guardrail_bundles({"affected_bundles": ["bundle-c"]}) == ("bundle-c",)


def test_unblocked_affected_bundle_without_refreshed_process_model_evidence_fails():
    result = validate_guardrail_refresh(
        requirement_deltas=[
            {
                "id": "delta-fee-1",
                "type": "fees",
                "affected_guardrail_bundles": ["residential-permit-intake"],
            }
        ],
        guardrail_bundles=[{"id": "residential-permit-intake", "state": "ready"}],
        evidence_records=[],
    )

    assert not result.ok
    assert result.findings[0].bundle_id == "residential-permit-intake"
    assert result.findings[0].delta_id == "delta-fee-1"


def test_blocked_affected_bundle_without_refreshed_process_model_evidence_passes():
    result = validate_guardrail_refresh(
        requirement_deltas=[
            {
                "id": "delta-docs-1",
                "type": "required_documents",
                "affected_guardrail_bundles": ["trade-permit-documents"],
            }
        ],
        guardrail_bundles=[{"id": "trade-permit-documents", "state": "blocked"}],
        evidence_records=[],
    )

    assert result.ok
    assert result.findings == ()


def test_unblocked_affected_bundle_with_refreshed_process_model_evidence_passes():
    result = validate_guardrail_refresh(
        requirement_deltas=[
            {
                "id": "delta-deadline-1",
                "type": "deadlines",
                "affected_guardrail_bundles": ["commercial-review-clock"],
            }
        ],
        guardrail_bundles=[{"id": "commercial-review-clock", "state": "ready"}],
        evidence_records=[
            {
                "kind": "process_model_refresh",
                "status": "verified",
                "guardrail_bundles": ["commercial-review-clock"],
                "requirement_delta_ids": ["delta-deadline-1"],
                "source": "ppd/tests/fixtures/process-model/commercial-review-clock.json",
                "refreshed_at": "2026-05-27T00:00:00Z",
            }
        ],
    )

    assert result.ok
    assert result.findings == ()
