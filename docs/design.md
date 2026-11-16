# Design

## Four questions

1. **What would a professional do beyond the request?** Keep the evidence for every blocked host, review shared-service risks, and distinguish the date of a source from the date we retrieved it.
2. **What is the raw material?** PAGCOR's register of gaming brands and domains, and community reports with public evidence. A domain name containing “bet” is not evidence.
3. **Which methods and tools?** Python, a pinned PDF reader for discovery, deterministic AdGuard DNS rules, source hashes, reviewable change reports and local tests. No classifier or paid model is needed to read an official register.
4. **What independently shows it is right?** Domain-by-domain comparison against the register, reproducible builds, rejected unsafe inputs and a smoke test with AdGuard Home.

## First release

- An AdGuard Home / Private AdGuard DNS subscription using `||host^` rules.
- A plain domain export and a readable domain tracker with evidence and review dates.
- A refresh command that compares the current PAGCOR register with reviewed records. Additions and missing entries are proposals, never automatic approvals or deletions.
- GitHub issue forms for missed gambling domains and false positives.

There is no application server, dashboard, browser extension, subscriber account, telemetry or AI service. Existing general gambling lists can complement this Philippine list; they are not copied without provenance and license review.

## Data and publication

The reviewed domain records identify a host, its evidence source, the source page and a review date. PAGCOR provenance includes the source URL, document date, retrieval date and SHA-256. A separate exclusion record prevents known false positives from reappearing. The build validates all input before writing files, deduplicates child rules already covered by a listed parent, and checks generated files for drift.

The first import uses the document actually downloaded from PAGCOR, whose heading reads October 29, 2026. Search-engine excerpts still describe an older January 29 document at the same URL. The downloaded heading and bytes take precedence over those excerpts.

Refresh fetches only the configured official register. It does not visit gambling platforms, scan users' browsing history, follow casino redirects or enumerate guessed mirrors. Source failures return an error and leave published files unchanged. The refresh report retains the document date, source digest and additions/missing entries so a maintainer can review the result.

## Privacy

| Recipient | What is sent | What is never sent | What is stored here |
| --- | --- | --- | --- |
| PAGCOR | Request for its public domain register | Subscriber identity, DNS queries, browsing history, credentials | Public source metadata and reviewed hostnames |
| GitHub | Repository files and public community submissions | AdGuard credentials, DNS query logs, personal browsing data | Source code, domain evidence, generated lists, public reports |

DNS blocking applies to listed hosts and their subdomains. It cannot filter a gambling ad served from the same domain as unrelated content, discover every new platform, or stop a device using a different resolver. Presence here describes gambling-related evidence; it is not a statement that an operator is illegal or currently licensed.
