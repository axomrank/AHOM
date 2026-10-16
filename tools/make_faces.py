#!/usr/bin/env python3
"""Cut a face portrait for each person from the face close-up cell of their turnaround sheet.

Turnaround sheets are laid out as two rows of four views; the bottom-left view is the face close-up.
This writes media/faces/<id>.webp (4:5, for the arch-framed portraits on the website) for every person
who has media/characters/<id>/turnaround-1.webp, skipping faces that already exist unless --force is given.
Run: python3 tools/make_faces.py [--force]; then python3 tools/build.py
"""
import sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "media/faces"


def main():
    force = "--force" in sys.argv
    OUT.mkdir(exist_ok=True)
    made = 0
    for sheet in sorted(ROOT.glob("media/characters/*/turnaround-1.webp")):
        out = OUT / f"{sheet.parent.name}.webp"
        if out.exists() and not force:
            continue
        im = Image.open(sheet).convert("RGB")
        W, H = im.size
        top, bottom = int(H * .60), int(H * .93)
        h = bottom - top
        w = int(h * .8)
        cx = int(W * .125)
        face = im.crop((cx - w // 2, top, cx + w // 2, bottom)).resize((320, 400), Image.LANCZOS)
        face.save(out, "WEBP", quality=80, method=6)
        made += 1
    print(f"{made} faces written to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
