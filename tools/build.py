#!/usr/bin/env python3
"""Build the website's data from the master file, data/ahom.csv (plus data/eras.json for the saga chapters).

Writes two files:
  data/ahom.json  the whole catalogue nested as period > groups > characters > scenes, and by century
  data/site.js    what the website loads: window.AHOM = {eras, reels, groups, people, reigns, scenes}

Each CSV row is one record, told apart by the `type` column:
  period  the Ahom period (name, dates, summary; group_order = the order of the person groups)
  person  a person; `group` places them, ahom_king_no places a king in the line (two numbers for two reigns).
          character_sheets lists images as "path | caption"; the kind (portrait, pose, turnaround, sheet)
          is the start of the file name, and the size is read from the file.
  scene   an event in the chronicle; scene_image is its painting (empty if not painted yet),
          people = everyone in it, main_people = who it is about, group = its era
Lists inside a cell are separated by "; ". Every image's thumbnail is the same file name in a thumb/ folder.

In site.js, versions of a scene (same era and title) become one scene with several images, kings are put
in reign order, and notes about how the images were made are left out. `face` is each person's small
portrait: a painted portrait if there is one, else the face cut from their sheet by tools/make_faces.py.
Loading the data as a script lets the site open straight from disk as well as from a server.
Unknown ids and missing files are printed and the build fails.
Run: python3 tools/build.py
"""
import csv, json, re, sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
problems = []


def exists(rel):
    if rel and not (ROOT / rel).is_file():
        problems.append(f"missing file: {rel}")
    return rel


# notes mix history with notes about how the images were made; the site shows only the history
MAKING = re.compile(r"catalogu|character sheet|\bsheet\b|reference|reconstruction|research/|\.md\b|user-provided|provisional|artistic|interpretive|costume|portrait|database|project", re.I)


def public_notes(text):
    return " ".join(s for s in re.split(r"(?<=[.!?])\s+", (text or "").strip()) if s and not MAKING.search(s))


def years(label):
    """'1811–1818, 1819–1821' -> [(1811, 1818), (1819, 1821)]"""
    spans = []
    for part in (label or "").split(","):
        nums = [int(n) for n in re.findall(r"\d{4}", part)]
        if nums:
            spans.append((nums[0], nums[-1]))
    return spans


