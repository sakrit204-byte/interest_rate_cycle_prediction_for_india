"""Collect NRB macro table workbooks directly from the live NRB website (decision D046).

The site was unreachable when the Wayback collection was built (D012). It is reachable again
from 28 October 2026, so this module fills what the archive could not supply:

* every workbook behind a "Tables" post of the "Current Macroeconomic and Financial Situation"
  category, found through the category RSS feed;
* every macro table URL whose Wayback copy failed (status other than ok in the Wayback manifest);
* every workbook of the NRB "Database on Nepalese Economy" (external, financial, fiscal and real
  sector pages), the continuous historical series, saved under data/raw/nepal/nrb_database/.

Macro tables are saved unchanged to the same folder as the archived copies, so the table parser
reads both. A file already held as a valid Wayback copy is not fetched again. Each download gets a row
in its own manifest with the same fields as the Wayback manifest (the wayback fields left empty).

Usage: python -m src.ingestion.nrb_live [--dry-run]
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd
import requests

from src.ingestion import wayback
from src.ingestion.nrb_archive import CATEGORIES, MANIFEST as WAYBACK_MANIFEST, RAW_DIR

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "data" / "source_registry" / "manifests" / "nrb_live_manifest.csv"
FEED_URL = "https://www.nrb.org.np/category/current-macroeconomic-situation/feed/"
PAUSE = 1.0
INCLUDE = re.compile(CATEGORIES["macro_tables"][0], re.IGNORECASE)
UPLOAD = re.compile(r'href="(https?://(?:www\.)?nrb\.org\.np/contents/uploads/[^"]+\.xlsx?)"', re.IGNORECASE)
DATABASE_URL = "https://www.nrb.org.np/database-on-nepalese-economy/"
DATABASE_SECTORS = ["external-sector", "financial-sector", "fiscal-sector", "real-sector"]
DATABASE_DIR = ROOT / "data" / "raw" / "nepal" / "nrb_database"
ITEM = re.compile(r"<item>\s*<title>([^<]*)</title>\s*<link>([^<?]+)", re.IGNORECASE)


def _get(session, url):
    content, _ = wayback._fetch(session, url, retries=3, pause_seconds=PAUSE)
    time.sleep(PAUSE)
    return content


def discover(session) -> list[str]:
    """Workbook URLs behind every "Tables" post of the category.

    The category pages build their post list by script, so posts are read from the RSS feed,
    page by page until a page has no items. A table post redirects to its workbook, so the
    redirect target is taken without downloading the file.
    """
    posts, page = [], 1
    while True:
        xml = _get(session, FEED_URL if page == 1 else f"{FEED_URL}?paged={page}")
        items = [] if xml is None else ITEM.findall(xml.decode("utf-8", "ignore"))
        if not items:
            break
        posts += [link for title, link in items if "table" in title.lower()]
        page += 1
    posts = list(dict.fromkeys(posts))
    print(f"{len(posts)} table posts on {page - 1} feed pages")
    files = []
    for post in posts:
        try:
            resp = session.head(post, allow_redirects=True, timeout=60)
            if UPLOAD.search(f'href="{resp.url}"'):
                files.append(resp.url)
            else:
                print(f"  no workbook behind {post}")
        except requests.RequestException as err:
            print(f"  {type(err).__name__} for {post}")
        time.sleep(PAUSE)
    return list(dict.fromkeys(files))


def database(session) -> list[tuple[str, str]]:
    """(sector, workbook URL) for every workbook on the sector pages of the NRB time series database."""
    found = []
    for sector in DATABASE_SECTORS:
        html = _get(session, f"{DATABASE_URL}{sector}/")
        if html is not None:
            found += [(sector, u) for u in UPLOAD.findall(html.decode("utf-8", "ignore"))]
    return list(dict.fromkeys(found))


def save(session, url: str, category: str, out_dir: Path) -> dict:
    url = url.replace("http://", "https://")
    target = out_dir / wayback.local_name(wayback.Capture("", url, "", ""))
    row = {"category": category, "original_url": url, "canonical_url": canonical(url),
           "local_path": target.relative_to(ROOT).as_posix()}
    content, info = wayback._fetch(session, url, retries=3, pause_seconds=PAUSE)
    row.update(retrieved_at_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"), **info)
    if content is not None:
        row.update(bytes=len(content), sha256=hashlib.sha256(content).hexdigest())
        if wayback.is_complete(content, url):
            out_dir.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
            row["status"] = "ok"
        else:
            row.update(status="invalid_content", local_path="")
    else:
        row["local_path"] = ""
    wayback._append(MANIFEST, row)
    print(f"{row['status']:>16}  {url.rsplit('/uploads/', 1)[-1]}")
    time.sleep(PAUSE)
    return row


def canonical(url: str) -> str:
    return wayback.Capture("", url, "", "").canonical


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="list files without downloading")
    args = parser.parse_args(argv)

    session = wayback.new_session()
    held = wayback._completed(WAYBACK_MANIFEST) | wayback._completed(MANIFEST)
    wb = pd.read_csv(WAYBACK_MANIFEST, dtype=str).drop_duplicates("canonical_url", keep="last")
    failed = wb.loc[(wb["category"] == "macro_tables") & (wb["status"] != "ok"), "original_url"].tolist()
    listed = [u for u in discover(session) if INCLUDE.search(u.rsplit("/", 1)[-1])]
    todo = [u for u in dict.fromkeys(listed + failed) if canonical(u) not in held]
    print(f"{len(listed)} macro table workbooks linked on the site, {len(failed)} failed Wayback copies, "
          f"{len(todo)} not yet held")
    db = [(s, u) for s, u in database(session) if canonical(u) not in held]
    print(f"{len(db)} database workbooks not yet held")
    if args.dry_run:
        print("\n".join(todo + [f"{s}: {u}" for s, u in db]))
        return 0

    for url in todo:
        save(session, url, "macro_tables", RAW_DIR / "macro_tables")
    for sector, url in db:
        save(session, url, f"database_{sector.replace('-', '_')}", DATABASE_DIR / sector.replace("-", "_"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
