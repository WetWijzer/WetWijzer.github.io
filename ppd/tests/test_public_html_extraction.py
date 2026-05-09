from pathlib import Path

from ppd.public_html_extraction import extract_public_html


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "public_html"


def test_extract_public_html_preserves_fixture_link_order() -> None:
    html = (FIXTURE_DIR / "order_fixture.html").read_text(encoding="utf-8")

    extracted = extract_public_html(html, base_url="https://www.portland.gov/notices/index.html")

    assert extracted.title == "PP&D Public Ordering Fixture"
    assert [link.text for link in extracted.links] == [
        "B permit packet",
        "A land use review",
        "C final decision",
    ]
    assert [link.href for link in extracted.links] == [
        "https://www.portland.gov/b-permit.pdf",
        "https://www.portland.gov/a-land-use.pdf",
        "https://www.portland.gov/c-final.pdf",
    ]


def test_extract_public_html_normalizes_visible_text_without_script_or_style() -> None:
    html = (FIXTURE_DIR / "order_fixture.html").read_text(encoding="utf-8")

    extracted = extract_public_html(html)

    assert "Public notices Documents are listed" in extracted.text
    assert "window.__raw_download" not in extracted.text
    assert "display: none" not in extracted.text
