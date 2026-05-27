from __future__ import annotations

from pathlib import Path

import pytest

from ppd.freshness_refresh_plan_validation import (
    assert_freshness_refresh_plan_is_live_crawl_safe,
    validate_freshness_refresh_plan,
)


FIXTURES = Path(__file__).parent / "fixtures" / "freshness_refresh"


def issue_codes(plan: dict[str, object]) -> set[str]:
    return {issue.code for issue in validate_freshness_refresh_plan(plan)}


def base_plan() -> dict[str, object]:
    return {
        "crawl_frequency": "P1D",
        "rate_limit_policy": {"requests_per_second": 0.2, "burst": 1},
        "seed_urls": ["https://www.portland.gov/bds"],
        "allowed_hosts": ["www.portland.gov"],
    }


def test_accepts_minimal_public_plan() -> None:
    assert validate_freshness_refresh_plan(base_plan()) == []
    assert_freshness_refresh_plan_is_live_crawl_safe(base_plan())


@pytest.mark.parametrize(
    "url",
    [
        "http://localhost:8000/devhub",
        "http://127.0.0.1/private",
        "http://10.0.0.5/crawl",
        "https://user:password@example.com/index.html",
        "https://www.portland.gov/login",
        "https://www.portland.gov/bds?token=secret",
    ],
)
def test_refuses_private_or_authenticated_urls(url: str) -> None:
    plan = base_plan()
    plan["seed_urls"] = [url]
    assert "private_or_authenticated_url" in issue_codes(plan)


@pytest.mark.parametrize("host", ["*", "*.portland.gov", ".portland.gov", "gov", "or.us", "https://www.portland.gov/bds"])
def test_refuses_over_broad_host_expansion(host: str) -> None:
    plan = base_plan()
    plan["allowed_hosts"] = [host]
    assert "over_broad_host_expansion" in issue_codes(plan)


def test_refuses_missing_crawl_frequency() -> None:
    plan = base_plan()
    del plan["crawl_frequency"]
    assert "missing_crawl_frequency" in issue_codes(plan)


def test_refuses_missing_rate_limit_policy() -> None:
    plan = base_plan()
    del plan["rate_limit_policy"]
    assert "missing_rate_limit_policy" in issue_codes(plan)


@pytest.mark.parametrize("key", ["raw_body_output_path", "raw_output_path", "body_output_path", "response_body_path"])
def test_refuses_raw_body_output_paths(key: str) -> None:
    plan = base_plan()
    plan[key] = str(FIXTURES / "raw-response.html")
    assert "raw_body_output_path_refused" in issue_codes(plan)


@pytest.mark.parametrize("key", ["download_dir", "downloaded_document_path", "downloaded_document_paths", "document_output_path"])
def test_refuses_downloaded_document_paths(key: str) -> None:
    plan = base_plan()
    plan[key] = str(FIXTURES / "downloaded.pdf")
    assert "downloaded_document_path_refused" in issue_codes(plan)


def test_assertion_raises_with_codes() -> None:
    plan = base_plan()
    del plan["crawl_frequency"]
    plan["raw_body_output_path"] = str(FIXTURES / "raw.html")

    with pytest.raises(ValueError) as error:
        assert_freshness_refresh_plan_is_live_crawl_safe(plan)

    message = str(error.value)
    assert "missing_crawl_frequency" in message
    assert "raw_body_output_path_refused" in message
