"""LangGraph workflow wiring the 7 agents.

Flow:
  Market Scout → fan-out (Technical | Fundamental | News) → Quant → Risk
  → (if rejected END else Portfolio Manager) → END
"""

from __future__ import annotations

from typing import Any, Literal

from langgraph.graph import END, START, StateGraph

from hedge_fund.agents.fundamental import fundamental_agent
from hedge_fund.agents.market_scout import market_scout_agent
from hedge_fund.agents.news import news_agent
from hedge_fund.agents.portfolio import portfolio_agent
from hedge_fund.agents.quant import quant_agent
from hedge_fund.agents.risk import risk_agent
from hedge_fund.agents.technical import technical_agent
from hedge_fund.state import AgentState


def _route_after_risk(state: AgentState) -> Literal["portfolio_manager", "__end__"]:
    if state.get("trade_rejected"):
        return "__end__"
    return "portfolio_manager"


def build_graph():
    """Compile the multi-agent investment research graph."""
    g: StateGraph = StateGraph(AgentState)

    g.add_node("market_scout", market_scout_agent)
    g.add_node("technical_analyst", technical_agent)
    g.add_node("fundamental_analyst", fundamental_agent)
    g.add_node("news_analyst", news_agent)
    g.add_node("quant_analyst", quant_agent)
    g.add_node("risk_manager", risk_agent)
    g.add_node("portfolio_manager", portfolio_agent)

    g.add_edge(START, "market_scout")

    # Fan-out from Market Scout to the three parallel analysts
    g.add_edge("market_scout", "technical_analyst")
    g.add_edge("market_scout", "fundamental_analyst")
    g.add_edge("market_scout", "news_analyst")

    # Fan-in to Quant (LangGraph waits for all upstream nodes)
    g.add_edge("technical_analyst", "quant_analyst")
    g.add_edge("fundamental_analyst", "quant_analyst")
    g.add_edge("news_analyst", "quant_analyst")

    g.add_edge("quant_analyst", "risk_manager")

    g.add_conditional_edges(
        "risk_manager",
        _route_after_risk,
        {
            "portfolio_manager": "portfolio_manager",
            "__end__": END,
        },
    )
    g.add_edge("portfolio_manager", END)

    return g.compile()


def run_analysis(
    ticker: str,
    *,
    demo: bool = False,
    portfolio_value: float | None = None,
    tickers: list[str] | None = None,
) -> dict[str, Any]:
    """Run the full pipeline for a ticker (or scan universe)."""
    from hedge_fund.config import get_settings

    settings = get_settings()
    graph = build_graph()
    initial: AgentState = {
        "ticker": ticker.upper() if ticker else "",
        "demo": demo,
        "portfolio_value": portfolio_value or settings.portfolio_value,
        "report_sections": {},
        "errors": [],
        "trade_rejected": False,
    }
    if tickers:
        initial["tickers"] = [t.upper() for t in tickers]

    return graph.invoke(initial)
