# PH Gambling Blocklist

Block Philippine gambling platforms with AdGuard Home or Private AdGuard DNS. Every hostname has a public evidence link and a review date.

The list combines PAGCOR's domain register with reviewed destinations found in public gambling promotions. See the [domain tracker](docs/domains.md) for current counts, evidence and review dates. Licensed and unlicensed gambling platforms are in scope; coverage is not the entire Philippine gambling market.

## Subscribe

Copy this URL:

```text
https://dieterstemmet.github.io/ph-gambling-blocklist/assets/filter_1.txt
```

**AdGuard Home:** Filters → DNS blocklists → Add blocklist → Add a custom list. Name it `PH Gambling Blocklist`, paste the URL and save.

**Private AdGuard DNS:** Dashboard → Servers → select your server → Blocklists → Custom → Add custom blocklist. Paste the URL and save. Your plan's custom-rule limit applies. The public AdGuard DNS resolver does not accept personal subscriptions.

Enable the list, refresh it, and check `bingoplus.ph` in AdGuard's filtering check or query log. It should match `||bingoplus.ph^`. Devices must use your AdGuard resolver for DNS blocking to apply.

| File | Purpose |
| --- | --- |
| [AdGuard subscription](blocklists/adguard.txt) | Rules for each reviewed host and its subdomains |
| [Plain domains](blocklists/domains.txt) | All reviewed hostnames; exact-host export, not a hosts file |
| [Domain tracker](docs/domains.md) | Evidence links and review dates |
| [Source provenance](sources/pagcor-2026-10-29.json) | Document date, retrieval time and SHA-256 |

## Updates

`refresh` reads the current PAGCOR register. `watch` reads a curated set of public gambling-promotion channels, extracting destinations from channel descriptions, messages and link buttons. Reports retain source evidence and identify hosts already covered by the reviewed rules. A maintainer reviews candidates before publishing changes. Missing entries remain blocked until a removal is reviewed.

Subscribers receive reviewed changes from GitHub Pages when AdGuard refreshes the subscription. Discovery and Pages publication are maintainer-run. The `Last reviewed` line describes evidence review, not a promise of daily coverage. [Where platforms reach people](docs/discovery-sources.md) lists the wider collection sources and access limits.

Report a [missed gambling domain](https://github.com/dieterstemmet/ph-gambling-blocklist/issues/new?template=gambling-domain.yml) or a [false positive](https://github.com/dieterstemmet/ph-gambling-blocklist/issues/new?template=false-positive.yml). Include public evidence. Never submit DNS query logs, browsing histories, credentials or referral tokens.

## Maintain the list

Python 3.11 or later. Building and testing need no third-party packages:

```sh
python -m unittest discover -s tests -v
python -m phblock build
python -m phblock build --check
```

To discover changes from the current PAGCOR PDF:

```sh
python -m pip install --require-hashes -r requirements.txt
python -m phblock refresh
```

To discover domains from curated public promotions, using only the Python standard library:

```sh
python -m phblock watch
```

Review `reports/pagcor.json` and `reports/promotions.json`, update the reviewed records, rebuild, run the checks and open a pull request. Neither discovery command publishes candidates. See [contributing](CONTRIBUTING.md) for review, Pages publication and scheduling instructions.

## Coverage

- No domain guessing, keyword blocking, casino crawling, subscriber telemetry or external AI calls.
- Rules cover only listed hosts and their children. A listed `www` or application subdomain does not imply its parent should be blocked.
- DNS cannot remove a gambling advert delivered from an otherwise useful site's own domain. Apps using unlisted hosts or a different DNS resolver may bypass this list.
- Inclusion describes gambling-related evidence. It does not assert that a platform is illegal, currently licensed or reachable.

For wider coverage, this list can accompany [HaGeZi's gambling list](https://github.com/hagezi/dns-blocklists#gambling). PH Gambling Blocklist does not redistribute HaGeZi's data.

[MIT license](LICENSE). [Design and privacy](docs/design.md). [Work log](docs/work-log.md).

Format and setup references: [AdGuard DNS syntax](https://adguard-dns.io/kb/general/dns-filtering-syntax/), [AdGuard DNS custom blocklists](https://adguard-dns.io/kb/private-dns/setting-up-filtering/blocklists/), [PAGCOR register](https://www.pagcor.ph/regulatory/pdf/App%20Kits/List-of-PAGCOR-Accredited-Gaming-System-Administrators-and-Registered-Brands-and-Domain-Names-URLs.pdf).
