"""Quant Analyst — edge score, win probability, scenarios, factors."""

from __future__ import annotations

from typing import Any

from hedge_fund.state import AgentState


def quant_agent(state: AgentState) -> dict[str, Any]:
    ticker = (state.get("ticker") or "TSLA").upper()
    tech = state.get("technical") or {}
    fund = state.get("fundamental") or {}
    news = state.get("news") or {}
    scout = state.get("market_scout") or {}

    t_score = float(tech.get("score") or 50)
    f_score = float(fund.get("score") or 50)
    n_score = float(news.get("score") or 50)
    opp = 50.0
    for o in state.get("opportunities") or []:
        if o.get("ticker") == ticker:
            # normalize opportunity score roughly into 0-100
            opp = min(100.0, max(0.0, float(o.get("opportunity_score", 50)) / 1.2))
            break

    # Factor model weights
    weights = {
        "technical": 0.30,
        "fundamental": 0.30,
        "news": 0.20,
        "momentum": 0.20,
    }
    edge_score = (
        t_score * weights["technical"]
        + f_score * weights["fundamental"]
        + n_score * weights["news"]
        + opp * weights["momentum"]
    )
    edge_score = round(edge_score, 1)

    # Logistic-ish win probability from edge
    win_prob = round(1 / (1 + pow(2.71828, -(edge_score - 50) / 12)) * 100, 1)

    quote = (scout.get("quote") or fund.get("quote") or {})
    price = float(quote.get("price") or tech.get("price") or 100)
    beta = float(quote.get("beta") or 1.0)

    # Scenario tree (± based on edge + beta)
    upside = price * (1 + 0.08 * (edge_score / 50) * (1 + 0.2 * beta))
    base = price * (1 + 0.02 * ((edge_score - 50) / 50))
    downside = price * (1 - 0.08 * (1 + 0.15 * beta) * (1.2 - edge_score / 100))

    scenarios = {
        "bull": {"price": round(upside, 2), "return_pct": round((upside / price - 1) * 100, 1), "prob": round(win_prob * 0.45, 1)},
        "base": {"price": round(base, 2), "return_pct": round((base / price - 1) * 100, 1), "prob": round(100 - win_prob * 0.55, 1)},
        "bear": {"price": round(downside, 2), "return_pct": round((downside / price - 1) * 100, 1), "prob": round(max(5, 100 - win_prob) * 0.5, 1)},
    }
    # Normalize scenario probs roughly
    ssum = scenarios["bull"]["prob"] + scenarios["base"]["prob"] + scenarios["bear"]["prob"]
    if ssum:
        for k in scenarios:
            scenarios[k]["prob"] = round(scenarios[k]["prob"] / ssum * 100, 1)

    factors = {
        "technical_momentum": round(t_score, 1),
        "fundamental_quality": round(f_score, 1),
        "news_sentiment": round(n_score, 1),
        "relative_strength": round(opp, 1),
        "volatility_proxy_beta": round(beta, 2),
    }

    expected_return = round(
        (
            scenarios["bull"]["return_pct"] * scenarios["bull"]["prob"]
            + scenarios["base"]["return_pct"] * scenarios["base"]["prob"]
            + scenarios["bear"]["return_pct"] * scenarios["bear"]["prob"]
        )
        / 100,
        2,
    )

    report = "\n".join(
        [
            f"Quant Analysis — {ticker}",
            f"  Edge score: {edge_score}/100",
            f"  Win probability: {win_prob}%",
            f"  Expected return (scenario-weighted): {expected_return}%",
            "  Factor contributions:",
            f"    Technical momentum: {factors['technical_momentum']}",
            f"    Fundamental quality: {factors['fundamental_quality']}",
            f"    News sentiment: {factors['news_sentiment']}",
            f"    Relative strength: {factors['relative_strength']}",
            f"    Beta: {factors['volatility_proxy_beta']}",
            "  Scenarios:",
            f"    Bull: ${scenarios['bull']['price']} ({scenarios['bull']['return_pct']}%) p={scenarios['bull']['prob']}%",
            f"    Base: ${scenarios['base']['price']} ({scenarios['base']['return_pct']}%) p={scenarios['base']['prob']}%",
            f"    Bear: ${scenarios['bear']['price']} ({scenarios['bear']['return_pct']}%) p={scenarios['bear']['prob']}%",
        ]
    )

    result = {
        "ticker": ticker,
        "edge_score": edge_score,
        "win_probability": win_prob,
        "expected_return": expected_return,
        "factors": factors,
        "scenarios": scenarios,
        "weights": weights,
        "recommendation": (
            "buy" if edge_score >= 62 else "sell" if edge_score <= 40 else "hold"
        ),
        "summary": report,
    }

    sections = dict(state.get("report_sections") or {})
    sections["5. Quant Analyst"] = report

    return {"quant": result, "report_sections": sections}
