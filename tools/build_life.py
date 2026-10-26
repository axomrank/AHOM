#!/usr/bin/env python3
"""Build the LIFE section: everyday life, villages and objects, from the generated collections in images/assam/.

Reads the curated list below and each collection's own manifest (titles, periods, uncertainty notes),
writes web copies to media/life/<section>/ (1600 px webp plus a 420 px thumb/), and the catalogue
data/life.json, which tools/build.py adds to data/site.js as `life`.

The originals under images/assam/ are never changed. Superseded versions, generation notes and the
real-photograph reference library (images/referance/) are left out. Kachari, Bhuyan and Ahom villages stay
separate sections, and every generated image is labelled as an interpretation.
Run: python3 tools/build_life.py   (then python3 tools/build.py)
"""
import json, re
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "images/assam"
OUT = ROOT / "media/life"
GEN = "AI-generated interpretation, not a reconstruction or a historical record."

# id, title, period, era (saga chapter it belongs beside), intro, caveat, [(file, title or None, note or None)]
SECTIONS = [
    ("ahom-village", "An Ahom village, c. 1450", "15th century", "foundation",
     "Ordinary Ahom households of the early kingdom: stilt and ground houses of timber, bamboo and thatch, ponds, rice fields and a village street.",
     "No plan of a 15th-century Ahom village survives. House forms, layout and dress are imagined from later and comparative evidence; this is not a specific royal town.",
     [("15th-century/ahom-whole-village-three-views/01-village-overview.png", "The whole village from above", None),
      ("15th-century/ahom-whole-village-three-views/02-pondside-village-life.png", "Life by the village pond", None),
      ("15th-century/ahom-whole-village-three-views/03-village-and-rice-fields.png", "Houses and rice fields", None),
      ("15th-century/ahom-common-people-village-15th-century/ahom-common-people-village-c1450.png", "Common people of the village", None),
      ("15th-century/ahom-village-street-shan-roof/ahom-common-village-street-c1450.png", "A village street", None),
      ("15th-century/ahom-village-street-shan-roof/ahom-common-village-street-shan-people-v2.png", "Village street with Shan-style roofs", "Roof form follows Tai-Shan comparisons; speculative for Assam.")]),
    ("royal-settlement", "A royal settlement, c. 1450", "15th century", "foundation",
     "An imagined early royal compound of timber and straw: residences, gates, verandas and guards, before any of the surviving brick buildings.",
     "Early royal settlements need more research. Timber-and-thatch buildings are assumed; no 18th-century masonry palace is projected back. Named characters are artistic.",
     [("15th-century/royal-houses-and-settlement/ahom-royal-houses-settlement-c1450.png", "Royal houses and settlement", None),
      ("15th-century/ahom-royal-settlement-15th-century/ahom-royal-settlement-c1450.png", "The royal settlement", None),
      ("15th-century/royal-residence-timber-straw/ahom-royal-residence-timber-straw-c1450.png", "A royal residence of timber and straw", None),
      ("15th-century/royal-residence-timber-straw/ahom-royal-residence-soldier-uniforms-v2.png", "Guards at the royal residence", "Guard uniforms are a creative design, not a documented uniform."),
      ("15th-century/royal-settlement-five-camera-shots/01-momai-tamuli-residential-gate.png", "Momai Tamuli at the residential gate", None),
      ("15th-century/royal-settlement-five-camera-shots/02-numali-rajmao-house-interior.png", "Inside Numali Rajmao’s house", None),
      ("15th-century/royal-settlement-five-camera-shots/03-sarbeswari-upper-veranda.png", "Sarbeswari on the upper veranda", None),
      ("15th-century/royal-settlement-five-camera-shots/04-atan-lower-veranda.png", "Atan on the lower veranda", None),
      ("15th-century/royal-settlement-five-camera-shots/05-ambika-smaller-residence.png", "Ambika’s smaller residence", None)]),
    ("kachari", "A common Kachari village", "15th century", "foundation",
     "A separate scene group: an ordinary Kachari village of low thatched homes, bamboo fences, a household courtyard and the village green.",
     "Houses and clothing follow modern comparative photographs, which do not by themselves establish 15th-century appearance. No named festival or ritual is shown.",
     [("15th-century/kachari/01-kachari-village-overview.png", "The village and its bamboo gate", None),
      ("15th-century/kachari/02-kachari-household-courtyard.png", "A household courtyard", None),
      ("15th-century/kachari/03-kachari-village-green-gathering.png", "A gathering on the village green", None)]),
    ("bhuyan", "A Bhuyan village with Sankardev", "late 15th century", "foundation",
     "Common homes and a chiefly residence in an imagined Bhuyan village, with Sankardev reading sanchi-pat folios and women weaving and caring for manuscripts.",
     "House plans, dress and the daily scenes are artistic. Men’s white dhoti and shoulder cloth is this project’s costume direction, not a universal historical claim. No specific event is asserted.",
     [("15th-century/bhuyan/01-bhuyan-village-sankardev.png", "The village, with Sankardev", None),
      ("15th-century/bhuyan/five-domestic-scenes/01-sankardev-sanchipat-on-thoga.png", "Sankardev reading sanchi-pat on a thoga", None),
      ("15th-century/bhuyan/five-domestic-scenes/02-women-weaving-common-home.png", "Women weaving in a common home", None),
      ("15th-century/bhuyan/five-domestic-scenes/03-sankardev-veranda-reading-gathering.png", "A reading on the veranda", None),
      ("15th-century/bhuyan/five-domestic-scenes/04-women-pondside-courtyard.png", "A pond-side courtyard", None),
      ("15th-century/bhuyan/five-domestic-scenes/05-women-manuscript-reading-and-care.png", "Reading and caring for folios", None),
      ("15th-century/bhuyan/common-house-adaptations/01-basic-common-home-c15.png", "A basic common home", None),
      ("15th-century/bhuyan/common-house-adaptations/02-larger-common-veranda-home-c15.png", "A larger home with a veranda", None)]),
    ("life-and-work", None, None, None, None, None, "MANIFEST"),
    ("monuments-c1760", "Rang Ghar and Garhgaon, c. 1760", "18th century", "tungkhungia",
     "The age of the surviving brick buildings: Rang Ghar (1740s) and the Garhgaon Kareng Ghar (1752), with a palace consultation, festival days and an ordinary household.",
     "Monument outlines follow real photographs; finishes, furnishings, crowds and clothing are interpreted. The festival scenes are imaginative character crossovers, not documented gatherings.",
     [("18th-century/first-five/01-rang-ghar-pavilion-and-field-c1760.png", "Rang Ghar and its field", None),
      ("18th-century/first-five/02-rang-ghar-wrestling-day-c1760.png", "Wrestling day at Rang Ghar", None),
      ("18th-century/rang-ghar-buffalo-festival/rang-ghar-clean-buffalo-fight-v2.png", "A buffalo fight watched from Rang Ghar", None),
      ("18th-century/first-five/03-kareng-ghar-garhgaon-exterior-c1760.png", "The Garhgaon Kareng Ghar", None),
      ("18th-century/first-five/04-kareng-ghar-palace-consultation-c1760.png", "A consultation in the palace", None),
      ("18th-century/kareng-ghar-buffalo-festival/kareng-ghar-new-palace-buffalo-fight.png", "Suteupha, Ambika and Sarbeswari at a buffalo fight", None),
      ("18th-century/first-five/05-common-household-courtyard-c1760.png", "A common household courtyard", None)]),
    ("objects", "Objects of daily life", "Assamese tradition", None,
     "Things people used, wore and played: bell-metal vessels, rice tools, baskets, looms and silks, jewellery, instruments, manuscripts, plants and the Ahom emblem.",
     "Modern-style object renderings based on surviving Assamese traditions. Many forms are later than the Ahom period; none is a museum record of a dated object.",
     "OBJECTS"),
    ("assam-1950s", "Assam in the 1950s", "c. 1952", None,
     "After the kingdom: a village namghar, homestead, kitchen, weaving corner, dheki shed, ploughing, market and river landing.",
     "Generated scenes of mid-20th-century village life, not archival photographs.",
     [("50s/01-namghar-exterior.png", None, None), ("50s/namghar-1950s-guru-asan.png", "Inside the namghar", None),
      ("50s/02-village-homestead.png", None, None), ("50s/03-kitchen-interior.png", None, None), ("50s/04-weaving-corner.png", None, None),
      ("50s/05-dheki-shed.png", None, None), ("50s/06-paddy-ploughing.png", None, None), ("50s/07-village-market.png", None, None),
      ("50s/08-river-landing.png", None, None)]),
    ("assam-1990s", "Assam in the 1990s", "1990s", None,
     "Homes from basic to well-off, a village namghar at golden hour and children dancing Bihu in a courtyard.",
     "Generated scenes, not photographs of real households.",
     [("90s/01-basic-home.png", None, None), ("90s/02-modest-farmstead.png", None, None), ("90s/03-middle-income-home.png", None, None),
      ("90s/04-prosperous-courtyard.png", None, None), ("90s/05-wealthy-bungalow.png", None, None),
      ("90s/assam-village-namghar-1990s-close-golden-hour.png", "A village namghar at golden hour", None),
      ("90s/assam-1990s-children-bihu-courtyard.png", "Children dancing Bihu", None)]),
    ("assam-today", "Assam today", "present day", None,
     "Village lanes, paddy fields, homes, a namghar interior, Bihu, husori and tea plucking.",
     "Generated present-day scenes, not photographs of particular places.",
     [(str(p.relative_to(SRC)), None, None) for d in ("scenes", "houses", "culture", "work") for p in sorted((SRC / "present-day" / d).glob("*.png"))]),
]

