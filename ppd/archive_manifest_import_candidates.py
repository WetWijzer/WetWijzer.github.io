"""Fixture-first archive manifest import candidate packet v1.

This module maps synthetic processor metadata rows into metadata-only archive
manifest and normalized-document candidate rows. It is intentionally offline:
it does not crawl, run processors, persist raw bodies, or mutate active PP&D
state.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

RAW_BODY_KEYS = {
    "body",
    "raw_body",
    "html",
    "text",
    "content",
    "bytes",
    "downloaded_document",
    "document_bytes",
}

REQUIRED_ROW_KEYS = {
    "source_url",
    "final_url",
    "http_status",
    "content_type",
    "content_hash",
    "processor_name",
    "processor_version",
}

PACKET_VERSION = "archive-manifest-import-candidate-packet-v1"


def _as_bool(value: Any, field_name: str) -> bool:
    if isinstance(value, bool):
        return value
    raise ValueError(f"{field_name} must be a boolean")


def _as_str(value: Any, field_name: str) -> str:
    if isinstance(value, str) and value:
        return value
    raise ValueError(f"{field_name} must be a non-empty string")


def _as_optional_str(value: Any, field_name: str) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    raise ValueError(f"{field_name} must be a string or null")


def _as_int(value: Any, field_name: str) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{field_name} must be an integer")
    if isinstance(value, int):
        return value
    raise ValueError(f"{field_name} must be an integer")


def _as_redirect_chain(value: Any) -> list[dict[str, Any]]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("redirect_chain must be a list")
    chain: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise ValueError(f"redirect_chain[{index}] must be an object")
        from_url = _as_str(item.get("from_url"), f"redirect_chain[{index}].from_url")
        to_url = _as_str(item.get("to_url"), f"redirect_chain[{index}].to_url")
        status = _as_int(item.get("status"), f"redirect_chain[{index}].status")
        chain.append({"from_url": from_url, "to_url": to_url, "status": status})
    return chain


def _as_reason_list(row: dict[str, Any]) -> list[str]:
    if "skipped_reasons" in row:
        reasons = row["skipped_reasons"]
        if not isinstance(reasons, list):
            raise ValueError("skipped_reasons must be a list")
        return [_as_str(reason, "skipped_reasons[]") for reason in reasons]
    reason = row.get("skipped_reason")
    if reason is None:
        return []
    return [_as_str(reason, "skipped_reason")]


def _reject_raw_body(row: dict[str, Any], row_index: int) -> None:
    present = sorted(key for key in RAW_BODY_KEYS if key in row and row[key] is not None)
    if present:
        joined = ", ".join(present)
        raise ValueError(f"processor_metadata_rows[{row_index}] contains raw body fields: {joined}")


def map_processor_metadata_rows(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    archive_manifest_candidates: list[dict[str, Any]] = []
    normalized_document_candidates: list[dict[str, Any]] = []

    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ValueError(f"processor_metadata_rows[{index}] must be an object")
        _reject_raw_body(row, index)
        missing = sorted(key for key in REQUIRED_ROW_KEYS if key not in row)
        if missing:
            raise ValueError(f"processor_metadata_rows[{index}] missing required fields: {', '.join(missing)}")

        source_url = _as_str(row["source_url"], "source_url")
        final_url = _as_str(row["final_url"], "final_url")
        content_hash = _as_str(row["content_hash"], "content_hash")
        processor_name = _as_str(row["processor_name"], "processor_name")
        processor_version = _as_str(row["processor_version"], "processor_version")
        reviewer_hold = _as_bool(row.get("reviewer_hold", False), "reviewer_hold")
        no_raw_body = _as_bool(row.get("no_raw_body", True), "no_raw_body")
        if not no_raw_body:
            raise ValueError(f"processor_metadata_rows[{index}] must set no_raw_body to true")

        candidate_id = _as_str(row.get("candidate_id", f"archive-candidate-{index + 1:03d}"), "candidate_id")
        normalized_document_id = _as_str(
            row.get("normalized_document_id", f"normalized-document-candidate-{index + 1:03d}"),
            "normalized_document_id",
        )
        skipped_reasons = _as_reason_list(row)

        archive_manifest_candidates.append(
            {
                "candidate_id": candidate_id,
                "source_url": source_url,
                "final_url": final_url,
                "redirect_chain": _as_redirect_chain(row.get("redirect_chain", [])),
                "http_status": _as_int(row["http_status"], "http_status"),
                "content_type": _as_str(row["content_type"], "content_type"),
                "content_hash": content_hash,
                "processor_name": processor_name,
                "processor_version": processor_version,
                "skipped_reasons": skipped_reasons,
                "no_raw_body": True,
                "reviewer_hold": reviewer_hold,
            }
        )
        normalized_document_candidates.append(
            {
                "candidate_id": normalized_document_id,
                "archive_manifest_candidate_id": candidate_id,
                "source_url": source_url,
                "final_url": final_url,
                "content_hash": content_hash,
                "document_title": _as_optional_str(row.get("document_title"), "document_title"),
                "processor_name": processor_name,
                "processor_version": processor_version,
                "skipped_reasons": skipped_reasons,
                "no_raw_body": True,
                "reviewer_hold": reviewer_hold,
            }
        )

    return {
        "archive_manifest_candidates": archive_manifest_candidates,
        "normalized_document_candidates": normalized_document_candidates,
    }


def build_packet(processor_metadata_rows: list[dict[str, Any]]) -> dict[str, Any]:
    mapped = map_processor_metadata_rows(processor_metadata_rows)
    return {
        "packet_version": PACKET_VERSION,
        "mode": "fixture-first-offline-validation-only",
        "mutation_policy": "metadata-only-candidate-rows-no-active-state-mutation",
        "validation_commands": [
            ["python3", "-m", "py_compile", "ppd/archive_manifest_import_candidates.py"],
            ["python3", "-m", "pytest", "ppd/tests/test_archive_manifest_import_candidates.py"],
        ],
        **mapped,
    }


def load_packet_fixture(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload.get("processor_metadata_rows")
    if not isinstance(rows, list):
        raise ValueError("fixture must contain processor_metadata_rows list")
    return build_packet(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an offline archive manifest import candidate fixture.")
    parser.add_argument("fixture", type=Path)
    args = parser.parse_args()
    packet = load_packet_fixture(args.fixture)
    print(json.dumps(packet, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
