from __future__ import annotations

import json
from pathlib import Path

from ppd.validation.post_recompile_agent_readiness_replay_v2 import validate_manifest

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "post_recompile_agent_readiness_replay_v2"


def test_valid_manifest_has_no_errors() -> None:
    manifest = json.loads((FIXTURE_DIR / "valid_manifest.json").read_text(encoding="utf-8"))

    assert validate_manifest(manifest) == []


def test_rejects_missing_required_replay_content() -> None:
    manifest = {
        "version": "post-recompile-agent-readiness-replay-v2",
        "replay_cases": [{"id": "case-001", "type": "replay_case"}],
        "validation_commands": [],
    }

    errors = validate_manifest(manifest)

    assert "missing replay case type: stale_source_hold_resolution_placeholder" in errors
    assert "missing replay case type: caution_template_check" in errors
    assert "missing replay case type: next_safe_action_summary" in errors
    assert "missing replay case type: refused_consequential_action_example" in errors
    assert "missing replay case type: reviewer_disposition" in errors
    assert "validation_commands must contain at least one argv-style command" in errors


def test_rejects_forbidden_claims_artifacts_and_active_mutations() -> None:
    manifest = json.loads((FIXTURE_DIR / "valid_manifest.json").read_text(encoding="utf-8"))
    manifest["notes"] = "Executed in DevHub and permit guaranteed."
    manifest["artifact"] = "ppd/private/session/browser/raw/downloaded/result.pdf"
    manifest["mutation_flags"]["source_mutation"] = True
    manifest["nested"] = {"active_prompt_mutation": True}

    errors = validate_manifest(manifest)

    assert any("forbidden claim" in error and "executed in devhub" in error for error in errors)
    assert any("forbidden claim" in error and "permit guaranteed" in error for error in errors)
    assert any("forbidden private/session/browser/raw/downloaded artifact" in error for error in errors)
    assert "active mutation flag is forbidden at $.mutation_flags.source_mutation" in errors
    assert "active mutation flag is forbidden at $.nested.active_prompt_mutation" in errors
