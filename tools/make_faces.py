#!/usr/bin/env python3
"""Cut a face portrait for each person from the face close-up cell of their turnaround sheet.

Turnaround sheets are laid out as two rows of four views; the bottom-left view is the face close-up.
This writes media/faces/<id>.webp (4:5, for the arch-framed portraits on the website) for every person
who has a turnaround-1.webp or legacy sheet-1.webp, skipping faces that already exist unless --force is given.
Run: python3 tools/make_faces.py [--force] [--person ID]; then python3 tools/build.py
"""
import argparse
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "media/faces"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--force', action='store_true')
    parser.add_argument('--person', help='Generate only this person’s preview')
    args = parser.parse_args()
    force = args.force
    OUT.mkdir(exist_ok=True)
    made = 0
    folders = [ROOT / 'media/characters' / args.person] if args.person else sorted((ROOT / 'media/characters').iterdir())
    for folder in folders:
        sheet = next((folder / name for name in ('turnaround-1.webp', 'sheet-1.webp') if (folder / name).is_file()), None)
        if sheet is None:
            continue
        out = OUT / f"{sheet.parent.name}.webp"
        if out.exists() and not force:
            continue
        im = Image.open(sheet).convert("RGB")
        W, H = im.size
        top, bottom = int(H * .60), int(H * .93)
        # Ragha's older labelled sheet places the full face panel higher than the turnaround template.
        if folder.name == 'ragha-moran':
            top, bottom = int(H * .53), int(H * .92)
        h = bottom - top
        w = int(h * .8)
        cx = int(W * .125)
        face = im.crop((cx - w // 2, top, cx + w // 2, bottom)).resize((320, 400), Image.LANCZOS)
        face.save(out, "WEBP", quality=80, method=6)
        made += 1
    print(f"{made} faces written to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
