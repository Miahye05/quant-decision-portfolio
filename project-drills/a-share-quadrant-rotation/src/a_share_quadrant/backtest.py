"""Weekly quadrant rotation backtest."""

from __future__ import annotations

import math

import pandas as pd

from a_share_quadrant.signals import target_condition


WEEKS_PER_YEAR = 52


def run_weekly_rotation(
    close: pd.DataFrame,
    prosperity: pd.DataFrame,
    valuation: pd.DataFrame,
    target_quadrant: str,
) -> pd.DataFrame:
    """Use last week's quadrant signal to evaluate next-week industry returns."""

    common_dates = close.index.intersection(prosperity.index).intersection(valuation.index)
    common_industries = close.columns.intersection(prosperity.columns).intersection(
        valuation.columns
    )
    close = close.loc[common_dates, common_industries].dropna(how="all")
    prosperity = prosperity.loc[close.index, common_industries]
    valuation = valuation.loc[close.index, common_industries]

    weekly_returns = close.pct_change().shift(-1)
    rows = []
    for index in range(1, len(close.index) - 1):
        signal_date = close.index[index - 1]
        trade_date = close.index[index]
        selected = target_condition(
            prosperity.loc[signal_date],
            valuation.loc[signal_date],
            target_quadrant,
        )
        selected_industries = selected[selected].index.tolist()
        next_returns = weekly_returns.loc[trade_date]

        if selected_industries:
            strategy_return = next_returns[selected_industries].mean()
        else:
            strategy_return = 0.0

        benchmark_return = next_returns.mean()
        rows.append(
            {
                "signal_date": signal_date,
                "trade_date": trade_date,
                "selected_count": len(selected_industries),
                "selected_industries": ";".join(selected_industries),
                "strategy_return": strategy_return,
                "benchmark_return": benchmark_return,
            }
        )

    returns = pd.DataFrame(rows).dropna(subset=["strategy_return", "benchmark_return"])
    returns["excess_return"] = returns["strategy_return"] - returns["benchmark_return"]
    returns["strategy_equity"] = (1 + returns["strategy_return"]).cumprod()
    returns["benchmark_equity"] = (1 + returns["benchmark_return"]).cumprod()
    returns["excess_equity"] = (1 + returns["excess_return"]).cumprod()
    return returns


def max_drawdown(equity_curve: pd.Series) -> float:
    running_peak = equity_curve.cummax()
    drawdown = equity_curve / running_peak - 1
    return float(drawdown.min())


def summarize_returns(returns: pd.Series, equity: pd.Series) -> dict[str, float]:
    clean_returns = returns.dropna()
    periods = len(clean_returns)
    if periods == 0:
        raise ValueError("Cannot summarize an empty return series.")

    cumulative_return = float((1 + clean_returns).prod() - 1)
    annualized_return = float((1 + cumulative_return) ** (WEEKS_PER_YEAR / periods) - 1)
    annualized_volatility = float(clean_returns.std(ddof=0) * math.sqrt(WEEKS_PER_YEAR))
    sharpe_ratio = (
        annualized_return / annualized_volatility
        if annualized_volatility != 0
        else float("nan")
    )
    return {
        "weeks": float(periods),
        "cumulative_return": cumulative_return,
        "annualized_return": annualized_return,
        "annualized_volatility": annualized_volatility,
        "sharpe_ratio": float(sharpe_ratio),
        "max_drawdown": max_drawdown(equity),
        "hit_rate": float((clean_returns > 0).mean()),
    }


def summarize_backtest(returns: pd.DataFrame) -> pd.DataFrame:
    rows = {
        "strategy": summarize_returns(
            returns["strategy_return"],
            returns["strategy_equity"],
        ),
        "equal_weight_benchmark": summarize_returns(
            returns["benchmark_return"],
            returns["benchmark_equity"],
        ),
        "strategy_minus_benchmark": summarize_returns(
            returns["excess_return"],
            returns["excess_equity"],
        ),
    }
    summary = pd.DataFrame.from_dict(rows, orient="index")
    summary.index.name = "portfolio"
    return summary.reset_index()
