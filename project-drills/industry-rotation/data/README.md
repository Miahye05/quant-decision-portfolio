# Data Notes

This folder is for project data.

- `raw/`: source files before cleaning
- `processed/`: reproducible analysis-ready files

Do not commit internal company files, private reports, API tokens, account exports, or restricted third-party datasets.

The current script creates `processed/sample_industry_panel.csv` from deterministic synthetic data so the backtesting workflow can be tested without private materials.

For the public-data version, the script downloads the official Kenneth French U.S. 10 Industry Portfolios CSV zip into `raw/` and writes a cleaned long panel to `processed/french_10_industry_returns.csv`.

Source:

```text
https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/10_Industry_Portfolios_CSV.zip
```
