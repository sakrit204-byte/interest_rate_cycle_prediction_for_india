"""Nepal monthly interbank rate from the NRB Quarterly Economic Bulletin (archived copy).

Source: table 41 "Weighted Average Interbank Rate (Among Commercial Banks)", mid month
values by Nepali fiscal year (mid July to mid July), in the latest archived QEB workbook.
Columns Aug to Dec belong to the first calendar year of the fiscal year, Jan to Jul to the
second. A value labelled Aug is the rate at mid August.

Output: data/interim/nepal/nepal_interbank_monthly.csv
Usage: python -m src.features.nepal_interbank
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import openpyxl
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
TABLES = ROOT / "data" / "raw" / "nepal" / "nrb_archive" / "macro_tables"
OUT = ROOT / "data" / "interim" / "nepal" / "nepal_interbank_monthly.csv"
SHEET = "41.42.43"
TITLE = "Weighted Average Interbank Rate"
MONTHS = ["Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul"]


def latest_qeb() -> Path:
    files = sorted(TABLES.rglob("*QEB*.xlsx"), key=lambda p: p.name)
    if not files:
        raise FileNotFoundError("no archived QEB workbook; run python -m src.ingestion.nrb_archive")
    return files[-1]


def parse(path: Path) -> pd.Series:
    ws = openpyxl.load_workbook(path, read_only=True, data_only=True)[SHEET]
    rows = [[c for c in r] for r in ws.iter_rows(values_only=True)]
    start = next(i for i, r in enumerate(rows) if r and r[0] and TITLE in str(r[0]))
    out = {}
    for r in rows[start + 1:]:
        cells = [c for c in r if c is not None]
        if not cells:
            continue
        label = str(cells[0])
        if not re.fullmatch(r"\d{4}/\d{2}", label):
            if out and not re.match(r"\d", label):
                break  # next table starts
            continue
        first_year = int(label[:4])
        for month, value in zip(MONTHS, cells[1:13]):
            if isinstance(value, (int, float)):
                year = first_year if month in MONTHS[:5] else first_year + 1
                out[pd.Period(f"{year}-{month}", freq="M")] = float(value)
    return pd.Series(out, name="interbank_rate").sort_index()


def main() -> int:
    path = latest_qeb()
    s = parse(path)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    frame = s.to_frame()
    frame["source_file"] = path.name
    frame.index.name = "month"
    frame.to_csv(OUT)
    print(f"{len(s)} months, {s.index.min()} to {s.index.max()}, from {path.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
