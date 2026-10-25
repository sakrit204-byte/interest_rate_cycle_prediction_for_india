"""Inventory the archived NRB macroeconomic table workbooks.

For each workbook: the data period it covers (from the file name), upload month, sheet
count, and whether key tables (CPI, interest rates, credit, reserves, remittances) appear.
Output: reports/tables/nrb_table_inventory.csv

Usage: python -m src.validation.nrb_table_inventory
"""

from __future__ import annotations

import csv
import re
import sys
import warnings
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "data" / "source_registry" / "manifests" / "nrb_wayback_manifest.csv"
OUT = ROOT / "reports" / "tables" / "nrb_table_inventory.csv"

MONTH_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
               "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "annual": 12}
KEY_TABLES = {
    "cpi": r"consumer price index|\bcpi\b",
    "interest_rates": r"interest rate|interbank|policy rate|bank rate",
    "credit": r"private sector credit|claims on private|credit to private",
    "reserves": r"foreign exchange reserve|gross foreign|reserves",
    "remittances": r"remittance|workers'? remittances",
    "trade": r"export|import",
}


def coverage_months(name: str) -> int | None:
    """Months of the Nepali fiscal year covered, from names such as 'Based on Three Months data'."""
    m = re.search(r"based_on_(\w+?)_months?_data", name, re.IGNORECASE)
    if m and m.group(1).lower() in MONTH_WORDS:
        return MONTH_WORDS[m.group(1).lower()]
    if re.search(r"based_on_annual", name, re.IGNORECASE):
        return 12
    return None


def scan(path: Path) -> dict:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        sheets = pd.read_excel(path, sheet_name=None, header=None, nrows=6)
    text = " ".join(
        " ".join(str(v) for v in df.astype(str).values.ravel() if v != "nan") for df in sheets.values()
    ).lower()
    found = {k: bool(re.search(p, text)) for k, p in KEY_TABLES.items()}
    return {"n_sheets": len(sheets), "first_sheets": "; ".join(list(sheets)[:6]), **found}


def main() -> int:
    latest = {}
    with MANIFEST.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            latest[r["canonical_url"]] = r
    out = []
    for r in latest.values():
        if r["status"] != "ok" or r["category"] != "macro_tables":
            continue
        path = ROOT / r["local_path"]
        row = {"file": path.name, "upload_month": "/".join(path.name.split("_")[:2]),
               "coverage_months": coverage_months(path.name)}
        try:
            row.update(scan(path), read_status="ok")
        except Exception as err:  # unreadable workbook is recorded, not hidden
            row.update(read_status=f"error: {type(err).__name__}")
        out.append(row)
    out.sort(key=lambda x: (x["upload_month"], x["file"]))
    fields = ["file", "upload_month", "coverage_months", "read_status", "n_sheets", "first_sheets", *KEY_TABLES]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows({k: row.get(k, "") for k in fields} for row in out)
    print(f"{len(out)} workbooks written to {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
