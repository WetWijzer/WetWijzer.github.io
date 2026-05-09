from __future__ import annotations

import json
from pathlib import Path

import pytest

from ppd.public_crawl_preflight import public_crawl_preflight_decision

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "public_crawl_preflight" / "cases.json"


def _load_cases() -> list[dict[str, object]]:
    with FIXTURE_PATH.open(encoding="utf-8") as fixture_file:
        return json.load(fixture_file)


@pytest.mark.parametrize("case", _load_cases(), ids=lambda case: str(case["name"]))
def test_public_crawl_preflight_decisions_from_fixtures(case: dict[str, object]) -> None:
    decision = public_crawl_preflight_decision(
        str(case["url"]),
        content_type=_optional_string(case.get("content_type")),
        linked_from_allowlisted_public_page=bool(case.get("linked_from_allowlisted_public_page", False)),
        raw_download=bool(case.get("raw_download", False)),
        headers=_optional_string_mapping(case.get("headers")),
    )

    assert decision.allowed is case["expected_allowed"]
    assert decision.reason == case["expected_reason"]


def test_fixture_covers_required_named_cases() -> None:
    case_names = {str(case["name"]) for case in _load_cases()}

    assert {
        "allowlisted_www_portland_gov",
        "allowlisted_devhub_portlandoregon_gov",
        "allowlisted_www_portlandoregon_gov",
        "linked_public_www_portlandmaps_com",
        "skip_outside_allowlist",
        "skip_unsupported_scheme",
        "skip_private_authenticated_path",
        "skip_raw_download_flag",
        "skip_unsupported_content_type",
    }.issubset(case_names)


def _optional_string(value: object) -> str | None:
    if value is None:
        return None
    assert isinstance(value, str)
    return value


def _optional_string_mapping(value: object) -> dict[str, str] | None:
    if value is None:
        return None
    assert isinstance(value, dict)
    return {str(key): str(item) for key, item in value.items()}
