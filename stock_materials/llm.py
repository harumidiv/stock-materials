from __future__ import annotations

import os
import shlex
import subprocess

from .models import Material, Stock


def summarize(stock: Stock, materials: list[Material], use_llm: bool) -> str:
    if use_llm:
        llm_summary = summarize_with_local_llm(stock, materials)
        if llm_summary:
            return llm_summary
    return summarize_by_rules(stock, materials)


def summarize_by_rules(stock: Stock, materials: list[Material]) -> str:
    if not materials:
        return "材料候補は見つかりませんでした。銘柄名の表記ゆれ、開示前の思惑、需給要因の可能性があります。"

    best = materials[0]
    if best.keywords:
        reason = "、".join(best.keywords[:4])
        return f"最有力候補は「{best.title}」。キーワードは {reason}。"
    return f"最有力候補は「{best.title}」。根拠URLを確認して、株価反応との時刻関係を見るのがよさそうです。"


def summarize_with_local_llm(stock: Stock, materials: list[Material]) -> str:
    command = os.getenv("LOCAL_LLM_CMD", "").strip()
    if not command:
        return ""

    prompt = build_prompt(stock, materials)
    if "{prompt}" in command:
        command = command.replace("{prompt}", shlex.quote(prompt))
        stdin = None
    else:
        stdin = prompt

    try:
        completed = subprocess.run(
            command,
            input=stdin,
            text=True,
            shell=True,
            capture_output=True,
            timeout=int(os.getenv("LOCAL_LLM_TIMEOUT", "120")),
            check=False,
        )
    except Exception:
        return ""

    output = completed.stdout.strip()
    if completed.returncode != 0 or not output:
        return ""
    return output.splitlines()[0][:300]


def build_prompt(stock: Stock, materials: list[Material]) -> str:
    lines = [
        "あなたは日本株の材料確認を補助するアナリストです。",
        "投資助言ではなく、根拠付きの材料候補だけを短く要約してください。",
        f"銘柄: {stock.name} ({stock.code})",
        "候補:",
    ]
    for material in materials[:8]:
        lines.append(
            f"- source={material.source} score={material.score} "
            f"title={material.title} published={material.published} url={material.url}"
        )
    lines.append("出力: 最有力候補、補足候補、確認すべき根拠URLを日本語で1文。")
    return "\n".join(lines)
