# Data files published for the hosted dashboard

The data folders are kept out of git (see `.gitignore`). These six files are committed as an exception, because the hosted Streamlit dashboard cannot run without them. All are free official statistics, republished here unchanged or as derived series, with attribution.

| File | Contents | Source |
|---|---|---|
| `raw/international/bis_cbpol/WS_CBPOL_D_IN_20261025.csv` | RBI policy rate, daily | Bank for International Settlements, central bank policy rates (WS_CBPOL) |
| `raw/international/bis_cbpol/WS_CBPOL_D_US_20261025.csv` | US policy rate, daily | Bank for International Settlements, central bank policy rates (WS_CBPOL) |
| `interim/india/india_macro_monthly.csv` | India CPI, WPI and IIP, monthly | Ministry of Statistics and Programme Implementation (eSankhyiki); IMF for CPI after December 2025 |
| `interim/nepal/nepal_target_monthly.csv` | Nepal interbank rate, raw and seasonally adjusted | Nepal Rastra Bank, Quarterly Economic Bulletin table 41 |
| `processed/india/india_features_cutoff7.csv` | Model inputs at each RBI decision, as known 7 days before it | Derived from the sources above and RBI policy statements |
| `processed/nepal/nepal_features_monthly.csv` | Nepal model inputs, monthly | Derived from Nepal Rastra Bank and IMF monetary and financial statistics |

Rebuild any of them from the raw downloads with the scripts in `src/ingestion` and `src/features`; the download manifests in `data/source_registry/manifests` record each file's address, time and SHA256 hash.
