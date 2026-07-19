"""Project configuration for the industry rotation backtest."""

from __future__ import annotations

from dataclasses import dataclass


FRENCH_10_INDUSTRY_URL = (
    "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/"
    "10_Industry_Portfolios_CSV.zip"
)


INDUSTRIES: tuple[str, ...] = (
    "Technology",
    "Healthcare",
    "Industrials",
    "Consumer Discretionary",
    "Consumer Staples",
    "Financials",
    "Energy",
    "Utilities",
)


SIGNAL_WEIGHTS: dict[str, float] = {
    "prosperity_score": 0.6,
    "valuation_score": 0.4,
}


FRENCH_INDUSTRY_NAMES: dict[str, str] = {
    "NoDur": "Consumer Non-Durables",
    "Durbl": "Consumer Durables",
    "Manuf": "Manufacturing",
    "Enrgy": "Energy",
    "HiTec": "Business Equipment",
    "Telcm": "Telecommunications",
    "Shops": "Retail and Wholesale",
    "Hlth": "Healthcare",
    "Utils": "Utilities",
    "Other": "Other",
}


@dataclass(frozen=True)
class BacktestConfig:
    """Parameters that define the first-pass industry rotation experiment."""

    start_date: str = "2017-01-31"
    periods: int = 96
    top_n: int = 3
    random_seed: int = 42
    initial_capital: float = 1.0
