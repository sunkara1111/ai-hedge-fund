"""Canned market data and rule-based outputs for --demo mode (no API keys)."""

from __future__ import annotations

from typing import Any

# Universe used by `scan --demo`
DEMO_UNIVERSE = ["TSLA", "AAPL", "NVDA", "MSFT", "AMZN", "META", "GOOGL"]

DEMO_QUOTES: dict[str, dict[str, Any]] = {
    "TSLA": {
        "symbol": "TSLA",
        "name": "Tesla, Inc.",
        "price": 248.50,
        "change_pct": 2.35,
        "volume": 95_000_000,
        "avg_volume": 80_000_000,
        "market_cap": 790_000_000_000,
        "sector": "Consumer Cyclical",
        "industry": "Auto Manufacturers",
        "pe_ratio": 62.5,
        "forward_pe": 48.0,
        "pb_ratio": 12.1,
        "ps_ratio": 8.4,
        "eps": 3.98,
        "revenue_growth": 0.18,
        "profit_margin": 0.095,
        "debt_to_equity": 0.18,
        "roe": 0.22,
        "beta": 2.05,
        "52w_high": 299.29,
        "52w_low": 138.80,
        "dividend_yield": 0.0,
    },
    "AAPL": {
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "price": 227.80,
        "change_pct": 0.85,
        "volume": 52_000_000,
        "avg_volume": 55_000_000,
        "market_cap": 3_450_000_000_000,
        "sector": "Technology",
        "industry": "Consumer Electronics",
        "pe_ratio": 34.2,
        "forward_pe": 29.5,
        "pb_ratio": 52.0,
        "ps_ratio": 8.9,
        "eps": 6.66,
        "revenue_growth": 0.06,
        "profit_margin": 0.26,
        "debt_to_equity": 1.45,
        "roe": 1.47,
        "beta": 1.25,
        "52w_high": 237.23,
        "52w_low": 164.08,
        "dividend_yield": 0.0044,
    },
    "NVDA": {
        "symbol": "NVDA",
        "name": "NVIDIA Corporation",
        "price": 128.40,
        "change_pct": 3.10,
        "volume": 280_000_000,
        "avg_volume": 250_000_000,
        "market_cap": 3_150_000_000_000,
        "sector": "Technology",
        "industry": "Semiconductors",
        "pe_ratio": 58.0,
        "forward_pe": 32.0,
        "pb_ratio": 48.0,
        "ps_ratio": 32.0,
        "eps": 2.21,
        "revenue_growth": 0.95,
        "profit_margin": 0.55,
        "debt_to_equity": 0.25,
        "roe": 1.15,
        "beta": 1.70,
        "52w_high": 140.76,
        "52w_low": 39.23,
        "dividend_yield": 0.0003,
    },
    "MSFT": {
        "symbol": "MSFT",
        "name": "Microsoft Corporation",
        "price": 430.20,
        "change_pct": 0.45,
        "volume": 18_000_000,
        "avg_volume": 20_000_000,
        "market_cap": 3_200_000_000_000,
        "sector": "Technology",
        "industry": "Software—Infrastructure",
        "pe_ratio": 36.5,
        "forward_pe": 30.0,
        "pb_ratio": 13.5,
        "ps_ratio": 13.0,
        "eps": 11.80,
        "revenue_growth": 0.15,
        "profit_margin": 0.36,
        "debt_to_equity": 0.35,
        "roe": 0.38,
        "beta": 0.90,
        "52w_high": 468.35,
        "52w_low": 344.79,
        "dividend_yield": 0.0072,
    },
    "AMZN": {
        "symbol": "AMZN",
        "name": "Amazon.com, Inc.",
        "price": 185.60,
        "change_pct": 1.20,
        "volume": 40_000_000,
        "avg_volume": 45_000_000,
        "market_cap": 1_950_000_000_000,
        "sector": "Consumer Cyclical",
        "industry": "Internet Retail",
        "pe_ratio": 42.0,
        "forward_pe": 32.0,
        "pb_ratio": 8.5,
        "ps_ratio": 3.2,
        "eps": 4.42,
        "revenue_growth": 0.12,
        "profit_margin": 0.08,
        "debt_to_equity": 0.55,
        "roe": 0.22,
        "beta": 1.15,
        "52w_high": 201.20,
        "52w_low": 118.35,
        "dividend_yield": 0.0,
    },
    "META": {
        "symbol": "META",
        "name": "Meta Platforms, Inc.",
        "price": 560.10,
        "change_pct": 1.55,
        "volume": 12_000_000,
        "avg_volume": 14_000_000,
        "market_cap": 1_420_000_000_000,
        "sector": "Communication Services",
        "industry": "Internet Content & Information",
        "pe_ratio": 27.5,
        "forward_pe": 22.0,
        "pb_ratio": 8.2,
        "ps_ratio": 9.5,
        "eps": 20.35,
        "revenue_growth": 0.22,
        "profit_margin": 0.34,
        "debt_to_equity": 0.20,
        "roe": 0.35,
        "beta": 1.20,
        "52w_high": 595.00,
        "52w_low": 279.00,
        "dividend_yield": 0.0035,
    },
    "GOOGL": {
        "symbol": "GOOGL",
        "name": "Alphabet Inc.",
        "price": 165.40,
        "change_pct": 0.70,
        "volume": 22_000_000,
        "avg_volume": 25_000_000,
        "market_cap": 2_050_000_000_000,
        "sector": "Communication Services",
        "industry": "Internet Content & Information",
        "pe_ratio": 24.0,
        "forward_pe": 20.0,
        "pb_ratio": 6.8,
        "ps_ratio": 6.2,
        "eps": 6.90,
        "revenue_growth": 0.14,
        "profit_margin": 0.27,
        "debt_to_equity": 0.10,
        "roe": 0.30,
        "beta": 1.05,
        "52w_high": 191.75,
        "52w_low": 130.67,
        "dividend_yield": 0.0048,
    },
}

