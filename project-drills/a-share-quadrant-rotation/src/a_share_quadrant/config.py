"""Configuration for the A-share quadrant rotation reconstruction."""

from __future__ import annotations

from dataclasses import dataclass


REQUIRED_FILES: dict[str, str] = {
    "income_ttm": "income_ttm.xlsx",
    "forecast_revenue_12m": "forecast_revenue_12m.xlsx",
    "profit_ttm": "profit_ttm.xlsx",
    "forecast_profit_current_year": "forecast_profit_current_year.xlsx",
    "forecast_profit_next_year": "forecast_profit_next_year.xlsx",
    "roe_ttm": "roe_ttm.xlsx",
    "forecast_roe_current_year": "forecast_roe_current_year.xlsx",
    "forecast_roe_next_year": "forecast_roe_next_year.xlsx",
    "pb": "pb.xlsx",
    "pe": "pe_ttm.xlsx",
    "close": "industry_close.xlsx",
}


TARGET_QUADRANTS: dict[str, tuple[str, str]] = {
    "low_low": ("low", "low"),
    "high_prosperity_low_valuation": ("high", "low"),
    "high_high": ("high", "high"),
    "low_prosperity_high_valuation": ("low", "high"),
}


@dataclass(frozen=True)
class QuadrantConfig:
    """Parameters for signal construction and weekly backtesting."""

    start_date: str = "2021-01-16"
    weekly_rule: str = "W"
    prosperity_window: int = 252 * 5
    valuation_window: int = 252 * 15
    target_quadrant: str = "low_low"
    initial_capital: float = 1.0
