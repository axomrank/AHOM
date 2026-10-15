# Assamese Heritage & Legends — AI Art Gallery

An offline-capable collection of **58 AI-generated artworks**, with subject/category browsing, original and personal tags, ratings, historical-review flags, and synchronized side-by-side image comparison.

## Use the gallery

Open `index.html` or the GitHub Pages site. Choose two **Compare this image** boxes and click **Compare**. Zoom with the linked slider or scroll wheel; drag either image to pan both. Select an artwork to rate it, add comma-separated tags, flag details for correction, or record notes. Existing artwork IDs are preserved as direct links (`#sukapha-portrait`, for example).

Categories remain History & Royalty, Folklore & Legends, Sacred & Culture, Traditional Architecture, and Notable Figures. Subjects and source tags come from the original catalogue, with titles and descriptions preserved. No unverified chronology has been invented. All 58 files remain, including one exact duplicate pair; `duplicate-review.html` lets you compare exact copies, perceptual-similarity suggestions, and same-subject variants, then export choices without deleting files automatically.

Personal reviews stay in this browser. **Export personal reviews** saves portable JSON; **Import personal reviews** merges matching entries, replacing reviews for matching IDs and image checksums. Local files and the hosted website use separate browser storage. The storage key and export schema are separate from the AHOM library, so the two galleries do not overwrite each other's notes.

## Assets and metadata

- `images/`: 58 original artworks with original filenames and folders unchanged.
- `data/gallery.json`: original gallery metadata, retained unchanged.
- `catalog.json` / `catalog.js`: review catalogue, original checksums and offline browser data.
- `thumbnails/`: lightweight WebP previews; originals load on demand.
- `gallery.js`, `gallery.css`, `gallery-template.html`: the gallery interface.
- `build_gallery.py`: verifies original checksums and rebuilds thumbnail/catalogue outputs (requires Pillow).
- `backup_library.py`: creates a verified local ZIP with SHA-256 sidecar under ignored `backups/`.

These images are AI-generated interpretations, not historical photographs, verified likenesses, or evidence of historical appearance. Source captions, identity associations, costumes, architecture and cultural details may need review. A personal review checkbox records your review and does not establish historical accuracy.

## Rebuild and back up

```sh
python -m pip install pillow
python build_gallery.py
python backup_library.py
```

The backup script verifies original image checksums, ZIP integrity and archived image checksums. Copy the ZIP and SHA-256 sidecar to another drive or cloud storage. Export personal review JSON separately and retain it alongside the backup; the script cannot access browser storage.

Other repository material, including Instagram cards and college research documents, remains unchanged and is not mixed into the 58-artwork gallery. GitHub Pages deploys via the existing workflow.
