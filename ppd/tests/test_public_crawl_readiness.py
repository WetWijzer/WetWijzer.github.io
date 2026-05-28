from __future__ import annotations

from datetime import datetime, timezone

from ppd.crawler.public_crawl_readiness import validate_public_crawl_readiness


def test_public_crawl_readiness_accepts_minimal_safe_packet() -> None:
    packet = {
        "url": "https://www.portland.gov/code/33",
        "source_anchors": [
            {
                "url": "https://www.portland.gov/code/33",
                "observed_at": "2026-05-20T00:00:00Z",
            }
        ],
        "robots_status": "allowed",
        "policy_status": "approved",
        "rate_limit": {"requests_per_minute": 6},
    }

    errors = validate_public_crawl_readiness(
        packet,
        now=datetime(2026, 5, 27, tzinfo=timezone.utc),
    )

    assert errors == []


def test_public_crawl_readiness_refuses_unsafe_handoff_packet() -> None:
    packet = {
        "url": "https://user:pass@example.test/private?token=secret",
        "source_anchors": [
            {
                "url": "http://127.0.0.1/admin",
                "observed_at": "2026-01-01T00:00:00Z",
                "downloaded_document_path": "ppd/tmp/document.pdf",
            }
        ],
        "robots_status": "unknown",
        "policy_status": "pending",
        "live_network": True,
        "raw_body": "",
    }

    errors = validate_public_crawl_readiness(
        packet,
        now=datetime(2026, 5, 27, tzinfo=timezone.utc),
    )

    joined = "\n".join(errors)
    assert "credentials" in joined
    assert "private" in joined
    assert "timestamp is stale" in joined
    assert "downloaded document paths" in joined
    assert "raw bodies" in joined
    assert "live-network" in joined
    assert "robots status" in joined
    assert "policy status" in joined
    assert "rate limit" in joined