def build_site(src):
    cfg = json.loads((ROOT / "data/eras.json").read_text(encoding="utf-8"))
    period = src["periods"][0]

    # scenes: every scene appears under each of its people and centuries, so collect by id first
    raw = {}
    for c in src["centuries"]:
        for s in c["scenes"]:
            raw.setdefault(s["id"], s)
    for s in src.get("scenes_without_characters", []):
        raw.setdefault(s["id"], s)

    era_of_group = {g: e["id"] for e in cfg["eras"] for g in e["groups"]}
    merged, by_key = [], {}
    for s in sorted(raw.values(), key=lambda s: (s.get("sort_year") or 0, s["id"])):
        if s["era"] not in era_of_group:
            problems.append(f"scene {s['id']}: era {s['era']!r} is in no chapter of eras.json")
            continue
        key = (s["era"], s["title"])
        img = s.get("scene_image")
        if key in by_key:
            m = by_key[key]
            m["alias"].append(s["id"])
            m['sources'] = list(dict.fromkeys(m.get('sources', []) + s.get('sources', [])))
            if img:
                m["images"].append([exists(img), exists(s.get("scene_thumbnail"))])
            continue
        m = {
            "id": s["id"], "alias": [], "title": s["title"], "date": s.get("date_label", ""),
            "year": s.get("sort_year") or (years(s.get("date_label"))[0][0] if years(s.get("date_label")) else None), "era": era_of_group[s["era"]], "summary": s.get("summary", ""),
            "notes": public_notes(s.get("notes")), "people": s.get("people", []), "main": s.get("main_people", []),
            "sources": s.get("sources", []),
            "alt": s["title"] + ". Modern illustrated reconstruction.",
            "images": [[exists(img), exists(s.get("scene_thumbnail"))]] if img else [],
        }
        by_key[key] = m
        merged.append(m)
    # undated scenes take the year of the scene before them so they stay inside their era
    last = {}
    for m in merged:
        if m["year"] is None:
            m["year"] = last.get(m["era"])
        last[m["era"]] = m["year"]
    merged.sort(key=lambda m: ([e["id"] for e in cfg["eras"]].index(m["era"]), m["year"] or 0))
    alias = {a: m["id"] for m in merged for a in [m["id"], *m["alias"]]}

    people, groups, reigns = {}, [], []
    for g in period["dynasties"]:
        groups.append({"name": g["name"], "ids": [c["id"] for c in g["characters"]]})
        for c in g["characters"]:
            imgs = [{"src": exists(i["image"]), "thumb": exists(i["thumbnail"]), "kind": i["kind"],
                     "caption": i.get("caption", "") if i["kind"] in ("portrait", "pose") else f"{c['name']}: character study",
                     "w": i.get("width"), "h": i.get("height")}
                    for i in c.get("character_sheets", [])]
            # the small arch portrait: a painted portrait if there is one, else the face cut from the sheet
            painted = [i["thumb"] for i in imgs if i["kind"] in ("portrait", "pose")]
            cut = f"media/faces/{c['id']}.webp"
            face = painted[0] if painted else cut if (ROOT / cut).is_file() else imgs[0]["thumb"] if imgs else ""
            scene_ids = list(dict.fromkeys(alias[s["id"]] for s in c.get("scenes", []) if s["id"] in alias))
            people[c["id"]] = {k: v for k, v in {
                "id": c["id"], "name": c["name"], "as": c.get("name_assamese", ""), "group": g["name"],
                "date": c.get("date_label", ""), "start": c.get("start_year"), "end": c.get("end_year"),
                "role": c.get("role", ""), "summary": c.get("summary", ""), "notes": public_notes(c.get("notes")),
                "tai": c.get("tai_name", ""), "hindu": c.get("hindu_name", ""), "aka": c.get("also_called", ""),
                "relation": c.get("relation", ""), "fate": c.get("fate", ""), "consort": c.get("consort", ""),
                "confidence": c.get("confidence", ""), "sources": c.get("sources", []),
                "face": face, "images": imgs, "scenes": scene_ids,
            }.items() if v not in ("", None, [])}
            nos = c.get("ahom_king_no") or []
            spans = years(c.get("date_label"))
            for i, no in enumerate(nos):
                a, b = spans[min(i, len(spans) - 1)] if spans else (c.get("start_year"), c.get("end_year"))
                reigns.append({"no": no, "id": c["id"], "start": a, "end": b, "again": i > 0})
    reigns.sort(key=lambda r: r["no"])

    for m in merged:
        for pid in m["people"] + m["main"]:
            if pid not in people:
                problems.append(f"scene {m['id']}: unknown person {pid!r}")
        m["people"] = [p for p in m["people"] if p in people]
        m["main"] = [p for p in m["main"] if p in people]
        if not m["alias"]:
            del m["alias"]

    eras = []
    for e in cfg["eras"]:
        for sid in e["moments"]:
            if sid not in alias:
                problems.append(f"era {e['id']}: unknown scene {sid!r}")
        for pid in e["people"]:
            if pid not in people:
                problems.append(f"era {e['id']}: unknown person {pid!r}")
        eras.append({k: e[k] for k in ("id", "title", "start", "end", "word", "gloss", "lead", "people")} | {
            "reel": e.get("reel"), "moments": [alias.get(s, s) for s in e["moments"]],
            "scenes": [m["id"] for m in merged if m["era"] == e["id"]]})

    reels = []
    for r in cfg["reels"]:
        exists(r.get("src", f"media/reels/{r['id']}.mp4")); exists(r.get("poster", f"media/reels/{r['id']}.webp"))
        if r.get("scene") not in alias:
            problems.append(f"reel {r['id']}: unknown scene {r.get('scene')!r}")
        else:
            r = dict(r, scene=alias[r["scene"]])
        reels.append(r)

    if problems:
        return
    explore = json.loads((ROOT / "data/explore.json").read_text(encoding="utf-8"))
    for trail in explore["trails"]:
        for sid in trail["scenes"]:
            if sid not in alias:
                problems.append(f"trail {trail['id']}: unknown scene {sid}")
        trail["scenes"] = [alias.get(sid, sid) for sid in trail["scenes"]]
    for place in explore["places"]:
        place["scenes"] = [m["id"] for m in merged if any(term.casefold() in (m["title"] + ' ' + m['summary']).casefold() for term in place["terms"])]
    if problems:
        return
    contexts = json.loads((ROOT / 'data/reel-context.json').read_text(encoding='utf-8'))['as']
    captions = ROOT / 'media/reels/context'
    captions.mkdir(exist_ok=True)
    for r in reels:
        number = int(r['id'].split('-')[0])
        if number > len(contexts):
            problems.append(f"reel {r['id']}: missing Assamese context title")
            continue
        milliseconds = int(r['duration'] * 1000)
        end = f"{milliseconds//3600000:02d}:{milliseconds//60000%60:02d}:{milliseconds//1000%60:02d}.{milliseconds%1000:03d}"
        r['tracks'] = []
        for lang, title, label in [('en', r['title'], 'English · scene context'), ('as', contexts[number-1], 'অসমীয়া · দৃশ্যৰ প্ৰসংগ')]:
            rel = f"media/reels/context/{r['id']}.{lang}.vtt"
            (ROOT / rel).write_text(f'WEBVTT\n\n00:00:00.000 --> {end}\n{title}\n', encoding='utf-8')
            r['tracks'].append({'src': rel, 'lang': lang, 'label': label})
    if problems:
        return
    basemap = json.loads((ROOT / 'assets/maps/assam.json').read_text(encoding='utf-8'))
    for place in explore['places']:
        if len(place.get('geo',[])) != 2:
            problems.append(f"place {place['id']}: missing [latitude, longitude]")
    if problems:
        return
    from map_events import build_map_events
    atlas = build_map_events(ROOT, merged, basemap)
    data = {"eras": eras, "reels": reels, "groups": groups, "people": people, "reigns": reigns, "scenes": merged, "basemap": basemap, "atlas": atlas, **explore}
    out = ROOT / "data/site.js"
    out.write_text("// Generated by tools/build.py from data/ahom.csv and data/eras.json. Do not edit.\nwindow.AHOM = "
                   + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    print(f"{out.relative_to(ROOT)}: {len(eras)} chapters, {len(people)} people, {len(reigns)} reigns, "
          f"{len(merged)} scenes ({sum(len(m['images']) for m in merged)} images), {out.stat().st_size // 1024} KB")
    from static_pages import build_pages
    build_pages(ROOT, data)
    return True


FULL_KINDS = {"sheet", "turnaround", "face", "costume", "props", "palette"}
INTS = ("start_year", "end_year", "sort_year", "koch_no")


def lst(v):
    return [x.strip() for x in (v or "").split(";") if x.strip()]


def thumb_of(path):
    d, n = path.rsplit("/", 1)
    return f"{d}/thumb/{n}"


def num(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return v


def scene_record(r):
    s = {"id": r["id"], "title": r["name"], "date_label": r["date_label"], "century": r["century"],
         "sort_year": num(r["sort_year"]) if r["sort_year"] else None, "era": r["group"],
         "collection": r["collection"], "summary": r["summary"], "notes": r["notes"], "status": r["status"],
         "people": lst(r["people"]), "main_people": lst(r["main_people"]), "sources": lst(r["sources"]),
         "scene_image": exists(r["scene_image"]), "scene_thumbnail": exists(thumb_of(r["scene_image"])) if r["scene_image"] else ""}
    return {k: v for k, v in s.items() if v not in ("", None, []) or k in ("scene_image", "scene_thumbnail")}


def build_tree(rows):
    """The catalogue as nested JSON (data/ahom.json)."""
    period = next(r for r in rows if r["type"] == "period")
    # scenes in date order; an undated scene takes the year in its date label, else the year of the scene
    # numbered just before it, so it stays beside the events it was catalogued with
    scenes = sorted((scene_record(r) for r in rows if r["type"] == "scene"), key=lambda s: s["id"])
    when, last = {}, 0
    for s in scenes:
        last = s.get("sort_year") or next(iter(years(s["date_label"])), (last,))[0]
        when[s["id"]] = (last, s["id"])
    scenes.sort(key=lambda s: when[s["id"]])
    people = [r for r in rows if r["type"] == "person"]
    known = {r["id"] for r in people}
    for s in scenes:
        for pid in s.get("people", []) + s.get("main_people", []):
            if pid not in known:
                problems.append(f"scene {s['id']}: unknown person {pid!r}")

    def character(r):
        c = {k: num(r[k]) if k in INTS else r[k] for k in (
            "id", "name", "name_assamese", "date_label", "start_year", "end_year", "sort_year", "role", "summary",
            "notes", "tai_name", "hindu_name", "also_called", "relation", "fate", "consort", "marital_status",
            "koch_no", "koch_branch", "confidence", "status", "approx_dates")}
        c["ahom_king_no"] = [int(n) for n in lst(r["ahom_king_no"])]
        c["sources"] = lst(r["sources"])
        sheets = []
        for item in lst(r["character_sheets"]):
            path, _, caption = (x.strip() for x in item.partition("|"))
            if not exists(path):
                continue
            w, h = Image.open(ROOT / path).size
            sheet = {"kind": re.sub(r"[-_]?\d+$", "", Path(path).stem), "caption": caption,
                     "image": path, "thumbnail": exists(thumb_of(path)), "width": w, "height": h}
            sheets.append({k: v for k, v in sheet.items() if v != ""})
        mine = [dict({k: v for k, v in s.items() if k != "main_people"}, main=r["id"] in s.get("main_people", []))
                for s in scenes if r["id"] in s.get("people", [])]
        c["sheet_status"] = ("sheet" if any(x["kind"] in FULL_KINDS for x in sheets) else
                             "portrait" if sheets else "scenes" if mine else "none")
        c["character_sheets"] = sheets
        c["scenes"] = mine
        return {k: v for k, v in c.items() if v not in ("", None, [])}

    order = lst(period["group_order"])
    groups = []
    for g in dict.fromkeys(r["group"] for r in people):
        chars = [character(r) for r in people if r["group"] == g]
        starts = [c["start_year"] for c in chars if isinstance(c.get("start_year"), int)]
        ends = [c["end_year"] for c in chars if isinstance(c.get("end_year"), int)]
        groups.append({"name": g, "start_year": min(starts, default=None), "end_year": max(ends, default=None),
                       "characters": chars})
    # groups named in group_order come first in that order, the rest by when they begin
    groups.sort(key=lambda g: (order.index(g["name"]), 0) if g["name"] in order else (len(order), g["start_year"] or 9999))

    centuries = []
    for name in dict.fromkeys(s["century"] for s in scenes if s.get("century")):
        n = int(re.match(r"\d+", name).group())
        these = [s for s in scenes if s.get("century") == name]
        centuries.append({"id": f"c{n}", "name": name, "start_year": (n - 1) * 100, "end_year": n * 100 - 1,
                          "eras": list(dict.fromkeys(s["era"] for s in these)), "scene_count": len(these),
                          "scene_titles": len({s["title"] for s in these}), "scenes": these})
    centuries.sort(key=lambda c: c["start_year"])

    p = {k: num(period[k]) if k in INTS else period[k] for k in ("id", "name", "name_assamese", "date_label", "start_year", "end_year", "summary")}
    return {"title": "Ahom kingdom (1228–1826): periods, groups, characters, centuries and scenes",
            "note": "Generated by tools/build.py from data/ahom.csv. Edit the CSV, then rebuild.",
            "periods": [dict(p, dynasties=groups)], "centuries": centuries,
            "scenes_without_characters": [s for s in scenes if not s.get("people")]}


def main():
    with open(ROOT / "data/ahom.csv", newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    tree = build_tree(rows)
    if not problems and build_site(tree):
        (ROOT / "data/ahom.json").write_text(json.dumps(tree, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    if problems:
        print("\n".join(problems)); sys.exit(1)
    print(f"data/ahom.json: {sum(len(g['characters']) for g in tree['periods'][0]['dynasties'])} people, "
          f"{sum(c['scene_count'] for c in tree['centuries'])} scenes")


if __name__ == "__main__":
    main()
