# Assam base map

`assam.json` is copied unchanged from the local APP project's `content/maps/assam.json`.
The same dataset exists in the current Axomrank project. It contains 33 district
polygon collections, 39 river paths and an approximate Patkai ridge.

The source catalogue records its origin as `Dist + Rivers (simplified).kmz`,
processed by APP's `scripts/import_kmz.py`. Coordinate arrays are `[latitude, longitude]`.
The district boundaries describe the source's modern administrative geography.
They are not historical Ahom boundaries. This view does not draw the approximate ridge.

The eight site coordinates in `data/explore.json` come from APP's `content/entities.json`.
Combined labels use a single explicit anchor: Saraighat for Guwahati / Saraighat,
Rangpur for Rangpur / Sivasagar, and Namrup for Namrup / Patkai.

`assets/map.js` projects the supplied river geometry directly and leaves the source data intact.
The MAP explorer can optionally draw the modern district polygons. Its expanded catalogue of
77 reference points is stored in `data/map-sites.json`; `data/map-stories.json` adds event
connections with explicit qualifications. These connections are not surveyed historical tracks.

## Optional boundary layers

Assam, India and district pills toggle independently and start off. They sit below rivers,
story routes and place pins. India also offers an overview; Follow event returns to the story.
These layers provide modern reference geography, not historical Ahom borders or a current
administrative gazetteer. Districts retain the source catalogue's 33-unit vintage.

`boundaries.json` contains `[latitude, longitude]` exterior rings:

- Assam: the original local KMZ district polygons dissolved before simplification (0.003°).
- India: [DataMeet Community Maps, india-soi.geojson](https://github.com/datameet/maps/blob/master/Country/india-soi.geojson),
  derived from Survey of India / Census 2011 geometry, simplified with topology preservation
  (0.008°). [Source and license](https://github.com/datameet/maps/blob/master/Country/README.md):
  CC BY-SA 2.5 / ODbL as recorded by DataMeet. This derived India geometry is shared under
  those same terms; attribution must be retained.

Rebuild with `tools/import_boundaries.py LOCAL_KMZ INDIA_SOI_GEOJSON` (requires Shapely).
Input SHA-256 hashes are retained in the output. The normal site build needs no GIS libraries.

## International borders

`world.json` supplies 258 country and territory features from
[Natural Earth 1:10m admin-0 countries](https://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-admin-0-countries/).
It includes coastlines, small countries and overseas islands. The International pill loads
this file on demand and exposes View world; all other boundary pills remain independent.
Natural Earth's default de facto geography may differ from the separately sourced India
outline. These are modern context layers. Data is [public domain](https://www.naturalearthdata.com/about/terms-of-use/).

Re-import with `tools/import_world_boundaries.py ne_10m_admin_0_countries.geojson`
(requires Shapely). Exterior rings are simplified at 0.012°, preserving topology and
small features. The renderer precompiles paths and excludes offscreen rings while panning.

## Sukaphaa journey

The `sukaphaa` reading path and `AHOM-001` overview link Mong Mao, the Patkai / Pangsau
catalogue reference, Namrup, Tipam, Habung, Simaluguri and Charaideo (1215–1253).
The following four stages animate subsets of the journey. Straight connections mark
approximate named reference places, omitting intermediate stops; they do not reconstruct
the exact migration trail or imply all settlements were founded in 1228.
Sources are attached to the overview in `data/map-stories.json`: Dimbeswar Neog,
*Introduction to Assam*, p. 67, and N. K. Basu, *Assam in the Ahom Age*.
