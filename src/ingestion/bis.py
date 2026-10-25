"""Download central bank policy rates from the BIS statistics API (dataset WS_CBPOL).

The BIS compiles official policy rates from each central bank. For India the daily
series is the RBI repo rate from 3 April 2001. Nepal is not covered by this dataset.

Usage: python -m src.ingestion.bis [--areas IN US]
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]
API = "https://stats.bis.org/api/v1/data/WS_CBPOL/{freq}.{area}"
RAW_DIR = ROOT / "data" / "raw" / "international" / "bis_cbpol"
MANIFEST = ROOT / "data" / "source_registry" / "manifests" / "bis_manifest.csv"
FIELDS = ["dataset", "series_key", "url", "retrieved_at_utc", "local_path", "bytes", "sha256", "status"]


def download(area: str, freq: str = "D", start: str = "2000-01-01") -> dict:
    url = API.format(freq=freq, area=area)
    resp = requests.get(url, params={"format": "csv", "startPeriod": start}, timeout=180)
    resp.raise_for_status()
    stamp = datetime.now(timezone.utc)
    target = RAW_DIR / f"WS_CBPOL_{freq}_{area}_{stamp:%Y%m%d}.csv"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(resp.content)
    return {
        "dataset": "WS_CBPOL",
        "series_key": f"{freq}.{area}",
        "url": resp.url,
        "retrieved_at_utc": stamp.isoformat(timespec="seconds"),
        "local_path": target.relative_to(ROOT).as_posix(),
        "bytes": len(resp.content),
        "sha256": hashlib.sha256(resp.content).hexdigest(),
        "status": "ok",
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--areas", nargs="+", default=["IN", "US"])
    args = parser.parse_args(argv)
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    new = not MANIFEST.exists()
    with MANIFEST.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if new:
            writer.writeheader()
        for area in args.areas:
            row = download(area)
            writer.writerow(row)
            print(area, row["bytes"], "bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
