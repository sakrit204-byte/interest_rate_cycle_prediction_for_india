"""Collect the RBI archive of monetary policy statements, one page per fiscal year.

Source: https://www.rbi.org.in/Scripts/Annualpolicy.aspx. The year list on that page is an
ordinary form submission (hidden field hdnYear). Each year's page is saved unchanged and
recorded in a manifest; parsing into a decision list happens separately.

Usage: python -m src.ingestion.rbi_policy_index [--years 2002 2027]
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
import sys
import time
from datetime import datetime, timezone
from html import unescape
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]
URL = "https://www.rbi.org.in/Scripts/Annualpolicy.aspx"
RAW_DIR = ROOT / "data" / "raw" / "india" / "rbi_policy_index"
MANIFEST = ROOT / "data" / "source_registry" / "manifests" / "rbi_policy_index_manifest.csv"
FIELDS = ["fiscal_year_end", "url", "retrieved_at_utc", "local_path", "bytes", "sha256", "status"]
USER_AGENT = "Mozilla/5.0 (RateCycleIndiaNepal academic research pipeline)"

HIDDEN_INPUT = re.compile(r'<input[^>]+type="hidden"[^>]*>', re.IGNORECASE)
ATTR = re.compile(r'(name|value)="([^"]*)"')
LINK = re.compile(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', re.IGNORECASE | re.DOTALL)


def hidden_fields(html: str) -> dict[str, str]:
    fields = {}
    for tag in HIDDEN_INPUT.findall(html):
        attrs = dict(ATTR.findall(tag))
        if "name" in attrs:
            fields[attrs["name"]] = unescape(attrs.get("value", ""))
    return fields


def links(html: str) -> list[tuple[str, str]]:
    """(text, href) pairs with tags stripped from the text."""
    out = []
    for href, inner in LINK.findall(html):
        text = re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", inner))).strip()
        if text:
            out.append((text, unescape(href)))
    return out


def fetch_year(session: requests.Session, landing_html: str, year: int) -> str:
    form = hidden_fields(landing_html)
    form["hdnYear"] = str(year)
    form["UsrFontCntr$btn"] = ""
    resp = session.post(URL, data=form, timeout=120)
    resp.raise_for_status()
    return resp.text


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--years", nargs=2, type=int, default=[2002, 2027], metavar=("FIRST", "LAST"),
                        help="fiscal year end, e.g. 2022 means 2021/22")
    args = parser.parse_args(argv)

    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT
    landing = session.get(URL, timeout=120)
    landing.raise_for_status()
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    new = not MANIFEST.exists()

    with MANIFEST.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if new:
            writer.writeheader()
        for year in range(args.years[0], args.years[1] + 1):
            target = RAW_DIR / f"annualpolicy_fy{year}.html"
            row = {"fiscal_year_end": year, "url": f"{URL} (POST hdnYear={year})", "local_path": target.relative_to(ROOT).as_posix()}
            try:
                html = fetch_year(session, landing.text, year)
                data = html.encode("utf-8")
                target.write_bytes(data)
                row.update(bytes=len(data), sha256=hashlib.sha256(data).hexdigest(), status="ok")
            except requests.RequestException as err:
                row.update(bytes="", sha256="", status=f"failed: {type(err).__name__}")
            row["retrieved_at_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
            writer.writerow(row)
            print(year, row["status"])
            time.sleep(2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
