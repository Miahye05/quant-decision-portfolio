"""Create deterministic sample data for the industry rotation workflow."""

from __future__ import annotations

import numpy as np
import pandas as pd

from industry_rotation.config import INDUSTRIES, BacktestConfig


def generate_sample_panel(config: BacktestConfig) -> pd.DataFrame:
    """Generate a monthly industry panel with transparent synthetic signals.

    The sample data is not market evidence. It is a deterministic fixture for
    testing the pipeline before public market or fundamental data is connected.
    """

    rng = np.random.default_rng(config.random_seed)
    dates = pd.date_range(
        config.start_date,
        periods=config.periods,
        freq=pd.offsets.MonthEnd(),
    )
    cycle = np.sin(np.linspace(0, 5 * np.pi, config.periods))
    liquidity_cycle = np.cos(np.linspace(0, 3 * np.pi, config.periods))

    rows: list[dict[str, object]] = []
    for idx, industry in enumerate(INDUSTRIES):
        base_return = 0.004 + idx * 0.0003
        industry_cycle_loading = rng.normal(0.35, 0.12)
        valuation_loading = rng.normal(0.25, 0.10)
        volatility = rng.uniform(0.035, 0.06)

        prosperity = (
            industry_cycle_loading * cycle
            + rng.normal(0, 0.45, config.periods)
            + idx * 0.03
        )
        valuation = (
            valuation_loading * liquidity_cycle
            + rng.normal(0, 0.40, config.periods)
            - idx * 0.02
        )

        monthly_return = (
            base_return
            + 0.012 * prosperity
            + 0.007 * valuation
            + rng.normal(0, volatility, config.periods)
        )
        monthly_return = np.clip(monthly_return, -0.22, 0.24)
        price_index = 100 * np.cumprod(1 + monthly_return)

        for date, price, p_score, v_score in zip(dates, price_index, prosperity, valuation):
            rows.append(
                {
                    "date": date,
                    "industry": industry,
                    "price_index": round(float(price), 4),
                    "prosperity_score": round(float(p_score), 6),
                    "valuation_score": round(float(v_score), 6),
                }
            )

    return pd.DataFrame(rows).sort_values(["date", "industry"]).reset_index(drop=True)
