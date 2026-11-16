# First-release verification

Verified November 17, 2026, on Python 3.11 and AdGuard Home v0.107.80.

| Check | Result |
| --- | --- |
| Reviewed catalog | 432 hostnames, 395 AdGuard rules |
| PAGCOR source | October 29, 2026 register, 15 pages; SHA-256 recorded in `sources/pagcor-2026-10-29.json` |
| Independent extraction | `pypdf` and `pdftotext -raw` produced the same 432 hostnames |
| Live source refresh | 0 additions and 0 missing entries; subsequent parser regression check found 0 extraction issues |
| Offline tests | 22 passed |
| Generated files | `python -m phblock build --check` passed |
| Dependency | Hash-locked install and clean-install dry run passed |
| Dryer | No duplicate candidates at similarity 0.8 or above |
| Crapper | Worst CRAP 9.0; all production functions had 100% line coverage |
| Mutator | 61 of 61 selected mutation sites killed; 0 survivors and 0 uncovered sites |
| Built-in review | Supplied diff reviewed after the first invocation could not execute shell commands; no actionable correctness defects found |
| Cold review | Four findings reproduced and resolved; details below |

## AdGuard Home smoke test

An isolated instance loaded the generated file as a DNS blocklist and reported 395 rules. A local synthetic upstream answered control queries with documentation IP addresses. No gambling platform was contacted.

- Each of the 432 reviewed hostnames returned a blocked answer for A and AAAA queries.
- A test subdomain beneath each hostname also returned a blocked answer for A and AAAA queries.
- Total: 1,728 blocked-answer assertions passed.
- `example.org`, `pagcor.ph` and `notbingoplus.ph` retained the local upstream's answers for both record types.
- Query logs were disabled. The test process was stopped afterward.

This proves that AdGuard Home consumes the generated syntax and applies it at DNS-label boundaries. It does not establish the availability or purpose of every subdomain, complete Philippine market coverage, or the user's resolver configuration. Private AdGuard DNS was not tested against a paid account; the subscription uses its documented DNS-rule format.

## Cold review resolutions

1. A bare namespace in extracted text could abort discovery. Invalid tokens are now retained as extraction issues; valid candidates on the same page remain discoverable.
2. Sentence-ending punctuation dropped hosts, and a hyphenated line wrap proposed a fragment as a host. Sentence-ending hosts are preserved; ambiguous wrapped tokens are flagged with their source page and never proposed as domains.
3. A non-PDF response escaped the CLI's error handling. The PDF adapter now translates the library exception to an actionable error. Tested with the real reader and an HTML input; no report or blocklist was overwritten.
4. The tests did not distinguish excluded domains from sibling names sharing a suffix. Added builder and discovery regressions for `notpayments.example` and `notregulator.example`.

Mutation testing was calibrated before trusting its score: one known untested length-boundary mutation survived, while three known damaging mutations failed. The missing boundary check was then added. Mutation scores describe the operators the tool selects; they are not proof against every possible defect.