# Synthetic OHLCV-ish series used for indicator math (newest last)
DEMO_PRICES: dict[str, list[float]] = {
    "TSLA": [214.94, 212.56, 212.74, 212.41, 217.01, 220.85, 226.68, 224.12, 225.12, 222.08, 221.15, 223.12, 220.2, 219.18, 222.67, 224.97, 223.88, 226.57, 231.38, 227.68, 232.42, 235.88, 235.41, 233.0, 239.15, 238.46, 235.19, 232.17, 237.2, 239.46, 243.82, 247.19, 248.27, 254.19, 253.15, 254.15, 258.27, 259.8, 264.12, 264.91, 267.19, 261.47, 258.27, 255.98, 251.41, 248.87, 245.0, 243.34, 245.69, 244.95, 244.31, 241.94, 240.33, 246.07, 248.44, 250.29, 247.12, 250.35, 247.09, 248.5],
    "AAPL": [194.77, 201.2, 204.3, 206.51, 209.81, 214.47, 218.33, 216.69, 213.23, 212.72, 211.78, 210.36, 215.95, 220.74, 219.8, 222.29, 222.08, 227.06, 227.24, 225.44, 223.55, 224.94, 223.24, 224.88, 229.61, 229.05, 226.67, 232.37, 232.82, 228.87, 224.72, 221.49, 223.63, 227.34, 227.13, 223.27, 222.87, 228.65, 229.47, 234.83, 238.88, 233.67, 236.28, 238.38, 238.84, 236.38, 238.04, 233.96, 233.55, 233.36, 238.44, 242.53, 239.82, 239.82, 236.36, 240.91, 244.87, 242.41, 243.8, 227.8],
    "NVDA": [110.91, 110.33, 112.81, 114.07, 116.51, 117.55, 115.75, 115.75, 114.17, 117.37, 120.22, 122.72, 122.25, 120.43, 123.18, 126.22, 124.3, 124.73, 122.81, 124.84, 126.82, 125.1, 125.43, 126.18, 125.27, 127.84, 127.74, 126.44, 127.08, 128.78, 127.35, 126.64, 129.87, 130.99, 130.83, 131.14, 129.09, 127.78, 127.2, 128.08, 126.86, 125.66, 123.68, 124.96, 123.92, 126.71, 129.17, 126.96, 125.85, 127.25, 125.99, 124.34, 127.29, 128.07, 128.25, 130.22, 132.26, 130.55, 128.4, 128.4],
    "MSFT": [368.68, 371.41, 374.72, 382.3, 388.63, 400.15, 395.42, 396.41, 396.23, 405.37, 403.04, 399.78, 401.38, 402.41, 400.8, 398.76, 408.92, 409.96, 418.66, 421.24, 414.22, 425.36, 433.1, 443.18, 452.14, 459.27, 452.06, 451.81, 446.04, 444.37, 435.95, 434.38, 444.74, 440.43, 446.65, 446.04, 444.82, 454.35, 464.41, 465.02, 469.02, 460.96, 456.36, 465.82, 466.86, 467.08, 471.62, 461.33, 462.67, 462.26, 469.15, 461.15, 470.31, 460.6, 453.72, 455.62, 459.08, 453.31, 445.53, 430.2],
    "AMZN": [162.32, 162.03, 164.31, 166.66, 167.42, 169.38, 170.79, 175.3, 173.92, 176.63, 175.44, 175.56, 177.86, 177.09, 176.5, 179.39, 176.7, 177.26, 182.09, 186.79, 183.61, 181.8, 180.52, 184.75, 188.42, 191.96, 191.0, 188.26, 191.43, 193.37, 194.44, 198.74, 199.96, 195.31, 198.1, 196.18, 197.59, 201.39, 197.79, 194.25, 190.87, 191.54, 189.76, 190.92, 193.0, 190.54, 191.92, 190.04, 190.2, 193.91, 197.0, 193.31, 192.74, 190.93, 186.88, 189.56, 191.01, 189.17, 191.51, 185.6],
    "META": [482.58, 486.1, 480.28, 476.3, 489.89, 503.53, 508.65, 520.15, 525.38, 520.11, 514.69, 513.81, 526.63, 536.64, 547.86, 559.68, 553.8, 549.26, 541.35, 550.47, 561.84, 560.79, 565.2, 557.58, 569.88, 580.17, 593.05, 601.18, 610.94, 596.86, 602.87, 597.69, 608.89, 616.25, 625.08, 632.14, 623.48, 629.93, 616.91, 625.94, 634.32, 624.27, 631.51, 628.39, 621.04, 627.8, 618.29, 603.67, 594.67, 589.83, 599.49, 611.61, 604.49, 607.63, 604.03, 616.42, 616.15, 627.07, 614.43, 560.1],
    "GOOGL": [145.16, 144.43, 148.85, 148.48, 147.08, 147.93, 150.69, 150.54, 152.38, 153.49, 153.68, 155.18, 154.36, 156.75, 154.06, 157.96, 159.0, 161.29, 163.66, 165.41, 164.81, 162.06, 163.83, 163.07, 162.23, 165.33, 167.38, 166.2, 165.15, 164.89, 164.61, 163.54, 161.3, 161.33, 165.14, 166.88, 170.25, 171.32, 169.92, 170.48, 166.82, 165.57, 165.45, 166.46, 167.98, 168.0, 167.86, 165.99, 166.18, 169.55, 172.03, 169.57, 166.62, 167.09, 168.42, 167.44, 170.16, 172.27, 173.7, 165.4],
}

