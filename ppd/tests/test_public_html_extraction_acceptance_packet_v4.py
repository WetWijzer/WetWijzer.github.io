import json
from pathlib import Path


FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "public_html_extraction_acceptance_v4"
    / "synthetic_ppd_records_v4.json"
)


def load_packet():
    with FIXTURE_PATH.open("r", encoding="utf-8") as fixture_file:
        return json.load(fixture_file)


def test_acceptance_packet_v4_is_fixture_first_and_offline():
    packet = load_packet()

    assert packet["packet_id"] == "public-html-extraction-acceptance-v4"
    assert packet["packet_version"] == 4
    assert packet["fixture_only"] is True
    assert packet["network_access_required"] is False
    assert packet["devhub_access_required"] is False
    assert packet["processor_execution_required"] is False
    assert packet["raw_body_persisted"] is False
    assert packet["offline_validation_commands"] == [
        ["python3", "-m", "py_compile", "ppd/tests/test_public_html_extraction_acceptance_packet_v4.py"],
        ["python3", "-m", "pytest", "ppd/tests/test_public_html_extraction_acceptance_packet_v4.py"],
        ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
    ]


def test_synthetic_records_cover_public_html_extraction_fields():
    records = load_packet()["records"]

    assert len(records) == 2
    for record in records:
        assert record["document_id"].startswith("synthetic-ppd-public-html-")
        assert record["document_type"] == "public_html"
        assert record["language"] == "en"
        assert record["title"]
        assert record["breadcrumbs"][0] == "Portland.gov"
        assert "Portland Permitting & Development" in record["breadcrumbs"]
        assert record["visible_updated_date"] == "2026-05-08"
        assert 0.85 <= record["extraction_confidence"] <= 1.0
        assert record["human_review_status"] in {"accepted_fixture", "hold_for_reviewer"}

        headings = record["headings"]
        assert headings[0]["level"] == 1
        assert [heading["order"] for heading in headings] == list(range(1, len(headings) + 1))
        assert all(1 <= heading["level"] <= 6 for heading in headings)

        steps = record["ordered_steps"]
        assert [step["number"] for step in steps] == list(range(1, len(steps) + 1))
        assert all(step["text"] for step in steps)

        assert record["callouts"]
        assert any(callout["kind"] == "warning" for callout in record["callouts"])

        table = record["tables"][0]
        assert table["caption"]
        assert table["headers"]
        assert table["rows"]
        assert all(len(row) == len(table["headers"]) for row in table["rows"])

        contact = record["contact_blocks"][0]
        assert contact["label"]
        assert contact["phone"].startswith("503-")
        assert contact["email"].endswith(".invalid")
        assert "Monday" in contact["hours"]

        assert all(link["url"].startswith("https://www.portland.gov/") for link in record["related_links"])

        download = record["downloadable_links"][0]
        assert download["download"] is True
        assert download["file_type"] == "pdf"
        assert download["metadata"]["content_type"] == "application/pdf"
        assert download["metadata"]["requires_authentication"] is False

        for span in record["citation_spans"]:
            assert span["field"]
            assert isinstance(span["start"], int)
            assert isinstance(span["end"], int)
            assert span["start"] < span["end"]
            assert span["source_text"]


def test_reviewer_holds_are_explicit_when_required():
    records = load_packet()["records"]
    held_records = [record for record in records if record["human_review_status"] == "hold_for_reviewer"]

    assert held_records
    for record in held_records:
        assert record["reviewer_holds"]
        for hold in record["reviewer_holds"]:
            assert hold["reason"]
            assert hold["field"]
            assert hold["note"]


def test_fixture_does_not_persist_raw_body_or_live_artifacts():
    packet_text = FIXTURE_PATH.read_text(encoding="utf-8").lower()
    forbidden_tokens = [
        "raw_html",
        "raw_body",
        "cookie",
        "authorization",
        "auth_state",
        "har",
        "trace.zip",
        "screenshot",
        "captcha",
        "mfa",
        "payment_detail",
    ]

    for token in forbidden_tokens:
        assert token not in packet_text
