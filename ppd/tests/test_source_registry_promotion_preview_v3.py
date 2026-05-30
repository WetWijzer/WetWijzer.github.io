from pathlib import Path

from ppd.source_registry_promotion_preview_v3 import (
    is_public_source_registry_promotion_preview_v3_valid,
    validate_public_source_registry_promotion_preview_v3,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "source_registry_promotion_preview_v3"


def _valid_preview():
    return {
        "preview_version": "v3",
        "patch_candidates": [
            {
                "patch_id": "patch-001",
                "citations": ["source:ppd-devhub-faq#account-services"],
                "before_metadata": {"freshness_status": "stale"},
                "after_metadata": {"freshness_status": "current"},
                "affected_source_ids": ["source:ppd-devhub-faq"],
                "affected_requirement_ids": ["requirement:devhub-account-services"],
                "canonical_url": "https://www.portland.gov/ppd/devhub-faqs",
                "notes": "Metadata-only preview; no live crawl or processor completion is claimed.",
            }
        ],
        "dependency_order": ["patch-001"],
        "rollback_checkpoints": [{"patch_id": "patch-001", "checkpoint_id": "rollback-001"}],
    }


def test_valid_preview_has_no_errors():
    preview = _valid_preview()

    assert validate_public_source_registry_promotion_preview_v3(preview) == []
    assert is_public_source_registry_promotion_preview_v3_valid(preview) is True


def test_rejects_uncited_and_under_specified_patch_candidate():
    preview = {
        "preview_version": "v3",
        "patch_candidates": [{"patch_id": "patch-001"}],
    }

    errors = validate_public_source_registry_promotion_preview_v3(preview)

    assert "patch_candidates[0].citations: uncited patch candidates are rejected" in errors
    assert "patch_candidates[0].before_metadata: before metadata is required" in errors
    assert "patch_candidates[0].after_metadata: after metadata is required" in errors
    assert "patch_candidates[0].affected_source_ids: at least one affected source id is required" in errors
    assert "patch_candidates[0].affected_requirement_ids: at least one affected requirement id is required" in errors
    assert "dependency_order: dependency order is required" in errors
    assert "rollback_checkpoints: rollback checkpoints are required" in errors


def test_rejects_non_allowlisted_and_authenticated_urls():
    preview = _valid_preview()
    patch = preview["patch_candidates"][0]
    patch["canonical_url"] = "https://example.com/ppd"
    patch["source_url"] = "https://token@example.com/private"
    patch["help_url"] = "https://www.portland.gov/ppd/devhub-faqs?token=secret"

    errors = validate_public_source_registry_promotion_preview_v3(preview)

    assert "patch_candidates[0].canonical_url: non-allowlisted URL is rejected" in errors
    assert "patch_candidates[0].source_url: non-allowlisted URL is rejected" in errors
    assert "patch_candidates[0].help_url: authenticated URL is rejected" in errors


def test_rejects_missing_order_and_rollback_for_patch_ids():
    preview = _valid_preview()
    preview["dependency_order"] = ["another-patch"]
    preview["rollback_checkpoints"] = [{"patch_id": "another-patch"}]

    errors = validate_public_source_registry_promotion_preview_v3(preview)

    assert "dependency_order: missing patch id patch-001" in errors
    assert "rollback_checkpoints: missing rollback checkpoint for patch id patch-001" in errors


def test_rejects_artifacts_completion_claims_guarantees_and_mutation_flags():
    preview = _valid_preview()
    patch = preview["patch_candidates"][0]
    patch.update(
        {
            "raw_body": "raw",
            "download_path": "/tmp/form.pdf",
            "browser_trace": "trace.zip",
            "live_crawl_completed": True,
            "summary": "The processor completed and the permit will be approved.",
            "source_mutation_enabled": True,
            "schedule_update_active": True,
            "requirement_patch_active": True,
            "process_mutation_enabled": True,
            "guardrail_update_active": True,
            "prompt_update_active": True,
            "monitoring_update_active": True,
            "release_state_mutation_enabled": True,
            "agent_state_mutation_enabled": True,
        }
    )

    errors = validate_public_source_registry_promotion_preview_v3(preview)

    assert "patch_candidates[0].raw_body: raw body, download, archive, and browser artifacts are rejected" in errors
    assert "patch_candidates[0].download_path: raw body, download, archive, and browser artifacts are rejected" in errors
    assert "patch_candidates[0].browser_trace: raw body, download, archive, and browser artifacts are rejected" in errors
    assert "patch_candidates[0].live_crawl_completed: live crawler or processor completion claims are rejected" in errors
    assert "patch_candidates[0].summary: live crawler or processor completion claims are rejected" in errors
    assert "patch_candidates[0].summary: legal or permitting outcome guarantees are rejected" in errors
    assert "patch_candidates[0].source_mutation_enabled: active registry, process, guardrail, prompt, monitoring, release-state, or agent-state mutation flags are rejected" in errors
    assert "patch_candidates[0].schedule_update_active: active registry, process, guardrail, prompt, monitoring, release-state, or agent-state mutation flags are rejected" in errors
    assert "patch_candidates[0].requirement_patch_active: active registry, process, guardrail, prompt, monitoring, release-state, or agent-state mutation flags are rejected" in errors
    assert "patch_candidates[0].process_mutation_enabled: active registry, process, guardrail, prompt, monitoring, release-state, or agent-state mutation flags are rejected" in errors
    assert "patch_candidates[0].guardrail_update_active: active registry, process, guardrail, prompt, monitoring, release-state, or agent-state mutation flags are rejected" in errors
    assert "patch_candidates[0].prompt_update_active: active registry, process, guardrail, prompt, monitoring, release-state, or agent-state mutation flags are rejected" in errors
    assert "patch_candidates[0].monitoring_update_active: active registry, process, guardrail, prompt, monitoring, release-state, or agent-state mutation flags are rejected" in errors
    assert "patch_candidates[0].release_state_mutation_enabled: active registry, process, guardrail, prompt, monitoring, release-state, or agent-state mutation flags are rejected" in errors
    assert "patch_candidates[0].agent_state_mutation_enabled: active registry, process, guardrail, prompt, monitoring, release-state, or agent-state mutation flags are rejected" in errors


def test_fixture_directory_reference_is_local_to_ppd_tests():
    assert FIXTURE_DIR == Path(__file__).parent / "fixtures" / "source_registry_promotion_preview_v3"
