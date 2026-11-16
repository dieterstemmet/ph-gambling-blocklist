from contextlib import redirect_stdout
from hashlib import sha256
from io import StringIO
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
from urllib.error import HTTPError

from phblock.discovery import SOURCE_URL, compare, extract_hosts, fetch_register, parse_document_date, read_register, refresh
from phblock.__main__ import main


HEADING = "List of PAGCOR-Accredited Gaming System Administrators and Registered Brands and Domain Names/URLs as of October 29, 2026:"


class DiscoveryTests(unittest.TestCase):
    def test_extraction_handles_urls_case_subdomains_and_email_boundaries(self):
        text = "Main domain: Casino.Example https://play.casino.example/start www.casino.example\ncontact@regulator.example host.example.evil 127.0.0.1"
        self.assertEqual(extract_hosts(text), {"casino.example", "play.casino.example", "www.casino.example", "host.example.evil"})

    def test_document_date_comes_from_the_register_heading(self):
        self.assertEqual(parse_document_date(HEADING), "2026-10-29")
        for invalid in ["Error page October 29, 2026", "as of February 30, 2026", "as of tomorrow"]:
            with self.assertRaises(ValueError):
                parse_document_date(invalid)

    def test_discovery_proposes_changes_without_approving_or_deleting(self):
        current = [{"domain": "casino.example"}, {"domain": "old.example"}]
        discovered = {"casino.example": [1, 3], "new.example": [2], "regulator.example": [4], "api.regulator.example": [4]}
        report = compare(discovered, current, [{"domain": "regulator.example"}])
        self.assertEqual(report, {"additions": [{"domain": "new.example", "pages": [2]}], "missing": ["old.example"], "retained": 1, "excluded": ["api.regulator.example", "regulator.example"]})
        self.assertEqual(current, [{"domain": "casino.example"}, {"domain": "old.example"}])

    def test_missing_reports_only_hosts_from_this_source(self):
        rows = [{"domain": "community.example", "evidence_url": "https://news.example/report"}]
        self.assertEqual(compare({}, rows, [], source_url="https://regulator.example/list.pdf")["missing"], [])

    def test_pdf_reader_records_evidence_pages_and_source_digest(self):
        pages = [SimpleNamespace(extract_text=lambda: HEADING + " casino.example"), SimpleNamespace(extract_text=lambda: "casino.example new.example")]
        reader = Mock(return_value=SimpleNamespace(pages=pages))
        with patch.dict(sys.modules, {"pypdf": SimpleNamespace(PdfReader=reader)}):
            source, domains = read_register(b"public source PDF")
        self.assertEqual(domains, {"casino.example": [1, 2], "new.example": [2]})
        self.assertEqual(source, {"url": SOURCE_URL, "published_on": "2026-10-29", "sha256": sha256(b"public source PDF").hexdigest(), "pages": 2, "extracted_hosts": 2})
        self.assertEqual(reader.call_args.args[0].getvalue(), b"public source PDF")

    def test_wrong_empty_and_unreadable_documents_fail(self):
        for texts in [[], ["Unrelated PDF"], [HEADING], [None]]:
            pages = [SimpleNamespace(extract_text=Mock(return_value=text)) for text in texts]
            with self.subTest(texts=texts), patch.dict(sys.modules, {"pypdf": SimpleNamespace(PdfReader=Mock(return_value=SimpleNamespace(pages=pages)))}):
                with self.assertRaises(ValueError):
                    read_register(b"document")

    def test_network_request_identifies_project_and_fetches_official_source(self):
        response = Mock()
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=False)
        response.read.return_value = b"PDF bytes"
        with patch("phblock.discovery.urlopen", return_value=response) as opened:
            self.assertEqual(fetch_register(), b"PDF bytes")
        request = opened.call_args.args[0]
        self.assertEqual(request.full_url, SOURCE_URL)
        self.assertIn("ph-gambling-blocklist", request.get_header("User-agent"))
        self.assertEqual(opened.call_args.kwargs["timeout"], 60)

    def test_refresh_report_leaves_published_data_unchanged_on_success_and_failure(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "data").mkdir()
            catalog = [{"domain": "casino.example", "evidence_url": SOURCE_URL + "#page=1", "reviewed_on": "2026-11-17"}]
            (root / "data/domains.json").write_text(json.dumps(catalog), encoding="utf-8")
            (root / "data/exclusions.json").write_text("[]", encoding="utf-8")
            pdf = root / "input.pdf"
            pdf.write_bytes(b"PDF content")
            with patch("phblock.discovery.read_register", return_value=({"published_on": "2026-10-29"}, {"new.example": [2]})) as reader:
                with redirect_stdout(StringIO()) as output:
                    self.assertEqual(main(["--root", str(root), "refresh", "--pdf", str(pdf)]), 0)
                reader.assert_called_once_with(b"PDF content")
                self.assertIn("1 additions, 1 missing", output.getvalue())
                report = json.loads((root / "reports/pagcor.json").read_text())
                self.assertEqual(report["counts"], {"reviewed": 1, "extracted": 1})
                self.assertEqual(report["additions"], [{"domain": "new.example", "pages": [2]}])
                self.assertEqual(report["missing"], ["casino.example"])
            original = (root / "reports/pagcor.json").read_bytes()
            with patch("phblock.discovery.fetch_register", side_effect=HTTPError(SOURCE_URL, 503, "Unavailable", {}, None)):
                with self.assertRaises(HTTPError):
                    refresh(root)
            self.assertEqual((root / "reports/pagcor.json").read_bytes(), original)
            self.assertEqual(json.loads((root / "data/domains.json").read_text()), catalog)
            self.assertFalse((root / "blocklists").exists())


if __name__ == "__main__":
    unittest.main()
