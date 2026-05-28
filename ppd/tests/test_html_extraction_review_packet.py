import json
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "html_extraction_review"
HTML_FIXTURE = FIXTURE_DIR / "synthetic_ppd_public_page.html"
PACKET_FIXTURE = FIXTURE_DIR / "synthetic_ppd_public_page_review_packet.json"
BASE_URL = "https://www.portland.gov/ppd/synthetic-public-permit-guide"


class ReviewPacketParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.items = []
        self._stack = []
        self._capture = None
        self._buffer = []
        self._in_title = False
        self._title_parts = []
        self._breadcrumb_depth = 0
        self._breadcrumb_items = []
        self._ol_stack = []
        self._current_steps = None
        self._pending_heading = None
        self._current_callout = None
        self._current_table = None
        self._current_row = None
        self._current_cell = None
        self._current_contact = None
        self._related_depth = 0
        self._related_links = []
        self._current_href = None
        self._current_image_src = None
        self._current_image_alt = None

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        attrs_dict = {name.lower(): value or "" for name, value in attrs}
        self._stack.append((tag, attrs_dict))

        if tag == "title":
            self._in_title = True
            return

        if tag == "nav" and attrs_dict.get("aria-label") == "Breadcrumb":
            self._breadcrumb_depth = len(self._stack)
            return

        if tag == "section" and "contact-card" in attrs_dict.get("class", "").split():
            self._current_contact = {"name": "", "methods": []}
            return

        if tag == "section" and "related-links" in attrs_dict.get("class", "").split():
            self._related_depth = len(self._stack)
            self._related_links = []
            return

        if tag == "aside" and "callout" in attrs_dict.get("class", "").split():
            severity = "warning" if "warning" in attrs_dict.get("class", "").split() else "note"
            self._current_callout = {"severity": severity, "heading": "", "text": ""}
            return

        if tag == "img":
            alt = attrs_dict.get("alt", "").strip()
            src = attrs_dict.get("src", "").strip()
            if alt:
                self.items.append(
                    {
                        "kind": "image_alt_text",
                        "id": "image-synthetic-permit-workflow",
                        "src": urljoin(BASE_URL, src),
                        "alt": alt,
                    }
                )
            return

        if tag == "ol" and not self._breadcrumb_depth:
            self._ol_stack.append([])
            return

        if tag == "table":
            self._current_table = {"caption": "", "headers": [], "rows": []}
            return

        if tag == "tr" and self._current_table is not None:
            self._current_row = []
            return

        if tag in {"td", "th"} and self._current_row is not None:
            self._start_capture(tag)
            return

        if tag == "a":
            self._current_href = attrs_dict.get("href") or ""
            self._start_capture("a")
            return

        if tag in {"h1", "h2", "h3", "p", "li", "caption"}:
            self._start_capture(tag)

    def handle_data(self, data):
        if self._in_title:
            self._title_parts.append(data)
        if self._capture is not None:
            self._buffer.append(data)

    def handle_endtag(self, tag):
        tag = tag.lower()
        text = ""
        if self._capture == tag:
            text = _clean("".join(self._buffer))
            self._capture = None
            self._buffer = []

        if tag == "title":
            self._in_title = False
            title = _clean("".join(self._title_parts))
            self.items.append({"kind": "title", "id": "title", "text": title})

        elif tag in {"h1", "h2", "h3"} and text:
            if self._current_callout is not None and tag == "h3":
                self._current_callout["heading"] = text
            elif self._current_contact is not None:
                pass
            elif self._related_depth:
                pass
            else:
                level = int(tag[1])
                self.items.append(
                    {
                        "kind": "heading",
                        "id": f"heading-{tag}-{_slug(text)}",
                        "level": level,
                        "text": text,
                    }
                )
                self._pending_heading = text

        elif tag == "p" and text:
            if text.startswith(("Published ", "Updated ")):
                self.items.append(
                    {
                        "kind": "visible_date",
                        "id": f"date-{_slug(text)}",
                        "text": text,
                    }
                )
            elif self._current_callout is not None:
                self._current_callout["text"] = text
            elif self._current_contact is not None:
                _add_contact_text(self._current_contact, text)

        elif tag == "li" and text:
            if self._breadcrumb_depth:
                self._breadcrumb_items.append(text)
            elif self._ol_stack:
                self._ol_stack[-1].append(text)

        elif tag == "a" and text:
            if self._related_depth and self._current_href:
                self._related_links.append({"text": text, "href": urljoin(BASE_URL, self._current_href)})
            self._current_href = None

        elif tag == "caption" and text and self._current_table is not None:
            self._current_table["caption"] = text

        elif tag in {"td", "th"} and text and self._current_row is not None:
            self._current_row.append((tag, text))

        elif tag == "tr" and self._current_row is not None and self._current_table is not None:
            values = [value for _cell_tag, value in self._current_row]
            if self._current_row and all(cell_tag == "th" for cell_tag, _value in self._current_row):
                self._current_table["headers"] = values
            elif values:
                self._current_table["rows"].append(values)
            self._current_row = None

        elif tag == "table" and self._current_table is not None:
            caption = self._current_table["caption"]
            self.items.append(
                {
                    "kind": "table",
                    "id": f"table-{_slug(caption)}",
                    "caption": caption,
                    "headers": self._current_table["headers"],
                    "rows": self._current_table["rows"],
                }
            )
            self._current_table = None

        elif tag == "aside" and self._current_callout is not None:
            heading = self._current_callout["heading"]
            self.items.append(
                {
                    "kind": "callout",
                    "id": f"callout-{_slug(heading)}",
                    "severity": self._current_callout["severity"],
                    "heading": heading,
                    "text": self._current_callout["text"],
                }
            )
            self._current_callout = None

        elif tag == "ol" and self._ol_stack:
            steps = self._ol_stack.pop()
            if steps:
                heading = self._pending_heading or "steps"
                self.items.append(
                    {
                        "kind": "steps",
                        "id": f"steps-{_slug(heading)}",
                        "items": [
                            {"number": index + 1, "text": value}
                            for index, value in enumerate(steps)
                        ],
                    }
                )

        elif tag == "nav" and self._breadcrumb_depth:
            self.items.append(
                {
                    "kind": "breadcrumbs",
                    "id": "breadcrumbs",
                    "items": self._breadcrumb_items,
                }
            )
            self._breadcrumb_depth = 0

        elif tag == "section" and self._current_contact is not None:
            self.items.append(
                {
                    "kind": "contact",
                    "id": "contact-permit-help",
                    "name": self._current_contact["name"],
                    "methods": self._current_contact["methods"],
                }
            )
            self._current_contact = None

        elif tag == "section" and self._related_depth:
            self.items.append(
                {
                    "kind": "related_links",
                    "id": "related-links",
                    "links": self._related_links,
                }
            )
            self._related_depth = 0

        if self._stack:
            self._stack.pop()

    def _start_capture(self, tag):
        self._capture = tag
        self._buffer = []


