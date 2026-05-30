from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest

from ppd.source_freshness_run_queue_v1 import (
    build_public_source_freshness_run_queue_v1,
    validate_public_source_freshness_run_queue_v1,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures"
BACKLOG_FIXTURE_PATH = FIXTURE_DIR / "source_freshness_monitor_backlog_v1.json"
RUN_QUEUE_FIXTURE_PATH = FIXTURE_DIR / "source_freshness" / "public_source_freshness_run_queue_v1.json"


def load_fixture(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    assert isinstance(data, dict)
    return data


def built_queue() -> dict[str, Any]:
    return build_public_source_freshness_run_queue_v1(load_fixture(BACKLOG_FIXTURE_PATH))


def test_builds_ordered_no_network_run_queue_from_backlog_packet() -> None:
    queue = built_queue()

    assert validate_public_source_freshness_run_queue_v1(queue) == []
    assert [row["order"] for row in queue["run_queue_rows"]] == [1, 2, 3]
    assert [row["source_anchor_ids"] for row in queue["run_queue_rows"]] == [
        ["anchor-portland-zoning-code-title-33"],
        ["anchor-portland-bds-land-use-review-fees"],
        ["anchor-portland-permit-forms"],
    ]
    assert [row["expected_freshness_cadence"] for row in queue["run_queue_rows"]] == [
        ["monthly"],
        ["quarterly"],
        ["monthly"],
    ]
    assert all(row["run_constraints"]["network_allowed"] is False for row in queue["run_queue_rows"])
    assert all(row["run_constraints"]["refresh_completion_claim_allowed"] is False for row in queue["run_queue_rows"])


def test_committed_run_queue_fixture_matches_builder_output() -> None:
    backlog = load_fixture(BACKLOG_FIXTURE_PATH)
    expected = load_fixture(RUN_QUEUE_FIXTURE_PATH)

    assert build_public_source_freshness_run_queue_v1(backlog) == expected


def test_run_queue_rows_preserve_synthetic_probes_reviewer_handoff_and_exact_commands() -> None:
    queue = built_queue()
    first_row = queue["run_queue_rows"][0]

    assert [probe["id"] for probe in first_row["synthetic_change_probes"]] == [
        "synthetic-last-modified-drift",
        "synthetic-policy-effective-date-delta",
    ]
    assert first_row["reviewer_handoff"]["review_state"] == "pending_offline_fixture_review"
    assert first_row["reviewer_handoff"]["reviewer_decision_required"] is True
    assert first_row["offline_validation_commands"] == [command for command in queue["validation_commands"]]
    assert all(command["network"] is False for command in first_row["offline_validation_commands"])


@pytest.mark.parametrize(
    ("mutate", "expected"),
    [
        (lambda queue: queue.__setitem__("version", "wrong"), "version must be public-source-freshness-run-queue-v1"),
        (lambda queue: queue.__setitem__("run_queue_rows", []), "run_queue_rows must be a non-empty list"),
        (lambda queue: queue["run_queue_rows"][0].__setitem__("source_anchor_ids", []), "source_anchor_ids must be a non-empty string list"),
        (lambda queue: queue["run_queue_rows"][0].__setitem__("expected_freshness_cadence", []), "expected_freshness_cadence must be a non-empty string list"),
        (lambda queue: queue["run_queue_rows"][0].__setitem__("synthetic_change_probes", []), "synthetic_change_probes must be a non-empty list"),
        (lambda queue: queue["run_queue_rows"][0].__setitem__("offline_validation_commands", []), "offline_validation_commands must be a non-empty list"),
        (lambda queue: queue["run_queue_rows"][0].pop("reviewer_handoff"), "reviewer_handoff must be an object"),
        (lambda queue: queue["run_queue_rows"][0]["reviewer_handoff"].pop("queue_owner"), "reviewer_handoff missing queue_owner"),
        (lambda queue: queue["run_queue_rows"][0]["reviewer_handoff"].__setitem__("review_state", "complete"), "must remain pending offline fixture review"),
        (lambda queue: queue["run_queue_rows"][0]["run_constraints"].__setitem__("network_allowed", True), "network_allowed must be false"),
        (lambda queue: queue["run_queue_rows"][0]["offline_validation_commands"][0].__setitem__("network", True), "offline command network must be false"),
        (lambda queue: queue.__setitem__("validation_commands", []), "validation_commands must be a non-empty list"),
    ],
)
def test_validator_rejects_incomplete_or_unsafe_run_queue_rows(mutate: Any, expected: str) -> None:
    broken = copy.deepcopy(built_queue())
    mutate(broken)

    errors = validate_public_source_freshness_run_queue_v1(broken)

    assert any(expected in error for error in errors)


@pytest.mark.parametrize(
    ("mutate", "expected"),
    [
        (lambda queue: queue["run_queue_rows"][0].__setitem__("session_artifact", "storageState.json"), "private/authenticated/session/browser artifact rejected"),
        (lambda queue: queue["run_queue_rows"][0].__setitem__("raw_pdf_download", "downloaded permit guide.pdf"), "raw crawl/PDF/downloaded data rejected"),
        (lambda queue: queue["run_queue_rows"][0].__setitem__("live_status", "live crawl completed for this source"), "live crawl or refresh-complete claim rejected"),
        (lambda queue: queue["run_queue_rows"][0].__setitem__("refresh_claim", "source refresh completed"), "live crawl or refresh-complete claim rejected"),
        (lambda queue: queue["run_queue_rows"][0].__setitem__("guarantee", "permit will issue after this check"), "legal or permitting outcome guarantee rejected"),
        (lambda queue: queue["run_queue_rows"][0].__setitem__("action", "submit the permit application"), "consequential action language rejected"),
        (lambda queue: queue["run_queue_rows"][0].__setitem__("active_source_mutation", True), "active mutation flag must be false"),
        (lambda queue: queue["run_queue_rows"][0].__setitem__("active_document_mutation", True), "active mutation flag must be false"),
        (lambda queue: queue["run_queue_rows"][0].__setitem__("active_requirement_mutation", True), "active mutation flag must be false"),
        (lambda queue: queue["run_queue_rows"][0].__setitem__("active_process_mutation", True), "active mutation flag must be false"),
        (lambda queue: queue["run_queue_rows"][0].__setitem__("active_guardrail_mutation", True), "active mutation flag must be false"),
        (lambda queue: queue["run_queue_rows"][0].__setitem__("active_release_state_mutation", True), "active mutation flag must be false"),
        (lambda queue: queue["run_queue_rows"][0].__setitem__("active_prompt_mutation", True), "active mutation flag must be false"),
        (lambda queue: queue["run_queue_rows"][0].__setitem__("active_agent_state_mutation", True), "active mutation flag must be false"),
    ],
)
def test_validator_rejects_forbidden_artifacts_claims_actions_and_mutation_flags(mutate: Any, expected: str) -> None:
    broken = copy.deepcopy(built_queue())
    mutate(broken)

    errors = validate_public_source_freshness_run_queue_v1(broken)

    assert any(expected in error for error in errors)


def test_validator_rejects_source_anchor_summary_mismatch() -> None:
    broken = copy.deepcopy(built_queue())
    broken["run_queue_rows"][0]["source_anchors"][0]["id"] = "different-anchor"

    errors = validate_public_source_freshness_run_queue_v1(broken)

    assert any("source anchor summary ids must match source_anchor_ids order" in error for error in errors)


def test_validator_rejects_synthetic_probe_without_fixture_only_mode() -> None:
    broken = copy.deepcopy(built_queue())
    broken["run_queue_rows"][0]["synthetic_change_probes"][0]["execution_mode"] = "live_probe"

    errors = validate_public_source_freshness_run_queue_v1(broken)

    assert any("synthetic probe execution_mode must be synthetic_fixture_only" in error for error in errors)


def test_builder_rejects_invalid_backlog_packet_before_queueing() -> None:
    backlog = load_fixture(BACKLOG_FIXTURE_PATH)
    backlog["work_items"][0]["offline_validation_command_ids"] = ["missing-command"]

    with pytest.raises(ValueError, match="invalid public source freshness monitor backlog packet v1"):
        build_public_source_freshness_run_queue_v1(backlog)
