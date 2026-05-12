from __future__ import annotations

from dataclasses import replace

from .models import Material


KEYWORD_WEIGHTS = {
    "上方修正": 8,
    "増配": 8,
    "自社株買い": 7,
    "自己株式": 7,
    "TOB": 9,
    "公開買付": 9,
    "資本業務提携": 7,
    "業務提携": 6,
    "大型受注": 7,
    "受注": 5,
    "承認": 5,
    "黒字転換": 8,
    "最高益": 7,
    "株式分割": 6,
    "配当予想": 6,
    "AI": 4,
    "人工知能": 4,
    "半導体": 4,
    "データセンター": 4,
    "防衛": 3,
    "宇宙": 3,
    "M&A": 5,
    "合併": 5,
}

RISK_KEYWORDS = {
    "下方修正": -5,
    "減配": -6,
    "赤字": -2,
    "増資": -3,
    "第三者割当": -2,
}


def score_materials(materials: list[Material]) -> list[Material]:
    scored = [score_material(material) for material in materials]
    return sorted(scored, key=lambda item: (item.score, item.published), reverse=True)


def score_material(material: Material) -> Material:
    haystack = f"{material.title}\n{material.snippet}".upper()
    score = 0
    hits: list[str] = []

    for keyword, weight in KEYWORD_WEIGHTS.items():
        if keyword.upper() in haystack:
            score += weight
            hits.append(keyword)

    for keyword, weight in RISK_KEYWORDS.items():
        if keyword.upper() in haystack:
            score += weight
            hits.append(keyword)

    if material.source == "TDnet":
        score += 3
    if material.url:
        score += 1

    return replace(material, score=score, keywords=tuple(hits))