OBJECT_GROUPS = ["vessels", "household", "textiles", "jewellery", "accessories", "instruments", "manuscripts", "plants", "emblems"]
OBJECT_SKIP = {"guru asan 2.png"}
STRIP = re.compile(r"(-c1[45]\d0|-c15|-c1760|-v\d+|^\d+-|^assam-|-1950s|-1990s)", re.I)


TITLES = {"guru-asan-minimal-3d": "Guru asan", "brass-bell-metal-utensils": "Brass and bell-metal utensils", "xorai-bell-metal": "Bell-metal xorai",
          "assam-harvested-paddy-sunset": "Harvested paddy at sunset", "assam-semi-rural-lane-red-roof-house-banana-utility-lines": "A semi-rural lane",
          "assam-village-lane-jeura-fences": "A village lane with jeura fences", "assam-village-road-harvested-paddy-namghar-haystacks-golden-hour": "Haystacks by the namghar road",
          "assam-village-road-paddy-field-homesteads-transmission-line": "Homesteads along a paddy road", "assam-wet-rice-homestead-dawn": "A wet-rice homestead at dawn",
          "assam-village-house-brick-pattern-sunlight": "A brick-patterned village house", "assam-village-house-painted-monsoon": "A painted house in the monsoon",
          "assam-rongali-bihu-dance-dhol-pepa-painted-gable-house-jeura": "Rongali Bihu dance", "assam-husori-xewa-men-women-betel-leaf-dhol-village-courtyard": "Husori in a village courtyard",
          "assam-namghar-interior-gamosa-columns-prayer-dais": "Inside a namghar today", "assam-tea-garden-workers-hand-plucking-bamboo-baskets": "Plucking tea by hand",
          "assamese-bihu-dhol-bamboo-slat-gamosa": "Bihu dhol", "assamese-toka-split-bamboo-clappers": "Toka bamboo clappers",
          "assamese-pepa-double-buffalo-horn-bamboo-pipes": "Pepa horn pipe", "ngi-ngao-kham-emblem-cloth-flag": "Ngi Ngao Kham flag",
          "ngi-ngao-kham-living-creature-v2": "Ngi Ngao Kham as a living creature", "ngi-ngao-kham-hyperreal-creature": "Ngi Ngao Kham, sculpted", "ngi-ngao-kham-gold": "Ngi Ngao Kham in gold",
          "03-middle-income-home": "A middle-income home"}


