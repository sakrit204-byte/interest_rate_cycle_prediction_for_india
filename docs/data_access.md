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

## Truncated captures (25 October 2026)

* Some archived files were cut off by the crawler, often at exactly 1,048,576 bytes (1 MiB). They start with a valid file signature, so the first check passed them.
* The downloader now also checks completeness: a PDF must end with its end of file marker, and an XLSX must be a readable zip archive. Failed files are deleted, flagged as `invalid_content` in the manifest, and retried from older captures on the next run.
* The revalidation pass flagged 54 files: 25 policy documents (including the English annual policies for 2008/09, 2009/10, 2011/12, 2012/13, 2013/14, 2014/15 and 2023/24), 5 circulars and 24 table workbooks.
* The retry run was stopped by Claude Code because the computer ran low on memory, not because of an error. It resumes where it stopped: `python -m src.ingestion.nrb_archive`.

## RBI and BIS sources (25 October 2026)

* **RBI monetary policy statement archive:** `https://www.rbi.org.in/Scripts/Annualpolicy.aspx`. The year list is a form submission, reproduced by `src/ingestion/rbi_policy_index.py` with a two second pause between requests. 26 fiscal year pages saved; manifest `data/source_registry/manifests/rbi_policy_index_manifest.csv`.
* **BIS central bank policy rates (WS_CBPOL):** `https://stats.bis.org/api/v1/data/WS_CBPOL/D.IN`. Daily RBI repo rate from 3 April 2001; the US series is also saved for the global rate feature. Nepal is not covered. Manifest `data/source_registry/manifests/bis_manifest.csv`.
* The Lakdawala and Sengupta dataset page (`sites.google.com/view/rasesite/...`) returned HTTP 404 on 25 October 2026. The paper was published in the Journal of Money, Credit and Banking, volume 57, issue 2 to 3 (2025), pages 407 to 437, whose replication archive is the next place to look.

## Retry outcome and alternate Nepal sources (25 October 2026)

The NRB server is expected to stay down for some days, so Nepal data now rests on two independent routes rather than waiting for the site.

**Route 1: NRB files from the Internet Archive (completed).** After the third run, all 142 monetary policy documents are complete, including the English annual policies for 2008/09, 2009/10, 2011/12 to 2014/15 and 2023/24 that were truncated before. 22 files have no complete capture (19 table workbooks, 2 circulars, 1 HTTP error). Most are second or third uploads of a release that is saved under another name; which months truly lack a table is checked in the table inventory.

**Route 2: IMF data API (new, `src/ingestion/imf.py`).** Independent of NRB's website, updated by the IMF on 25 October 2026.

| IMF series | Nepal coverage | What it is, verified against NRB annex Table 7 |
|---|---|---|
| MFS_IR, DISR ("Discount rate") | July 1976 to July 2026, monthly | NRB deposit collection rate, the corridor floor: 5.50 in July 2023, 3.00 in June 2024, 2.75 from August 2025 |
| MFS_IR, MFS166 ("Monetary policy related") | July 1976 to July 2026, monthly | NRB bank rate, the corridor ceiling: 7.50 in July 2023, 7.00 in June 2024, 6.50 in October 2024, 6.00 from August 2025, 5.75 from December 2025 |
| MFS_IR, GSTBILY | January 1981 to July 2026 | Treasury bill yield |
| MFS_IR, S13BOND | June 1981 to July 2026 | Government bond yield |
| CPI, all items and food | All items index from the 1960s to March 2026; food from August 2005 | Consumer price index |

* The IMF labels do not match NRB names, which is why the mapping was checked value by value. The NRB policy rate itself is not in the IMF data and still comes from NRB documents.
* The IMF India interest rate query returned no series. India rates come from BIS.
* IMF values are the latest revised figures, not the versions published at each decision date. They are used for cross checks and for the long corridor history; release timing for features comes from the NRB monthly tables where available.

**Other alternates kept in reserve:** World Bank WDI and ADB Key Indicators (annual context), FRED (global series). News reports of NRB announcements may confirm decision dates but are never the source of a rate value.
