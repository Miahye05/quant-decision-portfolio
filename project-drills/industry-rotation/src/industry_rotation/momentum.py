"""Momentum-based public-data industry rotation signals."""

from __future__ import annotations

import numpy as np
import pandas as pd


REQUIRED_RETURN_COLUMNS = {"date", "industry", "monthly_return"}


def validate_return_panel(panel: pd.DataFrame) -> pd.DataFrame:
    """Validate a long industry return panel."""

    missing = REQUIRED_RETURN_COLUMNS.difference(panel.columns)
    if missing:
        missing_list = ", ".join(sorted(missing))
        raise ValueError(f"Missing required columns: {missing_list}")

    clean = panel.copy()
    clean["date"] = pd.to_datetime(clean["date"])
    clean["industry"] = clean["industry"].astype(str)
    clean["monthly_return"] = pd.to_numeric(clean["monthly_return"], errors="coerce")
    clean = clean.dropna(subset=["date", "industry", "monthly_return"])
    return clean.sort_values(["industry", "date"]).reset_index(drop=True)


def _rolling_compound_return(returns: pd.Series, lookback: int) -> pd.Series:
    return (1 + returns).rolling(lookback).apply(np.prod, raw=True) - 1


def build_momentum_signal_table(
    return_panel: pd.DataFrame,
    top_n: int = 3,
    lookback: int = 12,
    skip_months: int = 1,
) -> pd.DataFrame:
    """Rank industries by trailing momentum and attach next-month returns.

    At signal date t, the score uses returns that end before t when
    `skip_months` is positive. The portfolio return is the next available
    monthly return after the signal date.
    """

    if lookback < 2:
        raise ValueError("lookback must be at least 2 months.")
    if skip_months < 0:
        raise ValueError("skip_months cannot be negative.")

    panel = validate_return_panel(return_panel)
    shifted_return = panel.groupby("industry")["monthly_return"].shift(skip_months)
    panel["momentum_score"] = shifted_return.groupby(panel["industry"]).transform(
        lambda series: _rolling_compound_return(series, lookback)
    )
    panel["signal_rank"] = panel.groupby("date")["momentum_score"].rank(
        ascending=False,
        method="first",
    )
    panel["selected"] = panel["signal_rank"] <= top_n
    panel["forward_return"] = panel.groupby("industry")["monthly_return"].shift(-1)

    signal_table = panel.dropna(subset=["momentum_score", "forward_return"]).copy()
    return signal_table.sort_values(["date", "signal_rank"]).reset_index(drop=True)
