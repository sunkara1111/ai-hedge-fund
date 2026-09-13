"""Market Scout — finds and ranks investment opportunities."""

from __future__ import annotations

from typing import Any

from hedge_fund.demo_data import DEMO_UNIVERSE
from hedge_fund.state import AgentState
from hedge_fund.tools.market_data import fetch_quote, rank_opportunities


def market_scout_agent(state: AgentState) -> dict[str, Any]:
    demo = bool(state.get("demo"))
    ticker = (state.get("ticker") or "").upper()
    scan_list = state.get("tickers") or ([ticker] if ticker else DEMO_UNIVERSE)

    opportunities = rank_opportunities(scan_list if len(scan_list) > 1 else DEMO_UNIVERSE, demo=demo)

    # If analyzing a single ticker, ensure it is featured
    focus = ticker or (opportunities[0]["ticker"] if opportunities else "TSLA")
    quote = fetch_quote(focus, demo=demo)
    focus_rank = next((o for o in opportunities if o["ticker"] == focus), None)

    summary_lines = [
        f"Market Scout scanned {len(opportunities)} names.",
        f"Focus ticker: {focus} ({quote.get('name')}) @ ${quote.get('price')}",
        f"Day change: {quote.get('change_pct')}% | Sector: {quote.get('sector')}",
    ]
    if focus_rank:
        summary_lines.append(
            f"Opportunity rank: #{focus_rank['rank']} | score={focus_rank['opportunity_score']}"
        )
    summary_lines.append("Top opportunities:")
    for o in opportunities[:5]:
        summary_lines.append(
            f"  #{o['rank']} {o['ticker']}: score={o['opportunity_score']} "
            f"({o['change_pct']}% / mom5d={o['momentum_5d']}%)"
        )

    report = "\n".join(summary_lines)
    result = {
        "focus_ticker": focus,
        "quote": quote,
        "opportunities": opportunities[:10],
        "thesis": (
            f"{focus} selected for deep-dive based on relative momentum, "
            f"liquidity, and sector positioning."
        ),
        "summary": report,
    }

    sections = dict(state.get("report_sections") or {})
    sections["1. Market Scout"] = report

    return {
        "ticker": focus,
        "market_scout": result,
        "opportunities": opportunities[:10],
        "report_sections": sections,
    }
