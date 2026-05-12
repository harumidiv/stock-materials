from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Stock:
    code: str
    name: str
    market: str = ""
    price: str = ""
    change: str = ""


@dataclass(frozen=True)
class Material:
    source: str
    title: str
    url: str = ""
    published: str = ""
    snippet: str = ""
    score: int = 0
    keywords: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class StockReport:
    stock: Stock
    materials: tuple[Material, ...]
    summary: str
