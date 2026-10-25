"""Download the policy statement documents behind each scheduled RBI decision.

Links come from the saved archive pages (src.ingestion.parse_rbi_policy_index). For each
decision the candidate documents are the entries dated on the decision day or up to
MERGE_DAYS later, ranked by DOC_RANK; every ranked document found is saved, so the
projection extractor can fall back from one to the next.

Output: data/raw/india/rbi_statements/<decision date>_<rank>_<id>.html and
data/source_registry/manifests/rbi_statements_manifest.csv
Usage: python -m src.ingestion.rbi_statements
"""

from __future__ import annotations

import csv
import hashlib
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[2]
ENTRIES = ROOT / "data" / "interim" / "india" / "rbi_policy_index_entries.csv"
DECISIONS = ROOT / "data" / "interim" / "india" / "rbi_decisions.csv"
RAW_DIR = ROOT / "data" / "raw" / "india" / "rbi_statements"
MANIFEST = ROOT / "data" / "source_registry" / "manifests" / "rbi_statements_manifest.csv"
FIELDS = ["decision_date", "rank", "label", "url", "retrieved_at_utc", "local_path", "bytes", "sha256", "status"]
BASE = "https://www.rbi.org.in/Scripts/"
MERGE_DAYS = 5

# rank, label pattern; lower rank is the preferred source of the projections
DOC_RANK = [
    (1, re.compile(r"resolution of the monetary policy committee", re.I)),
    (2, re.compile(r"^(full document|full statement)$|statement on monetary policy|monetary policy statement.*full|bi-?monthly monetary policy", re.I)),
    (3, re.compile(r"press release|press statement|governor's statement|policy statement", re.I)),
]
DOC_URL = re.compile(r"(BS_PressReleaseDisplay|NotificationUser|bs_viewcontent)\.aspx\?(prid|Id)=\d+", re.I)


def normalize(url: str) -> str:
    full = urljoin(BASE, url.strip())
    parts = urlparse(full)
    return f"https://www.rbi.org.in{parts.path}?{parts.query}" if parts.netloc.endswith("rbi.org.in") else full


def candidates(entries: pd.DataFrame, day: pd.Timestamp) -> list[tuple[int, str, str]]:
    near = entries[(entries["date"] >= day) & (entries["date"] <= day + pd.Timedelta(days=MERGE_DAYS))]
    found, seen = [], set()
    for _, e in near.iterrows():
        for item in str(e["links"]).split(" || "):
            label, _, url = item.rpartition(" | ")
            if not DOC_URL.search(url) or "transcript" in label.lower() or "minutes" in label.lower():
                continue
            label_core = re.sub(r"\s+full document$", "", label, flags=re.I)
            for rank, pattern in DOC_RANK:
                if pattern.search(label) or pattern.search(label_core):
                    url = normalize(url)
                    if url not in seen:
                        seen.add(url)
                        found.append((rank, label, url))
                    break
    return sorted(found)


def main() -> int:
    entries = pd.read_csv(ENTRIES, parse_dates=["date"])
    decisions = pd.read_csv(DECISIONS, parse_dates=["date"])
    decisions = decisions[~decisions["inter_meeting"]]
    done = set()
    if MANIFEST.exists():
        done = {(r["decision_date"], r["url"]) for r in csv.DictReader(MANIFEST.open(encoding="utf-8"))
                if r["status"] == "ok"}
    session = requests.Session()
    session.headers["User-Agent"] = "Mozilla/5.0 (research project RateCycle; contact via GitHub)"
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    new = not MANIFEST.exists()
    missing = 0
    with MANIFEST.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if new:
            writer.writeheader()
        for _, d in decisions.iterrows():
            day = d["date"].date().isoformat()
            found = candidates(entries, d["date"])
            if not found:
                missing += 1
                writer.writerow({"decision_date": day, "status": "no_candidate_link"})
                continue
            for rank, label, url in found:
                if (day, url) in done:
                    continue
                row = {"decision_date": day, "rank": rank, "label": label[:200], "url": url,
                       "retrieved_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds")}
                try:
                    resp = session.get(url, timeout=120)
                    resp.raise_for_status()
                    doc_id = re.search(r"(?:prid|Id)=(\d+)", url, re.I).group(1)
                    target = RAW_DIR / f"{day}_{rank}_{doc_id}.html"
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(resp.content)
                    row.update({"local_path": target.relative_to(ROOT).as_posix(), "bytes": len(resp.content),
                                "sha256": hashlib.sha256(resp.content).hexdigest(), "status": "ok"})
                except requests.RequestException as err:
                    row["status"] = f"failed: {type(err).__name__}"
                writer.writerow(row)
                f.flush()
                time.sleep(1.0)
            print(day, [(r, u.rsplit("=", 1)[-1]) for r, _, u in found])
    print(f"decisions without a candidate link: {missing}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
