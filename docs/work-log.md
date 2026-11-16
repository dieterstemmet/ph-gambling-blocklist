# Work log

## 2026-11-17

- Checked the workspace and GitHub account; created the public `dieterstemmet/ph-gambling-blocklist` repository and an isolated implementation worktree.
- Confirmed the first target with Dieter: AdGuard Home or AdGuard DNS.
- Read AdGuard's DNS filtering documentation and PAGCOR's domain register to choose a compatible output format and an evidence source.
- Downloaded the current PAGCOR PDF. Its heading says October 29, 2026; search excerpts at the same URL still refer to January. The tracker will record the downloaded document's date.
- Scoped the release to a subscription, evidence records, reviewable discovery and contribution forms. Excluded a hosted app and external AI because neither is needed to maintain a public domain list.
- Wrote failing tests for subscription scope, malformed records, source comparisons and publication safety, then implemented the Python builder and discovery command.
- Imported 432 explicit hostnames from the 15-page register, retaining each hostname's source page. Generated 395 AdGuard rules after removing child rules covered by reviewed parents.
- Installed the hash-locked PDF reader in a task-specific scratch environment. A live refresh reproduced all 432 hostnames with no additions or missing records and left the published files unchanged.
- Added AdGuard Home / Private AdGuard DNS setup instructions, a maintenance guide, issue forms and local push checks. Refresh scheduling is documented, not installed.
- Ran the built-in code review. Its first run could not read the diff because the CLI blocked shell commands; supplied the code/config/docs diff through stdin, and the review found no actionable correctness defects. Execution verification remained local to this session.
- Calibrated mutation testing with a known surviving hostname-length boundary and three known killed mutations. The full run then exposed five test gaps. Added maximum-length, command-required and credential-only URL cases; removed an unnecessary recursive-directory option.
- The required cold dependency review by Claude found punctuation/wrapping extraction cases, raw PDF-library errors and a missing suffix-boundary regression. Reproduced each before fixing it. Refresh now reports ambiguous/invalid tokens with source pages, preserves end-of-sentence hosts and returns an actionable error for non-PDF responses. Exclusion tests cover suffix-sharing sibling names.
- Verified 22 offline tests and parsed the original PDF again: 432 hosts, zero additions, zero missing entries and zero extraction issues. An independent `pdftotext` extraction also matched all 432 hosts. The hash-locked dependency install passed a clean-install dry run.
- Loaded the subscription into AdGuard Home v0.107.80. All 432 reviewed hosts and 432 child hosts returned blocked answers for both A and AAAA (1,728 checks); three controls retained their synthetic upstream answers. No external DNS queries were sent, and the isolated test process was stopped.
- Review runs so far: two built-in Codex runs (including one blocked attempt), one Claude cold review. The shipped updater makes no model calls.
