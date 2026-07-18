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
from industry_rotation.sample_data import generate_sample_panel  # noqa: E402
from industry_rotation.signals import (  # noqa: E402
    build_portfolio_returns,
    build_signal_table,
    latest_signal_snapshot,
)


DATA_PATH = PROJECT_DIR / "data" / "processed" / "sample_industry_panel.csv"
OUTPUT_DIR = PROJECT_DIR / "outputs"
FIGURE_DIR = OUTPUT_DIR / "figures"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--refresh-sample",
        action="store_true",
        help="Regenerate the deterministic sample panel before running.",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=BacktestConfig().top_n,
        help="Number of top-ranked industries held each month.",
    )
    return parser.parse_args()


def load_or_create_panel(config: BacktestConfig, refresh: bool) -> pd.DataFrame:
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    if refresh or not DATA_PATH.exists():
        panel = generate_sample_panel(config)
        panel.to_csv(DATA_PATH, index=False)
        return panel
    return pd.read_csv(DATA_PATH)


def save_equity_curve(returns: pd.DataFrame) -> Path:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    figure_path = FIGURE_DIR / "equity_curve.png"

    plot_data = returns.set_index("date")[["strategy_equity", "benchmark_equity"]]
    ax = plot_data.plot(figsize=(10, 6), linewidth=2)
    ax.set_title("Industry Rotation Backtest: Equity Curve")
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
    panel = load_or_create_panel(config, args.refresh_sample)
    signal_table = build_signal_table(panel, SIGNAL_WEIGHTS, top_n=config.top_n)
    returns = build_portfolio_returns(signal_table)
    summary = summarize_backtest(returns)
    snapshot = latest_signal_snapshot(signal_table)

    returns.to_csv(OUTPUT_DIR / "monthly_portfolio_returns.csv", index=False)
    summary.to_csv(OUTPUT_DIR / "backtest_summary.csv", index=False)
    snapshot.to_csv(OUTPUT_DIR / "signal_snapshot_latest.csv", index=False)
    figure_path = save_equity_curve(returns)

    pd.options.display.float_format = "{:.4f}".format
    print("Backtest complete.")
    print(f"Sample panel: {DATA_PATH.relative_to(PROJECT_DIR)}")
    print(f"Summary: {(OUTPUT_DIR / 'backtest_summary.csv').relative_to(PROJECT_DIR)}")
    print(f"Figure: {figure_path.relative_to(PROJECT_DIR)}")
    print()
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
