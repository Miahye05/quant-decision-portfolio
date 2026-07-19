"""Run the first-pass industry rotation backtest."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

from industry_rotation.backtest import summarize_backtest  # noqa: E402
from industry_rotation.config import BacktestConfig, SIGNAL_WEIGHTS  # noqa: E402
from industry_rotation.french_data import load_or_download_french_10_industry  # noqa: E402
from industry_rotation.momentum import build_momentum_signal_table  # noqa: E402
from industry_rotation.sample_data import generate_sample_panel  # noqa: E402
from industry_rotation.signals import (  # noqa: E402
    build_portfolio_returns,
    build_signal_table,
    latest_signal_snapshot,
)


DATA_PATH = PROJECT_DIR / "data" / "processed" / "sample_industry_panel.csv"
FRENCH_RAW_PATH = PROJECT_DIR / "data" / "raw" / "10_Industry_Portfolios_CSV.zip"
FRENCH_PROCESSED_PATH = PROJECT_DIR / "data" / "processed" / "french_10_industry_returns.csv"
OUTPUT_DIR = PROJECT_DIR / "outputs"
FIGURE_DIR = OUTPUT_DIR / "figures"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-source",
        choices=["sample", "french"],
        default="sample",
        help="Data source used for the backtest.",
    )
    parser.add_argument(
        "--refresh-sample",
        action="store_true",
        help="Regenerate the deterministic sample panel before running.",
    )
    parser.add_argument(
        "--refresh-data",
        action="store_true",
        help="Refresh external public data before running.",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=BacktestConfig().top_n,
        help="Number of top-ranked industries held each month.",
    )
    parser.add_argument(
        "--start-date",
        default="2000-01-31",
        help="Earliest signal date kept for public-data backtests.",
    )
    parser.add_argument(
        "--lookback",
        type=int,
        default=12,
        help="Momentum lookback window in months for the French public-data backtest.",
    )
    parser.add_argument(
        "--skip-months",
        type=int,
        default=1,
        help="Number of recent months skipped when forming the momentum signal.",
    )
    return parser.parse_args()


def load_or_create_panel(config: BacktestConfig, refresh: bool) -> pd.DataFrame:
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    if refresh or not DATA_PATH.exists():
        panel = generate_sample_panel(config)
        panel.to_csv(DATA_PATH, index=False)
        return panel
    return pd.read_csv(DATA_PATH)


def build_sample_backtest(
    config: BacktestConfig,
    refresh: bool,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    panel = load_or_create_panel(config, refresh)
    signal_table = build_signal_table(panel, SIGNAL_WEIGHTS, top_n=config.top_n)
    return panel, signal_table


def build_french_backtest(args: argparse.Namespace) -> tuple[pd.DataFrame, pd.DataFrame]:
    panel = load_or_download_french_10_industry(
        FRENCH_RAW_PATH,
        FRENCH_PROCESSED_PATH,
        refresh=args.refresh_data,
    )
    signal_table = build_momentum_signal_table(
        panel,
        top_n=args.top_n,
        lookback=args.lookback,
        skip_months=args.skip_months,
    )
    signal_table = signal_table[
        signal_table["date"] >= pd.Timestamp(args.start_date)
    ].copy()
    return panel, signal_table


def save_equity_curve(returns: pd.DataFrame, title: str) -> Path:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    figure_path = FIGURE_DIR / "equity_curve.png"

    plot_data = returns.set_index("date")[["strategy_equity", "benchmark_equity"]]
    ax = plot_data.plot(figsize=(10, 6), linewidth=2)
    ax.set_title(title)
    ax.set_xlabel("Signal Date")
    ax.set_ylabel("Growth of 1.0")
    ax.grid(True, alpha=0.3)
    ax.legend(["Strategy", "Equal-weight benchmark"])
    ax.figure.tight_layout()
    ax.figure.savefig(figure_path, dpi=150)
    plt.close(ax.figure)
    return figure_path


def main() -> None:
    args = parse_args()
    config = BacktestConfig(top_n=args.top_n)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if args.data_source == "french":
        panel, signal_table = build_french_backtest(args)
        data_path = FRENCH_PROCESSED_PATH
        figure_title = "U.S. French 10 Industry Momentum Backtest: Equity Curve"
    else:
        panel, signal_table = build_sample_backtest(config, args.refresh_sample)
        data_path = DATA_PATH
        figure_title = "Sample Industry Rotation Backtest: Equity Curve"

    returns = build_portfolio_returns(signal_table)
    summary = summarize_backtest(returns)
    snapshot = latest_signal_snapshot(signal_table)

    returns.to_csv(OUTPUT_DIR / "monthly_portfolio_returns.csv", index=False)
    summary.to_csv(OUTPUT_DIR / "backtest_summary.csv", index=False)
    snapshot.to_csv(OUTPUT_DIR / "signal_snapshot_latest.csv", index=False)
    figure_path = save_equity_curve(returns, figure_title)

    pd.options.display.float_format = "{:.4f}".format
    print("Backtest complete.")
    print(f"Data source: {args.data_source}")
    print(f"Panel rows: {len(panel):,}")
    print(
        "Signal range: "
        f"{returns['date'].min().date()} to {returns['date'].max().date()}"
    )
    print(f"Analysis panel: {data_path.relative_to(PROJECT_DIR)}")
    print(f"Summary: {(OUTPUT_DIR / 'backtest_summary.csv').relative_to(PROJECT_DIR)}")
    print(f"Figure: {figure_path.relative_to(PROJECT_DIR)}")
    print()
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
