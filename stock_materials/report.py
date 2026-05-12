from __future__ import annotations

from datetime import date, datetime

from .models import StockReport


def render_markdown(target_date: date, reports: list[StockReport], source: str) -> str:
    lines = [
        f"# ストップ高材料候補レポート ({target_date.isoformat()})",
        "",
        f"- ストップ高ソース: `{source}`",
        f"- 生成時刻: {datetime.now().isoformat(timespec='seconds')}",
        "- 注意: 自動収集による材料候補です。投資判断ではなく、必ず一次情報を確認してください。",
        "",
    ]

    if not reports:
        lines.append("対象銘柄が見つかりませんでした。")
        return "\n".join(lines) + "\n"

    for report in reports:
        stock = report.stock
        heading = f"## {stock.name} ({stock.code})"
        if stock.market:
            heading += f" / {stock.market}"
        lines.extend([heading, "", report.summary, ""])
        if stock.price or stock.change:
            lines.append(f"- 株価メモ: {stock.price} {stock.change}".strip())

        if report.materials:
            lines.append("- 材料候補:")
            for material in report.materials[:6]:
                keywords = f" / keywords: {', '.join(material.keywords)}" if material.keywords else ""
                published = f" / {material.published}" if material.published else ""
                url = f" / {material.url}" if material.url else ""
                lines.append(
                    f"  - score {material.score}: {material.source}{published} / {material.title}{keywords}{url}"
                )
        else:
            lines.append("- 材料候補: なし")

        if report.social_references:
            lines.append("- 市場の声チェック:")
            for reference in report.social_references:
                note = f" / {reference.note}" if reference.note else ""
                lines.append(f"  - {reference.source}: {reference.title} / {reference.url}{note}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"
