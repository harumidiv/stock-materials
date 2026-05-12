from __future__ import annotations

from .models import Material, Stock


def demo_materials(stock: Stock) -> list[Material]:
    samples = {
        "3905": [
            Material(
                source="DEMO",
                title="（デモ）生成AI関連サービスの大型案件を受注",
                url="https://example.com/demo/3905",
                published="2026-05-08 15:30",
                snippet="受注、AI、データセンター関連のサンプル材料です。",
            )
        ],
        "6232": [
            Material(
                source="DEMO",
                title="（デモ）防衛関連向けドローンの採用拡大を発表",
                url="https://example.com/demo/6232",
                published="2026-05-08 12:00",
                snippet="防衛、承認、大型受注のサンプル材料です。",
            )
        ],
        "7162": [
            Material(
                source="DEMO",
                title="（デモ）自己株式取得と増配を発表",
                url="https://example.com/demo/7162",
                published="2026-05-08 16:00",
                snippet="自己株式、増配のサンプル材料です。",
            )
        ],
    }
    return samples.get(stock.code, [])
