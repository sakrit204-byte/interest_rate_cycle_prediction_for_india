"""Retrieve archived copies of official files from the Internet Archive Wayback Machine.

Used when an official site is unavailable. Every file is saved unchanged with a
provenance record (original URL, snapshot timestamp, retrieval time, SHA256).
"""

from __future__ import annotations

import csv
import hashlib
import re
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

import requests

CDX_ENDPOINT = "http://web.archive.org/cdx/search/cdx"
SNAPSHOT_TEMPLATE = "http://web.archive.org/web/{timestamp}id_/{original}"
USER_AGENT = "RateCycleIndiaNepal research pipeline (academic, non commercial)"

MANIFEST_FIELDS = [
    "category",
    "original_url",
    "canonical_url",
    "wayback_timestamp",
    "wayback_url",
    "retrieved_at_utc",
    "local_path",
    "bytes",
    "sha256",
    "content_type",
    "status",
]


@dataclass(frozen=True)
class Capture:
    timestamp: str
    original: str
    mimetype: str
    length: str

    @property
    def canonical(self) -> str:
        """URL without scheme, www prefix or query string, used to deduplicate captures."""
        parts = urlsplit(self.original)
        host = parts.netloc.lower().removeprefix("www.")
        return f"{host}{parts.path}"


def parse_cdx_lines(lines) -> list[Capture]:
    """Parse CDX output requested with fl=timestamp,original,mimetype,length."""
    captures = []
    for line in lines:
        fields = line.strip().split(" ")
        if len(fields) != 4:
            continue
        captures.append(Capture(*fields))
    return captures


def latest_per_url(captures: list[Capture]) -> list[Capture]:
    """Keep the most recent capture of each canonical URL."""
    best: dict[str, Capture] = {}
    for cap in captures:
        current = best.get(cap.canonical)
        if current is None or cap.timestamp > current.timestamp:
            best[cap.canonical] = cap
    return sorted(best.values(), key=lambda c: c.canonical)


def select(captures: list[Capture], include: str, exclude: str | None = None) -> list[Capture]:
    """Filter captures whose URL path matches include and does not match exclude (case insensitive)."""
    inc = re.compile(include, re.IGNORECASE)
    exc = re.compile(exclude, re.IGNORECASE) if exclude else None
    return [
        c
        for c in captures
        if inc.search(urlsplit(c.original).path) and not (exc and exc.search(urlsplit(c.original).path))
    ]


def query_cdx(url_prefix: str, session: requests.Session, limit: int = 50000) -> list[Capture]:
    params = {
        "url": url_prefix,
        "matchType": "prefix",
        "filter": "statuscode:200",
        "collapse": "urlkey",
        "fl": "timestamp,original,mimetype,length",
        "limit": str(limit),
    }
    resp = session.get(CDX_ENDPOINT, params=params, timeout=180)
    resp.raise_for_status()
    return parse_cdx_lines(resp.text.splitlines())


def all_captures(original: str, session: requests.Session) -> list[Capture]:
    """Every successful capture of one exact URL, newest first, distinct by content digest."""
    params = {
        "url": original,
        "filter": "statuscode:200",
        "collapse": "digest",
        "fl": "timestamp,original,mimetype,length",
    }
    resp = session.get(CDX_ENDPOINT, params=params, timeout=180)
    resp.raise_for_status()
    return sorted(parse_cdx_lines(resp.text.splitlines()), key=lambda c: c.timestamp, reverse=True)


# Leading bytes of each expected file format. Crawlers sometimes stored login or
# redirect pages under a file URL, so content is checked, not just the HTTP status.
SIGNATURES = {
    ".pdf": (b"%PDF",),
    ".xlsx": (b"PK\x03\x04",),
    ".xls": (bytes.fromhex("D0CF11E0A1B11AE1"), b"PK\x03\x04"),
}


def has_expected_signature(content: bytes, path: str) -> bool:
    suffix = Path(urlsplit(path).path).suffix.lower()
    expected = SIGNATURES.get(suffix)
    return True if expected is None else content.startswith(expected)