def humanize(name):
    if Path(name).stem in TITLES:
        return TITLES[Path(name).stem]
    words = STRIP.sub("", Path(name).stem).replace("_", "-").split("-")
    words = [w for w in words if w]
    text = " ".join(words)
    return text[:1].upper() + text[1:]


def save(src, rel):
    """Write the web copy and thumb (skipped when newer than the original); return their paths and size."""
    full, thumb = OUT / rel, OUT / Path(rel).parent / "thumb" / Path(rel).name
    with Image.open(src) as im:
        size = im.size
        if not (full.is_file() and thumb.is_file() and full.stat().st_mtime >= src.stat().st_mtime):
            im = im.convert("RGBA" if "A" in im.getbands() or "transparency" in im.info else "RGB")
            full.parent.mkdir(parents=True, exist_ok=True); thumb.parent.mkdir(parents=True, exist_ok=True)
            big = im.copy(); big.thumbnail((1600, 1600)); big.save(full, quality=80, method=6)
            small = im.copy(); small.thumbnail((420, 420)); small.save(thumb, quality=78, method=6)
    return [str(full.relative_to(ROOT)), str(thumb.relative_to(ROOT))], size


def manifest_section():
    m = json.loads((SRC / "ahom-life-and-work/collection-manifest.json").read_text(encoding="utf-8"))
    sources = {s["id"]: s for s in m["sources"]}
    names = {"01-river-life": "River life", "02-craft-workshops": "Craft workshops", "03-household-life": "Household life",
             "04-market-day": "Market day", "05-writing-and-records": "Writing and records", "06-military-preparations": "Preparing for war",
             "07-building-and-maintenance": "Building and maintenance", "08-places-across-time": "Places across time"}
    items = []
    for a in m["assets"]:
        photo = "photograph" in a["kind"]
        src = ROOT / a["file"]
        img, size = save(src, f"life-and-work/{a['group']}/{Path(a['file']).stem}.webp")
        items.append({"id": a["id"].replace("/", "--"), "title": a["title"], "period": a["period"], "group": names[a["group"]],
                      "img": img, "w": size[0], "h": size[1], "alt": a.get("alt") or a["title"],
                      "text": a.get("caption") if photo else a["scene"].split(". ")[0] + ".",
                      "note": a["uncertainty"], "kind": "photo" if photo else "generated",
                      "credit": a.get("caption") if photo else "",
                      "sources": [{"title": sources[i]["title"], "url": sources[i]["url"]} for i in a.get("source_ids", []) if i in sources]})
    return {"id": "life-and-work", "title": "Life and work in the kingdom", "period": "c. 1750", "era": "tungkhungia",
            "intro": "Eight sets on how ordinary people worked: the river and its boats, craft workshops, the household, market day, writing chronicles, preparing for war, building, and two monuments then and now.",
            "caveat": m["historical_status"] + " Two modern photographs are included unchanged for comparison.", "items": items}


