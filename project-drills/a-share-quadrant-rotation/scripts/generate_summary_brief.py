"""Generate a sanitized summary brief for the A-share quadrant project."""

from __future__ import annotations

import argparse
import textwrap
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_DIR / "outputs"
FIGURE_DIR = OUTPUT_DIR / "figures"

NAVY = "#163b73"
BLUE = "#2563a8"
LIGHT_BLUE = "#d9e8f7"
GRID = "#e8edf3"
TEXT = "#3f4652"
MUTED = "#687384"
BENCHMARK = "#7b8794"

plt.rcParams.update(
    {
        "font.family": "Helvetica Neue",
        "axes.edgecolor": "#8aa0b8",
        "axes.labelcolor": TEXT,
        "xtick.color": TEXT,
        "ytick.color": TEXT,
    }
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--target-quadrant",
        default="low_low",
        help="Target quadrant used in the output filenames.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Brief output path. Defaults to outputs/figures/a_share_<target>_summary_brief.png.",
    )
    return parser.parse_args()


def load_outputs(target_quadrant: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    summary_path = OUTPUT_DIR / f"a_share_{target_quadrant}_backtest_summary.csv"
    returns_path = OUTPUT_DIR / f"a_share_{target_quadrant}_weekly_returns.csv"
    if not summary_path.exists() or not returns_path.exists():
        raise FileNotFoundError(
            "Missing backtest outputs. Run scripts/run_quadrant_rotation.py first."
        )
    summary = pd.read_csv(summary_path)
    returns = pd.read_csv(returns_path, parse_dates=["trade_date", "signal_date"])
    return summary, returns


def draw_background(fig: plt.Figure) -> None:
    """Draw a light grid background in figure coordinates."""

    for x_value in [i / 12 for i in range(13)]:
        fig.lines.append(
            plt.Line2D(
                [x_value, x_value],
                [0, 1],
                transform=fig.transFigure,
                color=GRID,
                linewidth=1,
                zorder=-10,
            )
        )
    for y_value in [i / 18 for i in range(19)]:
        fig.lines.append(
            plt.Line2D(
                [0, 1],
                [y_value, y_value],
                transform=fig.transFigure,
                color=GRID,
                linewidth=1,
                zorder=-10,
            )
        )


def add_section_bar(ax: plt.Axes, title: str) -> None:
    ax.axis("off")
    ax.add_patch(
        plt.Rectangle((0, 0.18), 1, 0.64, transform=ax.transAxes, color=NAVY)
    )
    ax.text(
        0.5,
        0.5,
        title,
        ha="center",
        va="center",
        color="white",
        fontsize=16,
        fontweight="semibold",
        transform=ax.transAxes,
    )


def add_table(ax: plt.Axes, columns: list[str], rows: list[list[str]], font_size: int = 9) -> None:
    ax.axis("off")
    table = ax.table(
        cellText=rows,
        colLabels=columns,
        cellLoc="center",
        colLoc="center",
        loc="center",
        bbox=[0, 0, 1, 1],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(font_size)
    for (row, _column), cell in table.get_celld().items():
        cell.set_edgecolor("#7a8796")
        cell.set_linewidth(0.65)
        if row == 0:
            cell.set_facecolor(LIGHT_BLUE)
            cell.set_text_props(weight="semibold", color=NAVY)
        elif row % 2 == 0:
            cell.set_facecolor("#f7fafd")
            cell.set_text_props(weight="normal", color="#202733")
        else:
            cell.set_text_props(weight="normal", color="#202733")


def add_metric_cards(ax: plt.Axes, summary: pd.DataFrame) -> None:
    ax.axis("off")
    metrics = summary.set_index("portfolio")
    strategy = metrics.loc["strategy"]
    benchmark = metrics.loc["equal_weight_benchmark"]
    excess = metrics.loc["strategy_minus_benchmark"]
    cards = [
        ("Strategy annualized", f"{strategy['annualized_return']:.1%}"),
        ("Benchmark annualized", f"{benchmark['annualized_return']:.1%}"),
        ("Excess annualized", f"{excess['annualized_return']:.1%}"),
        ("Max drawdown", f"{strategy['max_drawdown']:.1%}"),
    ]

    for index, (label, value) in enumerate(cards):
        left = index * 0.25 + 0.015
        ax.add_patch(
            plt.Rectangle(
                (left, 0.08),
                0.22,
                0.84,
                transform=ax.transAxes,
                facecolor="white",
                edgecolor="#cbd5e1",
                linewidth=1,
            )
        )
        ax.text(
            left + 0.11,
            0.61,
            value,
            ha="center",
            va="center",
            fontsize=16,
            fontweight="semibold",
            color=BLUE,
            transform=ax.transAxes,
        )
        ax.text(
            left + 0.11,
            0.33,
            label,
            ha="center",
            va="center",
            fontsize=8.5,
            color=MUTED,
            transform=ax.transAxes,
        )


def create_brief(target_quadrant: str, output_path: Path) -> Path:
    summary, returns = load_outputs(target_quadrant)

    fig = plt.figure(figsize=(9, 16), dpi=160)
    fig.patch.set_facecolor("white")
    draw_background(fig)
    grid = fig.add_gridspec(
        nrows=9,
        ncols=1,
        height_ratios=[1.2, 0.45, 1.65, 0.45, 1.2, 0.55, 1.0, 0.45, 2.5],
        hspace=0.16,
        left=0.055,
        right=0.945,
        top=0.97,
        bottom=0.07,
    )

    header = fig.add_subplot(grid[0])
    header.axis("off")
    header.text(
        0.0,
        0.78,
        "A-Share Quadrant Rotation",
        fontsize=27,
        fontweight="semibold",
        color=TEXT,
        transform=header.transAxes,
    )
    header.text(
        0.0,
        0.39,
        "Prosperity x Valuation Industry Framework",
        fontsize=18,
        fontweight="semibold",
        color=NAVY,
        transform=header.transAxes,
    )
    header.text(
        0.0,
        0.08,
        "Sanitized brief report generated from standardized industry-panel outputs.",
        fontsize=10,
        color=MUTED,
        transform=header.transAxes,
    )

    add_section_bar(fig.add_subplot(grid[1]), "Quadrant Logic")
    quadrant_ax = fig.add_subplot(grid[2])
    add_table(
        quadrant_ax,
        ["Quadrant", "Signal", "Interpretation", "Use"],
        [
            ["Q1", "High prosperity + high valuation", "Crowded leader", "Watch valuation risk"],
            ["Q2", "Low prosperity + high valuation", "Valuation trap", "Avoid or monitor"],
            ["Q3", "Low prosperity + low valuation", "Neglected value", "Contrarian target"],
            ["Q4", "High prosperity + low valuation", "Quality value", "Research priority"],
        ],
        font_size=8.7,
    )

    add_section_bar(fig.add_subplot(grid[3]), "Signal Construction")
    signal_ax = fig.add_subplot(grid[4])
    add_table(
        signal_ax,
        ["Axis", "Indicators"],
        [
            ["Prosperity", "Revenue growth percentile;\nprofit growth percentile;\nROE percentile"],
            ["Valuation", "PE percentile; PB percentile"],
            ["Timing", "Previous week's signal; next week's return"],
        ],
        font_size=9.5,
    )

    add_section_bar(fig.add_subplot(grid[5]), "Backtest Snapshot")
    add_metric_cards(fig.add_subplot(grid[6]), summary)

    add_section_bar(fig.add_subplot(grid[7]), "Strategy vs Benchmark")
    chart_ax = fig.add_subplot(grid[8])
    chart_data = returns.set_index("trade_date")[["strategy_equity", "benchmark_equity"]]
    chart_ax.plot(chart_data.index, chart_data["strategy_equity"], color=BLUE, linewidth=2.2)
    chart_ax.plot(chart_data.index, chart_data["benchmark_equity"], color=BENCHMARK, linewidth=1.9)
    chart_ax.grid(True, alpha=0.35)
    chart_ax.legend(["Strategy", "Equal-weight benchmark"], loc="upper left", frameon=True)
    chart_ax.set_title("Equity Curve (Growth of 1.0)", fontsize=11, pad=8)

    footer = (
        "Note: This brief report is generated from reproducible project outputs. "
        "No source files, vendor names, file paths, or institutional branding are included."
    )
    fig.text(0.055, 0.025, textwrap.fill(footer, width=135), fontsize=8.3, color=MUTED)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=160)
    plt.close(fig)
    return output_path


def main() -> None:
    args = parse_args()
    output = args.output or (
        FIGURE_DIR / f"a_share_{args.target_quadrant}_summary_brief.png"
    )
    if not output.is_absolute():
        output = PROJECT_DIR / output
    output_path = create_brief(args.target_quadrant, output)
    print(f"Generated brief: {output_path.relative_to(PROJECT_DIR)}")


if __name__ == "__main__":
    main()
