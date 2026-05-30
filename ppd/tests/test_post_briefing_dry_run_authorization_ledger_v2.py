from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from ppd.post_briefing_dry_run_authorization_ledger_v2 import (
    REQUIRED_ATTESTATION_IDS,
    REQUIRED_CONSUMED_KEYS,
    build_post_briefing_dry_run_authorization_ledger_v2,
    validate_post_briefing_dry_run_authorization_ledger_v2,
)


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "post_briefing_dry_run_authorization_ledger_v2" / "source_packets.json"


def _load_source_packets() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _build_ledger() -> dict:
    return build_post_briefing_dry_run_authorization_ledger_v2(_load_source_packets())


def test_builds_fixture_first_post_briefing_authorization_ledger_v2() -> None:
    ledger = _build_ledger()

    validate_post_briefing_dry_run_authorization_ledger_v2(ledger)

    assert ledger["packet_type"] == "post-briefing-dry-run-authorization-ledger"
    assert ledger["version"] == "v2"
    assert ledger["mode"] == "fixture_first_post_briefing_authorization_review"
    assert {item["source_key"] for item in ledger["consumes"]} == set(REQUIRED_CONSUMED_KEYS)


def test_authorization_rows_are_cited_no_go_rows() -> None:
    ledger = _build_ledger()

    assert len(ledger["authorization_rows"]) == 4
    for row in ledger["authorization_rows"]:
        assert row["decision"].startswith("no_go")
        assert row["authorization_effect"] in {
            "review_only",
            "checklist_review_only",
            "offline_fixture_validation_only",
        }
        assert row["citations"]


def test_signoff_placeholders_remain_blank_and_required() -> None:
    ledger = _build_ledger()

    reviewer_fields = ledger["reviewer_signoff_placeholders"]
    operator_fields = ledger["operator_signoff_placeholders"]

    assert {item["field_id"] for item in reviewer_fields} == {
        "reviewer_name",
        "reviewer_timestamp_utc",
        "reviewer_scope_decision",
    }
    assert "operator_name" in {item["field_id"] for item in operator_fields}
    assert all(item["blank_value"] is None for item in reviewer_fields + operator_fields)
    assert all(item["required"] is True for item in reviewer_fields)
    assert any(item["required"] is True for item in operator_fields)


def test_scope_windows_and_abort_conditions_do_not_authorize_live_execution() -> None:
    ledger = _build_ledger()

    assert {window["window_id"] for window in ledger["scope_limited_dry_run_windows"]} == {
        "public-plan-fixture-window",
        "devhub-plan-fixture-window",
    }
    assert all(window["live_execution_allowed"] is False for window in ledger["scope_limited_dry_run_windows"])
    assert len(ledger["independent_abort_conditions"]) == 3
    assert all(condition["citations"] for condition in ledger["independent_abort_conditions"])


def test_allowed_offline_validation_commands_are_narrow() -> None:
    ledger = _build_ledger()

    assert ledger["allowed_offline_validation_commands"] == [
        ["python3", "-m", "pytest", "ppd/tests/test_post_briefing_dry_run_authorization_ledger_v2.py"],
        ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
    ]

    bad = copy.deepcopy(ledger)
    bad["allowed_offline_validation_commands"] = [["python3", "-m", "playwright", "install"]]
    with pytest.raises(ValueError, match="forbidden live-operation token"):
        validate_post_briefing_dry_run_authorization_ledger_v2(bad)


def test_required_attestations_are_explicit_and_validated() -> None:
    ledger = _build_ledger()

    attestation_ids = {item["id"] for item in ledger["attestations"]}

    assert REQUIRED_ATTESTATION_IDS.issubset(attestation_ids)
    assert all(item["status"] == "attested_in_fixture" for item in ledger["attestations"])

    bad = copy.deepcopy(ledger)
    bad["attestations"] = [item for item in ledger["attestations"] if item["id"] != "no-auth-state"]
    with pytest.raises(ValueError, match="missing attestations"):
        validate_post_briefing_dry_run_authorization_ledger_v2(bad)


def test_validator_rejects_go_row_weakened_to_allowance() -> None:
    ledger = _build_ledger()
    ledger["authorization_rows"][0]["decision"] = "go_authorized"

    with pytest.raises(ValueError, match="decision must remain no_go"):
        validate_post_briefing_dry_run_authorization_ledger_v2(ledger)


def test_validator_rejects_uncited_authorization_rows() -> None:
    ledger = _build_ledger()
    ledger["authorization_rows"][0]["citations"] = []

    with pytest.raises(ValueError, match="must include citations"):
        validate_post_briefing_dry_run_authorization_ledger_v2(ledger)


@pytest.mark.parametrize(
    ("field_name", "expected"),
    [
        ("reviewer_signoff_placeholders", "reviewer_signoff_placeholders"),
        ("operator_signoff_placeholders", "operator_signoff_placeholders"),
    ],
)
def test_validator_rejects_missing_signoff_placeholder_groups(field_name: str, expected: str) -> None:
    ledger = _build_ledger()
    ledger[field_name] = []

    with pytest.raises(ValueError, match=expected):
        validate_post_briefing_dry_run_authorization_ledger_v2(ledger)


def test_validator_rejects_missing_scope_limits_or_abort_conditions() -> None:
    ledger = _build_ledger()
    ledger["scope_limited_dry_run_windows"][0].pop("scope")
    ledger["independent_abort_conditions"][0]["citations"] = []

    with pytest.raises(ValueError, match="missing scope"):
        validate_post_briefing_dry_run_authorization_ledger_v2(ledger)


@pytest.mark.parametrize(
    ("unsafe_summary", "expected"),
    [
        ("Use authenticated account-scoped facts from the DevHub record.", "private or authenticated fact"),
        ("Attach the saved browser trace.zip and raw PDF download.", "raw crawl/PDF/session/browser artifact"),
        ("The live DevHub run completed successfully.", "live execution or completion claim"),
        ("Automate MFA and solve CAPTCHA during sign in.", "credential, MFA, CAPTCHA"),
        ("This guarantees permit approval and legal acceptance.", "legal or permitting outcome guarantee"),
        ("Final submission was completed and payment submitted.", "final submission/payment/upload/scheduling/cancellation"),
        ("Activate source registry mutation and publish guardrail updates.", "active source/surface/prompt/guardrail/monitoring/release/agent mutation"),
    ],
)
def test_validator_rejects_unsafe_authorization_row_language(unsafe_summary: str, expected: str) -> None:
    ledger = _build_ledger()
    ledger["authorization_rows"][0]["summary"] = unsafe_summary

    with pytest.raises(ValueError, match=expected):
        validate_post_briefing_dry_run_authorization_ledger_v2(ledger)


def test_validator_rejects_active_mutation_flags() -> None:
    ledger = _build_ledger()
    ledger["release_state_mutation_enabled"] = True

    with pytest.raises(ValueError, match="mutation flag"):
        validate_post_briefing_dry_run_authorization_ledger_v2(ledger)


def test_validator_allows_negated_boundary_language_for_blockers() -> None:
    ledger = _build_ledger()
    ledger["authorization_rows"][0]["summary"] = (
        "Do not automate MFA, do not submit payment, and do not create browser artifacts."
    )

    validate_post_briefing_dry_run_authorization_ledger_v2(ledger)
