from __future__ import annotations

from urllib.request import Request, urlopen


USER_AGENT = (
    "Mozilla/5.0 (compatible; stock-materials-prototype/0.1; "
    "+https://github.com/)"
)


def fetch_text(url: str, timeout: int = 20) -> str:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=timeout) as response:
        raw = response.read()
        charset = response.headers.get_content_charset() or "utf-8"
    return raw.decode(charset, errors="replace")
