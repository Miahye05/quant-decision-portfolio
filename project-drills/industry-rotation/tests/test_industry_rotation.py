"""Basic tests for the industry rotation pipeline."""

from __future__ import annotations

import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

from industry_rotation.backtest import summarize_backtest  # noqa: E402
from industry_rotation.config import BacktestConfig, INDUSTRIES  # noqa: E402
from industry_rotation.french_data import parse_french_10_industry_zip  # noqa: E402
from industry_rotation.momentum import build_momentum_signal_table  # noqa: E402
from industry_rotation.sample_data import generate_sample_panel  # noqa: E402
from industry_rotation.signals import (  # noqa: E402
    build_portfolio_returns,
    build_signal_table,
)


class IndustryRotationPipelineTest(unittest.TestCase):
    def setUp(self) -> None:
        self.config = BacktestConfig(periods=24, top_n=3)
        self.panel = generate_sample_panel(self.config)

    def test_sample_panel_has_expected_shape(self) -> None:
        expected_rows = self.config.periods * len(INDUSTRIES)
        self.assertEqual(len(self.panel), expected_rows)
        self.assertEqual(set(self.panel["industry"].unique()), set(INDUSTRIES))

    def test_signal_table_uses_forward_returns(self) -> None:
        signal_table = build_signal_table(self.panel, top_n=self.config.top_n)
        selected_columns = {
            "monthly_return",
            "forward_return",
            "composite_signal",
            "signal_rank",
            "selected",
        }
        self.assertTrue(selected_columns.issubset(signal_table.columns))
        self.assertFalse(signal_table["forward_return"].isna().any())

    def test_portfolio_holds_configured_number_of_industries(self) -> None:
        signal_table = build_signal_table(self.panel, top_n=self.config.top_n)
        returns = build_portfolio_returns(signal_table)
        self.assertTrue((returns["selected_count"] == self.config.top_n).all())

    def test_backtest_summary_contains_strategy_and_benchmark(self) -> None:
        signal_table = build_signal_table(self.panel, top_n=self.config.top_n)
        returns = build_portfolio_returns(signal_table)
        summary = summarize_backtest(returns)
        portfolios = set(summary["portfolio"])
        self.assertIn("strategy", portfolios)
        self.assertIn("equal_weight_benchmark", portfolios)
        self.assertIn("strategy_minus_benchmark", portfolios)

    def test_french_parser_extracts_monthly_value_weighted_table(self) -> None:
        csv_text = """This file was created using the CRSP database.
It contains value- and equal-weighted returns for 10 industry portfolios.

  Average Value Weighted Returns -- Monthly
,NoDur,Durbl,Manuf,Enrgy,HiTec,Telcm,Shops,Hlth,Utils,Other
202001,1.00,2.00,3.00,4.00,5.00,6.00,7.00,8.00,9.00,10.00
202002,-1.00,-2.00,-3.00,-4.00,-5.00,-6.00,-7.00,-8.00,-9.00,-10.00

  Average Equal Weighted Returns -- Monthly
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = Path(tmpdir) / "french.zip"
            with zipfile.ZipFile(zip_path, "w") as archive:
                archive.writestr("10_Industry_Portfolios.csv", csv_text)

            parsed = parse_french_10_industry_zip(zip_path)

        self.assertEqual(len(parsed), 20)
        self.assertIn("monthly_return", parsed.columns)
        first_return = parsed.loc[parsed["industry_code"] == "NoDur", "monthly_return"].iloc[0]
        self.assertAlmostEqual(first_return, 0.01)

    def test_momentum_pipeline_builds_public_data_signal(self) -> None:
        return_panel = (
            self.panel[["date", "industry"]]
            .assign(monthly_return=self.panel.groupby("industry")["price_index"].pct_change())
            .dropna()
        )
        signal_table = build_momentum_signal_table(
            return_panel,
            top_n=2,
            lookback=6,
            skip_months=1,
        )
        returns = build_portfolio_returns(signal_table)

        self.assertFalse(signal_table.empty)
        self.assertTrue((returns["selected_count"] == 2).all())


if __name__ == "__main__":
    unittest.main()
