import json
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
import tempfile
import unittest

from phblock.catalog import build, canonical_host
from phblock.__main__ import main


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "data").mkdir()
        self.rows = [self.record("casino.example"), self.record("www.casino.example")]
        self.save("exclusions", [{"domain": "payments.example", "reason": "Shared payment provider"}])
        self.save("domains", self.rows)

    def record(self, domain):
        return {"domain": domain, "evidence_url": "https://regulator.example/list.pdf#page=1", "reviewed_on": "2026-11-17"}

    def save(self, name, rows):
        (self.root / "data" / f"{name}.json").write_text(json.dumps(rows), encoding="utf-8")

    def test_subscription_covers_children_without_overmatching_siblings(self):
        self.rows.append(self.record("notcasino.example"))
        self.save("domains", self.rows)
        self.assertEqual(build(self.root), [])
        rules = (self.root / "blocklists/adguard.txt").read_text().splitlines()
        self.assertIn("||casino.example^", rules)
        self.assertIn("||notcasino.example^", rules)
        self.assertNotIn("||www.casino.example^", rules)
        self.assertEqual([r for r in rules if not r.startswith("!")], ["||casino.example^", "||notcasino.example^"])
        tracker = (self.root / "docs/domains.md").read_text()
        self.assertIn("www.casino.example", tracker)
        self.assertIn("https://regulator.example/list.pdf#page=1", tracker)
        self.assertEqual((self.root / "blocklists/domains.txt").read_text(), "casino.example\nnotcasino.example\nwww.casino.example\n")

    def test_check_detects_missing_and_stale_outputs_without_writing(self):
        self.assertEqual(len(build(self.root, check=True)), 3)
        self.assertFalse((self.root / "blocklists").exists())
        build(self.root)
        self.assertEqual(build(self.root, check=True), [])
        output = self.root / "blocklists/adguard.txt"
        output.write_text("stale", encoding="utf-8")
        self.assertEqual(build(self.root, check=True), ["blocklists/adguard.txt"])
        self.assertEqual(output.read_text(), "stale")

    def test_bad_data_never_overwrites_existing_feed(self):
        build(self.root)
        original = (self.root / "blocklists/adguard.txt").read_bytes()
        invalid = [[], {}, [None], [self.record("*.casino.example")], [self.record("casino.example")] * 2]
        for rows in invalid:
            with self.subTest(rows=rows):
                self.save("domains", rows)
                with self.assertRaises(ValueError):
                    build(self.root)
                self.assertEqual((self.root / "blocklists/adguard.txt").read_bytes(), original)

    def test_review_and_evidence_are_required(self):
        for field, bad in [("reviewed_on", "tomorrow"), ("reviewed_on", "20261117"), ("reviewed_on", 42), ("evidence_url", "http://example.org"), ("evidence_url", "https:///missing-host"), ("evidence_url", "https://example.org/\n||good.example^"), ("evidence_url", "https://example.org/|x"), ("evidence_url", "https://user:password@example.org"), ("evidence_url", "https://user@example.org"), ("evidence_url", "https://:password@example.org"), ("evidence_url", 42)]:
            with self.subTest(field=field, bad=bad):
                row = self.record("casino.example")
                row[field] = bad
                self.save("domains", [row])
                with self.assertRaises(ValueError):
                    build(self.root)

    def test_exclusion_conflicts_in_both_directions(self):
        for host in ["payments.example", "api.payments.example", "example"]:
            with self.subTest(host=host):
                self.save("domains", [self.record(host)])
                with self.assertRaises(ValueError):
                    build(self.root)
        self.save("exclusions", [{"domain": "support.casino.example", "reason": "Support service"}])
        self.save("domains", self.rows)
        with self.assertRaisesRegex(ValueError, "exclusion"):
            build(self.root)

    def test_exclusions_need_a_reason_and_a_valid_host(self):
        for rows in [[{"domain": "payments.example", "reason": ""}], [{"domain": "https://payments.example", "reason": "Wrong shape"}], ["payments.example"]]:
            self.save("exclusions", rows)
            with self.assertRaises(ValueError):
                build(self.root)

    def test_host_boundary_rejects_rules_urls_ips_and_bare_namespaces(self):
        self.assertEqual(canonical_host("Casino.Example."), "casino.example")
        invalid = ["||casino.example^", "https://casino.example", "casino.example/path", "casino.example:443", "casino.example\n", "127.0.0.1", "localhost", "com.ph", "gov.ph", "-x.example", "x-.example", "x..example", "a" * 64 + ".example", ("a" * 60 + ".") * 5 + "example", 42]
        for host in invalid:
            with self.subTest(host=host), self.assertRaises(ValueError):
                canonical_host(host)

    def test_cli_build_check_and_data_errors(self):
        args = ["--root", str(self.root), "build"]
        with redirect_stdout(StringIO()) as output, redirect_stderr(StringIO()) as errors:
            self.assertEqual(main(args + ["--check"]), 1)
            self.assertIn("Generated files need rebuilding", errors.getvalue())
            self.assertEqual(main(args), 0)
            self.assertIn("blocklists built", output.getvalue())
            self.assertEqual(main(args + ["--check"]), 0)
            self.assertIn("blocklists verified", output.getvalue())
            self.save("domains", [])
            self.assertEqual(main(args), 1)
            self.assertIn("must not be empty", errors.getvalue())

    def test_maximum_dns_hostname_length_is_accepted(self):
        host = ".".join(["a" * 63, "b" * 63, "c" * 63, "d" * 61])
        self.assertEqual(len(host), 253)
        self.assertEqual(canonical_host(host), host)
        with self.assertRaises(ValueError):
            canonical_host(host + "d")

    def test_cli_requires_a_command(self):
        with redirect_stderr(StringIO()), self.assertRaises(SystemExit) as error:
            main([])
        self.assertEqual(error.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
