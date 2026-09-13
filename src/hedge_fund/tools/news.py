"""News / catalyst fetchers with demo fallback."""

from __future__ import annotations

from typing import Any

from hedge_fund.demo_data import get_demo_news


def fetch_news(ticker: str, demo: bool = False, limit: int = 5) -> list[dict[str, Any]]:
    """Fetch recent headlines for a ticker."""
    ticker = ticker.upper()
    if demo:
        return get_demo_news(ticker)[:limit]

    try:
        import yfinance as yf

        items = yf.Ticker(ticker).news or []
        out: list[dict[str, Any]] = []
        for item in items[:limit]:
            # yfinance news schema varies by version
            content = item.get("content") or item
            title = (
                content.get("title")
                or item.get("title")
                or "Untitled"
            )
            summary = (
                content.get("summary")
                or content.get("description")
                or item.get("summary")
                or ""
            )
            publisher = ""
            if isinstance(content.get("provider"), dict):
                publisher = content["provider"].get("displayName", "")
            publisher = publisher or item.get("publisher") or "Yahoo Finance"

            # Crude keyword sentiment
            text = f"{title} {summary}".lower()
            pos = sum(
                1
                for w in (
                    "beat",
                    "growth",
                    "surge",
                    "record",
                    "upgrade",
                    "bullish",
                    "expand",
                    "strong",
                )
                if w in text
            )
            neg = sum(
                1
                for w in (
                    "miss",
                    "cut",
                    "lawsuit",
                    "downgrade",
                    "weak",
                    "probe",
                    "decline",
                    "risk",
                )
                if w in text
            )
            if pos > neg:
                sentiment = "positive"
            elif neg > pos:
                sentiment = "negative"
            else:
                sentiment = "neutral"

            out.append(
                {
                    "title": title,
                    "sentiment": sentiment,
                    "source": publisher,
                    "summary": summary[:280] if summary else title,
                }
            )
        return out or get_demo_news(ticker)[:limit]
    except Exception:
        return get_demo_news(ticker)[:limit]


def aggregate_sentiment(articles: list[dict[str, Any]]) -> dict[str, Any]:
    if not articles:
        return {"label": "neutral", "score": 0.0, "positive": 0, "negative": 0, "neutral": 0}
    counts = {"positive": 0, "negative": 0, "neutral": 0}
    for a in articles:
        s = a.get("sentiment", "neutral")
        counts[s] = counts.get(s, 0) + 1
    total = len(articles)
    score = (counts["positive"] - counts["negative"]) / total
    if score > 0.2:
        label = "bullish"
    elif score < -0.2:
        label = "bearish"
    else:
        label = "neutral"
    return {"label": label, "score": round(score, 3), **counts}
