"""Signal construction and quadrant classification."""

from __future__ import annotations

import pandas as pd

from a_share_quadrant.config import TARGET_QUADRANTS, QuadrantConfig
from a_share_quadrant.io import align_industry_columns


def forward_12m_blend(
    current_year: pd.DataFrame,
    next_year: pd.DataFrame,
) -> pd.DataFrame:
    """Approximate next-12-month consensus value from current and next year forecasts."""

    current, next_ = current_year.align(next_year, join="inner", axis=0)
    current, next_ = current.align(next_, join="inner", axis=1)
    result = pd.DataFrame(index=current.index, columns=current.columns, dtype=float)

    for date in current.index:
        start_of_year = pd.Timestamp(year=date.year, month=1, day=1)
        days_passed = (date - start_of_year).days + 1
        total_days = 365
        days_left = total_days - days_passed
        result.loc[date] = (
            days_left * current.loc[date] + (total_days - days_left) * next_.loc[date]
        ) / total_days
    return result


def rolling_percentile(
    current_values: pd.DataFrame,
    history_values: pd.DataFrame,
    window: int,
    require_full_window: bool,
) -> pd.DataFrame:
    """Calculate each current value's percentile within its own rolling history."""

    current, history = current_values.align(history_values, join="inner", axis=1)
    result = pd.DataFrame(index=current.index, columns=current.columns, dtype=float)

    for industry in current.columns:
        history_series = history[industry].dropna().sort_index()
        for date, value in current[industry].dropna().items():
            trailing = history_series.loc[:date].tail(window).dropna()
            if require_full_window and len(trailing) < window:
                continue
            if len(trailing) == 0:
                continue
            result.loc[date, industry] = (trailing <= value).sum() / len(trailing)
    return result


def build_prosperity_score(
    panels: dict[str, pd.DataFrame],
    config: QuadrantConfig,
) -> pd.DataFrame:
    """Build the prosperity score from revenue, profit, and ROE percentiles."""

    aligned = align_industry_columns(panels)
    income_growth_history = aligned["income_ttm"].pct_change(252)
    forecast_revenue_growth = (
        aligned["forecast_revenue_12m"] / aligned["income_ttm"] - 1
    ).dropna(how="all")

    forward_profit = forward_12m_blend(
        aligned["forecast_profit_current_year"],
        aligned["forecast_profit_next_year"],
    )
    profit_growth_history = aligned["profit_ttm"].pct_change(252)
    forecast_profit_growth = (forward_profit / aligned["profit_ttm"] - 1).dropna(
        how="all"
    )

    forward_roe = forward_12m_blend(
        aligned["forecast_roe_current_year"],
        aligned["forecast_roe_next_year"],
    )
    roe_history = aligned["roe_ttm"] / 100.0

    income_pct = rolling_percentile(
        forecast_revenue_growth,
        income_growth_history,
        window=config.prosperity_window,
        require_full_window=False,
    )
    profit_pct = rolling_percentile(
        forecast_profit_growth,
        profit_growth_history,
        window=config.prosperity_window,
        require_full_window=False,
    )
    roe_pct = rolling_percentile(
        forward_roe,
        roe_history,
        window=config.prosperity_window,
        require_full_window=False,
    )
    return (income_pct + profit_pct + roe_pct) / 3


def build_valuation_score(
    panels: dict[str, pd.DataFrame],
    config: QuadrantConfig,
) -> pd.DataFrame:
    """Build the valuation score from PE and PB rolling percentiles."""

    aligned = align_industry_columns(panels)
    pe_pct = rolling_percentile(
        aligned["pe"],
        aligned["pe"],
        window=config.valuation_window,
        require_full_window=True,
    )
    pb_pct = rolling_percentile(
        aligned["pb"],
        aligned["pb"],
        window=config.valuation_window,
        require_full_window=True,
    )
    return (pe_pct + pb_pct) / 2


