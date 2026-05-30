import json
from pathlib import Path


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "combined_inactive_patch_preview_dependency_rehearsal_v1.json"


def load_fixture():
    with FIXTURE_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def test_combined_dependency_rows_are_ordered_and_cross_family():
    fixture = load_fixture()
    rows = fixture["ordered_dependency_rows"]

    assert fixture["schema"] == "ppd.combined_inactive_patch_preview_dependency_rehearsal.v1"
    assert fixture["mode"] == "fixture_first_offline_only"
    assert [row["order"] for row in rows] == [1, 2]
    assert [row["family"] for row in rows] == ["public_source", "devhub_observed_surface"]
    assert rows[1]["depends_on"] == [rows[0]["dependency_id"]]
    assert all(row["promotion_state"] == "inactive_blocked" for row in rows)


def test_evidence_joins_cover_citations_and_observations():
    fixture = load_fixture()
    rows = fixture["ordered_dependency_rows"]
    join = fixture["evidence_joins"][0]

    row_dependency_ids = {row["dependency_id"] for row in rows}
    assert set(join["dependency_ids"]) == row_dependency_ids
    assert join["citation_evidence_ids"] == ["citation-public-001"]
    assert join["observation_evidence_ids"] == ["observation-devhub-001"]
    assert rows[0]["citation_evidence_ids"]
    assert rows[1]["observation_evidence_ids"]


def test_unchanged_inventory_and_blocked_notes_are_explicit():
    fixture = load_fixture()
    unchanged = set(fixture["unchanged_family_inventory"])
    prohibited = set(fixture["prohibited_actions_confirmed_absent"])

    assert "active_source_artifacts" in unchanged
    assert "active_surface_artifacts" in unchanged
    assert "active_requirement_artifacts" in unchanged
    assert "active_process_artifacts" in unchanged
    assert "active_guardrail_artifacts" in unchanged
    assert "prompts" in unchanged
    assert "release_state" in unchanged
    assert "live_source_crawl" in prohibited
    assert "devhub_access" in prohibited
    assert "active_artifact_mutation" in prohibited
    assert all(row["carry_forward_note"] for row in fixture["ordered_dependency_rows"])


def test_reviewer_signoffs_rollback_and_offline_commands_are_present():
    fixture = load_fixture()

    assert [item["status"] for item in fixture["reviewer_signoff_placeholders"]] == ["pending", "pending"]
    assert len(fixture["rollback_checkpoints"]) == 2
    assert fixture["offline_validation_commands"] == [
        ["python3", "-m", "pytest", "ppd/tests/test_combined_inactive_patch_preview_dependency_rehearsal_v1.py"],
        ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
    ]
