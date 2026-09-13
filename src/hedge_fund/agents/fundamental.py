"""Fundamental Analyst — financials and valuation."""

from __future__ import annotations

from typing import Any

from hedge_fund.state import AgentState
from hedge_fund.tools.market_data import fetch_quote


def _valuation_verdict(q: dict[str, Any]) -> tuple[str, int]:
    """Return (label, score 0-100) from simple fundamental heuristics."""
    score = 50
    pe = q.get("pe_ratio") or 0
    fpe = q.get("forward_pe") or pe
    growth = q.get("revenue_growth") or 0
    margin = q.get("profit_margin") or 0
    roe = q.get("roe") or 0
    dte = q.get("debt_to_equity") or 0

    if pe and 0 < pe < 25:
        score += 10
    elif pe and pe > 50:
        score -= 10
    if fpe and pe and fpe < pe:
        score += 8  # earnings expected to grow into valuation
    if growth and growth > 0.15:
        score += 12
    elif growth and growth < 0:
        score -= 10
    if margin and margin > 0.2:
        score += 10
    elif margin and margin < 0.05:
        score -= 5
    if roe and roe > 0.2:
        score += 8
    if dte and dte > 1.5:
        score -= 8
    elif dte is not None and dte < 0.5:
        score += 5

    score = int(max(0, min(100, score)))
    if score >= 70:
        label = "undervalued / attractive"
    elif score <= 40:
        label = "expensive / cautious"
    else:
        label = "fairly valued"
    return label, score


def fundamental_agent(state: AgentState) -> dict[str, Any]:
    demo = bool(state.get("demo"))
    ticker = (state.get("ticker") or "TSLA").upper()
    q = fetch_quote(ticker, demo=demo)
    verdict, score = _valuation_verdict(q)

    def fmt(v: Any, pct: bool = False) -> str:
        if v is None:
            return "n/a"
        if pct:
            return f"{float(v) * 100:.1f}%"
        if isinstance(v, float):
            return f"{v:.2f}"
        return str(v)

    mcap = q.get("market_cap") or 0
    mcap_str = f"${mcap/1e9:.1f}B" if mcap >= 1e9 else f"${mcap:,.0f}"

    report = "\n".join(
        [
            f"Fundamental Analysis — {ticker} ({q.get('name')})",
            f"  Sector/Industry: {q.get('sector')} / {q.get('industry')}",
            f"  Price: ${q.get('price')} | Market Cap: {mcap_str}",
            f"  P/E: {fmt(q.get('pe_ratio'))} | Forward P/E: {fmt(q.get('forward_pe'))}",
            f"  P/B: {fmt(q.get('pb_ratio'))} | P/S: {fmt(q.get('ps_ratio'))}",
            f"  EPS: {fmt(q.get('eps'))} | ROE: {fmt(q.get('roe'), pct=True)}",
            f"  Revenue growth: {fmt(q.get('revenue_growth'), pct=True)} | Profit margin: {fmt(q.get('profit_margin'), pct=True)}",
            f"  Debt/Equity: {fmt(q.get('debt_to_equity'))} | Beta: {fmt(q.get('beta'))}",
            f"  52w range: {q.get('52w_low')} – {q.get('52w_high')}",
            f"  Valuation verdict: {verdict} (score {score}/100)",
        ]
    )

    result = {
        "ticker": ticker,
        "quote": q,
        "valuation": verdict,
        "score": score,
        "recommendation": "buy" if score >= 65 else "sell" if score <= 40 else "hold",
        "summary": report,
    }

    sections = dict(state.get("report_sections") or {})
    sections["3. Fundamental Analyst"] = report

    return {"fundamental": result, "report_sections": sections}
