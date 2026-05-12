from __future__ import annotations

from datetime import date, timedelta
from email.utils import parsedate_to_datetime
from urllib.parse import quote
from xml.etree import ElementTree

from .http_tools import fetch_text
from .html_tools import html_to_text
from .models import Material, Stock


def fetch_news_materials(stock: Stock, target_date: date, limit: int = 5, max_age_days: int = 14) -> list[Material]:
    query = quote(f'"{stock.name}" OR "{stock.code}" 株 材料 上方修正 増配 受注 提携 when:{max_age_days}d')
    url = f"https://news.google.com/rss/search?q={query}&hl=ja&gl=JP&ceid=JP:ja"
    try:
        xml = fetch_text(url)
    except Exception:
        return []
    return parse_google_news_rss(xml, target_date=target_date, limit=limit, max_age_days=max_age_days)


def parse_google_news_rss(xml: str, target_date: date, limit: int, max_age_days: int) -> list[Material]:
    try:
        root = ElementTree.fromstring(xml)
    except ElementTree.ParseError:
        return []

    materials: list[Material] = []
    oldest = target_date - timedelta(days=max_age_days)
    for item in root.findall(".//item"):
        title = item.findtext("title", default="").strip()
        link = item.findtext("link", default="").strip()
        published = item.findtext("pubDate", default="").strip()
        description = html_to_text(item.findtext("description", default=""))
        published_date = parse_rss_date(published)
        if published_date and not (oldest <= published_date <= target_date + timedelta(days=1)):
            continue
        if title:
            materials.append(
                Material(
                    source="Google News",
                    title=title,
                    url=link,
                    published=published,
                    snippet=description[:240],
                )
            )
        if len(materials) >= limit:
            break
    return materials


def parse_rss_date(value: str) -> date | None:
    try:
        return parsedate_to_datetime(value).date()
    except Exception:
        return None
