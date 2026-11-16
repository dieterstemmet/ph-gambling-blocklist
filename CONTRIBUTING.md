# Contributing

## Review a domain

Start with a public source that identifies the hostname as a gambling platform or a dedicated gambling mirror. The official register is one source; a documented platform announcement or public report can support a community submission. A name, a similar-looking domain, DNS resolution or a TLS certificate alone does not establish gambling use.

1. Confirm the hostname and the source date. Review the linked source page, including the domain's role. Do not log in, deposit money or supply personal information to test a platform.
2. Keep the scope to the evidenced hostname. Do not shorten `play.example.org` to `example.org`, or invent numbered mirrors. A `www` entry alone does not approve its bare parent.
3. Reject shared infrastructure, payment services, unrelated games, journalism, regulators and support services. Record a confirmed false positive in `data/exclusions.json` with its reason. Remove any overlapping reviewed block entry; the build rejects conflicts in either direction.
4. Add a record to `data/domains.json`:

   ```json
   {
     "domain": "casino.example",
     "evidence_url": "https://regulator.example/register.pdf#page=2",
     "reviewed_on": "2026-11-17"
   }
   ```

5. Run `python -m phblock build` and the tests, then open a pull request explaining the evidence. Contributions and generated data are covered by the repository's MIT license; only submit material you may contribute.

Case and one trailing DNS dot are normalized. Duplicate reviewed hosts, invalid hostnames, empty catalogs, malformed evidence and missing review dates fail the build. The builder removes child rules covered by a reviewed parent but retains every hostname in the tracker and plain export.

## Refresh PAGCOR

Install the hash-locked PDF reader, then run:

```sh
python -m phblock refresh
```

`reports/pagcor.json` is an ignored local report. It contains the document date, retrieval time in UTC, SHA-256, extracted and reviewed counts, additions with source page numbers, missing hostnames and excluded hostnames. Inspect those counts before reviewing candidates. The report is a proposal; it never changes the subscription or grants a review date.

For an official PDF downloaded separately:

```sh
python -m phblock refresh --pdf /path/to/pagcor-register.pdf
```

Keep the dated provenance files in `sources/`. When accepting a new source version, add a dated metadata file from the report's `source` object and retain older provenance. The original PDF is not redistributed. Its hash identifies the source bytes used for review; the live URL may later serve a different document.

If the source fails, changes format or produces an unexpected count, investigate the source and extraction before editing reviewed records. Never remove a domain solely because the current register omits it or DNS temporarily fails. Check the evidence for a genuine change of purpose before removing it.

## Schedule discovery

The repository does not install a scheduler. A maintainer may run `python -m phblock refresh` daily with Windows Task Scheduler or cron, setting the working directory to the repository and using the Python environment with `requirements.txt` installed. Review the report and command failures. Scheduling discovery alone does not publish changes.

AdGuard's subscription refresh is separate: it downloads the latest reviewed file from `main`. The filter includes `Expires: 1 days` as a refresh hint; the resolver's settings determine its refresh schedule.

## Verify a change

```sh
python -m unittest discover -s tests -v
python -m phblock build --check
```

`ops/gate` contains these local push checks. Do not add hosted CI. For code changes, follow the quality-gate and review requirements in Dieter's standing rules.

For a filtering change, load the generated file into a dedicated AdGuard Home test instance. Query a listed host and a child host; each should be blocked. Query an unrelated control host; it should retain its expected answer. Do not use a customer's resolver or collect subscriber query logs.
