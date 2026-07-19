"""Weekly quadrant rotation backtest."""

from __future__ import annotations

import math

import pandas as pd

from a_share_quadrant.signals import target_condition
from a_share_quadrant.config import TARGET_QUADRANTS


WEEKS_PER_YEAR = 52


def weekly_risk_free_rate(annual_risk_free_rate: float) -> float:
    """Convert an annual risk-free-rate assumption to a weekly rate."""

    if annual_risk_free_rate <= -1:
        raise ValueError("annual_risk_free_rate must be greater than -100%.")
    return (1 + annual_risk_free_rate) ** (1 / WEEKS_PER_YEAR) - 1


def _target_weights(selected_industries: list[str]) -> dict[str, float]:
    if not selected_industries:
        return {}
    weight = 1 / len(selected_industries)
    return {industry: weight for industry in selected_industries}


def _one_way_turnover(
    previous_weights: dict[str, float],
    target_weights: dict[str, float],
) -> float:
    """Calculate one-way turnover including cash as the residual asset."""

    industries = set(previous_weights) | set(target_weights)
    industry_change = sum(
        abs(target_weights.get(industry, 0.0) - previous_weights.get(industry, 0.0))
        for industry in industries
    )
    previous_cash = 1 - sum(previous_weights.values())
    target_cash = 1 - sum(target_weights.values())
    return (industry_change + abs(target_cash - previous_cash)) / 2


def run_weekly_rotation(
    close: pd.DataFrame,
    prosperity: pd.DataFrame,
    valuation: pd.DataFrame,
    target_quadrant: str,
    transaction_cost_bps: float = 10.0,
    annual_risk_free_rate: float = 0.0,
) -> pd.DataFrame:
    """Use last week's quadrant signal to evaluate next-week industry returns.

    Empty target-quadrant weeks are treated as cash holdings at the configured
    risk-free-rate assumption.
    """

    common_dates = close.index.intersection(prosperity.index).intersection(valuation.index)
    common_industries = close.columns.intersection(prosperity.columns).intersection(
        valuation.columns
    )
    close = close.loc[common_dates, common_industries].dropna(how="all")
    prosperity = prosperity.loc[close.index, common_industries]
    valuation = valuation.loc[close.index, common_industries]

    weekly_returns = close.pct_change().shift(-1)
    rows = []
    previous_weights: dict[str, float] = {}
    cost_rate = transaction_cost_bps / 10_000
    cash_return = weekly_risk_free_rate(annual_risk_free_rate)

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
            gross_strategy_return = next_returns[selected_industries].mean()
        else:
            gross_strategy_return = cash_return

        target_weights = _target_weights(selected_industries)
        turnover = _one_way_turnover(previous_weights, target_weights)
        transaction_cost = turnover * cost_rate
        strategy_return = gross_strategy_return - transaction_cost

        benchmark_return = next_returns.mean()
        rows.append(
            {
                "signal_date": signal_date,
                "trade_date": trade_date,
                "selected_count": len(selected_industries),
                "selected_industries": ";".join(selected_industries),
                "gross_strategy_return": gross_strategy_return,
                "turnover": turnover,
                "transaction_cost": transaction_cost,
                "strategy_return": strategy_return,
                "benchmark_return": benchmark_return,
            }
        )
        previous_weights = target_weights

    returns = pd.DataFrame(rows).dropna(subset=["strategy_return", "benchmark_return"])
    returns["active_return"] = returns["strategy_return"] - returns["benchmark_return"]
    returns["strategy_equity"] = (1 + returns["strategy_return"]).cumprod()
    returns["benchmark_equity"] = (1 + returns["benchmark_return"]).cumprod()
    returns["active_return_index"] = (1 + returns["active_return"]).cumprod()
    return returns


def max_drawdown(equity_curve: pd.Series) -> float:
    running_peak = equity_curve.cummax()
    drawdown = equity_curve / running_peak - 1
    return float(drawdown.min())