DEMO_NEWS: dict[str, list[dict[str, str]]] = {
    "TSLA": [
        {
            "title": "Tesla expands energy storage deployments in Europe",
            "sentiment": "positive",
            "source": "DemoWire",
            "summary": "Megapack orders accelerate as utilities seek grid flexibility.",
        },
        {
            "title": "EV price competition intensifies in China",
            "sentiment": "negative",
            "source": "DemoMarkets",
            "summary": "Margins under pressure from local EV rivals cutting prices.",
        },
        {
            "title": "Robotaxi software milestone reported by analysts",
            "sentiment": "positive",
            "source": "DemoTech",
            "summary": "Incremental FSD progress keeps long-term optionality alive.",
        },
    ],
    "AAPL": [
        {
            "title": "iPhone upgrade cycle shows steady demand",
            "sentiment": "positive",
            "source": "DemoWire",
            "summary": "Services attach rates remain a key profit driver.",
        },
        {
            "title": "Regulatory scrutiny of App Store continues",
            "sentiment": "negative",
            "source": "DemoMarkets",
            "summary": "Antitrust headlines create near-term sentiment noise.",
        },
    ],
    "NVDA": [
        {
            "title": "Data-center GPU demand remains robust",
            "sentiment": "positive",
            "source": "DemoWire",
            "summary": "Hyperscalers continue multi-year AI infrastructure spend.",
        },
        {
            "title": "Export control headlines weigh on sentiment",
            "sentiment": "negative",
            "source": "DemoMarkets",
            "summary": "Policy risk remains a watch item for China exposure.",
        },
    ],
    "MSFT": [
        {
            "title": "Azure AI workloads drive cloud growth",
            "sentiment": "positive",
            "source": "DemoWire",
            "summary": "Enterprise Copilot adoption supports higher ARPU narrative.",
        },
    ],
    "AMZN": [
        {
            "title": "AWS margin expansion continues",
            "sentiment": "positive",
            "source": "DemoWire",
            "summary": "Cloud profitability offsets retail investment cycle.",
        },
    ],
    "META": [
        {
            "title": "Ad pricing recovers as engagement stays high",
            "sentiment": "positive",
            "source": "DemoWire",
            "summary": "Reels monetization and AI targeting lift ROAS.",
        },
    ],
    "GOOGL": [
        {
            "title": "Search + Cloud mix supports steady growth",
            "sentiment": "positive",
            "source": "DemoWire",
            "summary": "YouTube and cloud remain the growth engines.",
        },
    ],
}


