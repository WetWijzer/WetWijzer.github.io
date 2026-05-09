"""Deterministic public HTML extraction helpers for PP&D fixtures.

This module intentionally accepts HTML that has already been supplied by tests or
other callers. It does not fetch URLs, persist downloaded pages, or perform live
crawl behavior.
"""

from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Iterable
from urllib.parse import urljoin


_IGNORED_TAGS = {"script", "style", "noscript", "template", "svg"}
_BLOCK_TAGS = {
    "address",
    "article",
    "aside",
    "blockquote",
    "br",
    "dd",
    "div",
    "dl",
    "dt",
    "figcaption",
    "figure",
    "footer",
    "form",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "header",
    "hr",
    "li",
    "main",
    "nav",
    "ol",
    "p",
    "pre",
    "section",
    "table",
    "td",
    "th",
    "tr",
    "ul",
}


@dataclass(frozen=True)
class PublicHtmlLink:
    """A link discovered in public HTML, preserving document order."""

    text: str
    href: str


@dataclass(frozen=True)
class PublicHtmlExtraction:
    """Normalized visible text and links from a public HTML document."""

    title: str
    text: str
    links: tuple[PublicHtmlLink, ...]


class _PublicHtmlParser(HTMLParser):
    def __init__(self, base_url: str | None) -> None:
        super().__init__(convert_charrefs=True)
        self._base_url = base_url
        self._ignored_depth = 0
        self._in_title = False
        self._active_href: str | None = None
        self._active_link_parts: list[str] = []
        self._text_parts: list[str] = []
        self._title_parts: list[str] = []
        self.links: list[PublicHtmlLink] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag in _IGNORED_TAGS:
            self._ignored_depth += 1
            return
        if self._ignored_depth:
            return
        if tag == "title":
            self._in_title = True
            return
        if tag in _BLOCK_TAGS:
            self._append_text_boundary()
        if tag == "a" and self._active_href is None:
            href = _attrs_to_dict(attrs).get("href")
            if href:
                self._active_href = urljoin(self._base_url, href) if self._base_url else href
                self._active_link_parts = []

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in _IGNORED_TAGS:
            if self._ignored_depth:
                self._ignored_depth -= 1
            return
        if self._ignored_depth:
            return
        if tag == "title":
            self._in_title = False
            return
        if tag == "a" and self._active_href is not None:
            link_text = _normalize_whitespace(" ".join(self._active_link_parts))
            self.links.append(PublicHtmlLink(text=link_text, href=self._active_href))
            self._active_href = None
            self._active_link_parts = []
        if tag in _BLOCK_TAGS:
            self._append_text_boundary()

    def handle_data(self, data: str) -> None:
        if self._ignored_depth:
            return
        if self._in_title:
            self._title_parts.append(data)
        self._text_parts.append(data)
        if self._active_href is not None:
            self._active_link_parts.append(data)

    def normalized(self) -> PublicHtmlExtraction:
        return PublicHtmlExtraction(
            title=_normalize_whitespace(" ".join(self._title_parts)),
            text=_normalize_whitespace(" ".join(self._text_parts)),
            links=tuple(self.links),
        )

    def _append_text_boundary(self) -> None:
        if self._text_parts and self._text_parts[-1] != " ":
            self._text_parts.append(" ")
        if self._active_href is not None and self._active_link_parts and self._active_link_parts[-1] != " ":
            self._active_link_parts.append(" ")


def extract_public_html(html: str, *, base_url: str | None = None) -> PublicHtmlExtraction:
    """Extract normalized public HTML text and links while preserving source order."""

    parser = _PublicHtmlParser(base_url)
    parser.feed(html)
    parser.close()
    return parser.normalized()


def _attrs_to_dict(attrs: Iterable[tuple[str, str | None]]) -> dict[str, str]:
    return {name.lower(): value for name, value in attrs if value is not None}


def _normalize_whitespace(value: str) -> str:
    return " ".join(value.split())
