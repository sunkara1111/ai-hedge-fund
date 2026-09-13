"""Configuration loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    anthropic_api_key: str | None
    anthropic_model: str
    portfolio_value: float
    max_position_pct: float
    alpaca_api_key: str | None
    alpaca_secret_key: str | None
    alpaca_base_url: str

    @property
    def has_llm(self) -> bool:
        return bool(self.anthropic_api_key)


def get_settings() -> Settings:
    return Settings(
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY") or None,
        anthropic_model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514"),
        portfolio_value=float(os.getenv("DEFAULT_PORTFOLIO_VALUE", "100000")),
        max_position_pct=float(os.getenv("MAX_POSITION_PCT", "0.10")),
        alpaca_api_key=os.getenv("ALPACA_API_KEY") or None,
        alpaca_secret_key=os.getenv("ALPACA_SECRET_KEY") or None,
        alpaca_base_url=os.getenv(
            "ALPACA_BASE_URL", "https://paper-api.alpaca.markets"
        ),
    )
