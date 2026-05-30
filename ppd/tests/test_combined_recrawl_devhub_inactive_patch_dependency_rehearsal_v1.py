from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest

from ppd.agent_readiness.combined_recrawl_devhub_inactive_patch_dependency_rehearsal_v1 import (
    EXACT_OFFLINE_VALIDATION_COMMANDS,
    REHEARSAL_ID,
    build_rehearsal,
    build_rehearsal_from_fixture_paths,
    validate_rehearsal,
)


FIXTURE_DIR = (
    Path(__file__).parent
    / "fixtures"
    / "combined_recrawl_devhub_inactive_patch_dependency_rehearsal_v1"
)
PUBLIC_PREVIEW = FIXTURE_DIR / "public_source_recrawl_inactive_patch_preview_v1.json"
DEVHUB_PREVIEW = FIXTURE_DIR / "devhub_observed_surface_inactive_patch_preview_v1.json"


def _fixture(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _valid_public_preview() -> dict[str, Any]:
    return _fixture(PUBLIC_PREVIEW)


def _valid_devhub_preview() -> dict[str, Any]:
    return _fixture(DEVHUB_PREVIEW)


def _valid_rehearsal() -> dict[str, Any]:
    return build_rehearsal(_valid_public_preview(), _valid_devhub_preview())


def test_combined_rehearsal_builds_ordered_dependency_rows() -> None:
    rehearsal = build_rehearsal_from_fixture_paths(PUBLIC_PREVIEW, DEVHUB_PREVIEW)

    assert rehearsal["rehearsal_id"] == REHEARSAL_ID
    assert rehearsal["mode"] == "fixture_first_offline_rehearsal"
    assert rehearsal["mutates_active_artifacts"] is False

    rows = rehearsal["dependency_rows"]
    assert [row["dependency_order"] for row in rows] == list(range(1, len(rows) + 1))
    assert len(rows) == 5

    first = rows[0]
    assert first["public_source_patch"]["source_id"] == "ppd-devhub-guide-submit-permit-application"
    assert first["devhub_surface_patch"]["surface_id"] == "devhub-permit-application-draft-surface"
    assert first["reviewer_decision_placeholders"] == [
        "placeholder:reviewer_decision=pending",
        "placeholder:activation_scope=pending",
        "placeholder:required_followup=pending",
    ]


def test_combined_rehearsal_includes_linkage_conflict_and_unlinked_placeholders() -> None:
    rehearsal = build_rehearsal_from_fixture_paths(PUBLIC_PREVIEW, DEVHUB_PREVIEW)
    rows = rehearsal["dependency_rows"]

    linked_rows = [
        row
        for row in rows
        if row["public_source_patch"]["source_id"] == "ppd-submit-plans-online-single-pdf"
    ]
    assert len(linked_rows) == 1
    assert linked_rows[0]["source_to_surface_linkage_placeholders"] == [
        "placeholder:review source evidence against observed DevHub surface before activation",
        "source_id:ppd-submit-plans-online-single-pdf -> surface_id:devhub-upload-staging-surface",
    ]
    assert "placeholder:hold if public source evidence conflicts with observed DevHub labels" in linked_rows[0][
        "conflict_hold_placeholders"
    ]

    unlinked_rows = [
        row
        for row in rows
        if row["devhub_surface_patch"]["surface_id"] == "devhub-account-home-surface"
    ]
    assert len(unlinked_rows) == 1
    assert unlinked_rows[0]["public_source_patch"]["source_patch_id"] == "placeholder:no-public-source-patch"
    assert unlinked_rows[0]["source_to_surface_linkage_placeholders"] == [
        "placeholder:no public source recrawl patch linked to this DevHub surface patch yet"
    ]


def test_combined_rehearsal_carries_rollback_refs_and_offline_validation_commands() -> None:
    rehearsal = build_rehearsal_from_fixture_paths(PUBLIC_PREVIEW, DEVHUB_PREVIEW)

    assert "rollback:public-source-recrawl-preview:how-pay-fees" in rehearsal["rollback_references"]
    assert "rollback:devhub-surface-preview:fee-payment-review" in rehearsal["rollback_references"]
    assert rehearsal["exact_offline_validation_commands"] == EXACT_OFFLINE_VALIDATION_COMMANDS
    assert ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"] in rehearsal[
        "exact_offline_validation_commands"
    ]


def test_rehearsal_boundaries_prevent_live_or_private_artifact_mutation() -> None:
    rehearsal = build_rehearsal_from_fixture_paths(PUBLIC_PREVIEW, DEVHUB_PREVIEW)
    boundary_text = "\n".join(rehearsal["artifact_boundaries"])

    assert "no active public source mutation" in boundary_text
    assert "no active DevHub surface mutation" in boundary_text
    assert "no browser/session/crawl/downloaded artifact creation" in boundary_text
    assert all(row["devhub_surface_patch"]["requires_attendance"] is True for row in rehearsal["dependency_rows"])


def test_validation_rejects_missing_public_preview_inputs() -> None:
    with pytest.raises(ValueError, match="public recrawl fixture preview_id"):
        build_rehearsal({}, _valid_devhub_preview())


@pytest.mark.parametrize("bad_public", [None, [], "missing"])
def test_validation_rejects_non_object_public_preview_inputs(bad_public: Any) -> None:
    with pytest.raises(ValueError, match="public recrawl fixture input is required"):
        build_rehearsal(bad_public, _valid_devhub_preview())


