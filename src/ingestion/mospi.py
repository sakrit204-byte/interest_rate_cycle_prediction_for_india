"""Download India CPI, WPI and IIP from the MoSPI eSankhyiki API (api.mospi.gov.in).

These endpoints are open: no account or token is needed. Results are paged at most 200
records per request; every page is fetched and all rows are saved together as one CSV
per query, with a manifest row (URL, time, bytes, SHA256, record count).

Endpoints and filter codes were found by probing on 25 October 2026 (see
docs/data_access.md): state_code=99 is All India; WPI headline is major_group_code
1000000000 on base 2011-12 and 1 on bases 2004-05 and 1993-94; IIP type=General gives the
headline index. The CPI 2024=100 series (from January 2026) was not found on this API.

Usage: python -m src.ingestion.mospi
"""

from __future__ import annotations

import csv
import hashlib
import io
import ssl
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
import requests.adapters

ROOT = Path(__file__).resolve().parents[2]
API = "https://api.mospi.gov.in/api/"
RAW_DIR = ROOT / "data" / "raw" / "india" / "mospi"
MANIFEST = ROOT / "data" / "source_registry" / "manifests" / "mospi_manifest.csv"
FIELDS = ["name", "endpoint", "params", "retrieved_at_utc", "local_path", "records",
          "expected_records", "bytes", "sha256", "status"]
PAGE_SIZE = 200

# short name, endpoint, filters
QUERIES = [
    ("cpi_2012_all_india", "cpi/getCPIIndex", {"base_year": "2012", "state_code": "99"}),
    ("wpi_2011_12_headline", "wpi/getWpiRecords", {"base_year": "2011-12", "major_group_code": "1000000000"}),
    ("wpi_2004_05_headline", "wpi/getWpiRecords", {"base_year": "2004-05", "major_group_code": "1"}),
    ("wpi_1993_94_headline", "wpi/getWpiRecords", {"base_year": "1993-94", "major_group_code": "1"}),
    ("iip_2022_23_general", "iip/getIIPMonthly", {"base_year": "2022-23", "type": "General"}),
    ("iip_2011_12_general", "iip/getIIPMonthly", {"base_year": "2011-12", "type": "General"}),
    ("iip_2004_05_general", "iip/getIIPMonthly", {"base_year": "2004-05", "type": "General"}),
    ("iip_1993_94_general", "iip/getIIPMonthly", {"base_year": "1993-94", "type": "General"}),
]


class LegacyRenegotiationAdapter(requests.adapters.HTTPAdapter):
    """The MoSPI server needs legacy TLS renegotiation, which OpenSSL 3 refuses by default.

    Only that option is enabled; certificate and host name verification stay on.
    """

    def init_poolmanager(self, *args, **kwargs):
        ctx = ssl.create_default_context()
        ctx.options |= getattr(ssl, "OP_LEGACY_SERVER_CONNECT", 0x4)
        kwargs["ssl_context"] = ctx
        return super().init_poolmanager(*args, **kwargs)


def make_session() -> requests.Session:
    session = requests.Session()
    session.mount("https://api.mospi.gov.in/", LegacyRenegotiationAdapter())
    return session


def fetch_all(endpoint: str, params: dict, session: requests.Session) -> tuple[list[dict], int]:
    """All rows of a paged query and the total the API reports."""
    rows: list[dict] = []
    page, total_pages, expected = 1, 1, 0
    while page <= total_pages:
        query = {**params, "Format": "JSON", "limit": PAGE_SIZE, "page": page}
        for attempt in range(4):
            try:
                resp = session.get(API + endpoint, params=query, timeout=120)
                resp.raise_for_status()
                body = resp.json()
                break
            except (requests.RequestException, ValueError):
                if attempt == 3:
                    raise
                time.sleep(5 * (attempt + 1))
        meta = body.get("meta_data") or {}
        total_pages = int(meta.get("totalPages") or 0)
        expected = int(meta.get("totalRecords") or 0)
        rows.extend(body.get("data") or [])
        page += 1
        time.sleep(0.5)
    return rows, expected


def to_csv(rows: list[dict]) -> bytes:
    fields: list[str] = []
    for r in rows:
        fields.extend(k for k in r if k not in fields)
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue().encode("utf-8")


def main() -> int:
    session = make_session()
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    new = not MANIFEST.exists()
    with MANIFEST.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if new:
            writer.writeheader()
        for name, endpoint, params in QUERIES:
            stamp = datetime.now(timezone.utc)
            row = {"name": name, "endpoint": endpoint,
                   "params": "&".join(f"{k}={v}" for k, v in params.items()),
                   "retrieved_at_utc": stamp.isoformat(timespec="seconds")}
            try:
                rows, expected = fetch_all(endpoint, params, session)
            except requests.RequestException as err:
                row["status"] = f"failed: {type(err).__name__}"
            else:
                content = to_csv(rows)
                target = RAW_DIR / f"{name}_{stamp:%Y%m%d}.csv"
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(content)
                row.update({
                    "local_path": target.relative_to(ROOT).as_posix(),
                    "records": len(rows),
                    "expected_records": expected,
                    "bytes": len(content),
                    "sha256": hashlib.sha256(content).hexdigest(),
                    "status": "ok" if len(rows) == expected else "incomplete",
                })
            writer.writerow({k: row.get(k, "") for k in FIELDS})
            f.flush()
            print(name, row["status"], row.get("records", ""), row.get("expected_records", ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
