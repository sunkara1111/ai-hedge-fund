"""Risk Manager — stress tests, downside, position sizing; can REJECT trades."""

from __future__ import annotations

from typing import Any

from hedge_fund.config import get_settings
from hedge_fund.state import AgentState


def risk_agent(state: AgentState) -> dict[str, Any]:
    settings = get_settings()
    ticker = (state.get("ticker") or "TSLA").upper()
    portfolio_value = float(state.get("portfolio_value") or settings.portfolio_value)
    max_pct = settings.max_position_pct

    quant = state.get("quant") or {}
    tech = state.get("technical") or {}
    fund = state.get("fundamental") or {}
    news = state.get("news") or {}
    scout = state.get("market_scout") or {}

    quote = scout.get("quote") or fund.get("quote") or {}
    price = float(quote.get("price") or tech.get("price") or 100)
    beta = float(quote.get("beta") or 1.0)
    edge = float(quant.get("edge_score") or 50)
    win_prob = float(quant.get("win_probability") or 50)
    scenarios = quant.get("scenarios") or {}
    bear = scenarios.get("bear") or {"return_pct": -10, "price": price * 0.9}

    # Stress tests
    stress = {
        "market_crash_-20pct": {
            "portfolio_impact_pct": round(-20 * beta * max_pct * 100 / 100, 2),
            "position_loss_pct": round(-20 * beta, 2),
        },
        "bear_scenario": {
            "price": bear.get("price"),
            "return_pct": bear.get("return_pct"),
        },
        "gap_down_-8pct": {
            "dollar_loss_on_full_size": round(portfolio_value * max_pct * 0.08, 2),
        },
    }

    # Position sizing: Kelly-lite scaled by edge & constrained by max_pct
    edge_frac = max(0.0, (edge - 50) / 50)  # 0..1
    kelly_lite = max(0.0, (win_prob / 100 - (1 - win_prob / 100)) * 0.35)
    raw_pct = min(max_pct, max(0.0, (kelly_lite * 0.5 + edge_frac * max_pct)))
    # Floor a tiny size only if edge is clearly positive
    if edge >= 55 and raw_pct < 0.01:
        raw_pct = 0.02
    position_pct = round(raw_pct, 4)
    position_dollars = round(portfolio_value * position_pct, 2)
    shares = int(position_dollars // price) if price else 0

    # Rejection rules
    reasons: list[str] = []
    if edge < 42:
        reasons.append(f"edge_score too low ({edge} < 42)")
    if win_prob < 38:
        reasons.append(f"win_probability too low ({win_prob}% < 38%)")
    if tech.get("bias") == "overbought" and edge < 70:
        reasons.append("technical overbought without exceptional edge")
    if (news.get("sentiment") or {}).get("label") == "bearish" and edge < 60:
        reasons.append("bearish news tape with insufficient edge")
    if beta > 2.5 and position_pct > max_pct * 0.5:
        reasons.append(f"beta {beta} too high for proposed size")
    if float(bear.get("return_pct") or 0) < -25 and edge < 65:
        reasons.append("bear scenario downside exceeds risk appetite")

    trade_rejected = len(reasons) > 0 and edge < 55
    # Hard reject if multiple red flags
    if len(reasons) >= 2:
        trade_rejected = True
    if edge < 40:
        trade_rejected = True

    if trade_rejected:
        position_pct = 0.0
        position_dollars = 0.0
        shares = 0
        rejection_reason = "; ".join(reasons) or "risk limits breached"
        decision = "REJECT"
    else:
        rejection_reason = ""
        decision = "APPROVE"
        if not reasons:
            reasons = ["within risk limits"]

    max_loss = round(abs(float(bear.get("return_pct") or 10)) / 100 * position_dollars, 2)

    report_lines = [
        f"Risk Management — {ticker}",
        f"  Decision: {decision}",
        f"  Portfolio value: ${portfolio_value:,.0f}",
        f"  Proposed size: {position_pct*100:.2f}% (${position_dollars:,.2f} / {shares} shares @ ${price})",
        f"  Max position cap: {max_pct*100:.1f}%",
        f"  Est. max loss (bear): ${max_loss:,.2f}",
        f"  Beta: {beta}",
        "  Stress tests:",
        f"    Market -20%: position loss ≈ {stress['market_crash_-20pct']['position_loss_pct']}%",
        f"    Bear scenario: {bear.get('return_pct')}% → ${bear.get('price')}",
        f"    Gap -8%: ${stress['gap_down_-8pct']['dollar_loss_on_full_size']} on full-cap size",
        f"  Notes: {'; '.join(reasons)}",
    ]
    if trade_rejected:
        report_lines.append(f"  REJECTION REASON: {rejection_reason}")

    report = "\n".join(report_lines)

    result = {
        "ticker": ticker,
        "decision": decision,
        "trade_rejected": trade_rejected,
        "rejection_reason": rejection_reason,
        "position_pct": position_pct,
        "position_dollars": position_dollars,
        "shares": shares,
        "max_loss": max_loss,
        "stress": stress,
        "reasons": reasons,
        "summary": report,
    }

    sections = dict(state.get("report_sections") or {})
    sections["6. Risk Manager"] = report

    return {
        "risk": result,
        "trade_rejected": trade_rejected,
        "rejection_reason": rejection_reason,
        "report_sections": sections,
    }
