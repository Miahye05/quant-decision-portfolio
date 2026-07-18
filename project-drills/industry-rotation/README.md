# Industry Rotation Strategy Backtest

Status: private reconstruction workspace.

This project is the first quantitative anchor in the portfolio. It translates an industry allocation question into a reproducible backtesting workflow.

## Question

Can industry-level prosperity and valuation signals support allocation decisions?

## Current Version

The current version uses a reproducible sample industry panel to test the full workflow before connecting external public data. It is designed to make the analytical logic clear:

1. define industry-level signals
2. rank industries cross-sectionally each month
3. form a top-ranked industry portfolio
4. apply this month's signal to next month's return
5. compare the strategy against an equal-weight industry benchmark
6. report return, risk, drawdown, and excess performance

The sample data is synthetic and should not be interpreted as market evidence. It exists to test the pipeline, code structure, and backtesting logic.

## Data Design

Expected panel format:

| Column | Meaning |
|---|---|
| `date` | month-end date |
| `industry` | industry name |
| `price_index` | industry price index or ETF-adjusted close |
| `prosperity_score` | higher values indicate stronger industry conditions |
| `valuation_score` | higher values indicate more attractive valuation |

For a public release, `price_index` can be built from industry ETFs or public industry portfolios. `prosperity_score` and `valuation_score` should come from public, documented, or reconstructed indicators.

## Methods

- Clean and validate industry panel data
- Construct cross-sectional z-scores for prosperity and valuation
- Combine signals into a composite score
- Select the top-ranked industries each month
- Use next-month returns to avoid look-ahead bias
- Compare against an equal-weight industry benchmark
- Evaluate annualized return, volatility, Sharpe ratio, maximum drawdown, hit rate, and excess return

## Run

From this project folder:

```bash
python3 scripts/run_backtest.py
```

Or:

```bash
make run
make test
```

Generated files:

```text
data/processed/sample_industry_panel.csv
outputs/monthly_portfolio_returns.csv
outputs/backtest_summary.csv
outputs/signal_snapshot_latest.csv
outputs/figures/equity_curve.png
```

## Project Boundary

This project is a research and learning tool. It is not investment advice, and the first version does not claim that the signals have predictive power in live markets.

## Skills Practiced

- Python project organization
- pandas time-series operations
- cross-sectional signal construction
- backtesting without look-ahead bias
- performance evaluation
- analytical documentation

## Public Release Criteria

- Use public, synthetic, or properly anonymized data.
- Remove all internal files, paths, tokens, and company-sensitive materials.
- Document data sources and signal definitions.
- Include reproducible notebook or scripts and figures.
- Include limitations and non-investment disclaimer.
