from __future__ import annotations

from urllib.parse import quote

from .models import SocialReference, Stock


def build_social_references(stock: Stock) -> list[SocialReference]:
    yahoo_symbol = stock.code.upper()
    if not yahoo_symbol.endswith(".T"):
        yahoo_symbol = f"{yahoo_symbol}.T"

    search_query = quote(f"{stock.code} {stock.name} 株")
    x_query = quote(f'("{stock.code}" OR "{stock.name}") 株')

    return [
        SocialReference(
            source="Yahoo!ファイナンス掲示板",
            title=f"{stock.name}の掲示板",
            url=f"https://finance.yahoo.co.jp/quote/{yahoo_symbol}/bbs",
            note="匿名投稿のため、材料確定ではなく市場の受け止め確認用。",
        ),
        SocialReference(
            source="Yahoo!ファイナンス株つぶやき",
            title=f"{stock.name}の株つぶやき",
            url=f"https://finance.yahoo.co.jp/quote/{yahoo_symbol}/post",
            note="Yahoo!ファイナンス上で確認できるX由来の投稿欄。",
        ),
        SocialReference(
            source="X検索",
            title=f"{stock.name} / {stock.code} のX検索",
            url=f"https://x.com/search?q={x_query}&src=typed_query&f=live",
            note="公式APIなしでは自動取得せず、確認リンクとして出力。",
        ),
        SocialReference(
            source="Google検索",
            title=f"{stock.name} / {stock.code} の掲示板・SNS検索",
            url=f"https://www.google.com/search?q={search_query}%20掲示板%20Twitter%20X",
            note="表記ゆれや外部掲示板の補助確認用。",
        ),
    ]
