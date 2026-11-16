# Where gambling platforms reach people

## Four questions

1. **What would a professional add?** Trace the public promotion to the destination hostname and preserve the evidence for that connection. Record migrations and alternative links without guessing related domains.
2. **What is the raw material?** Public channel descriptions, post text, link buttons, ad-library entries, creator captions, affiliate links and voluntarily reported hostnames. The regulator's register remains a separate source.
3. **Which methods and tools?** Curated public-source watches, hostname extraction, source permalinks, payload hashes, comparison with reviewed rules and manual purpose review. The first automated acquisition adapter reads public Telegram previews without an account.
4. **What independently demonstrates the result?** A public channel explicitly lists casino mirror domains; another announces a platform migration. A report on CICC's Facebook-promotion findings names 11 domains absent from the initial catalog. Source pages, parser fixtures and a fresh live scan establish what was observed.

## Collection sources

| Where people encounter a platform | What to collect | Collection status |
| --- | --- | --- |
| Facebook and Instagram ads, public creator pages, Reels and video captions | Public ad/post URL, advertiser or source-page reference, displayed hostname and outgoing destination | Manual. Use Meta Ad Library with Philippines selected; inspect public creator posts separately. |
| YouTube videos and search/display ads | Advertiser or website lookup in Google's Ads Transparency Center; public description or pinned promotional link | Manual. Filter by serving region and date; the library does not cover every organic creator promotion. |
| Public Telegram casino channels | Description links, messages announcing mirrors or migrations, and landing-page buttons | Automated for the two reviewed URLs in `sources/promotion-watchlist.json`. |
| Search results and casino comparison/bonus pages | Public affiliate page and the destination hostname it promotes | Manual. Treat rankings and licence claims as marketing; verify the destination's purpose separately. |
| SMS, Messenger, Viber and private groups | Voluntarily submitted hostname and a public evidence URL if available | Community reports only. Do not collect inboxes, phone numbers, contact lists or message exports. |
| CICC/PAGCOR notices and documented public reports | Explicitly identified gambling domain and the dated source | Manual review alongside the existing PAGCOR adapter. Allegations do not establish current licence status. |

Useful discovery terms include `scatter`, `online casino Philippines`, `free 100`, `libreng puhunan`, `GCash casino`, `alternative link`, `new link`, `perya` and `sabong`. These terms locate potential evidence; they never justify a DNS block by themselves.

## Observed public examples

- [The PHWIN public preview](https://t.me/s/phwintgchannel) lists alternative casino domains in its description. This provides explicit host evidence rather than inferred numbered mirrors.
- [The PHPLAY public preview](https://t.me/s/PHPLAY_Offical) includes promotion buttons and [a public migration announcement](https://t.me/PHPLAY_Offical/393). A watch can discover replacement domains from that announcement.
- [A public casino comparison page](https://www.betswin888.com/) discloses affiliate relationships and links to offer pages. This is a discovery source, not independent verification of its recommendations or licence claims.
- [Newsbytes' August 14, 2026 CICC report](https://newsbytes.ph/2026/08/14/cicc-flags-12-facebook-accounts-for-promoting-illegal-gambling-sites/) names 11 domains associated with Facebook promotions. None was in the initial PAGCOR-derived catalog. This report is a separate lead for review; its named domains are not automatically approved.

The public Telegram content can be old. A retrieval time establishes when the page was checked, not when the platform launched or whether it is still reachable. The discovery command reads the currently exposed preview, not a complete channel history.

## Access limits checked November 17, 2026

- [Meta Ad Library](https://business.facebook.com/ads/library) supports keyword/advertiser searches and branded-content discovery. The PH casino query was throttled during this research. No automated Meta collector is claimed.
- [Meta's API coverage](https://www.facebook.com/ads/library/api/) is narrower: political/issue ads worldwide and all ad types delivered in the EU/UK. It is not a complete API for Philippine commercial gambling ads.
- [Google's documentation](https://support.google.com/My-Ad-Center-Help/answer/12155361) describes advertiser/website lookup and serving-region/date filters. The center's dynamic results were not available through a static text fetch here.
- TikTok's transparency page was inaccessible through the research tool. No automated TikTok or private-message access is configured.
- PAGCOR's [marketing-service framework](https://www.pagcor.ph/regulatory/pdf/GSRM/Regulatory%20Manuals/Regulatory-Framework-for-the-Accreditation-of-Gaming-Affiliates-and-Support-Service-Providers-Rev-No-1.pdf) documents social, influencer, paid-search and display promotion. Its [text-blast memo](https://www.pagcor.ph/regulatory/pdf/announcements/responsible-use-of-text-blasts.pdf) records complaints about gaming-site SMS invitations. These establish acquisition channels, not the current status of a specific operator.

## Data handling

| Recipient | What is sent | What is never sent | What is retained |
| --- | --- | --- | --- |
| Telegram public web preview | GET for an explicitly configured public channel URL and project User-Agent | Subscriber data, DNS logs, personal messages, phone numbers, login sessions | Hostnames, public source permalinks, retrieval time and payload hash |
| GitHub Pages | Public subscription request | AdGuard credentials or query history | Reviewed filter asset only on the publication branch |

Reports omit full post bodies and outgoing URL paths, queries and fragments, including referral and download tokens. Linked destinations are not fetched. Collecting from a social platform does not put that shared platform in the DNS blocklist.
