# Use this library for image creation

## The distinction to preserve

**Hindu temple architecture and Ahom royal/civic architecture are separate reference groups.** Joy Dol, Shiva/Siva Dol, Vishnu Dol, Devi Dol, Ranganath and related temples belong in the Hindu temple group. Record Ahom royal patronage as historical context, independently of religious function and architectural form. Do not use a temple tower, sanctum, deity sculpture or temple plan as the default design for an Ahom royal house, palace, ordinary dwelling or town.

This is the user's reference-selection convention for this project. It is carried forward in the project `AGENTS.md`, folder names and each photograph's metadata.

## Find the right references

Open [the searchable gallery](index.html) to filter by group, then search a monument, interior, brickwork, relief, tank or other feature. The gallery hides unrelated Tripura material by default. Open a photograph at full size and read its adjacent `.source.json` before supplying it to image generation.

| Folder | Purpose | Limits |
|---|---|---|
| `01_ahom_royal_and_civic/` | Rang Ghar, Kareng Ghar, Talatal Ghar, Golaghar, Namdang bridge | Surviving masonry is predominantly later than the 15th century; function and date matter |
| `02_tai_ahom_funerary/` | Charaideo and other maidams | Funerary tradition; not palace or village-house plans. Individual visible structures and repairs need dating |
| `03_hindu_temple_architecture/` | Shiva, Vishnu/Joy Dol, Devi and other Hindu temples, separated by site | Use for a temple-specific brief; do not silently blend into a generic Ahom royal-town brief |
| `04_mixed_and_memorial/` | Ghanashyam's House and Fakuwa Doul, kept separately | Mixed influences and memorial interpretations require explicit qualification |
| `05_water_and_landscape/` | Assam tanks, water settings and surroundings | Modern scenery can contain temples, colleges, paths and contemporary buildings |
| `06_material_culture/` | Cannons and the displayed Charaideo iron boat | Objects are not architecture; their individual dates and original contexts need verification |
| `07_modern_site_context/` | Modern visitor structures, roads, tourist scenes and wildlife | Landscape/context only; exclude modern infrastructure from historical reconstructions |
| `90_needs_identity_review/` | Conflicting Kareng/Talatal labels | Identify the building visually and check sources before use |
| `99_excluded_unrelated/` | Tripura's Rudrasagar/Neermahal photographs | Not Assam or Ahom references. Retained only to document and reverse the collection error |

Within a building's folder, photographs are grouped as general views, interiors/access, details/materials, site/landscape, or information boards. View types are inferred from titles, so a “general view” may still contain a detail or an interior. Information boards support research; they are not visual style references.

## For a 15th-century Ahom royal town

1. Research the specific reign, settlement, building function and approximate date before selecting references. A royal town requires a royal/administrative settlement brief; a small rural village does not establish its appearance.
2. Treat surviving later masonry as comparative material only. Do not backdate Rang Ghar, the surviving Kareng/Talatal forms, later temples or Namdang bridge into circa 1450.
3. Separate evidence from interpretation in the prompt. Timber construction, exact roof form, gates, ramparts, street layout, courtyards, clothing and ornament each need their own support; a confident generated image is not historical evidence.
4. Assign each chosen image a narrow role: “brick texture only,” “later palace comparison,” “burial-mound landscape,” or “water and vegetation only.” State what must not be copied, including temple silhouettes and modern site works.
5. Keep generated images and their prompts under `output/imagegen/` or a clearly marked reconstruction folder, outside this real-photograph library. The two earlier village/town images in this chat are speculative generated interpretations and must not become source evidence.

**Prompt scaffold:** “Imagine [named place/function], Assam, circa [date]. Evidence: [source-backed features]. Reference A supplies [specific feature] only. Reference B supplies [specific feature] only. Interpretive details: [list]. Do not import Hindu temple form into the royal/civic buildings. Exclude later surviving masonry, modern site infrastructure and unrelated regional architecture unless independently justified.”

## Special cases and source notes

- **Ghanashyam's House:** the district source describes Hindu and Islamic architectural influences and an 18th-century structure. Keep it in the mixed-influences group; its name is not evidence for a generic medieval Ahom dwelling. [Government of Assam](https://sivasagar.assam.gov.in/tourist-place-detail/330)
- **Fakuwa Doul:** the district source dates it to 1703–1704 and records a local burial belief. Label it as memorial/shrine with qualified interpretation, rather than treating that belief as proof of an authenticated maidam. Ranganath is separately identified as a Shiva temple. [Government of Assam](https://sivasagar.assam.gov.in/tourist-place-detail/331)
- **Early timber palace analogy:** ASI describes Garhgaon's palace of 1540 as wood and other impermanent material, and distinguishes it from the surviving structure of 1752. This is later comparative evidence, not an exact 15th-century palace plan. [ASI](https://asiguwahaticircle.gov.in/Ahom%20Rajas%20palace.html)
- **Maidams:** UNESCO identifies the Tai-Ahom funerary tradition at Charaideo across the 13th–19th centuries. The tradition's date range does not individually date every photographed structure or restoration. [UNESCO](https://whc.unesco.org/en/list/1711)
- **Two Rudrasagars:** unrelated Tripura photographs entered through a Commons category for Rudrasagar Lake. Tripura's Neermahal is not an Ahom monument. These images are quarantined and excluded from normal gallery results. [Tripura Tourism](https://tripuratourism.gov.in/images/documents/1731059147.pdf)

## Metadata and audit limits

The authoritative index is [reference-manifest.json](00_catalogue/reference-manifest.json), also available as [CSV](00_catalogue/reference-manifest.csv). Each photograph retains source URL, original-image URL, attribution, licence information, original collection path, architectural group, period note, classification rationale and SHA-256 checksum. Official district photographs do not have individually stated reuse licences; do not infer a Commons licence for them.

Classification is based on source titles, descriptions/categories, the user's requested taxonomy and targeted source checks. It is **not a full visual authentication of all 850 photographs**. Site names and descriptions can be wrong; ambiguous identities are kept for review. Modern gates, restoration, visitor works and mixed temple/landscape compositions may still appear inside otherwise relevant images.

All image bytes were retained during organization. [The move ledger](00_catalogue/move-ledger.json) maps former paths to current ones. Original download manifests and logs in `00_catalogue/download_records/` are historical records with old paths, not current browsing indexes. Legacy downloaders are guarded against recreating the previous folders.
