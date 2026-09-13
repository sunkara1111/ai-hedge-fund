"""News Analyst — headlines, catalysts, sentiment."""

from __future__ import annotations

from typing import Any

from hedge_fund.state import AgentState
from hedge_fund.tools.news import aggregate_sentiment, fetch_news


def news_agent(state: AgentState) -> dict[str, Any]:
    demo = bool(state.get("demo"))
    ticker = (state.get("ticker") or "TSLA").upper()
    articles = fetch_news(ticker, demo=demo)
    sentiment = aggregate_sentiment(articles)

    lines = [
        f"News & Catalyst Analysis — {ticker}",
        f"  Aggregate sentiment: {sentiment['label']} (score={sentiment['score']})",
        f"  Breakdown: +{sentiment['positive']} / -{sentiment['negative']} / ~{sentiment['neutral']}",
        "  Headlines:",
    ]
    for a in articles:
        lines.append(f"    [{a['sentiment'].upper()}] {a['title']} — {a['source']}")
        if a.get("summary"):
            lines.append(f"      {a['summary'][:160]}")

    catalysts = [
        a["title"] for a in articles if a.get("sentiment") == "positive"
    ][:3]
    risks = [a["title"] for a in articles if a.get("sentiment") == "negative"][:3]

    if catalysts:
        lines.append("  Key catalysts:")
        for c in catalysts:
            lines.append(f"    • {c}")
    if risks:
        lines.append("  Headline risks:")
        for r in risks:
            lines.append(f"    • {r}")

    score = int(50 + sentiment["score"] * 40)
    score = max(0, min(100, score))
    report = "\n".join(lines)

    result = {
        "ticker": ticker,
        "articles": articles,
        "sentiment": sentiment,
        "catalysts": catalysts,
        "risks": risks,
        "score": score,
        "recommendation": (
            "buy" if score >= 65 else "sell" if score <= 35 else "hold"
        ),
        "summary": report,
    }

    sections = dict(state.get("report_sections") or {})
    sections["4. News Analyst"] = report

    return {"news": result, "report_sections": sections}
