"""Discover explicit hostnames from PAGCOR; never approve them automatically."""

from datetime import datetime, timezone
from hashlib import sha256
from io import BytesIO
import json
import re
from urllib.request import Request, urlopen

from .catalog import HOMEPAGE, canonical_host, load_catalog, overlaps, write_text


SOURCE_URL = "https://www.pagcor.ph/regulatory/pdf/App%20Kits/List-of-PAGCOR-Accredited-Gaming-System-Administrators-and-Registered-Brands-and-Domain-Names-URLs.pdf"
DOMAIN_TOKEN = re.compile(r"(?<![A-Za-z0-9@_.-])(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+[A-Za-z]{2,63}(?![A-Za-z0-9_.-])")


def extract_hosts(text):
    return {canonical_host(match.group()) for match in DOMAIN_TOKEN.finditer(text)}


def parse_document_date(text):
    match = re.search(r"as of ([A-Za-z]+ [0-9]{1,2}, [0-9]{4}):", text)
    if not match:
        raise ValueError("PAGCOR register date is missing; review the source format")
    return datetime.strptime(match.group(1), "%B %d, %Y").date().isoformat()


def read_register(payload):
    from pypdf import PdfReader

    reader = PdfReader(BytesIO(payload))
    texts = [page.extract_text() or "" for page in reader.pages]
    first = texts[0] if texts else ""
    if "List of PAGCOR-Accredited Gaming System Administrators" not in first:
        raise ValueError("document is not the expected PAGCOR domain register")
    published = parse_document_date(first)
    domains = {}
    for number, text in enumerate(texts, start=1):
        for host in extract_hosts(text):
            domains.setdefault(host, []).append(number)
    if not domains:
        raise ValueError("no domains extracted; review the source format")
    metadata = {"url": SOURCE_URL, "published_on": published, "sha256": sha256(payload).hexdigest(), "pages": len(texts), "extracted_hosts": len(domains)}
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


def fetch_register():
    request = Request(SOURCE_URL, headers={"User-Agent": f"ph-gambling-blocklist/0.1 (+{HOMEPAGE})"})
    with urlopen(request, timeout=60) as response:
        return response.read()


def refresh(root, pdf=None):
    records, exclusions = load_catalog(root)
    payload = pdf.read_bytes() if pdf else fetch_register()
    metadata, discovered = read_register(payload)
    metadata["retrieved_at"] = datetime.now(timezone.utc).isoformat()
    report = {"source": metadata, "counts": {"reviewed": len(records), "extracted": len(discovered)}, **compare(discovered, records, exclusions, source_url=SOURCE_URL)}
    write_text(root / "reports/pagcor.json", json.dumps(report, indent=2) + "\n")
    return report
