from __future__ import annotations

from html import unescape
from html.parser import HTMLParser
from urllib.parse import urljoin


class TableParser(HTMLParser):
    def __init__(self, base_url: str = "") -> None:
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.rows: list[list[str]] = []
        self.row_links: list[list[str]] = []
        self._in_row = False
        self._in_cell = False
        self._current_row: list[str] = []
        self._current_links: list[str] = []
        self._cell_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "tr":
            self._in_row = True
            self._current_row = []
            self._current_links = []
        elif tag in {"td", "th"} and self._in_row:
            self._in_cell = True
            self._cell_text = []
        elif tag == "a" and self._in_row:
            href = dict(attrs).get("href")
            if href:
                self._current_links.append(urljoin(self.base_url, href))

    def handle_data(self, data: str) -> None:
        if self._in_cell:
            self._cell_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag in {"td", "th"} and self._in_cell:
            text = normalize_text("".join(self._cell_text))
            self._current_row.append(text)
            self._in_cell = False
        elif tag == "tr" and self._in_row:
            if any(cell for cell in self._current_row):
                self.rows.append(self._current_row)
                self.row_links.append(self._current_links)
            self._in_row = False


def normalize_text(value: str) -> str:
    return " ".join(unescape(value).replace("\xa0", " ").split())


def html_to_text(value: str) -> str:
    class TextParser(HTMLParser):
        def __init__(self) -> None:
            super().__init__(convert_charrefs=True)
            self.parts: list[str] = []

        def handle_data(self, data: str) -> None:
            data = normalize_text(data)
            if data:
                self.parts.append(data)

    parser = TextParser()
    parser.feed(value)
    return normalize_text(" ".join(parser.parts))
