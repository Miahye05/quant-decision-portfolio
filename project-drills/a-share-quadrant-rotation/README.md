# A-Share Quadrant Rotation Reconstruction

This project reconstructs an A-share industry quadrant rotation workflow using modular, reproducible code. Data inputs are handled locally and are not included in the repository.

## Brief

![A-share quadrant rotation brief](assets/a-share-quadrant-brief.png)

## Question

Can A-share industry allocation decisions be structured through a two-dimensional framework of prosperity and valuation?

## Methodology

The project starts from a simple economic hypothesis: industry returns may differ when fundamental prosperity and valuation conditions are considered jointly. The four-quadrant framework is used to compare whether a target group shows stronger forward returns, better risk-adjusted performance, or lower drawdowns than an equal-weight industry benchmark.

One testable hypothesis is that high prosperity / low valuation industries may combine improving fundamentals with a valuation cushion, while low prosperity / high valuation industries may face weaker forward risk-reward.

Prosperity is measured with revenue growth, profit growth, and ROE percentiles. Valuation is measured with PE and PB percentiles. Historical percentiles are used so that each industry is compared with its own trailing history rather than with industries that may have structurally different valuation levels.

The default cut point is 0.5. This creates four interpretable groups and keeps the rule transparent enough to audit before adding more complicated signal thresholds.

## Core Logic

The reconstruction follows this workflow:

1. Build industry-level prosperity indicators from revenue growth, profit growth, and ROE.
2. Build industry-level valuation indicators from PE and PB percentiles.
3. Convert daily signals to weekly decision dates.
4. Classify industries into four quadrants.
5. Select a target quadrant using the previous week's signal.
6. Evaluate next-week industry returns against an equal-weight industry benchmark.
7. Compare all four quadrants by return, volatility, Sharpe ratio, drawdown, active return, and turnover.
8. Report performance, latest quadrant distribution, and week-over-week migration.

## Quadrants

| Quadrant | Prosperity | Valuation |
|---|---:|---:|
| High prosperity / high valuation | > 0.5 | > 0.5 |
| High prosperity / low valuation | > 0.5 | <= 0.5 |
| Low prosperity / high valuation | <= 0.5 | > 0.5 |
| Low prosperity / low valuation | <= 0.5 | <= 0.5 |

## Run

The default run uses deterministic synthetic A-share industry data to test the full pipeline.

A private validation version of this project was developed with restricted local A-share industry datasets. The public repository uses deterministic synthetic data to preserve reproducibility while respecting data licensing and confidentiality constraints.

```bash
python3 scripts/run_quadrant_rotation.py --data-source sample
```

The same pipeline can be connected to external industry panels once the input files are standardized.

## Interpretation

The main result table is `outputs/quadrant_comparison.csv`. It is designed to answer four questions:

1. Which quadrant performs best on annualized return and Sharpe ratio?
2. Does the selected quadrant consistently outperform the equal-weight benchmark?
3. How severe is the maximum drawdown?
4. Which calendar years or market regimes weaken the signal?

The target quadrant is not assumed to be correct in advance. The comparison table is meant to test whether a quadrant such as high prosperity / low valuation has stronger empirical support than alternatives such as low prosperity / low valuation.

## Assumptions

- Time alignment: week-ending signals are formed with the previous week's latest available signal; returns are evaluated from the next weekly price point to the following one.
- Empty target weeks: if no industry falls into the selected quadrant, the strategy is treated as holding cash.
- Transaction cost: the default assumption is 10 bps times one-way weekly turnover.
- Sharpe ratio: calculated using a configurable annual risk-free-rate assumption; the default is 0.
- Active return index: `active_return_index` compounds weekly strategy-minus-benchmark returns. It is an active-return index, not the same object as strategy equity divided by benchmark equity.

## Generated Outputs

```text
outputs/a_share_<target_quadrant>_weekly_returns.csv
outputs/a_share_<target_quadrant>_backtest_summary.csv
outputs/a_share_<target_quadrant>_calendar_year_returns.csv
outputs/quadrant_comparison.csv
outputs/latest_quadrants.csv
outputs/quadrant_migration.csv
outputs/figures/a_share_<target_quadrant>_equity_curve.png
```
