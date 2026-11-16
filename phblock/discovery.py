"""Discover explicit hostnames from PAGCOR; never approve them automatically."""

from datetime import datetime, timezone
from hashlib import sha256
from io import BytesIO
import json
import re
from urllib.request import Request, urlopen

from .catalog import HOMEPAGE, canonical_host, load_catalog, overlaps, write_text


SOURCE_URL = "https://www.pagcor.ph/regulatory/pdf/App%20Kits/List-of-PAGCOR-Accredited-Gaming-System-Administrators-and-Registered-Brands-and-Domain-Names-URLs.pdf"
DOMAIN_TOKEN = re.compile(r"(?<![A-Za-z0-9@_.-])(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+[A-Za-z]{2,63}(?![A-Za-z0-9_-]|\.[A-Za-z0-9_-])")
WRAPPED_TOKEN = re.compile(r"[A-Za-z0-9.-]+[.-][ \t]*\r?\n[ \t]*[A-Za-z0-9.-]+\.[A-Za-z]{2,63}")


def skip_wrapped(match, issues):
    issues.append({"token": match.group(), "reason": "line-wrapped token; inspect the PDF"})
    return " "


def extract_hosts(text, issues=None):
    issues = [] if issues is None else issues
    cleaned = WRAPPED_TOKEN.sub(lambda match: skip_wrapped(match, issues), text)
    hosts = set()
    for match in DOMAIN_TOKEN.finditer(cleaned):
        try:
            hosts.add(canonical_host(match.group()))
        except ValueError:
            issues.append({"token": match.group(), "reason": "invalid hostname"})
    return hosts


def parse_document_date(text):
    match = re.search(r"as of ([A-Za-z]+ [0-9]{1,2}, [0-9]{4}):", text)
    if not match:
        raise ValueError("PAGCOR register date is missing; review the source format")
    return datetime.strptime(match.group(1), "%B %d, %Y").date().isoformat()


def pdf_texts(payload):
    from pypdf import PdfReader
    from pypdf.errors import PyPdfError

    try:
        reader = PdfReader(BytesIO(payload))
        return [page.extract_text() or "" for page in reader.pages]
    except PyPdfError as error:
        raise ValueError("Cannot read PAGCOR document as PDF; check the download") from error


def read_register(payload):
    texts = pdf_texts(payload)
    first = texts[0] if texts else ""
    if "List of PAGCOR-Accredited Gaming System Administrators" not in first:
        raise ValueError("document is not the expected PAGCOR domain register")
    published = parse_document_date(first)
    domains = {}
    extraction_issues = []
    for number, text in enumerate(texts, start=1):
        issues = []
        for host in extract_hosts(text, issues):
            domains.setdefault(host, []).append(number)
        extraction_issues.extend({"page": number, **issue} for issue in issues)
    if not domains:
        raise ValueError("no domains extracted; review the source format")
    metadata = {"url": SOURCE_URL, "published_on": published, "sha256": sha256(payload).hexdigest(), "pages": len(texts), "extracted_hosts": len(domains), "extraction_issues": extraction_issues}
    return metadata, dict(sorted(domains.items()))


def compare(discovered, records, exclusions, source_url=None):
    reviewed = {row["domain"] for row in records}
    excluded = sorted(host for host in discovered if any(overlaps(host, entry["domain"]) for entry in exclusions))
    available = set(discovered) - set(excluded)
    relevant = {row["domain"] for row in records if source_url is None or row["evidence_url"].partition("#")[0] == source_url}
    return {
        "additions": [{"domain": host, "pages": discovered[host]} for host in sorted(available - reviewed)],
        "missing": sorted(relevant - available),
        "retained": len(reviewed & available),
        "excluded": excluded,
    }


def fetch_public(url):
    request = Request(url, headers={"User-Agent": f"ph-gambling-blocklist/0.1 (+{HOMEPAGE})"})
    with urlopen(request, timeout=60) as response:
        return response.read()


def fetch_register():
    return fetch_public(SOURCE_URL)


def refresh(root, pdf=None):
    records, exclusions = load_catalog(root)
    payload = pdf.read_bytes() if pdf else fetch_register()
    metadata, discovered = read_register(payload)
    metadata["retrieved_at"] = datetime.now(timezone.utc).isoformat()
    report = {"source": metadata, "counts": {"reviewed": len(records), "extracted": len(discovered)}, **compare(discovered, records, exclusions, source_url=SOURCE_URL)}
    write_text(root / "reports/pagcor.json", json.dumps(report, indent=2) + "\n")
    return report
