import hashlib

from src.ingestion import wayback

CDX = [
    "20200101000000 https://www.nrb.org.np/contents/uploads/2019/12/Monetary_Policy_in_English-2018-19_Full_Text.pdf application/pdf 100",
    "20240101000000 http://nrb.org.np/contents/uploads/2019/12/Monetary_Policy_in_English-2018-19_Full_Text.pdf application/pdf 100",
    "20240505000000 https://www.nrb.org.np/contents/uploads/2024/05/Monetary-Policy-2080-81-3rd-Quarter-Review.pdf?fbclid=abc application/pdf 90",
    "20240506000000 https://www.nrb.org.np/contents/uploads/2024/05/Monetary-Policy-2080-81-3rd-Quarter-Review.pdf application/pdf 90",
    "20220101000000 https://www.nrb.org.np/contents/uploads/2019/12/2069_70-Circular_02-Monetary-Policy-Bank-Rate.pdf application/pdf 50",
    "malformed line",
]


def test_parse_skips_malformed_lines():
    assert len(wayback.parse_cdx_lines(CDX)) == 5


def test_latest_per_url_dedupes_scheme_www_and_query():
    caps = wayback.latest_per_url(wayback.parse_cdx_lines(CDX))
    assert len(caps) == 3
    by_url = {c.canonical: c.timestamp for c in caps}
    assert by_url["nrb.org.np/contents/uploads/2019/12/Monetary_Policy_in_English-2018-19_Full_Text.pdf"] == "20240101000000"
    assert by_url["nrb.org.np/contents/uploads/2024/05/Monetary-Policy-2080-81-3rd-Quarter-Review.pdf"] == "20240506000000"


def test_select_include_and_exclude():
    caps = wayback.latest_per_url(wayback.parse_cdx_lines(CDX))
    docs = wayback.select(caps, r"monetary.?policy.*\.pdf$", r"circular")
    assert len(docs) == 2
    circulars = wayback.select(caps, r"circular.*monetary.?policy.*\.pdf$")
    assert len(circulars) == 1


def test_local_name_is_flat_and_traceable():
    cap = wayback.parse_cdx_lines(CDX)[0]
    assert wayback.local_name(cap) == "2019_12_Monetary_Policy_in_English_2018_19_Full_Text.pdf"


def test_download_records_manifest_and_skips_completed(tmp_path):
    class FakeResp:
        content = b"%PDF test"
        headers = {"Content-Type": "application/pdf"}

        def raise_for_status(self):
            pass

    class FakeSession:
        calls = 0

        def get(self, url, timeout, params=None):
            FakeSession.calls += 1
            return FakeResp()

    caps = wayback.latest_per_url(wayback.parse_cdx_lines(CDX))[:1]
    manifest = tmp_path / "manifest.csv"
    rows = wayback.download(caps, "test", tmp_path / "out", manifest, FakeSession(), pause_seconds=0)
    assert rows[0]["status"] == "ok"
    assert rows[0]["sha256"] == hashlib.sha256(b"%PDF test").hexdigest()
    assert (tmp_path / "out" / wayback.local_name(caps[0])).read_bytes() == b"%PDF test"
    again = wayback.download(caps, "test", tmp_path / "out", manifest, FakeSession(), pause_seconds=0)
    assert again == [] and FakeSession.calls == 1


def test_signature_check_rejects_html_saved_as_excel():
    html = b"<!DOCTYPE HTML PUBLIC"
    assert not wayback.has_expected_signature(html, "https://x.org/a/QEB-2024-OCT.xlsx")
    assert wayback.has_expected_signature(b"PK\x03\x04rest", "https://x.org/a/QEB-2024-OCT.xlsx")
    assert wayback.has_expected_signature(bytes.fromhex("D0CF11E0A1B11AE1"), "https://x.org/a/t.xls")
    assert wayback.has_expected_signature(b"%PDF-1.7", "https://x.org/a/policy.pdf?ref=x")


class _Resp:
    def __init__(self, content=b"", text=""):
        self.content = content
        self.text = text
        self.headers = {"Content-Type": "application/octet-stream"}

    def raise_for_status(self):
        pass


def test_download_falls_back_to_older_valid_capture(tmp_path):
    original = "https://www.nrb.org.np/contents/uploads/2025/03/QEB-2024-OCT.xlsx"
    newest = wayback.Capture("20250301000000", original, "application/vnd", "300")

    class Session:
        def get(self, url, timeout, params=None):
            if url == wayback.CDX_ENDPOINT:
                return _Resp(text=f"20250301000000 {original} x 300\n20250101000000 {original} x 900\n")
            if "20250301000000" in url:
                return _Resp(content=b"<!DOCTYPE HTML redirect")
            return _Resp(content=b"PK\x03\x04 real workbook")

    manifest = tmp_path / "m.csv"
    rows = wayback.download([newest], "macro_tables", tmp_path / "out", manifest, Session(), pause_seconds=0)
    assert rows[0]["status"] == "ok"
    assert rows[0]["wayback_timestamp"] == "20250101000000"
    assert (tmp_path / "out" / wayback.local_name(newest)).read_bytes().startswith(b"PK")


def test_download_records_failure_when_no_capture_is_valid(tmp_path):
    original = "https://www.nrb.org.np/contents/uploads/2025/03/QEB-2024-OCT.xlsx"
    cap = wayback.Capture("20250301000000", original, "x", "300")

    class Session:
        def get(self, url, timeout, params=None):
            if url == wayback.CDX_ENDPOINT:
                return _Resp(text=f"20250301000000 {original} x 300\n")
            return _Resp(content=b"<!DOCTYPE HTML redirect")

    rows = wayback.download([cap], "macro_tables", tmp_path / "out", tmp_path / "m.csv", Session(), pause_seconds=0)
    assert rows[0]["status"] == "invalid_content"
    assert rows[0]["local_path"] == ""
    assert not any((tmp_path / "out").iterdir())


def test_revalidate_flags_bad_file_and_allows_retry(tmp_path):
    bad = tmp_path / "QEB.xlsx"
    bad.write_bytes(b"<!DOCTYPE HTML")
    manifest = tmp_path / "m.csv"
    wayback._append(manifest, {"category": "c", "original_url": "https://nrb.org.np/u/QEB.xlsx",
                               "canonical_url": "nrb.org.np/u/QEB.xlsx", "local_path": bad.as_posix(), "status": "ok"})
    assert wayback.revalidate(manifest) == ["nrb.org.np/u/QEB.xlsx"]
    assert not bad.exists()
    assert "nrb.org.np/u/QEB.xlsx" not in wayback._completed(manifest)
