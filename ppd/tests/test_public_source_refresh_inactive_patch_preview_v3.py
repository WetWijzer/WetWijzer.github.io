from __future__ import annotations

import copy

from ppd.validation.public_source_refresh_inactive_patch_preview_v3 import (
    validate_inactive_patch_preview_v3,
)


def _valid_preview() -> dict:
    return {
        "preview_version": 3,
        "state": "inactive_patch_preview",
        "rows": [
            {
                "row_id": "row-1",
                "before": {"text": "existing cited requirement"},
                "after": {"text": "preview-only cited requirement"},
                "source_evidence": [
                    {
                        "summary": "public page supports the preview row",
                        "citation": {"source_id": "public-source-1", "locator": "section 1"},
                    }
                ],
                "citation_preservation_check": "existing citations remain attached to unchanged text",
                "affected_requirement": "req-public-source-refresh",
                "affected_process": "process-preview-validation",
                "affected_guardrail": "guardrail-inactive-only",
            }
        ],
        "blocked_rows": [
            {"row_id": "blocked-1", "explanation": "missing public citation, therefore excluded"}
        ],
        "validation_inventory": {
            "sources": ["public-source-1"],
            "documents": ["doc-1"],
            "requirements": ["req-public-source-refresh"],
            "processes": ["process-preview-validation"],
            "guardrails": ["guardrail-inactive-only"],
        },
        "active_source_mutation": False,
        "document_mutation": False,
        "requirement_mutation": False,
        "process_mutation": False,
        "guardrail_mutation": False,
        "release_state_mutation": False,
        "agent_state_mutation": False,
    }


def test_valid_preview_passes() -> None:
    result = validate_inactive_patch_preview_v3(_valid_preview())

    assert result.ok
    assert result.errors == ()


def test_rejects_missing_required_row_evidence_and_references() -> None:
    preview = _valid_preview()
    preview["rows"] = [
        {
            "row_id": "row-1",
            "source_evidence": [{"summary": "uncited evidence"}],
        }
    ]

    result = validate_inactive_patch_preview_v3(preview)

    assert not result.ok
    assert "rows[0] is missing before" in result.errors
    assert "rows[0] is missing after" in result.errors
    assert "rows[0] has uncited source_evidence" in result.errors
    assert "rows[0] is missing citation_preservation_check" in result.errors
    assert "rows[0] is missing affected_requirement" in result.errors
    assert "rows[0] is missing affected_process" in result.errors
    assert "rows[0] is missing affected_guardrail" in result.errors


def test_rejects_missing_blocked_rows_and_validation_inventory() -> None:
    preview = _valid_preview()
    preview["blocked_rows"] = []
    preview["validation_inventory"] = {"sources": []}

    result = validate_inactive_patch_preview_v3(preview)

    assert not result.ok
    assert "blocked_rows must explain every blocked row" in result.errors
    assert "validation_inventory.sources must be non-empty" in result.errors
    assert "validation_inventory.documents must be non-empty" in result.errors
    assert "validation_inventory.requirements must be non-empty" in result.errors
    assert "validation_inventory.processes must be non-empty" in result.errors
    assert "validation_inventory.guardrails must be non-empty" in result.errors


def test_rejects_forbidden_artifacts_claims_actions_and_mutations() -> None:
    preview = copy.deepcopy(_valid_preview())
    preview["rows"][0]["after"]["text"] = "raw crawl says permit approved and you should submit"
    preview["document_mutation"] = True

    result = validate_inactive_patch_preview_v3(preview)

    assert not result.ok
    assert "document_mutation must be false" in result.errors
    assert "forbidden content marker present: raw crawl" in result.errors
    assert "forbidden content marker present: permit approved" in result.errors
    assert "forbidden content marker present: you should submit" in result.errors
