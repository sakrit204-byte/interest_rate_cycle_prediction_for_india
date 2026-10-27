"""Download geopolitical and global risk indicators (decision D042).

Sources, both free and without an account:
  Caldara and Iacoviello Geopolitical Risk Index, monthly from 1985, global and by country
  (https://www.matteoiacoviello.com/gpr.htm), saved unchanged as .xls
  CBOE VIX daily close from FRED (VIXCLS), saved unchanged as .csv

Brent is already in data/raw/international/fred. Each file gets a manifest row with its hash.
Only VIXCLS is fetched from FRED so the vintages of the other FRED series stay unchanged.

Usage: python -m src.ingestion.geopolitical
"""

from __future__ import annotations

import csv
import hashlib
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "international"
MANIFEST = ROOT / "data" / "source_registry" / "manifests" / "geopolitical_manifest.csv"
FIELDS = ["series", "url", "retrieved_at_utc", "local_path", "bytes", "sha256", "status"]
SOURCES = [
    ("gpr", "https://www.matteoiacoviello.com/gpr_files/data_gpr_export.xls", "gpr", "xls"),
    ("VIXCLS", "https://fred.stlouisfed.org/graph/fredgraph.csv?id=VIXCLS", "fred", "csv"),
]


def main() -> int:
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    new = not MANIFEST.exists()
    with MANIFEST.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if new:
            writer.writeheader()
        for name, url, folder, ext in SOURCES:
            resp = requests.get(url, timeout=120)
            resp.raise_for_status()
            stamp = datetime.now(timezone.utc)
            target = RAW / folder / f"{name}_{stamp:%Y%m%d}.{ext}"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(resp.content)
            writer.writerow({"series": name, "url": url, "retrieved_at_utc": stamp.isoformat(timespec="seconds"),
                             "local_path": target.relative_to(ROOT).as_posix(), "bytes": len(resp.content),
                             "sha256": hashlib.sha256(resp.content).hexdigest(), "status": "ok"})
            print(f"{name}: {len(resp.content)} bytes -> {target.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
