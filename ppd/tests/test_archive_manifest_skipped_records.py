"""Fixture-first coverage for skipped ArchiveManifest records."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from importlib import import_module
from pathlib import Path
from typing import Any


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "archive_manifest" / "skipped_captures.json"


def _archive_manifest_class() -> type[Any]:
    for module_name in (
        "ppd.contracts.archive",
        "ppd.contracts.archives",
        "ppd.contracts.documents",
    ):
        try:
            module = import_module(module_name)
        except ModuleNotFoundError:
            continue
        manifest_class = getattr(module, "ArchiveManifest", None)
        if manifest_class is not None:
            return manifest_class
    raise AssertionError("ArchiveManifest contract class was not found in ppd.contracts")


def _build_manifest(record: dict[str, Any]) -> Any:
    manifest_class = _archive_manifest_class()
    if hasattr(manifest_class, "model_validate"):
        return manifest_class.model_validate(record)
    if hasattr(manifest_class, "parse_obj"):
        return manifest_class.parse_obj(record)
    return manifest_class(**record)


def _dump_manifest(manifest: Any) -> dict[str, Any]:
    if hasattr(manifest, "model_dump"):
        return manifest.model_dump()
    if hasattr(manifest, "dict"):
        return manifest.dict()
    if is_dataclass(manifest):
        return asdict(manifest)
    return dict(vars(manifest))


def _load_fixture_records() -> list[dict[str, Any]]:
    with FIXTURE_PATH.open(encoding="utf-8") as fixture_file:
        records = json.load(fixture_file)
    assert records, "skipped ArchiveManifest fixture must contain at least one record"
    return records


def test_skipped_archive_manifests_preserve_required_policy_metadata() -> None:
    for record in _load_fixture_records():
        manifest = _build_manifest(record)
        dumped = _dump_manifest(manifest)

        assert dumped["canonical_url"] == record["canonical_url"]
        assert dumped["requested_url"] == record["requested_url"]
        assert dumped["source_id"] == record["source_id"]
        assert dumped["skipped_reason"] == record["skipped_reason"]
        assert dumped["processor_policy"] == record["processor_policy"]
        assert dumped.get("content_type") == record["content_type"]


def test_skipped_archive_manifests_do_not_persist_raw_body_or_artifact_refs() -> None:
    for record in _load_fixture_records():
        manifest = _build_manifest(record)
        dumped = _dump_manifest(manifest)

        assert dumped["skipped_reason"]
        assert dumped["no_raw_body_persisted"] is True
        assert dumped.get("archive_artifact_ref") is None
        assert dumped.get("normalized_document_id") is None
        assert dumped.get("content_hash") is None


def test_skipped_archive_manifest_fixture_includes_known_and_unknown_content_types() -> None:
    records = _load_fixture_records()
    content_types = {record.get("content_type") for record in records}

    assert "text/html; charset=utf-8" in content_types
    assert None in content_types
