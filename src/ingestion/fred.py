"""Download FRED series as CSV (no key needed) with a manifest row per series.

Usage: python -m src.ingestion.fred
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
URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}"
RAW_DIR = ROOT / "data" / "raw" / "international" / "fred"
MANIFEST = ROOT / "data" / "source_registry" / "manifests" / "fred_manifest.csv"
FIELDS = ["series", "url", "retrieved_at_utc", "local_path", "bytes", "sha256", "status"]
SERIES = ["DEXINUS", "DCOILBRENTEU"]  # INR per USD daily; Brent crude daily


def main() -> int:
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    new = not MANIFEST.exists()
    with MANIFEST.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if new:
            writer.writeheader()
        for series in SERIES:
            url = URL.format(series=series)
            stamp = datetime.now(timezone.utc)
            row = {"series": series, "url": url, "retrieved_at_utc": stamp.isoformat(timespec="seconds")}
            try:
                resp = requests.get(url, timeout=120)
                resp.raise_for_status()
                target = RAW_DIR / f"{series}_{stamp:%Y%m%d}.csv"
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(resp.content)
                row.update({"local_path": target.relative_to(ROOT).as_posix(), "bytes": len(resp.content),
                            "sha256": hashlib.sha256(resp.content).hexdigest(), "status": "ok"})
            except requests.RequestException as err:
                row["status"] = f"failed: {type(err).__name__}"
            writer.writerow(row)
            print(series, row["status"], row.get("bytes", ""))
            time.sleep(1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
