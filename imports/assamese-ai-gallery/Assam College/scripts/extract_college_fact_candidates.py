"""Extract reviewable snippets for empty fields from reachable college sites."""

import csv
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

from scrape_general_colleges import ROOT, SOURCE, OUTPUT, PIN_RE, extract, fetch


TARGET = ROOT / "general_colleges_fact_candidates.csv"
YEAR_RE = re.compile(r"(?:established|founded|set up|came into existence|started functioning|estd\.?|since)\W{0,50}(?:in\W{0,15})?((?:18|19|20)\d{2})", re.I)
PRINCIPAL_RE = re.compile(r"(?:from the principal.?s desk|principal.?s desk|principal\s*[:\-])", re.I)


def snippet(text, match, before=75, after=120):
    return " ".join(text[max(0, match.start()-before):match.end()+after].split())[:230]


def inspect(row, audit):
    result = {"No.": row["No."], "College / Institute": row["College / Institute"],
              "Source URL": audit["Final URL"], "Candidate Established": "",
              "Year Evidence": "", "Principal Evidence": "", "Address Evidence": "", "PIN Evidence": "", "NAAC Evidence": "", "Affiliation Evidence": ""}
    if not audit["Status"].startswith("scraped"):
        return result
    status, response, html = fetch(audit["Final URL"])
    if status != "ok":
        return result
    text = extract(html, response.url)["text"]
    years = [m for m in YEAR_RE.finditer(text) if 1800 <= int(m.group(1)) <= 2026]
    if len({m.group(1) for m in years}) == 1:
        result["Candidate Established"] = years[0].group(1)
    result["Year Evidence"] = " | ".join(snippet(text, m) for m in years[:3])
    result["Principal Evidence"] = " | ".join(snippet(text, m, 30, 120) for m in list(PRINCIPAL_RE.finditer(text))[:3])
    addr = list(re.finditer(r"(?:address|location|pin\s*code)\s*[:\-]", text, re.I))
    result["Address Evidence"] = " | ".join(snippet(text, m, 15, 140) for m in addr[:2])
    pins = list(PIN_RE.finditer(text))
    result["PIN Evidence"] = " | ".join(snippet(text, m, 90, 55) for m in pins[:2])
    naac = list(re.finditer(r"NAAC\W{0,20}(?:accredited|grade|rated|re.?accredited|with\W+grade)", text, re.I))
    result["NAAC Evidence"] = " | ".join(snippet(text, m, 30, 90) for m in naac[:2])
    affiliated = list(re.finditer(r"affiliated\W{0,8}to", text, re.I))
    result["Affiliation Evidence"] = " | ".join(snippet(text, m, 25, 90) for m in affiliated[:2])
    return result


def main():
    with SOURCE.open(newline="", encoding="utf-8-sig") as file:
        rows = list(csv.DictReader(file))
    with OUTPUT.open(newline="", encoding="utf-8-sig") as file:
        audit = {a["No."]: a for a in csv.DictReader(file)}
    targets = [r for r in rows if audit[r["No."]]["Status"].startswith("scraped")]
    with ThreadPoolExecutor(max_workers=6) as pool:
        jobs = {pool.submit(inspect, r, audit[r["No."]]): r for r in targets}
        facts = [job.result() for job in as_completed(jobs)]
    facts.sort(key=lambda x: int(x["No."]))
    with TARGET.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=list(facts[0]))
        writer.writeheader()
        writer.writerows(facts)
    print(f"Saved {len(facts)} review rows; {sum(bool(x['Candidate Established']) for x in facts)} unambiguous year candidates")


if __name__ == "__main__":
    main()
