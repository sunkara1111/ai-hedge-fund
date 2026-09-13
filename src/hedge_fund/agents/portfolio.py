"""Portfolio Manager — final investment memo + allocation."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from hedge_fund.llm import enrich_text
from hedge_fund.state import AgentState


def portfolio_agent(state: AgentState) -> dict[str, Any]:
    ticker = (state.get("ticker") or "TSLA").upper()
    scout = state.get("market_scout") or {}
    tech = state.get("technical") or {}
    fund = state.get("fundamental") or {}
    news = state.get("news") or {}
    quant = state.get("quant") or {}
    risk = state.get("risk") or {}

    quote = scout.get("quote") or fund.get("quote") or {}
    name = quote.get("name") or ticker
    price = quote.get("price")
    edge = quant.get("edge_score")
    win_prob = quant.get("win_probability")
    expected = quant.get("expected_return")
    position_pct = risk.get("position_pct") or 0
    position_dollars = risk.get("position_dollars") or 0
    shares = risk.get("shares") or 0
    decision = risk.get("decision") or "APPROVE"

    # Consensus from analyst recommendations
    recs = [
        tech.get("recommendation"),
        fund.get("recommendation"),
        news.get("recommendation"),
        quant.get("recommendation"),
    ]
    buys = sum(1 for r in recs if r == "buy")
    sells = sum(1 for r in recs if r == "sell")
    if buys >= 3:
        action = "BUY"
    elif sells >= 3:
        action = "SELL / AVOID"
    elif decision == "REJECT":
        action = "PASS"
    else:
        action = "HOLD / WATCH"

    if decision == "REJECT":
        action = "PASS (risk rejected)"

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    scenarios = quant.get("scenarios") or {}
    demo = bool(state.get("demo"))

    llm_note = enrich_text(
        f"Write 3 short bullet points for an investment memo on {ticker}. "
        f"Edge={edge}, win_prob={win_prob}, action={action}. Be concise.",
        demo=demo,
        system=(
            "You are a portfolio manager. Paper trading research only. "
            "No advice disclaimers needed in bullets."
        ),
    )
    if llm_note:
        llm_block = "\n".join(f"  {line}" for line in llm_note.splitlines())
    else:
        llm_block = (
            "  (rule-based memo; set ANTHROPIC_API_KEY for live narrative)"
        )

    catalysts = news.get("catalysts") or ["None highlighted"]
    risks = news.get("risks") or risk.get("reasons") or ["Standard market risk"]
    catalyst_block = "\n".join(f"  • {c}" for c in catalysts)
    risk_block = "\n".join(f"  • {r}" for r in risks)

    memo = f"""
══════════════════════════════════════════════════════════════
 INVESTMENT MEMO — {ticker} ({name})
 Generated: {ts}
══════════════════════════════════════════════════════════════

RECOMMENDATION: {action}
Price: ${price} | Edge: {edge}/100 | Win Prob: {win_prob}%
Expected return: {expected}%

ALLOCATION
  Target weight: {float(position_pct)*100:.2f}%
  Notional: ${float(position_dollars):,.2f}
  Shares: {shares}
  Risk decision: {decision}

THESIS
  {scout.get('thesis') or 'Relative opportunity identified by Market Scout.'}
  Technical bias: {tech.get('bias')} / trend={tech.get('trend')} (score {tech.get('score')})
  Fundamentals: {fund.get('valuation')} (score {fund.get('score')})
  News tape: {(news.get('sentiment') or {}).get('label')} (score {news.get('score')})

SCENARIOS
  Bull: ${scenarios.get('bull', {}).get('price')} ({scenarios.get('bull', {}).get('return_pct')}%)
  Base: ${scenarios.get('base', {}).get('price')} ({scenarios.get('base', {}).get('return_pct')}%)
  Bear: ${scenarios.get('bear', {}).get('price')} ({scenarios.get('bear', {}).get('return_pct')}%)

LLM NOTES
{llm_block}

KEY CATALYSTS
{catalyst_block}

KEY RISKS
{risk_block}

ANALYST CONSENSUS
  Technical={tech.get('recommendation')} | Fundamental={fund.get('recommendation')}
  News={news.get('recommendation')} | Quant={quant.get('recommendation')}
  Votes → buy:{buys} sell:{sells}

DISCLAIMER
  Paper / research only. Not financial advice. Past patterns and
  simulated scores do not guarantee future results.
══════════════════════════════════════════════════════════════
""".strip()

    report = memo

    result = {
        "ticker": ticker,
        "action": action,
        "allocation_pct": position_pct,
        "allocation_dollars": position_dollars,
        "shares": shares,
        "memo": memo,
        "summary": report,
    }

    sections = dict(state.get("report_sections") or {})
    sections["7. Portfolio Manager"] = report

    return {
        "portfolio": result,
        "investment_memo": memo,
        "report_sections": sections,
    }
