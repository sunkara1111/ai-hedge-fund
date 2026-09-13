"""Technical Analyst — RSI, MACD, MAs, trend, bias."""

from __future__ import annotations

from typing import Any

from hedge_fund.state import AgentState
from hedge_fund.tools.indicators import compute_indicators
from hedge_fund.tools.market_data import fetch_price_history


def technical_agent(state: AgentState) -> dict[str, Any]:
    demo = bool(state.get("demo"))
    ticker = (state.get("ticker") or "TSLA").upper()
    prices = fetch_price_history(ticker, demo=demo)
    ind = compute_indicators(prices)

    report = "\n".join(
        [
            f"Technical Analysis — {ticker}",
            f"  Price: ${ind['price']}",
            f"  RSI(14): {ind['rsi']} → {ind['bias']}",
            f"  MACD: {ind['macd'].get('macd')} | signal={ind['macd'].get('signal')} | hist={ind['macd'].get('histogram')}",
            f"  SMA20: {ind['sma_20']} | SMA50: {ind['sma_50']} | EMA12: {ind['ema_12']}",
            f"  Trend: {ind['trend']} | Bias: {ind['bias']}",
            f"  Signal balance: {ind['bullish_signals']} bullish / {ind['bearish_signals']} bearish",
            f"  Technical score: {ind['score']}/100",
        ]
    )

    result = {
        **ind,
        "ticker": ticker,
        "recommendation": (
            "buy"
            if ind["score"] >= 65
            else "sell"
            if ind["score"] <= 35
            else "hold"
        ),
        "summary": report,
    }

    sections = dict(state.get("report_sections") or {})
    sections["2. Technical Analyst"] = report

    return {"technical": result, "report_sections": sections}
