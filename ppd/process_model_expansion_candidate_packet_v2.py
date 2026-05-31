"""Offline validator for PP&D inactive process-model expansion candidate packet v2.

The packet is intentionally fixture-first: it describes synthetic inactive candidate
rows only and must not fetch live sources, reference private artifacts, claim legal
or permitting outcomes, or mutate active PP&D artifacts.
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

PACKET_VERSION = "inactive_process_model_expansion_candidate_packet_v2"
REQUIRED_WORKFLOWS = {
    "building",
    "trade",
    "solar",
    "demolition",
    "sign",
    "urban_forestry",
    "corrections",
}

REQUIRED_ROW_KEYS = {
    "delta_id",
    "workflow",
    "status",
    "synthetic",
    "candidate_scope",
    "required_facts",
    "required_documents",
    "fee_triggers",
    "deadlines",
    "unsupported_paths",
    "source_evidence_placeholders",
    "reviewer_disposition_placeholder",
    "derived_from_packets",
    "mutation_policy",
}

REQUIRED_SOURCE_PACKET_KEYS = {
    "permit_type_coverage_inventory",
    "document_requirement_matrix",
    "fee_deadline_matrix",
    "citation_integrity_packet",
    "stale_evidence_conflict_packet",
}

FORBIDDEN_MUTATION_TARGETS = {
    "active_process_models",
    "requirements",
    "guardrails",
    "prompts",
    "contracts",
    "source_registries",
    "devhub_surfaces",
    "release_state",
}

ACTIVE_MUTATION_FLAG_TOKENS = (
    "active_process",
    "active_process_model",
    "active_requirement",
    "active_guardrail",
    "active_prompt",
    "active_contract",
    "active_source",
    "active_devhub_surface",
    "active_release_state",
)
PRIVATE_ARTIFACT_KEY_TOKENS = (
    "auth",
    "browser",
    "cookie",
    "credential",
    "download",
    "downloaded",
    "har",
    "password",
    "payment",
    "private",
    "raw",
    "screenshot",
    "session",
    "storage_state",
    "token",
    "trace",
    "warc",
)
PRIVATE_ARTIFACT_VALUE_TOKENS = (
    "auth state",
    "browser state",
    "cookie jar",
    "downloaded document",
    "har file",
    "private devhub",
    "raw crawl",
    "raw body",
    "raw html",
    "raw pdf",
    "session storage",
    "storage state",
    "trace.zip",
    "warc payload",
)
LIVE_OR_DEVHUB_CLAIM_TOKENS = (
    "devhub access completed",
    "devhub accessed",
    "live crawl completed",
    "live devhub",
    "live source crawl",
    "opened browser",
    "ran live crawl",
)
GUARANTEE_TOKENS = (
    "approval guaranteed",
    "guaranteed approval",
    "legal advice",
    "legal guarantee",
    "legally compliant",
    "permit will be approved",
    "permit will issue",
)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def load_packet(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    _require(isinstance(data, dict), "packet must be a JSON object")
    return data


def validate_packet(packet: dict[str, Any]) -> None:
    _require(packet.get("packet_version") == PACKET_VERSION, "unexpected packet_version")
    _require(packet.get("status") == "inactive_candidate", "packet status must be inactive_candidate")
    _require(packet.get("fixture_first") is True, "packet must be fixture_first")
    _require(packet.get("live_source_crawl_permitted") is False, "live source crawl must be disabled")
    _require(packet.get("devhub_access_permitted") is False, "DevHub access must be disabled")
    _require(packet.get("mutates_active_models") is False, "packet must not mutate active models")

    source_packets = packet.get("source_packets")
    _require(isinstance(source_packets, dict), "source_packets must be an object")
    _require(REQUIRED_SOURCE_PACKET_KEYS.issubset(source_packets), "missing required source packet placeholders")

    forbidden_targets = set(packet.get("forbidden_mutation_targets", []))
    _require(FORBIDDEN_MUTATION_TARGETS.issubset(forbidden_targets), "missing forbidden mutation target")

    rows = packet.get("delta_rows")
    _require(isinstance(rows, list), "delta_rows must be a list")
    _require(len(rows) >= len(REQUIRED_WORKFLOWS), "delta_rows must cover every required workflow")

    seen_workflows: set[str] = set()
    seen_delta_ids: set[str] = set()
    for index, row in enumerate(rows):
        _validate_delta_row(index, row, seen_delta_ids, seen_workflows)

    missing_workflows = REQUIRED_WORKFLOWS.difference(seen_workflows)
    _require(not missing_workflows, f"missing permit-family rows: {sorted(missing_workflows)}")
    _validate_validation_commands(packet)
    _validate_no_forbidden_payload(packet)


def _validate_delta_row(index: int, row: Any, seen_delta_ids: set[str], seen_workflows: set[str]) -> None:
    _require(isinstance(row, dict), f"delta row {index} must be an object")
    missing = REQUIRED_ROW_KEYS.difference(row)
    _require(not missing, f"delta row {index} missing keys: {sorted(missing)}")

    delta_id = row["delta_id"]
    workflow = row["workflow"]
    _require(isinstance(delta_id, str) and delta_id.startswith("inactive-pm-v2-"), f"invalid delta_id at row {index}")
    _require(delta_id not in seen_delta_ids, f"duplicate delta_id: {delta_id}")
    seen_delta_ids.add(delta_id)

    _require(workflow in REQUIRED_WORKFLOWS, f"unexpected workflow: {workflow}")
    seen_workflows.add(workflow)
    _require(row["status"] == "inactive_candidate", f"row {delta_id} must be inactive_candidate")
    _require(row["synthetic"] is True, f"row {delta_id} must be synthetic")
    _require(row["mutation_policy"] == "do_not_apply_without_human_review_and_separate_activation", f"row {delta_id} has unsafe mutation_policy")

    required_lists = {
        "required_facts": "required-fact rows",
        "required_documents": "document rows",
        "fee_triggers": "fee rows",
        "deadlines": "deadline rows",
        "unsupported_paths": "unsupported-path rows",
        "source_evidence_placeholders": "source-evidence placeholders",
        "derived_from_packets": "derived packet references",
    }
    for list_key, label in required_lists.items():
        value = row[list_key]
        _require(isinstance(value, list) and value, f"row {delta_id} missing {label}")
        _require(all(isinstance(item, str) and item.strip() for item in value), f"row {delta_id} {list_key} must contain non-empty strings")

    reviewer = row["reviewer_disposition_placeholder"]
    _require(isinstance(reviewer, dict), f"row {delta_id} reviewer_disposition_placeholder must be an object")
    _require(reviewer.get("status") == "unreviewed", f"row {delta_id} reviewer status must be unreviewed")
    _require("approved" not in reviewer, f"row {delta_id} must not pre-approve reviewer disposition")
    _require("reviewer" in reviewer and "notes" in reviewer, f"row {delta_id} missing reviewer disposition placeholder fields")


def _validate_validation_commands(packet: Mapping[str, Any]) -> None:
    commands = packet.get("exact_offline_validation_commands")
    _require(isinstance(commands, list) and commands, "exact_offline_validation_commands must be non-empty")
    for command in commands:
        _require(isinstance(command, list) and command, "each validation command must be an argv list")
        _require(all(isinstance(part, str) and part for part in command), "validation command parts must be non-empty strings")


def _validate_no_forbidden_payload(packet: Mapping[str, Any]) -> None:
    for path, key, value in _walk(packet):
        normalized_key = key.lower().replace("-", "_")
        if any(token in normalized_key for token in ACTIVE_MUTATION_FLAG_TOKENS):
            _require(value is False, f"{path} must be false")
        if any(token in normalized_key for token in PRIVATE_ARTIFACT_KEY_TOKENS):
            _require(not _truthy(value), f"{path} must not include private, session, browser, raw, or downloaded artifacts")
        if isinstance(value, str):
            text = value.lower()
            _require(not any(token in text for token in PRIVATE_ARTIFACT_VALUE_TOKENS), f"{path} must not reference private, session, browser, raw, or downloaded artifacts")
            _require(not any(token in text for token in LIVE_OR_DEVHUB_CLAIM_TOKENS), f"{path} must not claim live crawl or DevHub execution")
            _require(not any(token in text for token in GUARANTEE_TOKENS), f"{path} must not guarantee legal or permitting outcomes")


def _walk(value: Any, prefix: str = "packet", key: str = "packet") -> list[tuple[str, str, Any]]:
    rows: list[tuple[str, str, Any]] = []
    if isinstance(value, Mapping):
        for child_key, child_value in value.items():
            child_key_text = str(child_key)
            child_path = f"{prefix}.{child_key_text}"
            rows.append((child_path, child_key_text, child_value))
            rows.extend(_walk(child_value, child_path, child_key_text))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child_value in enumerate(value):
            child_path = f"{prefix}[{index}]"
            rows.append((child_path, key, child_value))
            rows.extend(_walk(child_value, child_path, key))
    return rows


def _truthy(value: Any) -> bool:
    if value is None or value is False or value == "":
        return False
    if isinstance(value, Mapping) and not value:
        return False
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)) and not value:
        return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate inactive process-model expansion candidate packet v2 fixture")
    parser.add_argument("fixture", type=Path)
    args = parser.parse_args()
    packet = load_packet(args.fixture)
    validate_packet(packet)
    print("inactive process-model expansion candidate packet v2 fixture is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
