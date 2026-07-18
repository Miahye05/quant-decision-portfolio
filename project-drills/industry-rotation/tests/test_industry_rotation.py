"""Basic tests for the industry rotation pipeline."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

from industry_rotation.backtest import summarize_backtest  # noqa: E402
from industry_rotation.config import BacktestConfig, INDUSTRIES  # noqa: E402
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


if __name__ == "__main__":
    unittest.main()
