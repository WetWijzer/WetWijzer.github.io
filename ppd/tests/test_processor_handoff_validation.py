from __future__ import annotations

from ppd.processor_handoff_validation import validate_processor_handoff_packet


def valid_packet() -> dict[str, object]:
    return {
        "policy_preflight_evidence": {
            "policy_id": "ppd-preflight-v1",
            "checked_at": "2026-05-28T00:00:00Z",
        },
        "processor_contract_id": "processor-contract-v1",
        "rate_limit": {"max_requests": 3, "per_seconds": 60},
        "artifacts": [
            {
                "id": "ordinance-index",
                "kind": "metadata",
                "metadata_only": True,
                "source_url": "https://www.portland.gov/code/1",
            }
        ],
    }


def assert_rejected(packet: dict[str, object], expected: str) -> None:
    errors = validate_processor_handoff_packet(packet)
    assert any(expected in error for error in errors), errors


def test_accepts_metadata_only_bounded_handoff_packet() -> None:
    assert validate_processor_handoff_packet(valid_packet()) == []


def test_rejects_missing_policy_preflight_evidence() -> None:
    packet = valid_packet()
    packet.pop("policy_preflight_evidence")
    assert_rejected(packet, "missing policy preflight evidence")


def test_rejects_missing_processor_contract_identifier() -> None:
    packet = valid_packet()
    packet["processor_contract_id"] = ""
    assert_rejected(packet, "missing processor contract identifier")


def test_rejects_live_network_flags() -> None:
    packet = valid_packet()
    packet["allow_live_network"] = True
    assert_rejected(packet, "live network flag")


def test_rejects_raw_archive_or_body_fields() -> None:
    packet = valid_packet()
    packet["raw_body"] = "raw response"
    assert_rejected(packet, "raw archive/body field")


def test_rejects_local_downloaded_paths() -> None:
    packet = valid_packet()
    packet["downloaded_path"] = "/tmp/ppd/raw.pdf"
    assert_rejected(packet, "local downloaded path")


def test_rejects_private_or_authenticated_urls() -> None:
    packet = valid_packet()
    packet["source_url"] = "https://user:secret@example.test/archive"
    assert_rejected(packet, "private or authenticated URL")


def test_rejects_private_network_urls() -> None:
    packet = valid_packet()
    packet["source_url"] = "http://127.0.0.1:8080/archive"
    assert_rejected(packet, "private or authenticated URL")


def test_rejects_unbounded_rate_limits() -> None:
    packet = valid_packet()
    packet["rate_limit"] = "unlimited"
    assert_rejected(packet, "missing bounded rate limit")


def test_rejects_artifacts_that_are_not_metadata_only() -> None:
    packet = valid_packet()
    packet["artifacts"] = [{"id": "raw-doc", "metadata_only": False}]
    assert_rejected(packet, "metadata-only")


def test_rejects_artifact_raw_payloads_even_when_marked_metadata_only() -> None:
    packet = valid_packet()
    packet["artifacts"] = [{"id": "raw-doc", "metadata_only": True, "body": "raw"}]
    assert_rejected(packet, "non-metadata field")
