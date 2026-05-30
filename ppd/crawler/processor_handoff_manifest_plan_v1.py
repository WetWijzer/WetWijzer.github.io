"""Fixture-first PP&D processor handoff dry-run manifest plan v1.

This module intentionally plans ArchiveManifest rows from committed fixtures only. It does
not fetch URLs, invoke processor suites, import ipfs_datasets_py, or write archive
artifacts. The output is a deterministic dry-run contract for the future processor
handoff boundary.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

PLAN_VERSION = "fixture-first-processor-handoff-dry-run-manifest-plan-v1"

REQUIRED_ROW_FIELDS = (
    "manifest_id",
    "source_id",
    "source_evidence_ids",
    "requested_url",
    "canonical_url",
    "redirect_chain",
    "http_status",
    "content_type",
    "content_hash",
    "capture_started_at",
    "capture_finished_at",
    "processor_name",
    "processor_version",
    "archive_artifact_ref",
    "normalized_document_id",
    "skipped_reason",
    "no_raw_body_persisted",
)

FORBIDDEN_ARTIFACT_KEYS = {
    "auth_state",
    "browser_artifact_ref",
    "browser_session",
    "cookie_jar",
    "cookies",
    "downloaded_pdf_path",
    "har_path",
    "html_body",
    "local_pdf_path",
    "page_body",
    "pdf_artifact_ref",
    "private_file_path",
    "raw_archive_path",
    "raw_archive_ref",
    "raw_body",
    "raw_body_path",
    "raw_document_path",
    "raw_pdf_ref",
    "screenshot_path",
    "session_state",
    "storage_state",
    "trace_path",
}

FORBIDDEN_MUTATION_FLAGS = {
    "active_agent_state_mutation",
    "active_archive_mutation",
    "active_document_mutation",
    "active_guardrail_mutation",
    "active_release_state_mutation",
    "active_requirement_mutation",
    "active_source_mutation",
    "agent_state_mutated",
    "archive_mutated",
    "document_mutated",
    "guardrail_mutated",
    "release_state_mutated",
    "requirement_mutated",
    "source_mutated",
}

FORBIDDEN_CLAIM_KEYS = {
    "live_processor_execution",
    "processor_executed",
    "processor_invoked",
    "promoted",
    "promotion_claimed",
    "promotion_ready",
}

OUTCOME_GUARANTEE_PHRASES = (
    "approval guaranteed",
    "guaranteed approval",
    "guaranteed permit",
    "permit approval guaranteed",
    "permit guaranteed",
    "permit will be approved",
    "permit will be issued",
)


@dataclass(frozen=True)
class CandidateDecision:
    """Resolved dry-run decision for one frontier candidate."""

    source_id: str
    source_evidence_ids: tuple[str, ...]
    requested_url: str
    canonical_url: str
    expected_content_type: str
    processor_name: str | None
    processor_version: str | None
    skipped_reason: str | None
    normalized_document_id: str | None

    def to_archive_manifest_row(self) -> dict[str, Any]:
        manifest_id = f"archive-manifest:dry-run:v1:{self.source_id}"
        return {
            "manifest_id": manifest_id,
            "source_id": self.source_id,
            "source_evidence_ids": list(self.source_evidence_ids),
            "requested_url": self.requested_url,
            "canonical_url": self.canonical_url,
            "redirect_chain": [],
            "http_status": None,
            "content_type": self.expected_content_type,
            "content_hash": None,
            "capture_started_at": None,
            "capture_finished_at": None,
            "processor_name": self.processor_name,
            "processor_version": self.processor_version,
            "archive_artifact_ref": None,
            "normalized_document_id": self.normalized_document_id,
            "skipped_reason": self.skipped_reason,
            "no_raw_body_persisted": True,
        }


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_dry_run_manifest_plan(frontier_plan: dict[str, Any], processor_policy: dict[str, Any]) -> dict[str, Any]:
    """Build deterministic expected ArchiveManifest rows from fixture dictionaries."""

    validate_processor_policy(processor_policy)

    allowed_hosts = set(frontier_plan.get("allowed_hosts", []))
    content_type_processors = processor_policy["content_type_processors"]
    skipped_processor = processor_policy["skipped_processor"]
    rows: list[dict[str, Any]] = []

    for candidate in frontier_plan.get("candidates", []):
        decision = decide_candidate(candidate, allowed_hosts, content_type_processors, skipped_processor)
        rows.append(decision.to_archive_manifest_row())

    plan = {
        "plan_version": PLAN_VERSION,
        "source_plan_version": frontier_plan.get("plan_version"),
        "processor_policy_version": processor_policy.get("policy_version"),
        "archive_manifest_rows": rows,
        "attestations": {
            "fixture_first": True,
            "network_fetch_performed": False,
            "ipfs_datasets_py_invoked": False,
            "archive_artifacts_written": False,
            "no_raw_body_persisted": True,
        },
        "rollback_note": (
            "Delete generated dry-run manifest rows or revert this fixture-only plan; "
            "no raw bodies, downloaded documents, processor outputs, or archive artifacts "
            "are produced by this handoff plan."
        ),
        "offline_validation_commands": [
            ["python3", "-m", "py_compile", "ppd/crawler/processor_handoff_manifest_plan_v1.py"],
            ["python3", "-m", "pytest", "ppd/tests/test_processor_handoff_manifest_plan_v1.py"],
            ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
        ],
    }
    validate_dry_run_manifest_plan(plan)
    return plan


def decide_candidate(
    candidate: dict[str, Any],
    allowed_hosts: set[str],
    content_type_processors: dict[str, dict[str, str]],
    skipped_processor: dict[str, str],
) -> CandidateDecision:
    source_id = require_string(candidate, "source_id")
    source_evidence_ids = require_string_tuple(candidate, "source_evidence_ids")
    requested_url = require_string(candidate, "requested_url")
    canonical_url = require_string(candidate, "canonical_url")
    expected_content_type = require_string(candidate, "expected_content_type")
    explicit_skip = candidate.get("skip_reason")

    skipped_reason = resolve_skip_reason(
        canonical_url=canonical_url,
        expected_content_type=expected_content_type,
        allowed_hosts=allowed_hosts,
        explicit_skip=explicit_skip,
        supported_content_types=set(content_type_processors),
    )

    if skipped_reason is not None:
        return CandidateDecision(
            source_id=source_id,
            source_evidence_ids=source_evidence_ids,
            requested_url=requested_url,
            canonical_url=canonical_url,
            expected_content_type=expected_content_type,
            processor_name=skipped_processor.get("processor_name"),
            processor_version=skipped_processor.get("processor_version"),
            skipped_reason=skipped_reason,
            normalized_document_id=None,
        )

    processor = content_type_processors[expected_content_type]
    return CandidateDecision(
        source_id=source_id,
        source_evidence_ids=source_evidence_ids,
        requested_url=requested_url,
        canonical_url=canonical_url,
        expected_content_type=expected_content_type,
        processor_name=processor["processor_name"],
        processor_version=processor["processor_version"],
        skipped_reason=None,
        normalized_document_id=f"normalized-document:placeholder:v1:{source_id}",
    )


def resolve_skip_reason(
    canonical_url: str,
    expected_content_type: str,
    allowed_hosts: set[str],
    explicit_skip: object,
    supported_content_types: set[str],
) -> str | None:
    if explicit_skip is not None:
        if not isinstance(explicit_skip, str) or not explicit_skip:
            raise TypeError("candidate skip_reason must be a non-empty string when present")
        return explicit_skip

    parsed = urlparse(canonical_url)
    if parsed.scheme not in {"http", "https"}:
        return "unsupported_scheme"
    if parsed.hostname not in allowed_hosts:
        return "outside_allowlist"
    if expected_content_type not in supported_content_types:
        return "unsupported_content_type"
    return None


def validate_processor_policy(processor_policy: dict[str, Any]) -> None:
    errors: list[str] = []
    if not isinstance(processor_policy.get("policy_version"), str) or not processor_policy.get("policy_version"):
        errors.append("processor policy missing policy_version")

    content_type_processors = processor_policy.get("content_type_processors")
    if not isinstance(content_type_processors, dict) or not content_type_processors:
        errors.append("processor policy missing content_type_processors")
    else:
        for content_type, processor in content_type_processors.items():
            if not isinstance(content_type, str) or not content_type:
                errors.append("processor policy has an invalid content type key")
                continue
            if not isinstance(processor, dict):
                errors.append(f"processor policy for {content_type} must be an object")
                continue
            for key in ("processor_name", "processor_version"):
                if not isinstance(processor.get(key), str) or not processor.get(key):
                    errors.append(f"processor policy for {content_type} missing {key}")

    skipped_processor = processor_policy.get("skipped_processor")
    if not isinstance(skipped_processor, dict):
        errors.append("processor policy missing skipped_processor")
    else:
        for key in ("processor_name", "processor_version"):
            if not isinstance(skipped_processor.get(key), str) or not skipped_processor.get(key):
                errors.append(f"skipped processor policy missing {key}")

    if errors:
        raise ValueError("invalid processor handoff dry-run policy: " + "; ".join(errors))


def validate_dry_run_manifest_plan(plan: dict[str, Any]) -> None:
    errors: list[str] = []
    attestations = plan.get("attestations")
    if not isinstance(attestations, dict):
        errors.append("plan missing attestations")
    else:
        required_false = ("network_fetch_performed", "ipfs_datasets_py_invoked", "archive_artifacts_written")
        for key in required_false:
            if attestations.get(key) is not False:
                errors.append(f"attestation {key} must be false")
        for key in ("fixture_first", "no_raw_body_persisted"):
            if attestations.get(key) is not True:
                errors.append(f"attestation {key} must be true")

    rows = plan.get("archive_manifest_rows")
    if not isinstance(rows, list) or not rows:
        errors.append("plan missing archive_manifest_rows")
    else:
        for index, row in enumerate(rows):
            if not isinstance(row, dict):
                errors.append(f"archive_manifest_rows[{index}] must be an object")
                continue
            errors.extend(validate_manifest_row(row, index))

    errors.extend(find_forbidden_recursive_claims(plan))
    if errors:
        raise ValueError("invalid processor handoff dry-run manifest plan v1: " + "; ".join(errors))


def validate_manifest_row(row: dict[str, Any], index: int) -> list[str]:
    errors: list[str] = []
    label = f"archive_manifest_rows[{index}]"

    for field in REQUIRED_ROW_FIELDS:
        if field not in row:
            errors.append(f"{label} missing {field}")

    for field in ("source_id", "manifest_id", "requested_url", "canonical_url", "content_type"):
        if not isinstance(row.get(field), str) or not row.get(field):
            errors.append(f"{label} missing non-empty {field}")

    evidence_ids = row.get("source_evidence_ids")
    if not isinstance(evidence_ids, list) or not evidence_ids:
        errors.append(f"{label} is uncited")
    elif any(not isinstance(item, str) or not item for item in evidence_ids):
        errors.append(f"{label} has invalid source_evidence_ids")

    if row.get("requested_url") and row.get("canonical_url"):
        for field in ("requested_url", "canonical_url"):
            parsed = urlparse(row[field])
            if parsed.scheme not in {"http", "https"} or not parsed.hostname:
                errors.append(f"{label} has invalid {field}")

    if row.get("archive_artifact_ref") is not None:
        errors.append(f"{label} must not reference archive artifacts")
    if row.get("no_raw_body_persisted") is not True:
        errors.append(f"{label} must attest no raw body persistence")

    skipped_reason = row.get("skipped_reason")
    normalized_document_id = row.get("normalized_document_id")
    if skipped_reason is None:
        for field in ("processor_name", "processor_version", "normalized_document_id"):
            if not isinstance(row.get(field), str) or not row.get(field):
                errors.append(f"{label} processor-ready row missing {field}")
    else:
        if not isinstance(skipped_reason, str) or not skipped_reason:
            errors.append(f"{label} skipped row has invalid skipped_reason")
        if normalized_document_id is not None:
            errors.append(f"{label} skipped row must not claim a normalized document")
        for field in ("processor_name", "processor_version"):
            if not isinstance(row.get(field), str) or not row.get(field):
                errors.append(f"{label} skipped row missing {field}")

    return errors


def find_forbidden_recursive_claims(value: Any, path: str = "plan") -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in FORBIDDEN_ARTIFACT_KEYS and child not in (None, "", [], {}):
                errors.append(f"{child_path} contains raw, private, session, browser, or PDF artifact data")
            if key in FORBIDDEN_MUTATION_FLAGS and child is True:
                errors.append(f"{child_path} claims an active mutation")
            if key in FORBIDDEN_CLAIM_KEYS and child is True:
                errors.append(f"{child_path} claims live processor execution or promotion")
            errors.extend(find_forbidden_recursive_claims(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(find_forbidden_recursive_claims(child, f"{path}[{index}]"))
    elif isinstance(value, str):
        normalized = " ".join(value.lower().split())
        for phrase in OUTCOME_GUARANTEE_PHRASES:
            if phrase in normalized:
                errors.append(f"{path} contains a legal or permitting outcome guarantee")
                break
    return errors


def require_string(item: dict[str, Any], key: str) -> str:
    value = item.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"expected non-empty string field: {key}")
    return value


def require_string_tuple(item: dict[str, Any], key: str) -> tuple[str, ...]:
    value = item.get(key)
    if not isinstance(value, list) or not value:
        raise ValueError(f"expected non-empty string list field: {key}")
    if any(not isinstance(entry, str) or not entry for entry in value):
        raise ValueError(f"expected non-empty string entries in field: {key}")
    return tuple(value)


def build_dry_run_manifest_plan_from_files(frontier_path: Path, policy_path: Path) -> dict[str, Any]:
    return build_dry_run_manifest_plan(load_json(frontier_path), load_json(policy_path))


def main() -> None:
    fixture_dir = Path(__file__).parents[1] / "tests" / "fixtures" / "processor_handoff_manifest_plan_v1"
    plan = build_dry_run_manifest_plan_from_files(
        fixture_dir / "public_crawl_frontier_expansion_plan_v1.fixture.json",
        fixture_dir / "processor_suite_policy.fixture.json",
    )
    print(json.dumps(plan, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