def objects_section(meta):
    sid, title, period, era, intro, caveat, _ = meta
    files = [p for p in sorted((SRC / "fixed-elements").glob("*.png")) if p.name not in OBJECT_SKIP]
    groups = [("Everyday things", files)] + [(g.capitalize(), sorted((SRC / "fixed-elements" / g).glob("*.png"))) for g in OBJECT_GROUPS]
    items = []
    for gname, paths in groups:
        for p in paths:
            rel = p.relative_to(SRC / "fixed-elements")
            img, size = save(p, f"objects/{rel.with_suffix('.webp')}")
            items.append({"id": f"objects--{rel.with_suffix('').as_posix().replace('/', '--')}", "title": humanize(p.name), "group": gname,
                          "img": img, "w": size[0], "h": size[1], "alt": humanize(p.name), "kind": "object"})
    return {"id": sid, "title": title, "period": period, "era": era, "intro": intro, "caveat": caveat, "items": items}


def main():
    out = []
    for meta in SECTIONS:
        sid, title, period, era, intro, caveat, files = meta
        if files == "MANIFEST":
            out.append(manifest_section()); continue
        if files == "OBJECTS":
            out.append(objects_section(meta)); continue
        items = []
        for f, t, note in files:
            src = SRC / f
            img, size = save(src, f"{sid}/{Path(f).stem}.webp")
            items.append({"id": f"{sid}--{Path(f).stem}", "title": t or humanize(f), "period": period, "img": img,
                          "w": size[0], "h": size[1], "alt": t or humanize(f), "kind": "generated", **({"note": note} if note else {})})
        out.append({"id": sid, "title": title, "period": period, "era": era, "intro": intro, "caveat": caveat, "items": items})
    data = {"note": "Generated by tools/build_life.py from images/assam/. Do not edit.", "label": GEN, "sections": out}
    (ROOT / "data/life.json").write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"data/life.json: {len(out)} sections, {sum(len(s['items']) for s in out)} images")


if __name__ == "__main__":
    main()
