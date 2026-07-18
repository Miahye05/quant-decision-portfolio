"""Backtest performance metrics."""

from __future__ import annotations

import math

import pandas as pd


MONTHS_PER_YEAR = 12


def max_drawdown(equity_curve: pd.Series) -> float:
    """Calculate the maximum drawdown of an equity curve."""

    running_peak = equity_curve.cummax()
    drawdown = equity_curve / running_peak - 1
    return float(drawdown.min())


def summarize_return_series(returns: pd.Series, equity: pd.Series) -> dict[str, float]:
    """Summarize monthly returns with annualized performance metrics."""

    clean_returns = returns.dropna()
    periods = len(clean_returns)
    if periods == 0:
        raise ValueError("Cannot summarize an empty return series.")

    cumulative_return = float((1 + clean_returns).prod() - 1)
    annualized_return = float((1 + cumulative_return) ** (MONTHS_PER_YEAR / periods) - 1)
    annualized_volatility = float(clean_returns.std(ddof=0) * math.sqrt(MONTHS_PER_YEAR))
    sharpe_ratio = (
        annualized_return / annualized_volatility
        if annualized_volatility != 0
        else float("nan")
    )
    hit_rate = float((clean_returns > 0).mean())

    return {
        "months": float(periods),
        "cumulative_return": cumulative_return,
        "annualized_return": annualized_return,
        "annualized_volatility": annualized_volatility,
        "sharpe_ratio": float(sharpe_ratio),
        "max_drawdown": max_drawdown(equity),
        "hit_rate": hit_rate,
    }


def summarize_backtest(returns: pd.DataFrame) -> pd.DataFrame:
    """Create a compact strategy versus benchmark summary table."""

    rows = {
        "strategy": summarize_return_series(
            returns["strategy_return"],
            returns["strategy_equity"],
        ),
        "equal_weight_benchmark": summarize_return_series(
            returns["benchmark_return"],
            returns["benchmark_equity"],
        ),
        "strategy_minus_benchmark": summarize_return_series(
            returns["excess_return"],
            returns["excess_equity"],
        ),
    }
    summary = pd.DataFrame.from_dict(rows, orient="index")
    summary.index.name = "portfolio"
    return summary.reset_index()
