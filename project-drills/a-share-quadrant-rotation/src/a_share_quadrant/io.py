"""Input helpers for A-share quadrant rotation data."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from a_share_quadrant.config import REQUIRED_FILES


def _read_excel_panel(path: Path) -> pd.DataFrame:
    panel = pd.read_excel(path, index_col=0)
    panel.index = pd.to_datetime(panel.index)
    panel = panel.sort_index()
    panel.columns = panel.columns.astype(str)
    return panel.apply(pd.to_numeric, errors="coerce")


def load_local_excel_panels(data_dir: Path) -> dict[str, pd.DataFrame]:
    """Load Excel panels with the expected input schema."""

    panels: dict[str, pd.DataFrame] = {}
    missing: list[str] = []
    for key, filename in REQUIRED_FILES.items():
        path = data_dir / filename
        if not path.exists():
            missing.append(filename)
            continue
        panels[key] = _read_excel_panel(path)

    if missing:
        missing_list = ", ".join(missing)
        raise FileNotFoundError(f"Missing required input Excel files: {missing_list}")

    return panels


def common_industries(panels: dict[str, pd.DataFrame]) -> list[str]:
    """Return the common industry columns across all panels."""

    column_sets = [set(panel.columns) for panel in panels.values()]
    if not column_sets:
        return []
    common = set.intersection(*column_sets)
    return sorted(common)


def align_industry_columns(panels: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """Align all panels to the same industry columns."""

    industries = common_industries(panels)
    if not industries:
        raise ValueError("No common industry columns found across input panels.")
    return {key: panel.loc[:, industries].copy() for key, panel in panels.items()}
