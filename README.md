# PH Gambling Blocklist

Block Philippine gambling platforms with AdGuard Home or Private AdGuard DNS. Every hostname has a public evidence link and a review date.

The first release contains **432 hostnames and 395 DNS rules**, sourced from PAGCOR's register dated **October 29, 2026** and reviewed **November 17, 2026**. Licensed and unlicensed gambling platforms are in scope; the initial list covers the official register, not the entire Philippine gambling market.

## Subscribe

Copy this URL:

```text
https://raw.githubusercontent.com/dieterstemmet/ph-gambling-blocklist/main/blocklists/adguard.txt
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

The refresh command reads the current PAGCOR register and reports **new hostnames, missing entries and exclusions**. A maintainer reviews the evidence before publishing changes. Missing entries remain blocked until a removal is reviewed. A failed download cannot erase the published list.

Subscribers receive reviewed changes when AdGuard refreshes the subscription. Source refreshes are maintainer-run; no unattended scheduler is installed or running for this repository. The `Last reviewed` line in the subscription describes evidence review, not a promise of daily coverage.

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

Review `reports/pagcor.json`, update the reviewed records, rebuild, run the checks and open a pull request. Refresh does not edit the reviewed records or subscription. See [contributing](CONTRIBUTING.md) for review and scheduling instructions.

## Coverage

- No domain guessing, keyword blocking, casino crawling, subscriber telemetry or external AI calls.
- Rules cover only listed hosts and their children. A listed `www` or application subdomain does not imply its parent should be blocked.
- DNS cannot remove a gambling advert delivered from an otherwise useful site's own domain. Apps using unlisted hosts or a different DNS resolver may bypass this list.
- Inclusion describes gambling-related evidence. It does not assert that a platform is illegal, currently licensed or reachable.

For wider coverage, this list can accompany [HaGeZi's gambling list](https://github.com/hagezi/dns-blocklists#gambling). PH Gambling Blocklist does not redistribute HaGeZi's data.

[MIT license](LICENSE). [Design and privacy](docs/design.md). [Work log](docs/work-log.md).

Format and setup references: [AdGuard DNS syntax](https://adguard-dns.io/kb/general/dns-filtering-syntax/), [AdGuard DNS custom blocklists](https://adguard-dns.io/kb/private-dns/setting-up-filtering/blocklists/), [PAGCOR register](https://www.pagcor.ph/regulatory/pdf/App%20Kits/List-of-PAGCOR-Accredited-Gaming-System-Administrators-and-Registered-Brands-and-Domain-Names-URLs.pdf).
