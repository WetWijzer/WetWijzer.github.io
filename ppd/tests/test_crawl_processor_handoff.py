from __future__ import annotations

import json
from pathlib import Path

import pytest

from ppd.contracts.archive_adapter import IPFS_DATASETS_PROCESSOR_BACKEND
from ppd.contracts.crawl_processor_handoff import (
    ALLOWED_PROCESSOR_MODULE_PREFIXES,
    assert_valid_crawl_processor_handoff_manifest,
    crawl_processor_handoff_manifest_from_dict,
)


FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "crawl_processor_handoff"
    / "public_ppd_seed_handoff_manifest.json"
)


def _fixture() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def test_public_ppd_seed_handoff_manifest_maps_seeds_to_ipfs_processors() -> None:
    data = _fixture()

    assert_valid_crawl_processor_handoff_manifest(data)
    manifest = crawl_processor_handoff_manifest_from_dict(data)

    assert manifest.backend_path == IPFS_DATASETS_PROCESSOR_BACKEND
    assert len(manifest.jobs) == 3
    assert {job.seed_id for job in manifest.jobs} == {
        "ppd-seed-landing",
        "ppd-seed-applications-forms",
        "ppd-seed-devhub-public",
    }
    assert {job.source_url for job in manifest.jobs} == {
        "https://www.portland.gov/ppd",
        "https://www.portland.gov/ppd/permits/applications-forms",
        "https://devhub.portlandoregon.gov",
    }
    assert all(job.manifest_only for job in manifest.jobs)
    assert all(
        job.processor.module.startswith(ALLOWED_PROCESSOR_MODULE_PREFIXES)
        for job in manifest.jobs
    )
    assert all(not job.processor.module.startswith("ppd.") for job in manifest.jobs)


def test_handoff_manifest_rejects_ppd_processor_forks() -> None:
    data = _fixture()
    data["processorJobs"][0]["processor"]["module"] = "ppd.crawler.forked_web_archiver"

    with pytest.raises(ValueError, match="PP&D fork|ipfs_datasets_py"):
        assert_valid_crawl_processor_handoff_manifest(data)


def test_handoff_manifest_rejects_private_devhub_paths() -> None:
    data = _fixture()
    data["processorJobs"][2]["sourceUrl"] = "https://devhub.portlandoregon.gov/account/permits"
    data["processorJobs"][2]["arguments"]["url"] = "https://devhub.portlandoregon.gov/account/permits"

    with pytest.raises(ValueError, match="private DevHub"):
        assert_valid_crawl_processor_handoff_manifest(data)


def test_handoff_manifest_rejects_raw_persistence_requests() -> None:
    data = _fixture()
    data["processorJobs"][0]["arguments"]["persistBody"] = True

    with pytest.raises(ValueError, match="raw body"):
        assert_valid_crawl_processor_handoff_manifest(data)


def test_handoff_manifest_rejects_credentials_and_trace_paths() -> None:
    data = _fixture()
    data["processorJobs"][0]["arguments"]["token"] = "not-allowed"
    data["processorJobs"][1]["arguments"]["tracePath"] = "ppd/data/private/devhub/session/trace.zip"

    with pytest.raises(ValueError, match="privacy validation"):
        assert_valid_crawl_processor_handoff_manifest(data)


@pytest.mark.parametrize(
    ("argument_patch", "message"),
    [
        ({"rawArchivePath": "ppd/archive/raw/landing.warc"}, "raw archive path"),
        ({"downloadedDocumentPath": "/tmp/ppd/form.pdf"}, "downloaded document path"),
        ({"raw_body": "raw response"}, "raw body field"),
        ({"callbackUrl": "http://127.0.0.1/private"}, "private URL"),
        ({"status": "skipped", "contentHash": "sha256:" + "a" * 64}, "skipped captures"),
        ({"allowLiveNetwork": True}, "side-effectful network execution flag"),
    ],
)
def test_handoff_manifest_rejects_unsafe_processor_invocation_arguments(
    argument_patch: dict[str, object],
    message: str,
) -> None:
    data = _fixture()
    data["processorJobs"][0]["arguments"].update(argument_patch)

    with pytest.raises(ValueError, match=message):
        assert_valid_crawl_processor_handoff_manifest(data)


def test_handoff_manifest_rejects_missing_processor_version_metadata() -> None:
    data = _fixture()
    data["processorJobs"][0]["processor"]["version"] = ""

    with pytest.raises(ValueError, match="version is required"):
        assert_valid_crawl_processor_handoff_manifest(data)
