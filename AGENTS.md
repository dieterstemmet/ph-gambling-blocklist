# PH Gambling Blocklist

This repository publishes an opt-in Philippine gambling DNS blocklist. Follow Dieter's standing rules.

- Python 3.11 or later. Building and testing use the standard library. Refreshing the PAGCOR PDF also needs `python -m pip install --require-hashes -r requirements.txt`.
- Commands: `python -m unittest discover -s tests -v`, `python -m phblock build`, `python -m phblock build --check`, `python -m phblock refresh`, `python -m phblock watch`.
- `data/domains.json` is the reviewed record of domains. `data/exclusions.json` records false positives. `sources/` records source provenance. `blocklists/` and `docs/domains.md` are generated; regenerate them after changing data.
- Discovery never grants approval or removes published domains. Review source changes and community evidence before editing the reviewed records.
- `sources/promotion-watchlist.json` contains reviewed public Telegram preview URLs only. `watch` collects hostnames and source permalinks, never full posts, referral parameters, private groups or destination-site content. Read `docs/discovery-sources.md` before extending acquisition sources.
- Keep DNS rules to explicit hosts and their children. Do not infer parent domains, guess mirror names, or block shared infrastructure, payment services, regulators or support services.
- No subscriber data, query logs, external AI, affiliate links or paid APIs.
- No hosted CI. `ops/gate` runs tests and verifies generated output locally on every push. Document refresh scheduling; do not install a scheduler on the maintainer's machine.
- Use an isolated worktree, small commits, and a pull request. Keep the action log in `docs/work-log.md`.
- After merging any filter change, publish the generated `blocklists/adguard.txt` as `assets/filter_1.txt` on the `gh-pages` artifact branch. Its root holds only built assets and `.nojekyll`. Commit/push that deployment from its own worktree and prove the live response matches main byte for byte; see `CONTRIBUTING.md`. No workflow is needed.
- When testing a local filter file with AdGuard Home on Windows, `safe_fs_patterns` must use native backslashes; a forward-slash glob does not match its normalized paths. Confirm `rules_count` before DNS assertions. Choose a DNS test port available for both TCP and UDP.