def get_quadrant_label(prosperity: float, valuation: float) -> str:
    """Classify a pair of percentile scores into a quadrant."""

    if prosperity > 0.5 and valuation > 0.5:
        return "high_prosperity_high_valuation"
    if prosperity > 0.5 and valuation <= 0.5:
        return "high_prosperity_low_valuation"
    if prosperity <= 0.5 and valuation > 0.5:
        return "low_prosperity_high_valuation"
    return "low_low"


def target_condition(
    prosperity: pd.Series,
    valuation: pd.Series,
    target_quadrant: str,
) -> pd.Series:
    """Return industries that fall into the configured target quadrant."""

    if target_quadrant not in TARGET_QUADRANTS:
        allowed = ", ".join(sorted(TARGET_QUADRANTS))
        raise ValueError(f"Unknown target_quadrant={target_quadrant}. Allowed: {allowed}")

    prosperity_side, valuation_side = TARGET_QUADRANTS[target_quadrant]
    prosperity_mask = prosperity > 0.5 if prosperity_side == "high" else prosperity <= 0.5
    valuation_mask = valuation > 0.5 if valuation_side == "high" else valuation <= 0.5
    return prosperity_mask & valuation_mask


def build_weekly_signals(
    panels: dict[str, pd.DataFrame],
    config: QuadrantConfig,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Build weekly close, prosperity, and valuation panels."""

    aligned = align_industry_columns(panels)
    prosperity = build_prosperity_score(aligned, config)
    valuation = build_valuation_score(aligned, config)
    close = aligned["close"]

    weekly_close = close.resample(config.weekly_rule).first()
    weekly_prosperity = prosperity.resample(config.weekly_rule).last()
    weekly_valuation = valuation.resample(config.weekly_rule).last()

    end_date = close.index.max()
    weekly_close = weekly_close[config.start_date : end_date]
    weekly_prosperity = weekly_prosperity[config.start_date : end_date]
    weekly_valuation = weekly_valuation[config.start_date : end_date]
    return weekly_close, weekly_prosperity, weekly_valuation


def latest_quadrants(
    prosperity: pd.DataFrame,
    valuation: pd.DataFrame,
) -> pd.DataFrame:
    """Return the latest quadrant distribution."""

    common_dates = prosperity.index.intersection(valuation.index)
    common_industries = prosperity.columns.intersection(valuation.columns)
    p_latest = prosperity.loc[common_dates[-1], common_industries]
    v_latest = valuation.loc[common_dates[-1], common_industries]

    rows = []
    for industry in common_industries:
        p_value = p_latest[industry]
        v_value = v_latest[industry]
        rows.append(
            {
                "date": common_dates[-1],
                "industry": industry,
                "prosperity": p_value,
                "valuation": v_value,
                "quadrant": get_quadrant_label(p_value, v_value),
            }
        )
    return pd.DataFrame(rows).sort_values(["quadrant", "industry"]).reset_index(drop=True)


def quadrant_migration(
    prosperity: pd.DataFrame,
    valuation: pd.DataFrame,
) -> pd.DataFrame:
    """Compare the latest two weekly quadrant snapshots."""

    columns = [
        "industry",
        "previous_date",
        "latest_date",
        "previous_quadrant",
        "latest_quadrant",
    ]
    common_dates = prosperity.index.intersection(valuation.index)
    common_industries = prosperity.columns.intersection(valuation.columns)
    if len(common_dates) < 2:
        raise ValueError("Need at least two weekly signal dates for migration analysis.")

    previous_date = common_dates[-2]
    latest_date = common_dates[-1]
    rows = []
    for industry in common_industries:
        prev_q = get_quadrant_label(
            prosperity.loc[previous_date, industry],
            valuation.loc[previous_date, industry],
        )
        latest_q = get_quadrant_label(
            prosperity.loc[latest_date, industry],
            valuation.loc[latest_date, industry],
        )
        if prev_q != latest_q:
            rows.append(
                {
                    "industry": industry,
                    "previous_date": previous_date,
                    "latest_date": latest_date,
                    "previous_quadrant": prev_q,
                    "latest_quadrant": latest_q,
                }
            )
    return pd.DataFrame(rows, columns=columns)
