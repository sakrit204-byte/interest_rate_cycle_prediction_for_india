"""Parse saved RBI monetary policy index pages into a table of dated entries.

Each entry on the page is a date header row followed by a title header row and a block
of links. Output: data/interim/india/rbi_policy_index_entries.csv with one row per entry.

Usage: python -m src.ingestion.parse_rbi_policy_index
"""

from __future__ import annotations

import csv
import re
import sys
from datetime import datetime
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw" / "india" / "rbi_policy_index"
OUT = ROOT / "data" / "interim" / "india" / "rbi_policy_index_entries.csv"

LINK = re.compile(r"""<a\s[^>]*href=["']([^"']+)["'][^>]*>(.*?)</a>""", re.IGNORECASE | re.DOTALL)
HEADER = re.compile(r'<td class="tableheader"><b>(.*?)</b></td>', re.IGNORECASE | re.DOTALL)
DATE_FORMATS = ("%b %d, %Y", "%B %d, %Y")


def clean(text: str) -> str:
    text = unescape(re.sub(r"<[^>]+>", " ", text))
    # Curly apostrophe, en and em dash, and the mojibake form of the apostrophe found on some pages.
    text = (text.replace(chr(0x2019), "'").replace(chr(0x2013), " ").replace(chr(0x2014), " ")
            .replace(chr(0xE2) + chr(0x20AC) + chr(0x2122), "'"))
    return re.sub(r"\s+", " ", text).strip()


def parse_date(text: str):
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def links(block: str) -> str:
    """Links of one entry as 'label | url' lines; the label includes the text before a
    'Full Document' link, which is where the RBI names the document."""
    out = []
    last = 0
    for m in LINK.finditer(block):
        text = clean(m.group(2))
        if text.lower().startswith("full document") or not text:
            before = clean(block[last:m.start()])
            text = f"{before[-120:]} {text}".strip()
        out.append(f"{text} | {m.group(1).strip()}")
        last = m.end()
    return " || ".join(out)


def entries(html: str) -> list[dict]:
    """Pair each date header with the title header that follows it."""
    out = []
    headers = [(m.start(), m.end(), clean(m.group(1))) for m in HEADER.finditer(html)]
    for i, (start, end, text) in enumerate(headers):
        date = parse_date(text)
        if date is None or i + 1 >= len(headers):
            continue
        title_end = headers[i + 1][1]
        title = headers[i + 1][2]
        if parse_date(title) is not None:
            continue
        block_end = headers[i + 2][0] if i + 2 < len(headers) else len(html)
        block = html[title_end:block_end]
        body = clean(block)
        out.append({"date": date.isoformat(), "title": title, "body": body[:1500], "links": links(block)})
    return out


def main() -> int:
    rows = []
    for path in sorted(RAW_DIR.glob("annualpolicy_fy*.html")):
        fy = int(re.search(r"fy(\d{4})", path.name).group(1))
        for e in entries(path.read_text(encoding="utf-8")):
            rows.append({"fiscal_year_end": fy, **e, "source_file": path.relative_to(ROOT).as_posix()})
    rows.sort(key=lambda r: r["date"])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["fiscal_year_end", "date", "title", "body", "links", "source_file"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"{len(rows)} entries written to {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