def summarize_returns(
    returns: pd.Series,
    equity: pd.Series,
    annual_risk_free_rate: float = 0.0,
) -> dict[str, float]:
    clean_returns = returns.dropna()
    periods = len(clean_returns)
    if periods == 0:
        raise ValueError("Cannot summarize an empty return series.")

    cumulative_return = float((1 + clean_returns).prod() - 1)
    annualized_return = float((1 + cumulative_return) ** (WEEKS_PER_YEAR / periods) - 1)
    annualized_volatility = float(clean_returns.std(ddof=0) * math.sqrt(WEEKS_PER_YEAR))
    weekly_rf = weekly_risk_free_rate(annual_risk_free_rate)
    excess_weekly_returns = clean_returns - weekly_rf
    sharpe_ratio = (
        excess_weekly_returns.mean() / clean_returns.std(ddof=0) * math.sqrt(WEEKS_PER_YEAR)
        if clean_returns.std(ddof=0) != 0
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


def summarize_backtest(
    returns: pd.DataFrame,
    annual_risk_free_rate: float = 0.0,
) -> pd.DataFrame:
    rows = {
        "strategy_net": summarize_returns(
            returns["strategy_return"],
            returns["strategy_equity"],
            annual_risk_free_rate=annual_risk_free_rate,
        ),
        "equal_weight_benchmark": summarize_returns(
            returns["benchmark_return"],
            returns["benchmark_equity"],
            annual_risk_free_rate=annual_risk_free_rate,
        ),
        "active_return_index": summarize_returns(
            returns["active_return"],
            returns["active_return_index"],
            annual_risk_free_rate=0.0,
        ),
    }
    summary = pd.DataFrame.from_dict(rows, orient="index")
    summary.index.name = "portfolio"
    return summary.reset_index()


def compare_quadrants(
    close: pd.DataFrame,
    prosperity: pd.DataFrame,
    valuation: pd.DataFrame,
    transaction_cost_bps: float = 10.0,
    annual_risk_free_rate: float = 0.0,
) -> pd.DataFrame:
    """Run all quadrant strategies and return a compact comparison table."""

    rows = []
    for target_quadrant in sorted(TARGET_QUADRANTS):
        returns = run_weekly_rotation(
            close,
            prosperity,
            valuation,
            target_quadrant=target_quadrant,
            transaction_cost_bps=transaction_cost_bps,
            annual_risk_free_rate=annual_risk_free_rate,
        )
        summary = summarize_backtest(
            returns,
            annual_risk_free_rate=annual_risk_free_rate,
        ).set_index("portfolio")
        strategy = summary.loc["strategy_net"]
        benchmark = summary.loc["equal_weight_benchmark"]
        active = summary.loc["active_return_index"]
        rows.append(
            {
                "target_quadrant": target_quadrant,
                "annualized_return": strategy["annualized_return"],
                "benchmark_annualized_return": benchmark["annualized_return"],
                "active_annualized_return": active["annualized_return"],
                "annualized_volatility": strategy["annualized_volatility"],
                "sharpe_ratio": strategy["sharpe_ratio"],
                "max_drawdown": strategy["max_drawdown"],
                "hit_rate": strategy["hit_rate"],
                "average_selected_count": returns["selected_count"].mean(),
                "no_position_weeks": float((returns["selected_count"] == 0).sum()),
                "average_turnover": returns["turnover"].mean(),
                "total_transaction_cost": returns["transaction_cost"].sum(),
            }
        )
    return pd.DataFrame(rows).sort_values(
        ["annualized_return", "sharpe_ratio"],
        ascending=False,
    )


def calendar_year_returns(returns: pd.DataFrame) -> pd.DataFrame:
    """Summarize strategy, benchmark, and active returns by calendar year."""

    data = returns.copy()
    data["year"] = pd.to_datetime(data["trade_date"]).dt.year
    grouped = data.groupby("year")
    rows = []
    for year, year_data in grouped:
        rows.append(
            {
                "year": year,
                "strategy_return": (1 + year_data["strategy_return"]).prod() - 1,
                "benchmark_return": (1 + year_data["benchmark_return"]).prod() - 1,
                "active_return": (1 + year_data["active_return"]).prod() - 1,
                "average_selected_count": year_data["selected_count"].mean(),
                "average_turnover": year_data["turnover"].mean(),
            }
        )
    return pd.DataFrame(rows)