def test_validation_rejects_missing_devhub_preview_inputs() -> None:
    with pytest.raises(ValueError, match="DevHub surface fixture preview_id"):
        build_rehearsal(_valid_public_preview(), {})


@pytest.mark.parametrize("bad_devhub", [None, [], "missing"])
def test_validation_rejects_non_object_devhub_preview_inputs(bad_devhub: Any) -> None:
    with pytest.raises(ValueError, match="DevHub preview fixture input is required"):
        build_rehearsal(_valid_public_preview(), bad_devhub)


def test_validation_rejects_missing_public_dependency_rows() -> None:
    public_preview = _valid_public_preview()
    public_preview["inactive_public_source_patches"] = []

    with pytest.raises(ValueError, match="non-empty inactive_public_source_patches"):
        build_rehearsal(public_preview, _valid_devhub_preview())


def test_validation_rejects_missing_devhub_dependency_rows() -> None:
    devhub_preview = _valid_devhub_preview()
    devhub_preview["inactive_devhub_surface_patches"] = []

    with pytest.raises(ValueError, match="non-empty inactive_devhub_surface_patches"):
        build_rehearsal(_valid_public_preview(), devhub_preview)


def test_validation_rejects_missing_required_public_row_fields() -> None:
    public_preview = _valid_public_preview()
    del public_preview["inactive_public_source_patches"][0]["evidence_ids"]

    with pytest.raises(ValueError, match="non-empty evidence_ids"):
        build_rehearsal(public_preview, _valid_devhub_preview())


def test_validation_rejects_missing_required_devhub_row_fields() -> None:
    devhub_preview = _valid_devhub_preview()
    del devhub_preview["inactive_devhub_surface_patches"][0]["rollback_ref"]

    with pytest.raises(ValueError, match="rollback_ref"):
        build_rehearsal(_valid_public_preview(), devhub_preview)


@pytest.mark.parametrize(
    ("field", "message"),
    [
        ("dependency_rows", "dependency_rows"),
        ("rollback_references", "rollback_references"),
        ("exact_offline_validation_commands", "validation_commands"),
    ],
)
def test_rehearsal_validation_rejects_missing_top_level_required_fields(field: str, message: str) -> None:
    rehearsal = _valid_rehearsal()
    if field == "exact_offline_validation_commands":
        rehearsal[field] = []
    else:
        rehearsal[field] = []

    with pytest.raises(ValueError, match=message):
        validate_rehearsal(rehearsal)


@pytest.mark.parametrize(
    ("field", "message"),
    [
        ("source_to_surface_linkage_placeholders", "source_to_surface_linkage_placeholders"),
        ("conflict_hold_placeholders", "conflict_hold_placeholders"),
        ("reviewer_decision_placeholders", "reviewer decision"),
        ("rollback_references", "rollback_references"),
    ],
)
def test_rehearsal_validation_rejects_missing_row_placeholders_and_rollback_refs(
    field: str, message: str
) -> None:
    rehearsal = _valid_rehearsal()
    rehearsal["dependency_rows"][0][field] = []

    with pytest.raises(ValueError, match=message):
        validate_rehearsal(rehearsal)


def test_rehearsal_validation_rejects_missing_dependency_patch_objects() -> None:
    rehearsal = _valid_rehearsal()
    rehearsal["dependency_rows"][0]["devhub_surface_patch"] = None

    with pytest.raises(ValueError, match="devhub_surface_patch"):
        validate_rehearsal(rehearsal)


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        ({"raw_crawl_output_path": "ppd/raw/crawl.json"}, "forbidden artifact key"),
        ({"downloaded_document_path": "private.pdf"}, "forbidden artifact key"),
        ({"private_artifact_ref": "secret"}, "forbidden artifact key"),
        ({"browser_state_path": "state.json"}, "forbidden artifact key"),
        ({"session_state_path": "state.json"}, "forbidden artifact key"),
        ({"trace_path": "trace.zip"}, "forbidden artifact key"),
        ({"claim": "live DevHub access completed"}, "live network or DevHub access claim"),
        ({"claim": "authenticated DevHub and captured session"}, "live network or DevHub access claim"),
        ({"decision": "agent may submit the permit"}, "consequential action language"),
        ({"decision": "ready to pay the fee"}, "consequential action language"),
        ({"guarantee": "permit approval guaranteed"}, "legal or permitting guarantee"),
        ({"mutates_active_artifacts": True}, "mutation flag"),
        ({"mutates_prompts": True}, "mutation flag"),
    ],
)
def test_rehearsal_validation_rejects_artifacts_claims_actions_guarantees_and_mutation_flags(
    payload: dict[str, Any], message: str
) -> None:
    rehearsal = _valid_rehearsal()
    rehearsal["unsafe_probe"] = payload

    with pytest.raises(ValueError, match=message):
        validate_rehearsal(rehearsal)


def test_preview_validation_rejects_raw_or_private_artifact_fields_before_rehearsal_build() -> None:
    public_preview = _valid_public_preview()
    public_preview["inactive_public_source_patches"][0]["raw_crawl_output_path"] = "tmp/raw.json"

    with pytest.raises(ValueError, match="forbidden artifact key"):
        build_rehearsal(public_preview, _valid_devhub_preview())


def test_validation_does_not_mutate_fixture_inputs() -> None:
    public_preview = _valid_public_preview()
    devhub_preview = _valid_devhub_preview()
    public_before = copy.deepcopy(public_preview)
    devhub_before = copy.deepcopy(devhub_preview)

    build_rehearsal(public_preview, devhub_preview)

    assert public_preview == public_before
    assert devhub_preview == devhub_before
