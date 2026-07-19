"""Download and parse Kenneth French 10 industry portfolio returns."""

from __future__ import annotations

import io
import zipfile
from pathlib import Path
from urllib.request import Request, urlopen

import pandas as pd

from industry_rotation.config import FRENCH_10_INDUSTRY_URL, FRENCH_INDUSTRY_NAMES


def download_french_10_industry_zip(
    destination: Path,
    url: str = FRENCH_10_INDUSTRY_URL,
    timeout: int = 30,
) -> Path:
    """Download the official Kenneth French 10 industry CSV zip."""

    destination.parent.mkdir(parents=True, exist_ok=True)
    request = Request(
        url,
        headers={"User-Agent": "quant-decision-portfolio/0.1"},
    )
    with urlopen(request, timeout=timeout) as response:
        destination.write_bytes(response.read())
    return destination


def parse_french_10_industry_zip(zip_path: Path) -> pd.DataFrame:
    """Parse value-weighted monthly returns into a long industry panel.

    Kenneth French files contain several tables in one CSV. This parser extracts
    the "Average Value Weighted Returns -- Monthly" table.
    """

    with zipfile.ZipFile(zip_path) as archive:
        csv_names = [name for name in archive.namelist() if name.lower().endswith(".csv")]
        if not csv_names:
            raise ValueError(f"No CSV file found inside {zip_path}.")
        text = archive.read(csv_names[0]).decode("utf-8", errors="replace")

    lines = text.splitlines()
    try:
        header_index = next(
            index for index, line in enumerate(lines) if line.strip().startswith(",NoDur")
        )
        end_index = next(
            index
            for index in range(header_index + 1, len(lines))
            if lines[index].strip() == ""
        )
    except StopIteration as exc:
        raise ValueError("Could not locate the monthly value-weighted table.") from exc
    table_text = "\n".join(lines[header_index:end_index])

    wide = pd.read_csv(io.StringIO(table_text))
    date_column = wide.columns[0]
    wide = wide.rename(columns={date_column: "date_code"})
    wide["date_code"] = wide["date_code"].astype(str).str.strip()
    wide = wide[wide["date_code"].str.fullmatch(r"\d{6}")]

    long = wide.melt(
        id_vars="date_code",
        var_name="industry_code",
        value_name="monthly_return",
    )
    long["monthly_return"] = pd.to_numeric(long["monthly_return"], errors="coerce")
    long = long[~long["monthly_return"].isin([-99.99, -999.0])]
    long = long.dropna(subset=["monthly_return"])
    long["monthly_return"] = long["monthly_return"] / 100.0
    long["date"] = (
        pd.to_datetime(long["date_code"], format="%Y%m") + pd.offsets.MonthEnd(0)
    )
    long["industry_code"] = long["industry_code"].str.strip()
    long["industry"] = long["industry_code"].map(FRENCH_INDUSTRY_NAMES).fillna(
        long["industry_code"]
    )

    panel = long[["date", "industry", "industry_code", "monthly_return"]].copy()
    panel = panel.sort_values(["industry", "date"]).reset_index(drop=True)
    panel["price_index"] = panel.groupby("industry")["monthly_return"].transform(
        lambda series: 100 * (1 + series).cumprod()
    )
    return panel.sort_values(["date", "industry"]).reset_index(drop=True)


def load_or_download_french_10_industry(
    raw_zip_path: Path,
    processed_csv_path: Path,
    refresh: bool = False,
) -> pd.DataFrame:
    """Load cached French industry returns or download and parse a fresh copy."""

    if refresh or not raw_zip_path.exists():
        download_french_10_industry_zip(raw_zip_path)

    panel = parse_french_10_industry_zip(raw_zip_path)
    processed_csv_path.parent.mkdir(parents=True, exist_ok=True)
    panel.to_csv(processed_csv_path, index=False)
    return panel
