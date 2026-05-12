from __future__ import annotations

from datetime import date, datetime, timedelta

from .html_tools import TableParser
from .http_tools import fetch_text
from .models import Material, Stock


TDNET_LIST_URL = "https://www.release.tdnet.info/inbs/I_list_001_{yyyymmdd}.html"


def fetch_tdnet_materials(stock: Stock, target_date: date, lookback_days: int) -> list[Material]:
    materials: list[Material] = []
    for offset in range(lookback_days):
        day = target_date - timedelta(days=offset)
        url = TDNET_LIST_URL.format(yyyymmdd=day.strftime("%Y%m%d"))
        try:
            html = fetch_text(url)
        except Exception:
            continue
        materials.extend(parse_tdnet_materials(html, stock, day, url))
    return materials


def parse_tdnet_materials(html: str, stock: Stock, published_date: date, base_url: str) -> list[Material]:
    parser = TableParser(base_url)
    parser.feed(html)

    items: list[Material] = []
    for row, links in zip(parser.rows, parser.row_links):
        if not row_matches_stock(row, stock.code):
            continue
        title = guess_title(row)
        if not title:
            continue
        published_time = guess_time(row)
        published = published_date.isoformat()
        if published_time:
            published = f"{published} {published_time}"
        pdf_url = next((link for link in links if link.lower().endswith(".pdf")), links[0] if links else "")
        items.append(
            Material(
                source="TDnet",
                title=title,
                url=pdf_url,
                published=published,
                snippet="適時開示情報",
            )
        )
    return items


def row_matches_stock(row: list[str], code: str) -> bool:
    normalized = normalize_code(code)
    for cell in row:
        cell_code = normalize_code(cell)
        if cell_code == normalized or cell_code.startswith(normalized):
            return True
    return False


def normalize_code(value: str) -> str:
    return "".join(ch for ch in value.upper() if ch.isdigit() or ("A" <= ch <= "Z"))[:4]


def guess_title(row: list[str]) -> str:
    candidates = [
        cell
        for cell in row
        if len(cell) >= 8
        and not cell.replace(":", "").isdigit()
        and not normalize_code(cell) == cell[:4].upper()
    ]
    if not candidates:
        return ""
    return max(candidates, key=len)


def guess_time(row: list[str]) -> str:
    for cell in row:
        try:
            datetime.strptime(cell, "%H:%M")
            return cell
        except ValueError:
            continue
    return ""
