"""Validate reviewed records and produce deterministic subscription files."""

from datetime import date
import json
from pathlib import Path
import re
import tempfile
from urllib.parse import urlsplit


HOMEPAGE = "https://github.com/dieterstemmet/ph-gambling-blocklist"
HOST = re.compile(r"(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}")
PH_NAMESPACES = {"com.ph", "net.ph", "org.ph", "gov.ph", "edu.ph", "mil.ph", "ngo.ph", "i.ph"}


def canonical_host(value):
    if not isinstance(value, str):
        raise ValueError("domain must be a hostname string")
    host = value.lower().removesuffix(".")
    if len(host) > 253 or not HOST.fullmatch(host) or host in PH_NAMESPACES:
        raise ValueError(f"invalid domain: {value!r}")
    return host


def read_rows(path, fields):
    rows = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(rows, list):
        raise ValueError(f"{path.name} must contain an array")
    for row in rows:
        if not isinstance(row, dict) or set(row) != fields:
            raise ValueError(f"invalid fields in {path.name}; expected {sorted(fields)}")
        row["domain"] = canonical_host(row["domain"])
    return rows


def validate_evidence(row):
    url = row["evidence_url"]
    if not isinstance(url, str) or not re.fullmatch(r"https://[^\s<>|]+", url):
        raise ValueError("evidence_url must be a public HTTPS URL")
    parsed = urlsplit(url)
    if not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("evidence_url must have a host and no credentials")
    if not isinstance(row["reviewed_on"], str):
        raise ValueError("reviewed_on must be an ISO date")
    reviewed = date.fromisoformat(row["reviewed_on"])
    if reviewed.isoformat() != row["reviewed_on"]:
        raise ValueError("reviewed_on must use YYYY-MM-DD")


def overlaps(left, right):
    return left == right or left.endswith("." + right) or right.endswith("." + left)


def load_catalog(root):
    records = read_rows(root / "data/domains.json", {"domain", "evidence_url", "reviewed_on"})
    exclusions = read_rows(root / "data/exclusions.json", {"domain", "reason"})
    if not records:
        raise ValueError("reviewed domains must not be empty")
    for entry in exclusions:
        if not isinstance(entry["reason"], str) or not entry["reason"].strip():
            raise ValueError("an exclusion needs a reason")
    seen = set()
    for row in records:
        validate_evidence(row)
        host = row["domain"]
        if host in seen:
            raise ValueError(f"duplicate reviewed domain: {host}")
        for entry in exclusions:
            if overlaps(host, entry["domain"]):
                raise ValueError(f"{host} conflicts with exclusion {entry['domain']}")
        seen.add(host)
    return sorted(records, key=lambda row: row["domain"]), exclusions


def rule_hosts(records):
    hosts = {row["domain"] for row in records}
    result = []
    for host in sorted(hosts):
        labels = host.split(".")
        if not any(".".join(labels[index:]) in hosts for index in range(1, len(labels))):
            result.append(host)
    return result


def render(records):
    hosts = rule_hosts(records)
    reviewed = max(row["reviewed_on"] for row in records)
    header = ["! Title: PH Gambling Blocklist", "! Description: Reviewed Philippine gambling domains and their subdomains.", f"! Homepage: {HOMEPAGE}", "! License: MIT", "! Expires: 1 days", f"! Last reviewed: {reviewed}", f"! Rules: {len(hosts)}"]
    tracker = ["# Reviewed domains", "", f"{len(records)} reviewed hostnames; {len(hosts)} AdGuard rules after removing covered subdomains.", "", "Generated from `data/domains.json`. Review dates describe evidence review, not live availability or licence status.", "", "| Domain | Evidence | Reviewed |", "| --- | --- | --- |"]
    tracker.extend(f"| `{row['domain']}` | [Source]({row['evidence_url']}) | {row['reviewed_on']} |" for row in records)
    return {
        "blocklists/adguard.txt": "\n".join(header + [f"||{host}^" for host in hosts]) + "\n",
        "blocklists/domains.txt": "".join(row["domain"] + "\n" for row in records),
        "docs/domains.md": "\n".join(tracker) + "\n",
    }


def write_text(path, content):
    path.parent.mkdir(exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n", dir=path.parent, delete=False) as temporary:
        temporary.write(content)
    Path(temporary.name).replace(path)


def build(root, check=False):
    records, _ = load_catalog(root)
    outputs = render(records)
    drift = []
    for name, content in outputs.items():
        path = root / name
        if check:
            if not path.exists() or path.read_bytes() != content.encode("utf-8"):
                drift.append(name)
        else:
            write_text(path, content)
    return drift
