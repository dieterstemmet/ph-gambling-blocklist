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

`reports/pagcor.json` is an ignored local report. It contains the document date, retrieval time in UTC, SHA-256, extracted and reviewed counts, additions with source page numbers, missing hostnames, excluded hostnames and extraction issues with page numbers. Inspect those counts and issues before reviewing candidates. Ambiguous line-wrapped tokens are flagged for inspection, not guessed or proposed as domains. The report never changes the subscription or grants a review date.

For an official PDF downloaded separately:

```sh
python -m phblock refresh --pdf /path/to/pagcor-register.pdf
```

Keep the dated provenance files in `sources/`. When accepting a new source version, add a dated metadata file from the report's `source` object and retain older provenance. The original PDF is not redistributed. Its hash identifies the source bytes used for review; the live URL may later serve a different document.

If the source fails, changes format or produces an unexpected count, investigate the source and extraction before editing reviewed records. Never remove a domain solely because the current register omits it or DNS temporarily fails. Check the evidence for a genuine change of purpose before removing it.

## Schedule discovery

Public promotion discovery uses only the Python standard library:

```sh
python -m phblock watch
```

Review `reports/promotions.json`. Each candidate records its source permalink and the reviewed rule covering it, if any. Counts distinguish candidates, already-covered hosts, exclusions and failed sources. A source failure yields a partial report and a nonzero exit code. A new observation does not prove a new launch or current availability.

Add a public channel to `sources/promotion-watchlist.json` only after inspecting its gambling-related purpose and Philippine connection. Channel names and claims of being official or licensed are not independently verified. The adapter reads only visible descriptions, message text and link buttons in the public preview. It does not fetch linked destinations, join groups, follow referral links or download apps. Chat and file-host links remain unapproved unless their dedicated gambling use is established.

For SMS, private messages or inaccessible ads, submit only the hostname and a public evidence link when available. Do not submit a message export, phone number, account identifiers or referral query parameters. The issue form can record where the promotion appeared.

The repository does not install a scheduler. A maintainer may run `python -m phblock refresh` and `python -m phblock watch` daily with Windows Task Scheduler or cron, setting the working directory to the repository. The PDF refresh needs the environment with `requirements.txt` installed. Review reports and command failures. Scheduling discovery alone does not publish changes.

AdGuard's subscription refresh is separate: it downloads the reviewed file deployed to GitHub Pages. The filter includes `Expires: 1 days` as a refresh hint; the resolver's settings determine its refresh schedule.

## Publish GitHub Pages

After a filter change is reviewed, tested and merged, update the `gh-pages` deployment branch from an isolated worktree. Keep that worktree separate from the source checkout. The deployment branch contains only `assets/filter_1.txt` and `.nojekyll`.

1. Run `python -m phblock build --check` from the clean, updated `main` source checkout.
2. Open the `gh-pages` worktree. Copy the verified `blocklists/adguard.txt` from `main` into `assets/filter_1.txt`, preserving its bytes. Do not copy the source checkout, data files or documentation.
3. Commit the changed asset with its source commit and verification in the body, then push `gh-pages`. Follow the standing branch/head verification rules. This is an artifact deployment; source changes still go through a pull request to `main`.
4. Confirm the Pages deployment succeeds and fetch `https://dieterstemmet.github.io/ph-gambling-blocklist/assets/filter_1.txt`. Require HTTP 200, `text/plain`, and an exact byte comparison with `main`'s reviewed file before reporting publication complete.

GitHub Pages is configured to deploy the root of `gh-pages`, with HTTPS enforced and Jekyll disabled. The raw GitHub file remains a source download; the documented subscription is the Pages URL. No repository CI workflow is installed.

## Verify a change

```sh
python -m unittest discover -s tests -v
python -m phblock build --check
```

`ops/gate` contains these local push checks. Do not add hosted CI. For code changes, follow the quality-gate and review requirements in Dieter's standing rules.

For a filtering change, load the generated file into a dedicated AdGuard Home test instance. Query a listed host and a child host; each should be blocked. Query an unrelated control host; it should retain its expected answer. Do not use a customer's resolver or collect subscriber query logs.
