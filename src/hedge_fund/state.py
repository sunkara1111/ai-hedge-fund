"""Shared LangGraph agent state."""

from __future__ import annotations

import operator
from typing import Annotated, Any, TypedDict


def merge_dicts(left: dict[str, Any] | None, right: dict[str, Any] | None) -> dict[str, Any]:
    """Reducer so parallel analysts can each append report sections."""
    out = dict(left or {})
    out.update(right or {})
    return out


class AgentState(TypedDict, total=False):
    """State passed through the multi-agent investment graph."""

    # Inputs
    ticker: str
    tickers: list[str]
    demo: bool
    portfolio_value: float

    # Market Scout
    market_scout: dict[str, Any]
    opportunities: list[dict[str, Any]]

    # Parallel analyst reports
    technical: dict[str, Any]
    fundamental: dict[str, Any]
    news: dict[str, Any]

    # Quant
    quant: dict[str, Any]

    # Risk
    risk: dict[str, Any]
    trade_rejected: bool
    rejection_reason: str

    # Portfolio Manager
    portfolio: dict[str, Any]
    investment_memo: str

    # Aggregate report sections for CLI (merged across parallel nodes)
    report_sections: Annotated[dict[str, str], merge_dicts]
    errors: Annotated[list[str], operator.add]
