# Ahom

The Ahom kingdom of Assam, 1228–1838: a website that tells its story chapter by chapter, sets out all forty-one reigns on one time line, and collects the people and painted scenes of the chronicles.

Live at https://axomrank.github.io/AHOM/

## What is where

| Path | What it holds |
| --- | --- |
| `index.html`, `assets/` | The website: one page, plain HTML, CSS and JavaScript, no build step |
| `data/ahom.csv` | The master file: the period, every person and every scene, one row each |
| `data/eras.json` | The eight chapters of the saga: their text, the Assamese word behind each, and the films |
| `data/ahom.json` | The whole catalogue as nested JSON (generated) |
| `data/site.js` | What the website loads (generated) |
| `media/characters/` | Portraits and character sheets, one folder per person, with `thumb/` copies |
| `media/scenes/` | Scene paintings by era, with `thumb/` copies |
| `media/faces/` | Face portraits cut from the character sheets (generated) |
| `media/reels/` | The short films, compressed, each with a poster frame |
| `research/` | Research notes per person and per batch, and the reel scripts |
| `tools/` | Content generation, reel preparation, validation and deployment packaging |
| `chapters/`, `people/`, `scenes/`, `films/`, `trails/` | Generated, crawlable reference pages with metadata and sources |
| `data/explore.json` | Reading paths and the schematic places guide |

`archive/` (originals, full-size reels, backups) and `incoming/` stay on your computer and are not in git.

## Changing the content

1. Edit `data/ahom.csv` (people, scenes, images) or `data/eras.json` (the saga chapters).
2. If you added a character sheet, cut its face portrait: `python3 tools/make_faces.py`
3. Rebuild the data: `python3 tools/build.py`

Install the build dependency with `python3 -m pip install -r requirements.txt`.
Run `python3 tools/verify_site.py` before publishing. Pages deployment runs both commands
and stages only public assets with `python3 tools/package_site.py _site`.

The film library has 49 distinct shots: the original 27 and 22 additional clips in
`media/reels/clean2/`. The 21 files in `Clean/` are alternate encodes or shorter cuts,
not additional shots. `research/reel-inventory.json` records every file and selection.
`python3 tools/prepare_reels.py` regenerates the editorial reel catalogue and posters
(requires ffmpeg/ffprobe); then run the regular content build. This leaves footage intact.

All 49 films have optional English and Assamese context subtitles, written scene
descriptions and links to historical context. The subtitles describe the scene;
they do not transcribe speech. `data/reel-context.json` holds the Assamese titles.
Existing scripted Assamese lines and English translations are labelled as scripts, not audio
transcripts. Verified speech captions are still needed; do not derive them from prompts.
The places guide uses real district polygons and 39 river paths from the local APP
catalogue (`assets/maps/assam.json`, originally imported from `Dist + Rivers (simplified).kmz`).
Site coordinates are copied from APP's `content/entities.json`. Modern district outlines
are a geographic reference, rather than the borders of the historical kingdom. The map
works without a tile service and supports region presets, zoom, pan and scene filtering.

The build stops and lists the problem if a row names an unknown person or an image file that is missing.

## Viewing it locally

Open `index.html` in a browser, or serve the folder:

```bash
python3 -m http.server 8765
```

Pushing to `main` publishes the site through the GitHub Pages workflow in `.github/workflows/deploy.yml`.

The paintings, portraits and films are modern reconstructions, not likenesses from the period.
