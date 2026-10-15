"""Apply conservative, source-backed scrape findings to general_colleges.csv."""

import csv
import os
import tempfile
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

from scrape_general_colleges import ROOT, SOURCE, OUTPUT, EXCLUDED_IDS


FACTS = ROOT / "general_colleges_fact_candidates.csv"
EMAIL_REJECT_IDS = {"176", "292"}  # Personal addresses, not institutional contacts.
YEAR_REJECT_IDS = {"232"}  # Year refers to local legislators, not the college.
PRINCIPALS = {
    "2": "Dr. Habib Shahidul Islam",
    "3": "Dr. Pradip Das",
    "11": "Dr. Biswajit Biswas (in charge)",
    "33": "Dr. Ghanashyam Deka",
    "45": "Mohd. Anwaru-Al Islam Khan",
    "48": "Dr. Nayan Jyoti Das",
    "71": "Dr. Zahurul Islam",
    "99": "Dr. Runumoni Lahkar Das",
    "104": "Dr. Dilip Kumar Jha",
    "149": "Dr. Utpal Das",
    "159": "Dr. Surajit Dutta",
    "176": "Dilwar Hussain Ahmed Mozumder",
    "182": "Sumita Debnath (in charge)",
    "198": "Uttam Baruah",
    "214": "Dr. Lukendra Kakati",
    "240": "Dr. Dinamani Kalita",
    "290": "Sri Kandarpa Saikia",
    "310": "Dr. Sayed Ahammed Ali",
    "318": "Dr. Arun Borah",
    "322": "Dr. Kabita Choudhury (in charge)",
    "349": "Dr. Shaher Ali",
}
DIRECT_OFFICIAL_FACTS = {
    "46": {
        "College / Institute": "Barpeta College (formerly Barpeta Girls' College)",
        "Courses / Streams": "Arts, Commerce / BA, B.Com",
        "Accreditation": "NAAC C",
        "Highlights": "Coeducational since 2024–25; formerly Barpeta Girls' College",
    },
    "47": {"Accreditation": "NAAC B"},
    "49": {"Accreditation": "NAAC B+"},
    "50": {"University / Board": "Bhattadev University"},
    "95": {"University / Board": "Bodoland University"},
    "140": {"Accreditation": "NAAC accredited; grade not verified"},
    "209": {"Accreditation": "NAAC accredited; grade not verified"},
    "236": {"Accreditation": "NAAC B"},
    "274": {"Accreditation": "NAAC accredited; grade not verified"},
    "298": {"District": "Hojai", "University / Board": "Rabindranath Tagore University", "Accreditation": "NAAC B"},
    "308": {"Accreditation": "NAAC B"},
    "21": {
        "Website URL": "https://gmcdeithor.ac.in/",
        "Location": "Deithor, Bokajan, Karbi Anglong, Assam",
        "PIN Code": "785615",
        "Established": "2020",
        "Principal / Head": "Dr. Phulmoni Das (in charge)",
    },
    "331": {"PIN Code": "785697"},
    "310": {"District": "Hojai"},
}
OFFICIAL_LOCATIONS = {
    "2": "Jahanar Ghola, Mandia, Barpeta, Assam",
    "3": "Kakdhowa, Gomaphulbari, Barpeta, Assam",
    "11": "Chirakuta, Bilasipara, Dhubri, Assam",
    "13": "Diblong, Dima Hasao, Assam",
    "33": "Baghmara, Bajali, Assam",
    "42": "Nagaon, Barpeta, Assam",
    "45": "Langla, Barpeta, Assam",
    "47": "Bhawanipur, Barpeta, Assam",
    "48": "Sarupeta, Barpeta, Assam",
    "49": "Barpeta Road, Barpeta, Assam",
    "50": "Naligaon, Barpeta, Assam",
    "52": "Alopati Majar Char, Kalairdia, Barpeta, Assam",
    "68": "Boitamari, Bongaigaon, Assam",
    "69": "Chalantapara, Bongaigaon, Assam",
    "71": "Lengtisinga, Bongaigaon, Assam",
    "95": "Serfanguri, Chirang, Assam",
    "99": "Karimchowk, Mangaldoi, Darrang, Assam",
    "104": "Gogamukh, Dhemaji, Assam",
    "105": "Jiadhal, Dhemaji, Assam",
    "125": "Satsia, Jamadarhat, Dhubri, Assam",
    "140": "Natun Nagar, Moran, Dibrugarh, Assam",
    "149": "Agia, Goalpara, Assam",
    "158": "Barpathar, Golaghat, Assam",
    "159": "Bokakhat, Golaghat, Assam",
    "164": "Hatiakhowa Gaon, Golaghat, Assam",
    "167": "Khumtai, Golaghat, Assam",
    "170": "Kamargaon, Golaghat, Assam",
    "171": "Doigrong, Golaghat, Assam",
    "172": "Melamora Gaon, Golaghat, Assam",
    "176": "Algapur, Hailakandi, Assam",
    "178": "Kalinagar, Hailakandi, Assam",
    "182": "Hojai, Assam",
    "187": "Jogduar, Teok, Jorhat, Assam",
    "209": "Chatribari, Guwahati, Kamrup Metropolitan, Assam",
    "231": "Kulhati, Kamrup, Assam",
    "232": "Garoimari, Kamrup, Assam",
    "234": "Rangia, Kamrup, Assam",
    "237": "Pacharia, Kamrup, Assam",
    "239": "Guiya, Kamrup, Assam",
    "240": "Rampur, South Kamrup, Assam",
    "274": "Charaimoria, North Lakhimpur, Lakhimpur, Assam",
    "276": "Ghilamara, Lakhimpur, Assam",
    "279": "Panigaon, Lakhimpur, Assam",
    "283": "Khaga, North Lakhimpur, Assam",
    "287": "Bongaon, Majuli, Assam",
    "290": "Bhuragaon, Morigaon, Assam",
    "298": "Udali Bazar, Hojai, Assam",
    "304": "Baliram Pathar, Jamunamukh, Nagaon, Assam",
    "310": "Murazar, Hojai, Assam",
    "311": "Panigaon, Nagaon, Assam",
    "322": "Rupiabathan, Chamata, Nalbari, Assam",
    "331": "Namtial Pathar, Sivasagar, Assam",
    "336": "Nitaipukhuri, Sivasagar, Assam",
    "344": "Tezpur, Sonitpur, Assam",
    "349": "Hatsingimari, South Salmara Mankachar, Assam",
    "357": "Kakopather, Tinsukia, Assam",
}


