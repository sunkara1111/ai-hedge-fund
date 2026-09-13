"""Technical indicator helpers (pure Python / numpy)."""

from __future__ import annotations

from typing import Any

import numpy as np


def _ema(values: np.ndarray, span: int) -> np.ndarray:
    alpha = 2 / (span + 1)
    out = np.empty_like(values, dtype=float)
    out[0] = values[0]
    for i in range(1, len(values)):
        out[i] = alpha * values[i] + (1 - alpha) * out[i - 1]
    return out


def _sma(values: np.ndarray, window: int) -> float:
    if len(values) < window:
        return float(np.mean(values))
    return float(np.mean(values[-window:]))


def _rsi(closes: np.ndarray, period: int = 14) -> float:
    if len(closes) < period + 1:
        return 50.0
    deltas = np.diff(closes)
    gains = np.where(deltas > 0, deltas, 0.0)
    losses = np.where(deltas < 0, -deltas, 0.0)
    avg_gain = float(np.mean(gains[-period:]))
    avg_loss = float(np.mean(losses[-period:]))
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return float(100 - (100 / (1 + rs)))


def _macd(closes: np.ndarray) -> dict[str, float]:
    if len(closes) < 26:
        return {"macd": 0.0, "signal": 0.0, "histogram": 0.0}
    ema12 = _ema(closes, 12)
    ema26 = _ema(closes, 26)
    macd_line = ema12 - ema26
    signal = _ema(macd_line, 9)
    hist = macd_line - signal
    return {
        "macd": float(macd_line[-1]),
        "signal": float(signal[-1]),
        "histogram": float(hist[-1]),
    }


def compute_indicators(prices: list[float]) -> dict[str, Any]:
    """Compute RSI, MACD, moving averages, trend, and bias from close prices."""
    closes = np.asarray(prices, dtype=float)
    if len(closes) == 0:
        return {
            "rsi": 50.0,
            "macd": {},
            "sma_20": 0.0,
            "sma_50": 0.0,
            "ema_12": 0.0,
            "price": 0.0,
            "trend": "neutral",
            "bias": "neutral",
            "score": 50,
        }

    price = float(closes[-1])
    rsi = _rsi(closes)
    macd = _macd(closes)
    sma_20 = _sma(closes, min(20, len(closes)))
    sma_50 = _sma(closes, min(50, len(closes))) if len(closes) >= 10 else sma_20
    ema_12 = float(_ema(closes, 12)[-1]) if len(closes) >= 2 else price

    # Trend: price vs MAs + MACD histogram
    bullish_signals = 0
    bearish_signals = 0

    if price > sma_20:
        bullish_signals += 1
    else:
        bearish_signals += 1
    if sma_20 > sma_50:
        bullish_signals += 1
    else:
        bearish_signals += 1
    if macd.get("histogram", 0) > 0:
        bullish_signals += 1
    else:
        bearish_signals += 1
    if rsi > 55:
        bullish_signals += 1
    elif rsi < 45:
        bearish_signals += 1

    if bullish_signals >= 3:
        trend = "uptrend"
    elif bearish_signals >= 3:
        trend = "downtrend"
    else:
        trend = "sideways"

    # Bias
    if rsi >= 70:
        bias = "overbought"
    elif rsi <= 30:
        bias = "oversold"
    elif trend == "uptrend":
        bias = "bullish"
    elif trend == "downtrend":
        bias = "bearish"
    else:
        bias = "neutral"

    # 0-100 technical score
    score = 50
    score += (bullish_signals - bearish_signals) * 8
    if 40 <= rsi <= 60:
        score += 5
    elif rsi > 70 or rsi < 30:
        score -= 5
    score = int(max(0, min(100, score)))

    return {
        "rsi": round(rsi, 2),
        "macd": {k: round(v, 4) for k, v in macd.items()},
        "sma_20": round(sma_20, 2),
        "sma_50": round(sma_50, 2),
        "ema_12": round(ema_12, 2),
        "price": round(price, 2),
        "trend": trend,
        "bias": bias,
        "score": score,
        "bullish_signals": bullish_signals,
        "bearish_signals": bearish_signals,
    }
