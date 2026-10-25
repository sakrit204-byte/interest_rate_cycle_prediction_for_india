# Data Access Log

Records how each source was reached, problems met, and the workaround used.

## Nepal Rastra Bank: site outage and archived copies

* **Problem:** from 25 October 2026, `www.nrb.org.np` and `nrb.org.np` timed out from this machine, while RBI and FRED responded normally. The user reports the outage is due to a security incident on the NRB site.
* **Workaround:** official NRB files are retrieved from the Internet Archive Wayback Machine, which stores byte copies of files exactly as NRB published them. Files are requested with the `id_` snapshot form, which returns the original bytes without Archive markup.
* **Code:** `src/ingestion/wayback.py` (generic) and `src/ingestion/nrb_archive.py` (NRB selection rules). Run `python -m src.ingestion.nrb_archive --dry-run` to list files, or without the flag to download.
* **Provenance:** every download is recorded in `data/source_registry/manifests/nrb_wayback_manifest.csv` with the original NRB URL, snapshot timestamp, Wayback URL, retrieval time, size and SHA256. Raw files sit in `data/raw/nepal/nrb_archive/` and are not committed to git until redistribution terms are checked.
* **Coverage found in the archive index (25 October 2026):** 12,481 unique archived NRB upload URLs. Selected: 142 monetary policy documents and reviews, 17 monetary policy circulars, 291 macroeconomic and financial table files, and 10 interest rate structure files.
* **Limitations:** the archive holds only what its crawlers captured, so some reviews or monthly tables may be missing. Gaps are listed in the Step 2 feasibility report rather than filled by guesswork. A snapshot timestamp shows when the Archive saw a file, which is not necessarily when NRB published it. Publication dates come from the documents themselves.
* **Verification rule:** once the NRB site is back, a sample of archived files is checked against the live files by SHA256.

## Cross check sources for Nepal (reachable on 25 October 2026)

| Source | Use | Access |
|---|---|---|
| IMF data portal SDMX API (`api.imf.org`) | Nepal CPI, interest rates, reserves, exchange rate as an independent check | Free, no key for public data |
| World Bank WDI API (`api.worldbank.org`) | Annual Nepal inflation, remittances, reserves | Free, CC BY 4.0 |
| ADB Key Indicators (`kidb.adb.org`) | Annual and some quarterly Nepal indicators | Free |
| FRED | Some Nepal series redistributed from the IMF | Free |

## First archived document verified

| File | Snapshot | SHA256 | Checked content |
|---|---|---|---|
| Monetary Policy for 2025/26 (English) | 13 July 2026 | 9DC73262B50E6B367F86A0DE99420324D11D435D5B461B0A6B6113373F02FE1D | Peg to INR kept as nominal anchor and intermediate target; weighted average interbank rate as operating target; policy rate cut from 5.0 to 4.5 percent, bank rate from 6.5 to 6.0 percent, deposit collection rate from 3.0 to 2.75 percent; annex table of policy rates mid July 2023 to mid June 2025 |

## NRB archive download results (25 October 2026)

| Category | Selected | Saved and format checked | Not recovered |
|---|---|---|---|
| Monetary policy documents and reviews | 142 | 142 | 0 |
| Monetary policy circulars | 17 | 17 | 0 |
| Macroeconomic and financial tables | 291 | 290 | 1 |
| Interest rate structure tables | 10 | 10 | 0 |

* Total saved: about 397 MB, 459 files.
* Junk captures found and handled: 19 archived "Excel" files were actually a captive portal login redirect page stored by a crawler. The downloader now checks file signatures (PDF, XLSX, XLS) and falls back to older captures of the same URL. All 19 were recovered from earlier valid captures. The manifest keeps the rejected attempts as `invalid_content` rows; it is append only.
* The single unrecovered file is a third upload (`...2081.82-2.xlsx`) of the three month 2081/82 tables; two other uploads of the same release were saved.
* Next: Step 2 parses the monetary policy documents into a dated NRB decision table and inventories which months the macro tables cover.
