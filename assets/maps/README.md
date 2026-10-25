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

`assets/map.js` projects the supplied geometry directly and leaves the source data intact.
