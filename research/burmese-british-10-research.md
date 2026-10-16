# Burmese and British figures — local reference batch

Prepared 16 October 2026. User requested ten realistic sheets using local references. The catalogue now has twelve people in this group. Scope interpreted as the original ten through Archibald Campbell, excluding the later Thomas Robertson and Francis Jenkins entries. No sheets generated: first built-in generation attempt for Welsh returned usage_limit_reached (HTTP429). Tool reports reset at 16 October 2026, 23:05 IST. No automatic retry or scheduled action created. Catalogue is unchanged.

## Prepared roster

1. Captain Thomas Welsh — research/captain-welsh/
2. Lord Cornwallis — research/cornwallis/
3. Bodawpaya — research/bodawpaya/
4. Kiamingi (Ala Mingi) — research/kiamingi/
5. Mingimaha Tilwa — research/mingimaha-tilwa/
6. Bagyidaw — research/bagyidaw/
7. Maha Bandula — research/maha-bandula/
8. David Scott — research/david-scott/
9. Colonel Alfred Richards — research/alfred-richards/
10. Sir Archibald Campbell — research/archibald-campbell/

Each folder contains a full generation-prompt.txt and local-scene-references.md. Each prompt requests a realistic eight-view sheet, serious expression, consistent identity/clothing, and ARTISTIC RECONSTRUCTION footer. Only local project images are supplied as generation inputs.

## Local artwork inspected

- 18_Captain_Thomas_Welsh_Expedition.webp: foreground mounted European officer is the strongest Welsh continuity reference. The scene is also linked to Cornwallis, but Cornwallis cannot be individually located: do not duplicate Welsh as Cornwallis.
- 19_Ahom_British_Commercial_Treaty_v02.webp: inspected for Welsh-era cloth and uniform context; seated European identities are not assigned individually.
- 22_First_Burmese_Invasion_v03.webp: regional maroon/gold military textile and ornamental vocabulary. Mounted general is not an authenticated Bodawpaya or Bagyidaw. Their royal faces must be newly reconstructed.
- 25_Second_Burmese_Invasion_and_Purandar_Flight.webp: foreground fleeing rider is Purandar. Background Burmese troops provide Kiamingi military context; no individual Kiamingi portrait assignment supported.
- 26_Chandrakanta_Singha_Restored_Under_Burmese_Control.webp: Burmese guard armor reference for Mingimaha Tilwa; seated king is Chandrakanta and must not be copied as Burmese general.
- 28_Jogeswar_Singha_Under_Burmese_Control.webp: prominent armored officer immediately right of centre selected provisionally for Maha Bandula continuity. Seated figure is Jogeswar. This is a production assignment, not authenticated likeness.
- 29_First_Anglo_Burmese_War_and_Treaty_of_Yandabo_Montage.webp: lower-left panel navy-coated official between redcoats provisionally selected for David Scott. Metadata links both Scott and Campbell but does not individually label panel positions. Civilian role informs removal of military epaulettes/medals.
- 30_First_Anglo_Burmese_War_v01.webp: left mounted officer provisionally selected for Richards. White pith helmet in scene is anachronistic for 1824; prompt substitutes period-style shako while retaining local face, red coat and overall identity. Exact uniform details remain unverified.
- 31_Treaty_of_Yandabo_v02.webp: seated redcoat behind navy-coated reader provisionally selected for Campbell; no individual labels support exact mapping. Avoid standing officer's oversized plumed helmet. Adapt apparent age to mid-fifties.

All are modern local illustrations. Do not treat scene-level person links as proof of which figure occupies a position. Choices above are disclosed creative continuity decisions. Burmese royal dress briefs are interpretive and need visual review after generation, particularly distinction from Ahom and Thai regalia.

## External checks and limitations

Local CSV roles, summaries and linked scenes reviewed first. Web discovery used for age, role and costume safeguards, not to replace the requested local visual inputs.

- National Portrait Gallery NPG4316, John Smart, Charles Cornwallis, 1792: contemporary portrait discovery. https://www.npg.org.uk/collections/search/portraitExtended/mw01484/Charles-Cornwallis-1st-Marquess-Cornwallis
- Nelson-Atkins John Smart portrait catalogue: indexed description supports scarlet coat, blue facings, gold epaulettes, Garter insignia. Portrait description, not local likeness. https://www.nelson-atkins.org/starr/contents/volume-4/John-Smart/India/F65-41-33/
- Government of Assam Jorhat district history: indexed passage records Scott, Richards and Campbell roles around1826; does not establish personal uniform or face. https://jorhat.assam.gov.in/about-us/history-jorhat
- British Museum parabaik2011,3015.1: indexed catalogue describes Burmese court/military dress and rank constraints. Object dates c1880, so it is later comparative evidence, not proof of early nineteenth-century royal clothing. https://www.britishmuseum.org/collection/object/A_2011-3015-1
- British Museum Myanmar timeline: Konbaung and Bodawpaya context. https://www.britishmuseum.org/exhibitions/burma-myanmar/myanmars-many-cultures-timeline
- Bodawpaya and Bagyidaw biography discovery used to avoid depicting both as same age: Bodawpaya born1745, Bagyidaw born1784. Ages in prompts are period approximations. https://en.wikipedia.org/wiki/Bodawpaya and https://en.wikipedia.org/wiki/Bagyidaw

No authenticated portrait established for Welsh, Kiamingi, Mingimaha Tilwa, Bandula, Scott or Richards in this check. Actual historical likeness is not claimed. Exact military unit insignia, personal awards and Burmese royal sumptuary entitlement are not established; prompts avoid unsupported precise insignia.

## Remaining work

Generate each sheet using its saved prompt and local image reference, inspect all eight views, repair material defects as needed, import through tools/add_sheets.py, add captions and provenance, run tools/build.py and verify images/thumbnails. Do not mark catalogue entries completed until actual generated assets exist.
