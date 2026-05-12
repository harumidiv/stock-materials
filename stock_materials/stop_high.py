from __future__ import annotations

import csv
import re
from pathlib import Path

from .html_tools import TableParser, html_to_text
from .http_tools import fetch_text
from .models import Stock


STOCKMASTER_URL = "https://stockmaster.jp/stocksearch/stophigh/"
YAHOO_STOP_HIGH_URL = "https://finance.yahoo.co.jp/stocks/ranking/stopHigh?market=tokyoAll"
CODE_RE = re.compile(r"\b(?:\d{4}|\d{3}[A-Z])\b")


def load_stop_high(source: str, csv_path: str | None, limit: int) -> list[Stock]:
    if source == "sample":
        stocks = sample_stop_high()
    elif source == "csv":
        if not csv_path:
            raise ValueError("--stop-csv is required when --stop-source csv is used")
        stocks = load_stop_high_csv(Path(csv_path))
    elif source == "stockmaster":
        stocks = fetch_stockmaster_stop_high()
    elif source == "yahoo":
        stocks = fetch_yahoo_stop_high()
    else:
        raise ValueError(f"Unknown stop-high source: {source}")

    return dedupe_stocks(stocks)[:limit]


def sample_stop_high() -> list[Stock]:
    return [
        Stock(code="3905", name="データセクション", market="東証GRT", price="2,089", change="+400"),
        Stock(code="6232", name="ACSL", market="東証GRT", price="2,927", change="+500"),
        Stock(code="7162", name="アストマックス", market="東証STD", price="458", change="+80"),
    ]


def load_stop_high_csv(path: Path) -> list[Stock]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = csv.DictReader(handle)
        stocks = []
        for row in rows:
            code = (row.get("code") or row.get("コード") or "").strip().upper()
            name = (row.get("name") or row.get("会社名") or row.get("銘柄名") or "").strip()
            if code and name:
                stocks.append(
                    Stock(
                        code=code,
                        name=name,
                        market=(row.get("market") or row.get("市場") or "").strip(),
                        price=(row.get("price") or row.get("株価") or "").strip(),
                        change=(row.get("change") or row.get("前日比") or "").strip(),
                    )
                )
    return stocks


def fetch_stockmaster_stop_high() -> list[Stock]:
    html = fetch_text(STOCKMASTER_URL)
    return parse_stop_high_rows(html, STOCKMASTER_URL)


def fetch_yahoo_stop_high() -> list[Stock]:
    html = fetch_text(YAHOO_STOP_HIGH_URL)
    return parse_stop_high_rows(html, YAHOO_STOP_HIGH_URL)


def parse_stop_high_rows(html: str, base_url: str = "") -> list[Stock]:
    parser = TableParser(base_url)
    parser.feed(html)

    stocks: list[Stock] = []
    for row in parser.rows:
        stock = stock_from_cells(row)
        if stock:
            stocks.append(stock)

    if stocks:
        return stocks

    text = html_to_text(html)
    return stocks_from_text(text)


def stock_from_cells(cells: list[str]) -> Stock | None:
    cleaned = [cell for cell in cells if cell]
    if len(cleaned) >= 10 and cleaned[0].isdigit() and extract_code(cleaned[1]) == cleaned[1]:
        return Stock(
            code=cleaned[1],
            name=cleanup_name(cleaned[2]),
            price=cleaned[6],
            change=f"{cleaned[-2]} / {cleaned[-1]}",
        )

    for index, cell in enumerate(cleaned):
        code = extract_code(cell)
        if not code:
            continue

        if cell == code and index + 1 < len(cleaned):
            name = cleaned[index + 1]
        else:
            name = extract_name_near_code(cell, code)
            if not name and index > 0:
                name = cleaned[index - 1]

        if not name or name == code:
            continue

        market = ""
        for candidate in cleaned:
            if "東証" in candidate or "名証" in candidate or "札証" in candidate or "福証" in candidate:
                market = candidate
                break

        price = cleaned[index + 2] if index + 2 < len(cleaned) else ""
        change = cleaned[index + 3] if index + 3 < len(cleaned) else ""
        return Stock(code=code, name=cleanup_name(name), market=market, price=price, change=change)
    return None


def stocks_from_text(text: str) -> list[Stock]:
    parts = text.split()
    stocks: list[Stock] = []
    for i, part in enumerate(parts):
        code = extract_code(part)
        if not code:
            continue
        before = parts[i - 1] if i > 0 else ""
        after = parts[i + 1] if i + 1 < len(parts) else ""
        name = cleanup_name(before if before and not extract_code(before) else after)
        if name:
            stocks.append(Stock(code=code, name=name))
    return stocks


def extract_code(text: str) -> str:
    match = CODE_RE.search(text.upper())
    return match.group(0) if match else ""


def extract_name_near_code(text: str, code: str) -> str:
    lines = [item.strip() for item in re.split(r"[\n\r]+|\s{2,}", text) if item.strip()]
    for index, line in enumerate(lines):
        if code not in line:
            continue
        if index > 0 and not extract_code(lines[index - 1]):
            return lines[index - 1]
        line_without_code = line.replace(code, "").strip()
        if line_without_code:
            return line_without_code
        if index + 1 < len(lines):
            return lines[index + 1]
    return ""


def cleanup_name(name: str) -> str:
    name = re.sub(r"\(株\)|株式会社|掲示板", "", name)
    name = re.sub(r"\s+", " ", name).strip(" -|/")
    return name.strip()


def dedupe_stocks(stocks: list[Stock]) -> list[Stock]:
    seen: set[str] = set()
    unique: list[Stock] = []
    for stock in stocks:
        key = stock.code
        if key in seen:
            continue
        seen.add(key)
        unique.append(stock)
    return unique
