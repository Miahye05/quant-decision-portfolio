# Industry Rotation Backtest

Public-data prototype for testing industry rotation signals with U.S. industry portfolios.

## Features

- Downloads and parses Kenneth French U.S. 10 Industry Portfolios
- Builds a 12-month momentum signal with a 1-month skip
- Ranks industries cross-sectionally each month
- Holds the top-ranked industries for the next month
- Compares strategy performance with an equal-weight industry benchmark
- Exports return tables, summary metrics, signal snapshots, and an equity curve

## Data

Public-data mode uses the official Kenneth French 10 Industry Portfolios CSV:

```text
https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/10_Industry_Portfolios_CSV.zip
```

The script extracts monthly value-weighted industry returns, reshapes them into a long panel, and constructs an indexed price series from cumulative returns.

## Method

```text
12-month industry momentum
-> skip most recent month
-> rank industries by signal date
-> hold top N industries next month
-> compare against equal-weight benchmark
```

## Run

```bash
python3 scripts/run_backtest.py --data-source french --refresh-data --start-date 2000-01-31
```

Sample mode:

```bash
python3 scripts/run_backtest.py --data-source sample --refresh-sample
```

Tests:

```bash
python3 -m unittest discover tests
```

## Outputs

```text
outputs/monthly_portfolio_returns.csv
outputs/backtest_summary.csv
outputs/signal_snapshot_latest.csv
outputs/figures/equity_curve.png
```
