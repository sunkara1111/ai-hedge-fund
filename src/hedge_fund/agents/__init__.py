"""Seven specialized investment research agents."""

from hedge_fund.agents.market_scout import market_scout_agent
from hedge_fund.agents.technical import technical_agent
from hedge_fund.agents.fundamental import fundamental_agent
from hedge_fund.agents.news import news_agent
from hedge_fund.agents.quant import quant_agent
from hedge_fund.agents.risk import risk_agent
from hedge_fund.agents.portfolio import portfolio_agent

__all__ = [
    "market_scout_agent",
    "technical_agent",
    "fundamental_agent",
    "news_agent",
    "quant_agent",
    "risk_agent",
    "portfolio_agent",
]
