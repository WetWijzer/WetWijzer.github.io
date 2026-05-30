from pathlib import Path

from ppd.public_source_refresh_launch_packet import (
    build_public_source_refresh_launch_packet,
    load_fixture_packet,
    validate_public_source_refresh_launch_packet,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "public_source_refresh_launch"


def test_builds_expected_fixture_first_launch_packet() -> None:
    inputs = load_fixture_packet(FIXTURE_DIR / "inputs.json")
    expected = load_fixture_packet(FIXTURE_DIR / "expected_launch_packet.json")

    actual = build_public_source_refresh_launch_packet(inputs)

    assert actual == expected


def test_launch_packet_stays_metadata_only() -> None:
    packet = build_public_source_refresh_launch_packet(load_fixture_packet(FIXTURE_DIR / "inputs.json"))

    validate_public_source_refresh_launch_packet(packet)
    assert packet["attestations"] == {
        "no_download": True,
        "no_processor": True,
        "no_registry_mutation": True,
        "no_schedule_mutation": True,
    }
    for record in packet["expected_metadata_only_result_records"]:
        assert record["document_downloaded"] is False
        assert record["processor_invoked"] is False
        assert record["registry_mutated"] is False
        assert record["schedule_mutated"] is False
