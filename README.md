# AHOM — Curated Image Library

A combined collection of **265 illustrations** (207 AHOM images and 58 Assamese AI artworks), organised by chronology, characters, places and themes. Open `index.html` offline or on static hosting. `timeline.html` opens the same current collection.

## Browse and compare

Search captions, filenames, character aliases and personal notes. Filter by character/ruler, era, place, theme, tag, rating or review status. Select two **Compare this image** boxes and open **Compare**. The linked zoom slider and scroll wheel zoom both images; dragging either image pans both. **Reset view** restores the overview. The layout stacks on small screens.

Click an image to add a 0–5 star rating, comma-separated custom tags (such as `best version`, `book cover`, `carousel`, `avoid`), historical-review flags and notes. Flags cover dates, character identity, costumes, architecture and scene details. Marking an image personally reviewed is not independent historical verification.

Personal reviews stay in browser storage. They are not sent to a server or committed automatically. Use **Export personal reviews** regularly, then **Import personal reviews** on another browser or computer. Import validates stable IDs and original image checksums, merges matching entries, and replaces existing reviews for imported images. Browser storage is separate for local files, localhost and the hosted website; JSON exports make notes portable.

`duplicate-review.html` preserves the selection/export workflow for further removals. Its selections never delete files automatically. The five exact-copy removals and 21 user-selected visual removals are recorded in `exact_duplicate_removals.json` and `visual_duplicate_removals.json`.

## Files and provenance

- `images/`: 207 full-resolution AHOM originals, tracked with Git LFS.
- `thumbnails/`: lightweight WebP previews; full originals load when opened or compared.
- `catalog.json` / `catalog.js`: structured metadata and an offline-friendly browser copy. Stable IDs retain original source row numbers.
- `indexes/`: chronological, character, place and theme reference lists.
- `AHOM_KINGDOM_MASTER_CHRONOLOGY.csv`: the retained 207 AHOM source rows.
- `build_gallery.py`: checks original checksums and rebuilds thumbnails and catalogue JS; requires Pillow.
- `backup_library.py`: creates a verified local ZIP snapshot, excluded from Git.

Dates, captions and figure associations follow the [original source chronology](https://github.com/Angsumi/AHOM/blob/main/AHOM_KINGDOM_MASTER_CHRONOLOGY.csv). They are inherited assertions, not independently verified history. Illustrations are not documentary evidence of historical appearance. Eight unconfirmed scenes have no chronological sort year. Ranges retain their labels and sort by source numeric year; within-year order does not assert exact sequence. A ruler association does not guarantee the ruler is depicted. Place tags reflect the source capital/location field rather than an exhaustive depiction inventory.

## Clone, rebuild and back up

```sh
git lfs install
git clone https://github.com/axomrank/AHOM.git
cd AHOM
git lfs pull
python -m pip install pillow
python build_gallery.py
python backup_library.py
```

Backups appear in `backups/AHOM-library-<UTC timestamp>.zip` with a SHA-256 sidecar. The script verifies original checksums, ZIP integrity and archived image checksums before finalising. Copy the ZIP and sidecar to another drive or cloud storage. Export browser reviews separately and retain that JSON alongside your backup: the Python script cannot read browser storage. ZIPs exclude `.git`, existing backups, dependencies and browser test artifacts.

GitHub Pages deploys through `.github/workflows/deploy.yml`; checkout downloads the LFS originals. Local backups remain useful independently of GitHub or LFS availability.

## Complete AI repository import

`imports/assamese-ai-gallery/` contains every tracked file from the AI gallery repository at the commit recorded in `imports/source-import-manifest.json`, including college research and Instagram production material. The import is a content snapshot, not a Git-history merge. One upstream gitlink has no supplied working files or .gitmodules mapping; its original commit reference is preserved. `imports/index.html` provides searchable file navigation.

The main gallery combines 207 AHOM images and 58 AI artworks. Use Collection to browse either separately. AI artworks remain organised by subject and category, without invented chronology. Root review import accepts exports from both gallery schemas and validates IDs and checksums. The imported original gallery remains independently usable. All original artwork names, source metadata and selected-deletion records are retained. No additional image was deleted during this import.

Pages uses `prepare_pages.py` to stage tracked content without dereferencing machine-specific symlinks. Git retains original symlinks and embedded Git references; the static site shows reference information in their place.
