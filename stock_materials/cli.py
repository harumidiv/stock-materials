from __future__ import annotations

import argparse
from datetime import date, datetime
from pathlib import Path

from .demo import demo_materials
from .llm import summarize
from .models import StockReport
from .news import fetch_news_materials
from .report import render_markdown
from .scoring import score_materials
from .social import build_social_references
from .stop_high import load_stop_high
from .tdnet import fetch_tdnet_materials


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Find likely catalysts behind Japanese limit-up stocks."
    )
    parser.add_argument("--date", default=date.today().isoformat(), help="Target date, YYYY-MM-DD")
    parser.add_argument(
        "--stop-source",
        choices=["stockmaster", "yahoo", "csv", "sample"],
        default="stockmaster",
        help="Where to get limit-up stocks from.",
    )
    parser.add_argument("--stop-csv", help="CSV path for --stop-source csv")
    parser.add_argument("--limit", type=int, default=15, help="Maximum number of stocks to inspect")
    parser.add_argument("--tdnet-days", type=int, default=3, help="TDnet lookback days")
    parser.add_argument("--include-news", action="store_true", help="Also search Google News RSS")
    parser.add_argument(
        "--include-social",
        action="store_true",
        help="Add Yahoo Finance board, stock-post, and X search reference links.",
    )
    parser.add_argument("--use-llm", action="store_true", help="Use LOCAL_LLM_CMD if available")
    parser.add_argument("--demo", action="store_true", help="Use built-in sample materials instead of network")
    parser.add_argument("--output", default="", help="Markdown output path")
    args = parser.parse_args(argv)

    target_date = datetime.strptime(args.date, "%Y-%m-%d").date()
    stocks = load_stop_high(args.stop_source, args.stop_csv, args.limit)

    reports: list[StockReport] = []
    for stock in stocks:
        if args.demo:
            materials = demo_materials(stock)
        else:
            materials = fetch_tdnet_materials(stock, target_date, args.tdnet_days)
            if args.include_news:
                materials.extend(fetch_news_materials(stock, target_date))

        scored = score_materials(materials)
        reports.append(
            StockReport(
                stock=stock,
                materials=tuple(scored),
                summary=summarize(stock, scored, use_llm=args.use_llm),
                social_references=tuple(build_social_references(stock)) if args.include_social else (),
            )
        )

    markdown = render_markdown(target_date, reports, args.stop_source)
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown, encoding="utf-8")
    else:
        print(markdown)

    return 0
