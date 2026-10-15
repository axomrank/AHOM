"""Retry failed college-site survey rows using alternate URLs already in the CSV."""

import csv
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urlparse

from scrape_general_colleges import ROOT, SOURCE, OUTPUT, SHARED_HOSTS, extract, fetch, host


def candidates(row):
    urls = []
    for field in ("Department Source URL", "Website URL"):
        for url in re.findall(r"https?://[^\s;]+", row[field]):
            if host(url) in SHARED_HOSTS:
                continue
            parsed = urlparse(url)
            base = f"{parsed.scheme}://{parsed.netloc}/"
            for candidate in (base, url):
                if candidate not in urls:
                    urls.append(candidate)
            if parsed.scheme == "https":
                fallback = f"http://{parsed.netloc}/"
                if fallback not in urls:
                    urls.append(fallback)
    return urls[:4]


def retry(row, audit):
    previous = audit["Candidate Website"]
    for target in candidates(row):
        if target == previous:
            continue
        status, response, html = fetch(target)
        if status != "ok":
            continue
        info = extract(html, response.url)
        return {**audit, "Status": "scraped on retry", "Candidate Website": target,
                "Website Basis": "alternate URL in CSV", "Final URL": response.url,
                "Page Title": info["title"], "Candidate Emails": "; ".join(info["emails"]),
                "Candidate PINs": "; ".join(info["pins"]),
                "Evidence Pages": response.url,
                "Notes": "Review candidate facts before editing CSV"}
    return audit


def main():
    with SOURCE.open(newline="", encoding="utf-8-sig") as file:
        source = {r["No."]: r for r in csv.DictReader(file)}
    with OUTPUT.open(newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        fields = reader.fieldnames
        audit = list(reader)
    todo = [a for a in audit if a["Status"] not in ("scraped", "no official site URL", "excluded: upgraded university")]
    with ThreadPoolExecutor(max_workers=6) as pool:
        jobs = {pool.submit(retry, source[a["No."]], a): a["No."] for a in todo}
        changed = {}
        for job in as_completed(jobs):
            result = job.result()
            if result["Status"] == "scraped on retry":
                changed[result["No."]] = result
    output = [changed.get(a["No."], a) for a in audit]
    with OUTPUT.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(output)
    print(f"Recovered {len(changed)} of {len(todo)} failed sites")


if __name__ == "__main__":
    main()
