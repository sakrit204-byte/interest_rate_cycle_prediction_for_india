"""Collect Nepal Rastra Bank documents and statistical tables from Wayback Machine archives.

The NRB website was unreachable from October 2026 (reported as a security incident),
so archived copies of the official files are used. Files are stored unchanged under
data/raw/nepal/nrb_archive/ and every download is recorded in the manifest.

Usage: python -m src.ingestion.nrb_archive [--dry-run]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.ingestion import wayback

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw" / "nepal" / "nrb_archive"
MANIFEST = ROOT / "data" / "source_registry" / "manifests" / "nrb_wayback_manifest.csv"
URL_PREFIX = "nrb.org.np/contents/uploads/"

# category: (include pattern, exclude pattern)
CATEGORIES = {
    "monetary_policy_documents": (
        r"monetary.?policy.*\.pdf$|mid.?term.?review.*\.pdf$|quarter.?review.*\.pdf$",
        r"circular|laghubitta|working_paper|economic_review|study_reports|procedure",
    ),
    "monetary_policy_circulars": (r"circular.*monetary.?policy.*\.pdf$", None),
    "macro_tables": (
        r"(current.?macro|cme_.?tables|key_financial_indicators|macroeconomic.?indicators.?of.?nepal|qeb).*\.xlsx?$",
        None,
    ),
    "interest_rate_structure": (r"interest.?rate.?structure.*\.xlsx?$", r"mfi"),
}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="list selected files without downloading")
    parser.add_argument("--category", choices=sorted(CATEGORIES), action="append")
    args = parser.parse_args(argv)

    if not args.dry_run:
        flagged = wayback.revalidate(MANIFEST, path_root=ROOT)
        print(f"{len(flagged)} saved files failed the format check and will be retried")

    session = wayback.new_session()
    captures = wayback.latest_per_url(wayback.query_cdx(URL_PREFIX, session))
    print(f"{len(captures)} unique archived NRB upload URLs")

    for name in args.category or sorted(CATEGORIES):
        include, exclude = CATEGORIES[name]
        chosen = wayback.select(captures, include, exclude)
        print(f"{name}: {len(chosen)} files")
        if args.dry_run:
            for cap in chosen:
                print(f"  {cap.timestamp} {cap.original}")
            continue
        rows = wayback.download(chosen, name, RAW_DIR / name, MANIFEST, session, path_root=ROOT)
        failed = [r for r in rows if r["status"] != "ok"]
        print(f"  downloaded {len(rows) - len(failed)}, failed {len(failed)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
