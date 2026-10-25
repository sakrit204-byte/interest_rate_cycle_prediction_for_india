"""RBI headline inflation projections, hand coded from the saved policy statements (D024).

The coded table is data/source_registry/rbi_projections_handcoded.csv. Each row gives the
projection stated in one decision's statement, the measure (WPI before 2014, CPI after),
the horizon, the kind of statement, the source file and an exact quote. This module checks
that every quote appears word for word in its saved document, so the coding can be audited.

Coding rule: the RBI's own headline projection for the furthest horizon stated, within
about four quarters; a range is coded at its midpoint. Kinds: projection (a forecast),
objective (a stated aim, common before 2009, such as "contain inflation close to 5.0 per
cent"), restated (an earlier projection repeated), restated_later (the value is known only
from the next statement's account of it), none (no number given), no_document.
An automated regex extractor was tried first and rejected: it misread ranges, picked up core
inflation and missed whole periods.

Output: data/interim/india/rbi_projections.csv
Usage: python -m src.features.rbi_projections
"""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
CODED = ROOT / "data" / "source_registry" / "rbi_projections_handcoded.csv"
DOCS = ROOT / "data" / "raw" / "india" / "rbi_statements"
OUT = ROOT / "data" / "interim" / "india" / "rbi_projections.csv"


def text(path: Path) -> str:
    raw = path.read_bytes().decode("utf-8", "ignore")
    raw = re.sub(r"(?is)<(script|style).*?</\1>", " ", raw)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", raw)))


def load(verify: bool = True) -> pd.DataFrame:
    coded = pd.read_csv(CODED, dtype={"decision_date": str, "quote": str, "doc": str})
    if verify:
        problems = []
        for _, r in coded[coded["quote"].notna()].iterrows():
            path = DOCS / r["doc"]
            if not path.exists():
                problems.append(f"{r['decision_date']}: missing file {r['doc']}")
            elif r["quote"] not in text(path):
                problems.append(f"{r['decision_date']}: quote not found in {r['doc']}")
        if problems:
            raise ValueError("hand coded projections failed verification:\n" + "\n".join(problems))
    return coded


def main() -> int:
    coded = load(verify=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    coded[["decision_date", "proj_infl", "measure", "horizon", "kind"]].to_csv(OUT, index=False)
    print(f"{len(coded)} decisions; projection coded for {coded['proj_infl'].notna().sum()}; "
          f"all {coded['quote'].notna().sum()} quotes verified")
    print(coded["kind"].value_counts().to_string())
    return 0


if __name__ == "__main__":
    sys.exit(main())