def local_name(cap: Capture) -> str:
    """Archive path below /uploads/ flattened into one file name, so names stay unique and traceable."""
    path = urlsplit(cap.original).path
    tail = path.split("/uploads/", 1)[-1] if "/uploads/" in path else path.lstrip("/")
    return re.sub(r"[^A-Za-z0-9._]+", "_", tail)


def download(
    captures: list[Capture],
    category: str,
    out_dir: Path,
    manifest_path: Path,
    session: requests.Session,
    pause_seconds: float = 1.0,
    retries: int = 3,
    path_root: Path | None = None,
) -> list[dict]:
    """Download captures not yet held as valid files; append one manifest row per URL.

    If the chosen capture is not the expected file format, older captures of the same
    URL are tried, newest first. A file that never validates is recorded, not saved.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    done = _completed(manifest_path)
    rows = []
    for cap in captures:
        if cap.canonical in done:
            continue
        target = out_dir / local_name(cap)
        shown = target.relative_to(path_root) if path_root else target
        row = {"category": category, "original_url": cap.original, "canonical_url": cap.canonical, "local_path": shown.as_posix()}
        candidates = [cap]
        tried_history = False
        while candidates:
            current = candidates.pop(0)
            url = SNAPSHOT_TEMPLATE.format(timestamp=current.timestamp, original=current.original)
            row.update(wayback_timestamp=current.timestamp, wayback_url=url)
            content, info = _fetch(session, url, retries, pause_seconds)
            row.update(retrieved_at_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"), **info)
            if content is not None and has_expected_signature(content, current.original):
                target.write_bytes(content)
                row.update(bytes=len(content), sha256=hashlib.sha256(content).hexdigest(), status="ok")
                break
            if content is not None:
                row.update(bytes=len(content), sha256=hashlib.sha256(content).hexdigest(), status="invalid_content")
            if not tried_history:
                tried_history = True
                try:
                    candidates = [c for c in all_captures(cap.original, session) if c.timestamp != current.timestamp]
                except requests.RequestException:
                    candidates = []
            time.sleep(pause_seconds)
        if row["status"] != "ok":
            row["local_path"] = ""
        _append(manifest_path, row)
        rows.append(row)
        time.sleep(pause_seconds)
    return rows


def revalidate(manifest_path: Path, path_root: Path | None = None) -> list[str]:
    """Flag saved files that fail the signature check, delete them, and record why.

    Returns the canonical URLs flagged, so they are downloaded again on the next run.
    """
    flagged = []
    for row in _latest_rows(manifest_path).values():
        if row["status"] != "ok":
            continue
        path = Path(row["local_path"])
        if path_root and not path.is_absolute():
            path = path_root / path
        content = path.read_bytes()[:16] if path.exists() else b""
        if not has_expected_signature(content, row["original_url"]):
            if path.exists():
                path.unlink()
            _append(manifest_path, {**row, "status": "invalid_content", "local_path": "",
                                    "retrieved_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds")})
            flagged.append(row["canonical_url"])
    return flagged


def _fetch(session, url, retries, pause_seconds):
    info = {"bytes": "", "sha256": "", "content_type": "", "status": ""}
    for attempt in range(1, retries + 1):
        try:
            resp = session.get(url, timeout=180)
            resp.raise_for_status()
            info["content_type"] = resp.headers.get("Content-Type", "")
            return resp.content, info
        except requests.RequestException as err:
            info["status"] = f"failed: {type(err).__name__}"
            time.sleep(pause_seconds * 2 * attempt)
    return None, info


def new_session() -> requests.Session:
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT
    return session


def _latest_rows(manifest_path: Path) -> dict[str, dict]:
    """Last manifest row per canonical URL; the manifest is append only."""
    if not manifest_path.exists():
        return {}
    with manifest_path.open(newline="", encoding="utf-8") as f:
        return {r["canonical_url"]: r for r in csv.DictReader(f)}


def _completed(manifest_path: Path) -> set[str]:
    return {url for url, r in _latest_rows(manifest_path).items() if r["status"] == "ok"}


def _append(manifest_path: Path, row: dict) -> None:
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    new = not manifest_path.exists()
    with manifest_path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=MANIFEST_FIELDS)
        if new:
            writer.writeheader()
        writer.writerow({k: row.get(k, "") for k in MANIFEST_FIELDS})
