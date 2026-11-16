"""Discover destination hosts in a curated set of public promotion channels."""

from datetime import datetime, timezone
from hashlib import sha256
from html.parser import HTMLParser
import json
import re
from urllib.parse import urlsplit

from .catalog import HOST, canonical_host, load_catalog, overlaps, rule_hosts, write_text
from .discovery import extract_hosts, fetch_public


SECTIONS = {"tgme_channel_info_description", "tgme_widget_message_text", "tgme_widget_message_inline_keyboard"}
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
VISIBLE_URL = re.compile(r"(?<![A-Za-z0-9@_.-])(?:https?://[^\s<>]+|" + HOST.pattern + r"(?::[0-9]+)?[/?#][^\s<>]*)", re.IGNORECASE)


class PublicChannel(HTMLParser):
    def __init__(self, url):
        super().__init__(convert_charrefs=True)
        self.url = url
        self.post_url = url
        self.section = None
        self.sections = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        post = attrs.get("data-post", "")
        if re.fullmatch(r"[A-Za-z0-9_]+/[0-9]+", post):
            self.post_url = "https://t.me/" + post
        classes = set(attrs.get("class", "").split())
        if self.section is None:
            if classes & SECTIONS:
                evidence = self.url if "tgme_channel_info_description" in classes else self.post_url
                self.section = {"text": [], "links": [], "evidence_url": evidence}
                self.depth = 1
        elif tag not in VOID_TAGS:
            self.depth += 1
        if self.section is not None:
            self.collect_link(tag, attrs)

    def collect_link(self, tag, attrs):
        if tag == "a":
            self.section["links"].append(attrs.get("href", ""))
        if tag == "br":
            self.section["text"].append("\n")

    def handle_endtag(self, tag):
        if self.section is None or tag in VOID_TAGS:
            return
        self.depth -= 1
        if self.depth == 0:
            self.sections.append(self.section)
            self.section = None

    def handle_data(self, data):
        if self.section is not None:
            self.section["text"].append(data)


def link_host(link):
    try:
        parsed = urlsplit(link)
        if parsed.scheme not in {"http", "https"} or parsed.username or parsed.password:
            return None
        return canonical_host(parsed.hostname)
    except ValueError:
        return None


def parse_channel(html, url):
    parser = PublicChannel(url)
    parser.feed(html)
    parser.close()
    if parser.section is not None or not parser.sections:
        raise ValueError("No complete public channel preview; inspect the source page")
    observations = []
    for section in parser.sections:
        hosts = visible_hosts("".join(section["text"]))
        hosts.update(host for host in map(link_host, section["links"]) if host is not None)
        observations.extend((host, section["evidence_url"]) for host in sorted(hosts))
    return observations


def visible_hosts(text):
    def replace_url(match):
        url = match.group()
        host = link_host(url if url.lower().startswith(("http://", "https://")) else "https://" + url)
        return " " + host + " " if host is not None else " "

    cleaned = VISIBLE_URL.sub(replace_url, text)
    return extract_hosts(cleaned)


def validate_source(source):
    if not isinstance(source, dict) or set(source) != {"id", "url", "reason"}:
        raise ValueError("invalid promotion watchlist fields")
    if not all(isinstance(value, str) and value.strip() for value in source.values()):
        raise ValueError("watchlist values must be nonempty strings")
    if not re.fullmatch(r"https://t\.me/s/[A-Za-z0-9_]+", source["url"]):
        raise ValueError("watchlist URLs must be public Telegram channel previews")


def load_watchlist(root):
    sources = json.loads((root / "sources/promotion-watchlist.json").read_text(encoding="utf-8"))
    if not isinstance(sources, list) or not sources:
        raise ValueError("promotion watchlist must be a nonempty array")
    seen = set()
    for source in sources:
        validate_source(source)
        if source["id"] in seen:
            raise ValueError("duplicate promotion source id")
        seen.add(source["id"])
    return sources


def candidate_report(observations, records, exclusions):
    rules = set(rule_hosts(records))
    candidates = []
    excluded = []
    for host, evidence in sorted(observations.items()):
        if any(overlaps(host, entry["domain"]) for entry in exclusions):
            excluded.append(host)
            continue
        labels = host.split(".")
        parents = (".".join(labels[index:]) for index in range(len(labels)))
        covered = next((parent for parent in parents if parent in rules), None)
        candidates.append({"domain": host, "evidence_urls": sorted(evidence), "covered_by": covered})
    return candidates, excluded


def watch(root):
    records, exclusions = load_catalog(root)
    sources = load_watchlist(root)
    observations = {}
    checked = []
    errors = []
    for source in sources:
        try:
            payload = fetch_public(source["url"])
            entries = parse_channel(payload.decode("utf-8"), source["url"])
        except (OSError, ValueError) as error:
            errors.append({"source_id": source["id"], "error": str(error)})
            continue
        checked.append({"id": source["id"], "url": source["url"], "sha256": sha256(payload).hexdigest()})
        for host, evidence in entries:
            observations.setdefault(host, set()).add(evidence)
    candidates, excluded = candidate_report(observations, records, exclusions)
    counts = {"sources_checked": len(sources), "sources_failed": len(errors), "candidates": len(candidates), "already_covered": sum(row["covered_by"] is not None for row in candidates), "excluded": len(excluded)}
    report = {"checked_at": datetime.now(timezone.utc).isoformat(), "counts": counts, "sources": checked, "candidates": candidates, "excluded": excluded, "errors": errors}
    write_text(root / "reports/promotions.json", json.dumps(report, indent=2) + "\n")
    return report
