"""Download IMF statistics through the IMF SDMX 2.1 API (api.imf.org).

An independent source for Nepal while the NRB website is down, and a cross check for
India. Monthly series only. Each query is saved unchanged as CSV with a manifest row.

Verified mapping for Nepal against NRB Monetary Policy 2025/26 annex Table 7 (see
docs/data_access.md): IMF MFS_IR indicator DISR ("Discount rate") is the NRB deposit
collection rate (corridor floor), and MFS166 ("Monetary policy related") is the NRB
bank rate (corridor ceiling). The NRB policy rate itself is not in this dataset.

Usage: python -m src.ingestion.imf [short_name ...]
"""

from __future__ import annotations

import csv
import hashlib
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]
API = "https://api.imf.org/external/sdmx/2.1/data/IMF.STA,{flow}/{key}"
RAW_DIR = ROOT / "data" / "raw" / "international" / "imf"
MANIFEST = ROOT / "data" / "source_registry" / "manifests" / "imf_manifest.csv"
FIELDS = ["dataflow", "key", "url", "retrieved_at_utc", "local_path", "bytes", "sha256", "status"]

# dataflow, series key, short name
QUERIES = [
    ("MFS_IR", "NPL..M", "npl_interest_rates"),
    ("MFS_IR", "IND..M", "ind_interest_rates"),
    ("CPI", "NPL.CPI._T+CP01..M", "npl_cpi"),
    ("CPI", "IND.CPI._T+CP01..M", "ind_cpi"),
    # Nepal monetary statistics for the liquidity channel (D030); these flows have four key dimensions
    ("MFS_CBS", "NPL...M", "npl_central_bank"),
    ("MFS_ODC", "NPL...M", "npl_other_depository"),
    ("MFS_DC", "NPL...M", "npl_depository"),
]


def fetch(flow: str, key: str, name: str, session: requests.Session) -> dict:
    url = API.format(flow=flow, key=key)
    resp = session.get(url, headers={"Accept": "application/vnd.sdmx.data+csv;version=1.0.0"}, timeout=300)
    resp.raise_for_status()
    stamp = datetime.now(timezone.utc)
    target = RAW_DIR / f"{flow}_{name}_{stamp:%Y%m%d}.csv"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(resp.content)
    return {
        "dataflow": flow,
        "key": key,
        "url": url,
        "retrieved_at_utc": stamp.isoformat(timespec="seconds"),
        "local_path": target.relative_to(ROOT).as_posix(),
        "bytes": len(resp.content),
        "sha256": hashlib.sha256(resp.content).hexdigest(),
        "status": "ok",
    }


def main() -> int:
    only = set(sys.argv[1:])  # optional short names to fetch, e.g. npl_central_bank
    session = requests.Session()
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    new = not MANIFEST.exists()
    with MANIFEST.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if new:
            writer.writeheader()
        for flow, key, name in QUERIES:
            if only and name not in only:
                continue
            try:
                row = fetch(flow, key, name, session)
            except requests.RequestException as err:
                row = {"dataflow": flow, "key": key, "url": API.format(flow=flow, key=key),
                       "retrieved_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                       "status": f"failed: {type(err).__name__}"}
            writer.writerow({k: row.get(k, "") for k in FIELDS})
            print(flow, key, row["status"], row.get("bytes", ""))
            time.sleep(2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
