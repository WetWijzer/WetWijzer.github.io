from pathlib import Path

from ppd.inactive_promotion_patch_preview_v1 import PREVIEW_VERSION, build_preview_from_files


FIXTURES = Path(__file__).parent / "fixtures" / "inactive_promotion_patch_preview_v1"


def test_preview_rows_are_deterministic_and_include_before_after_states() -> None:
    preview = build_preview_from_files(
        FIXTURES / "promotion_candidate_patch_plan_v1.json",
        FIXTURES / "inactive_fixture_families.json",
    )

    assert preview["preview_version"] == PREVIEW_VERSION
    assert preview["source_plan_id"] == "candidate_patch_plan_v1_fixture"
    assert [row["candidate_id"] for row in preview["preview_rows"]] == [
        "promote-electrical-ready",
        "promote-mechanical-blocked",
        "promote-plumbing-ready",
    ]

    ready_row = preview["preview_rows"][0]
    assert ready_row["preview_status"] == "ready_for_review"
    assert ready_row["before"]["active"] is False
    assert ready_row["after"]["active"] is True
    assert ready_row["after"]["would_promote"] is True
    assert ready_row["reviewer_signoff_required"] is True


def test_preview_reports_validation_inventory_blocked_rows_signoffs_and_rollbacks() -> None:
    preview = build_preview_from_files(
        FIXTURES / "promotion_candidate_patch_plan_v1.json",
        FIXTURES / "inactive_fixture_families.json",
    )

    assert preview["validation_inventory"] == {
        "candidate_count": 3,
        "ready_for_review_count": 2,
        "blocked_count": 1,
        "inactive_fixture_family_ids": ["trade-permit-inactive-fixtures"],
        "validation_refs": [
            "fixture-schema-v1",
            "inactive-family-manifest-v1",
            "promotion-candidate-plan-v1",
        ],
        "deterministic_order": "candidate_id,inactive_fixture_id",
    }

    assert preview["blocked_row_explanations"] == [
        {
            "candidate_id": "promote-mechanical-blocked",
            "inactive_fixture_id": "inactive-mechanical-fixture-v1",
            "reasons": [
                "candidate_missing_rollback_checkpoint",
                "candidate_validation_error:missing_required_document_fixture",
            ],
        }
    ]

    assert preview["reviewer_signoff_placeholders"] == [
        {
            "candidate_id": "promote-electrical-ready",
            "reviewer": "",
            "reviewed_at": "",
            "decision": "pending",
            "notes": "",
        },
        {
            "candidate_id": "promote-mechanical-blocked",
            "reviewer": "",
            "reviewed_at": "",
            "decision": "pending",
            "notes": "",
        },
        {
            "candidate_id": "promote-plumbing-ready",
            "reviewer": "",
            "reviewed_at": "",
            "decision": "pending",
            "notes": "",
        },
    ]

    assert preview["rollback_checkpoints"][0] == {
        "candidate_id": "promote-electrical-ready",
        "checkpoint_id": "rollback-electrical-ready",
        "restore_fixture_id": "inactive-electrical-fixture-v1",
        "restore_content_hash": "sha256:inactive-electrical-before",
        "rollback_status": "placeholder",
    }
    assert preview["side_effects"] == {
        "active_fixtures_edited": False,
        "prompts_edited": False,
        "process_models_edited": False,
        "guardrails_edited": False,
        "release_state_edited": False,
        "agent_state_edited": False,
    }