def get_demo_quote(ticker: str) -> dict[str, Any]:
    t = ticker.upper()
    if t in DEMO_QUOTES:
        return dict(DEMO_QUOTES[t])
    # Generic fallback for unknown tickers in demo
    return {
        "symbol": t,
        "name": f"{t} Corp (demo)",
        "price": 100.0,
        "change_pct": 0.5,
        "volume": 10_000_000,
        "avg_volume": 10_000_000,
        "market_cap": 50_000_000_000,
        "sector": "Unknown",
        "industry": "Unknown",
        "pe_ratio": 20.0,
        "forward_pe": 18.0,
        "pb_ratio": 3.0,
        "ps_ratio": 2.5,
        "eps": 5.0,
        "revenue_growth": 0.08,
        "profit_margin": 0.12,
        "debt_to_equity": 0.5,
        "roe": 0.15,
        "beta": 1.0,
        "52w_high": 120.0,
        "52w_low": 80.0,
        "dividend_yield": 0.01,
    }


def get_demo_prices(ticker: str) -> list[float]:
    t = ticker.upper()
    return list(DEMO_PRICES.get(t, [90 + i for i in range(20)]))


def get_demo_news(ticker: str) -> list[dict[str, str]]:
    t = ticker.upper()
    return list(
        DEMO_NEWS.get(
            t,
            [
                {
                    "title": f"{t} in focus as markets digest macro data",
                    "sentiment": "neutral",
                    "source": "DemoWire",
                    "summary": "No major company-specific catalysts in demo feed.",
                }
            ],
        )
    )