def test_review_packet_matches_fixture_extraction_order():
    parser = ReviewPacketParser()
    parser.feed(HTML_FIXTURE.read_text(encoding="utf-8"))
    parser.close()

    packet = json.loads(PACKET_FIXTURE.read_text(encoding="utf-8"))
    expected_items = [{key: value for key, value in item.items() if key != "order"} for item in packet["source_order"]]

    assert parser.items == expected_items
    assert [item["order"] for item in packet["source_order"]] == list(range(1, len(packet["source_order"]) + 1))


def test_review_packet_covers_required_public_page_signals():
    packet = json.loads(PACKET_FIXTURE.read_text(encoding="utf-8"))
    kinds = [item["kind"] for item in packet["source_order"]]

    for required_kind in (
        "title",
        "breadcrumbs",
        "heading",
        "steps",
        "callout",
        "table",
        "contact",
        "related_links",
        "image_alt_text",
        "visible_date",
    ):
        assert required_kind in kinds

    assert [date["normalized_date"] for date in packet["visible_dates"]] == ["2026-05-01", "2026-05-08"]


def test_citation_spans_are_ordered_and_anchor_to_blocks():
    packet = json.loads(PACKET_FIXTURE.read_text(encoding="utf-8"))
    block_ids = {item["id"] for item in packet["source_order"]}
    citation_orders = [span["source_order"] for span in packet["citation_spans"]]

    assert citation_orders == sorted(citation_orders)
    assert len(citation_orders) == len(set(citation_orders))
    for span in packet["citation_spans"]:
        assert span["block_id"] in block_ids
        assert span["text"].strip()


def _add_contact_text(contact, text):
    if text == "PP&D Permit Help":
        contact["name"] = text
    elif text.startswith("Phone: "):
        contact["methods"].append({"type": "phone", "value": text.removeprefix("Phone: ")})
    elif text.startswith("Email: "):
        contact["methods"].append({"type": "email", "value": text.removeprefix("Email: ")})
    elif text.startswith("Hours: "):
        contact["methods"].append({"type": "hours", "value": text.removeprefix("Hours: ")})


def _clean(value):
    return " ".join(value.split())


def _slug(value):
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug


if __name__ == "__main__":
    unittest.main()
