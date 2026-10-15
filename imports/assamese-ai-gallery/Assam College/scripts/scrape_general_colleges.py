"""Survey official college sites referenced by general_colleges.csv.

This script collects candidate facts and page URLs. It does not overwrite the
directory because contact and course details need college-specific review.
"""

from __future__ import annotations

import argparse
import csv
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "general_colleges.csv"
OUTPUT = ROOT / "general_colleges_scrape_audit.csv"
EXCLUDED_IDS = {"23", "67", "73", "193", "277", "313", "339"}
UNIVERSITY_EVIDENCE = {
    "23": "https://highereducation.assam.gov.in/documents-detail/the-first-statutes-of-kokrajhar-university-2026",
    "67": "https://highereducation.assam.gov.in/documents-detail/the-first-statutes-of-bongaigaon-university-2026",
    "73": "https://highereducation.assam.gov.in/documents-detail/the-first-statutes-of-gurucharan-university-2026",
    "193": "https://highereducation.assam.gov.in/documents/notifications-1?page=1",
    "277": "https://highereducation.assam.gov.in/documents-detail/the-first-statutes-of-north-lakhimpur-university-2026",
    "313": "https://highereducation.assam.gov.in/documents-detail/the-first-statutes-of-nagaon-university-2026",
    "339": "https://highereducation.assam.gov.in/documents/notifications-1?page=1",
}
SHARED_HOSTS = {
    "assamadmission.samarth.ac.in", "directorateofhighereducation.assam.gov.in",
    "highereducation.assam.gov.in", "drive.google.com", "study-india.org",
    "www.study-india.org", "dibru-files.sgp1.digitaloceanspaces.com",
    "www.careers360.com", "www.silapathartc.in",
}
EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.I)
PIN_RE = re.compile(r"\b(?:PIN\s*(?:CODE)?\s*[:\-]?\s*)?([78]\d{5})\b", re.I)
LINK_RE = re.compile(r"contact|about|principal|academic|course|programme|department", re.I)
BAD_EMAIL_RE = re.compile(r"noreply|no-reply|support@|webmaster|developer|webdesign|ss.?tech|example|gmail\.com\.png", re.I)
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; AssamCollegeResearch/1.0; public-information-audit)"}


def host(url: str) -> str:
    return (urlparse(url).hostname or "").lower()


def homepage(row: dict[str, str]) -> tuple[str, str]:
    listed = row["Website URL"].strip()
    if listed and host(listed) not in SHARED_HOSTS:
        return listed, "listed website"
    source = row["Department Source URL"].strip()
    verification = row["Department Verification"].lower()
    official_evidence = ("institution site" in verification or "official" in verification or "college navigation" in verification or "college-hosted" in verification)
    if source and host(source) not in SHARED_HOSTS and official_evidence:
        parsed = urlparse(source)
        return f"{parsed.scheme}://{parsed.netloc}/", "college department source domain"
    return "", "no college-specific URL in CSV"


def fetch(url: str) -> tuple[str, requests.Response | None, str]:
    try:
        response = requests.get(url, headers=HEADERS, timeout=(5, 12), allow_redirects=True)
        if response.status_code >= 400:
            return "HTTP " + str(response.status_code), response, ""
        kind = response.headers.get("Content-Type", "").lower()
        if "html" not in kind and not response.text.lstrip().startswith("<"):
            return "non-HTML", response, ""
        return "ok", response, response.text[:2_000_000]
    except requests.RequestException as exc:
        return type(exc).__name__, None, ""


def extract(html: str, page_url: str) -> dict[str, object]:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()
    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    text = soup.get_text(" ", strip=True)
    emails = set(EMAIL_RE.findall(text))
    links = []
    for a in soup.find_all("a", href=True):
        href = urljoin(page_url, a["href"])
        if a["href"].startswith("mailto:"):
            emails.update(EMAIL_RE.findall(a["href"]))
        label = a.get_text(" ", strip=True)
        if LINK_RE.search(label) and host(href) == host(page_url) and not re.search(r"\.(pdf|jpg|png|zip)(?:\?|$)", href, re.I):
            links.append((label, href))
    emails = sorted(e for e in emails if not BAD_EMAIL_RE.search(e))
    pins = sorted(set(PIN_RE.findall(text)))
    return {"title": title[:180], "emails": emails[:20], "pins": pins[:15], "links": links[:30], "text": text}


def survey(row: dict[str, str]) -> dict[str, str]:
    base = {"No.": row["No."], "College / Institute": row["College / Institute"]}
    if row["No."] in EXCLUDED_IDS:
        return {**base, "Status": "excluded: upgraded university", "Candidate Website": "", "Website Basis": "", "Final URL": "", "Page Title": "", "Candidate Emails": "", "Candidate PINs": "", "Evidence Pages": UNIVERSITY_EVIDENCE[row["No."]], "Notes": "Assam Higher Education university statutes or regulations"}
    target, basis = homepage(row)
    if not target:
        return {**base, "Status": "no official site URL", "Candidate Website": "", "Website Basis": basis, "Final URL": "", "Page Title": "", "Candidate Emails": "", "Candidate PINs": "", "Evidence Pages": "", "Notes": "Search needed"}
    status, response, html = fetch(target)
    if status != "ok":
        return {**base, "Status": status, "Candidate Website": target, "Website Basis": basis, "Final URL": response.url if response else "", "Page Title": "", "Candidate Emails": "", "Candidate PINs": "", "Evidence Pages": "", "Notes": ""}
    info = extract(html, response.url)
    evidence = [response.url]
    emails = set(info["emails"])
    pins = set(info["pins"])
    detail_links = sorted(info["links"], key=lambda x: (0 if re.search(r"contact", x[0], re.I) else 1, len(x[1])))
    for label, link in detail_links:
        if len(evidence) >= 3:
            break
        if link in evidence:
            continue
        time.sleep(0.25)
        substatus, subresponse, subhtml = fetch(link)
        if substatus != "ok":
            continue
        subinfo = extract(subhtml, subresponse.url)
        evidence.append(subresponse.url)
        emails.update(subinfo["emails"])
        pins.update(subinfo["pins"])
    notes = "Review candidate facts before editing CSV"
    return {**base, "Status": "scraped", "Candidate Website": target, "Website Basis": basis, "Final URL": response.url, "Page Title": info["title"], "Candidate Emails": "; ".join(sorted(emails)[:20]), "Candidate PINs": "; ".join(sorted(pins)[:15]), "Evidence Pages": "; ".join(evidence), "Notes": notes}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=5)
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    with SOURCE.open(newline="", encoding="utf-8-sig") as file:
        rows = list(csv.DictReader(file))
    if args.limit:
        rows = rows[:args.limit]
    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(survey, row): row["No."] for row in rows}
        for number, future in enumerate(as_completed(futures), 1):
            results.append(future.result())
            if number % 50 == 0:
                print(f"Surveyed {number}/{len(rows)}", flush=True)
    results.sort(key=lambda x: int(x["No."]))
    fields = ["No.", "College / Institute", "Status", "Candidate Website", "Website Basis", "Final URL", "Page Title", "Candidate Emails", "Candidate PINs", "Evidence Pages", "Notes"]
    with OUTPUT.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)
    print(f"Saved {len(results)} rows to {OUTPUT}")


if __name__ == "__main__":
    main()
