"""Run the A-share industry quadrant rotation reconstruction."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

from a_share_quadrant.backtest import (  # noqa: E402
    calendar_year_returns,
    compare_quadrants,
    run_weekly_rotation,
    summarize_backtest,
)
from a_share_quadrant.config import QuadrantConfig, TARGET_QUADRANTS  # noqa: E402
from a_share_quadrant.io import load_local_excel_panels  # noqa: E402
from a_share_quadrant.sample_data import generate_sample_panels  # noqa: E402
from a_share_quadrant.signals import (  # noqa: E402
    build_weekly_signals,
    latest_quadrants,
    quadrant_migration,
)


OUTPUT_DIR = PROJECT_DIR / "outputs"
FIGURE_DIR = OUTPUT_DIR / "figures"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-source",
        choices=["sample", "local"],
        default="sample",
        help="Use synthetic sample data or a local external input folder.",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        help="Folder containing local input files for --data-source local.",
    )
    parser.add_argument(
        "--start-date",
        default=QuadrantConfig().start_date,
        help="Backtest start date.",
    )
    parser.add_argument(
        "--target-quadrant",
        choices=sorted(TARGET_QUADRANTS),
        default=QuadrantConfig().target_quadrant,
        help="Quadrant selected by the strategy.",
    )
    parser.add_argument(
        "--prosperity-window-years",
        type=int,
        help="Rolling history window for prosperity percentiles. Defaults to 5 for local and 2 for sample.",
    )
    parser.add_argument(
        "--valuation-window-years",
        type=int,
        help="Rolling history window for valuation percentiles. Defaults to 15 for local and 3 for sample.",
    )
    parser.add_argument(
        "--transaction-cost-bps",
        type=float,
        default=10.0,
        help="One-way transaction cost assumption in basis points.",
    )
    parser.add_argument(
        "--risk-free-rate",
        type=float,
        default=0.0,
        help="Annual risk-free-rate assumption used for cash weeks and Sharpe ratio.",
    )
    return parser.parse_args()


def load_panels(args: argparse.Namespace) -> dict[str, pd.DataFrame]:
    if args.data_source == "local":
        if args.data_dir is None:
            raise ValueError("--data-dir is required when --data-source local.")
        return load_local_excel_panels(args.data_dir)
    return generate_sample_panels()


def save_equity_curve(
    returns: pd.DataFrame,
    data_source: str,
    target_quadrant: str,
) -> Path:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    figure_path = FIGURE_DIR / f"a_share_{target_quadrant}_equity_curve.png"

    plot_data = returns.set_index("trade_date")[["strategy_equity", "benchmark_equity"]]
    ax = plot_data.plot(figsize=(10, 6), linewidth=2)
    ax.set_title(f"A-Share Quadrant Rotation ({data_source}, {target_quadrant})")
    ax.set_xlabel("Trade Date")
    ax.set_ylabel("Growth of 1.0")
    ax.grid(True, alpha=0.3)
    ax.legend(["Strategy", "Equal-weight benchmark"])
    ax.figure.tight_layout()
    ax.figure.savefig(figure_path, dpi=150)
    plt.close(ax.figure)
    return figure_path


def main() -> None:
    args = parse_args()
    prosperity_years = (
        args.prosperity_window_years
        if args.prosperity_window_years is not None
        else (2 if args.data_source == "sample" else 5)
    )
    valuation_years = (
        args.valuation_window_years
        if args.valuation_window_years is not None
        else (3 if args.data_source == "sample" else 15)
    )
    config = QuadrantConfig(
        start_date=args.start_date,
        target_quadrant=args.target_quadrant,
        prosperity_window=252 * prosperity_years,
        valuation_window=252 * valuation_years,
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    panels = load_panels(args)
    weekly_close, weekly_prosperity, weekly_valuation = build_weekly_signals(
        panels,
        config,
    )
    returns = run_weekly_rotation(
        weekly_close,
        weekly_prosperity,
        weekly_valuation,
        target_quadrant=config.target_quadrant,
        transaction_cost_bps=args.transaction_cost_bps,
        annual_risk_free_rate=args.risk_free_rate,
    )
    summary = summarize_backtest(
        returns,
        annual_risk_free_rate=args.risk_free_rate,
    )
    comparison = compare_quadrants(
        weekly_close,
        weekly_prosperity,
        weekly_valuation,
        transaction_cost_bps=args.transaction_cost_bps,
        annual_risk_free_rate=args.risk_free_rate,
    )
    annual_returns = calendar_year_returns(returns)
    latest = latest_quadrants(weekly_prosperity, weekly_valuation)
    migration = quadrant_migration(weekly_prosperity, weekly_valuation)

    output_prefix = f"a_share_{config.target_quadrant}"
    returns.to_csv(OUTPUT_DIR / f"{output_prefix}_weekly_returns.csv", index=False)
    summary.to_csv(OUTPUT_DIR / f"{output_prefix}_backtest_summary.csv", index=False)
    comparison.to_csv(OUTPUT_DIR / "quadrant_comparison.csv", index=False)
    annual_returns.to_csv(
        OUTPUT_DIR / f"{output_prefix}_calendar_year_returns.csv",
        index=False,
    )
    latest.to_csv(OUTPUT_DIR / "latest_quadrants.csv", index=False)
    migration.to_csv(OUTPUT_DIR / "quadrant_migration.csv", index=False)
    figure_path = save_equity_curve(
        returns,
        data_source=args.data_source,
        target_quadrant=config.target_quadrant,
    )

    pd.options.display.float_format = "{:.4f}".format
    print("A-share quadrant rotation complete.")
    print(f"Data source: {args.data_source}")
    print(f"Target quadrant: {config.target_quadrant}")
    print(
        "Windows: "
        f"prosperity={prosperity_years}y, valuation={valuation_years}y"
    )
    print(
        "Assumptions: "
        f"transaction_cost={args.transaction_cost_bps:.1f} bps, "
        f"risk_free_rate={args.risk_free_rate:.2%}"
    )
    print(
        "Signal range: "
        f"{returns['signal_date'].min().date()} to {returns['signal_date'].max().date()}"
    )
    print(f"Weekly observations: {len(returns):,}")
    print(f"Latest quadrant date: {latest['date'].iloc[0].date()}")
    print(f"Migration count: {len(migration)}")
    print(f"Figure: {figure_path.relative_to(PROJECT_DIR)}")
    print()
    print(summary.to_string(index=False))
    print()
    print("Quadrant comparison:")
    print(comparison.to_string(index=False))


if __name__ == "__main__":
    main()
