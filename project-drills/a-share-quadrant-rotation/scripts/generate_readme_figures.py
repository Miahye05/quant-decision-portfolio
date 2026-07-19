"""Generate compact README figures for the A-share quadrant project."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_DIR / "outputs"
ASSET_DIR = PROJECT_DIR / "assets"

NAVY = "#163b73"
BLUE = "#2563a8"
GRID = "#dbe5ef"
TEXT = "#2f3642"
MUTED = "#6b7480"
GRAY = "#8793a0"

QUADRANT_LABELS = {
    "high_prosperity_low_valuation": "High P / Low V",
    "high_high": "High P / High V",
    "low_low": "Low P / Low V",
    "low_prosperity_high_valuation": "Low P / High V",
}


plt.rcParams.update(
    {
        "font.family": "Helvetica Neue",
        "axes.edgecolor": "#9aa8b8",
        "axes.labelcolor": TEXT,
        "xtick.color": TEXT,
        "ytick.color": TEXT,
        "figure.facecolor": "white",
    }
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--target-quadrant",
        default="low_low",
        help="Target quadrant used in output filenames.",
    )
    parser.add_argument(
        "--asset-dir",
        type=Path,
        default=ASSET_DIR,
        help="Directory where README figures are written.",
    )
    return parser.parse_args()


def load_outputs(target_quadrant: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    comparison_path = OUTPUT_DIR / "quadrant_comparison.csv"
    returns_path = OUTPUT_DIR / f"a_share_{target_quadrant}_weekly_returns.csv"
    missing = [
        path.name
        for path in (comparison_path, returns_path)
        if not path.exists()
    ]
    if missing:
        raise FileNotFoundError(
            "Missing outputs: "
            + ", ".join(missing)
            + ". Run scripts/run_quadrant_rotation.py first."
        )
    comparison = pd.read_csv(comparison_path)
    returns = pd.read_csv(returns_path, parse_dates=["trade_date", "signal_date"])
    return comparison, returns


def save_figure(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def create_quadrant_comparison(comparison: pd.DataFrame, path: Path) -> None:
    data = comparison.copy()
    data["label"] = data["target_quadrant"].map(QUADRANT_LABELS)
    ordered = [
        "high_prosperity_low_valuation",
        "high_high",
        "low_low",
        "low_prosperity_high_valuation",
    ]
    data["order"] = data["target_quadrant"].map({name: index for index, name in enumerate(ordered)})
    data = data.sort_values("order")

    fig, axes = plt.subplots(2, 2, figsize=(12, 7.2))
    metrics = [
        ("annualized_return", "Annualized Return", "{:.1%}", BLUE),
        ("active_annualized_return", "Active Annualized Return", "{:.1%}", NAVY),
        ("sharpe_ratio", "Sharpe Ratio", "{:.2f}", BLUE),
        ("max_drawdown", "Max Drawdown", "{:.1%}", GRAY),
    ]
    y_positions = range(len(data))
    for ax, (column, title, fmt, color) in zip(axes.ravel(), metrics):
        ax.barh(y_positions, data[column], color=color, alpha=0.88)
        ax.set_yticks(y_positions, data["label"])
        ax.invert_yaxis()
        ax.axvline(0, color="#8b96a3", linewidth=0.8)
        ax.grid(axis="x", color=GRID, linewidth=0.8, alpha=0.8)
        ax.set_title(title, fontsize=12.5, fontweight="semibold", color=TEXT)
        values = data[column]
        x_min = min(values.min(), 0)
        x_max = max(values.max(), 0)
        x_pad = max((x_max - x_min) * 0.18, 0.025 if column != "sharpe_ratio" else 0.25)
        ax.set_xlim(x_min - x_pad, x_max + x_pad)
        for idx, value in enumerate(data[column]):
            offset = x_pad * 0.2 if value >= 0 else -x_pad * 0.2
            ha = "left" if value >= 0 else "right"
            ax.text(value + offset, idx, fmt.format(value), va="center", ha=ha, fontsize=9, color=TEXT)
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.tick_params(axis="both", labelsize=9)

    fig.suptitle(
        "Four-Quadrant Backtest Comparison",
        fontsize=16,
        fontweight="semibold",
        color=TEXT,
        y=0.99,
    )
    fig.text(
        0.5,
        0.01,
        "Sample-data run; strategy returns are net of the default turnover-cost assumption.",
        ha="center",
        fontsize=9,
        color=MUTED,
    )
    fig.tight_layout(rect=[0, 0.035, 1, 0.96])
    save_figure(fig, path)

def create_equity_curve(returns: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 5.2))
    ax.plot(returns["trade_date"], returns["strategy_equity"], color=BLUE, linewidth=2.3)
    ax.plot(returns["trade_date"], returns["benchmark_equity"], color=GRAY, linewidth=2.0)
    ax.grid(True, color=GRID, linewidth=0.8, alpha=0.8)
    ax.set_title("Target-Quadrant Strategy vs Equal-Weight Benchmark", fontsize=15, fontweight="semibold", color=TEXT, pad=14)
    ax.set_ylabel("Growth of 1.0", fontsize=10.5)
    ax.legend(["Strategy net equity", "Equal-weight benchmark"], frameon=False, loc="upper left")
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(axis="both", labelsize=10)
    fig.tight_layout()
    save_figure(fig, path)


def main() -> None:
    args = parse_args()
    asset_dir = args.asset_dir
    if not asset_dir.is_absolute():
        asset_dir = PROJECT_DIR / asset_dir

    comparison, returns = load_outputs(args.target_quadrant)
    create_quadrant_comparison(comparison, asset_dir / "quadrant_comparison.png")
    create_equity_curve(returns, asset_dir / "equity_curve.png")
    print(f"Generated README figures in {asset_dir.relative_to(PROJECT_DIR)}")


if __name__ == "__main__":
    main()
