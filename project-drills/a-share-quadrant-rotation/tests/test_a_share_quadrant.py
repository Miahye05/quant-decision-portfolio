"""Tests for the A-share quadrant rotation reconstruction."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

from a_share_quadrant.backtest import run_weekly_rotation, summarize_backtest  # noqa: E402
from a_share_quadrant.config import QuadrantConfig  # noqa: E402
from a_share_quadrant.sample_data import generate_sample_panels  # noqa: E402
from a_share_quadrant.signals import (  # noqa: E402
    build_weekly_signals,
    latest_quadrants,
    quadrant_migration,
)


class AShareQuadrantPipelineTest(unittest.TestCase):
    def setUp(self) -> None:
        self.config = QuadrantConfig(
            start_date="2021-01-16",
            prosperity_window=252 * 2,
            valuation_window=252 * 3,
        )
        self.panels = generate_sample_panels(periods=1500)

    def test_weekly_signal_pipeline_runs(self) -> None:
        close, prosperity, valuation = build_weekly_signals(self.panels, self.config)
        self.assertFalse(close.empty)
        self.assertFalse(prosperity.empty)
        self.assertFalse(valuation.empty)
        self.assertEqual(set(close.columns), set(prosperity.columns))
        self.assertEqual(set(close.columns), set(valuation.columns))

    def test_rotation_backtest_outputs_summary(self) -> None:
        close, prosperity, valuation = build_weekly_signals(self.panels, self.config)
        returns = run_weekly_rotation(
            close,
            prosperity,
            valuation,
            target_quadrant="low_low",
        )
        summary = summarize_backtest(returns)
        portfolios = set(summary["portfolio"])
        self.assertIn("strategy", portfolios)
        self.assertIn("equal_weight_benchmark", portfolios)
        self.assertIn("strategy_minus_benchmark", portfolios)

    def test_quadrant_outputs_are_available(self) -> None:
        _, prosperity, valuation = build_weekly_signals(self.panels, self.config)
        latest = latest_quadrants(prosperity, valuation)
        migration = quadrant_migration(prosperity, valuation)
        self.assertFalse(latest.empty)
        self.assertIn("quadrant", latest.columns)
        self.assertIn("industry", migration.columns)


if __name__ == "__main__":
    unittest.main()
