"""Deterministic sample data for the A-share quadrant rotation pipeline."""

from __future__ import annotations

import numpy as np
import pandas as pd


SAMPLE_INDUSTRIES: tuple[str, ...] = (
    "电子",
    "医药生物",
    "食品饮料",
    "有色金属",
    "银行",
    "计算机",
    "电力设备",
    "基础化工",
)


def _positive_panel(
    dates: pd.DatetimeIndex,
    industries: tuple[str, ...],
    rng: np.random.Generator,
    base: float,
    trend: float,
    noise: float,
) -> pd.DataFrame:
    rows = {}
    t = np.arange(len(dates))
    for idx, industry in enumerate(industries):
        cycle = np.sin(t / (35 + idx * 2)) * 0.05
        shocks = rng.normal(0, noise, len(dates)).cumsum() * 0.01
        values = base * (1 + idx * 0.08) * (1 + trend) ** t * (1 + cycle + shocks)
        rows[industry] = np.maximum(values, base * 0.1)
    return pd.DataFrame(rows, index=dates)


def generate_sample_panels(periods: int = 1500, seed: int = 7) -> dict[str, pd.DataFrame]:
    """Generate a synthetic panel with the same schema as external inputs."""

    rng = np.random.default_rng(seed)
    dates = pd.bdate_range("2018-01-02", periods=periods)
    forecast_dates = dates[dates >= "2021-01-04"]

    income_ttm = _positive_panel(dates, SAMPLE_INDUSTRIES, rng, 1_000.0, 0.00012, 0.8)
    profit_ttm = _positive_panel(dates, SAMPLE_INDUSTRIES, rng, 80.0, 0.00010, 0.9)
    roe_ttm = _positive_panel(dates, SAMPLE_INDUSTRIES, rng, 8.0, 0.00002, 0.4)
    pb = _positive_panel(dates, SAMPLE_INDUSTRIES, rng, 2.0, 0.00001, 0.7)
    pe = _positive_panel(dates, SAMPLE_INDUSTRIES, rng, 22.0, 0.00001, 0.9)
    close = _positive_panel(forecast_dates, SAMPLE_INDUSTRIES, rng, 1000.0, 0.00025, 1.2)

    recent_income = income_ttm.reindex(forecast_dates, method="ffill")
    recent_profit = profit_ttm.reindex(forecast_dates, method="ffill")
    recent_roe = roe_ttm.reindex(forecast_dates, method="ffill") / 100.0

    growth_tilt = pd.DataFrame(
        rng.normal(0.12, 0.08, size=recent_income.shape),
        index=forecast_dates,
        columns=SAMPLE_INDUSTRIES,
    )
    forecast_revenue_12m = recent_income * (1 + growth_tilt)
    forecast_profit_current_year = recent_profit * (1 + growth_tilt * 0.8)
    forecast_profit_next_year = recent_profit * (1 + growth_tilt * 1.2)
    forecast_roe_current_year = recent_roe * (1 + growth_tilt * 0.3)
    forecast_roe_next_year = recent_roe * (1 + growth_tilt * 0.5)

    return {
        "income_ttm": income_ttm,
        "forecast_revenue_12m": forecast_revenue_12m,
        "profit_ttm": profit_ttm,
        "forecast_profit_current_year": forecast_profit_current_year,
        "forecast_profit_next_year": forecast_profit_next_year,
        "roe_ttm": roe_ttm,
        "forecast_roe_current_year": forecast_roe_current_year,
        "forecast_roe_next_year": forecast_roe_next_year,
        "pb": pb,
        "pe": pe,
        "close": close,
    }
