"""Signal construction and portfolio formation."""

from __future__ import annotations

import pandas as pd

from industry_rotation.config import SIGNAL_WEIGHTS


REQUIRED_COLUMNS = {
    "date",
    "industry",
    "price_index",
    "prosperity_score",
    "valuation_score",
}


def validate_panel(panel: pd.DataFrame) -> pd.DataFrame:
    """Validate and normalize the input industry panel."""

    missing = REQUIRED_COLUMNS.difference(panel.columns)
    if missing:
        missing_list = ", ".join(sorted(missing))
        raise ValueError(f"Missing required columns: {missing_list}")

    clean = panel.copy()
    clean["date"] = pd.to_datetime(clean["date"])
    clean["industry"] = clean["industry"].astype(str)

    numeric_columns = ["price_index", "prosperity_score", "valuation_score"]
    for column in numeric_columns:
        clean[column] = pd.to_numeric(clean[column], errors="coerce")

    clean = clean.dropna(subset=["date", "industry", *numeric_columns])
    clean = clean.sort_values(["industry", "date"]).reset_index(drop=True)
    return clean


def add_monthly_returns(panel: pd.DataFrame) -> pd.DataFrame:
    """Calculate realized monthly returns from each industry price index."""

    enriched = validate_panel(panel)
    enriched["monthly_return"] = (
        enriched.groupby("industry")["price_index"].pct_change()
    )
    return enriched


def _cross_sectional_zscore(values: pd.Series) -> pd.Series:
    std = values.std(ddof=0)
    if pd.isna(std) or std == 0:
        return pd.Series(0.0, index=values.index)
    return (values - values.mean()) / std


def build_signal_table(
    panel: pd.DataFrame,
    signal_weights: dict[str, float] | None = None,
    top_n: int = 3,
) -> pd.DataFrame:
    """Build signal ranks and next-month returns for the rotation backtest."""

    weights = signal_weights or SIGNAL_WEIGHTS
    enriched = add_monthly_returns(panel)

    for column in weights:
        z_column = f"{column}_z"
        enriched[z_column] = enriched.groupby("date")[column].transform(
            _cross_sectional_zscore
        )

    enriched["composite_signal"] = 0.0
    for column, weight in weights.items():
        enriched["composite_signal"] += weight * enriched[f"{column}_z"]

    enriched["signal_rank"] = enriched.groupby("date")["composite_signal"].rank(
        ascending=False,
        method="first",
    )
    enriched["selected"] = enriched["signal_rank"] <= top_n

    enriched["forward_return"] = enriched.groupby("industry")["monthly_return"].shift(-1)
    signal_table = enriched.dropna(subset=["monthly_return", "forward_return"]).copy()
    return signal_table.sort_values(["date", "signal_rank"]).reset_index(drop=True)


def build_portfolio_returns(signal_table: pd.DataFrame) -> pd.DataFrame:
    """Aggregate selected industry returns and equal-weight benchmark returns."""

    selected = signal_table[signal_table["selected"]].copy()
    strategy = (
        selected.groupby("date")["forward_return"]
        .mean()
        .rename("strategy_return")
    )
    benchmark = (
        signal_table.groupby("date")["forward_return"]
        .mean()
        .rename("benchmark_return")
    )
    selected_count = selected.groupby("date")["industry"].nunique().rename("selected_count")

    returns = pd.concat([strategy, benchmark, selected_count], axis=1).dropna()
    returns["excess_return"] = returns["strategy_return"] - returns["benchmark_return"]
    returns["strategy_equity"] = (1 + returns["strategy_return"]).cumprod()
    returns["benchmark_equity"] = (1 + returns["benchmark_return"]).cumprod()
    returns["excess_equity"] = (1 + returns["excess_return"]).cumprod()
    return returns.reset_index()


def latest_signal_snapshot(signal_table: pd.DataFrame) -> pd.DataFrame:
    """Return the most recent cross-sectional signal ranking."""

    latest_date = signal_table["date"].max()
    columns = [
        "date",
        "industry",
        "prosperity_score",
        "valuation_score",
        "composite_signal",
        "signal_rank",
        "selected",
    ]
    return signal_table.loc[signal_table["date"] == latest_date, columns].sort_values(
        "signal_rank"
    )