def read(path):
    with path.open(newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        return reader.fieldnames, list(reader)


def unique(value):
    return value.strip() if value.strip() and ";" not in value else ""


def main():
    fields, original = read(SOURCE)
    _, audits = read(OUTPUT)
    _, facts = read(FACTS)
    audits = {a["No."]: a for a in audits}
    facts = {a["No."]: a for a in facts}
    changes = Counter()
    output = []
    for old in original:
        row = old.copy()
        key = row["No."]
        if key in EXCLUDED_IDS:
            changes["excluded upgraded universities"] += 1
            continue
        audit = audits[key]
        if audit["Status"].startswith("scraped"):
            website = audit["Candidate Website"].strip()
            parsed = urlparse(website)
            if not row["Website URL"] and parsed.path in ("", "/"):
                row["Website URL"] = website
                changes["Website URL"] += 1
            email = unique(audit["Candidate Emails"])
            if not row["Official Email"] and email and key not in EMAIL_REJECT_IDS:
                row["Official Email"] = email
                changes["Official Email"] += 1
            pin = unique(audit["Candidate PINs"])
            if not row["PIN Code"] and pin:
                row["PIN Code"] = pin
                changes["PIN Code"] += 1
            year = facts.get(key, {}).get("Candidate Established", "")
            if not row["Established"] and year and key not in YEAR_REJECT_IDS:
                row["Established"] = year
                changes["Established"] += 1
            if not row["Principal / Head"] and key in PRINCIPALS:
                row["Principal / Head"] = PRINCIPALS[key]
                changes["Principal / Head"] += 1
        for column, value in DIRECT_OFFICIAL_FACTS.get(key, {}).items():
            if row[column] != value:
                row[column] = value
                changes[column] += 1
        if not row["Location"] and key in OFFICIAL_LOCATIONS:
            row["Location"] = OFFICIAL_LOCATIONS[key]
            changes["Location"] += 1
        output.append(row)
    assert len(output) == len(original) - sum(r["No."] in EXCLUDED_IDS for r in original)
    assert len({r["No."] for r in output}) == len(output)
    handle, tmp = tempfile.mkstemp(prefix="general_colleges_", suffix=".csv", dir=ROOT)
    try:
        with os.fdopen(handle, "w", newline="", encoding="utf-8-sig") as file:
            writer = csv.DictWriter(file, fieldnames=fields)
            writer.writeheader()
            writer.writerows(output)
        os.replace(tmp, SOURCE)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    print(dict(changes))
    print(f"Remaining colleges: {len(output)}")


if __name__ == "__main__":
    main()
