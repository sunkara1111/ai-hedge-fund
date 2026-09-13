"""Market data via yfinance, with demo fallbacks."""

from __future__ import annotations

from typing import Any

from hedge_fund.demo_data import (
    DEMO_UNIVERSE,
    get_demo_prices,
    get_demo_quote,
)


def fetch_quote(ticker: str, demo: bool = False) -> dict[str, Any]:
    """Fetch latest quote / fundamentals snapshot."""
    ticker = ticker.upper()
    if demo:
        return get_demo_quote(ticker)

    try:
        import yfinance as yf

        t = yf.Ticker(ticker)
        info = t.info or {}
        hist = t.history(period="5d")
        price = float(hist["Close"].iloc[-1]) if not hist.empty else float(info.get("currentPrice") or 0)
        prev = float(hist["Close"].iloc[-2]) if len(hist) >= 2 else price
        change_pct = ((price - prev) / prev * 100) if prev else 0.0

        return {
            "symbol": ticker,
            "name": info.get("shortName") or info.get("longName") or ticker,
            "price": price,
            "change_pct": round(change_pct, 2),
            "volume": int(info.get("volume") or 0),
            "avg_volume": int(info.get("averageVolume") or 0),
            "market_cap": int(info.get("marketCap") or 0),
            "sector": info.get("sector") or "Unknown",
            "industry": info.get("industry") or "Unknown",
            "pe_ratio": float(info.get("trailingPE") or 0) or None,
            "forward_pe": float(info.get("forwardPE") or 0) or None,
            "pb_ratio": float(info.get("priceToBook") or 0) or None,
            "ps_ratio": float(info.get("priceToSalesTrailing12Months") or 0) or None,
            "eps": float(info.get("trailingEps") or 0) or None,
            "revenue_growth": float(info.get("revenueGrowth") or 0) or None,
            "profit_margin": float(info.get("profitMargins") or 0) or None,
            "debt_to_equity": float(info.get("debtToEquity") or 0) / 100
            if info.get("debtToEquity")
            else None,
            "roe": float(info.get("returnOnEquity") or 0) or None,
            "beta": float(info.get("beta") or 1.0),
            "52w_high": float(info.get("fiftyTwoWeekHigh") or 0) or None,
            "52w_low": float(info.get("fiftyTwoWeekLow") or 0) or None,
            "dividend_yield": float(info.get("dividendYield") or 0) or 0.0,
        }
    except Exception:
        # Graceful fallback so the pipeline never hard-crashes
        return get_demo_quote(ticker)


def fetch_price_history(ticker: str, demo: bool = False, period: str = "3mo") -> list[float]:
    """Return list of closing prices (oldest → newest)."""
    ticker = ticker.upper()
    if demo:
        return get_demo_prices(ticker)

    try:
        import yfinance as yf

        hist = yf.Ticker(ticker).history(period=period)
        if hist.empty:
            return get_demo_prices(ticker)
        return [float(x) for x in hist["Close"].tolist()]
    except Exception:
        return get_demo_prices(ticker)


def rank_opportunities(
    tickers: list[str] | None = None,
    demo: bool = False,
) -> list[dict[str, Any]]:
    """Rank tickers by a simple opportunity score (momentum + liquidity + valuation)."""
    universe = [t.upper() for t in (tickers or DEMO_UNIVERSE)]
    ranked: list[dict[str, Any]] = []

    for sym in universe:
        q = fetch_quote(sym, demo=demo)
        prices = fetch_price_history(sym, demo=demo)
        momentum = 0.0
        if len(prices) >= 5:
            momentum = (prices[-1] - prices[-5]) / prices[-5] * 100

        vol_ratio = 1.0
        if q.get("avg_volume"):
            vol_ratio = (q.get("volume") or 0) / max(q["avg_volume"], 1)

        pe = q.get("pe_ratio") or 40
        # Lower PE slightly favored, but growth stocks not heavily punished
        valuation_score = max(0, 40 - abs(float(pe) - 25) * 0.5)

        score = (
            float(q.get("change_pct") or 0) * 2
            + momentum * 1.5
            + min(vol_ratio, 2.0) * 10
            + valuation_score
            + (10 if (q.get("revenue_growth") or 0) > 0.1 else 0)
        )
        ranked.append(
            {
                "ticker": sym,
                "name": q.get("name"),
                "price": q.get("price"),
                "change_pct": q.get("change_pct"),
                "momentum_5d": round(momentum, 2),
                "volume_ratio": round(vol_ratio, 2),
                "opportunity_score": round(score, 2),
                "sector": q.get("sector"),
            }
        )

    ranked.sort(key=lambda x: x["opportunity_score"], reverse=True)
    for i, row in enumerate(ranked, 1):
        row["rank"] = i
    return ranked
