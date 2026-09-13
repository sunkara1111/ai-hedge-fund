"""Smoke tests for the LangGraph multi-agent pipeline (demo mode)."""

from __future__ import annotations

from hedge_fund.graph import build_graph, run_analysis
from hedge_fund.tools.indicators import compute_indicators


def test_build_graph_compiles():
    g = build_graph()
    assert g is not None


def test_indicators_basic():
    prices = [100 + i * 0.5 for i in range(30)]
    ind = compute_indicators(prices)
    assert "rsi" in ind
    assert "macd" in ind
    assert 0 <= ind["score"] <= 100


def test_analyze_tsla_demo_produces_all_sections():
    result = run_analysis("TSLA", demo=True, portfolio_value=100_000)
    assert result["ticker"] == "TSLA"
    assert result.get("demo") is True
    sections = result.get("report_sections") or {}

    required = [
        "1. Market Scout",
        "2. Technical Analyst",
        "3. Fundamental Analyst",
        "4. News Analyst",
        "5. Quant Analyst",
        "6. Risk Manager",
    ]
    for key in required:
        assert key in sections, f"missing section: {key}"
        assert sections[key].strip(), f"empty section: {key}"

    assert "market_scout" in result
    assert "technical" in result
    assert "fundamental" in result
    assert "news" in result
    assert "quant" in result
    assert "risk" in result
    assert "trade_rejected" in result

    # If approved, portfolio memo must exist; if rejected, reason must exist
    if result["trade_rejected"]:
        assert result.get("rejection_reason")
    else:
        assert result.get("investment_memo")
        assert "7. Portfolio Manager" in sections
        assert "INVESTMENT MEMO" in result["investment_memo"]


def test_quant_edge_score_present():
    result = run_analysis("AAPL", demo=True)
    q = result["quant"]
    assert "edge_score" in q
    assert "win_probability" in q
    assert "scenarios" in q
