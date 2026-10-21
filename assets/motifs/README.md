# Ahom web restyle: art brief and provenance

**Status:** hand-authored fallback. Recraft's MCP tools were not available in this session, so
these SVGs were drawn directly (design-assets skill, fallback lane 1). Re-run through Recraft
(`generate_image` with `vector_illustration`) once it is reachable, and compare.

## Direction

Keep the existing site's UX (saga, kings, people, scenes, films, lightbox) and replace the UI
and palette with the look of the reference posters: warm cream paper, a lacquer-maroon seal bar,
gold ornament, sage botanicals, torn-paper photographs, and a hand-lettered annotation.

- Palette (light): paper `#F4EDDF`, maroon `#5A0E1C`, gold `#B8862B`, ink `#33241A`, sage `#5E7A45`.
  Dark (for `prefers-color-scheme: dark`): paper `#1D0A10`, gold `#C9A04A`.
- Type: Marcellus (display), Alegreya (text), Dancing Script (hand-lettered notes), Noto Serif
  Bengali and Tiro Bangla (Assamese).
- Shapes: keel arch for portraits and films (the temple doorway); torn-bottom print for paintings.

## Motifs

| File | Brief | Use |
| --- | --- | --- |
| `feather.svg` | Two-vane feather with cream banding, one shaft. Vanes in brown, two tones. | Hero, behind the film |
| `leaf-sprig.svg` | Stem with pinnate sage leaves, midribs. Filled. | Footer corner |
| `sprig-line.svg` | The same sprig as an ink line drawing. | Page-head corner |
| `bamboo.svg` | Three culms with nodes and blades, sage. | Films section, left edge |
| `sparkle.svg` | Four-point star, cream with gold edge. | Available for markers |
| `crest.svg` + `crest.css` | The Ahom crest: gilt beast in a lobed cartouche, traced from the reference image; the CSS component masks it with a restylable gilt fill. Variants: `--maroon`, `--bare`, `--organism` (the animal alone, from `organism.svg`), `--shine`, `--sm`, `--lg`. | Seal, cards, the cartouche |

Keep motifs decorative (`aria-hidden` or CSS background), never as content.

## Checks done

- Rendered light (1280) and phone (375) in the browser pane: home, chapter, scene grid, kings.
- Both themes: the light palette is the default look; dark applies under `prefers-color-scheme`.
- Class names in `assets/app.js` are unchanged, so the rendering logic is untouched.
