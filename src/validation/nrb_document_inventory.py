"""Inventory the archived NRB monetary policy PDFs: fiscal year, document type, language, pages.

Output: reports/tables/nrb_document_inventory.csv
Usage: python -m src.validation.nrb_document_inventory
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

import pymupdf as fitz

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "data" / "source_registry" / "manifests" / "nrb_wayback_manifest.csv"
OUT = ROOT / "reports" / "tables" / "nrb_document_inventory.csv"
CATEGORIES = {"monetary_policy_documents", "monetary_policy_circulars"}

# Nepali fiscal years in Bikram Sambat run mid July to mid July; 2078/79 BS is 2021/22 AD.
BS_TO_AD_OFFSET = 57


def fiscal_year(name: str) -> str:
    """Fiscal year as 'YYYY/YY' in AD, from AD (2021_22, 2021-22) or BS (2078_79, 2078-79, 2082-083) patterns.

    The leading 'YYYY_MM_' upload folder added by the archive download is ignored.
    """
    name = re.sub(r"^\d{4}_\d{2}_", "", name)
    for match in re.finditer(r"(20\d\d|19\d\d)[_.\-](\d{2,3})(?!\d)", name):
        start = int(match.group(1))
        if start >= 2050:  # Bikram Sambat year
            start -= BS_TO_AD_OFFSET
        if 1995 <= start <= 2030:
            return f"{start}/{(start + 1) % 100:02d}"
    match = re.search(r"(20[5-9]\d)", name)  # lone BS year such as 2071 or 2072_73 handled above
    if match:
        start = int(match.group(1)) - BS_TO_AD_OFFSET
        return f"{start}/{(start + 1) % 100:02d}"
    return ""


def doc_type(name: str) -> str:
    n = name.lower()
    if "circular" in n:
        return "circular"
    if "press" in n or "media_release" in n:
        return "press_release"
    if "1st" in n or "first" in n:
        return "first_quarter_review"
    if "mid" in n or "half" in n:
        return "mid_term_review"
    if "3rd" in n or "third" in n:
        return "third_quarter_review"
    if "annual" in n and "review" in n:
        return "annual_review"
    if "highlight" in n or "summary" in n or "table" in n:
        return "supplement"
    if "collection" in n:
        return "collection"
    return "annual_policy"


ENGLISH_STOPWORDS = {"the", "of", "and", "to", "in", "is", "for", "be", "will", "has", "with", "by", "as", "on"}


def language(text: str) -> str:
    """English, Nepali (Unicode Devanagari or legacy Preeti font), or no text layer.

    Legacy Nepali fonts such as Preeti store Devanagari as Latin letters, so a Latin
    text layer is only called English when common English function words are frequent.
    """
    letters = [c for c in text if c.isalpha()]
    if len(letters) < 50:
        return "no_text_layer"
    if sum("ऀ" <= c <= "ॿ" for c in letters) / len(letters) > 0.3:
        return "nepali"
    words = re.findall(r"[a-z]+", text.lower())
    share = sum(w in ENGLISH_STOPWORDS for w in words) / max(len(words), 1)
    return "english" if share > 0.08 else "nepali_legacy_font"


def main() -> int:
    fitz.TOOLS.mupdf_display_errors(False)
    rows = {}
    with MANIFEST.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows[r["canonical_url"]] = r
    out = []
    for r in rows.values():
        if r["status"] != "ok" or r["category"] not in CATEGORIES:
            continue
        path = ROOT / r["local_path"]
        unreadable = 0
        sample = ""
        with fitz.open(path) as doc:
            pages = doc.page_count
            for i in range(pages):
                try:
                    text = doc[i].get_text()
                except Exception:  # MuPDF raises its own error types for damaged page trees
                    unreadable += 1
                    continue
                if len(sample) < 4000:
                    sample += text
        name = path.name
        out.append({
            "file": name,
            "category": r["category"],
            "fiscal_year_ad": fiscal_year(name),
            "doc_type": doc_type(name),
            "language": language(sample),
            "pages": pages,
            "unreadable_pages": unreadable,
            "upload_month": "/".join(name.split("_")[:2]),
            "sha256": r["sha256"],
            "original_url": r["original_url"],
        })
    out.sort(key=lambda x: (x["fiscal_year_ad"], x["doc_type"], x["file"]))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(out[0]))
        writer.writeheader()
        writer.writerows(out)
    print(f"{len(out)} documents written to {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
