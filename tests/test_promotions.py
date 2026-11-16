from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import URLError

from phblock.__main__ import main
from phblock.promotions import candidate_report, load_watchlist, parse_channel, watch


PAGE = """<html><body>
<script>unrelated.example</script><a href="https://telegram.org">Download</a>
<div class="tgme_channel_info_description">Alternative links:<br>
<a href="https://mirror.example/signup?ref=PRIVATE_REFERRAL">Open</a>
<img src="https://image.example/a.png" /> support@contact.example</div>
<div data-post="example_channel/123">
<div class="tgme_widget_message_text js-message_text">old.example moves to
<b>new.example</b>. <a href="https://t.me/other">Channel</a></div>
<div class="tgme_widget_message_inline_keyboard"><a href="https://button.example/?token=PRIVATE_TOKEN">Play</a></div>
</div></body></html>"""
URL = "https://t.me/s/example_channel"


class PromotionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / "data").mkdir()
        (self.root / "sources").mkdir()
        self.sources = [{"id": "example", "url": URL, "reason": "Public PH casino promotion channel"}]
        self.save("sources/promotion-watchlist.json", self.sources)
        self.save("data/domains.json", [{"domain": "old.example", "evidence_url": "https://evidence.example/page", "reviewed_on": "2026-11-17"}])
        self.save("data/exclusions.json", [{"domain": "t.me", "reason": "Shared promotion source"}])

    def save(self, path, data):
        (self.root / path).write_text(json.dumps(data), encoding="utf-8")

    def test_public_channel_parser_keeps_destinations_and_post_provenance(self):
        self.assertEqual(set(parse_channel(PAGE, URL)), {
            ("mirror.example", URL),
            ("old.example", "https://t.me/example_channel/123"),
            ("new.example", "https://t.me/example_channel/123"),
            ("t.me", "https://t.me/example_channel/123"),
            ("button.example", "https://t.me/example_channel/123"),
        })

    def test_unavailable_preview_or_truncated_section_is_an_error(self):
        for html in ["<html>Sign in</html>", '<div class="tgme_widget_message_text">unfinished.example']:
            with self.subTest(html=html), self.assertRaises(ValueError):
                parse_channel(html, URL)

    def test_invalid_or_non_web_button_links_are_not_candidates(self):
        html = '<div class="tgme_channel_info_description"><a href="mailto:x@secret.example">Email</a><a href="javascript:alert(1)">Button</a><a href="ftp://unsupported.example">FTP</a><a href="https://name:secret@private.example">Bad</a><a href="https://name@private.example">User only</a><a href="https://:secret@private.example">Password only</a><a href="https://[broken">Bad URL</a><a href="https://127.0.0.1">IP</a></div>'
        self.assertEqual(parse_channel(html, URL), [])

    def test_visible_urls_do_not_turn_paths_or_referral_tokens_into_hosts(self):
        html = '<div class="tgme_widget_message_text">HTTPS://play.example/path.private?ref=referral.private#fragment.private www.mirror.example/private.path?token=token.private bare.example/signup?ref=private.referral#private.fragment query.example?ref=private.query</div>'
        self.assertEqual(set(parse_channel(html, URL)), {("play.example", URL), ("www.mirror.example", URL), ("bare.example", URL), ("query.example", URL)})

    def test_entities_line_breaks_and_self_closing_media_preserve_visible_hosts(self):
        html = '<div class="tgme_widget_message_text">one.example<br>two.example <img src="image.example"/> after.example entity&#46;example</div>'
        self.assertEqual(set(parse_channel(html, URL)), {(host, URL) for host in ["one.example", "two.example", "after.example", "entity.example"]})

    def test_candidate_coverage_uses_label_boundaries_and_retains_all_evidence(self):
        observations = {"api.old.example": {URL}, "notold.example": {URL}, "mirror.example": {URL, "https://t.me/example_channel/123"}, "t.me": {URL}}
        candidates, excluded = candidate_report(observations, [{"domain": "old.example"}], [{"domain": "t.me"}])
        by_host = {row["domain"]: row for row in candidates}
        self.assertEqual(by_host["api.old.example"]["covered_by"], "old.example")
        self.assertIsNone(by_host["notold.example"]["covered_by"])
        self.assertEqual(by_host["mirror.example"]["evidence_urls"], sorted(observations["mirror.example"]))
        self.assertEqual(excluded, ["t.me"])

    def test_watchlist_is_explicit_and_limited_to_public_channel_previews(self):
        self.assertEqual(load_watchlist(self.root), self.sources)
        invalid = [{}, [], [{"id": "x", "url": "https://example.org/private", "reason": "Wrong source"}], self.sources * 2, [{"id": "x", "url": URL, "reason": ""}], [{"id": "x", "url": URL}]]
        for sources in invalid:
            self.save("sources/promotion-watchlist.json", sources)
            with self.subTest(sources=sources), self.assertRaises(ValueError):
                load_watchlist(self.root)

    def test_watch_writes_sanitized_candidates_without_publishing_or_following_links(self):
        before = (self.root / "data/domains.json").read_bytes()
        with patch("phblock.promotions.fetch_public", return_value=PAGE.encode()) as fetched:
            with redirect_stdout(StringIO()) as output:
                self.assertEqual(main(["--root", str(self.root), "watch"]), 0)
        fetched.assert_called_once_with(URL)
        report_path = self.root / "reports/promotions.json"
        report = json.loads(report_path.read_text())
        self.assertEqual(report["counts"], {"sources_checked": 1, "sources_failed": 0, "candidates": 4, "already_covered": 1, "excluded": 1})
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["sources"][0]["url"], URL)
        self.assertEqual(len(report["sources"][0]["sha256"]), 64)
        self.assertIn("4 candidates", output.getvalue())
        for sensitive in ["PRIVATE_REFERRAL", "PRIVATE_TOKEN", "contact.example", "image.example"]:
            self.assertNotIn(sensitive, report_path.read_text())
        self.assertEqual((self.root / "data/domains.json").read_bytes(), before)
        self.assertFalse((self.root / "blocklists").exists())

    def test_failed_source_is_reported_with_partial_results_and_nonzero_exit(self):
        self.sources.append({"id": "unavailable", "url": "https://t.me/s/missing_channel", "reason": "Test failure"})
        self.save("sources/promotion-watchlist.json", self.sources)
        with patch("phblock.promotions.fetch_public", side_effect=[PAGE.encode(), URLError("unavailable")]):
            with redirect_stdout(StringIO()) as output:
                self.assertEqual(main(["--root", str(self.root), "watch"]), 1)
        report = json.loads((self.root / "reports/promotions.json").read_text())
        self.assertEqual(report["counts"]["sources_checked"], 2)
        self.assertEqual(report["counts"]["sources_failed"], 1)
        self.assertEqual(report["errors"][0]["source_id"], "unavailable")
        self.assertIn("1 source errors", output.getvalue())
        self.assertEqual(len(report["candidates"]), 4)


if __name__ == "__main__":
    unittest.main()
